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
 *  4b. (3.5.9, N26) QUALQUER animação ou transição em curso com `prefers-reduced-motion: reduce`. A página é carregada e rolada
 *     inteira em 390 e 1440 com `reducedMotion: 'reduce'`, e um laço de quadros anota o que `document.getAnimations()` devolve
 *     em curso com duração acima de 0,2 s (ou infinita, ou presa à rolagem). A mensagem nomeia o elemento e a propriedade.
 *     Duas auditorias acharam animação rodando com movimento reduzido e este gate passou verde, porque só olhava o scroll-behavior.
 * Fica de fora o que é fixo na tela (cabeçalho, barra do celular) e o cabeçalho.
 *
 *  5. (3.5.6, A28) CONTEÚDO INVISÍVEL SEM O SCRIPT. Duas provas, em desktop e celular: `script bloqueado` (os `.js` da própria
 *     página abortados e o script principal em linha removido) e `script que demora 7 s` (o principal em linha só roda 7 s
 *     depois e o externo demora 7 s). Em ambas, passado 6 s e rolando até o fim, nenhum elemento com texto ou imagem pode
 *     ficar com opacidade 0, `visibility: hidden` ou recortado por `clip`. Ficam de pé só os scripts curtos que trocam a
 *     classe do <html> (a rede de segurança da receita-base, que devolve a página ao estado sem script).
 *     Fora da conta: `display: none`, `[hidden]`, o que é fixo (barra do celular) e o texto só para leitor de tela (1 px).
 *
 *  6. (3.5.10, P12, P13b, P14) TEXTO QUE FICA INVISÍVEL COM O SCRIPT RODANDO, em 1440 e 390. Três provas:
 *     - parada no topo: a página carrega e fica PARADA_MS parada; nenhum texto da primeira tela pode estar invisível (a Torra
 *       Clara tinha os fatos do herói com translateY(26px) abaixo da linha do rootMargin -6%, e com a página parada eles nunca
 *       apareciam em 1440);
 *     - fim da visita: depois da visita inteira, nenhum texto da página pode continuar invisível (o rótulo da oferta tinha o
 *       clip-path de entrada no próprio alvo do IntersectionObserver: com threshold 0,18 a razão do alvo todo recortado é 0, o
 *       observador nunca dispara e as linhas nunca aparecem);
 *     - salto: a página pula do topo direto para o fim (âncora, painel, voltar do WhatsApp); o que ficou acima da tela tem de
 *       estar no estado final ("já passou = estado final").
 *     Invisível = opacidade efetiva abaixo de 0,05 (somando os pais), visibility: hidden ou recortado por inteiro por clip ou
 *     clip-path no próprio elemento ou num pai (a mensagem diz em quem).
 *
 * Uso: node scripts/gate-movimento.mjs --url <url> [--espera 8000] [--so-prova-script | --sem-prova-script | --so-visibilidade]
 *   --so-visibilidade: só a visita e as três provas do item 6 (sem a prova do script, sem o item a item e sem o movimento reduzido)
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import path from 'node:path';
import { exigirServidor } from './servidor-no-ar.mjs';

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
const SO_VISIBILIDADE = args.includes('--so-visibilidade');
const SEM_PROVA_SCRIPT = args.includes('--sem-prova-script') || SO_CELULAR || SO_VISIBILIDADE;
// 3.5.10 (P13b): quanto tempo a página fica parada no topo antes de medir a primeira tela.
const PARADA_MS = 4000;
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
    let atraso = 0;
    if (ev.type === 'animationstart') {
      const nomes = cs.animationName.split(',').map((s) => s.trim());
      const voltas = cs.animationIterationCount.split(',').map((s) => s.trim());
      const i = Math.max(0, nomes.indexOf(ev.animationName));
      if ((voltas[i] || voltas[0]) === 'infinite') return;
      // `animationstart` só sai no FIM do animation-delay: guarda o atraso para a mensagem dizer isso (3.5.8, N16)
      const ds = cs.animationDelay.split(',').map((x) => x.trim());
      const d = ds[i] || ds[0] || '0s';
      atraso = d.endsWith('ms') ? parseFloat(d) / 1000 : parseFloat(d) || 0;
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
      atraso,
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

await exigirServidor(URL_ALVO);   // servidor caído: uma mensagem clara (saída 3), não ERR_CONNECTION_REFUSED (P11)
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

/** 3.5.10: elementos com texto ou imagem que a pessoa não consegue ver AGORA, sem rolar. `onde`: 'todos', 'primeira' (pelo menos
 *  24 px ou metade da altura dentro da janela), 'acima' (acima da janela), 'fim' (a página toda, menos o que está fora da largura
 *  da janela, como cartão de carrossel não rolado), 'contar' (conta, por elemento, as paradas da visita em
 *  que ele estava na janela e invisível; devolve nada) ou 'na-tela' (os que ficaram invisíveis na janela em 2 paradas ou mais).
 *  Roda dentro da página (page.evaluate). */
function ocultosAgora(onde) {
  const caminho = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  // clip-path que recorta a caixa inteira: inset() com topo + base >= altura ou esquerda + direita >= largura, ou circle(0).
  const recorteTotal = (el, cs) => {
    if (/rect\(\s*0(px)?[ ,]+0(px)?[ ,]+0(px)?[ ,]+0(px)?\s*\)/.test(cs.clip || '')) return 'clip: rect(0 0 0 0)';
    const cp = cs.clipPath || 'none';
    if (cp === 'none') return null;
    if (/circle\(\s*0(px|%)?[\s)]/.test(cp)) return 'clip-path: ' + cp;
    const m = cp.match(/inset\(([^)]*)\)/);
    if (!m || /calc|var/.test(m[1])) return null;
    const v = m[1].split(/\s+round\s+/)[0].trim().split(/\s+/);
    const [t, r = t, b = t, l = r] = v;
    const c = el.getBoundingClientRect();
    const px = (x, base) => (x.endsWith('%') ? (parseFloat(x) / 100) * base : parseFloat(x));
    const T = px(t, c.height), R = px(r, c.width), B = px(b, c.height), L = px(l, c.width);
    if ([T, R, B, L].some(Number.isNaN)) return null;
    return T + B >= c.height - 0.5 || L + R >= c.width - 0.5 ? 'clip-path: ' + cp : null;
  };
  const vh = window.innerHeight;
  const achados = [];
  window.__ocultosNaTela = window.__ocultosNaTela || new Map();
  // Entrada em curso não é defeito: na contagem da visita, elemento com animação ou transição rodando (inclusive na fase de
  // atraso, como a foto da foto-que-se-monta, que espera 1,5 s as faixas montarem por cima) nele ou num pai não conta a parada.
  const animando = new Set();
  if (onde === 'contar' && document.getAnimations) for (const a of document.getAnimations()) if ((a.playState === 'running' || a.pending) && a.effect && a.effect.target) animando.add(a.effect.target);
  const emCurso = (el) => { for (let n = el; n && n !== document.documentElement; n = n.parentElement) if (animando.has(n)) return true; return false; };
  if (onde === 'na-tela') {
    for (const [el, n] of window.__ocultosNaTela) if (n.vezes >= 2) achados.push(`${n.rotulo} (${n.porque}; invisível na tela em ${n.vezes} paradas da visita)`);
    return achados;
  }
  for (const el of document.querySelectorAll('body *')) {
    if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'SVG', 'PATH'].includes(el.tagName.toUpperCase()) || el.closest('svg, [hidden], noscript, template, [aria-hidden="true"], [inert], dialog:not([open])')) continue;
    const temTexto = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 1);
    const ehMidia = ['IMG', 'VIDEO', 'PICTURE'].includes(el.tagName);
    if (!temTexto && !ehMidia) continue;
    // posição antes do estilo: nas provas com lugar (primeira tela, parada da visita, acima) só quem está nele paga o estilo dos pais
    const r = el.getBoundingClientRect();
    if (r.width <= 1 && r.height <= 1) continue;               // texto só para leitor de tela (ou display: none)
    if (onde === 'primeira' || onde === 'contar') {
      const dentro = Math.min(r.bottom, vh) - Math.max(r.top, 0);
      // também na horizontal: cartão de carrossel à direita da janela (overflow-x) não está na tela (falso positivo medido na Torra Clara)
      const dentroX = Math.min(r.right, window.innerWidth) - Math.max(r.left, 0);
      if (dentro < Math.min(24, r.height / 2) || dentroX < Math.min(24, r.width / 2)) continue;
    }
    if (onde === 'acima' && r.bottom > 0) continue;
    // fim da visita: a visita só rola na vertical; cartão de carrossel fora da largura da janela não foi visto, não se julga
    if (onde === 'fim' && (Math.min(r.right, window.innerWidth) - Math.max(r.left, 0)) < Math.min(24, r.width / 2)) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none') continue;
    let fixo = false, op = 1, oculto = false, recorte = null;
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
      const c = getComputedStyle(n);
      if (c.display === 'none') { oculto = true; break; }
      if (c.position === 'fixed') fixo = true;
      op *= parseFloat(c.opacity);
      if (!recorte) { const rc = recorteTotal(n, c); if (rc) recorte = n === el ? rc : `${rc} em ${caminho(n)}`; }
      if (n.tagName === 'DETAILS' && !n.open && el.tagName !== 'SUMMARY' && !el.closest('summary')) { oculto = true; break; }
    }
    if (oculto || fixo) continue;
    let porque = null;
    if (op < 0.05) porque = 'opacidade 0';
    else if (cs.visibility === 'hidden') porque = 'visibility: hidden';
    else if (recorte) porque = 'recortado por ' + recorte;
    const rotulo = `${caminho(el)} "${(el.innerText || el.getAttribute('alt') || '').replace(/\s+/g, ' ').trim().slice(0, 24)}"`;
    if (porque && onde === 'contar' && !emCurso(el)) {
      const n = window.__ocultosNaTela.get(el) || { vezes: 0, rotulo, porque };
      n.vezes++; n.porque = porque;
      window.__ocultosNaTela.set(el, n);
    } else if (porque) achados.push(`${rotulo} (${porque})`);
  }
  return achados;
}

