# Duna Press — Guia de implantação

Passo a passo do estado atual até o jornal no ar. Cada fase é independente
e reversível. Não pule a Fase 0.

Tempo estimado: 2 a 3 dias de trabalho, mais 4 a 6 semanas de observação
antes de trocar o domínio.

---

## Fase 0 — Rede de segurança (30 minutos)

Nada aqui é opcional. É o que permite desfazer qualquer passo seguinte.

```bash
git clone https://github.com/app-algoritmo/dunapressjr.git
cd dunapressjr

# marco do estado atual, para voltar a qualquer momento
git tag antes-da-reforma
git push origin antes-da-reforma

# todo o trabalho acontece fora da main
git checkout -b reforma-jornal
```

Baixe também uma cópia fria do repositório inteiro (Code → Download ZIP) e
guarde fora do GitHub. São 500 MB; vale o espaço.

**Antes de qualquer outra coisa**, no Google Search Console:
Desempenho → Exportar → últimos 16 meses, com as colunas de página e
cliques. Esse arquivo decide quais páginas merecem exceção ao `noindex`.
Ele leva minutos para gerar e não pode ser recuperado depois.

---

## Fase 1 — Emagrecer o repositório (1 hora)

O repositório tem ~515 MB. O limite recomendado do GitHub é 1 GB, e
repositório grande deixa lento cada `git clone` e cada build.

### 1.1 — `xmls/` (398 MB, 77% do peso)

São os exports do WordPress. Já foram convertidos: os 19.522 `.md` em
`artigos/` vieram deles. Estão ali sem função.

```bash
# guarde fora do repositório antes de remover
cp -r xmls ~/dunapress-backup-xmls

git rm -r --cached xmls
echo "xmls/" >> .gitignore
git commit -m "Remove exports do WordPress: já convertidos em artigos/"
```

> O histórico do Git ainda guarda os 398 MB. Para expurgar de vez é preciso
> `git filter-repo`, que reescreve o histórico e exige `push --force`.
> Recomendo **não** fazer agora: o ganho é de disco, o risco é de perder
> histórico. Deixe para depois que o site novo estiver estável.

### 1.2 — Índices gerados (15 MB)

Ficam obsoletos: o site novo não busca conteúdo por JSON no navegador.

```bash
git rm search-index.json search-index.backup.json \
       articles-cards.json drafts-index.json
git commit -m "Remove indices JSON: substituidos por HTML estatico"
```

---

## Fase 2 — Instalar o pipeline (30 minutos)

Crie a pasta `build/` na raiz e coloque os quatro scripts nela:

```
build/
  migrar.py       lê os .md, consolida 79 categorias em 9 editorias,
                  gera slugs em português e os mapas de redirect
  limpar.py       remove links de pagamento, afiliados e âncoras vazias
  classificar.py  decide o que entra no índice do Google
  gerar.py        escreve o HTML do jornal
```

No topo de cada script, ajuste a constante `RAIZ` para o caminho do
repositório na sua máquina.

### Ordem de execução — importa

```bash
python3 build/limpar.py        # 1º: altera os .md. Confira o diff antes de commitar.
python3 build/migrar.py        # 2º: lê os .md já limpos
python3 build/classificar.py   # 3º: precisa do manifesto do passo 2
python3 build/gerar.py         # 4º: precisa da classificação do passo 3
```

Depois do `limpar.py`, **revise antes de commitar**:

```bash
git diff --stat                      # deve mostrar ~6.976 arquivos
git diff artigos/news | head -100    # leia uma amostra de verdade
```

Se algo parecer errado: `git checkout -- artigos/` desfaz tudo.

---

## Fase 3 — O que fazer com cada arquivo existente

### Substituídos pelo gerador — apagar

| Arquivo | Por quê |
|---|---|
| `index.html` (176 KB) | A capa passa a ser gerada. A atual carrega 4,4 MB de JSON e monta tudo por JavaScript. |
| `artigo.html` (84 KB) | Cada matéria vira HTML próprio. Era ela que buscava o `.md` do `raw.githubusercontent.com`. |
| `categoria.html` (52 KB) | Vira uma página por editoria. |
| `categorias.js` | O mapa de categorias agora vive em `migrar.py`. |
| `biblioteca.html`, `escola.html` | Páginas de revista. Se o conteúdo importa, vira editoria; senão, sai. |
| `admin.html` (104 KB) | Publicação passa a ser por commit. Some junto com o Supabase. |
| `assinatura.html`, `unsubscribe.html` | Substituídos pelo serviço de newsletter (Fase 6). |

### Manter como estão

`CNAME` · `ads.txt` · `favicon.*` · `apple-touch-icon.png` ·
`web-app-manifest-*.png` · `site.webmanifest` · `og-default.jpg` ·
`404.html` · `404.gif` · `imagens/`

### Reescrever

| Arquivo | O que muda |
|---|---|
| `robots.txt` | Trocar `Disallow: /admin.html` pelo bloqueio do que for necessário e apontar o novo sitemap. |
| `sitemap.xml` | **Gerado** por `gerar.py`. Sai de 91 URLs para 5.058 reais. Apague o antigo. |
| `about.html`, `contato.html` | Viram `/quem-somos/` e `/contato/`, em português e no visual novo. |
| `privacy-policy.html`, `terms-of-use.html`, `cookie-notice.html` | Viram `/privacidade/`, `/termos/`, `/cookies/`. Os `.md` correspondentes podem virar a fonte. |
| `_config.yml` | Só se mantiver GitHub Pages. Com Cloudflare, some. |

### Scripts Python antigos

