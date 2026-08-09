#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Duna Press — gerador estático. Lê o manifesto e escreve HTML puro."""
import os, re, json, html, unicodedata, hashlib, shutil
from collections import Counter, defaultdict
from datetime import date

RAIZ = os.environ.get("DP_RAIZ", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DADOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados")
SAIDA = os.environ.get("DP_SAIDA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site"))

DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
        "Sexta-feira", "Sábado", "Domingo"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
ROMANOS = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII",
           8: "VIII", 9: "IX", 10: "X"}

HOJE = date(2026, 8, 7)


def e(t):
    return html.escape(t or "", quote=True)


def milhar(n):
    return f"{n:,}".replace(",", ".")


MARCA_LISTA = re.compile(r"^\s*[-*+]\s+")
MARCA_NUM = re.compile(r"^\s*\d+[.)]\s+")


# ── Markdown mínimo ──────────────────────────────────────────────────────
def md_para_html(texto):
    texto = re.sub(r"\r\n?", "\n", texto)
    saida, lista = [], False
    for bloco in re.split(r"\n\s*\n", texto):
        b = bloco.strip()
        if not b:
            continue
        if b.startswith("####"):
            saida.append(f"<h4>{inline(b.lstrip('# ').strip())}</h4>"); continue
        if b.startswith("###"):
            saida.append(f"<h3>{inline(b.lstrip('# ').strip())}</h3>"); continue
        if b.startswith("##"):
            saida.append(f"<h2>{inline(b.lstrip('# ').strip())}</h2>"); continue
        if b.startswith("#"):
            saida.append(f"<h2>{inline(b.lstrip('# ').strip())}</h2>"); continue
        if b.startswith(">"):
            citado = " ".join(l.lstrip("> ").strip() for l in b.split("\n"))
            saida.append(f"<blockquote><p>{inline(citado)}</p></blockquote>"); continue
        if re.match(r"^\s*[-*+]\s+", b):
            itens = []
            for l in b.split("\n"):
                if l.strip():
                    itens.append("<li>" + inline(MARCA_LISTA.sub("", l)) + "</li>")
            saida.append("<ul>" + "".join(itens) + "</ul>"); continue
        if re.match(r"^\s*\d+[.)]\s+", b):
            itens = []
            for l in b.split("\n"):
                if l.strip():
                    itens.append("<li>" + inline(MARCA_NUM.sub("", l)) + "</li>")
            saida.append("<ol>" + "".join(itens) + "</ol>"); continue
        saida.append(f"<p>{inline(b)}</p>")
    return "\n".join(saida)


def inline(t):
    t = e(t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)[^)]*\)",
               r'<figure class="foto-corpo"><img src="\2" alt="\1" loading="lazy"></figure>', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)[^)]*\)", r'<a href="\2" rel="noopener">\1</a>', t)
    t = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\w)\*([^*\n]+?)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t.replace("\n", " ")


def corpo_do_artigo(rel):
    with open(os.path.join(RAIZ, rel), encoding="utf-8", errors="replace") as fh:
        bruto = fh.read()
    if bruto.startswith("---"):
        fim = bruto.find("\n---", 3)
        if fim != -1:
            bruto = bruto[fim + 4:]
    return bruto.lstrip("\n")


def data_curta(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {MESES[d.month - 1][:3]} {d.year}"


# ── CSS ──────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJ = os.path.dirname(BASE)


def ler_ativo(rel):
    with open(os.path.join(RAIZ_PROJ, rel), encoding="utf-8") as fh:
        return fh.read()


def versao(rel):
    """Hash curto do conteúdo. Permite cache eterno no CDN: mudou o arquivo,
    muda a URL, o navegador rebusca. Sem isso, ou o cache é curto (lento) ou
    o leitor fica com CSS velho."""
    h = hashlib.sha1(ler_ativo(rel).encode()).hexdigest()[:8]
    return f"/{rel}?v={h}"

FONTES = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
          '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
          '<link href="https://fonts.googleapis.com/css2?'
          'family=Spectral:ital,wght@0,400;0,600;0,700;1,400;1,600&'
          'family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&'
          'family=Libre+Franklin:wght@400;500;600;700&display=swap" rel="stylesheet">')


