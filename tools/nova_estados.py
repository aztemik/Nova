"""NOVA - Utilidades comunes a los overlays de estado de A.3.

No hay primitivas aqui. Un overlay se dibuja con las mismas de `nova_core`
que un nodo; lo que no comparte con un nodo es COMO SE COMPRUEBA.

Un sprite de nodo se valida contra si mismo: que no toque el borde de la
celda, que no ensucie la capa `glow`, que el bucle cierre. Un overlay se
valida ademas contra OTRO asset -el sprite sobre el que se aplica- y, si es un
glifo contable, contra sus propias piezas. Eso es lo que vive aqui, para que
las propuestas de un mismo overlay se midan con la misma vara: medir cada una
a su manera es no compararlas.
"""

import os

import numpy as np
from PIL import Image

from nova_core import RAIZ, a_rgba

# El sprite de nodo por defecto: el Asteroide Neutral, que es sobre el que va
# `Dormido`. Los overlays de otro estado pasan los suyos.
ASTEROIDE = 'nodes/asteroide/v1/ast_lvl0_{}.png'


def sprites(*facciones):
    """Rutas absolutas de los sprites de Asteroide de esas facciones."""
    return [os.path.join(RAIZ, 'art', ASTEROIDE.format(f)) for f in facciones]


def _dilata(m):
    o = m.copy()
    o[1:, :] |= m[:-1, :]
    o[:-1, :] |= m[1:, :]
    o[:, 1:] |= m[:, :-1]
    o[:, :-1] |= m[:, 1:]
    return o


def verifica(fn_lienzo, frames, fn_piezas=None, bases=None, args=()):
    """Las comprobaciones de un overlay, sobre los sprites de verdad.

    `fn_lienzo(t, *args)` devuelve el lienzo del overlay en la fase `t`.
    `fn_piezas(t, *args)`, si se pasa, devuelve las mascaras de cada pieza por
    separado: sirve para exigir que un glifo contable no se funda consigo
    mismo. `bases` son las rutas de los sprites sobre los que se aplica.

    Devuelve True si todo pasa, para que el generador pueda fallar de verdad
    en vez de imprimir un aviso que nadie lee.
    """
    if bases is None:
        bases = sprites('neutral')

    cuerpos = {}
    for b in bases:
        if os.path.exists(b):
            cuerpos[os.path.basename(b)] = np.array(
                Image.open(b).convert('RGBA'))[..., 3] > 0
        else:
            print(f'  AVISO: no encuentro {b}; no compruebo solape')

    pisa = {k: 0 for k in cuerpos}
    borde = sucio = pegados = 0
    for i in range(frames):
        lz = fn_lienzo(i / frames, *args)
        a = a_rgba(lz)[..., 3] > 0
        if lz['glow'].any():
            sucio += 1
        if a[0, :].any() or a[-1, :].any() or a[:, 0].any() or a[:, -1].any():
            borde += 1
        for k, cuerpo in cuerpos.items():
            pisa[k] = max(pisa[k], int((a & cuerpo).sum()))
        if fn_piezas is not None:
            ms = fn_piezas(i / frames, *args)
            for x in range(len(ms)):
                for y in range(x + 1, len(ms)):
                    if (_dilata(ms[x]) & ms[y]).any():
                        pegados += 1

    cierra = np.array_equal(a_rgba(fn_lienzo(0.0, *args)),
                            a_rgba(fn_lienzo(1.0, *args)))
    print(f'  bucle cierra (f0 == f{frames}):      {cierra}')
    print(f'  frames con la capa glow sucia:    {sucio} de {frames}')
    print(f'  frames que tocan el borde:        {borde} de {frames}')
    for k in sorted(pisa):
        print(f'  px sobre {k:24} {pisa[k]} (peor frame)')
    if fn_piezas is not None:
        print(f'  pares de piezas que se tocan:     {pegados} en todo el ciclo')

    return (cierra and sucio == 0 and borde == 0
            and all(v == 0 for v in pisa.values()) and pegados == 0)


