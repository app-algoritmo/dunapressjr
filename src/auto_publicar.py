#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — publicação automática, editorias Brasil e Mundo.

Diferente de src/publicar.py, que abre Pull Request e espera aprovação,
aqui a matéria vai ao ar sozinha. A revisão humana prévia foi substituída
por verificação automática — não por ausência de verificação.

O que roda antes de cada publicação:

  1. a pauta vem de uma fonte real, buscada agora, não inventada no prompt
  2. o assunto não foi publicado nos últimos dias
  3. um segundo passe confere cada afirmação do texto contra a fonte
  4. sobreposição de trecho com a fonte precisa ser baixa — texto próprio,
     não republicação disfarçada
  5. conferência de forma, a mesma de src/publicar.py

Reprovou em qualquer etapa, não publica. Reprovar é o sistema funcionando.

Toda matéria daqui sai marcada como publicada sem revisão humana prévia, e
entra em editorial/revisao-pendente.md para conferência posterior.

    python3 src/auto_publicar.py                  # nacional + internacional
    python3 src/auto_publicar.py --so nacional
    python3 src/auto_publicar.py --ensaio         # não publica, só mostra

Ambiente:
    ANTHROPIC_API_KEY   obrigatória
    DP_TETO_AUTO        matérias por execução (padrão 4)