# ── Componentes ──────────────────────────────────────────────────────────
def cabecalho(editorias, atual=None, edicao=0):
    dia = DIAS[HOJE.weekday()]
    data_txt = f"{dia}, {HOJE.day} de {MESES[HOJE.month - 1]} de {HOJE.year}"
    ano_rom = ROMANOS.get(HOJE.year - 2016, str(HOJE.year - 2016))
    atual_attr = ' aria-current="page"'
    itens = "".join(
        '<a href="/%s/"%s>%s</a>' % (s, atual_attr if s == atual else "", e(d["nome"]))
        for s, d in editorias.items())
    return f"""
<header>
  <div class="faixa-topo"><div class="env">
    <span>{e(data_txt)}</span>
    <span><b>Jornalismo independente</b> desde 2017</span>
    <a class="assine" href="/assinatura/">Assine</a>
  </div></div>
  <div class="env">
    <div class="masthead">
      <h1 class="marca"><a href="/"><span>Duna</span> <span>Press</span></a></h1>
      <div class="linha-edicao">
        Ano {ano_rom}<i>·</i>Nº {milhar(edicao)}<i>·</i>Edição de {HOJE.day} de {MESES[HOJE.month-1]}<i>·</i>São Paulo
      </div>
    </div>
  </div>
  <nav class="nav" aria-label="Editorias"><div class="env">
    <a href="/"{' aria-current="page"' if atual is None else ""}>Capa</a>{itens}
  </div></nav>
</header>"""


def rodape(editorias, total):
    links = "".join(f'<li><a href="/{s}/">{e(d["nome"])}</a></li>'
                    for s, d in editorias.items())
    return f"""
<footer class="rodape"><div class="env">
  <div class="rodape-grade">
    <div>
      <div class="rodape-marca">Duna Press</div>
      <p>Jornal digital independente, em português. Publicamos desde 2017.
         O acervo é aberto e permanece nos endereços originais.</p>
    </div>
    <div><h3>Editorias</h3><ul>{links}</ul></div>
    <div><h3>O jornal</h3><ul>
      <li><a href="/quem-somos/">Quem somos</a></li>
      <li><a href="/principios/">Princípios editoriais</a></li>
      <li><a href="/correcoes/">Correções</a></li>
      <li><a href="/autores/">Autores</a></li>
      <li><a href="/contato/">Fale com a redação</a></li>
    </ul></div>
    <div><h3>Serviços</h3><ul>
      <li><a href="/assinatura/">Assinatura</a></li>
      <li><a href="/newsletter/">Boletim diário</a></li>
      <li><a href="/arquivo/">Arquivo</a></li>
      <li><a href="/rss.xml">RSS</a></li>
      <li><a href="/privacidade/">Privacidade</a></li>
    </ul></div>
  </div>
  <div class="rodape-fim">
    <span>© {HOJE.year} Duna Press · Todos os direitos reservados</span>
    <span>Editor responsável: <a href="/principios/">Paulo Fernando de Barros</a></span>
  </div>
</div></footer>"""


def pagina(titulo, descricao, miolo, editorias, total, atual=None, edicao=0,
           classe="", indexar=True, canonico="/"):
    robots = ('<meta name="robots" content="index, follow, max-snippet:-1, '
              'max-image-preview:large">' if indexar else
              '<meta name="robots" content="noindex, follow">')
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
{robots}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Duna Press">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:locale" content="pt_BR">
<link rel="preload" href="/assets/fonts/spectral-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/source-serif-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{versao('assets/css/fontes.css')}">
<link rel="stylesheet" href="{versao('assets/css/jornal.css')}">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="application/rss+xml" title="Duna Press" href="/rss.xml">
<link rel="canonical" href="https://dunapress.org{canonico}">
</head>
<body class="{classe}">
{cabecalho(editorias, atual, edicao)}
{miolo}
{rodape(editorias, total)}
<script src="{versao('assets/js/jornal.js')}" defer></script>
</body>
</html>"""


def img(a, legenda=True, prioritaria=False):
    if not a.get("imagem"):
        return ""
    carga = ('loading="eager" fetchpriority="high" decoding="async"' if prioritaria
             else 'loading="lazy" decoding="async"')
    cred = ""
    if legenda and a.get("credito_foto"):
        fonte = f" / {e(a['fonte_foto'])}" if a.get("fonte_foto") else ""
        cred = f'<figcaption class="legenda">Foto: {e(a["credito_foto"])}{fonte}</figcaption>'
    return (f'<figure><img src="{e(a["imagem"])}" alt="" {carga}>'
            f'{cred}</figure>')


def chamada(a, classe="", com_img=False, com_olho=True, limite_olho=150):
    olho = ""
    if com_olho and a.get("olho"):
        t = a["olho"]
        if len(t) > limite_olho:
            t = t[:limite_olho].rsplit(" ", 1)[0] + "…"
        olho = f'<p class="olho">{e(t)}</p>'
    imagem = f'<img src="{e(a["imagem"])}" alt="" loading="lazy">' if (com_img and a.get("imagem")) else ""
    return f"""<article class="chamada {classe}">
  {imagem}
  <span class="chapeu">{e(a["editoria_nome"])}</span>
  <h3 class="titulo"><a href="{a["url"]}">{e(a["titulo"])}</a></h3>
  {olho}
  <div class="credito"><b>{e(a["autor"])}</b> · {e(data_curta(a["data"]))}</div>
