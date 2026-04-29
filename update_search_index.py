import os, json, re

ARTIGOS_DIR = os.path.expanduser("~/Documents/Projetos/dunapressjr/artigos")
OUTPUT = os.path.expanduser("~/Documents/Projetos/dunapressjr/search-index.json")

def parse_frontmatter(text):
    meta = {"title": "", "date": "", "author": "", "category": ""}
    m = re.match(r'^---\r?\n(.*?)\r?\n---', text, re.DOTALL)
    if m:
        block = m.group(1)
        for key in ["title", "date", "author"]:
            km = re.search(rf'^{key}:\s*["\']?(.*?)["\']?\s*$', block, re.MULTILINE)
            if km:
                meta[key] = km.group(1).strip().strip("'\"")
    return meta

index = []
for cat in os.listdir(ARTIGOS_DIR):
    cat_path = os.path.join(ARTIGOS_DIR, cat)
    if not os.path.isdir(cat_path): continue
    for fname in os.listdir(cat_path):
        if not fname.endswith(".md"): continue
        fpath = os.path.join(cat_path, fname)
        try:
            text = open(fpath, encoding="utf-8").read()
            meta = parse_frontmatter(text)
            title = meta["title"]
            if not title:
                title = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname[:-3]).replace("-", " ").title()
            date = meta["date"]
            if not date:
                dm = re.match(r'^(\d{4}-\d{2}-\d{2})', fname)
                if dm: date = dm.group(1)
            index.append({
                "title": title,
                "date": date,
                "author": meta["author"],
                "category": cat,
                "path": f"artigos/{cat}/{fname}"
            })
        except: pass

index.sort(key=lambda x: x["date"], reverse=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, separators=(',',':'))
print(f"✅ {len(index)} artigos indexados com autor")
