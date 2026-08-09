#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — baixa as fontes para servir do próprio domínio.

Rode uma vez e versione os .woff2 no repositório. Depois disso o site não
depende mais de fonts.googleapis.com: menos uma conexão externa no caminho
crítico, e nenhum IP de leitor enviado a terceiro.

    python3 tools/baixar_fontes.py
"""
import os, re, urllib.request

DESTINO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "assets", "fonts")

# O CSS da API v2 devolve subconjuntos; latin-ext cobre o português.
FAMILIAS = {
    "spectral-600":        "Spectral:wght@600",
    "spectral-700":        "Spectral:wght@700",
    "spectral-400i":       "Spectral:ital,wght@1,400",
    "source-serif-400":    "Source+Serif+4:opsz,wght@8..60,400",
    "source-serif-600":    "Source+Serif+4:opsz,wght@8..60,600",
    "source-serif-400i":   "Source+Serif+4:ital,opsz,wght@1,8..60,400",
    "libre-franklin-400":  "Libre+Franklin:wght@400",
    "libre-franklin-600":  "Libre+Franklin:wght@600",
    "libre-franklin-700":  "Libre+Franklin:wght@700",
}

# User-agent moderno faz a API devolver woff2 em vez de ttf
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def buscar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    os.makedirs(DESTINO, exist_ok=True)
    for nome, familia in FAMILIAS.items():
        alvo = os.path.join(DESTINO, f"{nome}.woff2")
        if os.path.exists(alvo):
            print(f"  existe   {nome}.woff2")
            continue
        css = buscar(f"https://fonts.googleapis.com/css2?family={familia}"
                     "&display=swap&subset=latin-ext").decode()
        urls = re.findall(r"url\((https://[^)]+\.woff2)\)", css)
        if not urls:
            print(f"  FALHOU   {nome}: nenhum woff2 no CSS")
            continue
        with open(alvo, "wb") as fh:
            fh.write(buscar(urls[-1]))
        print(f"  baixado  {nome}.woff2  ({os.path.getsize(alvo) // 1024} KB)")

    print(f"\nFontes em {DESTINO}")
    print("Versione os .woff2 no repositório e remova o link do Google Fonts.")


if __name__ == "__main__":
    main()
