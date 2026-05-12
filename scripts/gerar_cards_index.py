#!/usr/bin/env python3
"""
scripts/gerar_cards_index.py
────────────────────────────
Lê search-index.json e, para cada artigo, abre o .md correspondente
para extrair o featuredImage do frontmatter.

Gera articles-cards.json com: title, path, category, date, featuredImage.
Esse arquivo substitui tanto o search-index.json (para listagem)
quanto as chamadas individuais à API do GitHub (para imagens).

Uso:
    python scripts/gerar_cards_index.py

Saída: articles-cards.json na raiz do repositório.
"""

import json
import os
import re
import sys

ROOT         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEARCH_INDEX = os.path.join(ROOT, "search-index.json")
CARDS_INDEX  = os.path.join(ROOT, "articles-cards.json")


def extrair_featured_image(md_path: str) -> str:
    """Lê as primeiras 30 linhas do .md e retorna featuredImage se existir."""
    full = os.path.join(ROOT, md_path)
    if not os.path.exists(full):
        return ""
    try:
        with open(full, encoding="utf-8") as f:
            cabecalho = "".join(f.readline() for _ in range(30))
        m = re.search(r'^featuredImage:\s*["\']?(.+?)["\']?\s*$', cabecalho, re.MULTILINE)
        if m:
            return m.group(1).strip().strip("\"'")
    except Exception:
        pass
    return ""


def gerar():
    if not os.path.exists(SEARCH_INDEX):
        print(f"[ERRO] Não encontrado: {SEARCH_INDEX}")
        sys.exit(1)

    tamanho_original = os.path.getsize(SEARCH_INDEX)
    print(f"[→] Lendo search-index.json ({tamanho_original / 1024:.0f} KB)...")

    with open(SEARCH_INDEX, encoding="utf-8") as f:
        dados = json.load(f)

    artigos = dados if isinstance(dados, list) else (
        dados.get("articles") or dados.get("artigos") or []
    )

    total = len(artigos)
    print(f"[→] Processando {total} artigos (extraindo featuredImage)...")

    cards = []
    com_imagem = 0

    for i, a in enumerate(artigos, 1):
        path  = a.get("path", "")
        title = a.get("title", "")
        if not path or not title:
            continue

        img = extrair_featured_image(path)
        if img:
            com_imagem += 1

        card = {
            "title":    title,
            "path":     path,
            "category": a.get("category", ""),
            "date":     a.get("date", ""),
        }
        if img:
            card["featuredImage"] = img

        cards.append(card)

        if i % 500 == 0:
            print(f"    {i}/{total}...")

    # Mais recente primeiro
    cards.sort(key=lambda x: x.get("date", ""), reverse=True)

    with open(CARDS_INDEX, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, separators=(",", ":"))

    tamanho_novo = os.path.getsize(CARDS_INDEX)
    reducao = (1 - tamanho_novo / tamanho_original) * 100
    print(f"\n[✓] articles-cards.json gerado:")
    print(f"    {len(cards)} artigos  |  {com_imagem} com featuredImage")
    print(f"    {tamanho_novo / 1024:.1f} KB  (era {tamanho_original / 1024:.0f} KB — {reducao:.0f}% menor)")


if __name__ == "__main__":
    gerar()
