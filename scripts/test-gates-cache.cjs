/**
 * Testes do `gates-cache.mjs` (cache de gate por conteúdo, corte 4 da auditoria de velocidade).
 *
 * Não precisa de navegador. O que fica provado:
 *  1. o hash de pasta olha o CONTEÚDO (a data não entra), muda com 1 byte, com arquivo novo e com nome trocado;
 *  2. cada parte da chave de um gate muda a chave: dist, projeto, argumentos, scripts, ambiente, o gate;
 *  3. qual gate lê o quê (dist, projeto, os dois) bate com o catálogo REAL do rodar-gates.mjs;
 *  4. o que os gates escrevem (gates/, auditoria/, wave) e a dist não entram no hash do projeto;
 *  5. teste e fixture não entram na versão dos scripts, gate e references entram;
 *  6. só PASSA é lido de volta; registro corrompido, de outro formato ou de outra chave vira "sem cache";
 *  7. mutante: uma chave que esquece uma parte é pega pela mesma verificação que aprova a chave de verdade.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const AQUI = __dirname;
const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);
const tmp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'cache çá '));
const escrever = (p, t) => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, t); };
const lib = () => import(pathToFileURL(path.join(AQUI, 'gates-cache.mjs')).href);
const rodarGates = () => import(pathToFileURL(path.join(AQUI, 'rodar-gates.mjs')).href);

// ---------------------------------------------------------------- 1. hash de pasta
teste('hash de pasta: mesmo conteúdo com data diferente dá o mesmo hash', async () => {
  const { hashPasta } = await lib();
  const d = tmp();
  escrever(path.join(d, 'index.html'), '<p>oi</p>');
  const antes = hashPasta(d);
  fs.utimesSync(path.join(d, 'index.html'), new Date(2001, 1, 1), new Date(2001, 1, 1));
  assert.equal(hashPasta(d), antes);
});

teste('hash de pasta: 1 byte, arquivo novo e nome trocado mudam o hash', async () => {
  const { hashPasta } = await lib();
  const d = tmp();
  escrever(path.join(d, 'a.css'), 'b{}');
  const base = hashPasta(d);
  escrever(path.join(d, 'a.css'), 'c{}');
  const umByte = hashPasta(d);
  assert.notEqual(umByte, base);
  escrever(path.join(d, 'novo.txt'), 'x');
  const novo = hashPasta(d);
  assert.notEqual(novo, umByte);
  fs.renameSync(path.join(d, 'novo.txt'), path.join(d, 'outro.txt'));
  assert.notEqual(hashPasta(d), novo);
});

teste('hash de pasta: a ordem de criação não importa e "ab"+"c" não vira "a"+"bc"', async () => {
  const { hashPasta } = await lib();
  const a = tmp(); const b = tmp(); const c = tmp();
  escrever(path.join(a, '1'), 'um'); escrever(path.join(a, '2'), 'dois');
  escrever(path.join(b, '2'), 'dois'); escrever(path.join(b, '1'), 'um');
  assert.equal(hashPasta(a), hashPasta(b));
  escrever(path.join(c, 'x'), 'ab'); escrever(path.join(c, 'y'), 'c');
  const d = tmp();
  escrever(path.join(d, 'x'), 'a'); escrever(path.join(d, 'y'), 'bc');
  assert.notEqual(hashPasta(c), hashPasta(d));
});

teste('hash de pasta: arquivo grande (mais de 1 bloco de leitura) entra inteiro, até o último byte', async () => {
  const { hashPasta } = await lib();
  const d = tmp();
  const grande = Buffer.alloc(3 * 1024 * 1024 + 17, 7);
  fs.writeFileSync(path.join(d, 'video.webm'), grande);
  const antes = hashPasta(d);
  grande[grande.length - 1] = 8;
  fs.writeFileSync(path.join(d, 'video.webm'), grande);
  assert.notEqual(hashPasta(d), antes, 'a mudança no último byte passou despercebida');
});

// ---------------------------------------------------------------- 2. a chave
const PARTES = { gate: 'texto', arquivo: 'gate-texto.mjs', argumentos: '["--url","@@URL@@"]', scripts: 's1', ambiente: 'darwin node22 playwright1.5', dist: 'd1', projeto: 'p1' };

teste('chave: igual para as mesmas partes, diferente quando QUALQUER parte muda', async () => {
  const { chaveDoGate } = await lib();
  const base = chaveDoGate(PARTES);
  assert.equal(chaveDoGate({ ...PARTES }), base);
  for (const k of Object.keys(PARTES)) assert.notEqual(chaveDoGate({ ...PARTES, [k]: PARTES[k] + 'x' }), base, `mudar "${k}" não mudou a chave`);
  const { projeto, ...semProjeto } = PARTES;
  assert.notEqual(chaveDoGate(semProjeto), base, 'gate que passa a ler o projeto tem outra chave');
});

/** Devolve as partes que NÃO mexem na chave: com uma função de chave certa, a lista é vazia. */
function partesIgnoradas(chaveFn, partes) {
  const base = chaveFn(partes);
  return Object.keys(partes).filter((k) => chaveFn({ ...partes, [k]: partes[k] + 'x' }) === base);
}