/** Elementos com texto ou imagem que a pessoa não consegue ver (opacidade 0, hidden, clip), com o caminho curto de cada um. */
async function invisiveis(page) {
  await page.evaluate(async () => {
    const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
    for (let y = 0; y <= document.documentElement.scrollHeight; y += Math.round(window.innerHeight * 0.8)) { window.scrollTo(0, y); await dorme(60); }
    window.scrollTo(0, document.documentElement.scrollHeight);
    await dorme(300);
  });
  return page.evaluate(ocultosAgora, 'todos');
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
    // 6 (P12): texto na janela e invisível nesta parada; em 2 paradas seguidas ou mais (quase 1 s na tela) é defeito.
    await page.evaluate(ocultosAgora, 'contar');
  }
  await page.waitForTimeout(1500);
  const eventos = await page.evaluate(() => window.__mov);
  // 6. Durante e no fim da visita (P12): nada com texto pode ficar invisível na tela, nem continuar invisível no fim.
  const naTela = await page.evaluate(ocultosAgora, 'na-tela');
  const restam = [...new Set([...naTela, ...(await page.evaluate(ocultosAgora, 'fim'))])];

  const onde = `${nome} (${w}x${h})`;
  const fora = new Map();
  for (const e of eventos) {
    if (!e.fora || e.secao < 0) continue;
    const s = fora.get(e.secao) || { n: 0, t: e.t, sy: e.sy, ex: `${e.tipo} ${e.prop} em ${e.alvo}`, atraso: 0 };
    s.atraso = Math.max(s.atraso, e.atraso || 0);
    s.n++; fora.set(e.secao, s);
  }
  const abaixo = secoes.filter((s) => s.abaixo && s.alta);
  const chegaram = new Set(eventos.filter((e) => !e.fora && e.t > t8 && e.secao >= 0).map((e) => e.secao));
  const animam = abaixo.filter((s) => chegaram.has(s.i));
  const minimo = Math.min(MINIMO_SECOES, abaixo.length);
  const lista = [];
  for (const [i, s] of fora) {
    const sec = secoes[i] || { nome: `seção ${i}` };
    lista.push(`seção "${sec.nome}": ${s.n} animação(ões) rodaram com a seção fora da tela (aos ${(s.t / 1000).toFixed(1)} s, scrollY ${s.sy}; a primeira: ${s.ex}): a visita chega nela já revelada e parada${s.atraso > 0 ? `. A animação tem animation-delay de ${s.atraso.toFixed(1)} s: o navegador só avisa o início no fim do atraso, e a pessoa pode rolar antes. Troque o animation-delay por um quadro-chave parado no começo (0%, 30% { ... }), como manda references/receitas-de-movimento.md` : ''}`);
  }
  if (animam.length < minimo) {
    lista.push(`só ${animam.length} de ${abaixo.length} seções abaixo da dobra animam ao chegar (mínimo ${minimo}): ${abaixo.filter((s) => !chegaram.has(s.i)).map((s) => `"${s.nome}"`).slice(0, 6).join(', ')} chegam paradas`);
  }
  console.log(`${onde.padEnd(30)} ${lista.length ? 'FALHA (' + lista.length + ')' : 'ok'}  ${animam.length}/${abaixo.length} seções animam ao chegar, ${fora.size} com animação fora da tela`);
  for (const l of lista) falhas.push(`${onde}: ${l}`);
  console.log(`${onde.padEnd(30)} ${restam.length ? 'FALHA' : 'ok'}  fim da visita: ${restam.length} elemento(s) com texto ou imagem invisível(is) na tela ou no fim`);
  if (restam.length) falhas.push(`${onde}: no fim da visita, ${restam.length} elemento(s) com texto ou imagem continuam invisíveis (na tela por quase 1 s, ou depois de a página inteira passar): ${restam.slice(0, 4).join('; ')}${restam.length > 4 ? '; ...' : ''}. Se o recorte de entrada (clip-path) está no próprio alvo do IntersectionObserver, a área visível do alvo é 0 e, com threshold acima de 0, o observador nunca dispara: o clip-path de entrada vai no filho, o observador olha o pai (references/receitas-de-movimento.md)`);
  await ctx.close();
}
// 6. Parada no topo (P13b) e salto até o fim (P14), em contextos novos.
for (const [nome, w, h, mob] of (SO_PROVA_SCRIPT ? [] : TELAS)) {
  const onde = `${nome} (${w}x${h})`;
  for (const prova of ['parada', 'salto']) {
    const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
    const page = await ctx.newPage();
    try { await page.goto(URL_ALVO, { waitUntil: 'load', timeout: 45000 }); }
    catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
    if (prova === 'parada') {
      await page.waitForTimeout(PARADA_MS);
      const lista = await page.evaluate(ocultosAgora, 'primeira');
      console.log(`${onde.padEnd(30)} ${lista.length ? 'FALHA' : 'ok'}  parada no topo por ${PARADA_MS / 1000} s: ${lista.length} elemento(s) da primeira tela invisível(is)`);
      if (lista.length) falhas.push(`${onde}: parada no topo por ${PARADA_MS / 1000} s, ${lista.length} elemento(s) com texto da primeira tela continuam invisíveis: ${lista.slice(0, 4).join('; ')}${lista.length > 4 ? '; ...' : ''}. Com a página parada o observador não dispara para o que está abaixo da linha do rootMargin (ou empurrado para baixo dela por translate): o que já está na primeira tela entra na carga (references/receitas-de-movimento.md, "a primeira tela entra na carga")`);
    } else {
      await page.waitForTimeout(1000);
      // Salto direto ao fim, sem passar pelo meio: como uma âncora, um painel ou a volta do WhatsApp que restaura a rolagem.
      await page.evaluate(() => window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'instant' }));
      await page.waitForTimeout(1500);
      const lista = await page.evaluate(ocultosAgora, 'acima');
      console.log(`${onde.padEnd(30)} ${lista.length ? 'FALHA' : 'ok'}  salto até o fim: ${lista.length} elemento(s) acima da tela invisível(is)`);
      if (lista.length) falhas.push(`${onde}: depois de um salto até o fim (âncora, painel, voltar do WhatsApp), ${lista.length} elemento(s) que ficaram acima da tela continuam invisíveis: ${lista.slice(0, 4).join('; ')}${lista.length > 4 ? '; ...' : ''}. A base das receitas põe no estado final, sem animação, o que já passou ("já passou = estado final" em references/receitas-de-movimento.md)`);
    }
    await ctx.close();
  }
}

