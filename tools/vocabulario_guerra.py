#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — vocabulário da guerra Rússia–Ucrânia.

Localiza «invasão», «ocupação» e «agressão» APENAS em artigos sobre a guerra,
APENAS no corpo do texto e APENAS na voz do jornal. Não toca em frontmatter,
em citação, em fala atribuída, nem em ocorrência sobre outro conflito.

O frontmatter fica de fora por um motivo prático: o slug do artigo é derivado
do título, e trocar uma palavra no título muda o endereço público. Três URLs
foram perdidas assim antes de esta trava existir.

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

# «ocupado» no sentido de atarefado: «estará ocupada com as eleições»,
# «ocupados mudando a imagem», «cassino extremamente ocupado».
OCIOSO = re.compile(r"ocupad[ao]s?\s+(?:com|em|a\s|na\s|no\s|lan[çc]|desenvolv|mudan|"
                    r"prepar|trabalh|cuidan|tentan|discut|negoci)|"
                    r"mant[ée]m\s+ocupad|manter\s+ocupad|invad\w*\s+a\s+rede", re.I)

# Fala com etiqueta de locutor: «TUCKER:», «PUTIN:», «SENHOR. FERTITTA:».
LOCUTOR = re.compile(r"^\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-ZÁÉÍÓÚÂÊÔÃÕÇ .]{2,}:", )

# A linha precisa falar desta guerra, não só o arquivo.
LINHA_TEMA = re.compile(r"ucr[âa]nia|ucranian|kiev|ky[ií]v|zelensk|donbas|donetsk|luhansk|"
                        r"kherson|zapor|r[úu]ssia|russo|russa|moscou|kremlin|putin", re.I)

# Outro conflito na mesma linha: não é desta guerra.
OUTRO = re.compile(r"s[íi]ria|jap[ãa]o|cuba|canad[áa]|m[ée]xico|china|taiwan|iraque|i[êe]men|"
                   r"gaza|israel|palestin|afeganist|sovi[ée]tic|segunda guerra|nazist|"
                   r"ba[íi]a dos porcos|alem[ãa]es|URSS|\b193\d|\b194\d|guerra fria|"
                   r"alemanha ocidental|pol[óo]nia|polonesa|lublin|holanda|ir[ãa]|"
                   r"coreia do norte|hungria", re.I)

