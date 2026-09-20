"""NOVA - Overlay de estado `Congelado` (ART-ST-FROZEN), v2: EL BLOQUE.

Ref: NOVA_Estados_Animaciones.md 14.1, 14.6 y 14.7 - NOVA_Assets_Diseno.md A.3

LA TESIS: `Congelado` NO ES UNA TEMPERATURA, ES UNA CAJA. 7.3 no dice que el
nodo este frio: dice que no genera, no dispara, no carga, no envia, no se
mejora y no se reconvierte. Puede recibir impactos y nada mas. El estado no
describe una superficie, describe un ENCIERRO, y el dibujo que dice encierro
es un solido alrededor, no una capa encima.

De ahi sale la unica propuesta de las tres cuyo contorno es RECTO. Un prisma
de hielo: seis caras, aristas duras, el nodo dentro. Y de ahi sale tambien
que se lea «parado» sin animar nada, que es lo que 14.1 exige -«idle
detenido»- y lo que A.3 ya habia anotado como el motivo de que este asset sea
de un frame: lo que esta metido en un bloque no se mueve.

REUSA EL MODELO DE LUZ, NO LO INVENTA. Las caras no llevan una densidad a
gusto: llevan la que les da la `L` global, muestreada UNA VEZ POR CARA, que
es exactamente lo que hace `poliedro` con la materia facetada (contrato,
*Materia facetada*). La normal se toma en el punto medio de la arista
exterior y no en el centroide, que es la misma correccion que el contrato
documenta para `poliedro` y por la misma razon.

PERO EL VOLUMEN NO LO LLEVA LA TRAMA, LO LLEVAN LAS ARISTAS, y eso no era el
plan: lo impuso una medida. La primera version repartia las caras entre 0.17
y 0.80 de densidad, que es lo que hace que un solido tenga lados. Sobre los
trece, esa rampa borraba hasta el 70 % de un frente de onda del Pulsar y de
una esquirla del Magnetar. Y no se arregla moviendo el bloque:

    Los contadores de nivel de los tres nodos ocupan TODOS los radios entre
    13 y 40 px -el frente interior del Pulsar N3 esta a 13, la esquirla
    exterior del Magnetar N5 a 40-. No hay ningun radio al que poner un
    anillo de caras densas sin caer encima de alguno.

Asi que la trama se aplana a 0.12-0.26 -suficiente para que las caras se
distingan entre si, poco para tapar- y el solido se dibuja con lo que no
cuesta area: sus ARISTAS. Que es, ademas, como se ve un bloque de hielo de
verdad: se le ven los cantos, no las caras.

LA CARA SE RESUELVE SOLA, Y ES LA MEJOR PARTE. En `poliedro` la mesa es la
cara frontal, la que mira al jugador. Aqui la mesa es el CRISTAL POR EL QUE
SE MIRA: se lleva la densidad mas baja de las siete y, medida la union de los
ojos en los trece congelables -`x 35-60, y 37-49`-, cabe entera dentro de
ella. No hay que abrirle un agujero al dibujo para que la cara respire: la
cara respira porque un bloque de hielo tiene un lado plano delante y por ese
lado se ve. 14.6 pide que `Asustado` y `Congelado` convivan; aqui conviven
por construccion.

EL BLOQUE ENVUELVE EL NODO ENTERO, no solo su cuerpo. Semiejes 43 x 44 px:
por fuera de la esquirla mas lejana del Magnetar N5 (radio 40) y de los
frentes del Pulsar N3 (37). Se probo un bloque ajustado al cuerpo -24 x 26,
que es lo que miden los cuerpos- y era peor por dos motivos: el contorno del
prisma cortaba en dos lo que cruzara, y encima se leia como que al nodo le
habia crecido una caja en el centro. Un bloque de hielo contiene al bicho;
no le sale de dentro.

LO QUE ESTA PROPUESTA PAGA. Es la primera figura de contorno recto y
regular que entra en el tablero, y ese fue el argumento que descarto la v1 de
`ART-ST-IGN`: «NOVA no tiene un solo simbolo de interfaz dentro del tablero».
La defensa es que un bloque de hielo no es un simbolo, es un objeto -tiene
volumen, luz y fracturas, y el anillo de encendido no tenia ninguna de las
tres-, pero la objecion es legitima y el riesgo es real: si a 1x el prisma se
lee como un recuadro de UI, esta propuesta ha fallado. Y hereda del Magnetar
v2 la lectura «recinto», que alli fue un defecto; aqui es literalmente lo que
hay que decir.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import (L, a_rgba, dir_estado, lienzo, rampa, tramar,
                       veta_luz, _poligono)
from nova_estados import CONGELABLES, verifica_tinte

ESTADO = 'frozen'
VERSION = 2
FRAMES = 1          # `Congelado` detiene el idle por definicion (14.1)
CELDA = 96
C = CELDA / 2.0

# --- El prisma -------------------------------------------------------------
# Semiejes medidos contra los trece: el cuerpo mas ancho que tiene que caber
# dentro es el del Magnetar N5 (radio 18.1) y el nucleo de la Estrella N1
# (20.7). Con 24 x 26 el bloque los envuelve y deja fuera corona, frentes y
# esquirlas, que es donde vive el contador de nivel.
RX, RY = 43.0, 44.0

# Seis vertices, en grados y con radio propio. Desiguales a proposito: un
# hexagono regular es una tuerca, y ademas su simetria radial 6-fold es la
# firma de la Estrella. Con radios y angulos distintos el solido tiene talle.
VERTS = ((  92.0, 0.98), (  28.0, 0.92), ( 327.0, 1.00),
         ( 262.0, 0.95), ( 203.0, 1.00), ( 147.0, 0.91))

# La mesa va GRANDE, y es la misma razon por la que la lleva grande el
# Magnetar (A.2.4): con mesa pequena las caras de talle son enormes y se
# comen el cuerpo; grande, el talle queda como un anillo de facetas
# estrechas -un solido tallado- y el interior del bloque se queda limpio.
# Aqui ademas eso es lo que salva las dos lecturas que no se pueden tapar:
# dentro de la mesa caen la cara y las piezas interiores del contador de
# nivel, y la mesa es la densidad mas baja de las siete.
MESA = 0.80
DENS_MESA = 0.12
DENS_MIN = 0.15     # cara de talle en sombra
DENS_MAX = 0.26     # cara de talle a favor de la luz

# Dos fracturas internas. Un bloque sin fractura es un cristal de joyeria; el
# hielo se raja siempre. Se definen como (arista, t) -> (arista, t): una
# grieta va de una cara a otra, y asi no puede salirse del prisma. Escritas
# en coordenadas sueltas se salian: el hexagono tiene menos area que la
# elipse RX x RY que lo circunscribe, y los extremos caian fuera por el
# hueco entre el vertice y el lado.
FRACTURAS = ((0, 0.35, 2, 0.60), (3, 0.30, 5, 0.55))


def _pts(k):
    return [(C + RX * k * r * np.cos(np.radians(a)),
             C - RY * k * r * np.sin(np.radians(a))) for a, r in VERTS]


def frozen(t=0.0):
    """El overlay. Un solo frame: lo que esta en un bloque no se mueve."""
    lz = lienzo(CELDA)
    ramp = rampa('hielo')
    y, x = np.mgrid[0:CELDA, 0:CELDA]
    px, py = x + 0.5, y + 0.5

    fuera, dentro = _pts(1.0), _pts(MESA)
    n = len(fuera)

    # --- Las caras de talle: la regla 1 muestreada una vez por cara -------
    dens = np.zeros((CELDA, CELDA), np.float32)
    banda = np.full((CELDA, CELDA), 4, np.int16)
    for i in range(n):
        j = (i + 1) % n
        cara = [fuera[i], fuera[j], dentro[j], dentro[i]]
        m = _poligono(px, py, cara)
        # normal en el punto medio de la arista EXTERIOR (contrato)
        mx = (fuera[i][0] + fuera[j][0]) / 2.0 - C
        my = (fuera[i][1] + fuera[j][1]) / 2.0 - C
        nx, ny = mx / RX, my / RY
        nz = 0.55
        nn = np.sqrt(nx * nx + ny * ny + nz * nz)
        d = max(0.0, (nx * L[0] + ny * L[1] + nz * L[2]) / nn)
        dens[m] = DENS_MIN + (DENS_MAX - DENS_MIN) * d
        banda[m] = 2 if d > 0.45 else 3

    m_mesa = _poligono(px, py, dentro)
    dens[m_mesa] = DENS_MESA
    banda[m_mesa] = 3

    on = dens > np.tile(np.array([[0]]), (1, 1))  # placeholder, ver tramar
    del on
    # Bandas por cara: se trama dos veces, una por banda, para que cada cara
    # conserve la suya. `tramar` decide por `corte`; aqui el corte lo pone la
    # geometria, no la densidad.
    for b in (2, 3, 4):
        sel = banda == b
        if not sel.any():
            continue
        tramar(lz, np.where(sel, dens, 0.0), ramp,
               banda_int=b, banda_ext=b, corte=0.0)

    # --- Las aristas: solidas, y con la banda de su cara ------------------
    for i in range(n):
        j = (i + 1) % n
        mx = (fuera[i][0] + fuera[j][0]) / 2.0 - C
        my = (fuera[i][1] + fuera[j][1]) / 2.0 - C
        nx, ny, nz = mx / RX, my / RY, 0.55
        nn = np.sqrt(nx * nx + ny * ny + nz * nz)
        d = (nx * L[0] + ny * L[1] + nz * L[2]) / nn
        veta_luz(lz, fuera[i], fuera[j], 0.60, ramp, 1 if d > 0.35 else 3)
        veta_luz(lz, dentro[i], dentro[j], 0.55, ramp, 2 if d > 0.35 else 4)

    # --- Las fracturas ----------------------------------------------------
    for ea, ta, eb, tb in FRACTURAS:
        def sobre_arista(e, t):
            a, b = fuera[e], fuera[(e + 1) % n]
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        veta_luz(lz, sobre_arista(ea, ta), sobre_arista(eb, tb), 0.55, ramp, 2)
    return lz


def main():
    raiz = dir_estado(ESTADO, VERSION)
    Image.fromarray(a_rgba(frozen()), 'RGBA').save(
        os.path.join(raiz, 'state_frozen_overlay.png'))

    print('ART-ST-FROZEN v2 «El bloque»')
    print(f'  1 archivo de 1 frame, {len(CONGELABLES)} nodos congelables')
    if not verifica_tinte(frozen, FRAMES):
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
