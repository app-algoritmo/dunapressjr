# Duna Press

Jornal digital independente, em português. Site estático gerado a partir de
arquivos Markdown, sem banco de dados e sem servidor de aplicação.

**Editor responsável:** Paulo Fernando de Barros
**Produção:** https://dunapress.org

---

## Como funciona

O conteúdo vive em `artigos/`, um arquivo Markdown por matéria. Quatro
scripts em Python transformam isso num jornal completo. Não há dependência
externa: só a biblioteca padrão do Python 3.12.

```
artigos/*.md  →  migrar  →  classificar  →  gerar  →  site/
```

| Etapa | O que faz |
|---|---|
| `src/limpar.py` | Remove links de pagamento, afiliado e apelo comercial do corpo editorial |
| `src/migrar.py` | Lê os `.md`, consolida categorias em 9 editorias, monta as URLs |
| `src/classificar.py` | Decide o que entra no índice do Google |
| `src/gerar.py` | Escreve o HTML, o sitemap, o RSS e os feeds |
| `src/publicar.py` | Redige com IA e abre Pull Request — para análise, opinião e reportagem |
| `src/auto_publicar.py` | Publica Brasil e Mundo sozinho, com verificação automática |

## Rodar localmente

```bash
git clone https://github.com/app-algoritmo/dunapressjr.git
cd dunapressjr

python3 src/migrar.py
python3 src/classificar.py
python3 src/gerar.py
python3 tools/conferir_build.py

# servir para conferir no navegador
python3 -m http.server 8000 --directory site
```

Gerar o acervo inteiro leva alguns minutos. Durante o desenvolvimento:

```bash
DP_AMOSTRA=1 python3 src/gerar.py    # só um punhado de matérias
```

## Publicar uma matéria

Há dois caminhos, e a diferença entre eles é declarada ao leitor na própria
matéria.

### Automático — Brasil e Mundo

```bash
python3 src/auto_publicar.py            # nacional + internacional
python3 src/auto_publicar.py --ensaio   # mostra sem publicar
```

Busca fatos em feeds públicos (Agência Brasil, Senado, Câmara, IBGE, Banco
Central, ONU, Comissão Europeia, FMI, Banco Mundial), redige e publica sem
revisão prévia. Quatro barreiras antes de ir ao ar:

1. o fato vem de fonte buscada na hora, não do prompt
2. o assunto não saiu nos últimos 10 dias
3. cada afirmação é conferida contra a fonte — o que ela não sustenta, cai
4. sobreposição de trecho com a fonte precisa ficar abaixo de 14%, senão é
   republicação disfarçada e não texto próprio

Sai marcada como **Publicação automática · sem revisão humana prévia**, com
link para a fonte, e entra em `editorial/revisao-pendente.md`.

Teto de 4 por execução, três execuções em dias úteis.

### Com revisão — o resto

Análise, opinião e reportagem de fôlego passam por Pull Request.

```bash
# 1. descreva o fato numa pauta
cat > pauta.json <<'JSON'
[{"fato": "O IBGE divulgou que o IPCA de julho fechou em 0,32%",
  "fonte_primaria": "https://www.ibge.gov.br/...",
  "data_do_fato": "2026-08-06",
  "por_que_agora": "Primeiro dado após a mudança da meta",
  "a_quem_afeta": "Assalariados com reajuste indexado",
  "formato": "nota", "editoria": "economia"}]
JSON

# 2. redija e abra o PR
python3 src/publicar.py pauta.json

# 3. revise no GitHub e aprove
```

Sem fato verificável e fonte primária, o script recusa antes de redigir.
Depois de redigir, confere a forma contra a pauta editorial. Recusa não é
falha: é o mecanismo funcionando.

Teto de **8 matérias por dia**. Acima disso a revisão vira carimbo.

## Estrutura

```
artigos/          conteúdo em Markdown — a fonte da verdade
src/              o gerador
assets/           css, js, fontes, imagens
editorial/        pauta, princípios, correções
dados/            derivados do build (não versionados)
tools/            conferências e utilitários
docs/             documentação
site/             saída do build (não versionada)
```

## Regras que o código faz valer

Estão em [`editorial/PAUTA-EDITORIAL.md`](editorial/PAUTA-EDITORIAL.md) e
não são decorativas — `tools/conferir_pauta.py` roda em todo Pull Request:

- Nenhum artigo nasce de tema. Todo artigo nasce de fato verificável.
- Texto redigido com IA sem revisor nomeado não passa.
- Nenhum link comercial no corpo editorial.
- Subtítulos genéricos e fórmulas de título são recusados.

## Publicação

`main` → GitHub Actions → GitHub Pages.

O deploy só acontece se `tools/conferir_build.py` aprovar. Ele interrompe a
publicação se o sitemap encolher demais, se faltar página obrigatória, se
alguma matéria sair sem selo de proveniência, ou se o número de arquivos
passar do teto da plataforma.

> **Limite de publicação.** O GitHub Pages recomenda até 1 GB por site e
> 100 GB de banda por mês. Com o acervo inteiro o site tem ~19.600 arquivos
> e cerca de 0,37 GB. A conferência mede o peso a cada build e interrompe a
> publicação se passar de 1 GB.

## URLs

O permalink é `/AAAA/MM/DD/slug/`, o mesmo da era WordPress. Duas
consequências deliberadas:

1. Os endereços antigos voltam a funcionar sem redirecionamento.
2. A editoria não está na URL, então a taxonomia pode ser reorganizada para
   sempre sem quebrar link nenhum.

## Documentação

- [Guia de implantação](docs/IMPLANTACAO.md)
- [Pauta editorial](editorial/PAUTA-EDITORIAL.md)
- [Princípios editoriais](editorial/principios.md)
- [Arquitetura](docs/ARQUITETURA.md)
