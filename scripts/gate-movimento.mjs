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
 *  5. (3.5.6, A28) CONTEÚDO INVISÍVEL SEM O SCRIPT. Duas provas, em desktop e celular: `script bloqueado` (os `.js` da própria
 *     página abortados e o script principal em linha removido) e `script que demora 7 s` (o principal em linha só roda 7 s
 *     depois e o externo demora 7 s). Em ambas, passado 6 s e rolando até o fim, nenhum elemento com texto ou imagem pode
 *     ficar com opacidade 0, `visibility: hidden` ou recortado por `clip`. Ficam de pé só os scripts curtos que trocam a
 *     classe do <html> (a rede de segurança da receita-base, que devolve a página ao estado sem script).
 *     Fora da conta: `display: none`, `[hidden]`, o que é fixo (barra do celular) e o texto só para leitor de tela (1 px).
 *
 * Uso: node scripts/gate-movimento.mjs --url <url> [--espera 8000] [--so-prova-script | --sem-prova-script]
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { dividirScript, MARCAS_DO_PRINCIPAL } = require('./rede-de-seguranca.cjs');
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
// `--engasgo N`: a thread principal da página trava N ms a cada ~120 ms (máquina que engasga: o aviso do observador e o evento da
// transição chegam atrasados). A CPU reduzida sozinha não reproduziu o defeito do CI do macOS; o engasgo reproduz o atraso.
const ENGASGO = Number(valor('--engasgo', '0'));
const SEM_PROVA_SCRIPT = args.includes('--sem-prova-script') || SO_CELULAR;
const SO_PROVA_SCRIPT = args.includes('--so-prova-script');
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
      alvo: el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''),
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

/** O script principal em linha: tudo que não é o script curto que só troca a classe do <html> (a rede de segurança). */
function ehScriptPrincipal(codigo) {
  return codigo.length > 600 || MARCAS_DO_PRINCIPAL.test(codigo);
}

/** Troca o HTML para simular o script principal falhando (modo 'bloqueado') ou chegando só 7 s depois (modo 'demora').
 *  3.5.8 (N13): se a rede de segurança divide o MESMO <script> com o principal (a medida do --vh, por exemplo), a rede fica de pé
 *  e só o resto é removido ou atrasado. Sem rede no script, vale a regra de antes. */
function reescrever(html, modo) {
  return html.replace(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi, (todo, attrs, codigo) => {
    if (/\bsrc\s*=/.test(attrs)) return modo === 'bloqueado' ? '' : todo;   // externo: abortado/atrasado pela rota
    if (!codigo.trim()) return todo;
    const { rede, principal } = dividirScript(codigo);
    if (rede) {
      if (!principal.trim() || !ehScriptPrincipal(principal)) return todo;
      const resto = modo === 'bloqueado' ? '' : `<script>setTimeout(function(){${principal}\n},7000)</script>`;
      return `<script${attrs}>${rede}</script>${resto}`;
    }
    if (!ehScriptPrincipal(codigo)) return todo;                                // a rede de segurança fica de pé
    return modo === 'bloqueado' ? '' : `<script${attrs}>setTimeout(function(){${codigo}\n},7000)</script>`;
  });
}

/** Elementos com texto ou imagem que a pessoa não consegue ver (opacidade 0, hidden, clip), com o caminho curto de cada um. */
async function invisiveis(page) {
  return page.evaluate(async () => {
    const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
    for (let y = 0; y <= document.documentElement.scrollHeight; y += Math.round(window.innerHeight * 0.8)) { window.scrollTo(0, y); await dorme(60); }
    window.scrollTo(0, document.documentElement.scrollHeight);
    await dorme(300);
    const caminho = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
    const achados = [];
    for (const el of document.querySelectorAll('body *')) {
      if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'SVG', 'PATH'].includes(el.tagName.toUpperCase()) || el.closest('svg, [hidden], noscript, template, [aria-hidden="true"]')) continue;
      const temTexto = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 1);
      const ehMidia = ['IMG', 'VIDEO', 'PICTURE'].includes(el.tagName);
      if (!temTexto && !ehMidia) continue;
      const cs = getComputedStyle(el);
      if (cs.display === 'none') continue;
      let fixo = false, op = 1, oculto = false;
      for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
        const c = getComputedStyle(n);
        if (c.display === 'none') { oculto = true; break; }
        if (c.position === 'fixed') fixo = true;
        op *= parseFloat(c.opacity);
        if (n.tagName === 'DETAILS' && !n.open && el.tagName !== 'SUMMARY' && !el.closest('summary')) { oculto = true; break; }
      }
      if (oculto || fixo) continue;
      const r = el.getBoundingClientRect();
      if (r.width <= 1 && r.height <= 1) continue;               // texto só para leitor de tela
      const clip = /rect\(\s*0(px)?[ ,]+0(px)?[ ,]+0(px)?[ ,]+0(px)?\s*\)/.test(cs.clip || '') || /inset\((50|100)%\)/.test(cs.clipPath || '');
      let porque = null;
      if (op < 0.05) porque = 'opacidade 0';
      else if (cs.visibility === 'hidden') porque = 'visibility: hidden';
      else if (clip) porque = 'recortado por clip';
      if (porque) achados.push(`${caminho(el)} (${porque}) "${(el.innerText || el.getAttribute('alt') || '').trim().slice(0, 24)}"`);
    }
    return achados;
  });
}