// 3. Item por item, numa rolagem contínua a 300 px/s.
console.log(`por item: rolagem contínua a ${VELOCIDADE} px/s`);
for (const [nome, w, h, mob] of ((SO_CELULAR || SO_PROVA_SCRIPT || SO_VISIBILIDADE) ? [] : TELAS_ITEM)) {
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
      // 3.5.8 (N15): o rótulo nomeia o PRÓPRIO elemento (tag.classe e o texto dele), não o texto da seção inteira
      const nome = el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
      const proprio = (el.innerText || el.getAttribute('alt') || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 40);
      return proprio ? `${nome} "${proprio}"` : nome;
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
    falhas.push(`${onde}: ${parados.length} item(ns) chegam parados na tela a ${VELOCIDADE} px/s (terminaram de animar antes de entrar): ${parados.slice(0, 5).map(([k, ms]) => `${k} ${ms} ms antes`).join(', ')}; revele cada item quando ele entra, não o grupo`);
  }
  await ctx.close();
}

// 4. Movimento reduzido: nada de rolagem suave e nada animado em curso (3.5.9, N26).
// Duas vezes o auditor achou animação rodando com prefers-reduced-motion: reduce e este gate passou verde, porque só
// olhava o scroll-behavior. Agora, com reducedMotion: 'reduce', a página é carregada e rolada inteira, e um laço de quadros
// anota toda animação ou transição em curso (document.getAnimations()) cuja duração passa do limiar. A skill diz que
// "movimento reduzido desliga tudo" e não declara número; o limiar é 0,2 s (LIMIAR_REDUZIDO_MS), o de uma troca de cor ou
// de foco que a pessoa nem percebe como movimento.
const LIMIAR_REDUZIDO_MS = 200;
function escutaReduzido(limiar) {
  window.__red = new Map();
  const rotulo = (el) => {
    if (!el || !el.tagName) return 'elemento desconhecido';
    return el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  };
  const volta = () => {
    try {
      for (const a of document.getAnimations()) {
        if (a.playState === 'finished' || a.playState === 'idle' || a.playState === 'paused') continue;
        const ef = a.effect;
        if (!ef) continue;
        const t = ef.getComputedTiming();
        const dur = Number(t.duration);
        const infinita = t.iterations === Infinity;
        const longa = Number.isNaN(dur) || dur > limiar;   // 'auto' (animação presa à rolagem) conta
        if (!longa && !(infinita && dur > 0)) continue;
        const alvo = ef.target;
        const prop = a.transitionProperty || a.animationName || (ef.getKeyframes ? [...new Set(ef.getKeyframes().flatMap((k) => Object.keys(k)).filter((k) => !['offset', 'easing', 'composite', 'computedOffset'].includes(k)))].join(', ') : '') || 'propriedade desconhecida';
        const tipo = a.transitionProperty ? 'transição' : (a.animationName ? 'animação CSS' : 'animação');
        const pseudo = ef.pseudoElement ? ' ' + ef.pseudoElement : '';
        const k = tipo + '|' + prop + '|' + rotulo(alvo) + pseudo;
        if (!window.__red.has(k)) window.__red.set(k, { tipo, prop, alvo: rotulo(alvo) + pseudo, dur: Number.isNaN(dur) ? null : Math.round(dur), infinita, sy: Math.round(window.scrollY) });
      }
    } catch (e) { /* navegador sem getAnimations: nada a medir */ }
    requestAnimationFrame(volta);
  };
  requestAnimationFrame(volta);
}
for (const [nome, w, h, mob] of [['iphone padrao', 390, 844, true], ['desktop comum', 1440, 900, false]]) {
  if (SO_VISIBILIDADE) continue;
  if ((SO_CELULAR || SO_PROVA_SCRIPT) && !mob) continue;
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob, reducedMotion: 'reduce' });
  await ctx.addInitScript(`(${escutaReduzido.toString()})(${LIMIAR_REDUZIDO_MS})`);
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'load', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  if (mob) {
    const suave = await page.evaluate(() => [document.documentElement, document.body].filter((el) => getComputedStyle(el).scrollBehavior === 'smooth').map((el) => el.tagName.toLowerCase()));
    console.log(`movimento reduzido: scroll-behavior ${suave.length ? 'smooth em ' + suave.join(', ') : 'auto'}`);
    if (suave.length) falhas.push(`movimento reduzido: scroll-behavior: smooth em ${suave.join(' e ')} com prefers-reduced-motion: reduce; os botões de âncora rolam animados para quem pediu menos movimento (use auto dentro de @media (prefers-reduced-motion: reduce))`);
  }
  await page.waitForTimeout(1200);
  const altura = await page.evaluate(() => document.documentElement.scrollHeight);
  const passo = Math.round(h * 0.4);
  for (let y = 0; y <= altura; y += passo) {
    await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);
    await page.waitForTimeout(350);
  }
  await page.waitForTimeout(800);
  const rodando = await page.evaluate(() => [...window.__red.values()]);
  const onde = `${nome} (${w}x${h})`;
  console.log(`movimento reduzido ${onde}: ${rodando.length ? rodando.length + ' animação(ões) em curso' : '0 animações em curso'}`);
  if (rodando.length) {
    const lista = rodando.slice(0, 5).map((r) => `${r.tipo} de ${r.prop} em ${r.alvo} (${r.infinita ? 'infinita' : r.dur === null ? 'presa à rolagem' : r.dur + ' ms'}, scrollY ${r.sy})`).join('; ');
    falhas.push(`movimento reduzido ${onde}: ${rodando.length} animação(ões) ou transição(ões) em curso com prefers-reduced-motion: reduce, acima de ${LIMIAR_REDUZIDO_MS} ms: ${lista}${rodando.length > 5 ? '; ...' : ''}. Dentro de @media (prefers-reduced-motion: reduce) ponha animation: none e transition: none nesses elementos (a página aparece no estado final, sem movimento)`);
  }
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
console.log(`  PASSA: ${TELAS.length} telas, nenhuma animação fora da tela e seções animando ao chegar; nenhum texto invisível parado no topo, no fim da visita nem depois de um salto; nenhum item chega parado a ${VELOCIDADE} px/s; nenhuma animação em curso com movimento reduzido.\n`);
