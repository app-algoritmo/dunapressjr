#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — renomeia arquivos cujo nome carrega resto de tag HTML.

A migração do WordPress slugificou títulos com <strong>, <em>, <sup> e
&amp;, e as tags viraram texto no nome do arquivo. O título já foi limpo
por limpar_frontmatter.py; isto acerta o nome.

O nome novo NÃO é adivinhado a partir do antigo — isso destruiria palavras
legítimas como "strongman" e "armstrong", e a preposição "em". Ele é
derivado do título limpo, com a mesma slugificar de src/migrar.py, e só é
aplicado quando se pode provar que a diferença entre o nome antigo e o
novo é exatamente a tag removida. O que não passa nessa prova é relatado
e não tocado.

O endereço público sai do título, não do nome do arquivo: renomear aqui
não mexe em URL.

    python3 tools/renomear_arquivos.py            # diagnóstico
    python3 tools/renomear_arquivos.py --aplicar  # renomeia com git mv
"""
import os, re, sys, glob, subprocess, unicodedata
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTIGOS = os.path.join(RAIZ, "artigos")

# Fragmentos que a slugificação deixou para trás ao comer as tags.
FRAGMENTOS = ("strong", "nbsp", "amp", "sup", "sub", "em", "br")

# Fragmentos que só contam quando colados a letra. "em" e "br" isolados
# são preposição e sigla de país — removê-los estragaria o nome.
SO_COLADOS = ("em", "br")


def slugificar(texto, limite=72):
    """Cópia literal de src/migrar.py."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^\w\s-]", "", t.lower())
    t = re.sub(r"[\s_-]+", "-", t).strip("-")
    if len(t) > limite:
        corte = t[:limite].rsplit("-", 1)[0]
        t = corte or t[:limite]
    return t.strip("-")


def titulo_de(caminho):
    with open(caminho, encoding="utf-8") as fh:
        linhas = fh.read().split("\n")
    if not linhas or linhas[0].strip() != "---":
        return None
    for l in linhas[1:]:
        if l.strip() == "---":
            return None
        m = re.match(r"^title:\s*(.*)$", l)
        if not m:
            continue
        v = m.group(1).strip()
        if len(v) >= 2 and v[0] == v[-1] == '"':
            return v[1:-1].replace('\\"', '"')
        if len(v) >= 2 and v[0] == v[-1] == "'":
            return v[1:-1].replace("''", "'")
        return v
    return None


def explicavel(antigo, novo):
    """Prova que a diferença é só a tag: remove os fragmentos do nome
    antigo e compara com o nome derivado do título. A truncagem em 72
    caracteres pode cortar em pontos diferentes, então prefixo de um lado
    ou do outro também conta como prova."""
    limpo = antigo
    for frag in FRAGMENTOS:
        # "em" isolado entre hífens é a preposição, não resto de <em>.
        # Só sai quando está colado a letra: "emhistoria", "brasilem".
        if frag not in SO_COLADOS:
            limpo = re.sub(rf"(?<![a-z]){frag}(?![a-z])", "", limpo)
        limpo = re.sub(rf"(?<![a-z]){frag}(?=[a-z])", "", limpo)
        limpo = re.sub(rf"(?<=[a-z]){frag}(?![a-z])", "", limpo)
    limpo = re.sub(r"-{2,}", "-", limpo).strip("-")
    return limpo == novo or limpo.startswith(novo) or novo.startswith(limpo)


def main():
    aplicar = "--aplicar" in sys.argv
    arquivos = sorted(glob.glob(os.path.join(ARTIGOS, "**", "*.md"),
                                recursive=True))

    alvos, nao_provados, colisoes, sem_titulo = [], [], [], []

    for caminho in arquivos:
        pasta, arquivo = os.path.split(caminho)
        base, ext = os.path.splitext(arquivo)
        m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", base)
        if not m:
            continue
        data, slug = m.group(1), m.group(2)

        titulo = titulo_de(caminho)
        if not titulo:
            sem_titulo.append(caminho)
            continue

        alvo = slugificar(titulo)
        if not alvo or alvo == slug:
            continue

        # Só interessa nome que ainda carregue fragmento de tag.
        if not any(f in slug for f in FRAGMENTOS):
            continue

        if not explicavel(slug, alvo):
            nao_provados.append((caminho, slug, alvo))
            continue

        novo = os.path.join(pasta, f"{data}-{alvo}{ext}")
        if os.path.exists(novo):
            colisoes.append((caminho, novo))
            continue
        alvos.append((caminho, novo))

    print(f"Arquivos varridos ......... {len(arquivos)}")
    print(f"A renomear (comprovado) ... {len(alvos)}")
    print(f"Diferença não comprovada .. {len(nao_provados)}")
    print(f"Colisões de destino ....... {len(colisoes)}")
    print(f"Sem título legível ........ {len(sem_titulo)}")
    print()

    for antigo, novo in alvos[:30]:
        print(f"  {os.path.basename(antigo)}")
        print(f"      -> {os.path.basename(novo)}")
    if len(alvos) > 30:
        print(f"  (e mais {len(alvos) - 30})")

    if nao_provados:
        print("\nNão renomeados, diferença vai além da tag:")
        for caminho, slug, alvo in nao_provados[:15]:
            print(f"  {os.path.basename(caminho)}")
            print(f"      título daria: {alvo}")
        if len(nao_provados) > 15:
            print(f"  (e mais {len(nao_provados) - 15})")

    for antigo, novo in colisoes:
        print(f"\n  COLISÃO: {os.path.basename(antigo)}")
        print(f"      destino ocupado: {os.path.basename(novo)}")

    por_pasta = Counter(os.path.basename(os.path.dirname(a)) for a, _ in alvos)
    if por_pasta:
        print("\nPor pasta:")
        for pasta, n in por_pasta.most_common():
            print(f"  {pasta:32} {n}")

    if not aplicar:
        print("\nDiagnóstico apenas. Rode com --aplicar para renomear.")
        return

    for antigo, novo in alvos:
        subprocess.run(["git", "mv", antigo, novo], cwd=RAIZ, check=True)
    print(f"\n{len(alvos)} arquivo(s) renomeado(s) com git mv.")


if __name__ == "__main__":
    main()