teste('chave: a verificação aprova a chave de verdade e PEGA um mutante que esquece uma parte (dist, projeto, argumentos, scripts)', async () => {
  const { chaveDoGate } = await lib();
  assert.deepEqual(partesIgnoradas(chaveDoGate, PARTES), []);
  for (const esquecida of ['dist', 'projeto', 'argumentos', 'scripts', 'ambiente']) {
    const mutante = (p) => chaveDoGate({ ...p, [esquecida]: 'fixo' });
    assert.deepEqual(partesIgnoradas(mutante, PARTES), [esquecida], `o mutante que ignora "${esquecida}" não foi pego`);
  }
});

// ---------------------------------------------------------------- 3. quem lê o quê, no catálogo real
teste('entradas: cada gate do catálogo real declara se lê a dist, o projeto, ou os dois', async () => {
  const { entradasDoGate } = await lib();
  const { CATALOGO } = await rodarGates();
  const esperado = {
    movimento: [true, false], responsivo: [true, false], oclusao: [true, false], simetria: [true, false], texto: [true, false], ritmo: [true, false],
    composicao: [true, true], imagens: [true, true],
    'sem-kicker': [false, true], 'classes-mortas': [false, true], verdade: [false, true], plano: [false, true], referencias: [false, true], animacao: [false, true],
    publicacao: [true, false], rastreamento: [true, true], seo: [true, true],   // 3.8.0: lê a dist e a linha Domínio final do PLANO.md
    video: [true, false], sobreposicao: [true, false],
  };
  assert.deepEqual(Object.keys(esperado).sort(), CATALOGO.map((g) => g.nome).sort(), 'a tabela do teste não cobre todos os gates');
  for (const g of CATALOGO) {
    const e = entradasDoGate(g, { publico: 'pub', fixo: '.a', contra: '.b' });
    assert.deepEqual([e.leDist, e.leProjeto], esperado[g.nome], `${g.nome}: [lê a dist, lê o projeto]`);
  }
});

teste('entradas: o caminho real, a porta e a pasta do projeto NÃO entram nos argumentos da chave', async () => {
  const { entradasDoGate, MARCADORES } = await lib();
  const { CATALOGO } = await rodarGates();
  for (const g of CATALOGO) {
    const { args } = entradasDoGate(g, { publico: 'pub', fixo: '.a', contra: '.b' });
    const junto = args.join(' ');
    assert.ok(!/127\.0\.0\.1|localhost|[\/\\](tmp|Users|home)[\/\\]/.test(junto), `${g.nome}: caminho ou porta de verdade nos argumentos: ${junto}`);
    if (g.url) assert.ok(junto.includes(MARCADORES.url), `${g.nome}: a URL devia ser o marcador`);
  }
});

