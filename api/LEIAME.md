# api/

Vazio no repositório. O build escreve aqui, em `site/api/`:

| Arquivo | O que é |
|---|---|
| `busca.json` | Índice da busca do site. Carregado sob demanda pelo `jornal.js` — quem não busca, não baixa. |
| `artigos.json` | Feed público no padrão JSON Feed 1.1, últimas 200 matérias. |

O RSS fica em `site/rss.xml`.

Não há API de servidor: o site é estático. Estes arquivos são gerados no
build e servidos como qualquer outro arquivo pelo CDN.
