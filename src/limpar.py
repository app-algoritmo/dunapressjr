#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — separação entre redação e comercial.

Remove do corpo editorial tudo que é monetização pessoal ou afiliação:
  · links de pagamento (Nubank /pagar, PIX autorizado, PicPay, Mercado Pago)
  · parâmetros de afiliado (?ref=, ?aff=, utm_source=afiliado)
  · âncoras vazias [](http...) — link sem texto visível
  · plataformas de infoproduto (Hotmart, Monetizze, Eduzz, Kiwify, Braip)
  · blocos de apelo comercial ("clique e comece já", "compre agora")

Não toca em links editoriais legítimos. Quando o link tem parâmetro de
afiliado mas aponta para destino de valor jornalístico, preserva o link e
retira só o parâmetro.

Grava um diário de tudo que mudou, para conferência linha a linha.
"""
import os, re, glob, json, shutil
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados")

# ── Padrões ──────────────────────────────────────────────────────────────
PAGAMENTO = re.compile(
    r"https?://[^\s)\]]{0,80}nubank\.com\.br/pagar/[^\s)\]]{0,120}"
    r"|https?://[^\s)\]]{0,80}picpay\.me/[^\s)\]]{0,120}"
    r"|https?://[^\s)\]]{0,80}mercadopago\.com[^\s)\]]{0,60}/pag[^\s)\]]{0,120}"
    r"|https?://[^\s)\]]{0,140}pix[-_ ]?autorizado[^\s)\]]{0,80}"
    r"|https?://[^\s)\]]{0,140}/pix/[^\s)\]]{0,80}", re.I)

INFOPRODUTO = re.compile(
    r"https?://[^\s)\]]{0,80}(?:hotmart|monetizze|eduzz|kiwify|braip|bit\.ly)"
    r"[^\s)\]]{0,120}", re.I)

APELO = re.compile(
    r"^[^\n]{0,120}(?:clique e comece j[áa]|compre agora|garanta o seu"
    r"|assine j[áa]|aproveite a promo[çc][ãa]o|clique aqui e adquira)[^\n]{0,160}$",
    re.I | re.M)

AFILIADO_PARAM = re.compile(r"[?&](ref|aff|afiliado|referral)=[^\s&)\]\"']*", re.I)


DATA_URI = re.compile(r"data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=]{200,}", re.I)


def limpar_texto(corpo):
    """Devolve (corpo_limpo, contagem_por_tipo)."""
    c = Counter()
    original = corpo

    # Imagem embutida em base64 não é conteúdo: infla a página e trava
    # qualquer varredura. Sai antes de tudo.
    n = len(DATA_URI.findall(corpo))
    if n:
        c["data_uri"] += n
        corpo = DATA_URI.sub("", corpo)

    # 1. Âncora vazia com destino de pagamento/afiliado → remove por inteiro.
    def _ancora_vazia(m):
        alvo = m.group(1)
        c["ancora_vazia"] += 1
        return ""
    corpo = re.sub(r"\[\s*\]\(((?:https?:|javascript:)[^)]*)\)", _ancora_vazia, corpo)

    # 2. Link markdown [texto](url) cujo destino é pagamento ou infoproduto
    #    → mantém o texto, descarta o link.
    def _link_monetizado(m):
        texto, url = m.group(1), m.group(2)
        if PAGAMENTO.search(url):
            c["pagamento"] += 1
            return ""                       # texto e link somem juntos
        if INFOPRODUTO.search(url):
            c["infoproduto"] += 1
            return texto
        if AFILIADO_PARAM.search(url):
            c["param_afiliado"] += 1
            return f"[{texto}]({AFILIADO_PARAM.sub('', url)})"
        return m.group(0)
    corpo = re.sub(r"\[([^\]]*)\]\((https?://[^)\s]+)[^)]*\)", _link_monetizado, corpo)

    # 3. URLs soltas (sem markdown) de pagamento ou infoproduto.
    for rotulo, rx in (("pagamento", PAGAMENTO), ("infoproduto", INFOPRODUTO),
                       ("param_afiliado", AFILIADO_PARAM)):
        n = len(rx.findall(corpo))
        if n:                       # += 0 criaria a chave e falsearia a contagem
            c[rotulo] += n
            corpo = rx.sub("", corpo)

    # 5. Linhas de apelo comercial.
    def _apelo(m):
        c["apelo"] += 1
        return ""
    corpo = APELO.sub(_apelo, corpo)

    # 6. Higiene: linhas que sobraram vazias ou com pontuação órfã.
    corpo = re.sub(r"^[ \t*_\-–—.,;:!]{0,6}$", "", corpo, flags=re.M)
    corpo = re.sub(r"\n{3,}", "\n\n", corpo)
    corpo = re.sub(r"[ \t]+\n", "\n", corpo)

    return (corpo.rstrip() + "\n") if corpo != original else original, c


def executar():
    arquivos = sorted(glob.glob(os.path.join(RAIZ, "artigos/*/*.md")))
    total = Counter()
    alterados, diario = 0, []

    for caminho in arquivos:
        with open(caminho, encoding="utf-8", errors="replace") as fh:
            bruto = fh.read()
        if bruto.startswith("---"):
            f = bruto.find("\n---", 3)
            cab, corpo = (bruto[:f + 4], bruto[f + 4:]) if f > 0 else ("", bruto)
        else:
            cab, corpo = "", bruto

        novo, c = limpar_texto(corpo)
        if not c:
            continue
        alterados += 1
        total.update(c)
        rel = os.path.relpath(caminho, RAIZ)
        diario.append({"arquivo": rel, "remocoes": dict(c),
                       "palavras_antes": len(corpo.split()),
                       "palavras_depois": len(novo.split())})
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(cab + novo)

    os.makedirs(DADOS, exist_ok=True)
    with open(f"{DADOS}/limpeza.json", "w", encoding="utf-8") as fh:
        json.dump(diario, fh, ensure_ascii=False, indent=1)

    perdidas = sum(d["palavras_antes"] - d["palavras_depois"] for d in diario)
    print("DUNA PRESS — SEPARAÇÃO REDAÇÃO / COMERCIAL")
    print("=" * 58)
    print(f"Artigos examinados ....... {len(arquivos):>6}")
    print(f"Artigos alterados ........ {alterados:>6}")
    print()
    print("REMOÇÕES POR TIPO")
    print("-" * 58)
    rotulos = {
        "param_afiliado": "parâmetro ?ref= / ?aff= retirado da URL",
        "ancora_vazia":   "âncora vazia [](http…) removida",
        "pagamento":      "link de pagamento pessoal removido",
        "apelo":          "linha de apelo comercial removida",
        "infoproduto":    "link de infoproduto removido",
        "data_uri":       "imagem base64 embutida removida",
    }
    for k, v in total.most_common():
        print(f"  {v:>6}  {rotulos.get(k, k)}")
    print()
    print(f"Palavras retiradas do acervo: {perdidas:,}".replace(",", "."))
    print(f"Diário completo: {DADOS}/limpeza.json")


if __name__ == "__main__":
    executar()
