#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — normaliza assinaturas e limpa emoji dos metadados.

Três defeitos herdados da conversão do WordPress:

  1. acentos perdidos nos nomes — "Joabson Joao", "Duna Press Redacao"
  2. preposições em maiúscula — "Paulo Fernando De Barros"
  3. emoji em título e crédito de foto

Numa assinatura de jornal isso denuncia processo automático. O nome de quem
escreve é a unidade de credibilidade do jornal: escrever errado é falta
editorial, não detalhe tipográfico.

    python3 tools/normalizar_assinaturas.py            # aplica
    python3 tools/normalizar_assinaturas.py --ensaio   # só mostra
"""
import os, re, sys, glob, unicodedata
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Correções confirmadas. Só entram nomes cuja grafia correta é certa —
# quando há dúvida, o nome fica como está e aparece no relatório para
# decisão humana.
NOMES = {
    "Joabson Joao": "Joabson João",
    "Duna Press Redacao": "Redação Duna Press",
    "Duna Press Redação": "Redação Duna Press",
    "Paulo Fernando De Barros": "Paulo Fernando de Barros",
    "Natalia Bellan": "Natália Bellan",
    "Vitor Guerino": "Vítor Guerino",
    "Leonardo Gabossa": "Leonardo Garbossa",
    "Hermes Rodrigues Nery": "Hermes Rodrigues Nery",
}

# Preposições vão em minúscula no meio do nome — norma do português.
PREPOSICOES = {"de", "da", "do", "das", "dos", "e"}


def arrumar_preposicoes(nome):
    partes = nome.split()
    if len(partes) < 3:
        return nome
    saida = [partes[0]]
    for p in partes[1:-1]:
        saida.append(p.lower() if p.lower() in PREPOSICOES else p)
    saida.append(partes[-1])
    return " ".join(saida)


def normalizar_nome(nome):
    nome = re.sub(r"\s+", " ", nome.strip())
    if nome in NOMES:
        return NOMES[nome]
    return arrumar_preposicoes(nome)


def sem_emoji(texto):
    """Remove pictogramas. Preserva acentuação e pontuação tipográfica —
    travessão, aspas curvas e reticências pertencem ao texto."""
    saida = []
    for c in texto:
        p = ord(c)
        if (0x1F000 <= p <= 0x1FAFF or 0x2600 <= p <= 0x27BF
                or 0xFE00 <= p <= 0xFE0F or p == 0x20E3
                or 0x1F1E6 <= p <= 0x1F1FF):
            continue
        saida.append(c)
    return re.sub(r"\s{2,}", " ", "".join(saida)).strip()


def main():
    ensaio = "--ensaio" in sys.argv
    trocas = Counter()
    emojis = Counter()
    suspeitos = Counter()
    alterados = 0

    for caminho in sorted(glob.glob(os.path.join(RAIZ, "artigos", "*", "*.md"))):
        with open(caminho, encoding="utf-8", errors="replace") as fh:
            bruto = fh.read()
        if not bruto.startswith("---"):
            continue
        fim = bruto.find("\n---", 3)
        if fim < 0:
            continue
        cab, resto = bruto[3:fim], bruto[fim:]
        original = cab

        # assinatura
        m = re.search(r"^author:\s*(.+)$", cab, re.M)
        if m:
            antigo = m.group(1).strip().strip("\"'")
            novo = normalizar_nome(antigo)
            if novo != antigo:
                trocas[f"{antigo} → {novo}"] += 1
                cab = re.sub(r"^author:\s*.+$", 'author: "%s"' % novo,
                             cab, count=1, flags=re.M)
            # nome sem nenhum acento e com 2+ palavras: pode faltar acento
            elif (" " in novo and novo == unicodedata.normalize("NFKD", novo)
                  .encode("ascii", "ignore").decode()
                  and novo not in NOMES.values()):
                suspeitos[novo] += 1

        # emoji em campos de texto
        for campo in ("title", "subtitle", "description",
                      "photoAuthor", "photoSource"):
            m = re.search(r"^%s:\s*(.+)$" % campo, cab, re.M)
            if not m:
                continue
            antigo = m.group(1)
            novo = sem_emoji(antigo)
            if novo != antigo:
                emojis[campo] += 1
                cab = re.sub(r"^%s:\s*.+$" % campo,
                             lambda _: "%s: %s" % (campo, novo),
                             cab, count=1, flags=re.M)

        if cab != original:
            alterados += 1
            if not ensaio:
                with open(caminho, "w", encoding="utf-8") as fh:
                    fh.write("---" + cab + resto)

    print("NORMALIZAÇÃO DE ASSINATURAS" + ("  [ensaio]" if ensaio else ""))
    print("=" * 56)
    print("Artigos alterados ....... %d" % alterados)
    print()
    if trocas:
        print("ASSINATURAS CORRIGIDAS")
        print("-" * 56)
        for k, v in trocas.most_common():
            print("  %5d  %s" % (v, k))
        print()
    if emojis:
        print("EMOJI REMOVIDO")
        print("-" * 56)
        for k, v in emojis.most_common():
            print("  %5d  %s" % (v, k))
        print()
    if suspeitos:
        print("POSSIVELMENTE SEM ACENTO — conferir à mão")
        print("-" * 56)
        print("  Nomes de duas ou mais palavras sem nenhum acento. Podem")
        print("  estar certos; podem ter perdido acento na conversão.")
        print()
        for k, v in suspeitos.most_common(15):
            print("  %5d  %s" % (v, k))
        print()
        print("  Para corrigir, acrescente o par ao dicionário NOMES")
        print("  no topo deste arquivo e rode de novo.")


if __name__ == "__main__":
    main()
