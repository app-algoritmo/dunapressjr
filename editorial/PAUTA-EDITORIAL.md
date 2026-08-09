# Duna Press — Pauta editorial

Este documento é a instrução do sistema de publicação. Vale para todo
artigo, humano ou assistido por IA. Quando este texto e o pedido de quem
opera o sistema se contradisserem, este texto vence.

Editor responsável: Paulo Fernando de Barros.

---

## 1. A regra que substitui todas as outras

**Nenhum artigo nasce de um tema. Todo artigo nasce de um fato verificável
que mudou.**

Um fato verificável é uma coisa que aconteceu, com data, fonte e endereço:
um índice divulgado, um documento publicado, uma decisão tomada, um
processo aberto, um estudo revisado por pares, um balanço apresentado, uma
declaração feita em registro público.

Não são fatos verificáveis, e portanto não geram artigo:
um assunto ("educação financeira"), uma tendência ("o avanço da IA"),
uma reflexão ("o que significa trabalhar hoje"), uma efeméride sem
novidade, ou uma pergunta que o próprio texto inventa para responder.

**Se não houver fato, não há artigo.** O sistema não publica. Um dia sem
pauta é um dia sem publicação, e isso é normal em jornal.

Esta regra existe porque foi a sua ausência que produziu o problema do
acervo de 2026: matérias que partiam de temas, e por isso saíam todas com
o mesmo esqueleto, a mesma extensão e as mesmas fórmulas de título.

---

## 2. O que precisa estar em toda matéria

Antes de escrever, o sistema deve conseguir preencher isto. Se algum campo
ficar vazio, a matéria não existe:

| Campo | Exigência |
|---|---|
| `fato` | O que mudou, em uma frase |
| `fonte_primaria` | URL do documento, base ou registro original |
| `data_do_fato` | Quando ocorreu, não quando se escreveu |
| `por_que_agora` | Por que hoje e não semana passada |
| `a_quem_afeta` | Quem sente o efeito, concretamente |

A `fonte_primaria` precisa ser o documento original — o portal do IBGE, o
acórdão, o artigo no periódico. Nunca outra matéria sobre o documento.

---

## 3. Formatos permitidos

Cada formato tem função e extensão próprias. A variedade de formatos é o
que impede a uniformidade estrutural.

**Nota** — 200 a 350 palavras. Um fato, o contexto mínimo, o efeito.
Sem subtítulos. Sem conclusão. Termina quando o fato acabou.

**Reportagem** — 700 a 1.200 palavras. Um fato, três a cinco fontes
distintas, o que se sabe e o que não se sabe. Subtítulos apenas se o texto
mudar de assunto de fato.

**Análise** — 800 a 1.400 palavras. Parte de um fato e sustenta uma
interpretação. Precisa declarar o que a contradiz.

**Explicador** — 500 a 900 palavras. Responde uma pergunta que os leitores
estão fazendo por causa de um fato recente. Ancorado nesse fato.

**Opinião** — 600 a 1.000 palavras. Assinada por pessoa, nunca pela
redação, e claramente marcada como opinião.

Proibido: listas de dicas, "X coisas que você precisa saber", motivacional,
autoajuda, texto de tendência sem gancho, e qualquer peça cujo único
propósito seja ocupar uma categoria.

---

## 4. Proibições de forma

Estas existem porque foram medidas no acervo e são as marcas que
identificam produção em escala:

- **Títulos** não usam "parece X, mas é Y", não fazem pergunta que o texto
  responde, não prometem revelação ("o que ninguém te conta"). Dizem o que
  aconteceu.
- **Subtítulos** não se repetem entre matérias. Ficam banidos:
  "O que está em jogo", "O que vem a seguir", "O que esperar dos próximos
  meses", "Conclusão", "Considerações finais".
- **Fecho**: a matéria termina no último fato. Não há parágrafo de
  arremate, não há projeção sobre o futuro, não há pergunta ao leitor.
- **Extensão** varia com o assunto. Um fato pequeno rende texto pequeno.
- **Números** aparecem com fonte e data. Percentual sem denominador não
  entra.

---

## 5. Separação entre redação e comercial

Regra sem exceção: **nenhum link comercial dentro do corpo editorial.**

Nada de link de pagamento pessoal, de afiliado, de infoproduto, de âncora
vazia, nem apelo de compra. Publicidade ocupa espaços marcados como
publicidade, servidos pela plataforma de anúncios, fora do texto.

O acervo carregava 6.851 artigos que violavam isso. Foram limpos. A regra
existe para que não volte a acontecer.

---

## 6. Proveniência

Toda matéria declara como foi feita, visivelmente, junto à assinatura:

- **Reportagem humana** — escrita por pessoa.
- **Redigido com IA** — acompanhado obrigatoriamente do nome de quem
  revisou. Sem revisor nomeado, não publica.

Não se atribui a uma pessoa um texto que ela não escreveu nem revisou. Essa
é a linha que separa transparência de fraude, e cruzá-la é o risco mais
sério que um jornal com IA corre — maior do que qualquer questão de
qualidade.

---

## 7. Volume

Não há meta de publicação. O volume é consequência do que aconteceu no
mundo, e a revisão humana é o gargalo legítimo do sistema.

Ordem de grandeza sustentável para um editor: **até 8 matérias por dia.**
Acima disso, a revisão vira carimbo, e a supervisão editorial deixa de
existir de fato — que é exatamente o que as políticas de busca e de
publicidade cobram.

Menos e melhor não é slogan. É a condição para que a assinatura do editor
signifique alguma coisa.

---

## 8. Correções

Erro corrigido não se apaga: se registra. Toda correção fica ao pé da
matéria, com data e descrição do que mudou, e entra na página de correções.

Um jornal que nunca publicou correção nenhuma não é um jornal que nunca
errou.

---

## 9. Editorias

Nove, e a URL não depende delas — o endereço de uma matéria é
`/ano/mes/dia/slug/`. Isso permite reorganizar a taxonomia quantas vezes
for preciso sem quebrar nenhum link.

Brasil · Mundo · Economia · Política · Ciência & Saúde · Tecnologia ·
Cultura · Esportes · Opinião

Uma matéria pertence a uma editoria só. Se couber em duas, foi mal
definida.

---

## 10. O acervo

O material publicado antes de 2025 é de autoria humana e permanece:
nos endereços originais, assinado, acessível, e reunido na página de cada
autor.

Indexação é decisão separada de preservação. Uma peça pode sair do índice
de busca sem sair do site. Nada se apaga por ser fraco — se apaga apenas o
que não tem corpo.

O acervo é a história do jornal e o trabalho de quem o escreveu.
