/**
 * Duna Press — redirecionamento das URLs legadas.
 *
 * A versão anterior deste Worker servia tags Open Graph para bots de rede
 * social, porque a página antiga era montada por JavaScript e chegava vazia
 * para quem não executa script. Isso deixou de ser necessário: cada matéria
 * agora é HTML completo, com og:title e og:description no servidor. Bot e
 * leitor recebem a mesma coisa.
 *
 * O que sobrou é um problema que o GitHub Pages não resolve sozinho: ele não
 * emite 301. Sem 301, um endereço antigo pode até levar o leitor ao lugar
 * certo por JavaScript, mas não transfere a autoridade de link acumulada — e
 * é justamente ela que sustenta o ranqueamento de um acervo de nove anos.
 *
 * Três formatos legados, todos resolvidos aqui com 301 permanente:
 *
 *   /artigo.html?file=/artigos/{cat}/{arq}.md   consulta o mapa publicado
 *   /categoria.html?cat={slug}                  79 categorias → 9 editorias
 *   /AAAA/MM/DD/{slug}/                         permalink usado até 2024
 *
 * O terceiro é o mais valioso: até 2024 o site usava data no permalink, e os
 * backlinks daquele período ainda apontam para lá.
 */

const SITE = "https://dunapress.org";

// ── Autenticação da redação ──────────────────────────────────────────────
// O painel em /admin/ grava no repositório pela API do GitHub, mas o GitHub
// não permite login direto de uma página estática: o segredo do aplicativo
// precisa ficar em algum lugar que o navegador não enxergue. É aqui.
//
// Duas variáveis de ambiente no Worker, marcadas como secretas:
//   GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
const ESCOPO_GITHUB = "repo";
const MAPA = `${SITE}/api/legado.json`;

// O mapa muda a cada publicação, mas raramente. Uma hora de cache evita ida
// à origem em toda visita a URL antiga, sem deixar o dado envelhecer demais.
const CACHE_MAPA = 3600;

// 79 categorias herdadas do WordPress → 9 editorias. Embutido no Worker
// porque é pequeno, estável, e evita uma segunda busca de rede.
const EDITORIAS = {
  news: "brasil", "economia-brasileira": "brasil", "geopolitica-brasil": "brasil",
  bicentennial: "brasil", education: "brasil", "courses-and-careers": "brasil",
  headlines: "brasil", events: "brasil", escola: "brasil",

  "world-affairs": "mundo", geopolitics: "mundo", "global-affairs": "mundo",
  "international-affairs": "mundo", "international-politics": "mundo",
  "international-relations": "mundo", "guerra-e-conflitos": "mundo",
  military: "mundo",

  "business-and-economy": "economia", "global-economy": "economia",
  finances: "economia", "financial-education": "economia",
  criptomoedas: "economia", entrepreneurship: "economia",
  shopping: "economia", works: "economia",

  policy: "politica", "politics-and-society": "politica",
  "ethics-and-society": "politica", "society-and-culture": "politica",

  science: "ciencia-e-saude", health: "ciencia-e-saude",
  "covid-19": "ciencia-e-saude", "saude-mental": "ciencia-e-saude",
  psicologia: "ciencia-e-saude", environment: "ciencia-e-saude",
  "energias-renovaveis": "ciencia-e-saude", agriculture: "ciencia-e-saude",
  astronomy: "ciencia-e-saude", "space-exploration": "ciencia-e-saude",
  "well-being": "ciencia-e-saude", fitness: "ciencia-e-saude",
  arqueologia: "ciencia-e-saude", ufologia: "ciencia-e-saude",

  technology: "tecnologia", innovation: "tecnologia",
  "future-and-innovation": "tecnologia", "inteligencia-artificial": "tecnologia",
  "social-networks": "tecnologia", "e-auto": "tecnologia",

  "culture-and-history": "cultura", history: "cultura",
  "history-and-philosophy": "cultura", philosophy: "cultura",
  literature: "cultura", books: "cultura", music: "cultura",
  "architecture-and-art": "cultura", religiosity: "cultura",
  fashion: "cultura", beauty: "cultura", food: "cultura",
  gastronomia: "cultura", "tourism-and-gastronomy": "cultura",
  lifestyle: "cultura", pets: "cultura", story: "cultura",
  documentaries: "cultura", magazine: "cultura", features: "cultura",
  "video-library": "cultura", "personal-development": "cultura",
  motivational: "cultura",

  sports: "esportes", soccer: "esportes", "formula-1": "esportes",
  tennis: "esportes", cycling: "esportes", "olympic-games": "esportes",
  "pan-american-games": "esportes",

  opinion: "opiniao", editorial: "opiniao", chronicle: "opiniao",
};

