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
    # adicione outros conforme necessário
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
        login_elem = a.find('wp:author_login', NS)
        name_elem = a.find('wp:author_display_name', NS)
        if login_elem is not None:
            authors[login_elem.text] = name_elem.text if name_elem is not None else login_elem.text
    return authors

def get_main_category(item):
    """Pega a categoria principal (domain='category')"""
    cats = item.findall('category[@domain="category"]', NS)
    if cats:
        c = cats[0]
        return c.text.strip() if c.text else 'Uncategorized', c.get('nicename', 'uncategorized')
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
    return re.sub(r'\
