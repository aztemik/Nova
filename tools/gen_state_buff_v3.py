"""NOVA - Overlay de estado `FX-BUFF` (ART-ST-BUFF), v3: EL SOBRECALENTADO.

Ref: NOVA_Estados_Animaciones.md 14.5 y 14.7 - NOVA_GameDesign_Spec.md 9 -
NOVA_Assets_Diseno.md A.3

LA LECTURA QUE A.3 DABA POR HECHA. La tabla de A.3 tiene esta fila como
«overlay de faccion buffeada», 16 frames, bucle, y la clasifica entre los
que **cubren el cuerpo** y por tanto se traman. Esta propuesta es esa: un
halo tramado pegado al cuerpo, en el color del power-up, que late. Conviene
tener sobre la mesa la version que le hace caso al documento, aunque solo
sea para saber que se pierde al no elegirla.

EL LATIDO VA AL DOBLE, Y AHI ESTA TODA LA IDEA. Los dos power-ups dan lo
mismo: **+50 % de ritmo** (9.2). Un halo que late una vez por ciclo dice
«esto respira», que es lo que ya dice el idle de cualquier nodo. Este late
**dos veces en los mismos 16 frames**, asi que lo que se lee no es que el
nodo brille: es que va **mas deprisa que su propio idle**. Es la unica
propuesta de las tres en la que el ritmo del bucle ES la informacion, y no
solo su portador.

    `sin(4*pi*t)` cierra igual de bien que `sin(2*pi*t)` -vale 0 en los dos
    extremos-, asi que doblar la frecuencia no cuesta nada en el bucle.

EL LATIDO RAPIDO VA MONTADO SOBRE UNA MAREA LENTA, y eso no es adorno: lo
pidio una medida. Con el latido doble a secas, el frame `i` y el `i+8` son
identicos -un seno de periodo 1/2 sobre 16 frames repite a los 8- y la hoja
daba **8 imagenes distintas de 16**: la regla del contrato la habria
suspendido igual que suspendio la animacion de `ART-ST-SCARE`. Doblar la
frecuencia divide por dos los frames distintos, y hay que compensarlo.

La compensacion es sumar un segundo canal de periodo completo: el radio y la
densidad llevan tambien un termino en `sin(2*pi*t)`, mas pequeno. El
resultado son 16 frames distintos y un latido que **no cae siempre en el
mismo sitio**, que es lo que hace que N nodos en fase no se lean como un
parpadeo de luces de navidad.

SESGADO HACIA ARRIBA, Y NO ES DECORACION. `Infectado` ya ocupa el registro
«nube tramada alrededor del cuerpo» y va sesgada **hacia abajo**, porque lo
que describe es Energia que se escapa (A.3.5). Un buff es lo contrario: algo
que sube. El sesgo es lo unico que separa a las dos construcciones, junto
con el color y con el radio -esta va pegada al cuerpo, r 19-31, y aquella
flota a r 15-35-.

CON CIZALLA, PORQUE EL CONTRATO NO DEJA OTRA: «una corona, aura o atmosfera
sin cizalla es un error, no una variante». La onda se evalua en el angulo
desfasado por el radio.

EL LIMITE INTERIOR NO SE ELIGE. Empieza en r=19 porque la caja de la cara
-`x 35-60, y 37-49`, la union de los ojos de los trece- llega hasta r=17
en su esquina mas lejana. Un pixel mas adentro y el halo se come los ojos
justo en el sesgo donde mas denso esta.

NO VA SOBRE LOS CATORCE. Rayo a Magnetar y Pulsar, Hidrogeno a Estrella
(9.2). El Asteroide no gana nada con ninguno y marcarlo seria prometerle una
ventaja que no tiene (A.2.1). De ahi sale que ningun nodo pueda llevar los
dos buffs aunque los dos esten activos.

COLOR DEL POWER-UP, NO DE FACCION, por la misma razon que las otras dos:
sobre un nodo buffeado no flota ningun icono que lo diga, asi que el overlay
es lo unico que puede.

LO QUE ESTA PROPUESTA PAGA, Y ES CARO. Es **la misma construccion que
`Infectado`**: un campo tramado en anillo alrededor del cuerpo, sesgado, con
cizalla y con un ciclo de densidad. Cambian el sentido del sesgo, el radio,
la frecuencia y la rampa —y ninguna de las cuatro cosas es la silueta—. El
contrato es explicito con los nodos: «dos nodos no se separan
repintandolos», y no hay motivo para que un overlay se libre de esa regla.
A 1x, un aro amarillo apretado y un aro verde suelto pueden acabar siendo el
mismo aro de otro color, y los dos pueden estar en pantalla a la vez sobre
nodos vecinos.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, dir_estado, lienzo, rampa, tramar
from nova_estados import BUFEABLES, SPRITE_PROPIO, verifica_tinte

ESTADO = 'buff'
VERSION = 3
FRAMES = 16
CELDA = 96
C = CELDA / 2.0

R_MEDIO = 25.0      # pegado al cuerpo; `Infectado` flota mas lejos
R_PULSO = 1.8
R_LENTO = 1.3       # ver *El latido rapido va montado sobre una marea lenta*
GROSOR = 6.0        # r 19-31: por fuera de la caja de la cara, que llega a 17
GAMMA = 1.3
DENS = 0.46
DENS_PULSO = 0.20
DENS_LENTO = 0.13
CIZALLA = 0.45      # capa pegada al cuerpo (contrato: 0.3 para estas)
SESGO_ARRIBA = 0.30
ONDA = ((3, 0.48, 1.7), (6, 0.30, 4.4), (10, 0.16, 0.6))


def campo(t):
    y, x = np.mgrid[0:CELDA, 0:CELDA]
    dx, dy = x + 0.5 - C, y + 0.5 - C
    rad = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)

    # DOS latidos por ciclo: el nodo va mas deprisa que su propio idle
    rm = (R_MEDIO + R_PULSO * np.sin(4 * np.pi * t)
          + R_LENTO * np.sin(2 * np.pi * t))
    avance = np.clip((rad - (rm - GROSOR)) / (2 * GROSOR), 0.0, 1.6)
    a = ang - CIZALLA * avance

    onda = sum(w * np.cos(n * a + f) for n, w, f in ONDA)
    onda = 0.58 + 0.42 * np.clip(onda, -1.0, 1.0)

    # en pantalla, -y es arriba
    sesgo = SESGO_ARRIBA + (1.0 - SESGO_ARRIBA) * np.clip(-np.sin(ang), 0.0, 1.0)

    radial = np.clip(1.0 - np.abs(rad - rm) / GROSOR, 0.0, 1.0) ** GAMMA
    pulso = (1.0 + DENS_PULSO * np.sin(4 * np.pi * t + 0.9)
             + DENS_LENTO * np.sin(2 * np.pi * t + 2.3))
    return radial * onda * sesgo * DENS * pulso


def buff(t=0.0, power='rayo'):
    lz = lienzo(CELDA)
    tramar(lz, campo(t), rampa(power), banda_int=2, banda_ext=4, corte=0.30)
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

    print('ART-ST-BUFF v3 «El sobrecalentado»')
    print(f'  2 hojas de {FRAMES} frames {CELDA * FRAMES}x{CELDA}, '
          f'una por power-up, dos latidos por ciclo')
    for power in ('rayo', 'hidrogeno'):
        print(f'  --- {power}: {len(BUFEABLES[power])} nodos ---')
        ok &= verifica_tinte(buff, FRAMES, nodos=BUFEABLES[power],
                             sprite=SPRITE_PROPIO, args=(power,))
    if not ok:
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
