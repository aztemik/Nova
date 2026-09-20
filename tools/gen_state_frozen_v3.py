"""NOVA - Overlay de estado `Congelado` (ART-ST-FROZEN), v3: EL VIDRIO.

Ref: NOVA_Estados_Animaciones.md 14.1, 14.6 y 14.7 - NOVA_Assets_Diseno.md A.3

LA TESIS: EL HIELO NO ES UNA CAPA, ES UNA GRIETA. Las otras dos propuestas
anaden material encima del nodo -escarcha que se le echa, un bloque que lo
encierra- y las dos tienen que negociar cuanto tapan. Esta no anade
material: ROMPE. Una red de grietas de un pixel dice «solido y quebradizo»
-que es lo que 7.3 describe: un cuerpo inerte que solo puede recibir
impactos- y no tapa practicamente nada, porque una linea no tiene area.

Es la propuesta mas barata de las tres en lectura: deja el contador de nivel
entero y la cara casi entera, y lo hace sin renunciar a nada, porque la
informacion que aporta no compite por el mismo sitio que la del sprite. Una
grieta CRUZA; un tinte CUBRE.

LA CARA: NO LA ESQUIVA, LA ENHEBRA. Las otras dos le abren hueco -v1 le deja
una ventana, v2 le pone un cristal delante-. Esta pasa por el medio, y puede
porque la geometria lo permite y esta medida: en los trece congelables el
ojo izquierdo termina como muy tarde en `x 45` y el derecho empieza como muy
pronto en `x 49`. Hay un PASILLO DE 4 PX entre los dos ojos que existe en los
trece, y el tronco de la grieta baja por ahi. No es un hueco que haya que
respetar: es el unico sitio por el que una grieta puede cruzar la cara sin
tocarla, y cruzarla es justo lo que la hace leer como grieta y no como
adorno pegado al lado.

DE DONDE SALE LA TRAMA. 14.1 pide los cristales «por trama» y aqui la trama
no es un campo con forma propia: es una FUNCION DE LA DISTANCIA A LA RED.
La escarcha florece desde la grieta hacia fuera y se apaga en 4 px. Asi el
overlay tiene una sola fuente de forma -la red- en vez de dos, y por el
pasillo de la cara el florecimiento cabe entero sin desbordarse a los ojos.

SIN SIMETRIA Y SIN CENTRO. La red no se organiza alrededor de nada: no tiene
centro, no tiene eje y no se repite. Es el unico principio de composicion
que le queda libre a un overlay que va sobre los tres nodos, porque
cualquier otro -radial, bilateral, hexagonal- choca con la firma de alguno
de ellos (A.8, *Ejes de diseno ya ocupados*). Un copo de nieve de seis
puntas habria sido lo obvio y habria sido lo peor: simetria radial n-fold
centrada es exactamente la Estrella.

LAS LINEAS NO LLEVAN CONTORNO. `veta_luz`, no `veta`. Sobre un sprite ya
dibujado el contorno no separa, tacha: engorda cada linea de 1 a 3 px y los
2 de mas son negros. Esta propuesta es casi toda linea, asi que es la que
mas lo notaria.

LO QUE ESTA PROPUESTA PAGA, Y ES CARO. Dos cosas, las dos reales:

  1. Puede no decir HIELO. Una red de grietas cianes sobre un nodo tambien
     se lee como «agrietado», y agrietado ya lo dice el Magnetar con sus
     vetas incandescentes. Es el unico sitio de las tres propuestas donde
     hay riesgo de colision con la firma de un nodo, y cae justo sobre el
     nodo con el que colisiona.
  2. Puede no verse. A 1x una red de 1 px sobre un sprite de 30 px es lo
     primero que se pierde, y `Congelado` dura hasta 30 s (7.3): un estado
     largo que no se ve es peor que uno corto que se ve poco. La huella que
     imprime el generador es la medida que hay que mirar antes de elegir
     esta.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import (a_rgba, dir_estado, lienzo, rampa, tramar, veta_luz,
                       _dist_seg)
from nova_estados import CONGELABLES, verifica_tinte

ESTADO = 'frozen'
VERSION = 3
FRAMES = 1          # `Congelado` detiene el idle por definicion (14.1)
CELDA = 96

# --- La red ----------------------------------------------------------------
# El tronco baja por el pasillo entre los ojos. Medido sobre los trece
# congelables: el ojo izquierdo acaba como muy tarde en x 45 y el derecho
# empieza como muy pronto en x 49, asi que entre 45 y 49 hay paso en TODOS.
PASILLO = (45.0, 49.0)

TRONCO = ((47.5, 19.0), (46.0, 31.0), (47.0, 43.0), (46.5, 56.0), (48.5, 74.0))

# Ramas: cada una arranca de un nudo del tronco y se va sin volver. Ningun
# angulo se repite y ninguna pareja es simetrica de otra: la red no tiene eje.
RAMAS = (
    ((46.0, 31.0), (31.0, 24.0), (24.0, 34.0)),
    ((46.0, 31.0), (63.0, 23.0)),
    ((46.5, 56.0), (30.0, 62.0)),
    ((46.5, 56.0), (65.0, 65.0), (72.0, 56.0)),
    ((63.0, 23.0), (68.0, 34.0)),
)

# Astillas sueltas: trozos cortos que no tocan la red. Un vidrio roto tiene
# esquirlas ademas de grietas, y sin ellas la red parece un dibujo.
ASTILLAS = (
    ((33.0, 45.0), (28.0, 41.0)),
    ((61.0, 51.0), (67.0, 47.0)),
)

GROSOR = 0.58
FLOR = 4.2          # hasta donde florece la escarcha desde la grieta
FLOR_MAX = 0.42     # densidad pegada a la linea
FLOR_GAMMA = 1.9


def _segmentos():
    seg = []
    for i in range(len(TRONCO) - 1):
        seg.append((TRONCO[i], TRONCO[i + 1], 1))
    for rama in RAMAS:
        for i in range(len(rama) - 1):
            seg.append((rama[i], rama[i + 1], 2))
    for a, b in ASTILLAS:
        seg.append((a, b, 2))
    return seg


def frozen(t=0.0):
    """El overlay. Un solo frame: `Congelado` detiene el idle (14.1)."""
    lz = lienzo(CELDA)
    ramp = rampa('hielo')
    y, x = np.mgrid[0:CELDA, 0:CELDA]
    px, py = x + 0.5, y + 0.5

    seg = _segmentos()

    # La escarcha florece DESDE la grieta: la densidad es funcion de la
    # distancia a la red, no de un campo con forma propia.
    d = np.full((CELDA, CELDA), 1e9, np.float32)
    for a, b, _ in seg:
        d = np.minimum(d, _dist_seg(px, py, a, b))
    dens = FLOR_MAX * np.clip(1.0 - (d - GROSOR) / FLOR, 0.0, 1.0) ** FLOR_GAMMA
    tramar(lz, dens, ramp, banda_int=3, banda_ext=4, corte=0.26)

    # Las grietas, encima de su propio florecimiento.
    for a, b, banda in seg:
        veta_luz(lz, a, b, GROSOR, ramp, banda)
    return lz


def main():
    raiz = dir_estado(ESTADO, VERSION)
    Image.fromarray(a_rgba(frozen()), 'RGBA').save(
        os.path.join(raiz, 'state_frozen_overlay.png'))

    print('ART-ST-FROZEN v3 «El vidrio»')
    print(f'  1 archivo de 1 frame, {len(CONGELABLES)} nodos congelables')
    print(f'  {len(_segmentos())} segmentos, pasillo de la cara x{PASILLO[0]:.0f}-{PASILLO[1]:.0f}')
    if not verifica_tinte(frozen, FRAMES):
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
