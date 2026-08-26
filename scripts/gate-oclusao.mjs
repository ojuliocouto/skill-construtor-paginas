#!/usr/bin/env node
/**
 * GATE DE OCLUSAO: acha conteudo COBERTO por outro elemento, ou CORTADO pela propria caixa.
 *
 * Por que existe (26/08/2026, falha real): uma faixa de numeros foi desenhada pra atravessar a
 * borda entre duas secoes. A textura de grao da secao de baixo era `absolute inset-0` sem
 * z-index, entao pintava por cima e comia os rotulos ("empresas atendidas", "colaboradores
 * impactados"). O dono viu na hora. Nenhum gate viu, nem no desktop nem no mobile, por DOIS
 * motivos distintos, e os dois valem pra qualquer pagina:
 *
 *  1. O que eu media era `opacity: 0` e `visibility: hidden`, e o elemento nao estava nem uma
 *     coisa nem outra: ele estava LA, opaco e visivel, com outra coisa por cima. Elemento
 *     coberto e elemento invisivel sao problemas diferentes, e so o segundo estava coberto
 *     por teste.
 *  2. Eu conferi olhando screenshot de pagina inteira reduzido a ~450px de largura. Um rotulo
 *     de 13px vira 4px nessa escala: o defeito era fisicamente invisivel na imagem que eu
 *     estava usando pra aprovar.
 *
 * O que este gate faz: rola ate CADA bloco de texto visivel, pergunta ao navegador quem esta
 * naquele pixel (`elementFromPoint`) e reprova quando a resposta nao e o proprio elemento.
 * Tambem pega texto cortado pela caixa (overflow escondendo linha).
 *
 * Uso:
 *   node scripts/gate-oclusao.mjs --url <url> [--min-chars 3]
 */
// NODE_PATH nao vale pra `import` em .mjs, so pra `require`: o mesmo gotcha que o
// extrai-identidade.mjs ja documenta. createRequire segue a resolucao CommonJS e acha o
// playwright no projeto, no NODE_PATH ou no root global do npm, em qualquer maquina.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import path from 'node:path';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try {
    return require('playwright');
  } catch {
    try {
      const rootGlobal = execSync('npm root -g', { encoding: 'utf8' }).trim();
      return require(path.join(rootGlobal, 'playwright'));
    } catch {
      console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium');
      process.exit(1);
    }
  }
}
const { chromium } = carregarPlaywright();

const args = process.argv.slice(2);
const pega = (n, padrao = null) => {
  const i = args.indexOf(n);
  return i >= 0 ? args[i + 1] : padrao;
};
const URL_ALVO = pega('--url');
const MIN = Number(pega('--min-chars', '3'));
if (!URL_ALVO) {
  console.error('uso: node gate-oclusao.mjs --url <url> [--min-chars 3]');
  process.exit(2);
}

const TELAS = [
  { nome: 'desktop', viewport: { width: 1440, height: 900 } },
  { nome: 'mobile', viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true },
];

const achados = [];
const navegador = await chromium.launch();

for (const tela of TELAS) {
  const ctx = await navegador.newContext(tela);
  const page = await ctx.newPage();
  try {
    await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 });
  } catch {
    await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 });
  }
  await page.waitForTimeout(1800);

  const r = await page.evaluate(async (minChars) => {
    const dorme = (ms) => new Promise((res) => setTimeout(res, ms));
    const cobertos = [];
    const cortados = [];

    // Folhas de texto: elementos sem filho-elemento, com texto de verdade.
    const folhas = [...document.querySelectorAll('p, h1, h2, h3, h4, li, span, a, dt, dd, figcaption, blockquote')]
      .filter((el) => {
        const t = (el.innerText || '').trim();
        if (t.length < minChars) return false;
        if (el.querySelector('p, h1, h2, h3, h4, li, span, a, dt, dd, figcaption, blockquote')) return false;
        const cs = getComputedStyle(el);
        if (cs.opacity === '0' || cs.visibility === 'hidden' || cs.display === 'none') return false;
        const c = el.getBoundingClientRect();
        return c.width > 8 && c.height > 6;
      })
      .slice(0, 220); // teto: pagina gigante nao vira teste de 10 minutos

    for (const el of folhas) {
      el.scrollIntoView({ block: 'center', behavior: 'instant' });
      await dorme(60);
      const c = el.getBoundingClientRect();
      if (c.bottom < 0 || c.top > window.innerHeight) continue;

      // Tres pontos: se o elemento e largo, a borda pode estar livre e o meio coberto.
      const ys = [c.y + c.height / 2];
      const xs = [c.x + c.width * 0.25, c.x + c.width * 0.5, c.x + c.width * 0.75];
      let cobriuEm = null;
      for (const x of xs) {
        for (const y of ys) {
          if (x < 0 || y < 0 || x > window.innerWidth || y > window.innerHeight) continue;
          const frente = document.elementFromPoint(Math.round(x), Math.round(y));
          if (!frente) continue;
          const meu = frente === el || el.contains(frente) || frente.contains(el);
          if (!meu) {
            cobriuEm = `${frente.tagName.toLowerCase()}.${(frente.className || '').toString().split(' ').slice(0, 2).join('.')}`;
          }
        }
      }
      if (cobriuEm) {
        cobertos.push({ texto: (el.innerText || '').trim().slice(0, 46), porQuem: cobriuEm });
      }

      // Texto cortado pela propria caixa (overflow comendo linha).
      const cs = getComputedStyle(el);
      const escondeY = cs.overflowY === 'hidden' || cs.overflow === 'hidden';
      if (escondeY && el.scrollHeight - el.clientHeight > 3 && cs.webkitLineClamp === 'none') {
        cortados.push({
          texto: (el.innerText || '').trim().slice(0, 46),
          sobra: el.scrollHeight - el.clientHeight,
        });
      }
    }
    return { cobertos, cortados, analisados: folhas.length };
  }, MIN);

  console.log(`\n[${tela.nome}] ${r.analisados} blocos de texto analisados`);
  for (const c of r.cobertos) {
    console.log(`   COBERTO  "${c.texto}"  <- ${c.porQuem}`);
    achados.push({ tela: tela.nome, tipo: 'coberto', ...c });
  }
  for (const c of r.cortados) {
    console.log(`   CORTADO  "${c.texto}"  (${c.sobra}px sobrando fora da caixa)`);
    achados.push({ tela: tela.nome, tipo: 'cortado', ...c });
  }
  if (!r.cobertos.length && !r.cortados.length) console.log('   ok       nada coberto, nada cortado');
  await ctx.close();
}
await navegador.close();

console.log('\n' + '='.repeat(70));
if (achados.length) {
  console.log(`  REPROVA: ${achados.length} bloco(s) de texto coberto(s) ou cortado(s).`);
  console.log('  Causa quase sempre a mesma: camada decorativa (textura, veu, gradiente) com');
  console.log('  `absolute inset-0` e SEM z-index, pintando por cima do conteudo. Mande a');
  console.log('  decoracao pra tras (-z-10) e declare a ordem entre as secoes com z explicito,');
  console.log('  em vez de depender da ordem do documento.\n');
  process.exit(1);
}
console.log('  PASSA: nenhum texto coberto ou cortado, nas duas telas.\n');
