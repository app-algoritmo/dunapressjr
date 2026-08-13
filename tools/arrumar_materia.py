#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — arrumar matéria.

Texto colado de um chat ou de um editor de texto chega quase sempre sem
linha em branco entre os parágrafos. Em Markdown, isso não é detalhe de
estética: blocos sem linha em branco entre si são um bloco só. Um artigo
inteiro pode virar um único cabeçalho, com tabelas e código dentro dele.

Esta ferramenta conserta o espaçamento e as armadilhas conhecidas, sem
tocar no texto em si.

    python3 tools/arrumar_materia.py artigos/technology/2026-08-11-x.md
    python3 tools/arrumar_materia.py --conferir artigos/**/*.md
"""
import os, re, sys

EDITORIAS = {"brasil", "mundo", "economia", "politica", "ciencia-e-saude",
             "tecnologia", "cultura", "esportes", "opiniao"}

FORMATOS = {"nota": (200, 350), "reportagem": (700, 1200),
            "analise": (800, 1400), "explicador": (400, 900),
            "opiniao": (600, 1000)}


def separar(texto):
    """Divide em cabeçalho e corpo, exigindo o frontmatter completo."""
    if not texto.startswith("---"):
        return None, texto
    fim = texto.find("\n---", 3)
    if fim == -1:
        return None, texto
    return texto[3:fim].strip("\n"), texto[fim + 4:].lstrip("\n")


def espacar(corpo):
    """Garante uma linha em branco entre blocos.

    Preserva o interior de blocos de código e de tabelas, onde as linhas
    são coladas de propósito.
    """
    linhas = corpo.split("\n")
    saida, dentro_codigo = [], False

    def e_tabela(i):
        return (i < len(linhas) and "|" in linhas[i]
                and linhas[i].strip().startswith("|"))

    for i, l in enumerate(linhas):
        se_fecha = l.strip().startswith("```")
        if se_fecha:
            dentro_codigo = not dentro_codigo
            if saida and saida[-1].strip():
                saida.append("")
            saida.append(l)
            if not dentro_codigo:
                saida.append("")
            continue

        if dentro_codigo:
            saida.append(l)
            continue

        vazia = not l.strip()
        if vazia:
            if saida and saida[-1] != "":
                saida.append("")
            continue

        # Linhas seguidas de tabela ficam juntas; o resto se separa.
        anterior_tabela = e_tabela(i - 1) if i else False
        esta_tabela = e_tabela(i)

        if saida and saida[-1].strip():
            if not (anterior_tabela and esta_tabela):
                saida.append("")
        saida.append(l)

    texto = "\n".join(saida)
    return re.sub(r"\n{3,}", "\n\n", texto).strip() + "\n"


def consertar(corpo):
    """Corrige as armadilhas que já custaram tempo neste projeto."""
    notas = []

    # --- no corpo fecha o frontmatter no lugar errado.
    n = len(re.findall(r"^---+$", corpo, re.M))
    if n:
        corpo = re.sub(r"^---+$", "***", corpo, flags=re.M)
        notas.append("%d separador(es) --- trocados por ***" % n)

    # Intertítulo em negrito vira parágrafo forte, não subtítulo.
    def negrito_para_titulo(m):
        return "## " + m.group(1)

    antes = corpo
    corpo = re.sub(r"^\*\*([^*\n]{3,80})\*\*$", negrito_para_titulo,
                   corpo, flags=re.M)
    if corpo != antes:
        notas.append("intertítulos em negrito convertidos para ##")

    return corpo, notas


def conferir(cabecalho, corpo):
    """Aponta o que a ferramenta não conserta sozinha."""
    avisos = []
    campos = dict(re.findall(r"^(\w+):\s*(.*)$", cabecalho or "", re.M))

    cat = campos.get("categories", "").strip('"\' ')
    if cat and cat not in EDITORIAS:
        avisos.append('categories: "%s" não é editoria — use uma de: %s'
                      % (cat, ", ".join(sorted(EDITORIAS))))

    fmt = campos.get("formato", "").strip('"\' ')
    palavras = len(re.sub(r"```.*?```", "", corpo, flags=re.S).split())
    if fmt in FORMATOS:
        mn, mx = FORMATOS[fmt]
        if not mn <= palavras <= mx:
            avisos.append("%d palavras, fora da faixa de %s (%d–%d)"
                          % (palavras, fmt, mn, mx))
    elif fmt:
        avisos.append("formato \"%s\" não existe — use: %s"
                      % (fmt, ", ".join(FORMATOS)))

    desc = campos.get("description", "").strip('"\' ')
    if len(desc) > 220:
        avisos.append("description com %d caracteres; o buscador corta "
                      "por volta de 160" % len(desc))

    prov = campos.get("proveniencia", "").strip()
    if prov == "ia-autonomo" and campos.get("revisor"):
        avisos.append("proveniencia ia-autonomo com revisor declarado — "
                      "se você revisou, use ia-assistido")

    banidos = ["o que está em jogo", "o que vem a seguir", "conclusão",
               "considerações finais", "em resumo"]
    for h in re.findall(r"^#{2,4}\s+(.+)$", corpo, re.M):
        if h.strip().lower() in banidos:
            avisos.append('subtítulo banido pela pauta: "%s"' % h.strip())

    if re.search(r"\bhttps?://\S+", corpo.split("\n")[0] if corpo else ""):
        avisos.append("URL crua no primeiro título — use link em Markdown")

    return avisos, palavras


def processar(caminho, so_conferir=False):
    with open(caminho, encoding="utf-8") as fh:
        bruto = fh.read()

    cabecalho, corpo = separar(bruto)
    nome = os.path.basename(caminho)

    if cabecalho is None:
        print("%s\n  ERRO: frontmatter ausente ou não fechado. O arquivo "
              "precisa começar\n       com --- na linha 1 e ter outro --- "
              "fechando o cabeçalho." % nome)
        return False

    novo_corpo, notas = consertar(corpo)
    novo_corpo = espacar(novo_corpo)
    avisos, palavras = conferir(cabecalho, novo_corpo)

    mudou = novo_corpo != corpo
    if mudou and not so_conferir:
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write("---\n%s\n---\n\n%s" % (cabecalho, novo_corpo))

    print("%s  ·  %d palavras" % (nome, palavras))
    if mudou:
        print("  %s espaçamento entre blocos normalizado"
              % ("[conferência]" if so_conferir else "corrigido:"))
    for n in notas:
        print("  corrigido: %s" % n)
    for a in avisos:
        print("  atenção: %s" % a)
    if not mudou and not notas and not avisos:
        print("  nada a corrigir")
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    so_conferir = "--conferir" in sys.argv

    if not args:
        print(__doc__.strip())
        return

    for caminho in args:
        if os.path.isfile(caminho):
            processar(caminho, so_conferir)
            print()


if __name__ == "__main__":
    main()
