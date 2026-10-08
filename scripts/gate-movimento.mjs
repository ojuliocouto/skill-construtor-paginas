#!/usr/bin/env node
/**
 * GATE DE MOVIMENTO NA VISITA: a animação acontece quando a pessoa chega na seção, não no print.
 *
 * Por que existe (02/10/2026, auditoria da v4 do estúdio, nota 6,5). As regras 15, 19 e 20 do
 * dono pedem caixas que entram escalonadas, FAQ e fecho animados. A v4 tinha tudo isso no CSS e
 * um `setTimeout(..., 3000)` que marcava todas as seções como visíveis 3 s depois da carga, com
 * a página parada no topo. Medido pelo auditor: aos 3,3 s, com scrollY 0, 8 de 8 grupos já
 * estavam revelados; numa visita que lê o topo por 8 s e só depois rola, as 6 seções chegavam
 * com opacidade 1,00 e 0 traços desenhando. Print de página inteira não vê isso: no print tudo
 * aparece pronto, que é justamente o defeito.
 *
 * Como mede: simula uma visita de verdade. Carrega a página, fica parada no topo por 8 s
 * (`--espera`), e só então rola em passos de 40% da tela, com pausa de leitura. Escuta
 * `transitionrun` e `animationstart` (animação infinita, como pulso, não conta) e anota, para
 * cada uma, se a seção do elemento estava na tela naquele instante.
 *
 * Reprova (exit 1):
 *  1. animação ou transição que rodou com a seção inteira FORA da tela (revelada antes de a
 *     pessoa chegar, por temporizador, por observador com margem enorme ou por classe na carga);
 *  2. menos de 2 seções abaixo da primeira dobra que animam ao chegar (página parada).
 *  3. (auditoria da v5, 03/10/2026) ITEM que termina de animar ANTES de entrar na tela, numa
 *     rolagem contínua a 300 px/s (leitura rápida) em 1440, 390 e 320. A v5 revelava por grupo:
 *     no celular a 3a situação, o 3o passo e duas perguntas chegavam à tela já paradas. Cada
 *     caixa, passo e pergunta revela quando ELE entra na tela (observar o filho, não o grupo);
 *  4. (auditoria da v5) rolagem suave (scroll-behavior: smooth) ligada para quem pediu
 *     movimento reduzido: os botões de âncora rolavam animados.
 * Fica de fora o que é fixo na tela (cabeçalho, barra do celular) e o cabeçalho.
 *
 * Uso: node scripts/gate-movimento.mjs --url <url> [--espera 8000]
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
const valor = (nome, padrao) => { const i = args.indexOf(nome); return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : padrao; };
const URL_ALVO = valor('--url');
const ESPERA = Number(valor('--espera', '8000'));
const MINIMO_SECOES = 2;
// Ferramentas de prova (segunda leva da 3.5.6): `--cpu 4` reduz a CPU 4x pelo CDP (máquina lenta do CI) e `--so-celular`
// roda só a visita do celular, para repetir o gate muitas vezes sem pagar o resto.
const CPU = Number(valor('--cpu', '1'));
const SO_CELULAR = args.includes('--so-celular');
if (!URL_ALVO) {
  console.error('uso: node gate-movimento.mjs --url <url> [--espera 8000]');
  process.exit(2);
}
const TELAS = [
  ['desktop comum', 1440, 900, false],
  ['iphone padrao', 390, 844, true],
].filter(([nome]) => !SO_CELULAR || nome === 'iphone padrao');

/** Instalado antes de qualquer script da página: registra cada animação com a posição da seção. */
function escuta() {
  window.__mov = [];
  const secoes = () => [...document.querySelectorAll('section, footer')];
  const registrar = (ev) => {
    const el = ev.target;
    if (!(el instanceof Element)) return;
    const cs = getComputedStyle(el);
    if (ev.type === 'animationstart') {
      const nomes = cs.animationName.split(',').map((s) => s.trim());
      const voltas = cs.animationIterationCount.split(',').map((s) => s.trim());
      const i = Math.max(0, nomes.indexOf(ev.animationName));
      if ((voltas[i] || voltas[0]) === 'infinite') return;
    }
    let fixo = false;
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
      const p = getComputedStyle(n).position;
      if (p === 'fixed' || p === 'sticky' || n.tagName === 'HEADER' || n.tagName === 'NAV') { fixo = true; break; }
    }
    if (fixo) return;
    const sec = el.closest('section, footer');
    const alvo = sec || el;
    const r = alvo.getBoundingClientRect();
    window.__mov.push({
      t: performance.now(), tipo: ev.type, prop: ev.propertyName || ev.animationName,
      secao: sec ? secoes().indexOf(sec) : -1,
      fora: r.bottom <= 0 || r.top >= window.innerHeight,
      sy: Math.round(window.scrollY),
    });
  };
  document.addEventListener('transitionrun', registrar, true);
  document.addEventListener('animationstart', registrar, true);
}

