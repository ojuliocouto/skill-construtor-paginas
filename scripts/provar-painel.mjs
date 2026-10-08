#!/usr/bin/env node
/**
 * Prova no navegador da receita `painel-de-cor` (painel na cor da marca que sobe e cobre a tela na
 * navegação interna). O dono aprovou o efeito num protótipo ("gostei muito desse"); aqui ele vira
 * receita com garantias medidas, porque um painel que cobre a tela é o pior defeito possível se travar.
 *
 * Verifica, em 1440, 390 e 360 px, no demo (`references/receitas/demo.html`):
 *   1. na fase `cobre` o painel cobre 100% da janela e é o elemento no topo; no fim a rolagem está no
 *      alvo, o painel não está mais ativo nem captura clique;
 *   2. o foco vai para o alvo (ou o título dele), o endereço ganha `#alvo` e o botão voltar funciona;
 *   3. só intercepta clique simples em link interno marcado: ctrl, cmd, shift, botão do meio, link
 *      externo, `target=_blank` e link interno sem a marca passam direto;
 *   4. movimento reduzido: sem painel, vai direto ao alvo. Sem JavaScript: a âncora comum funciona;
 *   5. se a animação nunca terminar (aba em segundo plano), o teto de tempo solta o painel;
 *   6. a cor vem do token `--marca` da página e nenhum texto fica no painel;
 *   7. sem rolagem horizontal em 390 e 360.
 *
 * Uso: node scripts/provar-painel.mjs --url <url do demo> --saida <pasta>
 * Saída: <saida>/painel-<largura>-cobre.png e <saida>/painel-medidas.json; código 1 se algo falhar.
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import fs from 'node:fs';
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
const valor = (n) => { const i = args.indexOf(n); return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : null; };
const URL_ALVO = valor('--url'), SAIDA = valor('--saida');
if (!URL_ALVO || !SAIDA) { console.error('uso: node provar-painel.mjs --url <url> --saida <pasta>'); process.exit(2); }
fs.mkdirSync(SAIDA, { recursive: true });

const espera = (ms) => new Promise((r) => setTimeout(r, ms));
const LARGURAS = [[1440, 900, {}], [390, 844, { isMobile: true, hasTouch: true, deviceScaleFactor: 2 }], [360, 780, { isMobile: true, hasTouch: true, deviceScaleFactor: 2 }]];
const SEL = '[data-receita="painel-de-cor"] [data-painel]';
const ALVO = 'alvo-painel';
const medidas = { url: URL_ALVO, provas: [] };
let falhou = false;
function prova(nome, ok, detalhe = '') {
  medidas.provas.push({ nome, ok, detalhe });
  if (!ok) falhou = true;
  console.log((ok ? 'OK    ' : 'FALHOU') + ' ' + nome + (detalhe ? ' -> ' + detalhe : ''));
}

// Registra cada mudança de fase do painel com o tempo desde o clique, e se o clique foi cancelado (defaultPrevented).
const OBSERVADOR = `
window.__fases = []; window.__dp = null;
document.addEventListener('DOMContentLoaded', function () {
  document.addEventListener('click', function () { window.__t0 = performance.now(); }, true);
  document.addEventListener('click', function (e) { window.__dp = e.defaultPrevented; }, false);
  new MutationObserver(function (ms) {
    var p = document.querySelector('.painel-cor'); if (!p || !ms.some(function (m) { return m.target === p; })) return;
    window.__fases.push([p.getAttribute('data-fase') || '', p.classList.contains('ativo'), Math.round(performance.now() - (window.__t0 || 0))]);
  }).observe(document.documentElement, { subtree: true, attributes: true, attributeFilter: ['data-fase', 'class'] });
});`;

async function abrir(navegador, [w, h, opc], extra = {}, init = []) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, ...opc, ...extra });
  ctx.setDefaultTimeout(8000);
  await ctx.addInitScript(OBSERVADOR);
  for (const s of init) await ctx.addInitScript(s);
  const p = await ctx.newPage();
  await p.goto(URL_ALVO, { waitUntil: 'load' });
  await espera(500);
  return { ctx, p };
}
const topoDoAlvo = (p) => p.evaluate((id) => Math.round(document.getElementById(id).getBoundingClientRect().top), ALVO);
const painelAtivo = (p) => p.evaluate(() => { const e = document.querySelector('.painel-cor'); return !!e && e.classList.contains('ativo'); });
async function esperarFase(p, fase, ms = 4000) {
  try { await p.waitForFunction((f) => { const e = document.querySelector('.painel-cor'); return e && e.getAttribute('data-fase') === f; }, fase, { timeout: ms, polling: 16 }); return true; } catch { return false; }
}
async function irAoBotao(p) {
  await p.locator(SEL).first().scrollIntoViewIfNeeded();
  await espera(700);
}

const navegador = await chromium.launch();

for (const tela of LARGURAS) {
  const [w] = tela;
  const rotulo = `[${w}]`;
  // ---- 1, 2, 6: o fluxo completo ----
  {
    const { ctx, p } = await abrir(navegador, tela);
    await irAoBotao(p);
    const antes = await p.evaluate(() => ({ y: Math.round(window.scrollY), url: location.href }));
    const bg = await p.evaluate(() => getComputedStyle(document.querySelector('.painel-cor')).backgroundColor);
    const marca = await p.evaluate(() => { const t = document.createElement('i'); t.style.color = 'var(--marca)'; document.body.appendChild(t); const c = getComputedStyle(t).color; t.remove(); return c; });
    prova(`${rotulo} a cor do painel é o token --marca da página (não um valor fixo)`, bg === marca && bg !== '', `${bg} x ${marca}`);
    await p.evaluate(() => document.documentElement.style.setProperty('--marca', 'rgb(200, 10, 20)'));
    const bg2 = await p.evaluate(() => getComputedStyle(document.querySelector('.painel-cor')).backgroundColor);
    prova(`${rotulo} trocar o token --marca muda a cor do painel`, bg2 === 'rgb(200, 10, 20)', bg2);
    await p.evaluate(() => document.documentElement.style.removeProperty('--marca'));

    await p.locator(SEL).first().click();
    const cobriu = await esperarFase(p, 'cobre');
    prova(`${rotulo} o painel chega à fase "cobre"`, cobriu);
    const c = await p.evaluate(() => {
      const e = document.querySelector('.painel-cor'), r = e.getBoundingClientRect(), vw = document.documentElement.clientWidth, vh = window.innerHeight;
      const pontos = [[2, 2], [vw / 2, vh / 2], [vw - 3, vh - 3], [vw / 2, 4], [vw / 2, vh - 4]];
      const topo = pontos.map(([x, y]) => document.elementFromPoint(x, y) === e);
      return { cobreTudo: r.top <= 1 && r.left <= 1 && r.bottom >= vh - 1 && r.right >= vw - 1, naFrente: topo.every(Boolean), filhos: e.children.length, texto: e.textContent.trim(), pointer: getComputedStyle(e).pointerEvents };
    });
    prova(`${rotulo} na fase "cobre" o painel cobre 100% da janela e é o elemento no topo em 5 pontos`, c.cobreTudo && c.naFrente, JSON.stringify(c));
    prova(`${rotulo} nenhum texto nem elemento fica por cima do painel`, c.filhos === 0 && c.texto === '');
    await p.screenshot({ path: path.join(SAIDA, `painel-${w}-cobre.png`) });
    const terminou = await p.waitForFunction(() => { const e = document.querySelector('.painel-cor'); return !e.classList.contains('ativo'); }, null, { timeout: 5000, polling: 50 }).then(() => true, () => false);
    prova(`${rotulo} o painel solta a tela no fim`, terminou);
    const fim = await p.evaluate(() => { const e = document.querySelector('.painel-cor'), s = getComputedStyle(e); const r = e.getBoundingClientRect(); const meio = document.elementFromPoint(document.documentElement.clientWidth / 2, window.innerHeight / 2); return { ativo: e.classList.contains('ativo'), pointer: s.pointerEvents, visivel: s.visibility, noTopo: meio === e, foco: document.activeElement && (document.activeElement.id || document.activeElement.tagName), url: location.hash, overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1 }; });
    const topo = await topoDoAlvo(p);
    prova(`${rotulo} no fim a rolagem está no alvo (topo do alvo a ${topo}px)`, Math.abs(topo) <= 2, String(topo));
    prova(`${rotulo} no fim o painel não está ativo, não captura clique e não está na frente`, !fim.ativo && !fim.noTopo && (fim.pointer === 'none' || fim.visivel === 'hidden'), JSON.stringify(fim));
    prova(`${rotulo} o endereço ganhou #${ALVO}`, fim.url === '#' + ALVO, fim.url);
    const foco = await p.evaluate((id) => { const a = document.getElementById(id), t = document.getElementById(a.getAttribute('aria-labelledby') || ''); return document.activeElement === a || document.activeElement === t; }, ALVO);
    prova(`${rotulo} o foco foi para o alvo ou para o título dele`, foco, String(fim.foco));
    prova(`${rotulo} sem rolagem horizontal`, !fim.overflowX);
    const t = await p.evaluate(() => window.__fases);
    const marcas = {};
    for (const [f, ativo, ms] of t) { if (f && marcas[f] === undefined) marcas[f] = ms; }
    medidas[`tempos_${w}`] = marcas;
    console.log('      fases e ms desde o clique: ' + JSON.stringify(marcas));
    // voltar
    await p.goBack();
    await espera(600);
    const volta = await p.evaluate(() => ({ hash: location.hash, y: Math.round(window.scrollY) }));
    prova(`${rotulo} o botão voltar tira o #${ALVO} e devolve a rolagem (${antes.y} -> ${volta.y})`, volta.hash === '' && Math.abs(volta.y - antes.y) <= 60, JSON.stringify(volta));
    await ctx.close();
  }
}

// ---- 3: o que passa direto ----
{
  const { ctx, p } = await abrir(navegador, LARGURAS[0]);
  await p.route('https://exemplo.invalid/**', (r) => r.fulfill({ status: 200, contentType: 'text/html', body: '<title>fora</title>' }));
  await irAoBotao(p);
  const casos = [
    ['ctrl+clique', () => p.locator(SEL).first().click({ modifiers: ['Control'], noWaitAfter: true })],
    ['cmd+clique', () => p.locator(SEL).first().click({ modifiers: ['Meta'], noWaitAfter: true })],
    ['shift+clique', () => p.locator(SEL).first().click({ modifiers: ['Shift'], noWaitAfter: true })],
    ['botão do meio', () => p.locator(SEL).first().click({ button: 'middle', noWaitAfter: true })],
    ['link interno sem a marca data-painel', () => p.locator('#link-direto').click({ noWaitAfter: true })],
    ['link com target=_blank', () => p.locator('#link-nova-aba').click({ noWaitAfter: true })],
  ];
  for (const [nome, fazer] of casos) {
    await p.evaluate(() => { window.__fases = []; window.__dp = null; });
    const y0 = await p.evaluate(() => window.scrollY);
    const paginas0 = ctx.pages().length;
    await fazer();
    await espera(450);
    const r = await p.evaluate(() => ({ dp: window.__dp, fases: window.__fases.length, ativo: !!document.querySelector('.painel-cor.ativo') }));
    // dp nulo = o navegador nem emitiu `click` (ctrl+clique no macOS vira menu de contexto; botão do meio emite auxclick): nada a cancelar
    prova(`[1440] ${nome} passa direto (sem painel, sem cancelar o clique)`, r.dp !== true && !r.ativo && r.fases === 0, JSON.stringify(r));
    for (const extra of ctx.pages().slice(paginas0)) await extra.close();
    await p.evaluate((y) => window.scrollTo({ top: y, behavior: 'instant' }), y0);
    await espera(150);
  }
  // link externo: o painel não pode nem acordar
  await p.evaluate(() => { window.__fases = []; window.__dp = null; });
  const navegou = p.waitForURL(/exemplo\.invalid/, { timeout: 4000 }).then(() => true, () => false);
  await p.locator('#link-externo').click({ noWaitAfter: true });
  prova('[1440] link externo navega normalmente (o painel não intercepta)', await navegou);
  await ctx.close();
}

// ---- 4: movimento reduzido e sem JavaScript ----
{
  const { ctx, p } = await abrir(navegador, LARGURAS[0], { reducedMotion: 'reduce' });
  await irAoBotao(p);
  await p.evaluate(() => { window.__fases = []; });
  await p.locator(SEL).first().click();
  await espera(250);
  const r = await p.evaluate(() => ({ fases: window.__fases.length, ativo: !!document.querySelector('.painel-cor.ativo'), hash: location.hash }));
  const topo = await topoDoAlvo(p);
  prova('[1440] movimento reduzido: sem painel, vai direto ao alvo e atualiza o endereço', r.fases === 0 && !r.ativo && Math.abs(topo) <= 2 && r.hash === '#' + ALVO, JSON.stringify({ ...r, topo }));
  await ctx.close();

  const sem = await navegador.newContext({ viewport: { width: 1440, height: 900 }, javaScriptEnabled: false });
  const q = await sem.newPage();
  await q.goto(URL_ALVO, { waitUntil: 'load' });
  await q.locator(SEL).first().scrollIntoViewIfNeeded();
  await q.locator(SEL).first().click();
  await espera(1800);
  const yAlvo = (await q.locator('#' + ALVO).boundingBox()).y;
  prova('[1440] sem JavaScript a âncora comum funciona (alvo no topo, endereço com #)', Math.abs(yAlvo) <= 100 && q.url().endsWith('#' + ALVO), `y=${Math.round(yAlvo)} ${q.url().slice(-14)}`);
  await sem.close();
}

// ---- 5: animação que nunca termina ----
{
  const travada = `(function () { var orig = Element.prototype.animate; Element.prototype.animate = function () { var a = orig.apply(this, arguments); try { a.pause(); } catch (e) {} return a; }; })();`;
  const { ctx, p } = await abrir(navegador, LARGURAS[0], {}, [travada]);
  await irAoBotao(p);
  await p.locator(SEL).first().click();
  await espera(600);
  const preso = await painelAtivo(p);
  const solto = await p.waitForFunction(() => !document.querySelector('.painel-cor').classList.contains('ativo'), null, { timeout: 6000, polling: 50 }).then(() => true, () => false);
  const topo = await topoDoAlvo(p);
  const noTopo = await p.evaluate(() => document.elementFromPoint(document.documentElement.clientWidth / 2, window.innerHeight / 2) === document.querySelector('.painel-cor'));
  prova('[1440] animação travada: o painel estava ativo e o teto de tempo o soltou', preso && solto, `ativo aos 600 ms: ${preso}, solto: ${solto}`);
  prova('[1440] animação travada: a página nunca fica coberta e o alvo foi alcançado', !noTopo && Math.abs(topo) <= 2, `topo do alvo ${topo}`);
  await ctx.close();
}

await navegador.close();
medidas.passou = !falhou;
fs.writeFileSync(path.join(SAIDA, 'painel-medidas.json'), JSON.stringify(medidas, null, 2));
console.log(falhou ? 'REPROVADO' : `APROVADO: ${medidas.provas.length} provas`);
process.exit(falhou ? 1 : 0);
