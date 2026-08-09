# Arquitetura

## Por que estático

O site anterior renderizava tudo no navegador: a página `artigo.html` baixava
um índice JSON de 6 MB, achava o caminho do arquivo e buscava o Markdown cru
no `raw.githubusercontent.com`. Para o Google, existia **uma** página.

O sitemap tinha 91 URLs para 19.522 artigos.

Aqui cada matéria é um arquivo HTML completo, entregue pronto no primeiro
byte. Não há JSON no caminho crítico, não há chamada a API de terceiro, não
há conteúdo que dependa de JavaScript para existir.

O JavaScript (`assets/js/jornal.js`) só acrescenta conforto — busca e
rolagem da barra de editorias. Desligado, o jornal continua legível inteiro.

## Fluxo

```
artigos/*.md
    │
    ├── src/limpar.py         separa redação de comercial (roda sob demanda)
    │
    ├── src/migrar.py         → dados/manifesto.json
    │                           dados/redirects.map
    │
    ├── src/classificar.py    → decide indexar / noindex / 410
    │                           lê dados/excecoes.txt se existir
    │
    └── src/gerar.py          → site/
                                 index.html
                                 {editoria}/index.html
                                 AAAA/MM/DD/slug/index.html
                                 autores/{slug}/index.html
                                 principios/ correcoes/
                                 sitemap.xml  rss.xml
                                 api/busca.json  api/artigos.json
                                 assets/
```

## Decisões e o que custaram

**Permalink `/AAAA/MM/DD/slug/`** — o mesmo da era WordPress. As URLs
antigas voltam a funcionar sem redirecionamento, e a editoria fora da URL
permite reorganizar a taxonomia sem quebrar links. Custo: a URL não diz a
que editoria pertence.

**CSS externo com hash** (`jornal.css?v=a1b2c3d4`) — com 19.600 páginas, CSS
embutido significaria reenviar 14 KB a cada visita. Externo com hash permite
cache eterno no CDN. Custo: uma requisição a mais na primeira visita.

**Fontes no próprio domínio** — corta a conexão a `fonts.googleapis.com` do
caminho crítico e evita enviar o IP do leitor a terceiro, o que importa sob
LGPD. Baixadas por `tools/baixar_fontes.py`.

**Sem dependência externa em Python** — o pipeline roda só com a biblioteca
padrão. Um build que roda todo dia sem supervisão tem menos superfície de
quebra assim.

**`noindex` em vez de remoção** — 14.473 páginas do acervo saem do índice
de busca mas continuam publicadas, assinadas e no endereço original. É
decisão de busca, não de arquivo. Reversível por commit.

## Limites conhecidos

**Cloudflare Pages: 20.000 arquivos** no plano gratuito, 100.000 nos pagos
(exige `PAGES_WRANGLER_MAJOR_VERSION=4`). O acervo completo gera ~19.600.
`tools/conferir_build.py` avisa quando a folga fica pequena.

**`_redirects`: 2.000 regras.** Suficiente para o que sobrou, já que o
permalink resolve o grosso. Se voltar a crescer, use Bulk Redirects ou um
Worker.

**Índice de busca** cresce com o acervo indexado. Passando de ~2 MB, vale
dividir por editoria e carregar sob demanda.

**Tempo de build** cresce linearmente com o acervo. O workflow tem teto de
20 minutos, que é também o limite do Cloudflare Pages.