# --- Anclaje de ojos --------------------------------------------------------
#
# `Asustado` (14.2) es el unico overlay de A.3 que va SOBRE el cuerpo y sobre
# los CUATRO tipos de nodo. Eso lo convierte en un problema distinto: el `zzz`
# y la brasa solo tenian que caber en un hueco, y este tiene que ATERRIZAR
# encima de unos ojos que cada nodo coloca donde le conviene.
#
# Medido sobre los 34 sprites (los tonos exclusivos de la rampa `ojo`):
#
#     centro en x     47.0 - 47.5  en TODOS.  Practicamente registrado.
#     centro en y     41.1 - 45.5  la Estrella sube con el nivel.
#     separacion       9.5 - 16.0  factor 1.7 entre el Pulsar N1 y la
#                                  Estrella N5.
#     ojo mas grande  10 x 10 px   (Estrella N5)
#
# Un overlay de geometria fija NO puede registrar en los 34, y escalarlo esta
# prohibido: con `Filter Mode: Point` una escala no entera rompe el
# pixel-perfect (contrato, Resolucion; es la misma razon por la que el proton
# tiene tres sprites discretos y no escala continua, A.4.2).
#
# La salida es la misma que la del proton: TAMANOS DISCRETOS mas
# DESPLAZAMIENTO ENTERO. El overlay es un OJO, no un par: se instancia dos
# veces por nodo, cada una en su ancla, y asi la separacion y la deriva
# vertical se resuelven con enteros sin tocar el sprite.
#
# Y la forma no es redonda. Un ojo asustado es MAS ALTO, no mas ancho, y eso
# no es una licencia: el ancho lo raciona la separacion -dos ojos que se tocan
# se leen como uno- y la altura no la raciona nada. Con ojos redondos hacian
# falta dos tallas y en el Pulsar N1 la mayor no agrandaba nada; con elipses
# altas, dos formas cubren los catorce abriendo el ojo al menos 2 px en todos.
#
# (tipo, nivel) -> (talla, ancla izquierda, ancla derecha) desde el centro de
# celda, en pixeles enteros.
OJOS = {
    ('ast', 0): ('chico',  (-8, -2), (+6, -2)),
    ('str', 1): ('chico',  (-6, -4), (+5, -4)),
    ('str', 2): ('grande', (-7, -5), (+6, -5)),
    ('str', 3): ('grande', (-8, -6), (+6, -6)),
    ('str', 4): ('grande', (-8, -6), (+7, -6)),
    ('str', 5): ('grande', (-8, -6), (+8, -6)),
    ('pul', 1): ('chico',  (-6, -2), (+4, -2)),
    ('pul', 2): ('chico',  (-6, -2), (+4, -2)),
    ('pul', 3): ('chico',  (-6, -3), (+5, -3)),
    ('mag', 1): ('chico',  (-6, -2), (+6, -2)),
    ('mag', 2): ('grande', (-7, -3), (+6, -3)),
    ('mag', 3): ('grande', (-7, -3), (+6, -3)),
    ('mag', 4): ('grande', (-8, -2), (+6, -2)),
    ('mag', 5): ('grande', (-8, -2), (+6, -2)),
}

TALLAS = {'chico': (6, 8), 'grande': (8, 12)}   # ancho x alto, en pixeles

# El sprite de cada entrada. La faccion no importa: los cuatro generadores
# dibujan los ojos con la rampa `ojo`, que es la misma para los tres bandos.
SPRITE = {
    'ast': 'nodes/asteroide/v1/ast_lvl0_neutral.png',
    'str': 'nodes/estrella/v1/str_lvl{n}_player.png',
    'pul': 'nodes/pulsar/v2/pul_lvl{n}_player.png',
    'mag': 'nodes/magnetar/v1/mag_lvl{n}_neutral.png',
}


