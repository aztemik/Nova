"""NOVA - Overlay de estado `FX-BUFF` (ART-ST-BUFF), v1: EL GALON.

Ref: NOVA_Estados_Animaciones.md 14.5 y 14.7 - NOVA_GameDesign_Spec.md 9 -
NOVA_Assets_Diseno.md A.3

EL ULTIMO DE A.3 Y EL MAS RARO DE LOS NUEVE. Los otros ocho se aplican a UN
nodo; este se aplica a **todos los de una faccion a la vez** durante 20 s
(9.1). Es el unico que va a verse repetido ocho o diez veces en pantalla al
mismo tiempo, que es exactamente la situacion en la que el Asteroide v2 se
cayo por leer como papel pintado (A.2.1).

    Aqui esa repeticion no es un defecto: es la informacion. Alla eran ocho
    rocas identicas y quietas, una textura. Aqui son N nodos marcados a la
    vez y en fase, y lo que dicen juntos es «mi faccion entera esta
    acelerada», que es literalmente lo que ha pasado. La diferencia no es
    cuantos hay, es si repiten una textura o un SUCESO.

NO VA SOBRE LOS CATORCE, Y ESO NO ES UNA LICENCIA. 9.1 dice que el efecto se
aplica a toda la faccion, pero 9.2 dice a que: el Rayo Cosmico sube la
cadencia del Magnetar y la carga del Pulsar; la Nube de Hidrogeno, el
intervalo de la Estrella. **El Asteroide no gana nada con ninguno de los
dos**: no dispara, no carga y no genera. Marcarlo seria prometer una ventaja
que ese nodo no tiene, que es lo que A.2.1 le prohibe al sprite.

    Rayo      -> Magnetar y Pulsar   (8 sprites)
    Hidrogeno -> Estrella            (5 sprites)

Y de ahi sale gratis una propiedad que simplifica el asset: aunque 9.1
permita que los dos power-ups esten activos a la vez, **ningun nodo puede
llevar los dos**. El overlay nunca tiene que apilarse consigo mismo.

DONDE CABE, MEDIDO. Los anillos alrededor del nodo estan adjudicados: A.4.3
reserva uno para la seleccion (`ART-WLD-SEL`) y otro para el alcance del
poder (`ART-WLD-RANGE`), y un nodo propio puede estar seleccionado y
buffeado a la vez. Los campos tramados sobre el cuerpo tambien: `Congelado`
y `Infectado` ya son dos, y los dos conviven con este. Lo que queda libre es
la esquina:

    Medido sobre los 14 sprites en su variante de faccion, el mayor cuadrado
    libre en la esquina inferior derecha es de **23 px** -y de 33 si solo se
    cuentan los ocho del Rayo-. A.3.1 midio 20 px y concluyo que ahi no cabe
    un `zzz`, que necesita 33x16. No cabe un `zzz`; **si cabe una marca**.

Es la misma esquina en los cuatro tipos y en todos los niveles, asi que la
marca no necesita tabla de anclaje: geometria fija, un solo archivo por
power-up.

EL GALON SON DOS CHEVRONES, Y NO SE ANIMA. Se probo: dos chevrones
encendiendose por turnos mas un punto que late dan **7 frames distintos de
16**. Es la misma pared con la que se topo `ART-ST-SCARE` -que mide 6x8 px y
se quedaba entre 2 y 9- y la misma regla del contrato: «una hoja cuyos
frames no son distintos no es una animacion, es un atlas mintiendo sobre su
tamano». Se mide antes de decidir, no despues de dibujar.

    A.3 tenia esta fila en 16 frames y bucle. Era una previsión escrita
    antes de que existiera ningun overlay, igual que la de `ART-ST-SCARE`,
    y la rejilla la desmiente igual: en 23 px de esquina no cabe un compas.

Asi que es de **un frame**, y eso tiene un coste que conviene no disimular:
un galon quieto dice «este nodo esta buffeado» pero no dice «va mas
deprisa». El tempo, que es de lo que trata un +50 % de cadencia, se queda
sin decir. Las otras dos propuestas lo dicen porque tienen sitio; esta no lo
tiene porque su sitio es el unico que estaba libre.

COLOR DEL POWER-UP, NO DE FACCION. A.4.4 decidio lo contrario para el halo
del drop -«el halo no dice que power-up es, eso lo dice el icono»- y aqui no
hay icono que lo diga: sobre un nodo buffeado no flota nada. Asi que esta
marca es lo unico que puede decirlo, y lleva el `#FFD23F` o el `#FF8FD0`
literales de 14.4 en el indice 3 de su rampa. La faccion la sigue diciendo
el sprite, que no cambia.

LO QUE ESTA PROPUESTA PAGA. Una marca en la esquina de la celda esta lejos
del cuerpo en los nodos pequenos -a 49 px del centro, cuando un Magnetar N1
mide 18 de radio- y puede leerse como una chincheta pegada a la casilla en
vez de como algo que le pasa al bicho. Es el precio de ser la unica zona que
no esta adjudicada.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, dir_estado, lienzo, rampa, tramar, veta_luz
from nova_estados import BUFEABLES, SPRITE_PROPIO, verifica_tinte

ESTADO = 'buff'
VERSION = 1
FRAMES = 1          # medido: a 23 px, el compas da 7 frames distintos
                    # de 16. Ver la cabecera y el contrato, *Reglas de trabajo*
CELDA = 96

# Centro del galon. Medido: el cuadrado libre de la esquina inferior derecha
# es de 23 px en los 14, o sea x 73-95 / y 73-95. Con margen de borde.
GX, GY = 83.0, 82.0
ANCHO = 6.5         # semiancho de un chevron
ALTO = 3.2          # cuanto sube la punta
SEP = 6.0           # entre los dos chevrones
GROSOR = 0.95


def _chevron(lz, cy, ramp, banda):
    """Un chevron apuntando hacia arriba: dos segmentos que se juntan."""
    p = (GX, cy - ALTO)
    veta_luz(lz, (GX - ANCHO, cy + ALTO), p, GROSOR, ramp, banda)
    veta_luz(lz, p, (GX + ANCHO, cy + ALTO), GROSOR, ramp, banda)


def buff(t=0.0, power='rayo'):
    """El overlay en la fase `t`. 16 frames, bucle."""
    lz = lienzo(CELDA)
    ramp = rampa(power)
    # Dos chevrones, el de fuera un punto mas apagado: lee como direccion
    # aunque este quieto.
    _chevron(lz, GY + SEP / 2.0, ramp, 2)
    _chevron(lz, GY - SEP / 2.0, ramp, 1)

    # El punto de apoyo, para que el galon no parezca dos piezas sueltas.
    y, x = np.mgrid[0:CELDA, 0:CELDA]
    r = np.hypot(x + 0.5 - GX, y + 0.5 - (GY + SEP))
    tramar(lz, np.clip(1.0 - r / 2.6, 0.0, 1.0), ramp,
           banda_int=1, banda_ext=3, corte=0.40)
    return lz


def main():
    raiz = dir_estado(ESTADO, VERSION)
    ok = True
    for power in ('rayo', 'hidrogeno'):
        Image.fromarray(a_rgba(buff(0.0, power)), 'RGBA').save(
            os.path.join(raiz, f'state_buff_{power}.png'))

    print('ART-ST-BUFF v1 «El galon»')
    print(f'  2 archivos de 1 frame {CELDA}x{CELDA}, uno por power-up')
    for power in ('rayo', 'hidrogeno'):
        print(f'  --- {power}: {len(BUFEABLES[power])} nodos ---')
        ok &= verifica_tinte(buff, FRAMES, nodos=BUFEABLES[power],
                             sprite=SPRITE_PROPIO, args=(power,))
    if not ok:
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
