#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — publicação assistida por IA, sob revisão humana.

Substitui o auto_publicar.py, que escrevia direto na main. Aqui nada entra
no jornal sem um humano aprovar: cada matéria vira um Pull Request.

A pauta (editorial/PAUTA-EDITORIAL.md) é aplicada em dois momentos:

  antes  — sem fato verificável e fonte primária, nem chega a redigir
  depois — o texto passa por conferência de forma; reprovou, não abre PR

As reprovações não são desperdício. São o mecanismo que impede o padrão que
degradou o acervo de 2026: matéria nascida de tema, não de fato.

Uso:
    python3 publicar.py pauta.json
    python3 publicar.py pauta.json --ensaio      # não abre PR, só mostra

Variáveis de ambiente:
    ANTHROPIC_API_KEY    obrigatória
    GITHUB_TOKEN         obrigatória, salvo em --ensaio
    GITHUB_REPO          ex.: app-algoritmo/dunapressjr
"""
import os, re, sys, json, subprocess, unicodedata, urllib.request
from datetime import date, datetime

RAIZ = os.path.dirname(os.path.abspath(__file__))
MODELO = "claude-sonnet-4-6"
TETO_DIARIO = 8          # acima disso a revisão vira carimbo

FORMATOS = {
    "nota":        (200, 350),
    "reportagem":  (700, 1200),
    "analise":     (800, 1400),
    "explicador":  (500, 900),
    "opiniao":     (600, 1000),
}

EDITORIAS = ["brasil", "mundo", "economia", "politica", "ciencia-e-saude",
             "tecnologia", "cultura", "esportes", "opiniao"]

# ── Conferência de forma ─────────────────────────────────────────────────
# Cada item aqui foi medido no acervo. São as marcas de produção em escala.
SUBTITULOS_BANIDOS = [
    "o que está em jogo", "o que esta em jogo", "o que vem a seguir",
    "o que esperar dos próximos", "o que esperar dos proximos",
    "conclusão", "conclusao", "considerações finais", "consideracoes finais",
    "o que realmente está em jogo", "em resumo", "para concluir",
]
TITULOS_BANIDOS = [
    (r"\bparece\b.{0,40}\bmas (é|e)\b", "fórmula 'parece X, mas é Y'"),
    (r"\bo que ningu(é|e)m (te )?conta\b", "promessa de revelação"),
    (r"^(você|voce|será que|sera que)\b", "pergunta ao leitor no título"),
    (r"\be ningu(é|e)m (percebeu|viu|notou)\b", "promessa de revelação"),
    (r"\bvai (mudar|surpreender) tudo\b", "sensacionalismo"),
]
FECHOS_BANIDOS = [
    (r"\b(resta|só resta|so resta) (saber|aguardar|esperar)\b", "fecho especulativo"),
    (r"\bo tempo (dirá|dira|vai dizer)\b", "fecho especulativo"),
    (r"\buma coisa é certa\b", "fecho de efeito"),
    (r"\be você, o que (acha|pensa)\b", "pergunta ao leitor no fecho"),
]

CAMPOS_OBRIGATORIOS = ["fato", "fonte_primaria", "data_do_fato",
                       "por_que_agora", "a_quem_afeta"]


def slugificar(t, limite=72):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^\w\s-]", "", t.lower())
    t = re.sub(r"[\s_-]+", "-", t).strip("-")
    if len(t) > limite:
        t = t[:limite].rsplit("-", 1)[0]
    return t.strip("-")


# ── Etapa 1: a pauta é válida? ───────────────────────────────────────────
def conferir_pauta(p):
    """Sem fato verificável, não há matéria. Esta é a regra que substitui
    todas as outras."""
    faltando = [c for c in CAMPOS_OBRIGATORIOS if not str(p.get(c, "")).strip()]
    if faltando:
        return [f"campo obrigatório vazio: {', '.join(faltando)}"]

    erros = []
    fonte = p["fonte_primaria"]
    if not re.match(r"^https?://", fonte):
        erros.append("fonte_primaria precisa ser uma URL")

    if p.get("formato") not in FORMATOS:
        erros.append(f"formato inválido; use um de {list(FORMATOS)}")
    if p.get("editoria") not in EDITORIAS:
        erros.append(f"editoria inválida; use uma de {EDITORIAS}")

    try:
        d = datetime.strptime(p["data_do_fato"], "%Y-%m-%d").date()
        atraso = (date.today() - d).days
        if atraso > 30:
            erros.append(f"o fato tem {atraso} dias; não é notícia")
        if atraso < 0:
            erros.append("data_do_fato no futuro")
    except ValueError:
        erros.append("data_do_fato deve ser AAAA-MM-DD")

    # um "fato" que é assunto costuma vir sem verbo e sem número
    fato = p["fato"]
    if len(fato.split()) < 5:
        erros.append("o campo fato está vago demais para gerar matéria")
    return erros


# ── Etapa 2: redigir ─────────────────────────────────────────────────────
def instrucao(p):
    mn, mx = FORMATOS[p["formato"]]
    return f"""Você redige para o Duna Press, jornal digital em português do Brasil.