"""
import os, re, sys, json, html, time, hashlib, subprocess
import unicodedata, urllib.request, urllib.error
from datetime import date, datetime, timedelta, timezone
from xml.etree import ElementTree

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = "claude-sonnet-4-6"
TETO = int(os.environ.get("DP_TETO_AUTO", "4"))
JANELA_DEDUPE = 10            # dias para trás na checagem de assunto repetido
SOBREPOSICAO_MAX = 0.14       # fração de 8-gramas em comum com a fonte

UA = "DunaPressBot/1.0 (+https://dunapress.org/principios/)"

# ── Fontes ───────────────────────────────────────────────────────────────
# Feeds públicos. Servem para descobrir o fato e para verificá-lo depois —
# não para copiar texto. A conferência de originalidade garante isso.
FONTES = {
    "nacional": {
        "editoria": "brasil",
        "feeds": [
            ("Agência Brasil", "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml"),
            ("Agência Senado", "https://www12.senado.leg.br/noticias/ultimas/rss"),
            ("Agência Câmara", "https://www.camara.leg.br/noticias/rss/ultimas"),
            ("IBGE", "https://agenciadenoticias.ibge.gov.br/agencia-noticias/rss.html"),
            ("Banco Central", "https://www.bcb.gov.br/rss/noticias"),
        ],
    },
    "internacional": {
        "editoria": "mundo",
        "feeds": [
            ("UN News", "https://news.un.org/feed/subscribe/en/news/all/rss.xml"),
            ("European Commission", "https://ec.europa.eu/commission/presscorner/api/rss"),
            ("IMF", "https://www.imf.org/en/News/RSS?Language=ENG"),
            ("World Bank", "https://www.worldbank.org/en/news/all?format=rss"),
        ],
    },
}


# ── Utilidades ───────────────────────────────────────────────────────────
def sem_acento(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


# Palavras vazias: presentes em todo título, não distinguem assunto nenhum.
VAZIAS = {"para", "pela", "pelo", "pelas", "pelos", "sobre", "entre", "apos",
          "ante", "desde", "durante", "contra", "como", "mais", "menos",
          "esta", "este", "isso", "aquele", "seus", "suas", "quer", "sera",
          "ainda", "tambem", "depois", "antes", "cada", "onde", "quando",
          "porque", "cento", "anos", "meses", "novo", "nova", "diz", "tem"}


def termos(titulo):
    """Palavras que de fato identificam o assunto de um título."""
    limpo = re.sub(r"[^\w\s]", " ", sem_acento(titulo))
    return {p for p in limpo.split() if len(p) > 3 and p not in VAZIAS}


def slugificar(t, limite=72):
    t = sem_acento(t)
    t = re.sub(r"[^\w\s-]", "", t)
    t = re.sub(r"[\s_-]+", "-", t).strip("-")
    if len(t) > limite:
        t = t[:limite].rsplit("-", 1)[0]
    return t.strip("-")


def buscar(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        bruto = r.read()
    return bruto.decode("utf-8", errors="replace")


def limpar_html(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


# ── 1. Descobrir fatos ───────────────────────────────────────────────────
def ler_feed(nome, url):
    """RSS e Atom, com a biblioteca padrão. Falha de feed não derruba a
    execução: seguimos com os que responderam."""
    itens = []
    try:
        xml = buscar(url)
        raiz = ElementTree.fromstring(xml)
    except Exception as exc:
        print(f"    feed indisponível ({nome}): {type(exc).__name__}")
        return itens

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entradas = raiz.findall(".//item") or raiz.findall(".//atom:entry", ns)
    for e in entradas[:12]:
        def campo(*tags):
            for t in tags:
                achado = e.find(t) if not t.startswith("atom:") else e.find(t, ns)
                if achado is not None:
                    if achado.text:
                        return achado.text.strip()
                    if achado.get("href"):
                        return achado.get("href")
            return ""

        titulo = campo("title", "atom:title")
        link = campo("link", "atom:link")
        resumo = limpar_html(campo("description", "summary", "atom:summary"))
        quando = campo("pubDate", "published", "atom:updated")
        if titulo and link:
            itens.append({"fonte": nome, "titulo": titulo, "url": link,
                          "resumo": resumo[:600], "quando": quando})
    return itens


def recente(item):
    """Fato com mais de dois dias não é notícia para publicação automática."""
    for formato in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%SZ"):
        try:
            d = datetime.strptime(item["quando"].strip(), formato)
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - d) <= timedelta(days=2)
        except (ValueError, AttributeError):
            continue
    return True     # sem data legível, deixa passar e o dedupe resolve


# ── 2. Já publicamos isso? ───────────────────────────────────────────────
def publicados_recentes():
    """Títulos dos últimos dias, normalizados, para não repetir assunto."""
    limite = date.today() - timedelta(days=JANELA_DEDUPE)
    vistos = []
    base = os.path.join(RAIZ, "artigos")
    for pasta, _, arquivos in os.walk(base):
        for nome in arquivos:
            m = re.match(r"^(\d{4}-\d{2}-\d{2})-", nome)
            if not m or date.fromisoformat(m.group(1)) < limite:
                continue
            with open(os.path.join(pasta, nome), encoding="utf-8",
                      errors="replace") as fh:
                cab = fh.read(1200)
            t = re.search(r"^title:\s*(.+)$", cab, re.M)
            if t:
                vistos.append(termos(t.group(1)))
    return vistos


def assunto_repetido(titulo, vistos):
    """Duas manchetes sobre o mesmo fato compartilham os termos que importam,
    mesmo redigidas de forma diferente. Comparamos pela sobreposição relativa
    ao menor dos dois conjuntos: título curto e título longo sobre o mesmo
    assunto continuam batendo."""
    novos = termos(titulo)
    if len(novos) < 2:
        return False
    for antigo in vistos:
        if len(antigo) < 2:
            continue
        comum = novos & antigo
        if len(comum) >= 2 and len(comum) / min(len(novos), len(antigo)) >= 0.45:
            return True
    return False


def hoje_publicados():
    hoje = date.today().isoformat()
    n = 0
    for _, _, arquivos in os.walk(os.path.join(RAIZ, "artigos")):
        n += sum(1 for f in arquivos if f.startswith(hoje))
    return n


# ── 3. Chamada ao modelo ─────────────────────────────────────────────────
def chamar(prompt, max_tokens=4000):
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        raise SystemExit("ANTHROPIC_API_KEY não definida")
    corpo = json.dumps({"model": MODELO, "max_tokens": max_tokens,
                        "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=corpo,
        headers={"content-type": "application/json", "x-api-key": chave,
                 "anthropic-version": "2023-06-01"})
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                dados = json.loads(r.read())
            return "".join(b.get("text", "") for b in dados.get("content", [])
                           if b.get("type") == "text")
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 529) and tentativa < 2:
                time.sleep(8 * (tentativa + 1))
                continue
            raise
    return ""


def json_de(texto):
    t = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    return json.loads(t)


def redigir(item, editoria, corpo_fonte):
    idioma = ("O material de origem está em inglês. Escreva em português do "
              "Brasil." if editoria == "mundo" else "")
    prompt = f"""Você redige para o Duna Press, jornal digital em português do Brasil.

