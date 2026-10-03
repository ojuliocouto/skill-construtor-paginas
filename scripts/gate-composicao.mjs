#!/usr/bin/env node
/**
 * GATE DE COMPOSIÇÃO: cara de template (o mesmo esqueleto seção após seção) e ícone de biblioteca.
 *
 * Por que existe (02/10/2026, auditoria da v4 do estúdio, nota 6,5). A v4 trocou o "jornal de
 * filetes" da v3 por outro molde: Situações, Como funciona, Duas formas e Dúvidas usavam o mesmo
 * h2 à esquerda com uma grade de caixas embaixo (14 caixas na página). E os ícones eram a
 * metáfora de biblioteca: balão de conversa com reticências para "Chame no WhatsApp", calendário
 * com check para "Combine o horário", o mesmo par de bonecos em duas seções. As referências
 * fortes (Kins, Tia, Parsley) dão a cada seção uma composição própria. Todos os gates passavam,
 * porque nenhum olhava a página como sequência.
 *
 * O que mede, no desktop (1440x900), depois de rolar a página inteira:
 *  1. ESQUELETO REPETIDO: a assinatura de cada seção com h2 é a posição do título (à esquerda,
 *     centralizado ou ao lado do conteúdo) mais o corpo (grade de caixas, split com imagem,
 *     lista, colunas sem caixa ou texto). Mais de 2 seções SEGUIDAS com a mesma assinatura
 *     reprova.
 *  2. ÍCONE: todo SVG desenhado na página (fora de botão e link, a partir de 24 px) declara o que
 *     desenha em `data-desenho`. Sem a declaração reprova; declaração de metáfora de biblioteca
 *     (balão, calendário, check, boneco de palito, estrela, coração, lâmpada, foguete...) reprova;
 *     o mesmo desenho (mesmo traçado) em dois lugares reprova.
 *
 * Exceções declaradas: `data-composicao-ok="motivo"` na seção e `data-icone-repetido-ok` no SVG.
 *
 * Uso: node scripts/gate-composicao.mjs --url <url>
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
  console.error('uso: node gate-composicao.mjs --url <url>');
  process.exit(2);
}
const MAXIMO_SEGUIDAS = 2;
// Metáforas de biblioteca de ícone. O problema não é o ícone, é o genérico: desenhe o assunto.
const GENERICOS = String.raw`bal[aã]o|chat|calend[aá]rio|agenda|check|visto|boneco|palito|estrela|cora[cç][aã]o|l[aâ]mpada|foguete|alvo|engrenagem|cadeado|escudo|trof[eé]u|medalha|sino|lupa|envelope|telefone|rel[oó]gio|raio|polegar|joinha|aperto de m[aã]o|gr[aá]fico subindo`;

const navegador = await chromium.launch();
const ctx = await navegador.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
try { await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
const altura = await page.evaluate(() => document.documentElement.scrollHeight);
for (let y = 0; y <= altura; y += 450) {
  await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await page.waitForTimeout(120);
}
await page.waitForTimeout(1500);
await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
await page.waitForTimeout(200);

const r = await page.evaluate((genericos) => {
  const visivel = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const c = el.getBoundingClientRect();
    return c.width > 1 && c.height > 1;
  };
  const fundo = (el) => {
    for (let n = el; n; n = n.parentElement) {
      const b = getComputedStyle(n).backgroundColor;
      if (b && b !== 'rgba(0, 0, 0, 0)' && b !== 'transparent') return b;
    }
    return 'rgb(255, 255, 255)';
  };
  const temCaixa = (el, base) => {
    const cs = getComputedStyle(el);
    if (cs.boxShadow !== 'none') return true;
    if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== base) return true;
    return ['Top', 'Right', 'Bottom', 'Left'].filter((l) => parseFloat(cs['border' + l + 'Width']) > 0 && cs['border' + l + 'Style'] !== 'none').length >= 3;
  };
  const rotulo = (el) => (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 40);
  const lado = (a, b) => (a.right <= b.left + 4 || b.right <= a.left + 4) && a.top < b.bottom && b.top < a.bottom;

  const secoes = [...document.querySelectorAll('section')].filter((s) => visivel(s) && !s.parentElement.closest('section') && s.getBoundingClientRect().height >= 120);
  const assinaturas = secoes.map((s, i) => {
    if (s.hasAttribute('data-composicao-ok')) return { sig: `exceção:${i}`, nome: rotulo(s), excecao: s.getAttribute('data-composicao-ok') };
    const h = [...s.querySelectorAll('h2')].find(visivel);
    if (!h) return { sig: `sem-titulo:${i}`, nome: s.id || 'sem h2' };
    const hr = h.getBoundingClientRect();
    const sr = s.getBoundingClientRect();
    const base = fundo(s);
    const todos = [...s.querySelectorAll('*')].filter((el) => visivel(el) && !el.contains(h) && !h.contains(el));
    // Título: ao lado de algum bloco de conteúdo, centralizado, ou à esquerda em cima.
    let titulo = 'esq';
    if (todos.some((el) => { const c = el.getBoundingClientRect(); return c.width >= 120 && c.height >= 60 && c.left >= hr.right - 4 && c.top < hr.bottom + 40 && c.bottom > hr.top; })) titulo = 'lado';
    else {
      const rg = document.createRange(); rg.selectNodeContents(h);
      const tr = rg.getBoundingClientRect();
      if (getComputedStyle(h).textAlign === 'center' || Math.abs((tr.left + tr.right) / 2 - (sr.left + sr.right) / 2) < 40) titulo = 'centro';
    }
    // Corpo.
    let corpo = 'texto';
    const grade = todos.find((el) => {
      const filhos = [...el.children].filter((f) => visivel(f) && f.getBoundingClientRect().width >= 120);
      const caixas = filhos.filter((f) => temCaixa(f, fundo(el)));
      if (caixas.length < 2) return false;
      return caixas.some((a, k) => caixas.slice(k + 1).some((b) => lado(a.getBoundingClientRect(), b.getBoundingClientRect())));
    });
    if (grade) corpo = 'grade de caixas';
    else if (todos.some((el) => {
      if (!['IMG', 'PICTURE', 'VIDEO', 'svg', 'CANVAS', 'FIGURE'].includes(el.tagName)) return false;
      const c = el.getBoundingClientRect();
      if (c.width < sr.width * 0.25) return false;
      return [...s.querySelectorAll('p, h2')].some((t) => visivel(t) && lado(c, t.getBoundingClientRect()));
    })) corpo = 'split com imagem';
    else if (todos.some((el) => ['UL', 'OL', 'DL'].includes(el.tagName) && [...el.children].filter(visivel).length >= 3) || s.querySelectorAll('details').length >= 3) corpo = 'lista';
    else if (todos.some((el) => { const f = [...el.children].filter((x) => visivel(x) && x.getBoundingClientRect().width >= 120); return f.length >= 2 && lado(f[0].getBoundingClientRect(), f[1].getBoundingClientRect()); })) corpo = 'colunas sem caixa';
    const nomes = { esq: 'título à esquerda', centro: 'título centralizado', lado: 'título ao lado do conteúdo' };
    return { sig: `${nomes[titulo]} + ${corpo}`, nome: rotulo(h) };
  });

  // Ícones e desenhos.
  const re = new RegExp(genericos, 'i');
  const svgs = [...document.querySelectorAll('svg')].filter((v) => {
    if (!visivel(v) || v.closest('a, button, summary, label, [data-icone-ok]')) return false;
    const c = v.getBoundingClientRect();
    return c.width >= 24 && c.height >= 24;
  });
  const semDesenho = [], genericosAchados = [], tracados = new Map();
  for (const v of svgs) {
    const d = (v.getAttribute('data-desenho') || (v.closest('[data-desenho]') || { getAttribute: () => '' }).getAttribute('data-desenho') || '').trim();
    const secao = v.closest('section');
    const onde = secao ? rotulo(secao.querySelector('h1, h2') || secao) : 'fora de seção';
    if (!d) semDesenho.push(`SVG de ${Math.round(v.getBoundingClientRect().width)} px em "${onde}"`);
    else if (re.test(d)) genericosAchados.push(`"${d}" em "${onde}"`);
    if (v.hasAttribute('data-icone-repetido-ok')) continue;
    const chave = [...v.querySelectorAll('path, circle, rect, line, polyline, polygon, ellipse')]
      .map((n) => n.tagName + ':' + ['d', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'points', 'x1', 'y1', 'x2', 'y2'].map((a) => n.getAttribute(a) || '').join(',')).join('|');
    if (!chave) continue;
    const lista = tracados.get(chave) || [];
    lista.push(d || onde); tracados.set(chave, lista);
  }
  const repetidos = [...tracados.values()].filter((l) => l.length > 1).map((l) => `${l.length}x: ${l.map((x) => `"${x}"`).join(', ')}`);
  return { assinaturas, semDesenho, genericosAchados, repetidos, nSvgs: svgs.length };
}, GENERICOS);
await navegador.close();

const falhas = [];
console.log('\nGATE DE COMPOSIÇÃO  ' + URL_ALVO);
console.log('='.repeat(88));
console.log('Seções com h2, na ordem da página (desktop 1440):');
r.assinaturas.forEach((a, i) => console.log(`  ${String(i + 1).padStart(2)}. ${a.nome.padEnd(42)} ${a.sig.startsWith('sem-titulo') ? '(sem h2)' : a.excecao ? `(exceção: ${a.excecao})` : a.sig}`));
let ini = 0;
for (let i = 1; i <= r.assinaturas.length; i++) {
  if (i < r.assinaturas.length && r.assinaturas[i].sig === r.assinaturas[ini].sig) continue;
  const n = i - ini;
  if (n > MAXIMO_SEGUIDAS) falhas.push(`mesmo esqueleto ("${r.assinaturas[ini].sig}") em ${n} seções seguidas: ${r.assinaturas.slice(ini, i).map((a) => `"${a.nome}"`).join(', ')} (máximo ${MAXIMO_SEGUIDAS}); dê a cada seção um tratamento próprio`);
  ini = i;
}
r.semDesenho.forEach((s) => falhas.push(`desenho sem data-desenho (declare o que ele desenha, ligado ao conteúdo): ${s}`));
r.genericosAchados.forEach((s) => falhas.push(`ícone genérico de biblioteca: ${s}; desenhe o assunto da seção`));
r.repetidos.forEach((s) => falhas.push(`desenho repetido com o mesmo traçado ${s}`));
console.log(`Desenhos SVG medidos: ${r.nSvgs}`);
console.log('='.repeat(88));
if (falhas.length) {
  falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${falhas.length} problema(s) de composição.\n`);
  process.exit(1);
}
console.log('  PASSA: nenhuma sequência de mais de 2 seções com o mesmo esqueleto, desenhos declarados e próprios.\n');