FATO QUE ORIGINA A MATÉRIA
{p['fato']}

Fonte primária: {p['fonte_primaria']}
Data do fato: {p['data_do_fato']}
Por que agora: {p['por_que_agora']}
A quem afeta: {p['a_quem_afeta']}
Contexto adicional: {p.get('contexto', '(nenhum)')}

FORMATO: {p['formato']} — entre {mn} e {mx} palavras.

REGRAS DE ESCRITA, TODAS OBRIGATÓRIAS

1. Escreva a partir do fato acima. Não invente dados, declarações, nomes,
   números ou fontes que não estejam no material fornecido. Se faltar
   informação para sustentar uma afirmação, omita a afirmação.
2. O título diz o que aconteceu. Não use a fórmula "parece X mas é Y", não
   faça pergunta, não prometa revelação.
3. Não use estes subtítulos: "O que está em jogo", "O que vem a seguir",
   "O que esperar dos próximos meses", "Conclusão", "Considerações finais".
   Use subtítulo apenas se o texto realmente mudar de assunto — e escreva
   um subtítulo específico daquele texto.
4. Termine no último fato. Sem parágrafo de arremate, sem projeção de
   futuro, sem pergunta ao leitor.
5. Todo número vem com fonte e período.
6. Nenhum link comercial, de afiliado ou de pagamento.
7. Português do Brasil, frase direta, sem jargão de marketing.

Responda SOMENTE com JSON válido, sem cercas de código:
{{"titulo": "...", "subtitulo": "...", "descricao": "resumo em até 200 caracteres", "corpo": "texto em Markdown", "tags": ["...", "..."]}}"""


def redigir(p):
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        raise SystemExit("ANTHROPIC_API_KEY não definida")
    corpo = json.dumps({
        "model": MODELO, "max_tokens": 4000,
        "messages": [{"role": "user", "content": instrucao(p)}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=corpo,
        headers={"content-type": "application/json", "x-api-key": chave,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=180) as r:
        dados = json.loads(r.read())
    texto = "".join(b.get("text", "") for b in dados.get("content", [])
                    if b.get("type") == "text")
    texto = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    return json.loads(texto)


# ── Etapa 3: o texto passa na conferência de forma? ──────────────────────
def conferir_texto(a, p):
    erros = []
    titulo = a.get("titulo", "")
    corpo = a.get("corpo", "")

    if not titulo or not corpo:
        return ["resposta sem título ou sem corpo"]

    for rx, motivo in TITULOS_BANIDOS:
        if re.search(rx, titulo, re.I):
            erros.append(f"título: {motivo}")

    mn, mx = FORMATOS[p["formato"]]
    n = len(corpo.split())
    if not (mn * 0.8 <= n <= mx * 1.2):
        erros.append(f"extensão {n} palavras, fora da faixa {mn}–{mx}")

    for h in re.findall(r"^#{2,4}\s+(.+)$", corpo, re.M):
        alvo = unicodedata.normalize("NFKD", h.lower()).encode("ascii", "ignore").decode()
        for banido in SUBTITULOS_BANIDOS:
            b = unicodedata.normalize("NFKD", banido).encode("ascii", "ignore").decode()
            if b in alvo:
                erros.append(f"subtítulo banido: “{h.strip()}”")

    fecho = " ".join(corpo.strip().split("\n\n")[-1].split()[-40:])
    for rx, motivo in FECHOS_BANIDOS:
        if re.search(rx, fecho, re.I):
            erros.append(f"fecho: {motivo}")

    if re.search(r"\[\s*\]\(|[?&](ref|aff)=|nubank\.com\.br/pagar|hotmart", corpo, re.I):
        erros.append("link comercial no corpo")

    return erros


# ── Etapa 4: Pull Request ────────────────────────────────────────────────
def montar_md(a, p):
    hoje = date.today()
    tags = a.get("tags", [])[:8]
    linhas = [
        "---",
        f'title: "{a["titulo"].replace(chr(34), chr(39))}"',
        f'subtitle: "{a.get("subtitulo", "").replace(chr(34), chr(39))}"',
        f'description: "{a.get("descricao", "").replace(chr(34), chr(39))}"',
        f"date: {hoje.isoformat()}",
        "status: publish",
        f'author: "{p.get("autor", "Redação Duna Press")}"',
        f'categories: "{p["editoria"]}"',
        f'formato: {p["formato"]}',
        "proveniencia: ia-assistido",
        f'revisor: "{p.get("revisor", "Paulo Fernando de Barros")}"',
        f'fonte_primaria: "{p["fonte_primaria"]}"',
        f'data_do_fato: {p["data_do_fato"]}',
    ]
    if tags:
        linhas.append("tags:")
        linhas += [f"  - {t}" for t in tags]
    linhas += ["---", "", a["corpo"].strip(), ""]
    return "\n".join(linhas)


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=RAIZ, check=check,
                          capture_output=True, text=True).stdout.strip()


def publicados_hoje():
    hoje = date.today().isoformat()
    pasta = os.path.join(RAIZ, "artigos")
    n = 0
    for raiz, _, arquivos in os.walk(pasta):
        n += sum(1 for f in arquivos if f.startswith(hoje))
    return n


def abrir_pr(caminho_md, a, p, ensaio=False):
    hoje = date.today()
    ramo = f'pauta/{hoje.isoformat()}-{slugificar(a["titulo"], 40)}'
    destino = os.path.join(RAIZ, "artigos", p["editoria"],
                           f'{hoje.isoformat()}-{slugificar(a["titulo"])}.md')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(caminho_md)

    if ensaio:
        print(f"\n[ensaio] gravaria em {os.path.relpath(destino, RAIZ)}")
        return None

    git("checkout", "-b", ramo)
    git("add", destino)
    git("commit", "-m", f'pauta: {a["titulo"][:64]}')
    git("push", "origin", ramo)

    repo = os.environ.get("GITHUB_REPO", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not (repo and token):
        print(f"Ramo {ramo} enviado. Abra o PR à mão (faltou GITHUB_REPO/TOKEN).")
        return ramo

    corpo_pr = f"""**Fato:** {p['fato']}

