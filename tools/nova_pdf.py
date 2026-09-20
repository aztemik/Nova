"""Motor de documento PDF para NOVA.

Mismo principio que el arte del proyecto: el PDF no se maqueta a mano, se
calcula. Este modulo es la imprenta; `gen_doc1.py` es el contenido.

Sin dependencias fuera de las que el proyecto ya usa (NumPy y Pillow). El
PDF se escribe a mano: objetos, xref y trailer. Las fuentes son las base-14
de PDF (Helvetica y ZapfDingbats), que no hay que incrustar, y la
codificacion es WinAnsi, que cubre el espanol completo.

Uso tipico:

    doc = Doc('salida.pdf')
    doc.portada(...)
    doc.nueva_pagina()
    doc.h1('1', 'CONCEPTO')
    doc.parrafo('...')
    doc.cierra()
"""

import zlib

from PIL import Image

# --------------------------------------------------------------------------
# Metricas de las fuentes base-14
# --------------------------------------------------------------------------
# Anchos AFM en milesimas de em. Las vocales acentuadas de WinAnsi miden lo
# mismo que su letra base en Helvetica, asi que se derivan en vez de listarse.

_ASCII_REG = (
    "278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278 "
    "556 556 556 556 556 556 556 556 556 556 278 278 584 584 584 556 "
    "1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778 "
    "667 778 722 667 611 722 667 944 667 667 611 278 278 278 469 556 "
    "333 556 556 500 556 556 278 556 556 222 222 500 222 833 556 556 "
    "556 556 333 500 278 556 500 722 500 500 500 334 260 334 584"
)
_ASCII_BLD = (
    "278 333 474 556 556 889 722 238 333 333 389 584 278 333 278 278 "
    "556 556 556 556 556 556 556 556 556 556 333 333 584 584 584 611 "
    "975 722 722 722 722 667 611 778 722 278 556 722 611 833 722 778 "
    "667 778 722 667 611 722 667 944 667 667 611 333 278 333 584 556 "
    "333 556 611 556 611 556 333 611 611 278 278 556 278 889 611 611 "
    "611 611 389 556 333 611 556 778 556 556 500 389 280 389 584"
)

# Acentuadas y signos de WinAnsi que el documento usa, mapeados a la letra
# cuyo ancho comparten. Lo que no este aqui cae en el ancho de la 'n'.
_EQUIV = {
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n",
    "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ü": "U", "Ñ": "N",
    "¿": "?", "¡": "!", "°": "*", "·": ".", "º": "*", "ª": "*",
}
# Anchos propios, iguales en redonda y negrita.
_PROPIOS = {"—": 1000, "–": 556, "«": 556, "»": 556, "…": 1000,
            "“": 333, "”": 333, "‘": 222, "’": 222, "×": 584, "½": 834}


def _tabla(serie):
    w = [int(x) for x in serie.split()]
    t = {chr(32 + i): v for i, v in enumerate(w)}
    for car, base in _EQUIV.items():
        t[car] = t[base]
    t.update(_PROPIOS)
    return t


ANCHOS = {"R": _tabla(_ASCII_REG), "B": _tabla(_ASCII_BLD)}
ANCHOS["I"] = ANCHOS["R"]          # Oblique comparte metricas con la redonda
FUENTE = {"R": "F1", "B": "F2", "I": "F3", "D": "F4"}

# Sustituciones para lo que WinAnsi no tiene. Es preferible un guion visible
# a un cuadro vacio en la pagina impresa.
_SUSTITUTOS = {
    "→": "->", "←": "<-", "↔": "<->", "⇒": "=>", "≥": ">=", "≤": "<=",
    "≠": "!=", "✅": "si", "⬜": "-", "🟨": "-", "🔴": "-", "✓": "v",
    " ": " ", "‑": "-", "−": "-",
}


def limpia(texto):
    for malo, bueno in _SUSTITUTOS.items():
        texto = texto.replace(malo, bueno)
    return texto