teste('entradas: --produto-fisico e --trafego-real entram na chave (são outra pergunta)', async () => {
  const { entradasDoGate } = await lib();
  const { CATALOGO } = await rodarGates();
  const comp = CATALOGO.find((g) => g.nome === 'composicao');
  const img = CATALOGO.find((g) => g.nome === 'imagens');
  assert.notDeepEqual(entradasDoGate(comp, {}).args, entradasDoGate(comp, { produtoFisico: true }).args);
  assert.notDeepEqual(entradasDoGate(img, {}).args, entradasDoGate(img, { trafegoReal: true }).args);
});

// ---------------------------------------------------------------- 4. o que entra no hash do projeto
teste('projeto: gates/, auditoria/, dist/ e o registro da wave ficam de fora; referencias/, prova/ e index.html entram', async () => {
  const { hashPasta, ignorarNoProjeto } = await lib();
  const p = tmp();
  escrever(path.join(p, 'index.html'), 'a');
  escrever(path.join(p, 'referencias', '01-dobra.png'), 'png');
  escrever(path.join(p, 'prova', 'anim', 'x.png'), 'png');
  const base = hashPasta(p, ignorarNoProjeto);
  escrever(path.join(p, 'gates', 'texto-r1.txt'), 'saída');
  escrever(path.join(p, 'auditoria', 'pacote.json'), '{}');
  escrever(path.join(p, 'dist', 'index.html'), 'dist');
  escrever(path.join(p, '.wave-auditoria.json'), '{}');
  escrever(path.join(p, 'node_modules', 'x', 'y.js'), 'z');
  assert.equal(hashPasta(p, ignorarNoProjeto), base, 'saída de gate ou dist invalidou o projeto');
  for (const rel of [['index.html'], ['referencias', '01-dobra.png'], ['prova', 'anim', 'x.png']]) {
    const alvo = path.join(p, ...rel);
    const antes = fs.readFileSync(alvo);
    fs.writeFileSync(alvo, antes + 'mudou');
    assert.notEqual(hashPasta(p, ignorarNoProjeto), base, `${rel.join('/')} devia invalidar o projeto`);
    fs.writeFileSync(alvo, antes);
  }
  assert.equal(hashPasta(p, ignorarNoProjeto), base);
});

teste('projeto: pasta chamada "gates" mais fundo na árvore não é a dos gates e entra', async () => {
  const { hashPasta, ignorarNoProjeto } = await lib();
  const p = tmp();
  escrever(path.join(p, 'index.html'), 'a');
  const base = hashPasta(p, ignorarNoProjeto);
  escrever(path.join(p, 'conteudo', 'gates', 'x.txt'), 'importa');
  assert.notEqual(hashPasta(p, ignorarNoProjeto), base);
});

// ---------------------------------------------------------------- 5. versão dos scripts
teste('scripts: gate e references entram na versão; teste e fixtures não', async () => {
  const { versaoDosScripts } = await lib();
  const s = tmp(); const r = tmp();
  escrever(path.join(s, 'gate-a.mjs'), 'v1');
  escrever(path.join(s, 'test-a.cjs'), 't1');
  escrever(path.join(s, 'a.test.mjs'), 't1');
  escrever(path.join(s, 'fixtures', 'f.json'), 'f1');
  escrever(path.join(r, 'receitas.md'), 'r1');
  const pastas = [['gates', s], ['references', r]];
  const base = versaoDosScripts(pastas);
  escrever(path.join(s, 'test-a.cjs'), 't2'); escrever(path.join(s, 'a.test.mjs'), 't2'); escrever(path.join(s, 'fixtures', 'f.json'), 'f2');
  assert.equal(versaoDosScripts(pastas), base, 'mexer em teste ou fixture invalidou o gate');
  escrever(path.join(s, 'gate-a.mjs'), 'v2');
  const v2 = versaoDosScripts(pastas);
  assert.notEqual(v2, base);
  escrever(path.join(r, 'receitas.md'), 'r2');
  assert.notEqual(versaoDosScripts(pastas), v2, 'o gate-plano lê references/: mexer lá tem que invalidar');
});

