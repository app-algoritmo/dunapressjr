#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Duna Press — gerador estático. Lê o manifesto e escreve HTML puro."""
import os, re, json, html, unicodedata, hashlib, shutil, urllib.parse
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

# Primeira publicação do acervo. Baliza o número da edição e o "Ano".
FUNDACAO = date(2017, 9, 10)

# A data da edição é a de hoje, não uma constante. Ficou fixa desde a
# construção e o cabeçalho passou a anunciar 7 de agosto enquanto as
# matérias saíam com 9 — a contradição mais visível que um jornal pode ter.
# DP_HOJE permite congelar a data em teste, sem afetar a publicação.
HOJE = (date.fromisoformat(os.environ["DP_HOJE"])
        if os.environ.get("DP_HOJE") else date.today())


def e(t):
    return html.escape(t or "", quote=True)


def milhar(n):
    return f"{n:,}".replace(",", ".")


MARCA_LISTA = re.compile(r"^\s*[-*+]\s+")
MARCA_NUM = re.compile(r"^\s*\d+[.)]\s+")


# ── Markdown mínimo ──────────────────────────────────────────────────────
def md_para_html(texto):
    texto = re.sub(r"\r\n?", "\n", texto)

    # Blocos de código saem do fluxo antes de qualquer outra coisa: dentro
    # deles, # e | e * são texto, não marcação.
    codigos = []

    def guardar(m):
        codigos.append((m.group(1) or "", m.group(2)))
        return "\n\nCODIGO%d\n\n" % (len(codigos) - 1)

    texto = re.sub(r"```(\w*)\n(.*?)```", guardar, texto, flags=re.S)

    saida = []
    for bloco in re.split(r"\n\s*\n", texto):
        b = bloco.strip()
        if not b:
            continue

        m = re.fullmatch(r"CODIGO(\d+)", b)
        if m:
            lang, corpo = codigos[int(m.group(1))]
            saida.append('<pre class="codigo"%s><code>%s</code></pre>'
                         % (' data-lang="%s"' % lang if lang else "",
                            e(corpo.rstrip())))
            continue

        # Linha divisória: --- ou *** sozinhos numa linha.
        if re.fullmatch(r"(\*\s*){3,}|(-\s*){3,}|(_\s*){3,}", b):
            saida.append("<hr>")
            continue

        # Tabela: a segunda linha é o separador de cabeçalho.
        linhas_b = b.split("\n")
        if (len(linhas_b) >= 2 and "|" in linhas_b[0]
                and re.fullmatch(r"[\s|:-]+", linhas_b[1])
                and "-" in linhas_b[1]):
            saida.append(montar_tabela(linhas_b))
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


