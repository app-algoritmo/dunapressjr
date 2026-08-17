#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duna Press — acrescenta ao Worker as rotas legadas do WordPress que hoje
caem em 404.

Rode da raiz do repositório:
    python3 patch-worker.py

Faz backup em tools/worker-redirects.js.bak antes de alterar.
Rodar duas vezes não duplica nada: o script detecta e avisa.
"""
import os, shutil, sys

ALVO = "tools/worker-redirects.js"

HELPERS = '''
// ── Rotas nativas do WordPress ───────────────────────────────────────────
// O site intermediário usava /categoria.html?cat=x; o WordPress original
// usava /category/x/. O Google indexou os dois, e só o primeiro tinha
// tratamento aqui — daí o volume de 404 em /category/, /tag/ e /author/.
const EDITORIA_SLUG = new Set(["brasil", "mundo", "economia", "politica",
  "ciencia-e-saude", "tecnologia", "cultura", "esportes", "opiniao"]);

// Parâmetros que o WordPress e as redes sociais penduram na URL sem mudar
// o conteúdo. Cada um cria um endereço duplicado aos olhos do buscador.
// utm_ fica de fora: é medição de campanha e sobrevive ao 301.
const LIXO_QUERY = /^(amp|noamp|currency|fbclid|gclid|msclkid|replytocom|share|like_comment|_ga)$/i;

/**
 * Devolve o 301 para as rotas legadas, ou nulo se a URL não for de nenhuma
 * delas — nesse caso o chamador segue o fluxo normal.
 */
function rotaLegada(url, requestUrl) {
  // Parâmetro herdado que só duplica a URL: remove e redireciona ao limpo.
  const sujos = [...url.searchParams.keys()].filter((k) => LIXO_QUERY.test(k));
  if (sujos.length) {
    const limpo = new URL(url);
    for (const k of sujos) limpo.searchParams.delete(k);
    return permanente(limpo.pathname + limpo.search, requestUrl);
  }

  // Arquivo mensal ou anual: /2022/05/ e /2022/.
  if (/^\\/\\d{4}\\/(\\d{2}\\/)?$/.test(url.pathname)) {
    return permanente("/arquivo/", requestUrl);
  }

  // Categoria nativa, inclusive aninhada: /category/a/b/ usa o último nível.
  const cat = url.pathname.match(/^\\/category\\/(?:[^/]+\\/)*([^/]+)\\/?$/);
  if (cat) {
    const s = cat[1];
    const ed = EDITORIA_SLUG.has(s)
      ? s
      : (EDITORIAS[s] || EDITORIAS[s.replace(/-en$/, "")]);
    return permanente(ed ? `/${ed}/` : "/arquivo/", requestUrl);
  }

  // Etiquetas não têm equivalente no site novo. A busca é o destino honesto:
  // entrega o que existe sobre o assunto em vez de fingir uma página.
  const tag = url.pathname.match(/^\\/tag\\/(?:[^/]+\\/)*([^/]+)\\/?$/);
  if (tag) {
    const termo = tag[1].replace(/-/g, " ");
    return permanente(`/busca/?q=${encodeURIComponent(termo)}`, requestUrl);
  }

  const autor = url.pathname.match(/^\\/author\\/([^/]+)\\/?$/);
  if (autor) return permanente(`/autores/${autor[1]}/`, requestUrl);

  if (/^\\/page\\/\\d+\\/?$/.test(url.pathname)) {
    return permanente("/arquivo/", requestUrl);
  }
  if (url.pathname === "/home/") return permanente("/", requestUrl);

  return null;
}

'''

ANTIGO = '''    // 3. Permalink com data, usado até 2024. O slug continua válido: apenas
    //    o prefixo saiu quando o permalink foi reconfigurado.
    const datado = url.pathname.match(/^\\/\\d{4}\\/\\d{2}\\/\\d{2}\\/([^/]+)\\/?$/);
    if (datado) return permanente(`/${datado[1]}/`, request.url);

    // Qualquer outra coisa segue para a origem.
    return fetch(request);'''

NOVO = '''    // 3. Permalink com data, usado até 2024. O slug continua válido: apenas
    //    o prefixo saiu quando o permalink foi reconfigurado.
    const datado = url.pathname.match(/^\\/\\d{4}\\/\\d{2}\\/\\d{2}\\/([^/]+)\\/?$/);
    if (datado) return permanente(`/${datado[1]}/`, request.url);

    // 4. Demais rotas nativas do WordPress: /category/, /tag/, /author/,
    //    arquivo por data, paginação e parâmetros duplicadores.
    const legada = rotaLegada(url, request.url);
    if (legada) return legada;

    // Qualquer outra coisa segue para a origem.
    return fetch(request);'''

ANCORA = "export default {"


def main():
    if not os.path.exists(ALVO):
        sys.exit(f"ERRO: {ALVO} não encontrado. Rode da raiz do repositório.")

    s = open(ALVO, encoding="utf-8").read()

    if "rotaLegada" in s:
        sys.exit("Nada a fazer: o Worker já tem as rotas legadas.")
    if ANTIGO not in s:
        sys.exit("ERRO: o bloco de roteamento não bate com o esperado.\n"
                 "O arquivo mudou desde a última leitura — não vou editar às cegas.")
    if ANCORA not in s:
        sys.exit("ERRO: não achei 'export default' para inserir os helpers.")

    shutil.copy(ALVO, ALVO + ".bak")
    s = s.replace(ANCORA, HELPERS.lstrip("\n") + ANCORA, 1)
    s = s.replace(ANTIGO, NOVO, 1)
    open(ALVO, "w", encoding="utf-8").write(s)

    print(f"OK — {ALVO} atualizado. Backup em {ALVO}.bak")
    print("Rotas acrescentadas: /category/, /tag/, /author/, /AAAA/MM/,")
    print("/page/N/, /home/ e limpeza de ?amp, ?noamp, ?currency, ?fbclid.")


if __name__ == "__main__":
    main()
