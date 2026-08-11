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
    DP_TETO_AUTO        matérias publicadas por execução (padrão 2)
    DP_TETO_TENTATIVAS  redações tentadas por seção (padrão 4) — é isto
                        que limita o gasto, porque recusa também custa
    DP_TETO_MENSAL      teto de gasto em dólares (padrão 5.00)
    DP_MODELO           modelo de redação
    DP_MODELO_VERIF     modelo de verificação (mais barato de propósito)
"""
import os, re, sys, json, html, time, hashlib, subprocess
import unicodedata, urllib.request, urllib.error, urllib.parse
from datetime import date, datetime, timedelta, timezone
from xml.etree import ElementTree

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Redigir exige julgamento de linguagem; conferir afirmação contra fonte é
# leitura comparada. Usar o mesmo modelo nas duas etapas dobrava o custo
# sem ganho proporcional de rigor.
MODELO_REDACAO = os.environ.get("DP_MODELO", "claude-sonnet-4-6")
MODELO_VERIFICACAO = os.environ.get("DP_MODELO_VERIF", "claude-haiku-4-5-20251001")

TETO = int(os.environ.get("DP_TETO_AUTO", "2"))

# Cada tentativa custa, aprovada ou não. Sem este limite, uma sequência de
# recusas consome o orçamento do mês sem publicar nada.
TETO_TENTATIVAS = int(os.environ.get("DP_TETO_TENTATIVAS", "3"))

# Teto de gasto mensal, em dólares. O script estima o custo de cada chamada
# e para quando chega no limite — melhor um dia sem publicação que uma
# fatura inesperada. O acumulado fica em dados/custo-api.json.
TETO_MENSAL = float(os.environ.get("DP_TETO_MENSAL", "5.00"))

# Preço por milhão de tokens (entrada, saída). Valores de referência para
# estimativa: o número exato vem da fatura, este serve para frear a tempo.
PRECOS = {
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5-20251001": (0.80, 4.00),
}
JANELA_DEDUPE = 10            # dias para trás na checagem de assunto repetido
# Fração de sequências de 8 palavras em comum com a fonte. Texto curto que
# repete a fonte é republicação evidente; texto longo compartilha mais por
# aritmética, não por cópia. O teto acompanha isso.
# Fração de afirmações sem base que ainda permite publicar. Acima disso, o
# texto tem problema de fundo. Abaixo, é imprecisão pontual — e reprovar a
# matéria inteira por uma linha em vinte é desperdício.
FRACAO_NAO_SUSTENTADA = 0.15

# Abaixo disso, o Unsplash não tem o assunto e devolveu o que sobrou.
# "measles vaccination São Paulo" trouxe 2 resultados — e a primeira foto
# era de hipnose.
# Piso de resultados. Busca com pouco retorno significa que o Unsplash não
# tem o assunto e devolveu o que sobrou — foi assim que uma matéria sobre
# sarampo quase saiu ilustrada com hipnose, a partir de 2 resultados.
MINIMO_RESULTADOS = 60

SOBREPOSICAO_CURTA = 0.10     # até 300 palavras
SOBREPOSICAO_LONGA = 0.18     # acima disso

# Vários portais públicos recusam requisição sem cabeçalho de navegador.
# Mantemos a identificação do bot no final, para quem inspecionar o log
# saber quem somos e onde está a política editorial.
CABECALHO = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 "
                   "Safari/537.36 DunaPressBot/1.0 "
                   "(+https://dunapress.org/principios/)"),
    "Accept": "application/rss+xml, application/xml, text/xml, text/html, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

# ── Imagem de abertura ───────────────────────────────────────────────────
# A busca vai em cascata, do específico ao genérico:
#   1. tags da própria matéria, traduzidas   → foto daquele assunto
#   2. termo da editoria                      → foto do tema
#   3. nada                                   → publica sem imagem
#
# Foto genérica que não conversa com o texto é pior que nenhuma: o leitor
# vê a imagem antes do título e ela promete outro assunto.
UNSPLASH_EDITORIA = {
    # Em português, como as tags: a API traduz a consulta com lang=pt.
    "brasil": "cidade brasileira",
    "mundo": "diplomacia internacional",
    "economia": "mercado financeiro",
    "politica": "parlamento governo",
    "ciencia-e-saude": "laboratório pesquisa",
    "tecnologia": "tecnologia computador",
    "cultura": "arte museu",
    "esportes": "estádio atleta",
    "opiniao": "jornal escrita",
}


def termos_de_busca(artigo, editoria):
    """Consultas para a foto de abertura, da mais específica à mais ampla.

    O modelo sugere os termos junto com a matéria, pensando no que ilustra
    a cena. Antes reaproveitávamos as tags do artigo — mas elas existem
    para indexar, e "São Paulo" ou "Anvisa" nomeiam lugar e instituição,
    não imagem. Foi assim que uma matéria sobre sarampo recebeu a foto de
    uma caneta.
    """
    consultas = [t.strip() for t in (artigo.get("imagens") or [])
                 if t and t.strip()][:2]

    if UNSPLASH_EDITORIA.get(editoria):
        consultas.append(UNSPLASH_EDITORIA[editoria])

    return consultas


def buscar_imagem(artigo, editoria):
    """Procura no Unsplash uma foto que tenha relação com a matéria.

    Sem chave, sem resultado suficiente, ou sem foto cuja descrição
    combine com a consulta, devolve nada — e a matéria sai sem imagem,
    que é melhor que sair com imagem errada.
    """
    chave = os.environ.get("UNSPLASH_KEY", "")
    if not chave:
        return None

    for consulta in termos_de_busca(artigo, editoria):
        try:
            endereco = ("https://api.unsplash.com/search/photos"
                        "?query=%s&orientation=landscape&content_filter=high"
                        "&lang=pt&per_page=10" % urllib.parse.quote(consulta))
            req = urllib.request.Request(
                endereco, headers={"Authorization": "Client-ID %s" % chave,
                                   "Accept-Version": "v1"})
            with urllib.request.urlopen(req, timeout=20) as r:
                dados = json.loads(r.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 403:
                print("    Unsplash: chave inválida ou limite atingido")
                return None
            continue
        except Exception:
            continue

        total = dados.get("total", 0)
        resultados = dados.get("results") or []

        # Poucos resultados significam que o Unsplash não tem o assunto e
        # devolveu o que sobrou. Foi assim que 2 fotos viraram hipnose.
        if total < MINIMO_RESULTADOS or not resultados:
            print("      \"%s\" descartada: %d resultados (mínimo %d)"
                  % (consulta[:34], total, MINIMO_RESULTADOS))
            continue

        foto = resultados[0]
        if True:
            return {
                "url": "%s?w=1600&q=75" % foto["urls"]["raw"].split("?")[0],
                "autor": foto["user"]["name"],
                "autor_url": foto["user"]["links"]["html"],
                "consulta": consulta,
                "descricao": (foto.get("alt_description") or "")[:60],
                "total": total,
            }

    return None


# ── Fontes ───────────────────────────────────────────────────────────────
# Princípio: só fonte primária. Nada de veículo comercial — gerar matéria a
# partir da reportagem alheia é apropriar-se da apuração de outra redação,
# e é o padrão que os buscadores tratam como conteúdo em escala.
#
# A diversidade vem do TIPO de instituição, não do número de endereços. Se
# todas forem do Executivo, o jornal reproduz a pauta do governo. Cruzando
# Executivo, Judiciário, reguladores, institutos de pesquisa e organismos
# internacionais, as pautas se contradizem entre si — e é aí que aparece
# o que merece ser apurado.
#
# Feeds saem do ar sem aviso. tools/conferir_fontes.py testa todos de uma
# vez; feed que falha é ignorado e a execução segue com os que responderam.
FONTES = {
    "nacional": {
        "editoria": "brasil",
        "feeds": [
            # Confirmados em 10/08/2026 por tools/conferir_fontes.py.
            # Feeds de órgãos públicos mudam de endereço com frequência;
            # rode a conferência antes de acrescentar qualquer linha aqui.
            ("Agência Brasil", "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml"),
            ("Agência Gov", "https://agenciagov.ebc.com.br/rss.xml"),
            ("Agência FAPESP", "https://agencia.fapesp.br/rss/"),
            ("Fiocruz", "https://portal.fiocruz.br/rss.xml"),
        ],
    },
    "internacional": {
        "editoria": "mundo",
        "feeds": [
            ("OMS", "https://www.who.int/rss-feeds/news-english.xml"),
        ],
    },
}

# Candidatos que falharam no teste de 10/08/2026. Ficam registrados para
# quem for procurar o endereço novo — a instituição continua valendo como
# fonte, só o feed mudou de lugar.
#
#   Agência Senado    devolveu HTML   www12.senado.leg.br/noticias/ultimas/rss
#   Agência Câmara    404             camara.leg.br/rss/noticias
#   STF               404             noticias.stf.jus.br/postsrss
#   STJ               403             stj.jus.br/sites/portalp/RSS/Noticias
#   TSE               404             tse.jus.br/rss/noticias-tse
#   IBGE              403             agenciadenoticias.ibge.gov.br/...
#   Banco Central     400             bcb.gov.br/api/feed/sitebcb/noticias
#   IPEA              sem resposta    ipea.gov.br/portal/...
#   ANVISA            feed vazio      gov.br/anvisa/.../RSS
#   ANEEL             404             gov.br/aneel/.../RSS
#   ONU News          404             news.un.org/pt/feed/...
#   OIT, UNICEF, FMI, Banco Mundial, OCDE, AIE, Nature, Science


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
    req = urllib.request.Request(url, headers=CABECALHO)
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


JANELA_RECENCIA = int(os.environ.get("DP_JANELA_DIAS", "4"))


def recente(item):
    """Fato antigo demais não rende notícia. A janela é maior que a de uma
    agência porque organismos institucionais publicam com menos frequência
    e o fato permanece novo por mais tempo."""
    for formato in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%SZ"):
        try:
            d = datetime.strptime(item["quando"].strip(), formato)
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - d) <= timedelta(days=JANELA_RECENCIA)
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
    """Quantas matérias a publicação automática já pôs no ar hoje.

    Contava todos os arquivos do dia, inclusive os escritos à mão — então
    um dia produtivo do editor bloqueava a automação. O teto existe para
    limitar o que a IA publica, não o jornal.
    """
    hoje = date.today().isoformat()
    n = 0
    base = os.path.join(RAIZ, "artigos")
    for pasta, _, arquivos in os.walk(base):
        for f in arquivos:
            if not f.startswith(hoje) or not f.endswith(".md"):
                continue
            try:
                with open(os.path.join(pasta, f), encoding="utf-8",
                          errors="replace") as fh:
                    cab = fh.read(900)
            except OSError:
                continue
            if re.search(r"^proveniencia:\s*ia-autonomo\s*$", cab, re.M):
                n += 1
    return n


# ── 3. Chamada ao modelo ─────────────────────────────────────────────────
def caminho_custo():
    return os.path.join(RAIZ, "dados", "custo-api.json")


def custo_do_mes():
    """Gasto acumulado no mês corrente. Reinicia sozinho na virada."""
    mes = date.today().strftime("%Y-%m")
    try:
        with open(caminho_custo(), encoding="utf-8") as fh:
            dados = json.load(fh)
        return mes, dados.get(mes, 0.0), dados
    except (OSError, ValueError):
        return mes, 0.0, {}


def registrar_custo(modelo, entrada, saida):
    preco_e, preco_s = PRECOS.get(modelo, (3.00, 15.00))
    valor = (entrada / 1e6) * preco_e + (saida / 1e6) * preco_s
    mes, acumulado, dados = custo_do_mes()
    dados[mes] = round(acumulado + valor, 4)
    os.makedirs(os.path.dirname(caminho_custo()), exist_ok=True)
    with open(caminho_custo(), "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=1)
    return valor, dados[mes]


def chamar(prompt, max_tokens=4000, modelo=None):
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        raise SystemExit("ANTHROPIC_API_KEY não definida")
    modelo = modelo or MODELO_REDACAO

    _, gasto, _ = custo_do_mes()
    if gasto >= TETO_MENSAL:
        raise SystemExit(
            "Teto mensal de US$ %.2f atingido (US$ %.2f gastos).\n"
            "A publicação para aqui. Para elevar o teto, ajuste\n"
            "DP_TETO_MENSAL no workflow." % (TETO_MENSAL, gasto))

    corpo = json.dumps({"model": modelo, "max_tokens": max_tokens,
                        "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=corpo,
        headers={"content-type": "application/json", "x-api-key": chave,
                 "anthropic-version": "2023-06-01"})
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                dados = json.loads(r.read())
            uso = dados.get("usage", {})
            registrar_custo(modelo, uso.get("input_tokens", 0),
                            uso.get("output_tokens", 0))
            return "".join(b.get("text", "") for b in dados.get("content", [])
                           if b.get("type") == "text")
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 529) and tentativa < 2:
                time.sleep(8 * (tentativa + 1))
                continue
            raise
    return ""


def json_de(texto):
    """O modelo às vezes devolve JSON com quebra de linha literal dentro de
    uma string, o que é inválido. Duas matérias por rodada se perdiam aqui —
    falha técnica, não decisão editorial. Tentamos o parse direto e, se
    falhar, reparamos os defeitos conhecidos antes de desistir."""
    t = re.sub(r"^```(?:json)?|```$", "", texto.strip(), flags=re.M).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass

    # Quebra de linha crua dentro de string: escapar sem tocar na estrutura.
    reparado, dentro, escape = [], False, False
    for c in t:
        if escape:
            reparado.append(c); escape = False; continue
        if c == "\\":
            reparado.append(c); escape = True; continue
        if c == '"':
            dentro = not dentro
        if dentro and c == "\n":
            reparado.append("\\n"); continue
        if dentro and c == "\t":
            reparado.append("\\t"); continue
        reparado.append(c)
    try:
        return json.loads("".join(reparado))
    except json.JSONDecodeError:
        pass

    # Último recurso: extrair campo a campo. Preferimos uma matéria com um
    # campo faltando a perder o trabalho inteiro por uma vírgula.
    def campo(nome):
        m = re.search(r'"%s"\s*:\s*"((?:[^"\\]|\\.)*)"' % nome, t, re.S)
        if not m:
            return ""
        return (m.group(1).replace("\\n", "\n").replace('\\"', '"')
                .replace("\\\\", "\\"))
    corpo = campo("corpo")
    if not corpo:
        raise ValueError("resposta do modelo não é JSON e não tem campo corpo")
    tags = re.search(r'"tags"\s*:\s*\[(.*?)\]', t, re.S)
    afirma = re.search(r'"afirmacoes"\s*:\s*\[(.*?)\]', t, re.S)
    imgs = re.search(r'"imagens"\s*:\s*\[(.*?)\]', t, re.S)
    lista = lambda m: re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1)) if m else []
    return {"titulo": campo("titulo"), "subtitulo": campo("subtitulo"),
            "descricao": campo("descricao"), "corpo": corpo,
            "tags": lista(tags), "afirmacoes": lista(afirma),
            "imagens": lista(imgs)}


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
{editoria}.

EXTENSÃO — o mínimo é 220 palavras, sem exceção. Abaixo disso o texto é
recusado e o trabalho se perde.
- fato simples e autocontido (resultado, número divulgado, decisão pontual):
  220 a 350 palavras
- fato com contexto, efeito ou mais de uma parte envolvida:
  350 a 700 palavras

Se o material de origem for curto, não invente para alcançar as 220: use o
contexto que o próprio material fornece — quem divulgou, quando, o que essa
instituição faz, a que se refere o dado. Não acrescente nada de fora.

REGRAS, TODAS OBRIGATÓRIAS
1. Escreva com suas próprias palavras. Não reproduza frases do material de
   origem. Este é um texto novo, não uma reescrita parágrafo a parágrafo.
2. Use apenas fatos que estão no material acima. Não acrescente dados,
   números, nomes, datas ou declarações que não estejam ali. Se algo é
   necessário para o texto e não está no material, omita.
3. O título diz o que aconteceu. Sem a fórmula "parece X mas é Y", sem
   pergunta, sem promessa de revelação.
4. Se o texto mudar de assunto, marque o intertítulo com ## no início da
   linha — nunca com **negrito**, que vira parágrafo e não subtítulo.
   Não use os subtítulos "O que está em jogo", "O que vem a seguir",
   "O que esperar dos próximos meses", "Conclusão", "Considerações finais".
5. Termine no último fato. Sem arremate, sem projeção, sem pergunta ao
   leitor.
6. Todo número vem com a fonte e o período.
7. Nenhum link comercial.
8. Atribua ao órgão de origem quando a informação for declaração dele.
9. Ao reproduzir declaração textual, diga a quem ela foi dada e onde saiu.
   Aspas sem essa indicação parecem apuração própria, e não foram.

IMAGENS
Sugira dois termos de busca para a foto de abertura, em português,
pensando no que ILUSTRA a matéria — não no que a indexa. "criança
recebendo vacina" serve; "São Paulo" ou "Anvisa" não, porque nomeiam
lugar e instituição, não a cena. Dois a quatro substantivos concretos
por termo, do mais específico ao mais amplo.

Responda SOMENTE com JSON válido, sem cercas. Dentro das strings, escreva
quebra de linha como \\n — quebra literal invalida o JSON:
{{"titulo":"...","subtitulo":"...","descricao":"até 200 caracteres","corpo":"markdown","tags":["..."],"imagens":["termo específico","termo mais amplo"],"afirmacoes":["cada afirmação factual do texto, uma por item"]}}"""
    return json_de(chamar(prompt))


