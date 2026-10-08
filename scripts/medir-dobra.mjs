#!/usr/bin/env node
/**
 * Mede, no navegador, o que a primeira tela mostra de imagem: usado pelo gate-imagens.py com --url.
 *
 * Em desktop 1440x900 e celular 390x844 (Playwright com isMobile), depois de carregar e esperar as
 * animações de entrada, em scrollY 0:
 *   foto:     área (px²) das <img> visíveis dentro da primeira tela;
 *   desenho:  área dos <svg> de topo com 40 px ou mais, fora de botão, link e rótulo, e sem
 *             `data-ilustracao-ok` (acento declarado pelo plano);
 *   aviso:    há um elemento com o texto "imagem ilustrativa" inteiro dentro da primeira tela
 *             (topo >= 0 e base <= altura da janela).
 * Imprime um JSON {desk:{foto,desenho,aviso,vw,vh}, mob:{...}} e nada mais.
 *
 * Uso: node scripts/medir-dobra.mjs --url <url>
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import path from 'node:path';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(raizGlobalNpm(), 'playwright')); }
    catch { console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}
const { chromium } = carregarPlaywright();
const args = process.argv.slice(2);
const URL_ALVO = args[args.indexOf('--url') + 1];
if (!URL_ALVO || URL_ALVO.startsWith('--')) { console.error('uso: node medir-dobra.mjs --url <url>'); process.exit(2); }

const navegador = await chromium.launch();
const saida = {};
for (const [tag, w, h, movel] of [['desk', 1440, 900, false], ['mob', 390, 844, true]]) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: movel, hasTouch: movel });
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(2600);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.waitForTimeout(300);
  saida[tag] = await page.evaluate(() => {
    const vw = window.innerWidth, vh = window.innerHeight;
    const visivel = (el) => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      const c = el.getBoundingClientRect();
      return c.width > 1 && c.height > 1;
    };
    const naTela = (c) => Math.max(0, Math.min(c.right, vw) - Math.max(c.left, 0)) * Math.max(0, Math.min(c.bottom, vh) - Math.max(c.top, 0));
    let foto = 0, desenho = 0;
    for (const img of document.querySelectorAll('img')) {
      const c = img.getBoundingClientRect();
      if (!visivel(img) || Math.min(c.width, c.height) < 40) continue;
      foto += naTela(c);
    }
    for (const svg of document.querySelectorAll('svg')) {
      if (svg.parentElement && svg.parentElement.closest('svg')) continue;
      if (svg.closest('a, button, summary, label, [data-ilustracao-ok]') || svg.hasAttribute('data-ilustracao-ok')) continue;
      const c = svg.getBoundingClientRect();
      if (!visivel(svg) || Math.min(c.width, c.height) < 40) continue;
      desenho += naTela(c);
    }
    const achados = [...document.querySelectorAll('body *')].filter((el) => {
      if (!/imagem ilustrativa/i.test(el.textContent || '') || !visivel(el)) return false;
      return ![...el.children].some((f) => /imagem ilustrativa/i.test(f.textContent || ''));
    });
    const aviso = achados.some((el) => {
      const rg = document.createRange(); rg.selectNodeContents(el);
      const c = rg.getBoundingClientRect();
      return c.height > 0 && c.top >= 0 && c.bottom <= vh;
    });
    return { foto: Math.round(foto), desenho: Math.round(desenho), aviso, vw, vh };
  });
  await ctx.close();
}
await navegador.close();
console.log(JSON.stringify(saida));
