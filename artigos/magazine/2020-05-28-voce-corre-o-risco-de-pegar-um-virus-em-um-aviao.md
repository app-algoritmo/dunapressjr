---
title: Você corre o risco de pegar um vírus em um avião?
date: 2020-05-28
status: publish
author: Paulo Fernando De Barros
categories:
- Magazine
---


Justo ou não, os aviões têm reputação de germes. No entanto, existem maneiras de minimizar os riscos. Esta pesquisa é usada especialmente para viagens aéreas, onde há um risco aumentado de infecção ou doença contagiosa, como o recente surto mundial de coronavírus, que causa a doença de COVID-19.

Pesquisas históricas baseadas em movimentos de grupos de humanos e animais sugerem três regras simples:

- afaste-se daqueles que estão muito próximos.
- mova-se para aqueles que estão longe.
- coincidir com a direção do movimento de seus vizinhos.

Esta pesquisa é usada especialmente para viagens aéreas, onde há um risco aumentado de infecção ou doença contagiosa, como o recente surto mundial de coronavírus, que causa a doença de COVID-19.

"As companhias aéreas usam várias zonas no embarque", disse Ashok Srinivasan, professor do Departamento de Ciência da Computação da Universidade da Flórida Ocidental. "Ao embarcar em um avião, as pessoas são bloqueadas e forçadas a ficar perto da pessoa que coloca a bagagem na lixeira - as pessoas estão muito próximas umas das outras. Esse problema é exacerbado quando muitas zonas são usadas. O desembarque é muito mais suave e rápido - há não há tanto tempo para ser infectado. "

Srinivasan é o principal pesquisador de novas pesquisas sobre modelos de dinâmica de pedestres que foram usadas recentemente na análise de procedimentos para reduzir o risco de propagação de doenças em aviões. A pesquisa foi publicada na revista *PLOS ONE* em março de 2020.

Por muitos anos, os cientistas confiaram no modelo SPED (Self Propelled Entity Dynamics), um modelo de força social que trata cada indivíduo como uma partícula pontual, análoga a um átomo em simulações de dinâmica molecular. Em tais simulações, as forças atraentes e repulsivas entre átomos governam o movimento dos átomos. O modelo SPED modifica o código e substitui átomos por humanos.

"[O modelo SPED] altera os valores dos parâmetros que governam as interações entre os átomos, para que eles reflitam as interações entre os seres humanos, mantendo a mesma forma funcional", disse Srinivasan.

Srinivasan e seus colegas usaram o modelo SPED para analisar o risco de um surto de ebola em 2015, amplamente coberto por veículos de notícias em todo o mundo. No entanto, uma limitação do modelo SPED é que ele é lento - o que dificulta a tomada de decisões oportunas. As respostas são necessárias rapidamente em situações como um surto como o COVID-19.

Os pesquisadores decidiram que havia uma necessidade de um modelo que pudesse simular os mesmos aplicativos que o SPED, sendo muito mais rápido. Eles propuseram o modelo CALM (para movimento linear restrito de indivíduos em uma multidão). O CALM produz resultados semelhantes ao SPED, mas não se baseia no código MD. Em outras palavras, o CALM foi projetado para executar rapidamente.

Como o SPED, o CALM foi projetado para simular movimentos em passagens lineares estreitas. Os resultados de suas pesquisas mostram que o CALM executa quase 60 vezes mais rápido que o modelo SPED. Além do ganho de desempenho, os pesquisadores também modelaram comportamentos adicionais de pedestres.

"O modelo CALM superou as limitações do SPED quando são necessárias decisões em tempo real", disse Srinivasan.

**Trabalho computacional usando Frontera**

Os cientistas projetaram o modelo CALM a partir do zero para que ele funcionasse com eficiência em computadores, especialmente em GPUs (unidades de processamento gráfico).

Para sua pesquisa, Srinivasan e colegas usaram o Frontera, o supercomputador nº 5 mais poderoso do mundo e o supercomputador acadêmico mais rápido, de acordo com os rankings de novembro de 2019 da organização Top500. Frontera está localizado no Texas Advanced Computing Center e é apoiado pela National Science Foundation.

"Assim que a Blue Waters começou a ser desativada, a Frontera foi a escolha natural, já que era a nova máquina capitânia financiada pela NSF", disse Srinivasan. "Uma pergunta que você tem é se gerou um número suficiente de cenários para cobrir o leque de possibilidades. Verificamos isso gerando histogramas de quantidades de interesse e verificando se o histograma converge. Usando o Frontera, conseguimos realizar simulações suficientemente grandes. agora sabemos como é uma resposta precisa ".