**Fonte primária:** {p['fonte_primaria']}
**Data do fato:** {p['data_do_fato']}
**Por que agora:** {p['por_que_agora']}
**A quem afeta:** {p['a_quem_afeta']}

Formato: `{p['formato']}` · {len(a['corpo'].split())} palavras
Proveniência: redigido com IA, aguardando revisão

---
### Antes de aprovar, confira
- [ ] O fato confere com a fonte primária
- [ ] Nenhum dado, nome ou declaração foi inventado
- [ ] Os números têm fonte e período
- [ ] O texto não repete estrutura de outra matéria da semana
"""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/pulls",
        data=json.dumps({"title": a["titulo"][:80], "head": ramo,
                         "base": "main", "body": corpo_pr}).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        pr = json.loads(r.read())
    print(f"PR aberto: {pr.get('html_url')}")
    return ramo


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ensaio = "--ensaio" in sys.argv
    with open(sys.argv[1], encoding="utf-8") as fh:
        pautas = json.load(fh)
    if isinstance(pautas, dict):
        pautas = [pautas]

    ja = publicados_hoje()
    if ja >= TETO_DIARIO:
        raise SystemExit(f"Teto diário atingido ({ja}/{TETO_DIARIO}). "
                         "Acima disso a revisão deixa de ser revisão.")

    aprovadas = recusadas = 0
    for p in pautas:
        if ja + aprovadas >= TETO_DIARIO:
            print(f"\n— teto de {TETO_DIARIO}/dia atingido; as demais ficam para amanhã")
            break

        print(f"\n▸ {p.get('fato', '(sem fato)')[:72]}")

        erros = conferir_pauta(p)
        if erros:
            recusadas += 1
            print("  recusada na pauta:")
            for x in erros:
                print(f"    · {x}")
            continue

        try:
            a = redigir(p)
        except Exception as exc:
            recusadas += 1
            print(f"  falhou ao redigir: {exc}")
            continue

        erros = conferir_texto(a, p)
        if erros:
            recusadas += 1
            print(f"  recusada na forma — “{a.get('titulo', '')[:52]}”")
            for x in erros:
                print(f"    · {x}")
            continue

        abrir_pr(montar_md(a, p), a, p, ensaio)
        aprovadas += 1
        print(f"  ok — “{a['titulo'][:60]}” ({len(a['corpo'].split())} palavras)")

    print(f"\n{aprovadas} para revisão · {recusadas} recusadas · "
          f"{ja + aprovadas}/{TETO_DIARIO} hoje")
    if recusadas and not aprovadas:
        print("Nenhuma pauta passou. Dia sem publicação é normal em jornal.")


if __name__ == "__main__":
    main()
