/**
 * "Texto em linhas": nenhum trecho gerado pode ocupar mais de uma linha visual, em 1440, 390 e 360 px,
 * mesmo quando a fonte da página chega DEPOIS de o texto ser dividido.
 *
 * Defeito medido na v7 no ar (06/10/2026, 1440 px, 3 cargas seguidas): o script dividia o item "Você
 * parou a academia porque doeu, e ficou com medo de voltar." em 3 trechos, mas o primeiro não cabia na
 * largura real (515 px) e quebrava de novo, deixando "porque" sozinho numa linha. A divisão era medida
 * com uma fonte ou largura que já não valiam. Aqui a fonte chega atrasada de propósito (uma fonte
 * sintética bem larga, `scripts/fixtures/larga.ttf`, entra 700 ms depois da carga).
 *
 *   vermelho: o código da v7 (`scripts/fixtures/linhas-v7.js`) no lugar do módulo da receita;
 *   verde:    o módulo `texto-em-linhas` do `references/receitas/demo.html`.
 *
 * Sem Playwright, avisa e sai com 0 (NAO VERIFICADO).
 */
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { acharPlaywright } = require('./video/achar-playwright.cjs');

const raiz = path.resolve(__dirname, '..');
const demo = fs.readFileSync(path.join(raiz, 'references', 'receitas', 'demo.html'), 'utf8');
const v7 = fs.readFileSync(path.join(__dirname, 'fixtures', 'linhas-v7.js'), 'utf8');
const fonte = fs.readFileSync(path.join(__dirname, 'fixtures', 'larga.ttf')).toString('base64');
const LARGURAS = [1440, 390, 360];

const MODULO = /<script data-modulo="texto-em-linhas">[\s\S]*?<\/script>/;
const comV7 = () => { if (!MODULO.test(demo)) throw new Error('o demo não tem o módulo texto-em-linhas'); return demo.replace(MODULO, () => `<script data-modulo="texto-em-linhas">\n${v7}</script>`); };

const FONTE_ATRASADA = `
document.addEventListener('DOMContentLoaded', function () {
  var st = document.createElement('style');
  st.textContent = '[data-linhas]{font-family:Larga,serif !important;font-size:26px}';
  document.head.appendChild(st);
  setTimeout(function () { var f = new FontFace('Larga', 'url(data:font/ttf;base64,${fonte})'); document.fonts.add(f); f.load(); }, 700);
});`;

const MEDIR = () => {
  const linhasVisuais = (el) => { const r = document.createRange(); r.selectNodeContents(el); const tops = []; Array.prototype.forEach.call(r.getClientRects(), (c) => { if (c.width > 0 && !tops.some((t) => Math.abs(t - c.top) < 4)) tops.push(c.top); }); return tops.length; };
  const nos = Array.prototype.slice.call(document.querySelectorAll('[data-linhas]'));
  const trechos = Array.prototype.slice.call(document.querySelectorAll('[data-linhas] .linha'));
  return {
    elementos: nos.length,
    divididos: nos.filter((n) => n.classList.contains('dividido')).length,
    trechos: trechos.length,
    quebrados: trechos.filter((l) => linhasVisuais(l) > 1).map((l) => l.textContent),
    fonteChegou: document.fonts.check('26px Larga'),
  };
};

let falhas = 0;
const checa = (nome, ok, det = '') => { console.log(`${ok ? 'ok   ' : 'FALHA'} ${nome}${det ? ' -> ' + det : ''}`); if (!ok) falhas++; };

(async () => {
  const pw = acharPlaywright();
  if (!pw) { console.log('PULADO: Playwright não encontrado. Teste NAO VERIFICADO.'); return; }
  let html = demo;
  const servidor = http.createServer((_, res) => { res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(html); });
  await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${servidor.address().port}/`;
  const navegador = await pw.chromium.launch();
  const rodar = async (largura) => {
    const ctx = await navegador.newContext({ viewport: { width: largura, height: 900 } });
    const p = await ctx.newPage();
    await p.addInitScript(FONTE_ATRASADA);
    await p.goto(url, { waitUntil: 'load' });
    await p.waitForTimeout(2600);
    const m = await p.evaluate(MEDIR);
    await ctx.close();
    return m;
  };
  const resultado = {};
  for (const variante of ['v7', 'receita']) {
    html = variante === 'v7' ? comV7() : demo;
    for (const l of LARGURAS) resultado[`${variante}-${l}`] = await rodar(l);
  }
  await navegador.close();
  servidor.close();

  for (const l of LARGURAS) {
    const a = resultado[`v7-${l}`], b = resultado[`receita-${l}`];
    checa(`[${l}] a fonte atrasada chegou (o cenário é válido)`, a.fonteChegou && b.fonteChegou);
    checa(`[${l}] código da v7: o defeito aparece (trecho que quebra em 2 linhas)`, a.quebrados.length > 0, `${a.quebrados.length} de ${a.trechos} trechos: ${JSON.stringify(a.quebrados.slice(0, 2))}`);
    checa(`[${l}] receita: nenhum trecho gerado ocupa mais de uma linha`, b.quebrados.length === 0, `${b.quebrados.length} de ${b.trechos} trechos quebrados`);
    checa(`[${l}] receita: o texto foi mesmo dividido (${b.divididos} de ${b.elementos})`, b.divididos === b.elementos && b.trechos > b.elementos);
  }
  process.exitCode = falhas ? 1 : 0;
  console.log(falhas ? `\n${falhas} falha(s)` : '\nTudo verde.');
})().catch((e) => { console.error('FALHA inesperada:', e.message); process.exit(1); });