teste('scripts: um arquivo novo na pasta dos gates também muda a versão', async () => {
  const { versaoDosScripts } = await lib();
  const s = tmp();
  escrever(path.join(s, 'gate-a.mjs'), 'v1');
  const base = versaoDosScripts([['gates', s]]);
  escrever(path.join(s, 'gates-visuais-lib.cjs'), 'lib');
  assert.notEqual(versaoDosScripts([['gates', s]]), base);
});

// ---------------------------------------------------------------- 6. armazenamento
const reg = (extra = {}) => ({ chave: 'k1', partes: { gate: 'texto' }, segundos: 7.3, rodada: 2, laudo: 'ok texto\n', ...extra });

teste('armazenamento: grava e lê de volta; só acerta com a MESMA chave', async () => {
  const { gravarCache, lerCache, acerto } = await lib();
  const g = tmp();
  gravarCache(g, 'texto', reg());
  assert.equal(lerCache(g, 'texto').laudo, 'ok texto\n');
  assert.ok(acerto(g, 'texto', 'k1'));
  assert.equal(acerto(g, 'texto', 'k2'), null, 'chave diferente não pode acertar');
  assert.equal(acerto(g, 'ritmo', 'k1'), null, 'outro gate não pode acertar com a chave deste');
  assert.equal(acerto(tmp(), 'texto', 'k1'), null, 'sem pasta de cache');
});

teste('armazenamento: registro corrompido, de outro formato, de outro gate ou com saída diferente de 0 vira "sem cache"', async () => {
  const { gravarCache, lerCache, pastaDoCache } = await lib();
  const g = tmp();
  gravarCache(g, 'texto', reg());
  const arq = path.join(pastaDoCache(g), 'texto.json');
  const bom = JSON.parse(fs.readFileSync(arq, 'utf8'));
  const casos = [
    ['json quebrado', '{ nope'],
    ['formato de outra versão', JSON.stringify({ ...bom, versao: 999 })],
    ['de outro gate', JSON.stringify({ ...bom, nome: 'ritmo' })],
    ['saída 1 (reprovação nunca vale)', JSON.stringify({ ...bom, codigo: 1 })],
    ['sem laudo', JSON.stringify({ ...bom, laudo: undefined })],
    ['vazio', ''],
  ];
  for (const [rotulo, conteudo] of casos) {
    fs.writeFileSync(arq, conteudo);
    assert.equal(lerCache(g, 'texto'), null, rotulo);
  }
});

teste('armazenamento: a gravação não deixa arquivo temporário para trás', async () => {
  const { gravarCache, pastaDoCache } = await lib();
  const g = tmp();
  gravarCache(g, 'texto', reg());
  gravarCache(g, 'texto', reg({ chave: 'k2' }));
  assert.deepEqual(fs.readdirSync(pastaDoCache(g)), ['texto.json']);
});

// ---------------------------------------------------------------- 7. memória e ambiente
teste('memória: o hash é calculado uma vez por memória, mas sempre do disco (memória nova vê a mudança)', async () => {
  const { criarMemo } = await lib();
  const d = tmp();
  escrever(path.join(d, 'index.html'), 'a');
  const m1 = criarMemo();
  const h1 = m1.dist(d);
  escrever(path.join(d, 'index.html'), 'b');
  assert.equal(m1.dist(d), h1, 'dentro do mesmo comando o hash é calculado uma vez');
  assert.notEqual(criarMemo().dist(d), h1, 'um comando novo tem que reler o disco');
});

teste('ambiente: leva o sistema, o Node e o Playwright', async () => {
  const { ambiente } = await lib();
  const a = ambiente();
  assert.ok(a.includes(process.platform));
  assert.ok(a.includes(`node${process.versions.node.split('.')[0]}`));
  assert.match(a, /playwright/);
});

(async () => {
  let falhas = 0;
  for (const [nome, fn] of testes) {
    try { await fn(); console.log(`ok   ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome}\n  ${String(e && e.stack || e).split('\n').slice(0, 6).join('\n  ')}`); }
  }
  console.log(`\n${testes.length - falhas} de ${testes.length} testes passaram.`);
  process.exit(falhas ? 1 : 0);
})();