# Linha que é link ou endereço: mexer aí quebra referência.
LINK = re.compile(r"https?://|\]\(")

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
    (re.compile(r"\ba R[úu]ssia invadiu a Ucr[âa]nia\b", re.I), "começou a guerra na Ucrânia"),
    (re.compile(r"\binvas[ãa]o da R[úu]ssia\b", re.I),         "ofensiva da Rússia"),
    (re.compile(r"\bocupa[çc][ãa]o da Ucr[âa]nia por tropas russas\b", re.I),
                                                              "entrada de tropas russas na Ucrânia"),
    (re.compile(r"\bocupa[çc][ãa]o da Ucr[âa]nia\b", re.I),    "guerra na Ucrânia"),
    (re.compile(r"\bregi[õo]es ocupadas\b", re.I),             "regiões sob controle russo"),
    (re.compile(r"\b[áa]reas ocupadas\b", re.I),               "áreas sob controle russo"),
    (re.compile(r"\bzonas ocupadas\b", re.I),                  "zonas sob controle russo"),
    (re.compile(r"\bcidades? ocupadas?\b", re.I),              "cidade sob controle russo"),
    (re.compile(r"\bantes da invas[ãa]o\b", re.I),             "antes da guerra"),
    (re.compile(r"\bdepois da invas[ãa]o\b", re.I),            "depois do início da guerra"),
    (re.compile(r"\blan[çc]ou sua invas[ãa]o ao\b", re.I),     "entrou em guerra com o"),
    (re.compile(r"\binvas[ãa]o de grande escala\b", re.I),     "guerra de grande escala"),
    (re.compile(r"\binvas[ãa]o de territ[óo]rios ucranianos por for[çc]as russas\b", re.I),
                                                              "entrada de forças russas em território ucraniano"),
    (re.compile(r"\ba invas[ãa]o continua\b", re.I),           "a guerra continua"),
    (re.compile(r"\bocupa[çc][ãa]o de alguns de seus territ[óo]rios\b", re.I),
                                                              "controle de alguns de seus territórios"),
    (re.compile(r"\bteria invadido a Ucr[âa]nia\b", re.I),     "teria entrado em guerra com a Ucrânia"),
    (re.compile(r"\bn[ãa]o tivesse invadido\b", re.I),         "não tivesse entrado em guerra"),
    (re.compile(r"\bocupada pelos russos\b", re.I),            "sob controle russo"),
    (re.compile(r"\ba R[úu]ssia invadiu a terra\b", re.I),     "começou a guerra"),
    (re.compile(r"\ba R[úu]ssia invadiu o pa[íi]s vizinho\b", re.I), "começou a guerra"),
    (re.compile(r"\bagress[ãa]o e ocupa[çc][ãa]o russas\b", re.I), "ofensiva e o controle russos"),
    (re.compile(r"\btropas de ocupa[çc][ãa]o\b", re.I),        "tropas russas"),
    (re.compile(r"\binvas[ãa]o das for[çc]as militares russas\b", re.I),
                                                              "entrada das forças militares russas"),
    (re.compile(r"\bguerra de agress[ãa]o\b", re.I),           "guerra"),
    (re.compile(r"\binvas[ãa]o de Putin [àa] Ucr[âa]nia\b", re.I), "ofensiva de Putin na Ucrânia"),
    (re.compile(r"\bagress[ãa]o militar\b", re.I),             "ação militar"),
    (re.compile(r"\ba ocupa[çc][ãa]o e a atividade militar russa\b", re.I),
                                                              "o controle russo e a atividade militar"),
    (re.compile(r"\buma invas[ãa]o limitada\b", re.I),         "uma ofensiva limitada"),
    (re.compile(r"\bqualquer agress[ãa]o futura\b", re.I),     "qualquer ofensiva futura"),
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
        linhas = texto.split("\n")
        # O frontmatter fica fora: mexer em title muda o slug, e mudar o slug
        # quebra o endereço público do artigo. Só o corpo é editável aqui.
        fim_fm = 0
        if linhas and linhas[0].strip() == "---":
            for i, l in enumerate(linhas[1:], 1):
                if l.strip() == "---":
                    fim_fm = i
                    break
        for n, linha in enumerate(linhas, 1):
            if n <= fim_fm + 1:
                continue
            if not ALVOS.search(linha):
                continue
            if not LINHA_TEMA.search(linha):
                continue
            if OCIOSO.search(linha) or LOCUTOR.search(linha) or LINK.search(linha):
                continue
            if CITACAO.search(linha) or OUTRO.search(linha):
                citados += 1
                continue
            velho, novo = sugerir(linha)
            rel = os.path.relpath(caminho, RAIZ)
            if velho:
                achados.append((rel, n, velho, novo, linha.strip()))
            else:
                m = ALVOS.search(linha)
                ini = max(0, m.start() - 70)
                sem_regra.append((rel, n, "…" + linha[ini:m.end() + 70].strip() + "…"))
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
            for rel, n, ctx in sem_regra[:40]:
                print(f"  {rel}:{n}\n      {ctx}")
            if len(sem_regra) > 25:
                print(f"  (e mais {len(sem_regra)-40})")
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
        fim_fm = 0
        if linhas and linhas[0].strip() == "---":
            for j, l in enumerate(linhas[1:], 1):
                if l.strip() == "---":
                    fim_fm = j
                    break
        for n, velho, novo in trocas:
            i = n - 1
            if n <= fim_fm + 1:
                print(f"  -- frontmatter, ignorado: {rel}:{n}")
                continue
            if velho in linhas[i]:
                linhas[i] = linhas[i].replace(velho, novo, 1)
                total += 1
            else:
                print(f"  !! não encontrado: {rel}:{n} «{velho}»")
        open(caminho, "w", encoding="utf-8").write("\n".join(linhas))
    print(f"{total} troca(s) aplicada(s) em {len(porarq)} arquivo(s).")


if __name__ == "__main__":
    main()