async function provaScript(nome, w, h, mob, modo) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  const origem = new URL(URL_ALVO).origin;
  await ctx.route('**/*', async (rota) => {
    const rq = rota.request();
    if (rq.resourceType() === 'document' && rq.url().split('#')[0] === URL_ALVO.split('#')[0]) {
      const r = await rota.fetch();
      return rota.fulfill({ response: r, body: reescrever(await r.text(), modo) });
    }
    if (rq.resourceType() === 'script' && rq.url().startsWith(origem)) {
      if (modo === 'bloqueado') return rota.abort('failed');
      await new Promise((ok) => setTimeout(ok, 7000));
      return rota.continue();
    }
    return rota.continue();
  });
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); } catch { /* segue: medimos o que carregou */ }
  await page.waitForTimeout(6000);   // a rede de segurança dispara aos 5 s; o script atrasado só chega aos 7 s
  const lista = await invisiveis(page);
  const rotulo = modo === 'bloqueado' ? 'script bloqueado' : 'script que demora 7 s';
  console.log(`${(nome + ' (' + w + 'x' + h + ')').padEnd(30)} ${lista.length ? 'FALHA' : 'ok'}  ${rotulo}: ${lista.length} elemento(s) com texto ou imagem invisível(is)`);
  if (lista.length) falhas.push(`${nome} (${w}x${h}): ${rotulo}: ${lista.length} elemento(s) com texto ou imagem invisível(is) sem o script (${lista.slice(0, 4).join('; ')}${lista.length > 4 ? '; ...' : ''}). Falta a rede de segurança: classe \`js\` posta por script em linha no <head> e retirada por temporizador se o script principal não confirmar (references/receitas-de-movimento.md)`);
  await ctx.close();
}

console.log('\nGATE DE MOVIMENTO NA VISITA  ' + URL_ALVO);
console.log(`visita: ${ESPERA / 1000} s parada no topo, depois rolagem em passos de 40% da tela`);
console.log('='.repeat(88));

if (!SEM_PROVA_SCRIPT) {
  console.log('conteúdo sem o script (6 s de espera por prova):');
  for (const [nome, w, h, mob] of TELAS) for (const modo of ['bloqueado', 'demora']) await provaScript(nome, w, h, mob, modo);
}

for (const [nome, w, h, mob] of (SO_PROVA_SCRIPT ? [] : TELAS)) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  await ctx.addInitScript(escuta);
  if (ENGASGO > 0) await ctx.addInitScript(`setInterval(function(){var f=performance.now()+${ENGASGO};while(performance.now()<f){}},120)`);
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
    const s = fora.get(e.secao) || { n: 0, t: e.t, sy: e.sy, ex: `${e.tipo} ${e.prop} em ${e.alvo}` };
    s.n++; fora.set(e.secao, s);
  }
  const abaixo = secoes.filter((s) => s.abaixo && s.alta);
  const chegaram = new Set(eventos.filter((e) => !e.fora && e.t > t8 && e.secao >= 0).map((e) => e.secao));
  const animam = abaixo.filter((s) => chegaram.has(s.i));
  const minimo = Math.min(MINIMO_SECOES, abaixo.length);
  const lista = [];
  for (const [i, s] of fora) {
    const sec = secoes[i] || { nome: `seção ${i}` };
    lista.push(`seção "${sec.nome}": ${s.n} animação(ões) rodaram com a seção fora da tela (aos ${(s.t / 1000).toFixed(1)} s, scrollY ${s.sy}; a primeira: ${s.ex}): a visita chega nela já revelada e parada`);
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
for (const [nome, w, h, mob] of ((SO_CELULAR || SO_PROVA_SCRIPT) ? [] : TELAS_ITEM)) {
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
