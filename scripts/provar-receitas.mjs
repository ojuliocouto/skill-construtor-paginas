#!/usr/bin/env node
/**
 * Prova no navegador de que cada receita do demo se move, e de que a página aguenta sem script e
 * com movimento reduzido.
 *
 * Por que existe (06/10/2026). A página aprovada pelo dono ficou boa pelo movimento, e esse movimento
 * não estava na skill. As receitas de `references/receitas-de-movimento.md` vêm com uma página de
 * demonstração (`references/receitas/demo.html`), e este script é o que impede a demonstração de
 * virar enfeite parado: para cada bloco `data-receita` ele grava um quadro antes e um depois do
 * gatilho do bloco (`data-gatilho`: carga, entrar, rolagem, clique ou hover) e mede a porcentagem de
 * pixels que mudou (limiar de 12 níveis de cinza, o mesmo do prancha.py).
 *
 * Também prova três garantias da gramática de base:
 *   1. com `javaScriptEnabled: false`, nenhum elemento do bloco fica com opacidade zero, escondido
 *      ou com área zero (todo estado escondido mora atrás de `.js`);
 *   2. com `prefers-reduced-motion: reduce`, nada fica escondido ao carregar e o texto da página
 *      inteira é o mesmo do modo normal;
 *   3. nenhum bloco gera rolagem lateral na página em 390 px.
 *
 * Uso: node scripts/provar-receitas.mjs --url <url do demo> --saida <pasta> [--so <receita>]
 * Saída: <saida>/<viewport>/<receita>-antes.png e -depois.png, <saida>/pagina-<viewport>.png e
 * <saida>/medidas.json. Código de saída 1 se alguma prova falhar.
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
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
const valor = (n) => { const i = args.indexOf(n); return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : null; };
const URL_ALVO = valor('--url'), SAIDA = valor('--saida'), SO = valor('--so');
if (!URL_ALVO || !SAIDA) { console.error('uso: node provar-receitas.mjs --url <url> --saida <pasta> [--so <receita>]'); process.exit(2); }
fs.mkdirSync(SAIDA, { recursive: true });

const LIMIAR_NIVEL = 12;
const MINIMO_MUDOU = 0.5; // por cento da área medida
const TELAS = [['desk', { width: 1440, height: 900 }, {}], ['mob', { width: 390, height: 844 }, { isMobile: true, hasTouch: true, deviceScaleFactor: 2 }]];
const espera = (ms) => new Promise((r) => setTimeout(r, ms));

// Compara duas imagens dentro de uma página em branco (sem dependência de PNG no Node).
async function porcentagemMudou(pagina, bufA, bufB) {
  return pagina.evaluate(async ([a, b, limiar]) => {
    const carregar = (b64) => new Promise((ok, erro) => { const i = new Image(); i.onload = () => ok(i); i.onerror = erro; i.src = 'data:image/png;base64,' + b64; });
    const [ia, ib] = await Promise.all([carregar(a), carregar(b)]);
    const w = Math.min(ia.width, ib.width), h = Math.min(ia.height, ib.height);
    const dados = (img) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.drawImage(img, 0, 0); return x.getImageData(0, 0, w, h).data; };
    const da = dados(ia), db = dados(ib);
    let n = 0;
    for (let i = 0; i < da.length; i += 4) {
      const ga = da[i] * 0.299 + da[i + 1] * 0.587 + da[i + 2] * 0.114, gb = db[i] * 0.299 + db[i + 1] * 0.587 + db[i + 2] * 0.114;
      if (Math.abs(ga - gb) > limiar) n++;
    }
    return +(100 * n / (w * h)).toFixed(2);
  }, [bufA.toString('base64'), bufB.toString('base64'), LIMIAR_NIVEL]);
}

async function caixaDoBloco(p, nome) {
  // `data-medir` no bloco aponta a parte que se move (as marcas, as vagas); sem ele vale o bloco inteiro.
  return p.evaluate((n) => {
    const b = document.querySelector('[data-receita="' + n + '"]'), sel = b.getAttribute('data-medir');
    const e = (sel && b.querySelector(sel)) || b, r = e.getBoundingClientRect(), L = document.documentElement.clientWidth;
    const x = sel ? Math.max(0, r.left - 12) : 0;
    return { x, y: r.top + window.scrollY, width: sel ? Math.min(L - x, r.width + 24) : L, height: r.height };
  }, nome);
}
const rolarPara = (p, y) => p.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);

const GATILHOS = {
  async carga(ctx, nome, tela, dir) {
    const p = await ctx.newPage();
    await p.goto(URL_ALVO, { waitUntil: 'load' });
    await espera(60);
    const clip = { x: 0, y: 0, width: tela.width, height: tela.height };
    const antes = await p.screenshot({ clip });
    await espera(2300);
    const depois = await p.screenshot({ clip });
    return { p, antes, depois };
  },
  async entrar(ctx, nome, tela) {
    // Sem fullPage: no celular a captura de página inteira redimensiona a tela e dispara o observador
    // de tudo antes da medida. O "antes" sai logo depois de a seção chegar, quando a animação mal começou.
    const p = await ctx.newPage();
    await p.goto(URL_ALVO, { waitUntil: 'load' });
    await espera(400);
    const topoBloco = await p.evaluate((n) => document.querySelector('[data-receita="' + n + '"]').getBoundingClientRect().top + window.scrollY, nome);
    await rolarPara(p, Math.max(0, topoBloco - tela.height * 0.1));
    const clip = await p.evaluate((n) => {
      const b = document.querySelector('[data-receita="' + n + '"]'), sel = b.getAttribute('data-medir');
      const e = (sel && b.querySelector(sel)) || b, r = e.getBoundingClientRect(), L = document.documentElement.clientWidth, A = window.innerHeight;
      const x = sel ? Math.max(0, r.left - 12) : 0, y = Math.max(0, r.top), y2 = Math.min(A, r.bottom);
      return { x, y, width: sel ? Math.min(L - x, r.width + 24) : L, height: Math.max(8, y2 - y) };
    }, nome);
    const antes = await p.screenshot({ clip, scale: 'css' });
    await espera(3200);
    const depois = await p.screenshot({ clip, scale: 'css' });
    return { p, antes, depois };
  },
  async rolagem(ctx, nome, tela) {
    const p = await ctx.newPage();
    await p.goto(URL_ALVO, { waitUntil: 'load' });
    await espera(400);
    const cx = await caixaDoBloco(p, nome);
    if (nome === 'paralaxe-da-foto' || nome === 'assinatura-em-tres-estados') {
      const alvo = nome === 'paralaxe-da-foto' ? '.paralaxe-quadro' : '.assin-coluna svg';
      const ref = nome === 'paralaxe-da-foto' ? await p.evaluate(() => { const r = document.querySelector('.paralaxe-quadro').getBoundingClientRect(); return r.top + window.scrollY + r.height / 2; })
        : await p.evaluate(() => { const r = document.querySelector('.passos').getBoundingClientRect(); return r.top + window.scrollY; });
      const fim = nome === 'paralaxe-da-foto' ? ref : await p.evaluate(() => { const r = document.querySelector('.passos').getBoundingClientRect(); return r.bottom + window.scrollY; });
      await rolarPara(p, nome === 'paralaxe-da-foto' ? ref - tela.height * 0.85 : ref - tela.height * 0.7);
      await espera(1800);
      const antes = await p.locator(alvo).first().screenshot();
      await rolarPara(p, nome === 'paralaxe-da-foto' ? ref - tela.height * 0.15 : fim - tela.height * 0.4);
      await espera(900);
      const depois = await p.locator(alvo).first().screenshot();
      return { p, antes, depois };
    }
    if (nome === 'barra-fixa-do-celular') {
      await rolarPara(p, 0);
      await espera(300);
      const antes = await p.screenshot();
      await rolarPara(p, cx.y + 40);
      await espera(900);
      const depois = await p.screenshot();
      return { p, antes, depois };
    }
    await rolarPara(p, cx.y - tela.height * 0.05);
    await espera(1500);
    const antes = await p.screenshot();
    await rolarPara(p, cx.y + tela.height * 0.55);
    await espera(900);
    const depois = await p.screenshot();
    return { p, antes, depois };
  },
  async clique(ctx, nome) {
    const p = await ctx.newPage();
    await p.goto(URL_ALVO, { waitUntil: 'load' });
    await espera(300);
    const alvo = p.locator('[data-receita="' + nome + '"] .faq');
    await alvo.scrollIntoViewIfNeeded();
    await espera(400);
    const antes = await alvo.screenshot();
    await p.locator('[data-receita="' + nome + '"] summary').first().click();
    await espera(700);
    const depois = await alvo.screenshot();
    return { p, antes, depois };
  },
  async navegacao(ctx, nome) {
    // O "depois" é o quadro com o painel cobrindo a tela (fase "cobre"); o "antes" é a página parada.
    const p = await ctx.newPage();
    await p.goto(URL_ALVO, { waitUntil: 'load' });
    await espera(300);
    const alvo = p.locator('[data-receita="' + nome + '"] [data-painel]').first();
    await alvo.scrollIntoViewIfNeeded();
    await espera(700);
    const antes = await p.screenshot({ scale: 'css' });
    await alvo.click();
    await p.waitForFunction(() => { const e = document.querySelector('.painel-cor'); return e && e.getAttribute('data-fase') === 'cobre'; }, null, { timeout: 4000, polling: 16 });
    const depois = await p.screenshot({ scale: 'css' });
    return { p, antes, depois };
  },
  async hover(ctx, nome) {
    const p = await ctx.newPage();
    await p.goto(URL_ALVO, { waitUntil: 'load' });
    await espera(300);
    const alvo = p.locator('[data-receita="' + nome + '"] [data-alvo-hover]');
    await alvo.scrollIntoViewIfNeeded();
    await espera(400);
    await p.mouse.move(2, 2);
    await espera(200);
    const caixa = await alvo.boundingBox();
    const clip = { x: Math.max(0, caixa.x - 14), y: Math.max(0, caixa.y - 14), width: caixa.width + 28, height: caixa.height + 40 };
    const antes = await p.screenshot({ clip });
    await alvo.hover();
    await espera(600);
    const depois = await p.screenshot({ clip });
    return { p, antes, depois };
  },
};

const resultado = { url: URL_ALVO, limiar_nivel: LIMIAR_NIVEL, minimo_mudou: MINIMO_MUDOU, blocos: [], sem_script: {}, movimento_reduzido: {}, lateral: {} };
let falhou = false;
const navegador = await chromium.launch();
const folha = await navegador.newPage();
await folha.setContent('<html><body></body></html>');

// 1. Cada bloco muda de pixel
const aba = await navegador.newPage({ viewport: { width: 1440, height: 900 } });
await aba.goto(URL_ALVO, { waitUntil: 'load' });
const receitas = await aba.evaluate(() => Array.prototype.map.call(document.querySelectorAll('[data-receita]'), (e) => ({ nome: e.getAttribute('data-receita'), gatilho: e.getAttribute('data-gatilho') })));
await aba.close();
for (const [tn, tela, opc] of TELAS) {
  const dir = path.join(SAIDA, tn); fs.mkdirSync(dir, { recursive: true });
  for (const r of receitas) {
    if (SO && r.nome !== SO) continue;
    const ctx = await navegador.newContext({ viewport: tela, ...opc });
    let linha = { receita: r.nome, tela: tn, gatilho: r.gatilho };
    try {
      const { antes, depois } = await GATILHOS[r.gatilho](ctx, r.nome, tela);
      fs.writeFileSync(path.join(dir, r.nome + '-antes.png'), antes);
      fs.writeFileSync(path.join(dir, r.nome + '-depois.png'), depois);
      linha.mudou = await porcentagemMudou(folha, antes, depois);
      linha.ok = linha.mudou >= MINIMO_MUDOU;
    } catch (e) { linha.ok = false; linha.erro = String(e.message).split('\n')[0]; }
    await ctx.close();
    if (!linha.ok) falhou = true;
    resultado.blocos.push(linha);
    console.log((linha.ok ? 'OK    ' : 'FALHOU') + ' ' + tn + ' ' + r.nome.padEnd(30) + ' ' + r.gatilho.padEnd(8) + ' ' + (linha.mudou !== undefined ? linha.mudou + '% mudou' : linha.erro));
  }
}

// 1b. Título fixo: em tela larga o título fica à esquerda da lista e não sai do lugar enquanto a lista passa
if (!SO || SO === 'titulo-fixo') {
  const ctx = await navegador.newContext({ viewport: TELAS[0][1] });
  const p = await ctx.newPage();
  await p.goto(URL_ALVO, { waitUntil: 'load' });
  const topo = await p.evaluate(() => document.querySelector('[data-receita="titulo-fixo"]').getBoundingClientRect().top + window.scrollY);
  const medir = () => p.evaluate(() => { const t = document.querySelector('[data-receita="titulo-fixo"] h2').getBoundingClientRect(), l = document.querySelector('[data-receita="titulo-fixo"] .fixo-lista').getBoundingClientRect(); return { tituloY: Math.round(t.top), tituloEsquerda: t.left < l.left }; });
  await rolarPara(p, topo + 200); await espera(400);
  const a = await medir();
  await rolarPara(p, topo + 500); await espera(400);
  const b = await medir();
  const ok = a.tituloEsquerda && b.tituloEsquerda && a.tituloY === b.tituloY;
  resultado.titulo_fixo = { a, b, ok };
  if (!ok) falhou = true;
  console.log((ok ? 'OK    ' : 'FALHOU') + ' título fixo: à esquerda=' + a.tituloEsquerda + ', y ' + a.tituloY + ' e ' + b.tituloY);
  await ctx.close();
}

// 2. Sem script: nada com opacidade zero ou escondido, e o conteúdo está lá
{
  const ctx = await navegador.newContext({ viewport: TELAS[0][1], javaScriptEnabled: false });
  const p = await ctx.newPage();
  await p.goto(URL_ALVO, { waitUntil: 'load' });
  const total = await p.locator('[data-receita]').count();
  // Com o JavaScript desligado o evaluate não roda: a medida usa a visibilidade que o próprio Playwright calcula.
  const ruins = [];
  const sel = await p.locator('[data-receita] h1, [data-receita] h2, [data-receita] h3, [data-receita] p, [data-receita] li, [data-receita] figure, [data-receita] dd i, [data-receita] summary, [data-receita] .vagas i, [data-receita] .botao').all();
  for (const el of sel) {
    if (await el.evaluate((e) => !!e.closest('details:not([open])') && e.tagName !== 'SUMMARY').catch(() => false)) continue;
    const vis = await el.isVisible();
    const op = await el.evaluate((e) => getComputedStyle(e).opacity).catch(() => null);
    if (!vis || op === '0') ruins.push(await el.evaluate((e) => e.tagName + '.' + e.className).catch(() => '?'));
  }
  await p.screenshot({ path: path.join(SAIDA, 'sem-script-desk.png'), fullPage: true });
  resultado.sem_script = { javaScriptEnabled: false, blocos: total, elementos_medidos: sel.length, escondidos: ruins };
  const ok = total >= 12 && ruins.length === 0;
  if (!ok) falhou = true;
  console.log((ok ? 'OK    ' : 'FALHOU') + ' sem script: ' + total + ' blocos, ' + sel.length + ' elementos medidos, ' + ruins.length + ' escondidos' + (ruins.length ? ' ' + JSON.stringify(ruins.slice(0, 6)) : ''));
  await ctx.close();
}

// 3. Movimento reduzido: nada escondido ao carregar e o mesmo texto do modo normal
{
  const texto = async (opc) => {
    const ctx = await navegador.newContext({ viewport: TELAS[0][1], ...opc });
    const p = await ctx.newPage();
    await p.goto(URL_ALVO, { waitUntil: 'load' });
    await espera(600);
    const escondidosAoCarregar = await p.evaluate(() => Array.prototype.filter.call(document.querySelectorAll('[data-receita] *'), (e) => {
      if (e.closest('svg') || e.closest('details:not([open])')) return false;
      const s = getComputedStyle(e);
      return s.opacity === '0' && e.textContent.trim().length > 0;
    }).length);
    const alt = await p.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y <= alt; y += 350) { await rolarPara(p, y); await espera(120); }
    await espera(3200);
    const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ').trim());
    const scrollLateral = await p.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    await ctx.close();
    return { t, escondidosAoCarregar, scrollLateral };
  };
  const normal = await texto({}), reduzido = await texto({ reducedMotion: 'reduce' });
  const igual = normal.t === reduzido.t;
  resultado.movimento_reduzido = { texto_igual: igual, caracteres: reduzido.t.length, escondidos_ao_carregar: reduzido.escondidosAoCarregar };
  const ok = igual && reduzido.escondidosAoCarregar === 0;
  if (!ok) falhou = true;
  console.log((ok ? 'OK    ' : 'FALHOU') + ' movimento reduzido: texto igual=' + igual + ' (' + reduzido.t.length + ' caracteres), escondidos ao carregar=' + reduzido.escondidosAoCarregar);
}

// 4. Prints da página inteira depois de rolar tudo, e rolagem lateral no celular
for (const [tn, tela, opc] of TELAS) {
  const ctx = await navegador.newContext({ viewport: tela, ...opc });
  const p = await ctx.newPage();
  await p.goto(URL_ALVO, { waitUntil: 'load' });
  const alt = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y <= alt; y += 300) { await rolarPara(p, y); await espera(150); }
  await espera(3000);
  const lateral = await p.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  await rolarPara(p, 0); await espera(400);
  await p.screenshot({ path: path.join(SAIDA, 'pagina-' + tn + '.png'), fullPage: true });
  resultado.lateral[tn] = lateral;
  if (lateral) falhou = true;
  console.log((lateral ? 'FALHOU' : 'OK    ') + ' rolagem lateral em ' + tn + ': ' + lateral);
  await ctx.close();
}

await navegador.close();
resultado.passou = !falhou;
fs.writeFileSync(path.join(SAIDA, 'medidas.json'), JSON.stringify(resultado, null, 2));
console.log(falhou ? 'REPROVADO' : 'APROVADO: ' + resultado.blocos.length + ' medidas de bloco');
process.exit(falhou ? 1 : 0);
