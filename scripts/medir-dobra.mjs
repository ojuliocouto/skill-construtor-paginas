#!/usr/bin/env node
/**
 * Mede, no navegador, o que a primeira tela mostra de imagem: usado pelo gate-imagens.py com --url.
 *
 * Em desktop 1440x900 e celular 390x844 (Playwright com isMobile), depois de carregar e esperar as
 * animações de entrada, em scrollY 0:
 *   foto:     área (px²) das <img> visíveis dentro da primeira tela;
 *   desenho:  área dos <svg> de topo com 40 px ou mais, fora de botão, link e rótulo, e sem
 *             `data-ilustracao-ok` (acento declarado pelo plano);
 *   aviso:    há um elemento com o texto "imagem ilustrativa" (ou "imagens ilustrativas") inteiro dentro da primeira tela
 *   avisoNaPagina: o texto existe, visível, em algum lugar da página (separa "fora da tela" de "não achei")
 *             (topo >= 0 e base <= altura da janela).
 *   manchete, apoio, botao: [topo, base] em px do h1, do texto de apoio e do botão principal do herói (G22, 3.5.10; mesma
 *             definição do gate-responsivo, em topo-da-pagina.mjs); null quando não há
 *   legenda:  a primeira legenda "imagem ilustrativa" da primeira tela: { fonte (px), altura (px), sobreFoto (posição absoluta
 *             ou fixa, por cima da foto), entreFotoEManchete (no fluxo, entre a base da foto e o topo do h1) }; null sem legenda
 *             na primeira tela. A v7 antiga tinha uma legenda de 14 px e 45 px de altura no fluxo, entre a foto e a manchete,
 *             e nada media isso.
 * Imprime um JSON {desk:{foto,desenho,aviso,vw,vh,manchete,apoio,botao,legenda}, mob:{...}} e nada mais.
 *
 * Uso: node scripts/medir-dobra.mjs --url <url>
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import path from 'node:path';
import { DETECTAR_TOPO } from './topo-da-pagina.mjs';

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
  await page.evaluate(DETECTAR_TOPO);
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
    // singular ou plural ("Imagem ilustrativa", "Imagens ilustrativas"): 3.5.8, achado N9
    const AVISO = /imag(?:em|ens)\s+ilustrativas?/i;
    const achados = [...document.querySelectorAll('body *')].filter((el) => {
      if (!AVISO.test(el.textContent || '') || !visivel(el)) return false;
      return ![...el.children].some((f) => AVISO.test(f.textContent || ''));
    });
    const aviso = achados.some((el) => {
      const rg = document.createRange(); rg.selectNodeContents(el);
      const c = rg.getBoundingClientRect();
      return c.height > 0 && c.top >= 0 && c.bottom <= vh;
    });
    // Topo (G22): onde terminam manchete, apoio e botão, e onde está a legenda da foto.
    const t = window.__topo();
    const faixa = (q) => (q ? [Math.round(q.top), Math.round(q.bottom)] : null);
    const manchete = faixa(t.h1 && t.linhas(t.h1));
    const apoio = faixa(t.apoio && t.linhas(t.apoio));
    const botao = faixa(t.botao && t.botao.getBoundingClientRect());
    let legenda = null;
    const naPrimeira = achados.find((el) => { const c = el.getBoundingClientRect(); return c.top < vh && c.bottom > 0; });
    if (naPrimeira) {
      let sobreFoto = false;
      for (let n = naPrimeira; n && n !== document.body; n = n.parentElement) {
        const pos = getComputedStyle(n).position;
        if (pos === 'absolute' || pos === 'fixed') { sobreFoto = true; break; }
        if (n.tagName === 'FIGURE' || n === t.heroi) break;
      }
      const c = naPrimeira.getBoundingClientRect();
      // Foto que começa acima da legenda (a base da foto não serve: paralaxe passa da moldura e o painel de texto pode cobrir a
      // parte de baixo da foto, como na v7 antiga, em que a legenda em 440 px ficava sobre a caixa da foto, que ia até 468).
      const fotoAcima = [...document.querySelectorAll('img, video')].some((f) => { const q = f.getBoundingClientRect(); return q.height >= 40 && q.top < c.top && q.bottom > 0; });
      const topoH1 = manchete ? manchete[0] : null;
      legenda = {
        fonte: Math.round(parseFloat(getComputedStyle(naPrimeira).fontSize)),
        altura: Math.round(c.height + parseFloat(getComputedStyle(naPrimeira).marginTop) + parseFloat(getComputedStyle(naPrimeira).marginBottom)),
        sobreFoto,
        entreFotoEManchete: !sobreFoto && fotoAcima && topoH1 !== null && c.bottom <= topoH1 + 1,
      };
    }
    return { foto: Math.round(foto), desenho: Math.round(desenho), aviso, avisoNaPagina: achados.length > 0, vw, vh, manchete, apoio, botao, legenda };
  });
  await ctx.close();
}
await navegador.close();
console.log(JSON.stringify(saida));
