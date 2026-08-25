/**
 * GATE DE VÍDEO para página. As 7 checagens do item 8 do gate de qualidade,
 * agora executáveis.
 *
 * POR QUE VIROU SCRIPT: o gate existia em prosa, e prosa não pega o que script
 * pega. Toda checagem daqui nasceu de defeito que passou por uma revisão humana
 * numa pagina de lancamento em producao e so apareceu quando alguem mediu.
 *
 * USO
 *   node gate-video.mjs --url http://127.0.0.1:8765/ --publico ./public
 *
 * PRÉ
 *   Playwright com chromium baixado (o mesmo da prova de entrega):
 *     npm install -g playwright && npx playwright install chromium
 *   ffmpeg e ffprobe no PATH.
 *
 *   O gate SOBE O NAVEGADOR SOZINHO. Não precisa de Edge, nem de CDP no ar.
 *   Quem já tiver um navegador com porta de depuração aberta pode reaproveitar:
 *     node gate-video.mjs --url ... --publico ... --cdp http://localhost:9333
 *   (opcional; sem a flag, nada de CDP é usado)
 */
import { createRequire } from "node:module";
import { execFileSync, execSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { join } from "node:path";

// playwright e CommonJS e o NODE_PATH nao vale pra `import` (so pra `require`).
// createRequire segue a resolucao CommonJS: projeto, NODE_PATH ou root global do
// npm. Nunca cravar caminho absoluto aqui: so funcionaria numa maquina.
const require = createRequire(import.meta.url);

/* MENSAGEM NO LUGAR DE STACK TRACE. Qualquer falha inesperada (navegador não
   baixado, caminho de frames inválido, browser que caiu no meio) sai em UMA
   linha acionável. Sem isso a saída era "node:internal/..." com caminho de
   arquivo do node, e parecia que a skill inteira tinha quebrado. */
function explicarFalha(e) {
  const msg = String((e && e.message) || e);
  if (msg.includes("Executable doesn't exist")) {
    return "FALHA: o navegador do Playwright nao foi baixado. Rode: npx playwright install chromium";
  }
  return `FALHA no gate de video: ${msg.split("\n")[0]}`;
}
function bloquear(e) {
  console.error(explicarFalha(e));
  console.error("GATE BLOQUEADO: conserte a verificacao antes de declarar pronto.");
  process.exit(1);
}
process.on("uncaughtException", bloquear);
process.on("unhandledRejection", bloquear);

function carregarPlaywright() {
  try {
    return require("playwright");
  } catch {
    try {
      return require(join(execSync("npm root -g", { encoding: "utf8" }).trim(), "playwright"));
    } catch {
      console.error(
        "FALHA: playwright nao encontrado. Instale com:\n" +
          "  npm install -g playwright && npx playwright install chromium"
      );
      process.exit(1);
    }
  }
}
const { chromium } = carregarPlaywright();

const arg = (n, d) => {
  const i = process.argv.indexOf(`--${n}`);
  return i > -1 ? process.argv[i + 1] : d;
};
const URL_ALVO = arg("url", "http://127.0.0.1:8765/");
const PUBLICO = arg("publico", "./public");
// CDP é OPCIONAL e opt-in. Antes o gate só sabia falar com um Edge headless numa
// porta fixa, que ninguém tinha no ar: o gate reprovava a si mesmo antes de olhar
// uma linha da página. Agora ele sobe o chromium do Playwright, que já é
// dependência obrigatória da skill.
const CDP = process.argv.includes("--cdp") ? arg("cdp", "http://localhost:9333") : null;
const FRAMES = arg("frames", "./_gate-frames");

const TELAS = [
  { nome: "celular", w: 390, h: 844, movel: true },
  { nome: "desktop", w: 1440, h: 900, movel: false },
];

const ffprobe = (f) => {
  try {
    const o = execFileSync("ffprobe", ["-v", "error", "-select_streams", "v:0",
      "-show_entries", "stream=width,height", "-of", "csv=p=0", f], { encoding: "utf-8" }).trim();
    const [w, h] = o.split(",").map(Number);
    return { w, h, razao: +(w / h).toFixed(3) };
  } catch { return null; }
};

let falhas = 0;
const reprova = (msg) => { falhas++; console.log(`   REPROVA  ${msg}`); };
const ok = (msg) => console.log(`   ok       ${msg}`);

let browser;
if (CDP) {
  try {
    browser = await chromium.connectOverCDP(CDP);
  } catch (e) {
    console.error(
      `\nERRO: voce passou --cdp ${CDP} e nao ha navegador escutando nesse endereco.\n` +
        "Tire a flag --cdp para o gate subir o chromium do Playwright sozinho, ou suba o navegador com a porta de depuracao aberta.\n" +
        `Detalhe: ${e.message}`
    );
    process.exit(1);
  }
} else {
  browser = await chromium.launch({ headless: true });
}
console.log("=".repeat(72));
console.log(`GATE DE VIDEO  ${URL_ALVO}`);
console.log("=".repeat(72));

/* Coleta o que a página realmente usa, em cada tela: caminho do arquivo, a caixa
   pintada, e se está acima da dobra. */
const porTela = {};
for (const t of TELAS) {
  const ctx = await browser.newContext({
    viewport: { width: t.w, height: t.h }, isMobile: t.movel, hasTouch: t.movel,
  });
  const page = await ctx.newPage();
  try {
    await page.goto(URL_ALVO, { waitUntil: "load", timeout: 90000 });
  } catch (e) {
    console.error(
      `\nERRO: nao foi possivel abrir ${URL_ALVO} (tela ${t.nome}).\n` +
        "Confirme que a pagina esta no ar nesse endereco antes de rodar o gate.\n" +
        `Detalhe: ${e.message}`
    );
    await browser.close();
    process.exit(1);
  }
  await page.evaluate(async () => {
    for (let y = 0; y < document.documentElement.scrollHeight; y += 600) {
      scrollTo(0, y); await new Promise((r) => setTimeout(r, 90));
    }
    scrollTo(0, 0);
  });
  await page.waitForTimeout(2500);

  porTela[t.nome] = await page.evaluate(() => {
    // FONTES: o <video> quase nunca traz `src` direto. O padrao recomendado pela
    // propria skill e WebM + MP4, que so existe com filhos <source>. Enquanto esta
    // funcao lia so o atributo `src`, o gate media ZERO arquivo na pagina que a
    // skill manda construir, e passava em silencio.
    const fontes = (v) => {
      const s = new Set();
      if (v.getAttribute("src")) s.add(v.getAttribute("src"));
      if (v.dataset.src) s.add(v.dataset.src);
      (v.dataset.fila || "").split(",").filter(Boolean).forEach((x) => s.add(x.trim()));
      for (const src of v.querySelectorAll("source")) {
        if (src.getAttribute("src")) s.add(src.getAttribute("src"));
        if (src.dataset.src) s.add(src.dataset.src);
      }
      return [...s];
    };
    return [...document.querySelectorAll("video")].map((v) => {
      const r = v.getBoundingClientRect();
      const e = getComputedStyle(v);
      return {
        fontes: fontes(v),
        poster: v.getAttribute("poster") || "",
        caixa: { w: Math.round(r.width), h: Math.round(r.height) },
        objectFit: e.objectFit,
        objectPosition: e.objectPosition,
        acimaDaDobra: r.top + scrollY < innerHeight,
        classe: String(v.className || ""),
        // TRILHA = a seção onde o vídeo vive, não a classe dele. A classe do
        // <video> quase sempre é vazia, e agrupar por ela jogava os 14 clipes
        // da página numa "trilha" só, acusando 6 razões onde na verdade são
        // três trilhas distintas com problemas diferentes.
        // `ol` na lista, e NUNCA `li`: com `li` cada card viraria a propria
        // trilha, e a checagem de razao unica passaria sozinha com um clipe em
        // cada grupo. Gate que se poupa nao serve. Com `ol` os 6 cards das
        // fases sao um grupo so, que e o que precisa ser comparado.
        trilha: (v.closest("section, figure, ul, ol")?.className || "").split(/\s+/)
          .find((c) => c.startsWith("v3-") || c.startsWith("secao")) || "raiz",
      };
    });
  });
  await ctx.close();
}

/* 1. RAZAO UNICA POR TRILHA
   A fila do herói da /v3 acumulou 11 clipes com 5 razões. Não existe caixa que
   sirva pras cinco, e o `cover` decide sozinho o que cortar. */
console.log("\n[1] RAZAO UNICA POR TRILHA");
const trilhas = new Map();
let medidos1 = 0;
for (const v of porTela.desktop) {
  const chave = v.trilha || "sem-trilha";
  if (!trilhas.has(chave)) trilhas.set(chave, new Set());
  for (const f of v.fontes) {
    const p = join(PUBLICO, f.replace(/^\//, ""));
    const m = existsSync(p) && ffprobe(p);
    if (m) { trilhas.get(chave).add(m.razao); medidos1++; }
  }
}
/* GATE QUE NAO CONSEGUE MEDIR TEM QUE REPROVAR. Antes isto era um aviso, e uma
   pagina com 14 clipes saia "PASSA (0 checagens falhando)" so porque nenhum
   arquivo tinha sido resolvido em disco. Aviso nao bloqueia nada. */
const totalVideos = porTela.desktop.length;
const totalFontes = porTela.desktop.reduce((n, v) => n + v.fontes.length, 0);
if (medidos1 === 0 && totalVideos > 0) {
  reprova(
    `a pagina tem ${totalVideos} <video> (${totalFontes} fonte(s) declarada(s)) e NENHUM arquivo foi medido. ` +
      `Confira se --publico "${PUBLICO}" e mesmo a pasta que serve esses arquivos e se o ffprobe esta no PATH. ` +
      "Gate que nao consegue medir nao aprova."
  );
} else if (medidos1 === 0) {
  ok("a pagina nao tem <video>: nada a verificar neste gate");
} else {
  for (const [nome, razoes] of trilhas) {
    if (!razoes.size) continue;
    if (razoes.size > 1) reprova(`trilha "${nome.slice(0, 40)}" tem ${razoes.size} razoes: ${[...razoes].join(", ")}`);
    else ok(`trilha "${nome.slice(0, 40)}" com razao unica ${[...razoes][0]}`);
  }
}

/* 2 e 3. ESCALA e CORTE
   Arquivo muito maior que a caixa é banda jogada fora; corte acima de 15%
   significa que quem decide o conteúdo do clipe é o CSS, não o encoder.

   O DPR ENTRA NA CONTA, e este gate errou DUAS vezes antes de acertar a pergunta.
   Primeiro comparava pixel de arquivo com pixel CSS e acusou 14 clipes de "2x de
   sobra" que estavam certos numa tela retina. Depois assumiu DPR 2 em todo lugar
   e passou a acusar de "borrado" quase tudo no desktop, onde a maioria dos
   monitores ainda é DPR 1.

   A pergunta certa tem duas pontas, e só reprova quem falha numa delas de fato:
     borrado          arquivo menor que 0,9x da caixa em DPR 1, ou seja ruim
                      até no monitor comum;
     banda jogada fora  arquivo maior que 1,3x da caixa em DPR 2, ou seja
                      desperdício até na tela retina.
   Entre os dois extremos existe uma faixa larga que é escolha legítima, e gate
   não opina em escolha legítima. */
console.log("\n[2+3] ESCALA E CORTE (borrado em DPR1, desperdicio em DPR2)");
let medidos2 = 0;
for (const t of TELAS) {
  for (const v of porTela[t.nome]) {
    if (!v.caixa.w || !v.caixa.h) continue;
    for (const f of v.fontes) {
      const p = join(PUBLICO, f.replace(/^\//, ""));
      if (!existsSync(p)) continue;
      const m = ffprobe(p);
      if (!m) continue;
      medidos2++;
      const nome = f.split("/").pop();
      const emDpr1 = Math.max(m.w / v.caixa.w, m.h / v.caixa.h);
      const emDpr2 = Math.max(m.w / (v.caixa.w * 2), m.h / (v.caixa.h * 2));
      if (emDpr1 < 0.9) reprova(`${t.nome} ${nome}: ${m.w}x${m.h} numa caixa ${v.caixa.w}x${v.caixa.h} (${emDpr1.toFixed(2)}x em DPR1, borrado ate no monitor comum)`);
      else if (emDpr2 > 1.3) reprova(`${t.nome} ${nome}: ${m.w}x${m.h} numa caixa ${v.caixa.w}x${v.caixa.h} (${emDpr2.toFixed(2)}x em DPR2, banda jogada fora ate na retina)`);
      if (v.objectFit === "cover") {
        const esc = Math.max(v.caixa.w / m.w, v.caixa.h / m.h);
        const pw2 = m.w * esc, ph = m.h * esc;
        const cx = Math.max(0, 1 - v.caixa.w / pw2), cy = Math.max(0, 1 - v.caixa.h / ph);
        if (Math.max(cx, cy) > 0.15) {
          /* `object-position` fora do centro significa que ALGUEM AFINOU o corte
             pra preservar a parte que importa. Na /v3 o clipe do medidor é 4:3
             numa caixa 16:9 e leva `object-position: 50% 100%` justamente pra o
             "97" não ser cortado. Reprovar isso é o gate opinando em escolha
             legítima, que é o oposto do que ele existe pra fazer. Vira aviso. */
          const afinado = v.objectPosition && !/^50%\s+50%$/.test(v.objectPosition.trim());
          const txt = `${t.nome} ${nome}: cover corta ${(cx * 100).toFixed(1)}% h / ${(cy * 100).toFixed(1)}% v`;
          if (afinado) console.log(`   aviso    ${txt} (object-position ${v.objectPosition}: corte afinado de proposito)`);
          else reprova(txt);
        }
      }
    }
  }
}
if (medidos2 === 0 && totalVideos > 0) {
  reprova("0 arquivos medidos e a pagina TEM video: escala e corte ficaram sem verificacao (ver a checagem [1])");
} else if (medidos2 === 0) {
  ok("a pagina nao tem <video>: nada a medir");
} else if (!falhas) {
  ok(`nenhum arquivo desproporcional a caixa (${medidos2} arquivo(s) medido(s))`);
}

/* 4. POSTER com hash proprio
   Derivar o pôster do nome do mp4 levou 6 pôsteres a 404 quando os vídeos foram
   reencodados: a seção virou seis lajes pretas. */
console.log("\n[4] POSTER");
for (const v of porTela.desktop) {
  if (!v.poster) { reprova(`video sem poster: .${v.classe.slice(0, 40)}`); continue; }
  const p = join(PUBLICO, v.poster.replace(/^\//, ""));
  if (!existsSync(p)) { reprova(`poster nao existe em disco: ${v.poster}`); continue; }
  const baseP = v.poster.split("/").pop().replace(/\.\w+$/, "");
  const colide = v.fontes.some((f) => f.split("/").pop().replace(/\.\w+$/, "") === baseP);
  if (colide) reprova(`poster com o MESMO hash do mp4 (${baseP}): reencodar o video leva o poster a 404`);
  else ok(`poster ok: ${v.poster.split("/").pop()}`);
}

/* 5. CONTEUDO DO QUADRO
   A checagem que mais pega coisa. Um clipe da /v3 tinha o texto do terminal
   saindo do quadro NO PROPRIO ARQUIVO, e isso só apareceu extraindo o frame. */
console.log("\n[5] CONTEUDO DO QUADRO");
/* LIMPAR A PASTA ANTES. Contar `readdirSync(FRAMES).length` sem limpar fazia o
   gate mandar OLHAR quadros de OUTRA pagina, sobrados da corrida anterior: ele
   anunciava "0 clipe(s), 2 frames" e os 2 frames eram de outro projeto. */
if (existsSync(FRAMES)) rmSync(FRAMES, { recursive: true, force: true });
mkdirSync(FRAMES, { recursive: true });
const vistos = new Set();
for (const v of porTela.desktop) for (const f of v.fontes) {
  const p = join(PUBLICO, f.replace(/^\//, ""));
  if (vistos.has(p) || !existsSync(p)) continue;
  vistos.add(p);
  const base = f.split("/").pop().replace(/\.\w+$/, "");
  for (let i = 1; i <= 6; i++) {
    try {
      execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-ss", String(i), "-i", p,
        "-frames:v", "1", "-vf", "scale=420:-1", join(FRAMES, `${base}-f${i}.png`)]);
    } catch { /* clipe mais curto que o instante pedido */ }
  }
}
const n = readdirSync(FRAMES).length;
if (vistos.size === 0) {
  console.log(`   NENHUM frame extraido: nenhum arquivo de video foi encontrado em ${PUBLICO}.`);
  if (totalVideos > 0) reprova("checagem [5] sem frame nenhum pra olhar (arquivos nao resolvidos em disco)");
} else {
  console.log(`   ${vistos.size} clipe(s), ${n} frames NOVOS em ${FRAMES}`);
  console.log("   ESTA CHECAGEM NAO E AUTOMATICA: abra os frames e OLHE.");
  console.log("   procure: texto cortado na borda, nome de cliente, credencial, ID interno, valor.");
}

/* 6. LCP: video acima da dobra exige preload no poster */
console.log("\n[6] LCP");
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true });
const page = await ctx.newPage();
try {
  await page.goto(URL_ALVO, { waitUntil: "load", timeout: 90000 });
} catch (e) {
  console.error(
    `\nERRO: nao foi possivel abrir ${URL_ALVO} (checagem [6] LCP).\n` +
      "Confirme que a pagina esta no ar nesse endereco antes de rodar o gate.\n" +
      `Detalhe: ${e.message}`
  );
  await browser.close();
  process.exit(1);
}
const lcp = await page.evaluate(() => {
  const v = [...document.querySelectorAll("video")].find((x) => {
    const r = x.getBoundingClientRect();
    return r.top < innerHeight && r.height > 0;
  });
  if (!v) return { temVideoNaDobra: false };
  const poster = v.getAttribute("poster");
  const link = [...document.querySelectorAll('link[rel="preload"][as="image"]')]
    .find((l) => poster && l.getAttribute("href") === poster);
  return {
    temVideoNaDobra: true, poster,
    temPreload: !!link,
    prioridade: link?.getAttribute("fetchpriority") || link?.fetchPriority || "",
  };
});
if (!lcp.temVideoNaDobra) ok("nenhum video acima da dobra no celular");
else if (!lcp.temPreload) reprova(`video acima da dobra e o poster (${lcp.poster}) nao tem <link rel="preload">`);
else if ((lcp.prioridade || "").toLowerCase() !== "high") reprova(`poster tem preload mas sem fetchPriority="high"`);
else ok(`poster do heroi com preload e prioridade alta`);

/* 7. MOVIMENTO REDUZIDO: sobra so o poster */
console.log("\n[7] MOVIMENTO REDUZIDO");
await ctx.close();
const ctxR = await browser.newContext({
  viewport: { width: 1440, height: 900 }, reducedMotion: "reduce",
});
const pageR = await ctxR.newPage();
try {
  await pageR.goto(URL_ALVO, { waitUntil: "load", timeout: 90000 });
} catch (e) {
  console.error(
    `\nERRO: nao foi possivel abrir ${URL_ALVO} (checagem [7] movimento reduzido).\n` +
      "Confirme que a pagina esta no ar nesse endereco antes de rodar o gate.\n" +
      `Detalhe: ${e.message}`
  );
  await browser.close();
  process.exit(1);
}
await pageR.evaluate(async () => {
  for (let y = 0; y < document.documentElement.scrollHeight; y += 700) {
    scrollTo(0, y); await new Promise((r) => setTimeout(r, 80));
  }
});
await pageR.waitForTimeout(2000);
const red = await pageR.evaluate(() => ({
  tocando: [...document.querySelectorAll("video")].filter((v) => !v.paused && !v.ended).length,
  animando: document.getAnimations().filter((a) => a.playState === "running"
    && (a.effect?.getTiming?.().duration ?? 0) > 0).length,
}));
if (red.tocando || red.animando) reprova(`com reduced-motion sobrou ${red.tocando} video(s) tocando e ${red.animando} animacao(oes) rodando`);
else ok("com reduced-motion nao sobra video tocando nem animacao rodando");
await ctxR.close();

console.log("\n" + "=".repeat(72));
console.log(`VEREDITO: ${falhas ? "REPROVA" : "PASSA"} (${falhas} checagem(ns) dura(s) falhando)`);
console.log("lembrete: a checagem [5] depende de alguem OLHAR os frames.");
await browser.close();
process.exit(falhas ? 1 : 0);
