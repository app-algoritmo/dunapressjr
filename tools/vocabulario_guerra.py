#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — vocabulário da guerra Rússia–Ucrânia.

Localiza «invasão», «ocupação» e «agressão» APENAS em artigos sobre a guerra
e APENAS na voz do jornal. Não toca em citação, em fala atribuída, nem em
ocorrência sobre outro conflito.

Por que existe: uma busca ingênua por «ocupa» casa dentro de «preocupação»,
«preocupado» e «despreocupado», e uma busca por «ocupada» pega «a elite
estará ocupada com suas eleições». Numa varredura do acervo, a maioria
esmagadora das ocorrências é falso positivo.

O trabalho é em duas etapas, de propósito:

    python3 tools/vocabulario_guerra.py            # gera a proposta, não altera nada
    # revise dados/proposta-vocabulario.txt, apague as linhas que não quer
    python3 tools/vocabulario_guerra.py --aplicar  # aplica só o que sobrou
"""
import os, re, sys, glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIGOS = os.path.join(RAIZ, "artigos")
PROPOSTA = os.path.join(RAIZ, "dados", "proposta-vocabulario.txt")

# O artigo precisa ser sobre esta guerra.
TEMA = re.compile(r"ucr[âa]nia|ucranian|kiev|ky[ií]v|zelensk|donbas|donetsk|luhansk|kherson|zapor", re.I)

# Fronteira de palavra de verdade, e «preocupa» fora do caminho.
ALVOS = re.compile(
    r"(?<![a-zçãéíóúâêôàü])("
    r"invas(?:ão|ões)|invadi(?:u|r|ram|ndo|da|do|das|dos)|"
    r"ocupa(?:ção|ções|da|do|das|dos)|"
    r"agress(?:ão|ões|or|ora|ores)"
    r")(?![a-zçãéíóúâêôàü])", re.I)

# Sinais de que a linha reproduz fala de terceiro — nesses casos não se mexe.
CITACAO = re.compile(r"[«»\u201c\u201d\"]|\bdisse\b|\bafirm|\bdeclar|\bsegundo\b|\bescreveu\b|"
                     r"\bcitou\b|\bacusou\b|\bchamou\b|\bsustenta\b|\bnas palavras\b", re.I)

# Outro conflito na mesma linha: não é desta guerra.
OUTRO = re.compile(r"s[íi]ria|jap[ãa]o|cuba|canad[áa]|m[ée]xico|china|taiwan|iraque|i[êe]men|"
                   r"gaza|israel|palestin|afeganist|sovi[ée]tic|segunda guerra|nazist|"
                   r"ba[íi]a dos porcos", re.I)

SUGESTOES = [
    (re.compile(r"\bdesde o in[íi]cio da invas[ãa]o\b", re.I), "desde o início da guerra"),
    (re.compile(r"\bdesde a invas[ãa]o\b", re.I),             "desde o início da guerra"),
    (re.compile(r"\bantes da invas[ãa]o em larga escala\b", re.I), "antes do início da guerra"),
    (re.compile(r"\binvas[ãa]o em larga escala\b", re.I),     "guerra em larga escala"),
    (re.compile(r"\binvas[ãa]o russa da Ucr[âa]nia\b", re.I), "guerra da Rússia na Ucrânia"),
    (re.compile(r"\binvas[ãa]o da Ucr[âa]nia\b", re.I),       "guerra na Ucrânia"),
    (re.compile(r"\binvas[ãa]o russa\b", re.I),               "ofensiva russa"),
    (re.compile(r"\bocupa[çc][ãa]o russa\b", re.I),           "controle russo"),
    (re.compile(r"\bterrit[óo]rios? ocupados?\b", re.I),      "território sob controle russo"),
    (re.compile(r"\bCrimeia ocupada\b", re.I),                "Crimeia sob controle russo"),
    (re.compile(r"\bocupada pela R[úu]ssia\b", re.I),         "sob controle da Rússia"),
    (re.compile(r"\bocupada por for[çc]as russas\b", re.I),   "sob controle de forças russas"),
    (re.compile(r"\bagress[ãa]o russa\b", re.I),              "ofensiva russa"),
]


def sugerir(trecho):
    for rx, novo in SUGESTOES:
        m = rx.search(trecho)
        if m:
            return m.group(0), novo
    return None, None


def varrer():
    achados, sem_regra, citados = [], [], 0
    for caminho in sorted(glob.glob(os.path.join(ARTIGOS, "**", "*.md"), recursive=True)):
        texto = open(caminho, encoding="utf-8").read()
        if not TEMA.search(texto):
            continue
        for n, linha in enumerate(texto.split("\n"), 1):
            if not ALVOS.search(linha):
                continue
            if CITACAO.search(linha) or OUTRO.search(linha):
                citados += 1
                continue
            velho, novo = sugerir(linha)
            rel = os.path.relpath(caminho, RAIZ)
            if velho:
                achados.append((rel, n, velho, novo, linha.strip()))
            else:
                sem_regra.append((rel, n, linha.strip()))
    return achados, sem_regra, citados


def main():
    aplicar = "--aplicar" in sys.argv
    if not aplicar:
        achados, sem_regra, citados = varrer()
        os.makedirs(os.path.dirname(PROPOSTA), exist_ok=True)
        with open(PROPOSTA, "w", encoding="utf-8") as fh:
            fh.write("# Uma troca por linha: caminho|linha|texto atual|texto novo\n")
            fh.write("# Apague as linhas que NÃO quer trocar. Depois rode com --aplicar.\n\n")
            for rel, n, velho, novo, ctx in achados:
                fh.write(f"{rel}|{n}|{velho}|{novo}\n")
        print(f"Trocas propostas ......... {len(achados)}")
        print(f"Ocorrência em citação .... {citados}  (não tocadas)")
        print(f"Sem regra, ver à mão ..... {len(sem_regra)}")
        print(f"\nProposta em {os.path.relpath(PROPOSTA, RAIZ)}")
        if sem_regra:
            print("\nSem regra automática:")
            for rel, n, ctx in sem_regra[:25]:
                print(f"  {rel}:{n}\n      {ctx[:150]}")
            if len(sem_regra) > 25:
                print(f"  (e mais {len(sem_regra)-25})")
        return

    if not os.path.exists(PROPOSTA):
        print("Rode primeiro sem --aplicar para gerar a proposta.")
        return
    porarq = {}
    for linha in open(PROPOSTA, encoding="utf-8"):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        rel, n, velho, novo = linha.split("|")
        porarq.setdefault(rel, []).append((int(n), velho, novo))

    total = 0
    for rel, trocas in porarq.items():
        caminho = os.path.join(RAIZ, rel)
        linhas = open(caminho, encoding="utf-8").read().split("\n")
        for n, velho, novo in trocas:
            i = n - 1
            if velho in linhas[i]:
                linhas[i] = linhas[i].replace(velho, novo, 1)
                total += 1
            else:
                print(f"  !! não encontrado: {rel}:{n} «{velho}»")
        open(caminho, "w", encoding="utf-8").write("\n".join(linhas))
    print(f"{total} troca(s) aplicada(s) em {len(porarq)} arquivo(s).")


if __name__ == "__main__":
    main()
