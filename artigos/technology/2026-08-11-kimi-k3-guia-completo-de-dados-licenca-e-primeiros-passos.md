---
title: "Kimi K3: Guia Completo de Dados, Licença e Primeiros Passos"
subtitle: "Do tamanho dos pesos ao preço da API — tudo o que você precisa saber para começar agora"
description: "Em julho de 2026, a Moonshot AI lançou o Kimi K3 — 2,8 trilhões de parâmetros, arquitetura híbrida de atenção linear e pesos abertos sob uma licença própria. A cobertura inicial destacou o tamanho e a controvérsia geopolítica, mas deixou de fora os números que realmente importam para quem quer usar o modelo. Este artigo é o complemento que faltava: benchmarks detalhados com comparações diretas, uma análise completa da Kimi K3 License (o que é MIT, o que não é), os requisitos de hardware para inferência local (de 8 GB de RAM experimental a 64+ GPUs em produção), as três ferramentas de infraestrutura liberadas (MoonEP, FlashKDA, AgentEnv) e, acima de tudo, um guia prático de primeiros passos para desenvolvedores que querem começar a trabalhar com o Kimi K3 agora — pela API, pelo terminal ou pelo desktop."
date: 2026-08-11
status: publish
author: "Redação Duna Press"
categories: "technology"
formato: explicador
proveniencia: ia-assistido
revisor: Paulo Fernando De Barros
fonte_primaria: "https://arxiv.org/abs/2607.24653"
fonte_nome: "Arxiv - Computer Science"
data_do_fato: 2026-08-11
featuredImage: "https://images.unsplash.com/photo-1739036868260-c26b292cd85d?w=1600&auto=format&fit=crop&q=60"
photoAuthor: "Igor Omilaev"
photoSource: "Unsplash"
tags:
  - KIMI
  - Inteligência Artificial
---

# Kimi K3: O Que o Artigo (https://dunapress.org/moonshot-publica-os-pesos-do-kimi-k3-maior-modelo-aberto-de-ia-ja/) Não Te Contou — Guia Completo de Dados, Licença e Primeiros Passos

## 1. O modelo, em números concretos

O **Kimi K3** é um modelo de mistura de especialistas (MoE) com **2,8 trilhões de parâmetros totais** e **104 bilhões ativos por token**. Ele foi treinado com **quantização-aware** desde o estágio SFT, usando pesos em **MXFP4** e ativações em **MXFP8**.

A arquitetura é híbrida: **3 camadas de Kimi Delta Attention (KDA)** — uma atenção linear de estado fixo — para cada **1 camada de Gated MLA** (atenção completa). Isso significa que **75% do modelo** processa contexto longo com custo linear, não quadrático. O resultado prático: **janela de contexto de 1.048.576 tokens** (1 milhão) para entrada e saída.

O sistema MoE usa **896 especialistas roteados**, dos quais apenas **16 são ativados por token**, através do framework **Stable LatentMoE**. Para evitar o colapso de especialistas comum em MoEs grandes, a Moonshot introduziu o **Quantile Balancing**, que deriva a alocação de especialistas diretamente dos quantis das pontuações do roteador, eliminando um hiperparâmetro sensível de balanceamento.

A Moonshot afirma um ganho de **2,5× em eficiência de escala** sobre o Kimi K2. O modelo tem **93 camadas** e foi pós-treinado com nove políticas de RL especializadas em três domínios (codificação, agentes gerais e raciocínio), com três níveis de esforço de raciocínio cada (baixo, alto, máximo).

***

## 2. Benchmarks: onde ele ganha, onde perde, e por quanto

| Benchmark | Kimi K3 | Claude Fable 5 | GPT-5.6 Sol | DeepSeek V4.5 | Qwen 3.8 |
|-----------|---------|----------------|-------------|---------------|----------|
| **MMLU** | 89,5% | 94,6% | 93,8% | 88,7% | 87,9% |
| **MMLU-Pro** | 81,1% | — | — | — | — |
| **MMLU-Redux** | 92,7% | — | — | — | — |
| **HumanEval** | 93,3% | 96,2% | 94,7% | 90,8% | 88,4% |
| **MATH-500** | 97,4% | — | 97,8% | 96,4% | — |
| **MathVision** | 97,8% | — | — | — | — |
| **GPQA** | 93,5% | — | 89,6% | 82,6% | — |
| **GSM8K** | — | — | 99,3% | 99,0% | — |
| **Humanity's Last Exam** | 56,0% | — | — | — | — |
| **FrontierSWE** | 81,2% | — | — | — | 73,5% |
| **TerminalBench** | 88,3 | — | 88,8 | — | 86,6 |
| **BrowseComp** | 91,2% | — | — | — | — |
| **LiveBench** | 76,4% | — | — | — | — |
| **AIME 2025** | 49,5% | — | — | — | — |