def montar_tabela(linhas):
    """Converte tabela em canos para HTML.

    O conversor antigo não a reconhecia, e cada linha virava um parágrafo
    com os canos à mostra. Numa matéria com dez comparações, o texto
    aparecia como uma sequência de símbolos.
    """
    def celulas(l):
        l = l.strip()
        if l.startswith("|"):
            l = l[1:]
        if l.endswith("|"):
            l = l[:-1]
        return [c.strip() for c in l.split("|")]

    # A linha de separação pode declarar alinhamento com dois-pontos.
    alinha = []
    for c in celulas(linhas[1]):
        if c.startswith(":") and c.endswith(":"):
            alinha.append(" style=\"text-align:center\"")
        elif c.endswith(":"):
            alinha.append(" style=\"text-align:right\"")
        else:
            alinha.append("")

    cab = celulas(linhas[0])
    partes = ["<div class=\"tabela-rolagem\"><table><thead><tr>"]
    for i, c in enumerate(cab):
        partes.append("<th%s>%s</th>" % (alinha[i] if i < len(alinha) else "",
                                         inline(c)))
    partes.append("</tr></thead><tbody>")
    for l in linhas[2:]:
        if not l.strip():
            continue
        partes.append("<tr>")
        for i, c in enumerate(celulas(l)):
            partes.append("<td%s>%s</td>" % (alinha[i] if i < len(alinha) else "",
                                             inline(c)))
        partes.append("</tr>")
    partes.append("</tbody></table></div>")
    return "".join(partes)


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
    # Ano do jornal, contado da fundação — não do ano civil.
    anos = HOJE.year - FUNDACAO.year + 1
    if (HOJE.month, HOJE.day) < (FUNDACAO.month, FUNDACAO.day):
        anos -= 1
    ano_rom = ROMANOS.get(anos, str(anos))
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
      <li><a href="/busca/">Busca</a></li>
      <li><a href="/rss.xml">RSS</a></li>
    </ul></div>
    <div><h3>Nas redes</h3><ul class="rodape-redes">
      <li><a href="https://www.youtube.com/@dunapress" rel="me noopener"
             target="_blank">YouTube</a></li>
      <li><a href="https://www.instagram.com/dunapressjr/" rel="me noopener"
             target="_blank">Instagram</a></li>
      <li><a href="https://www.facebook.com/dunapressjr/" rel="me noopener"
             target="_blank">Facebook</a></li>
      <li><a href="https://x.com/dunapressjr" rel="me noopener"
             target="_blank">X</a></li>
      <li><a href="https://www.threads.com/@dunapressjr" rel="me noopener"
             target="_blank">Threads</a></li>
    </ul></div>
  </div>
  <div class="rodape-fim">
    <span>© {HOJE.year} Duna Press ·
      <a href="/privacidade/">Privacidade</a> ·
      <a href="/cookies/">Cookies</a> ·
      <a href="/termos/">Termos</a></span>
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


def montar_arquivo(m, edicao):
    """O acervo inteiro, por ano — inclusive o que está fora do índice de
    busca. Sair do índice não é sair do site: cada texto continua no
    endereço em que foi publicado, assinado por quem o escreveu. Esta é a
    porta de entrada para isso."""
    eds, todos = m["editorias"], m["artigos"]
    por_ano = {}
    for a in todos:
        if a.get("situacao") == "removido":
            continue
        por_ano.setdefault(a["ano"], []).append(a)

    blocos = []
    for ano in sorted(por_ano, reverse=True):
        do_ano = sorted(por_ano[ano], key=lambda x: x["data"], reverse=True)
        indexados = sum(1 for a in do_ano if a.get("indexar", True))
        eds_ano = Counter(a["editoria_nome"] for a in do_ano)
        lista = "".join(
            '<li><a href="%s">%s</a><span class="arq-meta">%s · %s</span></li>'
            % (a["url"], e(a["titulo"]), e(a["editoria_nome"]),
               e(data_curta(a["data"])))
            for a in do_ano[:120])
        mais = ""
        if len(do_ano) > 120:
            mais = ('<p class="arq-mais">Mostrando 120 de %s textos de %s. '
                    'Use a <a href="/busca/">busca</a> para encontrar um '
                    'título específico.</p>' % (milhar(len(do_ano)), ano))
        blocos.append(
            '<details class="ano"%s><summary><b>%s</b>'
            '<span class="arq-conta">%s textos · %s no índice de busca</span>'
            '</summary><p class="arq-eds">%s</p><ul class="arq-lista">%s</ul>%s</details>'
            % (" open" if ano == max(por_ano) else "", ano,
               milhar(len(do_ano)), milhar(indexados),
               e(" · ".join("%s (%d)" % (n, c) for n, c in eds_ano.most_common(5))),
               lista, mais))

    total = sum(len(v) for v in por_ano.values())
    miolo = """
<main class="env">
  <div class="trilha"><a href="/">Capa</a> › Arquivo</div>
  <div style="border-bottom:2px solid var(--tinta);padding:12px 0 18px">
    <h1 style="font-family:var(--display);font-size:44px;font-weight:700;
      letter-spacing:-.026em;margin:0">Arquivo</h1>
    <p style="font-family:var(--util);font-size:13px;color:var(--tinta-2);
      margin:8px 0 0;max-width:64ch">Tudo que o Duna Press publicou desde
      2017, ano a ano. Parte do acervo está fora do índice dos buscadores —
      republicação de agência, notas curtas, material duplicado. Continua
      aqui, no endereço original e assinado por quem escreveu.</p>
  </div>
  <div class="arquivo">%s</div>
</main>""" % "".join(blocos)
    return pagina("Arquivo — Duna Press",
                  "O acervo completo do Duna Press, ano a ano, desde 2017.",
                  miolo, eds, len(todos), None, edicao, canonico="/arquivo/")


