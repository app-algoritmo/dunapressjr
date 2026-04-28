---
title: Engenheiros desenvolvem sistema de GPS de baixo custo e alta precisão para
  robôs médicos flexíveis
date: 2020-06-05
status: publish
author: Paulo Fernando De Barros
categories:
- Magazine
---


Os roboticistas da Universidade da Califórnia em San Diego desenvolveram um sistema acessível e fácil de usar para rastrear a localização de robôs cirúrgicos flexíveis dentro do corpo humano. O sistema tem um desempenho tão bom quanto os métodos atuais, mas é muito mais barato. Muitos métodos atuais também exigem exposição à radiação, enquanto este sistema não.

O sistema foi desenvolvido por Tania Morimoto, professora de engenharia mecânica na Jacobs School of Engineering da UC San Diego, e Ph.D. em engenharia mecânica. estudante Connor Watson. Suas descobertas foram publicadas na edição de abril de 2020 da *IEEE Robotics and Automation Letters* .

"Os robôs médicos contínuos funcionam muito bem em ambientes altamente restritos dentro do corpo", disse Morimoto. "Eles são inerentemente mais seguros e compatíveis do que as ferramentas rígidas. Mas fica muito mais difícil rastrear sua localização e sua forma dentro do corpo. E, portanto, se formos capazes de rastreá-los com mais facilidade, isso seria um grande benefício para os pacientes e cirurgiões ".

Os pesquisadores incorporaram um ímã na ponta de um robô flexível que pode ser usado em locais delicados do corpo, como passagens arteriais no cérebro. "Trabalhamos com um robô em crescimento, que é um robô feito de nylon muito fino que invertemos, quase como uma meia, e pressurizamos com um fluido que faz com que o robô cresça", disse Watson. Como o robô é macio e se move em crescimento, ele tem muito pouco impacto sobre o ambiente, sendo ideal para uso em ambientes médicos.

Os pesquisadores usaram os métodos existentes de localização de ímãs, que funcionam muito como o GPS, para desenvolver um modelo de computador que prediz a localização do robô. Os satélites GPS fazem ping nos smartphones e, com base no tempo que leva para o sinal chegar, o receptor GPS no smartphone pode determinar onde está o telefone celular. Da mesma forma, os pesquisadores sabem o quão forte o campo magnético deve estar em torno do ímã incorporado no robô. Eles contam com quatro sensores que são cuidadosamente espaçados ao redor da área em que o robô opera para medir a força do campo magnético. Com base na força do campo, eles são capazes de determinar onde está a ponta do robô.

Todo o sistema, incluindo a instalação do robô, ímãs e localização de ímãs, custa cerca de US $ 100.

Morimoto e Watson deram um passo adiante. Eles então treinaram uma rede neural para aprender a diferença entre o que os sensores estavam lendo e o que o modelo dizia que os sensores deveriam estar lendo. Como resultado, eles aprimoraram a precisão da localização para rastrear a ponta do robô.

"Idealmente, esperamos que nossas ferramentas de localização possam ajudar a melhorar esse tipo de crescente tecnologia de robôs. Queremos levar essa pesquisa adiante para que possamos testar nosso sistema em um ambiente clínico e, eventualmente, traduzi-lo em uso clínico", disse Morimoto.

**Fonte da história:**

Fonte de pesquisa [**Universidade da Califórnia - San Diego**](http://www.ucsd.edu/) - Ioana Patringenaru. 

**Referência**s:

- Connor Watson, Tania K. Morimoto. **Localização permanente baseada em ímã para robôs em crescimento em aplicações médicas** . *Cartas de Robótica e Automação do IEEE* , 2020; 5 (2): 2666 DOI: [10.1109 / LRA.2020.2972890](http://dx.doi.org/10.1109/LRA.2020.2972890)

Imagem de destaque: David Baillot
