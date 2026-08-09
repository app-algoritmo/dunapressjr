---
title: Jogo com sensores de movimentos pode ajudar a tratar AVC
date: 2023-02-16
status: publish
author: Joice Ferreira
categories:
- Technology
---


Gabriel Cyrino é bacharel em Sistemas de Informação pelo Centro Universitário de Patos de Minas (Unipam). Pela Universidade Federal de Uberlândia (UFU), tornou-se mestre e cursa doutorado em Engenharia Elétrica, sempre com bolsas da CAPES. Na primeira etapa, desenvolveu um jogo para promover uma reabilitação lúdica para pacientes que sofreram acidente vascular cerebral (AVC). Agora, ele se dedica a aperfeiçoar o *game*.

**O que motivou o trabalho e qual foi a ideia?
**A fisioterapia convencional pode guiar a reabilitação de um paciente de uma forma bastante cansativa. A partir disso, ainda no mestrado, surgiu a ideia de desenvolver um jogo sério (jogo virtual para fins educacionais) para reabilitação de pacientes pós-AVC, em um ambiente lúdico. O jogador controla uma harpia com o braço afetado pelo AVC.

**E como funciona o jogo?
**O paciente presencia três níveis diferentes para definição de protocolo. No primeiro, é preciso passar por uns anéis no cenário. No segundo, tem que capturar peixes em um lago. No terceiro, tem que pegar uns pedaços de carne enquanto toma cuidado com predadores que estão presentes na fase. A partir das nossas pesquisas, nós vimos que a maioria dos Jogos Sérios são fixos para um determinado protocolo e voltados para um determinado tipo de paciente. Não são customizáveis o suficiente para que o fisioterapeuta guie o paciente para desenvolver novos protocolos para específicos tipos de reabilitação. Foi a principal razão para desenvolvermos um jogo mais customizável. 

**O que motivou a continuação do projeto no doutorado?
**A partir de novas pesquisas, percebemos que o jogo não identificava alguns movimentos que podem ser julgados como incorretos, algo que os fisioterapeutas chamam de movimentos compensatórios. Movimentos como rotação do ombro na hora de virar a harpia para a esquerda ou para a direita. O paciente pode realizar um movimento compensatório para ele mesmo auxiliar um movimento que não consegue fazer naquele momento. Ou inclinação de tronco na hora de ir para frente ou para trás. É preciso evitar esses movimentos, para que o paciente não se reabilite de forma errada.

**Como vocês avançaram nisso?
**O Laboratório de Engenharia Biomédica da UFU (BioLab) já tinha desenvolvido uma plataforma de força, uma plataforma robótica constituída por um manche e dois motores, que podem aplicar dois tipos de força: de impedância e de admitância. Já foi usada para outros projetos, para auxiliar a movimentação do voluntário, quando ele não consegue executar o movimento, caso em que os motores ativam a força de admitância para ajudar a movimentar corretamente. E, em estágios mais avançados, em que o paciente já consegue executar o movimento, vem a força de impedância, ou seja, os motores fazem o esforço no movimento ser maior, aumentando a força do paciente. Esses dois tipos de força podem ser aplicados. Então, a ideia foi usar essa interface, essa plataforma, como interface de controle do jogo sério.

**Como isso se aplicou ao jogo?
**A partir daí, além de movimentos mais corretos durante a execução do jogo, é possível usar forças dentro do jogo paralelas à reabilitação tradicional. Por exemplo, eu posso aplicar um vento contrário à harpia. Esse vento pode ativar o motor de impedância, fazendo o movimento ficar mais rígido, mais travado, para adquirir força. Tudo controlado pelo fisioterapeuta. Outro exemplo é colocar um peso nos peixes. Quando o paciente tenta voltar com o manche para trás, para a harpia subir, ele vai sentir mais pesado. Então, vários movimentos podem ser implementados dentro do protocolo.

**Onde entram os rastreadores de movimentos?
**Mesmo que os movimentos fiquem mais corretos e travados, o paciente ainda pode executar movimentos compensatórios. Na fisioterapia tradicional, esses movimentos são identificados pela *expertise *do fisioterapeuta, que guia o paciente, auxiliando-o na movimentação, segurando-o pelo braço. Nossa ideia é dar mais autonomia para o paciente, mesmo que o fisioterapeuta ainda seja essencial, porque é ele que define o protocolo. Usamos cinco rastreadores de movimentos: um é colocado no peito, outro no ombro, outro no braço, outro no antebraço e outro na mão.

**O que acontece com eles?
**Vou dar um exemplo. Na hora da execução do movimento no jogo sério, o fisioterapeuta pode ter definido anteriormente, pelo painel de controle, que, quando for cumprir certo objetivo, a compensação de rotação de ombro não pode ser identificada quando vai virar para a esquerda ou para a direita com a harpia. O rastreador identificará se houve o movimento a ser evitado, o que leva o fisioterapeuta a estabelecer uma punição no jogo: pode ser que a harpia fique mais rígida, mais dura, até que o próprio paciente corrija a forma de se mover. Já no painel de controle, ao qual só o fisioterapeuta tem acesso e em tempo real, vê-se o tipo de compensação feita e o porquê da aplicação da punição. Ou seja, o paciente consegue identificar melhor os movimentos compensatórios, e o fisioterapeuta não precisa ficar toda hora corrigindo.

**Qual o impacto que você enxerga no projeto?
**Como na reabilitação tradicional os movimentos são identificados de uma forma mais visual, no futuro o impacto vai ser o paciente poder se reabilitar com o jogo sério em casa. O fisioterapeuta vai acompanhar, claro, mas não necessariamente da forma 100% presencial, e sem precisar corrigir os movimentos a cada instante. Ele pode definir um protocolo a ser seguido em casa.

Fonte: https://www.gov.br/capes
