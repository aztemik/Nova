#!/usr/bin/env python3
"""Documento 1 del proyecto NOVA: Tabla 3, Plantilla del Documento de Diseno.

Genera `GonzalezRamirezIvan_diseño.pdf` en la raiz del proyecto a partir de
las especificaciones de `mds/` y de los PNG ya generados en `art/`.

    PYTHONPATH=.venv/lib/python3.14/site-packages python3 tools/gen_doc1.py

Todo lo que dice este documento sale de los .md o de un archivo real de
`art/`. Lo que aun no existe se declara en la seccion 16 y no se rellena.
"""

import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import nova_pdf as P                                        # noqa: E402
from nova_pdf import (ACENTO, CEBRA, CIAN, LINEA, MAGENTA,   # noqa: E402
                      PROFUNDO, SUAVE, TINTA, TITULO, Doc, ancho)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(RAIZ, "art")
SALIDA = os.path.join(RAIZ, "GonzalezRamirezIvan_diseño.pdf")


def png(*partes):
    return Image.open(os.path.join(ART, *partes))


# ==========================================================================
# Figuras. Se componen aqui, no se recortan a mano.
# ==========================================================================
def eyes_asustado(base, tipo, nivel):
    """Compone el overlay de susto sobre un nodo con su anclaje real.

    `nova_estados.OJOS` da la talla y el desplazamiento entero de cada ojo
    desde el centro de la celda; el sprite del ojo viene centrado, asi que
    el desplazamiento se corrige con media talla.
    """
    import nova_estados as NE
    talla, ai, ad = NE.OJOS[(tipo, nivel)]
    w, h = NE.TALLAS[talla]
    ojo = png("states", "scare", "v1", f"state_scared_{talla}.png")
    salida = base.convert("RGBA")
    for anc in (ai, ad):
        capa = Image.new("RGBA", salida.size, (0, 0, 0, 0))
        capa.paste(ojo, (anc[0] + w // 2, anc[1] + h // 2))
        salida = Image.alpha_composite(salida, capa)
    return salida


def frames(hoja, indices):
    """Recorta frames de una hoja de 96 px de celda."""
    return [hoja.crop((i * 96, 0, (i + 1) * 96, 96)) for i in indices]


def encima(base, overlay):
    return Image.alpha_composite(base.convert("RGBA"), overlay.convert("RGBA"))


def construye_figuras(doc):
    """Registra todas las imágenes del documento y devuelve sus claves."""
    f = {}
    ast = {v: png("nodes", "asteroide", "v1", f"ast_lvl0_{v}.png")
           for v in ("neutral", "player", "enemy")}
    str_ = {(n, v): png("nodes", "estrella", "v1", f"str_lvl{n}_{v}.png")
            for n in range(1, 6) for v in ("player", "enemy")}
    pul = {(n, v): png("nodes", "pulsar", "v2", f"pul_lvl{n}_{v}.png")
           for n in range(1, 4) for v in ("player", "enemy")}
    mag = {(n, v): png("nodes", "magnetar", "v1", f"mag_lvl{n}_{v}.png")
           for n in range(1, 6) for v in ("neutral", "player", "enemy")}

    # Los cuatro tipos juntos, que es la lectura que el jugador tiene que
    # resolver de un vistazo.
    f["Fcuatro"] = doc.registra("Fcuatro", P.tira(
        [ast["neutral"], str_[(3, "player")], pul[(2, "player")],
         mag[(3, "player")]], factor=4, hueco=18, margen=14))

    f["Fast"] = doc.registra("Fast", P.tira(
        [ast["neutral"], ast["player"], ast["enemy"]], factor=4, hueco=20))
    f["Fstr"] = doc.registra("Fstr", P.tira(
        [str_[(n, "player")] for n in range(1, 6)], factor=3, hueco=8))
    f["Fpul"] = doc.registra("Fpul", P.tira(
        [pul[(n, "player")] for n in range(1, 4)], factor=4, hueco=14))
    f["Fmag"] = doc.registra("Fmag", P.tira(
        [mag[(n, "neutral")] for n in range(1, 6)], factor=3, hueco=8))

    # Paridad de facciones: misma geometria, otra rampa.
    f["Ffac"] = doc.registra("Ffac", P.rejilla([
        [str_[(4, "player")], pul[(3, "player")], mag[(4, "player")],
         ast["player"]],
        [str_[(4, "enemy")], pul[(3, "enemy")], mag[(4, "enemy")],
         ast["enemy"]]], factor=3, hueco=10))

    # Estados: cada overlay sobre un nodo real, como se veria en partida.
    est = [
        encima(ast["neutral"], png("states", "sleep", "v2",
                                   "state_sleep.png")),
        encima(ast["player"], png("states", "ign", "v2",
                                  "state_ready_player.png")),
        eyes_asustado(str_[(3, "player")], "str", 3),
        encima(str_[(3, "player")], png("states", "frozen", "v3",
                                        "state_frozen_overlay.png")),
        encima(mag[(3, "player")], png("states", "decay", "v2",
                                       "state_decay.png")),
        encima(str_[(3, "player")], png("states", "conv", "v2",
                                        "state_convert_player.png")),
        encima(str_[(3, "player")], png("states", "cap", "v2",
                                        "state_captured.png")),
        encima(mag[(3, "player")], png("states", "buff", "v1",
                                       "state_buff_rayo.png")),
    ]
    f["Fest"] = doc.registra("Fest", P.rejilla(
        [est[:4], est[4:]], factor=3, hueco=12))

    # Mas arte de estados: el mismo overlay sobre nodos distintos, el par
    # normal/asustado, el ciclo de captura y el galon de power-up.
    frozen = png("states", "frozen", "v3", "state_frozen_overlay.png")
    f["Ffrozen"] = doc.registra("Ffrozen", P.tira(
        [encima(str_[(5, "player")], frozen),
         encima(pul[(3, "player")], frozen),
         encima(mag[(4, "neutral")], frozen),
         encima(str_[(2, "enemy")], frozen)], factor=3, hueco=12))

    caras = [("ast", 0, ast["neutral"]), ("str", 2, str_[(2, "player")]),
             ("pul", 1, pul[(1, "player")]), ("mag", 5, mag[(5, "enemy")])]
    f["Fscare"] = doc.registra("Fscare", P.rejilla(
        [[b for _, _, b in caras],
         [eyes_asustado(b, t, n) for t, n, b in caras]],
        factor=5, hueco=16))

    hoja_cap = png("states", "cap", "v2", "state_captured_sheet.png")
    f["Fcap"] = doc.registra("Fcap", P.tira(
        [encima(str_[(3, "player")], fr) for fr in frames(hoja_cap, range(5))],
        factor=3, hueco=10))

    f["Fbuff"] = doc.registra("Fbuff", P.tira(
        [encima(mag[(4, "player")], png("states", "buff", "v1",
                                        "state_buff_rayo.png")),
         encima(pul[(3, "player")], png("states", "buff", "v1",
                                        "state_buff_rayo.png")),
         encima(str_[(4, "player")], png("states", "buff", "v1",
                                         "state_buff_hidrogeno.png"))],
        factor=4, hueco=16))

    f["Fpu"] = doc.registra("Fpu", P.tira(
        [png("world", "world_drop_halo.png"),
         png("ui", "ui_pu_cosmicray.png"),
         png("ui", "ui_pu_hydrogen.png")], factor=3, hueco=20))

    # Fondos: se reducen por factor entero para no romper la trama.
    for n in (1, 2, 3):
        im = png("_preview", "fondos", f"s{n}_tablero.png")
        f[f"Fbg{n}"] = doc.registra(
            f"Fbg{n}", im.resize((im.width // 2, im.height // 2), Image.BOX))

    # La hoja de paleta viene en vertical (22 rampas x 7 tonos). Girada,
    # ocupa una banda ancha en vez de media pagina.
    f["Fpal"] = doc.registra("Fpal", png(
        "_preview", "preview_paleta.png").transpose(Image.ROTATE_270))

    f["Flogo"] = doc.registra("Flogo", P.sobre_fondo(
        Image.open(os.path.join(RAIZ, "mds", "logoUTP.png")), "#FFFFFF"))
    return f


# ==========================================================================
# Diagramas vectoriales
# ==========================================================================
def caja(doc, x, y, w, h, titulo, sub=None, relleno="#FFFFFF",
         borde=ACENTO, color_texto=TITULO, tam=8.6):
    doc.rect(x, y, w, h, relleno)
    r, g, b = P.rgb(borde)
    doc.op.append(f"{r:.3f} {g:.3f} {b:.3f} RG 0.9 w "
                  f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re S")
    cy = y + h / 2 + (2.2 if sub else -tam * 0.35)
    doc.texto(titulo, x + (w - ancho(titulo, "B", tam)) / 2, cy, "B", tam,
              color_texto)
    if sub:
        doc.texto(sub, x + (w - ancho(sub, "R", 7.0)) / 2, cy - 9.4, "R", 7.0,
                  SUAVE)


def flecha(doc, x1, y1, x2, y2, etiqueta=None, color=SUAVE, doble=False):
    r, g, b = P.rgb(color)
    doc.op.append(f"{r:.3f} {g:.3f} {b:.3f} RG 0.8 w "
                  f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    for (px, py, a) in ([(x2, y2, ang)] +
                        ([(x1, y1, ang + math.pi)] if doble else [])):
        p = 4.2
        doc.op.append(
            f"{r:.3f} {g:.3f} {b:.3f} rg "
            f"{px:.2f} {py:.2f} m "
            f"{px - p * math.cos(a - 0.42):.2f} "
            f"{py - p * math.sin(a - 0.42):.2f} l "
            f"{px - p * math.cos(a + 0.42):.2f} "
            f"{py - p * math.sin(a + 0.42):.2f} l f")
    if etiqueta:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        w = ancho(etiqueta, "R", 6.8)
        doc.rect(mx - w / 2 - 2.5, my - 3.2, w + 5, 9.2, "#FFFFFF")
        doc.texto(etiqueta, mx - w / 2, my, "R", 6.8, SUAVE)


def ruta(doc, puntos, etiqueta=None, en=0.5, color=SUAVE, desvio=0):
    """Polilinea ortogonal con punta al final. `en` situa la etiqueta a lo
    largo del ultimo tramo; `desvio` la aparta en perpendicular."""
    import math
    r, g, b = P.rgb(color)
    trazo = f"{puntos[0][0]:.2f} {puntos[0][1]:.2f} m " + " ".join(
        f"{x:.2f} {y:.2f} l" for x, y in puntos[1:])
    doc.op.append(f"{r:.3f} {g:.3f} {b:.3f} RG 0.8 w {trazo} S")
    (x1, y1), (x2, y2) = puntos[-2], puntos[-1]
    a = math.atan2(y2 - y1, x2 - x1)
    pt = 4.2
    doc.op.append(
        f"{r:.3f} {g:.3f} {b:.3f} rg {x2:.2f} {y2:.2f} m "
        f"{x2 - pt * math.cos(a - 0.42):.2f} "
        f"{y2 - pt * math.sin(a - 0.42):.2f} l "
        f"{x2 - pt * math.cos(a + 0.42):.2f} "
        f"{y2 - pt * math.sin(a + 0.42):.2f} l f")
    if etiqueta:
        mx = x1 + (x2 - x1) * en - math.sin(a) * desvio
        my = y1 + (y2 - y1) * en + math.cos(a) * desvio
        w = ancho(etiqueta, "R", 6.8)
        doc.rect(mx - w / 2 - 2.5, my - 2.6, w + 5, 9.0, "#FAFBFD")
        doc.texto(etiqueta, mx - w / 2, my, "R", 6.8, SUAVE)


def diagrama_estados(doc):
    """Grafo de estados de pantalla. Fuente: 10.3, 13.1 y 13.6 del maestro,
    mas las pantallas inventariadas en A.6."""
    alto = 250
    doc.sitio(alto + 14)
    doc.y -= alto
    b = doc.y
    x0, W = doc.ml, doc.ancho_util
    doc.rect(x0, b, W, alto, "#FAFBFD")

    w, h = 108, 32
    cx = x0 + W / 2
    y_men, y_sel, y_par, y_fin = b + alto - 42, b + alto - 104, b + 96, b + 22
    x_pau = x0 + 16

    caja(doc, cx - w / 2, y_men, w, h, "Menú principal", "Arranque del juego")
    caja(doc, cx - w / 2, y_sel, w, h, "Selección de nivel", "3 mapas x 3")
    caja(doc, cx - w / 2, y_par, w, h, "Partida", "HUD permanente",
         relleno="#EAF8FC")
    caja(doc, x_pau, y_par, w - 16, h, "Menú de pausa",
         "El juego se detiene")
    caja(doc, cx - w - 20, y_fin, w, h, "Victoria", "Siguiente / Repetir")
    caja(doc, cx + 20, y_fin, w, h, "Derrota", "Reintentar / Mapa",
         borde="#C9425F")

    m = h / 2
    # Bajada central
    ruta(doc, [(cx, y_men), (cx, y_sel + h)], "Jugar")
    ruta(doc, [(cx, y_sel), (cx, y_par + h)], "Nivel elegido")
    # Partida <-> pausa
    ruta(doc, [(cx - w / 2, y_par + m), (x_pau + w - 16, y_par + m)], "Esc")
    ruta(doc, [(x_pau + w - 16, y_par + m - 10),
               (cx - w / 2, y_par + m - 10)], "Reanudar")
    # Pausa -> mapa, por la izquierda
    ruta(doc, [(x_pau + (w - 16) / 2, y_par + h),
               (x_pau + (w - 16) / 2, y_sel + m),
               (cx - w / 2, y_sel + m)], "Volver al mapa", en=0.55)
    # Partida -> fin
    ruta(doc, [(cx - w / 4, y_par), (cx - w / 4, y_fin + h + 16),
               (cx - w / 2 - 20, y_fin + h + 16),
               (cx - w / 2 - 20, y_fin + h)], "Enemigo sin nodos", en=0.4,
         desvio=-16)
    ruta(doc, [(cx + w / 4, y_par), (cx + w / 4, y_fin + h + 16),
               (cx + w / 2 + 20, y_fin + h + 16),
               (cx + w / 2 + 20, y_fin + h)], "Sin nodos o estancamiento",
         en=0.4, desvio=16)
    # Fin -> mapa, por la derecha
    ruta(doc, [(cx + 20 + w, y_fin + m), (x0 + W - 12, y_fin + m),
               (x0 + W - 12, y_sel + m), (cx + w / 2, y_sel + m)],
         "Siguiente / Volver al mapa", en=0.62)
    doc.y -= 10


def diagrama_progreso(doc):
    """Flujo de los 3 mapas x 3 niveles (11.1 y 11.2)."""
    alto = 132
    doc.sitio(alto + 14)
    doc.y -= alto
    base = doc.y
    x0 = doc.ml
    W = doc.ancho_util
    doc.rect(x0, base, W, alto, "#FAFBFD")

    mapas = [
        ("MAPA 1 - Sistema Interior", "1  2  3",
         "Envío, captura, Estrella, Magnetar, mejoras"),
        ("MAPA 2 - El Cinturón", "4  5  6",
         "Púlsar, Cero Absoluto, Decaimiento, Magnetar neutral"),
        ("MAPA 3 - Espacio Profundo", "7  8  9",
         "Agujero de Gusano, reconversión, IA agresiva"),
    ]
    w = (W - 2 * 16 - 2 * 26) / 3
    x = x0 + 16
    for i, (titulo, niveles, mecanicas) in enumerate(mapas):
        doc.rect(x, base + 30, w, 74, "#FFFFFF")
        r, g, b = P.rgb(ACENTO)
        doc.op.append(f"{r:.3f} {g:.3f} {b:.3f} RG 0.9 w "
                      f"{x:.2f} {base + 30:.2f} {w:.2f} 74 re S")
        doc.rect(x, base + 30 + 74 - 3, w, 3, CIAN)
        doc.texto(titulo, x + (w - ancho(titulo, "B", 7.4)) / 2,
                  base + 88, "B", 7.4, TITULO)
        # Los tres niveles como circulos numerados
        for j, n in enumerate(niveles.split()):
            ccx = x + w / 2 + (j - 1) * 30
            doc.rect(ccx - 10, base + 62, 20, 18, "#EAF8FC")
            doc.texto(n, ccx - ancho(n, "B", 9.5) / 2, base + 67, "B", 9.5,
                      ACENTO)
        for k, linea in enumerate(doc.corta(mecanicas, "R", 6.8, w - 10)):
            doc.texto(linea, x + (w - ancho(linea, "R", 6.8)) / 2,
                      base + 48 - k * 8.6, "R", 6.8, SUAVE)
        if i < 2:
            flecha(doc, x + w + 4, base + 67, x + w + 22, base + 67)
        x += w + 26

    pie = ("Sin progresión entre niveles: cada uno arranca desde cero. Lo "
           "único que persiste es el nivel máximo desbloqueado.")
    doc.texto(pie, x0 + (W - ancho(pie, "I", 7.4)) / 2, base + 13, "I", 7.4,
              SUAVE)
    doc.y -= 10


# ==========================================================================
# Portada
# ==========================================================================
def portada(doc, fig):
    W, H = doc.w, doc.h
    doc.rect(0, 0, W, H, "#FFFFFF")

    def centrado(texto, y, estilo, tam, color, track=0.0):
        w = ancho(texto, estilo, tam) + track * (len(texto) - 1)
        doc.texto(texto, (W - w) / 2, y, estilo, tam, color,
                  seguimiento=track)

    w_px, h_px, _ = doc.imagenes["Flogo"]
    lw = 96
    lh = lw * h_px / w_px
    doc.dibuja_imagen("Flogo", (W - lw) / 2, H - 120 - lh, lw, lh)

    y = H - 120 - lh - 38
    centrado("UNIVERSIDAD TECNOLÓGICA DE PUEBLA", y, "B", 12.5, TITULO, 1.7)
    y -= 19
    centrado("Desarrollo de Software Multiplataforma", y, "R", 9.8, SUAVE,
             0.4)

    y -= 24
    doc.linea(W / 2 - 52, y, W / 2 + 52, y, CIAN, 1.6)

    y -= 78
    centrado("NOVA", y, "B", 54, TITULO, 13)
    y -= 30
    centrado("Conquista de sistemas estelares", y, "R", 13.5, ACENTO, 1.2)
    y -= 26
    centrado("Documento de Diseño de Videojuego", y, "R", 8.6, SUAVE, 2.2)

    # Bloque de datos: las dos columnas se centran como un solo bloque, no
    # cada una por su cuenta, o el conjunto queda descuadrado del eje.
    datos = [
        ("Materia", "Creación de Videojuegos"),
        ("Entregable", "Producto 1. Documentos del proyecto de Videojuego"),
        ("Alumno", "Ivan Gonzalez Ramirez"),
        ("Grado y grupo", "10.° “C”"),
        ("Docente", "Jose Francisco Espinosa Garita"),
        ("Cuatrimestre", "Septiembre - Diciembre 2026"),
        ("Fecha de entrega", "19 de septiembre de 2026"),
    ]
    sep = 16
    w_et = max(ancho(e, "R", 9) for e, _ in datos)
    w_va = max(ancho(v, "B", 9) for _, v in datos)
    x0 = (W - (w_et + sep + w_va)) / 2
    x_va = x0 + w_et + sep

    y -= 92
    doc.linea(x0 - 24, y, x_va + w_va + 24, y, LINEA, 0.6)
    y -= 32
    for etiqueta, valor in datos:
        doc.texto(etiqueta, x_va - sep - ancho(etiqueta, "R", 9), y, "R", 9,
                  SUAVE)
        doc.texto(valor, x_va, y, "B", 9, TITULO)
        y -= 20
    doc.linea(x0 - 24, y + 8, x_va + w_va + 24, y + 8, LINEA, 0.6)


# ==========================================================================
# Contenido
# ==========================================================================
def indice_y_versiones(doc):
    doc.h1("", "Contenido")
    entradas = [
        ("1", "Concepto"), ("2", "Visión general del juego"),
        ("3", "Mecánica del juego"), ("4", "Estados del juego"),
        ("5", "Interfaces"), ("6", "Niveles"), ("7", "Progreso del juego"),
        ("8", "Personajes"), ("9", "Enemigos"), ("10", "Habilidades"),
        ("11", "Armas"), ("12", "Items"), ("13", "Imágenes de concepto"),
        ("14", "Miembros del equipo"), ("15", "Detalles de producción"),
        ("16", "Alcance no cubierto en esta entrega"),
    ]
    col = doc.ancho_util / 2
    arriba = doc.y
    for i, (n, titulo) in enumerate(entradas):
        cx = doc.ml + (0 if i < 8 else col)
        cy = arriba - (i % 8) * 15.5 - 4
        doc.texto(n, cx + (14 - ancho(n, "B", 9)), cy, "B", 9, ACENTO)
        doc.texto(titulo, cx + 22, cy, "R", 9, TINTA)
    doc.y = arriba - 8 * 15.5 - 12

    doc.h1("", "Historial de versiones")
    doc.parrafo(
        "Mantengo el historial porque el documento de diseño cambia todo el "
        "tiempo y necesito saber qué cambió y por qué. La plantilla advierte "
        "que este apartado no se incluye en una versión enviada a revisión "
        "externa, para que nadie juzgue la idea por la fecha; aquí sí va, "
        "porque es un entregable académico y el proceso forma parte de lo "
        "que se evalúa.")
    doc.tabla(
        ["Versión", "Alcance del cambio"],
        [["0.1", "Concepto inicial: conquista de nodos con tema de "
                 "astrofísica, un jugador contra IA."],
         ["1.0", "Especificación completa: economía, protones, poderes del "
                 "Púlsar, reconversión, power-ups, 9 niveles, condiciones de "
                 "victoria, 26 casos borde y arquitectura en Unity."],
         ["1.1", "División en seis documentos por materia (reglas, nodos, IA, "
                 "estados, inventario de arte y seguimiento) conservando la "
                 "numeración original de cada sección. Cierre del arte de "
                 "los 4 nodos y de los 9 estados: 49 de 95 assets."]],
        [0.13, 0.87], tam=8.6, negrita_col0=True)
    doc.nota(
        "El número de versión es un número y no una fecha, como pide la "
        "plantilla. Un cambio menor sube el decimal; uno que obligue a "
        "rehacer el arte o las reglas subiría el entero.")


def concepto(doc, fig):
    doc.h1("1", "Concepto")
    campos = [
        ("Título", "NOVA — Conquista de sistemas estelares."),
        ("Estudio / Diseñador", "Ivan Gonzalez Ramirez. Proyecto individual: "
         "diseño, programación, arte y documentación."),
        ("Género", "Estrategia en tiempo real de conquista de nodos. Un "
         "jugador humano contra una IA. Sin multijugador y sin red."),
        ("Plataforma", "Computadora personal, Windows y Linux. Pantalla "
         "única en 16:9, sin desplazamiento de cámara. Se juega con el "
         "ratón; del teclado solo se usa Esc."),
        ("Versión", "1.1"),
        ("Sinopsis de jugabilidad y contenido",
         "El jugador controla un conjunto de cuerpos celestes en un sistema "
         "estelar. Cada cuerpo almacena Energía, el único recurso del juego. "
         "Enviar Energía de un cuerpo a otro lanza un Protón que viaja en "
         "línea recta: si llega a un cuerpo aliado lo recarga, y si llega a "
         "uno rival o neutral le resta Energía hasta que cambia de bando. "
         "Hay cuatro tipos de cuerpo —Asteroide, Estrella, Púlsar y "
         "Magnetar— y solo la Estrella genera Energía, de modo que perder "
         "todas las Estrellas es perder la partida a plazo. El Púlsar lanza "
         "tres poderes y el Magnetar derriba protones en vuelo. El contenido "
         "son 9 niveles repartidos en 3 mapas, cada uno con su fondo y su "
         "perfil de IA. El objetivo de cada nivel es que no quede en el "
         "tablero ningún cuerpo del Enemigo ni ningún Asteroide neutral."),
        ("Categoría",
         "La referencia de género es JellyGo! (AvoxGames), de donde tomo el "
         "bucle de enviar unidades entre nodos para capturarlos. NOVA se "
         "separa de él en tres puntos. En JellyGo todos los nodos son "
         "iguales; aquí hay cuatro tipos con papeles excluyentes. Allí la "
         "unidad enviada es un enjambre; aquí es un único Protón con una "
         "Carga visible que un Magnetar puede desgastar en vuelo. Y allí un "
         "nodo tomado se queda como está; aquí puede reconvertirse a otro "
         "tipo pagando con su propia Energía. El resultado es un juego que "
         "se decide por composición del tablero y no por velocidad de clic."),
        ("Licencia",
         "Obra original, no basada en ningún libro ni película. La "
         "estructura de 3 mapas × 3 niveles la hace ampliable: un cuarto "
         "mapa son un tipo de nodo y tres niveles más, sin tocar la "
         "arquitectura, porque todo el balance vive en ScriptableObjects."),
        ("Mecánica",
         "El jugador hace cinco cosas: seleccionar un nodo propio, enviar su "
         "Energía a otro nodo, encender un Asteroide eligiendo en qué se "
         "convierte, mejorar un nodo de nivel y reconvertirlo a otro tipo. "
         "Todo con el ratón. Se detalla en la sección 3."),
        ("Tecnología",
         "Motor Unity 2D con C#, ScriptableObjects para todo el balance y "
         "TextMeshPro para los números. El arte no se dibuja: se calcula. El "
         "proyecto incluye un pipeline propio en Python 3.14 con NumPy y "
         "Pillow —30 generadores sobre 4 módulos de biblioteca— en el que "
         "cada sprite es una función que devuelve una matriz de píxeles y el "
         "PNG es una salida derivada. La especificación se mantiene en "
         "Markdown. Como apoyo uso un asistente de IA para revisar "
         "consistencia entre documentos y acelerar código repetitivo; las "
         "decisiones de diseño y su verificación son mías. El editor de "
         "sonido queda por elegir."),
        ("Público",
         "Jugador casual con paciencia para pensar, no para reaccionar: "
         "alguien que disfruta leyendo un tablero y decidiendo a dónde "
         "mandar lo que tiene, y que no quiere invertir más de cuatro "
         "minutos por partida. No exige reflejos ni conocimiento previo del "
         "género, porque cada mapa introduce sus mecánicas en el primero de "
         "sus tres niveles."),
    ]
    for etiqueta, cuerpo in campos:
        doc.campo(etiqueta, cuerpo)
    doc.espacio(4)
    doc.figura(fig["Fcuatro"], 340,
               "Los cuatro tipos de nodo, en sprites definitivos y a escala "
               "4x sobre el fondo real del juego. De izquierda a derecha: "
               "Asteroide neutral, Estrella nivel 3, Púlsar nivel 2 y "
               "Magnetar nivel 3.", numero=1)


def vision(doc):
    doc.h1("2", "Visión general del juego")
    doc.parrafo(
        "NOVA es un juego de estrategia que se entiende en diez segundos y "
        "no se agota en diez minutos. Una sola regla lo sostiene: solo la "
        "Estrella genera Energía. A partir de ahí toda la partida es la "
        "misma pregunta repetida —dónde pongo lo poco que tengo— y esa "
        "pregunta nunca tiene la misma respuesta, porque el tablero cambia "
        "mientras se contesta.")
    doc.parrafo(
        "Tres decisiones lo separan del género. La primera: expandirse "
        "cuesta dos veces, diez de Energía para capturar un Asteroide y "
        "otros diez para encenderlo. Ese doble peaje convierte la primera "
        "Estrella en la jugada más importante de la partida y hace que un "
        "Asteroide propio sin encender sea capital muerto. La segunda: la "
        "Energía se puede destruir. Un Magnetar que derriba un Protón no lo "
        "devuelve ni lo entrega, lo borra del juego, y eso da a la defensa "
        "un peso que no tendría si solo bloqueara. La tercera: la "
        "reconversión. Un nodo ya encendido puede cambiar de tipo pagando "
        "con su propia Energía y volviendo a nivel 1 —tres segundos "
        "indefenso y toda la inversión de nivel perdida—, y existe para que "
        "quedarse sin Estrellas no sea todavía una derrota.")
    doc.parrafo(
        "Todo lo demás está al servicio de que eso se lea sin números. El "
        "nivel de un nodo se ve en su sprite: la Estrella crece y arde más, "
        "el Púlsar añade un frente de onda por nivel y el Magnetar añade una "
        "esquirla capturada, siempre en el mismo sitio, de modo que contar "
        "el nivel es contar piezas. Todos los nodos tienen cara, y cuando a "
        "uno le llega un Protón capaz de capturarlo abre mucho los ojos y "
        "tiembla. Esa señal funciona igual en los nodos del Jugador, en los "
        "del Enemigo y en los neutrales, y es la información que más veces "
        "se lee por partida.")
    doc.parrafo(
        "El Enemigo no hace trampa: ejecuta las mismas acciones legales que "
        "el jugador, con la misma tabla de costes, y todo lo que hace pasa "
        "por la misma interfaz que los comandos humanos. Entre mapas solo "
        "cambian sus parámetros de decisión —cada cuánto piensa, cuánto "
        "arriesga y cuánto ruido aleatorio altera su evaluación—. Retirar "
        "ese ruido poco a poco es lo que lleva a la IA de torpe a "
        "implacable sin escribir un algoritmo distinto.")
    doc.parrafo(
        "En una pantalla fija, sin texto y sin tutorial, se ve todo lo que "
        "está pasando y aun así no es obvio qué hay que hacer. Una partida "
        "dura lo que un descanso, y la que se pierde se pierde por una "
        "decisión que el jugador puede señalar.")


def mecanica(doc, fig):
    doc.h1("3", "Mecánica del juego")
    doc.parrafo(
        "Estas son las acciones del jugador, en el orden en que aparecen en "
        "una partida real.")
    doc.tabla(
        ["#", "Acción", "Cómo se hace", "Qué ocurre"],
        [["1", "Seleccionar",
          "Clic izquierdo sobre un nodo propio. Arrastre en vacío para "
          "selección múltiple.",
          "El nodo queda marcado. Se pueden acumular varios orígenes."],
         ["2", "Enviar al 50 %",
          "Con la selección activa, clic izquierdo sobre el destino. El "
          "arrastre origen-destino hace lo mismo.",
          "Cada origen lanza su propio Protón con la mitad de su Energía, "
          "redondeada hacia abajo. La Energía sale del nodo en el mismo "
          "frame."],
         ["3", "Enviar al 100 %",
          "Doble clic izquierdo sobre el destino.",
          "El origen queda a cero. Es la maniobra de evacuación: ceder un "
          "nodo vacío en vez de uno lleno."],
         ["4", "Encender",
          "Clic derecho sobre un Asteroide propio con 10 de Energía y "
          "elección en el menú radial.",
          "Consume los 10 y el Asteroide pasa a nivel 1 de Estrella, Púlsar "
          "o Magnetar, con 0 de Energía."],
         ["5", "Mejorar",
          "Clic derecho sobre un nodo propio y botón de mejora.",
          "Sube un nivel dentro del mismo tipo. El coste se paga con la "
          "Energía del propio nodo."],
         ["6", "Cargar y lanzar un poder",
          "Clic izquierdo sobre un Púlsar propio, ranura de la rueda, y clic "
          "sobre un objetivo en alcance.",
          "La carga drena la Energía del Púlsar poco a poco; una vez al "
          "100 % el poder espera indefinidamente hasta que se lanza."],
         ["7", "Reconvertir",
          "Clic derecho sobre un nodo propio y destino en el panel.",
          "Tres segundos de animación en los que el nodo no hace nada pero "
          "si puede ser capturado. Acaba como nivel 1 del tipo nuevo."]],
        [0.04, 0.16, 0.38, 0.42], tam=8.2, alineados=["c", "i", "i", "i"],
        negrita_col0=False)

    campos = [
        ("Cámara", "2D con vista cenital ortográfica, fija y sin "
         "desplazamiento. El área jugable mide 32 x 18 unidades de mundo y "
         "coincide exactamente con una cámara ortográfica de tamaño 9 en "
         "16:9, así que el nivel entero cabe siempre en pantalla. Sin scroll: "
         "el jugador decide a dónde manda su Energía viendo el tablero "
         "completo."),
        ("Periféricos", "Ratón y teclado. El ratón hace todo el juego: "
         "seleccionar, enviar, arrastrar, abrir paneles y apuntar poderes. "
         "Del teclado solo se usa Esc, para la pausa. Sin soporte de gamepad "
         "ni de micrófono."),
        ("Controles", "Clic izquierdo: seleccionar nodo propio, o enviar el "
         "50 % si ya hay selección. Doble clic izquierdo: enviar el 100 %. "
         "Arrastre desde un nodo propio: equivale al envío del 50 %. "
         "Arrastre en vacío: lazo de selección múltiple. Clic derecho sobre "
         "un nodo: panel de información, mejora y reconversión. Clic derecho "
         "en vacío: cancelar selección o cerrar el panel. Esc: menú de "
         "pausa."),
        ("Puntaje", "NOVA no tiene marcador de puntos ni tabla comparativa, "
         "ni local ni en línea: un marcador premiaría la rapidez, y NOVA se "
         "gana componiendo el tablero. El único registro es binario, qué "
         "niveles se han completado. En pantalla, la barra de poder inferior "
         "compara en todo momento la Energía total de los dos bandos; crece "
         "desde la izquierda para el Jugador y desde la derecha para el "
         "Enemigo, y es puramente informativa: no tiene ningún efecto de "
         "juego."),
        ("Guardar / Cargar", "No hay guardado a mitad de nivel ni sistema de "
         "contraseñas. Lo único que persiste entre sesiones es el nivel "
         "máximo desbloqueado, que se escribe en el almacenamiento local del "
         "equipo cuando se gana un nivel. Cada nivel arranca desde cero, dura "
         "entre 90 y 240 segundos y se reinicia entero desde el menú de "
         "pausa."),
    ]
    for etiqueta, cuerpo in campos:
        doc.campo(etiqueta, cuerpo)


def estados(doc):
    doc.h1("4", "Estados del juego")
    doc.parrafo(
        "El juego tiene seis estados de pantalla y las transiciones entre "
        "ellos son todas explícitas. El diagrama recoge qué las provoca y "
        "adónde llevan.")
    diagrama_estados(doc)
    doc.espacio(4)
    doc.tabla(
        ["Estado", "Qué muestra", "Cómo se entra", "Cómo se sale"],
        [["Menú principal", "Título y acceso al mapa de niveles.",
          "Arranque del juego.", "Jugar lleva a la selección de nivel."],
         ["Selección de nivel",
          "Los 9 niveles en 3 mapas, con los no desbloqueados en "
          "bloqueo.", "Desde el menú principal, desde la pausa o al terminar "
          "un nivel.", "Elegir un nivel desbloqueado carga la partida."],
         ["Partida", "El tablero y el HUD permanente descrito en la sección "
          "5.", "Al cargar un nivel.",
          "Esc abre la pausa; cumplir la condición de victoria o de derrota "
          "lleva a la pantalla de fin."],
         ["Menú de pausa", "Reanudar, reiniciar el nivel y volver al mapa. "
          "El juego se detiene.", "Tecla Esc durante la partida.",
          "Reanudar vuelve a la partida; reiniciar recarga el nivel desde "
          "cero."],
         ["Victoria", "Resultado y botones Siguiente y Repetir.",
          "El Enemigo se queda sin ningún nodo.",
          "Siguiente carga el nivel recien desbloqueado; Repetir reinicia "
          "el actual."],
         ["Derrota", "Resultado y botones Reintentar y Volver al mapa.",
          "El Jugador se queda sin nodos, o sin Estrellas y con menos de 10 "
          "de Energía total.",
          "Reintentar reinicia el nivel desde cero."]],
        [0.15, 0.27, 0.29, 0.29], tam=8.0, negrita_col0=True)
    doc.nota(
        "La derrota por estancamiento fue una regla que tuve que añadir al "
        "cerrar el diseño: sin ella existe una partida en la que el jugador "
        "sigue vivo pero es matemáticamente incapaz de volver a crecer, y "
        "esa partida no termina nunca. Solo se comprueba si además no tiene "
        "protones en vuelo ni poderes cargados.")


def interfaces(doc, fig):
    doc.h1("5", "Interfaces")
    doc.parrafo(
        "La apariencia está cerrada como contrato. Todo es pixel art sobre "
        "fondo profundo #0B0E1A, con una paleta de 22 rampas de siete tonos "
        "en la que la luz tiende al blanco cálido y la sombra converge "
        "siempre a índigo o ciruela: es lo que hace que veintidós rampas "
        "distintas se lean como una sola. Tres colores llevan significado "
        "de juego y no se usan para nada más: cian #3FD7F5 es el Jugador, "
        "magenta #F2456B es el Enemigo "
        "y gris #8A93A6 es lo neutral. A esos se suman los colores de "
        "estado -cian helado para Congelado, verde para Infectado- y los de "
        "los dos power-ups. Un fondo no puede usar ninguno de ellos: los "
        "fondos se pintan con tres rampas que no significan nada, porque un "
        "fondo pintado con un color de juego le miente al jugador durante "
        "toda la partida.")
    doc.figura(fig["Fpal"], 440,
               "Las 22 rampas de la paleta, una por columna. Cada material es "
               "una rampa de siete tonos ordenada de arriba abajo, de más "
               "claro a más oscuro; el tono superior, el índice 0, queda "
               "reservado al punto especular.", numero=2)

    pantallas = [
        ("H.U.D. de partida",
         "Es la única interfaz que está siempre presente. Ocupa los bordes y "
         "deja el centro libre, porque el centro es el tablero. Lleva cuatro "
         "elementos: la barra de poder a lo ancho de la parte inferior, con "
         "dos colores que crecen desde los extremos y comparan la Energía "
         "total de cada bando; el cronómetro y el botón de pausa arriba a la "
         "derecha; y el identificador de nivel arriba a la izquierda, con el "
         "formato Mapa 2 - Nivel 5. Sobre cada nodo, en TextMeshPro y no "
         "horneado en el sprite, va su Energía actual, que no se oculta "
         "nunca en ningún estado.",
         "Partida. No invoca ninguna otra pantalla salvo la pausa."),
        ("Panel de información (clic derecho)",
         "Aparece sobre cualquier nodo al pulsar el botón derecho y contiene "
         "seis bloques en orden fijo: tipo y nivel, Energía actual sobre el "
         "tope, velocidad de ataque, botón de mejora con su coste, botones "
         "de reconversión con los tres destinos posibles y, si el nodo es un "
         "Púlsar propio, la rueda de poderes. Sobre un nodo enemigo muestra "
         "solo los tres primeros bloques. El botón de mejora, cuando no hay "
         "Energía suficiente, se muestra deshabilitado y con el coste en "
         "rojo, nunca oculto: el jugador necesita saber cuánto le falta.",
         "Partida. Puede invocar el menú radial de encendido y la rueda de "
         "poderes."),
        ("Menú radial de encendido",
         "Tres opciones -Estrella, Púlsar, Magnetar- alrededor de un "
         "Asteroide propio que ya tiene 10 de Energía. Es el único momento "
         "en que el jugador elige qué va a ser un nodo.",
         "Partida, desde el panel de información de un Asteroide propio."),
        ("Rueda de poderes del Púlsar",
         "Tres ranuras en orden fijo: 1 Cero Absoluto, 2 Decaimiento, 3 "
         "Agujero de Gusano. Las que el nivel del Púlsar aún no desbloquea "
         "aparecen con candado y el nivel requerido. Al iniciar una carga "
         "aparece una barra bajo el nodo; con el poder cargado la ranura "
         "brilla y el cursor pasa a modo de apuntado.",
         "Partida, sobre un Púlsar propio."),
        ("Mapa de selección de nivel",
         "Los 9 niveles agrupados en sus 3 mapas, con los no "
         "desbloqueados bloqueados. Es la pantalla que lee el progreso "
         "guardado.",
         "Menú principal, menú de pausa y pantallas de fin de nivel."),
        ("Pantallas de victoria y derrota",
         "Resultado del nivel y dos botones. En victoria, Siguiente y "
         "Repetir; en derrota, Reintentar y Volver al mapa.",
         "Partida, al cumplirse la condición correspondiente. Invocan el "
         "mapa de selección o recargan la partida."),
    ]
    doc.h2("Pantallas")
    doc.tabla(
        ["Nombre de la pantalla", "Descripción", "Estados del juego"],
        [[n, d, e] for n, d, e in pantallas],
        [0.19, 0.55, 0.26], tam=8.0, negrita_col0=True)
    doc.figura(fig["Fbg1"], 430,
               "Imagen de la pantalla de juego: el fondo definitivo de la "
               "mapa 1 con una mezcla de nodos reales encima, en la "
               "proporción que pide el diseño de niveles de ese mapa. La "
               "capa de interfaz todavía no tiene arte definitivo.",
               numero=3)
    doc.nota(
        "Los tres fondos cumplen un presupuesto de contraste que verifico "
        "sobre el PNG terminado: la luminancia media de cualquier ventana de "
        "96 x 96 píxeles -el tamaño de la celda de un nodo- queda por debajo "
        "del tono más oscuro de un cuerpo de nodo. Si el fondo local lo "
        "supera, el lado en sombra de un nodo pasa a ser más oscuro que el "
        "cielo y el nodo deja de leerse como un objeto iluminado para "
        "leerse como un agujero recortado.")


def niveles(doc, fig):
    doc.h1("6", "Niveles")
    doc.parrafo(
        "Hay 9 niveles en 3 mapas de 3. No hay progresión entre ellos: "
        "cada nivel arranca desde cero, con la repartición inicial que fija "
        "su definición. Lo que sube es la dificultad, y sube por tres vías a "
        "la vez: la ventaja inicial del Enemigo, la calidad de su IA y la "
        "geometría del tablero. Una condición que ningún nivel puede romper: "
        "el jugador debe tener siempre al menos un Asteroide neutral "
        "a menos de 5 unidades de su posición inicial y alcanzable antes de "
        "que el Enemigo llegue a él. Sin esa garantía un nivel puede ser "
        "imposible desde el primer segundo, y eso no es dificultad.")
    doc.tabla(
        ["Niv.", "Mapa", "Nodos", "El Jugador inicia con",
         "El Enemigo inicia con", "Ast.", "Neutrales especiales", "Objetivo"],
        [["1", "1", "5", "Estrella(1)", "Estrella(1)", "3", "-", "90 s"],
         ["2", "1", "7", "Estrella(1)", "Estrella(2)", "5", "-", "110 s"],
         ["3", "1", "8", "Estrella(1), Asteroide",
          "Estrella(2), Magnetar(1)", "4", "-", "130 s"],
         ["4", "2", "9", "Estrella(1)", "Estrella(2), Púlsar(1)", "6", "-",
          "150 s"],
         ["5", "2", "10", "Estrella(1), Magnetar(1)",
          "Estrella(2), Púlsar(1)", "6", "1 Magnetar(2)", "170 s"],
         ["6", "2", "11", "Estrella(2)",
          "Estrella(3), Púlsar(2), Magnetar(2)", "6", "1 Magnetar(3)",
          "190 s"],
         ["7", "3", "12", "Estrella(1) x2",
          "Estrella(3), Púlsar(3), Magnetar(3)", "7", "1 Magnetar(3)",
          "210 s"],
         ["8", "3", "13", "Estrella(2)",
          "Estrella(3) x2, Púlsar(3), Magnetar(3)", "7", "2 Magnetar(3)",
          "230 s"],
         ["9", "3", "14", "Estrella(2), Magnetar(1)",
          "Estrella(4) x2, Púlsar(3) x2, Magnetar(4)", "7", "2 Magnetar(4)",
          "240 s"]],
        [0.055, 0.065, 0.06, 0.20, 0.24, 0.05, 0.145, 0.085], tam=7.6,
        alineados=["c", "c", "c", "i", "i", "c", "i", "c"])
    doc.nota(
        "Los niveles todavía no tienen nombre propio. El HUD los identifica "
        "por mapa y número, con el formato Mapa 2 - Nivel 5, y las "
        "coordenadas exactas de cada nivel son trabajo del Producto 2. Las "
        "fichas que siguen desarrollan un nivel por mapa: el primero, el "
        "de en medio y el último.")

    fichas = [
        ("Mapa 1 - Nivel 1  ·  Sistema Interior",
         [("Encuentro",
           "Es el primer nivel del juego y hace de tutorial sin texto. Se "
           "llega a el nada más empezar; es el único nivel desbloqueado en "
           "una instalación nueva."),
          ("Descripción",
           "Cinco nodos en un sistema interior polvoriento, barrido por la "
           "luz de un sol que queda fuera del encuadre. Repartición "
           "simétrica: una Estrella de nivel 1 para cada bando y tres "
           "Asteroides neutrales entre ambas. Ningún bando arranca con "
           "Magnetar ni con Púlsar, así que al principio no hay protones "
           "que derribar ni poderes que lanzar: todo lo que pasa en "
           "pantalla es enviar y capturar."),
          ("Objetivos",
           "Que no quede en el mapa ningún nodo del Enemigo. No hay "
           "acertijos ni enemigos concretos que derrotar: el Enemigo es la "
           "facción entera."),
          ("Progreso",
           "Al ganar, los Asteroides neutrales que queden pasan "
           "automáticamente al Jugador en una cascada de 3 segundos, de más "
           "cercano a más lejano, y se desbloquea el nivel 2."),
          ("Enemigos",
           "Una Estrella nivel 1 del Enemigo, gobernada por el perfil de IA "
           "del mapa 1: decide cada 3 segundos, con umbral de acción "
           "alto, agresividad 0.7 y un ruido de más menos 25 % que la hace "
           "equivocarse a menudo. No usa evacuación ni reconversión y no "
           "prioriza power-ups."),
          ("Items",
           "Hasta 3 power-ups. El primero cae a los 25 segundos y los "
           "siguientes cada 40 a 55 segundos."),
          ("Personajes",
           "Asteroide y Estrella en la repartición inicial. El Púlsar y el "
           "Magnetar solo llegan al tablero si el jugador decide "
           "encender uno.")]),
        ("Mapa 2 - Nivel 5  ·  El Cinturón",
         [("Encuentro",
           "Segundo nivel del mapa 2. Se llega tras completar el 4, que "
           "es donde el Enemigo estrena el Púlsar."),
          ("Descripción",
           "Diez nodos bajo una corriente de escombro que cruza el cielo "
           "combada. Es el primer nivel en el que el Jugador arranca con un "
           "Magnetar propio y el primero con un Magnetar neutral de nivel 2 "
           "en el mapa: ese nodo dispara a los protones de los dos bandos y "
           "bloquea un corredor entero hasta que alguien lo tome. Con 100 de "
           "tope y resistencia doble, tomarlo cuesta el doble que cualquier "
           "otro nodo, y por eso el nivel se decide en si merece la pena."),
          ("Objetivos",
           "Que no quede ningún nodo del Enemigo. El Magnetar neutral no "
           "hace falta capturarlo para ganar: la cascada de conquista lo "
           "resuelve."),
          ("Progreso",
           "Cascada de conquista, desbloqueo del nivel 6 y pantalla de "
           "victoria con Siguiente y Repetir."),
          ("Enemigos",
           "Una Estrella nivel 2 y un Púlsar nivel 1 del Enemigo, con el "
           "perfil del mapa 2: decide cada 2 segundos, agresividad 1.0, "
           "ruido de más menos 15 %, prioriza los Asteroides marcados con "
           "power-up y ya sabe evacuar un nodo antes de perderlo."),
          ("Items",
           "Hasta 4 power-ups. El primero a los 30 segundos y los siguientes "
           "cada 50 a 70 segundos."),
          ("Personajes",
           "Los cuatro: Asteroide, Estrella, Púlsar y Magnetar, este último "
           "en sus tres facciones.")]),
        ("Mapa 3 - Nivel 9  ·  Espacio Profundo",
         [("Encuentro",
           "Es el último nivel del juego. Se llega tras completar los ocho "
           "anteriores."),
          ("Descripción",
           "Catorce nodos en un cielo casi vacío, donde la única referencia "
           "de escala es una galaxia del tamaño de una uña. El Enemigo "
           "arranca con dos Estrellas de nivel 4, dos Púlsares de nivel 3 "
           "-es decir, con los tres poderes disponibles, incluido el Agujero "
           "de Gusano- y un Magnetar de nivel 4. El Jugador empieza con una "
           "Estrella de nivel 2 y un Magnetar de nivel 1. Dos Magnetares "
           "neutrales de nivel 4 parten el mapa en corredores."),
          ("Objetivos",
           "Que no quede ningún nodo del Enemigo. En la práctica obliga a "
           "reconvertir al menos una vez y a usar el Agujero de Gusano para "
           "robar un nodo de nivel alto, porque capturarlo a base de "
           "protones no da tiempo."),
          ("Progreso",
           "Fin del juego. Pantalla de victoria; no hay nivel siguiente que "
           "desbloquear."),
          ("Enemigos",
           "Dos Estrellas nivel 4, dos Púlsares nivel 3 y un Magnetar nivel "
           "4, con el perfil del mapa 3: decide cada 1.2 segundos, "
           "umbral de acción bajo, agresividad 1.3 y ruido de solo más menos "
           "5 %. Usa evacuación y reconversión."),
          ("Items",
           "Hasta 5 power-ups. El primero a los 35 segundos y los siguientes "
           "cada 60 a 85 segundos."),
          ("Personajes",
           "Los cuatro tipos, en todos los niveles y en las tres "
           "facciones.")]),
    ]
    for titulo, campos in fichas:
        doc.h2(titulo)
        for etiqueta, cuerpo in campos:
            doc.campo(etiqueta, cuerpo, ancho_etiqueta=78, tam=8.8)


def progreso(doc):
    doc.h1("7", "Progreso del juego")
    doc.parrafo(
        "El juego tiene un único modo y una sola línea de progreso. Los "
        "nueve niveles se recorren en orden y cada mapa introduce sus "
        "mecánicas en el primero de sus tres niveles, para que los otros dos "
        "sirvan de práctica antes de que llegue la siguiente.")
    diagrama_progreso(doc)
    doc.tabla(
        ["Paso", "Qué ocurre"],
        [["1", "Menú principal. Solo el nivel 1 está desbloqueado en una "
               "instalación nueva."],
         ["2", "Mapa 1, niveles 1 a 3. Se aprende el bucle completo: "
               "enviar, capturar, encender, mejorar, y defender con el "
               "Magnetar."],
         ["3", "Mapa 2, niveles 4 a 6. Entran el Púlsar con Cero Absoluto "
               "y Decaimiento, y los Magnetares neutrales que bloquean "
               "corredores para los dos bandos."],
         ["4", "Mapa 3, niveles 7 a 9. Entran el Agujero de Gusano, la "
               "reconversión y la IA sin ruido de decisión."],
         ["5", "Al ganar un nivel se guarda el nivel máximo desbloqueado y "
               "se ofrece pasar al siguiente. Al perderlo se puede "
               "reintentar sin límite."]],
        [0.07, 0.93], tam=8.4, alineados=["c", "i"], negrita_col0=True)


def personajes(doc, fig):
    doc.h1("8", "Personajes")
    doc.parrafo(
        "Los personajes de NOVA son los cuatro tipos de nodo: cada uno es "
        "una regla distinta del juego, con cara. Los cuatro tienen ojos, "
        "porque la señal que más veces se lee por partida es que un nodo "
        "los abra mucho al ver llegar un Protón capaz de capturarlo.")
    doc.parrafo(
        "Dos nodos no se separan repintándolos: si comparten silueta, "
        "simetría, material y composición, se siguen pareciendo con "
        "cualquier paleta. Por eso cada nodo se comprobó contra los "
        "anteriores sobre nueve ejes de construcción antes de dibujarlo. "
        "Ningún par comparte más de tres de los nueve, y el peor caso "
        "—Magnetar y Asteroide, que coinciden en simetría e idle— se "
        "distingue en los seis restantes. Una propuesta completa del "
        "Púlsar se descartó por este criterio: funcionaba, pero compartía "
        "con la Estrella los cinco ejes que deciden la lectura.")
    doc.tabla(
        ["Eje de construcción", "Estrella", "Púlsar", "Magnetar",
         "Asteroide"],
        [["Silueta", "disco con púas", "reloj de arena",
          "cúmulo: cuerpo y satélites", "contorno orgánico irregular"],
         ["Simetría", "radial, centrada", "bilateral sobre eje a 32°",
          "ninguna (ángulo áureo)", "ninguna"],
         ["Material", "banda sólida y halo", "trama sobre luz",
          "materia facetada, vetas", "superficie cóncava, mate"],
         ["Composición", "isotrópica", "direccional, diagonal",
          "dispersa, centrífuga", "excéntrica, por puntos"],
         ["Luz propia", "sí", "sí", "sí (vetas)", "ninguna"],
         ["Contador de nivel", "púas radiales", "frentes de onda",
          "esquirlas capturadas", "no tiene: un solo nivel"]],
        [0.17, 0.20, 0.21, 0.22, 0.20], tam=7.6, negrita_col0=True)

    personajes_datos = [
        ("Asteroide", "Fast", 190, [
            ("Descripción",
             "Una roca muerta, apaleada, de contorno orgánico irregular y "
             "acabado mate. Es el único nodo del juego que no enseña un solo "
             "píxel de luz propia: su píxel más claro es un reflejo. Tiene "
             "los ojos cerrados, dos rendijas inclinadas en espejo, y en "
             "reposo es el único del reparto que no te mira. La superficie "
             "está picada de cráteres, que son el único accidente cóncavo "
             "del juego: todo lo demás abulta."),
            ("Concepto",
             "Es capital muerto, y el sprite lo dice sin un solo símbolo: "
             "no genera, no dispara, no envía y solo espera a que alguien "
             "pague por él. Sin veta incandescente ni chispa. La partida "
             "se apoya en que el jugador pague 10 por capturarlo y otros "
             "10 por encenderlo sin que el objeto le prometa nada; la "
             "promesa la hace el menú de encendido."),
            ("Encuentro",
             "En los nueve niveles y desde el primer segundo. Es el nodo más "
             "numeroso de la partida: entre 3 y 7 por nivel."),
            ("Habilidades",
             "Encendido: un Asteroide propio con 10 de Energía puede "
             "convertirse en Estrella, Púlsar o Magnetar de nivel 1, "
             "consumiendo los 10 y quedando a cero. Es su única acción y es "
             "la única fuente de nodos nuevos del juego."),
            ("Items",
             "Es el único nodo sobre el que caen los power-ups, y solo "
             "mientras es neutral."),
            ("No jugable",
             "Mientras es neutral no lo controla nadie. Su papel es ser el "
             "terreno que los dos bandos se disputan y el peaje que hay que "
             "pagar para crecer."),
        ]),
        ("Estrella", "Fstr", 380, [
            ("Descripción",
             "Un cuerpo esférico con atmósfera de dos capas: una cromosfera "
             "de quince lenguas cortas y casi rectas, y por debajo una "
             "corona de seis lenguas largas y barridas, desfasadas media "
             "longitud de onda para que no se alineen. El núcleo se blanquea "
             "al subir de nivel. Cinco niveles, de enana apagada sin corona "
             "a gigante con halo."),
            ("Concepto",
             "Es el único generador de Energía del juego y por tanto el "
             "objetivo prioritario de los dos bandos. Toda la partida se "
             "ordena alrededor de esta regla: un bando sin Estrellas está "
             "condenado a plazo, porque su Energía total solo puede bajar. "
             "El nivel tenía que leerse de un vistazo -si el jugador no "
             "distingue una nivel 1 de una nivel 4, no puede priorizar- y "
             "por eso la escalera es la más visible de las cuatro."),
            ("Encuentro",
             "En los nueve niveles. Los dos bandos arrancan siempre con al "
             "menos una."),
            ("Habilidades",
             "Genera 1 punto de Energía cada intervalo, hasta su tope de 50, "
             "y al llenarse se detiene. El nivel acelera el intervalo: de "
             "2.00 segundos en el nivel 1 a 0.85 en el 5, lo que traduce en "
             "100 y 43 segundos para llenarse desde cero. También envía "
             "Energía a cualquier nodo."),
            ("Armas", "Ninguna. No dispara ni lanza poderes."),
            ("Items",
             "La Nube de Hidrógeno le acelera la generación un 50 % durante "
             "20 segundos."),
        ]),
        ("Púlsar", "Fpul", 260, [
            ("Descripción",
             "Un faro, no una bola que irradia. Gira tan rápido que se "
             "achata, y lo único que el universo ve de él son dos conos de "
             "luz que barren. Toda la composición se organiza alrededor de "
             "un eje inclinado 32 grados, y ninguna otra pieza del juego "
             "tiene una diagonal. Los conos son luz y no materia: no hacen "
             "silueta, no llevan contorno y no cuentan para el área "
             "clicable. Los ojos van horizontales aunque el cuerpo este "
             "inclinado, porque la criatura mira de frente y es la máquina "
             "que la rodea la que gira."),
            ("Concepto",
             "Es el nodo táctico. No genera nada: almacena Energía y la "
             "gasta como munición. Su nivel no cambia ninguna estadística, "
             "solo desbloquea poderes, así que la señal de nivel tenía que "
             "ser contable y no gradual: son arcos abiertos hacia fuera, uno "
             "por nivel, y un arco abierto es el dibujo universal de algo "
             "que se aleja del emisor."),
            ("Encuentro",
             "Desde el nivel 4, donde el Enemigo estrena uno de nivel 1. El "
             "Jugador puede encender el suyo desde el nivel 1 si decide "
             "gastar en el sus primeros 10 de Energía."),
            ("Habilidades",
             "Carga y lanza un poder cada vez, de los tres que se describen "
             "en la sección 10. Tope de 100 de Energía y envío a cualquier "
             "nodo. Un Púlsar de nivel 3 conserva el acceso a los tres "
             "poderes, pero solo puede tener uno cargado a la vez."),
            ("Armas",
             "El proyectil de poder: viaja a 6 unidades por segundo y ningún "
             "Magnetar puede derribarlo."),
            ("Items", "El Rayo Cósmico le acelera la carga un 50 %."),
        ]),
        ("Magnetar", "Fmag", 380, [
            ("Descripción",
             "Un cuerpo colapsado y tallado, de siete caras planas y aristas "
             "duras, partido por vetas incandescentes que son sus temblores "
             "de estrella. A su alrededor flotan las esquirlas que su campo "
             "arrancó a lo que pasó cerca. No irradia: atrapa. Es el único "
             "nodo sin un solo píxel de resplandor: su silueta y su área "
             "clicable son la misma figura, así que no promete área que no "
             "se pueda pulsar."),
            ("Concepto",
             "Es la defensa, y el único nodo que existe también en versión "
             "neutral: dispara a los dos bandos y bloquea un corredor "
             "entero hasta que alguien lo tome, lo que lo convierte en la "
             "herramienta central para diseñar la geometría de un nivel. "
             "Cada esquirla orbita al radio de alcance de su nivel, así "
             "que la correlación entre nivel y alcance es una consecuencia "
             "aritmética del generador. Su reparto sigue el ángulo áureo, "
             "el de las semillas de un girasol: deja fija cada pieza, de "
             "modo que subir de nivel añade una esquirla donde antes no "
             "había nada en vez de mover todas."),
            ("Encuentro",
             "Desde el nivel 3 en manos del Enemigo. La primera versión "
             "neutral aparece en el nivel 5."),
            ("Habilidades",
             "Dispara al Protón hostil más cercano a su centro y le resta 2 "
             "puntos de Carga por disparo; si la Carga llega a cero el "
             "Protón desaparece y esa Energía se pierde del juego. El nivel "
             "mejora radio -de 2.0 a 3.6 unidades- y cadencia -de 1.0 a 3.2 "
             "disparos por segundo-. Resistencia doble: cada punto de Carga "
             "hostil que le impacta le resta solo medio punto de Energía."),
            ("Armas",
             "Un haz instantáneo, de su centro al Protón. Un disparo afecta "
             "a un solo Protón; no hay daño en área."),
            ("Items", "El Rayo Cósmico le acelera la cadencia un 50 %."),
        ]),
    ]
    pies = {
        "Fast": "Asteroide, las tres facciones. La geometría no cambia entre "
                "bandos: solo la rampa de color.",
        "Fstr": "Estrella, niveles 1 a 5. La corona aparece en el nivel 2, se "
                "alarga en el 3, el núcleo se vuelve blanco en el 4 y el 5 "
                "añade halo.",
        "Fpul": "Púlsar, niveles 1 a 3. El contador de nivel son los frentes "
                "de onda: uno, dos y tres.",
        "Fmag": "Magnetar, niveles 1 a 5. Cada nivel añade una esquirla en un "
                "sitio fijo que antes estaba vacío.",
    }
    n = 4
    for nombre, clave, w, campos in personajes_datos:
        doc.h2(nombre, reserva=w * 0.42 + 120)
        doc.figura(fig[clave], w, pies[clave], numero=n)
        n += 1
        for etiqueta, cuerpo in campos:
            doc.campo(etiqueta, cuerpo, ancho_etiqueta=76, tam=8.8)
    return n


def enemigos(doc, fig, n):
    doc.h1("9", "Enemigos")
    doc.parrafo(
        "El Enemigo no es un reparto aparte: usa exactamente los mismos "
        "cuatro tipos de nodo que el Jugador, con la misma geometría y solo "
        "otra rampa de color. Esa paridad es una regla dura del diseño y no "
        "un detalle de producción. El Enemigo y el Jugador comparten el "
        "mismo conjunto de acciones legales y la misma tabla de costes, y "
        "todo comando de ambos pasa por la misma interfaz; está prohibido "
        "que la IA toque energía, niveles o estados por vías que el jugador "
        "no tenga. Lo único que los distingue es quien decide.")
    doc.figura(fig["Ffac"], 300,
               "Paridad de facciones. Arriba el Jugador en cian, abajo el "
               "Enemigo en magenta. Misma llamada de geometría, otra rampa: "
               "comprobado byte a byte sobre los 34 sprites de nodo.",
               numero=n)
    n += 1
    campos = [
        ("Nombre", "El Enemigo, la facción magenta. En el código es una sola "
         "entidad que gobierna todos sus nodos."),
        ("Descripción",
         "Físicamente son los mismos Asteroides, Estrellas, Púlsares y "
         "Magnetares descritos en la sección 8, en magenta #F2456B. Su "
         "comportamiento es un ciclo de decisión que se repite cada tantos "
         "segundos: toma una instantánea del tablero, comprueba si alguno de "
         "sus nodos está amenazado y responde, y si no lo está genera una "
         "lista de acciones candidatas, las puntúa y ejecuta la mejor si "
         "supera su umbral. Nunca actúa más de una vez por ciclo, y eso es a "
         "propósito: lo hace legible y evita ráfagas inhumanas."),
        ("Encuentro", "En los nueve niveles. Es el oponente único del juego."),
        ("Habilidades",
         "Las mismas siete acciones del jugador -atacar, encender, mejorar, "
         "reforzar, cargar poder, lanzar poder y reconvertir-, más tres "
         "respuestas defensivas: reforzar un nodo amenazado con el 50 % de "
         "otro, congelar el origen del ataque si tiene Cero Absoluto "
         "cargado, y evacuar. La evacuación es lo que hace que se sienta "
         "inteligente: cuando el refuerzo no llega a tiempo, vacía el nodo "
         "amenazado y cede una carcasa en lugar de un nodo lleno."),
        ("Armas", "Las mismas: protones y, si tiene Púlsar, los tres poderes."),
        ("Items",
         "Los mismos dos power-ups, que recoge encendiendo el Asteroide "
         "marcado antes que el Jugador. Desde el mapa 2 los prioriza "
         "explícitamente en su función de puntuación."),
    ]
    for etiqueta, cuerpo in campos:
        doc.campo(etiqueta, cuerpo, ancho_etiqueta=76, tam=8.8)

    doc.h2("Perfiles de dificultad por mapa")
    doc.parrafo(
        "No escribí tres IA. Escribí una y tres juegos de parámetros. El "
        "mecanismo que más trabaja es el ruido de decisión, que altera al "
        "azar la puntuación final: es lo que hace que la IA del mapa 1 "
        "se sienta torpe sin necesidad de un algoritmo distinto, y retirarlo "
        "poco a poco es lo que la vuelve implacable al final.")
    doc.tabla(
        ["Parámetro", "Mapa 1", "Mapa 2", "Mapa 3"],
        [["Intervalo de decisión", "3.0 s", "2.0 s", "1.2 s"],
         ["Umbral de acción", "40", "25", "10"],
         ["Multiplicador de agresividad", "0.7", "1.0", "1.3"],
         ["Usa evacuación", "No", "Sí", "Sí"],
         ["Usa reconversión", "No", "No", "Sí"],
         ["Prioriza power-ups", "No", "Sí", "Sí"],
         ["Ruido de decisión", "± 25 %", "± 15 %", "± 5 %"]],
        [0.34, 0.22, 0.22, 0.22], tam=8.2,
        alineados=["i", "c", "c", "c"], negrita_col0=True)
    doc.nota(
        "La IA tiene prohibido ver los protones antes de que se lancen, "
        "conocer el poder que el jugador está cargando antes de que la barra "
        "sea visible, generar Energía extra e ignorar tiempos de carga o de "
        "reconversión. Son cuatro prohibiciones escritas y con test propio, "
        "porque una IA que hace trampa deja de enseñar a jugar.")
    return n


def habilidades(doc, fig, n):
    doc.h1("10", "Habilidades")
    doc.parrafo(
        "Fuera de las acciones comunes, hay siete habilidades en el juego. "
        "Tres son pasivas y propias de un tipo de nodo; tres son los poderes "
        "del Púlsar; y una, la reconversión, la tienen todos los nodos ya "
        "encendidos.")
    doc.tabla(
        ["Habilidad", "Quién la tiene", "Qué hace", "Coste"],
        [["Generación", "Estrella",
          "Suma 1 de Energía cada intervalo, hasta el tope de 50. Es la "
          "única fuente de Energía del juego.", "Ninguno"],
         ["Intercepción", "Magnetar",
          "Dispara al Protón hostil más cercano a su centro y le resta 2 de "
          "Carga. A cero, el Protón desaparece y su Energía se pierde.",
          "Ninguno"],
         ["Resistencia doble", "Magnetar",
          "Cada punto de Carga hostil le resta solo medio punto de Energía. "
          "Un refuerzo aliado, en cambio, entra 1:1.", "Ninguno"],
         ["Encendido", "Asteroide propio",
          "Lo convierte en Estrella, Púlsar o Magnetar de nivel 1 con 0 de "
          "Energía.", "10"],
         ["Reconversión", "Estrella, Púlsar y Magnetar propios",
          "Cambia el tipo del nodo y lo devuelve a nivel 1, conservando la "
          "Energía sobrante. Dura 3 s, durante los cuales el nodo no hace "
          "nada pero sí puede ser capturado.",
          "20 desde Estrella o Púlsar; 30 desde Magnetar"],
         ["Mejora", "Cualquier nodo encendido",
          "Sube un nivel dentro del mismo tipo.",
          "Según tipo y nivel; 150 en total para Estrella y Magnetar, 75 "
          "para Púlsar"]],
        [0.16, 0.19, 0.47, 0.18], tam=8.0, negrita_col0=True)

    doc.h2("Los tres poderes del Púlsar")
    doc.parrafo(
        "El Púlsar carga un solo poder a la vez. Mientras carga, su Energía "
        "baja de forma continua y la barra de carga sube acoplada a ella: si "
        "se queda sin Energía la carga se pausa en el porcentaje alcanzado y "
        "se reanuda sola en cuanto reciba más, sin perder lo invertido. Una "
        "vez al 100 %, el poder espera indefinidamente hasta que se lanza. "
        "Cancelar una carga devuelve la mitad de lo invertido.")
    doc.tabla(
        ["Poder", "Nivel", "Coste", "Carga", "Alcance", "Efecto"],
        [["Cero Absoluto", "1", "20", "8 s", "7 u",
          "Congela el nodo objetivo: deja de generar, disparar, cargar y "
          "enviar, y no puede mejorarse ni reconvertirse. La regla que lo "
          "hace interesante es que invierte el sentido de recibir Energía: "
          "un nodo congelado pierde Energía cuando cualquier facción, "
          "incluida la suya, le envía, y al llegar a cero se descongela y "
          "pasa al bando del último que lo toco. A los 30 s sin recibir nada "
          "se descongela solo."],
         ["Decaimiento", "2", "35", "12 s", "7 u",
          "Infecta el nodo: pierde 2 de Energía por segundo hasta cero y ahí "
          "se queda, infectado y del mismo dueño. Sigue funcionando con "
          "normalidad mientras tanto. Cualquier facción que le envie Energía "
          "lo cura, incluida la suya. No es acumulable: un segundo "
          "Decaimiento reinicia el efecto, no duplica la tasa."],
         ["Agujero de Gusano", "3", "60", "16 s", "5 u",
          "Cambia de bando el nodo objetivo conservando su Energía, su tipo "
          "y su nivel, e ignorando la resistencia doble del Magnetar. Si el "
          "objetivo es un Púlsar enemigo hay tres ventanas distintas: con la "
          "carga a medias, el Púlsar cambia de bando y la carga se pierde; "
          "con la carga al 100 % y el poder sin lanzar, el nuevo dueño lo "
          "hereda intacto; y si el proyectil ya salió, ese proyectil "
          "completa su efecto a favor de quien lo lanzó."]],
        [0.15, 0.06, 0.06, 0.07, 0.07, 0.59], tam=8.0,
        alineados=["i", "c", "c", "c", "c", "i"], negrita_col0=True)
    doc.nota(
        "El coste del Agujero de Gusano es alto a propósito: 60 de Energía y "
        "16 segundos de carga sobre un nodo con tope 100. Es el poder "
        "definitivo y tiene que dolerle al que lo usa.")
    return n


def armas(doc, fig, n):
    doc.h1("11", "Armas")
    doc.parrafo(
        "NOVA no tiene un arsenal: tiene un proyectil, tres proyectiles de "
        "poder y un haz de defensa. Nada más, y es deliberado. La Energía es "
        "el único recurso y también el único proyectil, así que atacar y "
        "reforzar son literalmente la misma acción con distinto destino.")
    doc.tabla(
        ["Arma", "Quién la usa", "Comportamiento"],
        [["Protón", "Estrella, Púlsar y Magnetar de cualquier bando",
          "Cada envío genera un único Protón, no un enjambre. Lleva una "
          "Carga igual a la Energía enviada y la muestra como número sobre "
          "el sprite, actualizado en tiempo real si un Magnetar lo va "
          "desgastando. Viaja a 2.5 unidades por segundo en línea recta, no "
          "se puede redirigir, no colisiona con otros protones y conserva la "
          "facción de su emisor aunque el nodo origen cambie de bando "
          "durante el viaje."],
         ["Haz del Magnetar", "Magnetar de cualquier bando, incluido el "
          "neutral",
          "Instantáneo, del centro del Magnetar al Protón. Resta 2 de Carga "
          "por disparo. Varios Magnetares que cubran el mismo tramo disparan "
          "de forma independiente y acumulativa. Un Magnetar nunca dispara a "
          "protones de su propia facción, ni siquiera si van dirigidos a un "
          "enemigo."],
         ["Proyectil de poder", "Púlsar",
          "Uno por cada poder: Cero Absoluto, Decaimiento y Agujero de "
          "Gusano. Viaja a 6 unidades por segundo -más del doble que un "
          "Protón- y ningún Magnetar puede derribarlo. Solo los protones son "
          "derribables."]],
        [0.16, 0.24, 0.60], tam=8.2, negrita_col0=True)
    doc.nota(
        "La consecuencia de diseño más importante de este apartado es que la "
        "Energía se puede destruir. Un Protón derribado no vuelve al emisor "
        "ni llega al destino: desaparece del juego. Es lo que le da a la "
        "defensa un valor que no tendría si solo bloqueara.")
    return n


def items(doc, fig, n):
    doc.h1("12", "Items")
    doc.parrafo(
        "Hay exactamente dos items en el juego y no debe haber más: un "
        "tercero sería inventar una regla nueva. Los dos son power-ups que "
        "caen del cielo sobre un Asteroide neutral elegido al azar y lo "
        "marcan con un halo luminoso y un icono flotante. El primer bando "
        "que encienda ese Asteroide se lleva el efecto, que se aplica a toda "
        "su facción durante 20 segundos y vale un 50 % más de lo que "
        "afecte.")
    doc.figura(fig["Fpu"], 230,
               "El halo del Asteroide marcado y los dos iconos de power-up: "
               "Rayo Cósmico y Nube de Hidrógeno.", numero=n)
    n += 1
    doc.tabla(
        ["Item", "Efecto", "Afecta a", "Reglas"],
        [["Rayo Cósmico", "+50 % de velocidad de ataque",
          "Cadencia del Magnetar y velocidad de carga del Púlsar",
          "Duración 20 s. Dos Rayos seguidos no se acumulan: el segundo "
          "reinicia el temporizador."],
         ["Nube de Hidrógeno", "+50 % de generación de Energía",
          "Intervalo de la Estrella",
          "Duración 20 s, misma regla de no acumulación. Los dos tipos sí "
          "pueden estar activos a la vez."]],
        [0.16, 0.20, 0.28, 0.36], tam=8.2, negrita_col0=True)
    doc.parrafo(
        "El halo va en gris y partido en ocho tramos. En gris porque el "
        "color lo aporta el icono que flota encima; partido porque el "
        "power-up caduca: si nadie enciende el Asteroide en 30 segundos, "
        "se apaga.")
    doc.tabla(
        ["Mapa", "Primer drop", "Intervalo entre drops", "Máximo por "
         "nivel"],
        [["1 (niveles 1-3)", "25 s", "40 a 55 s al azar", "3"],
         ["2 (niveles 4-6)", "30 s", "50 a 70 s al azar", "4"],
         ["3 (niveles 7-9)", "35 s", "60 a 85 s al azar", "5"]],
        [0.28, 0.20, 0.32, 0.20], tam=8.2,
        alineados=["i", "c", "c", "c"], negrita_col0=True)
    return n


def imagenes_concepto(doc, fig, n):
    doc.h1("13", "Imágenes de concepto")
    doc.parrafo(
        "Todas las imágenes de este documento son sprites finales, no "
        "bocetos: salen de los PNG que ya están en el repositorio del "
        "proyecto. A la fecha de esta entrega hay 49 de los 95 assets "
        "inventariados, y los dos grupos que bloqueaban el desarrollo —los "
        "34 sprites de nodo y los 9 overlays de estado— están cerrados.")

    doc.h2("Los nueve overlays de estado")
    doc.parrafo(
        "Un overlay se dibuja encima del sprite del nodo y no lo sustituye, "
        "así que uno solo sirve para los catorce sprites de nodo en lugar de "
        "multiplicarlos. Los nueve están generados y verificados sobre los "
        "nodos reales.")
    doc.tabla(
        ["ID", "Estado", "Qué lo dispara", "Archivos", "Frames"],
        [["ART-ST-SLEEP", "Dormido",
          "Un Asteroide es neutral", "1 hoja", "16"],
         ["ART-ST-IGN", "SinEncender, por debajo de 10 de Energía",
          "Un Asteroide pasa a ser propio", "2, una por facción", "1"],
         ["ART-ST-READY", "SinEncender, con 10 de Energía",
          "El Asteroide propio ya puede encenderse", "2 hojas, una por "
          "facción", "16"],
         ["ART-ST-SCARE", "Asustado",
          "Un Protón capaz de capturar el nodo llega en menos de 1.5 s",
          "2, un ojo en dos tallas", "1"],
         ["ART-ST-FROZEN", "Congelado",
          "Impacto de Cero Absoluto", "1", "1"],
         ["ART-ST-DECAY", "Infectado", "Impacto de Decaimiento", "1 hoja",
          "16"],
         ["ART-ST-CONV", "Reconvirtiendo", "Se confirma una reconversión",
          "2 hojas, una por facción", "36"],
         ["ART-ST-CAP", "Capturado", "Un nodo cambia de facción", "1 hoja",
          "5"],
         ["ART-ST-BUFF", "Power-up activo",
          "Su facción recoge un power-up que afecta a ese tipo de nodo",
          "2, uno por power-up", "1"]],
        [0.16, 0.20, 0.30, 0.22, 0.08], tam=7.8,
        alineados=["i", "i", "i", "i", "c"], negrita_col0=True)

    doc.figura(fig["Fest"], 420,
               "Los ocho estados sobre nodos reales, a escala 3x. Fila "
               "superior: Dormido (el zzz del Asteroide neutral), "
               "SinEncender (la brasa de un Asteroide propio con 10 de "
               "Energía), Asustado y Congelado. Fila inferior: Infectado, "
               "Reconvirtiendo, Capturado y power-up activo.", numero=n)
    n += 1
    doc.parrafo(
        "Los nueve overlays comparten una restricción: no tapar la cara. "
        "Congelado y Asustado pueden coincidir, y un nodo congelado que no "
        "puede abrir los ojos deja de avisar. La red de grietas del hielo "
        "cruza la cara por el pasillo de 4 píxeles que hay entre los dos "
        "ojos en los trece nodos encendidos; el aura de Infectado no entra "
        "en la caja de la cara en ningún frame.")

    doc.h2("Un overlay, trece nodos", reserva=190)
    doc.figura(fig["Ffrozen"], 300,
               "El mismo archivo de Congelado sobre cuatro cuerpos "
               "distintos: Estrella nivel 5, Púlsar nivel 3, Magnetar "
               "neutral nivel 4 y Estrella nivel 2 del Enemigo. Ni se "
               "reescala ni se redibuja por nodo.", numero=n)
    n += 1

    doc.h2("La señal de susto", reserva=290)
    doc.figura(fig["Fscare"], 400,
               "Arriba, cuatro nodos en reposo; abajo, los mismos con el "
               "overlay de Asustado. El asset es un solo ojo en dos tallas, "
               "instanciado dos veces con el desplazamiento entero que "
               "declara cada tipo y nivel: la separación entre ojos va de "
               "9.5 a 16 píxeles y un overlay de posición fija no aterrizaría "
               "en ninguno.", numero=n)
    n += 1

    doc.h2("Una animación completa", reserva=160)
    doc.figura(fig["Fcap"], 400,
               "Los cinco frames de Capturado, en orden, sobre una Estrella "
               "nivel 3. Dos anillos blancos se cruzan en el frame central: "
               "uno se cierra sobre el nodo y otro sale de él. El cambio de "
               "paleta ocurre en el frame 0, porque la silueta es idéntica "
               "entre facciones y no hay corte de geometría que tapar.",
               numero=n)
    n += 1

    doc.h2("Marca de power-up activo", reserva=180)
    doc.figura(fig["Fbuff"], 250,
               "El galón va en la esquina libre de la celda, en el color del "
               "power-up: Rayo Cósmico sobre Magnetar y Púlsar, Nube de "
               "Hidrógeno sobre Estrella. Solo se marcan los nodos a los que "
               "el power-up afecta, así que ningún nodo lleva los dos a la "
               "vez.", numero=n)
    n += 1

    doc.h2("Los tres fondos", reserva=120)
    doc.parrafo(
        "Uno por mapa, de 2048 x 1152 píxeles, que es el área jugable entera "
        "sin desplazamiento. Los tres mapas no se separan por tono sino por "
        "estructura y densidad, porque las rampas de color con significado "
        "de juego están prohibidas en un fondo.")
    for clave, pie in [
        ("Fbg1", "Mapa 1, Sistema Interior. Lleno y polvoriento, barrido por "
                 "la luz de un sol que queda fuera del encuadre: dibujarlo "
                 "dentro habría metido en el tablero un objeto más brillante "
                 "que cualquier Estrella."),
        ("Fbg2", "Mapa 2, El Cinturón. Una corriente de escombro cruza el "
                 "cielo combada, para no pasar por el centro, que es donde "
                 "se juega, y oculta estrellas al pasar: es lo que la hace "
                 "leer como materia y no como una mancha clara."),
        ("Fbg3", "Mapa 3, Espacio Profundo. El único cuya idea es la "
                 "ausencia. Media imagen es fondo plano, y la galaxia del "
                 "tamaño de una uña está ahí para dar escala."),
    ]:
        doc.figura(fig[clave], 300, pie, numero=n)
        n += 1
    return n


def equipo_y_produccion(doc):
    doc.h1("14", "Miembros del equipo")
    doc.parrafo(
        "El proyecto es individual: asumo los cuatro roles. Es una "
        "restricción real de producción, y de ella salen dos decisiones "
        "del proyecto: que el arte se genere por código y que el alcance "
        "esté cerrado en 4 tipos de nodo y 9 niveles.")
    doc.tabla(
        ["Nombre", "Roles", "Contacto"],
        [["Ivan Gonzalez Ramirez",
          "Diseño de juego - Programación en Unity y C# - Dirección de arte "
          "y pipeline de generación - Documentación",
          "utp0155873@alumno.utpuebla.edu.mx"]],
        [0.24, 0.48, 0.28], tam=8.4, negrita_col0=True)

    doc.h1("15", "Detalles de producción")
    doc.tabla(
        ["Hito", "Fecha", "Entregable"],
        [["Inicio del proyecto", "1 de septiembre de 2026",
          "Arranque del diseño"],
         ["Producto 1", "19 de septiembre de 2026",
          "Documentos del proyecto: Tabla 3 (este documento) y Tabla 4"],
         ["Producto 2", "30 de octubre de 2026", "Beta jugable"],
         ["Producto 3", "20 de noviembre de 2026",
          "Ejecutable y Tabla 5"],
         ["Entrega final", "30 de noviembre de 2026", "Cierre del proyecto"]],
        [0.24, 0.24, 0.52], tam=8.4, negrita_col0=True)
    doc.parrafo(
        "La etapa de producción propiamente dicha -la implementación en "
        "Unity- arranca el 20 de septiembre de 2026, al día siguiente de "
        "esta entrega, y termina el 20 de noviembre de 2026 con el "
        "ejecutable. Los diez días que quedan hasta el 30 de noviembre son "
        "de corrección y cierre documental.")

    doc.h2("Presupuesto")
    doc.parrafo(
        "El costo directo del proyecto es prácticamente nulo, porque elegí a "
        "propósito una cadena de herramientas libre o gratuita y porque el "
        "arte se genera por código y no se compra. El único gasto recurrente "
        "es la suscripción al asistente de IA que uso como apoyo de "
        "documentación y de código repetitivo. El costo real del proyecto es "
        "tiempo, así que lo cuantifico en horas.")
    doc.tabla(
        ["Concepto", "Detalle", "Costo"],
        [["Motor y licencia", "Unity Personal", "$0"],
         ["Pipeline de arte", "Python 3.14, NumPy, Pillow", "$0"],
         ["Tipografía", "Una pixel font de licencia libre", "$0"],
         ["Editor de sonido", "Por elegir, se prevé una opción libre", "$0"],
         ["Equipo de cómputo", "Ya disponible, sin compra asociada", "$0"],
         ["Asistente de IA", "Suscripción mensual, 3 meses de proyecto",
          "20 USD/mes  =  60 USD"],
         ["", "Total en efectivo", "60 USD"]],
        [0.22, 0.52, 0.26], tam=8.4,
        alineados=["i", "i", "d"], negrita_col0=True)
    doc.tabla(
        ["Fase", "Alcance", "Horas estimadas"],
        [["1. Núcleo jugable",
          "Reglas puras, nodos, protones, entrada y captura", "35"],
         ["2. Tipos y defensa",
          "Encendido, mejoras, Magnetar, resistencia y reconversión", "25"],
         ["3. Poderes", "Los tres poderes del Púlsar y su rueda", "25"],
         ["4. IA", "Evaluador, ciclo de decisión y respuesta a amenazas",
          "25"],
         ["5. Flujo y contenido",
          "Los 9 niveles, condiciones de fin, power-ups y progreso", "30"],
         ["6. Presentación",
          "Integración del arte restante, VFX, interfaz y audio", "40"],
         ["Arte y documentación", "Trabajo ya realizado hasta esta entrega",
          "60"],
         ["", "Total", "240 h"]],
        [0.24, 0.56, 0.20], tam=8.4,
        alineados=["i", "i", "d"], negrita_col0=True)
    doc.nota(
        "240 horas en los tres meses de proyecto son unas 20 horas por "
        "semana. A una tarifa de becario de desarrollo de 120 pesos la "
        "hora, equivalen a unos 28 800 pesos de trabajo.")


def pendientes(doc):
    doc.h1("16", "Alcance no cubierto en esta entrega")
    doc.parrafo(
        "La plantilla de la Tabla 3 tiene apartados que a la fecha de esta "
        "entrega no puedo rellenar con nada real. Prefiero declararlos aquí, "
        "con la razón y la fecha en que los cierro, antes que inventarlos: "
        "un documento de diseño solo sirve si se puede confiar en que lo que "
        "dice está decidido de verdad.")
    doc.h2("Decidido que no existirá")
    doc.tabla(
        ["Apartado", "Decisión y motivo"],
        [["Guión",
          "NOVA no lleva diálogo. Toda la información del juego es de "
          "tablero y tiene que leerse en movimiento; un texto obligaría a "
          "detenerse justo cuando algo está pasando. No hay personajes que "
          "hablen: los nodos comunican con la cara y con el color."],
         ["Códigos secretos",
          "No habrá. Una partida dura entre 90 y 240 segundos y se puede "
          "reintentar sin límite, así que un código no resolvería ninguna "
          "frustración real y si permitiría saltarse la curva de dificultad, "
          "que es el contenido del juego."],
         ["Puntaje y tabla de puntuaciones",
          "No habrá. Un marcador premiaría la rapidez y NOVA se gana "
          "componiendo el tablero. El único registro es binario: qué niveles "
          "se han completado. Detallado en la sección 3."],
         ["Más armas o más items",
          "El arsenal está cerrado en un Protón, tres proyectiles de poder y "
          "el haz del Magnetar; los items, en dos power-ups. Añadir un "
          "tercero de cualquiera de los dos sería inventar una regla de "
          "juego, no añadir contenido."]],
        [0.22, 0.78], tam=8.2, negrita_col0=True)

    doc.h2("Pendiente, con fecha")
    doc.tabla(
        ["Apartado", "Estado a la fecha", "Cuándo se cierra"],
        [["Música y efectos de sonido",
          "Sin diseñar. Las 19 animaciones puntuales del juego ya están "
          "inventariadas con su disparador exacto y su duración, así que la "
          "lista de efectos de sonido está implícitamente definida: cada "
          "evento que tiene animación necesita su sonido. Falta elegir "
          "editor, componer y asignar las referencias con la nomenclatura "
          "que pide la plantilla, M para música de fondo y S para efectos.",
          "Producto 2, 30 de octubre"],
         ["Referencias de BGM y SFX",
          "Dependen del apartado anterior. Sin sonidos no hay referencias "
          "que numerar.", "Producto 2, 30 de octubre"],
         ["Logros",
          "El juego registra el nivel máximo desbloqueado, que es el único "
          "hito real hoy. Un sistema de logros con medallas está fuera del "
          "alcance cerrado de la versión 1.0 y lo evaluaré solo si sobra "
          "tiempo tras la beta.",
          "Se decide tras el Producto 2"],
         ["Nombres propios de los 9 niveles",
          "Hoy se identifican por mapa y número. Los tres mapas sí tienen "
          "nombre: Sistema Interior, El Cinturón y Espacio Profundo.",
          "Producto 2, 30 de octubre"],
         ["Coordenadas exactas de los 9 niveles",
          "Están definidos los nodos, los niveles y las duraciones "
          "objetivo de los nueve, pero no la posición de cada nodo en "
          "unidades de mundo. Es lo que convierte una tabla en un nivel "
          "jugable.", "Producto 2, 30 de octubre"],
         ["Arte de interfaz",
          "13 assets de interfaz y 15 efectos visuales pendientes, de 95 "
          "inventariados en total. La paleta y el lenguaje visual están "
          "cerrados; falta el lenguaje de paneles y botones.",
          "Producto 3, 20 de noviembre"]],
        [0.20, 0.54, 0.26], tam=8.0, negrita_col0=True)
    doc.parrafo(
        "El inventario completo de arte, con los 95 assets, su identificador "
        "y su estado uno a uno, vive en la especificación del proyecto y se "
        "actualiza cada vez que un asset se cierra. Hoy marca 49 de 95, y "
        "los dos grupos que bloqueaban el inicio de la fase de presentación "
        "-los 34 sprites de nodo y los 9 overlays de estado- están "
        "completos.")


# ==========================================================================
def main():
    doc = Doc(SALIDA)
    fig = construye_figuras(doc)

    portada(doc, fig)
    doc.nueva_pagina()

    indice_y_versiones(doc)
    concepto(doc, fig)
    vision(doc)
    mecanica(doc, fig)
    estados(doc)
    interfaces(doc, fig)
    niveles(doc, fig)
    progreso(doc)
    n = personajes(doc, fig)
    n = enemigos(doc, fig, n)
    n = habilidades(doc, fig, n)
    n = armas(doc, fig, n)
    n = items(doc, fig, n)
    n = imagenes_concepto(doc, fig, n)
    equipo_y_produccion(doc)
    pendientes(doc)

    paginas, tam = doc.cierra()
    print(f"{os.path.relpath(SALIDA, RAIZ)}: {paginas} paginas, "
          f"{tam / 1024:.0f} KB, {len(doc.imagenes)} imagenes")


if __name__ == "__main__":
    main()
