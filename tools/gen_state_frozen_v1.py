"""NOVA - Overlay de estado `Congelado` (ART-ST-FROZEN), v1: LA ESCARCHA.

Ref: NOVA_Estados_Animaciones.md 14.1, 14.6 y 14.7 - NOVA_Assets_Diseno.md A.3

EL TERCER CASO DE A.3, Y EL PRIMERO DE SU CLASE. Los dos glifos del Asteroide
viven FUERA del cuerpo y `ART-ST-SCARE` tiene que ATERRIZAR en la cara. Este
es el primero que CUBRE el cuerpo, que es el caso que A.3 daba por facil -«no
tienen que registrar con nada, asi que la regla les vale entera»-. No es
facil: es un problema distinto, y tiene dos restricciones duras que no se ven
hasta que se miden.

   1. LA CARA NO SE PUEDE ENTERRAR. 14.6 hace `Congelado` compatible con
      `Asustado` y 14.2 dice que el susto «siempre debe poder avisar». Si el
      hielo tapa los ojos, esa casilla de la matriz es mentira y 14.0 #5
      -«si el estado no se ve, es un bug»- se incumple para el estado mas
      importante del juego, no para este.
   2. EL CONTADOR DE NIVEL TAMPOCO. A.8 #2 cerro que el nivel se lee SOLO en
      el sprite, y un nodo congelado es EXACTAMENTE el que el jugador esta
      decidiendo si captura (7.3: se descongela vaciandolo y se lo lleva el
      ultimo emisor). Taparle el nivel es taparle el precio.

Y hay una tercera cosa, que es una correccion al inventario: `Congelado` se
aplica a «cualquier nodo encendido» (14.1) y el Asteroide NUNCA lo esta
-encenderlo lo convierte en otro tipo (4.1)-. Son TRECE sprites, no catorce.
Eso es lo que mide `nova_estados.CONGELABLES`.

DE DONDE SALE LA FORMA. El frio no sale del nodo: le llega. Asi que esta
propuesta se organiza desde FUERA HACIA DENTRO, y ese eje esta libre: la
Estrella se ordena alrededor de su centro, el Pulsar alrededor de un eje a
32 grados, el Magnetar por angulo aureo desde el suyo. Ninguno se organiza
desde su limbo. Este si.

Pero un campo que decrece con el radio es un halo -el material de la
Estrella- y ademas leeria como vineta. La escarcha de verdad no es uniforme:
NUCLEA. Se agarra en unos pocos puntos y crece en lenguas desde cada uno.
Aqui son CINCO nucleos, con angulos y radios deliberadamente desiguales
-cualquier reparto regular devuelve simetria radial n-fold, que es la firma
de la Estrella- y cada uno con un campo ALARGADO HACIA EL CENTRO, no
redondo: una mancha redonda es vaho, una lengua tiene direccion.

LOS NUCLEOS VAN EN EL CUERPO, NO EN EL LIMBO. La primera version los ponia a
radio 25-29, que es donde el frio «llega» si uno se cree el relato. Medido,
ahi no hay nodo: el cuerpo del Magnetar tiene radio 15-18 y el de la Estrella
N1, 20.7, asi que la escarcha flotaba en el vacio alrededor de cinco de los
trece y encima caia justo sobre las esquirlas, que son el contador de nivel.
A radio 19-23 se agarra a los trece. El relato sobrevive igual -las lenguas
siguen creciendo hacia dentro-, pero se agarra a algo.

LAS AGUJAS SON LOS «CRISTALES DE HIELO» QUE PIDE 14.1, y no van tramadas: lo
que se trama es el RELLENO, no el trazo -misma distincion que hizo A.3.1 con
el `zzz`-. Van con `veta_luz` y no con `veta`, o sea sin contorno: sobre un
sprite ya dibujado el contorno no separa, tacha. Y van CORTAS, de 4 a 7 px.
Con 9-13 se leian como puas, y una pua blanca alrededor de un Magnetar es
indistinguible de una esquirla mas: el overlay le estaba sumando niveles al
nodo que no tiene.

LA VENTANA DE LA CARA. Medida sobre los trece sprites, la union de los ojos
ocupa `x 35-60, y 37-49`. La densidad se anula ahi dentro con un borde
IRREGULAR por armonicos: con un ovalo limpio el nodo parece llevar antifaz;
irregular, se lee como que la escarcha aun no ha llegado a la cara, que es
tambien lo que pasa en un cristal de verdad.

LO QUE ESTA PROPUESTA PAGA. Nuclear en el limbo es nuclear exactamente donde
los tres nodos guardan su contador de nivel: la corona de la Estrella, los
frentes del Pulsar, las esquirlas del Magnetar. Es la unica de las tres que
paga ahi, y por eso el generador lo mide y falla si un satelite pierde mas de
la mitad de sus pixeles, en vez de darlo por bueno.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import (a_rgba, dir_estado, lienzo, rampa, tramar, veta_luz)
from nova_estados import CONGELABLES, verifica_tinte

ESTADO = 'frozen'
VERSION = 1
FRAMES = 1          # `Congelado` detiene el idle por definicion (14.1)
CELDA = 96
C = CELDA / 2.0

# --- La ventana de la cara -------------------------------------------------
# Union de los ojos en los 13 congelables: x 35-60, y 37-49. Centro (47.5,43),
# semiejes 12.5 x 6. Mas 2 px de respeto y un borde irregular.
CARA = (47.5, 43.0, 15.0, 9.5)
CARA_ARM = ((3, 0.13, 0.7), (5, 0.07, 2.1))   # (k, amplitud, fase)
CARA_SUAVE = 0.30                             # anchura del desvanecido

# --- Los cinco nucleos -----------------------------------------------------
# (angulo en grados, radio, largo de la lengua, semiancho, gamma, agujas)
# Angulos y radios desiguales a proposito: un reparto regular devuelve
# simetria radial n-fold, que es de la Estrella.
NUCLEOS = (
    (205.0, 21.0, 17.0, 10.0, 1.25, ((6.5, -7.0), (4.5, 11.0))),
    (158.0, 23.0, 15.0,  8.5, 1.35, ((5.5,  6.0),)),
    ( 96.0, 19.0, 18.0, 11.0, 1.20, ((7.0, -5.0), (5.0, 9.0))),
    ( 21.0, 22.0, 14.0,  9.0, 1.40, ((5.0, -8.0),)),
    (301.0, 20.0, 16.0,  9.5, 1.30, ((6.0,  7.0), (4.0, -9.5))),
)


def _malla():
    y, x = np.mgrid[0:CELDA, 0:CELDA]
    return x + 0.5, y + 0.5


def ventana(x, y):
    """1 fuera de la cara, 0 dentro. El borde va rizado, no liso."""
    cx, cy, rx, ry = CARA
    a = np.arctan2(y - cy, x - cx)
    k = 1.0 + sum(amp * np.cos(n * a + f) for n, amp, f in CARA_ARM)
    d = np.hypot((x - cx) / (rx * k), (y - cy) / (ry * k))
    return np.clip((d - 1.0) / CARA_SUAVE, 0.0, 1.0)


def campo(x, y):
    """La densidad de escarcha: el maximo de las cinco lenguas."""
    dens = np.zeros_like(x)
    for ang, rad, largo, ancho, gamma, _ in NUCLEOS:
        a = np.radians(ang)
        nx, ny = C + rad * np.cos(a), C - rad * np.sin(a)
        # eje mayor apuntando al centro de la celda: la lengua crece hacia
        # dentro, no en redondo.
        ux, uy = (C - nx), (C - ny)
        n = np.hypot(ux, uy) or 1.0
        ux, uy = ux / n, uy / n
        dx, dy = x - nx, y - ny
        u = dx * ux + dy * uy          # a lo largo de la lengua
        v = -dx * uy + dy * ux         # a lo ancho
        # semieje largo hacia dentro, corto hacia fuera: la lengua crece
        # hacia el nodo y apenas rebasa su propio nucleo.
        ue = np.where(u >= 0, u / largo, u / (largo * 0.22))
        e = np.hypot(ue, v / ancho)
        dens = np.maximum(dens, np.clip(1.0 - e, 0.0, 1.0) ** gamma)
    return dens


def frozen(t=0.0):
    """El overlay. Un solo frame: `Congelado` detiene el idle (14.1)."""
    lz = lienzo(CELDA)
    ramp = rampa('hielo')
    x, y = _malla()
    w = ventana(x, y)

    tramar(lz, campo(x, y) * w, ramp, banda_int=2, banda_ext=4, corte=0.50)

    # Las agujas: solidas y con contorno. Lo que se trama es el relleno, no
    # el trazo (ver la cabecera).
    for (ang, rad, _, _, _, agujas) in NUCLEOS:
        a = np.radians(ang)
        nx, ny = C + rad * np.cos(a), C - rad * np.sin(a)
        ux, uy = (C - nx), (C - ny)
        n = np.hypot(ux, uy) or 1.0
        ux, uy = ux / n, uy / n
        for j, (largo, desvio) in enumerate(agujas):
            b = np.radians(desvio)
            vx = ux * np.cos(b) - uy * np.sin(b)
            vy = ux * np.sin(b) + uy * np.cos(b)
            p1 = (nx + vx * largo, ny + vy * largo)
            # una aguja que entra en la ventana de la cara se recorta
            if ventana(np.array([[p1[0]]]), np.array([[p1[1]]]))[0, 0] < 1.0:
                for k in np.linspace(1.0, 0.0, 24):
                    q = (nx + vx * largo * k, ny + vy * largo * k)
                    if ventana(np.array([[q[0]]]), np.array([[q[1]]]))[0, 0] >= 1.0:
                        p1 = q
                        break
            veta_luz(lz, (nx, ny), p1, 0.62, ramp, 1 if j == 0 else 2)
    return lz


def main():
    raiz = dir_estado(ESTADO, VERSION)
    Image.fromarray(a_rgba(frozen()), 'RGBA').save(
        os.path.join(raiz, 'state_frozen_overlay.png'))

    print('ART-ST-FROZEN v1 «La escarcha»')
    print(f'  1 archivo de 1 frame, {len(CONGELABLES)} nodos congelables')
    if not verifica_tinte(frozen, FRAMES):
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
