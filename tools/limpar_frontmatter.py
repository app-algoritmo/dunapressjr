#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — limpeza de HTML no frontmatter e detecção de duplicatas.

Herança da migração do WordPress: títulos, linhas finas e resumos que
vieram com <strong>, <em>, <p> e entidades HTML. O gerador escapa essas
tags, então elas aparecem como texto na capa.

Por padrão só relata. Nada é escrito sem --aplicar.

    python3 tools/limpar_frontmatter.py                 # diagnóstico
    python3 tools/limpar_frontmatter.py --duplicatas    # títulos repetidos
    python3 tools/limpar_frontmatter.py --aplicar       # grava as correções
"""
import os, re, sys, html, glob
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIGOS = os.path.join(RAIZ, "artigos")

CAMPOS = ("title", "subtitle", "description")

# Só tag HTML de verdade. Um título legítimo pode conter "<" solto
# (por exemplo "PIB < 1%"), e esse não deve ser tocado.
TAG = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(?:\s[^<>]*)?/?>")


def limpar(valor):
    """Remove tags, resolve entidades e normaliza espaço."""
    novo = TAG.sub("", valor)
    novo = html.unescape(novo)
    novo = re.sub(r"\s+", " ", novo).strip()
    return novo


def desaspar(valor):
    """Tira as aspas do YAML e desfaz o escape interno. Título com
    dois-pontos ou apóstrofo vem entre aspas simples, com '' no lugar de ',
    e tratá-lo como texto solto corrompe o campo."""
    v = valor.strip()
    if len(v) >= 2 and v[0] == v[-1] == '"':
        return v[1:-1].replace('\\"', '"')
    if len(v) >= 2 and v[0] == v[-1] == "'":
        return v[1:-1].replace("''", "'")
    return v


def aspar(valor):
    """Reescreve o valor com o tipo de aspas que o conteúdo permite."""
    if '"' in valor:
        return "'" + valor.replace("'", "''") + "'"
    return '"' + valor + '"'


def campos_do_frontmatter(texto):
    """Devolve (linhas, indice_de_fechamento). Frontmatter mal formado
    devolve indice None, e o arquivo é ignorado em vez de corrompido."""
    linhas = texto.split("\n")
    if not linhas or linhas[0].strip() != "---":
        return linhas, None
    for i, l in enumerate(linhas[1:], start=1):
        if l.strip() == "---":
            return linhas, i
    return linhas, None


def main():
    aplicar = "--aplicar" in sys.argv
    so_duplicatas = "--duplicatas" in sys.argv

    arquivos = sorted(glob.glob(os.path.join(ARTIGOS, "**", "*.md"),
                                recursive=True))
    if not arquivos:
        print(f"Nenhum .md em {ARTIGOS}")
        sys.exit(1)

    sujos, ignorados = [], []
    por_titulo = defaultdict(list)

    for caminho in arquivos:
        texto = open(caminho, encoding="utf-8").read()
        linhas, fim = campos_do_frontmatter(texto)
        if fim is None:
            ignorados.append(caminho)
            continue

        mudou = False
        for i in range(1, fim):
            m = re.match(r'^(title|subtitle|description):\s*(.*)$', linhas[i])
            if not m:
                continue
            campo, valor = m.group(1), m.group(2)
            miolo = desaspar(valor)
            if not TAG.search(miolo) and "&" not in miolo:
                continue
            novo = limpar(miolo)
            if novo == miolo:
                continue
            sujos.append((caminho, campo, miolo, novo))
            linhas[i] = f"{campo}: {aspar(novo)}"
            mudou = True

            if campo == "title":
                por_titulo[novo.lower()].append(caminho)

        if campo_titulo := next(
                (re.match(r'^title:\s*"?(.*?)"?\s*$', linhas[i])
                 for i in range(1, fim) if linhas[i].startswith("title:")), None):
            por_titulo[limpar(campo_titulo.group(1)).lower()].append(caminho)

        if mudou and aplicar:
            open(caminho, "w", encoding="utf-8").write("\n".join(linhas))

    if so_duplicatas:
        repetidos = {t: v for t, v in por_titulo.items() if len(set(v)) > 1}
        print(f"TÍTULOS REPETIDOS: {len(repetidos)}\n")
        for titulo, caminhos in sorted(repetidos.items())[:60]:
            print(f"  {titulo[:80]}")
            for c in sorted(set(caminhos)):
                print(f"      {os.path.relpath(c, RAIZ)}")
            print()
        return

    print(f"Arquivos varridos ........ {len(arquivos)}")
    print(f"Campos com HTML .......... {len(sujos)}")
    print(f"Frontmatter mal formado .. {len(ignorados)}")
    print()

    for caminho, campo, antes, depois in sujos[:40]:
        print(f"  {os.path.relpath(caminho, RAIZ)}")
        print(f"    {campo}  antes:  {antes[:90]}")
        print(f"    {campo}  depois: {depois[:90]}")
        print()
    if len(sujos) > 40:
        print(f"  (e mais {len(sujos) - 40})\n")

    for c in ignorados[:10]:
        print(f"  ignorado, frontmatter mal formado: {os.path.relpath(c, RAIZ)}")

    if aplicar:
        print(f"\n{len(sujos)} campo(s) corrigido(s) e gravado(s).")
    else:
        print("\nDiagnóstico apenas. Rode com --aplicar para gravar.")


if __name__ == "__main__":
    main()
