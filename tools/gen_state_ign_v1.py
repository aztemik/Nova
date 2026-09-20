"""NOVA - Overlay de estado `SinEncender` (ART-ST-IGN), propuesta v1: EL INTERRUPTOR.

Ref: NOVA_Estados_Animaciones.md 14.1 y 14.7 - NOVA_Assets_Diseno.md A.2.1 y A.3

QUE PIDE LA SPEC. 14.1: «icono de ignicion parpadeante (sustituye al `zzz`)»,
sobre el Asteroide del Jugador O DEL ENEMIGO, indefinido, hasta que se
enciende. 4.1 lo dice con las mismas palabras: «un icono parpadeante de
"encender" en lugar de zzz». A.3: 16 frames en bucle.

DOS FACCIONES, NO UNA. Este es el unico overlay de A.3 que sale en dos
versiones de color, y no es un capricho: A.2.1 cerro que LA MARCA DE POSESION
DEL ASTEROIDE ES ESTE OVERLAY, no el sprite -ninguna geometria cambia entre
facciones (14.0 #3)-. Un icono gris no marcaria nada: la roca propia y la
enemiga solo se distinguen por el tinte de su rampa, que es sutil a proposito
porque es capital muerto. El icono lleva el color de faccion literal de 14.4,
#3FD7F5 y #F2456B, y con el la roca dice de quien es de un vistazo.

Las rampas son `str_p` y `str_e`. Se llaman asi por la Estrella, pero son las
que guardan esos dos colores en su indice 3, que es lo que 14.4 exige. No hay
una rampa de faccion generica en la paleta; usar estas es lo correcto hoy y
queda anotado por si algun dia se separa.

EL SIMBOLO ES EL UNIVERSAL DE ENCENDIDO: anillo abierto por arriba y barra
vertical saliendo por el hueco. No hay que aprenderlo y no se parece a nada
mas del juego. La alternativa -una chispa, una llama- es mas diegetica pero
tiene que competir con lo que ya significa algo: cualquier destello radial es
la firma de la Estrella, que ademas es UNA DE LAS TRES COSAS en las que este
asteroide puede encenderse, asi que un icono con forma de estrella prometeria
de mas. Ver la v2, que asume ese riesgo a cambio de no parecer UI.

DE QUE ESTA HECHO. `veta`, otra vez, y nada mas. El anillo son catorce tramos
rectos cortos recorriendo el arco: `anillo()` dibuja un annulus CERRADO y aqui
hace falta abierto, y abrirlo seria borrar pixeles, que este pipeline no hace.
Catorce tramos sobre un radio de 7 px dan una curva sin escalones visibles a
1x. La barra es un `veta` mas.

EL PARPADEO ES DE TONO, NO DE PRESENCIA. «Parpadeante» con alfa binario
invita a encender y apagar el icono, y eso lo apagaria de verdad: 14.0 #5 dice
que un estado que no se ve es un bug, y medio ciclo sin icono es medio ciclo
sin saber que ese asteroide es tuyo. Aqui lo que oscila es LA BANDA de la
rampa, entre la 2 y la 4: el icono nunca deja de estar, cambia de intensidad.
Es el mismo razonamiento con el que el Magnetar v2 decidio que su onda solo
aclarase, y a 12 fps un salto de banda discreto se lee como un parpadeo real,
no como un desvanecido.

LA BARRA VA POR DELANTE DEL ANILLO. Las dos oscilan con el mismo seno, pero la
barra `DESFASE` de ciclo antes: la corriente entra por el contacto y despues
recorre el aro. Con las dos en fase el icono entero late en bloque y parece
que cambia de color; escalonadas, parece que se enciende.

DONDE VA. En el hueco que deja el Asteroide y en EL MISMO SITIO que el `zzz`
al que sustituye (A.3.1): el centro del area ocupada cae en (53, 17), asi que
al capturar una roca neutral el jugador ve cambiar el simbolo sin que se mueva
de sitio. La roca ocupa y 29-67, x 26-68 de la celda de 96 y el icono no la
pisa en ningun frame; `main` lo comprueba contra los DOS sprites, el del
Jugador y el del Enemigo.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, dir_estado, lienzo, rampa, veta
from nova_estados import sprites, verifica

ESTADO = 'ign'
VERSION = 1
FRAMES = 16
CELDA = 96

# `SinEncender` no existe en Neutral: esa roca esta `Dormido` (14.1).
FACCIONES = ('player', 'enemy')
RAMPAS = {'player': 'str_p', 'enemy': 'str_e'}

# Mismo sitio que el `zzz` de A.3.1: el centro de lo que ocupa, no el de la
# celda. Uno sustituye al otro y no deben saltar de sitio al relevarse.
C = (53.0, 17.0)

R = 9.0             # radio del anillo. Con 6 el hueco de arriba se cierra a
                    # 1x y el simbolo pasa a ser una O. El techo lo pone la
                    # roca, no la celda: con 9 el icono mide 306 px y el `zzz`
                    # al que sustituye mide 418, que es la referencia de
                    # cuanto pesa un overlay de este hueco.
HUECO = 62.0        # grados de apertura arriba. Menos y no se lee el corte.
TRAMOS = 14         # tramos rectos del arco. Menos y se ve el poligono.
GROSOR = 1.5

BARRA_ALTA = 1.15   # en multiplos de R, desde el centro
BARRA_BAJA = 0.10

B_MEDIA = 3.0       # banda central del parpadeo (el color literal de 14.4)
B_AMP = 1.0         # oscila entre la 2 y la 4. Nunca se apaga.
DESFASE = 0.12      # la barra enciende antes que el anillo, en ciclos

B_APAGADO = 5       # el aro sin corriente: dos bandas por debajo del parpadeo.
                    # Se ve, pero no llama.


def _banda(t):
    return int(round(B_MEDIA - B_AMP * math.sin(2 * math.pi * t)))


def _arco(lz, cx, cy, r, a0, a1, g, ramp, banda, oid, n=TRAMOS):
    pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
            cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    for i in range(n):
        veta(lz, pts[i], pts[i + 1], g, ramp, banda, oid + i, solo_dentro=False)


def ign(t=0.0, faccion='player', listo=True):
    """El overlay en la fase `t`. `listo` es `energy >= 10` (4.1).

    APAGADO: el aro solo, quieto y en banda baja. Hay un contacto, no hay
    corriente. `t` no se usa: es un asset de un frame.
    LISTO:   el aro mas la barra, parpadeando. El circuito esta cerrado.
    """
    lz = lienzo(CELDA)
    ramp = rampa(RAMPAS[faccion])
    if not listo:
        _arco(lz, C[0], C[1], R, -90 + HUECO / 2, -90 + 360 - HUECO / 2,
              GROSOR, ramp, B_APAGADO, oid=20)
        return lz
    _arco(lz, C[0], C[1], R, -90 + HUECO / 2, -90 + 360 - HUECO / 2,
          GROSOR, ramp, _banda(t), oid=20)
    veta(lz, (C[0], C[1] - R * BARRA_ALTA), (C[0], C[1] - R * BARRA_BAJA),
         GROSOR, ramp, _banda(t + DESFASE), 60, solo_dentro=False)
    return lz


def _piezas(t, faccion='player', listo=True):
    """Anillo y barra por separado. Aqui SI deben tocarse: son un simbolo.

    Se devuelve una sola pieza a proposito, para que la comprobacion de
    separacion no de un falso positivo: lo que no puede fundirse son los
    glifos CONTABLES, y este icono es uno solo.
    """
    return [a_rgba(ign(t, faccion, listo))[..., 3] > 0]


def hoja(faccion):
    """Tira horizontal de FRAMES celdas: 1536x96 (contrato, Resolucion)."""
    return np.hstack([a_rgba(ign(i / FRAMES, faccion, True))
                      for i in range(FRAMES)])


def main():
    raiz = dir_estado(ESTADO, VERSION)
    for fac in FACCIONES:
        # apagado: un frame, estatico. No parpadea porque no hay nada que hacer.
        Image.fromarray(a_rgba(ign(0.0, fac, False)), 'RGBA').save(
            os.path.join(raiz, f'state_unlit_{fac}.png'))
        # encendible: 16 frames en bucle
        Image.fromarray(hoja(fac), 'RGBA').save(
            os.path.join(raiz, f'state_ready_{fac}_sheet.png'))
        Image.fromarray(a_rgba(ign(0.0, fac, True)), 'RGBA').save(
            os.path.join(raiz, f'state_ready_{fac}.png'))

    ok = True
    for fac in FACCIONES:
        for listo, etiq in ((False, 'apagado'), (True, 'encendible')):
            print(f'ART-ST-IGN v1 «El interruptor» — {fac}, {etiq}')
            ok &= verifica(ign, FRAMES, _piezas,
                           bases=sprites('player', 'enemy'),
                           args=(fac, listo))
    if not ok:
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
