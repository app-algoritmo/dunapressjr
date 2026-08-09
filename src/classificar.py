#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — classificação de indexação.

Decide, artigo a artigo, se entra no índice do Google. Três motivos de
exclusão, todos reversíveis (noindex, follow — o link continua passando
autoridade; só a página sai do índice).

  duplicado  mesma abertura de corpo que outro artigo. Preserva o mais
             antigo, exclui as repetições.
  curto      corpo abaixo do piso editorial.
  agencia    republicação de assessoria, órgão público ou agência de
             notícia, identificada pelo campo "Fonte:" ou por marcadores
             fortes no corpo.

Exclusão total (410 Gone) fica reservada ao que não tem corpo nenhum:
página vazia não é conteúdo fraco, é defeito.
"""
import os, re, json, glob, unicodedata, hashlib
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados")

# Categorias herdadas que eram fluxo de notícia/republicação, não reportagem
# própria. Saem do índice em bloco, por decisão editorial.
ORIGEM_NOTICIA = {"news", "headlines", "events"}

PISO_CURTO = 300          # palavras. abaixo disto, sai do índice
PISO_VAZIO = 40           # abaixo disto, não é artigo: 410

# ── Republicação: quem assina a fonte ────────────────────────────────────
FONTES_AGENCIA = re.compile(
    r"ag[êe]ncia\s+(brasil|senado|c[âa]mara|gov|nacional|petrobras|fapesp)"
    r"|gov\.br|\.gov\.|governo\s+d|minist[ée]rio|secretaria\s+d"
    r"|portal\s+de\s+imprensa|assessoria|sebrae|embrapa|fiocruz|inpe|ibge"
    r"|banco\s+central|reuters|\bafp\b|\befe\b|\bansa\b|central\s+press"
    r"|exército|for[çc]a\s+a[ée]rea|marinha|senado\s+federal|c[âa]mara\s+dos",
    re.I)

# marcadores no corpo que, sozinhos, já caracterizam republicação
CORPO_AGENCIA = re.compile(
    r"com\s+informa[çc][õo]es\s+d[aeo]"
    r"|texto\s+(publicado|reproduzido)\s+originalmente"
    r"|\(ag[êe]ncia\s+(brasil|senado|c[âa]mara)\)"
    r"|^\s*Fonte:\s*(?!Ver\s+tamb[ée]m)", re.I | re.M)


def corpo_de(caminho):
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        t = fh.read()
    if t.startswith("---"):
        f = t.find("\n---", 3)
        if f > 0:
            return t[:f + 4], t[f + 4:]
    return "", t


def normalizar(texto):
    """Reduz a uma impressão digital: sem acento, sem pontuação, sem espaço
    duplo. Duas republicações do mesmo release batem aqui."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9 ]", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def carregar_excecoes():
    """URLs que o Search Console mostrou receber tráfego real. Vencem a
    régua editorial: dado observado supera regra presumida."""
    caminho = f"{DADOS}/excecoes.txt"
    if not os.path.exists(caminho):
        return set()
    with open(caminho, encoding="utf-8") as fh:
        return {l.split("\t")[0].strip() for l in fh
                if l.strip() and not l.lstrip().startswith("#")}


