/**
 * Testes do `rodar-gates.mjs` (comando único dos gates mecânicos da etapa f).
 *
 * Não precisa de navegador: os gates de verdade são trocados por gates de mentira numa pasta
 * temporária (opção `--scripts-dir`), que gravam marcas para provar o que o comando fez.
 * Precisa de Node e Python (o lançador py.mjs), como o resto da suíte portátil.
 *
 * O que fica provado:
 *  1. a lista de gates do comando bate com a documentação (`criar.md`, etapa f), nos dois sentidos;
 *  2. um gate que reprova faz o conjunto reprovar (saída 1), com a mensagem inteira no relatório;
 *  3. os gates rodam EM PARALELO de verdade (barreira: cada um espera o outro começar) e o teto
 *     de concorrência é respeitado;
 *  4. `--so`, `--reprovados` e a numeração das rodadas;
 *  5. caminho com acento e espaço, comando impresso com aspas, tempo máximo por gate.
 */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const AQUI = __dirname;
const RODAR = path.join(AQUI, 'rodar-gates.mjs');
const CRIAR_MD = path.join(AQUI, '..', 'references', 'caminhos', 'criar.md');
const PASTAS = [];

function pastaTemp(nome = 'rg') {
  const p = fs.mkdtempSync(path.join(os.tmpdir(), `${nome} çá `));
  PASTAS.push(p);
  return p;
}

function limpar() {
  // sem rm: a pasta temporária do sistema se limpa sozinha; aqui só esquecemos os caminhos
  PASTAS.length = 0;
}

async function catalogo() {
  const mod = await import(pathToFileURL(RODAR).href);
  return mod;
}

/** Gates de mentira com os MESMOS nomes de arquivo do catálogo. `corpo(nome)` devolve o código. */
function montarFalsos(dir, corpoPorGate = {}) {
  fs.mkdirSync(dir, { recursive: true });
  const ext = (a) => (a.endsWith('.py') ? 'py' : 'mjs');
  return (cat) => {
    for (const g of cat) {
      const alvo = path.join(dir, g.arquivo);
      const corpo = corpoPorGate[g.nome];
      if (ext(g.arquivo) === 'py') {
        fs.writeFileSync(alvo, corpo && corpo.py ? corpo.py : 'import sys\nprint("ok %s")\nsys.exit(0)\n'.replace('%s', g.nome), 'utf8');
      } else {
        fs.writeFileSync(alvo, corpo && corpo.mjs ? corpo.mjs : `console.log("ok ${g.nome}");\n`, 'utf8');
      }
    }
  };
}

function rodar(args, extraEnv = {}) {
  const r = spawnSync(process.execPath, [RODAR, ...args], {
    encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1', ...extraEnv }, windowsHide: true, timeout: 120000,
  });
  return { codigo: r.status, saida: `${r.stdout || ''}${r.stderr || ''}` };
}

function projetoFalso() {
  const proj = pastaTemp('projeto');
  fs.mkdirSync(path.join(proj, 'dist'), { recursive: true });
  fs.writeFileSync(path.join(proj, 'index.html'), '<html></html>', 'utf8');
  fs.writeFileSync(path.join(proj, 'PLANO.md'), 'Pixel pedido: nenhum\n', 'utf8');
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), '<html></html>', 'utf8');
  return proj;
}

const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);

