"""Motor de documento DOCX para NOVA.

Misma imprenta, otro papel. `nova_pdf.Doc` calcula el documento en puntos
sobre A4; esta clase hereda de ella, la deja calcular exactamente igual y,
en paralelo, va anotando cada bloque como contenido real de Word.

De ahi que el contenido no se toque: `gen_doc1.py` no se modifica ni se
copia. Se le cambia la imprenta desde fuera:

    import gen_doc1 as G
    G.Doc = nova_docx.Doc
    G.SALIDA = '.../documento.docx'
    G.main()

Lo que en el PDF es texto de flujo (titulos, parrafos, tablas, campos,
notas, figuras) sale en el DOCX como texto y tablas de Word, editable y
seleccionable, con la misma fuente, cuerpo, color y orden.

Lo que en el PDF es dibujo vectorial a coordenadas absolutas -la portada y
los dos diagramas- no tiene equivalente en Word sin rehacerlo. Esas zonas
se recortan del PDF que esta misma clase genera y se incrustan como imagen,
asi que salen identicas al milimetro en vez de aproximadas.

Sin dependencias nuevas de Python: el .docx se escribe a mano (OOXML dentro
de un zip), igual que el PDF. Para rasterizar las zonas de dibujo usa
`pdftoppm` (poppler) y, si no esta, `gs`.
"""

import os
import shutil
import subprocess
import tempfile
import zipfile

from PIL import Image, ImageDraw

import nova_pdf as P
from nova_pdf import ACENTO, CEBRA, LINEA, SUAVE, TINTA, TITULO

DPI = 200                     # rasterizado de las zonas de dibujo
FUENTE_DOCX = "Arial"         # equivalente metrico de la Helvetica del PDF


# --------------------------------------------------------------------------
# Utilidades de unidades y XML
# --------------------------------------------------------------------------
def tw(pt):
    """Puntos a twips (1/20 de punto), la unidad de Word."""
    return int(round(pt * 20))


def emu(pt):
    """Puntos a EMU, la unidad de los graficos de OOXML."""
    return int(round(pt * 12700))


def hp(pt):
    """Puntos a medios puntos, que es como Word mide el cuerpo."""
    return max(1, int(round(pt * 2)))


