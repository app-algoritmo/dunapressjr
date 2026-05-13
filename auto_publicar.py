import anthropic, requests, json, re, os, sys, time, uuid, unicodedata
from datetime import datetime

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")
GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO   = "app-algoritmo/dunapressjr"
SUPABASE_URL  = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY  = os.environ.get("SUPABASE_KEY", "")
ORCAMENTO_MENSAL_USD   = 2.00
PRECO_INPUT_POR_TOKEN  = 1.50 / 1_000_000
PRECO_OUTPUT_POR_TOKEN = 7.50 / 1_000_000
FICHEIRO_GASTOS = "/tmp/dunapress_gastos.json"
AUTOR = "Duna Press Redacao"

# ──────────────────────────────────────────────────────────────
# AGENDA ROTATIVA — 7 dias × 6 categorias (a cada 3 horas)
# Slugs = nomes exactos das pastas em artigos/ no GitHub
# 0=Segunda ... 6=Domingo
# ──────────────────────────────────────────────────────────────
AGENDA_ROTATIVA = {
    0: [  # Segunda — Saúde & Bem-Estar
        {"slug": "health",               "nome": "Saúde",                   "hora": "09:00"},
        {"slug": "well-being",           "nome": "Bem-Estar",               "hora": "12:00"},
        {"slug": "fitness",              "nome": "Fitness",                 "hora": "15:00"},
        {"slug": "personal-development", "nome": "Desenvolvimento Pessoal", "hora": "18:00"},
        {"slug": "motivational",         "nome": "Motivacional",            "hora": "21:00"},
        {"slug": "beauty",               "nome": "Beleza",                  "hora": "00:00"},
    ],
    1: [  # Terça — Tecnologia & Ciência
        {"slug": "technology",            "nome": "Tecnologia",          "hora": "09:00"},
        {"slug": "science",               "nome": "Ciência",             "hora": "12:00"},
        {"slug": "innovation",            "nome": "Inovação",            "hora": "15:00"},
        {"slug": "future-and-innovation", "nome": "Futuro e Inovação",   "hora": "18:00"},
        {"slug": "astronomy",             "nome": "Astronomia",          "hora": "21:00"},
        {"slug": "e-auto",                "nome": "E-Auto",              "hora": "00:00"},
    ],
    2: [  # Quarta — Economia & Negócios
        {"slug": "global-economy",       "nome": "Economia Global",       "hora": "09:00"},
        {"slug": "business-and-economy", "nome": "Negócios e Economia",   "hora": "12:00"},
        {"slug": "finances",             "nome": "Finanças",              "hora": "15:00"},
        {"slug": "financial-education",  "nome": "Educação Financeira",   "hora": "18:00"},
        {"slug": "entrepreneurship",     "nome": "Empreendedorismo",      "hora": "21:00"},
        {"slug": "courses-and-careers",  "nome": "Cursos e Carreiras",    "hora": "00:00"},
    ],
    3: [  # Quinta — Política & Mundo
        {"slug": "geopolitics",           "nome": "Geopolítica",              "hora": "09:00"},
        {"slug": "politics-and-society",  "nome": "Política e Sociedade",     "hora": "12:00"},
        {"slug": "international-affairs", "nome": "Assuntos Internacionais",  "hora": "15:00"},
        {"slug": "military",              "nome": "Militar",                  "hora": "18:00"},
        {"slug": "world-affairs",         "nome": "Assuntos Mundiais",        "hora": "21:00"},
        {"slug": "global-affairs",        "nome": "Assuntos Globais",         "hora": "00:00"},
    ],
    4: [  # Sexta — Cultura & Sociedade
        {"slug": "culture-and-history", "nome": "Cultura e História", "hora": "09:00"},
        {"slug": "history",             "nome": "História",           "hora": "12:00"},
        {"slug": "literature",          "nome": "Literatura",         "hora": "15:00"},
        {"slug": "music",               "nome": "Música",             "hora": "18:00"},
        {"slug": "philosophy",          "nome": "Filosofia",          "hora": "21:00"},
        {"slug": "education",           "nome": "Educação",           "hora": "00:00"},
    ],
    5: [  # Sábado — Desporto & Lazer
        {"slug": "soccer",        "nome": "Futebol",         "hora": "09:00"},
        {"slug": "sports",        "nome": "Desporto",        "hora": "12:00"},
        {"slug": "tennis",        "nome": "Ténis",           "hora": "15:00"},
        {"slug": "formula-1",     "nome": "Fórmula 1",       "hora": "18:00"},
        {"slug": "cycling",       "nome": "Ciclismo",        "hora": "21:00"},
        {"slug": "olympic-games", "nome": "Jogos Olímpicos", "hora": "00:00"},
    ],
    6: [  # Domingo — Estilo de Vida & Ambiente
        {"slug": "environment",             "nome": "Meio Ambiente",        "hora": "09:00"},
        {"slug": "agriculture",             "nome": "Agricultura",          "hora": "12:00"},
        {"slug": "tourism-and-gastronomy",  "nome": "Turismo e Gastronomia","hora": "15:00"},
        {"slug": "fashion",                 "nome": "Moda",                 "hora": "18:00"},
        {"slug": "lifestyle",               "nome": "Estilo de Vida",       "hora": "21:00"},
        {"slug": "pets",                    "nome": "Animais de Estimação", "hora": "00:00"},
    ],
}

