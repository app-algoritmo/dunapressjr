#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — remove apelos comerciais que sobraram sem link.

O limpar.py tirou os links, mas a frase que os acompanhava ficou dentro de
parágrafos longos. Texto de anúncio apontando para lugar nenhum é pior que
o anúncio: parece defeito.

Aqui a remoção é cirúrgica — corta a frase, não o parágrafo.
"""
import os, re, glob
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cada padrão remove UMA frase, delimitada por pontuação. Nunca o parágrafo.
FRASES = [
    (r"[^.!?\n]*\bclique e comece j[áa]\b[^.!?\n]*[.!?]?", "clique e comece já"),
    (r"[^.!?\n]*\bpara saber mais,?\s*clique[^.!?\n]*[.!?]?", "para saber mais clique"),
    (r"[^.!?\n]*\bclique aqui para (fechar|acessar|adquirir|comprar)[^.!?\n]*[.!?]?",
     "clique aqui para…"),
    (r"^\s*\*{0,2}Disclaimer\*{0,2}\s*[-–—]\s*Clique aqui.*$", "disclaimer com clique"),
    (r"^\s*Saiba mais em:\s*$", "saiba mais órfão"),
]


def limpar(corpo):
    c = Counter()
    for rx, rotulo in FRASES:
        novo, n = re.subn(rx, "", corpo, flags=re.I | re.M)
        if n:
            c[rotulo] += n
            corpo = novo
    # higiene: espaço duplo e linha que ficou vazia
    corpo = re.sub(r"[ \t]{2,}", " ", corpo)
    corpo = re.sub(r"^[ \t]*[.!?,;:]\s*$", "", corpo, flags=re.M)
    corpo = re.sub(r"\n{3,}", "\n\n", corpo)
    return corpo, c


def main():
    total = Counter()
    alterados = 0
    for caminho in sorted(glob.glob(os.path.join(RAIZ, "artigos", "*", "*.md"))):
        with open(caminho, encoding="utf-8", errors="replace") as fh:
            bruto = fh.read()
        if bruto.startswith("---"):
            f = bruto.find("\n---", 3)
            cab, corpo = (bruto[:f + 4], bruto[f + 4:]) if f > 0 else ("", bruto)
        else:
            cab, corpo = "", bruto
        novo, c = limpar(corpo)
        if not c:
            continue
        alterados += 1
        total.update(c)
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(cab + novo.rstrip() + "\n")

    print("APELOS COMERCIAIS ÓRFÃOS")
    print("=" * 46)
    print(f"Artigos alterados ....... {alterados}")
    print()
    for k, v in total.most_common():
        print(f"  {v:5}  {k}")


if __name__ == "__main__":
    main()
