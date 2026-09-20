"""NOVA - Overlay de estado `Dormido` (ART-ST-SLEEP), propuesta v1: LA ESCALERA.

Ref: NOVA_Estados_Animaciones.md 14.1 y 14.7 - NOVA_Assets_Diseno.md A.3

QUE PIDE LA SPEC. 14.1: «`zzz` flotante, gris #8A93A6, balanceo lento»,
permanente, sobre el Asteroide Neutral. A.3: 16 frames en bucle, y el overlay
se dibuja SOBRE un sprite de nodo ya opaco.

NI UN PIXEL DE TRAMA, Y NO ES UNA EXCEPCION. A.3 manda tramar los overlays en
vez de bajar la opacidad, pero esa regla habla de TINTES Y AURAS -Congelado,
Infectado, buff-, que cubren el cuerpo entero y tienen que dejarlo ver. Un
`zzz` no cubre nada: es un GLIFO, vive fuera del cuerpo y compite con el
fondo, no con el nodo. Tramado seria un borron gris. Solido y con contorno se
lee sobre cualquier sprite y sobre cualquiera de los tres fondos, que es lo
que A.3 pide de verdad cuando exige independencia del tipo.

DE QUE ESTA HECHO. Tres `veta` por glifo: barra alta, diagonal, barra baja. No
hace falta primitiva nueva. La Z no es un material que el catalogo no tenga:
es un segmento solido de banda constante repetido tres veces, y eso es
exactamente `veta`. La regla del contrato -si el nodo pide un material que no
existe, se escribe la primitiva- no se dispara aqui, y escribir `glifo_z` en
`nova_core` seria meter tipografia en un catalogo de materia.

EL RECORRIDO SE REPARTE, NO SE ESCRIBE A MANO. Las tres Z ocupan el mismo
camino en tres tramos iguales: la Z `k` va en la fase `(t + k/3) mod 1`. En un
ciclo cada una ocupa el sitio de la siguiente, asi que EL BUCLE CIERRA POR
CONSTRUCCION sea cual sea el numero de frames. Es el mismo mecanismo con el
que el Pulsar v2 resuelve sus frentes de onda, y por el mismo motivo: con
posiciones a mano el avance y el recorrido no son conmensurables y el ciclo
salta al reiniciarse.

NACEN GRANDES Y SE DESHACEN PEQUENAS, al reves que el zzz de comic. Dos
razones, y las dos son de este proyecto y no de gusto:

  1. El alfa es binario. Un glifo no se puede desvanecer, solo desaparecer.
     Si crece mientras sube, lo que desaparece de golpe es el elemento MAS
     GRANDE del overlay y el parpadeo es lo primero que ve el ojo. Menguando,
     lo que se apaga mide 3.9 px de semitamano y el relevo no se nota.
  2. La Z mas legible cae SIEMPRE en el mismo sitio, sobre la roca, que es
     donde el jugador ya esta mirando. La informacion no viaja.

El tono acompana al tamano: banda 3 -#8A93A6 literal, el color que pide
14.1- en la que nace, y sube a banda 2 al deshacerse. Se aclara, no se apaga:
en esta paleta el indice bajo es el tono claro, y sobre el fondo profundo
aclarar es alejar.

EL BALANCEO ES PERPENDICULAR AL RECORRIDO, no horizontal. Horizontal, las tres
Z se mueven a la vez y el grupo entero parece temblar; perpendicular y en
funcion de la fase propia de cada una, la columna ondula como humo y el
balanceo lento de 14.1 sale de la misma variable que ya mueve el glifo.

DONDE CABE, Y NO ES UN AJUSTE A OJO. El sitio no se eligio mirando: se
calculo. Medido sobre el sprite real, el Asteroide Neutral ocupa y 29-67,
x 26-68 de la celda de 96, asi que el overlay tiene libre la franja de encima
(y < 29) y la columna de la derecha (x > 68), y nada mas.

El primer reparto de este generador ponia el `zzz` pegado al hombro derecho,
en un recorrido corto de (64, 37) a (85, 9). Dos fallos, los dos medidos y
ninguno visible en un boceto: 152 px de glifo caian sobre la roca, y -peor- un
camino de 21 px repartido en tres deja 7 px entre Z para glifos de 12 px de
ancho, asi que las tres se solapaban y el `zzz` se leia como una marana.

LA SEPARACION ES LA QUE MANDA EN ESTE ASSET. Tres glifos que se tocan no se
cuentan, y un `zzz` que no se cuenta no dice «duerme», dice «hay algo gris
ahi». Con Z de 5.0 a 3.9 de semitamano hacen falta ~17 px entre estaciones, o
sea unos 50 px de recorrido, y el unico sitio de la celda donde caben es
cruzando la franja de arriba. De ahi sale (38, 22) -> (86, 10): el aliento
sube por encima de la roca y se va hacia la derecha.

VERIFICADO sobre los 16 frames, contra el sprite de verdad y no contra una
suposicion: cero pixeles sobre el cuerpo, ningun frame toca el borde de la
celda, las tres Z estan siempre separadas por al menos un pixel y el bucle
cierra pixel a pixel.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, dir_estado, lienzo, rampa, veta
from nova_estados import verifica

ESTADO = 'sleep'
VERSION = 1
FRAMES = 16         # bucle sin duracion fija: 16 frames (contrato, Animacion)
CELDA = 96

N_Z = 3             # las tres del `zzz` de 14.1. Ni dos ni cuatro.

# Recorrido, en pixeles de celda. Derivado de la silueta real del Asteroide
# Neutral y de la separacion minima entre glifos: ver el docstring.
P0 = (38.0, 22.0)   # nace sobre la roca, en la franja libre de arriba
P1 = (86.0, 10.0)   # se deshace saliendo por la derecha

S0, S1 = 5.0, 3.9   # semitamano al nacer y al deshacerse. 3.8 es el suelo
                    # medido: por debajo, a 1x la Z es una mancha, no una Z.
B0, B1 = 3, 2       # banda al nacer (#8A93A6, literal de 14.1) y al morir
U_BANDA = 0.55      # a partir de aqui se aclara

ANG0, ANG1 = -8.0, -22.0    # se va tumbando al alejarse: sube y se afloja
VAIVEN = 1.6        # amplitud del balanceo, perpendicular al recorrido
VAIVEN_N = 1.0      # una ondulacion por recorrido. Con dos, tiembla.

GROSOR = 0.30       # del semitamano. Mas fino no sobrevive al contorno.
ALTO = 1.05         # la Z es un pelo mas alta que ancha, como en imprenta


def _z(lz, cx, cy, s, ang, ramp, banda, oid):
    """Un glifo Z: barra alta, diagonal, barra baja. Tres `veta` y ya."""
    g = max(0.95, s * GROSOR)
    w, h = s, s * ALTO
    co, si = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def r(x, y):
        return (cx + x * co - y * si, cy + x * si + y * co)

    a, b, c, d = r(-w, -h), r(w, -h), r(-w, h), r(w, h)
    for k, (p, q) in enumerate(((a, b), (b, c), (c, d))):
        veta(lz, p, q, g, ramp, banda, oid + k, solo_dentro=False)


def sleep(t=0.0):
    """Devuelve el lienzo del overlay en la fase `t` de [0, 1)."""
    ramp = rampa('neutral')
    lz = lienzo(CELDA)

    dx, dy = P1[0] - P0[0], P1[1] - P0[1]
    largo = math.hypot(dx, dy)
    nx, ny = -dy / largo, dx / largo      # normal al recorrido

    # De la mas vieja a la mas joven: la joven se dibuja encima, porque es la
    # que esta mas cerca del que respira.
    for k in range(N_Z - 1, -1, -1):
        u = (t + k / N_Z) % 1.0
        s = S0 + (S1 - S0) * u
        vai = VAIVEN * math.sin(2 * math.pi * VAIVEN_N * u)
        cx = P0[0] + dx * u + nx * vai
        cy = P0[1] + dy * u + ny * vai
        banda = B0 if u < U_BANDA else B1
        _z(lz, cx, cy, s, ANG0 + (ANG1 - ANG0) * u, ramp, banda, oid=10 + k * 4)

    return lz


def hoja():
    """Tira horizontal de FRAMES celdas: 1536x96 (contrato, Resolucion)."""
    return np.hstack([a_rgba(sleep(i / FRAMES)) for i in range(FRAMES)])


def _piezas(t):
    """Las tres Z por separado, para medir que no se toquen entre ellas."""
    ramp = rampa('neutral')
    dx, dy = P1[0] - P0[0], P1[1] - P0[1]
    largo = math.hypot(dx, dy)
    nx, ny = -dy / largo, dx / largo
    out = []
    for k in range(N_Z):
        u = (t + k / N_Z) % 1.0
        s = S0 + (S1 - S0) * u
        vai = VAIVEN * math.sin(2 * math.pi * VAIVEN_N * u)
        lz = lienzo(CELDA)
        _z(lz, P0[0] + dx * u + nx * vai, P0[1] + dy * u + ny * vai, s,
           ANG0 + (ANG1 - ANG0) * u, ramp, B0, oid=10)
        out.append(a_rgba(lz)[..., 3] > 0)
    return out


def main():
    raiz = dir_estado(ESTADO, VERSION)
    Image.fromarray(hoja(), 'RGBA').save(
        os.path.join(raiz, 'state_sleep_sheet.png'))
    # el estatico es el frame 0, para hojas de contacto y documentacion
    Image.fromarray(a_rgba(sleep(0.0)), 'RGBA').save(
        os.path.join(raiz, 'state_sleep.png'))
    print('ART-ST-SLEEP v1 «La escalera»')
    verifica(sleep, FRAMES, _piezas)


if __name__ == '__main__':
    main()
