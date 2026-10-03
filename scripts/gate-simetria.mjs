#!/usr/bin/env node
/**
 * GATE DE SIMETRIA: itens paralelos em caixas iguais e colunas que terminam juntas.
 *
 * Por que existe (02/10/2026). Duas reprovações do dono no mesmo dia viraram regra de gosto
 * (itens paralelos em caixas simétricas; passos em grade, nunca "título à esquerda + lista
 * vertical à direita") e, horas depois, a página do estúdio repetiu os dois desenhos: três
 * situações em escada (x 176, 448 e 629 px, alturas 161, 117 e 162 px), passos ao lado do
 * título e um card que terminava 210 px antes do vizinho. A autoavaliação contou "tells 0".
 * Regra escrita não bloqueia; medida no navegador bloqueia.
 *
 * O que mede, depois de rolar a página inteira e esperar as animações terminarem:
 *  1. GRUPO PARALELO: 3 a 6 irmãos do mesmo tipo (li, article, details, figure ou div com a
 *     mesma classe) dispostos lado a lado. Na mesma linha: topo e altura iguais com 1 px de
 *     tolerância. Cada um numa linha e numa coluna diferente: ESCADA, reprova. Linhas com
 *     quantidades diferentes (4 + 2): reprova.
 *  2. LISTA AO LADO DO TÍTULO (desktop, a partir de 1024 px): 3 ou mais li, details ou article
 *     empilhados numa coluna com o h2 da seção à esquerda deles. Reprova.
 *  4. DENTRO DE CARDS VIZINHOS (auditoria da v4): o título de um card e o do vizinho com o topo
 *     igual (4 px de folga), e nenhum card com um vão interno entre dois blocos mais de 80 px
 *     maior que o do vizinho (conteúdo flutuando por margin-top:auto). "Duas formas" tinha as
 *     caixas iguais (540 = 540 px) e os títulos a 147 px um do outro.
 *  3. COLUNAS VIZINHAS: filhos lado a lado de um grid ou flex cuja base visual (a caixa, se o
 *     filho tem fundo, borda ou sombra; senão o fim do conteúdo) difere mais de 80 px.
 *  5. (auditoria da v5) FAIXA DE LINHAS: caixas da mesma linha com o texto principal em
 *     quantidades de linhas que diferem mais de 1 (regra 20; em 768 eram 5, 3 e 4); e PASSOS
 *     SEM CAIXA: ol (ou [data-passos]) com 3 a 6 passos lado a lado sem fundo, borda nem sombra
 *     (regra 15: sequência de passos também vira grade de caixas iguais).
 *
 * Exceção declarada: `data-simetria-ok="motivo"` no contêiner (e cabeçalho, rodapé, nav e
 * aria-hidden ficam de fora). O motivo aparece na saída.
 *
 * Uso: node scripts/gate-simetria.mjs --url <url>
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
  console.error('uso: node gate-simetria.mjs --url <url>');
  process.exit(2);
}
const LIMITE_COLUNAS = 80;
const TOL_TITULO = 4;      // título com título nos cards vizinhos: topo igual com 4 px de folga
const BURACO = 80;         // diferença de vão interno entre cards vizinhos
const BURACO_MIN = 100;    // vão interno a partir do qual se chama de buraco
const TELAS = [
  ['desktop comum', 1440, 900],
  ['notebook comum', 1366, 768],
  ['tablet paisagem', 1024, 768],
  ['tablet retrato', 768, 1024],
];

/** Rola até o fim (dispara IntersectionObserver de revelação) e espera as animações. */
async function assentar(page) {
  const altura = await page.evaluate(() => document.documentElement.scrollHeight);
  const h = page.viewportSize().height;
  for (let y = 0; y <= altura; y += Math.round(h / 2)) {
    await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);
    await page.waitForTimeout(90);
  }
  const fim = Date.now() + 4000;
  while (Date.now() < fim) {
    const rodando = await page.evaluate(() => document.getAnimations()
      .filter((a) => a.playState === 'running' && a.effect && a.effect.getComputedTiming().endTime !== Infinity).length);
    if (!rodando) break;
    await page.waitForTimeout(150);
  }
  await page.waitForTimeout(250);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.waitForTimeout(150);
}