let mapaEmMemoria = null;
let mapaExpiraEm = 0;

/**
 * Mapa de URL antiga → nova, publicado pelo build em /api/legado.json.
 * Guardado em memória entre requisições do mesmo isolate; falha de rede
 * devolve nulo e o chamador segue para a origem sem quebrar a página.
 */
async function carregarMapa() {
  const agora = Date.now();
  if (mapaEmMemoria && agora < mapaExpiraEm) return mapaEmMemoria;
  try {
    const r = await fetch(MAPA, { cf: { cacheTtl: CACHE_MAPA } });
    if (!r.ok) return mapaEmMemoria;
    mapaEmMemoria = await r.json();
    mapaExpiraEm = agora + CACHE_MAPA * 1000;
    return mapaEmMemoria;
  } catch {
    return mapaEmMemoria;
  }
}

function permanente(destino, origem) {
  const alvo = new URL(destino, origem);
  // Parâmetros de campanha sobrevivem ao redirecionamento: quem chega por
  // uma newsletter continua sendo contado como vindo dela.
  for (const [k, v] of new URL(origem).searchParams) {
    if (k.startsWith("utm_")) alvo.searchParams.set(k, v);
  }
  return new Response(null, {
    status: 301,
    headers: {
      Location: alvo.toString(),
      "Cache-Control": "public, max-age=86400",
    },
  });
}

/** Envia ao GitHub para o dono do site autorizar o acesso ao repositório. */
function iniciarLogin(url, env) {
  const destino = new URL("https://github.com/login/oauth/authorize");
  destino.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  destino.searchParams.set("scope", ESCOPO_GITHUB);
  destino.searchParams.set("redirect_uri", `${url.origin}/admin/callback`);
  return Response.redirect(destino.toString(), 302);
}

/**
 * O GitHub devolve um código; trocamos por um token e o entregamos à janela
 * que abriu o login. O token nunca passa pela URL — só por postMessage para
 * a origem do próprio site.
 */
async function concluirLogin(url, env) {
  const codigo = url.searchParams.get("code");
  if (!codigo) return new Response("Código ausente", { status: 400 });

  const r = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      client_id: env.GITHUB_CLIENT_ID,
      client_secret: env.GITHUB_CLIENT_SECRET,
      code: codigo,
    }),
  });
  const dados = await r.json();

  const carga = dados.access_token
    ? { token: dados.access_token, provider: "github" }
    : { error: dados.error_description || "falha ao autenticar" };

  // O painel espera exatamente este formato de mensagem.
  const html = `<!DOCTYPE html><html><body><script>
(function () {
  function avisar(e) {
    window.opener.postMessage(
      'authorization:github:${dados.access_token ? "success" : "error"}:' +
      ${JSON.stringify(JSON.stringify(carga))},
      e.origin
    );
    window.removeEventListener("message", avisar, false);
  }
  window.addEventListener("message", avisar, false);
  window.opener.postMessage("authorizing:github", "*");
})();
<\/script><p>Autenticado. Pode fechar esta janela.</p></body></html>`;

  return new Response(html, {
    headers: { "content-type": "text/html;charset=UTF-8" },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Redação: login e retorno do GitHub.
    if (url.pathname === "/admin/auth") return iniciarLogin(url, env);
    if (url.pathname === "/admin/callback") return concluirLogin(url, env);

    // 1. Matéria no formato de página estática com JavaScript.
    if (url.pathname === "/artigo.html") {
      const arquivo = url.searchParams.get("file");
      if (arquivo) {
        const mapa = await carregarMapa();
        // O mapa é indexado sem o prefixo "artigos/", como o build o escreve.
        const chave = arquivo.replace(/^\/?artigos\//, "");
        const destino = mapa && mapa[chave];
        if (destino) return permanente(destino, request.url);
      }
      return permanente("/", request.url);
    }

    // 2. Categoria antiga → editoria.
    if (url.pathname === "/categoria.html") {
      const cat = url.searchParams.get("cat");
      const editoria = cat && EDITORIAS[cat];
      return permanente(editoria ? `/${editoria}/` : "/", request.url);
    }

    // 3. Permalink com data, usado até 2024. O slug continua válido: apenas
    //    o prefixo saiu quando o permalink foi reconfigurado.
    const datado = url.pathname.match(/^\/\d{4}\/\d{2}\/\d{2}\/([^/]+)\/?$/);
    if (datado) return permanente(`/${datado[1]}/`, request.url);

    // Qualquer outra coisa segue para a origem.
    return fetch(request);
  },
};
