---
title: "IA pode detectar os primeiros sinais da doença de Alzheimer"
date: 2023-02-12
status: publish
author: debarrospaulo
categories:
  - Technology
---

Os algoritmos de inteligência artificial por trás do programa chatbot ChatGPT – que chamou a atenção por sua capacidade de gerar respostas escritas semelhantes às humanas para algumas das perguntas mais criativas – podem um dia ajudar os médicos a detectar a doença de Alzheimer em seus estágios iniciais. Pesquisas da Escola de Engenharia Biomédica, Ciências e Sistemas de Saúde da Drexel University demonstraram recentemente que o programa GPT-3 da OpenAI pode identificar pistas da fala espontânea com 80% de precisão na previsão dos estágios iniciais da demência.

Relatado na revista *PLOS Digital Health* , o estudo Drexel é o mais recente de uma série de esforços para mostrar a eficácia dos programas de processamento de linguagem natural para a previsão precoce da doença de Alzheimer – alavancando pesquisas atuais que sugerem que o comprometimento da linguagem pode ser um indicador precoce de distúrbios neurodegenerativos.

**Encontrar um sinal precoce**

A prática atual para diagnosticar a doença de Alzheimer geralmente envolve uma revisão do histórico médico e um longo conjunto de avaliações e testes físicos e neurológicos. Embora ainda não haja cura para a doença, identificá-la precocemente pode dar aos pacientes mais opções terapêuticas e de suporte. Como o comprometimento da linguagem é um sintoma em 60-80% dos pacientes com demência, os pesquisadores têm se concentrado em programas que podem captar pistas sutis – como hesitação, cometer erros de gramática e pronúncia e esquecer o significado das palavras – como um rápido teste que poderia indicar se um paciente deve ou não ser submetido a um exame completo.

“Sabemos por pesquisas em andamento que os efeitos cognitivos da doença de Alzheimer podem se manifestar na produção da linguagem”, disse Hualou Liang, PhD, professor da Escola de Engenharia Biomédica, Ciência e Sistemas de Saúde de Drexel e coautor da pesquisa. “Os testes mais comumente usados ​​para a detecção precoce da doença de Alzheimer analisam características acústicas, como pausa, articulação e qualidade vocal, além de testes de cognição. Mas acreditamos que a melhoria dos programas de processamento de linguagem natural fornece outro caminho para apoiar a identificação precoce de Alzheimer”.

**Um programa que ouve e aprende**

O GPT-3, oficialmente a terceira geração do transformador pré-treinado geral (GPT) da OpenAI, usa um algoritmo de aprendizado profundo – treinado pelo processamento de vastas faixas de informações da Internet, com foco particular em como as palavras são usadas e como a linguagem é construída . Esse treinamento permite que ele produza uma resposta semelhante à humana para qualquer tarefa que envolva linguagem, desde respostas a perguntas simples até a escrita de poemas ou ensaios.

O GPT-3 é particularmente bom em “aprendizado de dados zero” – o que significa que pode responder a perguntas que normalmente exigiriam conhecimento externo que não foi fornecido. Por exemplo, pedir ao programa para escrever “Notas de Cliff” de um texto normalmente exigiria uma explicação de que isso significa um resumo. Mas o GPT-3 passou por treinamento suficiente para entender a referência e se adaptar para produzir a resposta esperada.

“A abordagem sistêmica do GPT3 para análise e produção de linguagem o torna um candidato promissor para identificar as características sutis da fala que podem prever o início da demência”, disse Felix Agbavor, pesquisador de doutorado na Escola e principal autor do artigo. “Treinar o GPT-3 com um enorme conjunto de dados de entrevistas – algumas das quais com pacientes com Alzheimer – forneceria as informações necessárias para extrair padrões de fala que poderiam ser aplicados para identificar marcadores em futuros pacientes”.

**Buscando Sinais de Fala**

Os pesquisadores testaram sua teoria treinando o programa com um conjunto de transcrições de uma parte de um conjunto de dados de gravações de fala compiladas com o apoio dos Institutos Nacionais de Saúde especificamente com o objetivo de testar a capacidade dos programas de processamento de linguagem natural de prever a demência. O programa capturou características significativas do uso da palavra, estrutura da frase e significado do texto para produzir o que os pesquisadores chamam de “incorporação” – um perfil característico da fala do Alzheimer.

Eles então usaram a incorporação para treinar novamente o programa – transformando-o em uma máquina de triagem de Alzheimer. Para testá-lo, eles pediram ao programa para revisar dezenas de transcrições do conjunto de dados e decidir se cada uma delas foi ou não produzida por alguém que estava desenvolvendo a doença de Alzheimer.

Executando dois dos principais programas de processamento de linguagem natural no mesmo ritmo, o grupo descobriu que o GPT-3 teve um desempenho melhor do que ambos, em termos de identificação precisa de exemplos de Alzheimer, identificação de exemplos não-Alzheimer e com menos casos perdidos do que ambos os programas.

Um segundo teste usou a análise textual do GPT-3 para prever a pontuação de vários pacientes do conjunto de dados em um teste comum para prever a gravidade da demência, chamado Mini-Mental State Exam (MMSE).

A equipe então comparou a precisão da previsão do GPT-3 com a de uma análise usando apenas os recursos acústicos das gravações, como pausas, intensidade da voz e fala arrastada, para prever a pontuação do MMSE. O GPT-3 provou ser quase 20% mais preciso na previsão dos escores do MMSE dos pacientes.

“Nossos resultados demonstram que a incorporação de texto, gerada pelo GPT-3, pode ser usada de forma confiável não apenas para detectar indivíduos com doença de Alzheimer de controles saudáveis, mas também inferir a pontuação do teste cognitivo do sujeito, ambos baseados apenas em dados de fala”, escreveram eles. . “Mostramos ainda que a incorporação de texto supera a abordagem convencional baseada em recursos acústicos e até mesmo funciona competitivamente com modelos ajustados. Esses resultados, todos juntos, sugerem que a incorporação de texto baseada em GPT-3 é uma abordagem promissora para avaliação AD e tem o potencial para melhorar o diagnóstico precoce da demência.”

**Continuando a Pesquisa**

Para aproveitar esses resultados promissores, os pesquisadores planejam desenvolver um aplicativo da Web que possa ser usado em casa ou no consultório médico como uma ferramenta de pré-triagem.

“Nossa prova de conceito mostra que esta pode ser uma ferramenta simples, acessível e adequadamente sensível para testes baseados na comunidade”, disse Liang. “Isso pode ser muito útil para triagem precoce e avaliação de risco antes de um diagnóstico clínico”.

**Fonte da história:**

[Materiais](https://drexel.edu/news/archive/2022/December/GPT-3-alzheimers-disease) fornecidos pela [**Drexel University**](https://drexel.edu/).

**Referência do periódico** :

- Felix Agbavor, Hualou Liang. **Prevendo a demência da fala espontânea usando grandes modelos de linguagem** . *PLOS Saúde Digital* , 2022; 1 (12): e0000168 DOI: [10.1371/journal.pdig.0000168](http://dx.doi.org/10.1371/journal.pdig.0000168)
