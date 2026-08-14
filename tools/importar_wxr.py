#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
importar_wxr.py — converte um export WordPress (WXR) em arquivos .md do Duna Press.

Uso:
    python3 tools/importar_wxr.py EXPORT.xml                  # simulação, não escreve nada
    python3 tools/importar_wxr.py EXPORT.xml --escrever       # grava em artigos/
    python3 tools/importar_wxr.py EXPORT.xml --escrever --incluir-comercial

Padrões: não escreve nada sem --escrever; pula o que já existe no acervo;
põe de quarentena o conteúdo com marcador comercial.
"""

import argparse, glob, html, os, re, sys, unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser

NS = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
}

# ---------------------------------------------------------------- categorias

EDITORIA = {}
def _reg(ed, cats):
    for c in cats.split():
        EDITORIA[c] = ed

_reg('mundo', """international-politics geopolitics world-affairs politics-and-society news
    international-affairs international-relations global-affairs military policy
    international-regulation society-and-demographics global-development trade-networks
    social-issues politics-and-culture covid-19""")
_reg('economia', """business-and-economy global-economy international-economy personal-finance
    finances economy economy-and-sustainability future-economy financial-education
    digital-business digital-economy global-finance bitcoin real-estate entrepreneurship
    digital-entrepreneurship business-opportunities freelance careers courses-and-careers
    professions classifieds""")
_reg('tecnologia', """technology artificial-intelligence innovation science-and-tech
    future-and-innovation robotics cibersecurity social-networks digital-productivity
    5g-technology quantum-technology naval-technology healthcare-technology
    programming-education digital-education business-and-technology e-auto vehicles""")
_reg('ciencia-e-saude', """health mental-health environment sustainability science astronomy
    space-exploration neuroscience neurological-health clinical-science health-and-well-being
    health-and-wellness well-being wellness sustainable-living renewable-energy
    science-and-innovation science-and-climate astrobiology astrophysics aging-research
    genetic-engineering biotech-and-innovation agriculture nutrition diet fitness
    scientific-regulation nature-therapy""")
_reg('cultura', """magazine society-and-culture lifestyle culture-and-history history education
    teaching-strategies personal-development celebrations travel tourism-and-gastronomy
    celebrities personality architecture-and-art beauty fashion music entertainment-news
    culture-and-entertainment did-you-know science-and-fiction astrology astrological-insights
    family-and-relationships home-decor pets philosophy history-and-philosophy motivational
    works food archaeology creative-content ufology""")
_reg('esportes', 'soccer motorsport cycling tennis formula-1')
_reg('opiniao', 'opinion')

PASTA = {
    'mundo': 'world-affairs', 'tecnologia': 'technology', 'ciencia-e-saude': 'science',
    'economia': 'business-and-economy', 'brasil': 'brasil', 'cultura': 'culture-and-history',
    'esportes': 'sports', 'politica': 'world-affairs', 'opiniao': 'opinion',
}
# categorias de saúde vão para artigos/health/ em vez de artigos/science/
SAUDE = set("""health mental-health neurological-health clinical-science health-and-well-being
    health-and-wellness well-being wellness nutrition diet fitness healthcare-technology
    aging-research nature-therapy""".split())

# prioridade quando o post tem mais de uma categoria: a mais específica ganha
PRIORIDADE = ['esportes', 'opiniao', 'ciencia-e-saude', 'tecnologia', 'economia',
              'cultura', 'mundo']

# ---------------------------------------------------------------- limpeza

COMERCIAL = re.compile(
    r'(hotmart|monetizze|eduzz|kiwify|braip|\bafilia\w*|affiliate link|'
    r'inscreva-se|compre agora|cupom|link na bio|clique aqui|buy now|sign up now)', re.I)

RODAPE = re.compile(
    r'(join the oslo meet|oslomeet\.org|/subscriptions|follow the boreal times|'
    r'thank you for reading|subscribe to)', re.I)

PROIBIDOS = re.compile(
    r'^\s*(o que está em jogo|o que vem a seguir|conclusão|considerações finais|'
    r'em resumo|what.s at stake|what.s next|conclusion|final thoughts|in summary|'
    r'key takeaways|bottom line)\s*$', re.I)

STAGING = 'dunaong.wpcomstaging.com'

# ---------------------------------------------------------------- HTML → MD

class ParaMarkdown(HTMLParser):
    PULAR = {'script', 'style', 'noscript'}
    BLOCOS = {'p', 'div', 'section', 'article', 'figure', 'figcaption', 'blockquote',
              'ul', 'ol', 'li', 'table', 'tr', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.buf = []
        self.pular = 0
        self.pilha = []
        self.lista = []          # 'ul' | 'ol'
        self.contador = []
        self.link = None
        self.link_ini = None
        self.pre = False
        self.descartar = 0

    # --- utilitários
    def _texto(self):
        t = ''.join(self.buf)
        self.buf = []
        return t

    def _fecha(self, prefixo=''):
        t = self._texto()
        if not self.pre:
            t = re.sub(r'[ \t]+', ' ', t).strip()
        if t:
            self.out.append(prefixo + t)

    # --- eventos
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.PULAR:
            self.pular += 1
            return
        classe = (a.get('class') or '') + ' ' + (a.get('id') or '')
        if self.descartar or re.search(r'(twitter-tweet|instagram-media|tiktok-embed|fb-post|wp-block-embed__wrapper)', classe, re.I):
            if tag in ('blockquote', 'div', 'figure'):
                self.descartar += 1
                self._texto()
                return
        if self.descartar:
            return
        if self.pular:
            return

        if tag == 'br':
            self._fecha()
        elif tag == 'hr':
            self._fecha(); self.out.append('***')
        elif tag == 'img':
            src = a.get('src', '')
            alt = (a.get('alt') or 'imagem').strip() or 'imagem'
            if src:
                self.buf.append(f'\n![{alt}]({src})\n')
        elif tag == 'iframe':
            src = a.get('src', '')
            if src:
                self._fecha()
                self.out.append(f'[Vídeo]({src})')
        elif tag == 'a':
            self.link = a.get('href', '')
            self.link_ini = len(self.buf)
        elif tag in ('strong', 'b'):
            self.buf.append('**')
        elif tag in ('em', 'i'):
            self.buf.append('*')
        elif tag == 'code' and not self.pre:
            self.buf.append('`')
        elif tag == 'pre':
            self._fecha(); self.pre = True
        elif tag in ('ul', 'ol'):
            self._fecha()
            self.lista.append(tag)
            self.contador.append(0)
        elif tag == 'li':
            self._fecha()
            if self.contador:
                self.contador[-1] += 1
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._fecha()
            self.pilha.append(tag)
        elif tag in self.BLOCOS:
            self._fecha()

    def handle_endtag(self, tag):
        if tag in self.PULAR:
            self.pular = max(0, self.pular - 1)
            return
        if self.descartar:
            if tag in ('blockquote', 'div', 'figure'):
                self.descartar -= 1
                self.buf = []
            return
        if self.pular:
            return

        if tag == 'a':
            if self.link_ini is None:
                return
            texto = ''.join(self.buf[self.link_ini:])
            del self.buf[self.link_ini:]
            href = (self.link or '').strip()
            self.link, self.link_ini = None, None
            if not texto.strip():
                pass
            elif not href or href.startswith('#') or 'twitter.com' in href or 'x.com' in href or 't.co/' in href:
                self.buf.append(texto)
            else:
                self.buf.append(f'[{texto.strip()}]({href})')
        elif tag in ('strong', 'b'):
            self.buf.append('**')
        elif tag in ('em', 'i'):
            self.buf.append('*')
        elif tag == 'code' and not self.pre:
            self.buf.append('`')
        elif tag == 'pre':
            t = self._texto().strip('\n')
            if t:
                self.out.append('```\n' + t + '\n```')
            self.pre = False
        elif tag == 'li':
            t = self._texto().strip()
            if t:
                if self.lista and self.lista[-1] == 'ol':
                    self.out.append(f'{self.contador[-1]}. {t}')
                else:
                    self.out.append(f'- {t}')
        elif tag in ('ul', 'ol'):
            self._fecha()
            if self.lista:
                self.lista.pop(); self.contador.pop()
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            nivel = '##' if tag in ('h1', 'h2') else '###'
            self._fecha(prefixo=nivel + ' ')
            if self.pilha:
                self.pilha.pop()
        elif tag == 'blockquote':
            t = self._texto().strip()
            if t:
                self.out.append('> ' + t.replace('\n', '\n> '))
        elif tag in self.BLOCOS:
            self._fecha()

    def handle_data(self, d):
        if not self.pular and not self.descartar:
            self.buf.append(d)

    def handle_comment(self, d):
        pass  # descarta os marcadores <!-- wp:... -->

    def resultado(self):
        self._fecha()
        return [b for b in self.out if b.strip()]


def html_para_md(raw):
    p = ParaMarkdown()
    p.feed(raw or '')
    p.close()
    return normalizar_titulos(p.resultado())


def normalizar_titulos(blocos):
    """O WordPress costuma usar h3 como intertítulo sem nenhum h2 acima.
    Reduz tudo para que o nível mais raso vire '##'."""
    niveis = [len(re.match(r'^#+', b).group()) for b in blocos if b.startswith('#')]
    if not niveis:
        return blocos
    desloc = min(niveis) - 2
    if desloc <= 0:
        return blocos
    saida = []
    for b in blocos:
        m = re.match(r'^(#+)\s*(.*)$', b)
        if m:
            n = max(2, len(m.group(1)) - desloc)
            saida.append('#' * n + ' ' + m.group(2))
        else:
            saida.append(b)
    return saida


# ---------------------------------------------------------------- utilitários

def sem_acento(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))


def encurtar_slug(slug, limite=60):
    slug = sem_acento(slug).lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    if len(slug) <= limite:
        return slug
    corte = slug[:limite].rsplit('-', 1)[0]
    return corte or slug[:limite]


def detectar_idioma(texto):
    pt = set('de que não para com uma como mais dos das pela pelo são também já sobre entre'.split())
    en = set('the of and to in that with for from this are was were which have has'.split())
    w = re.findall(r"[a-zà-ÿ]+", texto.lower())
    a = sum(1 for x in w if x in pt)
    b = sum(1 for x in w if x in en)
    return 'pt' if a > b else 'en'


def escolher_formato(n):
    if n < 200:   return 'nota', 'curto demais para nota'
    if n <= 350:  return 'nota', None
    if n < 400:   return 'explicador', 'abaixo da faixa do explicador'
    if n <= 900:  return 'explicador', None
    if n <= 1200: return 'reportagem', None
    if n <= 1400: return 'analise', None
    return 'analise', 'acima da faixa da analise'


def escolher_editoria(cats):
    if not cats:
        return 'mundo', None
    eds = [(EDITORIA.get(c), c) for c in cats]
    eds = [(e, c) for e, c in eds if e]
    if not eds:
        return 'mundo', None
    for pref in PRIORIDADE:
        for e, c in eds:
            if e == pref:
                return e, c
    return eds[0]


def yaml_str(s):
    s = (s or '').replace('\\', '').replace('"', "'").replace('\n', ' ')
    return re.sub(r'\s+', ' ', s).strip()


# ---------------------------------------------------------------- corpo

def limpar_blocos(blocos, titulo, mapa_slugs):
    saida = []
    for b in blocos:
        # rodapé promocional do outro jornal
        if RODAPE.search(b):
            continue
        # intertítulo proibido
        if b.startswith('#') and PROIBIDOS.match(re.sub(r'^#+\s*', '', b)):
            continue
        # H1 repetindo o título
        if b.startswith('## ') and sem_acento(b[3:]).lower().strip() == sem_acento(titulo).lower().strip():
            continue
        # intertítulo de SEO carregando a marca do outro jornal
        if b.startswith('#'):
            limpo = MARCA.sub('', b).rstrip(' *|')
            if len(re.sub(r'^#+\s*|\*', '', limpo).strip()) < 4:
                continue
            b = limpo
        # negrito usado como intertítulo
        m = re.match(r'^\*\*(.{3,90})\*\*[:：]?$', b.strip())
        if m:
            b = '## ' + m.group(1).strip()
        # separador que quebraria o frontmatter
        b = re.sub(r'^\s*-{3,}\s*$', '***', b)
        b = re.sub(r'^\s*_{3,}\s*$', '***', b)
        # links para o staging do WordPress
        b = reescrever_links(b, mapa_slugs)
        # URL crua vira link markdown
        b = re.sub(r'(?<![(\[])(?<!\]\()\bhttps?://\S+', _url_crua, b)
        # quebra interna sobrando colaria dois blocos no conversor
        for pedaco in re.split(r'\n+', b):
            pedaco = pedaco.rstrip()
            if not pedaco.strip():
                continue
            # colchete ou parêntese órfão quebra o link no build
            if pedaco.count('[') != pedaco.count(']'):
                pedaco = pedaco.replace('[', '').replace(']', '')
            saida.append(pedaco)
    return saida


def _url_crua(m):
    u = m.group(0)
    cauda = ''
    while u and u[-1] in '.,;:)!?"\'':
        cauda = u[-1] + cauda
        u = u[:-1]
    dominio = re.sub(r'^https?://(www\.)?', '', u).split('/')[0]
    return f'[{dominio}]({u}){cauda}'


MARCA = re.compile(r'\s*(?:[|–—-]\s*)?(?:on\s+)?(?:the\s+)?boreal\s+times\b.*$', re.I)


def reescrever_links(b, mapa_slugs):
    def troca(m):
        texto, href = m.group(1), m.group(2)
        if STAGING not in href:
            return m.group(0)
        slug = href.rstrip('/').rsplit('/', 1)[-1]
        if slug in mapa_slugs:
            return f'[{texto}](/{mapa_slugs[slug]}/)'
        return texto  # link morto: fica só o texto
    return re.sub(r'\[([^\]]*)\]\(([^)]+)\)', troca, b)


# ---------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('xml')
    ap.add_argument('--escrever', action='store_true')
    ap.add_argument('--incluir-comercial', action='store_true')
    ap.add_argument('--raiz', default='artigos')
    ap.add_argument('--revisor', default='Paulo Fernando de Barros')
    ap.add_argument('--autor', default='Paulo Fernando de Barros')
    ap.add_argument('--limite', type=int, default=0, help='processa só N posts (teste)')
    args = ap.parse_args()

    root = ET.parse(args.xml).getroot()
    itens = root.findall('./channel/item')
    posts = [i for i in itens if i.findtext('wp:post_type', None, NS) == 'post'
             and i.findtext('wp:status', None, NS) == 'publish']

    # id do anexo -> url
    anexos = {}
    for i in itens:
        if i.findtext('wp:post_type', None, NS) == 'attachment':
            anexos[i.findtext('wp:post_id', None, NS)] = i.findtext('wp:attachment_url', None, NS)

    # slugs já publicados no acervo
    existentes = {}
    for f in glob.glob(os.path.join(args.raiz, '**', '*.md'), recursive=True):
        nome = os.path.basename(f)[:-3]
        existentes[re.sub(r'^\d{4}-\d{2}-\d{2}-', '', nome)] = nome

    mapa_slugs = {i.findtext('wp:post_name', None, NS): encurtar_slug(i.findtext('wp:post_name', None, NS) or '')
                  for i in posts}

    if args.limite:
        posts = posts[:args.limite]

    rel = {'escritos': 0, 'duplicados': [], 'comerciais': [], 'avisos': [], 'vazios': []}
    por_editoria = Counter()
    por_idioma = Counter()
    usados = set()

    for i in posts:
        titulo = html.unescape(i.findtext('title') or '').strip()
        slug_wp = i.findtext('wp:post_name', None, NS) or ''
        data = (i.findtext('wp:post_date', None, NS) or '')[:10]
        raw = i.findtext('content:encoded', None, NS) or ''
        resumo = re.sub(r'<[^>]+>', ' ', i.findtext('excerpt:encoded', None, NS) or '')

        cats = [c.get('nicename') for c in i.findall('category') if c.get('domain') == 'category']
        tags = [c.get('nicename') for c in i.findall('category') if c.get('domain') == 'post_tag']

        thumb = None
        for m in i.findall('wp:postmeta', NS):
            if m.findtext('wp:meta_key', None, NS) == '_thumbnail_id':
                thumb = anexos.get(m.findtext('wp:meta_value', None, NS))

        if COMERCIAL.search(raw) and not args.incluir_comercial:
            rel['comerciais'].append((data, titulo))
            continue

        blocos = html_para_md(raw)
        blocos = limpar_blocos(blocos, titulo, mapa_slugs)
        corpo = '\n\n'.join(blocos)
        palavras = len(re.sub(r'[#>*`\[\]()]', ' ', corpo).split())

        if palavras < 40:
            rel['vazios'].append((data, titulo, palavras))
            continue

        slug = encurtar_slug(slug_wp or titulo)
        if slug in existentes:
            rel['duplicados'].append((data, slug))
            continue
        base = slug
        n = 2
        while slug in usados:
            slug = f'{base}-{n}'; n += 1
        usados.add(slug)

        editoria, cat_origem = escolher_editoria(cats)
        pasta = PASTA[editoria]
        if editoria == 'ciencia-e-saude' and any(c in SAUDE for c in cats):
            pasta = 'health'

        formato, aviso = escolher_formato(palavras)
        if aviso:
            rel['avisos'].append((data, slug, palavras, aviso))

        idioma = detectar_idioma(titulo + ' ' + corpo[:4000])
        por_editoria[editoria] += 1
        por_idioma[idioma] += 1

        desc = yaml_str(html.unescape(resumo))[:197]
        if len(desc) < 40:
            primeiro = next((b for b in blocos if not b.startswith(('#', '-', '>', '!', '['))), '')
            desc = yaml_str(re.sub(r'[*`\[\]]', '', primeiro))[:197]
        if len(desc) == 197:
            desc = desc.rsplit(' ', 1)[0] + '…'

        etiquetas = []
        for t in tags[:6]:
            e = sem_acento(t).replace('-', ' ').strip().lower()
            if e and e not in etiquetas:
                etiquetas.append(e)
        if not etiquetas and cat_origem:
            etiquetas = [cat_origem.replace('-', ' ')]

        sub = ''
        fonte_sub = yaml_str(html.unescape(resumo)) or desc
        if fonte_sub:
            partes = re.split(r'(?<=[.!?])\s+', fonte_sub)
            sub = partes[0][:180].strip()
            if sub.lower() == yaml_str(titulo).lower() or len(sub) < 25:
                sub = ''

        fm = [
            '---',
            f'title: "{yaml_str(titulo)}"',
            f'subtitle: "{sub}"',
            f'description: "{desc}"',
            f'date: {data}',
            'status: publish',
            f'author: "{args.autor}"',
            f'categories: "{editoria}"',
            f'formato: {formato}',
            'proveniencia: humano',
            f'revisor: {args.revisor}',
            'fonte_primaria: ""',
            'fonte_nome: "Arquivo Duna Press / The Boreal Times"',
            f'data_do_fato: {data}',
            f'featuredImage: "{thumb or ""}"',
            'photoAuthor: ""',
            'photoSource: "Arquivo Duna Press"',
            f'idioma: {idioma}',
            'tags:',
        ]
        fm += [f'  - {e}' for e in etiquetas]
        fm.append('---')

        texto = '\n'.join(fm) + '\n\n' + corpo + '\n'

        destino = os.path.join(args.raiz, pasta, f'{data}-{slug}.md')
        if args.escrever:
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, 'w', encoding='utf-8') as f:
                f.write(texto)
        rel['escritos'] += 1

    # ------------------------------------------------------------ relatório
    print('DUNA PRESS — IMPORTAÇÃO WXR')
    print('=' * 54)
    print(f'modo ................ {"ESCRITA" if args.escrever else "SIMULAÇÃO (nada gravado)"}')
    print(f'posts no export ..... {len(posts)}')
    print(f'convertidos ......... {rel["escritos"]}')
    print(f'já no acervo ........ {len(rel["duplicados"])}')
    print(f'quarentena comercial  {len(rel["comerciais"])}')
    print(f'curtos demais (<40) . {len(rel["vazios"])}')
    print()
    print('POR EDITORIA')
    print('-' * 54)
    for k, v in por_editoria.most_common():
        print(f'  {k:<18} {v:>5}   → artigos/{PASTA[k]}/')
    print()
    print('POR IDIOMA')
    print('-' * 54)
    for k, v in por_idioma.most_common():
        print(f'  {k:<18} {v:>5}')
    if rel['avisos']:
        print()
        print(f'FORMATO FORA DE FAIXA ({len(rel["avisos"])})')
        print('-' * 54)
        for d, s, n, a in rel['avisos'][:15]:
            print(f'  {d}  {n:>5} pal  {a}  {s[:40]}')
        if len(rel['avisos']) > 15:
            print(f'  ... mais {len(rel["avisos"]) - 15}')
    if rel['comerciais']:
        print()
        print(f'QUARENTENA COMERCIAL ({len(rel["comerciais"])}) — use --incluir-comercial para trazer')
        print('-' * 54)
        for d, t in rel['comerciais']:
            print(f'  {d}  {t[:64]}')
    if rel['duplicados']:
        print()
        print(f'JÁ NO ACERVO ({len(rel["duplicados"])})')
        print('-' * 54)
        for d, s in rel['duplicados'][:15]:
            print(f'  {d}  {s[:60]}')
        if len(rel['duplicados']) > 15:
            print(f'  ... mais {len(rel["duplicados"]) - 15}')
    if rel['vazios']:
        print()
        print(f'CURTOS DEMAIS ({len(rel["vazios"])})')
        print('-' * 54)
        for d, t, n in rel['vazios']:
            print(f'  {d}  {n:>3} pal  {t[:56]}')


if __name__ == '__main__':
    main()