MATERIAL DE ORIGEM ({item['fonte']})
Título: {item['titulo']}
URL: {item['url']}
Conteúdo:
{corpo_fonte[:6000]}

{idioma}

TAREFA
Escreva uma matéria própria a partir dos fatos acima, para a editoria
{editoria}. Entre 350 e 700 palavras.

REGRAS, TODAS OBRIGATÓRIAS
1. Escreva com suas próprias palavras. Não reproduza frases do material de
   origem. Este é um texto novo, não uma reescrita parágrafo a parágrafo.
2. Use apenas fatos que estão no material acima. Não acrescente dados,
   números, nomes, datas ou declarações que não estejam ali. Se algo é
   necessário para o texto e não está no material, omita.
3. O título diz o que aconteceu. Sem a fórmula "parece X mas é Y", sem
   pergunta, sem promessa de revelação.
4. Não use os subtítulos "O que está em jogo", "O que vem a seguir",
   "O que esperar dos próximos meses", "Conclusão", "Considerações finais".
5. Termine no último fato. Sem arremate, sem projeção, sem pergunta ao
   leitor.
6. Todo número vem com a fonte e o período.
7. Nenhum link comercial.
8. Atribua ao órgão de origem quando a informação for declaração dele.

Responda SOMENTE com JSON, sem cercas:
{{"titulo":"...","subtitulo":"...","descricao":"até 200 caracteres","corpo":"markdown","tags":["..."],"afirmacoes":["cada afirmação factual do texto, uma por item"]}}"""
    return json_de(chamar(prompt))


def verificar(artigo, corpo_fonte):
    """Segundo passe: confere afirmação por afirmação contra a fonte. É o
    que substitui o olho do editor na pergunta que mais importa — o texto
    inventou alguma coisa?"""
    prompt = f"""Confira se cada afirmação abaixo é sustentada pelo material de origem.

MATERIAL DE ORIGEM
{corpo_fonte[:6000]}

TEXTO PRODUZIDO
{artigo['corpo'][:5000]}

AFIRMAÇÕES A CONFERIR
{json.dumps(artigo.get('afirmacoes', []), ensure_ascii=False, indent=1)}

Para cada afirmação, diga se o material de origem a sustenta. Seja rigoroso:
número, data, nome ou declaração que não aparece no material NÃO está
sustentado, mesmo que pareça plausível ou seja de conhecimento geral.

