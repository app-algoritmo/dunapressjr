#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — conferência do site gerado.

Roda depois do build, antes de publicar. Existe porque um pipeline que
falha em silêncio publica um jornal quebrado, e ninguém percebe até o
tráfego cair.

Sai com código 1 se algo estiver errado, o que interrompe a publicação.
"""
import os, re, sys, json, glob
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("DP_SAIDA", os.path.join(RAIZ, "site"))

# Piso do sitemap. Queda abrupta indica pipeline quebrado, não decisão
# editorial — decisão editorial se toma em classificar.py, não por acidente.
MINIMO_SITEMAP = 3000

# GitHub Pages não limita a contagem de arquivos, mas recomenda até 1 GB
# por publicação. O teto abaixo é folgado e serve para pegar build
# desgovernado; o peso em GB é a checagem que importa de fato.
TETO_ARQUIVOS = int(os.environ.get("DP_TETO_ARQUIVOS", "250000"))

# Só a meta tag conta como noindex. Procurar a palavra solta no HTML
# reprova matéria que apenas fala do assunto — uma reportagem sobre
# rastreadores web cita "noindex" no corpo e não está desindexada.
META_NOINDEX = re.compile(
    r'<meta[^>]+name=["\']robots["\'][^>]*content=["\'][^"\']*noindex', re.I)

falhas, avisos = [], []


def exigir(condicao, mensagem):
    if not condicao:
        falhas.append(mensagem)


def avisar(condicao, mensagem):
    if not condicao:
        avisos.append(mensagem)


def main():
    if not os.path.isdir(SITE):
        print(f"ERRO: {SITE} não existe. O build rodou?")
        sys.exit(1)

    # ── Arquivos que precisam existir ────────────────────────────────────
    # Toda página que o rodapé promete precisa existir. Link do rodapé que
    # leva a 404 é o tipo de defeito que passa despercebido por meses.
    for rel in ("index.html", "sitemap.xml", "rss.xml", "robots.txt",
                "404.html", "autores/index.html", "principios/index.html",
                "correcoes/index.html", "arquivo/index.html",
                "busca/index.html", "quem-somos/index.html",
                "contato/index.html", "privacidade/index.html",
                "cookies/index.html", "termos/index.html",
                "newsletter/index.html", "assinatura/index.html",
                "api/busca.json", "assets/css/jornal.css",
                "assets/js/jornal.js", "admin/index.html", "admin/config.yml"):
        exigir(os.path.exists(os.path.join(SITE, rel)), f"faltando: {rel}")

    if falhas:
        relatar()

    # ── Sitemap ──────────────────────────────────────────────────────────
    # sitemap.xml é um índice; as URLs de matéria estão nas partes. Somamos
    # as partes, senão o piso reprovaria um índice de três linhas.
    indice = open(os.path.join(SITE, "sitemap.xml"), encoding="utf-8").read()
    exigir("<sitemapindex" in indice, "sitemap.xml não é um índice")
    exigir("dunapress.org" in indice, "sitemap sem o domínio")

    partes = re.findall(r"<loc>https://dunapress\.org/([^<]+\.xml)</loc>", indice)
    exigir(len(partes) >= 2, f"índice do sitemap com {len(partes)} partes")

    sm = ""
    for parte in partes:
        caminho = os.path.join(SITE, parte)
        if not os.path.exists(caminho):
            falhas.append(f"sitemap {parte} listado no índice mas ausente")
            continue
        sm += open(caminho, encoding="utf-8").read()

    n = sm.count("<loc>")
    exigir(n >= MINIMO_SITEMAP,
           f"sitemap com {n} URLs, abaixo do piso de {MINIMO_SITEMAP}")

    # ── Páginas de matéria ───────────────────────────────────────────────
    # Permalink plano: /slug/index.html. Excluímos as pastas de seção,
    # que também têm index.html mas não são matéria.
    secoes = {"autores", "principios", "correcoes", "api", "assets",
              "arquivo", "busca", "quem-somos", "contato", "privacidade",
              "cookies", "termos", "newsletter", "assinatura", "admin",
              "brasil", "mundo", "economia", "politica", "ciencia-e-saude",
              "tecnologia", "cultura", "esportes", "opiniao"}
    materias = [f for f in glob.glob(os.path.join(SITE, "*", "index.html"))
                if os.path.basename(os.path.dirname(f)) not in secoes]
    exigir(len(materias) > 0, "nenhuma página de matéria gerada")

    urls_sitemap = set(re.findall(r"<loc>https://dunapress\.org([^<]*)</loc>", sm))

    robots = Counter()
    sem_titulo = sem_selo = sem_ld = 0
    conflitos = []
    for f in materias:
        h = open(f, encoding="utf-8").read()
        noindex = bool(META_NOINDEX.search(h))
        robots["noindex" if noindex else "index"] += 1
        if not re.search(r"<h1>[^<]+</h1>", h):
            sem_titulo += 1
        if "class=\"selo" not in h:
            sem_selo += 1
        if '"@type": "NewsArticle"' not in h:
            sem_ld += 1

        # ── Só o que está no sitemap pode ser indexável ──────────────────
        # Sem break: interromper no primeiro conflito esconde os demais e
        # obriga a rodar o build de novo a cada correção.
        url = "/" + os.path.relpath(f, SITE).replace("\\", "/").replace("index.html", "")
        if noindex and url in urls_sitemap:
            conflitos.append(url)

    exigir(sem_titulo == 0, f"{sem_titulo} matérias sem <h1>")
    exigir(sem_selo == 0, f"{sem_selo} matérias sem selo de proveniência")
    exigir(sem_ld == 0, f"{sem_ld} matérias sem JSON-LD")

    if conflitos:
        falhas.append(f"{len(conflitos)} no sitemap mas com noindex: "
                      + ", ".join(conflitos[:6])
                      + (f" (e mais {len(conflitos) - 6})" if len(conflitos) > 6 else ""))

    # ── Índice de busca ──────────────────────────────────────────────────
    busca = json.load(open(os.path.join(SITE, "api", "busca.json"), encoding="utf-8"))
    exigir(len(busca) > 0, "índice de busca vazio")
    avisar(len(busca) < 12000, "")  # placeholder: tamanho é decisão editorial

    tamanho = os.path.getsize(os.path.join(SITE, "api", "busca.json")) / 1024
    avisar(tamanho < 2048,
           f"índice de busca com {tamanho:.0f} KB — considere dividir por editoria")

    # ── Nenhum link interno pode levar a 404 ─────────────────────────────
    alvos = set()
    for f in ("index.html", "arquivo/index.html", "autores/index.html",
              "principios/index.html", "quem-somos/index.html"):
        caminho = os.path.join(SITE, f)
        if not os.path.exists(caminho):
            continue
        h = open(caminho, encoding="utf-8").read()
        alvos |= set(re.findall(r'href="(/[^"#?]*)"', h))
    quebrados = []
    for a in sorted(alvos):
        rel = a.strip("/")
        if (os.path.exists(os.path.join(SITE, rel))
                or os.path.exists(os.path.join(SITE, rel, "index.html"))):
            continue
        quebrados.append(a)
    exigir(not quebrados,
           "links internos sem destino: " + ", ".join(quebrados[:6]))

    # ── Teto de arquivos da plataforma ───────────────────────────────────
    total_arquivos = sum(len(fs) for _, _, fs in os.walk(SITE))
    exigir(total_arquivos <= TETO_ARQUIVOS,
           f"{total_arquivos} arquivos, acima do teto de {TETO_ARQUIVOS} "
           "do Cloudflare Pages — o deploy será recusado")
    folga = TETO_ARQUIVOS - total_arquivos
    avisar(folga > 1500,
           f"{total_arquivos} arquivos, restam {folga} até o teto configurado "
           f"de {TETO_ARQUIVOS}")

    # GitHub Pages: 1 GB por publicação é o limite recomendado.
    peso = sum(os.path.getsize(os.path.join(r, f))
               for r, _, fs in os.walk(SITE) for f in fs) / (1024 ** 3)
    exigir(peso < 1.0, f"site com {peso:.2f} GB, acima do limite de 1 GB do "
                       "GitHub Pages")
    avisar(peso < 0.7, f"site com {peso:.2f} GB — o limite do GitHub Pages é 1 GB")

    # ── Peso da capa ─────────────────────────────────────────────────────
    capa = os.path.getsize(os.path.join(SITE, "index.html")) / 1024
    avisar(capa < 150, f"capa com {capa:.0f} KB, acima do razoável para HTML")

    # ── Nenhum link comercial deve sobreviver ao build ───────────────────
    # Só interessa o que é LINK, e só dentro do corpo editorial. Citar
    # "Hotmart" numa reportagem sobre educação é jornalismo; linkar para lá
    # com parâmetro de afiliado é outra coisa. A versão anterior desta
    # checagem confundia as duas e barrava a publicação por uma palavra
    # legítima no texto.
    CORPO = re.compile(r'<div class="texto[^"]*">(.*?)</div>\s*(?:<aside|<div class="etiquetas"|<section)', re.S)
    LINK_COMERCIAL = re.compile(
        r'href="[^"]*(?:nubank\.com\.br/pagar|picpay\.me|pix[-_]?autorizado'
        r'|hotmart\.com|monetizze|eduzz|kiwify|braip'
        r'|[?&](?:ref|aff|afiliado)=)[^"]*"', re.I)
    comerciais = []
    for f in materias:
        h = open(f, encoding="utf-8").read()
        m = CORPO.search(h)
        if not m:
            continue
        achado = LINK_COMERCIAL.search(m.group(1))
        if achado:
            comerciais.append(f"{os.path.relpath(f, SITE)}: {achado.group()[:70]}")
    if comerciais:
        falhas.append(f"{len(comerciais)} link(s) comercial(is): "
                      + "; ".join(comerciais[:4]))

    relatar(n, len(materias), robots, capa)


def relatar(urls=0, materias=0, robots=None, capa=0):
    if materias:
        print(f"sitemap ............ {urls} URLs")
        print(f"matérias geradas ... {materias}")
        if robots:
            print(f"  indexadas ........ {robots['index']}")
            print(f"  noindex .......... {robots['noindex']}")
        print(f"capa ............... {capa:.0f} KB")
        n_arq = sum(len(fs) for _, _, fs in os.walk(SITE))
        gb = sum(os.path.getsize(os.path.join(r, f))
                 for r, _, fs in os.walk(SITE) for f in fs) / (1024 ** 3)
        print(f"arquivos ........... {n_arq}")
        print(f"peso ............... {gb:.2f} GB / 1 GB")
        print()

    for a in avisos:
        if a:
            print(f"aviso: {a}")
    if falhas:
        print()
        for f in falhas:
            print(f"FALHA: {f}")
        print(f"\n{len(falhas)} problema(s). Publicação interrompida.")
        sys.exit(1)
    print("Build conferido.")


if __name__ == "__main__":
    main()
