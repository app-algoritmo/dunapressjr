# Publicar uma matéria

## O caminho normal

Toda matéria entra por Pull Request. Ninguém escreve direto na `main`, nem
pessoa nem script.

### 1. A pauta

Antes de escrever, cinco campos. Sem eles não há matéria:

| Campo | O que é |
|---|---|
| `fato` | O que mudou, em uma frase |
| `fonte_primaria` | URL do documento original |
| `data_do_fato` | Quando ocorreu — não quando você escreveu |
| `por_que_agora` | Por que é notícia hoje |
| `a_quem_afeta` | Quem sente o efeito |

A fonte primária é o documento original: o portal do IBGE, o acórdão, o
artigo no periódico. Nunca outra reportagem sobre ele.

### 2. Redigir

**Com assistência de IA:**

```bash
python3 src/publicar.py pauta.json
```

O script recusa antes de redigir se a pauta estiver incompleta, e recusa
depois de redigir se o texto violar a forma. Para ver sem abrir PR:

```bash
python3 src/publicar.py pauta.json --ensaio
```

**À mão:** crie o `.md` em `artigos/{editoria}/AAAA-MM-DD-slug.md` e abra o
PR. As mesmas regras valem — `tools/conferir_pauta.py` roda igual.

### 3. Revisar

O PR traz a lista de conferência. Nenhum item é decorativo:

- O fato confere com a fonte primária
- Nenhum dado, nome ou declaração foi inventado
- Os números têm fonte e período
- Não repete estrutura de outra matéria da semana

Aprovado o merge, o site é reconstruído e publicado sozinho.

## Frontmatter

```yaml
---
title: "O que aconteceu"
subtitle: "A linha fina"
description: "Resumo em até 200 caracteres"
date: 2026-08-07
status: publish
author: "Nome de quem assina"
categories: "economia"
formato: nota
proveniencia: ia-assistido      # ou: humano
revisor: "Paulo Fernando de Barros"   # obrigatório se proveniencia=ia-assistido
fonte_primaria: "https://..."
data_do_fato: 2026-08-06
tags:
  - inflação
---
```

## Corrigir uma matéria publicada

Erro corrigido não se apaga: se registra.

1. Corrija o texto em `artigos/`
2. Acrescente a entrada em `editorial/correcoes.md`
3. Abra o PR descrevendo o que mudou

## Quando não publicar

Sem fato verificável, não há matéria. Um dia sem pauta é um dia sem
publicação, e isso é normal em jornal.

O teto é de 8 matérias por dia. Acima disso a revisão vira carimbo, e a
supervisão editorial deixa de existir de fato.
