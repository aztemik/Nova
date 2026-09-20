"""NOVA - Generador del Asteroide, propuesta v2: EL FRAGMENTO.

Ref: NOVA_Nodos.md 4.1 · NOVA_Assets_Diseno.md A.2.1
Propuesta alternativa a `gen_asteroide_v1.py`. Las dos conviven hasta elegir.

LA IDEA. Un asteroide no es un planeta pequeno: es un TROZO DE UNO GRANDE
QUE SE ROMPIO. La v1 cuenta una piedra a la que el tiempo ha ido picando; la
v2 cuenta la otra mitad de la historia -la violencia- y lo cuenta con dos
cosas que se ven a la vez: las CARAS DE FRACTURA por donde se partio, y los
ESTRATOS que la cruzan y que esas caras cortan a hachazo.

Los estratos son el argumento. Una capa que rodea el contorno dice "esto
crecio asi"; una capa que entra por un borde, cruza la pieza y sale por el
otro dice "esto era mas grande". Sin tocar un solo simbolo, el sprite dice de
donde sale el material del juego: el Asteroide es el escombro del que se
sacan todos los demas nodos.

                        Asteroide v1              Asteroide v2
    Historia            erosionada por el tiempo  rota por violencia
    Contorno            organico, todo curvo      recto: caras de fractura
    Superficie          picada de crateres        estratificada
    Organizacion        excentrica, por puntos    DIRECCIONAL, sin centro
    Acabado             mate, sin especular       brillo en la cara fresca
    Cuerpo              `bulto`                   `esquirla`

LA ORGANIZACION ES LO MAS NUEVO QUE HAY AQUI. Los cuatro disenos vivos del
juego se ordenan alrededor de su centro: radial la Estrella, bilateral desde
el centro el Pulsar, concentrico el Magnetar, y excentrica pero puntual la
v1. Los estratos no tienen centro, son una direccion. Es el unico principio
de composicion que quedaba libre en todo el reparto.

EL BRILLO ES LA DIFERENCIA CON LA v1, Y ES FISICA. La v1 apaga el especular
porque una roca lijada por mil millones de anos de micrometeoritos es mate.
Una cara de fractura RECIENTE no lo es: es plano limpio, y el plano limpio
devuelve luz. Las dos decisiones son correctas y son opuestas, que es
exactamente lo que se quiere de dos propuestas.

LO QUE LAS DOS COMPARTEN, porque es del nodo y no de la version: ni un pixel
de luz propia, ojos cerrados, un solo nivel, idle por transform, y ninguna
promesa de valor. 4.1 dice "sin valor APARENTE", y la partida entera se apoya
en que pagues 10 por capturarlo y otros 10 por encenderlo sin que el objeto
te prometa nada.

LOS OJOS VAN TUMBADOS CON LOS ESTRATOS. Es lo que los convierte en parte de
la roca en vez de en dos cosas pegadas encima: parecen dos grietas que por
casualidad forman una cara, y esa duda es la gracia del nodo. La v1 los pone
en espejo; aqui los dos van paralelos, con el mismo angulo que las capas.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nova_core import (a_rgba, dir_nodo, esferoide, estratos, esquirla,
                       guardar, lienzo, rampa, veta)

NODO = 'asteroide'
VERSION = 2
IDLE = False
FACCIONES = ('neutral', 'player', 'enemy')

CELDA = 96
C = CELDA / 2.0
PPU = 64.0

# Casi equidimensional, y es a proposito. Alargada, el cuerpo tiene un eje
# largo, los estratos se alinean con el y el conjunto se lee como una
# almeja: las capas parecen seguir al contorno en vez de cruzarlo. En un
# cuerpo sin eje propio, la direccion de las capas es la unica que hay, que
# es justo lo que este diseno tiene que decir.
RX = 19.5
RY = 18.5

# Contorno: (angulo en grados, factor de radio). Los huecos entre vertices
# son MUY desiguales a proposito:
#   - dos huecos grandes (62 y 52 grados) = las dos CARAS DE FRACTURA, las
#     aristas largas y rectas por donde se partio
#   - el resto, huecos cortos = borde comido, irregular, sin fracturar
# Repartidos por igual saldria un poligono regular, que es un cristal, y el
# cristal ya es otro nodo.
#
# Y LAS DOS CARAS LARGAS MIRAN A LA LUZ, arriba a la izquierda. Puestas
# abajo, la unica parte del sprite que tiene que decir "esto se acaba de
# romper" cae en la sombra y no dice nada; puestas a la luz, la fractura es
# un plano grande e iluminado contra un borde comido y oscuro, que es el
# contraste que cuenta la historia entera.
PERFIL = ((-8, 1.00), (30, 0.85), (68, 0.76), (104, 0.80), (140, 0.88),
          (172, 0.98), (196, 1.00), (256, 0.84), (312, 0.92))

# Indices de PERFIL donde arranca una cara de fractura.
FRACTURAS = (6, 7)
FILO_BANDA = 1      # el filo de una rotura reciente devuelve luz
FILO_ADENTRO = 1.6  # cuanto se mete hacia dentro, en pixeles

ANG_CAPA = math.radians(-22.0)   # las capas cruzan; ni horizontales -se
                                 # confunden con el sombreado- ni en la
                                 # diagonal de 32 grados, que es del Pulsar

# Secuencia de capas, en pixeles, y su desplazamiento de banda. Se recorre en
# ciclo. Gruesos desiguales y un solo delta fuerte aislado leen como roca;
# todos iguales leen como persiana.
GROSORES = (4.2, 1.8, 5.4, 2.6, 1.5, 4.6, 3.0)
DELTAS   = (0, 1, -1, 0, 1, -1, 0)

PLIEGUE_AMP = 0.85   # las capas no son rectas: la roca se plego antes de
PLIEGUE_K   = 0.048  # romperse. Recto del todo se lee como contrachapado

OJO_SEP = 0.34      # en multiplos de RX
OJO_ALT = -0.06     # en multiplos de RY
OJO_RX  = 0.165
OJO_RY  = 0.095
OJO_CIERRE = 0.66   # el derecho, mas cerrado

NIVELES = {0: dict()}   # un solo nivel, por firma uniforme con el resto


def _perfil():
    return [(math.cos(math.radians(a)) * RX * f,
             math.sin(math.radians(a)) * RY * f) for a, f in PERFIL]


def asteroide(nivel=0, faccion='neutral', t=0.0):
    """Devuelve el lienzo de un Asteroide v2. `t` no se usa: idle por transform."""
    ramp = rampa({'player': 'roca_p', 'enemy': 'roca_e'}.get(faccion, 'roca_n'))
    ojo = rampa('ojo')

    lz = lienzo(CELDA)

    # 1. el fragmento. Sin especular redondo: en un cuerpo alargado el punto
    #    de brillo se estira hasta ser un manchon en mitad de la pieza y se
    #    lee como un agujero. El brillo de esta roca no es un punto, es un
    #    filo, y va en el paso 3.
    verts = _perfil()
    esquirla(lz, C, C, verts, ramp, oid=10, apagado=1.25, especular=False)

    # 2. estratos. Cruzan la pieza entera y los corta la silueta, no se
    #    doblan a seguirla: eso es lo que prueba que esto es un trozo.
    estratos(lz, C, C, ANG_CAPA, GROSORES, DELTAS, oid_cuerpo=10, ramp=ramp,
             amp_pliegue=PLIEGUE_AMP, k_pliegue=PLIEGUE_K)

    # 3. filo de las caras de fractura. Va DESPUES de los estratos: la
    #    fractura es posterior a la roca, y una capa que cruzara por encima
    #    del filo desharia el orden de los acontecimientos.
    n = len(verts)
    for i in FRACTURAS:
        ax, ay = verts[i]
        bx, by = verts[(i + 1) % n]
        k = FILO_ADENTRO / max(math.hypot((ax + bx) / 2, (ay + by) / 2), 1e-6)
        veta(lz, (C + ax * (1 - k), C + ay * (1 - k)),
             (C + bx * (1 - k), C + by * (1 - k)),
             0.95, ramp, FILO_BANDA, oid=10)

    # 4. ojos cerrados y TUMBADOS CON LAS CAPAS, los ultimos (14.7)
    for signo in (-1, 1):
        cierre = OJO_CIERRE if signo > 0 else 1.0
        esferoide(lz, C + signo * OJO_SEP * RX, C + OJO_ALT * RY,
                  OJO_RX * RX, OJO_RY * RY * cierre, ANG_CAPA, ojo,
                  oid=30 + signo)

    return lz


def main():
    import numpy as np

    # El limite de `esquirla` se calcula por funcion soporte, que solo vale
    # para poligonos convexos: un entrante se rellenaria igual y el error no
    # se ve, solo se ve raro. Se comprueba, no se supone.
    p = _perfil()
    n = len(p)
    cruces = [(p[(i + 1) % n][0] - p[i][0]) * (p[(i + 2) % n][1] - p[(i + 1) % n][1]) -
              (p[(i + 1) % n][1] - p[i][1]) * (p[(i + 2) % n][0] - p[(i + 1) % n][0])
              for i in range(n)]
    if not (all(c > 0 for c in cruces) or all(c < 0 for c in cruces)):
        print('  AVISO: el contorno no es convexo, `esquirla` no lo respetara')

    raiz = dir_nodo(NODO, VERSION)
    for fac in FACCIONES:
        guardar(asteroide(0, fac), os.path.join(raiz, f'ast_lvl0_{fac}.png'))

    lz = asteroide(0, 'neutral')
    a = a_rgba(lz)[..., 3] > 0
    ys, xs = np.where(a)
    ext = max(ys.max() - ys.min(), xs.max() - xs.min()) + 1
    if lz['glow'].any():
        print('  AVISO: ha ensuciado la capa glow')
    if a[0, :].any() or a[-1, :].any() or a[:, 0].any() or a[:, -1].any():
        print('  AVISO: toca el borde de la celda')
    print(f'huella: {ext / PPU:.2f}u   (sin glow: solida = total)')


if __name__ == '__main__':
    main()
