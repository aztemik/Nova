"""NOVA - Overlay de estado `Infectado` (ART-ST-DECAY), v2: EL MIASMA.

Ref: NOVA_Estados_Animaciones.md 14.1, 14.6 y 14.7 - NOVA_Assets_Diseno.md A.3

LA LECTURA LITERAL DE 14.1: «aura verde pulsante ... y particulas
descendentes». Esta propuesta hace exactamente eso y no lo reinterpreta: una
nube tramada alrededor del cuerpo que respira en un ciclo de 16 frames, y
gotas que se descuelgan de su borde de abajo. Si el documento pide un aura,
conviene tener sobre la mesa la version que se la da, aunque solo sea para
saber que se pierde al no elegirla.

CON CIZALLA, PORQUE EL CONTRATO NO DEJA OTRA. «Una corona, aura o atmosfera
sin cizalla es un error, no una variante»: una onda evaluada en el angulo
crudo del pixel es invariante bajo rotacion de 360/n y el ojo la lee como
engranaje. Aqui la onda se evalua en el angulo desfasado por el radio.

EL CICLO ES RADIAL, NO GIRATORIO, Y NO POR GUSTO. La primera version hacia
viajar la fase de la onda con `t`, que es lo que hace fluir a una atmosfera.
No cierra: la onda suma armonicos 4, 7 y 11, y un desfase devuelve el mismo
dibujo solo cuando es multiplo de 2*pi para los tres a la vez, o sea cuando
la nube ha dado una vuelta entera. Una vuelta entera en 16 frames a 12 fps
son 1.3 s por revolucion: eso ya no es una atmosfera que fluye, es un aura
que gira, que es justo lo que la regla 6 quiere evitar. Asi que el ciclo lo
llevan el RADIO y la DENSIDAD, desfasados entre si, y el bucle cierra por
construccion.

Y SESGADA HACIA ABAJO, que es lo unico que la separa de una corona. Un aura
isotropa centrada en el nodo es la firma de la Estrella (A.8, *Ejes de diseno
ya ocupados*) y aqui iria encima de una Estrella de verdad. El sesgo -1.0
abajo, 0.32 arriba- la convierte en algo que CAE, que es lo que 7.4 describe:
Energia que se escapa sola a 2 por segundo.

NO SE CONSTRUYE CON `halo_trama`, Y ES DELIBERADO. Esa primitiva es el
material de la Estrella —«luz continua: banda solida y halo»— y heredar el
reparto de primitivas del vecino es justo lo que el contrato prohibe. El
campo se arma aqui y se tira con `tramar`, que es el paso comun.

LO QUE ESTA PROPUESTA PAGA, Y ES MUCHO. Dos cosas, las dos medidas por el
generador:

  1. EL CONTADOR DE NIVEL. Una nube que rodea el cuerpo vive exactamente
     donde los tres nodos guardan su contador: entre `r 13` y `r 40` estan
     todos los frentes del Pulsar y todas las esquirlas del Magnetar. Es el
     mismo muro contra el que choco `ART-ST-FROZEN`, y aqui no hay mesa que
     lo salve.
  2. LA ESTRELLA. Un aura tramada alrededor de una Estrella es una segunda
     corona, y `Congelado` ya ocupa el registro «nube alrededor del cuerpo».
     14.6 los hace convivir: sobre el mismo nodo pueden verse los dos a la
     vez, y dos campos de Bayer apilados pueden acabar en un borron.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, dir_estado, lienzo, rampa, tramar, veta_luz
from nova_estados import CONGELABLES, verifica_tinte

ESTADO = 'decay'
VERSION = 2
FRAMES = 16
CELDA = 96
C = CELDA / 2.0

R_MEDIO = 25.0      # radio del eje de la nube
R_PULSO = 2.4       # cuanto respira en un ciclo
GROSOR = 10.5        # semianchura radial
GAMMA = 1.45
DENS = 0.40
DENS_PULSO = 0.16
CIZALLA = 0.75      # contrato, regla 6: capa externa, 0.7-0.8
SESGO_ABAJO = 0.32  # cuanto queda del aura por arriba
ONDA = ((4, 0.52, 0.0), (7, 0.31, 2.2), (11, 0.17, 4.9))

GOTAS = ((40.0, -1.6, 1.30), (47.5, 0.6, 1.45), (55.0, 1.9, 1.20),
         (35.5, -0.8, 1.10), (60.0, 1.2, 1.15))
GOTA_Y0 = 64.0
GOTA_Y1 = 91.0


def campo(t):
    y, x = np.mgrid[0:CELDA, 0:CELDA]
    dx, dy = x + 0.5 - C, y + 0.5 - C
    rad = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)

    rm = R_MEDIO + R_PULSO * np.sin(2 * np.pi * t)
    # la onda se evalua en el angulo DESFASADO POR EL RADIO (regla 6), y la
    # fase viaja con t para que la atmosfera fluya en vez de girar rigida.
    avance = np.clip((rad - (rm - GROSOR)) / (2 * GROSOR), 0.0, 1.6)
    a = ang - CIZALLA * avance

    onda = sum(w * np.cos(n * a + f) for n, w, f in ONDA)
    onda = 0.55 + 0.45 * np.clip(onda, -1.0, 1.0)

    # sesgo hacia abajo: en pantalla, +y es abajo
    sesgo = SESGO_ABAJO + (1.0 - SESGO_ABAJO) * np.clip(np.sin(ang), 0.0, 1.0)

    radial = np.clip(1.0 - np.abs(rad - rm) / GROSOR, 0.0, 1.0) ** GAMMA
    pulso = 1.0 + DENS_PULSO * np.sin(2 * np.pi * t + 1.0)
    return radial * onda * sesgo * DENS * pulso


def decay(t=0.0):
    lz = lienzo(CELDA)
    ramp = rampa('decaimiento')
    tramar(lz, campo(t), ramp, banda_int=3, banda_ext=5, corte=0.24)

    n = len(GOTAS)
    for i, (gx, deriva, r0) in enumerate(GOTAS):
        u = (t + i / n) % 1.0
        px, py = gx + deriva * u, GOTA_Y0 + (GOTA_Y1 - GOTA_Y0) * u
        banda = 2 if u < 0.30 else (3 if u < 0.62 else (4 if u < 0.85 else 5))
        veta_luz(lz, (px, py), (px, py), max(0.9, r0 - 0.4 * u), ramp, banda)
    return lz


def main():
    raiz = dir_estado(ESTADO, VERSION)
    frames = [a_rgba(decay(i / FRAMES)) for i in range(FRAMES)]
    Image.fromarray(np.hstack(frames), 'RGBA').save(
        os.path.join(raiz, 'state_decay_sheet.png'))
    Image.fromarray(frames[0], 'RGBA').save(
        os.path.join(raiz, 'state_decay.png'))

    print('ART-ST-DECAY v2 «El miasma»')
    print(f'  hoja de {FRAMES} frames {CELDA * FRAMES}x{CELDA}, '
          f'{len(GOTAS)} gotas, {len(CONGELABLES)} nodos infectables')
    if not verifica_tinte(decay, FRAMES,
                          convive_con='states/frozen/v2/state_frozen_overlay.png'):
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
