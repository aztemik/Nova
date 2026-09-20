"""NOVA - Overlay de estado `Infectado` (ART-ST-DECAY), v1: EL GOTEO.

Ref: NOVA_Estados_Animaciones.md 14.1, 14.6 y 14.7 - NOVA_Assets_Diseno.md A.3

LA TESIS: LA INFECCION NO SE VE, SE VE LO QUE SE ESTA CAYENDO. 7.4 no dice
que el nodo este enfermo: dice que pierde 2 de Energia por segundo, solo, y
que mientras tanto SIGUE FUNCIONANDO -la Estrella genera, el Magnetar
dispara, el Pulsar carga-. No es un nodo apagado como el congelado: es un
nodo intacto con un agujero. Asi que esta propuesta no le pone un aura
encima: le pone una FUGA debajo, y el aura que pide 14.1 es el caudal.

Es ademas lo unico que separa de verdad a `Infectado` de `Congelado` sin
depender del color. Los dos son trama; si los dos son ademas una nube
alrededor del cuerpo, a 1x son la misma mancha en otro tono, y 14.6 los hace
CONVIVIR: hay partidas en las que el jugador ve los dos a la vez sobre el
mismo nodo. Uno tiene que ser cerrado y quieto y el otro abierto y en
movimiento.

LA MEDIDA QUE MANDA EN ESTE ASSET. `Infectado` va sobre los mismos trece
nodos encendidos que `Congelado`, y la interseccion de los trece cuerpos es
mucho mas pequena de lo que parece:

    El cuerpo comun a los trece son 505 px, un bulto de radio <= 19.9 en
    `x 36-60, y 30-60`. La caja de la cara -`x 35-60, y 37-49`, la union de
    los ojos- se come la mayor parte: quedan 228 px, y 195 de esos 228 estan
    DEBAJO de la cara. Encima de la cara quedan 33.

O sea: «pintar sobre el cuerpo» y «pintar en los trece» solo son compatibles
en una franja estrecha justo debajo de la cara. Eso no es una limitacion de
esta propuesta, es el terreno; las tres la tienen. Esta es la que la asume en
vez de pelearse con ella: la costra vive en la franja y todo lo demas cae
por fuera del cuerpo, donde no hay nada que respetar.

EL CICLO NO CUENTA UNA HISTORIA. `Infectado` es indefinido y no avanza hacia
ningun sitio -se quita curandolo o capturandolo (7.4)-, asi que las gotas no
«terminan»: se reparten el recorrido en N tramos iguales y en un ciclo cada
una ocupa el sitio de la siguiente. El bucle cierra por construccion, sea
cual sea el numero de frames, que es la regla del contrato y el mismo
mecanismo que cierra los frentes de onda del Pulsar.

UNA GOTA SE APAGA, NO SE DESVANECE. Con alfa binario no hay medio camino: al
caer, la gota BAJA DE BANDA -de la 2 a la 5 de la rampa `decaimiento`- y
encoge un pixel. Desvanecerla seria apagarla de golpe, que es el defecto por
el que perdio la v1 de `ART-ST-SLEEP`.

NI LA COSTRA NI LAS GOTAS LLEVAN CONTORNO. Se dibujan encima de un sprite ya
terminado, y ahi el contorno no separa: tacha (contrato, *Lo que se dibuja
encima de otro dibujo no lleva contorno*). Las gotas son `veta_luz` con los
dos extremos en el mismo punto, que es un disco sin contorno.

LO QUE ESTA PROPUESTA PAGA. 14.1 pide literalmente «aura verde pulsante», y
aqui no hay aura: hay una costra y un goteo. La defensa es que el pulso esta
-en el caudal y en la costra, que late- y que un aura alrededor del cuerpo
es justo lo que ya ocupa `Congelado`. Pero es una reinterpretacion del texto,
no una lectura, y conviene que este escrito.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, dir_estado, lienzo, rampa, tramar, veta_luz
from nova_estados import CONGELABLES, verifica_tinte

ESTADO = 'decay'
VERSION = 1
FRAMES = 16         # bucle sin duracion fija (contrato, Animacion)
CELDA = 96

# --- La franja comun -------------------------------------------------------
# Medido sobre los trece: el cuerpo que comparten los trece y que no es cara
# vive en `y 50-60`. La costra se centra ahi y se apaga hacia arriba antes de
# llegar a los ojos.
COSTRA_Y = 55.0
COSTRA_ALTO = 6.5
COSTRA_X = 48.0
COSTRA_ANCHO = 13.0
COSTRA_DENS = 0.52
COSTRA_PULSO = 0.22     # cuanto respira la costra en un ciclo
COSTRA_ARM = ((3, 0.22, 1.1), (5, 0.11, 4.3))   # borde irregular

# --- Las gotas -------------------------------------------------------------
# (x de salida, deriva en x a lo largo de la caida, radio inicial)
GOTAS = (
    (38.0, -2.5, 1.45),
    (43.5,  1.0, 1.15),
    (47.0, -0.5, 1.60),
    (51.5,  1.8, 1.25),
    (56.0, -1.2, 1.50),
    (60.5,  2.2, 1.10),
    (35.0,  0.8, 1.30),
)
GOTA_Y0 = 57.0
GOTA_Y1 = 90.0      # el suelo de la celda menos el margen de borde


def _malla():
    y, x = np.mgrid[0:CELDA, 0:CELDA]
    return x + 0.5, y + 0.5


def costra(t):
    """La corteza podrida bajo la cara. Late, no viaja."""
    x, y = _malla()
    dx, dy = x - COSTRA_X, y - COSTRA_Y
    a = np.arctan2(dy, dx)
    k = 1.0 + sum(amp * np.cos(n * a + f) for n, amp, f in COSTRA_ARM)
    e = np.hypot(dx / (COSTRA_ANCHO * k), dy / (COSTRA_ALTO * k))
    pulso = 1.0 + COSTRA_PULSO * np.sin(2 * np.pi * t)
    return np.clip(1.0 - e, 0.0, 1.0) ** 1.15 * COSTRA_DENS * pulso


def decay(t=0.0):
    """El overlay en la fase `t`. 16 frames, bucle."""
    lz = lienzo(CELDA)
    ramp = rampa('decaimiento')

    tramar(lz, costra(t), ramp, banda_int=3, banda_ext=4, corte=0.30)

    # Las gotas: N tramos iguales del mismo recorrido, asi que en un ciclo
    # cada una ocupa el sitio de la siguiente y el bucle cierra solo.
    n = len(GOTAS)
    for i, (gx, deriva, r0) in enumerate(GOTAS):
        u = (t + i / n) % 1.0
        px = gx + deriva * u
        py = GOTA_Y0 + (GOTA_Y1 - GOTA_Y0) * u
        banda = 2 if u < 0.30 else (3 if u < 0.62 else (4 if u < 0.85 else 5))
        veta_luz(lz, (px, py), (px, py), max(0.9, r0 - 0.5 * u), ramp, banda)
    return lz


def main():
    raiz = dir_estado(ESTADO, VERSION)
    frames = [a_rgba(decay(i / FRAMES)) for i in range(FRAMES)]
    Image.fromarray(np.hstack(frames), 'RGBA').save(
        os.path.join(raiz, 'state_decay_sheet.png'))
    Image.fromarray(frames[0], 'RGBA').save(
        os.path.join(raiz, 'state_decay.png'))

    print('ART-ST-DECAY v1 «El goteo»')
    print(f'  hoja de {FRAMES} frames {CELDA * FRAMES}x{CELDA}, '
          f'{len(GOTAS)} gotas, {len(CONGELABLES)} nodos infectables')
    if not verifica_tinte(decay, FRAMES,
                          convive_con='states/frozen/v2/state_frozen_overlay.png'):
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