def _tonos_ojo():
    """Tonos que SOLO aparecen en la rampa `ojo`, para localizarla sin dudas."""
    from nova_paleta import CONTORNO, RAMPAS
    otros = set()
    for k, v in RAMPAS.items():
        if k != 'ojo':
            otros.update(x.upper() for x in v)
    otros.add(CONTORNO.upper())
    return np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)]
                     for h in RAMPAS['ojo'] if h.upper() not in otros], np.int16)


def mascara_ojos(ruta):
    """Los pixeles de ojo de un sprite de nodo."""
    a = np.array(Image.open(ruta).convert('RGBA'))
    rgb = a[..., :3].astype(np.int16)
    m = np.zeros(a.shape[:2], bool)
    for c in _tonos_ojo():
        m |= (np.abs(rgb - c).sum(2) == 0) & (a[..., 3] > 0)
    return m


def _islas(m):
    from collections import deque
    visto = np.zeros(m.shape, bool)
    n = 0
    for y, x in zip(*np.where(m)):
        if visto[y, x]:
            continue
        n += 1
        q = deque([(y, x)])
        visto[y, x] = True
        while q:
            cy, cx = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if (0 <= ny < m.shape[0] and 0 <= nx < m.shape[1]
                        and m[ny, nx] and not visto[ny, nx]):
                    visto[ny, nx] = True
                    q.append((ny, nx))
    return n


def verifica_ojos(fn_par, frames):
    """Las dos condiciones que definen este asset, sobre los 14 nodos reales.

    `fn_par(talla, ancla_izq, ancla_der, t)` devuelve el lienzo del par de
    ojos ya colocado.

    1. TAPA. Ni un pixel del ojo viejo puede asomar por debajo del nuevo: dos
       ojos concentricos de distinto tamano se leen como cuatro.
    2. SEPARA. El par tiene que dejar DOS islas conexas. Dos ojos que se tocan
       son un visor, y un visor no tiene expresion.
    """
    fallos = 0
    for (tipo, nivel), (talla, ai, ad) in sorted(OJOS.items()):
        ruta = os.path.join(RAIZ, 'art', SPRITE[tipo].format(n=nivel))
        viejo = mascara_ojos(ruta)
        peor_asoman = peor_islas = 0
        for i in range(frames):
            m = a_rgba(fn_par(talla, ai, ad, i / frames))[..., 3] > 0
            peor_asoman = max(peor_asoman, int((viejo & ~m).sum()))
            peor_islas = max(peor_islas, abs(_islas(m) - 2))
        mal = peor_asoman or peor_islas
        fallos += bool(mal)
        marca = '  <-- FALLA' if mal else ''
        print(f'  {tipo}{nivel} {talla:>6}: asoman {peor_asoman:2} px, '
              f'islas {"2" if not peor_islas else "!=2"}{marca}')
    print(f'  nodos que fallan: {fallos} de {len(OJOS)}')
    return fallos == 0


