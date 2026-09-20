"""NOVA - Overlay de estado `Dormido` (ART-ST-SLEEP), propuesta v2: EL VAIVEN.

Ref: NOVA_Estados_Animaciones.md 14.1 y 14.7 - NOVA_Assets_Diseno.md A.3

EL MISMO ZZZ, EL CANAL DE ANIMACION CONTRARIO. 14.1 pide dos
cosas -«`zzz` flotante» y «balanceo lento»- y hay dos maneras limpias de darlas
con 16 frames y alfa binario:

                        v1 La escalera            v2 El vaiven
    Canal               traslacion                cabeceo en el sitio
    Ciclo               relevo: cada Z recorre    onda: el cabeceo se propaga
                        el camino y se apaga      de dentro afuera
    Que hay en el sitio  una Z distinta cada vez  siempre la misma Z
    Glifos encendidos   3, cambiando              3, los mismos, siempre
    Lectura             «sigue exhalando»         «esto lleva asi un rato»
    Punto debil         el relevo apaga un glifo  no cuenta una historia:
                        de golpe, 16 veces        puede leerse como adorno

Las dos propuestas comparten EL MISMO ARRANQUE, LA MISMA DIRECCION, LA MISMA
LEY DE TAMANOS Y LA MISMA SEPARACION ENTRE Z -16.5 px medidos-. Es deliberado:
si ademas cambiara la composicion, la comparacion no diria cual animacion
funciona, diria cual encuadre gusta mas. Aqui lo unico que cambia es que la Z
no viaja.

POR QUE MERECE EXISTIR. Tres motivos, y los tres son medibles:

  1. NINGUN FRAME PIERDE INFORMACION. Con alfa binario, cualquier glifo que se
     apague lo hace de golpe. En la v1 eso pasa una vez por vuelta y por Z.
     Aqui no pasa nunca: las mismas tres Z estan en los 16 frames y 14.0 #5
     -«si el estado no se ve, es un bug»- se cumple por construccion.
  2. LA POSICION DEJA DE SER RUIDO. `Dormido` es el estado del Asteroide
     Neutral, y en un mapa hay muchos a la vez. Con la v1, dos asteroides
     vecinos ensenan sus Z en sitios distintos segun la fase en que esten y el
     ojo lee movimiento donde no hay informacion. Aqui el `zzz` esta siempre
     en el mismo sitio en todos: lo unico que se mueve es un cabeceo de 1 px.
  3. ES EL GESTO CORRECTO PARA UN ESTADO PERMANENTE. `Dormido` no avanza hacia
     ningun sitio: dura hasta que el nodo es capturado. Un ciclo que vuelve
     sobre si mismo dice eso; un relevo que produce glifos nuevos dice «esta
     pasando algo».

Y EL COSTE, QUE ES EL REVERSO EXACTO: sin relevo no hay lectura de
exhalacion, y tres glifos que solo cabecean se parecen mas a un cartel que a
un aliento. Si al verlo en juego el `zzz` parece UI pegada encima y no el
bicho respirando, la que hay que elegir es la v1.

LA ONDA VA HACIA FUERA, CON RETRASO DE FASE. Cada estacion cabecea con la
misma amplitud pero `LAG` de ciclo mas tarde que la de dentro, asi que el
gesto se propaga del que duerme hacia el vacio y no las tres a la vez. Las
tres a la vez es un temblor; escalonadas, es una respiracion. Es el mismo
recurso con el que el Magnetar v2 propagaba su realce de dentro afuera, y
aqui hace exactamente el mismo trabajo.

CABECEO Y BAMBOLEO SON EL MISMO SENO. La Z gira `AMP` grados y sube `BAMBOLEO`
pixeles con la misma fase: girar sin subir es un limpiaparabrisas, y subir sin
girar es un ascensor. Juntos es algo colgado del aire.

EL BUCLE CIERRA PORQUE TODO ES `sin(2 pi f)` con `f` funcion de `t`: a t = 1
el angulo, la altura y por tanto cada pixel son los del frame 0. No hay estado
que arrastrar entre frames.

UN MOVIL RIGIDO NO CABE, Y SE DESCARTO CON NUMEROS. La primera version de esta
propuesta colgaba las tres Z de un solo solido que basculaba alrededor de un
pivote en el hombro de la roca. Un grupo de ~50 px girando aunque sea 4 grados
barre 7 px en la punta, y en la celda de 96 con la roca ocupando y 29-67,
x 26-68 no hay sitio: se probaron 64 combinaciones de pivote, amplitud y
reparto, y en TODAS la Z exterior invadia la roca o salia de la celda en algun
frame. El cabeceo en el sitio da el mismo balanceo sin barrer nada.

NI UN PIXEL DE TRAMA, por el mismo motivo que en la v1: la regla de A.3 habla
de tintes y auras que cubren el cuerpo, y un glifo que vive fuera del cuerpo
compite con el fondo. Solido, con contorno, tres `veta` por Z.
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
VERSION = 2
FRAMES = 16
CELDA = 96

N_Z = 3

# Mismo arranque y misma direccion que la v1. El final es mas corto a
# proposito: la v1 reparte su camino en TRES tramos y aqui hay DOS huecos
# entre tres sitios fijos, asi que para que la separacion entre Z sea la misma
# -16.5 px medidos- el recorrido tiene que ser dos tercios del suyo. Si no, la
# comparacion mediria el encuadre en vez de la animacion.
P0 = (38.0, 22.0)
P1 = (70.0, 14.0)

ESTACIONES = (0.0, 0.5, 1.0)

S0, S1 = 5.0, 3.9
B0, B1 = 3, 2
U_BANDA = 0.55

ANG0, ANG1 = -6.0, -20.0     # giro en reposo de la Z de dentro y la de fuera

AMP = 8.0           # grados de cabeceo. Sube a 10 y la Z exterior sale de la
                    # celda; a 6 el gesto deja de verse a 1x.
BAMBOLEO = 1.0      # px de subida y bajada, en fase con el cabeceo
LAG = 0.12          # retraso de fase por estacion hacia fuera, en ciclos

GROSOR = 0.30
ALTO = 1.05


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


def _estacion(k, t):
    """Sitio, tamano, giro y banda de la Z `k` en la fase `t`."""
    u = ESTACIONES[k]
    f = (t - k * LAG) % 1.0
    onda = math.sin(2 * math.pi * f)
    cx = P0[0] + (P1[0] - P0[0]) * u
    cy = P0[1] + (P1[1] - P0[1]) * u + BAMBOLEO * onda
    s = S0 + (S1 - S0) * u
    ang = ANG0 + (ANG1 - ANG0) * u + AMP * onda
    return cx, cy, s, ang, (B0 if u < U_BANDA else B1)


def sleep(t=0.0):
    """Devuelve el lienzo del overlay en la fase `t` de [0, 1)."""
    ramp = rampa('neutral')
    lz = lienzo(CELDA)
    # De fuera adentro: la de dentro se dibuja encima, porque es la que esta
    # mas cerca del que respira.
    for k in range(N_Z - 1, -1, -1):
        cx, cy, s, ang, banda = _estacion(k, t)
        _z(lz, cx, cy, s, ang, ramp, banda, oid=10 + k * 4)
    return lz


def _piezas(t):
    """Las tres Z por separado, para medir que no se toquen entre ellas."""
    ramp = rampa('neutral')
    out = []
    for k in range(N_Z):
        cx, cy, s, ang, banda = _estacion(k, t)
        lz = lienzo(CELDA)
        _z(lz, cx, cy, s, ang, ramp, banda, oid=10)
        out.append(a_rgba(lz)[..., 3] > 0)
    return out


def hoja():
    """Tira horizontal de FRAMES celdas: 1536x96 (contrato, Resolucion)."""
    return np.hstack([a_rgba(sleep(i / FRAMES)) for i in range(FRAMES)])


def main():
    raiz = dir_estado(ESTADO, VERSION)
    Image.fromarray(hoja(), 'RGBA').save(
        os.path.join(raiz, 'state_sleep_sheet.png'))
    Image.fromarray(a_rgba(sleep(0.0)), 'RGBA').save(
        os.path.join(raiz, 'state_sleep.png'))
    print('ART-ST-SLEEP v2 «El vaiven»')
    verifica(sleep, FRAMES, _piezas)


if __name__ == '__main__':
    main()