// ---------------------------------------------------------------- 1. lista bate com a documentação
function comandosDaEtapaF() {
  const md = fs.readFileSync(CRIAR_MD, 'utf8');
  const ini = md.indexOf('## f. Gates mecânicos');
  assert.ok(ini >= 0, 'criar.md perdeu o título "## f. Gates mecânicos"');
  const resto = md.slice(ini + 5);
  const fim = resto.search(/\n## [a-z]\. /);
  const trecho = fim >= 0 ? resto.slice(0, fim) : resto;
  const achados = new Set();
  const re = /(?:scripts\/|py\.mjs )((?:gate-[a-z0-9-]+|sobreposicao)\.(?:py|mjs))/g;
  let m;
  while ((m = re.exec(trecho))) achados.add(m[1]);
  return { trecho, achados };
}

teste('a lista de gates do comando bate com a etapa f do criar.md (documentação para o comando)', async () => {
  const { CATALOGO } = await catalogo();
  const { achados } = comandosDaEtapaF();
  const doComando = new Set(CATALOGO.map((g) => g.arquivo));
  const faltamNoComando = [...achados].filter((a) => !doComando.has(a));
  assert.deepEqual(faltamNoComando, [], `gate no criar.md que o rodar-gates.mjs esqueceu: ${faltamNoComando.join(', ')}`);
});

teste('a lista de gates do comando bate com a etapa f do criar.md (comando para a documentação)', async () => {
  const { CATALOGO } = await catalogo();
  const { achados } = comandosDaEtapaF();
  const sobrando = CATALOGO.map((g) => g.arquivo).filter((a) => !achados.has(a));
  assert.deepEqual(sobrando, [], `gate no rodar-gates.mjs que o criar.md (etapa f) não documenta: ${sobrando.join(', ')}`);
});

teste('todo gate do comando existe na pasta scripts e tem nome da wave', async () => {
  const { CATALOGO } = await catalogo();
  const { trecho } = comandosDaEtapaF();
  const linhaNomes = (trecho.match(/\(nomes: ([^)]+)\)/) || [])[1] || '';
  const nomesWave = linhaNomes.split(',').map((s) => s.replace(/`/g, '').trim());
  for (const g of CATALOGO) {
    assert.ok(fs.existsSync(path.join(AQUI, g.arquivo)), `${g.arquivo} não existe`);
    // video e sobreposicao não têm nome na wave (o criar.md os cita fora da lista de nomes)
    if (!['video', 'sobreposicao'].includes(g.nome)) assert.ok(nomesWave.includes(g.nome), `"${g.nome}" não está na lista de nomes da wave do criar.md`);
  }
  const nomes = CATALOGO.map((g) => g.nome);
  assert.equal(new Set(nomes).size, nomes.length, 'nome de gate repetido no catálogo');
});

teste('os 15 gates do fluxo antigo (gates-todos) continuam todos no conjunto padrão', async () => {
  const { CATALOGO } = await catalogo();
  const padrao = CATALOGO.filter((g) => !g.opcional).map((g) => g.nome).sort();
  const antigos = ['sem-kicker', 'classes-mortas', 'verdade', 'publicacao', 'rastreamento', 'plano', 'referencias',
    'responsivo', 'oclusao', 'simetria', 'texto', 'composicao', 'ritmo', 'imagens', 'movimento'].sort();
  assert.deepEqual(padrao, antigos);
});

// ---------------------------------------------------------------- 2. reprovar um reprova o conjunto
teste('um gate que reprova faz o conjunto reprovar, com a mensagem inteira no relatório', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos, {
    simetria: { mjs: 'console.log("linha 1 da falha");\nconsole.log("linha 2 da falha com acento: coluna ç");\nprocess.exit(1);\n' },
  })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar']);
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /REPROVA\s+simetria/);
  assert.match(r.saida, /linha 1 da falha/);
  assert.match(r.saida, /linha 2 da falha com acento: coluna ç/);
  assert.match(r.saida, /PASSA\s+sem-kicker/);
  assert.ok(fs.existsSync(path.join(proj, 'gates', 'simetria-r1.txt')), 'saída do gate não gravada em gates/simetria-r1.txt');
  const exec = fs.readFileSync(path.join(proj, 'gates', '_execucoes.txt'), 'utf8');
  assert.match(exec, /^1 simetria 1$/m);
  assert.match(exec, /^1 texto 0$/m);
});

teste('todos passando: saída 0 e um relatório com tempo por gate e total', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos)(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar']);
  assert.equal(r.codigo, 0, r.saida);
  assert.match(r.saida, /Total/);
  assert.match(r.saida, /PASSA\s+movimento\s+\d/);
  assert.doesNotMatch(r.saida, /REPROVA\s/);
});

teste('gate que quebra (script ausente) reprova em vez de sumir', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos)(CATALOGO);
  fs.renameSync(path.join(falsos, 'gate-ritmo.mjs'), path.join(falsos, 'gate-ritmo.mjs.bak'));
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar']);
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /REPROVA\s+ritmo/);
});

teste('gate que passa do tempo máximo é interrompido e reprova (saída 124)', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos, { texto: { mjs: 'setTimeout(() => {}, 60000);\n' } })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--tempo-max', '2']);
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /REPROVA\s+texto/);
  assert.match(r.saida, /tempo máximo/i);
});

teste('aviso de um gate que passou aparece no relatório, mas a contagem "(8 aviso(s)" não vira aviso', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos, {
    simetria: { mjs: 'console.log("desktop ok (8 aviso(s) de assimetria declarada)");\nconsole.log("desktop: AVISO (data-assimetrico): coluna curta");\n' },
  })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--so', 'simetria']);
  assert.equal(r.codigo, 0, r.saida);
  assert.match(r.saida, /\[simetria\] desktop: AVISO \(data-assimetrico\): coluna curta/);
  assert.doesNotMatch(r.saida, /\[simetria\] desktop ok \(8 aviso/);
});

teste('cada gate recebe os MESMOS argumentos que o criar.md manda (nenhum gate muda de comportamento)', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const marcas = pastaTemp('marcas');
  const corpos = {};
  for (const g of CATALOGO) {
    const destino = path.join(marcas, `${g.nome}.json`);
    corpos[g.nome] = g.arquivo.endsWith('.py')
      ? { py: `import json, sys\nopen(${JSON.stringify(destino)}, 'w', encoding='utf-8').write(json.dumps(sys.argv[1:]))\n` }
      : { mjs: `import fs from 'node:fs';\nfs.writeFileSync(${JSON.stringify(destino)}, JSON.stringify(process.argv.slice(2)));\n` };
  }
  montarFalsos(falsos, corpos)(CATALOGO);
  const proj = projetoFalso();
  const URL = 'http://127.0.0.1:1/';
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', URL, '--sem-montar', '--com', 'animacao,video,sobreposicao',
    '--publico', 'pub', '--fixo', '.fixo', '--contra', '.largo', '--produto-fisico', '--trafego-real']);
  assert.equal(r.codigo, 0, r.saida);
  const lido = (n) => JSON.parse(fs.readFileSync(path.join(marcas, `${n}.json`), 'utf8'));
  const dist = path.join(proj, 'dist');
  const esperado = {
    'sem-kicker': [path.join(proj, 'index.html')],
    'classes-mortas': ['--projeto', proj],
    responsivo: ['--url', URL], oclusao: ['--url', URL], simetria: ['--url', URL], texto: ['--url', URL],
    composicao: ['--url', URL, '--projeto', proj, '--produto-fisico'],
    movimento: ['--url', URL],
    verdade: ['--projeto', proj],
    imagens: ['--projeto', proj, '--url', URL, '--trafego-real'],
    ritmo: ['--url', URL],
    animacao: ['--pasta', path.join(proj, 'prova', 'anim'), '--plano', path.join(proj, 'PLANO.md')],
    sobreposicao: ['--url', URL, '--fixo', '.fixo', '--contra', '.largo'],
    video: ['--url', URL, '--publico', 'pub'],
    publicacao: ['--dist', dist],
    rastreamento: ['--dist', dist, '--plano', path.join(proj, 'PLANO.md')],
    plano: ['--projeto', proj],
    referencias: ['--projeto', proj],
  };
  assert.deepEqual(Object.keys(esperado).sort(), CATALOGO.map((g) => g.nome).sort(), 'a tabela do teste não cobre todos os gates');
  for (const [nome, args] of Object.entries(esperado)) assert.deepEqual(lido(nome), args, `argumentos de ${nome}`);
  // sem as opções, as opções não vazam para os gates
  const r2 = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', URL, '--sem-montar', '--so', 'composicao,imagens']);
  assert.equal(r2.codigo, 0, r2.saida);
  assert.deepEqual(lido('composicao'), ['--url', URL, '--projeto', proj]);
  assert.deepEqual(lido('imagens'), ['--projeto', proj, '--url', URL]);
});

function vivo(pid) { try { process.kill(pid, 0); return true; } catch (e) { return e.code === 'EPERM'; } }
async function esperarMorrer(pids, ms = 5000) {
  const limite = Date.now() + ms;
  while (Date.now() < limite && pids.some(vivo)) await new Promise((r) => setTimeout(r, 50));
  return pids.filter(vivo);
}

teste('estouro de tempo mata a ÁRVORE do gate (o filho e o neto), sem deixar processo escondido', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const marcas = pastaTemp('marcas');
  const corpo = `
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const neto = spawn(process.execPath, ['-e', 'setTimeout(function(){}, 60000)'], { stdio: 'ignore' });
fs.writeFileSync(path.join(${JSON.stringify(marcas)}, 'pids.json'), JSON.stringify([process.pid, neto.pid]));
setTimeout(() => {}, 60000);
`;
  montarFalsos(falsos, { texto: { mjs: corpo } })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--so', 'texto', '--tempo-max', '2']);
  assert.equal(r.codigo, 1, r.saida);
  const pids = JSON.parse(fs.readFileSync(path.join(marcas, 'pids.json'), 'utf8'));
  const sobrou = await esperarMorrer(pids);
  assert.deepEqual(sobrou, [], `processo(s) ainda vivo(s) depois do tempo máximo: ${sobrou.join(', ')}`);
});

// ---------------------------------------------------------------- 3. paralelismo e teto
teste('os gates rodam em paralelo de verdade (barreira: cada um espera o outro começar)', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const marcas = pastaTemp('marcas');
  const barreira = (eu, outro) => `
import fs from 'node:fs';
import path from 'node:path';
const m = ${JSON.stringify(marcas)};
fs.writeFileSync(path.join(m, ${JSON.stringify(eu)}), '1');
const limite = Date.now() + 15000;
while (!fs.existsSync(path.join(m, ${JSON.stringify(outro)}))) {
  if (Date.now() > limite) { console.log('o outro gate nunca começou: não rodou em paralelo'); process.exit(1); }
  await new Promise((r) => setTimeout(r, 20));
}
console.log('os dois estavam vivos ao mesmo tempo');
`;
  montarFalsos(falsos, { texto: { mjs: barreira('a', 'b') }, ritmo: { mjs: barreira('b', 'a') } })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--so', 'texto,ritmo', '--paralelo', '2']);
  assert.equal(r.codigo, 0, r.saida);
});

teste('com --paralelo 1 nunca há dois gates de navegador vivos ao mesmo tempo', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const marcas = pastaTemp('marcas');
  const exclusivo = (eu) => `
import fs from 'node:fs';
import path from 'node:path';
const m = ${JSON.stringify(marcas)};
const meu = path.join(m, 'vivo-' + ${JSON.stringify(eu)});
const outros = fs.readdirSync(m).filter((n) => n.startsWith('vivo-'));
if (outros.length) { console.log('havia outro gate vivo: ' + outros.join(',')); process.exit(1); }
fs.writeFileSync(meu, '1');
await new Promise((r) => setTimeout(r, 400));
fs.rmSync(meu);
console.log('sozinho');
`;
  const corpos = {};
  for (const n of ['texto', 'ritmo', 'oclusao']) corpos[n] = { mjs: exclusivo(n) };
  montarFalsos(falsos, corpos)(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--so', 'texto,ritmo,oclusao', '--paralelo', '1']);
  assert.equal(r.codigo, 0, r.saida);
});

teste('o teto padrão nunca passa de 4 nem fica abaixo de 1, qualquer que seja a máquina', async () => {
  const mod = await catalogo();
  for (const cpus of [1, 2, 4, 8, 16, 64]) {
    const t = mod.tetoPadrao(cpus);
    assert.ok(t >= 1 && t <= 4, `teto ${t} para ${cpus} CPUs`);
  }
  assert.equal(mod.tetoPadrao(1), 1);
});

teste('--confirmar-sozinho: gate que reprova só com outro vivo e passa sozinho vira INSTÁVEL e o veredito oficial é o isolado', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const marcas = pastaTemp('marcas');
  // texto e ritmo esperam um ao outro; o texto REPROVA se viu o outro vivo, e passa se está sozinho
  const par = (eu, outro, falhaSeVer) => `
import fs from 'node:fs';
import path from 'node:path';
const m = ${JSON.stringify(marcas)};
fs.writeFileSync(path.join(m, ${JSON.stringify(eu)}), String(process.pid));
const vivo = (pid) => { try { process.kill(pid, 0); return true; } catch (e) { return e.code === 'EPERM'; } };
const limite = Date.now() + 3000;
let viu = false;
while (Date.now() < limite) {
  const f = path.join(m, ${JSON.stringify(outro)});
  if (fs.existsSync(f) && vivo(Number(fs.readFileSync(f, 'utf8')))) { viu = true; break; }
  await new Promise((r) => setTimeout(r, 20));
}
${falhaSeVer ? 'if (viu) { console.log("FALHA: medi com a máquina cheia"); process.exit(1); }' : 'await new Promise((r) => setTimeout(r, 3500));'}
console.log('ok');
`;
  montarFalsos(falsos, { texto: { mjs: par('texto-vivo', 'ritmo-vivo', true) }, ritmo: { mjs: par('ritmo-vivo', 'texto-vivo', false) } })(CATALOGO);
  const proj = projetoFalso();
  const base = ['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--so', 'texto,ritmo', '--paralelo', '2'];
  const sem = rodar(base);
  assert.equal(sem.codigo, 1, 'sem a opção o veredito do paralelo vale:\n' + sem.saida);
  const com = rodar([...base, '--confirmar-sozinho']);
  assert.equal(com.codigo, 0, com.saida);
  assert.match(com.saida, /INSTÁVEIS POR CARGA/);
  assert.match(com.saida, /texto: saída 1 em paralelo/);
  assert.ok(fs.existsSync(path.join(proj, 'gates', 'texto-r2-paralelo.txt')), 'a saída do paralelo deve ficar guardada');
  assert.match(fs.readFileSync(path.join(proj, 'gates', 'texto-r2-paralelo.txt'), 'utf8'), /medi com a máquina cheia/);
  const exec = fs.readFileSync(path.join(proj, 'gates', '_execucoes.txt'), 'utf8');
  assert.match(exec, /^2 texto 0$/m);
});

teste('--confirmar-sozinho NÃO absolve gate que também reprova sozinho', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos, { texto: { mjs: 'console.log("falha de verdade");\nprocess.exit(1);\n' } })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--so', 'texto,ritmo', '--confirmar-sozinho']);
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /REPROVA\s+texto/);
  assert.doesNotMatch(r.saida, /INSTÁVEIS POR CARGA/);
  assert.match(r.saida, /falha de verdade/);
});

// ---------------------------------------------------------------- 4. --so, --reprovados, rodadas
teste('--so roda só os gates pedidos e recusa nome que não existe', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos)(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--so', 'texto,verdade']);
  assert.equal(r.codigo, 0, r.saida);
  assert.match(r.saida, /PASSA\s+texto/);
  assert.match(r.saida, /PASSA\s+verdade/);
  assert.doesNotMatch(r.saida, /sem-kicker/);
  const ruim = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--so', 'texto,inexistente']);
  assert.equal(ruim.codigo, 2, ruim.saida);
  assert.match(ruim.saida, /inexistente/);
});

teste('--reprovados roda só o que reprovou por último (e o que nunca rodou), e a rodada seguinte é numerada', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const proj = projetoFalso();
  // simetria reprova enquanto existir o arquivo 'quebrado' no projeto
  const falhaSeQuebrado = `
import fs from 'node:fs';
import path from 'node:path';
const proj = ${JSON.stringify(proj)};
if (fs.existsSync(path.join(proj, 'quebrado'))) { console.log('simetria quebrada'); process.exit(1); }
console.log('simetria ok');
`;
  montarFalsos(falsos, { simetria: { mjs: falhaSeQuebrado } })(CATALOGO);
  fs.writeFileSync(path.join(proj, 'quebrado'), '1');
  const base = ['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar'];
  const r1 = rodar(base);
  assert.equal(r1.codigo, 1, r1.saida);
  fs.unlinkSync(path.join(proj, 'quebrado'));
  const r2 = rodar([...base, '--reprovados']);
  assert.equal(r2.codigo, 0, r2.saida);
  assert.match(r2.saida, /PASSA\s+simetria/);
  assert.doesNotMatch(r2.saida, /sem-kicker/, '--reprovados não pode rodar gate que já passou');
  assert.ok(fs.existsSync(path.join(proj, 'gates', 'simetria-r2.txt')), 'a segunda rodada deve gravar -r2');
  // agora tudo passou: --reprovados não tem o que rodar e diz isso, saindo 0
  const r3 = rodar([...base, '--reprovados']);
  assert.equal(r3.codigo, 0, r3.saida);
  assert.match(r3.saida, /nenhum gate reprovado/i);
  // gate que nunca rodou conta como pendente
  const proj2 = projetoFalso();
  fs.mkdirSync(path.join(proj2, 'gates'));
  fs.writeFileSync(path.join(proj2, 'gates', '_execucoes.txt'), '1 sem-kicker 0\n1 texto 1\n');
  const r4 = rodar(['--projeto', proj2, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--reprovados']);
  assert.match(r4.saida, /PASSA\s+texto/);
  assert.match(r4.saida, /PASSA\s+movimento/, 'gate que nunca rodou deve entrar no --reprovados');
  assert.doesNotMatch(r4.saida, /PASSA\s+sem-kicker/);
});

// ---------------------------------------------------------------- 5. portabilidade e servidor
teste('o comando de repetição impresso leva aspas em volta dos caminhos (pasta com espaço e acento)', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos, { texto: { mjs: 'process.exit(1);\n' } })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar']);
  assert.equal(r.codigo, 1);
  const linha = r.saida.split('\n').find((l) => l.includes('--reprovados'));
  assert.ok(linha, 'sem linha de repetição');
  assert.ok(linha.includes(`"${proj.split(path.sep).join('/')}"`) || linha.includes(`"${proj}"`), linha);
  assert.ok(/rodar-gates\.mjs"/.test(linha), linha);
});

teste('um servidor por gate: cada gate de navegador recebe uma porta própria e livre', async () => {
  const mod = await catalogo();
  const proj = pastaTemp('serv');
  fs.writeFileSync(path.join(proj, 'index.html'), '<h1>oi çá</h1>', 'utf8');
  const a = await mod.subirServidor(proj, AQUI);
  const b = await mod.subirServidor(proj, AQUI);
  try {
    assert.notEqual(a.porta, b.porta);
    for (const s of [a, b]) {
      const resp = await fetch(s.url);
      assert.equal(resp.status, 200);
      assert.match(await resp.text(), /oi çá/);
    }
  } finally {
    a.parar(); b.parar();
  }
  // parar() mata o servidor de verdade (o py.mjs e o Python dele): a porta deixa de responder
  const limite = Date.now() + 5000;
  let ainda = true;
  while (ainda && Date.now() < limite) {
    ainda = await fetch(a.url).then(() => true, () => false);
    if (ainda) await new Promise((r) => setTimeout(r, 50));
  }
  assert.equal(ainda, false, 'o servidor continuou vivo depois de parar()');
});

teste('--lista mostra o conjunto sem rodar nada', async () => {
  const r = rodar(['--lista']);
  assert.equal(r.codigo, 0, r.saida);
  for (const n of ['movimento', 'responsivo', 'sem-kicker', 'imagens']) assert.match(r.saida, new RegExp(n));
});

// ---------------------------------------------------------------- 6. servidor que cai no meio (P11, 3.5.10)
const gateQueCaiUmaVez = (marca) => ({
  mjs: `import fs from 'node:fs';\nconst m = ${JSON.stringify(marca)};\n` +
    `if (!fs.existsSync(m)) { fs.writeFileSync(m, '1'); console.error('servidor fora do ar em http://127.0.0.1:1/: nada ouve nessa porta'); process.exit(3); }\n` +
    `console.log('ok oclusao na segunda tentativa');\n`,
});

teste('servidor que caiu no meio do gate: o comando sobe outro e repete o gate uma vez, dizendo isso', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const marca = path.join(pastaTemp('marca'), 'tentou.txt');
  montarFalsos(falsos, { oclusao: gateQueCaiUmaVez(marca) })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--sem-montar', '--so', 'oclusao']);
  assert.equal(r.codigo, 0, r.saida);
  assert.match(r.saida, /servidor.*caiu.*repito/i, r.saida);
  assert.ok(fs.existsSync(path.join(proj, 'gates', 'oclusao-r1-servidor-caiu.txt')), 'a saída da 1ª tentativa deve ficar guardada');
});

teste('servidor que cai de novo na repetição: o gate reprova e a mensagem de servidor fora fica no relatório', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  montarFalsos(falsos, {
    oclusao: { mjs: `console.error('servidor fora do ar em http://127.0.0.1:1/: nada ouve nessa porta');\nprocess.exit(3);\n` },
  })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--sem-montar', '--so', 'oclusao']);
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /servidor fora do ar em http:\/\/127\.0\.0\.1:1\//, r.saida);
});

teste('gate que reprova SEM a marca de servidor fora não é repetido (reprovação de verdade não se maquia)', async () => {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const contador = path.join(pastaTemp('marca'), 'vezes.txt');
  montarFalsos(falsos, {
    oclusao: { mjs: `import fs from 'node:fs';\nfs.appendFileSync(${JSON.stringify(contador)}, 'x');\nconsole.log('REPROVA texto coberto');\nprocess.exit(1);\n` },
  })(CATALOGO);
  const proj = projetoFalso();
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--sem-montar', '--so', 'oclusao']);
  assert.equal(r.codigo, 1, r.saida);
  assert.equal(fs.readFileSync(contador, 'utf8'), 'x', 'o gate que reprovou de verdade rodou mais de uma vez');
});

(async () => {
  let falhas = 0;
  for (const [nome, fn] of testes) {
    try { await fn(); console.log(`ok   ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome}\n  ${String(e && e.stack || e).split('\n').slice(0, 6).join('\n  ')}`); }
  }
  limpar();
  console.log(`\n${testes.length - falhas} de ${testes.length} testes passaram.`);
  process.exit(falhas ? 1 : 0);
})();
