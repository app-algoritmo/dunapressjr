---
title: "O governo holandês está montando o próprio ambiente de trabalho digital em Linux, e o estopim foi o que aconteceu em Haia"
subtitle: "Em maio de 2025, uma sanção americana contra o procurador do Tribunal Penal Internacional deixou-o sem acesso à própria conta de correio eletrônico, mantida por fornecedor americano. O episódio mostrou a um país europeu que a infraestrutura digital do seu judiciário internacional dependia de decisão tomada em Washington"
description: "A reação holandesa à dependência de fornecedores americanos de software: o caso do TPI, o projeto em NixOS e o conceito de soberania digital."
date: 2026-10-02
status: publish
author: "Redação Duna Press"
categories: "tecnologia"
formato: explicador
proveniencia: humano
revisor: Paulo Fernando de Barros
fonte_primaria: ""
fonte_nome: "Tweakers, reportagem de Jasper Bakker sobre o ambiente de trabalho digital do governo holandês; registros públicos sobre a perda de acesso a serviços de correio eletrônico pelo procurador do Tribunal Penal Internacional em maio de 2025; documentação do projeto NixOS"
data_do_fato: 2026-10-02
featuredImage: "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=1200&auto=format&fit=crop&q=75"
photoAuthor: "Gabriel Heinzer"
photoSource: "Unsplash"
tags:
  - holanda
  - soberania-digital
  - software-livre
  - europa
---

Em maio de 2025, o procurador do Tribunal Penal Internacional, em Haia, perdeu o acesso à própria conta de correio eletrônico.

Não houve invasão nem falha técnica. Ele havia sido alvo de sanções americanas, e o fornecedor do serviço — empresa americana — cumpriu a determinação do próprio governo, cortando o acesso.

O tribunal é instituição internacional sediada nos Países Baixos. O episódio causou transtorno operacional significativo à equipe, e deixou uma demonstração difícil de ignorar: a infraestrutura digital de um tribunal internacional dependia de decisão administrativa tomada em outro país.

## A reação holandesa

Segundo Jasper Bakker, do site de notícias de tecnologia Tweakers, o governo dos Países Baixos está construindo o próprio ambiente de trabalho digital, baseado na distribuição Linux **NixOS**, de origem holandesa.

Ambiente de trabalho digital, nesse contexto, significa o conjunto de ferramentas que um servidor público usa todos os dias: sistema operacional, correio eletrônico, editor de texto, planilha, agenda, armazenamento de arquivo e videoconferência.

Hoje, na maior parte dos governos europeus, esse conjunto é fornecido por duas ou três empresas americanas, operado em nuvem, sob licença que o cliente não controla.

## O que é o NixOS

Uma distribuição do sistema operacional Linux com uma característica incomum: a configuração inteira da máquina é descrita num arquivo de texto.

A consequência prática é que o estado do sistema é reproduzível. Qualquer máquina configurada com o mesmo arquivo fica idêntica, e é possível voltar a uma versão anterior com segurança — propriedade valiosa para uma administração pública que precisa manter milhares de estações padronizadas e auditáveis.

O projeto nasceu na Universidade de Utrecht, e a origem holandesa não é detalhe menor num debate sobre soberania.

## O que significa soberania digital

Não é autarquia tecnológica nem recusa de produto estrangeiro.

É a capacidade de continuar operando quando o fornecedor muda de ideia, é comprado, muda de política de preço, ou é obrigado por um governo estrangeiro a interromper o serviço.

Três condições a sustentam: código auditável, dado armazenado sob jurisdição própria, e possibilidade real de trocar de fornecedor sem reconstruir tudo.

Software livre atende às três por desenho — não porque seja melhor tecnicamente, mas porque ninguém pode revogar uma licença que concede o direito de usar, estudar, modificar e redistribuir.

## Quem mais faz isso

A Alemanha tem o caso mais documentado, e também o mais instrutivo.

Munique migrou a administração municipal para Linux num projeto que durou mais de uma década, e depois reverteu parcialmente para software proprietário — episódio citado pelos dois lados do debate como prova de que a migração funciona ou de que não funciona.

Mais recentemente, o estado alemão de Schleswig-Holstein anunciou migração da administração pública para software livre, com argumento explícito de soberania digital.

França e outros países mantêm programas de incentivo a software livre na administração. A Comissão Europeia discute o tema sob o rótulo de autonomia estratégica digital.

## O argumento contrário

Ele existe e é sério, e nenhum governo que migrou o ignorou.

**Custo de transição.** Treinar dezenas de milhares de servidores, converter documentos acumulados por décadas e manter compatibilidade com o mundo exterior custa caro e demora. Munique mostrou isso.

**Integração.** Órgão público troca arquivo com empresa, com cidadão e com outros governos, e a maior parte deles usa formato de fornecedor proprietário.

**Suporte.** Software livre não vem com contrato de atendimento garantido por padrão. É preciso contratá-lo de alguém — e aí a economia esperada diminui.

**Resistência interna.** A ferramenta que o servidor conhece é a que ele usa há vinte anos.

## O que o caso de Haia acrescentou ao debate

Deslocou o argumento.

Até então, a discussão sobre software livre no setor público girava em torno de custo de licença e de preferência técnica — temas em que os dois lados tinham argumentos razoáveis e nenhum era urgente.

O episódio de 2025 transformou a questão em risco operacional concreto e documentado: um funcionário de tribunal internacional perdeu acesso ao próprio correio eletrônico por decisão de um terceiro Estado.

É um argumento de natureza diferente, e é mais difícil de responder.
