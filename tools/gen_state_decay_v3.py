"""NOVA - Overlay de estado `Infectado` (ART-ST-DECAY), v3: EL ENJAMBRE.

Ref: NOVA_Estados_Animaciones.md 14.1, 14.6 y 14.7 - NOVA_Assets_Diseno.md A.3

LA TESIS: NI COSTRA NI NUBE. PARTICULAS, Y NADA MAS. Las otras dos
propuestas dibujan un CAMPO CONTINUO y le cuelgan unas gotas; esta no tiene
campo. Es un enjambre de trece motas que van cayendo alrededor del nodo,
cada una por su carril y con su fase, y el «aura pulsante» de 14.1 es la
densidad del enjambre, que sube y baja en un ciclo.

POR QUE ESE EJE ESTA LIBRE, Y POR QUE IMPORTA. Los cuatro overlays cerrados
de A.3 son campos o trazos: tres glifos solidos, un abanico de cinco trazos,
un ojo, y un prisma de facetas tramadas. **Nada en A.3 esta hecho de muchas
piezas pequenas iguales**, y esa es la unica forma de decir «esto se esta
desintegrando» sin dibujar un aura, que es el registro que ya ocupa
`Congelado`. 14.6 los hace convivir, asi que no es un lujo: hay partidas en
las que se ven los dos sobre el mismo nodo, y si los dos son una nube
tramada alrededor del cuerpo, a 1x son una sola mancha.

RESUELVE EL PROBLEMA DEL CUERPO NO RESOLVIENDOLO. Medido, la interseccion de
los trece cuerpos son 505 px y la caja de la cara se come casi todo: quedan
228 px, 195 de ellos debajo de la cara. Un tinte que quiera apoyarse en el
cuerpo tiene esa franja y poco mas. Una mota no necesita cuerpo: vive en el
aire, y el aire lo hay alrededor de los trece por igual.

LOS CARRILES ESQUIVAN LA CARA POR GEOMETRIA, NO POR MASCARA. Ningun carril
cruza la caja `x 35-60, y 37-49`: los que caen por el centro arrancan ya por
debajo de ella, los que arrancan arriba van por fuera en x, y el unico que la
atraviesa entera baja por el PASILLO DE 4 PX que hay entre los dos ojos en
los trece (`x 45-49`). Asi ninguna mota tiene que apagarse a mitad de vuelo
para respetar los ojos, que con alfa binario seria apagarse de golpe.

CADA MOTA ES TRAMA, NO UN PUNTO SOLIDO. Nucleo denso y borde dithered: a
1.5-2.2 px de radio, un disco solido es un pixel suelto -que fue una de las
cuatro formas descartadas en A.3.2- y con el borde tramado la mota tiene
tamano sin tener peso. Sigue cumpliendo 14.1, que pide el verde por trama.

EL CICLO CIERRA POR CONSTRUCCION. Cada mota recorre su carril en un ciclo
completo y reaparece arriba; las fases van repartidas en trece tramos
iguales. No hay posiciones escritas a mano, asi que el bucle cierra sea cual
sea el numero de frames.

LO QUE ESTA PROPUESTA PAGA. Una mota verde de 3 px cerca de un Magnetar se
parece a una esquirla, y las esquirlas son el contador de nivel de ese nodo
(A.2.4) y ya cuestan de contar a 1x. Aqui hay trece motas moviendose. Es
exactamente el riesgo por el que se acortaron las agujas de
`ART-ST-FROZEN` v1, y esta propuesta no lo puede acortar: las motas son el
asset entero.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, dir_estado, lienzo, rampa, tramar
from nova_estados import CONGELABLES, verifica_tinte

ESTADO = 'decay'
VERSION = 3
FRAMES = 16
CELDA = 96

CARA = (35, 60, 37, 49)     # x0, x1, y0, y1: union de los ojos en los trece
PASILLO = (45.0, 49.0)      # hueco entre los dos ojos, en los trece

# (x de salida, y de salida, recorrido, deriva en x, radio)
#
#   - por el pasillo de la cara: uno solo, y cabe entero
#   - por el centro, arrancando ya debajo de la cara
#   - por los lados, fuera de la caja en x
#
# Dos carriles del centro llevan una deriva grande (13.5 y -18 px) y no es
# adorno: caian rectos sobre la esquirla que el Magnetar tiene en
# `x 49-56, y 69-80` -la que aparece a partir de N2- y se llevaban el 56 %
# de sus 64 px. Una mota que ademas se desplaza de lado mientras cae se lee
# igual de bien y esquiva la unica pieza de contador que hay ahi abajo.
CARRILES = (
    (46.5, 28.0, 58.0,  0.8, 1.5),
    (38.0, 52.0, 34.0,  1.4, 2.0),
    (42.0, 56.0, 30.0, -0.9, 1.7),
    (50.5, 52.0, 35.0, 13.5, 2.1),
    (54.5, 55.0, 32.0,-18.0, 1.6),
    (58.0, 52.0, 33.0,  0.9, 1.9),
    (47.0, 60.0, 28.0, -0.6, 2.0),
    (31.0, 30.0, 52.0,  1.8, 1.8),
    (27.5, 42.0, 44.0,  1.0, 1.4),
    (64.0, 32.0, 50.0, -1.6, 1.9),
    (68.0, 44.0, 42.0, -1.1, 1.5),
    (33.5, 58.0, 28.0, -0.8, 1.6),
    (62.5, 60.0, 26.0,  1.3, 1.7),
)

PULSO = 0.22        # cuanto respira la densidad del enjambre en un ciclo
GAMMA = 0.65        # nucleo denso, borde que se deshace


def _comprueba_carriles():
    """Ningun carril cruza la cara salvo por el pasillo, y ninguno toca el borde."""
    x0, x1, y0, y1 = CARA
    for (cx, cy, rec, der, r) in CARRILES:
        ax, bx = min(cx, cx + der) - r, max(cx, cx + der) + r
        assert 1.0 < ax and bx < CELDA - 1.0, f'carril {cx},{cy} se sale en x'
        assert cy - r > 1.0 and cy + rec + r < CELDA - 1.0, \
            f'carril {cx},{cy} se sale en y'
        cruza_y = not (cy + rec + r < y0 or cy - r > y1)
        cruza_x = not (bx < x0 or ax > x1)
        if cruza_y and cruza_x:
            assert PASILLO[0] <= ax and bx <= PASILLO[1], \
                f'el carril {cx},{cy} pisa la cara fuera del pasillo'


def decay(t=0.0):
    """El overlay en la fase `t`. 16 frames, bucle."""
    lz = lienzo(CELDA)
    ramp = rampa('decaimiento')
    y, x = np.mgrid[0:CELDA, 0:CELDA]
    px, py = x + 0.5, y + 0.5

    n = len(CARRILES)
    pulso = 1.0 + PULSO * np.sin(2 * np.pi * t)
    for i, (cx, cy, rec, der, r) in enumerate(CARRILES):
        u = (t + i / n) % 1.0
        mx, my = cx + der * u, cy + rec * u
        rr = max(0.9, r - 0.45 * u)
        d = np.hypot(px - mx, py - my)
        dens = np.clip(1.0 - d / rr, 0.0, 1.0) ** GAMMA * pulso
        banda = 2 if u < 0.28 else (3 if u < 0.58 else (4 if u < 0.82 else 5))
        tramar(lz, dens, ramp, banda_int=banda, banda_ext=min(banda + 1, 6),
               corte=0.62)
    return lz


def main():
    _comprueba_carriles()
    raiz = dir_estado(ESTADO, VERSION)
    frames = [a_rgba(decay(i / FRAMES)) for i in range(FRAMES)]
    Image.fromarray(np.hstack(frames), 'RGBA').save(
        os.path.join(raiz, 'state_decay_sheet.png'))
    Image.fromarray(frames[0], 'RGBA').save(
        os.path.join(raiz, 'state_decay.png'))

    print('ART-ST-DECAY v3 «El enjambre»')
    print(f'  hoja de {FRAMES} frames {CELDA * FRAMES}x{CELDA}, '
          f'{len(CARRILES)} motas, {len(CONGELABLES)} nodos infectables')
    if not verifica_tinte(decay, FRAMES,
                          convive_con='states/frozen/v2/state_frozen_overlay.png'):
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