def ancho(texto, estilo, tam):
    """Ancho de una cadena en puntos."""
    t = ANCHOS.get(estilo, ANCHOS["R"])
    n = t["n"]
    return sum(t.get(c, n) for c in limpia(texto)) * tam / 1000.0


def _esc(texto):
    b = limpia(texto).encode("cp1252", "replace")
    out = bytearray()
    for byte in b:
        if byte in (0x28, 0x29, 0x5C):     # ( ) \
            out += b"\\"
        out.append(byte)
    # El flujo de contenido se ensambla como texto latin-1, asi que los
    # bytes ya codificados en WinAnsi vuelven como cadena sin reinterpretar.
    return bytes(out).decode("latin-1")


def rgb(hexa):
    h = hexa.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


# --------------------------------------------------------------------------
# Paleta del documento, derivada de la del juego
# --------------------------------------------------------------------------
TINTA = "#1C2028"        # cuerpo de texto
TITULO = "#0B0E1A"       # fondo profundo de NOVA: los titulares
ACENTO = "#0E7C96"       # cian del Jugador, oscurecido para leerse en papel
CIAN = "#3FD7F5"         # cian literal, solo en bloques solidos
MAGENTA = "#F2456B"      # Enemigo, solo en bloques solidos
SUAVE = "#5D6570"        # texto secundario
LINEA = "#D5DAE2"        # filetes
CEBRA = "#F3F5F9"        # fondo de fila alterna
PROFUNDO = "#0B0E1A"     # fondo real del juego, para las figuras

A4 = (595.28, 841.89)


