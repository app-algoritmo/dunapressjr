---
title: "Moonshot publica os pesos do Kimi K3, maior modelo aberto de IA já divulgado"
subtitle: "Com 2,8 trilhões de parâmetros e terceiro lugar no principal índice independente, o modelo chinês encurta para semanas a distância que se media em meses — e reacende a disputa sobre destilação e controle de chips"
description: "Onze dias separaram o anúncio da liberação dos pesos. Nesse intervalo, a Casa Branca acusou a empresa de destilar um modelo americano."
date: 2026-08-10
status: publish
author: "Redação Duna Press"
categories: "technology"
formato: analise
proveniencia: ia-assistido
fonte_primaria: "https://huggingface.co/moonshotai/Kimi-K3"
data_do_fato: 2026-07-16
featuredImage: "https://images.unsplash.com/photo-1674027444485-cec3da58eef4?w=1600&auto=format&fit=crop&q=75"
photoAuthor: "Growtika"
photoSource: "Unsplash"
tags:
  - Inteligência Artificial
  - Moonshot AI
  - Kimi K3
  - China
  - código aberto
---

A Moonshot AI, laboratório de Pequim, anunciou em 16 de julho de 2026 o Kimi
K3, durante a Conferência Mundial de Inteligência Artificial em Xangai. Onze
dias depois, em 27 de julho, publicou os pesos completos no Hugging Face, junto
com o relatório técnico e três ferramentas de infraestrutura usadas no
treinamento, sob uma licença própria chamada Kimi K3 License.

A sequência de datas importa mais que o número de parâmetros. Entre o anúncio
e a liberação dos pesos, o modelo saiu de promessa a artefato baixável — e foi
nesse intervalo que o mercado, os laboratórios americanos e o governo dos
Estados Unidos reagiram.

## O que o modelo é

O Kimi K3 tem 2,8 trilhões de parâmetros, quase o triplo do Kimi K2.5, que
sucede. É um modelo de mistura de especialistas construído sobre um arranjo
que a empresa chama de Stable LatentMoE: um conjunto de 896 especialistas dos
quais apenas 16 são acionados por token, o que resulta em 104 bilhões de
parâmetros ativos. A esparsidade é o ponto — o modelo é enorme em capacidade
armazenada e comparativamente barato em capacidade usada.

A arquitetura combina Kimi Delta Attention, uma variante de atenção linear que
substitui a matriz quadrática por convoluções curtas e atualizações de estado
controladas, com blocos de Attention Residuals que regulam o fluxo de
informação ao longo da profundidade da rede. A Moonshot atribui a esse conjunto
um ganho de cerca de 2,5 vezes em eficiência de escala sobre a geração
anterior. O modelo entende texto, imagem e vídeo no mesmo corpo, com janela de
contexto de um milhão de tokens.

A empresa é incomumente franca sobre onde está: afirma que o K3 ainda fica
atrás dos modelos proprietários mais poderosos no conjunto geral, enquanto
lidera todo o resto. Os números sustentam a formulação. Nas 33 linhas públicas
da tabela de lançamento, o K3 aparece em primeiro ou empatado em primeiro em
oito, à frente de qualquer outro modelo aberto em praticamente todas, e em
geral a poucos pontos da fronteira. O Artificial Analysis o posicionou em
terceiro no Intelligence Index, atrás somente do Claude Fable 5, da Anthropic,
e do GPT-5.6 Sol, da OpenAI.

## Aberto não quer dizer acessível

A recepção foi rápida a ponto de virar dado: o diretor-executivo do Hugging
Face registrou que o K3 chegou ao topo da lista de tendências da plataforma com
mais de 4 mil curtidas em trinta minutos, o lançamento de crescimento mais
veloz já visto ali.

Baixar, porém, é outra história. Os fragmentos em BF16 somam cerca de 594
gigabytes, sem contar o cache de chaves e valores. Rodar o modelo exige
infraestrutura de dezenas de aceleradores. A abertura dos pesos amplia quem
pode estudar e adaptar o modelo; não amplia, na mesma medida, quem pode
executá-lo.

O limite apareceu também do lado da empresa. Em 19 de julho, três dias após o
anúncio, a Moonshot suspendeu novas assinaturas porque a capacidade de GPU
havia chegado ao teto diante da demanda. Priorizou os usuários existentes e
prometeu reabertura gradual.

## A acusação de destilação

Em 22 de julho, o diretor do Escritório de Política de Ciência e Tecnologia da
Casa Branca acusou a Moonshot de operar uma plataforma interna de destilação
contra o Claude Fable 5, usando chips da Nvidia sob restrição de exportação
obtidos por meio da Tailândia. O secretário do Tesouro, Scott Bessent,
mencionou a possibilidade de sanções e de inclusão em lista de entidades
restritas.

A objeção mais direta é cronológica: os testes do K3 seriam anteriores ao
lançamento do Fable 5. A Moonshot nega a prática.

Vale registrar quem falou. A acusação partiu do governo americano, não da
Anthropic, e a distinção não é de detalhe — uma coisa é a disputa comercial
entre laboratórios, outra é a política de controle de exportação de um Estado.

## O que muda para quem usa

Para desenvolvedores e empresas, o K3 reforça uma linha que já vinha de
DeepSeek, Qwen e GLM: modelos de fronteira, ou perto dela, disponíveis para
adaptação local, com menor dependência de interfaces estrangeiras.

A licença, no entanto, não é a de um projeto de código aberto clássico. A Kimi
K3 License impõe condições próprias, o que separa o modelo dos plenamente
permissivos. Chamá-lo de aberto é correto no sentido de pesos disponíveis, e
impreciso no sentido de liberdade irrestrita de uso.

## O que ainda não está resolvido

As medições de eficiência divulgadas pela Moonshot não foram verificadas de
forma independente até o fechamento desta edição. A restrição americana a chips
avançados segue sendo o limite estrutural das empresas chinesas, e é justamente
ela que transforma eficiência de arquitetura em vantagem competitiva, e não em
detalhe técnico.

O que o Kimi K3 demonstra não é superioridade. É proximidade — e a velocidade
com que ela foi alcançada.
