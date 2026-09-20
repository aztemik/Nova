#!/usr/bin/env python3
"""Documento 1 del proyecto NOVA en Word (.docx).

No hay un segundo documento: hay un segundo motor. Este script no copia
nada de `gen_doc1.py` ni lo modifica; lo importa, le cambia la imprenta por
`nova_docx.Doc` y le deja generar el mismo documento con el mismo contenido,
el mismo orden y los mismos estilos.

    PYTHONPATH=.venv/lib/python3.14/site-packages python3 tools/gen_doc1_docx.py

Si `gen_doc1.py` cambia, el .docx cambia con el; no hay nada que sincronizar
a mano.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gen_doc1 as G                                        # noqa: E402
import nova_docx                                            # noqa: E402

SALIDA = os.path.join(G.RAIZ, "GonzalezRamirezIvan_diseño.docx")


def main():
    G.Doc = nova_docx.Doc
    G.SALIDA = SALIDA
    G.main()


if __name__ == "__main__":
    main()
