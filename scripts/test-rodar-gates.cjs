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

teste('os 15 gates do fluxo antigo (gates-todos) continuam todos no conjunto padrão, mais o gate de SEO da 3.8.0', async () => {
  const { CATALOGO } = await catalogo();
  const padrao = CATALOGO.filter((g) => !g.opcional).map((g) => g.nome).sort();
  const antigos = ['sem-kicker', 'classes-mortas', 'verdade', 'publicacao', 'rastreamento', 'plano', 'referencias',
    'responsivo', 'oclusao', 'simetria', 'texto', 'composicao', 'ritmo', 'imagens', 'movimento', 'seo'].sort();
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
    seo: ['--dist', dist, '--plano', path.join(proj, 'PLANO.md')],
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

// ---------------------------------------------------------------- 7. cache de gate por conteúdo (corte 4 da auditoria de velocidade)
// Cada gate de mentira conta quantas vezes RODOU (um 'x' por execução num arquivo da pasta de marcas).
function corposContando(CATALOGO, marcas, extra = {}) {
  const corpos = {};
  for (const g of CATALOGO) {
    const arq = path.join(marcas, `${g.nome}.count`);
    const sai = extra[g.nome] || `console.log("ok ${g.nome}");`;
    corpos[g.nome] = g.arquivo.endsWith('.py')
      ? { py: `import sys\nwith open(${JSON.stringify(arq)}, 'a', encoding='utf-8') as f:\n    f.write('x')\nprint("ok ${g.nome}")\n` }
      : { mjs: `import fs from 'node:fs';\nfs.appendFileSync(${JSON.stringify(arq)}, 'x');\n${sai}\n` };
  }
  return corpos;
}
const vezes = (marcas, nome) => { try { return fs.readFileSync(path.join(marcas, `${nome}.count`), 'utf8').length; } catch (_) { return 0; } };
const BASE_CACHE = (proj, falsos) => ['--projeto', proj, '--scripts-dir', falsos, '--sem-montar'];
const SO_URL = ['movimento', 'responsivo', 'oclusao', 'simetria', 'texto', 'ritmo'];            // leem só a dist servida
const SO_PROJETO = ['sem-kicker', 'classes-mortas', 'verdade', 'plano', 'referencias'];         // leem só o projeto
const AMBOS = ['composicao', 'imagens'];                                                        // dist servida e projeto

async function cenarioCache() {
  const { CATALOGO } = await catalogo();
  const falsos = pastaTemp('falsos');
  const marcas = pastaTemp('marcas');
  montarFalsos(falsos, corposContando(CATALOGO, marcas))(CATALOGO);
  const proj = projetoFalso();
  return { CATALOGO, falsos, marcas, proj, base: BASE_CACHE(proj, falsos) };
}

teste('cache: a segunda rodada sem mudança nenhuma não roda gate nenhum e diz que veio do cache', async () => {
  const { CATALOGO, marcas, base } = await cenarioCache();
  const r1 = rodar(base);
  assert.equal(r1.codigo, 0, r1.saida);
  for (const g of CATALOGO.filter((x) => !x.opcional)) assert.equal(vezes(marcas, g.nome), 1, `${g.nome} na rodada 1`);
  const r2 = rodar(base);
  assert.equal(r2.codigo, 0, r2.saida);
  for (const g of CATALOGO.filter((x) => !x.opcional)) assert.equal(vezes(marcas, g.nome), 1, `${g.nome} rodou de novo na rodada 2, com a entrada idêntica`);
  assert.match(r2.saida, /PASSA\s+movimento\s+0,0 s.*cache/i);
  assert.match(r2.saida, /Cache: 16 de 16 gate\(s\)/);
  assert.match(r2.saida, /RESULTADO: PASSA em 16 de 16/);
});

teste('cache: o arquivo de saída da rodada guarda o laudo de antes e diz de onde ele veio', async () => {
  const { base, proj } = await cenarioCache();
  rodar(base); rodar(base);
  const txt = fs.readFileSync(path.join(proj, 'gates', 'texto-r2.txt'), 'utf8');
  assert.match(txt, /laudo reaproveitado da rodada 1/);
  assert.match(txt, /ok texto/, 'o laudo de antes tem que estar no arquivo');
  const exec = fs.readFileSync(path.join(proj, 'gates', '_execucoes.txt'), 'utf8');
  assert.match(exec, /^2 texto 0$/m, 'a rodada 2 entra no histórico mesmo vinda do cache');
});

teste('cache: 1 byte trocado na dist faz rodar de novo todo gate que lê a dist, e só eles', async () => {
  const { CATALOGO, marcas, base, proj } = await cenarioCache();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), '<html>x</html>', 'utf8');
  const r = rodar(base);
  assert.equal(r.codigo, 0, r.saida);
  for (const n of [...SO_URL, ...AMBOS, 'publicacao', 'rastreamento']) assert.equal(vezes(marcas, n), 2, `${n} devia rodar de novo`);
  for (const n of SO_PROJETO) assert.equal(vezes(marcas, n), 1, `${n} não lê a dist e devia vir do cache`);
  assert.ok(CATALOGO.length > 0);
});

