#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — migração do acervo para arquitetura estática.

Lê os .md em artigos/, normaliza o frontmatter (duas gerações distintas
convivem no acervo), consolida 79 categorias em 9 editorias, gera slugs
em português e produz:
  - manifesto.json   inventário completo, pronto para o gerador
  - redirects.map    mapa 1:1 das URLs antigas para as novas
  - relatorio.txt    diagnóstico editorial do acervo
"""
import os, re, json, unicodedata, sys
from collections import defaultdict, Counter
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados")

# ── Editorias ────────────────────────────────────────────────────────────
# 79 categorias herdadas viram 9 editorias. Cada linha é uma decisão
# editorial, não uma agregação automática.
EDITORIAS = {
    "brasil": {
        "nome": "Brasil",
        "descricao": "Política nacional, contas públicas, educação e o país no dia a dia.",
        "origens": ["news", "economia-brasileira", "geopolitica-brasil", "bicentennial",
                    "education", "courses-and-careers", "headlines", "events", "escola"],
    },
    "mundo": {
        "nome": "Mundo",
        "descricao": "Geopolítica, conflitos armados, diplomacia e a ordem internacional.",
        "origens": ["world-affairs", "geopolitics", "global-affairs", "international-affairs",
                    "international-politics", "international-relations", "guerra-e-conflitos",
                    "military"],
    },
    "economia": {
        "nome": "Economia",
        "descricao": "Mercados, empresas, moeda, trabalho e finanças pessoais.",
        "origens": ["business-and-economy", "global-economy", "finances", "financial-education",
                    "criptomoedas", "entrepreneurship", "shopping", "works"],
    },
    "politica": {
        "nome": "Política",
        "descricao": "Poder, instituições, regulação e o debate público.",
        "origens": ["policy", "politics-and-society", "ethics-and-society", "society-and-culture"],
    },
    "ciencia-e-saude": {
        "nome": "Ciência & Saúde",
        "descricao": "Pesquisa, medicina, clima, energia e o mundo natural.",
        "origens": ["science", "health", "covid-19", "saude-mental", "psicologia", "environment",
                    "energias-renovaveis", "agriculture", "astronomy", "space-exploration",
                    "well-being", "fitness", "arqueologia", "ufologia"],
    },
    "tecnologia": {
        "nome": "Tecnologia",
        "descricao": "Inteligência artificial, plataformas, inovação e indústria digital.",
        "origens": ["technology", "innovation", "future-and-innovation", "inteligencia-artificial",
                    "social-networks", "e-auto"],
    },
    "cultura": {
        "nome": "Cultura",
        "descricao": "História, ideias, literatura, gastronomia, viagem e modos de viver.",
        "origens": ["culture-and-history", "history", "history-and-philosophy", "philosophy",
                    "literature", "books", "music", "architecture-and-art", "religiosity",
                    "fashion", "beauty", "food", "gastronomia", "tourism-and-gastronomy",
                    "lifestyle", "pets", "story", "documentaries", "magazine", "features",
                    "video-library", "personal-development", "motivational"],
    },
    "esportes": {
        "nome": "Esportes",
        "descricao": "Futebol, automobilismo, olimpismo e a economia do esporte.",
        "origens": ["sports", "soccer", "formula-1", "tennis", "cycling", "olympic-games",
                    "pan-american-games"],
    },
    "opiniao": {
        "nome": "Opinião",
        "descricao": "Editoriais, colunas e crônicas assinadas.",
        "origens": ["opinion", "editorial", "chronicle"],
    },
}

DE_PARA = {}
for slug, ed in EDITORIAS.items():
    for origem in ed["origens"]:
        DE_PARA[origem] = slug
    # As matérias novas já nascem na pasta da editoria final. Sem isto, tudo
    # que publicarmos de hoje em diante cai em "sem mapeamento".
    DE_PARA[slug] = slug

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def slugificar(texto, limite=72):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^\w\s-]", "", t.lower())
    t = re.sub(r"[\s_-]+", "-", t).strip("-")
    if len(t) > limite:
        corte = t[:limite].rsplit("-", 1)[0]
        t = corte or t[:limite]
    return t.strip("-")


def ler_frontmatter(bruto):
    """Parser tolerante. O acervo tem YAML de duas gerações, com aspas
    inconsistentes e listas em dois estilos. Nada de dependência externa."""
    if not bruto.startswith("---"):
        return {}, bruto
    fim = bruto.find("\n---", 3)
    if fim == -1:
        return {}, bruto
    cabeca, corpo = bruto[3:fim], bruto[fim + 4:]
    meta, chave_lista = {}, None
    for linha in cabeca.split("\n"):
        if not linha.strip():
            continue
        item = re.match(r"^\s*-\s+(.*)$", linha)
        if item and chave_lista:
            meta.setdefault(chave_lista, []).append(item.group(1).strip().strip("\"'"))
            continue
        par = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", linha)
        if par:
            chave, valor = par.group(1), par.group(2).strip()
            if valor == "":
                chave_lista = chave
                meta.setdefault(chave, [])
            else:
                chave_lista = None
                meta[chave] = valor.strip("\"'")
    return meta, corpo.lstrip("\n")


def primeiro_paragrafo(corpo):
    for bloco in corpo.split("\n\n"):
        b = bloco.strip()
        if not b or b.startswith(("#", "!", ">", "|", "---")):
            continue
        b = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", b)
        b = re.sub(r"[*_`]", "", b).replace("\n", " ")
        return re.sub(r"\s+", " ", b).strip()
    return ""


def data_extenso(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def processar():
    artigos, redirects = [], []
    origens_vistas, sem_mapa = Counter(), Counter()
    caminho_base = os.path.join(RAIZ, "artigos")

    for cat_dir in sorted(os.listdir(caminho_base)):
        pasta = os.path.join(caminho_base, cat_dir)
        if not os.path.isdir(pasta):
            continue
        for nome in sorted(os.listdir(pasta)):
            if not nome.endswith(".md"):
                continue
            caminho = os.path.join(pasta, nome)
            with open(caminho, encoding="utf-8", errors="replace") as fh:
                bruto = fh.read()
            meta, corpo = ler_frontmatter(bruto)
            if meta.get("status", "publish") != "publish":
                continue

            titulo = (meta.get("title") or "").strip()
            if not titulo:
                continue

            m = re.match(r"^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", nome)
            if m:
                ano, mes, dia, resto = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
            else:
                continue
            try:
                quando = date(ano, mes, dia)
            except ValueError:
                continue

            origens_vistas[cat_dir] += 1
            editoria = DE_PARA.get(cat_dir)
            if not editoria:
                sem_mapa[cat_dir] += 1
                editoria = "brasil"

            slug = slugificar(titulo) or slugificar(resto)
            # Permalink herdado do WordPress. A URL não carrega editoria:
            # assim a taxonomia pode ser reorganizada para sempre sem
            # quebrar um único endereço — e os backlinks antigos voltam a
            # funcionar sozinhos, sem redirecionamento.
            url_nova = f"/{ano}/{mes:02d}/{dia:02d}/{slug}/"
            url_antiga = f"/artigo.html?file=/artigos/{cat_dir}/{nome}"
            # slug do WordPress: o nome do arquivo foi truncado na conversão,
            # então guardamos o prefixo para casamento por início de string
            slug_wp = resto

            palavras = len(corpo.split())
            olho = (meta.get("description") or meta.get("subtitle") or "").strip()
            if not olho:
                olho = primeiro_paragrafo(corpo)[:240]

            tags = meta.get("tags") or []
            if isinstance(tags, str):
                tags = [tags]

            artigos.append({
                "titulo": titulo,
                "subtitulo": (meta.get("subtitle") or "").strip(),
                "olho": olho,
                "autor": (meta.get("author") or "Redação Duna Press").strip(),
                "autor_slug": slugificar(meta.get("author") or "Redacao Duna Press"),
                "data": quando.isoformat(),
                "data_extenso": data_extenso(quando),
                "ano": ano,
                "editoria": editoria,
                "editoria_nome": EDITORIAS[editoria]["nome"],
                "origem": cat_dir,
                "slug": slug,
                "url": url_nova,
                "imagem": (meta.get("featuredImage") or "").strip(),
                "credito_foto": (meta.get("photoAuthor") or "").strip(),
                "fonte_foto": (meta.get("photoSource") or "").strip(),
                "tags": [t for t in tags if t][:8],
                "palavras": palavras,
                "porte": "longa" if palavras >= 800 else "media" if palavras >= 300 else "curta",
                "arquivo": os.path.relpath(caminho, RAIZ),
                # Proveniência declarada. Confirmado com a redação: todo o
                # acervo anterior a 2025 é de autoria humana.
                "proveniencia": (meta.get("proveniencia")
                                 or ("humano" if ano < 2025 else "ia-assistido")),
                "revisor": (meta.get("revisor") or "").strip(),
                "fonte_primaria": (meta.get("fonte_primaria") or "").strip(),
                "fonte_nome": (meta.get("fonte_nome") or "").strip(),
                "wp": f"{ano:04d}/{mes:02d}/{dia:02d}",
                "wp_slug": slug_wp,
            })
            redirects.append((url_antiga, url_nova))

    # colisões de slug dentro da mesma editoria/mês
    vistos, colisoes = set(), 0
    for a in artigos:
        chave = a["url"]
        if chave in vistos:
            colisoes += 1
            a["slug"] = f"{a['slug']}-2"
            a["url"] = f"/{a['ano']}/{a['data'][5:7]}/{a['data'][8:10]}/{a['slug']}/"
        vistos.add(a["url"])

    artigos.sort(key=lambda a: a["data"], reverse=True)
    os.makedirs(SAIDA, exist_ok=True)

    with open(f"{SAIDA}/manifesto.json", "w", encoding="utf-8") as fh:
        json.dump({"editorias": EDITORIAS, "artigos": artigos}, fh, ensure_ascii=False)

    with open(f"{SAIDA}/redirects.map", "w", encoding="utf-8") as fh:
        for antiga, nova in redirects:
            fh.write(f"{antiga} {nova} 301\n")

    # Índice para as URLs da era WordPress (/ano/mes/dia/slug/). O slug do
    # arquivo .md está truncado, então o casamento é por prefixo: agrupamos
    # por data e o edge escolhe o slug que começa igual.
    wp = {}
    for a in artigos:
        wp.setdefault(a["wp"], []).append([a["wp_slug"], a["url"]])
    with open(f"{SAIDA}/wp-legado.json", "w", encoding="utf-8") as fh:
        json.dump(wp, fh, ensure_ascii=False, separators=(",", ":"))

    # Redirects das categorias antigas para as 9 editorias
    with open(f"{SAIDA}/redirects-categoria.map", "w", encoding="utf-8") as fh:
        for origem, destino in sorted(DE_PARA.items()):
            fh.write(f"/categoria.html?cat={origem} /{destino}/ 301\n")

    por_editoria = Counter(a["editoria"] for a in artigos)
    por_porte = Counter(a["porte"] for a in artigos)
    por_ano = Counter(a["ano"] for a in artigos)

    linhas = ["DUNA PRESS — DIAGNÓSTICO DO ACERVO", "=" * 52, "",
              f"Artigos publicados ........ {len(artigos):,}".replace(",", "."),
              f"Redirects 301 gerados ..... {len(redirects):,}".replace(",", "."),
              f"Colisões de slug ajustadas  {colisoes}",
              f"Categorias de origem ...... {len(origens_vistas)} → 9 editorias", "",
              "POR EDITORIA", "-" * 52]
    for slug, ed in EDITORIAS.items():
        linhas.append(f"{ed['nome']:<18} {por_editoria[slug]:>6}   ({len(ed['origens'])} categorias absorvidas)")
    linhas += ["", "POR PORTE", "-" * 52,
               f"Longa (800+ palavras)   {por_porte['longa']:>6}",
               f"Média (300–799)         {por_porte['media']:>6}",
               f"Curta (<300)            {por_porte['curta']:>6}   ← candidatos a arquivo",
               "", "POR ANO", "-" * 52]
    for ano in sorted(por_ano):
        barra = "█" * max(1, round(por_ano[ano] / 120))
        linhas.append(f"{ano}  {por_ano[ano]:>5}  {barra}")
    if sem_mapa:
        linhas += ["", "SEM MAPEAMENTO EXPLÍCITO", "-" * 52]
        linhas += [f"{c:<28} {n}" for c, n in sem_mapa.most_common()]

    relatorio = "\n".join(linhas)
    with open(f"{SAIDA}/relatorio.txt", "w", encoding="utf-8") as fh:
        fh.write(relatorio)
    print(relatorio)


if __name__ == "__main__":
    processar()
