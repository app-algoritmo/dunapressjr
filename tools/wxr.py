#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — extração dos slugs canônicos do export do WordPress.

O acervo em Markdown tem os nomes de arquivo truncados: a conversão
original cortou os slugs em ~60 caracteres. O WXR guarda o slug inteiro em
<wp:post_name>, que é o que as URLs indexadas pelo Google usam.

Lê 275 MB por streaming, item a item, sem carregar o arquivo na memória.
Produz:
  wp-posts.json      todo post publicado: id, slug, data, autor, título
  wp-slugs.json      "AAAA/MM/DD" → [[slug, título]], para casar com o .md
  wp-diagnostico.txt o que existe no WordPress e não existe no acervo
"""
import re, json, os, html
from collections import Counter, defaultdict

WXR = "/mnt/user-data/uploads/dunapressjournalampmagazine_WordPress_2026-08-07.xml"
SAIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados")

CAMPOS = {
    "titulo":  re.compile(r"<title>(.*?)</title>", re.S),
    "link":    re.compile(r"<link>(.*?)</link>", re.S),
    "autor":   re.compile(r"<dc:creator>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</dc:creator>", re.S),
    "post_id": re.compile(r"<wp:post_id>(\d+)</wp:post_id>"),
    "data":    re.compile(r"<wp:post_date>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</wp:post_date>", re.S),
    "slug":    re.compile(r"<wp:post_name>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</wp:post_name>", re.S),
    "status":  re.compile(r"<wp:status>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</wp:status>", re.S),
    "tipo":    re.compile(r"<wp:post_type>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</wp:post_type>", re.S),
}
CATEGORIA = re.compile(r'<category domain="category"[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</category>', re.S)
CONTEUDO = re.compile(r"<content:encoded>", re.S)


def campo(rx, item):
    m = rx.search(item)
    if not m:
        return ""
    return html.unescape(m.group(1).replace("<![CDATA[", "").replace("]]>", "")).strip()


def itens(caminho):
    """Percorre o XML devolvendo um <item> por vez. Guarda apenas o item
    corrente em memória — o arquivo tem 275 MB."""
    dentro, buf = False, []
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        for linha in fh:
            if not dentro:
                i = linha.find("<item>")
                if i == -1:
                    continue
                dentro, buf = True, [linha[i:]]
            else:
                buf.append(linha)
            if "</item>" in buf[-1]:
                item = "".join(buf)
                yield item[:item.rfind("</item>")]
                dentro, buf = False, []


def main():
    posts, por_data = [], defaultdict(list)
    tipos, status_conta = Counter(), Counter()
    total = 0

    for item in itens(WXR):
        total += 1
        tipo = campo(CAMPOS["tipo"], item)
        tipos[tipo] += 1
        if tipo != "post":
            continue
        st = campo(CAMPOS["status"], item)
        status_conta[st] += 1
        if st != "publish":
            continue

        slug = campo(CAMPOS["slug"], item)
        data = campo(CAMPOS["data"], item)[:10]
        if not slug or not re.match(r"^\d{4}-\d{2}-\d{2}$", data):
            continue

        # conteúdo pode ser gigante; guardamos só o tamanho
        corte = item.find("<content:encoded>")
        tam = len(item) - corte if corte != -1 else 0

        p = {
            "id": campo(CAMPOS["post_id"], item),
            "slug": slug,
            "data": data,
            "titulo": campo(CAMPOS["titulo"], item),
            "autor": campo(CAMPOS["autor"], item),
            "categorias": [html.unescape(c.replace("<![CDATA[", "").replace("]]>", "")).strip()
                           for c in CATEGORIA.findall(item)][:4],
            "bytes": tam,
        }
        posts.append(p)
        a, m, d = data.split("-")
        por_data[f"{a}/{m}/{d}"].append([slug, p["titulo"][:90]])

    os.makedirs(SAIDA, exist_ok=True)
    with open(f"{SAIDA}/wp-posts.json", "w", encoding="utf-8") as fh:
        json.dump(posts, fh, ensure_ascii=False, separators=(",", ":"))
    with open(f"{SAIDA}/wp-slugs.json", "w", encoding="utf-8") as fh:
        json.dump(por_data, fh, ensure_ascii=False, separators=(",", ":"))

    anos = Counter(p["data"][:4] for p in posts)
    autores = Counter(p["autor"] for p in posts)

    L = ["DUNA PRESS — EXPORT DO WORDPRESS", "=" * 58, ""]
    L.append(f"Itens no arquivo ......... {total:>7}")
    L.append("")
    L.append("POR TIPO")
    for k, v in tipos.most_common(8):
        L.append(f"  {k or '(vazio)':<24} {v:>7}")
    L.append("")
    L.append("POSTS POR SITUAÇÃO")
    for k, v in status_conta.most_common():
        L.append(f"  {k or '(vazio)':<24} {v:>7}")
    L.append("")
    L.append(f"POSTS PUBLICADOS COM SLUG: {len(posts)}")
    L.append("")
    L.append("POR ANO")
    for a in sorted(anos):
        L.append(f"  {a}  {anos[a]:>6}")
    L.append("")
    L.append("POR AUTOR (top 15)")
    for k, v in autores.most_common(15):
        L.append(f"  {k:<28} {v:>6}")

    rel = "\n".join(L)
    with open(f"{SAIDA}/wp-diagnostico.txt", "w", encoding="utf-8") as fh:
        fh.write(rel)
    print(rel)


if __name__ == "__main__":
    main()