const navegador = await chromium.launch();
const falhas = [];
const excecoes = new Set();
console.log('\nGATE DE SIMETRIA  ' + URL_ALVO);
console.log('='.repeat(80));

for (const [nome, w, h] of TELAS) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h } });
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  await assentar(page);

  const r = await page.evaluate(({ limite, desktop, TOL_TITULO, BURACO, BURACO_MIN }) => {
    const out = { grupos: [], ladoTitulo: [], colunas: [], titulos: [], buracos: [], excecoes: [], maiorTitulo: 0, faixas: [], passosSemCaixa: [], maiorFaixa: 0 };
    const visivel = (el) => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      const c = el.getBoundingClientRect();
      return c.width > 0 && c.height > 0;
    };
    const fora = (el) => {
      const ok = el.closest('[data-simetria-ok]');
      if (ok) { out.excecoes.push(ok.getAttribute('data-simetria-ok') || 'sem motivo escrito'); return true; }
      return !!el.closest('header, footer, nav, [aria-hidden="true"], [hidden], script, style');
    };
    const solto = (el) => ['absolute', 'fixed'].includes(getComputedStyle(el).position);
    const rotulo = (el) => (el.innerText || el.tagName).replace(/\s+/g, ' ').trim().slice(0, 28);
    const assinatura = (el) => {
      const t = el.tagName;
      if (['LI', 'ARTICLE', 'DETAILS', 'FIGURE'].includes(t)) return t;
      if (t === 'DIV' && el.className && typeof el.className === 'string') return 'DIV.' + el.className.trim();
      return null;
    };
    const agrupar = (vals, tol) => {
      const grupos = [];
      for (const v of vals) {
        const g = grupos.find((x) => Math.abs(x.ref - v.k) <= tol);
        if (g) g.itens.push(v); else grupos.push({ ref: v.k, itens: [v] });
      }
      return grupos;
    };

    // Linhas renderizadas do texto principal de uma caixa (o parágrafo mais longo).
    const linhasDe = (el) => {
      const blocos = [...el.querySelectorAll('p, dd, blockquote')].filter(visivel);
      if (!blocos.length) return null;
      const b = blocos.sort((x, y) => (y.innerText || '').length - (x.innerText || '').length)[0];
      const rg = document.createRange(); rg.selectNodeContents(b);
      const tops = [];
      for (const r of rg.getClientRects()) {
        if (r.width < 1) continue;
        if (!tops.some((t) => Math.abs(t - r.top) < r.height * 0.5)) tops.push(r.top);
      }
      return tops.length;
    };
    const fundoDe = (el) => {
      for (let n = el; n; n = n.parentElement) {
        const b = getComputedStyle(n).backgroundColor;
        if (b && b !== 'rgba(0, 0, 0, 0)' && b !== 'transparent') return b;
      }
      return 'rgb(255, 255, 255)';
    };
    const caixaDe = (el) => {
      const cs = getComputedStyle(el);
      if (cs.boxShadow !== 'none' || cs.backgroundImage !== 'none') return true;
      if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && cs.backgroundColor !== fundoDe(el.parentElement)) return true;
      return ['Top', 'Right', 'Bottom', 'Left'].filter((l) => parseFloat(cs['border' + l + 'Width']) > 0 && cs['border' + l + 'Style'] !== 'none').length >= 3;
    };

    // 5 (auditoria da v5): PASSOS SEM CAIXA. A regra 15 do dono pede sequência de passos em
    // grade de caixas iguais; a v5 trocou as caixas por uma linha do tempo sem caixa e passou.
    for (const ol of document.querySelectorAll('ol, [data-passos]')) {
      if (!visivel(ol) || fora(ol)) continue;
      const passos = [...ol.children].filter((f) => visivel(f) && !solto(f));
      if (passos.length < 3 || passos.length > 6) continue;
      const tops = passos.map((f) => f.getBoundingClientRect().top);
      if (Math.max(...tops) - Math.min(...tops) > 12) continue;
      if (passos.some(caixaDe)) continue;
      out.passosSemCaixa.push(`${passos.length} passos lado a lado sem caixa a partir de "${rotulo(passos[0])}" (sequência de passos vira grade de caixas iguais)`);
    }

    // 1 e 2: grupos paralelos
    for (const pai of document.querySelectorAll('body *')) {
      if (!visivel(pai) || fora(pai)) continue;
      const porTipo = {};
      for (const f of pai.children) {
        if (!visivel(f) || solto(f)) continue;
        const a = assinatura(f);
        if (!a) continue;
        (porTipo[a] = porTipo[a] || []).push(f);
      }
      for (const [tipo, itens] of Object.entries(porTipo)) {
        if (itens.length < 3 || itens.length > 6) continue;
        const caixas = itens.map((el) => ({ el, c: el.getBoundingClientRect() }));
        if (caixas.some((x) => x.c.height < 40)) continue;
        const colunas = agrupar(caixas.map((x) => ({ k: x.c.left, x })), 8);
        if (colunas.length === 1) {
          if (!desktop || !['LI', 'DETAILS', 'ARTICLE'].includes(tipo)) continue;
          const topo = Math.min(...caixas.map((x) => x.c.top));
          const base = Math.max(...caixas.map((x) => x.c.bottom));
          const esq = Math.min(...caixas.map((x) => x.c.left));
          const secao = pai.closest('section') || document.body;
          const titulo = [...secao.querySelectorAll('h2')].find((t) => {
            const c = t.getBoundingClientRect();
            return visivel(t) && c.right <= esq + 4 && c.top < base && c.bottom > topo - 40;
          });
          if (titulo) out.ladoTitulo.push(`"${rotulo(titulo)}" à esquerda + ${itens.length} itens empilhados à direita`);
          continue;
        }
        const linhas = agrupar(caixas.map((x) => ({ k: x.c.top, x })), 12);
        const porLinha = linhas.map((l) => l.itens.length);
        if (Math.max(...porLinha) === 1) {
          out.grupos.push(`escada: ${itens.length} ${tipo.toLowerCase()} em ${linhas.length} alturas e ${colunas.length} colunas (x ${caixas.map((x) => Math.round(x.c.left)).join(', ')}) a partir de "${rotulo(itens[0])}"`);
          continue;
        }
        if (new Set(porLinha).size > 1) out.grupos.push(`grade irregular (${porLinha.join(' + ')}) em "${rotulo(itens[0])}"`);
        for (const l of linhas) {
          if (l.itens.length < 2) continue;
          const tops = l.itens.map((v) => v.x.c.top), alts = l.itens.map((v) => v.x.c.height);
          const dt = Math.max(...tops) - Math.min(...tops), dh = Math.max(...alts) - Math.min(...alts);
          if (dt > 1) out.grupos.push(`topos diferentes em ${dt.toFixed(1)} px na linha de "${rotulo(l.itens[0].x.el)}"`);
          if (dh > 1) out.grupos.push(`alturas diferentes em ${dh.toFixed(1)} px (${alts.map(Math.round).join(', ')}) na linha de "${rotulo(l.itens[0].x.el)}"`);
          // Regra 20 do dono (auditoria da v5): texto de cada caixa na mesma faixa de linhas.
          // Em 768 as situações tinham 5, 3 e 4 linhas e o gate só olhava topo e altura.
          const nl = l.itens.map((v) => linhasDe(v.x.el)).filter((n) => n !== null);
          if (nl.length === l.itens.length && Math.max(...nl) - Math.min(...nl) > 1) {
            out.faixas.push(`texto em ${nl.join(', ')} linhas nas caixas de "${rotulo(l.itens[0].x.el)}" (máximo 1 linha de diferença)`);
          }
          out.maiorFaixa = Math.max(out.maiorFaixa, nl.length ? Math.max(...nl) - Math.min(...nl) : 0);
        }
      }
    }

    // 3: colunas vizinhas
    const temCaixa = (el) => {
      const cs = getComputedStyle(el);
      if (['IMG', 'VIDEO', 'PICTURE', 'CANVAS', 'svg', 'SVG', 'IFRAME'].includes(el.tagName)) return true;
      if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || cs.backgroundImage !== 'none' || cs.boxShadow !== 'none') return true;
      return ['Top', 'Right', 'Bottom', 'Left'].filter((l) => parseFloat(cs['border' + l + 'Width']) > 0 && cs['border' + l + 'Style'] !== 'none').length >= 3;
    };
    // Ilustração em fluxo com aria-hidden é decorativa para leitor de tela, mas é o conteúdo
    // visual da coluna (v5: a coluna vertebral da avaliação contava como coluna vazia).
    const ilustracao = (n) => ['svg', 'IMG', 'PICTURE', 'CANVAS', 'VIDEO'].includes(n.tagName) && n.getBoundingClientRect().width >= 80 && n.getBoundingClientRect().height >= 80;
    const baseVisual = (el) => {
      if (temCaixa(el)) return el.getBoundingClientRect().bottom;
      let m = -Infinity;
      for (const n of el.childNodes) {
        if (n.nodeType === 3 && n.textContent.trim()) {
          const rg = document.createRange(); rg.selectNodeContents(n);
          const b = rg.getBoundingClientRect(); if (b.height) m = Math.max(m, b.bottom);
        } else if (n.nodeType === 1 && visivel(n) && !solto(n) && (n.getAttribute('aria-hidden') !== 'true' || ilustracao(n))) {
          m = Math.max(m, baseVisual(n));
        }
      }
      return m === -Infinity ? el.getBoundingClientRect().top : m;
    };
    const tituloDe = (card) => [...card.querySelectorAll('h2, h3, h4, dt, [data-titulo]')]
      .find((el) => visivel(el) && !el.closest('[aria-hidden="true"]')) || null;
    const maiorBuraco = (card) => {
      const blocos = [...card.children].filter((f) => visivel(f) && !solto(f)).map((f) => f.getBoundingClientRect()).sort((x, y) => x.top - y.top);
      let m = 0;
      for (let k = 1; k < blocos.length; k++) m = Math.max(m, blocos[k].top - blocos[k - 1].bottom);
      return m;
    };
    for (const pai of document.querySelectorAll('body *')) {
      if (!visivel(pai) || fora(pai)) continue;
      const cs = getComputedStyle(pai);
      const ehLinha = cs.display === 'grid' || cs.display === 'inline-grid'
        || ((cs.display === 'flex') && !cs.flexDirection.startsWith('column'));
      if (!ehLinha || pai.getBoundingClientRect().width < 400) continue;
      const filhos = [...pai.children].filter((f) => visivel(f) && !solto(f) && f.getBoundingClientRect().width >= 120);
      for (let i = 0; i < filhos.length; i++) {
        for (let j = i + 1; j < filhos.length; j++) {
          const a = filhos[i].getBoundingClientRect(), b = filhos[j].getBoundingClientRect();
          const vizinhos = (a.right <= b.left + 2 || b.right <= a.left + 2) && a.top < b.bottom && b.top < a.bottom;
          if (!vizinhos) continue;
          const d = Math.abs(baseVisual(filhos[i]) - baseVisual(filhos[j]));
          if (d > limite) out.colunas.push(`"${rotulo(filhos[i])}" e "${rotulo(filhos[j])}" terminam com ${Math.round(d)} px de diferença`);
          // 4 (auditoria da v4): DENTRO dos cards vizinhos. Caixa igual não basta: o título de um
          // card ficava 147 px acima do título do vizinho, e um card tinha um buraco no meio.
          // Título com título vale para coluna com ou sem caixa (v5: duas colunas sem caixa).
          const ta = tituloDe(filhos[i]), tb = tituloDe(filhos[j]);
          if (ta && tb && a.height >= 80 && b.height >= 80) {
            const dt = Math.abs(ta.getBoundingClientRect().top - tb.getBoundingClientRect().top);
            out.maiorTitulo = Math.max(out.maiorTitulo, dt);
            if (dt > TOL_TITULO) out.titulos.push(`"${rotulo(ta)}" e "${rotulo(tb)}" com ${Math.round(dt)} px de diferença no topo (máximo ${TOL_TITULO})`);
          }
          if (temCaixa(filhos[i]) && temCaixa(filhos[j]) && a.height >= 80 && b.height >= 80) {
            const ga = maiorBuraco(filhos[i]), gb = maiorBuraco(filhos[j]);
            if (Math.abs(ga - gb) > BURACO && Math.max(ga, gb) > BURACO_MIN) {
              const [cheio, oco] = ga > gb ? [filhos[j], filhos[i]] : [filhos[i], filhos[j]];
              out.buracos.push(`"${rotulo(oco)}" tem ${Math.round(Math.max(ga, gb))} px vazios entre dois blocos, o vizinho "${rotulo(cheio)}" tem ${Math.round(Math.min(ga, gb))} px (conteúdo flutuando no card)`);
            }
          }
        }
      }
    }
    return out;
  }, { limite: LIMITE_COLUNAS, desktop: w >= 1024, TOL_TITULO, BURACO, BURACO_MIN });

  const onde = `${nome} (${w}x${h})`;
  const todas = [...new Set(r.grupos)].map((x) => `grupo paralelo: ${x}`)
    .concat([...new Set(r.ladoTitulo)].map((x) => `lista vertical ao lado do título: ${x}`))
    .concat([...new Set(r.colunas)].map((x) => `colunas desbalanceadas: ${x}`))
    .concat([...new Set(r.titulos)].map((x) => `títulos de cards vizinhos desalinhados: ${x}`))
    .concat([...new Set(r.buracos)].map((x) => `buraco interno: ${x}`))
    .concat([...new Set(r.faixas)].map((x) => `faixa de linhas diferente: ${x}`))
    .concat([...new Set(r.passosSemCaixa)].map((x) => `passos sem caixa: ${x}`));
  r.excecoes.forEach((e) => excecoes.add(e));
  console.log(`${onde.padEnd(32)} ${todas.length ? 'FALHA (' + todas.length + ')' : 'ok'}`);
  console.log(`  medido: maior diferença entre títulos vizinhos ${Math.round(r.maiorTitulo)} px, maior diferença de linhas entre caixas da mesma linha ${r.maiorFaixa}`);
  for (const t of todas) falhas.push(`${onde}: ${t}`);
  await ctx.close();
}
await navegador.close();

console.log('='.repeat(80));
excecoes.forEach((e) => console.log(`  exceção declarada (data-simetria-ok): ${e}`));
if (falhas.length) {
  falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${falhas.length} problema(s) de simetria.`);
  console.log('  Itens paralelos: grade de caixas iguais (mesmo topo, mesma altura, entrada escalonada).');
  console.log('  Passos e perguntas: título em largura total em cima, itens em grade embaixo.');
  console.log(`  Colunas vizinhas terminam juntas (até ${LIMITE_COLUNAS} px) ou a seção se reestrutura.`);
  console.log('  Cards vizinhos: mesma estrutura por dentro (mídia do mesmo tamanho, título na mesma altura).\n');
  process.exit(1);
}
console.log(`  PASSA: ${TELAS.length} telas, itens paralelos simétricos e colunas equilibradas.\n`);