def montar_busca(m, edicao):
    """Busca no cliente, sobre um índice estático. Sem servidor, sem
    rastreamento do que o leitor procura."""
    eds, todos = m["editorias"], m["artigos"]
    miolo = """
<main class="env">
  <div class="trilha"><a href="/">Capa</a> › Busca</div>
  <div style="border-bottom:2px solid var(--tinta);padding:12px 0 18px">
    <h1 style="font-family:var(--display);font-size:44px;font-weight:700;
      letter-spacing:-.026em;margin:0">Busca</h1>
    <p style="font-family:var(--util);font-size:13px;color:var(--tinta-2);
      margin:8px 0 0">Procura por título e linha de apoio. Três letras no
      mínimo.</p>
  </div>
  <div style="padding:26px 0 0;max-width:680px">
    <label for="busca" class="rotulo" style="display:block;border:0;
      padding:0;margin-bottom:8px">O que você procura</label>
    <input id="busca" type="search" autocomplete="off" autofocus
      placeholder="palavra do título…"
      style="width:100%;font-family:var(--corpo);font-size:19px;padding:12px 14px;
      border:1px solid var(--fio-2);background:var(--papel);color:var(--tinta)">
    <div id="busca-resultado" style="margin-top:26px"></div>
  </div>
</main>"""
    return pagina("Busca — Duna Press", "Busque no acervo do Duna Press.",
                  miolo, eds, len(todos), None, edicao, canonico="/busca/")


