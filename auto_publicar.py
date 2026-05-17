import anthropic, requests, json, re, os, sys, time, uuid, unicodedata
from datetime import datetime

ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_KEY", "")
GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
UNSPLASH_KEY   = os.environ.get("UNSPLASH_KEY", "")
RESEND_KEY     = os.environ.get("RESEND_KEY", "")
SUPABASE_URL   = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY   = os.environ.get("SUPABASE_KEY", "")
GITHUB_REPO    = "app-algoritmo/dunapressjr"
SITE_BASE_URL  = "https://dunapress.org"
FROM_EMAIL     = "Duna Press <newsletter@dunapress.org>"

ORCAMENTO_MENSAL_USD   = 2.00
PRECO_INPUT_POR_TOKEN  = 1.50 / 1_000_000
PRECO_OUTPUT_POR_TOKEN = 7.50 / 1_000_000
FICHEIRO_GASTOS = "/tmp/dunapress_gastos.json"
AUTOR = "Duna Press Redacao"

# ── AGENDA: horas UTC 10-15 (igual ao publicar.yml) ──
AGENDA_ROTATIVA = {
    0: [
        {"slug": "health",               "nome": "Saude",                   "hora": "10"},
        {"slug": "well-being",           "nome": "Bem-Estar",               "hora": "11"},
        {"slug": "fitness",              "nome": "Fitness",                 "hora": "12"},
        {"slug": "personal-development", "nome": "Desenvolvimento Pessoal", "hora": "13"},
        {"slug": "motivational",         "nome": "Motivacional",            "hora": "14"},
        {"slug": "beauty",               "nome": "Beleza",                  "hora": "15"},
    ],
    1: [
        {"slug": "technology",            "nome": "Tecnologia",        "hora": "10"},
        {"slug": "science",               "nome": "Ciencia",           "hora": "11"},
        {"slug": "innovation",            "nome": "Inovacao",          "hora": "12"},
        {"slug": "future-and-innovation", "nome": "Futuro e Inovacao", "hora": "13"},
        {"slug": "astronomy",             "nome": "Astronomia",        "hora": "14"},
        {"slug": "e-auto",                "nome": "E-Auto",            "hora": "15"},
    ],
    2: [
        {"slug": "global-economy",       "nome": "Economia Global",     "hora": "10"},
        {"slug": "business-and-economy", "nome": "Negocios e Economia", "hora": "11"},
        {"slug": "finances",             "nome": "Financas",            "hora": "12"},
        {"slug": "financial-education",  "nome": "Educacao Financeira", "hora": "13"},
        {"slug": "entrepreneurship",     "nome": "Empreendedorismo",    "hora": "14"},
        {"slug": "courses-and-careers",  "nome": "Cursos e Carreiras",  "hora": "15"},
    ],
    3: [
        {"slug": "geopolitics",           "nome": "Geopolitica",              "hora": "10"},
        {"slug": "politics-and-society",  "nome": "Politica e Sociedade",     "hora": "11"},
        {"slug": "international-affairs", "nome": "Assuntos Internacionais",  "hora": "12"},
        {"slug": "military",              "nome": "Militar",                  "hora": "13"},
        {"slug": "world-affairs",         "nome": "Assuntos Mundiais",        "hora": "14"},
        {"slug": "global-affairs",        "nome": "Assuntos Globais",         "hora": "15"},
    ],
    4: [
        {"slug": "culture-and-history", "nome": "Cultura e Historia", "hora": "10"},
        {"slug": "history",             "nome": "Historia",           "hora": "11"},
        {"slug": "literature",          "nome": "Literatura",         "hora": "12"},
        {"slug": "music",               "nome": "Musica",             "hora": "13"},
        {"slug": "philosophy",          "nome": "Filosofia",          "hora": "14"},
        {"slug": "education",           "nome": "Educacao",           "hora": "15"},
    ],
    5: [
        {"slug": "soccer",        "nome": "Futebol",         "hora": "10"},
        {"slug": "sports",        "nome": "Desporto",        "hora": "11"},
        {"slug": "tennis",        "nome": "Tenis",           "hora": "12"},
        {"slug": "formula-1",     "nome": "Formula 1",       "hora": "13"},
        {"slug": "cycling",       "nome": "Ciclismo",        "hora": "14"},
        {"slug": "olympic-games", "nome": "Jogos Olimpicos", "hora": "15"},
    ],
    6: [
        {"slug": "environment",            "nome": "Meio Ambiente",         "hora": "10"},
        {"slug": "agriculture",            "nome": "Agricultura",           "hora": "11"},
        {"slug": "tourism-and-gastronomy", "nome": "Turismo e Gastronomia", "hora": "12"},
        {"slug": "fashion",                "nome": "Moda",                  "hora": "13"},
        {"slug": "lifestyle",              "nome": "Estilo de Vida",        "hora": "14"},
        {"slug": "pets",                   "nome": "Animais de Estimacao",  "hora": "15"},
    ],
}

