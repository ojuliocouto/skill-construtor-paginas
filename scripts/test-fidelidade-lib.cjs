/**
 * 3.7.0: as contas do gate de fidelidade (`fidelidade-lib.mjs`), sem navegador. De onde vem: o `medir.mjs` e o `comparar.py`
 * que o aluno escreveu à mão no teste do CLONAR da 3.6.3, e que acharam todos os defeitos de fidelidade do clone.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);
const lib = () => import(pathToFileURL(path.join(__dirname, 'fidelidade-lib.mjs')).href);
const el = (tag, texto, rect, estilo = {}, extra = {}) => ({ tag, texto, visivel: texto, rect, estilo: { fontSize: '16px', color: 'rgb(0, 0, 0)', ...estilo }, ...extra });

teste('nome da imagem sem pasta, query nem hash do empacotador', async () => {
  const { nomeDaImagem } = await lib();
  assert.equal(nomeDaImagem('https://x.io/_app/immutable/assets/logo.DqJRMuTx.svg?v=2'), 'logo');
  assert.equal(nomeDaImagem('/imagens/flutter_logo.png'), 'flutter_logo');
  assert.equal(nomeDaImagem('imagens/Foto%20Hero.webp'), 'foto hero');
});

teste('pareia pela tag e pelo texto, mesmo com a classe trocada, e acha a fonte e a caixa diferentes', async () => {
  const { compararElementos } = await lib();
  const o = [el('h1', 'Open Source backend', [10, 100, 600, 80], { fontSize: '40px' }), el('p', 'Um parágrafo', [10, 200, 600, 22])];
  const c = [el('h1', 'Open Source backend', [10, 100, 600, 95], { fontSize: '44px' }), el('p', 'Um parágrafo', [10, 200, 600, 22])];
  const r = compararElementos(o, c);
  assert.equal(r.pares, 2);
  assert.equal(r.faltando.length, 0);
  assert.equal(r.diferencas.length, 1);
  assert.match(r.diferencas[0].itens.join(' '), /caixa altura 80 contra 95/);
  assert.match(r.diferencas[0].itens.join(' '), /fonte de 40px contra 44px/);
});

teste('o herói de 708 contra 723 px do aluno reprova a largura', async () => {
  const { compararElementos, falhasDaLargura } = await lib();
  const o = [el('section', '', [0, 0, 1440, 723])], c = [el('section', '', [0, 0, 1440, 708])];
  const comparacao = compararElementos(o, c);
  const f = falhasDaLargura('1440 px', { pixelsPct: 0.4, alturaOriginal: 2295, alturaClone: 2280, comparacao });
  assert.ok(f.some((x) => /altura da página 2295 px na original contra 2280/.test(x)), f.join('\n'));
  assert.ok(f.some((x) => /com caixa, texto ou estilo diferente/.test(x)), f.join('\n'));
});

teste('quem mudou de texto no mesmo lugar se pareia e mostra o texto (a original mudou depois do clone)', async () => {
  const { compararElementos } = await lib();
  const r = compararElementos([el('a', 'PocketBase v0.41.0', [20, 20, 160, 30])], [el('a', 'PocketBase v0.40.6', [20, 20, 160, 30])]);
  assert.equal(r.faltando.length, 0);
  assert.match(r.diferencas[0].itens[0], /texto "PocketBase v0.41.0" contra "PocketBase v0.40.6"/);
});

teste('elemento da original sem par no clone vai em faltando', async () => {
  const { compararElementos, falhasDaLargura } = await lib();
  const comparacao = compararElementos([el('button', 'Live demo', [20, 600, 120, 40])], []);
  assert.deepEqual(comparacao.faltando, ['button|live demo@1']);
  assert.ok(falhasDaLargura('390 px', { pixelsPct: 0, alturaOriginal: 10, alturaClone: 10, comparacao }).some((x) => /sem par no clone/.test(x)));
});

teste('estilo diferente sem pixel diferente na caixa é aviso, não reprova', async () => {
  const { compararElementos, falhasDaLargura } = await lib();
  const o = [el('img', 'logo', [0, 0, 40, 40], { display: 'inline' }, { src: 'a/logo.png' })];
  const c = [el('img', 'logo', [0, 0, 40, 40], { display: 'block' }, { src: 'b/logo.png' })];
  const comparacao = compararElementos(o, c, undefined, () => false);
  assert.equal(comparacao.diferencas.length, 1);
  assert.equal(comparacao.diferencas[0].invisivel, true);
  assert.deepEqual(falhasDaLargura('1440 px', { pixelsPct: 0, alturaOriginal: 10, alturaClone: 10, comparacao }), []);
});

teste('células diferentes vizinhas viram um retângulo só; as soltas, outro', async () => {
  const { retangulos } = await lib();
  const col = 10, lin = 10, m = new Uint8Array(col * lin);
  m[0] = 1; m[1] = 1; m[col + 1] = 1;   // bloco no canto
  m[5 * col + 8] = 1;                    // solta
  const r = retangulos(m, col, lin, 8);
  assert.equal(r.length, 2);
  assert.deepEqual([r[0].x, r[0].y, r[0].largura, r[0].altura], [0, 0, 16, 16]);
  assert.deepEqual([r[1].x, r[1].y], [64, 40]);
});

teste('pixels acima do limite reprovam, abaixo passam', async () => {
  const { falhasDaLargura } = await lib();
  const comparacao = { pares: 1, faltando: [], diferencas: [] };
  assert.equal(falhasDaLargura('1440 px', { pixelsPct: 0.054, alturaOriginal: 2295, alturaClone: 2295, comparacao }).length, 0);
  assert.match(falhasDaLargura('1440 px', { pixelsPct: 22, alturaOriginal: 2295, alturaClone: 2295, comparacao })[0], /22% dos pixels diferentes/);
});

(async () => {
  let falhas = 0;
  for (const [nome, fn] of testes) {
    try { await fn(); console.log(`ok   ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome}\n  ${String(e && e.stack || e).split('\n').slice(0, 6).join('\n  ')}`); }
  }
  console.log(`\n${testes.length - falhas} de ${testes.length} testes passaram.`);
  process.exit(falhas ? 1 : 0);
})();
