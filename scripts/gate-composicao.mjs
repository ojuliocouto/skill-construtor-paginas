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
 *  3. (auditoria da v5, 03/10/2026) DESENHO QUE LÊ COMO WIREFRAME: SVG com data-desenho em que
 *     80% ou mais dos traços são retas alinhadas e retângulos (as "plantas baixas" de "Duas
 *     formas" e a "mesa" das situações). Desenhe a cena: pessoa, aparelho com volume, gesto.
 *  4. (auditoria da v5) LINHA DO TEMPO QUE PASSA DO ÚLTIMO MARCO (mais de 16 px), em 1440 e
 *     390: a da v5 seguia 311 px depois do 3o passo.
 *  5. (auditoria da v5) PÚBLICO DE PESSOAS SEM NINGUÉM NA PRIMEIRA TELA: com --publico (ou
 *     --projeto, que lê o público do briefing) falando de pessoas, a primeira tela em 1440 e em
 *     390 mostra uma figura humana: foto com alt que diz quem aparece, ou SVG próprio com
 *     data-figura="pessoa" de pelo menos 8 formas (um retângulo não é gente). A v5 tinha uma
 *     sala vazia e 7 desenhos de objeto para "mulheres de 35 a 60 com dor nas costas".
 *  6. (auditoria da v5) DESTAQUE ABAIXO DE 3:1: traço fino (até 3,5 px na tela) ou elemento
 *     .acento / [data-acento] de um data-desenho com contraste menor que 3:1 contra o que está
 *     embaixo dele. O amarelo que dava sentido aos desenhos estava a 2,07:1 no palco.
 *
 * Exceções declaradas: `data-composicao-ok="motivo"` na seção, `data-icone-repetido-ok` no SVG e
 * `data-assinatura` no SVG do momento assinatura (que repete por regra do plano).
 * O que está invisível (opacity 0, visibility hidden, display none) não entra na medida de contraste.
 *
 * Uso: node scripts/gate-composicao.mjs --url <url> [--publico "<público do briefing>" | --projeto <dir>]
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
const URL_ALVO = args[args.indexOf('--url') + 1];
if (!URL_ALVO || URL_ALVO.startsWith('--')) {
  console.error('uso: node gate-composicao.mjs --url <url>');
  process.exit(2);
}
const valor = (nome) => { const i = args.indexOf(nome); return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : null; };
let PUBLICO = valor('--publico');
const PROJETO = valor('--projeto');
if (!PUBLICO && PROJETO) {
  try { PUBLICO = JSON.parse(fs.readFileSync(path.join(PROJETO, 'evidencias', 'etapa-0.json'), 'utf8').replace(/^\uFEFF/, '')).briefing.publico; }
  catch {
    try { PUBLICO = (fs.readFileSync(path.join(PROJETO, 'evidencias', 'briefing.md'), 'utf8').match(/Para quem:\s*(.+)/i) || [])[1] || null; } catch { PUBLICO = null; }
  }
}
const PESSOAS = /mulher|homem|homens|pessoa|m[aã]es|pais\b|crian[cç]a|alun[oa]|paciente|cliente|idos[oa]|jovens|adult|fam[ií]lia|gestante|atleta|estudante|profission|donos?\b|donas?\b|empreendedor|moradores|p[uú]blico feminino|p[uú]blico masculino/i;
const MAXIMO_SEGUIDAS = 2;
// Metáforas de biblioteca de ícone. O problema não é o ícone, é o genérico: desenhe o assunto.
const GENERICOS = String.raw`bal[aã]o|chat|calend[aá]rio|agenda|check|sinal de visto|boneco|palito|estrela|cora[cç][aã]o|l[aâ]mpada|foguete|alvo|engrenagem|cadeado|escudo|trof[eé]u|medalha|sino|lupa|envelope|telefone|rel[oó]gio|raio|polegar|joinha|aperto de m[aã]o|gr[aá]fico subindo`;


const AJUDA = () => {
  const H = {};
  H.visivel = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const c = el.getBoundingClientRect();
    return c.width > 1 && c.height > 1;
  };
  H.fundoCss = (el) => {
    for (let n = el; n; n = n.parentElement) {
      const b = getComputedStyle(n).backgroundColor;
      if (b && b !== 'rgba(0, 0, 0, 0)' && b !== 'transparent') return b;
    }
    return 'rgb(255, 255, 255)';
  };
  H.rgb = (c) => { const m = (c || '').match(/[\d.]+/g); return m ? m.slice(0, 4).map(Number) : null; };
  H.mistura = (cima, alfa, baixo) => cima.slice(0, 3).map((v, i) => v * alfa + baixo[i] * (1 - alfa));
  H.lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  H.contraste = (a, b) => { const x = H.lum(a), y = H.lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  H.FORMAS = 'path, circle, rect, line, polyline, polygon, ellipse';
  // Traço reto e alinhado aos eixos: rect, line/polyline/polygon/path só com H, V e L horizontal ou vertical.
  H.alinhado = (n) => {
    const t = n.tagName.toLowerCase();
    if (t === 'rect') return true;
    if (t === 'circle' || t === 'ellipse') return false;
    const nums = (txt) => (txt.match(/-?\d*\.?\d+(?:e-?\d+)?/gi) || []).map(Number);
    if (t === 'line') { const [x1, y1, x2, y2] = ['x1', 'y1', 'x2', 'y2'].map((a) => Number(n.getAttribute(a) || 0)); return x1 === x2 || y1 === y2; }
    if (t === 'polyline' || t === 'polygon') {
      const v = nums(n.getAttribute('points') || '');
      for (let i = 2; i + 1 < v.length; i += 2) if (v[i] !== v[i - 2] && v[i + 1] !== v[i - 1]) return false;
      return true;
    }
    const d = n.getAttribute('d') || '';
    if (/[CcSsQqTtAa]/.test(d)) return false;
    const re = /([MmLlHhVvZz])([^MmLlHhVvZz]*)/g; let m, x = 0, y = 0;
    while ((m = re.exec(d))) {
      const c = m[1], v = nums(m[2]);
      if (c === 'H') x = v[v.length - 1] ?? x; else if (c === 'h') x += v.reduce((a, b) => a + b, 0);
      else if (c === 'V') y = v[v.length - 1] ?? y; else if (c === 'v') y += v.reduce((a, b) => a + b, 0);
      else if (c === 'M' || c === 'L' || c === 'm' || c === 'l') {
        for (let i = 0; i + 1 < v.length; i += 2) {
          const rel = c === 'm' || c === 'l';
          const nx = rel ? x + v[i] : v[i], ny = rel ? y + v[i + 1] : v[i + 1];
          const desenha = c === 'L' || c === 'l' || i > 0;
          if (desenha && nx !== x && ny !== y) return false;
          x = nx; y = ny;
        }
      }
    }
    return true;
  };
  H.formasDe = (svg) => [...svg.querySelectorAll(H.FORMAS)].filter((f) => !f.closest('defs, clipPath, mask'));
  H.wireframe = (svg) => {
    const f = H.formasDe(svg);
    if (f.length < 2) return null;
    const retas = f.filter(H.alinhado).length;
    return retas / f.length >= 0.8 ? { retas, total: f.length } : null;
  };
  return H;
};

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

await page.evaluate(`window.__H = (${AJUDA.toString()})()`);
const r = await page.evaluate((genericos) => {
  const H = window.__H;
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
    // O momento assinatura repete o mesmo desenho por regra do plano (3 ou mais seções): o marcador da receita
    // `data-assinatura` no próprio SVG o isenta. O mesmo desenho FORA da assinatura continua reprovando.
    if (v.hasAttribute('data-icone-repetido-ok') || v.hasAttribute('data-assinatura')) continue;
    const chave = [...v.querySelectorAll('path, circle, rect, line, polyline, polygon, ellipse')]
      .map((n) => n.tagName + ':' + ['d', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'points', 'x1', 'y1', 'x2', 'y2'].map((a) => n.getAttribute(a) || '').join(',')).join('|');
    if (!chave) continue;
    const lista = tracados.get(chave) || [];
    lista.push(d || onde); tracados.set(chave, lista);
  }
  const repetidos = [...tracados.values()].filter((l) => l.length > 1).map((l) => `${l.length}x: ${l.map((x) => `"${x}"`).join(', ')}`);

  // 3. Desenho que lê como wireframe. 6. Destaque abaixo de 3:1 contra o que está embaixo.
  const wireframes = [], fracos = [];
  let menorContraste = null;
  for (const v of svgs) {
    const d = (v.getAttribute('data-desenho') || (v.closest('[data-desenho]') || { getAttribute: () => '' }).getAttribute('data-desenho') || '').trim();
    if (!d) continue;
    const w = H.wireframe(v);
    if (w) wireframes.push(`"${d}" lê como wireframe: ${w.retas} de ${w.total} traços são retas alinhadas e retângulos`);
    const formas = H.formasDe(v);
    const base = H.rgb(H.fundoCss(v));
    const escala = (n) => { const m = n.getScreenCTM(); return m ? Math.hypot(m.a, m.b) : 1; };
    for (let i = 0; i < formas.length; i++) {
      const n = formas[i];
      // O que está invisível (opacity 0 no próprio elemento ou acima, visibility hidden, display none) não se mede.
      if (n.checkVisibility && !n.checkVisibility({ opacityProperty: true, visibilityProperty: true })) continue;
      const cs = getComputedStyle(n);
      const acento = n.matches('.acento, [data-acento]') || !!n.closest('.acento, [data-acento]');
      const larg = parseFloat(cs.strokeWidth) * escala(n);
      const temTraco = cs.stroke && cs.stroke !== 'none' && !cs.stroke.startsWith('url') && larg > 0;
      let cor = null, alfa = 1;
      if (temTraco && (larg <= 3.5 || acento)) { cor = H.rgb(cs.stroke); alfa = parseFloat(cs.strokeOpacity); }
      else if (acento && cs.fill && cs.fill !== 'none' && !cs.fill.startsWith('url')) { cor = H.rgb(cs.fill); alfa = parseFloat(cs.fillOpacity); }
      if (!cor) continue;
      alfa *= (cor[3] !== undefined && cor.length === 4 ? cor[3] : 1);
      for (let e = n; e && e !== v.parentElement; e = e.parentElement) alfa *= parseFloat(getComputedStyle(e).opacity);
      if (alfa < 0.05) continue;
      // Ponto do meio do traço, em coordenadas da tela.
      let px, py;
      try {
        const L = n.getTotalLength();
        const pt = n.getPointAtLength(L / 2);
        const sp = new DOMPoint(pt.x, pt.y).matrixTransform(n.getScreenCTM());
        px = sp.x; py = sp.y;
      } catch { const c = n.getBoundingClientRect(); px = c.left + c.width / 2; py = c.top + c.height / 2; }
      // O que está embaixo: a última forma preenchida ANTES desta que contém o ponto, senão o fundo CSS.
      let baixo = base;
      for (let j = i - 1; j >= 0; j--) {
        const f = formas[j];
        const fs = getComputedStyle(f);
        if (!fs.fill || fs.fill === 'none' || fs.fill.startsWith('url') || parseFloat(fs.fillOpacity) === 0) continue;
        try {
          const loc = new DOMPoint(px, py).matrixTransform(f.getScreenCTM().inverse());
          if (f.isPointInFill(loc)) { baixo = H.mistura(H.rgb(fs.fill), parseFloat(fs.fillOpacity), base); break; }
        } catch { /* forma sem geometria */ }
      }
      const visto = H.mistura(cor, alfa, baixo);
      const k = H.contraste(visto, baixo);
      menorContraste = menorContraste === null ? k : Math.min(menorContraste, k);
      if (k < 3) fracos.push(`${acento ? 'destaque' : 'traço fino'} ${cs.stroke !== 'none' && temTraco ? cs.stroke : cs.fill} a ${k.toFixed(2)}:1 contra o fundo em "${d}" (mínimo 3:1 para o que carrega informação)`);
    }
  }
  return { assinaturas, semDesenho, genericosAchados, repetidos, nSvgs: svgs.length, wireframes, fracos: [...new Set(fracos)], menorContraste };
}, GENERICOS);

