"""NOVA - Generador del Pulsar (ART-NOD-PUL-01..03).

Ref: NOVA_Nodos.md 4.3 · NOVA_Assets_Diseno.md A.2.3

DIRECCION. El Pulsar no genera Energia: la almacena y la gasta en poderes.
Su nivel no cambia ninguna stat, solo desbloquea poderes (1, 2 o 3). Asi que
su sprite no puede comunicar "mas potencia" -que es lo que hace la Estrella-
sino "mas poderes". La senal de nivel tiene que ser CONTABLE, no gradual.

De ahi el reparto de canales, que es lo que separa este nodo de la Estrella:

    IDENTIDAD (constante en los 3 niveles)  cuerpo pequeno y muy caliente,
                                            anillo ecuatorial con profundidad
    NIVEL     (contable de un vistazo)      1, 2 o 3 haces barridos

La Estrella fusiono identidad y nivel en el mismo canal -la atmosfera- y el
precio fue que N3 y N4 se parecen (A.2.2, riesgo conocido). Aqui no puede
pasar: uno o dos o tres haces se cuentan, no se estiman.

Anatomia, en orden de dibujo:

    1. halo             trama Bayer sobre los haces, solo N3
    2. haces            corona_radial con picos = nivel, muy cizallada
    3. anillo (atras)   mitad trasera, fina y oscura
    4. cuerpo           esfera pequena, `calor` alto: estrella de neutrones
    5. anillo (delante) mitad delantera, mas gruesa y mas clara
    6. ojos             siempre por encima de todo (14.7)

POR QUE HACES Y NO ANILLOS CONCENTRICOS. Tres anillos con inclinaciones
distintas leen como el simbolo del atomo -ya se descarto para la Estrella- y
tres anillos coplanares no se separan: en perspectiva b/a = sen(inclinacion)
es el mismo para todos los radios, asi que se tocan por arriba y por abajo y
dejan de contarse. El haz barrido, ademas, es la senal que el nombre promete:
al animar la fase, el Pulsar barre.

CUERPO PEQUENO A PROPOSITO. Es una estrella de neutrones: masa enorme en un
cuerpo diminuto. Radio 12-14 px frente a los 17-25 de la Estrella. Lo que
crece con el nivel es el alcance de los haces, no el cuerpo, porque el cuerpo
no es donde vive la informacion.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nova_core import (a_rgba, dir_nodo, anillo_orbital, corona_radial, esfera, guardar,
                       halo_trama, lienzo, rampa)

NODO = 'pulsar'
VERSION = 1

CELDA = 96
C = CELDA / 2.0
PPU = 64.0

# r      radio del cuerpo
# calor  aclarado radial del nucleo. Alto en los tres: siempre esta al rojo
# haz    alcance del haz por encima del limbo, en px
# a, b   semiejes del anillo ecuatorial
# halo   grosor de la trama exterior, o None

NIVELES = {
    1: dict(r=12, calor=2.2, haz=19, a=21, b=7,  halo=None),
    2: dict(r=13, calor=2.6, haz=22, a=23, b=8,  halo=None),
    3: dict(r=14, calor=3.2, haz=25, a=25, b=9,  halo=6),
}

# Coseno puro, por dos razones distintas.
#
# LECTURA. Los armonicos por defecto llevan un multiplo 0.5 que, con picos=1
# o 2, inyecta un lobulo de media frecuencia: el haz deja de contarse y el
# sprite se lee como una capa. Con tan pocos picos no hace falta romper la
# simetria por armonicos -un engranaje necesita muchos dientes-; aqui la
# rompe la cizalla, que es lo que exige el contrato.
#
# NUMERICA. Un armonico desfasado hace que el maximo de la onda no valga
# exactamente 1.0, sino ~0.93. `corona_radial` eleva esa onda a `dureza`, y
# con las durezas altas que pide un haz estrecho (hasta 108 en N1) 0.93**108
# es 0.0004: el alcance efectivo se desploma a r_int y el haz desaparece del
# sprite. Con un solo coseno el pico es 1.0 exacto y `r_ext` se alcanza.
ARM_HAZ = ((1.0, 1.0, 0.0),)

# Haz: pocos picos, mucha dureza (lengua estrecha) y cizalla de capa externa.
# dureza por debajo de 10 engorda la lengua y el sprite se lee como petalo.
HAZ = dict(amp=1.0, cizalla=0.55, armonicos=ARM_HAZ, sesgo_banda=0)

DUREZA_N3 = 12.0   # anchura de referencia, medida sobre el nivel 3


def _dureza(picos):
    """Dureza que mantiene la anchura angular del haz constante.

    Cerca del pico, (0.5 + 0.5*cos(n*a))**d vale aprox. exp(-d*n*n*a*a/4), o
    sea que el semiancho del haz va como 1/(n*raiz(d)). Con una dureza fija
    el haz de N1 sale tres veces mas ancho que los de N3: se derrama sobre la
    cara y tapa los ojos, que es justo lo que 14.7 prohibe. Compensarlo es
    d proporcional a 1/n**2.
    """
    return DUREZA_N3 * (3.0 / picos) ** 2


PHI = math.radians(-20.0)   # inclinacion del plano ecuatorial


def _fase_polar(picos):
    """Fase que pone el primer haz apuntando hacia arriba.

    `_onda` tiene su maximo donde `picos*ang + fase == 0`, y en pantalla el
    eje Y crece hacia abajo, asi que arriba es ang = -pi/2. Sin este anclaje
    la fase 0 deja el unico haz de N1 abajo a la derecha, justo debajo del
    anillo, donde se lee como una sombra del cuerpo y no como un haz.

    Anclado, los tres niveles comparten la misma lectura: sale un haz por el
    polo y los siguientes se reparten alrededor. Contar 1, 2, 3 deja de
    depender de donde cayera la fase.
    """
    return picos * math.pi / 2


def pulsar(nivel, faccion, t=0.0):
    """Devuelve el lienzo de un Pulsar. `t` en [0,1) para animar el barrido."""
    cfg = NIVELES[nivel]
    suf = 'p' if faccion == 'player' else 'e'
    cuerpo = rampa(f'pul_{suf}')
    ojo    = rampa('ojo')

    lz = lienzo(CELDA)
    r = cfg['r']
    # un ciclo idle barre exactamente un periodo de lengua: cierra sin salto
    fase = _fase_polar(nivel) + 2 * math.pi * t

    perfil = dict(r_int=r - 1, r_ext=r + cfg['haz'], picos=nivel,
                  dureza=_dureza(nivel), **HAZ)

    # Halo pegado al cuerpo, no siguiendo los haces. La Estrella puede
    # abrazar su corona porque tiene 15 lenguas y el glow queda continuo;
    # aqui los lobulos son tres agujas separadas y el mismo halo sale como
    # tres arcos punteados sueltos, que se leen como suciedad. Ceñido al
    # nucleo dice lo que N3 tiene que decir: "este esta al maximo".
    if cfg['halo']:
        halo_trama(lz, C, C, cuerpo, r0=r + 1, grosor=cfg['halo'],
                   banda_int=2, banda_ext=4, gamma=1.25)

    corona_radial(lz, C, C, fase=fase, ramp=cuerpo, oid=1, **perfil)

    anillo_orbital(lz, C, C, cfg['a'], cfg['b'], PHI, grosor=1.6,
                   ramp=cuerpo, oid=5, mitad='atras', sesgo_banda=2)

    esfera(lz, C, C, r, cuerpo, oid=10, calor=cfg['calor'])

    anillo_orbital(lz, C, C, cfg['a'], cfg['b'], PHI, grosor=2.2,
                   ramp=cuerpo, oid=6, mitad='delante', sesgo_banda=0)

    ro = max(3.0, r * 0.235)
    dx = r * 0.345
    dy = -r * 0.22
    esfera(lz, C - dx, C + dy, ro, ojo, oid=20)
    esfera(lz, C + dx, C + dy, ro, ojo, oid=21)

    return lz


def main():
    import numpy as np
    raiz = dir_nodo(NODO, VERSION)
    for nivel in NIVELES:
        for fac in ('player', 'enemy'):
            guardar(pulsar(nivel, fac),
                    os.path.join(raiz, f'pul_lvl{nivel}_{fac}.png'))

    def _ext(m):
        ys, xs = np.where(m)
        return max(ys.max() - ys.min(), xs.max() - xs.min()) + 1

    print(f"{'':4} {'solida':>9} {'con halo':>10}")
    for nivel in NIVELES:
        lz = pulsar(nivel, 'player')
        solido = lz['lleno'].copy()
        a = a_rgba(lz)[..., 3] > 0
        if a[0, :].any() or a[-1, :].any() or a[:, 0].any() or a[:, -1].any():
            print(f'  AVISO: N{nivel} toca el borde de la celda')
        print(f'N{nivel}: {_ext(solido) / PPU:8.2f}u {_ext(a) / PPU:9.2f}u')


if __name__ == '__main__':
    main()
