---
title: "A inteligência artificial de código aberto alcançou a fronteira e deixou de caber num computador comum"
subtitle: "Os modelos abertos líderes hoje são estruturas de mais de um trilhão de parâmetros. Um deles exige cerca de um terabyte de memória de vídeo; outro precisa de mais de sessenta aceleradores para rodar. A Meta, que sustentou a fronteira aberta por anos, não lançou a versão nova e passou a desenvolver modelo fechado"
description: "A bifurcação da IA de código aberto: modelos de fronteira que exigem centro de dados e modelos pequenos que rodam num telefone."
date: 2026-09-24
status: publish
author: "Redação Duna Press"
categories: "tecnologia"
formato: explicador
proveniencia: humano
revisor: Paulo Fernando de Barros
fonte_primaria: ""
fonte_nome: "Placares públicos de modelos de linguagem mantidos por Artificial Analysis, LLM Stats e SWE-bench; documentação técnica publicada pelos desenvolvedores dos modelos citados"
data_do_fato: 2026-09-24
featuredImage: "https://plus.unsplash.com/premium_photo-1676150789916-2c7d1fdda6b9?w=1200&auto=format&fit=crop&q=75"
photoAuthor: "Mike Hindle"
photoSource: "Unsplash"
tags:
  - inteligencia-artificial
  - codigo-aberto
  - tecnologia
  - hardware
---

Durante alguns anos, código aberto em inteligência artificial significou duas coisas ao mesmo tempo: os pesos do modelo eram publicados, e uma pessoa com uma placa de vídeo razoável conseguia rodá-lo em casa.

As duas coisas se separaram.

## O que mudou na capacidade

Os modelos abertos alcançaram a fronteira. Um modelo aberto chinês figura hoje em terceiro lugar geral num dos índices independentes de inteligência, à frente de quase todos os modelos proprietários. Outro marca desempenho em engenharia de software equivalente ao de modelos de fronteira fechados — e, num teste específico de tarefa agêntica, um modelo aberto com licença permissiva supera um produto comercial cobrado a preço de topo.

Essa é a notícia boa para quem defende abertura: a diferença de qualidade entre aberto e fechado deixou de ser o argumento decisivo.

## O que mudou no hardware

Os modelos que fazem isso são estruturas de mistura de especialistas com mais de um trilhão de parâmetros.

Na prática: um deles exige cerca de um terabyte de memória de vídeo em precisão padrão — o equivalente a oito aceleradores de topo em precisão reduzida. Outro precisa de mais de sessenta aceleradores para operar.

Nenhum desses números descreve um computador. Descrevem um centro de dados pequeno.

Baixar os pesos continua sendo gratuito e legal. Executá-los custa o que custa alugar infraestrutura — e quem aluga infraestrutura de uma nuvem comercial está, do ponto de vista prático, na mesma posição de quem paga uma interface de programação fechada.

## A bifurcação

O ecossistema se partiu em duas pontas, com pouco no meio.

De um lado, os gigantes abertos de escala de centro de dados. De outro, modelos genuinamente pequenos — na casa de dezenas de bilhões de parâmetros ou menos — que rodam numa única placa de vídeo ou mesmo num telefone.

O que sumiu é a faixa intermediária: o modelo que um laboratório de universidade, uma empresa média ou um entusiasta conseguia rodar sozinho com resultado competitivo.

## A saída da Meta

A Meta sustentou por anos a fronteira aberta com a família Llama, e foi a principal razão pela qual pesquisadores e empresas fora das grandes companhias tiveram acesso a modelos de qualidade.

A versão nova não foi lançada, e a previsão atual é 2027. A empresa passou a desenvolver modelo fechado.

O lugar deixado por ela foi ocupado sobretudo por laboratórios chineses, que hoje publicam a maior parte dos modelos abertos de fronteira.

## Por que isso importa fora do setor

Porque muda quem pode auditar.

O argumento central a favor de pesos abertos nunca foi economia — foi escrutínio: um modelo cujos pesos são públicos pode ser examinado por pesquisadores independentes, testado quanto a viés e estudado sem autorização do fabricante.

Esse argumento continua válido em tese e ficou mais caro na prática. Auditar um modelo que exige sessenta aceleradores para rodar é atividade para quem tem sessenta aceleradores.

É a mesma dinâmica que se vê em outros campos onde a capacidade técnica se concentrou: a informação continua pública, e a capacidade de usá-la, não.