# --- Tintes que cubren el cuerpo -------------------------------------------
#
# A.3 parte los overlays en tres casos, y cada uno se comprueba distinto.
# `verifica` (arriba) sirve a los dos GLIFOS del Asteroide: exige cero pixeles
# sobre el cuerpo y la capa `glow` limpia. Un TINTE hace justo lo contrario:
# va ENCIMA del cuerpo por definicion y es trama Bayer por obligacion (A.3,
# «los overlays se traman, no se translucen»). Aplicarle aquella vara seria
# suspenderlo por hacer su trabajo.
#
# Lo que hay que medir en un tinte es lo que NO puede tapar. Son dos cosas, y
# las dos estan escritas en otro sitio del documento, no aqui:
#
#   1. LA CARA. 14.6 hace `Congelado` compatible con `Asustado`, y 14.2 dice
#      que el susto «siempre debe poder avisar». Un tinte que entierra los
#      ojos convierte esa casilla de la matriz en mentira.
#   2. EL CONTADOR DE NIVEL. A.8 #2 cerro que el nivel se lee SOLO en el
#      sprite. En los tres nodos congelables el contador vive en la periferia
#      y en piezas sueltas -las esquirlas del Magnetar, los frentes del
#      Pulsar-, que son islas de alfa separadas del cuerpo. Si el tinte se las
#      come, el jugador deja de saber que esta a punto de capturar, y un nodo
#      congelado es EXACTAMENTE el que esta a punto de capturar (7.3).
#
# `Congelado` se aplica a «cualquier nodo encendido» (14.1). El Asteroide
# nunca lo esta: encenderlo lo convierte en otro tipo (4.1), asi que sale de
# la lista. Son 13 sprites, no 14.
CONGELABLES = [k for k in sorted(OJOS) if k[0] != 'ast']

# `Reconvirtiendo` es mas estrecho todavia: 14.1 lo limita a «Estrella,
# Pulsar o Magnetar PROPIO», y 8.1 confirma por que -se paga con la Energia
# del propio nodo-. Son los mismos trece tipos y niveles, pero medidos sobre
# el sprite del JUGADOR y no sobre el neutral: el Magnetar neutral existe y
# dispara (3.2), pero no se reconvierte.
RECONVERTIBLES = list(CONGELABLES)

# `Capturado` es el mas ancho de todos: 14.1 lo aplica a «cualquier nodo» y
# `ChangeFaction()` puede caerle a un Asteroide dormido igual que a una
# Estrella N5. Son los CATORCE.
CAPTURABLES = sorted(OJOS)

# `FX-BUFF` dice «toda la faccion» (9.1, 14.5), pero el efecto solo le HACE
# algo a unos tipos: el Rayo Cosmico sube la cadencia del Magnetar y la carga
# del Pulsar, y la Nube de Hidrogeno el intervalo de la Estrella (9.2). El
# Asteroide no gana nada con ninguno de los dos: no dispara, no carga y no
# genera. Marcarlo seria prometerle al jugador una ventaja que ese nodo no
# tiene, que es justo lo que A.2.1 prohibe hacerle al sprite.
#
# Consecuencia util: NINGUN nodo puede llevar los dos buffs a la vez, aunque
# 9.1 permita que los dos power-ups esten activos. Un tipo o es de Rayo o es
# de Hidrogeno. Asi que el overlay nunca tiene que apilarse consigo mismo.
BUFEABLES = {
    'rayo':      [k for k in sorted(OJOS) if k[0] in ('mag', 'pul')],
    'hidrogeno': [k for k in sorted(OJOS) if k[0] == 'str'],
}

# Los buffs se miden sobre el sprite del Jugador -van sobre nodos de una
# faccion-, o sea con el mismo mapa que `Reconvirtiendo`: `SPRITE_PROPIO`,
# que se define justo debajo.

SPRITE_PROPIO = {
    'str': 'nodes/estrella/v1/str_lvl{n}_player.png',
    'pul': 'nodes/pulsar/v2/pul_lvl{n}_player.png',
    'mag': 'nodes/magnetar/v1/mag_lvl{n}_player.png',
}


def _etiqueta(m):
    """Componentes conexas 4-vecinas: devuelve (n, matriz de etiquetas)."""
    from collections import deque
    lab = np.zeros(m.shape, np.int32)
    n = 0
    for y, x in zip(*np.where(m)):
        if lab[y, x]:
            continue
        n += 1
        q = deque([(y, x)])
        lab[y, x] = n
        while q:
            cy, cx = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if (0 <= ny < m.shape[0] and 0 <= nx < m.shape[1]
                        and m[ny, nx] and not lab[ny, nx]):
                    lab[ny, nx] = n
                    q.append((ny, nx))
    return n, lab


