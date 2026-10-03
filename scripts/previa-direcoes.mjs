#!/usr/bin/env node
/**
 * Prévias da etapa PLANO (references/plano.md).
 *
 * Modo direções: três HTML de primeira dobra viram, na pasta de saída,
 *   direcao-a.png e direcao-a-celular.png (1440x900 e 390x844), idem b e c,
 *   e direcoes.png com as três lado a lado (desktop em cima, celular embaixo).
 *   node scripts/previa-direcoes.mjs --saida <dir>/plano <a.html> <b.html> <c.html>
 *
 * Modo miniaturas: cada .html de uma pasta (references/secoes/) vira <nome>.png pequeno para o
 * cardápio de seções do plano.
 *   node scripts/previa-direcoes.mjs --miniaturas <dir-da-skill>/references/secoes --saida <dir>/plano/miniaturas
 *
 * Sai 1 com mensagem de uma linha se não forem 3 direções, se um arquivo não existir ou se o
 * navegador falhar. Usa o Chromium do Playwright.
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(execSync('npm root -g', { encoding: 'utf8' }).trim(), 'playwright')); }
    catch { console.error('FALHA: playwright não encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}

const args = process.argv.slice(2);
const valor = (flag) => { const i = args.indexOf(flag); return i >= 0 ? args[i + 1] : undefined; };
const saida = valor('--saida');
const miniaturas = valor('--miniaturas');
const soltos = args.filter((a, i) => !a.startsWith('--') && !['--saida', '--miniaturas'].includes(args[i - 1]));

if (!saida) {
  console.error('uso: node previa-direcoes.mjs --saida <pasta> <a.html> <b.html> <c.html> | --miniaturas <pasta-html> --saida <pasta>');
  process.exit(2);
}

async function abrir(browser, largura, altura, escala = 1) {
  const ctx = await browser.newContext({ viewport: { width: largura, height: altura }, deviceScaleFactor: escala,
    isMobile: largura < 768, hasTouch: largura < 768, reducedMotion: 'reduce' });
  return { ctx, page: await ctx.newPage() };
}

async function fotografar(browser, arquivo, destino, largura, altura, escala = 1) {
  const { ctx, page } = await abrir(browser, largura, altura, escala);
  await page.goto(pathToFileURL(path.resolve(arquivo)).href, { waitUntil: 'networkidle', timeout: 30000 });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(400);
  await page.screenshot({ path: destino, clip: { x: 0, y: 0, width: largura, height: altura } });
  await ctx.close();
}

async function direcoes(browser) {
  if (soltos.length !== 3) {
    console.error(`FALHA: são 3 direções, uma por arquivo HTML; vieram ${soltos.length}.`);
    process.exit(1);
  }
  for (const f of soltos) {
    if (!fs.existsSync(f)) { console.error(`FALHA: ${f} não existe.`); process.exit(1); }
  }
  fs.mkdirSync(saida, { recursive: true });
  const letras = ['a', 'b', 'c'];
  for (const [i, f] of soltos.entries()) {
    await fotografar(browser, f, path.join(saida, `direcao-${letras[i]}.png`), 1440, 900);
    await fotografar(browser, f, path.join(saida, `direcao-${letras[i]}-celular.png`), 390, 844);
  }
  // Prancha lado a lado: uma coluna por direção, desktop em cima e celular embaixo, mesma escala.
  const colunas = letras.map((l) => `
    <figure>
      <figcaption>Direção ${l.toUpperCase()}</figcaption>
      <img class="d" src="direcao-${l}.png" alt="">
      <img class="m" src="direcao-${l}-celular.png" alt="">
    </figure>`).join('');
  const prancha = path.join(saida, `_prancha-${process.pid}.html`);
  fs.writeFileSync(prancha, `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
    body{margin:0;background:#f2f2f2;font:600 22px/1.2 system-ui,sans-serif;color:#1a1a1a}
    main{display:grid;grid-template-columns:repeat(3,600px);gap:32px;padding:32px}
    figure{margin:0;display:grid;gap:14px;justify-items:center}
    figcaption{justify-self:start}
    img{display:block;box-shadow:0 0 0 1px #0002}
    .d{width:600px;height:375px}.m{width:195px;height:422px}
  </style></head><body><main>${colunas}</main></body></html>`);
  const { ctx, page } = await abrir(browser, 1928, 900);
  await page.goto(pathToFileURL(prancha).href, { waitUntil: 'load' });
  await page.screenshot({ path: path.join(saida, 'direcoes.png'), fullPage: true });
  await ctx.close();
  fs.rmSync(prancha);
  console.log(`ok: ${path.join(saida, 'direcoes.png')} e as 6 prévias (desktop 1440 e celular 390) gravadas.`);
}

async function cardapio(browser) {
  if (!fs.existsSync(miniaturas)) { console.error(`FALHA: ${miniaturas} não existe.`); process.exit(1); }
  const htmls = fs.readdirSync(miniaturas).filter((f) => f.endsWith('.html')).sort();
  if (!htmls.length) { console.error(`FALHA: nenhum .html em ${miniaturas}.`); process.exit(1); }
  fs.mkdirSync(saida, { recursive: true });
  for (const f of htmls) {
    await fotografar(browser, path.join(miniaturas, f), path.join(saida, f.replace(/\.html$/, '.png')), 1200, 750, 0.5);
  }
  console.log(`ok: ${htmls.length} miniatura(s) em ${saida}.`);
}

const { chromium } = carregarPlaywright();
let browser;
try {
  browser = await chromium.launch();
  if (miniaturas) await cardapio(browser); else await direcoes(browser);
} catch (e) {
  const msg = String((e && e.message) || e).split('\n')[0];
  console.error(msg.includes("Executable doesn't exist")
    ? 'FALHA: o navegador do Playwright não foi baixado. Rode: npx playwright install chromium'
    : `FALHA na prévia: ${msg}`);
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
}
