/**
 * 3.7.0, item 2: o gate de movimento só onde importa (teste de aluno da 3.6.2: 5 rodadas completas com ele, cerca de 150 s cada).
 *
 * Ele roda na primeira rodada completa e na rodada final. Nas rodadas completas do meio, `--sem-movimento` o pula quando a
 * animação não mudou: o HTML sem o texto, o CSS e o JS da dist iguais aos da última vez em que ele PASSOU. Mudou a animação,
 * ele roda mesmo com a flag. A rodada pulada fica marcada na wave, e a rodada sem a flag (a final) roda o gate e limpa a marca.
 * Sem navegador: gates de mentira numa pasta temporária (`--scripts-dir`), que contam quantas vezes rodaram.
 */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const RODAR = path.join(__dirname, 'rodar-gates.mjs');
const tmp = (n) => fs.mkdtempSync(path.join(os.tmpdir(), `${n} çá `));

function rodar(args) {
  const r = spawnSync(process.execPath, [RODAR, ...args], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' }, windowsHide: true, timeout: 120000 });
  return { codigo: r.status, saida: `${r.stdout || ''}${r.stderr || ''}` };
}

const HTML = (texto, css = '.r{opacity:0;transition:opacity .8s}') => `<!doctype html><html><head><style>${css}</style></head><body>`
  + `<section class="r"><h1>${texto}</h1><p>Um parágrafo.</p></section><script>document.querySelectorAll('.r')</script></body></html>`;

async function cenario() {
  const { CATALOGO } = await import(pathToFileURL(RODAR).href);
  const falsos = tmp('falsos'); const marcas = tmp('marcas'); const proj = tmp('proj');
  for (const g of CATALOGO) {
    const arq = path.join(marcas, `${g.nome}.count`);
    const alvo = path.join(falsos, g.arquivo);
    if (g.arquivo.endsWith('.py')) fs.writeFileSync(alvo, `with open(${JSON.stringify(arq)}, 'a', encoding='utf-8') as f:\n    f.write('x')\nprint("ok ${g.nome}")\n`);
    else fs.writeFileSync(alvo, `import fs from 'node:fs';\nfs.appendFileSync(${JSON.stringify(arq)}, 'x');\nconsole.log("ok ${g.nome}");\n`);
  }
  fs.mkdirSync(path.join(proj, 'dist'), { recursive: true });
  fs.writeFileSync(path.join(proj, 'index.html'), '<html></html>');
  fs.writeFileSync(path.join(proj, 'PLANO.md'), 'Pixel pedido: nenhum\n');
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), HTML('Título'));
  const base = ['--projeto', proj, '--scripts-dir', falsos, '--sem-montar'];
  const vezes = () => { try { return fs.readFileSync(path.join(marcas, 'movimento.count'), 'utf8').length; } catch (_) { return 0; } };
  const wave = () => JSON.parse(fs.readFileSync(path.join(proj, '.wave-auditoria.json'), 'utf8'));
  return { proj, base, vezes, wave };
}

const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);

teste('rodada do meio com --sem-movimento e só texto mudado: o movimento não roda, fica marcado na wave e o relatório diz por quê', async () => {
  const { proj, base, vezes, wave } = await cenario();
  assert.equal(rodar(base).codigo, 0);
  assert.equal(vezes(), 1, 'a primeira rodada completa roda o movimento');
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), HTML('Outro título, com a copy corrigida'));
  fs.writeFileSync(path.join(proj, 'dist', 'foto.png'), 'imagem nova');
  const r = rodar([...base, '--sem-movimento']);
  assert.equal(r.codigo, 0, r.saida);
  assert.equal(vezes(), 1, 'a animação não mudou: o movimento não devia rodar');
  assert.match(r.saida, /PULADO\s+movimento[^\n]*--sem-movimento[^\n]*rodada 1/);
  assert.match(r.saida, /rodada final/);
  const lote = JSON.parse(fs.readFileSync(path.join(proj, 'gates', '_wave-r2.json'), 'utf8'));
  assert.ok(!lote.gates.some((g) => g.nome === 'movimento'), 'o movimento pulado não entra como execução');
  assert.equal(lote.pulados[0].nome, 'movimento');
  assert.ok(wave().gates.movimento.pulado_em, 'a wave marca o movimento pulado');
  assert.equal(wave().gates.texto.exit, 0, 'os outros gates se registram como numa rodada completa');
});

teste('--sem-movimento com o CSS mudado: o movimento roda mesmo assim e diz que a animação mudou', async () => {
  const { proj, base, vezes } = await cenario();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), HTML('Título', '.r{opacity:0;transition:opacity 1.2s}'));
  const r = rodar([...base, '--sem-movimento']);
  assert.equal(r.codigo, 0, r.saida);
  assert.equal(vezes(), 2);
  assert.match(r.saida, /movimento[^\n]*a animação mudou/);
});

teste('--sem-movimento com o JS mudado também roda o movimento', async () => {
  const { proj, base, vezes } = await cenario();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'dist', 'app.js'), 'new IntersectionObserver(() => {})');
  rodar([...base, '--sem-movimento']);
  assert.equal(vezes(), 2);
});

teste('--sem-movimento sem nenhum PASSA guardado do movimento: ele roda', async () => {
  const { base, vezes } = await cenario();
  rodar([...base, '--sem-movimento']);
  assert.equal(vezes(), 1);
});

teste('a rodada sem a flag (a final) roda o movimento depois do pulo e limpa a marca da wave', async () => {
  const { proj, base, vezes, wave } = await cenario();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), HTML('Copy nova'));
  rodar([...base, '--sem-movimento']);
  assert.equal(vezes(), 1);
  const r = rodar(base);
  assert.equal(r.codigo, 0, r.saida);
  assert.equal(vezes(), 2, 'a rodada final roda o movimento com a dist de agora');
  assert.ok(!wave().gates.movimento.pulado_em, 'a marca de pulado some quando ele roda');
});

teste('--sem-movimento numa rodada parcial é erro: a flag é para a rodada completa do meio', async () => {
  const { base } = await cenario();
  const r = rodar([...base, '--sem-movimento', '--so', 'texto']);
  assert.equal(r.codigo, 2, r.saida);
});

(async () => {
  let falhas = 0;
  for (const [nome, fn] of testes) {
    try { await fn(); console.log(`ok   ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome}\n  ${String(e && e.stack || e).split('\n').slice(0, 6).join('\n  ')}`); }
  }
  console.log(`\n${testes.length - falhas} de ${testes.length} testes passaram.`);
  process.exit(falhas ? 1 : 0);
})();