# Lista plana de todos os slugs válidos (para uso manual via CLI)
TODOS_SLUGS = [cat["slug"] for agenda in AGENDA_ROTATIVA.values() for cat in agenda]


# ──────────────────────────────────────────────────────────────
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

def salvar_local(artigo, categoria_slug):
    agora    = datetime.now()
    data_str = agora.strftime("%Y-%m-%d")
    slug     = slugify(artigo["titulo"])
    pasta    = categoria_slug  # slug = nome exacto da pasta no GitHub

    os.makedirs(f"artigos/{pasta}", exist_ok=True)

    caminho = f"artigos/{pasta}/{data_str}-{slug}.md"
    tags    = artigo.get("tags", [])
    tags_fm = "\n".join([f"  - {t}" for t in tags])

    md = f"""---
title: "{artigo['titulo'].replace('"', "'")}"
subtitle: "{artigo.get('subtitulo','').replace('"', "'")}"
date: {data_str}
status: draft
author: {artigo['autor']}
categories:
  - {pasta}
description: "{artigo.get('resumo','').replace('"', "'")}"
tags:
{tags_fm}
---

{artigo['conteudo']}"""

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"  Ficheiro: {caminho}")
    return slug, caminho

def actualizar_drafts_index_local(artigo, caminho, categoria_slug):
    index_path = "drafts-index.json"
    try:
        with open(index_path, encoding="utf-8") as f:
            current = json.load(f)
    except:
        current = []

    current.insert(0, {
        "title":    artigo["titulo"],
        "path":     caminho,
        "category": categoria_slug,
        "date":     datetime.now().strftime("%Y-%m-%d"),
        "status":   "draft",
    })

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)

    print("  drafts-index.json actualizado")

def publicar(categoria):
    print(f"\nPublicando: {categoria['nome']} ({categoria['slug']})")
    if not verificar_orcamento():
        return False
    try:
        artigo = gerar_artigo_batch(categoria)
        slug, caminho = salvar_local(artigo, categoria["slug"])
        actualizar_drafts_index_local(artigo, caminho, categoria["slug"])
        print(f"  OK: {artigo['titulo']}")
        return True
    except Exception as e:
        print(f"  ERRO: {e}")
        return False

def publicar_agendado():
    agora      = datetime.now()
    hora_atual = agora.strftime("%H:%M")
    dia_semana = agora.weekday()  # 0=Segunda ... 6=Domingo

    nomes_dias  = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
    agenda_hoje = AGENDA_ROTATIVA[dia_semana]
    print(f"[{hora_atual}] {nomes_dias[dia_semana]} — {[c['slug'] for c in agenda_hoje]}")

    # Correspondência exacta primeiro
    for cat in agenda_hoje:
        if cat["hora"] == hora_atual:
            publicar(cat)
            return

    # Fallback: só a hora (absorve ±1 min de latência do runner)
    hora_h = hora_atual[:2]
    for cat in agenda_hoje:
        if cat["hora"][:2] == hora_h:
            publicar(cat)
            return

    print(f"  Nenhuma publicação agendada para {hora_atual}.")

def mostrar_gastos():
    dados = carregar_gastos()
    print(f"\n{dados['mes']} | {dados.get('artigos',0)} artigos | "
          f"${dados['total_usd']:.4f} de ${ORCAMENTO_MENSAL_USD:.2f}\n")

def mostrar_agenda():
    nomes = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
    print("\n=== AGENDA SEMANAL ===")
    for dia, cats in AGENDA_ROTATIVA.items():
        print(f"\n{nomes[dia]}:")
        for c in cats:
            print(f"  {c['hora']} → {c['slug']} ({c['nome']})")

# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "agendado"

    if modo == "todos":
        # Publica as 6 categorias do dia actual
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
        # Força uma categoria específica manualmente
        for cat in [c for agenda in AGENDA_ROTATIVA.values() for c in agenda]:
            if cat["slug"] == modo:
                publicar(cat)
                break

    else:
        publicar_agendado()
