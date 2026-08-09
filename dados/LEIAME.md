# dados/

Derivados do build. Quase tudo aqui é ignorado pelo Git, porque é
reconstruído a cada publicação:

| Arquivo | Origem |
|---|---|
| `manifesto.json` | `src/migrar.py` — inventário do acervo |
| `redirects.map` | `src/migrar.py` — URLs antigas → novas |
| `noindex.txt` | `src/classificar.py` — o que sai do índice, e por quê |
| `indexacao.txt` | `src/classificar.py` — relatório legível |
| `limpeza.json` | `src/limpar.py` — diário do que foi removido |

**A exceção é `excecoes.txt`**, que é versionado. Ele contém as URLs que o
Search Console mostrou receber tráfego real e que, por isso, permanecem no
índice apesar da régua editorial. É decisão editorial baseada em dado
observado, não subproduto de build — e por isso pertence ao histórico.

Para gerá-lo:

```bash
python3 tools/excecoes.py caminho/para/search-console.csv
python3 src/classificar.py      # relê o arquivo e preserva a lista
```
