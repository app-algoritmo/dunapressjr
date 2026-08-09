#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — conferência da pauta nos artigos de um Pull Request.

Roda em toda proposta de matéria. Aplica as mesmas regras de forma que
src/publicar.py aplica na geração, para que texto escrito à mão passe pelo
mesmo crivo que o texto assistido por IA.

    python3 tools/conferir_pauta.py            # artigos alterados vs. main
    python3 tools/conferir_pauta.py caminho.md # um arquivo específico
"""
import os, re, sys, subprocess, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUBTITULOS_BANIDOS = [
    "o que esta em jogo", "o que vem a seguir", "o que esperar dos proximos",
    "conclusao", "consideracoes finais", "em resumo", "para concluir",
]
TITULOS_BANIDOS = [
    (r"\bparece\b.{0,40}\bmas (é|e)\b", "fórmula 'parece X, mas é Y'"),
    (r"\bo que ningu(é|e)m (te )?conta\b", "promessa de revelação"),
    (r"^(você|voce|será que|sera que)\b", "pergunta ao leitor no título"),
    (r"\bvai (mudar|surpreender) tudo\b", "sensacionalismo"),
]
COMERCIAL = re.compile(
    r"\[\s*\]\(|[?&](ref|aff|afiliado)=|nubank\.com\.br/pagar|picpay\.me"
    r"|pix[-_ ]?autorizado|hotmart|monetizze|eduzz|kiwify", re.I)


def sem_acento(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def alterados():
    """Artigos que este PR toca. Compara com a base, não com o disco."""
    for base in ("origin/main", "main"):
        try:
            saida = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=AM", f"{base}...HEAD"],
                cwd=RAIZ, capture_output=True, text=True, check=True).stdout
            return [l for l in saida.split("\n")
                    if l.startswith("artigos/") and l.endswith(".md")]
        except subprocess.CalledProcessError:
            continue
    return []


def conferir(rel):
    caminho = os.path.join(RAIZ, rel)
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        bruto = fh.read()

    erros = []
    cab, corpo = "", bruto
    if bruto.startswith("---"):
        f = bruto.find("\n---", 3)
        if f > 0:
            cab, corpo = bruto[3:f], bruto[f + 4:]

    def campo(nome):
        m = re.search(rf"^{nome}:\s*(.+)$", cab, re.M)
        return m.group(1).strip().strip("\"'") if m else ""

    titulo = campo("title")
    if not titulo:
        erros.append("sem título no frontmatter")
    for rx, motivo in TITULOS_BANIDOS:
        if titulo and re.search(rx, titulo, re.I):
            erros.append(f"título: {motivo}")

    if not campo("author"):
        erros.append("sem autor")

    # Proveniência: exigência da política editorial, não detalhe de metadado
    prov = campo("proveniencia")
    if prov == "ia-assistido" and not campo("revisor"):
        erros.append("redigido com IA sem revisor nomeado")
    if prov and prov not in ("humano", "ia-assistido"):
        erros.append(f"proveniência inválida: {prov}")

    # Fato verificável
    if prov == "ia-assistido":
        if not campo("fonte_primaria"):
            erros.append("sem fonte_primaria")
        if not campo("data_do_fato"):
            erros.append("sem data_do_fato")

    for h in re.findall(r"^#{2,4}\s+(.+)$", corpo, re.M):
        alvo = sem_acento(h)
        for banido in SUBTITULOS_BANIDOS:
            if banido in alvo:
                erros.append(f"subtítulo banido: “{h.strip()[:48]}”")

    if COMERCIAL.search(corpo):
        erros.append("link comercial no corpo")

    n = len(corpo.split())
    if n < 150:
        erros.append(f"corpo com {n} palavras — curto demais para publicar")

    return erros


def main():
    alvos = sys.argv[1:] or alterados()
    if not alvos:
        print("Nenhum artigo alterado neste PR.")
        return

    total = 0
    for rel in alvos:
        erros = conferir(rel)
        nome = os.path.basename(rel)
        if erros:
            total += len(erros)
            print(f"\n✗ {nome}")
            for x in erros:
                print(f"    · {x}")
        else:
            print(f"✓ {nome}")

    print()
    if total:
        print(f"{total} problema(s) contra a pauta editorial.")
        print("Ver editorial/PAUTA-EDITORIAL.md")
        sys.exit(1)
    print(f"{len(alvos)} artigo(s) conferido(s).")


if __name__ == "__main__":
    main()