def classificar():
    excecoes = carregar_excecoes()
    with open(f"{DADOS}/manifesto.json", encoding="utf-8") as fh:
        m = json.load(fh)
    artigos = m["artigos"]

    # 1ª passada: ler corpo, medir, detectar agência
    for a in artigos:
        cab, corpo = corpo_de(os.path.join(RAIZ, a["arquivo"]))
        corpo = corpo.strip()
        a["_palavras"] = len(corpo.split())
        chave = normalizar(corpo)[:500]
        a["_impressao"] = hashlib.sha1(chave.encode()).hexdigest() if len(chave) > 80 else None

        fonte = re.search(r"^\s*Fonte:\s*(.+)$", corpo, re.M)
        a["_agencia"] = bool(
            (fonte and FONTES_AGENCIA.search(fonte.group(1)))
            or CORPO_AGENCIA.search(corpo) and FONTES_AGENCIA.search(corpo[-600:] or "")
        )
        a["_fonte"] = fonte.group(1).strip()[:60] if fonte else ""

    # 2ª passada: duplicatas — o mais antigo fica, os demais saem
    grupos = defaultdict(list)
    for a in artigos:
        if a["_impressao"]:
            grupos[a["_impressao"]].append(a)
    duplicados = set()
    for imp, grupo in grupos.items():
        if len(grupo) > 1:
            grupo.sort(key=lambda x: x["data"])
            for a in grupo[1:]:
                duplicados.add(a["url"])
                a["_original"] = grupo[0]["url"]

    # 3ª passada: veredito
    contas = Counter()
    for a in artigos:
        motivos = []
        if a["_palavras"] < PISO_VAZIO:
            a["indexar"] = False
            a["situacao"] = "removido"
            a["motivos"] = ["vazio"]
            contas["removido"] += 1
            continue
        if a["url"] in duplicados:
            motivos.append("duplicado")
        if a["_palavras"] < PISO_CURTO:
            motivos.append("curto")
        if a["_agencia"]:
            motivos.append("agencia")
        if a["origem"] in ORIGEM_NOTICIA:
            motivos.append("noticia")

        if motivos and a["url"] in excecoes:
            a["indexar"] = True
            a["situacao"] = "indexado"
            a["motivos"] = []
            contas["indexado"] += 1
            contas["excecao_trafego"] += 1
            continue

        a["indexar"] = not motivos
        a["situacao"] = "indexado" if not motivos else "noindex"
        a["motivos"] = motivos
        contas[a["situacao"]] += 1
        for mo in motivos:
            contas[f"motivo:{mo}"] += 1

    # limpeza dos campos internos
    for a in artigos:
        for k in [k for k in a if k.startswith("_")]:
            if k != "_original":
                del a[k]

    with open(f"{DADOS}/manifesto.json", "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False)

    # ── relatório ────────────────────────────────────────────────────────
    total = len(artigos)
    ind = contas["indexado"]
    por_ano_ind = Counter(a["ano"] for a in artigos if a["indexar"])
    por_ano_tot = Counter(a["ano"] for a in artigos)
    por_ed = Counter(a["editoria_nome"] for a in artigos if a["indexar"])
    por_ed_tot = Counter(a["editoria_nome"] for a in artigos)

    L = []
    L.append("DUNA PRESS — CLASSIFICAÇÃO DE INDEXAÇÃO")
    L.append("=" * 62)
    L.append(f"Piso editorial: {PISO_CURTO} palavras · vazio: <{PISO_VAZIO}")
    L.append("")
    L.append(f"Acervo total ............ {total:>6}")
    L.append(f"Indexado (o jornal) ..... {ind:>6}   {ind/total*100:>5.1f}%")
    L.append(f"noindex, follow ......... {contas['noindex']:>6}   {contas['noindex']/total*100:>5.1f}%")
    L.append(f"410 Gone (vazios) ....... {contas['removido']:>6}   {contas['removido']/total*100:>5.1f}%")
    if contas["excecao_trafego"]:
        L.append(f"  dos indexados, preservados por tráfego: {contas['excecao_trafego']}")
    elif not excecoes:
        L.append("")
        L.append("  ! Sem excecoes.txt: nenhuma página foi preservada por tráfego.")
        L.append("    Rode excecoes.py com a exportação do Search Console.")
    L.append("")
    L.append("MOTIVOS DE EXCLUSÃO  (um artigo pode ter mais de um)")
    L.append("-" * 62)
    for mo in ("noticia", "agencia", "curto", "duplicado"):
        n = contas[f"motivo:{mo}"]
        L.append(f"  {mo:<12} {n:>6}   {n/total*100:>5.1f}% do acervo")
    L.append("")
    L.append("SOBREPOSIÇÃO DOS MOTIVOS")
    L.append("-" * 62)
    combos = Counter(" + ".join(a["motivos"]) for a in artigos if a["motivos"] and a["situacao"] == "noindex")
    for k, v in combos.most_common():
        L.append(f"  {k:<28} {v:>6}")
    L.append("")
    L.append("O QUE SOBRA, POR ANO")
    L.append("-" * 62)
    L.append(f"  {'ano':<6}{'indexado':>9}{'de':>8}{'':>4}{'perfil':<26}")
    for ano in sorted(por_ano_tot):
        i, t = por_ano_ind[ano], por_ano_tot[ano]
        barra = "█" * max(0, round(i / 60))
        L.append(f"  {ano:<6}{i:>9}{t:>8}    {barra}")
    L.append("")
    L.append("O QUE SOBRA, POR EDITORIA")
    L.append("-" * 62)
    for ed, t in por_ed_tot.most_common():
        i = por_ed[ed]
        L.append(f"  {ed:<20}{i:>6} de {t:<6}  {i/t*100:>5.1f}%")

    rel = "\n".join(L)
    with open(f"{DADOS}/indexacao.txt", "w", encoding="utf-8") as fh:
        fh.write(rel)

    # arquivos operacionais
    with open(f"{DADOS}/noindex.txt", "w", encoding="utf-8") as fh:
        for a in artigos:
            if a["situacao"] == "noindex":
                fh.write(f'{a["url"]}\t{",".join(a["motivos"])}\n')
    with open(f"{DADOS}/gone-410.txt", "w", encoding="utf-8") as fh:
        for a in artigos:
            if a["situacao"] == "removido":
                fh.write(f'{a["url"]}\n')
    print(rel)


if __name__ == "__main__":
    classificar()