| Arquivo | Destino |
|---|---|
| `update_search_index.py` | Apagar — não há mais índice JSON. |
| `converter_2025_en.py`, `fix_authors.py` | Apagar — foram scripts de migração, já cumpriram a função. |
| `test_token.py` | Apagar. |
| `auto_publicar.py` | **Reescrever.** Publica direto com Supabase. Precisa virar: gera `.md` → abre Pull Request → um humano aprova. Ver Fase 7. |
| `auto_video.py` | Manter, mas tirar a dependência do Supabase. |
| `scripts/build_search_index.py`, `gerar_cards_index.py` | Apagar — obsoletos. |
| `scripts/update_videos.py` | Manter. |

### Workflows do GitHub Actions

| Workflow | Destino |
|---|---|
| `build-index.yml`, `gerar-cards.yml` | Apagar. |
| `publicar.yml` | Reescrever sem Supabase, com Pull Request. |
| `auto_video.yml`, `update-videos.yml`, `gerar_youtube_token.yml`, `test_token.yml` | Manter; revisar as chaves. |
| **novo:** `publicar-site.yml` | Roda o pipeline e publica. Está pronto, em `workflows/`. |

---

## Fase 4 — Hospedagem: por que é obrigatório sair do GitHub Pages

**GitHub Pages não faz redirecionamento 301.** Serve arquivo estático e
nada mais. Não existe `.htaccess`, não existe regra de redirect.

Você tem 19.522 URLs antigas que precisam apontar para as novas. Sem 301,
todas viram 404 e a autoridade acumulada em 10 milhões de visualizações
evapora. Não é preferência de arquitetura: é impossibilidade técnica.

Há um segundo motivo: GitHub Pages tem banda de 100 GB/mês como limite
recomendado e não se destina a uso comercial de alto tráfego.

### Recomendação: Cloudflare Pages

Gratuito, banda ilimitada, CDN global, e resolve os três formatos de URL
antigos. O domínio `dunapress.org` continua o mesmo — muda só quem serve.

Os redirects não cabem em arquivo estático: o `_redirects` do Cloudflare
aceita 2.000 regras e você tem 19.522. A solução está na pasta
`workers/`: uma única função no edge que lê o mapa e resolve os três
formatos de uma vez.

```
/artigo.html?file=…      →  consulta redirects.map          (19.522 URLs)
/categoria.html?cat=…    →  consulta redirects-categoria    (79 categorias)
/2024/08/31/slug/        →  consulta wp-legado.json          (casamento por prefixo)
```

O terceiro formato é o da era WordPress e resolve 69% dos casos. Os 31%
restantes são artigos que se perderam na conversão original: vão para
410 Gone com uma página que oferece busca.

### Passos

1. Conta em `dash.cloudflare.com`
2. Workers & Pages → Create → Pages → conectar o repositório
3. Build command: `python3 build/migrar.py && python3 build/classificar.py && python3 build/gerar.py`
4. Output directory: `site`
5. Custom domain: `dunapress.org`
6. Alterar os nameservers do domínio para os da Cloudflare
7. Publicar o Worker de redirects (`workers/redirects.js`)

Mantenha o GitHub Pages ligado por uma semana como rede de segurança.

---

## Fase 5 — Aplicar as exceções do Search Console

Com o CSV exportado na Fase 0:

```bash
python3 build/excecoes.py caminho/para/search-console.csv
```

O script cruza as URLs com cliques contra a lista de `noindex` e devolve as
que devem ser preservadas. Rode `classificar.py` de novo depois.

**Não pule.** São 14.310 páginas saindo do índice. Se 200 delas trazem
tráfego real, é melhor descobrir agora.

---

## Fase 6 — Encerrar o Supabase

As quatro tabelas em uso:

| Tabela | Destino |
|---|---|
| `authors` | Vira `dados/autores.yaml` no repositório, alimentado pelos 24 XMLs. |
| `config` | Vira constante nos scripts. |
| `newsletter`, `subscribers` | **Exportar antes de desligar.** Migrar para Beehiiv, MailerLite ou Buttondown. |

Ordem: exportar os assinantes → migrar para o novo serviço → confirmar que
chegaram → só então desligar o projeto no Supabase.

---

## Fase 7 — O que ainda precisa ser construído

Em ordem de importância:

1. **Páginas de autor** com credencial e histórico. São os 24 XMLs parados
   no repositório. É o maior item de credibilidade pendente.
2. **Página de princípios editoriais**, declarando o uso de IA e quem
   responde por ele.
3. **Página de correções.**
4. **`auto_publicar.py` reescrito** para abrir Pull Request em vez de
   publicar direto. Enquanto publicar sozinho, a supervisão editorial não
   existe de fato — e é ela que a política do Google exige.
5. Busca (Pagefind gera índice estático no build, sem servidor).
6. Paginação das editorias.

---

## Fase 8 — Trocar o domínio (só depois de tudo acima)

Espere 4 a 6 semanas com o site novo estável e a indexação subindo no
Search Console.

1. Mapear cada URL do domínio antigo para a nova, 1 para 1
2. 301 permanente em todas
3. Ferramenta de Mudança de Endereço no Search Console
4. Renovar o domínio antigo indefinidamente — os redirects precisam viver
5. Atualizar `ads.txt` e a propriedade do AdSense

Nunca troque o domínio junto com a reestruturação. Se o tráfego cair, você
precisa saber qual das duas mudanças causou.

---

## Ordem resumida

```
0. Branch + tag + exportar Search Console          ← nada avança sem isto
1. Remover xmls/ e os JSON                          -415 MB
2. Instalar pipeline em build/
3. limpar → migrar → classificar → gerar
4. Revisar o diff, commitar
5. Cloudflare Pages + Worker de redirects
6. Aplicar exceções do Search Console
7. Migrar newsletter, desligar Supabase
8. Autores, princípios, correções
9. Observar 4-6 semanas
10. Trocar o domínio
```
