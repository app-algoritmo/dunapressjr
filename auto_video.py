#!/usr/bin/env python3
"""
auto_video.py - Geração automática de vídeos para o canal YouTube do Duna Press
"""

import os
import sys
import json
import requests
import tempfile
import shutil
from datetime import date

import anthropic
import moviepy.video.io.ImageSequenceClip as ImageSequenceClip
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image
import numpy as np

# ─── Configurações ────────────────────────────────────────────────────────────

YOUTUBE_CHANNEL_ID = "UCiXYKVWDEwjULv6QpPj2dZA"  # @borealtimesPT

CATEGORIAS = [
    "tecnologia", "gastronomia", "cultura", "ciência",
    "economia", "saúde", "viagens", "esporte", "arte",
    "meio ambiente", "política internacional", "inovação"
]

VIDEO_WIDTH  = 1920
VIDEO_HEIGHT = 1080
FPS          = 24
NUM_IMAGENS  = 15

# ─── Categoria do dia ─────────────────────────────────────────────────────────

def get_categoria():
    dia = date.today().timetuple().tm_yday
    return CATEGORIAS[dia % len(CATEGORIAS)]

# ─── Gerar script com Claude ──────────────────────────────────────────────────

def gerar_script(categoria):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_KEY"])

    prompt = f"""Cria um script de narração em português do Brasil para um vídeo jornalístico de 3-5 minutos sobre {categoria}.

O script deve:
- Ter entre 550-700 palavras (para ~3-4 minutos de narração)
- Tom jornalístico, informativo e envolvente
- Começar com uma abertura forte que prenda a atenção
- Cobrir aspectos relevantes e actuais do tema
- Terminar com uma reflexão ou conclusão impactante
- Ser fluido e natural para ser narrado em voz off
- NÃO incluir indicações de cena, didascálias ou marcações técnicas
- Apenas o texto puro da narração

Tema: {categoria.upper()}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()

# ─── Gerar título e descrição ─────────────────────────────────────────────────

def gerar_metadados(script, categoria):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_KEY"])

    prompt = f"""Com base neste script de vídeo sobre {categoria}, gera:
1. Um título para YouTube (máx. 60 caracteres, jornalístico e chamativo)
2. Uma descrição para YouTube (2-3 parágrafos, inclui hashtags relevantes no final)

Responde APENAS em JSON válido, sem markdown:
{{"titulo": "...", "descricao": "..."}}

Script:
{script[:500]}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text.strip())

# ─── Gerar áudio com ElevenLabs ───────────────────────────────────────────────

def gerar_audio(script, output_path):
    api_key  = os.environ["ELEVENLABS_API_KEY"]
    voice_id = os.environ["ELEVENLABS_VOICE_ID"]

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    data = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"  Áudio gerado: {output_path}")

# ─── Buscar imagens no Unsplash ───────────────────────────────────────────────

def buscar_imagens(categoria, n=NUM_IMAGENS):
    access_key = os.environ["UNSPLASH_KEY"]

    # Query principal + query secundária para variedade
    urls = []
    metade = n // 2

    for query in [categoria, f"{categoria} brasil"]:
        params = {
            "query": query,
            "count": metade,
            "orientation": "landscape",
            "content_filter": "high",
            "order_by": "relevant",
            "client_id": access_key
        }
        response = requests.get("https://api.unsplash.com/photos/random", params=params)
        response.raise_for_status()
        urls += [foto["urls"]["full"] for foto in response.json()]

    return urls[:n]

# ─── Baixar e redimensionar imagens ──────────────────────────────────────────

def baixar_imagens(urls, pasta):
    caminhos = []
    for i, url in enumerate(urls):
        path = os.path.join(pasta, f"img_{i:03d}.jpg")
        r = requests.get(url, timeout=60)
        r.raise_for_status()

        # Redimensionar para 1920x1080 com crop central
        img = Image.open(__import__("io").BytesIO(r.content)).convert("RGB")
        img_ratio   = img.width / img.height
        target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT

        if img_ratio > target_ratio:
            new_h = VIDEO_HEIGHT
            new_w = int(new_h * img_ratio)
        else:
            new_w = VIDEO_WIDTH
            new_h = int(new_w / img_ratio)

        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - VIDEO_WIDTH)  // 2
        top  = (new_h - VIDEO_HEIGHT) // 2
        img  = img.crop((left, top, left + VIDEO_WIDTH, top + VIDEO_HEIGHT))
        img.save(path, "JPEG", quality=95)

        caminhos.append(path)
        print(f"  Imagem {i+1}/{len(urls)} — {img.size}")
    return caminhos

# ─── Montar vídeo com moviepy ─────────────────────────────────────────────────

def montar_video(imagens_paths, audio_path, output_path):
    audio         = AudioFileClip(audio_path)
    duracao_total = audio.duration
    n_imgs        = len(imagens_paths)
    duracao_img   = duracao_total / n_imgs

    print(f"  Duração: {duracao_total:.1f}s | {n_imgs} imagens | {duracao_img:.1f}s/img")

    clips = []
    for path in imagens_paths:
        clip = ImageClip(path).set_duration(duracao_img)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)

    video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=os.path.join(os.path.dirname(output_path), "temp_audio.m4a"),
        remove_temp=True,
        verbose=False,
        logger=None
    )

    print(f"  Vídeo montado: {output_path}")

# ─── Upload para YouTube ──────────────────────────────────────────────────────

def upload_youtube(video_path, titulo, descricao):
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token"
    )

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": titulo,
            "description": descricao,
            "tags": ["Duna Press", "Boreal Times", "borealtimesPT", "jornalismo", "noticias", "brasil"],
            "categoryId": "25"  # News & Politics
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 5
    )

    request  = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload: {int(status.progress() * 100)}%")

    video_id = response["id"]
    url      = f"https://www.youtube.com/watch?v={video_id}"
    print(f"  Publicado: {url}")
    return video_id, url

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    categoria = get_categoria()
    print(f"\n🎬 Duna Press Auto-Vídeo — @borealtimesPT")
    print(f"   Categoria: {categoria}")

    tmp = tempfile.mkdtemp()

    try:
        print("\n📝 Gerando script...")
        script = gerar_script(categoria)
        print(f"   {len(script.split())} palavras")

        print("\n🏷️  Gerando metadados...")
        meta      = gerar_metadados(script, categoria)
        titulo    = meta["titulo"]
        descricao = meta["descricao"]
        print(f"   Título: {titulo}")

        print("\n🎙️  Gerando áudio (ElevenLabs)...")
        audio_path = os.path.join(tmp, "narration.mp3")
        gerar_audio(script, audio_path)

        print("\n🖼️  Buscando imagens (Unsplash)...")
        urls    = buscar_imagens(categoria)
        imagens = baixar_imagens(urls, tmp)

        print("\n🎞️  Montando vídeo (moviepy)...")
        video_path = os.path.join(tmp, "video.mp4")
        montar_video(imagens, audio_path, video_path)

        print("\n📤 Fazendo upload para YouTube...")
        video_id, url = upload_youtube(video_path, titulo, descricao)

        print(f"\n✅ OK: {titulo}")
        print(f"   {url}")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
