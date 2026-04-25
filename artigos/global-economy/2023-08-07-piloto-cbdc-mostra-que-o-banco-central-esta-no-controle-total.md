---
title: "Piloto CBDC mostra que o banco central está no controle total"
date: 2023-08-07
status: publish
author: edicleiaalveslima
categories:
  - Global Economy
---

**
Os "teóricos da conspiração" estavam certos novamente!**

O piloto da moeda Real Digital do Banco Central do Brasil permite que as carteiras dos usuários sejam congeladas e os saldos reduzidos, como sempre foi sugerido pelos “teóricos da conspiração”!

**O verdadeiro digital**

*O presidente do Banco Central, Roberto Campos Neto, apresentou a agenda digital do Brasil em novembro de 2022 e apresentou uma prévia do aplicativo Real Digital. Segundo Campos, “o Real Digital, moeda digital do Banco Central do Brasil (CBDC), parece estar tokenizando o sistema bancário”, e explicou que “CBDC nada mais é do que um token emitido pelo banco mediante depósito”.*[(Fonte)](https://elevenews.com/2022/11/29/president-of-the-central-bank-presents-the-brazilian-cbdc-digital-wallet/)

Porém, é claramente mais do que isso, segundo reportagem do jornalista Vini Barbosa no site [Portal do Bitcoin](https://portaldobitcoin.uol.com.br/piloto-do-real-digital-permite-congelamento-de-carteiras-de-usuarios/) .

**O concurso público**

O Banco Central do Brasil (Bacen) divulgou nesta segunda-feira, 3, informações sobre o projeto-piloto de moeda digital do banco central, que permitiu a participação do público no exame. Como resultado, os desenvolvedores descobriram que a moeda digital permite que os usuários congelem e manipulem suas carteiras.

Segundo Barbosa, após a publicação da documentação do projeto-piloto do CBDC brasileiro no GitHub, o Banco Central do Brasil também permitiu o início de uma auditoria pública do código-fonte do sistema.

A revisão pública e colaborativa de seu projeto piloto CBDC na plataforma aberta "Kit Onboarding" contém documentação e arquivos de configuração que todos podem acessar, como um dos propósitos de publicação do projeto piloto (conforme descrito no projeto chamado "onboarding kit ") é para receber feedback - toda a documentação está sujeita a desenvolvimento ou alterações adicionais.

**Desenvolvedor**

Sem surpresa, a revisão atraiu a atenção e o feedback de vários desenvolvedores, que analisaram o código e descobriram alguns recursos de código desconhecidos (comandos). Esses recursos permitem essencialmente que os controladores façam várias alterações relevantes nos dados contábeis do CBDC que afetam diretamente os usuários.

**Engenharia reversa**

Um desenvolvedor full-stack, [Pedro Magalhães](https://www.linkedin.com/in/pemagalhaes/) , especializado em blockchain e DeFI e na linguagem de programação Solidity, [anunciou](https://www.linkedin.com/feed/update/urn:li:activity:7082009809549484032/) no LinkedIn que “fez engenharia reversa do [código](https://www.linkedin.com/feed/update/urn:li:activity:7082009809549484032/) -fonte CBDC Solidity por meio da ABI (interface) da Real Digital”.

Magalhães escreveu: “Recentemente mergulhei no mundo das ABIs (interfaces) da Real Digital, uma iniciativa do banco central, com a intenção de explorar possíveis vulnerabilidades por motivos puramente didáticos”.

Falando ao **Portal do Bitcoin,** Magalhães explicou que “a engenharia reversa é uma técnica para entender como um sistema funciona observando seu comportamento” e que uma Application Binary Interface (ABI) “é basicamente uma forma de usar Smart Interacting Contracts no Ethereum”.

É como um manual que explica como ler e redigir o contrato." Ele explica ainda: "Analisei o ABI para entender as funcionalidades do Real Digital e descobri os vários recursos que eles implementaram.

"Isso resultou em vários insights, incluindo operações como "criação" de tokens Real Digital e ativação/desativação de contas-alvo. Além disso, por meio de engenharia reversa, ele conseguiu encontrar funções que poderiam ser executadas por qualquer entidade autorizada pelo controlador do novo sistema – o banco central.

Com base nessa análise, Pedro diz que foi possível recriar o contrato inteligente usado no piloto em Solidity (a linguagem de computador). Este contrato permite o desempenho das seguintes funções:

disableAccount: Desativa uma conta que tem permissão para transferir tokens.

enableAccount: Habilita uma conta que foi previamente bloqueada para transferências de token..

aumentarFrozenBalance: Aumenta o saldo congelado de um endereço de carteira.

diminuirFrozenBalance: Diminui o saldo congelado de um endereço de carteira.transferência: Substitui a função de transferência ERC20 para contabilizar verificações de status da conta e fundos congelados.

transferFrom: Substitui a função ERC20 transferFrom para conta para verificações de saldo e fundos congelados.

mint: Cria novos tokens digitais reais para um endereço específico.

queimar: Queima (destrói) um certo número de tokens Real Digital.

pausa: Pausa a transferência de tokens.

Unpause: Retoma a transferência do token.

frozenBalanceOf: Recupera o saldo congelado de um endereço de carteira.

authorizedAccount: verifica se uma conta está autorizada para transferências de token.

move: Transfere tokens de uma carteira para outra.

moveAndBurn: Transfere e queima tokens de uma carteira.

burnFrom: Grava tokens de uma conta específica.

Essas funções podem ser exercidas por qualquer órgão autorizado pelo Banco Central por meio de outra função (também presente no código-fonte) denominada *Controle de Acesso . *

**O Portal do Bitcoin** também verificou a existência desses recursos no código-fonte da **Real Digital** e os confirmou com outros desenvolvedores.

**Destinado a um ambiente de teste?**

Segundo Barbosa, o Banco Central do Brasil afirmou inicialmente que “o piloto **Real-Digital** é destinado apenas para uso em ambiente de teste e não deve ser reproduzido para operações reais”. No entanto, questionado pela reportagem, o banco central reconheceu a possibilidade de exercer as funções descobertas por Magalhães.

No entanto, “o BC e as instituições já possuem capacidades semelhantes no ambiente atual de sistemas como SPB e Pix, cuja utilização é regulamentada por leis e regulamentos”, disse a autoridade monetária do país.

**O banco confirmou que vai manter as funcionalidades**

O banco central confirmou seus planos de manter os recursos que permitem à Autoridade Monetária e órgãos autorizados congelar **contas** de usuários , esgotar saldos de endereços de destino, fazer prisões e cunhar novas unidades de moeda digital (CBDC).

Barbosa twittou: "Até o momento, houve apenas especulações populares sobre se eles serão mantidos após o lançamento oficial do **Real Digital** ou se foram feitos apenas para o testnet.

*Relatório completo (em pt-br): [https://portaldobitcoin.uol.com.br/bc-podera-cong](https://portaldobitcoin.uol.com.br/bc-podera-cong)

Essa capacidade de "congelar ou reter fundos" mantidos nesse sistema é protegida pela legislação brasileira vigente, segundo o banco central. Realmente esperávamos mais alguma coisa? Por que abririam mão dessas funções que lhes facilitam o controle das massas?

Fonte: [Expose News ](https://expose-news.com/2023/07/31/pilot-cbdc-shows-central-bank-has-total-control/)
