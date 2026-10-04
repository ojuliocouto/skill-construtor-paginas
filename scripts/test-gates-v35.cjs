/**
 * Controles dos gates de tela da v3.5 (padrão da v7): ritmo, simetria com `data-assimetrico`,
 * responsivo com carrossel, aviso e foto na primeira tela do gate-imagens e a gravação de quadros
 * do anim.mjs. Páginas locais controladas isolam cada defeito; um processo pesado por vez.
 *
 * node scripts/test-gates-v35.cjs            todos os controles
 * GATES_FILTRO=ritmo node scripts/test-gates-v35.cjs   só os que começam com "ritmo"
 */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn, execFileSync } = require('node:child_process');

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'gates-v35-'));
// Foto de controle com textura (nítida) e uma versão lisa (borrada), geradas por PIL.
fs.writeFileSync(path.join(pasta, 'fazer-fotos.py'), [
  'import numpy as np, sys',
  'from PIL import Image',
  'rng = np.random.default_rng(7)',
  'pasta = sys.argv[1]',
  'ruido = rng.integers(0, 255, (600, 900, 3), dtype=np.uint8)',
  'Image.fromarray(ruido).save(pasta + "/foto-nitida.jpg", quality=95)',
  'Image.fromarray(np.full((600, 900, 3), 128, dtype=np.uint8)).save(pasta + "/foto-lisa.jpg", quality=95)',
].join('\n'));
execFileSync('python3', [path.join(pasta, 'fazer-fotos.py'), pasta]);

const head = '<title>Página de controle</title><meta name="viewport" content="width=device-width,initial-scale=1">';
const estilo = '<style>body{margin:0;font:18px Arial;background:#fff;color:#111}section{padding:48px 32px;min-height:220px}h1,h2,h3{margin:0 0 16px}p{max-width:600px;line-height:1.6;margin:0 0 12px}ul{margin:0;padding:0;list-style:none}li{padding:10px 0}a,button{display:inline-block;padding:16px;background:#111;color:#fff;border:0;font:18px Arial}</style>';

const caixa = (t) => `<article style="background:#eee;padding:16px"><h3>${t}</h3><p>Descrição curta do item paralelo.</p></article>`;
const cartoes = (titulo, extra = '', attr = '') => `<section ${attr}><h2 ${extra}>${titulo}</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">${caixa('Um')}${caixa('Dois')}${caixa('Três')}</div></section>`;
const lista = (titulo, extra = '') => `<section><h2 ${extra}>${titulo}</h2><ul><li>Primeira frase da lista.</li><li>Segunda frase da lista.</li><li>Terceira frase da lista.</li><li>Quarta frase da lista.</li></ul></section>`;
const assim = (titulo, extra = '') => `<section><h2 ${extra}>${titulo}</h2><div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;align-items:start"><div style="background:#eee;padding:16px"><h3>Largo</h3><p>Bloco largo com mais texto para pesar mais que o vizinho estreito ao lado.</p></div><div style="padding:16px;margin-top:40px"><h3>Estreito</h3><p>Bloco estreito.</p></div></div></section>`;
const ladoLista = (titulo) => `<section><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px"><h2>${titulo}</h2><ul><li>Frase um da lista.</li><li>Frase dois da lista.</li><li>Frase três da lista.</li></ul></div></section>`;
const splitImg = (titulo) => `<section><h2>${titulo}</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:center"><img src="/foto-nitida.jpg" alt="Foto de controle" style="width:100%;height:260px;object-fit:cover"><p>Texto ao lado da foto, para a seção ler como split com imagem.</p></div></section>`;
const hero = '<section><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:center"><div><h1>Título da página</h1><p>Subtítulo curto.</p><a href="#c">Ver como funciona</a></div><img src="/foto-nitida.jpg" alt="Foto de controle" style="width:100%;height:320px;object-fit:cover"></div></section>';

const servidor = http.createServer((req, res) => {
  const rota = req.url.split('?')[0];
  if (rota.endsWith('.jpg')) { res.writeHead(200, { 'Content-Type': 'image/jpeg' }); res.end(fs.readFileSync(path.join(pasta, rota.slice(1)))); return; }
  let corpo = '<main><h1>Página simples</h1></main>';
  // gate-ritmo: duas seções vizinhas com o mesmo esqueleto, mais de 1 "título centralizado + cartões".
  if (rota === '/ritmo-variado') corpo = hero + ladoLista('Situações') + cartoes('Três itens') + assim('Duas formas', 'style="text-align:center"') + lista('Passos') + lista('Dúvidas', 'style="text-align:center"') + splitImg('Fecho');
  if (rota === '/ritmo-vizinhas') corpo = hero + cartoes('Primeiro bloco') + cartoes('Segundo bloco') + lista('Passos');
  if (rota === '/ritmo-centro-cartoes') corpo = hero + cartoes('Situações', 'style="text-align:center"') + lista('Passos') + cartoes('Grupo ou particular', 'style="text-align:center"') + splitImg('Fecho');
  if (rota === '/ritmo-excecao') corpo = hero + cartoes('Primeiro bloco', '', 'data-ritmo-ok="duas grades de preço pedidas pelo cliente"') + cartoes('Segundo bloco', '', 'data-ritmo-ok="duas grades de preço pedidas pelo cliente"') + lista('Passos');
  if (rota === '/ritmo-assimetrico-nao-e-cartao') corpo = hero + cartoes('Situações', 'style="text-align:center"') + lista('Passos') + assim('Para quem é', 'style="text-align:center"') + splitImg('Fecho');
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end('<!doctype html><html lang="pt-BR"><head>' + head + estilo + '</head><body>' + corpo + '</body></html>');
});