teste('cache: 1 byte trocado no projeto faz rodar de novo todo gate que lê o projeto, e só eles', async () => {
  const { marcas, base, proj } = await cenarioCache();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'PLANO.md'), 'Pixel pedido: nenhum\nmudou\n', 'utf8');
  rodar(base);
  for (const n of [...SO_PROJETO, ...AMBOS, 'rastreamento']) assert.equal(vezes(marcas, n), 2, `${n} devia rodar de novo`);
  for (const n of [...SO_URL, 'publicacao']) assert.equal(vezes(marcas, n), 1, `${n} não lê o projeto e devia vir do cache`);
});

teste('cache: o que os gates escrevem em gates/ e auditoria/ não invalida nada', async () => {
  const { marcas, base, proj } = await cenarioCache();
  rodar(base);
  fs.mkdirSync(path.join(proj, 'auditoria'), { recursive: true });
  fs.writeFileSync(path.join(proj, 'auditoria', 'pacote.json'), '{}', 'utf8');
  fs.writeFileSync(path.join(proj, 'gates', 'qualquer-coisa.txt'), 'saida de outro gate', 'utf8');
  fs.writeFileSync(path.join(proj, '.wave-auditoria.json'), '{}', 'utf8');
  rodar(base);
  for (const n of [...SO_URL, ...SO_PROJETO, ...AMBOS]) assert.equal(vezes(marcas, n), 1, `${n} rodou de novo por causa de arquivo que é saída de gate`);
});

teste('cache: foto nova no projeto (referencias/, prova/) invalida o gate que lê o projeto', async () => {
  const { marcas, base, proj } = await cenarioCache();
  fs.mkdirSync(path.join(proj, 'referencias'), { recursive: true });
  rodar(base);
  fs.writeFileSync(path.join(proj, 'referencias', '01-dobra.png'), 'png-novo', 'utf8');
  rodar(base);
  assert.equal(vezes(marcas, 'referencias'), 2);
  assert.equal(vezes(marcas, 'texto'), 1);
});

teste('cache: trocar o script do gate (nova versão do gate) faz ele rodar de novo, e só ele', async () => {
  const { CATALOGO, falsos, marcas, base } = await cenarioCache();
  rodar(base);
  const alvo = path.join(falsos, 'gate-ritmo.mjs');
  fs.writeFileSync(alvo, fs.readFileSync(alvo, 'utf8') + '\n// versão nova do gate\n', 'utf8');
  rodar(base);
  // a versão dos scripts é da PASTA inteira: mexer num gate refaz os que usam a mesma pasta de scripts
  assert.equal(vezes(marcas, 'ritmo'), 2, 'o gate trocado tem que rodar de novo');
  assert.ok(CATALOGO.length);
});

