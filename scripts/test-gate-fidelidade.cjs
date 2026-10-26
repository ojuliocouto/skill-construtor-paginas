/**
 * 3.7.0: o gate de fidelidade no navegador, contra páginas locais (file://), sem rede.
 *   - clone igual à original: PASSA, com o lado a lado e o diff em tamanho real gravados;
 *   - clone com o herói 15 px mais baixo e o título com outra fonte (os defeitos da volta 1 do aluno): REPROVA e diz onde;
 *   - original que não abre: ERRO DE FERRAMENTA (saída 3), sem culpar o clone;
 *   - sem --original, a URL vem de <projeto>/original/identidade.json (a saída do extrai-identidade.mjs).
 */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const GATE = path.join(__dirname, 'gate-fidelidade.mjs');
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'fidelidade çá '));
const pagina = ({ heroi = 300, h1 = '40px', cor = '#123456' } = {}) => `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>
body{margin:0;font-family:Georgia,serif;color:#222}header{height:60px;background:${cor};color:#fff;padding:0 24px;display:flex;align-items:center}
.heroi{height:${heroi}px;background:#b8dbe5;padding:40px 24px;box-sizing:border-box}h1{font-size:${h1};margin:0 0 16px}
ul{list-style:none;display:flex;gap:16px;padding:24px;margin:0}li{width:80px;height:40px;background:#ddd}footer{padding:24px;height:1000px;background:#e8eaee}
</style></head><body><header><a href="#">Marca v1.0</a></header><section class="heroi"><h1>Título do herói</h1><p>Um parágrafo de apoio.</p>
<button>Comprar</button></section><section><ul><li>Um</li><li>Dois</li><li>Três</li></ul></section><footer><p>Rodapé</p></footer></body></html>`;

function rodar(args) {
  const r = spawnSync(process.execPath, [GATE, ...args], { encoding: 'utf8', timeout: 180000, env: { ...process.env, PYTHONUTF8: '1' } });
  return { codigo: r.status, saida: `${r.stdout || ''}${r.stderr || ''}` };
}

const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);

teste('clone igual à original: PASSA e grava lado a lado e diff em tamanho real', () => {
  const d = tmp();
  fs.writeFileSync(path.join(d, 'original.html'), pagina());
  fs.writeFileSync(path.join(d, 'clone.html'), pagina());
  const r = rodar(['--original', pathToFileURL(path.join(d, 'original.html')).href, '--url', pathToFileURL(path.join(d, 'clone.html')).href, '--saida', path.join(d, 'saida')]);
  assert.equal(r.codigo, 0, r.saida);
  assert.match(r.saida, /RESULTADO: PASSA/);
  assert.match(r.saida, /1440 px: altura \d+ contra \d+ px; 0% dos pixels diferentes/);
  for (const f of ['lado-1440.png', 'diff-1440.png', 'lado-390.png', 'original-390.png', 'clone-390.png', 'laudo.json']) assert.ok(fs.existsSync(path.join(d, 'saida', f)), f);
  const png = fs.readFileSync(path.join(d, 'saida', 'lado-1440.png'));
  assert.equal(png.readUInt32BE(16), 1440 * 2 + 24, 'o lado a lado sai sem redução: 1440 + 24 + 1440 de largura');
});

teste('herói 15 px mais baixo e título com outra fonte: REPROVA, com a caixa, a fonte e os pixels', () => {
  const d = tmp();
  fs.writeFileSync(path.join(d, 'original.html'), pagina({ heroi: 323 }));
  fs.writeFileSync(path.join(d, 'clone.html'), pagina({ heroi: 308, h1: '44px' }));
  const r = rodar(['--original', pathToFileURL(path.join(d, 'original.html')).href, '--url', pathToFileURL(path.join(d, 'clone.html')).href, '--saida', path.join(d, 'saida')]);
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /altura da página/);
  assert.match(r.saida, /DIFERE\s+h1 "Título do herói"[^\n]*fonte de 40px contra 44px/);
  assert.match(r.saida, /DIFERE\s+section[^\n]*caixa[^\n]*altura 323 contra 308/);
  assert.match(r.saida, /PIXELS\s+x \d+ y \d+/);
});

teste('original que não abre: ERRO DE FERRAMENTA, saída 3, sem culpar o clone', () => {
  const d = tmp();
  fs.writeFileSync(path.join(d, 'clone.html'), pagina());
  const r = rodar(['--original', 'http://127.0.0.1:9/', '--url', pathToFileURL(path.join(d, 'clone.html')).href, '--saida', path.join(d, 'saida')]);
  assert.equal(r.codigo, 3, r.saida);
  assert.match(r.saida, /ERRO DE FERRAMENTA/);
  assert.doesNotMatch(r.saida, /REPROVA|\n\s+at /);
});

teste('sem --original, a URL vem de original/identidade.json do projeto', () => {
  const d = tmp();
  fs.mkdirSync(path.join(d, 'original'));
  fs.writeFileSync(path.join(d, 'original.html'), pagina({ cor: '#654321' }));
  fs.writeFileSync(path.join(d, 'clone.html'), pagina());
  fs.writeFileSync(path.join(d, 'original', 'identidade.json'), JSON.stringify({ url: pathToFileURL(path.join(d, 'original.html')).href }));
  const r = rodar(['--projeto', d, '--url', pathToFileURL(path.join(d, 'clone.html')).href, '--sem-registrar-uso']);
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /original: file:/);
  assert.match(r.saida, /DIFERE\s+header[^\n]*fundo rgb\(101, 67, 33\) contra rgb\(18, 52, 86\)/);
  assert.ok(fs.existsSync(path.join(d, 'gates', 'fidelidade', 'laudo.json')));
});

(async () => {
  let falhas = 0;
  for (const [nome, fn] of testes) {
    try { await fn(); console.log(`ok   ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome}\n  ${String(e && e.stack || e).split('\n').slice(0, 8).join('\n  ')}`); }
  }
  console.log(`\n${testes.length - falhas} de ${testes.length} testes passaram.`);
  process.exit(falhas ? 1 : 0);
})();
