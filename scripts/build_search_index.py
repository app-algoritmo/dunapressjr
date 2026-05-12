import os, json, re

articles = []

for root, dirs, files in os.walk('artigos'):
    for f in sorted(files, reverse=True):
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f).replace('\\', '/')
        cat = root.replace('artigos/', '').replace('artigos', '')
        slug = f.replace('.md', '')
        date = slug[:10] if len(slug) > 10 else ''
        title = slug[11:].replace('-', ' ').title() if len(slug) > 10 else slug
        featured_image = ''
        description = ''
        status = 'publish'
        try:
            with open(path, 'r', encoding='utf-8') as md:
                content = md.read()
            fm = re.match(r'^---\r?\n([\s\S]*?)\r?\n---', content)
            if fm:
                block = fm.group(1)
                t = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', block, re.M)
                if t: title = t.group(1).strip().strip('"\'')
                img = re.search(r'^featuredImage:\s*["\']?(.+?)["\']?\s*$', block, re.M)
                if img: featured_image = img.group(1).strip().strip('"\'')
                desc = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', block, re.M)
                if desc: description = desc.group(1).strip().strip('"\'')
                st = re.search(r'^status:\s*(.+)\s*$', block, re.M)
                if st: status = st.group(1).strip()
        except Exception:
            pass
        if status == 'draft':
            continue
        articles.append({
            'title': title,
            'path': path,
            'category': cat,
            'date': date,
            'featuredImage': featured_image,
            'description': description
        })

with open('search-index.json', 'w', encoding='utf-8') as out:
    json.dump(articles, out, ensure_ascii=False)

print(f"Indexados: {len(articles)} artigos")