def verificar(artigo, corpo_fonte):
    """Confere afirmação por afirmação e decide no código, não no modelo.

    A versão anterior pedia ao modelo um booleano de aprovação junto com a
    lista de problemas. Ele produzia a análise correta — "Afirmação 1:
    SUSTENTADA, Afirmação 2: SUSTENTADA" — e devolvia aprovado: false
    assim mesmo, porque usava o campo de problemas como espaço de anotação.
    Matéria correta reprovada por um campo preenchido errado.

    Agora o modelo só classifica cada afirmação. Contar e decidir é
    trabalho do código, que não se confunde.
    """
    afirmacoes = artigo.get("afirmacoes") or []
    if not afirmacoes:
        return {"aprovado": True, "nao_sustentadas": [],
                "observacao": "sem afirmações declaradas"}

    numeradas = "\n".join("%d. %s" % (i, a)
                          for i, a in enumerate(afirmacoes, 1))

    prompt = """Confira cada afirmação contra o material de origem.

MATERIAL DE ORIGEM
%s

AFIRMAÇÕES
%s

Para cada uma, responda SUSTENTADA ou NAO_SUSTENTADA.

SUSTENTADA quando o material dá base para a afirmação, ainda que com
outras palavras: reformulação, sinônimo, gentílico ("escritor manauara"
sustenta "natural de Manaus"), síntese fiel, conversão de unidade.
Diferença de fraseado não é divergência de fato.

NAO_SUSTENTADA apenas quando o material contradiz a afirmação, ou quando
ela traz número, data, nome próprio ou declaração que não aparece ali.
Detalhe plausível mas ausente também é NAO_SUSTENTADA.

Responda SOMENTE com JSON, um item por afirmação, na mesma ordem:
{"resultados": [{"n": 1, "veredito": "SUSTENTADA", "nota": ""},
                {"n": 2, "veredito": "NAO_SUSTENTADA", "nota": "por quê"}]}""" % (
        corpo_fonte[:6000], numeradas)

    try:
        r = json_de(chamar(prompt, 2000, modelo=MODELO_VERIFICACAO))
    except Exception as exc:
        return {"aprovado": False,
                "nao_sustentadas": ["a verificação falhou: %s" % exc]}

    resultados = r.get("resultados") or []
    if not resultados:
        return {"aprovado": False,
                "nao_sustentadas": ["a verificação não devolveu resultados"]}

    problemas = []
    for item in resultados:
        if str(item.get("veredito", "")).upper().startswith("NAO"):
            n = item.get("n")
            texto = (afirmacoes[n - 1] if isinstance(n, int)
                     and 1 <= n <= len(afirmacoes) else "afirmação %s" % n)
            problemas.append("%s — %s" % (texto[:90],
                                          item.get("nota", "sem base na fonte")))

    fracao = len(problemas) / max(1, len(resultados))

    # Proporcionalidade. Uma objeção em vinte afirmações não invalida a
    # matéria; uma redação corta a linha duvidosa e publica o resto. Acima
    # do limite, o texto tem problema de fundo e não vale corrigir.
    if fracao > FRACAO_NAO_SUSTENTADA:
        return {"aprovado": False, "nao_sustentadas": problemas,
                "observacao": "%.0f%% das afirmações sem base" % (fracao * 100)}

    return {"aprovado": True, "nao_sustentadas": problemas,
            "observacao": ("%d de %d afirmações sem base, dentro do limite"
                           % (len(problemas), len(resultados))
                           if problemas else "todas sustentadas")}


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
    # Um resultado de loteria é uma nota; um julgamento do STF é reportagem.
    # Faixa única forçava o modelo a inflar fato pequeno — que é justamente
    # o vício que a pauta editorial proíbe.
    n = len(corpo.split())
    if not 180 <= n <= 850:
        erros.append("extensão %d palavras, fora da faixa 200–700" % n)
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
def montar_md(a, item, editoria, imagem=None):
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
    if imagem:
        linhas += [
            'featuredImage: "%s"' % imagem["url"],
            'photoAuthor: "%s"' % imagem["autor"].replace('"', "'"),
            'photoAuthorUrl: "%s"' % imagem["autor_url"],
            'photoSource: "Unsplash"',
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
        fh.write("- [ ] `%s` [%s](%s) — %s · fonte: [%s](%s)\n"
                 % (date.today().isoformat(), a["titulo"][:70], url_final,
                    editoria, item["fonte"], item["url"]))
        for r in a.get("_ressalvas", [])[:3]:
            fh.write("      - ressalva: %s\n" % str(r)[:110])


def git(*args):
    return subprocess.run(["git", *args], cwd=RAIZ,
                          capture_output=True, text=True)


def publicar(md, a, item, editoria, ensaio):
    hoje = date.today()
    slug = slugificar(a["titulo"])
    destino = os.path.join(RAIZ, "artigos", editoria,
                           f"{hoje.isoformat()}-{slug}.md")
    if ensaio:
        rascunho = os.path.join(RAIZ, "rascunhos",
                                "%s-%s.md" % (hoje.isoformat(), slug))
        os.makedirs(os.path.dirname(rascunho), exist_ok=True)
        with open(rascunho, "w", encoding="utf-8") as fh:
            fh.write(md)
        print("    [ensaio] em rascunhos/%s-%s.md" % (hoje.isoformat(), slug))
        print("             publicaria em %s" % os.path.relpath(destino, RAIZ))
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
    # Fatos mais recentes primeiro: notícia velha rende matéria pior e
    # aumenta a chance de recusa — que custa igual.
    candidatos.sort(key=lambda i: i.get("quando", ""), reverse=True)
    print("  %d fatos nos feeds · até %d tentativas"
          % (len(candidatos), TETO_TENTATIVAS))

    publicadas = tentativas = 0
    for item in candidatos:
        if publicadas >= restantes:
            break
        if tentativas >= TETO_TENTATIVAS:
            print("\n  teto de %d tentativas atingido nesta seção" % TETO_TENTATIVAS)
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

        tentativas += 1
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
        limite = (SOBREPOSICAO_CURTA if len(a["corpo"].split()) <= 300
                  else SOBREPOSICAO_LONGA)
        if sob > limite:
            print("    recusada: %.0f%% de sobreposição com a fonte, acima do "
                  "limite de %.0f%% — é republicação, não texto próprio"
                  % (sob * 100, limite * 100))
            continue

        v = verificar(a, corpo_fonte)
        if not v.get("aprovado"):
            print("    recusada na verificação de fatos (%s):"
                  % v.get("observacao", ""))
            for x in v.get("nao_sustentadas", [])[:3]:
                print("      · %s" % str(x)[:88])
            continue
        if v.get("nao_sustentadas"):
            # Aprovada com ressalva: fica registrado na fila de revisão.
            print("    ressalva — %s" % v.get("observacao", ""))
            for x in v["nao_sustentadas"][:2]:
                print("      · %s" % str(x)[:88])
            a["_ressalvas"] = v["nao_sustentadas"]

        sugeridos = a.get("imagens") or []
        if sugeridos:
            print("    termos sugeridos: %s" % " · ".join(sugeridos[:2]))
        else:
            print("    o modelo não sugeriu termo de imagem")
        imagem = buscar_imagem(a, config["editoria"])
        if imagem:
            print("    foto: %s · busca \"%s\" (%d resultados)"
                  % (imagem["autor"], imagem["consulta"][:32],
                     imagem.get("total", 0)))
            if imagem.get("descricao"):
                print("          %s" % imagem["descricao"])
        publicar(montar_md(a, item, config["editoria"], imagem), a, item,
                 config["editoria"], ensaio)
        vistos.append(termos(a["titulo"]))
        publicadas += 1
        print("    publicada — %d palavras, %.0f%% de sobreposição (limite %.0f%%)"
              % (len(a["corpo"].split()), sob * 100, limite * 100))

    return publicadas


def main():
    ensaio = "--ensaio" in sys.argv
    so = None
    if "--so" in sys.argv:
        so = sys.argv[sys.argv.index("--so") + 1]

    mes, gasto, _ = custo_do_mes()
    print("Gasto em %s: US$ %.2f de US$ %.2f" % (mes, gasto, TETO_MENSAL))
    if gasto >= TETO_MENSAL:
        print("Teto mensal atingido. Sem publicação até a virada do mês.")
        return

    ja = hoje_publicados()
    if ja >= TETO:
        # Sair com erro marcaria a execução como falha no painel, e um teto
        # atingido não é falha — é o limite funcionando.
        print("Teto de %d publicações automáticas já atingido hoje (%d)."
              % (TETO, ja))
        return

    vistos = publicados_recentes()
    print("Teto: %d por execução, %d tentativas · publicadas hoje: %d · "
          "assuntos recentes na memória: %d"
          % (TETO, TETO_TENTATIVAS, ja, len(vistos)))

    total = 0
    for secao, config in FONTES.items():
        if so and secao != so:
            continue
        total += processar(secao, config, vistos, ensaio, TETO - ja - total)
        if ja + total >= TETO:
            break

    _, gasto_fim, _ = custo_do_mes()
    print("\n%d publicada(s). %d/%d hoje. Gasto no mês: US$ %.2f de US$ %.2f"
          % (total, ja + total, TETO, gasto_fim, TETO_MENSAL))
    if total == 0:
        print("Nada passou nas conferências. Dia sem publicação é normal em jornal.")
    elif not ensaio:
        print("Enfileiradas em editorial/revisao-pendente.md para conferência.")


if __name__ == "__main__":
    main()
