// Testa o passo 1 do caminho CLONAR: extrair a identidade REAL da pagina,
// nunca olhar e chutar. Se isto nao rodar, o fluxo de clone da skill nao fecha.
// playwright e CommonJS: com ESM tem que entrar pelo default export, e o
// NODE_PATH nao vale pra `import` (so pra `require`). Por isso resolvemos via
// createRequire, que segue a resolucao CommonJS: acha o playwright instalado
// no projeto, no NODE_PATH ou no root global do npm (funciona em qualquer maquina;
// caminho absoluto cravado aqui so funcionaria na maquina de quem escreveu).
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import path from "node:path";

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try {
    return require("playwright");
  } catch {
    try {
      const rootGlobal = execSync("npm root -g", { encoding: "utf8" }).trim();
      return require(path.join(rootGlobal, "playwright"));
    } catch {
      console.error(
        "playwright nao encontrado. Instale com:\n" +
          "  npm install -g playwright && npx playwright install chromium"
      );
      process.exit(1);
    }
  }
}
const { chromium } = carregarPlaywright();

const alvo = process.argv[2];
if (!alvo) {
  console.error("uso: node extrai_identidade.mjs <url>");
  process.exit(1);
}

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 1440, height: 1200 } });
try {
  await pagina.goto(alvo, { waitUntil: "networkidle" });
} catch (e) {
  console.error(
    `\nERRO: nao foi possivel abrir ${alvo}.\n` +
      "Confirme que o endereco esta correto e que a pagina esta no ar.\n" +
      `Detalhe: ${e.message}`
  );
  await navegador.close();
  process.exit(1);
}

const identidade = await pagina.evaluate(() => {
  const lidos = (el) => {
    const s = getComputedStyle(el);
    return {
      cor: s.color,
      fundo: s.backgroundColor,
      fonte: s.fontFamily,
      tamanho: s.fontSize,
      peso: s.fontWeight,
      espacamento: s.letterSpacing,
    };
  };

  // paleta real: conta as cores que a pagina de fato usa
  const contagem = {};
  for (const el of document.querySelectorAll("*")) {
    const s = getComputedStyle(el);
    for (const c of [s.color, s.backgroundColor, s.borderColor]) {
      if (c && c !== "rgba(0, 0, 0, 0)" && c !== "transparent") {
        contagem[c] = (contagem[c] || 0) + 1;
      }
    }
  }
  const paleta = Object.entries(contagem)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([cor, n]) => ({ cor, ocorrencias: n }));

  // variaveis CSS declaradas (tokens da marca)
  const raiz = getComputedStyle(document.documentElement);
  const tokens = {};
  for (const folha of Array.from(document.styleSheets)) {
    let regras = [];
    try { regras = Array.from(folha.cssRules || []); } catch { continue; }
    for (const r of regras) {
      if (r.style) {
        for (const p of Array.from(r.style)) {
          if (p.startsWith("--")) tokens[p] = raiz.getPropertyValue(p).trim();
        }
      }
    }
  }

  const h1 = document.querySelector("h1");
  const cta = document.querySelector("a[class*=cta], button, .cta");

  return {
    titulo: document.title,
    paleta,
    tokens,
    h1: h1 ? { texto: h1.textContent.trim(), estilo: lidos(h1) } : null,
    cta: cta ? { texto: cta.textContent.trim(), estilo: lidos(cta) } : null,
    corpo: lidos(document.body),
    secoes: Array.from(document.querySelectorAll("section")).map((s) => ({
      classe: s.className,
      titulo: s.querySelector("h1,h2,h3")?.textContent.trim() || null,
    })),
    imagens: Array.from(document.images).map((i) => i.src),
  };
});

await navegador.close();
console.log(JSON.stringify(identidade, null, 2));
