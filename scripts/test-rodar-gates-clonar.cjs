/**
 * 3.7.0, teste de aluno do CLONAR na 3.6.3 (clone de pocketbase.io com 0,054% de pixels diferentes em 1440): a rodada de
 * gates reprovou em 8 de 15 e não havia rota de saída. `rodar-gates.mjs --caminho clonar` tem o conjunto do clone:
 *   - fidelidade, oclusão, classes mortas, publicação e uso de ferramentas reprovam;
 *   - verdade, rastreamento, plano e referências NÃO rodam (pedem briefing, PLANO, pixel e 6 referências);
 *   - movimento, responsivo, texto e imagens (e o resto de gosto) viram AVISO "ressalva por fidelidade": a saída é 0;
 *   - a wave recebe o exit real, e o `wave.py --caminho clonar checar` não bloqueia pelos avisos.
 * O CRIAR não muda: sem a flag, o conjunto é o de sempre.
 * Sem navegador: gates de mentira numa pasta temporária (`--scripts-dir`), que marcam quando rodaram.
 */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const AQUI = __dirname;
const RODAR = path.join(AQUI, 'rodar-gates.mjs');
const tmp = (n) => fs.mkdtempSync(path.join(os.tmpdir(), `${n} çá `));

function rodar(args) {
  const r = spawnSync(process.execPath, [RODAR, ...args], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' }, windowsHide: true, timeout: 120000 });
  return { codigo: r.status, saida: `${r.stdout || ''}${r.stderr || ''}` };
}

const VERMELHOS_DO_ALUNO = ['movimento', 'responsivo', 'imagens', 'texto', 'verdade', 'rastreamento', 'plano', 'referencias'];

async function cenario({ vermelhos = VERMELHOS_DO_ALUNO } = {}) {
  const mod = await import(pathToFileURL(RODAR).href);
  const todos = [...mod.CATALOGO, ...(mod.CATALOGO_CLONAR || [])];
  const falsos = tmp('falsos'); const marcas = tmp('marcas'); const proj = tmp('proj');
  for (const g of todos) {
    const arq = path.join(marcas, `${g.nome}.rodou`);
    const sai = vermelhos.includes(g.nome) ? 1 : 0;
    const alvo = path.join(falsos, g.arquivo);
    if (g.arquivo.endsWith('.py')) fs.writeFileSync(alvo, `import sys\nopen(${JSON.stringify(arq)}, 'a', encoding='utf-8').write('x')\nprint("${sai ? 'FALHA' : 'ok'} ${g.nome}")\nsys.exit(${sai})\n`);
    else fs.writeFileSync(alvo, `import fs from 'node:fs';\nfs.appendFileSync(${JSON.stringify(arq)}, 'x');\nconsole.log("${sai ? 'FALHA' : 'ok'} ${g.nome}");\nprocess.exit(${sai});\n`);
  }
  fs.mkdirSync(path.join(proj, 'dist'), { recursive: true });
  fs.writeFileSync(path.join(proj, 'index.html'), '<html></html>');
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), '<!doctype html><html><body><h1>Clone</h1></body></html>');
  const rodou = (n) => fs.existsSync(path.join(marcas, `${n}.rodou`));
  const wave = () => JSON.parse(fs.readFileSync(path.join(proj, '.wave-auditoria.json'), 'utf8'));
  return { mod, proj, rodou, wave, base: ['--projeto', proj, '--scripts-dir', falsos, '--sem-montar', '--original', 'http://127.0.0.1:9/'] };
}

const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);

