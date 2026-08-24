// Passo 1 do caminho CLONAR: extrair a identidade REAL da página, nunca olhar e
// chutar. Se isto não rodar, o fluxo de clone da skill não fecha.
//
// Duas garantias que este arquivo precisa dar, porque página moderna quebra o
// jeito ingênuo de ler:
//   1. Cor SEMPRE em hex. Navegador atual devolve lab()/oklch()/color() no
//      getComputedStyle, e isso não dá pra colar em lugar nenhum. A conversão é
//      feita pintando a cor num canvas 1x1 e lendo o pixel de volta, o que
//      resolve qualquer espaço de cor sem depender de biblioteca.
//   2. CTA é PALPITE, nunca certeza. Em vez de um querySelector ingênuo (que na
//      tailwindcss.com elegia o badge "v4.3" do menu), medimos todos os
//      clicáveis e devolvemos uma LISTA ranqueada por heurística de botão de
//      verdade. O campo `cta` é só o primeiro da lista, e vem marcado como
//      palpite a conferir no print.
//
// playwright é CommonJS: com ESM tem que entrar pelo default export, e o
// NODE_PATH não vale pra `import` (só pra `require`). Por isso resolvemos via
// createRequire, que segue a resolução CommonJS: acha o playwright instalado
// no projeto, no NODE_PATH ou no root global do npm (funciona em qualquer máquina;
// caminho absoluto cravado aqui só funcionaria na máquina de quem escreveu).
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

// ---------------------------------------------------------------------------
// Funções puras (testadas em extrai-identidade.test.mjs)
// ---------------------------------------------------------------------------

// Pixel lido do canvas -> hex. Vive aqui e é injetada no navegador como texto,
// pra existir uma fonte única da verdade.
export function pixelParaHex(pixel) {
  if (!pixel || pixel.length < 3) return null;
  const canais = [];
  for (let i = 0; i < 3; i++) {
    const n = Number(pixel[i]);
    if (!Number.isFinite(n)) return null;
    canais.push(Math.max(0, Math.min(255, Math.round(n))));
  }
  return "#" + canais.map((n) => n.toString(16).padStart(2, "0")).join("").toUpperCase();
}

// Tokens de utilitário (Tailwind, LightningCSS) não são identidade de marca:
// são engrenagem interna do framework e quase sempre vêm vazios.
export const PREFIXOS_DE_UTILITARIO = ["--tw-", "--lightningcss-"];

export function filtrarTokens(tokens) {
  const saida = {};
  if (!tokens || typeof tokens !== "object") return saida;
  for (const [nome, valor] of Object.entries(tokens)) {
    const limpo = typeof valor === "string" ? valor.trim() : "";
    if (!limpo) continue;
    if (PREFIXOS_DE_UTILITARIO.some((p) => nome.startsWith(p))) continue;
    saida[nome] = limpo;
  }
  return saida;
}

// Heurística de "isso é botão de verdade?". Cada critério vira ponto e motivo,
// pra pessoa entender POR QUE o extrator apostou naquele elemento.
export function pontuarCta(candidato, contexto = {}) {
  const c = candidato || {};
  const motivos = [];
  let pontuacao = 0;

  const largura = Number(c.largura) || 0;
  const altura = Number(c.altura) || 0;
  const texto = String(c.texto || "").trim();
  const palavras = texto ? texto.split(/\s+/).length : 0;
  const tamanho = Number(c.tamanhoPx) || 0;
  const peso = Number(c.peso) || 400;
  const alfa = c.fundoAlfa == null ? 0 : Number(c.fundoAlfa);
  const fundo = String(c.fundoHex || "").toUpperCase();
  const fundoDoCorpo = String(contexto.fundoDoCorpo || "").toUpperCase();

  if (largura >= 72 && altura >= 32) {
    pontuacao += 3;
    motivos.push(`área clicável de botão (${Math.round(largura)}x${Math.round(altura)})`);
  } else if (largura >= 48 && altura >= 24) {
    pontuacao += 1;
    motivos.push(`área clicável pequena (${Math.round(largura)}x${Math.round(altura)})`);
  } else {
    pontuacao -= 1;
    motivos.push(`área menor que um botão (${Math.round(largura)}x${Math.round(altura)})`);
  }

  if (fundo && alfa >= 0.6 && fundo !== fundoDoCorpo) {
    pontuacao += 3;
    motivos.push(`fundo sólido diferente do corpo (${fundo})`);
  } else if (alfa < 0.6) {
    motivos.push("fundo quase transparente");
  } else {
    motivos.push("fundo igual ao do corpo");
  }

  if (c.dentroDoPrimeiroViewport) {
    pontuacao += 2;
    motivos.push("dentro do primeiro viewport");
  } else {
    motivos.push("fora do primeiro viewport");
  }

  if (palavras >= 2 && palavras <= 6) {
    pontuacao += 2;
    motivos.push(`texto de ${palavras} palavras`);
  } else if (palavras === 1) {
    motivos.push("texto de uma palavra só");
  } else if (palavras > 6) {
    pontuacao -= 2;
    motivos.push(`texto longo demais para botão (${palavras} palavras)`);
  } else {
    pontuacao -= 3;
    motivos.push("sem texto");
  }

  if (peso >= 600) {
    pontuacao += 1;
    motivos.push(`fonte pesada (${peso})`);
  }
  if (tamanho >= 14) {
    pontuacao += 1;
    motivos.push(`texto de ${tamanho}px`);
  } else if (tamanho > 0 && tamanho < 12.5) {
    pontuacao -= 1;
    motivos.push(`texto miúdo de ${tamanho}px`);
  }

  return { pontuacao, motivos };
}

