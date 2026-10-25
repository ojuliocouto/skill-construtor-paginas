/**
 * Testes do `provar.mjs` (a prova de tela feita de uma vez: prints, vídeo e quadros de animação em paralelo).
 * Corte 4 da auditoria de velocidade: a prova inteira custava 191,7 s (prints 39,9 s, vídeo 85,4 s, `anim.mjs` 63,7 s), cada uma
 * depois da outra, mesmo sem uma depender da outra.
 *
 * Não precisa de navegador: os scripts de verdade são trocados por scripts de mentira numa pasta temporária (`--scripts-dir`)
 * que gravam as marcas do que foi chamado, com que argumentos e quando. Fica provado:
 *  1. cada script recebe os argumentos que o `criar.md` manda (a URL, as pastas de saída, `--com-360 --com-320`, `--click`);
 *  2. no máximo 2 ao mesmo tempo (a regra de memória), 2 de fato ao mesmo tempo, e `--paralelo 1` põe em fila;
 *  3. o `prancha.py` roda depois do `anim.mjs` e só se ele passou;
 *  4. uma prova que reprova não impede as outras; o comando sai 1 e mostra o fim do laudo de quem falhou;
 *  5. sem `secoes.json` a animação é PULADA dizendo por quê (nunca em silêncio); `--sem-anim` pula de propósito;
 *  6. sem `--url` o comando serve a dist (uma porta livre) e passa a URL; com `--url` não sobe servidor;
 *  7. o exit real da prova de identidade vai para a wave, sem digitar; `--sem-registrar` não toca na wave.
 */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const AQUI = __dirname;
const PROVAR = path.join(AQUI, 'provar.mjs');
const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);
const pasta = (nome = 'pv') => fs.mkdtempSync(path.join(os.tmpdir(), `${nome} çá `));
const escrever = (p, t) => { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, t, 'utf8'); };

/** Scripts de mentira: cada um anota o início (e o fim) e os argumentos num arquivo de marcas. `.js` é CommonJS, `.mjs` é módulo. */
function falsos(marcas, { espera = {}, saida = {}, corpo = {} } = {}) {
  const dir = pasta('falsos');
  const prog = (nome, ext) => {
    const alvo = path.join(dir, `${nome}.${ext}`);
    const ms = espera[nome] || 0;
    const codigo = saida[nome] ?? 0;
    const marcaJson = JSON.stringify(path.join(marcas, nome + '.json'));
    if (ext === 'py') {
      escrever(alvo, `import sys, time, json\nm = ${marcaJson}\nopen(m, 'w', encoding='utf-8').write(json.dumps({"args": sys.argv[1:], "ini": time.time()}))\ntime.sleep(${ms / 1000})\n${corpo[nome] || ''}print("saida do ${nome}")\nsys.exit(${codigo})\n`);
    } else if (ext === 'js') {
      escrever(alvo, `const fs = require('node:fs');\n(async () => {\nconst m = ${marcaJson};\nconst ini = Date.now();\nfs.writeFileSync(m, JSON.stringify({ args: process.argv.slice(2), ini }));\n${corpo[nome] || ''}await new Promise((r) => setTimeout(r, ${ms}));\nconsole.log("saida do ${nome}");\nfs.writeFileSync(m, JSON.stringify({ args: process.argv.slice(2), ini, fim: Date.now() }));\nprocess.exit(${codigo});\n})();\n`);
    } else {
      escrever(alvo, `import fs from 'node:fs';\nconst m = ${marcaJson};\nconst ini = Date.now();\nfs.writeFileSync(m, JSON.stringify({ args: process.argv.slice(2), ini }));\n${corpo[nome] || ''}await new Promise((r) => setTimeout(r, ${ms}));\nconsole.log("saida do ${nome}");\nfs.writeFileSync(m, JSON.stringify({ args: process.argv.slice(2), ini, fim: Date.now() }));\nprocess.exit(${codigo});\n`);
    }
  };
  prog('screenshot-prova', 'js'); prog('gravar-video', 'js'); prog('anim', 'mjs'); prog('prancha', 'py');
  return dir;
}