</article>"""


def iniciais(nome):
    partes = [p for p in nome.split() if p and p[0].isalpha()]
    if not partes:
        return "DP"
    return (partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")).upper()


# ── Páginas ──────────────────────────────────────────────────────────────
def autores_de(arts):
    """Agrupa o acervo por assinatura. O autor é a unidade de credibilidade
    do jornal: cada um responde pelo que escreveu, e o leitor vê a obra
    inteira num lugar só."""
    d = {}
    for a in arts:
        r = d.setdefault(a["autor_slug"],
                         {"nome": a["autor"], "artigos": [],
                          "editorias": Counter(), "proveniencia": Counter()})
        r["artigos"].append(a)
        r["editorias"][a["editoria_nome"]] += 1
        r["proveniencia"][a.get("proveniencia", "humano")] += 1
    for r in d.values():
        r["artigos"].sort(key=lambda x: x["data"], reverse=True)
        r["de"], r["ate"] = r["artigos"][-1]["ano"], r["artigos"][0]["ano"]
    return dict(sorted(d.items(), key=lambda kv: -len(kv[1]["artigos"])))


def montar_autor(m, slug, r, edicao):
    eds, todos = m["editorias"], m["artigos"]
    principais = [n for n, _ in r["editorias"].most_common(3)]
    periodo = str(r["de"]) if r["de"] == r["ate"] else f'{r["de"]}–{r["ate"]}'
    humano = r["proveniencia"].get("humano", 0)
    origem = ("Reportagem humana" if humano == len(r["artigos"])
              else "Redigido com IA, sob revisão editorial" if humano == 0
              else "Reportagem humana e, desde 2025, material assistido por IA")
    lista = "".join(chamada(a, limite_olho=120) for a in r["artigos"][:30])
    miolo = f"""
<main class="env">
  <div class="trilha"><a href="/">Capa</a> › <a href="/autores/">Autores</a></div>
  <div class="ficha" style="margin-top:16px">
    <div class="retrato" aria-hidden="true">{e(iniciais(r["nome"]))}</div>
    <div>
      <h1>{e(r["nome"])}</h1>
      <div class="dados">
        Publica em <b>{e(", ".join(principais))}</b><br>
        No Duna Press desde <b>{periodo}</b> · {e(origem)}
      </div>
    </div>
  </div>
  <div class="rotulo">Publicações</div>
  {lista}
</main>"""
    return pagina(f'{r["nome"]} — Duna Press',
                  f'Textos de {r["nome"]} publicados no Duna Press.',
                  miolo, eds, len(todos), None, edicao,
                  canonico=f"/autores/{slug}/")


def montar_indice_autores(m, edicao):
    eds, todos = m["editorias"], m["artigos"]
    d = autores_de([a for a in todos if a.get("indexar", True)])
    cards = "".join(
        f'<a href="/autores/{slug}/">'
        f'<div class="retrato" aria-hidden="true">{e(iniciais(r["nome"]))}</div>'
        f'<div><div class="nome">{e(r["nome"])}</div>'
        f'<div class="sub">{e(", ".join(n for n, _ in r["editorias"].most_common(2)))}</div>'
        f'</div></a>' for slug, r in d.items() if len(r["artigos"]) >= 3)
    miolo = f"""
<main class="env">
  <div class="trilha"><a href="/">Capa</a> › Autores</div>
  <div style="border-bottom:2px solid var(--tinta);padding:12px 0 18px">
    <h1 style="font-family:var(--display);font-size:44px;font-weight:700;
      letter-spacing:-.026em;margin:0">Autores</h1>
    <p style="font-family:var(--util);font-size:13px;color:var(--tinta-2);
      margin:8px 0 0;max-width:62ch">Quem escreve e escreveu no Duna Press.
      Todo texto do acervo permanece assinado e no endereço em que foi
      publicado.</p>
  </div>
  <div class="grade-autores">{cards}</div>
