---
title: "Desenvolvedores acham que a IA os deixa 20% mais rápidos. O cronômetro diz que estão 19% mais lentos"
subtitle: "O único ensaio randomizado já feito sobre produtividade com IA mediu o oposto do que todos esperavam. E o rastro no código é pior: duplicação em alta de 81%, refatoração em queda de 70%"
description: "Estudo da METR acompanhou 16 desenvolvedores experientes em 246 tarefas reais. Eles previram ganho de 24%. Sentiram ganho de 20%. Perderam 19% do tempo."
date: 2026-08-27
status: publish
author: "Redação Duna Press"
categories: "tecnologia"
formato: reportagem
proveniencia: humano
revisor: Paulo Fernando de Barros
fonte_primaria: "https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/"
fonte_nome: "METR, arXiv, GitClear e Google DORA"
data_do_fato: 2026-02-01
featuredImage: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=1200&q=75"
photoAuthor: "Chris Ried"
photoSource: "Unsplash"
tags:
  - inteligencia artificial
  - programacao
  - produtividade
  - divida tecnica
  - desenvolvedores
  - tecnologia
---

Há uma diferença de 39 pontos percentuais entre o que os desenvolvedores acham que a inteligência artificial faz por eles e o que ela de fato faz. Essa distância não vem de pesquisa de opinião nem de blog corporativo. Vem do único ensaio clínico randomizado já conduzido sobre o assunto.

Em julho de 2025, a organização de pesquisa METR publicou os resultados de um experimento com 16 desenvolvedores experientes de projetos abertos de grande porte. Antes de começar, eles previram que o uso de ferramentas de IA reduziria o tempo de conclusão das tarefas em 24%. Ao terminar, avaliaram que haviam sido cerca de 20% mais rápidos.

A medição do tempo real mostrou que levaram **19% mais tempo** quando podiam usar IA.

## Por que este estudo pesa mais que os outros

Quase tudo o que se publica sobre produtividade com IA depende de duas coisas frágeis: tarefas artificiais e autoavaliação. A METR eliminou as duas.

Os participantes eram mantenedores de repositórios com mais de um milhão de linhas de código e mais de 22 mil estrelas, nos quais trabalhavam havia em média cinco anos. Cada um apresentou uma lista de problemas reais do próprio projeto — correções, funcionalidades, refatorações que fariam de qualquer modo. Foram 246 tarefas ao todo, de aproximadamente duas horas cada.

Cada tarefa foi sorteada para uma de duas condições: uso de IA permitido ou proibido. Quando permitido, os desenvolvedores usavam as ferramentas que quisessem — na prática, o editor Cursor Pro combinado ao Claude 3.5 e 3.7 Sonnet, modelos de fronteira à época. Todos gravaram a tela enquanto trabalhavam e receberam 150 dólares por hora de participação.

Os autores — Joel Becker, Nate Rush, Beth Barnes e David Rein — registram no artigo que esperavam encontrar aceleração. A frase está no texto: a expectativa inicial era, de modo geral, de ganho de velocidade.

Em fevereiro de 2026 a METR repetiu a medição com ferramentas do fim de 2025. A estimativa central permaneceu em torno de 18% de lentidão.

## Onde o tempo se perde

O experimento não explica sozinho o mecanismo, mas a descrição do trabalho ajuda.

Em bases maduras, a maior parte do esforço não é digitar. É entender restrições implícitas, preservar estilo, notar casos extremos, respeitar testes existentes e manter abstrações de pé — fazer uma alteração que sobreviva à revisão de outro humano.

Uma ferramenta pode tornar cada momento isolado mais fácil e ainda assim acrescentar sobrecarga ao conjunto. Ela redige rápido; o desenvolvedor então lê, confere, corrige, adapta e integra. Reduz o desconforto de começar e aumenta silenciosamente o tempo de revisão depois.

É essa assimetria que explica o desencontro entre percepção e relógio. A sensação de aceleração é real. Ela simplesmente não sobrevive ao contato com o cronômetro.

## O rastro que fica no código

O segundo corpo de evidência vem de outra direção. A GitClear analisou, em parceria com a GitKraken, 623 milhões de alterações reais de código entre 2023 e 2026, rastreando sete indicadores de qualidade estrutural.

A duplicação de blocos — trechos de cinco ou mais linhas repetidas — subiu de 40,3 para 73,0 por milhão de linhas alteradas, alta de 81% e o maior nível já registrado.

A refatoração fez o caminho inverso. O código movido, indicador de reorganização e reuso, caiu de 21% das linhas alteradas em 2022 para 3,8% em 2026. Chamadas de função entre arquivos recuaram 35%. A manutenção de código legado caiu 74% em relação a 2022. O mascaramento de erros aumentou 47%.

Um bloco duplicado cria o que a GitClear chama de imposto de propagação: quem altera uma cópia herda a obrigação de encontrar e avaliar todas as outras, em arquivos e domínios que pode não conhecer. Pesquisas associam código clonado a taxas de defeito entre 15% e 50% mais altas.

O relatório DORA do Google, de 2024, mediu o efeito por outro ângulo: cada 25% a mais de uso de IA correspondia a 7,2% mais instabilidade nas entregas.

## O que os dados não dizem

Nenhum desses estudos afirma que IA atrapalha todo desenvolvedor em toda situação, e a própria METR faz questão de marcar o limite.

O resultado vale para aquele grupo, naquelas tarefas, naqueles repositórios e com as ferramentas daquele período. Não mede iniciantes. Não mede projeto começando do zero, geração de código repetitivo ou protótipo descartável — contextos em que os ganhos costumam aparecer.

Uma pesquisa da própria GitClear, de janeiro de 2026, acrescenta nuance incômoda para os dois lados: usuários intensos de IA produzem de quatro a dez vezes mais que os não usuários, mas quase toda essa diferença já existia antes das ferramentas. Comparados a si mesmos no passado, o ganho de velocidade foi de 25%.

O achado mais transferível do experimento da METR talvez não seja sobre programação. É sobre medição. Dezesseis profissionais experientes, trabalhando no próprio código, com a tela gravada, erraram em 39 pontos percentuais a avaliação do próprio desempenho — e erraram na direção que confirmava o que esperavam encontrar.