function projeto({ secoes = true } = {}) {
  const p = pasta('projeto');
  escrever(path.join(p, 'index.html'), '<!doctype html><html><head><title>x</title></head><body><h1>oi çá</h1></body></html>');
  if (secoes) escrever(path.join(p, 'prova', 'anim', 'secoes.json'), JSON.stringify([{ nome: '01', seletor: 'h1' }]));
  return p;
}

function provar(args, extraEnv = {}) {
  const r = spawnSync(process.execPath, [PROVAR, ...args], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1', ...extraEnv }, windowsHide: true, timeout: 120000 });
  return { codigo: r.status, saida: `${r.stdout || ''}${r.stderr || ''}` };
}
const marca = (marcas, nome) => JSON.parse(fs.readFileSync(path.join(marcas, `${nome}.json`), 'utf8'));
const existe = (marcas, nome) => fs.existsSync(path.join(marcas, `${nome}.json`));
const BASE = (proj, dir) => ['--projeto', proj, '--scripts-dir', dir, '--sem-montar', '--url', 'http://127.0.0.1:1/'];

teste('cada prova recebe os argumentos do criar.md: URL, pastas de saída, telas de 360 e 320, clique', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const proj = projeto();
  const r = provar([...BASE(proj, dir), '--click', '#comprar']);
  assert.equal(r.codigo, 0, r.saida);
  assert.deepEqual(marca(marcas, 'screenshot-prova').args, ['http://127.0.0.1:1/', path.join(proj, 'provas'), '--com-360', '--com-320', '--click', '#comprar']);
  assert.deepEqual(marca(marcas, 'gravar-video').args, ['http://127.0.0.1:1/', '--saida', path.join(proj, 'videos')]);
  const secoes = path.join(proj, 'prova', 'anim', 'secoes.json');
  assert.deepEqual(marca(marcas, 'anim').args, ['--url', 'http://127.0.0.1:1/', '--saida', path.join(proj, 'prova', 'anim'), '--secoes', secoes]);
  assert.deepEqual(marca(marcas, 'prancha').args, ['--pasta', path.join(proj, 'prova', 'anim'), '--secoes', secoes]);
});

teste('sem --click o clique não vai para o screenshot-prova', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const proj = projeto();
  provar(BASE(proj, dir));
  assert.ok(!marca(marcas, 'screenshot-prova').args.includes('--click'));
});

teste('paralelo de verdade: com teto 2, duas provas vivas ao mesmo tempo; a terceira espera', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas, { espera: { anim: 1500, 'gravar-video': 1500, 'screenshot-prova': 1500 } });
  const proj = projeto();
  const r = provar([...BASE(proj, dir), '--paralelo', '2']);
  assert.equal(r.codigo, 0, r.saida);
  const m = ['anim', 'gravar-video', 'screenshot-prova'].map((n) => marca(marcas, n));
  const sobrepoe = (a, b) => a.ini < b.fim && b.ini < a.fim;
  const pares = [[0, 1], [0, 2], [1, 2]].filter(([i, j]) => sobrepoe(m[i], m[j])).length;
  assert.ok(pares >= 1, 'nenhum par de provas rodou ao mesmo tempo');
  const vivosJuntos = (t) => m.filter((x) => x.ini <= t && t < x.fim).length;
  const pontos = m.flatMap((x) => [x.ini, x.fim - 1]);
  assert.ok(Math.max(...pontos.map(vivosJuntos)) <= 2, 'mais de 2 provas de navegador vivas ao mesmo tempo');
  assert.ok(Math.max(...pontos.map(vivosJuntos)) === 2, 'duas provas deviam estar vivas ao mesmo tempo');
});

teste('--paralelo 1 põe as provas em fila (nunca duas vivas)', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas, { espera: { anim: 600, 'gravar-video': 600, 'screenshot-prova': 600 } });
  const proj = projeto();
  const r = provar([...BASE(proj, dir), '--paralelo', '1']);
  assert.equal(r.codigo, 0, r.saida);
  const m = ['anim', 'gravar-video', 'screenshot-prova'].map((n) => marca(marcas, n)).sort((a, b) => a.ini - b.ini);
  assert.ok(m[1].ini >= m[0].fim && m[2].ini >= m[1].fim, 'duas provas se sobrepuseram com --paralelo 1');
});