def montar_capa(m, edicao):
    eds, todos = m["editorias"], m["artigos"]
    arts = [a for a in todos if a.get("indexar", True)]
    total = len(todos)
    if not arts:
        raise SystemExit(
            "Nenhuma matéria indexável: a capa não tem o que mostrar.\n"
            "Verifique dados/indexacao.txt — provavelmente a régua de\n"
            "classificação está excluindo tudo, ou artigos/ está vazia.")
    # Ordem da capa. Sem peso, a manchete seria sempre a última coisa
    # publicada — e uma nota de 220 palavras sobre alerta de vento tomaria
    # o lugar de uma reportagem de fôlego. Recência continua mandando, mas
    # dentro do dia o porte decide.
    def peso(a):
        dias = (HOJE - date.fromisoformat(a["data"])).days
        porte = {"longa": 3, "media": 2, "curta": 0}.get(a.get("porte"), 1)
        # Cada dia de idade custa mais que qualquer diferença de porte:
        # jornal é cronológico, o porte só desempata o que saiu junto.
        return (-max(dias, 0) * 10) + porte

    recentes = sorted(arts[:400], key=peso, reverse=True)[:200]
    lead = recentes[0]
    # "Em desenvolvimento" só quando a manchete é do dia. Depois disso a
    # cobertura não está mais em andamento — está publicada.
    do_dia = (HOJE - date.fromisoformat(lead["data"])).days <= 0
    viva = " viva" if do_dia else ""
    selo_lead = " · Em desenvolvimento" if do_dia else ""
    secundarias = recentes[1:4]
    ultimas = recentes[4:13]
    # Com acervo pequeno as faixas simplesmente não aparecem, em vez de
    # quebrar o build.

    opinioes = [a for a in arts if a["editoria"] == "opiniao"][:3]
    if len(opinioes) < 3:
        opinioes += [a for a in recentes if a not in opinioes][:3 - len(opinioes)]

    usados = {a["url"] for a in recentes[:13]} | {a["url"] for a in opinioes}

    def marca_tempo(a):
        """Hoje mostra "hoje"; ontem, "ontem"; antes disso, a data. Nunca
        uma hora — o acervo não guarda hora de publicação, e inventá-la
        numa coluna de chamadas seria informação falsa."""
        d = date.fromisoformat(a["data"])
        dias = (HOJE - d).days
        if dias <= 0:
            return "hoje"
        if dias == 1:
            return "ontem"
        if dias < 7:
            return "%d dias" % dias
        return "%d %s" % (d.day, MESES[d.month - 1][:3])

    lista_ultimas = "".join(
        '<article class="ultima"><span class="hora">%s</span>'
        '<h3 class="titulo"><a href="%s">%s</a></h3></article>'
        % (marca_tempo(a), a["url"], e(a["titulo"]))
        for a in ultimas)

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
      <div class="rotulo marcado">Ver também</div>
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
        <span class="chapeu{viva}">{e(lead["editoria_nome"])}{selo_lead}</span>
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
  <div class="capa capa-editoria">
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

    # Compartilhar fica no fim do texto, antes das etiquetas: é ali que o
    # leitor decide se valeu a pena. No alto, o botão pede divulgação de
    # algo que ainda não foi lido — e ocupa o espaço da manchete.
    endereco = "https://dunapress.org%s" % a["url"]
    titulo_share = a["titulo"]
    compartilhar = (
        '<div class="compartilhar" data-url="%s" data-titulo="%s">'
        '<span class="rotulo-share">Compartilhar</span>'
        '<a class="share-btn" data-rede="whatsapp" target="_blank" rel="noopener"'
        ' href="https://api.whatsapp.com/send?text=%s%%20%s"'
        ' aria-label="Compartilhar no WhatsApp">WhatsApp</a>'
        '<a class="share-btn" data-rede="x" target="_blank" rel="noopener"'
        ' href="https://x.com/intent/post?text=%s&amp;url=%s"'
        ' aria-label="Compartilhar no X">X</a>'
        '<a class="share-btn" data-rede="facebook" target="_blank" rel="noopener"'
        ' href="https://www.facebook.com/sharer/sharer.php?u=%s"'
        ' aria-label="Compartilhar no Facebook">Facebook</a>'
        '<a class="share-btn" data-rede="linkedin" target="_blank" rel="noopener"'
        ' href="https://www.linkedin.com/sharing/share-offsite/?url=%s"'
        ' aria-label="Compartilhar no LinkedIn">LinkedIn</a>'
        '<button class="share-btn share-copiar" type="button"'
        ' aria-label="Copiar o endereço">Copiar link</button>'
        '</div>'
        % (e(endereco), e(titulo_share),
           urllib.parse.quote(titulo_share), urllib.parse.quote(endereco),
           urllib.parse.quote(titulo_share), urllib.parse.quote(endereco),
           urllib.parse.quote(endereco),
           urllib.parse.quote(endereco)))


    relacionados = [x for x in arts if x.get("indexar", True)
                    and x["editoria"] == a["editoria"] and x["url"] != a["url"]][:4]
    minutos = max(1, round(a["palavras"] / 220))
    # Proveniência declarada em toda matéria. É a resposta honesta à
    # pergunta que todo leitor faz em 2026 antes mesmo de ler.
    prov = a.get("proveniencia", "humano")
    revisor = a.get("revisor", "")
    if prov == "humano":
        selo = ('<span class="sep">|</span>'
                '<span class="selo selo-h">Reportagem humana</span>')
    elif prov == "ia-autonomo" and not revisor:
        # Publicada por processo automático. Não afirmamos revisão que não
        # houve: o leitor merece saber, e declarar o contrário seria falso.
        selo = ('<span class="sep">|</span>'
                '<span class="selo selo-auto">Publicação automática</span>'
                '<span class="sep">|</span>'
                '<span>Verificada contra a fonte, sem revisão humana prévia</span>')
    else:
        selo = ('<span class="sep">|</span>'
                '<span class="selo selo-ia">Redigido com IA</span>'
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
      {selo}
    </div>
  </div>
  {abertura}
  <div class="texto">{corpo}</div>
  {fonte_bloco}
  {compartilhar}
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
    # Número da edição: dias corridos desde a fundação, como faz jornal de
    # papel. Contar apenas os dias em que houve publicação parecia mais
    # honesto, mas produzia um número que não avança em dia sem matéria —
    # e número de edição existe justamente para ser único por dia.
    # O jornal existe desde 2017 inclusive nos dias em que não saiu.
    edicao = (HOJE - FUNDACAO).days + 1

    # A saída é reconstruída do zero. Sem isto, uma mudança de permalink
    # deixa as páginas do formato antigo para trás: o site publicado passa
    # a ter duas versões de cada matéria, e a contagem de arquivos dobra.
    if os.path.isdir(SAIDA):
        shutil.rmtree(SAIDA)
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
    escrever("arquivo/index.html", montar_arquivo(m, edicao))
    escrever("busca/index.html", montar_busca(m, edicao))
    for arquivo, destino in (("principios.md", "principios"),
                             ("correcoes.md", "correcoes"),
                             ("quem-somos.md", "quem-somos"),
                             ("contato.md", "contato"),
                             ("privacidade.md", "privacidade"),
                             ("cookies.md", "cookies"),
                             ("termos.md", "termos"),
                             ("newsletter.md", "newsletter"),
                             ("assinatura.md", "assinatura")):
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
    for pasta in ("assets", "admin"):
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

    # ── 404: resgata as URLs com data, do permalink usado até 2024 ───────
    # O GitHub Pages serve esta página para qualquer caminho inexistente.
    # Em vez de anunciar o erro, ela tenta primeiro salvar a visita: se o
    # caminho tem a forma /AAAA/MM/DD/slug/, o slug ainda é válido — só o
    # prefixo de data saiu. Gerar uma página de redirecionamento para cada
    # uma das 19.540 URLs antigas dobraria a contagem de arquivos; aqui
    # uma página só resolve todas.
    css_404 = ('<link rel="stylesheet" href="%s">\n'
               '<link rel="stylesheet" href="%s">'
               % (versao("assets/css/fontes.css"),
                  versao("assets/css/jornal.css")))
    salto = (r'var m = location.pathname.match(/^\/\d{4}\/\d{2}\/\d{2}\/'
             r'([^\/]+)\/?$/); if (m && m[1]) location.replace("/" + m[1] + "/");')
    with open(os.path.join(SAIDA, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(
            '<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<meta name="robots" content="noindex, follow">\n'
            '<title>Página não encontrada — Duna Press</title>\n'
            + css_404 +
            '\n<script>(function(){' + salto + '})();</script>\n'
            '</head>\n<body>\n<main class="env" style="padding:80px 28px;max-width:640px">\n'
            '  <p class="chapeu">Erro 404</p>\n'
            '  <h1 style="font-family:var(--display);font-size:44px;font-weight:700;'
            'letter-spacing:-.026em;line-height:1.05;margin:10px 0 0">'
            'Esta página não existe</h1>\n'
            '  <p class="olho" style="font-size:18px;margin-top:16px">O endereço pode '
            'ter mudado ou o texto pode ter saído do ar. O acervo continua aberto.</p>\n'
            '  <p style="margin-top:28px">'
            '<a href="/" style="color:var(--marca);border-bottom:1px solid var(--marca)">'
            'Ir para a capa</a> &nbsp;·&nbsp; '
            '<a href="/autores/" style="color:var(--marca);'
            'border-bottom:1px solid var(--marca)">Ver os autores</a></p>\n'
            '</main>\n</body></html>\n')

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