def esc(texto):
    return (str(texto).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def col(hexa):
    return hexa.lstrip("#").upper()


def rpr(estilo="R", tam=9.5, color=TINTA, track=0.0):
    """Propiedades de fuente de una tirada de texto."""
    p = ['<w:rPr>',
         f'<w:rFonts w:ascii="{FUENTE_DOCX}" w:hAnsi="{FUENTE_DOCX}"'
         f' w:cs="{FUENTE_DOCX}"/>']
    if estilo == "B":
        p.append("<w:b/>")
    if estilo == "I":
        p.append("<w:i/>")
    p.append(f'<w:color w:val="{col(color)}"/>')
    if track:
        p.append(f'<w:spacing w:val="{tw(track)}"/>')
    p.append(f'<w:sz w:val="{hp(tam)}"/><w:szCs w:val="{hp(tam)}"/>')
    p.append("</w:rPr>")
    return "".join(p)


def run(texto, estilo="R", tam=9.5, color=TINTA, track=0.0):
    return (f"<w:r>{rpr(estilo, tam, color, track)}"
            f'<w:t xml:space="preserve">{esc(texto)}</w:t></w:r>')


def parr(runs, antes=0, despues=0, interlinea=None, jc=None, ind=0,
         colgante=0, bordes="", nivel=None, junto=False, extra=""):
    """Un parrafo de Word con sus propiedades de bloque."""
    p = ["<w:pPr>"]
    if junto:
        p.append("<w:keepNext/>")
    if bordes:
        p.append(bordes)
    esp = f'<w:spacing w:before="{tw(antes)}" w:after="{tw(despues)}"'
    if interlinea:
        esp += f' w:line="{tw(interlinea)}" w:lineRule="exact"'
    p.append(esp + "/>")
    if ind or colgante:
        p.append(f'<w:ind w:left="{tw(ind)}" w:hanging="{tw(colgante)}"/>')
    if jc:
        p.append(f'<w:jc w:val="{jc}"/>')
    if nivel is not None:
        p.append(f'<w:outlineLvl w:val="{nivel}"/>')
    p.append(extra)
    p.append("</w:pPr>")
    return "<w:p>" + "".join(p) + "".join(runs) + "</w:p>"


def imagen_xml(rid, n, w_pt, h_pt, nombre):
    return (
        "<w:r><w:drawing>"
        '<wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{emu(w_pt)}" cy="{emu(h_pt)}"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{n}" name="{esc(nombre)}"/>'
        "<wp:cNvGraphicFramePr>"
        '<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/'
        'drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/'
        '2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/'
        'drawingml/2006/picture">'
        '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/'
        '2006/picture"><pic:nvPicPr>'
        f'<pic:cNvPr id="{n}" name="{esc(nombre)}"/><pic:cNvPicPr/>'
        "</pic:nvPicPr><pic:blipFill>"
        f'<a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch>'
        "</pic:blipFill><pic:spPr><a:xfrm>"
        f'<a:off x="0" y="0"/><a:ext cx="{emu(w_pt)}" cy="{emu(h_pt)}"/>'
        "</a:xfrm><a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom>"
        "</pic:spPr></pic:pic></a:graphicData></a:graphic>"
        "</wp:inline></w:drawing></w:r>")


# --------------------------------------------------------------------------
# Rasterizado de las zonas de dibujo
# --------------------------------------------------------------------------
def pagina_png(pdf, pagina, carpeta, dpi=DPI):
    """Rasteriza una pagina del PDF y devuelve la imagen PIL."""
    destino = os.path.join(carpeta, f"p{pagina}")
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi),
                        "-f", str(pagina), "-l", str(pagina), "-singlefile",
                        pdf, destino], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif shutil.which("gs"):
        subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER",
                        "-sDEVICE=png16m", f"-r{dpi}",
                        f"-dFirstPage={pagina}", f"-dLastPage={pagina}",
                        f"-sOutputFile={destino}.png", pdf], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        raise RuntimeError(
            "Hace falta pdftoppm (poppler-utils) o gs (ghostscript) para "
            "pasar la portada y los diagramas al DOCX.")
    return Image.open(destino + ".png").convert("RGB")


