#!/usr/bin/env python3
# converter_2025_en.py - Converte XML WordPress (artigos em inglês de 2025) para Markdown
import xml.etree.ElementTree as ET
import os, re, html
from datetime import datetime
from pathlib import Path
import yaml

# Seu AUTHOR_MAP existente
AUTHOR_MAP = {
    "debarrospaulo": "Paulo Fernando De Barros",
    # ... adicione outros conforme necessário
}

NS = {
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
}

def parse_authors(root):
    """Extrai mapa de autores do XML"""
    authors = {}
    for a in root.findall('.//wp:author', NS):
        login = a.find('wp:author_login', NS)
        name = a.find('wp:author_display_name', NS)
        if login is not None:
            authors[login.text] = name.text if name is not None else login.text
    return authors

def get_main_category(item):
    """Pega a categoria principal (domain='category')"""
    cats = item.findall('category[@domain="category"]', NS)
    if cats:
        c = cats[0]
        return c.text.strip(), c.get('nicename', 'uncategorized')
    return 'Uncategorized', 'uncategorized'

def generate_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    return slug[:70] or 'untitled'

def clean_gutenberg(html_content):
    """Remove comentários do Gutenberg e limpa HTML básico"""
    md = re.sub(r'<!-- /?wp:[\w/]+[^>]*-->\n?', '', html_content)
    md = re.sub(r'<h([1-6])[^\>]*>(.*?)</h\1>', r'\n### \2\n', md, flags=re.DOTALL|re.IGNORECASE)
    md = re.sub(r'<strong>(.*?)</strong>', r'**\1**', md, flags=re.DOTALL)
    md = re.sub(r'<b>(.*?)</b>', r'**\1**', md, flags=re.DOTALL)
    md = re.sub(r'<em>(.*?)</em>', r'*\1*', md, flags=re.DOTALL)
    md = re.sub(r'<a\s+[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', md, flags=re.DOTALL)
    md = re.sub(r'<p>(.*?)</p>', r'\n\1\n', md, flags=re.DOTALL)
    md = re.sub(r'<li>(.*?)</li>', r'* \1\n', md, flags=re.DOTALL)
    md = re.sub(r'<br\s*/?>', '\n', md)
    md = re.sub(r'<[^>]+>', '', md)
    md = html.unescape(md)
    return re.sub(r'\n{3,}', '\n\n', md).strip()

def convert_xml_to_md(xml_path, output_base):
    """Converte um arquivo XML para arquivos Markdown"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    authors_db = parse_authors(root)
    posts_created = 0
    
    for item in root.findall('.//item', NS):
        # Filtros
        if item.find('wp:post_type', NS)?.text != 'post': continue
        if item.find('wp:status', NS)?.text != 'publish': continue
        
        pub_date = item.find('pubDate')
        if pub_date is None or '2025' not in pub_date.text: continue
        
        # Extrair dados
        title = (item.find('title')?.text or 'Untitled').strip()
        content_elem = item.find('content:encoded', NS)
        content_html = content_elem.text if content_elem is not None else ''
        
        creator = item.find('dc:creator', NS)
        author_login = creator.text if creator is not None else 'unknown'
        author_name = AUTHOR_MAP.get(author_login, authors_db.get(author_login, author_login))
        
        cat_name, cat_slug = get_main_category(item)
        
        # Formatar data
        try:
            dt = datetime.strptime(pub_date.text, '%a, %d %b %Y %H:%M:%S %z')
            date_str = dt.strftime('%Y-%m-%d')
        except:
            date_str = '2025-01-01'
        
        slug = generate_slug(title)
        filename = f"{date_str}-{slug}.md"
        
        # Criar pasta da categoria
        cat_path = Path(output_base) / 'artigos' / cat_slug
        cat_path.mkdir(parents=True, exist_ok=True)
        
        # Frontmatter
        fm = {
            'title': title,
            'date': date_str,
            'status': 'publish',
            'author': author_name,
            'categories': cat_name
        }
        fm_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False, default_flow_style=False).strip()
        
        # Conteúdo Markdown
        md_content = clean_gutenberg(content_html)
        
        # Salvar arquivo
        filepath = cat_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"---\n{fm_yaml}\n---\n\n{md_content}\n")
        
        print(f"✓ {filepath.relative_to(output_base)}")
        posts_created += 1
    
    return posts_created

def main():
    xml_dir = 'xmls_originais'  # ← ajuste se necessário
    output_dir = 'dunapressjr'   # ← pasta do repositório local
    
    if not os.path.isdir(xml_dir):
        print(f"❌ Pasta não encontrada: {xml_dir}")
        return
    
    xml_files = [f for f in os.listdir(xml_dir) if f.endswith('.xml')]
    if not xml_files:
        print(f"❌ Nenhum arquivo .xml em {xml_dir}")
        return
    
    print(f"🔍 Processando {len(xml_files)} arquivo(s) XML...\n")
    
    total = 0
    for xml_file in xml_files:
        print(f"📄 {xml_file}:")
        try:
            count = convert_xml_to_md(os.path.join(xml_dir, xml_file), output_dir)
            print(f"   → {count} artigo(s) convertido(s)\n")
            total += count
        except Exception as e:
            print(f"   ❌ Erro: {e}\n")
    
    print(f"\n✅ Conclusão: {total} artigo(s) de 2025 em inglês processado(s)!")
    print(f"📁 Verifique: {output_dir}/artigos/")
    print(f"\n🚀 Próximo passo: cd {output_dir} && git add . && git commit -m 'Add 2025 EN articles' && git push")

if __name__ == "__main__":
    main()