function rodar(nome, script, args, esperado, padrao) {
  return new Promise((resolve) => {
    const filho = spawn(script.endsWith('.py') ? 'python3' : process.execPath, [script, ...args], { cwd: pasta });
    let saida = '';
    filho.stdout.on('data', (d) => { saida += d; });
    filho.stderr.on('data', (d) => { saida += d; });
    const teto = setTimeout(() => filho.kill('SIGTERM'), 180000);
    filho.on('close', (code) => {
      clearTimeout(teto);
      fs.writeFileSync(path.join(pasta, nome + '.log'), saida);
      const casou = !padrao || padrao.test(saida);
      const passou = code === esperado && casou;
      console.log(`${passou ? 'OK' : 'FALHA'} ${nome}: exit=${code}, esperado=${esperado}${padrao ? `, mensagem ${casou ? 'presente' : 'AUSENTE'}` : ''}`);
      if (!passou) console.log(saida.split('\n').slice(0, 14).map((l) => '    ' + l).join('\n'));
      resolve(passou);
    });
  });
}

async function unidade() {
  // A decisão do ritmo sem navegador.
  const resultados = [];
  const confere = (nome, ok, detalhe) => { console.log(`${ok ? 'OK' : 'FALHA'} ${nome}${ok ? '' : ': ' + detalhe}`); resultados.push(ok); };
  let m;
  try { m = await import(path.join(__dirname, 'ritmo-regras.mjs')); }
  catch (e) { confere('ritmo-regras-existe', false, e.message); return resultados; }
  const s = (nome, sig, excecao) => ({ nome, sig, excecao });
  const a = m.avaliarRitmo([s('A', 'x'), s('B', 'y'), s('C', 'x')]);
  confere('ritmo-unidade-nao-vizinhas-passa', a.falhas.length === 0, JSON.stringify(a));
  const b = m.avaliarRitmo([s('A', 'x'), s('B', 'x')]);
  confere('ritmo-unidade-vizinhas-reprova', b.falhas.length === 1 && /vizinhas/.test(b.falhas[0]), JSON.stringify(b));
  const c = m.avaliarRitmo([s('A', m.CENTRO_CARTOES), s('B', 'y'), s('C', m.CENTRO_CARTOES)]);
  confere('ritmo-unidade-dois-centro-cartoes-reprova', c.falhas.length === 1 && /no m[aá]ximo 1/.test(c.falhas[0]), JSON.stringify(c));
  const d = m.avaliarRitmo([s('A', m.CENTRO_CARTOES), s('B', 'y')]);
  confere('ritmo-unidade-um-centro-cartoes-passa', d.falhas.length === 0, JSON.stringify(d));
  const e = m.avaliarRitmo([s('A', 'x', 'motivo'), s('B', 'x')]);
  confere('ritmo-unidade-excecao-passa', e.falhas.length === 0 && e.excecoes.length === 1, JSON.stringify(e));
  const f = m.avaliarRitmo([s('A', 'sem-titulo:0'), s('B', 'sem-titulo:0')]);
  confere('ritmo-unidade-sem-titulo-nao-compara', f.falhas.length === 0, JSON.stringify(f));
  return resultados;
}

servidor.listen(0, '127.0.0.1', async () => {
  const url = `http://127.0.0.1:${servidor.address().port}`;
  const script = (nome) => path.join(__dirname, nome);
  const casos = [
    ['ritmo-variado', 'gate-ritmo.mjs', ['--url', url + '/ritmo-variado'], 0],
    ['ritmo-vizinhas', 'gate-ritmo.mjs', ['--url', url + '/ritmo-vizinhas'], 1, /seções vizinhas com o mesmo esqueleto/],
    ['ritmo-centro-cartoes', 'gate-ritmo.mjs', ['--url', url + '/ritmo-centro-cartoes'], 1, /2 seções no formato "título centralizado \+ cartões"/],
    ['ritmo-excecao', 'gate-ritmo.mjs', ['--url', url + '/ritmo-excecao'], 0, /exceção declarada/],
    ['ritmo-assimetrico-nao-e-cartao', 'gate-ritmo.mjs', ['--url', url + '/ritmo-assimetrico-nao-e-cartao'], 0],
  ];
  const resultados = [...await unidade()];
  const filtro = process.env.GATES_FILTRO;
  const selecionados = casos.filter(([nome]) => !filtro || nome.startsWith(filtro));
  for (const [nome, arquivo, args, esperado, padrao] of selecionados) {
    resultados.push(await rodar(nome, path.isAbsolute(arquivo) ? arquivo : script(arquivo), args, esperado, padrao));
  }
  console.log(`Evidências: ${pasta}`);
  console.log(`${resultados.filter(Boolean).length}/${resultados.length} controles passaram`);
  servidor.close();
  process.exitCode = resultados.every(Boolean) ? 0 : 1;
});
