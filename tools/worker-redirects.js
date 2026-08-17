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
 * Formatos legados resolvidos aqui com 301 permanente:
 *
 *   /artigo.html?file=/artigos/{cat}/{arq}.md   consulta o mapa publicado
 *   /categoria.html?cat={slug}                  79 categorias → 9 editorias
 *   /AAAA/MM/DD/{slug}/                         permalink usado até 2024
 *   /category/{slug}/                           categoria nativa do WordPress
 *   /tag/{slug}/                                etiqueta → busca
 *   /author/{slug}/                             autor
 *   /AAAA/MM/ e /page/N/                        arquivo e paginação
 *   ?amp, ?noamp, ?currency, ?fbclid            URL duplicada → limpa
 *
 * O permalink com data é o mais valioso: até 2024 o site usava data no
 * endereço, e os backlinks daquele período ainda apontam para lá.
 */

const SITE = "https://dunapress.org";
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
// ── Rotas nativas do WordPress ───────────────────────────────────────────
// O site intermediário usava /categoria.html?cat=x; o WordPress original
// usava /category/x/. O Google indexou os dois, e só o primeiro tinha
// tratamento aqui — daí o volume de 404 em /category/, /tag/ e /author/.
const EDITORIA_SLUG = new Set(["brasil", "mundo", "economia", "politica",
  "ciencia-e-saude", "tecnologia", "cultura", "esportes", "opiniao"]);

// Parâmetros que o WordPress e as redes sociais penduram na URL sem mudar o
// conteúdo. Cada um cria um endereço duplicado aos olhos do buscador.
// utm_ fica de fora: é medição de campanha e sobrevive ao 301.
const LIXO_QUERY = /^(amp|noamp|currency|fbclid|gclid|msclkid|replytocom|share|like_comment|_ga)$/i;

/**
 * Devolve o 301 das rotas legadas do WordPress, ou nulo quando a URL não é
 * de nenhuma delas — nesse caso o chamador segue para a origem.
 */
function rotaLegada(url, requestUrl) {
  // Parâmetro herdado que só duplica a URL: remove e manda para a limpa.
  const sujos = [...url.searchParams.keys()].filter((k) => LIXO_QUERY.test(k));
  if (sujos.length) {
    const limpo = new URL(url);
    for (const k of sujos) limpo.searchParams.delete(k);
    return permanente(limpo.pathname + limpo.search, requestUrl);
  }

  // Arquivo mensal ou anual: /2022/05/ e /2022/.
  if (/^\/\d{4}\/(\d{2}\/)?$/.test(url.pathname)) {
    return permanente("/arquivo/", requestUrl);
  }

  // Categoria nativa, inclusive aninhada: /category/a/b/ usa o último nível.
  const cat = url.pathname.match(/^\/category\/(?:[^/]+\/)*([^/]+)\/?$/);
  if (cat) {
    const s = cat[1];
    const ed = EDITORIA_SLUG.has(s)
      ? s
      : (EDITORIAS[s] || EDITORIAS[s.replace(/-en$/, "")]);
    return permanente(ed ? `/${ed}/` : "/arquivo/", requestUrl);
  }

  // Etiquetas não têm equivalente no site novo. A busca é o destino honesto:
  // entrega o que existe sobre o assunto em vez de fingir uma página.
  const tag = url.pathname.match(/^\/tag\/(?:[^/]+\/)*([^/]+)\/?$/);
  if (tag) {
    const termo = tag[1].replace(/-/g, " ");
    return permanente(`/busca/?q=${encodeURIComponent(termo)}`, requestUrl);
  }

  const autor = url.pathname.match(/^\/author\/([^/]+)\/?$/);
  if (autor) return permanente(`/autores/${autor[1]}/`, requestUrl);

  if (/^\/page\/\d+\/?$/.test(url.pathname)) {
    return permanente("/arquivo/", requestUrl);
  }
  if (url.pathname === "/home/") return permanente("/", requestUrl);

  return null;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

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

    // 4. Demais rotas nativas do WordPress: /category/, /tag/, /author/,
    //    arquivo por data, paginação e parâmetros duplicadores.
    const legada = rotaLegada(url, request.url);
    if (legada) return legada;

    // Qualquer outra coisa segue para a origem.
    return fetch(request);
  },
};
