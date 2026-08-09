# artigos/

O conteúdo do jornal: um arquivo Markdown por matéria.

```
artigos/{editoria}/AAAA-MM-DD-slug.md
```

Vazio de propósito. Os 19.522 artigos já estão no repositório atual — ao
montar o `dunapressjr` novo, traga `artigos/` do `dunapress_v1`. É a única
coisa que se copia de lá, além dos ícones.

```bash
cp -r ../dunapress_v1/artigos/* artigos/
```

Antes de qualquer outra coisa, rode a limpeza uma vez:

```bash
python3 src/limpar.py
git diff --stat                       # ~6.976 arquivos alterados
git diff artigos/news | head -100     # leia uma amostra antes de commitar
```

Formato do frontmatter: `docs/PUBLICAR.md`.
