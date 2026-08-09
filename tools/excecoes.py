#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — exceções ao noindex.

Cruza a exportação do Search Console com a lista de páginas marcadas para
sair do índice. Página que recebe clique real fica, independentemente do
que a régua editorial disse.

Uso:
    python3 excecoes.py search-console.csv [cliques_minimos]
"""
import csv, json, sys, re, os
from urllib.parse import urlparse, unquote

DADOS = os.path.join(os.path.dirname(__file__), "dados")
MINIMO = int(sys.argv[2]) if len(sys.argv) > 2 else 1


def caminho_de(url):
    try:
        p = urlparse(unquote(url.strip()))
        return (p.path + ("?" + p.query if p.query else "")) or "/"
    except Exception:
        return None


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)

    # 1. ler o CSV do Search Console (o nome das colunas varia com o idioma)
    cliques = {}
    with open(sys.argv[1], encoding="utf-8-sig", newline="") as fh:
        leitor = csv.DictReader(fh)
        col_url = col_cli = None
        for c in leitor.fieldnames or []:
            b = c.strip().lower()
            if col_url is None and b in ("página", "pagina", "page", "url"):
                col_url = c
            if col_cli is None and b in ("cliques", "clicks"):
                col_cli = c
        if not col_url:
            print(f"Não achei a coluna de página em: {leitor.fieldnames}")
            sys.exit(1)
        for linha in leitor:
            cam = caminho_de(linha[col_url])
            if not cam:
                continue
            try:
                n = int(float(str(linha.get(col_cli, 0)).replace(".", "").replace(",", ".") or 0))
            except ValueError:
                n = 0
            cliques[cam] = cliques.get(cam, 0) + n

    print(f"URLs no Search Console: {len(cliques)}")

    # 2. mapear URL antiga → nova, para achar as marcadas
    antiga_para_nova = {}
    with open(f"{DADOS}/redirects.map", encoding="utf-8") as fh:
        for l in fh:
            p = l.rsplit(" ", 2)
            if len(p) == 3:
                antiga_para_nova[p[0]] = p[1]
    wp = json.load(open(f"{DADOS}/wp-legado.json", encoding="utf-8"))

    def para_nova(cam):
        if cam in antiga_para_nova:
            return antiga_para_nova[cam]
        m = re.match(r"^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$", cam)
        if m:
            a, me, d, slug = m.groups()
            for s, url in wp.get(f"{a}/{me}/{d}", []):
                if slug.startswith(s[:40]) or s.startswith(slug[:40]):
                    return url
        return cam if cam.count("/") >= 3 else None

    # 3. cruzar com a lista de noindex
    marcadas = {}
    with open(f"{DADOS}/noindex.txt", encoding="utf-8") as fh:
        for l in fh:
            url, _, motivos = l.strip().partition("\t")
            marcadas[url] = motivos

    excecoes, total_cliques = {}, 0
    for cam, n in cliques.items():
        if n < MINIMO:
            continue
        nova = para_nova(cam)
        if nova and nova in marcadas:
            excecoes[nova] = max(excecoes.get(nova, 0), n)
            total_cliques += n

    ordenadas = sorted(excecoes.items(), key=lambda x: -x[1])
    with open(f"{DADOS}/excecoes.txt", "w", encoding="utf-8") as fh:
        for url, n in ordenadas:
            fh.write(f"{url}\t{n}\t{marcadas[url]}\n")

    print(f"Páginas marcadas para noindex ....... {len(marcadas)}")
    print(f"Delas, com {MINIMO}+ clique(s) ............. {len(excecoes)}")
    print(f"Cliques que seriam perdidos ......... {total_cliques}")
    print(f"\nGravado em {DADOS}/excecoes.txt")
    if ordenadas:
        print("\nAs 10 de maior tráfego que seriam sacrificadas:")
        for url, n in ordenadas[:10]:
            print(f"  {n:>6} cliques  [{marcadas[url]}]  {url[:64]}")
    print("\nPara aplicar: classificar.py lê esse arquivo e preserva a lista.")


if __name__ == "__main__":
    main()