teste('cache: mudar um argumento do gate (--produto-fisico) faz ele rodar de novo', async () => {
  const { marcas, base } = await cenarioCache();
  rodar(base);
  rodar([...base, '--produto-fisico']);
  assert.equal(vezes(marcas, 'composicao'), 2, 'composicao recebe --produto-fisico: é outra pergunta');
  assert.equal(vezes(marcas, 'texto'), 1, 'texto não recebe o argumento: continua no cache');
});

teste('cache: gate que reprova nunca vira cache (roda de novo na rodada seguinte)', async () => {
  const { CATALOGO, falsos, marcas, proj } = await cenarioCache();
  montarFalsos(falsos, corposContando(CATALOGO, marcas, { texto: 'console.log("falhei");\nprocess.exit(1);' }))(CATALOGO);
  const base = BASE_CACHE(proj, falsos);
  assert.equal(rodar(base).codigo, 1);
  assert.equal(rodar(base).codigo, 1);
  assert.equal(vezes(marcas, 'texto'), 2, 'reprovação não pode ser reaproveitada');
  assert.equal(vezes(marcas, 'ritmo'), 1, 'quem passou segue no cache');
  assert.ok(!fs.existsSync(path.join(proj, 'gates', '_cache', 'texto.json')), 'reprovação foi parar no cache');
});

teste('cache: --sem-cache roda tudo de novo', async () => {
  const { marcas, base } = await cenarioCache();
  rodar(base);
  const r = rodar([...base, '--sem-cache']);
  assert.equal(r.codigo, 0, r.saida);
  for (const n of [...SO_URL, ...SO_PROJETO]) assert.equal(vezes(marcas, n), 2, `${n} com --sem-cache`);
  assert.doesNotMatch(r.saida, /laudo reaproveitado|Cache: \d/);
});

teste('cache: página servida por quem chamou (--url) não entra no cache dos gates de tela, mas os de arquivo sim', async () => {
  const { marcas, base } = await cenarioCache();
  const comUrl = [...base, '--url', 'http://127.0.0.1:1/'];
  rodar(comUrl); rodar(comUrl);
  for (const n of [...SO_URL, ...AMBOS]) assert.equal(vezes(marcas, n), 2, `${n}: não sabemos o que há na URL de fora`);
  for (const n of [...SO_PROJETO, 'publicacao', 'rastreamento']) assert.equal(vezes(marcas, n), 1, `${n}: lê só arquivos locais`);
});

teste('cache: registro de cache corrompido ou de outro formato é ignorado, o gate roda', async () => {
  const { marcas, base, proj } = await cenarioCache();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'gates', '_cache', 'texto.json'), '{ isto não é json', 'utf8');
  const reg = path.join(proj, 'gates', '_cache', 'ritmo.json');
  const r = JSON.parse(fs.readFileSync(reg, 'utf8'));
  r.versao = 999;
  fs.writeFileSync(reg, JSON.stringify(r), 'utf8');
  const out = rodar(base);
  assert.equal(out.codigo, 0, out.saida);
  assert.equal(vezes(marcas, 'texto'), 2);
  assert.equal(vezes(marcas, 'ritmo'), 2);
  assert.equal(vezes(marcas, 'oclusao'), 1);
});

teste('cache: aviso de um gate que passou continua aparecendo quando o laudo vem do cache', async () => {
  const { CATALOGO, falsos, marcas, proj } = await cenarioCache();
  montarFalsos(falsos, corposContando(CATALOGO, marcas, { simetria: 'console.log("desktop: AVISO (data-assimetrico): coluna curta");' }))(CATALOGO);
  const base = BASE_CACHE(proj, falsos);
  rodar(base);
  const r = rodar(base);
  assert.match(r.saida, /\[simetria\] desktop: AVISO \(data-assimetrico\): coluna curta/);
  assert.equal(vezes(marcas, 'simetria'), 1);
});

teste('cache: o gate opcional de vídeo nunca entra no cache (lê uma pasta que o comando não conhece)', async () => {
  const { marcas, base } = await cenarioCache();
  const comVideo = [...base, '--com', 'video', '--publico', 'pub'];
  rodar(comVideo); rodar(comVideo);
  assert.equal(vezes(marcas, 'video'), 2);
});