teste('o teto nunca passa de 2, mesmo que peçam mais (regra de memória: no máximo 2 processos pesados de navegador)', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas, { espera: { anim: 1200, 'gravar-video': 1200, 'screenshot-prova': 1200 } });
  const proj = projeto();
  const r = provar([...BASE(proj, dir), '--paralelo', '8']);
  assert.equal(r.codigo, 0, r.saida);
  const m = ['anim', 'gravar-video', 'screenshot-prova'].map((n) => marca(marcas, n));
  const vivos = (t) => m.filter((x) => x.ini <= t && t < x.fim).length;
  assert.ok(Math.max(...m.flatMap((x) => [x.ini, x.fim - 1]).map(vivos)) <= 2);
});

teste('o prancha.py roda depois do anim.mjs; se o anim.mjs reprova, o prancha não roda', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas, { espera: { anim: 300 } });
  const proj = projeto();
  provar(BASE(proj, dir));
  const a = marca(marcas, 'anim'), p = marca(marcas, 'prancha');
  assert.ok(p.ini * 1000 >= a.fim - 50, 'o prancha começou antes de o anim terminar');
  const marcas2 = pasta('marcas');
  const dir2 = falsos(marcas2, { saida: { anim: 1 } });
  const r2 = provar(BASE(projeto(), dir2));
  assert.equal(r2.codigo, 1, r2.saida);
  assert.ok(!existe(marcas2, 'prancha'), 'o prancha rodou em cima de um anim reprovado');
  assert.match(r2.saida, /REPROVA\s+animacao/);
});

teste('uma prova que reprova não impede as outras; o comando sai 1 e mostra o laudo de quem falhou', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas, { saida: { 'gravar-video': 1 } });
  const r = provar(BASE(projeto(), dir));
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /REPROVA\s+video/);
  assert.match(r.saida, /PASSA\s+prints/);
  assert.match(r.saida, /saida do gravar-video/, 'o laudo de quem reprovou tem que aparecer');
  assert.ok(existe(marcas, 'screenshot-prova') && existe(marcas, 'anim'), 'as outras provas rodaram');
});

teste('sem secoes.json a animação é PULADA dizendo por quê, e o comando segue (nunca em silêncio)', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const r = provar(BASE(projeto({ secoes: false }), dir));
  assert.equal(r.codigo, 0, r.saida);
  assert.match(r.saida, /PULADA\s+animacao.*secoes\.json.*plano-para-secoes/s);
  assert.ok(!existe(marcas, 'anim') && !existe(marcas, 'prancha'));
  assert.ok(existe(marcas, 'screenshot-prova') && existe(marcas, 'gravar-video'));
});

teste('--sem-anim pula a animação de propósito e diz isso', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const r = provar([...BASE(projeto(), dir), '--sem-anim']);
  assert.equal(r.codigo, 0, r.saida);
  assert.match(r.saida, /PULADA\s+animacao.*--sem-anim/s);
  assert.ok(!existe(marcas, 'anim'));
});

teste('--secoes aponta outro secoes.json', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const proj = projeto({ secoes: false });
  const outro = path.join(proj, 'meu', 'secoes.json');
  escrever(outro, '[]');
  provar([...BASE(proj, dir), '--secoes', outro]);
  assert.deepEqual(marca(marcas, 'anim').args.slice(-2), ['--secoes', outro]);
});

teste('sem --url o comando serve a dist numa porta própria e passa a URL (e ela entrega a página)', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas, { corpo: { anim: `const r = await fetch(process.argv[3]); fs.writeFileSync(${JSON.stringify(path.join(marcas, 'pagina.txt'))}, await r.text());\n` } });
  const proj = projeto();
  escrever(path.join(proj, 'dist', 'index.html'), '<h1>da dist çá</h1>');
  const r = provar(['--projeto', proj, '--scripts-dir', dir, '--sem-montar']);
  assert.equal(r.codigo, 0, r.saida);
  assert.match(marca(marcas, 'screenshot-prova').args[0], /^http:\/\/127\.0\.0\.1:\d+\/$/);
  assert.equal(marca(marcas, 'screenshot-prova').args[0], marca(marcas, 'gravar-video').args[0], 'as três provas leem a MESMA página servida');
  assert.match(fs.readFileSync(path.join(marcas, 'pagina.txt'), 'utf8'), /da dist çá/);
});