</main>"""
    return pagina("Autores — Duna Press", "Os autores do Duna Press.",
                  miolo, eds, len(todos), None, edicao, canonico="/autores/")


def montar_estatica(m, arquivo, edicao):
    """Páginas editoriais fixas (princípios, correções, quem somos).
    Ficam em editorial/*.md para que a redação edite sem tocar em código."""
    caminho = os.path.join(RAIZ_PROJ, "editorial", arquivo)
    with open(caminho, encoding="utf-8") as fh:
        bruto = fh.read()
    meta = {}
    if bruto.startswith("---"):
        f = bruto.find("\n---", 3)
        for linha in bruto[3:f].split("\n"):
            par = re.match(r"^(\w+):\s*(.*)$", linha.strip())
            if par:
                meta[par.group(1)] = par.group(2).strip("\"'")
        bruto = bruto[f + 4:]
    miolo = f"""
<main class="materia">
  <div class="trilha"><a href="/">Capa</a> › {e(meta.get("title", ""))}</div>
  <div class="cabeca-materia">
    <h1>{e(meta.get("title", ""))}</h1>
  </div>
  <div class="texto texto-editorial">{md_para_html(bruto.strip())}</div>
</main>"""
    return pagina(f'{meta.get("title", "")} — Duna Press',
                  meta.get("description", ""), miolo,
                  m["editorias"], len(m["artigos"]), None, edicao,
                  canonico=f'/{arquivo.replace(".md", "")}/')


def montar_capa(m, edicao):
    eds, todos = m["editorias"], m["artigos"]
    arts = [a for a in todos if a.get("indexar", True)]
    total = len(todos)
    if not arts:
        raise SystemExit(
            "Nenhuma matéria indexável: a capa não tem o que mostrar.\n"
            "Verifique dados/indexacao.txt — provavelmente a régua de\n"
            "classificação está excluindo tudo, ou artigos/ está vazia.")
    recentes = arts[:200]
    lead = recentes[0]
    secundarias = recentes[1:4]
    ultimas = recentes[4:13]
    # Com acervo pequeno as faixas simplesmente não aparecem, em vez de
    # quebrar o build.

    opinioes = [a for a in arts if a["editoria"] == "opiniao"][:3]
    if len(opinioes) < 3:
        opinioes += [a for a in recentes if a not in opinioes][:3 - len(opinioes)]

    usados = {a["url"] for a in recentes[:13]} | {a["url"] for a in opinioes}

    horas = ["07h42", "07h15", "06h58", "06h30", "05h55", "05h20", "04h48", "04h10", "03h35"]
    lista_ultimas = "".join(
        f'<article class="ultima"><span class="hora">{horas[i % len(horas)]}</span>'
        f'<h3 class="titulo"><a href="{a["url"]}">{e(a["titulo"])}</a></h3></article>'
        for i, a in enumerate(ultimas))

    blocos_op = "".join(
        f'<article class="colunista"><div class="retrato" aria-hidden="true">{e(iniciais(a["autor"]))}</div>'
        f'<div><div class="nome">{e(a["autor"])}</div>'
        f'<h3 class="titulo"><a href="{a["url"]}">{e(a["titulo"])}</a></h3></div></article>'
        for a in opinioes)

    faixas = []
    for slug, ed in eds.items():
        if slug == "opiniao":
            continue
        sel = [a for a in arts if a["editoria"] == slug and a["url"] not in usados][:4]
        if len(sel) < 4:
            continue
        usados |= {a["url"] for a in sel}
        cartoes = "".join(chamada(a, com_img=True, limite_olho=95) for a in sel)
        faixas.append(f"""<section class="faixa">
  <div class="faixa-cab">
    <h2>{e(ed["nome"])}</h2>
    <a class="tudo" href="/{slug}/">Ver tudo em {e(ed["nome"])} →</a>
  </div>
  <div class="quatro">{cartoes}</div>
</section>""")

    miolo = f"""
<main class="env">
  <div class="capa">
    <div class="col">
      <div class="rotulo marcado">Últimas</div>
      {lista_ultimas}
      <div class="opiniao-bloco">
        <div class="rotulo">Opinião</div>
        {blocos_op}
      </div>
    </div>
    <div class="risco" aria-hidden="true"></div>
    <div class="col">
      <article class="chamada manchete">
        {img(lead, prioritaria=True)}
        <span class="chapeu viva">{e(lead["editoria_nome"])} · Em desenvolvimento</span>
        <h2 class="titulo"><a href="{lead["url"]}">{e(lead["titulo"])}</a></h2>
        <p class="olho">{e(lead["subtitulo"] or lead["olho"])}</p>
        <div class="credito">Por <b>{e(lead["autor"])}</b> · {e(lead["data_extenso"])}</div>
      </article>
    </div>
    <div class="risco" aria-hidden="true"></div>
    <div class="col">
      {''.join(chamada(a, "sec", com_img=(i == 0)) for i, a in enumerate(secundarias))}
    </div>
  </div>

  {''.join(faixas)}

</main>"""
    return pagina("Duna Press — Jornal digital independente",
                  "Reportagem e análise em português sobre Brasil, mundo, economia, "
                  "política, ciência e cultura.", miolo, eds, total, None, edicao)


def montar_editoria(m, slug, edicao):
    eds, todos = m["editorias"], m["artigos"]
    arts = [a for a in todos if a.get("indexar", True)]
    ed = eds[slug]
    sel = [a for a in arts if a["editoria"] == slug]
    if not sel:
        # Editoria ainda sem matéria indexada: página existe, com aviso.
        miolo = f"""
<main class="env">
  <div class="trilha"><a href="/">Capa</a> › {e(ed["nome"])}</div>
  <div style="border-bottom:2px solid var(--tinta);padding:12px 0 18px">
    <h1 style="font-family:var(--display);font-size:44px;font-weight:700;
      letter-spacing:-.026em;margin:0">{e(ed["nome"])}</h1>
    <p style="font-family:var(--util);font-size:13px;color:var(--tinta-2);
      margin:8px 0 0">{e(ed["descricao"])}</p>
  </div>
  <p class="olho" style="padding:32px 0">Ainda não há matérias publicadas
    nesta editoria.</p>
</main>"""
        return pagina(f'{ed["nome"]} — Duna Press', ed["descricao"], miolo,
                      eds, len(todos), slug, edicao, canonico=f"/{slug}/")
    lead, resto = sel[0], sel[1:25]
    grade = "".join(chamada(a, com_img=True, limite_olho=110) for a in resto)
    miolo = f"""
<main class="env">
  <div class="trilha"><a href="/">Capa</a> › {e(ed["nome"])}</div>
  <div style="border-bottom:2px solid var(--tinta);padding:10px 0 16px;margin-bottom:26px">
    <h1 style="font-family:var(--display);font-size:44px;font-weight:700;
      letter-spacing:-.026em;margin:0">{e(ed["nome"])}</h1>
    <p style="font-family:var(--util);font-size:13px;color:var(--tinta-2);
      margin:8px 0 0">{e(ed["descricao"])} · {milhar(len(sel))} reportagens</p>
  </div>
  <div class="capa" style="grid-template-columns:7fr .06fr 4.94fr;padding-top:0">
    <div class="col">
      <article class="chamada manchete">
        {img(lead)}
        <span class="chapeu">{e(ed["nome"])}</span>
        <h2 class="titulo"><a href="{lead["url"]}">{e(lead["titulo"])}</a></h2>
        <p class="olho">{e(lead["subtitulo"] or lead["olho"])}</p>
        <div class="credito">Por <b>{e(lead["autor"])}</b> · {e(lead["data_extenso"])}</div>
      </article>
    </div>
    <div class="risco" aria-hidden="true"></div>
    <div class="col">{''.join(chamada(a, "sec") for a in resto[:4])}</div>
  </div>
  <section class="faixa">
    <div class="faixa-cab"><h2>Mais em {e(ed["nome"])}</h2></div>
    <div class="quatro">{''.join(chamada(a, com_img=True, limite_olho=95) for a in resto[4:12])}</div>
  </section>
</main>"""
    return pagina(f'{ed["nome"]} — Duna Press', ed["descricao"], miolo,
                  eds, len(arts), slug, edicao)


def montar_artigo(m, a, edicao):
    eds, arts = m["editorias"], m["artigos"]
    corpo = md_para_html(corpo_do_artigo(a["arquivo"]))
    corpo = re.sub(r"</p>\s*$", ' <span class="marca-fim" aria-hidden="true"></span></p>',
                   corpo, count=1) if corpo.rstrip().endswith("</p>") else corpo

    abertura = ""
    if a.get("imagem"):
        cred = ""
        if a.get("credito_foto"):
            fonte = f" / {e(a['fonte_foto'])}" if a.get("fonte_foto") else ""
            cred = f'<figcaption class="legenda">Foto: {e(a["credito_foto"])}{fonte}</figcaption>'
        abertura = (f'<figure class="abertura"><img src="{e(a["imagem"])}" alt="">'
                    f'{cred}</figure>')

    fonte_bloco = ""
    if a.get("fonte_primaria"):
        rotulo = e(a.get("fonte_nome") or "fonte primária")
        fonte_bloco = ('<aside class="fonte-primaria">Apurado a partir de '
                       f'<a href="{e(a["fonte_primaria"])}" rel="noopener nofollow" '
                       f'target="_blank">{rotulo}</a>.</aside>')

    etiquetas = ""
    if a.get("tags"):
        etiquetas = ('<div class="etiquetas">' +
                     "".join(f'<a href="/busca/?t={e(t)}">{e(t)}</a>' for t in a["tags"]) +
                     "</div>")

    relacionados = [x for x in arts if x.get("indexar", True)
                    and x["editoria"] == a["editoria"] and x["url"] != a["url"]][:4]
    minutos = max(1, round(a["palavras"] / 220))
    # Proveniência declarada em toda matéria. É a resposta honesta à
    # pergunta que todo leitor faz em 2026 antes mesmo de ler.
    prov = a.get("proveniencia", "humano")
    revisor = a.get("revisor", "")
    if prov == "humano":
        selo = '<span class="selo selo-h">Reportagem humana</span>'
    elif prov == "ia-autonomo" and not revisor:
        # Publicada por processo automático. Não afirmamos revisão que não
        # houve: o leitor merece saber, e declarar o contrário seria falso.
        selo = ('<span class="selo selo-auto">Publicação automática</span>'
                '<span class="sep">|</span>'
                '<span>Verificada contra a fonte, sem revisão humana prévia</span>')
    else:
        selo = ('<span class="selo selo-ia">Redigido com IA</span>'
                '<span class="sep">|</span><span>Revisão: '
                f'<b>{e(revisor or "Paulo Fernando de Barros")}</b></span>')
    tarja = ""
    if not a.get("indexar", True):
        explica = {"agencia": "republicação de agência ou órgão público",
                   "noticia": "fluxo noticioso arquivado",
                   "curto": "nota curta", "duplicado": "versão duplicada"}
        razao = ", ".join(explica.get(mo, mo) for mo in a.get("motivos", []))
        tarja = ('<aside class="tarja-acervo"><b>Acervo</b> — '
                 f'{e(razao)}. Mantido para consulta; fora do jornal do dia.</aside>')

    ld = json.dumps({
        "@context": "https://schema.org", "@type": "NewsArticle",
        "headline": a["titulo"], "description": a["olho"],
        "datePublished": a["data"], "author": {"@type": "Person", "name": a["autor"]},
        "publisher": {"@type": "Organization", "name": "Duna Press"},
        "articleSection": a["editoria_nome"],
        "inLanguage": "pt-BR",
    }, ensure_ascii=False)

    miolo = f"""
<main class="materia">
  <div class="trilha"><a href="/">Capa</a> › <a href="/{a["editoria"]}/">{e(a["editoria_nome"])}</a></div>
  {tarja}
  <div class="cabeca-materia">
    <span class="chapeu">{e(a["editoria_nome"])}</span>
    <h1>{e(a["titulo"])}</h1>
    {f'<p class="linha-fina">{e(a["subtitulo"])}</p>' if a.get("subtitulo") else ""}
    <div class="assinatura">
      <span>Por <a href="/autores/{a["autor_slug"]}/"><b>{e(a["autor"])}</b></a></span>
      <span class="sep">|</span>
      <span>{e(a["data_extenso"])}</span>
      <span class="sep">|</span>
      <span>{minutos} min de leitura</span>
      <span class="sep">|</span>
      {selo}
    </div>
  </div>
  {abertura}
  <div class="texto">{corpo}</div>
  {fonte_bloco}
  {etiquetas}
  <section class="leia-mais">
    <div class="faixa-cab"><h2>Mais em {e(a["editoria_nome"])}</h2>
      <a class="tudo" href="/{a["editoria"]}/">Ver tudo →</a></div>
    <div class="quatro">{''.join(chamada(x, com_img=True, limite_olho=95) for x in relacionados)}</div>
  </section>
</main>
<script type="application/ld+json">{ld}</script>"""
    return pagina(f'{a["titulo"]} — Duna Press', a["olho"][:180], miolo,
                  eds, len(arts), a["editoria"], edicao,
                  indexar=a.get("indexar", True), canonico=a["url"])


def main():
    with open(f"{DADOS}/manifesto.json", encoding="utf-8") as fh:
        m = json.load(fh)
    arts, eds = m["artigos"], m["editorias"]
    edicao = len({a["data"] for a in arts})

    os.makedirs(SAIDA, exist_ok=True)
    escritas = 0

    def escrever(caminho, conteudo):
        nonlocal escritas
        destino = os.path.join(SAIDA, caminho.strip("/"))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(conteudo)
        escritas += 1

    escrever("index.html", montar_capa(m, edicao))
    escrever("autores/index.html", montar_indice_autores(m, edicao))
    for arquivo, destino in (("principios.md", "principios"),
                             ("correcoes.md", "correcoes")):
        escrever(f"{destino}/index.html", montar_estatica(m, arquivo, edicao))
    for slug, dados in autores_de(arts).items():
        escrever(f"autores/{slug}/index.html", montar_autor(m, slug, dados, edicao))
    for slug in eds:
        escrever(f"{slug}/index.html", montar_editoria(m, slug, edicao))

    # Todas as matérias, inclusive as que saem do índice: elas continuam
    # acessíveis e assinadas — noindex é decisão de busca, não de remoção.
    # DP_AMOSTRA=1 gera só um punhado, para desenvolvimento local.
    if os.environ.get("DP_AMOSTRA"):
        alvo, vistos = [], set()
        for a in arts:
            if a["editoria"] not in vistos:
                vistos.add(a["editoria"]); alvo.append(a)
        alvo += [a for a in arts[:6] if a not in alvo]
        fora = next((a for a in arts if not a.get("indexar", True)), None)
        if fora:
            alvo.append(fora)
    else:
        alvo = arts

    for i, a in enumerate(alvo, 1):
        escrever(f'{a["url"]}index.html', montar_artigo(m, a, edicao))
        if i % 2000 == 0:
            print(f"  {i}/{len(alvo)} matérias")

    # assets vão para o site como estão; o hash na URL cuida do cache
    for pasta in ("assets",):
        destino = os.path.join(SAIDA, pasta)
        if os.path.isdir(destino):
            shutil.rmtree(destino)
        shutil.copytree(os.path.join(RAIZ_PROJ, pasta), destino)
    open(os.path.join(SAIDA, ".nojekyll"), "w").close()
    for solto in ("robots.txt", "ads.txt", "CNAME", "site.webmanifest"):
        origem = os.path.join(RAIZ_PROJ, solto)
        if os.path.exists(origem):
            shutil.copy(origem, os.path.join(SAIDA, solto))

    os.makedirs(os.path.join(SAIDA, "api"), exist_ok=True)

    # ── Compatibilidade com os dois formatos de URL antigos ─────────────
    # O permalink /AAAA/MM/DD/slug/ é o mesmo da era WordPress, então aquelas
    # URLs voltam a funcionar sozinhas. Restam estas duas, do período em que
    # o site rodou como página estática com JavaScript. O GitHub Pages não
    # faz 301, então redirecionamos no próprio HTML — não passa autoridade
    # de link como um 301 passaria, mas nenhuma delas foi indexada (o
    # sitemap antigo tinha 91 URLs, nenhuma de matéria).
    mapa_artigo = {a["arquivo"].replace("artigos/", ""): a["url"] for a in arts}
    with open(os.path.join(SAIDA, "artigo.html"), "w", encoding="utf-8") as fh:
        fh.write(r"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="robots" content="noindex, follow">
<title>Redirecionando — Duna Press</title>
<script>
(function () {
  var p = new URLSearchParams(location.search).get("file") || "";
  var chave = p.replace(/^\/?artigos\//, "");
  fetch("/api/legado.json").then(function (r) { return r.json(); })
    .then(function (m) { location.replace(m[chave] || "/"); })
    .catch(function () { location.replace("/"); });
})();
</script></head>
<body><p>Redirecionando… <a href="/">ir para a capa</a></p></body></html>""")

    with open(os.path.join(SAIDA, "api", "legado.json"), "w", encoding="utf-8") as fh:
        json.dump(mapa_artigo, fh, ensure_ascii=False, separators=(",", ":"))

    de_para_cat = {}
    for slug_ed, dados_ed in eds.items():
        for origem in dados_ed["origens"]:
            de_para_cat[origem] = slug_ed
        de_para_cat[slug_ed] = slug_ed
    with open(os.path.join(SAIDA, "categoria.html"), "w", encoding="utf-8") as fh:
        fh.write("""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="robots" content="noindex, follow">
<title>Redirecionando — Duna Press</title>
<script>
var CAT = """ + json.dumps(de_para_cat, ensure_ascii=False) + """;
(function () {
  var c = new URLSearchParams(location.search).get("cat") || "";
  location.replace(CAT[c] ? "/" + CAT[c] + "/" : "/");
})();
</script></head>
<body><p>Redirecionando… <a href="/">ir para a capa</a></p></body></html>""")

    indexaveis = [a for a in arts if a.get("indexar", True)]

    # índice de busca: só o indexável, campos curtos, carregado sob demanda
    os.makedirs(os.path.join(SAIDA, "api"), exist_ok=True)
    with open(os.path.join(SAIDA, "api", "busca.json"), "w", encoding="utf-8") as fh:
        json.dump([{"t": a["titulo"], "u": a["url"], "e": a["editoria_nome"],
                    "d": a["data_extenso"], "o": a["olho"][:110]}
                   for a in indexaveis],
                  fh, ensure_ascii=False, separators=(",", ":"))

    # feed JSON público, para quem quiser consumir o jornal
    with open(os.path.join(SAIDA, "api", "artigos.json"), "w", encoding="utf-8") as fh:
        json.dump({
            "versao": "https://jsonfeed.org/version/1.1",
            "title": "Duna Press",
            "home_page_url": "https://dunapress.org/",
            "feed_url": "https://dunapress.org/api/artigos.json",
            "language": "pt-BR",
            "items": [{"id": f'https://dunapress.org{a["url"]}',
                       "url": f'https://dunapress.org{a["url"]}',
                       "title": a["titulo"], "summary": a["olho"],
                       "date_published": a["data"] + "T09:00:00-03:00",
                       "authors": [{"name": a["autor"]}],
                       "tags": [a["editoria_nome"]]}
                      for a in indexaveis[:200]],
        }, fh, ensure_ascii=False, indent=1)

    # RSS
    def xml(t):
        return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    with open(os.path.join(SAIDA, "rss.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
                 "<title>Duna Press</title>\n"
                 "<link>https://dunapress.org/</link>\n"
                 "<description>Jornal digital independente, em português.</description>\n"
                 "<language>pt-BR</language>\n"
                 '<atom:link href="https://dunapress.org/rss.xml" rel="self" '
                 'type="application/rss+xml"/>\n')
        for a in indexaveis[:60]:
            fh.write(f"<item><title>{xml(a['titulo'])}</title>"
                     f"<link>https://dunapress.org{a['url']}</link>"
                     f"<guid>https://dunapress.org{a['url']}</guid>"
                     f"<description>{xml(a['olho'][:280])}</description>"
                     f"<dc:creator xmlns:dc='http://purl.org/dc/elements/1.1/'>"
                     f"{xml(a['autor'])}</dc:creator>"
                     f"</item>\n")
        fh.write("</channel>\n</rss>\n")
    with open(os.path.join(SAIDA, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        fh.write("<url><loc>https://dunapress.org/</loc></url>\n")
        for slug in eds:
            fh.write(f"<url><loc>https://dunapress.org/{slug}/</loc></url>\n")
        for a in indexaveis:
            fh.write(f'<url><loc>https://dunapress.org{a["url"]}</loc>'
                     f'<lastmod>{a["data"]}</lastmod></url>\n')
        fh.write("</urlset>\n")
    print(f"sitemap.xml: {len(indexaveis) + len(eds) + 1} URLs")
    print(f"{escritas} páginas escritas em {SAIDA}")
    print(f"Capa: index.html · {len(eds)} editorias · {len(alvo)} matérias")
    print(f"Edição nº {milhar(edicao)} · acervo {milhar(len(arts))}")
    for a in alvo[:3]:
        print(f"  {a['url']}")


if __name__ == "__main__":
    main()