/** Rolagem contínua: anota, para cada elemento que anima, quando terminou e quando entrou na tela. */
function escutaItens() {
  window.__itens = new Map();
  const fixo = (el) => {
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
      const p = getComputedStyle(n).position;
      if (p === 'fixed' || p === 'sticky' || n.tagName === 'HEADER' || n.tagName === 'NAV') return true;
    }
    return false;
  };
  const anota = (ev) => {
    const el = ev.target;
    if (!(el instanceof Element) || fixo(el)) return;
    if (ev.type.startsWith('animation')) {
      const cs = getComputedStyle(el);
      if (cs.animationIterationCount.split(',').some((v) => v.trim() === 'infinite')) return;
    }
    const r = window.__itens.get(el) || { inicio: null, fim: null, entrou: null };
    if (ev.type === 'transitionrun' || ev.type === 'animationstart') r.inicio = r.inicio ?? performance.now();
    else r.fim = Math.max(r.fim || 0, performance.now());
    window.__itens.set(el, r);
  };
  for (const t of ['transitionrun', 'animationstart', 'transitionend', 'animationend']) document.addEventListener(t, anota, true);
  const olhar = () => {
    for (const [el, r] of window.__itens) {
      if (r.entrou !== null || !el.isConnected) continue;
      const c = el.getBoundingClientRect();
      if (c.width > 0 && c.height > 0 && c.top < window.innerHeight && c.bottom > 0) r.entrou = performance.now();
    }
    requestAnimationFrame(olhar);
  };
  requestAnimationFrame(olhar);
}

const VELOCIDADE = 300; // px/s
const TELAS_ITEM = [
  ['desktop comum', 1440, 900, false],
  ['iphone padrao', 390, 844, true],
  ['menor suportado', 320, 568, true],
];

const navegador = await chromium.launch();
const falhas = [];
console.log('\nGATE DE MOVIMENTO NA VISITA  ' + URL_ALVO);
console.log(`visita: ${ESPERA / 1000} s parada no topo, depois rolagem em passos de 40% da tela`);
console.log('='.repeat(88));

