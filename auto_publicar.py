#!/usr/bin/env python3
import anthropic, requests, json, base64, re, os, sys, time, uuid
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
    print(f"  💰 Gasto: ${gasto:.4f} / ${ORCAMENTO_MENSAL_USD:.2f}")
    if gasto >= ORCAMENTO_MENSAL_USD:
        print(f"  🚫 ORCAMENTO ESGOTADO")
        return False
    return True

AGENDA = [
    {"slug": "tecnologia",  "nome": "Tecnologia",   "hora": "06:00"},
    {"slug": "economia",    "nome": "Economia",     "hora": "09:00"},
    {"slug": "ciencia",     "nome": "Ciencia",      "hora": "12:00"},
    {"slug": "geopolitica", "nome": "Geopolitica",  "hora": "15:00"},
    {"slug": "saude",       "nome": "Saude",        "hora": "18:00"},
    {"slug": "ambiente",    "nome": "Meio Ambiente", "hora": "21:00"},
]
AUTOR = "Duna Press Redacao"

def montar_prompt(categoria):
    hoje = datetime.now().strftime("%d/%m/%Y")
    return (f"Jornalista senior da Duna Press. Artigo original sobre {categoria['nome']} ({hoje}). "
            f"Tom analitico, relevante, sem sensacionalismo. Autor: \"{AUTOR}\". "
            f"Retorne APENAS JSON valido (sem markdown): "
            f"{{\"titulo\":\"max 85 chars\",\"subtitulo\":\"lead max 150 chars\","
            f"\"autor\":\"{AUTOR}\",\"categoria\":\"{categoria['slug']}\","
            f"\"tempo_leitura\":7,\"tags\":[\"{categoria['slug']}\",\"analise\",\"duna press\"],"
            f"\"resumo\":\"2 linhas para meta description\","
            f"\"conteudo\":\"Markdown com ## subtitulos, min 650 palavras\"}}")

def gerar_artigo_batch(categoria):
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    prompt = montar_prompt(categoria)
    req_id = f"dp-{categoria['slug']}-{uuid.uuid4().hex[:8]}"
    print(f"  → Submetendo Batch para '{categoria['nome']}'...")
    batch = client.messages.batches.create(requests=[{
        "custom_id": req_id,
        "params": {"model": "claude-sonnet-4-6", "max_tokens": 1800,
                   "messages": [{"role": "user", "content": prompt}]}
    }])
    print(f"  → Batch id: {batch.id}. Aguardando...")
    for tentativa in range(60):
        time.sleep(10)
        status = client.messages.batches.retrieve(batch.id)
        if status.processing_status == "ended":
            break
        if tentativa % 6 == 5:
            print(f"     ... {(tentativa+1)*10}s")
    resultado = None
    for item in client.messages.batches.results(batch.id):
        if item.custom_id == req_id and item.result.type == "succeeded":
            resultado = item.result.message
            break
    if not resultado:
        raise RuntimeError("Batch sem resultado")
    custo = registar_custo(resultado.usage.input_tokens, resultado.usage.output_tokens)
    print(f"  💵 Custo: ${custo:.5f} (in:{resultado.usage.input_tokens} out:{resultado.usage.output_tokens})")
    texto = resultado.content[0].text.strip()
    texto = re.sub(r"^```json\s*", "", texto)
    texto = re.sub(r"\s*```$", "", texto)
    return json.loads(texto)

def salvar_github(artigo, categoria_slug):
    agora = datetime.now()
    slug = re.sub(r"[^a-z0-9]+", "-", artigo["titulo"].lower())[:70].strip("-")
    caminho = f"artigos/{categoria_slug}/{slug}.xml"
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<artigo>
  <titulo><![CDATA[{artigo['titulo']}]]></titulo>
  <subtitulo><![CDATA[{artigo['subtitulo']}]]></subtitulo>
  <autor>{artigo['autor']}</autor>
  <categoria>{categoria_slug}</categoria>
  <data>{agora.strftime('%Y-%m-%dT%H:%M:%S')}</data>
  <tempo_leitura>{artigo.get('tempo_leitura', 7)}</tempo_leitura>
  <tags>{','.join(artigo.get('tags', []))}</tags>
  <resumo><![CDATA[{artigo['resumo']}]]></resumo>
  <conteudo><![CDATA[{artigo['conteudo']}]]></conteudo>
</artigo>"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{caminho}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    payload = {"message": f"auto: {artigo['titulo'][:60]}", "content": base64.b64encode(xml.encode("utf-8")).decode()}
    print(f"  → GitHub: {caminho}")
    r = requests.put(url, json=payload, headers=headers, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ⚠️  GitHub erro {r.status_code}: {r.text[:200]}")
    return slug

def inserir_supabase(artigo, slug, categoria_slug):
    url = f"{SUPABASE_URL}/rest/v1/artigos"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
               "Content-Type": "application/json", "Prefer": "return=minimal"}
    payload = {"slug": slug, "titulo": artigo["titulo"], "subtitulo": artigo["subtitulo"],
               "autor": artigo["autor"], "categoria_slug": categoria_slug,
               "tempo_leitura": artigo.get("tempo_leitura", 7), "tags": artigo.get("tags", []),
               "resumo": artigo["resumo"], "conteudo": artigo["conteudo"],
               "publicado": True, "visualizacoes": 0, "criado_em": datetime.now().isoformat()}
    print(f"  → Supabase: inserindo...")
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ⚠️  Supabase erro {r.status_code}: {r.text[:200]}")

def publicar(categoria):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Publicando: {categoria['nome']}")
    if not verificar_orcamento():
        return False
    try:
        artigo = gerar_artigo_batch(categoria)
        slug = salvar_github(artigo, categoria["slug"])
        inserir_supabase(artigo, slug, categoria["sl