/** Linha do tempo e pessoa na primeira tela: medidas que valem em 1440 e em 390. */
async function medirTela(pg, publico) {
  return pg.evaluate(({ publico, PESSOAS_SRC }) => {
    const H = window.__H;
    const out = { linhas: [], pessoa: null, maiorPassagem: 0 };
    // 4. Linha do tempo: o fio de um ol (::before ou ::after) contra o marco do último passo.
    for (const ol of document.querySelectorAll('ol')) {
      if (!H.visivel(ol) || getComputedStyle(ol).position === 'static') continue;
      const lis = [...ol.children].filter(H.visivel);
      // Tamanho de layout (offsetWidth), que a animação de escala não zera; o centro da caixa
      // escalada é o mesmo da caixa inteira.
      const marcos = lis.map((li) => [...li.querySelectorAll('*')].find((m) => {
        const c = m.getBoundingClientRect();
        const w = m.offsetWidth ?? c.width, h = m.offsetHeight ?? c.height;
        const cs = getComputedStyle(m);
        return cs.display !== 'none' && cs.visibility !== 'hidden' && w >= 8 && w <= 48 && h >= 8 && h <= 48 && Math.abs(w - h) <= 4;
      })).filter(Boolean);
      if (marcos.length < 2) continue;
      const or = ol.getBoundingClientRect();
      const ocs = getComputedStyle(ol);
      for (const pseudo of ['::before', '::after']) {
        const ps = getComputedStyle(ol, pseudo);
        if (ps.content === 'none' || ps.position !== 'absolute' || ps.display === 'none') continue;
        const w = parseFloat(ps.width), h = parseFloat(ps.height);
        if (!(w > 0 && h > 0) || Math.min(w, h) > 4 || Math.max(w, h) < 60) continue;
        const x0 = or.left + parseFloat(ocs.borderLeftWidth) + (parseFloat(ps.left) || 0);
        const y0 = or.top + parseFloat(ocs.borderTopWidth) + (parseFloat(ps.top) || 0);
        const centros = marcos.map((m) => { const c = m.getBoundingClientRect(); return { x: c.left + c.width / 2, y: c.top + c.height / 2 }; });
        const horizontal = w > h;
        const fim = horizontal ? x0 + w : y0 + h;
        const ultimo = horizontal ? Math.max(...centros.map((c) => c.x)) : Math.max(...centros.map((c) => c.y));
        const passa = Math.round(fim - ultimo);
        out.maiorPassagem = Math.max(out.maiorPassagem, passa);
        if (passa > 16) out.linhas.push(`a linha do tempo passa do último marco em ${passa} px (${horizontal ? 'horizontal' : 'vertical'}, "${(lis[lis.length - 1].innerText || '').replace(/\s+/g, ' ').trim().slice(0, 30)}")`);
      }
    }
    // 5. Pessoa na primeira tela (scrollY 0).
    if (publico) {
      const pessoas = new RegExp(PESSOAS_SRC, 'i');
      const PALAVRAS = /mulher|homem|pessoa|alun[oa]|fisioterapeuta|instrutor|instrutora|professor|professora|crian[cç]a|idos[oa]|paciente|senhora|senhor|menin[oa]|m[eé]dic[oa]|atendente|dona|dono/i;
      const vistoNaTela = (el) => { const c = el.getBoundingClientRect(); return Math.max(0, Math.min(c.bottom, window.innerHeight) - Math.max(c.top, 0)); };
      const candidatos = [];
      for (const img of document.querySelectorAll('img')) {
        if (H.visivel(img) && PALAVRAS.test(img.alt || '') && Math.max(img.getBoundingClientRect().width, img.getBoundingClientRect().height) >= 120) candidatos.push({ el: img, nome: `foto "${(img.alt || '').slice(0, 40)}"` });
      }
      for (const svg of document.querySelectorAll('svg')) {
        if (!H.visivel(svg)) continue;
        const dono = svg.closest('[data-figura], [data-desenho]') || svg;
        const fig = (dono.getAttribute('data-figura') || '') === 'pessoa' || PALAVRAS.test(dono.getAttribute('data-desenho') || '');
        if (!fig) continue;
        const c = svg.getBoundingClientRect();
        if (Math.max(c.width, c.height) < 120 || H.formasDe(svg).length < 8 || H.wireframe(svg)) continue;
        candidatos.push({ el: svg, nome: `desenho "${(dono.getAttribute('data-desenho') || 'pessoa').slice(0, 50)}"` });
      }
      const naTela = candidatos.map((c) => ({ ...c, px: Math.round(vistoNaTela(c.el)) })).filter((c) => c.px >= 100).sort((a, b) => b.px - a.px);
      out.pessoa = { publicoDePessoas: pessoas.test(publico), naTela: naTela.slice(0, 2).map((c) => `${c.nome} (${c.px} px à vista)`), total: candidatos.length };
    }
    return out;
  }, { publico, PESSOAS_SRC: PESSOAS.source });
}
const telasMedidas = [];
await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
await page.waitForTimeout(300);
telasMedidas.push(['desktop 1440', await medirTela(page, PUBLICO)]);
{
  const ctxM = await navegador.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const pm = await ctxM.newPage();
  try { await pm.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
  catch { await pm.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  const altM = await pm.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y <= altM; y += 420) { await pm.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y); await pm.waitForTimeout(100); }
  await pm.waitForTimeout(1500);
  await pm.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await pm.waitForTimeout(300);
  await pm.evaluate(`window.__H = (${AJUDA.toString()})()`);
  telasMedidas.push(['celular 390', await medirTela(pm, PUBLICO)]);
  await ctxM.close();
}
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
r.wireframes.forEach((x) => falhas.push(`desenho ${x}: ninguém do público lê um retângulo; desenhe a cena (pessoa, aparelho com volume, gesto)`));
r.fracos.forEach((x) => falhas.push(x));
for (const [tela, m] of telasMedidas) {
  m.linhas.forEach((x) => falhas.push(`${tela}: ${x}; termine a linha no centro do último marco`));
  if (m.pessoa && m.pessoa.publicoDePessoas && !m.pessoa.naTela.length) {
    falhas.push(`${tela}: nenhuma figura humana na primeira tela para um público de pessoas ("${PUBLICO}"): foto real com autorização ou ilustração própria com data-figura="pessoa" (${m.pessoa.total} figura(s) na página inteira)`);
  }
}
console.log(`Desenhos SVG medidos: ${r.nSvgs}; menor contraste de traço fino ou destaque: ${r.menorContraste === null ? 'nenhum medido' : r.menorContraste.toFixed(2) + ':1'}`);
for (const [tela, m] of telasMedidas) {
  console.log(`${tela}: linha do tempo passa do último marco em até ${m.maiorPassagem} px; pessoa na primeira tela: ${m.pessoa ? (m.pessoa.naTela.join('; ') || 'nenhuma') : 'não conferido (sem --publico nem --projeto)'}`);
}
console.log('='.repeat(88));
if (falhas.length) {
  falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${falhas.length} problema(s) de composição.\n`);
  process.exit(1);
}
console.log('  PASSA: nenhuma sequência de mais de 2 seções com o mesmo esqueleto, desenhos declarados e próprios.\n');