for (const [nome, w, h, mob] of TELAS) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  await ctx.addInitScript(escuta);
  const page = await ctx.newPage();
  if (CPU > 1) await (await ctx.newCDPSession(page)).send('Emulation.setCPUThrottlingRate', { rate: CPU });
  try { await page.goto(URL_ALVO, { waitUntil: 'load', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  const secoes = await page.evaluate(() => [...document.querySelectorAll('section, footer')].map((s, i) => {
    const r = s.getBoundingClientRect();
    const t = s.querySelector('h1, h2, h3');
    return { i, abaixo: r.top + window.scrollY >= window.innerHeight, alta: r.height > 40 && getComputedStyle(s).display !== 'none',
      nome: ((t && t.innerText) || s.id || s.tagName).replace(/\s+/g, ' ').trim().slice(0, 40) };
  }));
  await page.waitForTimeout(ESPERA);
  const t8 = await page.evaluate(() => performance.now());
  const altura = await page.evaluate(() => document.documentElement.scrollHeight);
  const passo = Math.round(h * 0.4);
  for (let y = passo; y <= altura; y += passo) {
    await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);
    await page.waitForTimeout(450);
  }
  await page.waitForTimeout(1500);
  const eventos = await page.evaluate(() => window.__mov);

  const onde = `${nome} (${w}x${h})`;
  const fora = new Map();
  for (const e of eventos) {
    if (!e.fora || e.secao < 0) continue;
    const s = fora.get(e.secao) || { n: 0, t: e.t, sy: e.sy };
    s.n++; fora.set(e.secao, s);
  }
  const abaixo = secoes.filter((s) => s.abaixo && s.alta);
  const chegaram = new Set(eventos.filter((e) => !e.fora && e.t > t8 && e.secao >= 0).map((e) => e.secao));
  const animam = abaixo.filter((s) => chegaram.has(s.i));
  const minimo = Math.min(MINIMO_SECOES, abaixo.length);
  const lista = [];
  for (const [i, s] of fora) {
    const sec = secoes[i] || { nome: `seção ${i}` };
    lista.push(`seção "${sec.nome}": ${s.n} animação(ões) rodaram com a seção fora da tela (aos ${(s.t / 1000).toFixed(1)} s, scrollY ${s.sy}): a visita chega nela já revelada e parada`);
  }
  if (animam.length < minimo) {
    lista.push(`só ${animam.length} de ${abaixo.length} seções abaixo da dobra animam ao chegar (mínimo ${minimo}): ${abaixo.filter((s) => !chegaram.has(s.i)).map((s) => `"${s.nome}"`).slice(0, 6).join(', ')} chegam paradas`);
  }
  console.log(`${onde.padEnd(30)} ${lista.length ? 'FALHA (' + lista.length + ')' : 'ok'}  ${animam.length}/${abaixo.length} seções animam ao chegar, ${fora.size} com animação fora da tela`);
  for (const l of lista) falhas.push(`${onde}: ${l}`);
  await ctx.close();
}
// 3. Item por item, numa rolagem contínua a 300 px/s.
console.log(`por item: rolagem contínua a ${VELOCIDADE} px/s`);
for (const [nome, w, h, mob] of (SO_CELULAR ? [] : TELAS_ITEM)) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  await ctx.addInitScript(escutaItens);
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'load', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  await page.waitForTimeout(1000);
  await page.evaluate((v) => new Promise((ok) => {
    const passo = v / 20;
    const t = setInterval(() => {
      const antes = window.scrollY;
      window.scrollTo({ top: antes + passo, behavior: 'instant' });
      if (window.scrollY === antes || window.scrollY + window.innerHeight >= document.documentElement.scrollHeight) { clearInterval(t); ok(); }
    }, 50);
  }), VELOCIDADE);
  await page.waitForTimeout(1500);
  const parados = await page.evaluate(() => {
    const rotulo = (el) => {
      const item = el.closest('li, article, details, figure, section') || el;
      const t = (item.innerText || item.getAttribute('aria-label') || el.tagName).replace(/\s+/g, ' ').trim();
      return t.slice(0, 40) || el.tagName.toLowerCase();
    };
    const porItem = new Map();
    for (const [el, r] of window.__itens) {
      if (r.fim === null || r.entrou === null || r.fim >= r.entrou - 30) continue;
      const k = rotulo(el);
      porItem.set(k, Math.max(porItem.get(k) || 0, Math.round(r.entrou - r.fim)));
    }
    return [...porItem.entries()];
  });
  const onde = `${nome} (${w}x${h})`;
  console.log(`${onde.padEnd(30)} ${parados.length ? 'FALHA' : 'ok'}  ${parados.length} item(ns) chegam parados`);
  if (parados.length) {
    falhas.push(`${onde}: ${parados.length} item(ns) chegam parados na tela a ${VELOCIDADE} px/s (terminaram de animar antes de entrar): ${parados.slice(0, 5).map(([k, ms]) => `"${k}" ${ms} ms antes`).join(', ')}; revele cada item quando ele entra, não o grupo`);
  }
  await ctx.close();
}

// 4. Movimento reduzido: nada de rolagem suave.
{
  const ctx = await navegador.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'load', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  const suave = await page.evaluate(() => [document.documentElement, document.body].filter((el) => getComputedStyle(el).scrollBehavior === 'smooth').map((el) => el.tagName.toLowerCase()));
  console.log(`movimento reduzido: scroll-behavior ${suave.length ? 'smooth em ' + suave.join(', ') : 'auto'}`);
  if (suave.length) falhas.push(`movimento reduzido: scroll-behavior: smooth em ${suave.join(' e ')} com prefers-reduced-motion: reduce; os botões de âncora rolam animados para quem pediu menos movimento (use auto dentro de @media (prefers-reduced-motion: reduce))`);
  await ctx.close();
}
await navegador.close();

console.log('='.repeat(88));
if (falhas.length) {
  falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${falhas.length} problema(s) de movimento na visita.`);
  console.log('  Revele só o que entra na tela (IntersectionObserver sem temporizador que revela tudo).');
  console.log('  Conteúdo continua visível sem JavaScript e com movimento reduzido.\n');
  process.exit(1);
}
console.log(`  PASSA: ${TELAS.length} telas, nenhuma animação fora da tela e seções animando ao chegar; nenhum item chega parado a ${VELOCIDADE} px/s; rolagem sem animação com movimento reduzido.\n`);