// Por que o gate rodou de novo (pedido do coordenador: confirmar que o movimento pula quando HTML, CSS e JS não mudaram, e ver o motivo quando não pula)
teste('cache: o relatório diz por que cada gate rodou de novo (a dist mudou) e quem veio do cache', async () => {
  const { marcas, base, proj } = await cenarioCache();
  const r1 = rodar(base);
  assert.match(r1.saida, /movimento[^\n]*\(rodou: sem laudo PASSA guardado\)/, 'primeira rodada: não havia cache');
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), '<html>x</html>', 'utf8');
  const r2 = rodar(base);
  assert.match(r2.saida, /PASSA\s+movimento[^\n]*\(rodou: a dist mudou/);
  assert.match(r2.saida, /PASSA\s+sem-kicker[^\n]*\(cache: laudo da rodada 1/);
  assert.equal(vezes(marcas, 'movimento'), 2);
  assert.equal(vezes(marcas, 'sem-kicker'), 1);
});

teste('cache: o motivo nomeia o que mudou: o projeto, os scripts, os argumentos', async () => {
  const { falsos, base, proj } = await cenarioCache();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'PLANO.md'), 'Pixel pedido: nenhum\nmudou\n', 'utf8');
  const a = rodar(base);
  assert.match(a.saida, /PASSA\s+plano[^\n]*\(rodou: o projeto mudou/);
  fs.appendFileSync(path.join(falsos, 'gate-ritmo.mjs'), '\n// outra versão\n');
  const b = rodar(base);
  assert.match(b.saida, /PASSA\s+ritmo[^\n]*\(rodou: os scripts da skill mudaram/);
  const c = rodar([...base, '--produto-fisico']);
  assert.match(c.saida, /PASSA\s+composicao[^\n]*\(rodou: os argumentos mudaram/);
});

teste('--explicar-cache: mostra, gate por gate, se acerta ou erra o cache e por quê, sem rodar gate nenhum', async () => {
  const { marcas, base, proj } = await cenarioCache();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), '<html>y</html>', 'utf8');
  const antes = fs.readdirSync(path.join(proj, 'gates')).sort().join(',');
  const r = rodar([...base, '--explicar-cache']);
  assert.equal(r.codigo, 0, r.saida);
  for (const n of SO_URL) assert.match(r.saida, new RegExp(`ERRA\\s+${n}\\s+a dist mudou`), `${n} devia errar por causa da dist`);
  for (const n of SO_PROJETO) assert.match(r.saida, new RegExp(`ACERTA\\s+${n}\\s`), `${n} não lê a dist e devia acertar`);
  assert.match(r.saida, /nada foi rodado/i);
  for (const n of [...SO_URL, ...SO_PROJETO]) assert.equal(vezes(marcas, n), 1, `${n} rodou durante o --explicar-cache`);
  assert.ok(!fs.existsSync(path.join(proj, 'gates', 'texto-r2.txt')), 'não pode gravar laudo de rodada');
  assert.ok(!/^2 /m.test(fs.readFileSync(path.join(proj, 'gates', '_execucoes.txt'), 'utf8')), 'não pode entrar no histórico de rodadas');
  assert.ok(fs.readdirSync(path.join(proj, 'gates')).sort().join(',').startsWith(antes.split(',')[0]));
});

teste('--explicar-cache: a conta bate com a rodada de verdade (quem acerta no resumo vem do cache, quem erra roda)', async () => {
  const { marcas, base, proj } = await cenarioCache();
  rodar(base);
  fs.writeFileSync(path.join(proj, 'PLANO.md'), 'Pixel pedido: nenhum\notra\n', 'utf8');
  const e = rodar([...base, '--explicar-cache']);
  const acertam = [...e.saida.matchAll(/ACERTA\s+(\S+)/g)].map((m) => m[1]).sort();
  const erram = [...e.saida.matchAll(/ERRA\s+(\S+)/g)].map((m) => m[1]).sort();
  rodar(base);
  for (const n of acertam) assert.equal(vezes(marcas, n), 1, `${n}: o resumo disse que acertava`);
  for (const n of erram) assert.equal(vezes(marcas, n), 2, `${n}: o resumo disse que errava`);
  assert.ok(acertam.length > 0 && erram.length > 0);
});

