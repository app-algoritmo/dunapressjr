---
title: "Um canal de análise de hardware gastou 70 mil dólares para descobrir o que a televisão faz quando parece desligada"
subtitle: "A investigação do Gamers Nexus com o Level1Techs durou mais de 500 horas e resultou num vídeo de 2h15 publicado em 7 de setembro. Os testes indicam varredura da rede doméstica, captura de áudio em modo de espera e cerca de 4 GB mensais de dados enviados. A LG nega as acusações centrais. E uma correção: foi desconectada da internet, não da tomada"
description: "O que a investigação do Gamers Nexus encontrou nas TVs LG, o que a empresa responde e o que o leitor pode desligar nas configurações."
date: 2026-10-02
status: publish
author: "Redação Duna Press"
categories: "tecnologia"
formato: explicador
proveniencia: humano
revisor: Paulo Fernando de Barros
fonte_primaria: ""
fonte_nome: "Gamers Nexus, investigação publicada em 7 de setembro de 2026, conduzida por Steve Burke com Level1Techs e os pesquisadores independentes MrBruh e uturn; resposta pública da LG de 9 e 13 de setembro; cobertura de The Verge, Malwarebytes e Al Jazeera"
data_do_fato: 2026-09-07
featuredImage: "https://images.unsplash.com/photo-1560169897-fc0cdbdfa4d5?w=1200&auto=format&fit=crop&q=75"
photoAuthor: "Glenn Carstens-Peters"
photoSource: "Unsplash"
tags:
  - privacidade
  - lg
  - vigilancia
  - tecnologia
---

Em 7 de setembro, o canal Gamers Nexus — conhecido por testar placas de vídeo e dissipadores com rigor de laboratório — publicou um vídeo de duas horas e quinze minutos sobre televisores LG.

A investigação consumiu mais de 500 horas de trabalho e cerca de 70 mil dólares, financiados por campanha de apoiadores. Foi conduzida por Steve Burke em conjunto com o canal Level1Techs e com os pesquisadores independentes MrBruh e uturn.

O título escolhido foi direto: 216 milhões de TVs espiãs.

## A correção que a história precisa

Circula a versão de que os aparelhos gravariam mesmo **desligados da tomada**. Não é o que foi demonstrado, e a diferença importa.

O que os pesquisadores mostraram foi que a TV armazenou áudio enquanto estava **desconectada da internet**, e enviou o material depois que a conexão foi restaurada.

Um televisor sem energia elétrica não processa nada. O que o teste expõe é outra coisa, e é grave o bastante por si: desligar o Wi-Fi não interrompe a coleta — apenas adia o envio.

## O que os testes indicam

**Varredura da rede doméstica.** Captura de pacotes e análise de firmware mostraram os aparelhos identificando outros dispositivos na rede local: telefones, computadores, impressoras, switches e equipamento de casa conectada. Também coletaram nomes de redes Wi-Fi próximas, informação de sinal e identificadores de dispositivo.

**Reconhecimento automático de conteúdo.** É a tecnologia conhecida pela sigla ACR. O aparelho tira amostras do que aparece na tela, gera uma impressão digital daquilo e envia a um banco de dados para identificação — inclusive quando o conteúdo vem de um aparelho ligado por HDMI, e não de um aplicativo da própria TV.

**Volume.** Um aparelho de teste enviou cerca de **4 gigabytes por mês** de dados de impressão digital, majoritariamente texto.

**Áudio em modo de espera.** Os pesquisadores demonstraram captura de áudio pelo microfone com o aparelho aparentando estar desligado, após o acionamento do botão de energia do controle remoto, com transcrição para texto simples.

**Vulnerabilidades.** A equipe reportou à LG falhas de execução remota de código — brechas que permitiriam a um terceiro assumir controle do aparelho.

## O que a LG responde

A empresa negou formalmente as acusações centrais em 9 e 13 de setembro.

Sustenta que o recurso de reconhecimento automático de conteúdo só é ativado com consentimento do usuário, e contesta a interpretação dada às observações técnicas.

O Gamers Nexus rebateu ponto a ponto.

A distinção que vale manter em mente é a que o próprio noticiário registra: as **observações técnicas** e a **interpretação** delas são coisas diferentes, e a disputa é sobre a segunda.

Até a última atualização pública, a LG não havia se pronunciado sobre as vulnerabilidades de segurança reportadas, que seguem em processo de divulgação responsável.

## O que não é exclusivo da LG

Praticamente nada disso.

O reconhecimento automático de conteúdo está embutido em quase todo televisor moderno de qualquer marca. Os dados de visualização são compartilhados com o fabricante e seus parceiros comerciais. O consentimento é obtido em documentos longos que o usuário precisa aceitar para usar o aparelho.

Há processos em andamento nos Estados Unidos contra outros fabricantes por práticas semelhantes. Uma ordem judicial anterior obrigou um fabricante a apagar dados coletados antes de 2016 e a obter consentimento expresso a partir dali.

O que a investigação acrescenta é a profundidade da coleta num fabricante específico, documentada com captura de pacotes.

## O que o leitor pode fazer

Nas configurações do aparelho, procurar as seções de privacidade, termos de uso ou acordos de usuário, e desativar: reconhecimento automático de conteúdo, coleta de informação de visualização, anúncios personalizados e reconhecimento de voz.

Manter o firmware atualizado, porque as correções de segurança chegam por ali.

E considerar o óbvio: um televisor não precisa estar conectado à internet para exibir imagem de um aparelho externo. Quem usa decodificador, console ou computador pode simplesmente não conectar a TV ao Wi-Fi.

Os pesquisadores registraram um detalhe que resume o problema: ao optar por sair da coleta, o aparelho envia um último pacote com todos os dados de rastreamento acumulados antes de parar.
