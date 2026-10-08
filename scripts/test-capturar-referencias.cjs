/** Captura de referências contra páginas locais: dois prints diferentes por página, manifesto
 *  gravado com lido:false, e o gate de referências reprovando até a leitura existir. */
const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');

// O servidor mora neste processo: spawnSync travaria o laço de eventos e a página nunca responderia.
const rodar = (cmd, argv) => new Promise((ok) => {
  const p = spawn(cmd, argv, { env: process.env });
  let out = '', err = '';
  p.stdout.on('data', (d) => { out += d; });
  p.stderr.on('data', (d) => { err += d; });
  p.on('close', (status) => ok({ status, stdout: out, stderr: err }));
});

const AQUI = __dirname;
const projeto = fs.mkdtempSync(path.join(os.tmpdir(), 'capturar-ref-'));
const cores = ['#d8e2dc', '#ffe5d9', '#cfe1f2'];
const LONGO = 'Móveis sob medida em madeira maciça, desenhados para a medida da sua casa e entregues montados. '.repeat(12);
const ESTILO = '<style>body{margin:0;font:20px Georgia;background:#f4efe6}main{padding:60px}h1{font-size:44px}</style>';
const pagina = (titulo, corpo, extra = '') =>
  `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>${titulo}</title>${extra}</head><body>${corpo}</body></html>`;
const servidor = http.createServer((req, res) => {
  const rota = req.url.split('?')[0];
  const html = (cod, corpo) => { res.writeHead(cod, { 'Content-Type': 'text/html; charset=utf-8' }); res.end(corpo); };
  if (rota === '/403') return html(403, pagina('403 Forbidden', '<h1>Forbidden</h1><p>You do not have permission to access this resource.</p>'));
  if (rota === '/404') return html(404, pagina('Não encontrada', `<main><h1>Página não encontrada</h1><p>${LONGO}</p></main>`, ESTILO));
  if (rota === '/desafio') return html(200, pagina('Just a moment...', '<h1>Verificando se você é humano</h1><p>Este processo é automático. Aguarde.</p>', ESTILO));
  if (rota === '/semestilo') return html(200, pagina('Marcenaria', `<h1>Marcenaria</h1><p>${LONGO.repeat(8)}</p><p><a href="/a">Contato</a> <a href="/b">Obras</a></p>`));
  if (rota === '/folhasolta') return html(200, pagina('Folha que não pegou', `<h1>Marcenaria</h1><p>${LONGO.repeat(8)}</p><p><a href="/a">Contato</a> <a href="/b">Obras</a> <a href="/c">Cart</a></p>`, '<style>.nada{color:red}</style>'));
  if (rota === '/cookie') return html(200, pagina('Com aviso de cookies', `<main><h1>Ateliê</h1><p>${LONGO.repeat(10)}</p></main>
    <div id="aviso" style="position:fixed;inset:0;z-index:99;background:rgba(0,0,0,.7);color:#fff;padding:80px"><p>Usamos cookies.</p><button onclick="document.getElementById('aviso').remove()">Aceitar todos</button></div>`, ESTILO));
  if (rota === '/modal') return html(200, pagina('Com modal de região', `<main><h1>Ateliê</h1><p>${LONGO.repeat(10)}</p></main>
    <div role="dialog" aria-modal="true" style="position:fixed;left:10%;top:5%;width:80%;height:80%;z-index:99;background:#fff;border:2px solid #000;padding:40px"><p>Escolha a sua região para continuar.</p><button>Brasil</button><button>Portugal</button></div>`, ESTILO));
  // 3.5.8 (N1): herói que não rendeu (dobra branca) e meio com fotos que não chegaram (blocos chapados)
  if (rota === '/brancadobra') return html(200, pagina('Herói em vídeo', `<div style="height:900px;background:#fff"></div><main><h1>Ateliê</h1><p>${LONGO.repeat(12)}</p></main><div style="height:1400px"></div>`, ESTILO.replace('background:#f4efe6', 'background:#fff')));
  if (rota === '/fotas') {
    const sec = (i) => `<section style="height:700px;background:#5b3a29;color:#fff;padding:40px"><p>Obra ${i}</p><img src="/nao-existe-${i}.jpg" alt="" width="300" height="200"></section>`;
    return html(200, pagina('Fotos que não carregam', `<section style="height:900px;background:linear-gradient(90deg,#fff 50%,#222 50%);padding:60px;font:32px Georgia">${LONGO.slice(0, 300)}</section>${[1, 2, 3, 4, 5, 6, 7, 8].map(sec).join('')}`, ESTILO));
  }
  // foto que só começa a carregar quando entra na tela (IntersectionObserver) e demora 3,5 s: sem esperar o carregamento, o print do meio sai com blocos chapados
  if (rota === '/lentas') {
    const sec = (i) => `<section style="height:700px;background:#5b3a29;color:#fff;padding:40px"><p>Obra ${i}</p><img data-src="/lenta-${i}.png" alt="" width="300" height="200"></section>`;
    return html(200, pagina('Fotos lentas', `<section style="height:900px;background:linear-gradient(90deg,#fff 50%,#222 50%);padding:60px;font:32px Georgia">${LONGO.slice(0, 300)}</section>${[1, 2, 3, 4, 5, 6, 7, 8].map(sec).join('')}<script>const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting && !e.target.src) e.target.src = e.target.dataset.src; })); document.querySelectorAll('img[data-src]').forEach((im) => io.observe(im));</script>`, ESTILO));
  }
  if (rota.startsWith('/lenta-')) {
    const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAY' + 'AAAAfFcSJAAAADUlEQVR4nGP4z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg==', 'base64');
    return setTimeout(() => { res.writeHead(200, { 'Content-Type': 'image/png' }); res.end(png); }, 3500);
  }
  if (rota.startsWith('/nao-existe')) { res.writeHead(404); return res.end(); }
  if (rota === '/curta') return html(200, pagina('Página curta', `<main><h1>Ateliê</h1><p>${LONGO}</p></main>`, ESTILO));
  const n = Number((req.url.match(/\d+/) || ['0'])[0]);
  const blocos = Array.from({ length: 8 }, (_, i) =>
    `<section style="height:700px;background:${cores[(i + n) % 3]};padding:60px;font:32px Georgia">Seção ${i + 1} da página ${n}. ${LONGO.slice(0, 200)}</section>`).join('');
  html(200, `<!doctype html><html lang="pt-BR"><head><title>Referência ${n}</title></head><body style="margin:0">${blocos}</body></html>`);
});