# --------------------------------------------------------------------------
# Documento
# --------------------------------------------------------------------------
class Doc:
    def __init__(self, ruta, margen=(62, 62, 66, 64)):
        """margen: izquierda, derecha, arriba, abajo (en puntos)."""
        self.ruta = ruta
        self.ml, self.mr, self.mt, self.mb = margen
        self.w, self.h = A4
        self.ancho_util = self.w - self.ml - self.mr
        self.paginas = []          # lista de listas de operadores
        self.imagenes = {}         # clave -> (ancho, alto, bytes zlib)
        self.op = None
        self.y = 0
        self.num = 0
        self.pie = True
        self.nueva_pagina(pie=False)

    # -- infraestructura de pagina -----------------------------------------
    def nueva_pagina(self, pie=True):
        self.op = []
        self.paginas.append(self.op)
        self.num = len(self.paginas)
        self.y = self.h - self.mt
        if pie and self.pie:
            self._pie()

    def _pie(self):
        y = self.mb - 22
        self.linea(self.ml, y + 13, self.w - self.mr, y + 13, LINEA, 0.5)
        self.texto("NOVA · Documento de diseño · Producto 1", self.ml, y,
                   "R", 7.5, SUAVE)
        n = str(self.num - 1)      # la portada no cuenta
        self.texto(n, self.w - self.mr - ancho(n, "R", 7.5), y, "R", 7.5, SUAVE)

    def espacio(self, alto):
        self.y -= alto

    def sitio(self, alto):
        """Asegura `alto` puntos de hueco; si no hay, salta de pagina."""
        if self.y - alto < self.mb:
            self.nueva_pagina()
            return True
        return False

    # -- primitivas de dibujo ----------------------------------------------
    def texto(self, cadena, x, y, estilo="R", tam=9.5, color=TINTA,
              espacio_palabra=0.0, seguimiento=0.0):
        r, g, b = rgb(color)
        self.op.append(
            f"BT /{FUENTE[estilo]} {tam:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg "
            f"{espacio_palabra:.3f} Tw {seguimiento:.3f} Tc "
            f"1 0 0 1 {x:.2f} {y:.2f} Tm ({_esc(cadena)}) Tj 0 Tw 0 Tc ET"
        )

    def rect(self, x, y, w, h, color):
        r, g, b = rgb(color)
        self.op.append(f"{r:.3f} {g:.3f} {b:.3f} rg "
                       f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")

    def linea(self, x1, y1, x2, y2, color=LINEA, grosor=0.6):
        r, g, b = rgb(color)
        self.op.append(f"{r:.3f} {g:.3f} {b:.3f} RG {grosor:.2f} w "
                       f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    # -- texto de flujo ----------------------------------------------------
    def corta(self, cadena, estilo, tam, ancho_max):
        """Parte una cadena en lineas que caben en `ancho_max`."""
        lineas, actual = [], ""
        for palabra in limpia(cadena).split():
            prueba = f"{actual} {palabra}".strip()
            if ancho(prueba, estilo, tam) <= ancho_max or not actual:
                actual = prueba
            else:
                lineas.append(actual)
                actual = palabra
        if actual:
            lineas.append(actual)
        return lineas

    def parrafo(self, cadena, estilo="R", tam=9.5, color=TINTA, interlinea=13.2,
                sangria=0, justificado=True, despues=8):
        x0 = self.ml + sangria
        disponible = self.ancho_util - sangria
        lineas = self.corta(cadena, estilo, tam, disponible)
        for i, linea in enumerate(lineas):
            self.sitio(interlinea)
            self.y -= interlinea
            ultima = i == len(lineas) - 1
            tw = 0.0
            if justificado and not ultima:
                huecos = linea.count(" ")
                if huecos:
                    sobra = disponible - ancho(linea, estilo, tam)
                    # No estirar mas de lo razonable: una linea con dos
                    # palabras justificada a la fuerza abre un rio blanco.
                    tw = min(sobra / huecos, tam * 0.45)
            self.texto(linea, x0, self.y, estilo, tam, color, espacio_palabra=tw)
        self.y -= despues

    def h1(self, numero, titulo):
        self.sitio(64)
        self.y -= 26
        if numero:
            self.rect(self.ml, self.y - 3, 3.2, 17, CIAN)
            self.texto(numero, self.ml + 10, self.y + 1, "B", 13, ACENTO)
            x = self.ml + 10 + ancho(numero, "B", 13) + 9
        else:
            self.rect(self.ml, self.y - 3, 3.2, 17, CIAN)
            x = self.ml + 10
        self.texto(titulo.upper(), x, self.y + 1, "B", 13, TITULO,
                   seguimiento=0.9)
        self.y -= 9
        self.linea(self.ml, self.y, self.w - self.mr, self.y, LINEA, 0.7)
        self.y -= 12

    def h2(self, titulo, reserva=40):
        # `reserva` es el hueco que el titulo necesita por debajo. Un h2
        # seguido de figura pide el alto de la figura, o queda huerfano.
        self.sitio(reserva)
        self.y -= 17
        self.texto(titulo, self.ml, self.y, "B", 10.2, TITULO)
        self.y -= 6

    def h3(self, titulo):
        self.sitio(30)
        self.y -= 13
        self.texto(titulo, self.ml, self.y, "B", 9.2, ACENTO)
        self.y -= 4

    def nota(self, cadena, tam=8.4):
        """Parrafo secundario, sangrado y con filete lateral."""
        lineas = self.corta(cadena, "I", tam, self.ancho_util - 16)
        alto = len(lineas) * 11.4
        self.sitio(alto + 8)
        self.y -= 3
        arriba = self.y
        for linea in lineas:
            self.y -= 11.4
            self.texto(linea, self.ml + 16, self.y, "I", tam, SUAVE)
        self.rect(self.ml + 3, self.y - 1, 1.6, arriba - self.y + 1, LINEA)
        self.y -= 8

    def campo(self, etiqueta, cuerpo, ancho_etiqueta=112, tam=9.5):
        """Fila `Campo / Descripcion` de las tablas de la plantilla.

        El rotulo tambien envuelve: uno de dos lineas dejado en una se sale
        de su columna y se mete dentro del cuerpo.
        """
        sep = 12
        disponible = self.ancho_util - ancho_etiqueta - sep
        lineas = self.corta(cuerpo, "R", tam, disponible)
        rotulo = self.corta(etiqueta, "B", tam, ancho_etiqueta)
        alto = max(len(lineas), len(rotulo), 1) * 13.0
        self.sitio(alto + 9)
        arriba = self.y
        for i, linea in enumerate(rotulo):
            self.texto(linea, self.ml, arriba - 9.6 - i * 13.0, "B", tam,
                       TITULO)
        for i, linea in enumerate(lineas):
            self.texto(linea, self.ml + ancho_etiqueta + sep,
                       arriba - 9.6 - i * 13.0, "R", tam, TINTA)
        self.y = arriba - alto - 5.5
        self.linea(self.ml, self.y + 2, self.w - self.mr, self.y + 2,
                   LINEA, 0.5)
        self.y -= 4.5

    def viñetas(self, items, tam=9.5, interlinea=13.0, marca="-"):
        for item in items:
            sangria = 13
            lineas = self.corta(item, "R", tam, self.ancho_util - sangria)
            for i, linea in enumerate(lineas):
                self.sitio(interlinea)
                self.y -= interlinea
                if i == 0:
                    self.texto(marca, self.ml + 3, self.y, "R", tam, ACENTO)
                self.texto(linea, self.ml + sangria, self.y, "R", tam, TINTA)
            self.y -= 1.5
        self.y -= 6

    # -- tablas ------------------------------------------------------------
    def tabla(self, cabecera, filas, anchos, tam=8.4, alineados=None,
              despues=10, negrita_col0=False):
        """Tabla con cabecera oscura, cebra y salto de pagina automatico.

        `anchos` en fraccion del ancho util. `alineados`: 'i', 'c' o 'd'.
        """
        total = sum(anchos)
        cols = [a / total * self.ancho_util for a in anchos]
        alineados = alineados or ["i"] * len(cols)
        pad = 5.5
        interlinea = tam * 1.28

        def dibuja_cabecera():
            # La cabecera envuelve igual que una fila: un rotulo de dos
            # lineas en una celda de una no cabe y se sale por abajo.
            n = max(len(self.corta(str(t), "B", tam, w - 2 * pad))
                    for t, w in zip(cabecera, cols))
            alto = n * interlinea + 8
            self.sitio(alto + interlinea * 2)
            self.y -= alto
            self.rect(self.ml, self.y, self.ancho_util, alto, TITULO)
            x = self.ml
            for texto, w, al in zip(cabecera, cols, alineados):
                self._celda(texto, x, self.y, w, alto, "B", tam, "#FFFFFF",
                            al, pad, interlinea)
                x += w

        dibuja_cabecera()
        for n, fila in enumerate(filas):
            alturas = []
            for texto, w in zip(fila, cols):
                alturas.append(len(self.corta(str(texto), "R", tam,
                                              w - 2 * pad)))
            alto = max(alturas) * interlinea + 7
            if self.y - alto < self.mb:
                self.nueva_pagina()
                dibuja_cabecera()
            self.y -= alto
            if n % 2 == 1:
                self.rect(self.ml, self.y, self.ancho_util, alto, CEBRA)
            x = self.ml
            for c, (texto, w, al) in enumerate(zip(fila, cols, alineados)):
                est = "B" if (c == 0 and negrita_col0) else "R"
                self._celda(str(texto), x, self.y, w, alto, est, tam, TINTA,
                            al, pad, interlinea)
                x += w
            self.linea(self.ml, self.y, self.w - self.mr, self.y, LINEA, 0.4)
        self.y -= despues

    def _celda(self, texto, x, y, w, alto, estilo, tam, color, al, pad,
               interlinea):
        lineas = self.corta(str(texto), estilo, tam, w - 2 * pad)
        cursor = y + alto - 4 - tam * 0.82
        for linea in lineas:
            if al == "c":
                px = x + (w - ancho(linea, estilo, tam)) / 2
            elif al == "d":
                px = x + w - pad - ancho(linea, estilo, tam)
            else:
                px = x + pad
            self.texto(linea, px, cursor, estilo, tam, color)
            cursor -= interlinea

    # -- imagenes ----------------------------------------------------------
    def registra(self, clave, imagen):
        """Guarda una imagen PIL RGB ya aplanada y devuelve su clave."""
        if clave in self.imagenes:
            return clave
        im = imagen.convert("RGB")
        self.imagenes[clave] = (im.width, im.height,
                                zlib.compress(im.tobytes(), 9))
        return clave

    def dibuja_imagen(self, clave, x, y, w, h):
        self.op.append(f"q {w:.2f} 0 0 {h:.2f} {x:.2f} {y:.2f} cm "
                       f"/{clave} Do Q")

    def figura(self, clave, ancho_pt, pie=None, numero=None, centrada=True,
               marco=True, despues=12):
        w_px, h_px, _ = self.imagenes[clave]
        alto_pt = ancho_pt * h_px / w_px
        alto_pie = 0
        if pie:
            alto_pie = len(self.corta(pie, "R", 8.0,
                                      self.ancho_util - 20)) * 10.6 + 5
        self.sitio(alto_pt + alto_pie + 10)
        x = self.ml + (self.ancho_util - ancho_pt) / 2 if centrada else self.ml
        self.y -= alto_pt
        self.dibuja_imagen(clave, x, self.y, ancho_pt, alto_pt)
        if marco:
            r, g, b = rgb(LINEA)
            self.op.append(f"{r:.3f} {g:.3f} {b:.3f} RG 0.5 w "
                           f"{x:.2f} {self.y:.2f} {ancho_pt:.2f} "
                           f"{alto_pt:.2f} re S")
        if pie:
            self.y -= 4
            etiqueta = f"Figura {numero}. " if numero else ""
            lineas = self.corta(etiqueta + pie, "R", 8.0, self.ancho_util - 20)
            for linea in lineas:
                self.y -= 10.6
                px = self.ml + (self.ancho_util - ancho(linea, "R", 8.0)) / 2
                self.texto(linea, px, self.y, "R", 8.0, SUAVE)
        self.y -= despues

    # -- salida ------------------------------------------------------------
    def cierra(self):
        objetos = []

        def add(cuerpo):
            objetos.append(cuerpo)
            return len(objetos)          # numero de objeto (1-indexado)

        fuentes = [
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
            b"/Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
            b"/Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique "
            b"/Encoding /WinAnsiEncoding >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /ZapfDingbats >>",
        ]
        ids_fuente = [add(f) for f in fuentes]

        ids_img = {}
        for clave, (w, h, datos) in self.imagenes.items():
            cabeza = (f"<< /Type /XObject /Subtype /Image /Width {w} "
                      f"/Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 "
                      f"/Filter /FlateDecode /Length {len(datos)} >>\nstream\n"
                      ).encode("latin-1")
            ids_img[clave] = add(cabeza + datos + b"\nendstream")

        # El objeto /Pages se escribe despues de las paginas, pero cada
        # pagina tiene que apuntar a el: su numero se reserva ahora.
        id_paginas = len(objetos) + 2 * len(self.paginas) + 1
        recursos = ("<< /Font << " +
                    " ".join(f"/F{i + 1} {ids_fuente[i]} 0 R"
                             for i in range(4)) +
                    " >> /XObject << " +
                    " ".join(f"/{k} {v} 0 R" for k, v in ids_img.items()) +
                    " >> >>")

        ids_pagina = []
        for ops in self.paginas:
            flujo = zlib.compress("\n".join(ops).encode("latin-1"), 9)
            id_c = add((f"<< /Filter /FlateDecode /Length {len(flujo)} >>\n"
                        "stream\n").encode("latin-1") + flujo + b"\nendstream")
            ids_pagina.append(add(
                (f"<< /Type /Page /Parent {id_paginas} 0 R /MediaBox "
                 f"[0 0 {self.w:.2f} {self.h:.2f}] /Resources {recursos} "
                 f"/Contents {id_c} 0 R >>").encode("latin-1")))

        add((f"<< /Type /Pages /Count {len(ids_pagina)} /Kids [" +
             " ".join(f"{i} 0 R" for i in ids_pagina) +
             "] >>").encode("latin-1"))
        id_cat = add(f"<< /Type /Catalog /Pages {id_paginas} 0 R >>"
                     .encode("latin-1"))
        # El Info va en latin-1, que es lo que PDFDocEncoding acepta
        # para los acentos del espanol.
        id_info = add(
            "<< /Title (NOVA - Documento de diseño) "
            "/Author (Ivan Gonzalez Ramirez) "
            "/Subject (Producto 1. Tabla 3, Plantilla del Documento "
            "de Diseño) >>".encode("latin-1"))

        salida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = []
        for i, cuerpo in enumerate(objetos, 1):
            offsets.append(len(salida))
            salida += f"{i} 0 obj\n".encode("latin-1") + cuerpo + b"\nendobj\n"
        inicio = len(salida)
        salida += f"xref\n0 {len(objetos) + 1}\n".encode("latin-1")
        salida += b"0000000000 65535 f \n"
        for off in offsets:
            salida += f"{off:010d} 00000 n \n".encode("latin-1")
        salida += (f"trailer\n<< /Size {len(objetos) + 1} /Root {id_cat} 0 R "
                   f"/Info {id_info} 0 R >>\nstartxref\n{inicio}\n%%EOF\n"
                   ).encode("latin-1")

        with open(self.ruta, "wb") as f:
            f.write(bytes(salida))
        return len(self.paginas), len(salida)


# --------------------------------------------------------------------------
# Utilidades de imagen: las figuras se componen, no se recortan a mano
# --------------------------------------------------------------------------
def sobre_fondo(im, color=PROFUNDO):
    """Aplana un RGBA sobre el fondo real del juego. Regla del contrato de
    arte: una previsualizacion se juzga sobre #0B0E1A, no sobre blanco."""
    fondo = Image.new("RGBA", im.size, tuple(int(c * 255) for c in rgb(color))
                      + (255,))
    return Image.alpha_composite(fondo, im.convert("RGBA")).convert("RGB")


def escala(im, factor):
    """Ampliacion entera por vecino mas cercano: es pixel art."""
    return im.resize((im.width * factor, im.height * factor), Image.NEAREST)


def tira(imagenes, factor=3, hueco=10, margen=10, fondo=PROFUNDO):
    """Fila horizontal de sprites sobre el fondo del juego."""
    ims = [escala(sobre_fondo(i), factor) for i in imagenes]
    w = sum(i.width for i in ims) + hueco * (len(ims) - 1) + 2 * margen
    h = max(i.height for i in ims) + 2 * margen
    lienzo = Image.new("RGB", (w, h), tuple(int(c * 255) for c in rgb(fondo)))
    x = margen
    for i in ims:
        lienzo.paste(i, (x, margen + (h - 2 * margen - i.height) // 2))
        x += i.width + hueco
    return lienzo


def rejilla(filas, factor=3, hueco=10, margen=10, fondo=PROFUNDO):
    """Rejilla de sprites: lista de filas de imagenes PIL."""
    tiras = [tira(f, factor, hueco, 0, fondo) for f in filas]
    w = max(t.width for t in tiras) + 2 * margen
    h = sum(t.height for t in tiras) + hueco * (len(tiras) - 1) + 2 * margen
    lienzo = Image.new("RGB", (w, h), tuple(int(c * 255) for c in rgb(fondo)))
    y = margen
    for t in tiras:
        lienzo.paste(t, ((w - t.width) // 2, y))
        y += t.height + hueco
    return lienzo