def satelites(alfa, minimo=40):
    """Las piezas del sprite que NO tocan su cuerpo principal.

    En dos de los tres nodos congelables el contador de nivel vive fuera del
    cuerpo: las esquirlas del Magnetar y los frentes de onda del Pulsar son
    islas de alfa propias. Contarlas antes y despues del tinte es la unica
    forma honesta de saber si el nivel se sigue leyendo; medir «cuanto tapa»
    de media no lo dice, porque tapar 20 px de corona no cuesta nada y tapar
    20 px de esquirla cuesta un nivel.

    `minimo` no es un numero redondo elegido a ojo: separa dos poblaciones
    que en estos sprites no se solapan. Medido sobre los trece, una pieza de
    contador ocupa de 64 a 289 px -esquirlas 64-98, frentes 131-289- y la
    isla de trama mas grande que produce el halo de la Estrella N5 ocupa 20.
    Entre 20 y 64 no hay nada, asi que el corte cae en el hueco y no en el
    borde de ninguna de las dos.
    """
    n, lab = _etiqueta(alfa)
    if n == 0:
        return []
    tam = [(lab == i).sum() for i in range(1, n + 1)]
    principal = 1 + int(np.argmax(tam))
    return [(lab == i) for i in range(1, n + 1)
            if i != principal and tam[i - 1] >= minimo]


