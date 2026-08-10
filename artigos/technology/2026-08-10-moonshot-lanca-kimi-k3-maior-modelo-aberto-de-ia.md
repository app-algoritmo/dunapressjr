---
title: "Moonshot publica o Kimi K3, maior modelo aberto de IA já divulgado"
subtitle: "Com 2,8 trilhões de parâmetros e pesos liberados em 27 de julho, o modelo chinês reduz a distância para os sistemas fechados americanos — e reacende a disputa sobre destilação e controle de chips"
categories: tecnologia
date: 2026-08-10
autor: Redação Duna Press
proveniencia: ia
revisor: Paulo Fernando de Barros
status: publish
revisao_humana: concluida
featuredImage: "https://images.unsplash.com/photo-1674027444485-cec3da58eef4?w=1600&auto=format&fit=crop&q=75"
photoAuthor: "Growtika"
photoSource: "Unsplash"
tags:
  - Inteligência Artificial
  - KIMI IA
  - China
---

A Moonshot AI, startup de Pequim financiada, entre outros, pela Alibaba,
lançou em 16 de julho de 2026 o Kimi K3, durante a Conferência Mundial de
Inteligência Artificial em Xangai. O modelo tem 2,8 trilhões de parâmetros e
é, segundo a empresa, o maior de pesos abertos já disponibilizado. Onze dias
depois, em 27 de julho, os pesos completos foram publicados no Hugging Face,
com 96 fragmentos, arquivos de configuração e relatório técnico, sob uma
licença própria batizada de Kimi K3 License.

A sequência de datas importa mais que o número de parâmetros. Entre o anúncio
e a liberação dos pesos, o modelo saiu de promessa a artefato baixável — e foi
nesse intervalo que o mercado, os laboratórios americanos e o governo dos
Estados Unidos reagiram.

## O que o modelo é

O Kimi K3 é um modelo de mistura de especialistas com 104 bilhões de
parâmetros ativos e janela de contexto de 1.048.576 tokens, com capacidade
multimodal nativa em texto e visão. A Moonshot atribui o ganho de eficiência a
duas mudanças de arquitetura, Kimi Delta Attention e Attention Residuals — a
primeira já havia aparecido no Kimi Linear, de outubro de 2025.

A própria empresa reconhece que o modelo não lidera entre os sistemas fechados.
O que ela afirma é ter estabelecido um novo patamar entre os abertos. Em
avaliações independentes, o K3 apareceu em quarto lugar no Artificial Analysis
Intelligence Index.

A escala aberta tem um custo que raramente aparece nas manchetes: a Moonshot
recomenda configurações com pelo menos 64 aceleradores para rodar o modelo.
Aberto não quer dizer acessível.

## Três dias até o limite de capacidade

Em 19 de julho, três dias após o lançamento, a Moonshot suspendeu novas
assinaturas. A capacidade de GPU havia chegado ao limite diante da demanda. A
empresa priorizou os usuários existentes e anunciou reabertura gradual.

A ironia é que o problema de hardware que a arquitetura tentava contornar
reapareceu pelo lado da operação.

## A acusação de destilação

Em 22 de julho, o diretor do Escritório de Política de Ciência e Tecnologia da
Casa Branca acusou a Moonshot de operar uma plataforma interna de destilação
contra o Claude Fable 5, da Anthropic, usando chips da Nvidia sob restrição de
exportação obtidos por meio da Tailândia. O secretário do Tesouro, Scott
Bessent, mencionou a possibilidade de sanções e de inclusão em lista de
entidades restritas.

A objeção mais direta à acusação é cronológica: os testes do K3 seriam
anteriores ao lançamento do Fable 5. A Moonshot nega a prática.

## O que muda para quem usa

Para desenvolvedores e empresas, o K3 reforça uma linha que já vinha de
DeepSeek, Qwen e GLM: modelos de fronteira, ou perto dela, disponíveis para
customização local, com menor dependência de interfaces estrangeiras. A
vantagem de preço, porém, é menos direta do que as tabelas sugerem — o modelo
consome mais tokens por tarefa, o que corrói parte da diferença.

A licença também não é a de um projeto de código aberto clássico. Ela impõe
condições, e isso separa o K3 de modelos plenamente permissivos.

## O que ainda não está resolvido

Nenhuma das medições de eficiência divulgadas pela Moonshot foi verificada de
forma independente até o fechamento desta edição. A restrição americana a
chips avançados segue sendo o limite estrutural das empresas chinesas, e é
justamente ela que torna a eficiência de arquitetura uma vantagem competitiva
em vez de um detalhe técnico.

O que o Kimi K3 demonstra não é superioridade. É proximidade — e a velocidade
com que ela foi alcançada.
