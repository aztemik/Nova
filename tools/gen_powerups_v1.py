"""NOVA - Generador de los assets de los dos power-ups.

Ref: NOVA_GameDesign_Spec.md 9 · NOVA_Assets_Diseno.md A.4.4
`ART-UI-PU-RAY` · `ART-UI-PU-HYD` · `ART-WLD-DROP-HALO`

Son los UNICOS items del juego. No hay mas y no debe haber mas: la seccion 9
los cierra en dos, y un tercero seria inventar una regla de juego.

LOS DOS ICONOS NO SON NODOS, y eso decide como se dibujan. Un nodo es una
criatura: tiene cara, volumen y una silueta que hay que reconocer entre
otras cuatro. Un icono es un simbolo que se lee a 48 px en dos sitios a la
vez -flotando sobre el Asteroide marcado y en el HUD-, asi que se construye
al reves: primero la silueta legible, el volumen despues y solo el que quepa.
Por eso llevan `esquirla` y `bulto` en vez de `esfera`: contorno primero.

EL HALO NO DICE QUE POWER-UP ES. Lo dice el icono que flota encima. El halo
solo dice DONDE y CUANTO QUEDA, asi que va en `neutral` -la rampa sin
significado- y no en la del tipo: pintarlo de amarillo o de rosa duplicaria
la informacion del icono y, peor, obligaria a dos versiones del mismo asset.

Y VA PARTIDO EN OCHO. Un aro continuo dice "aqui pasa algo"; un aro partido
en tramos dice "aqui pasa algo Y SE ACABA", que es la mitad de la regla de
9.1 -si nadie lo enciende en 30 s, se apaga-. Es la unica pieza del juego
que tiene que comunicar una cuenta atras sin numeros, porque el numero va
aparte en TextMeshPro (contrato, Importacion en Unity).

`anillo` estrena aqui: era la unica primitiva del catalogo sin usar.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from nova_core import (CONTORNO, RAIZ, bulto, esquirla, guardar, lienzo,
                       rampa, veta)

VERSION = 1
ICONO = 48          # contrato, Resolucion: items pequenos e iconos
HALO = 128          # tiene que rodear un Asteroide de 43 px de huella

# Rayo Cosmico: dos tajos que bajan hacia la izquierda, con el de abajo
# desplazado a la derecha. Es el rayo de toda la vida, y se descompone en dos
# piezas convexas porque `esquirla` calcula su limite por funcion soporte.
# Mismo `oid` en las dos: si fueran distintos se dibujarian un contorno
# interno entre ellas y el rayo saldria partido por la mitad.
RAYO_ALTO = ((30, 4), (37, 19), (15, 30), (9, 23))
RAYO_BAJO = ((31, 19), (36, 23), (19, 45), (15, 32))

# Nube de Hidrogeno: tres lobulos de distinto tamano con el mismo `oid`, que
# es lo que los funde en una sola nube en vez de en tres bolas pegadas.
NUBE = (((16, 31), 10.0), ((32, 31), 8.8), ((24, 23), 11.8))
NUBE_PERFIL = ((2, 0.10, 0.6), (3, 0.06, 2.4))


def _conv(p):
    n = len(p)
    c = [(p[(i + 1) % n][0] - p[i][0]) * (p[(i + 2) % n][1] - p[(i + 1) % n][1])
         - (p[(i + 1) % n][1] - p[i][1]) * (p[(i + 2) % n][0] - p[(i + 1) % n][0])
         for i in range(n)]
    return all(x > 0 for x in c) or all(x < 0 for x in c)


def rayo():
    """Icono del Rayo Cosmico. Rampa `rayo`, con su #FFD23F en el indice 3."""
    lz = lienzo(ICONO)
    ramp = rampa('rayo')
    for pieza in (RAYO_ALTO, RAYO_BAJO):
        assert _conv(pieza), 'pieza no convexa: `esquirla` no la respetaria'
        c = (sum(p[0] for p in pieza) / len(pieza),
             sum(p[1] for p in pieza) / len(pieza))
        esquirla(lz, c[0], c[1], [(x - c[0], y - c[1]) for x, y in pieza],
                 ramp, oid=10)
    return lz


def nube():
    """Icono de la Nube de Hidrogeno: nube con cruz (9.2)."""
    lz = lienzo(ICONO)
    ramp = rampa('hidrogeno')
    for (cx, cy), r in NUBE:
        bulto(lz, cx, cy, r, ramp, oid=10, perfil=NUBE_PERFIL, apagado=0.2)
    # la cruz va encima y es lo unico de banda 1: en un icono de 48 px lo
    # que se lee primero es la marca, no el volumen de la nube
    veta(lz, (25, 25), (25, 38), 1.25, ramp, 1, oid=10)
    veta(lz, (18.5, 31.5), (31.5, 31.5), 1.25, ramp, 1, oid=10)
    return lz


def halo():
    """Aro partido del Asteroide marcado. `neutral`: no dice de que tipo es."""
    S = HALO
    lz = lienzo(S)
    ramp = rampa('neutral')
    c = S / 2.0
    y, x = np.mgrid[0:S, 0:S]
    rad = np.hypot(x + 0.5 - c, y + 0.5 - c)
    ang = np.arctan2(y + 0.5 - c, x + 0.5 - c)

    # ocho tramos con hueco: el hueco es lo que lo convierte en cuenta atras
    tramo = (np.mod(ang, math.pi / 4.0) < math.pi / 4.0 * 0.62)
    for r0, r1, banda in ((39.0, 42.0, 2), (42.0, 44.0, 4)):
        m = (rad >= r0) & (rad < r1) & tramo
        lz['col'][m] = ramp[banda]
        lz['lleno'][m] = True
        lz['id'][m] = 10

    # cuatro marcas en los ejes, mas largas: dan el norte del aro y evitan
    # que ocho tramos iguales se lean como una rueda girando
    for k in range(4):
        a = math.pi / 2.0 * k
        m = (rad >= 35.5) & (rad < 47.0) & (np.abs(
            np.mod(ang - a + math.pi, 2 * math.pi) - math.pi) < 0.07)
        lz['col'][m] = ramp[1]
        lz['lleno'][m] = True
        lz['id'][m] = 11
    return lz


PIEZAS = (('ui', 'ui_pu_cosmicray.png', rayo),
          ('ui', 'ui_pu_hydrogen.png', nube),
          ('world', 'world_drop_halo.png', halo))


def main():
    for carpeta, nombre, fn in PIEZAS:
        d = os.path.join(RAIZ, 'art', carpeta)
        os.makedirs(d, exist_ok=True)
        lz = fn()
        guardar(lz, os.path.join(d, nombre))
        ys, xs = np.where(lz['lleno'] | lz['glow'])
        print(f'{nombre:24} {lz["S"]}x{lz["S"]}  '
              f'ocupa {xs.max()-xs.min()+1}x{ys.max()-ys.min()+1} px')


if __name__ == '__main__':
    main()