def verifica_tinte(fn_lienzo, frames=1, nodos=None, min_ojo=0.55,
                   min_satelite=0.50, min_distintos=None, convive_con=None,
                   bucle=True, exige_contador=True, max_frames_ciego=0,
                   entra_de_nada=True, sprite=None, args=()):
    """Lo que hay que medirle a un tinte de estado, sobre los nodos reales.

    `fn_lienzo(t, *args)` devuelve el lienzo del overlay en la fase `t`.

    Mide tres cosas por nodo -cuanta CARA sobrevive, cuanto CONTADOR DE NIVEL
    sobrevive y cuanto CONTRASTE tiene el tinte contra el nodo de debajo- y,
    si el tinte se mueve, tres mas sobre el ciclo:

      - que CIERRE, f0 identico a fN;
      - cuantos frames DISTINTOS produce de verdad. Una hoja de 16 frames que
        contiene 7 imagenes no es una animacion, es un atlas mintiendo sobre
        su tamano (contrato, *Reglas de trabajo*; se midio antes en
        `ART-ST-SCARE`, A.3.3, y alli el resultado fue no animar);
      - si convive con otro overlay. 14.6 no es decorativa: `Congelado` +
        `Infectado` es una casilla marcada «Si», y los dos son trama. Dos
        campos de Bayer apilados pueden acabar en un borron donde no se lee
        ninguno de los dos. `convive_con` es la ruta del otro overlay, y lo
        que se imprime es cuanto le tapa este a aquel.

    La union de los frames es la que se usa para las medidas de tapado: un
    pixel que se cubre en UN frame es un pixel que parpadea encima del
    contador, y eso es peor que taparlo fijo, no mejor.

    CON `bucle=False` el asset no es un estado que dura: es un EFECTO CON
    DURACION, como `Reconvirtiendo`, que son 3.0 s exactos y se acaba. Eso
    cambia tres cosas:

      - no se le exige cerrar, se le exige ENTRAR DESDE NADA Y SALIR A NADA.
        Un efecto cuyo primer o ultimo frame ya tiene pixeles aparece o
        desaparece de golpe y hace un salto contra el estado que lo rodea;
      - la union de los frames deja de servir para medir la cara. Un efecto
        que tapa el nodo un instante no «tapa la cara»: la tapa DURANTE N
        FRAMES, y lo que hay que acotar es N. Eso es `max_frames_ciego`;
      - `exige_contador=False` lo exime del contador de nivel. No es un
        favor: durante una reconversion el nivel del nodo esta cambiando
        -acaba en N1 del tipo nuevo (8.1)-, asi que no hay nada fiable que
        tapar. Es la unica exencion legitima a la regla, y solo la tiene un
        asset cuya duracion coincide con la del cambio.

    `sprite` sustituye el mapa de sprites por defecto: `Reconvirtiendo` se
    mide sobre el nodo PROPIO, no sobre el neutral.
    """
    if nodos is None:
        nodos = CONGELABLES
    mapa = sprite if sprite is not None else SPRITE

    capas = [a_rgba(fn_lienzo(i / frames, *args)) for i in range(frames)]
    tapa = np.zeros(capas[0].shape[:2], bool)
    for c in capas:
        tapa |= c[..., 3] > 0
    lum_capa = capas[0][..., :3].astype(np.float32) @ (0.2126, 0.7152, 0.0722)
    borde = any(c[..., 3][[0, -1], :].any() or c[..., 3][:, [0, -1]].any()
                for c in capas)

    # DONDE cae el overlay, que es lo que decide contra QUE compite. Un tinte
    # que vive pegado al cuerpo compite con el nodo; uno que vive en el aire
    # compite con el fondo, y contra `#0B0E1A` gana siempre -toda la rampa
    # `decaimiento` esta por encima de 87 de luminancia y el fondo esta en
    # 14-. Sin este reparto, la columna `contraste` de mas abajo se calcula
    # sobre una muestra minuscula y dice poco: un aura que solo toca el 1 %
    # del sprite puede sacar un contraste pesimo y verse perfectamente.
    # Va POR NODO, no contra la union: la union de los trece llena media
    # celda -la Estrella N5 sola ocupa `x 6-92`- y contra ella cualquier
    # overlay parece pegado al cuerpo. Sobre un Magnetar N1, que mide 18 px
    # de radio, el mismo overlay puede estar casi entero en el aire.
    al_aire = []
    for (tipo, nivel) in nodos:
        cuerpo = np.array(Image.open(os.path.join(
            RAIZ, 'art', mapa[tipo].format(n=nivel))).convert('RGBA'))[..., 3] > 0
        al_aire.append((tapa & ~cuerpo).sum() / max(int(tapa.sum()), 1))

    fallos = globales = 0
    print(f'  huella del overlay: {int(tapa.sum())} px'
          f'   toca el borde de la celda: {borde}')
    print(f'  del overlay cae al aire, contra el fondo: '
          f'{min(al_aire):.0%} (sobre el nodo mas grande) a '
          f'{max(al_aire):.0%} (sobre el mas pequeno)')

    if frames > 1:
        if bucle:
            distintos = len({c.tobytes() for c in capas})
            tope = min_distintos if min_distintos is not None else frames
        else:
            # Un efecto con duracion acaba en nada, y si ademas empieza en
            # nada esos dos frames son iguales por definicion y no cuentan.
            # Lo que tiene que ser distinto es todo lo demas. En un efecto de
            # impacto el frame 0 SI cuenta: es su pico.
            dentro = [c.tobytes() for c in (capas[1:-1] if entra_de_nada
                                            else capas[:-1])]
            distintos = len(set(dentro))
            tope = min_distintos if min_distintos is not None else len(dentro)
        if bucle:
            ok = np.array_equal(a_rgba(fn_lienzo(0.0, *args)),
                                a_rgba(fn_lienzo(1.0, *args)))
            etiqueta = f'bucle cierra (f0 == f{frames}): {ok}'
        else:
            vacio0 = not (capas[0][..., 3] > 0).any()
            vacioN = not (capas[-1][..., 3] > 0).any()
            ok = vacioN and (vacio0 or not entra_de_nada)
            etiqueta = (f'sale a nada: {vacioN}'
                        + (f', entra desde nada: {vacio0}' if entra_de_nada
                           else ' (arranca en su pico: efecto de impacto)'))
            # `distintos` cuenta solo el interior, ver arriba
        mal = (not ok) or distintos < tope
        globales += bool(mal)
        print(f'  {etiqueta} · frames distintos: {distintos} de {tope}'
              f'{"   <-- FALLA" if mal else ""}')

    if convive_con is not None:
        ruta = os.path.join(RAIZ, 'art', convive_con)
        otro = np.array(Image.open(ruta).convert('RGBA'))[..., 3] > 0
        pisa = (otro & tapa).sum() / max(int(otro.sum()), 1)
        print(f'  convivencia con {os.path.basename(convive_con)}: '
              f'le tapa el {pisa:.1%} de sus {int(otro.sum())} px')
    for (tipo, nivel) in nodos:
        ruta = os.path.join(RAIZ, 'art', mapa[tipo].format(n=nivel))
        a = np.array(Image.open(ruta).convert('RGBA'))[..., 3] > 0
        ojos = mascara_ojos(ruta)
        vive_ojo = 1.0 - (ojos & tapa).sum() / max(int(ojos.sum()), 1)
        sats = satelites(a)
        peor_sat = 1.0
        for s in sats:
            peor_sat = min(peor_sat, 1.0 - (s & tapa).sum() / int(s.sum()))
        cubre = (a & tapa).sum() / max(int(a.sum()), 1)

        # CONTRASTE. Un tinte que cae sobre un nodo del mismo tono no se ve, y
        # 14.0 #5 no admite estados que no se ven. `Congelado` dura hasta 30 s
        # (7.3): es el estado mas largo del juego, y la rampa `hielo` es cian
        # claro, o sea la familia de la Estrella del Jugador. Este numero es
        # la distancia media de luminancia entre lo que pinta el overlay y lo
        # que habia debajo, y es la unica de las tres medidas que no habla de
        # lo que el tinte tapa sino de si se ve.
        sobre_nodo = a & tapa
        if sobre_nodo.any():
            rgb = np.array(Image.open(ruta).convert('RGBA'))[..., :3]
            lum_nodo = rgb.astype(np.float32) @ (0.2126, 0.7152, 0.0722)
            dlum = float(np.abs(lum_capa - lum_nodo)[sobre_nodo].mean())
        else:
            dlum = 0.0

        if bucle:
            mal = vive_ojo < min_ojo or (
                exige_contador and sats and peor_sat < min_satelite)
            fallos += bool(mal)
            print(f'  {tipo}{nivel}: cubre {cubre:5.1%} · '
                  f'cara libre {vive_ojo:5.1%} · '
                  f'{len(sats)} sat, el peor conserva {peor_sat:5.1%} · '
                  f'contraste {dlum:5.1f}'
                  f'{"   <-- FALLA" if mal else ""}')
        else:
            # En un efecto con duracion la union no sirve: lo que importa no
            # es SI tapa la cara, es CUANTOS FRAMES la tapa. Un frame ciego
            # es un parpadeo; diez son medio segundo sin poder avisar, y 14.6
            # hace `Asustado` compatible con este estado.
            ciegos = sum(1 for c in capas
                         if (ojos & (c[..., 3] > 0)).sum() > 0.45 * ojos.sum())
            pico = max((a & (c[..., 3] > 0)).sum() for c in capas) / max(int(a.sum()), 1)
            mal = ciegos > max_frames_ciego or (
                exige_contador and sats and peor_sat < min_satelite)
            fallos += bool(mal)
            print(f'  {tipo}{nivel}: pico de tapado {pico:5.1%} del sprite · '
                  f'frames con la cara ciega: {ciegos:2} de {frames} · '
                  f'contraste {dlum:5.1f}'
                  f'{"   <-- FALLA" if mal else ""}')
    print(f'  nodos que fallan: {fallos} de {len(nodos)}'
          f'{"  ·  " + str(globales) + " comprobacion(es) global(es) fallan" if globales else ""}')
    return fallos == 0 and globales == 0 and not borde