teste('sem dist e sem --url o comando recusa com a instrução (saída 2)', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const proj = projeto();
  const r = provar(['--projeto', proj, '--scripts-dir', dir, '--sem-montar']);
  assert.equal(r.codigo, 2, r.saida);
  assert.match(r.saida, /dist/);
});

teste('registro: o exit real do screenshot-prova vai para a wave como "identidade", sem digitar', async () => {
  for (const [codigo, esperado] of [[0, 0], [1, 1]]) {
    const marcas = pasta('marcas');
    const dir = falsos(marcas, { saida: { 'screenshot-prova': codigo } });
    const proj = projeto();
    const r = provar(BASE(proj, dir));
    assert.equal(r.codigo, codigo, r.saida);
    const w = JSON.parse(fs.readFileSync(path.join(proj, '.wave-auditoria.json'), 'utf8'));
    assert.equal(w.gates.identidade.exit, esperado);
    assert.match(w.gates.identidade.detalhe, /provar/);
    assert.match(w.gates.identidade.detalhe, /screenshot-prova/);
    assert.match(r.saida, /Wave: 1 gate\(s\) registrado\(s\)/);
  }
});

teste('registro: --sem-registrar e --sem-anim com a identidade ainda rodando', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const proj = projeto();
  provar([...BASE(proj, dir), '--sem-registrar']);
  assert.ok(!fs.existsSync(path.join(proj, '.wave-auditoria.json')));
});

teste('cada prova grava o laudo em gates/prova-<nome>.txt', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const proj = projeto();
  provar(BASE(proj, dir));
  for (const n of ['prints', 'video', 'animacao']) assert.ok(fs.existsSync(path.join(proj, 'gates', `prova-${n}.txt`)), `gates/prova-${n}.txt`);
  assert.match(fs.readFileSync(path.join(proj, 'gates', 'prova-prints.txt'), 'utf8'), /saida do screenshot-prova/);
});

teste('o relatório mostra o tempo de cada prova e o total de relógio contra a soma', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas, { espera: { anim: 400, 'gravar-video': 400, 'screenshot-prova': 400 } });
  const r = provar(BASE(projeto(), dir));
  assert.match(r.saida, /PASSA\s+prints\s+\d/);
  assert.match(r.saida, /Total: [\d,]+ s de relógio \(soma das provas: [\d,]+ s/);
  assert.match(r.saida, /RESULTADO: PASSA/);
});

teste('o comando diz que roda em primeiro plano com tempo-limite de 10 minutos', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas);
  const r = provar(BASE(projeto(), dir));
  assert.match(r.saida, /primeiro plano/);
  assert.match(r.saida, /600000/);
});

teste('prova que estoura o tempo é interrompida e reprova (saída 124)', async () => {
  const marcas = pasta('marcas');
  const dir = falsos(marcas, { espera: { 'gravar-video': 60000 } });
  const r = provar([...BASE(projeto(), dir), '--tempo-max', '2']);
  assert.equal(r.codigo, 1, r.saida);
  assert.match(r.saida, /REPROVA\s+video/);
  assert.match(r.saida, /tempo máximo/i);
});

teste('pedido errado: sem --projeto, pasta que não existe e opção desconhecida saem 2', async () => {
  assert.equal(provar([]).codigo, 2);
  assert.equal(provar(['--projeto', path.join(os.tmpdir(), 'nao-existe-pv-çá')]).codigo, 2);
  assert.equal(provar(['--projeto', projeto(), '--inventada']).codigo, 2);
});

(async () => {
  let falhas = 0;
  for (const [nome, fn] of testes) {
    try { await fn(); console.log(`ok   ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome}\n  ${String(e && e.stack || e).split('\n').slice(0, 6).join('\n  ')}`); }
  }
  console.log(`\n${testes.length - falhas} de ${testes.length} testes passaram.`);
  process.exit(falhas ? 1 : 0);
})();