teste('--caminho clonar com os 8 vermelhos do aluno: saída 0, os 4 de fora não rodam e os de gosto viram AVISO', async () => {
  const { proj, rodou, base } = await cenario();
  const r = rodar([...base, '--caminho', 'clonar']);
  assert.equal(r.codigo, 0, r.saida);
  for (const n of ['verdade', 'rastreamento', 'plano', 'referencias']) assert.ok(!rodou(n), `${n} não roda no clone`);
  for (const n of ['fidelidade', 'oclusao', 'classes-mortas', 'publicacao', 'uso-ferramentas', 'movimento', 'responsivo', 'texto', 'imagens']) assert.ok(rodou(n), `${n} roda no clone`);
  for (const n of ['movimento', 'responsivo', 'texto', 'imagens']) assert.match(r.saida, new RegExp(`AVISO\\s+${n}[^\\n]*ressalva por fidelidade`), n);
  assert.doesNotMatch(r.saida, /RESULTADO: REPROVA/);
  assert.match(r.saida, /RESULTADO: PASSA/);
  const ch = spawnSync(process.execPath, [path.join(AQUI, 'py.mjs'), path.join(AQUI, 'wave.py'), '--projeto', proj, '--caminho', 'clonar', 'checar'], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' } });
  const out = `${ch.stdout}${ch.stderr}`;
  assert.doesNotMatch(out, /gate\(s\) vermelho\(s\)/, out);
  assert.match(out, /RESSALVA/, out);
});

teste('no clone, fidelidade, oclusão, classes mortas, publicação e uso de ferramentas vermelhos reprovam', async () => {
  for (const n of ['fidelidade', 'oclusao', 'classes-mortas', 'publicacao', 'uso-ferramentas']) {
    const { base } = await cenario({ vermelhos: [...VERMELHOS_DO_ALUNO, n] });
    const r = rodar([...base, '--caminho', 'clonar']);
    assert.equal(r.codigo, 1, `${n}: ${r.saida}`);
    assert.match(r.saida, new RegExp(`REPROVA\\s+${n}`), n);
  }
});

teste('a wave do clone recebe o exit real de cada gate que rodou, e nenhum dos 4 de fora', async () => {
  const { base, wave } = await cenario();
  rodar([...base, '--caminho', 'clonar']);
  const g = wave().gates;
  assert.equal(g.movimento.exit, 1);
  assert.match(g.movimento.detalhe, /ressalva por fidelidade/);
  assert.equal(g.fidelidade.exit, 0);
  assert.equal(g['uso-ferramentas'].exit, 0);
  for (const n of ['verdade', 'rastreamento', 'plano', 'referencias']) assert.ok(!(n in g), n);
});

teste('--reprovados no clone não roda de novo os avisos por fidelidade', async () => {
  const { base, rodou } = await cenario({ vermelhos: [...VERMELHOS_DO_ALUNO, 'oclusao'] });
  rodar([...base, '--caminho', 'clonar']);
  const r = rodar([...base, '--caminho', 'clonar', '--reprovados']);
  assert.match(r.saida, /oclusao/);
  assert.doesNotMatch(r.saida, /AVISO\s+movimento/, r.saida);
  assert.ok(rodou('oclusao'));
});

teste('o CRIAR não muda: sem --caminho, os 8 vermelhos reprovam e os gates do clone não rodam', async () => {
  const { base, rodou } = await cenario();
  const r = rodar(base.filter((a, i) => a !== '--original' && base[i - 1] !== '--original'));
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /RESULTADO: REPROVA em 8 de 15/);
  assert.ok(!rodou('fidelidade'));
  assert.ok(!rodou('uso-ferramentas'));
});

teste('no clone, o gate de classes mortas recebe --clone (utilitário do Tailwind com classe da original); no CRIAR, não', async () => {
  const { base, proj } = await cenario();
  const falsos = base[base.indexOf('--scripts-dir') + 1];
  const saida = path.join(proj, 'argv.txt');
  fs.writeFileSync(path.join(falsos, 'gate-classes-mortas.py'), `import sys\nopen(${JSON.stringify(saida)}, 'a', encoding='utf-8').write(' '.join(sys.argv[1:]) + '\\n')\nprint('ok')\n`);
  rodar([...base, '--caminho', 'clonar', '--so', 'classes-mortas']);
  rodar(base.filter((a, i) => a !== '--original' && base[i - 1] !== '--original').concat(['--so', 'classes-mortas', '--sem-cache']));
  const [clone, criar] = fs.readFileSync(saida, 'utf8').trim().split('\n');
  assert.match(clone, /--clone/);
  assert.doesNotMatch(criar, /--clone/);
});

teste('os grupos do clone no rodar-gates batem com os do wave.py', async () => {
  const { mod } = await cenario();
  const codigo = `import importlib.util,json;s=importlib.util.spec_from_file_location('w',${JSON.stringify(path.join(AQUI, 'wave.py'))});w=importlib.util.module_from_spec(s);s.loader.exec_module(w);print(json.dumps({'fora':sorted(w.FORA_DO_CLONE),'ressalva':sorted(w.RESSALVA_POR_FIDELIDADE)}))`;
  const arq = path.join(tmp('grupos'), 'grupos.py');
  fs.writeFileSync(arq, codigo.split(';').join('\n'), 'utf8');
  const r = spawnSync(process.execPath, [path.join(AQUI, 'py.mjs'), arq], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' } });
  const w = JSON.parse(r.stdout.trim().split('\n').pop());
  assert.deepEqual([...mod.FORA_DO_CLONE].sort(), w.fora);
  assert.deepEqual([...mod.RESSALVA_POR_FIDELIDADE].sort(), w.ressalva);
});

(async () => {
  let falhas = 0;
  for (const [nome, fn] of testes) {
    try { await fn(); console.log(`ok   ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome}\n  ${String(e && e.stack || e).split('\n').slice(0, 6).join('\n  ')}`); }
  }
  console.log(`\n${testes.length - falhas} de ${testes.length} testes passaram.`);
  process.exit(falhas ? 1 : 0);
})();