let falhas = 0;
const checa = (nome, ok, detalhe = '') => {
  console.log(`  [${ok ? 'ok  ' : 'FALHA'}] ${nome}${detalhe ? ' -> ' + detalhe : ''}`);
  if (!ok) falhas++;
};

servidor.listen(0, '127.0.0.1', async () => {
  const porta = servidor.address().port;
  const r = await rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto, '--tipo', 'design',
    '--minimo', '2', `http://127.0.0.1:${porta}/1`, `http://127.0.0.1:${porta}/2`]);
  checa('captura sai 0 quando há referências boas o bastante', r.status === 0, (r.stderr || '').split('\n')[0]);
  const manifesto = path.join(projeto, 'referencias', 'referencias.json');
  checa('manifesto gravado', fs.existsSync(manifesto));
  const doc = fs.existsSync(manifesto) ? JSON.parse(fs.readFileSync(manifesto, 'utf8')) : { referencias: [] };
  checa('duas entradas no manifesto', doc.referencias.length === 2, String(doc.referencias.length));
  for (const ref of doc.referencias) {
    const dobra = path.join(projeto, ref.prints.dobra);
    const meio = path.join(projeto, ref.prints.meio);
    checa(`${ref.titulo}: dobra e meio existem`, fs.existsSync(dobra) && fs.existsSync(meio));
    checa(`${ref.titulo}: dobra e meio são prints diferentes`,
      fs.existsSync(dobra) && fs.existsSync(meio) && !fs.readFileSync(dobra).equals(fs.readFileSync(meio)));
    checa(`${ref.titulo}: leitura nasce vazia e lido:false`, ref.lido === false && ref.principio === '');
  }
  const again = await rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto, '--tipo', 'design',
    '--minimo', '2', `http://127.0.0.1:${porta}/1`]);
  const doc2 = JSON.parse(fs.readFileSync(manifesto, 'utf8'));
  checa('recapturar a mesma url não duplica a entrada', again.status === 0 && doc2.referencias.length === 2,
    String(doc2.referencias.length));
  const gate = await rodar(process.execPath, [path.join(AQUI, 'py.mjs'), 'gate-referencias.py', '--projeto', projeto]);
  checa('gate reprova enquanto a leitura não existe', gate.status === 1, String(gate.status));
  // ---- A1: a captura olha o que capturou (08/10/2026) ----
  const base = `http://127.0.0.1:${porta}`;
  const projeto2 = fs.mkdtempSync(path.join(os.tmpdir(), 'capturar-ref2-'));
  const cap = (...urls) => rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto2, '--tipo', 'mesmo-negocio', ...urls.map((u) => base + u)]);
  const r2 = await cap('/1', '/403', '/desafio', '/semestilo', '/folhasolta', '/cookie', '/modal', '/curta', '/404');
  const man2 = JSON.parse(fs.readFileSync(path.join(projeto2, 'referencias', 'referencias.json'), 'utf8'));
  const estado = (rota) => (man2.referencias.find((x) => x.url === base + rota) || {}).captura || {};
  checa('403 Forbidden é bloqueada', estado('/403').estado === 'bloqueada', JSON.stringify(estado('/403')));
  checa('desafio "Just a moment" com HTTP 200 é bloqueada', estado('/desafio').estado === 'bloqueada', JSON.stringify(estado('/desafio')));
  checa('404 é quebrada', estado('/404').estado === 'quebrada', JSON.stringify(estado('/404')));
  checa('página sem folha de estilo é quebrada', estado('/semestilo').estado === 'quebrada', JSON.stringify(estado('/semestilo')));
  checa('folha declarada que não pegou (links azuis padrão) é quebrada', estado('/folhasolta').estado === 'quebrada', JSON.stringify(estado('/folhasolta')));
  checa('aviso de cookies com botão Aceitar é fechado e a página é ok', estado('/cookie').estado === 'ok', JSON.stringify(estado('/cookie')));
  checa('modal de região que não fecha é coberta', estado('/modal').estado === 'coberta', JSON.stringify(estado('/modal')));
  checa('página boa é ok', estado('/1').estado === 'ok', JSON.stringify(estado('/1')));
  checa('página curta de verdade com conteúdo é ok', estado('/curta').estado === 'ok', JSON.stringify(estado('/curta')));
  checa('motivo escrito para cada captura ruim', ['/403', '/desafio', '/404', '/semestilo', '/modal'].every((x) => (estado(x).motivo || '').length > 10));
  checa('sobraram menos referências boas que o mínimo: sai diferente de zero', r2.status === 1, String(r2.status));
  checa('a saída diz o estado de cada URL', /bloqueada/.test(r2.stdout + r2.stderr) && /coberta/.test(r2.stdout + r2.stderr) && /quebrada/.test(r2.stdout + r2.stderr));
  const gate2 = await rodar(process.execPath, [path.join(AQUI, 'py.mjs'), 'gate-referencias.py', '--projeto', projeto2]);
  checa('gate reprova referência marcada como bloqueada', /bloqueada/.test(gate2.stdout) && gate2.status === 1, gate2.stdout.split('\n').find((l) => /bloqueada/.test(l)) || '');
  const curta = man2.referencias.find((x) => x.url === base + '/curta');
  checa('página curta: altura registrada cabe numa janela', curta && curta.altura_pagina <= 905, String(curta && curta.altura_pagina));
  const limpa = await rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto2, '--limpar-ruins']);
  const man3 = JSON.parse(fs.readFileSync(path.join(projeto2, 'referencias', 'referencias.json'), 'utf8'));
  checa('--limpar-ruins tira do manifesto só as ruins', man3.referencias.every((x) => x.captura.estado === 'ok') && man3.referencias.length === 3, String(man3.referencias.length));
  checa('--limpar-ruins move os PNG para descartados/referencias', fs.readdirSync(path.join(projeto2, 'descartados', 'referencias')).length >= 8);
  // ---- 3.5.8: N1 (folha lisa e foto que não carregou), N2 (numeração), N3 (--remover) ----
  const projeto3 = fs.mkdtempSync(path.join(os.tmpdir(), 'capturar-ref3-'));
  const cap3 = (...urls) => rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto3, '--tipo', 'design', '--minimo', '1', ...urls.map((u) => base + u)]);
  const man = () => JSON.parse(fs.readFileSync(path.join(projeto3, 'referencias', 'referencias.json'), 'utf8'));
  const est3 = (rota) => (man().referencias.find((x) => x.url === base + rota) || {}).captura || {};
  const r3 = await cap3('/1', '/brancadobra', '/fotas', '/curta');
  checa('N1: dobra toda branca é vazia, com o motivo', est3('/brancadobra').estado === 'vazia' && /dobra/.test(est3('/brancadobra').motivo || ''), JSON.stringify(est3('/brancadobra')));
  checa('N1: meio com fotos que não carregaram é vazia, com o motivo', est3('/fotas').estado === 'vazia' && /meio/.test(est3('/fotas').motivo || ''), JSON.stringify(est3('/fotas')));
  await cap3('/lentas');
  checa('N1: foto preguiçosa que demora é esperada antes do print do meio (não vira vazia)', est3('/lentas').estado === 'ok' && est3('/lentas').imagens_sem_carregar === 0, JSON.stringify(est3('/lentas')));
  fs.rmSync(path.join(projeto3, 'referencias'), { recursive: true, force: true });
  await cap3('/1', '/brancadobra', '/fotas', '/curta');
  checa('N1: página boa e página curta de verdade seguem ok', est3('/1').estado === 'ok' && est3('/curta').estado === 'ok', JSON.stringify([est3('/1'), est3('/curta')]));
  checa('N1: a saída diz "vazia" e o gate de referências reprova a vazia', /vazia/.test(r3.stdout) && /vazia/.test((await rodar(process.execPath, [path.join(AQUI, 'py.mjs'), 'gate-referencias.py', '--projeto', projeto3])).stdout));
  const antes = man().referencias.length;
  await rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto3, '--limpar-ruins']);
  checa('N1: --limpar-ruins tira as vazias', man().referencias.every((x) => x.captura.estado === 'ok') && man().referencias.length === antes - 2, String(man().referencias.length));
  await cap3('/2', '/cookie');
  const prefixos = fs.readdirSync(path.join(projeto3, 'referencias')).filter((n) => n.endsWith('-dobra.png')).map((n) => n.split('-')[0]);
  checa('N2: depois do --limpar-ruins a numeração não se repete', new Set(prefixos).size === prefixos.length && prefixos.length === 4, prefixos.join(','));
  const usadosFora = fs.readdirSync(path.join(projeto3, 'descartados', 'referencias')).map((n) => n.split('-')[0]);
  checa('N2: o número novo também não repete o de um print descartado', prefixos.slice(2).every((x) => !usadosFora.includes(x)), `${prefixos} x ${usadosFora}`);
  const rem = await rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto3, '--remover', base + '/curta']);
  checa('N3: --remover tira do manifesto a referência ok que não serve e move os PNG', rem.status === 0 && !man().referencias.some((x) => x.url === base + '/curta') && fs.readdirSync(path.join(projeto3, 'descartados', 'referencias')).some((n) => /curta/.test(n)) && !fs.readdirSync(path.join(projeto3, 'referencias')).some((n) => /curta/.test(n)), rem.stdout + rem.stderr);
  const ambig = await rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto3, '--remover', '127.0.0.1']);
  checa('N3: trecho que casa várias referências recusa e não mexe no manifesto', ambig.status === 1 && man().referencias.length === 3, `${ambig.status} ${man().referencias.length}`);
  const nada = await rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto3, '--remover', 'https://nao-esta.example/']);
  checa('N3: endereço que não está no manifesto sai diferente de zero', nada.status === 1, String(nada.status));
  fs.rmSync(projeto3, { recursive: true, force: true });
  fs.rmSync(projeto2, { recursive: true, force: true });
  servidor.close();
  fs.rmSync(projeto, { recursive: true, force: true });
  console.log(falhas ? `\n  ${falhas} falha(s).\n` : '\n  Captura confiável.\n');
  process.exit(falhas ? 1 : 0);
});