# --------------------------------------------------------------------------
# Documento
# --------------------------------------------------------------------------
class Doc(P.Doc):
    def __init__(self, ruta, margen=(62, 62, 66, 64)):
        self.destino = ruta
        self.bloques = []        # flujo de bloques del DOCX
        self.pil = {}            # clave de imagen -> PIL, para incrustarla
        self._prof = 0           # profundidad de metodo de flujo
        self._en_sitio = False
        self._listo = False
        self._n_ops = 0
        self._pag_marca = 1
        self._y_marca = 0
        self._tmp = tempfile.mkdtemp(prefix="nova_docx_")
        base = os.path.splitext(os.path.basename(ruta))[0]
        super().__init__(os.path.join(self._tmp, base + ".pdf"), margen)
        self._listo = True
        self._sincroniza()

    # -- contabilidad de lo que ya esta contado -----------------------------
    def _sincroniza(self):
        self._n_ops = len(self.op)
        self._pag_marca = self.num
        self._y_marca = self.y

    def _graficos_sueltos(self):
        vistos = self._n_ops if self.num == self._pag_marca else 0
        return len(self.op) > vistos

    def _cierra_lienzo(self):
        """Todo dibujo que no venga de un metodo de flujo es una figura."""
        if not self._listo or not self._graficos_sueltos():
            self._sincroniza()
            return
        arriba = self._y_marca if self.num == self._pag_marca else self.h - self.mt
        abajo = self.y
        if arriba - abajo < 6:              # la portada: ocupa la pagina
            caja, pagina_entera = (0, 0, self.w, self.h), True
        else:
            caja = (self.ml - 6, max(abajo - 4, 0),
                    self.w - self.mr + 6, min(arriba + 4, self.h))
            pagina_entera = False
        self.bloques.append(("lienzo", self.num, caja, pagina_entera))
        self._sincroniza()

    def _flujo(self, bloque, metodo, *a, **kw):
        """Ejecuta el metodo del PDF tal cual y anota su bloque de Word."""
        self._cierra_lienzo()
        self._prof += 1
        try:
            r = metodo(*a, **kw)
        finally:
            self._prof -= 1
        self._sincroniza()
        if bloque is not None:
            self.bloques.append(bloque)
        return r

    # -- infraestructura de pagina -----------------------------------------
    def sitio(self, alto):
        previo, self._en_sitio = self._en_sitio, True
        try:
            return super().sitio(alto)
        finally:
            self._en_sitio = previo

    def nueva_pagina(self, pie=True):
        externo = self._listo and self._prof == 0 and not self._en_sitio
        if externo:
            self._cierra_lienzo()
        super().nueva_pagina(pie)
        self._sincroniza()
        if externo:
            self.bloques.append(("salto",))

    def espacio(self, alto):
        self._flujo(("espacio", alto), super().espacio, alto)

    # -- texto de flujo ----------------------------------------------------
    def parrafo(self, cadena, estilo="R", tam=9.5, color=TINTA,
                interlinea=13.2, sangria=0, justificado=True, despues=8):
        self._flujo(("parrafo", cadena, estilo, tam, color, interlinea,
                     sangria, justificado, despues),
                    super().parrafo, cadena, estilo, tam, color, interlinea,
                    sangria, justificado, despues)

    def h1(self, numero, titulo):
        self._flujo(("h1", numero, titulo), super().h1, numero, titulo)

    def h2(self, titulo, reserva=40):
        self._flujo(("h2", titulo), super().h2, titulo, reserva)

    def h3(self, titulo):
        self._flujo(("h3", titulo), super().h3, titulo)

    def nota(self, cadena, tam=8.4):
        self._flujo(("nota", cadena, tam), super().nota, cadena, tam)

    def campo(self, etiqueta, cuerpo, ancho_etiqueta=112, tam=9.5):
        self._flujo(("campo", etiqueta, cuerpo, ancho_etiqueta, tam),
                    super().campo, etiqueta, cuerpo, ancho_etiqueta, tam)

    def viñetas(self, items, tam=9.5, interlinea=13.0, marca="-"):
        self._flujo(("viñetas", list(items), tam, interlinea, marca),
                    super().viñetas, items, tam, interlinea, marca)

    def tabla(self, cabecera, filas, anchos, tam=8.4, alineados=None,
              despues=10, negrita_col0=False):
        self._flujo(("tabla", list(cabecera), [list(f) for f in filas],
                     list(anchos), tam, alineados, despues, negrita_col0),
                    super().tabla, cabecera, filas, anchos, tam, alineados,
                    despues, negrita_col0)

    # -- imagenes ----------------------------------------------------------
    def registra(self, clave, imagen):
        if clave not in self.pil:
            self.pil[clave] = imagen.convert("RGB")
        return super().registra(clave, imagen)

    def figura(self, clave, ancho_pt, pie=None, numero=None, centrada=True,
               marco=True, despues=12):
        self._flujo(("figura", clave, ancho_pt, pie, numero, centrada, marco,
                     despues),
                    super().figura, clave, ancho_pt, pie, numero, centrada,
                    marco, despues)

    # ----------------------------------------------------------------------
    # Salida
    # ----------------------------------------------------------------------
    def cierra(self):
        self._cierra_lienzo()
        paginas, _ = super().cierra()          # el PDF intermedio, intacto
        try:
            medios, cuerpo = self._arma_cuerpo()
            self._escribe_zip(medios, cuerpo)
        finally:
            shutil.rmtree(self._tmp, ignore_errors=True)
        # Se devuelve lo mismo que el motor PDF -paginas y bytes- para que
        # `gen_doc1.main()` pueda imprimir su resumen sin enterarse. Las
        # paginas son las del calculo en A4; Word repagina al abrir.
        return paginas, os.path.getsize(self.destino)

    # -- recorte de las zonas de dibujo ------------------------------------
    def _recorta(self, pagina, caja, cache):
        if pagina not in cache:
            cache[pagina] = pagina_png(self.ruta, pagina, self._tmp)
        im = cache[pagina]
        k = im.width / self.w                  # pixeles por punto
        x0, y0, x1, y1 = caja
        recorte = im.crop((int(x0 * k), int((self.h - y1) * k),
                           int(x1 * k), int((self.h - y0) * k)))
        return recorte, (x1 - x0), (y1 - y0)

    # -- cuerpo del documento ----------------------------------------------
    def _arma_cuerpo(self):
        util = self.ancho_util
        alto_util = self.h - self.mt - self.mb
        medios = []            # (nombre, bytes PNG)
        cache = {}
        partes = []

        def guarda(im):
            ruta = os.path.join(self._tmp, f"img{len(medios) + 1}.png")
            im.save(ruta, "PNG", optimize=True)
            with open(ruta, "rb") as f:
                datos = f.read()
            nombre = f"img{len(medios) + 1}.png"
            medios.append((nombre, datos))
            return f"rId{100 + len(medios)}", len(medios), nombre

        i = 0
        while i < len(self.bloques):
            b = self.bloques[i]
            tipo = b[0]

            if tipo == "campo":                # los campos seguidos son una tabla
                grupo = []
                while i < len(self.bloques) and self.bloques[i][0] == "campo":
                    grupo.append(self.bloques[i])
                    i += 1
                partes.append(self._xml_campos(grupo, util))
                partes.append(parr([], despues=0, interlinea=1))
                continue

            i += 1
            if tipo == "salto":
                partes.append(parr(['<w:r><w:br w:type="page"/></w:r>']))
            elif tipo == "espacio":
                partes.append(parr([], interlinea=max(b[1], 1)))
            elif tipo == "parrafo":
                _, cadena, estilo, tam, color, interlinea, sangria, just, desp = b
                partes.append(parr(
                    [run(cadena, estilo, tam, color)],
                    despues=desp, interlinea=interlinea,
                    jc="both" if just else "left", ind=sangria))
            elif tipo == "h1":
                partes.append(self._xml_h1(b[1], b[2]))
            elif tipo == "h2":
                partes.append(parr([run(b[1], "B", 10.2, TITULO)],
                                   antes=11, despues=4, interlinea=13.5,
                                   nivel=1, junto=True))
            elif tipo == "h3":
                partes.append(parr([run(b[1], "B", 9.2, ACENTO)],
                                   antes=8, despues=3, interlinea=12.2,
                                   nivel=2, junto=True))
            elif tipo == "nota":
                borde = ('<w:pBdr><w:left w:val="single" w:sz="13" '
                         f'w:color="{col(LINEA)}" w:space="8"/></w:pBdr>')
                partes.append(parr([run(b[1], "I", b[2], SUAVE)],
                                   antes=3, despues=8, interlinea=11.4,
                                   ind=16, bordes=borde))
            elif tipo == "viñetas":
                _, items, tam, interlinea, marca = b
                for item in items:
                    partes.append(parr(
                        [run(marca + "\t", "R", tam, ACENTO),
                         run(item, "R", tam, TINTA)],
                        despues=1.5, interlinea=interlinea, ind=13,
                        colgante=13))
                partes.append(parr([], interlinea=6))
            elif tipo == "tabla":
                partes.append(self._xml_tabla(b, util))
                partes.append(parr([], despues=0, interlinea=max(b[6], 1)))
            elif tipo == "figura":
                _, clave, ancho_pt, pie, numero, centrada, marco, desp = b
                im = self.pil[clave].copy()
                if marco:
                    grosor = max(1, int(round(im.width / ancho_pt * 0.5)))
                    d = ImageDraw.Draw(im)
                    d.rectangle([0, 0, im.width - 1, im.height - 1],
                                outline=tuple(int(c * 255)
                                              for c in P.rgb(LINEA)),
                                width=grosor)
                rid, n, nombre = guarda(im)
                alto_pt = ancho_pt * im.height / im.width
                partes.append(parr(
                    [imagen_xml(rid, n, ancho_pt, alto_pt, nombre)],
                    despues=4 if pie else desp,
                    jc="center" if centrada else "left", junto=bool(pie)))
                if pie:
                    etiqueta = f"Figura {numero}. " if numero else ""
                    partes.append(parr([run(etiqueta + pie, "R", 8.0, SUAVE)],
                                       despues=desp, interlinea=10.6,
                                       jc="center"))
            elif tipo == "lienzo":
                _, pagina, caja, entera = b
                im, w_pt, h_pt = self._recorta(pagina, caja, cache)
                rid, n, nombre = guarda(im)
                if entera:
                    # La portada es una pagina completa, no una ilustracion
                    # dentro del texto: va en su propia seccion sin margenes
                    # ni pie, para que salga a sangre como en el PDF. El
                    # salto de pagina que viene detras ya lo da la seccion.
                    if i < len(self.bloques) and self.bloques[i][0] == "salto":
                        i += 1
                    partes.append(parr(
                        [imagen_xml(rid, n, w_pt * 0.995, h_pt * 0.995,
                                    nombre)],
                        jc="center", extra=self._xml_sectpr(portada=True)))
                else:
                    factor = min(util / w_pt, alto_util / h_pt, 1.0)
                    partes.append(parr(
                        [imagen_xml(rid, n, w_pt * factor, h_pt * factor,
                                    nombre)],
                        despues=6, jc="center"))

        partes.append(self._xml_sectpr())
        return medios, "".join(partes)

    def _xml_h1(self, numero, titulo):
        bordes = ('<w:pBdr>'
                  f'<w:left w:val="single" w:sz="26" w:color="{col(P.CIAN)}"'
                  ' w:space="6"/>'
                  f'<w:bottom w:val="single" w:sz="6" w:color="{col(LINEA)}"'
                  ' w:space="6"/></w:pBdr>')
        runs = []
        if numero:
            runs.append(run(numero + "  ", "B", 13, ACENTO))
        runs.append(run(titulo.upper(), "B", 13, TITULO, track=0.9))
        return parr(runs, antes=20, despues=10, interlinea=17,
                    bordes=bordes, ind=4, nivel=0, junto=True)

    def _xml_campos(self, grupo, util):
        ancho_et = grupo[0][3]
        cols = [tw(ancho_et), tw(util - ancho_et)]
        borde = ('<w:tblBorders>'
                 f'<w:insideH w:val="single" w:sz="4" w:color="{col(LINEA)}"/>'
                 f'<w:bottom w:val="single" w:sz="4" w:color="{col(LINEA)}"/>'
                 "</w:tblBorders>")
        filas = []
        for _, etiqueta, cuerpo, _, tam in grupo:
            celdas = [
                self._xml_celda(etiqueta, cols[0], "B", tam, TITULO, "i",
                                None, tam * 1.37, pad_izq=0),
                self._xml_celda(cuerpo, cols[1], "R", tam, TINTA, "i",
                                None, tam * 1.37),
            ]
            filas.append("<w:tr><w:trPr><w:cantSplit/></w:trPr>" +
                         "".join(celdas) + "</w:tr>")
        return (self._xml_tblpr(util, borde, 5.5) +
                f'<w:tblGrid><w:gridCol w:w="{cols[0]}"/>'
                f'<w:gridCol w:w="{cols[1]}"/></w:tblGrid>' +
                "".join(filas) + "</w:tbl>")

    def _xml_tabla(self, b, util):
        _, cabecera, filas, anchos, tam, alineados, _, negrita_col0 = b
        total = sum(anchos)
        cols = [tw(a / total * util) for a in anchos]
        alineados = alineados or ["i"] * len(cols)
        interlinea = tam * 1.28
        borde = ('<w:tblBorders>'
                 f'<w:insideH w:val="single" w:sz="4" w:color="{col(LINEA)}"/>'
                 f'<w:bottom w:val="single" w:sz="4" w:color="{col(LINEA)}"/>'
                 "</w:tblBorders>")
        xml = [self._xml_tblpr(util, borde, 5.5),
               "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{c}"/>'
                                       for c in cols) + "</w:tblGrid>"]
        celdas = [self._xml_celda(t, w, "B", tam, "#FFFFFF", al, TITULO,
                                  interlinea)
                  for t, w, al in zip(cabecera, cols, alineados)]
        xml.append("<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>" +
                   "".join(celdas) + "</w:tr>")
        for n, fila in enumerate(filas):
            fondo = CEBRA if n % 2 == 1 else None
            celdas = []
            for c, (texto, w, al) in enumerate(zip(fila, cols, alineados)):
                est = "B" if (c == 0 and negrita_col0) else "R"
                celdas.append(self._xml_celda(texto, w, est, tam, TINTA, al,
                                              fondo, interlinea))
            xml.append("<w:tr><w:trPr><w:cantSplit/></w:trPr>" +
                       "".join(celdas) + "</w:tr>")
        xml.append("</w:tbl>")
        return "".join(xml)

    def _xml_tblpr(self, util, bordes, pad):
        return ("<w:tbl><w:tblPr>"
                f'<w:tblW w:w="{tw(util)}" w:type="dxa"/>'
                '<w:tblLayout w:type="fixed"/>'
                f"{bordes}<w:tblCellMar>"
                f'<w:top w:w="{tw(3.5)}" w:type="dxa"/>'
                f'<w:left w:w="{tw(pad)}" w:type="dxa"/>'
                f'<w:bottom w:w="{tw(3.5)}" w:type="dxa"/>'
                f'<w:right w:w="{tw(pad)}" w:type="dxa"/>'
                "</w:tblCellMar></w:tblPr>")

    def _xml_celda(self, texto, ancho, estilo, tam, color, al, fondo,
                   interlinea, pad_izq=None):
        jc = {"c": "center", "d": "right"}.get(al)
        pr = [f'<w:tcW w:w="{ancho}" w:type="dxa"/>']
        if fondo:
            pr.append('<w:shd w:val="clear" w:color="auto" '
                      f'w:fill="{col(fondo)}"/>')
        if pad_izq is not None:
            pr.append(f'<w:tcMar><w:left w:w="{tw(pad_izq)}" w:type="dxa"/>'
                      "</w:tcMar>")
        pr.append('<w:vAlign w:val="top"/>')
        cuerpo = parr([run(texto, estilo, tam, color)], interlinea=interlinea,
                      jc=jc)
        return f"<w:tc><w:tcPr>{''.join(pr)}</w:tcPr>{cuerpo}</w:tc>"

    def _xml_sectpr(self, portada=False):
        if portada:
            # Seccion de la portada: A4 sin margenes, sin pie y contando
            # como pagina 0, que es como la numera el PDF.
            return ("<w:sectPr>"
                    f'<w:pgSz w:w="{tw(self.w)}" w:h="{tw(self.h)}"/>'
                    '<w:pgMar w:top="0" w:right="0" w:bottom="0" w:left="0" '
                    'w:header="0" w:footer="0" w:gutter="0"/>'
                    '<w:pgNumType w:start="0"/>'
                    "</w:sectPr>")
        return (
            "<w:sectPr>"
            '<w:footerReference w:type="default" r:id="rId3"/>'
            f'<w:pgSz w:w="{tw(self.w)}" w:h="{tw(self.h)}"/>'
            f'<w:pgMar w:top="{tw(self.mt)}" w:right="{tw(self.mr)}" '
            f'w:bottom="{tw(self.mb)}" w:left="{tw(self.ml)}" '
            f'w:header="{tw(28)}" w:footer="{tw(30)}" w:gutter="0"/>'
            "</w:sectPr>")

    # -- empaquetado -------------------------------------------------------
    def _escribe_zip(self, medios, cuerpo):
        ns = (
            'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/'
            '2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/'
            '2006/relationships" '
            'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/'
            'wordprocessingDrawing"')
        cab = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

        documento = f"{cab}<w:document {ns}><w:body>{cuerpo}</w:body></w:document>"

        estilos = (
            f"{cab}<w:styles {ns}><w:docDefaults><w:rPrDefault><w:rPr>"
            f'<w:rFonts w:ascii="{FUENTE_DOCX}" w:hAnsi="{FUENTE_DOCX}"'
            f' w:cs="{FUENTE_DOCX}"/>'
            f'<w:color w:val="{col(TINTA)}"/>'
            f'<w:sz w:val="{hp(9.5)}"/><w:szCs w:val="{hp(9.5)}"/>'
            '<w:lang w:val="es-MX"/></w:rPr></w:rPrDefault>'
            "<w:pPrDefault><w:pPr>"
            '<w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
            "</w:pPr></w:pPrDefault></w:docDefaults>"
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
            '<w:name w:val="Normal"/><w:qFormat/></w:style>'
            "</w:styles>")

        marca = "NOVA · Documento de diseño · Producto 1"
        pie = (
            f"{cab}<w:ftr {ns}>" + parr(
                [run(marca, "R", 7.5, SUAVE),
                 "<w:r>" + rpr("R", 7.5, SUAVE) + "<w:tab/></w:r>",
                 "<w:r>" + rpr("R", 7.5, SUAVE) +
                 '<w:fldChar w:fldCharType="begin"/></w:r>',
                 "<w:r>" + rpr("R", 7.5, SUAVE) +
                 '<w:instrText xml:space="preserve"> PAGE </w:instrText>'
                 "</w:r>",
                 "<w:r>" + rpr("R", 7.5, SUAVE) +
                 '<w:fldChar w:fldCharType="end"/></w:r>'],
                interlinea=11,
                bordes=('<w:pBdr><w:top w:val="single" w:sz="4" '
                        f'w:color="{col(LINEA)}" w:space="4"/></w:pBdr>'),
                extra=('<w:tabs><w:tab w:val="right" '
                       f'w:pos="{tw(self.ancho_util)}"/></w:tabs>')
            ) + "</w:ftr>")
        tipos = [cab,
                 '<Types xmlns="http://schemas.openxmlformats.org/package/'
                 '2006/content-types">',
                 '<Default Extension="rels" ContentType="application/'
                 'vnd.openxmlformats-package.relationships+xml"/>',
                 '<Default Extension="xml" ContentType="application/xml"/>',
                 '<Default Extension="png" ContentType="image/png"/>']
        for parte, tipo in (("document", "document.main"),
                            ("styles", "styles"),
                            ("footer1", "footer")):
            tipos.append(f'<Override PartName="/word/{parte}.xml" '
                         'ContentType="application/vnd.openxmlformats-'
                         f'officedocument.wordprocessingml.{tipo}+xml"/>')
        tipos.append('<Override PartName="/docProps/core.xml" '
                     'ContentType="application/vnd.openxmlformats-package.'
                     'core-properties+xml"/>')
        tipos.append("</Types>")

        rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        raiz = (f"{cab}<Relationships xmlns=\"http://schemas.openxmlformats."
                "org/package/2006/relationships\">"
                f'<Relationship Id="rId1" Type="{rel}/officeDocument" '
                'Target="word/document.xml"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.'
                'org/package/2006/relationships/metadata/core-properties" '
                'Target="docProps/core.xml"/></Relationships>')

        rels = [f"{cab}<Relationships xmlns=\"http://schemas.openxmlformats."
                "org/package/2006/relationships\">",
                f'<Relationship Id="rId1" Type="{rel}/styles" '
                'Target="styles.xml"/>',
                f'<Relationship Id="rId3" Type="{rel}/footer" '
                'Target="footer1.xml"/>']
        for n, (nombre, _) in enumerate(medios, 1):
            rels.append(f'<Relationship Id="rId{100 + n}" Type="{rel}/image" '
                        f'Target="media/{nombre}"/>')
        rels.append("</Relationships>")

        core = (f"{cab}<cp:coreProperties "
                'xmlns:cp="http://schemas.openxmlformats.org/package/2006/'
                'metadata/core-properties" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/">'
                "<dc:title>NOVA - Documento de diseño</dc:title>"
                "<dc:creator>Ivan Gonzalez Ramirez</dc:creator>"
                "<dc:subject>Producto 1. Tabla 3, Plantilla del Documento "
                "de Diseño</dc:subject>"
                "</cp:coreProperties>")

        with zipfile.ZipFile(self.destino, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", "".join(tipos))
            z.writestr("_rels/.rels", raiz)
            z.writestr("docProps/core.xml", core)
            z.writestr("word/document.xml", documento)
            z.writestr("word/styles.xml", estilos)
            z.writestr("word/footer1.xml", pie)
            z.writestr("word/_rels/document.xml.rels", "".join(rels))
            for nombre, datos in medios:
                z.writestr(f"word/media/{nombre}", datos)
