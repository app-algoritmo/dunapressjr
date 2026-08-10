#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — conferência das fontes.

Feeds saem do ar, mudam de endereço e passam a exigir cabeçalho diferente
sem aviso nenhum. Quando isso acontece, o publicador simplesmente encontra
menos pautas — e ninguém percebe, porque "dia sem publicação é normal em
jornal" também é a mensagem de um sistema quebrado.

Esta ferramenta testa todos de uma vez e diz exatamente o que está errado.
Vale rodar de tempos em tempos, e sempre que a publicação automática ficar
vários dias sem produzir nada.

    python3 tools/conferir_fontes.py
    python3 tools/conferir_fontes.py --corpo    # mede também o texto da matéria
"""
import os, sys, ssl, time, urllib.request, urllib.error, re, html
from xml.etree import ElementTree

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

try:
    from auto_publicar import FONTES, limpar_html
except ImportError:
    print("Não achei src/auto_publicar.py. Rode a partir da raiz do projeto.")
    sys.exit(1)

# Alguns portais recusam requisição sem cabeçalho de navegador. Não é
# contorno de bloqueio: é identificar-se de forma que o servidor aceite.
CABECALHO = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def buscar(url, timeout=25):
    req = urllib.request.Request(url, headers=CABECALHO)
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read(), r.headers.get("content-type", "")


def medir_corpo(url):
    """Quantas palavras tem a página de destino. O publicador exige 120 no
    mínimo — abaixo disso a fonte não sustenta matéria própria."""
    try:
        bruto, _ = buscar(url, timeout=20)
        texto = limpar_html(bruto.decode("utf-8", errors="replace"))
        return len(texto.split())
    except Exception:
        return -1


def main():
    medir = "--corpo" in sys.argv
    total = ok = 0
    quebrados, rasos = [], []

    for secao, config in FONTES.items():
        print("\n%s" % secao.upper())
        print("-" * 66)
        for nome, url in config["feeds"]:
            total += 1
            try:
                bruto, tipo = buscar(url)
            except urllib.error.HTTPError as exc:
                print("  FORA   %-18s HTTP %s" % (nome, exc.code))
                quebrados.append((nome, "HTTP %s" % exc.code, url))
                continue
            except Exception as exc:
                print("  FORA   %-18s %s" % (nome, type(exc).__name__))
                quebrados.append((nome, type(exc).__name__, url))
                continue

            try:
                raiz = ElementTree.fromstring(bruto)
            except ElementTree.ParseError:
                # Resposta que não é XML costuma ser página de erro em HTML
                amostra = bruto[:80].decode("utf-8", errors="replace").strip()
                print("  XML    %-18s não é XML · %s" % (nome, amostra[:40]))
                quebrados.append((nome, "resposta não é XML", url))
                continue

            ns = {"atom": "http://www.w3.org/2005/Atom"}
            itens = raiz.findall(".//item") or raiz.findall(".//atom:entry", ns)
            if not itens:
                print("  VAZIO  %-18s XML válido, nenhum item" % nome)
                quebrados.append((nome, "feed sem itens", url))
                continue

            ok += 1
            recado = "%3d itens" % len(itens)

            if medir:
                link = None
                for tag in ("link", "{http://www.w3.org/2005/Atom}link"):
                    achado = itens[0].find(tag)
                    if achado is not None:
                        link = (achado.text or achado.get("href") or "").strip()
                        break
                if link:
                    palavras = medir_corpo(link)
                    if palavras < 0:
                        recado += " · corpo inacessível"
                    elif palavras < 120:
                        recado += " · corpo com %d palavras" % palavras
                        rasos.append((nome, palavras))
                    else:
                        recado += " · corpo com %d palavras" % palavras
                time.sleep(0.4)

            print("  ok     %-18s %s" % (nome, recado))

    print("\n" + "=" * 66)
    print("%d de %d feeds respondendo" % (ok, total))

    if quebrados:
        print("\nPRECISAM DE ENDEREÇO NOVO")
        print("-" * 66)
        for nome, motivo, url in quebrados:
            print("  %-18s %s" % (nome, motivo))
            print("  %s%s" % (" " * 20, url))
        print("\n  Procure o feed atual no site da instituição e substitua a")
        print("  linha em src/auto_publicar.py. Feed fora do ar não quebra a")
        print("  publicação: ele é ignorado e a execução segue.")

    if rasos:
        print("\nFONTES RASAS — o publicador vai recusar")
        print("-" * 66)
        for nome, palavras in rasos:
            print("  %-18s primeira matéria com %d palavras" % (nome, palavras))
        print("\n  Feeds que trazem só resumo não sustentam matéria própria.")
        print("  Considere remover, ou aceitar que rendem pouco.")

    if ok == 0:
        print("\nNenhum feed respondeu. Verifique a conexão antes de concluir")
        print("que as fontes mudaram de endereço.")
        sys.exit(1)


if __name__ == "__main__":
    main()
