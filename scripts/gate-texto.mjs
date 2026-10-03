#!/usr/bin/env node
/**
 * GATE DE TEXTO NA TELA: viúva em título, minúscula no começo de item e itálico colorido repetido.
 *
 * Por que existe (02/10/2026, auditoria da página do estúdio, nota 5,5). Três coisas que o dono
 * já tinha cobrado passaram por todos os gates porque nenhum media texto RENDERIZADO:
 *  - palavra sozinha na última linha de h1 e h2 ("Como marcar a sua aula / experimental"),
 *    que já tinha sido achado ALTO dele em outra página;
 *  - descrição começando com minúscula ("até 4 pessoas por turma", "só você e a profissional");
 *  - a fórmula "serifa + uma palavra em itálico colorida" em 3 de 7 títulos, o tell do
 *    "jornal de filetes".
 * Quebra de linha só existe no navegador, na largura real: por isso é Playwright, em 6 telas.
 *
 * Reprova (exit 1):
 *  1. título (h1, h2, h3, h4, dt, summary ou [data-titulo]) com mais de uma linha cuja última
 *     linha tem UMA palavra só, em 7 telas de 320 a 1440 (a 320 entrou na auditoria da v4).
 *  2. item de texto visível (bloco com texto próprio: p, li, dd, dt, td, legenda, botão, rótulo)
 *     que começa com letra minúscula. Exceção declarada: `data-minuscula-ok` (marca que se
 *     escreve assim, por exemplo).
 *  3. mais de uma palavra ou trecho em itálico com cor diferente do texto em volta, na página.
 * Avisa (não reprova): 10 ou mais filetes de 1 px (uma borda só), sinal do "jornal de filetes".
 *
 * Uso: node scripts/gate-texto.mjs --url <url>
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import path from 'node:path';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(execSync('npm root -g', { encoding: 'utf8' }).trim(), 'playwright')); }
    catch { console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}
const { chromium } = carregarPlaywright();

const args = process.argv.slice(2);
const URL_ALVO = args[args.indexOf('--url') + 1];
if (!URL_ALVO || URL_ALVO.startsWith('--')) {
  console.error('uso: node gate-texto.mjs --url <url>');
  process.exit(2);
}
const TELAS = [
  ['desktop comum', 1440, 900, false],
  ['notebook comum', 1366, 768, false],
  ['tablet retrato', 768, 1024, false],
  ['iphone pro max', 430, 932, true],
  ['iphone padrao', 390, 844, true],
  ['android comum', 360, 740, true],
  // Auditoria da v4: em 320 o h2 do fecho ficou "Marque / a sua aula / experimental" e o gate,
  // que parava em 360, dava PASSA.
  ['menor suportado', 320, 568, true],
];

const navegador = await chromium.launch();
const falhas = [];
const avisos = new Set();
console.log('\nGATE DE TEXTO NA TELA  ' + URL_ALVO);
console.log('='.repeat(80));

for (const [nome, w, h, mob] of TELAS) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(400);

  const r = await page.evaluate(() => {
    const out = { viuvas: [], minusculas: [], italicos: [], filetes: 0 };
    const visivel = (el) => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      if (el.closest('[hidden], [aria-hidden="true"], script, style, noscript')) return false;
      const c = el.getBoundingClientRect();
      return c.width > 1 && c.height > 1;
    };
    const curto = (t) => t.replace(/\s+/g, ' ').trim().slice(0, 40);

    // 1. viúva em título: h1 e h2, e também os subtítulos (h3, h4) e os títulos de card (dt,
    //    summary de pergunta e o que for marcado com data-titulo). Na v4 os 3 h3 dos passos
    //    quebravam com palavra sozinha em 768 e o gate só olhava h1 e h2.
    for (const t of document.querySelectorAll('h1, h2, h3, h4, dt, summary, [data-titulo]')) {
      if (t.closest('[data-viuva-ok]')) continue;
      if (!visivel(t)) continue;
      const palavras = [];
      const andar = document.createTreeWalker(t, NodeFilter.SHOW_TEXT);
      for (let n = andar.nextNode(); n; n = andar.nextNode()) {
        const re = /\S+/g; let m;
        while ((m = re.exec(n.textContent))) {
          const rg = document.createRange();
          rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
          const rr = rg.getClientRects()[0];
          if (rr && rr.width > 0) palavras.push({ p: m[0], top: rr.top, bottom: rr.bottom });
        }
      }
      // Pedaços da mesma palavra (palavra com <em> no meio) não contam como duas.
      const linhas = [];
      for (const pw of palavras) {
        const l = linhas.find((x) => Math.abs(x.top - pw.top) < (pw.bottom - pw.top) * 0.5);
        if (l) l.n++; else linhas.push({ top: pw.top, n: 1, ult: pw.p });
        if (l) l.ult = pw.p;
      }
      linhas.sort((a, b) => a.top - b.top);
      if (linhas.length >= 2 && linhas[linhas.length - 1].n === 1) {
        out.viuvas.push(`${t.tagName.toLowerCase()} "${curto(t.innerText)}" termina com "${linhas[linhas.length - 1].ult}" sozinha (${linhas.length} linhas)`);
      }
    }

    // 2. item de texto que começa com minúscula
    const BLOCO = ['block', 'flex', 'grid', 'list-item', 'inline-block', 'inline-flex', 'table-cell', 'flow-root'];
    const CONTEINER_DE_FRASE = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'P', 'A', 'BUTTON', 'LABEL', 'SUMMARY', 'DT', 'DD', 'LI', 'FIGCAPTION', 'TD', 'TH', 'SPAN', 'STRONG', 'EM'];
    for (const el of document.querySelectorAll('body *')) {
      if (!visivel(el) || el.closest('[data-minuscula-ok]')) continue;
      const cs = getComputedStyle(el);
      if (!BLOCO.includes(cs.display)) continue;
      const proprio = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
      if (!proprio) continue;
      const txt = (el.innerText || '').trim();
      if (!txt) continue;
      const pai = el.parentElement;
      if (pai && CONTEINER_DE_FRASE.includes(pai.tagName) && !(pai.innerText || '').trim().startsWith(txt.slice(0, 12))) continue;
      const m = txt.match(/\p{L}|\p{N}/u);
      if (!m || /\p{N}/u.test(m[0])) continue;
      if (cs.textTransform === 'uppercase' || cs.textTransform === 'capitalize') continue;
      if (m[0] !== m[0].toUpperCase() && m[0] === m[0].toLowerCase()) out.minusculas.push(`<${el.tagName.toLowerCase()}> "${curto(txt)}"`);
    }

    // 3. itálico colorido
    for (const el of document.querySelectorAll('body *')) {
      if (!visivel(el)) continue;
      const cs = getComputedStyle(el);
      const pai = el.parentElement;
      if (!pai || cs.fontStyle !== 'italic' || getComputedStyle(pai).fontStyle === 'italic') continue;
      if (!(el.innerText || '').trim()) continue;
      if (cs.color !== getComputedStyle(pai).color) out.italicos.push(`"${curto(el.innerText)}" em <${pai.tagName.toLowerCase()}>`);
    }

    // aviso: filetes de 1 px
    for (const el of document.querySelectorAll('body *')) {
      if (!visivel(el)) continue;
      const cs = getComputedStyle(el);
      const lados = ['Top', 'Right', 'Bottom', 'Left'].filter((l) => cs['border' + l + 'Style'] !== 'none' && parseFloat(cs['border' + l + 'Width']) > 0 && parseFloat(cs['border' + l + 'Width']) <= 1.5);
      if (lados.length >= 1 && lados.length <= 2) out.filetes++;
    }
    return out;
  });

  const onde = `${nome} (${w}x${h})`;
  const lista = r.viuvas.map((v) => `viúva: ${v}`)
    .concat(r.minusculas.map((v) => `começa com minúscula: ${v}`))
    .concat(r.italicos.length > 1 ? [`${r.italicos.length} trechos em itálico colorido (máximo 1): ${r.italicos.slice(0, 3).join(', ')}`] : []);
  if (r.filetes >= 10) avisos.add(`${r.filetes} filetes de 1 px (${onde}): sinal do "jornal de filetes", conferir no print`);
  console.log(`${onde.padEnd(32)} ${lista.length ? 'FALHA (' + lista.length + ')' : 'ok'}`);
  for (const l of lista) falhas.push(`${onde}: ${l}`);
  await ctx.close();
}
await navegador.close();

console.log('='.repeat(80));
avisos.forEach((a) => console.log('  aviso: ' + a));
if (falhas.length) {
  falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${falhas.length} problema(s) de texto na tela.`);
  console.log('  Viúva: text-wrap: balance no título ou ajuste da copy. Minúscula: primeira letra maiúscula');
  console.log('  em todo item. Itálico colorido: no máximo um trecho na página.\n');
  process.exit(1);
}
console.log(`  PASSA: ${TELAS.length} telas (320 a 1440), sem viúva em título nem subtítulo, sem item em minúscula, itálico contido.\n`);
