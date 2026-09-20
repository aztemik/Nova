"""NOVA - Overlay de estado `FX-BUFF` (ART-ST-BUFF), v2: EL TEMBLOR.

Ref: NOVA_Estados_Animaciones.md 14.5 y 14.7 - NOVA_GameDesign_Spec.md 9 -
NOVA_Assets_Diseno.md A.3

LA TESIS: UN BUFF NO ES UN ADORNO, ES UN TEMPO. Los dos power-ups hacen lo
mismo en el fondo: **+50 % de ritmo**. El Rayo sube la cadencia del Magnetar
y la carga del Pulsar; el Hidrogeno acorta el intervalo de la Estrella (9.2).
No dan potencia, no dan alcance, no dan resistencia: dan velocidad. El
dibujo universal de la velocidad son las lineas de movimiento, y aqui lo son
literalmente: seis trazos horizontales que flanquean el nodo y corren.

HORIZONTAL, QUE ES EL EJE QUE QUEDABA. La tabla de ejes de A.8 tiene los
otros tres cogidos: la Estrella es isotropa, el Pulsar se ordena sobre una
diagonal de 32 grados y el Magnetar sobre un eje vertical. **Ningun nodo y
ningun overlay usa el eje horizontal**, y un trazo horizontal no se confunde
con nada de lo que hay en pantalla. Ademas es el eje en el que el ojo lee
velocidad: nadie dibuja las lineas de un coche en vertical.

Y NO ES UN ANILLO, QUE ES LO QUE NO PODIA SER. A.4.3 tiene adjudicados dos
anillos alrededor del nodo -`ART-WLD-SEL` para la seleccion y
`ART-WLD-RANGE` para el alcance del poder- y un nodo propio puede estar
seleccionado y buffeado a la vez. Un tercer aro concentrico seria ilegible.

NO VA SOBRE LOS CATORCE. 9.1 aplica el efecto a toda la faccion, pero 9.2
dice a que: Rayo a Magnetar y Pulsar, Hidrogeno a Estrella. El Asteroide no
gana nada con ninguno -no dispara, no carga, no genera- y marcarlo seria
prometerle una ventaja que no tiene (A.2.1). De ahi sale gratis que **ningun
nodo pueda llevar los dos buffs**, aunque 9.1 permita que los dos esten
activos: el overlay nunca se apila consigo mismo.

EL CICLO ES EL CANAL, Y AQUI SI CABE. `ART-ST-SCARE` se quedo en un frame
porque a 6x8 px la rejilla se come el movimiento, y la marca de esquina de
la v1 se queda en 7 frames distintos de 16 por lo mismo. Un trazo que
recorre 14 px da los 16 sin esfuerzo: los trazos viajan hacia fuera, se
reparten el recorrido en tramos iguales y el bucle cierra por construccion,
que es el mismo mecanismo que cierra los frentes de onda del Pulsar.

    Los seis no van en fila ni emparejados en espejo. Tres a cada lado, a
    alturas distintas y con largos distintos: en espejo se leerian como un
    marco, y un marco alrededor de un nodo es lo que va a ser la seleccion.

COLOR DEL POWER-UP, NO DE FACCION. A.4.4 decidio lo contrario para el halo
del drop -«el halo no dice que power-up es, eso lo dice el icono»- y aqui no
hay icono: sobre un nodo buffeado no flota nada. Esta marca es lo unico que
puede decir cual de los dos corre, y lleva el `#FFD23F` o el `#FF8FD0`
literales de 14.4 en el indice 3 de su rampa. La faccion la sigue diciendo
el sprite.

LO QUE ESTA PROPUESTA PAGA. Los trazos viven en la franja donde el Magnetar
guarda sus esquirlas, que son su contador de nivel y ya cuestan de contar a
1x (T.7 #14). El generador lo mide y falla si alguna pierde mas de la mitad.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, dir_estado, lienzo, rampa, veta_luz
from nova_estados import BUFEABLES, SPRITE_PROPIO, verifica_tinte

ESTADO = 'buff'
VERSION = 2
FRAMES = 16
CELDA = 96

# (y, x de salida, recorrido, largo). Tres por lado, sin simetria: en espejo
# se leerian como un marco, y el marco va a ser la seleccion (A.4.3).
TRAZOS = (
    (30.0, 26.0, -14.0, 9.0),
    (45.0, 22.0, -13.0, 12.0),
    (61.0, 27.0, -12.0, 8.0),
    (36.0, 70.0,  13.0, 10.0),
    (52.0, 74.0,  14.0, 8.0),
    (66.0, 69.0,  12.0, 11.0),
)
GROSOR = 0.85
BANDAS = (1, 2, 3, 5)       # el trazo se apaga al alejarse, no se desvanece


def buff(t=0.0, power='rayo'):
    """El overlay en la fase `t`. 16 frames, bucle."""
    lz = lienzo(CELDA)
    ramp = rampa(power)
    n = len(TRAZOS)
    for i, (y, x0, rec, largo) in enumerate(TRAZOS):
        u = (t + i / n) % 1.0
        x = x0 + rec * u
        # el trazo encoge y se apaga segun se aleja; con alfa binario no hay
        # medio camino, asi que baja de banda en vez de desvanecerse
        l = largo * (1.0 - 0.45 * u)
        b = BANDAS[min(int(u * len(BANDAS)), len(BANDAS) - 1)]
        d = np.sign(rec)
        veta_luz(lz, (x, y), (x + d * l, y), GROSOR, ramp, b)
    return lz


def main():
    raiz = dir_estado(ESTADO, VERSION)
    ok = True
    for power in ('rayo', 'hidrogeno'):
        frames = [a_rgba(buff(i / FRAMES, power)) for i in range(FRAMES)]
        Image.fromarray(np.hstack(frames), 'RGBA').save(
            os.path.join(raiz, f'state_buff_{power}_sheet.png'))
        Image.fromarray(frames[0], 'RGBA').save(
            os.path.join(raiz, f'state_buff_{power}.png'))

    print('ART-ST-BUFF v2 «El temblor»')
    print(f'  2 hojas de {FRAMES} frames {CELDA * FRAMES}x{CELDA}, '
          f'{len(TRAZOS)} trazos, una por power-up')
    for power in ('rayo', 'hidrogeno'):
        print(f'  --- {power}: {len(BUFEABLES[power])} nodos ---')
        ok &= verifica_tinte(buff, FRAMES, nodos=BUFEABLES[power],
                             sprite=SPRITE_PROPIO, args=(power,))
    if not ok:
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