*Fontes: llm-stats.com, TokenCalculator, relatório técnico da Moonshot*

### O que os números revelam:

- O K3 é **líder entre modelos abertos** na maioria das categorias, mas ainda **fica atrás dos proprietários de ponta** (Claude Fable 5 e GPT-5.6 Sol) em tarefas de conhecimento geral.

- Em **codificação de longo horizonte** (FrontierSWE, TerminalBench) e **raciocínio matemático avançado** (MATH-500, MathVision), ele empata ou supera muitos concorrentes.

- No **Humanity's Last Exam** — um benchmark brutal de conhecimento de fronteira — ele marca 56,0%, um salto enorme em relação ao K2, mas ainda abaixo dos líderes proprietários.

O **Intelligence Index da Artificial Analysis** posicionou o K3 em **terceiro lugar geral** (pontuação 57), atrás apenas do Claude Fable 5 e do GPT-5.6 Sol.

***

## 3. A licença Kimi K3: o que você pode fazer (e o que não pode)

A **Kimi K3 License** é construída sobre a estrutura MIT, com três camadas de restrição comerciais adicionadas:

### ✅ O que é permitido sem restrição

- Uso, modificação, distribuição e criação de obras derivadas (incluindo fine-tunes).

- Uso comercial em produtos finais (desde que não seja MaaS).

- Uso interno em empresas de qualquer tamanho.

### ⚠️ O que exige acordo separado com a Moonshot

- **Model as a Service (MaaS):** Se você oferece o K3 como serviço hospedado (API que dá ao terceiro controle sobre inputs, parâmetros ou dados de treinamento) e sua empresa (incluindo afiliadas) fatura **mais de US$ 20 milhões em qualquer período de 12 meses consecutivos**, precisa de contrato comercial separado.

- **Importante:** o cálculo de receita inclui **toda a receita do licenciado e afiliadas**, não apenas a receita gerada pelo K3.

### ⚠️ O que exige atribuição visível

- Se seu produto ou serviço comercial usando o K3 ultrapassar **100 milhões de usuários ativos mensais** OU **US$ 20 milhões em receita mensal**, você deve exibir **"Kimi K3" de forma proeminente na interface do usuário**.

### ✅ Isenções

- Uso **interno** (que não disponibiliza o modelo a terceiros).

- Uso através dos **produtos oficiais da Moonshot** ou **parceiros de inferência certificados**.

**Veredito prático:** para startups, pesquisadores e uso interno empresarial, a licença comporta-se como MIT. Para hyperscalers e provedores de nuvem que querem revender o K3, ela é uma porta de entrada para negociação comercial.

***

## 4. Como começar a trabalhar com Kimi K3 hoje

### A) API Oficial (a forma mais rápida)

A API é **compatível com o formato OpenAI**, então se você já usa o SDK da OpenAI, a mudança é mínima.

## Preços (oficiais):

- **Input com cache hit:** US$ 0,30 / milhão de tokens

- **Input sem cache:** US$ 3,00 / milhão de tokens

- **Output:** US$ 15,00 / milhão de tokens

A Moonshot reporta **taxa de cache hit acima de 90%** em workloads de codificação, graças à arquitetura Mooncake de inferência desagregada.

**Modelo:** `kimi-k3`  

**Base URL:** `https://api.moonshot.ai/v1`

## Exemplo de chamada (Python):

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["MOONSHOT_API_KEY"],
    base_url="https://api.moonshot.ai/v1",
)

response = client.chat.completions.create(
    model="kimi-k3",
    messages=[{"role": "user", "content": "Explique a arquitetura Kimi Delta Attention"}],
    reasoning_effort="max"  # ou "low", "high", ou desativado
)