TODOS_SLUGS = [cat["slug"] for agenda in AGENDA_ROTATIVA.values() for cat in agenda]
NOMES_DIAS  = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]


# ──────────────────────────────────────────────────────────────
# NEWSLETTER
# ──────────────────────────────────────────────────────────────
def buscar_subscribers():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("  Supabase nao configurado — newsletter ignorada.")
        return []
    try:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/newsletter",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
            params={"status": "eq.active", "select": "email"},
            timeout=10
        )
        if res.status_code == 200:
            emails = [row["email"] for row in res.json() if row.get("email")]
            print(f"  Subscribers activos: {len(emails)}")
            return emails
        else:
            print(f"  Supabase erro {res.status_code}: {res.text[:100]}")
            return []
    except Exception as e:
        print(f"  Supabase erro: {e}")
        return []


def montar_email_html(artigo, caminho, imagem=None, email=""):
    titulo    = artigo.get("titulo", "Novo artigo")
    resumo    = artigo.get("resumo", "")
    categoria = artigo.get("categoria", "")
    artigo_url = f"{SITE_BASE_URL}/artigo.html?file=/{caminho}"

    img_html = ""
    if imagem and imagem.get("url"):
        img_html = f"""
        <div style="margin:0 0 24px 0;">
            <img src="{imagem['url']}" alt="{titulo}"
                 style="width:100%;max-width:600px;height:220px;object-fit:cover;
                        border-radius:8px;display:block;">
            <p style="font-size:11px;color:#999;margin:6px 0 0 0;text-align:right;">
                Foto: <a href="{imagem.get('autor_url','#')}" style="color:#999;"
                         target="_blank">{imagem.get('autor','Unsplash')}</a> / Unsplash
            </p>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:'Georgia',serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;width:100%;">
        <tr>
          <td style="background:#0f0f0f;padding:24px 36px;text-align:center;">
            <p style="margin:0;font-family:'Georgia',serif;font-size:22px;
                      font-weight:700;color:#ffffff;letter-spacing:1px;">Duna Press</p>
            <p style="margin:4px 0 0 0;font-size:11px;color:#888;
                      letter-spacing:3px;text-transform:uppercase;">
              {categoria.replace('-',' ').title()}</p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 36px 28px 36px;">
            {img_html}
            <h1 style="font-family:'Georgia',serif;font-size:24px;
                       color:#1a1a1a;margin:0 0 16px 0;line-height:1.3;">{titulo}</h1>
            <p style="font-size:15px;color:#444;line-height:1.7;margin:0 0 28px 0;">{resumo}</p>
            <a href="{artigo_url}"
               style="display:inline-block;background:#c94d3a;color:#ffffff;
                      text-decoration:none;padding:13px 28px;border-radius:6px;
                      font-size:14px;font-weight:700;letter-spacing:0.5px;">
              Ler artigo completo →</a>
          </td>
        </tr>
        <tr>
          <td style="background:#f9f9f9;padding:20px 36px;border-top:1px solid #eee;">
            <p style="margin:0;font-size:11px;color:#aaa;text-align:center;line-height:1.6;">
              Recebeste este email porque subscreveste a newsletter da Duna Press.<br>
              <a href="https://dunapress.org" style="color:#aaa;">dunapress.org</a>
              &nbsp;&middot;&nbsp;
              <a href="https://dunapress.org/unsubscribe.html?email=" + email + "" style="color:#aaa;">Cancelar subscrição</a>
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return html, artigo_url


def enviar_newsletter(artigo, caminho, imagem=None):
    if not RESEND_KEY:
        print("  RESEND_KEY nao configurada — newsletter ignorada.")
        return
    subscribers = buscar_subscribers()
    if not subscribers:
        print("  Sem subscribers activos — newsletter ignorada.")
        return
    titulo  = artigo.get("titulo", "Novo artigo na Duna Press")
    enviados, erros = 0, 0
    for email in subscribers:
        html, _ = montar_email_html(artigo, caminho, imagem, email=email)
        try:
            res = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from":    FROM_EMAIL,
                    "to":      [email],
                    "subject": f"📰 {titulo}",
                    "html":    html,
                },
                timeout=15
            )
            if res.status_code in (200, 201):
                enviados += 1
            else:
                print(f"  Resend erro {email}: {res.status_code} — {res.text[:80]}")
                erros += 1
        except Exception as e:
            print(f"  Resend excepcao {email}: {e}")
            erros += 1
        time.sleep(0.2)
    print(f"  Newsletter: {enviados} enviados, {erros} erros.")


# ──────────────────────────────────────────────────────────────
# UNSPLASH
# ──────────────────────────────────────────────────────────────
def buscar_imagem_unsplash(titulo, categoria_slug):
    if not UNSPLASH_KEY:
        print("  UNSPLASH_KEY nao configurada — sem imagem.")
        return None
    headers  = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    palavras = " ".join(titulo.split()[:5])
    fallback = categoria_slug.replace("-", " ")
    for query in [palavras, fallback]:
        try:
            res = requests.get(
                "https://api.unsplash.com/photos/random",
                headers=headers,
                params={"query": query, "orientation": "landscape", "content_filter": "high"},
                timeout=10
            )
            if res.status_code == 200:
                data      = res.json()
                url       = data["urls"]["regular"]
                autor     = data["user"]["name"]
                autor_url = data["user"]["links"]["html"]
                print(f"  Imagem Unsplash: {url[:60]}... (foto de {autor})")
                return {"url": url, "autor": autor, "autor_url": autor_url}
            elif res.status_code == 403:
                print("  Unsplash: chave invalida ou limite atingido.")
                return None
        except Exception as e:
            print(f"  Unsplash erro ({query!r}): {e}")
    print("  Unsplash: sem resultado.")
    return None


# ──────────────────────────────────────────────────────────────
# UTILITÁRIOS (iguais ao original)
# ──────────────────────────────────────────────────────────────
def hora_alvo_do_schedule():
    schedule = os.environ.get("SCHEDULE", "").strip()
    if not schedule:
        return None
    parts = schedule.split()
    if len(parts) >= 2:
        try:
            return str(int(parts[1])).zfill(2)
        except (ValueError, IndexError):
            pass
    return None

def slugify(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    return texto.strip("-")[:60]

def carregar_gastos():
    try:
        with open(FICHEIRO_GASTOS) as f:
            dados = json.load(f)
        if dados.get("mes") != datetime.now().strftime("%Y-%m"):
            raise ValueError
        return dados
    except:
        return {"mes": datetime.now().strftime("%Y-%m"), "total_usd": 0.0, "artigos": 0}

def guardar_gastos(dados):
    with open(FICHEIRO_GASTOS, "w") as f:
        json.dump(dados, f, indent=2)

def registar_custo(input_tokens, output_tokens):
    custo = (input_tokens * PRECO_INPUT_POR_TOKEN) + (output_tokens * PRECO_OUTPUT_POR_TOKEN)
    dados = carregar_gastos()
    dados["total_usd"] = round(dados["total_usd"] + custo, 6)
    dados["artigos"]   = dados.get("artigos", 0) + 1
    guardar_gastos(dados)
    return custo

def verificar_orcamento():
    dados = carregar_gastos()
    gasto = dados["total_usd"]
    print(f"  Gasto: ${gasto:.4f} / ${ORCAMENTO_MENSAL_USD:.2f}")
    if gasto >= ORCAMENTO_MENSAL_USD:
        print("  ORCAMENTO ESGOTADO")
        return False
    return True

def montar_prompt(categoria):
    hoje = datetime.now().strftime("%d/%m/%Y")
    slug = categoria["slug"]
    nome = categoria["nome"]
    return (
        "Jornalista senior da Duna Press. "
        f"Artigo original sobre {nome} ({hoje}). "
        "Tom analitico, relevante. "
        f"Autor: {AUTOR}. "
        "Retorne APENAS JSON valido sem markdown: "
        "{" + f'"titulo":"titulo aqui","subtitulo":"lead aqui",'
        f'"autor":"{AUTOR}","categoria":"{slug}",'
        '"tempo_leitura":7,'
        f'"tags":["{slug}","analise","duna press"],'
        '"resumo":"resumo aqui",'
        '"conteudo":"artigo markdown min 650 palavras"' + "}"
    )

def gerar_artigo_batch(categoria):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    prompt = montar_prompt(categoria)
    req_id = f"dp-{categoria['slug']}-{uuid.uuid4().hex[:8]}"
    print(f"  Submetendo Batch para {categoria['nome']}...")
    batch = client.messages.batches.create(requests=[{
        "custom_id": req_id,
        "params": {
            "model": "claude-sonnet-4-6",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        }
    }])
    print(f"  Batch id: {batch.id}. Aguardando...")
    for tentativa in range(60):
        time.sleep(10)
        status = client.messages.batches.retrieve(batch.id)
        if status.processing_status == "ended":
            break
        if tentativa % 6 == 5:
            print(f"  ... {(tentativa+1)*10}s")
    resultado = None
    for item in client.messages.batches.results(batch.id):
        if item.custom_id == req_id and item.result.type == "succeeded":
            resultado = item.result.message
            break
    if not resultado:
        raise RuntimeError("Batch sem resultado")
    custo = registar_custo(resultado.usage.input_tokens, resultado.usage.output_tokens)
    print(f"  Custo: ${custo:.5f}")
    texto = resultado.content[0].text.strip()
    texto = re.sub(r"^```json\s*", "", texto)
    texto = re.sub(r"\s*```$",     "", texto)
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        def extrair(campo):
            m = re.search(rf'"{campo}"\s*:\s*"((?:[^"\\]|\\.)*)"', texto, re.DOTALL)
            return m.group(1) if m else ""
        def extrair_lista(campo):
            m = re.search(rf'"{campo}"\s*:\s*\[([^\]]*)\]', texto)
            if not m: return []
            return [t.strip().strip('"') for t in m.group(1).split(',')]
        conteudo_m = re.search(r'"conteudo"\s*:\s*"(.*?)(?:"\s*\})', texto, re.DOTALL)
        conteudo   = conteudo_m.group(1) if conteudo_m else ""
        conteudo   = conteudo.replace('\\"', '"').replace('\\n', '\n')
        return {
            "titulo":        extrair("titulo"),
            "subtitulo":     extrair("subtitulo"),
            "autor":         extrair("autor"),
            "categoria":     extrair("categoria"),
            "resumo":        extrair("resumo"),
            "tags":          extrair_lista("tags"),
            "tempo_leitura": 7,
            "conteudo":      conteudo,
        }

def salvar_local(artigo, categoria_slug, imagem=None):
    agora    = datetime.now()
    data_str = agora.strftime("%Y-%m-%d")
    slug     = slugify(artigo["titulo"])
    pasta    = categoria_slug
    os.makedirs(f"artigos/{pasta}", exist_ok=True)
    caminho = f"artigos/{pasta}/{data_str}-{slug}.md"
    tags    = artigo.get("tags", [])
    tags_fm = "\n".join([f"  - {t}" for t in tags])
    imagem_fm = ""
    if imagem and imagem.get("url"):
        imagem_fm = (
            f'\nfeaturedImage: "{imagem["url"]}"'
            f'\nphotoAuthor: "{imagem["autor"]}"'
            f'\nphotoAuthorUrl: "{imagem["autor_url"]}"'
            f'\nphotoSource: "Unsplash"'
        )
    md = (
        f'---\n'
        f'title: "{artigo["titulo"].replace(chr(34), chr(39))}"\n'
        f'subtitle: "{artigo.get("subtitulo","").replace(chr(34), chr(39))}"\n'
        f'date: {data_str}\n'
        f'status: publish\n'
        f'author: {artigo["autor"]}\n'
        f'categories:\n'
        f'  - {pasta}\n'
        f'description: "{artigo.get("resumo","").replace(chr(34), chr(39))}"'
        f'{imagem_fm}\n'
        f'tags:\n'
        f'{tags_fm}\n'
        f'---\n\n'
        f'{artigo["conteudo"]}'
    )
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"  Ficheiro: {caminho}")
    return slug, caminho

def actualizar_search_index_local(artigo, caminho, categoria_slug, imagem=None):
    index_path = "search-index.json"
    try:
        with open(index_path, encoding="utf-8") as f:
            current = json.load(f)
    except:
        current = []
    entry = {
        "title":    artigo["titulo"],
        "path":     caminho,
        "category": categoria_slug,
        "date":     datetime.now().strftime("%Y-%m-%d"),
        "status":   "publish",
    }
    if imagem and imagem.get("url"):
        entry["featuredImage"] = imagem["url"]
    current.insert(0, entry)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    print("  search-index.json actualizado")

def publicar(categoria):
    print(f"\nPublicando: {categoria['nome']} ({categoria['slug']})")
    if not verificar_orcamento():
        return False
    try:
        artigo = gerar_artigo_batch(categoria)
        imagem = buscar_imagem_unsplash(artigo.get("titulo", ""), categoria["slug"])
        slug, caminho = salvar_local(artigo, categoria["slug"], imagem)
        actualizar_search_index_local(artigo, caminho, categoria["slug"], imagem)
        enviar_newsletter(artigo, caminho, imagem)   # ← NOVO
        print(f"  OK: {artigo['titulo']}")
        return True
    except Exception as e:
        print(f"  ERRO: {e}")
        return False

def publicar_agendado():
    agora       = datetime.now()
    hora_atual  = agora.strftime("%H:%M")
    dia_semana  = agora.weekday()
    agenda_hoje = AGENDA_ROTATIVA[dia_semana]
    hora_alvo   = hora_alvo_do_schedule()
    fonte       = f"schedule={os.environ.get('SCHEDULE','').strip()!r}"
    if hora_alvo is None:
        agora_min = agora.hour * 60 + agora.minute
        melhor, melhor_diff = None, 999
        for cat in agenda_hoje:
            h = int(cat["hora"])
            slot_min = h * 60
            diff = agora_min - slot_min
            if diff < -30:
                diff += 24 * 60
            if 0 <= diff <= 30 and diff < melhor_diff:
                melhor_diff = diff
                melhor = cat["hora"]
        hora_alvo = melhor
        fonte     = f"clock={hora_atual} (janela 30 min)"
    print(f"[{hora_atual} UTC] {NOMES_DIAS[dia_semana]} | hora-alvo: {hora_alvo or 'nenhuma'} | {fonte}")
    print(f"Agenda: {[c['slug'] for c in agenda_hoje]}")
    if hora_alvo is None:
        print(f"  Nenhum slot activo para {hora_atual}.")
        return
    for cat in agenda_hoje:
        if cat["hora"] == hora_alvo:
            publicar(cat)
            return
    print(f"  Slot {hora_alvo} nao encontrado na agenda de hoje.")

def mostrar_gastos():
    dados = carregar_gastos()
    print(f"\n{dados['mes']} | {dados.get('artigos',0)} artigos | "
          f"${dados['total_usd']:.4f} de ${ORCAMENTO_MENSAL_USD:.2f}\n")

def mostrar_agenda():
    print("\n=== AGENDA SEMANAL (UTC) ===")
    for dia, cats in AGENDA_ROTATIVA.items():
        print(f"\n{NOMES_DIAS[dia]}:")
        for c in cats:
            print(f"  {c['hora']}:00 UTC -> {c['slug']} ({c['nome']})")

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "agendado"
    if modo == "todos":
        dia     = datetime.now().weekday()
        sucesso = 0
        for cat in AGENDA_ROTATIVA[dia]:
            if publicar(cat):
                sucesso += 1
            time.sleep(3)
        dados = carregar_gastos()
        print(f"\nTotal: {sucesso}/6 | ${dados['total_usd']:.4f} de ${ORCAMENTO_MENSAL_USD:.2f}")
    elif modo == "gastos":
        mostrar_gastos()
    elif modo == "agenda":
        mostrar_agenda()
    elif modo in TODOS_SLUGS:
        for cat in [c for agenda in AGENDA_ROTATIVA.values() for c in agenda]:
            if cat["slug"] == modo:
                publicar(cat)
                break
    else:
        publicar_agendado()
