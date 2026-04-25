---
title: "Aplicativos JavaScript têm menos falhas que Java e .NET"
date: 2023-02-14
status: publish
author: debarrospaulo
categories:
  - Science
---

Relatório de segurança de software descobre que aplicativos JavaScript têm menos falhas que Java e .NET

[O relatório State of Software Security](https://info.veracode.com/report-state-of-software-security-2023.html) da [Veracode](https://www.veracode.com/) para 2023 descobriu que há 27% de chance em um determinado mês de que falhas de segurança sejam introduzidas em um aplicativo. Vários fatores foram encontrados para afetar essa chance, incluindo frequência de varredura, método de varredura, quantidade de educação do desenvolvedor e o idioma do aplicativo. O relatório também descobriu que os aplicativos JavaScript, em média, têm menos falhas e resolução de falhas mais rápida do que os aplicativos Java e .NET.

O relatório revisou todos os aplicativos verificados na plataforma Veracode. Uma descoberta importante é que a escolha da linguagem de programação afeta os tipos, a quantidade e a resolução das falhas. Embora os aplicativos JavaScript ainda apresentem falhas, eles tendem a ser resolvidos mais rapidamente. Essa resolução mais rápida no início do ciclo de vida do aplicativo leva a uma tendência de resolução aprimorada ao longo do tempo.

Tempo para correção de falhas por idioma dentro da plataforma Veracode (crédito: Veracode )

Em média, quatro em cada cinco aplicativos Java e .NET têm pelo menos uma falha em comparação com os aplicativos JavaScript, onde pouco mais da metade dos aplicativos tem uma ou mais falhas. Além disso, os aplicativos Java e .NET têm quase o dobro de problemas de alta gravidade em comparação com os aplicativos JavaScript.

Também foram abordados os principais tipos de falhas descobertas pelas diferentes verificações feitas na plataforma. O principal problema descoberto pela análise estática foi a injeção de alimentação de linha de retorno de carro (CRLF) em 64,8%, seguido de perto por problemas criptográficos (59,8%) e vazamento de informações (59,3%). Nas varreduras de análise dinâmica, a configuração do servidor foi o principal problema encontrado, com 96,5% das falhas descobertas sendo marcadas como problemas de configuração.

Os projetos analisados ​​mostraram que as candidaturas crescem cerca de 40% ao ano independentemente do seu tamanho inicial. Além disso, a introdução de falhas tende a acompanhar o crescimento do aplicativo, com algumas exceções. Como observa o relatório:

Após a integração inicial de um aplicativo, vemos uma rápida diminuição. O aplicativo então entra no que chamamos de "período de lua de mel" e, nos primeiros dois anos, as coisas estão estáveis. Pelo contrário, cerca de 80% das aplicações não apresentam falhas nesta fase inicial do ciclo de vida.

Introdução de falhas por idade de aplicação (crédito: Veracode )

Em um determinado mês, um aplicativo tem 27% de chance de ter uma ou mais novas falhas introduzidas e descobertas. O relatório teve uma série de descobertas que ajudam a ajustar esse número para cima ou para baixo. As organizações que digitalizaram seus aplicativos via API tiveram uma redução de 2% nessa probabilidade. Os autores postulam que a varredura via API tende a ser uma atividade mais madura e que "podemos supor que ela tenha outras coisas em vigor, como controle de acesso ao pipeline".

Tendo os desenvolvedores concluídos os programas de treinamento, houve uma redução de 1,8% na probabilidade de novos problemas serem introduzidos. Por outro lado, os aplicativos com um débito de segurança maior, medido como uma densidade de falha de uma falha por um megabyte de código, tiveram 2,2% mais chances de introduzir um defeito.

O relatório tem uma série de recomendações para ajudar a reduzir a curva de remediação mais rapidamente e mais cedo. As recomendações incluem priorizar a automação, fornecer treinamento de segurança para desenvolvedores e estabelecer o gerenciamento do ciclo de vida do aplicativo. Para o gerenciamento do ciclo de vida do aplicativo, os principais objetivos são garantir que fique claro quem é o proprietário do aplicativo, a finalidade a que ele serve e quando o aplicativo deve ser movido para o fim de sua vida útil.

Para obter mais detalhes do relatório Veracode State of Software Security 2023, os leitores são direcionados ao [site Veracode](https://info.veracode.com/report-state-of-software-security-2023.html).

Originalmente escrito por **Matt Campbell**, líder na equipe editorial de DevOps do InfoQ.