Responda SOMENTE com JSON:
{{"aprovado": true/false, "nao_sustentadas": ["afirmação e por quê"], "observacao": "..."}}"""
    try:
        return json_de(chamar(prompt, 2000))
    except Exception as exc:
        return {"aprovado": False, "nao_sustentadas": [f"verificação falhou: {exc}"]}


# ── 4. Originalidade ─────────────────────────────────────────────────────
def sobreposicao(texto, fonte, n=8):
    """Fração de sequências de 8 palavras do texto que aparecem na fonte.
    Alta sobreposição significa republicação com outra roupa — foi isso que
    tirou 8.621 artigos do índice no acervo antigo."""
    def gramas(t):
        p = sem_acento(re.sub(r"[^\w\s]", " ", t)).split()
        return {" ".join(p[i:i + n]) for i in range(max(0, len(p) - n + 1))}
    a, b = gramas(texto), gramas(fonte)
    if not a:
        return 1.0
    return len(a & b) / len(a)


# ── 5. Conferência de forma ──────────────────────────────────────────────
SUBTITULOS_BANIDOS = ["o que esta em jogo", "o que vem a seguir",
                      "o que esperar dos proximos", "conclusao",
                      "consideracoes finais", "em resumo", "para concluir"]
TITULOS_BANIDOS = [
    (r"\bparece\b.{0,40}\bmas (é|e)\b", "fórmula 'parece X, mas é Y'"),
    (r"\bo que ningu(é|e)m (te )?conta\b", "promessa de revelação"),
    (r"^(você|voce|será que|sera que)\b", "pergunta no título"),
]
FECHOS_BANIDOS = [
    (r"\b(resta|só resta|so resta) (saber|aguardar|esperar)\b", "fecho especulativo"),
    (r"\bo tempo (dirá|dira|vai dizer)\b", "fecho especulativo"),
    (r"\buma coisa é certa\b", "fecho de efeito"),
]


def conferir_forma(a):
    erros = []
    titulo, corpo = a.get("titulo", ""), a.get("corpo", "")
    if not titulo or not corpo:
        return ["resposta sem título ou corpo"]
    for rx, motivo in TITULOS_BANIDOS:
        if re.search(rx, titulo, re.I):
            erros.append(f"título: {motivo}")
    n = len(corpo.split())
    if not 300 <= n <= 850:
        erros.append(f"extensão {n} palavras, fora da faixa 350–700")
    for h in re.findall(r"^#{2,4}\s+(.+)$", corpo, re.M):
        for banido in SUBTITULOS_BANIDOS:
            if banido in sem_acento(h):
                erros.append(f"subtítulo banido: “{h.strip()[:44]}”")
    fecho = " ".join(corpo.strip().split()[-40:])
    for rx, motivo in FECHOS_BANIDOS:
        if re.search(rx, fecho, re.I):
            erros.append(f"fecho: {motivo}")
    if re.search(r"\[\s*\]\(|[?&](ref|aff)=|nubank\.com\.br/pagar|hotmart", corpo, re.I):
        erros.append("link comercial no corpo")
    return erros


# ── 6. Gravar e publicar ─────────────────────────────────────────────────
def montar_md(a, item, editoria):
    hoje = date.today()
    linhas = [
        "---",
        f'title: "{a["titulo"].replace(chr(34), chr(39))}"',
        f'subtitle: "{a.get("subtitulo", "").replace(chr(34), chr(39))}"',
        f'description: "{a.get("descricao", "").replace(chr(34), chr(39))}"',
        f"date: {hoje.isoformat()}",
        "status: publish",
        'author: "Redação Duna Press"',
        f'categories: "{editoria}"',
        "formato: nota",
        # Rótulo próprio: não afirma revisão humana que não houve.
        "proveniencia: ia-autonomo",
        "revisao_humana: pendente",
        f'fonte_primaria: "{item["url"]}"',
        f'fonte_nome: "{item["fonte"]}"',
        f"data_do_fato: {hoje.isoformat()}",
    ]
    tags = a.get("tags", [])[:8]
    if tags:
        linhas.append("tags:")
        linhas += [f"  - {t}" for t in tags]
    linhas += ["---", "", a["corpo"].strip(), ""]
    return "\n".join(linhas)


def enfileirar_revisao(a, item, editoria, url_final):
    """Fila de conferência posterior. Publicar sem revisão prévia é uma
    decisão; publicar sem que ninguém nunca olhe é outra."""
    caminho = os.path.join(RAIZ, "editorial", "revisao-pendente.md")
    novo = not os.path.exists(caminho)
    with open(caminho, "a", encoding="utf-8") as fh:
        if novo:
            fh.write("# Revisão pendente\n\n"
                     "Matérias publicadas automaticamente, ainda sem conferência\n"
                     "humana. Ao revisar, troque `revisao_humana: pendente` por\n"
                     "`revisao_humana: <seu nome>` no artigo e risque a linha aqui.\n\n")
        fh.write(f"- [ ] `{date.today().isoformat()}` "
                 f"[{a['titulo'][:70]}]({url_final}) "
                 f"— {editoria} · fonte: [{item['fonte']}]({item['url']})\n")


def git(*args):
    return subprocess.run(["git", *args], cwd=RAIZ,
                          capture_output=True, text=True)


def publicar(md, a, item, editoria, ensaio):
    hoje = date.today()
    slug = slugificar(a["titulo"])
    destino = os.path.join(RAIZ, "artigos", editoria,
                           f"{hoje.isoformat()}-{slug}.md")
    if ensaio:
        print(f"    [ensaio] gravaria {os.path.relpath(destino, RAIZ)}")
        return
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(md)
    url = f"/{hoje.year}/{hoje.month:02d}/{hoje.day:02d}/{slug}/"
    enfileirar_revisao(a, item, editoria, url)
    git("add", destino, os.path.join(RAIZ, "editorial", "revisao-pendente.md"))
    r = git("commit", "-m", f'auto: {a["titulo"][:60]}')
    if r.returncode == 0:
        git("push", "origin", "HEAD")


# ── Execução ─────────────────────────────────────────────────────────────
def processar(secao, config, vistos, ensaio, restantes):
    print(f"\n▸ {secao}")
    candidatos = []
    for nome, url in config["feeds"]:
        candidatos += [i for i in ler_feed(nome, url) if recente(i)]
    print(f"  {len(candidatos)} fatos nos feeds")

    publicadas = 0
    for item in candidatos:
        if publicadas >= restantes:
            break
        if assunto_repetido(item["titulo"], vistos):
            continue

        print(f"\n  · {item['titulo'][:64]}")
        try:
            corpo_fonte = limpar_html(buscar(item["url"]))
        except Exception as exc:
            print(f"    fonte inacessível: {type(exc).__name__}")
            continue
        if len(corpo_fonte.split()) < 120:
            print("    fonte curta demais para sustentar matéria")
            continue

        try:
            a = redigir(item, config["editoria"], corpo_fonte)
        except Exception as exc:
            print(f"    falhou ao redigir: {exc}")
            continue

        erros = conferir_forma(a)
        if erros:
            print(f"    recusada na forma: {erros[0]}")
            continue

        sob = sobreposicao(a["corpo"], corpo_fonte)
        if sob > SOBREPOSICAO_MAX:
            print(f"    recusada: {sob:.0%} de sobreposição com a fonte "
                  "— é republicação, não texto próprio")
            continue

        v = verificar(a, corpo_fonte)
        if not v.get("aprovado"):
            print("    recusada na verificação de fatos:")
            for x in v.get("nao_sustentadas", [])[:3]:
                print(f"      · {str(x)[:88]}")
            continue

        publicar(montar_md(a, item, config["editoria"]), a, item,
                 config["editoria"], ensaio)
        vistos.append(termos(a["titulo"]))
        publicadas += 1
        print(f"    publicada — {len(a['corpo'].split())} palavras, "
              f"{sob:.0%} de sobreposição")

    return publicadas


def main():
    ensaio = "--ensaio" in sys.argv
    so = None
    if "--so" in sys.argv:
        so = sys.argv[sys.argv.index("--so") + 1]

    ja = hoje_publicados()
    if ja >= TETO:
        raise SystemExit(f"Teto de {TETO} por execução já atingido hoje ({ja}).")

    vistos = publicados_recentes()
    print(f"Teto: {TETO} · publicadas hoje: {ja} · "
          f"assuntos recentes na memória: {len(vistos)}")

    total = 0
    for secao, config in FONTES.items():
        if so and secao != so:
            continue
        total += processar(secao, config, vistos, ensaio, TETO - ja - total)
        if ja + total >= TETO:
            break

    print(f"\n{total} publicada(s). {ja + total}/{TETO} hoje.")
    if total == 0:
        print("Nada passou nas conferências. Dia sem publicação é normal em jornal.")
    elif not ensaio:
        print("Enfileiradas em editorial/revisao-pendente.md para conferência.")


if __name__ == "__main__":
    main()
