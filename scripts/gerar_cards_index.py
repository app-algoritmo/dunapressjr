#!/usr/bin/env python3
"""
scripts/gerar_cards_index.py
────────────────────────────
Lê search-index.json e gera articles-cards.json com apenas os campos
necessários para renderizar os cards de artigos (title, path, category, date).

O search-index.json cresce sem parar (4+ MB) porque acumula todos os artigos.
Este script produz um arquivo enxuto, ordenado do mais recente para o mais
antigo, e deve ser chamado a cada novo artigo publicado.

Uso:
    python scripts/gerar_cards_index.py

Saída: articles-cards.json na raiz do repositório.
"""

import json
import os
import sys

ROOT         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEARCH_INDEX = os.path.join(ROOT, "search-index.json")
CARDS_INDEX  = os.path.join(ROOT, "articles-cards.json")

# Apenas os campos que o card precisa exibir
CAMPOS_CARD = {"title", "path", "category", "date"}


def gerar():
    if not os.path.exists(SEARCH_INDEX):
        print(f"[ERRO] Não encontrado: {SEARCH_INDEX}")
        sys.exit(1)

    tamanho_original = os.path.getsize(SEARCH_INDEX)
    print(f"[→] Lendo search-index.json ({tamanho_original / 1024:.0f} KB)...")

    with open(SEARCH_INDEX, encoding="utf-8") as f:
        dados = json.load(f)

    # Suporte a lista direta ou dict com chave "articles"/"artigos"
    if isinstance(dados, dict):
        artigos = dados.get("articles") or dados.get("artigos") or []
    else:
        artigos = dados

    cards = []
    for a in artigos:
        card = {k: a[k] for k in CAMPOS_CARD if k in a}
        if card.get("title") and card.get("path"):
            cards.append(card)

    # Ordenar do mais recente para o mais antigo
    cards.sort(key=lambda x: x.get("date", ""), reverse=True)

    # Gravar minificado (sem espaços extras = menor ainda)
    with open(CARDS_INDEX, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, separators=(",", ":"))

    tamanho_novo = os.path.getsize(CARDS_INDEX)
    reducao = (1 - tamanho_novo / tamanho_original) * 100
    print(f"[✓] articles-cards.json gerado:")
    print(f"    {len(cards)} artigos")
    print(f"    {tamanho_novo / 1024:.1f} KB  (era {tamanho_original / 1024:.0f} KB — {reducao:.0f}% menor)")


if __name__ == "__main__":
    gerar()
