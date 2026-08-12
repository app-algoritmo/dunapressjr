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

# Slugs canônicos extraídos do export do WordPress. São eles que o Google
# indexou: 883 das 932 URLs com tráfego real batem com esta tabela.
# Os nomes de arquivo .md foram truncados na conversão original, então
# reconstruí-los a partir do título produziria URLs que ninguém acessa.
CANONICO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "dados", "wp-canonico.json")


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


# Slugs que o WordPress cria sozinho e não devem virar endereço público.
LIXO = re.compile(r"__trashed|^auto-draft|^rascunho-automatico|^untitled", re.I)


def util(slug):
    return bool(slug) and not LIXO.search(slug) and len(slug) > 2


def indice_canonico():
    """Devolve dois índices do WXR: por data e por título normalizado.
    O casamento tenta a data primeiro, que é mais confiável; o título é
    o recurso para quando o slug do arquivo divergiu demais."""
    if not os.path.exists(CANONICO):
        print("AVISO: dados/wp-canonico.json ausente — os slugs serão\n"
              "       derivados do título, e URLs antigas podem quebrar.")
        return {}, {}
    with open(CANONICO, encoding="utf-8") as fh:
        wp = json.load(fh)
    por_data, por_titulo = {}, {}
    for p in wp.values():
        if not util(p.get("slug", "")):
            continue
        por_data.setdefault(p["data"], []).append(p)
        if p.get("titulo"):
            por_titulo.setdefault(chave_titulo(p["titulo"]), p)
    return por_data, por_titulo


def chave_titulo(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def processar():
    por_data, por_titulo = indice_canonico()
    artigos, redirects = [], []
    origem_slug = Counter()
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

            # 1º o slug canônico do WordPress; só depois o derivado do título
            canon = None
            for c in por_data.get(quando.isoformat(), []):
                if not util(c["slug"]):
                    continue
                if (c["slug"].startswith(resto[:45])
                        or resto.startswith(c["slug"][:45])):
                    canon = c["slug"]
                    origem_slug["wordpress: data+slug"] += 1
                    break
            if not canon:
                c = por_titulo.get(chave_titulo(titulo))
                if c and util(c["slug"]):
                    canon = c["slug"]
                    origem_slug["wordpress: título"] += 1
            if not canon:
                origem_slug["derivado do título"] += 1

            slug = canon or slugificar(titulo) or slugificar(resto)
            # Permalink plano, como no WordPress. O Search Console mostra
            # que 923 das 1.000 páginas com tráfego usam /slug/ sem data —
            # apenas uma usa /AAAA/MM/DD/. Com este formato as URLs
            # indexadas voltam a funcionar sem redirecionamento algum.
            url_nova = f"/{slug}/"
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
                # Marcado pelo editor: sai da capa e do índice, fica no
                # acervo. O nome evita colidir com "arquivo", que aqui já
                # significa o caminho do ficheiro.
                "fora_da_capa": str(meta.get("fora_da_capa", meta.get("arquivo_editorial", ""))).lower()
                                in ("true", "sim", "1"),
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

    # Nomes reservados. Com permalink plano, um artigo cujo slug seja
    # "economia" ou "autores" disputa o endereço com a página de seção — e
    # como o artigo é escrito depois, ele vence e a seção desaparece. Foi
    # o que apagou /economia/ do jornal.
    RESERVADOS = set(EDITORIAS) | {
        "autores", "arquivo", "busca", "principios", "correcoes",
        "quem-somos", "contato", "privacidade", "cookies", "termos",
        "newsletter", "assinatura", "api", "assets", "sitemap", "rss",
        "index", "404", "artigo", "categoria", "feed", "tag", "tags",
    }

    # Colisões. Sem data na URL, dois textos homônimos disputam o mesmo
    # endereço. Fica com ele o mais antigo — que é o que o Google indexou;
    # os demais recebem sufixo de ano.
    artigos.sort(key=lambda a: a["data"])
    vistos, colisoes, reservados = set(), 0, 0
    for a in artigos:
        if a["slug"] in RESERVADOS:
            reservados += 1
            a["slug"] = "%s-%s" % (a["slug"], a["ano"])
            a["url"] = "/%s/" % a["slug"]
        if a["url"] in vistos:
            colisoes += 1
            a["slug"] = "%s-%s" % (a["slug"], a["ano"])
            a["url"] = "/%s/" % a["slug"]
            n = 2
            while a["url"] in vistos:
                a["slug"] = "%s-%d" % (a["slug"], n)
                a["url"] = "/%s/" % a["slug"]
                n += 1
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
              f"Slugs reservados desviados  {reservados}"
              + ("   ← disputavam endereço de seção" if reservados else ""),
              f"Categorias de origem ...... {len(origens_vistas)} → 9 editorias", "",
              "POR EDITORIA", "-" * 52]
    for slug, ed in EDITORIAS.items():
        linhas.append(f"{ed['nome']:<18} {por_editoria[slug]:>6}   ({len(ed['origens'])} categorias absorvidas)")
    linhas += ["", "ORIGEM DO SLUG", "-" * 52]
    for k, v in origem_slug.most_common():
        linhas.append("%-28s %6d   %4.1f%%" % (k, v, v / len(artigos) * 100))
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
