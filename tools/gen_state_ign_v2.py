"""NOVA - Overlay de estado `SinEncender` (ART-ST-IGN), propuesta v2: EL PEDERNAL.

Ref: NOVA_Estados_Animaciones.md 14.1 y 14.7 - NOVA_Assets_Diseno.md A.2.1 y A.3

LA MISMA SPEC, EL REGISTRO CONTRARIO. Las dos propuestas ocupan el mismo sitio,
llevan las mismas dos rampas de faccion y duran los mismos 16 frames. Lo que
cambia es de que habla el simbolo:

                        v1 El interruptor        v2 El pedernal
    Registro            convencional: UI         diegetico: una chispa
    Composicion         concentrica, cerrada     direccional, abierta hacia
                                                 arriba
    Canal del parpadeo  tono (salta de banda)    tamano (los trazos se abren
                                                 y se cierran)
    Que hay que saber   nada: el simbolo de      nada: algo esta a punto de
                        encendido es universal   prender
    Punto debil         parece UI pegada encima  es radial-ish, y lo radial ya
                                                 significa Estrella

POR QUE MERECE EXISTIR. NOVA no tiene un solo simbolo de interfaz dentro del
tablero: el nivel se lee en el sprite, la posesion en la rampa, el alcance en
un anillo de mundo. Meter un boton de encendido seria el primer icono de
aplicacion del juego, y en un tablero de rocas y estrellas eso se nota. Una
chispa saltando de la roca dice lo mismo sin salir del mundo.

Y EL COSTE, QUE ES EL REVERSO EXACTO: cualquier destello se acerca a la firma
de la Estrella, que es UNA DE LAS TRES COSAS en las que este asteroide puede
encenderse ([4.1]). Prometeria de mas. Aqui el riesgo se rebaja pero no se
elimina, y se rebaja por construccion:

  - EL ABANICO NO ES RADIAL. Los cinco trazos salen hacia arriba, entre -142 y
    -38 grados, y con largos distintos. La Estrella es isotropa y n-fold; esto
    tiene una direccion y no cierra. Un destello de ocho puntas centrado -que
    fue la primera forma de esta propuesta- si se leia como una estrella
    pequena a 1x, y por eso se descarto antes de llegar aqui.
  - LOS TRAZOS NO TOCAN EL NUCLEO. Arrancan a `R0` del centro, asi que hay
    hueco entre el punto y sus rayos: eso lee «saltando», no «irradiando». Una
    corona sale del cuerpo; una chispa ya se ha separado.

DOS LECTURAS, NO UNA. 14.1 dispara `SinEncender` con `faction != Neutral` a
secas, pero 4.1 solo deja encender con 10 de Energia: el icono parpadeaba
igual en una roca que no se puede encender todavia, y eso es una promesa que
el jugador no siempre puede cobrar. Aqui el overlay tiene dos lecturas y el
animador elige con `energy >= 10`, sin estado nuevo: la presentacion solo lee
(14.0 #1), asi que ni la maquina de estados ni la matriz de 14.6 se tocan.

    apagado      la brasa sola, quieta, un frame
    encendible   la brasa se abre en cinco trazos que crepitan, 16 frames

LA DIFERENCIA ES DE PRESENCIA, NO DE GRADO, y ademas el apagado NO PUEDE PESAR
MAS que el encendible en ningun frame: seria el estado accionable siendo el
mas callado de los dos. Medido: 141 px la brasa contra 143-196 el abanico. No
se cruzan, y por eso `K0` vale lo que vale.

EL PARPADEO ES DE TAMANO, Y EL NUCLEO NO PARTICIPA. Los trazos se abren y se
cierran entre `K0` y `K1` del largo; el punto central mide siempre lo mismo.
Asi el icono NUNCA desaparece -14.0 #5: un estado que no se ve es un bug- ni
siquiera en el frame mas cerrado, donde queda el nucleo y cinco muñones. Con
el nucleo tambien pulsando, en el minimo el overlay se quedaba en tres pixeles
y el asteroide parecia apagarse.

LOS TRAZOS DE FUERA VAN RETRASADOS. Cada par se abre `LAG` de ciclo despues
que el del medio, asi que la chispa crepita del centro hacia los lados en vez
de inflarse en bloque. Es el mismo recurso que el `zzz` de A.3.1 y el realce
del Magnetar: una onda de fase cuesta una linea y convierte un latido en un
gesto.

DOS FACCIONES, igual que la v1 y por el mismo motivo de A.2.1: la marca de
posesion del Asteroide es este overlay, no el sprite, asi que lleva el color
literal de 14.4 (#3FD7F5 y #F2456B, indice 3 de `str_p` y `str_e`).

DONDE VA. El nucleo en (53, 22) deja el centro del area ocupada en (53, 17),
que es el del `zzz` al que sustituye (A.3.1) y el de la v1: los tres simbolos
se relevan sin moverse de sitio. No pisa la roca en ningun frame, y `main` lo
comprueba contra los dos sprites.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image

from nova_core import a_rgba, bulto, dir_estado, esfera, lienzo, rampa, veta
from nova_estados import sprites, verifica

ESTADO = 'ign'
VERSION = 2
FRAMES = 16
CELDA = 96

FACCIONES = ('player', 'enemy')
RAMPAS = {'player': 'str_p', 'enemy': 'str_e'}

NUCLEO = (53.0, 22.0)   # deja el centro de lo ocupado en (53, 17): ver arriba

R = 13.0            # largo de referencia del trazo mas largo
R0 = 0.34           # arranque del trazo, en multiplos de R. El hueco es lo
                    # que hace que lea «chispa» y no «corona».
GROSOR = 1.25

# (angulo en grados, largo en multiplos de R). Ni equiespaciados ni iguales:
# un abanico regular vuelve a ser radial.
ABANICO = ((-142, 0.60), (-116, 0.90), (-90, 1.10), (-64, 0.86), (-38, 0.56))

NUCLEO_R = 0.24     # del largo de referencia. Constante: no pulsa.
# --- La brasa: la lectura «tuyo y apagado» ---------------------------------
#
# No es el nucleo del encendible en pequeño, y ese es el punto. Un icono que
# solo se diferencia por tener los trazos mas cortos se diferencia POR GRADO, y
# el grado es el fallo reconocido del escalon N3->N4 de la Estrella (A.2.2).
# Aqui la diferencia es de PRESENCIA y de MATERIAL a la vez: el apagado no
# tiene ni un trazo, y su cuerpo no es una esfera lisa sino un `bulto`
# irregular encendido por dentro. Un carbon, no una canica.
#
# Se probaron cinco: la esfera lisa (no parece un simbolo, parece un pixel
# suelto), el pedernal facetado y frio (78 px, se pierde sobre el fondo), dos
# esquirlas (68 px, leen como escombro), una llamita de tres trazos cortos
# (bonita, pero a 1x es un abanico pequeño: grado otra vez) y esta.
BRASA = (53.0, 15.0)      # centrada donde esta el centro del encendible, para
                          # que el simbolo no salte de sitio al cruzar los 10
BRASA_R = 5.6
BRASA_CALOR = 2.2   # desplazamiento de banda hacia el tono claro: el centro
                    # arde y el borde se apaga. Es lo que separa una brasa de
                    # una bola de color plano.
BRASA_PERFIL = ((3, 0.18, 1.0), (5, 0.11, 2.4))   # contorno irregular: un
                    # carbon no es redondo. `especular` no se toca: a 5.6 px
                    # de radio y con este calor no llega a marcar un pixel.
K0, K1 = 0.72, 1.0  # los trazos se cierran y se abren entre estos factores.
                    #
                    # EL SUELO DEL PARPADEO LO FIJA EL APAGADO, NO EL GUSTO. El
                    # icono encendible no puede pesar MENOS que el apagado en
                    # ningun frame: seria el estado accionable siendo el mas
                    # callado. Con K0 = 0.62 y el nucleo apagado en 0.48 pasaba
                    # exactamente eso: 120 px en el valle contra 156 px de la
                    # piedra fria. Medido, no supuesto. Ahora son 120 px
                    # apagado contra 143-196 encendible, y no se cruzan.
LAG = 0.10          # retraso de fase de cada par hacia los lados, en ciclos


def _k(t, i):
    """Factor de apertura del trazo `i` en la fase `t`."""
    f = (t - abs(i - 2) * LAG) % 1.0
    return K0 + (K1 - K0) * (0.5 + 0.5 * math.sin(2 * math.pi * f))


def ign(t=0.0, faccion='player', listo=True):
    """El overlay en la fase `t`. `listo` es `energy >= 10` (4.1).

    APAGADO: la brasa sola, quieta. Hay calor, no hay llama. `t` no se usa:
             es un asset de un frame.
    LISTO:   el nucleo mas los cinco trazos, crepitando.
    """
    lz = lienzo(CELDA)
    ramp = rampa(RAMPAS[faccion])
    cx, cy = NUCLEO
    if not listo:
        bulto(lz, BRASA[0], BRASA[1], BRASA_R, ramp, 90,
              perfil=BRASA_PERFIL, calor=BRASA_CALOR)
        return lz
    for i, (ang, largo) in enumerate(ABANICO):
        a = math.radians(ang)
        k = _k(t, i)
        veta(lz,
             (cx + math.cos(a) * R * R0, cy + math.sin(a) * R * R0),
             (cx + math.cos(a) * R * largo * k, cy + math.sin(a) * R * largo * k),
             GROSOR, ramp, 3, 20 + i, solo_dentro=False)
    esfera(lz, cx, cy, max(1.7, R * NUCLEO_R), ramp, 90)
    return lz


def _piezas(t, faccion='player', listo=True):
    """El icono es uno solo: no hay glifos contables que puedan fundirse."""
    return [a_rgba(ign(t, faccion, listo))[..., 3] > 0]


def hoja(faccion):
    """Tira horizontal de FRAMES celdas: 1536x96 (contrato, Resolucion)."""
    return np.hstack([a_rgba(ign(i / FRAMES, faccion, True))
                      for i in range(FRAMES)])


def main():
    raiz = dir_estado(ESTADO, VERSION)
    for fac in FACCIONES:
        Image.fromarray(a_rgba(ign(0.0, fac, False)), 'RGBA').save(
            os.path.join(raiz, f'state_unlit_{fac}.png'))
        Image.fromarray(hoja(fac), 'RGBA').save(
            os.path.join(raiz, f'state_ready_{fac}_sheet.png'))
        Image.fromarray(a_rgba(ign(0.0, fac, True)), 'RGBA').save(
            os.path.join(raiz, f'state_ready_{fac}.png'))

    ok = True
    for fac in FACCIONES:
        for listo, etiq in ((False, 'apagado'), (True, 'encendible')):
            print(f'ART-ST-IGN v2 «El pedernal» — {fac}, {etiq}')
            ok &= verifica(ign, FRAMES, _piezas,
                           bases=sprites('player', 'enemy'),
                           args=(fac, listo))
    if not ok:
        raise SystemExit('alguna comprobacion ha fallado')


if __name__ == '__main__':
    main()