teste('--explicar-cache: --url de fora, vídeo e --sem-cache aparecem como FORA do cache, com o motivo', async () => {
  const { base } = await cenarioCache();
  const a = rodar([...base, '--url', 'http://127.0.0.1:1/', '--explicar-cache']);
  assert.match(a.saida, /FORA\s+texto\s+.*--url/);
  const b = rodar([...base, '--com', 'video', '--publico', 'pub', '--explicar-cache']);
  assert.match(b.saida, /FORA\s+video\s+.*pasta pública/);
  const c = rodar([...base, '--sem-cache', '--explicar-cache']);
  assert.match(c.saida, /ERRA\s+texto\s+.*--sem-cache/);
});

// ---------------------------------------------------------------- 8. registro automático na wave (corte 5)
const lerWave = (proj) => JSON.parse(fs.readFileSync(path.join(proj, '.wave-auditoria.json'), 'utf8'));

teste('registro: a rodada completa grava o exit REAL de cada gate na wave, sem ninguém digitar', async () => {
  const { CATALOGO, falsos, marcas, proj } = await cenarioCache();
  montarFalsos(falsos, corposContando(CATALOGO, marcas, { simetria: 'console.log("coluna torta");\nprocess.exit(1);' }))(CATALOGO);
  const r = rodar(BASE_CACHE(proj, falsos));
  assert.equal(r.codigo, 1, r.saida);
  const w = lerWave(proj);
  const esperados = ['movimento', 'responsivo', 'oclusao', 'simetria', 'composicao', 'imagens', 'texto', 'ritmo', 'sem-kicker',
    'classes-mortas', 'verdade', 'publicacao', 'rastreamento', 'seo', 'plano', 'referencias'];
  for (const n of esperados) assert.ok(w.gates[n], `gate ${n} sem registro na wave`);
  assert.equal(w.gates.simetria.exit, 1, 'o exit real da reprovação');
  assert.equal(w.gates.texto.exit, 0);
  assert.match(w.gates.simetria.detalhe, /rodar-gates/);
  assert.match(w.gates.simetria.detalhe, /gates\/simetria-r1\.txt/);
  assert.equal(w.gates.video, undefined, 'video e sobreposicao não têm nome na wave');
  assert.match(r.saida, /Wave: 16 gate\(s\) registrado\(s\)/);
});

teste('registro: o gate que veio do cache é registrado como tal, com o exit 0 da rodada de origem', async () => {
  const { base, proj } = await cenarioCache();
  rodar(base);
  rodar(base);
  const w = lerWave(proj);
  assert.match(w.gates.texto.detalhe, /cache/);
  assert.match(w.gates.texto.detalhe, /rodada 1/);
  assert.equal(w.gates.texto.exit, 0);
});

teste('registro: rodada parcial (--so, --reprovados) NÃO registra; o criar.md manda registrar só depois da rodada completa', async () => {
  const { base, proj } = await cenarioCache();
  const r = rodar([...base, '--so', 'texto,ritmo']);
  assert.equal(r.codigo, 0, r.saida);
  assert.ok(!fs.existsSync(path.join(proj, '.wave-auditoria.json')), 'rodada parcial não pode registrar');
  assert.match(r.saida, /rodada parcial.*não registr/i);
  const r2 = rodar([...base, '--reprovados']);
  assert.ok(!fs.existsSync(path.join(proj, '.wave-auditoria.json')) || !lerWave(proj).gates.texto);
  assert.equal(r2.codigo, 0);
});

