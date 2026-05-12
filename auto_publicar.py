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
AGENDA = [
    {"slug": "tecnologia",  "nome": "Tecnologia",   "hora": "06:00"},
    {"slug": "economia",    "nome": "Economia",     "hora": "09:00"},
    {"slug": "ciencia",     "nome": "Ciencia",      "hora": "12:00"},
    {"slug": "geopolitica", "nome": "Geopolitica",  "hora": "15:00"},
    {"slug": "saude",       "nome": "Saude",        "hora": "18:00"},
    {"slug": "ambiente",    "nome": "Meio Ambiente", "hora": "21:00"},
]

# ──────────────────────────────────────────────────────────────
# FIX: slugify com suporte correto a acentos e caracteres especiais
# unicodedata.normalize('NFD') decompõe é → e + combining accent
# .encode('ascii', 'ignore') descarta o combining accent, mantém a letra base
# Resultado: "Aquíferos" → "aquiferos", "Hídrica" → "hidrica"
# ──────────────────────────────────────────────────────────────
def slugify(texto):
    # Normaliza para NFD: decompõe caracteres acentuados nas suas partes (letra + acento)
    texto = unicodedata.normalize("NFD", texto)
    # Encode ASCII ignorando os combining accents (que não têm representação ASCII)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    # Substitui qualquer sequência de não-alfanuméricos por "-"
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    # Remove hífens no início/fim e limita tamanho
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
    dados["artigos"] = dados.get("artigos", 0) + 1
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
    texto = re.sub(r"\s*```$", "", texto)
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
        conteudo = conteudo_m.group(1) if conteudo_m else ""
        conteudo = conteudo.replace('\\"', '"').replace('\\n', '\n')
        return {
            "titulo": extrair("titulo"),
            "subtitulo": extrair("subtitulo"),
            "autor": extrair("autor"),
            "categoria": extrair("categoria"),
            "resumo": extrair("resumo"),
            "tags": extrair_lista("tags"),
            "tempo_leitura": 7,
            "conteudo": conteudo
        }

CATEGORIA_PASTA = {
    "tecnologia":  "technology",
    "economia":    "global-economy",
    "ciencia":     "science",
    "geopolitica": "geopolitics",
    "saude":       "health",
    "ambiente":    "environment",
}

def salvar_local(artigo, categoria_slug):
    agora = datetime.now()
    data_str = agora.strftime("%Y-%m-%d")

    """
    Escreve o ficheiro .md directamente no sistema de ficheiros local.
    O workflow git (git add / commit / push) trata do upload para o GitHub.
    Evita problemas de permissões com GITHUB_TOKEN via API REST.
    """
    agora = datetime.now()
    data_str = agora.strftime("%Y-%m-%d")
    slug = slugify(artigo["titulo"])
    pasta = CATEGORIA_PASTA.get(categoria_slug, categoria_slug)

    # Garante que a pasta existe
    os.makedirs(f"artigos/{pasta}", exist_ok=True)

    caminho = f"artigos/{pasta}/{data_str}-{slug}.md"
    tags = artigo.get("tags", [])
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

    print(f"  Ficheiro local: {caminho}")
    return slug, caminho

def inserir_supabase(artigo, slug, categoria_slug):
    url = f"{SUPABASE_URL}/rest/v1/artigos"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = {
        "slug": slug,
        "titulo": artigo["titulo"],
        "subtitulo": artigo["subtitulo"],
        "autor": artigo["autor"],
        "categoria_slug": categoria_slug,
        "tempo_leitura": artigo.get("tempo_leitura", 7),
        "tags": artigo.get("tags", []),
        "resumo": artigo["resumo"],
        "conteudo": artigo["conteudo"],
        "publicado": True,
        "visualizacoes": 0,
        "criado_em": datetime.now().isoformat()
    }
    print("  Supabase: inserindo...")
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  Supabase erro {r.status_code}: {r.text[:200]}")

def publicar(categoria):
    print(f"\nPublicando: {categoria['nome']}")
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

def actualizar_drafts_index_local(artigo, caminho, categoria_slug):
    """Actualiza drafts-index.json localmente. O git push trata do resto."""
    index_path = "drafts-index.json"
    try:
        with open(index_path, encoding="utf-8") as f:
            current = json.load(f)
    except:
        current = []

    pasta = CATEGORIA_PASTA.get(categoria_slug, categoria_slug)
    current.insert(0, {
        "title": artigo["titulo"],
        "path": caminho,
        "category": pasta,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "draft"
    })

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)

    print("  drafts-index.json actualizado localmente")

def publicar_todos():
    sucesso = 0
    for cat in AGENDA:
        if publicar(cat):
            sucesso += 1
        time.sleep(3)
    dados = carregar_gastos()
    print(f"\nTotal: {sucesso}/{len(AGENDA)} | ${dados['total_usd']:.4f} de ${ORCAMENTO_MENSAL_USD:.2f}")

def publicar_agendado():
    hora_atual = datetime.now().strftime("%H:%M")
    for cat in AGENDA:
        if cat["hora"] == hora_atual:
            publicar(cat)
            return
    print(f"[{hora_atual}] Nenhuma publicacao agendada.")

def mostrar_gastos():
    dados = carregar_gastos()
    print(f"\n{dados['mes']} | {dados.get('artigos',0)} artigos | ${dados['total_usd']:.4f} de ${ORCAMENTO_MENSAL_USD:.2f}\n")

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "agendado"
    if modo == "todos":
        publicar_todos()
    elif modo == "gastos":
        mostrar_gastos()
    elif modo in ["tecnologia", "economia", "ciencia", "geopolitica", "saude", "ambiente"]:
        for cat in AGENDA:
            if cat["slug"] == modo:
                publicar(cat)
                break
    else:
        publicar_agendado()