```

### B) Kimi Work (trabalho de conhecimento)

Aplicativo desktop (Windows e Mac Apple Silicon) na versão 3.1.0+, com recursos de **Widgets** e **Dashboard** — componentes interativos gerados dentro do chat com conexão a dados locais ou plugins externos.

### C) Kimi Code (codificação no terminal)

Rode no terminal e selecione o K3 com o comando `/model`. O modelo suporta **"vision in the loop"** — iteração entre código e screenshots ao vivo para desenvolvimento de jogos, design de chips, EDA, etc.

### D) Kimi Enterprise

Para empresas: privacidade de dados enterprise-grade, separação completa entre contas pessoais e organizacionais, gerenciamento de membros.

***

## 5. Rodar localmente: a realidade dos números

### Pesos e armazenamento

- **Pesos originais (MXFP4):** ~1,56 TB no Hugging Face

- **Em BF16 (inference completa):** ~5.940 GB (quase 6 TB)

- **Em INT4 (quantizado):** ~1.515 GB de VRAM

### Hardware mínimo para inferência

- **Não roda em GPU única.** Nenhuma GPU individual suporta 1,56 TB de pesos.

- **Nó de 8 GPUs?** Nem mesmo oito GPUs de 192 GB cada (total ~1,5 TB) cobrem os pesos + KV cache + overhead de serviço.

- **Recomendação da Moonshot para produção:** **64+ aceleradores** em configuração de supernó com alta largura de banda de comunicação.

- **Mínimo viável:** cluster multi-nó com ~2 TB+ de memória GPU agregada e interconexão rápida.

### Alternativas de quantização (comunidade)

A Unsloth criou versões **GGUF** do K3:

| Quantização | Tamanho | Acurácia top-1 |
|-------------|---------|----------------|
| **Dynamic 1-bit** | 553–610 GB | ~78,9% |
| **Dynamic 2-bit** | 726–880 GB | ~90% |
| **Q8 (lossless)** | ~1,6 TB | ~100% |

Roda via **llama.cpp** ou **Unsloth Studio**. Há até um projeto experimental (**Kimi K3 in C**) que roda o modelo em CPU com apenas 8 GB de RAM, implementado em C99 puro — uma façanha de engenharia, não uma solução prática de produção.

**Veredito:** para 99,9% dos desenvolvedores, a **API oficial** é a única opção viável. Self-hosting só faz sentido em escala empresarial sustentada ou para pesquisa em infraestrutura.

***

## 6. As três ferramentas de infraestrutura liberadas

### MoonEP

Biblioteca de comunicação de alta performance para **expert-parallel** em MoEs de granularidade ultra-fina. Resolve o gargalo de comunicação all-to-all que tipicamente limita a eficiência de escalamento de MoEs grandes, mantendo desempenho de pico mesmo sob desbalanceamento de carga.

### FlashKDA

Implementação em kernel de alta performance do **Kimi Delta Attention**. Em GPUs NVIDIA H20, entrega **1,72× a 2,22× de aceleração** na latência de prefill em comparação com a baseline flash-linear-attention, e pode ser usado como backend drop-in replacement. A Moonshot também contribuiu uma implementação de prefix caching para KDA com a comunidade vLLM.

### AgentEnv

Sistema de sandbox desenvolvido em parceria com a **KVCache.ai**, projetado para treinamento de agentes em escala. Fornece sandboxes de alta fidelidade e forte isolamento, com suporte a **snapshot, restore e fork** rápidos para lidar com workflows de agente massivamente paralelos.

Essas ferramentas não são meros bônus — são **componentes críticos** que permitiram treinar o K3 em escala 2,8T. A liberação delas indica que a Moonshot quer que a comunidade não apenas use o modelo, mas também **reproduza e estenda** a stack de treinamento.

***

## 7. Comparação direta: Kimi K3 vs. os concorrentes abertos

| Aspecto | Kimi K3 | DeepSeek V4 Flash | Qwen 3.8 Max |
|---------|---------|-------------------|--------------|
| **Parâmetros (total/ativos)** | 2,8T / 104B | 284B / 13B | 2,4T / 95B |
| **Contexto** | 1M tokens | 1M tokens | 1M tokens |
| **Multimodal** | Texto, imagem, vídeo | Texto apenas | Texto, imagem, vídeo |
| **Licença de pesos** | Kimi K3 License (custom) | MIT | Ainda não publicada |
| **API Input/Output** | $3,00 / $15,00 | $0,14 / $0,28 | $2,00 / $6,00 |
| **Pesos disponíveis** | ✅ Sim (MXFP4) | ✅ Sim | ⏳ Prometido, não lançado |
| **Inteligência Index (Artificial Analysis)** | 57 | 50 | N/A ainda |
| **Melhor uso** | Codificação longa, agentes, pesquisa | Custo baixo, texto, MIT puro | Ecossistema Alibaba, multimodal |

## Onde o K3 se destaca:

- **Maior modelo aberto com pesos disponíveis** (2,8T vs. 2,4T do Qwen).

- **Líder independente em benchmarks abertos** (Intelligence Index 57).

- **Pesos baixáveis agora** — diferente do Qwen 3.8 Max, que ainda não liberou os pesos.

- **Codificação de longo horizonte** (FrontierSWE, TerminalBench) é seu território mais forte.

## Onde ele perde:

- **Custo de API:** o output a $15/MTok é **53× mais caro** que o DeepSeek V4 Flash e **2,5× mais caro** que o Qwen 3.8 Max.

- **Licença:** MIT do DeepSeek é mais permissiva; a licença customizada do K3 cria fricção para MaaS em escala.

- **Tamanho de deploy:** 1,56 TB de pesos MXFP4 tornam o self-hosting inviável para a maioria.

***

## 8. O que ainda não sabemos (lacunas do relatório técnico)

Apesar dos 47 páginas, o relatório técnico omite:

- **Número total de tokens de pré-treinamento**

- **Custo total de treinamento** (estimativas externas sugerem centenas de milhões de dólares, mas não há confirmação).

- **Detalhes completos do dataset** (proporção de código, web, multimodal, sintético).

- **Resultados de segurança independentes** — os testes de cibersegurança internos encontraram 16 vulnerabilidades desconhecidas, mas uma avaliação independente registrou **zero casos de execução arbitrária de código** em 41 tarefas.

***

## 9. Guia de primeiros passos para você começar agora

### Passo 1: API (5 minutos)

1. Acesse [platform.kimi.ai](https://platform.kimi.ai) e crie uma conta.

2. Gere uma API Key na seção "API Keys".

3. Instale o SDK: `pip install openai`.

4. Configure a `base_url` para `https://api.moonshot.ai/v1` e o modelo `kimi-k3`.

