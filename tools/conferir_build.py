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
    for rel in ("index.html", "sitemap.xml", "rss.xml", "robots.txt",
                "autores/index.html", "principios/index.html",
                "correcoes/index.html", "api/busca.json",
                "assets/css/jornal.css", "assets/js/jornal.js"):
        exigir(os.path.exists(os.path.join(SITE, rel)), f"faltando: {rel}")

    if falhas:
        relatar()

    # ── Sitemap ──────────────────────────────────────────────────────────
    sm = open(os.path.join(SITE, "sitemap.xml"), encoding="utf-8").read()
    n = sm.count("<loc>")
    exigir(n >= MINIMO_SITEMAP,
           f"sitemap com {n} URLs, abaixo do piso de {MINIMO_SITEMAP}")
    exigir("dunapress.org" in sm, "sitemap sem o domínio")

    # ── Páginas de matéria ───────────────────────────────────────────────
    # Permalink plano: /slug/index.html. Excluímos as pastas de seção,
    # que também têm index.html mas não são matéria.
    secoes = {"autores", "principios", "correcoes", "api", "assets",
              "brasil", "mundo", "economia", "politica", "ciencia-e-saude",
              "tecnologia", "cultura", "esportes", "opiniao"}
    materias = [f for f in glob.glob(os.path.join(SITE, "*", "index.html"))
                if os.path.basename(os.path.dirname(f)) not in secoes]
    exigir(len(materias) > 0, "nenhuma página de matéria gerada")

    robots = Counter()
    sem_titulo = sem_selo = sem_ld = 0
    for f in materias:
        h = open(f, encoding="utf-8").read()
        robots["noindex" if "noindex" in h else "index"] += 1
        if not re.search(r"<h1>[^<]+</h1>", h):
            sem_titulo += 1
        if "class=\"selo" not in h:
            sem_selo += 1
        if '"@type": "NewsArticle"' not in h:
            sem_ld += 1

    exigir(sem_titulo == 0, f"{sem_titulo} matérias sem <h1>")
    exigir(sem_selo == 0, f"{sem_selo} matérias sem selo de proveniência")
    exigir(sem_ld == 0, f"{sem_ld} matérias sem JSON-LD")

    # ── Só o que está no sitemap pode ser indexável ──────────────────────
    urls_sitemap = set(re.findall(r"<loc>https://dunapress\.org([^<]*)</loc>", sm))
    for f in materias:
        h = open(f, encoding="utf-8").read()
        url = "/" + os.path.relpath(f, SITE).replace("\\", "/").replace("index.html", "")
        if "noindex" in h and url in urls_sitemap:
            falhas.append(f"no sitemap mas com noindex: {url}")
            break

    # ── Índice de busca ──────────────────────────────────────────────────
    busca = json.load(open(os.path.join(SITE, "api", "busca.json"), encoding="utf-8"))
    exigir(len(busca) > 0, "índice de busca vazio")
    avisar(len(busca) < 12000, "")  # placeholder: tamanho é decisão editorial

    tamanho = os.path.getsize(os.path.join(SITE, "api", "busca.json")) / 1024
    avisar(tamanho < 2048,
           f"índice de busca com {tamanho:.0f} KB — considere dividir por editoria")

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
    for f in materias[:600]:
        h = open(f, encoding="utf-8").read()
        m = CORPO.search(h)
        if not m:
            continue
        achado = LINK_COMERCIAL.search(m.group(1))
        if achado:
            falhas.append(f"link comercial em {os.path.relpath(f, SITE)}: "
                          f"{achado.group()[:70]}")
            break

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
