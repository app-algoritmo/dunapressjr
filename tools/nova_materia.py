#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — criar matéria nova.

Escrever à mão dá certo, mas há três armadilhas: o nome da pasta precisa
ser uma editoria válida, o nome do arquivo vira a URL, e frontmatter
incompleto reprova no build. Esta ferramenta cuida das três.

    python3 tools/nova_materia.py

Sem argumento, ela pergunta. Com argumentos, vai direto:

    python3 tools/nova_materia.py "Título da matéria" economia reportagem

Depois de criar, abra o arquivo, escreva, e publique:

    git add artigos/ && git commit -m "Título" && git push
"""
import os, re, sys, unicodedata
from datetime import date

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EDITORIAS = ["brasil", "mundo", "economia", "politica", "ciencia-e-saude",
             "tecnologia", "cultura", "esportes", "opiniao"]

FORMATOS = {
    "nota": (200, 350, "Um fato, o contexto mínimo, o efeito. Sem subtítulo."),
    "reportagem": (700, 1200, "Um fato, três a cinco fontes, o que se sabe "
                              "e o que não se sabe."),
    "analise": (800, 1400, "Parte de um fato e sustenta uma interpretação. "
                           "Precisa declarar o que a contradiz."),
    "explicador": (500, 900, "Responde uma pergunta que os leitores estão "
                             "fazendo por causa de um fato recente."),
    "opiniao": (600, 1000, "Assinada por pessoa, nunca pela redação."),
}


def slugificar(t, limite=72):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^\w\s-]", "", t.lower())
    t = re.sub(r"[\s_-]+", "-", t).strip("-")
    if len(t) > limite:
        t = t[:limite].rsplit("-", 1)[0]
    return t.strip("-")


def reservados():
    """Endereços de seção. Um artigo com slug igual a um deles rouba a
    página da seção — foi o que apagou /economia/ do jornal."""
    return set(EDITORIAS) | {
        "autores", "arquivo", "busca", "principios", "correcoes",
        "quem-somos", "contato", "privacidade", "cookies", "termos",
        "newsletter", "assinatura", "api", "assets", "sitemap", "rss",
        "index", "404", "artigo", "categoria", "feed", "tag", "tags",
    }


def slug_livre(slug):
    """A URL é plana: dois artigos não podem ter o mesmo slug, ainda que de
    anos diferentes."""
    for pasta, _, arquivos in os.walk(os.path.join(RAIZ, "artigos")):
        for nome in arquivos:
            if not nome.endswith(".md"):
                continue
            m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)\.md$", nome)
            if m and m.group(1) == slug:
                return os.path.join(os.path.basename(pasta), nome)
    return None


def perguntar(rotulo, opcoes=None, padrao=None):
    if opcoes:
        print("\n%s" % rotulo)
        for i, o in enumerate(opcoes, 1):
            extra = ""
            if o in FORMATOS:
                mn, mx, desc = FORMATOS[o]
                extra = "  %d–%d palavras · %s" % (mn, mx, desc)
            print("  %d. %s%s" % (i, o, extra))
        while True:
            r = input("Número%s: " % (" [%s]" % padrao if padrao else "")).strip()
            if not r and padrao:
                return padrao
            if r.isdigit() and 1 <= int(r) <= len(opcoes):
                return opcoes[int(r) - 1]
            print("  Escolha um número da lista.")
    r = input("%s%s: " % (rotulo, " [%s]" % padrao if padrao else "")).strip()
    return r or padrao or ""


def main():
    args = sys.argv[1:]
    print("DUNA PRESS — matéria nova")
    print("=" * 52)

    titulo = args[0] if args else perguntar("Título")
    while not titulo.strip():
        titulo = perguntar("Título")

    editoria = args[1] if len(args) > 1 else perguntar("Editoria", EDITORIAS)
    if editoria not in EDITORIAS:
        raise SystemExit("Editoria inválida. Use uma de: %s" % ", ".join(EDITORIAS))

    formato = args[2] if len(args) > 2 else perguntar(
        "Formato", list(FORMATOS), padrao="reportagem")
    if formato not in FORMATOS:
        raise SystemExit("Formato inválido. Use um de: %s" % ", ".join(FORMATOS))

    autor = perguntar("Assinatura", padrao="Paulo Fernando de Barros")

    slug = slugificar(titulo)
    if slug in reservados():
        slug = "%s-%d" % (slug, date.today().year)
        print("\n  aviso: o slug colidia com um endereço de seção; virou %s" % slug)
    ocupado = slug_livre(slug)
    if ocupado:
        slug = "%s-%d" % (slug, date.today().year)
        print("\n  aviso: já existe %s; o slug virou %s" % (ocupado, slug))

    hoje = date.today()
    destino = os.path.join(RAIZ, "artigos", editoria,
                           "%s-%s.md" % (hoje.isoformat(), slug))
    if os.path.exists(destino):
        raise SystemExit("Já existe: %s" % os.path.relpath(destino, RAIZ))

    mn, mx, _ = FORMATOS[formato]
    modelo = """---
title: "{titulo}"
subtitle: ""
description: ""
date: {data}
status: publish
author: "{autor}"
categories: "{editoria}"
formato: {formato}
proveniencia: humano
fonte_primaria: ""
data_do_fato: {data}
featuredImage: ""
photoAuthor: ""
photoSource: ""
tags:
  - 
---

<!-- {formato}: {mn} a {mx} palavras.

     Antes de escrever, confira se você consegue responder:
       o fato ............ o que mudou, em uma frase
       fonte primária .... URL do documento, dado ou registro original
       por que agora ..... por que é notícia hoje
       a quem afeta ...... quem sente o efeito

     Se algum ficar vazio, ainda não há matéria.

     Regras que o build verifica:
       · título não usa "parece X mas é Y" nem promete revelação
       · subtítulo com ## no início da linha, nunca **negrito**
       · proibidos: "O que está em jogo", "O que vem a seguir",
         "Conclusão", "Considerações finais"
       · termina no último fato — sem arremate nem projeção
       · nenhum link comercial no corpo

     Apague este comentário antes de publicar. -->

"""
    conteudo = modelo.format(titulo=titulo.replace('"', "'"), data=hoje.isoformat(),
                             autor=autor, editoria=editoria, formato=formato,
                             mn=mn, mx=mx)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(conteudo)

    rel = os.path.relpath(destino, RAIZ)
    print("\n" + "=" * 52)
    print("Criado: %s" % rel)
    print("URL:    https://dunapress.org/%s/" % slug)
    print()
    print("Escreva o texto e publique:")
    print()
    print("  open %s" % rel)
    print("  python3 tools/conferir_pauta.py %s" % rel)
    print("  git add %s" % rel)
    print('  git commit -m "%s"' % titulo[:60].replace('"', "'"))
    print("  git push")
    print()
    print("O push reconstrói o site e publica. Leva cerca de dois minutos.")


if __name__ == "__main__":
    main()