5. Teste com um prompt de codificação ou raciocínio longo.

### Passo 2: Explore os modos de raciocínio

O K3 tem três níveis de esforço de raciocínio: `low`, `high`, `max`. No lançamento, o modo padrão é `max`. Teste diferentes níveis para encontrar o equilíbrio entre qualidade e latência para seu caso de uso.

### Passo 3: Teste capacidades multimodais

Envie imagens e vídeos junto com o prompt. O modelo processa texto, imagem e vídeo no **mesmo corpo** — não usa adaptadores visuais separados.

### Passo 4: Experimente Kimi Code

Se você é desenvolvedor, instale o Kimi Code no terminal e use o comando `/model kimi-k3`. Teste workflows de "vision in the loop" — por exemplo, envie um screenshot de um bug e peça para o modelo gerar o fix.

### Passo 5: Avalie se precisa dos pesos locais

A menos que você tenha acesso a um cluster com 64+ GPUs e interconexão de alta largura de banda, os pesos locais são para pesquisa, não para produção. Para produção, fique na API.

### Passo 6: Leia o relatório técnico

O PDF de 47 páginas está disponível no repositório oficial da Moonshot no Hugging Face. É leitura obrigatória se você quer entender as decisões de arquitetura.

***

## Conclusão

O Kimi K3 não é apenas "o maior modelo aberto já lançado". Ele é um **sistema completo**: modelo + relatório técnico + kernels otimizados + biblioteca de comunicação + sandbox de agentes. A Moonshot está jogando um jogo de ecossistema, não apenas de benchmarks.

Para você, que quer trabalhar com Kimi, a mensagem é clara: **comece pela API**. Ela é compatível com OpenAI, tem cache agressivo (90%+ hit rate em código) e te dá acesso ao modelo mais capaz da Moonshot sem precisar de um data center. Os pesos abertos são um presente para a comunidade de pesquisa e para grandes empresas com infraestrutura própria — mas a porta de entrada para 99% dos desenvolvedores é a API.

A proximidade com os modelos proprietários de ponta é real. A superioridade absoluta, ainda não. Mas a velocidade com que essa proximidade foi alcançada — e a generosidade da liberação técnica — é o que torna o K3 um marco.

***

*Dados compilados a partir do relatório técnico da Moonshot, benchmarks independentes (Artificial Analysis, llm-stats.com, TokenCalculator), documentação oficial da API e análises de especialistas. Última atualização: agosto de 2026.*