teste('registro: --registrar-conserto numa rodada parcial grava SÓ os gates que rodaram (conserto de regressão trivial, 3.6.1)', async () => {
  const { CATALOGO, falsos, marcas, proj } = await cenarioCache();
  montarFalsos(falsos, corposContando(CATALOGO, marcas, { texto: 'console.log("falhei");\nprocess.exit(1);' }))(CATALOGO);
  rodar(BASE_CACHE(proj, falsos));
  assert.equal(lerWave(proj).gates.texto.exit, 1);
  const antes = JSON.stringify(lerWave(proj).gates.ritmo);
  // o conserto: o gate passa agora, e só ele roda
  montarFalsos(falsos, corposContando(CATALOGO, marcas))(CATALOGO);
  const r = rodar([...BASE_CACHE(proj, falsos), '--so', 'texto', '--registrar-conserto']);
  assert.equal(r.codigo, 0, r.saida);
  const w = lerWave(proj);
  assert.equal(w.gates.texto.exit, 0, 'o vermelho vira verde');
  assert.match(w.gates.texto.detalhe, /conserto parcial/);
  assert.equal(JSON.stringify(w.gates.ritmo), antes, 'os outros gates não são tocados');
  assert.match(r.saida, /Wave: 1 gate\(s\) registrado\(s\)/);
});

teste('registro: --registrar-conserto com --reprovados registra o exit real, inclusive o que continua vermelho', async () => {
  const { CATALOGO, falsos, marcas, proj } = await cenarioCache();
  montarFalsos(falsos, corposContando(CATALOGO, marcas, { texto: 'console.log("falhei");\nprocess.exit(1);' }))(CATALOGO);
  rodar(BASE_CACHE(proj, falsos));
  const r = rodar([...BASE_CACHE(proj, falsos), '--reprovados', '--registrar-conserto']);
  assert.equal(r.codigo, 1, r.saida);
  assert.equal(lerWave(proj).gates.texto.exit, 1);
  assert.match(lerWave(proj).gates.texto.detalhe, /conserto parcial/);
});

teste('registro: a rodada parcial sem --registrar-conserto continua sem registrar e diz como registrar o conserto', async () => {
  const { base, proj } = await cenarioCache();
  const r = rodar([...base, '--so', 'texto']);
  assert.ok(!fs.existsSync(path.join(proj, '.wave-auditoria.json')));
  assert.match(r.saida, /--registrar-conserto/);
});

teste('registro: --sem-registrar não toca na wave', async () => {
  const { base, proj } = await cenarioCache();
  const r = rodar([...base, '--sem-registrar']);
  assert.equal(r.codigo, 0, r.saida);
  assert.ok(!fs.existsSync(path.join(proj, '.wave-auditoria.json')));
});

teste('registro: um gate reprovado que passa na rodada seguinte troca o vermelho pelo verde', async () => {
  const { CATALOGO, falsos, marcas, proj } = await cenarioCache();
  montarFalsos(falsos, corposContando(CATALOGO, marcas, { texto: 'console.log("falhei");\nprocess.exit(1);' }))(CATALOGO);
  rodar(BASE_CACHE(proj, falsos));
  assert.equal(lerWave(proj).gates.texto.exit, 1);
  montarFalsos(falsos, corposContando(CATALOGO, marcas))(CATALOGO);
  const r = rodar(BASE_CACHE(proj, falsos));
  assert.equal(r.codigo, 0, r.saida);
  assert.equal(lerWave(proj).gates.texto.exit, 0);
});

teste('registro: o gate opcional animacao entra na wave quando é pedido com --com animacao', async () => {
  const { base, proj } = await cenarioCache();
  rodar([...base, '--com', 'animacao']);
  assert.equal(lerWave(proj).gates.animacao.exit, 0);
});

// ---------------------------------------------------------------- 9. aviso de tempo-limite (corte 3)
teste('tempo: o comando diz no começo que roda em primeiro plano com tempo-limite de 10 minutos, sem laço de espera', async () => {
  const { base } = await cenarioCache();
  const r = rodar(base);
  assert.match(r.saida, /primeiro plano/);
  assert.match(r.saida, /600000/);
  assert.match(r.saida, /laço de espera/);
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