Na prática, não é possível fazer previsões precisas devido a incertezas inerentes, especialmente nos estágios iniciais de uma epidemia - é isso que torna desafiador o aspecto computacional desta pesquisa.

"Precisávamos gerar um grande número de cenários possíveis para cobrir o leque de possibilidades. Isso o torna intensivamente computacionalmente", disse Srinivasan.

A equipe validou seus resultados examinando os tempos de desembarque em três tipos diferentes de aviões. Como uma única simulação não captura a variedade de padrões de movimento humano, eles realizaram simulações com 1.000 combinações diferentes de valores e compararam com os dados empíricos.

Usando o subsistema de GPU da Frontera, os pesquisadores conseguiram reduzir o tempo de computação para 1,5 minutos. "O uso das GPUs acabou sendo uma escolha feliz, porque conseguimos implantar essas simulações na emergência COVID-19. As GPUs da Frontera são um meio de gerar respostas rapidamente".

**Mas espere - os modelos não capturam eventos extremos? **Em termos de preparação geral, Srinivasan quer que as pessoas entendam que os modelos científicos geralmente não capturam eventos extremos com precisão.

Embora tenha havido estudos empíricos completos em vários vôos para entender o comportamento humano e a limpeza das superfícies e do ar, um grande surto de infecção é um evento extremo - dados de situações típicas podem não capturá-lo.

Existem cerca de 100.000 voos em um dia médio. Um evento de probabilidade muito baixa pode levar a surtos frequentes de infecção apenas porque o número de vôos é muito grande. Embora os modelos tenham previsto a transmissão de infecções em aviões como improvável, houve vários surtos conhecidos.

Srinivasan oferece um exemplo.

"Geralmente, acredita-se que a infecção espalhada nos aviões ocorra duas filas na frente e atrás do paciente", disse ele. "Durante o surto de SARS em 2002, nos poucos vôos com infecção disseminada, isso era verdade. No entanto, um único surto foi responsável por mais da metade dos casos, e metade dos infectados estavam sentados a mais de duas filas de distância naquele voo. Pode-se ficar tentado a encarar esse surto como um desvio. Mas o "desvio" teve o maior impacto e, portanto, as pessoas a mais de duas filas de distância representaram um número significativo de pessoas infectadas com SARS nos voos ".

Atualmente, no que diz respeito ao COVID-19, acredita-se que a pessoa infectada típica sofra 2,5 outras pessoas. No entanto, houve comunidades em que um único 'super espalhador' infectou um grande número de pessoas e desempenhou o papel principal em um surto. O impacto de tais eventos extremos e a dificuldade em modelá-los com precisão tornam a previsão difícil, de acordo com Srinivasan.

"Em nossa abordagem, não pretendemos prever com precisão o número real de casos", disse Srinivasan. "Em vez disso, tentamos identificar vulnerabilidades em diferentes políticas ou opções de procedimentos, como diferentes procedimentos de embarque em um avião. Geramos um grande número de cenários possíveis que podem ocorrer e examinamos se uma opção é consistentemente melhor que a outra. Se for , pode ser considerado mais robusto. Em um ambiente de tomada de decisão, pode-se escolher a opção mais robusta, em vez de confiar nos valores esperados das previsões ".

**Alguns conselhos práticos**

Srinivasan também oferece alguns conselhos práticos para os leitores.

"Você ainda pode estar em risco [de um vírus], mesmo que esteja a menos de um metro e oitenta", disse ele. "Em discussão com os modeladores que a defendem, parece que esses modelos não levam em consideração o fluxo de ar. Assim como uma bola vai mais longe se você jogá-la com o vento, as gotículas que carregam os vírus vão mais longe na direção do vento. fluxo de ar."

Essas não são apenas considerações teóricas. Em Cingapura, eles observaram que uma saída de ar de um banheiro usado por um paciente apresentou resultado positivo para o novo Coronavírus e o atribuiu ao fluxo de ar.

"Os modelos não são responsáveis ​​por todos os fatores que afetam a realidade. Quando as apostas são altas, pode-se querer errar com cautela", conclui Srinivasan.

Pesquisa [**Universidade do Texas em Austin, Texas Advanced Computing Center**](http://www.tacc.utexas.edu/) 

**Referências**:

- Mehran Sadeghi Lahijani, Tasvirul Islam, Ashok Srinivasan, Sirish Namilae. **Modelo de Movimento Linear Restrito (CALM): Simulação de movimento de passageiros em aviões** . *PLOS ONE* , 2020; 15 (3): e0229690 DOI: [10.1371 / journal.pone.0229690](http://dx.doi.org/10.1371/journal.pone.0229690)

Imagem de destaque: Freepick