export function classificarConfianca(pontuacao) {
  if (pontuacao >= 10) return "alta";
  if (pontuacao >= 5) return "media";
  return "baixa";
}

export function ranquearCtas(candidatos, contexto = {}) {
  if (!Array.isArray(candidatos)) return [];
  return candidatos
    .map((c, ordem) => {
      const { pontuacao, motivos } = pontuarCta(c, contexto);
      return { ...c, ordem, pontuacao, motivos, confianca: classificarConfianca(pontuacao) };
    })
    .sort((a, b) => {
      if (b.pontuacao !== a.pontuacao) return b.pontuacao - a.pontuacao;
      const areaA = (Number(a.largura) || 0) * (Number(a.altura) || 0);
      const areaB = (Number(b.largura) || 0) * (Number(b.altura) || 0);
      if (areaB !== areaA) return areaB - areaA;
      return a.ordem - b.ordem;
    })
    .map(({ ordem, ...resto }) => resto);
}

// ---------------------------------------------------------------------------
// Coleta dentro do navegador
// ---------------------------------------------------------------------------

// Roda dentro da página. Recebe o código de pixelParaHex como texto porque
// page.evaluate não enxerga o escopo deste módulo.
function coletarNaPagina(fonte) {
  const pixelParaHex = new Function("return (" + fonte.pixelParaHex + ")")();

  const tela = document.createElement("canvas");
  tela.width = 1;
  tela.height = 1;
  const pincel = tela.getContext("2d", { willReadFrequently: true });
  const cache = new Map();

  // Pinta a cor num canvas 1x1 e lê o pixel de volta: converte lab, oklab,
  // oklch, color(), rgb, hsl e nome de cor sem depender de biblioteca.
  function corParaHex(valor) {
    if (!valor || typeof valor !== "string") return null;
    const chave = valor.trim();
    if (!chave) return null;
    if (cache.has(chave)) return cache.get(chave);
    let saida = null;
    try {
      const sentinela = "#010203";
      pincel.fillStyle = sentinela;
      pincel.fillStyle = chave;
      const aceitou = pincel.fillStyle !== sentinela || /^#0*10*20*3$/i.test(chave.replace(/\s/g, ""));
      if (aceitou) {
        pincel.globalCompositeOperation = "copy";
        pincel.fillRect(0, 0, 1, 1);
        const p = pincel.getImageData(0, 0, 1, 1).data;
        const hex = pixelParaHex(p);
        if (hex) saida = { hex, alfa: Number((p[3] / 255).toFixed(3)) };
      }
    } catch (e) {
      saida = null;
    }
    cache.set(chave, saida);
    return saida;
  }

  const hexDe = (valor) => {
    const c = corParaHex(valor);
    return c ? c.hex : null;
  };
  const numeroPx = (valor) => {
    const n = parseFloat(valor);
    return Number.isFinite(n) ? n : 0;
  };

  function lidos(el) {
    const s = getComputedStyle(el);
    const fundo = corParaHex(s.backgroundColor);
    return {
      cor: hexDe(s.color),
      fundo: fundo && fundo.alfa > 0 ? fundo.hex : null,
      fundo_alfa: fundo ? fundo.alfa : 0,
      fonte: s.fontFamily,
      tamanho: s.fontSize,
      peso: s.fontWeight,
      espacamento: s.letterSpacing,
    };
  }

  function visivel(el) {
    const s = getComputedStyle(el);
    if (s.visibility === "hidden" || s.display === "none" || Number(s.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  const alturaDaJanela = window.innerHeight || 900;
  const texto = (el) => (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();

  // ---- paleta real, já em hex, agrupada por cor final ----
  const contagem = new Map();
  for (const el of document.querySelectorAll("*")) {
    const s = getComputedStyle(el);
    for (const bruta of [s.color, s.backgroundColor, s.borderTopColor]) {
      const c = corParaHex(bruta);
      if (!c || c.alfa === 0) continue;
      const chave = c.hex;
      const atual = contagem.get(chave) || { cor: c.hex, ocorrencias: 0, alfa_min: c.alfa };
      atual.ocorrencias += 1;
      atual.alfa_min = Math.min(atual.alfa_min, c.alfa);
      contagem.set(chave, atual);
    }
  }
  const paleta = Array.from(contagem.values())
    .sort((a, b) => b.ocorrencias - a.ocorrencias)
    .slice(0, 10);

  // ---- variáveis CSS declaradas (tokens da marca) ----
  const raiz = getComputedStyle(document.documentElement);
  const tokensBrutos = {};
  for (const folha of Array.from(document.styleSheets)) {
    let regras = [];
    try {
      regras = Array.from(folha.cssRules || []);
    } catch (e) {
      continue;
    }
    for (const r of regras) {
      if (!r.style) continue;
      for (const p of Array.from(r.style)) {
        if (!p.startsWith("--")) continue;
        // O valor no :root é o que vale; quando o token é declarado em outro
        // seletor (tema escuro, componente), o :root devolve vazio e a gente cai
        // no valor da própria regra em vez de descartar o token.
        let valor = raiz.getPropertyValue(p).trim() || r.style.getPropertyValue(p).trim();
        const cor = valor ? corParaHex(valor) : null;
        if (cor && cor.alfa > 0) valor = cor.hex;
        tokensBrutos[p] = valor;
      }
    }
  }

  // ---- candidatos a CTA, medidos ----
  const seletorDeClicavel = [
    "a",
    "button",
    '[role="button"]',
    'input[type="submit"]',
    'input[type="button"]',
    "[class*=cta]",
    "[class*=btn]",
    "[class*=button]",
  ].join(",");
  const candidatos = [];
  for (const el of new Set(document.querySelectorAll(seletorDeClicavel))) {
    if (!visivel(el)) continue;
    const conteudo = el.tagName === "INPUT" ? String(el.value || "").trim() : texto(el);
    if (!conteudo) continue;
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    const fundo = corParaHex(s.backgroundColor);
    candidatos.push({
      texto: conteudo.slice(0, 90),
      tag: el.tagName.toLowerCase(),
      classe: typeof el.className === "string" ? el.className.slice(0, 120) : "",
      href: el.getAttribute("href") || null,
      largura: Math.round(r.width),
      altura: Math.round(r.height),
      topo: Math.round(r.top),
      dentroDoPrimeiroViewport: r.top < alturaDaJanela && r.bottom > 0,
      fundoHex: fundo && fundo.alfa > 0 ? fundo.hex : null,
      fundoAlfa: fundo ? fundo.alfa : 0,
      corHex: hexDe(s.color),
      peso: numeroPx(s.fontWeight) || 400,
      tamanhoPx: numeroPx(s.fontSize),
      raioPx: numeroPx(s.borderRadius),
    });
  }

  // ---- título principal, com plano B pra página sem h1 ----
  const noPrimeiroViewport = (el) => {
    const r = el.getBoundingClientRect();
    return r.top < alturaDaJanela && r.bottom > 0;
  };
  // Só o texto que é filho direto do elemento: evita colar a navegação inteira
  // num "título" quando a página não tem cabeçalho nenhum.
  const textoDireto = (el) =>
    Array.from(el.childNodes)
      .filter((n) => n.nodeType === 3)
      .map((n) => n.textContent)
      .join(" ")
      .replace(/\s+/g, " ")
      .trim();

  function acharTitulo() {
    const h1 = Array.from(document.querySelectorAll("h1")).filter(visivel).find((el) => texto(el));
    if (h1) return { el: h1, texto: texto(h1), origem: "h1" };

    // Sem h1: o maior cabeçalho vale, mas o do topo da página vale mais que um
    // do meio (num FAQ, por exemplo, todo h3 tem o mesmo tamanho).
    const cabecalhos = Array.from(document.querySelectorAll("h2,h3,h4,h5,h6")).filter(
      (el) => visivel(el) && texto(el)
    );
    const doTopo = cabecalhos.filter(noPrimeiroViewport);
    const pool = doTopo.length ? doTopo : cabecalhos;
    if (pool.length) {
      const maior = pool
        .slice()
        .sort(
          (a, b) => numeroPx(getComputedStyle(b).fontSize) - numeroPx(getComputedStyle(a).fontSize)
        )[0];
      return { el: maior, texto: texto(maior), origem: "maior-cabecalho" };
    }

    // Página sem cabeçalho nenhum (Hacker News é assim): o maior texto próprio
    // do primeiro viewport.
    let melhor = null;
    let maiorFonte = 0;
    for (const el of document.querySelectorAll("body *")) {
      if (!visivel(el) || !noPrimeiroViewport(el)) continue;
      const proprio = textoDireto(el);
      if (proprio.replace(/[^\p{L}\p{N}]/gu, "").length < 3) continue;
      const t = numeroPx(getComputedStyle(el).fontSize);
      if (t > maiorFonte) {
        maiorFonte = t;
        melhor = { el, texto: proprio };
      }
    }
    return melhor ? { el: melhor.el, texto: melhor.texto, origem: "maior-texto" } : null;
  }
  const tituloAchado = acharTitulo();

  const corpo = lidos(document.body);

  return {
    titulo: document.title,
    paleta,
    tokensBrutos,
    candidatosDeCta: candidatos,
    fundoDoCorpo: corpo.fundo,
    h1: tituloAchado
      ? {
          texto: tituloAchado.texto.slice(0, 300),
          origem: tituloAchado.origem,
          estilo: lidos(tituloAchado.el),
        }
      : null,
    corpo,
    secoes: Array.from(document.querySelectorAll("section")).map((s) => ({
      classe: typeof s.className === "string" ? s.className : "",
      titulo: s.querySelector("h1,h2,h3")?.textContent.trim() || null,
    })),
    imagens: Array.from(document.images).map((i) => i.src),
  };
}

// ---------------------------------------------------------------------------
// Orquestração
// ---------------------------------------------------------------------------

function carregarPlaywright() {
  const require = createRequire(import.meta.url);
  try {
    return require("playwright");
  } catch {
    try {
      const rootGlobal = execSync("npm root -g", { encoding: "utf8" }).trim();
      return require(path.join(rootGlobal, "playwright"));
    } catch {
      console.error(
        "playwright não encontrado. Instale com:\n" +
          "  npm install -g playwright && npx playwright install chromium"
      );
      process.exit(1);
    }
  }
}

export async function extrairIdentidade(alvo) {
  const { chromium } = carregarPlaywright();
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({ viewport: { width: 1440, height: 1200 } });
  try {
    try {
      await pagina.goto(alvo, { waitUntil: "networkidle", timeout: 45000 });
    } catch {
      // Página com animação ou polling nunca fica "idle": vale tentar de novo
      // esperando só o DOM, em vez de desistir.
      await pagina.goto(alvo, { waitUntil: "domcontentloaded", timeout: 45000 });
    }

    const bruto = await pagina.evaluate(coletarNaPagina, {
      pixelParaHex: pixelParaHex.toString(),
    });

    const tokens = filtrarTokens(bruto.tokensBrutos);
    const candidatos = ranquearCtas(bruto.candidatosDeCta, {
      fundoDoCorpo: bruto.fundoDoCorpo,
    }).slice(0, 8);
    const primeiro = candidatos[0] || null;

    return {
      url: alvo,
      titulo: bruto.titulo,
      aviso:
        "cta e cta_candidatos são PALPITE de heurística: confira no print antes de usar. " +
        "Cores já vêm em hex; tokens de utilitário (--tw-, --lightningcss-) foram descartados.",
      paleta: bruto.paleta,
      tokens,
      tokens_descartados: Object.keys(bruto.tokensBrutos || {}).length - Object.keys(tokens).length,
      h1: bruto.h1,
      cta: primeiro
        ? {
            texto: primeiro.texto,
            confianca: primeiro.confianca,
            pontuacao: primeiro.pontuacao,
            observacao: "primeiro da lista ranqueada, é palpite: confirme no print",
            estilo: {
              cor: primeiro.corHex,
              fundo: primeiro.fundoHex,
              fundo_alfa: primeiro.fundoAlfa,
              tamanho: `${primeiro.tamanhoPx}px`,
              peso: String(primeiro.peso),
              raio: `${primeiro.raioPx}px`,
            },
          }
        : null,
      cta_candidatos: candidatos,
      corpo: bruto.corpo,
      secoes: bruto.secoes,
      imagens: bruto.imagens,
    };
  } finally {
    await navegador.close();
  }
}

const executadoDireto =
  process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (executadoDireto) {
  const alvo = process.argv[2];
  if (!alvo) {
    console.error("uso: node extrai-identidade.mjs <url>");
    process.exit(1);
  }
  try {
    const identidade = await extrairIdentidade(alvo);
    console.log(JSON.stringify(identidade, null, 2));
  } catch (e) {
    console.error(
      `\nERRO: não foi possível extrair a identidade de ${alvo}.\n` +
        "Confirme que o endereço está correto e que a página está no ar.\n" +
        `Detalhe: ${e.message}`
    );
    process.exit(1);
  }
}
