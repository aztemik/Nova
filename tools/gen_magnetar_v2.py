"""NOVA - Generador del Magnetar, propuesta v2: LA BOTELLA.

Ref: NOVA_Nodos.md 4.4 · NOVA_Assets_Diseno.md A.2.4
Propuesta alternativa a `gen_magnetar_v1.py`. Las dos conviven hasta elegir.

LA IDEA. Un campo dipolar lo bastante intenso es una BOTELLA MAGNETICA: las
lineas de fuerza se cierran sobre si mismas, se aprietan en los dos polos y
se abren en el ecuador, y lo que entra en ellas no vuelve a salir. Es el
aparato con el que un laboratorio confina plasma, y es literalmente lo que
hace este nodo: retener lo que le pasa cerca. Asi que la v2 no ensena lo que
el Magnetar ya cazo -eso es la v1-: ensena LA TRAMPA, con el bicho dentro.

El nodo es una columna vertical de tres piezas -yugo, nucleo, yugo- envuelta
en la familia de lineas de campo que ella misma genera. El nucleo esta
pellizcado por los polos, encendido, y mira hacia fuera desde dentro de su
propia jaula.

CONTRA LA v1, PIEZA POR PIEZA. Dos propuestas del mismo nodo solo sirven
para elegir si no comparten construccion. Estas no comparten ninguna:

                        Magnetar v1            Magnetar v2
    Silueta             cumulo disperso        cruz: columna + flor de lazos
    Espacio interior    macizo                 CALADO: se ve el fondo dentro
    Simetria            ninguna (aureo)        doble espejo sobre el eje
    Composicion         dispersa, centrifuga   anidada, concentrica
    Cuerpo              poliedro tallado       elipsoide prolato, fundido
    Material            caras planas, aristas  volumen curvo y tubo
    Contador de nivel   esquirlas sueltas      lazos de campo cerrados
    Que cuenta el nodo  lo que ya cazo         la trampa que tiene puesta

EL CALADO ES LO MAS NUEVO QUE HAY AQUI. Ninguna pieza de NOVA tiene hueco:
todas son masas llenas sobre el fondo. Esta tiene agujeros -entre un lazo y
el siguiente se ve el espacio-, y un objeto que encierra vacio se lee como
recinto, no como cuerpo. Para el unico nodo del juego cuyo trabajo es cerrar
un corredor, esa es la lectura exacta.

EL NIVEL SON LAZOS, Y EL DE FUERA MARCA EL ALCANCE. Un lazo por nivel, de
dentro hacia fuera: el lazo `i` tiene el radio ecuatorial que le toca al
radio de alcance del nivel `i+1` de 4.4, comprimido a la celda. Los lazos de
dentro no se mueven nunca, asi que N4 es N3 mas un lazo por fuera: escalera
aditiva, igual que la v1, pero apilada en vez de esparcida. El grosor de
cada lazo baja una banda hacia fuera, que es el campo perdiendo fuerza: el
mas cercano es el mas solido y por ahi empieza la cuenta.

LO QUE MANTIENE DE LA IDENTIDAD DEL NODO. Ni un pixel de `glow`, igual que
la v1: la Estrella es luz continua, el Pulsar luz tramada y el Magnetar es
materia. Su silueta y su hitbox siguen siendo la misma figura.

EL IDLE ES HOJA DE 16 FRAMES, NO TRANSFORM. El contrato reparte el idle asi:
transform para Asteroide y Magnetar, hoja para Estrella y Pulsar, "porque una
corona congelada delata que el sprite es estatico". Ese reparto se decidio
cuando el Magnetar iba a ser una masa lisa, y esta version no lo es: los
lazos son su firma, y un campo congelado delata el sprite exactamente igual
que una corona congelada. El motivo de la regla, aplicado a esta propuesta,
la manda al otro lado del reparto. Ver T.2 #6: si el documento y el diseno
se contradicen, se corrige el documento, no se disimula el diseno.

Se mueven tres cosas, y ninguna es decorativa:

  1. Un realce VIAJA POR CADA LAZO. Es plasma atrapado recorriendo el tubo
     de campo y rebotando entre los dos espejos magneticos de los polos, que
     es literalmente lo que pasa dentro de una botella magnetica. El mismo
     elemento que cuenta el nivel es el que da vida al idle.
  2. Los lazos exteriores van RETRASADOS de fase, asi que el pulso se ve
     propagarse de dentro hacia fuera: el nodo bombea.
  3. La columna respira con el squash and stretch de volumen conservado del
     contrato, `s = 1 + 0.07 sin(2 pi t)`. El campo NO respira con ella: esta
     anclado al dipolo, no a la piel del bicho. Esa desincronia es la que
     hace que el nucleo se lea dentro de la jaula y no pegado a ella.

EL CICLO CIERRA POR CONSTRUCCION. Todo lo que se mueve es funcion de `t` con
periodo 1: la fase de la onda recorre exactamente una vuelta en N frames y la
respiracion es un seno completo. No hay ninguna posicion escrita a mano, asi
que el bucle cierra para cualquier numero de frames. Verificado ademas pixel
a pixel: frame 0 identico a frame N.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import (a_rgba, dir_nodo, esfera, esferoide, guardar, lienzo,
                       linea_dipolar, rampa)

NODO = 'magnetar'
VERSION = 2
IDLE = True
FRAMES = 16         # bucle sin duracion fija: 16 (contrato, Animacion)
FACCIONES = ('neutral', 'player', 'enemy')

CELDA = 96
C = CELDA / 2.0
PPU = 64.0

# Radio de alcance por nivel, en unidades de mundo. Dato de balance (4.4).
RADIO_U = {1: 2.0, 2: 2.4, 3: 2.8, 4: 3.2, 5: 3.6}

# Compresion del radio a radio ecuatorial del lazo. El alcance de verdad lo
# dibuja ART-WLD-RAD-* (A.4.1); aqui solo se conserva el orden del escalon.
LAZO_0 = 26.0
LAZO_K = 9.8
# El lazo crudo de un dipolo mide 2R por 0.77R: 2.6 a 1. Tal cual, el ecuador
# se sale de la celda con el nodo aun bajito. Se escala 0.82 / 1.30 para que
# la familia entera quepa; el orden y los cruces, que es lo que se lee, no
# cambian.
LAZO_ECU = 0.86
LAZO_EJE = 2.15

# La cota de LAZO_0 no es estetica: EL LAZO TIENE QUE CERRARSE POR ENCIMA DE
# LA COLUMNA. Un lazo cuyo vertice queda tapado por el yugo se ve solo por
# los costados, deja de leerse como lazo cerrado y pasa a leerse como dos
# parentesis -y unos parentesis anidados son los frentes de onda del Pulsar,
# que es justo el vecino del que hay que separarse-. El vertice del lazo `i`
# cae a 0.385 * R_i * LAZO_EJE del centro y tiene que superar el alto de
# media columna. Con las medidas de abajo, el lazo mas interior saca 5 px.

EJE = math.radians(-90.0)   # momento magnetico vertical

# El nucleo es PROLATO: mas alto que ancho. No es estilo, es la consecuencia
# de estar pellizcado por los dos polos. Y de paso ninguna otra pieza del
# juego lo es: el Pulsar es achatado por rotacion y la Estrella es redonda.
NUCLEO_RX = 0.72            # rx = ry * NUCLEO_RX

# Yugos polares: dos casquetes achatados que tapan la convergencia de los
# lazos -todas las lineas del dipolo pasan por el centro- y dan masa al N1,
# donde solo hay un lazo. Son los dos polos del iman.
YUGO_RX = 0.60              # en multiplos del ry del nucleo
YUGO_RY = 0.29
YUGO_D  = 0.86              # separacion desde el centro, en ry de nucleo

ONDA_AMP  = 1.4     # banda que gana el realce al pasar. Corta a proposito:
ONDA_N    = 4       # un lazo que se apagase del todo restaria en la cuenta.
                    # Par, para que los dos costados vayan en espejo, y
                    # cuatro y no dos para que nunca queden todos los tramos
                    # brillantes a la vez detras de la columna.
ONDA_DESF = 0.13    # retraso de fase por lazo hacia fuera: el pulso propaga
RESPIRO   = 0.07    # squash and stretch del contrato, volumen conservado

# ry     semieje vertical del nucleo
# calor  el nucleo se enciende con el nivel: mas campo, mas plasma
NIVELES = {
    1: dict(ry=13.2, calor=1.6),
    2: dict(ry=13.9, calor=2.1),
    3: dict(ry=14.6, calor=2.6),
    4: dict(ry=15.3, calor=3.1),
    5: dict(ry=16.0, calor=3.6),
}


def _lazo(i):
    """Radio ecuatorial del lazo `i`, derivado del alcance de 4.4."""
    return LAZO_0 + LAZO_K * (RADIO_U[i + 1] - RADIO_U[1])


def magnetar(nivel, faccion, t=0.0):
    """Devuelve el lienzo de un Magnetar v2. `t` en [0,1) recorre el idle."""
    cfg = NIVELES[nivel]
    ramp = rampa({'player': 'mag_p', 'enemy': 'mag_e'}.get(faccion, 'mag_n'))
    ojo = rampa('ojo')

    lz = lienzo(CELDA)
    # Respiracion de la columna: volumen conservado, alto x s y ancho / raiz
    # de s. Solo afecta al cuerpo; el campo esta anclado al dipolo.
    s = 1.0 + RESPIRO * math.sin(2.0 * math.pi * t)
    ry = cfg['ry'] * s
    rx = cfg['ry'] * NUCLEO_RX / math.sqrt(s)

    # 1. la botella: N lazos cerrados, de dentro hacia fuera. `r_min` recorta
    #    el tramo que converge en el centro; lo tapa el nucleo.
    for i in range(nivel):
        linea_dipolar(lz, C, C, _lazo(i), EJE, ramp, oid=50 + i,
                      g_polo=2.9 - 0.15 * i, g_ecu=1.30 - 0.06 * i,
                      r_min=rx * 0.50, sesgo_banda=min(i, 2),
                      k_eje=LAZO_EJE, k_ecu=LAZO_ECU,
                      onda_amp=ONDA_AMP, onda_n=ONDA_N,
                      onda_fase=t - ONDA_DESF * i)

    # 2. nucleo prolato y encendido. Va por delante de los lazos: el bicho
    #    esta DENTRO de la botella, no detras de ella.
    esferoide(lz, C, C, rx, ry, 0.0, ramp, oid=10, calor=cfg['calor'])

    # 3. yugos polares por encima del nucleo: lo pellizcan. Por debajo se
    #    leerian como dos lunas y el nodo dejaria de ser una sola pieza.
    for signo in (-1, 1):
        esferoide(lz, C, C + signo * ry * YUGO_D, ry * YUGO_RX, ry * YUGO_RY,
                  0.0, ramp, oid=20 + signo, apagado=0.6)

    # 4. ojos, los ultimos por encima de todo (14.7)
    ro = max(3.0, ry * 0.285)
    sep = rx * 0.54
    for signo in (-1, 1):
        esfera(lz, C + sep * signo, C - ry * 0.10, ro, ojo, oid=30 + signo)

    return lz


def hoja(nivel, faccion):
    """Tira horizontal de FRAMES celdas: ancho = celda x n_frames (contrato)."""
    return np.hstack([a_rgba(magnetar(nivel, faccion, t=i / FRAMES))
                      for i in range(FRAMES)])


def main():
    raiz = dir_nodo(NODO, VERSION)
    for nivel in NIVELES:
        for fac in FACCIONES:
            # el estatico es el frame 0, para UI y hojas de contacto
            guardar(magnetar(nivel, fac),
                    os.path.join(raiz, f'mag_lvl{nivel}_{fac}.png'))
            Image.fromarray(hoja(nivel, fac), 'RGBA').save(
                os.path.join(raiz, f'mag_lvl{nivel}_{fac}_sheet.png'))

    def _ext(m):
        ys, xs = np.where(m)
        return max(ys.max() - ys.min(), xs.max() - xs.min()) + 1

    # LA HUELLA SE MIDE SOBRE EL CICLO ENTERO, no sobre el frame 0: la
    # columna respira, y el maximo no tiene por que caer en el estatico.
    print(f"{'':4} {'frame 0':>9} {'ciclo':>9}   (sin glow: solida = total)")
    for nivel in NIVELES:
        peor = 0
        for i in range(FRAMES):
            lz = magnetar(nivel, 'player', t=i / FRAMES)
            a = a_rgba(lz)[..., 3] > 0
            if lz['glow'].any():
                print(f'  AVISO: N{nivel} f{i} ha ensuciado la capa glow')
            if a[0, :].any() or a[-1, :].any() or a[:, 0].any() or a[:, -1].any():
                print(f'  AVISO: N{nivel} f{i} toca el borde de la celda')
            peor = max(peor, _ext(a))
            if i == 0:
                cero = _ext(a)
        cierra = np.array_equal(a_rgba(magnetar(nivel, 'player', 0.0)),
                                a_rgba(magnetar(nivel, 'player', 1.0)))
        if not cierra:
            print(f'  AVISO: N{nivel} el bucle no cierra')
        print(f'N{nivel}: {cero / PPU:8.2f}u {peor / PPU:8.2f}u')


if __name__ == '__main__':
    main()
