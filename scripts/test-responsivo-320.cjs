/** 3.6.1, corte 3: a primeira tela do celular em 320 px causou 3 das 5 voltas da etapa f no teste de aluno da 3.6.0.
 *
 *  Duas causas, medidas nos laudos do projeto (gates/responsivo-r1.txt a r11.txt):
 *   - "o texto ganha, a foto cai até 20%" valia em 390 e 360 (que têm área visível medida), mas não em 320: a foto de 21,0% (119 px de
 *     568) reprovava contra o mínimo de 35% mesmo com manchete, apoio e botão ocupando o resto da tela;
 *   - 34,9% contra 35% reprovava por arredondamento (232 px de 664 em 390; 326 px de 932 em 430).
 *  A página abaixo imita o herói do Studio Equilíbrio: foto, manchete, apoio e botão, com a altura da foto em 320 trocada por caso.
 *  Fora de 320 a foto mede 42% da altura (passa em todas as telas), então só o que muda no caso é o que o gate decide em 320x568.
 *  Cada caso roda o gate inteiro (12 telas e 3 primeiras telas visíveis). */
const http = require('node:http');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');

const temPlaywright = () => {
  try { require('playwright'); return true; } catch { /* segue */ }
  const r = spawnSync('npm', ['root', '-g'], { encoding: 'utf8', shell: process.platform === 'win32' });
  try { require(path.join((r.stdout || '').trim(), 'playwright')); return true; } catch { return false; }
};
if (!temPlaywright()) { console.log('PULADO: Playwright ausente, a primeira tela em 320 NAO VERIFICADA'); process.exit(0); }

const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64');
const pagina = (foto320, folga320) => `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controle</title>`
  + '<style>body{margin:0;font:18px/1.5 Arial;color:#111;background:#fff}section{padding:0 0 24px}.t{padding:0 20px}h1{font:700 32px/1.1 Arial;margin:16px 0 12px}p{margin:0 0 16px}'
  + '.botao{display:inline-block;padding:14px 24px;background:#111;color:#fff;text-decoration:none;border-radius:12px}img{display:block;width:100%;object-fit:cover;height:42svh}'
  + `@media (max-width:330px){img{height:${foto320}px}.abre{padding-bottom:${folga320}px}}</style></head><body>`
  + '<section id="topo"><img src="/foto.png" width="1200" height="1200" alt="Foto de controle"><div class="t"><h1>Suas costas, cuidadas de perto.</h1>'
  + '<p class="abre">Texto de apoio do topo, que diz o que é, para quem e como funciona.</p><a class="botao" href="#c">Ver como é</a></div></section>'
  + `<section><div class="t"><p>${'Texto corrido da seção seguinte. '.repeat(14)}</p></div></section></body></html>`;

// [rota, foto em 320 (px), espaço extra no apoio (px) que empurra o botão para o pé de 568]
const PAGINAS = {
  // 119 px = 21,0% (o valor do laudo r2). O apoio empurra o botão até 560: a manchete, o apoio e o botão ocupam o resto da tela.
  '/texto-ganha': [119, 156],
  // a mesma foto de 21% com a tela sobrando embaixo do botão: não há conflito, a foto é que está pequena
  '/foto-pequena-sobra': [119, 0],
  // abaixo do piso de 20% (17,6%) mesmo com o texto ocupando o resto: a manchete é que está grande demais
  '/abaixo-do-piso': [100, 175],
  // 198 px = 34,86%, o caso 34,9 contra 35 do laudo r2: arredondamento, não defeito
  '/tolerancia-34-9': [198, 0],
  // 193 px = 33,98%: abaixo do mínimo mesmo com a tolerância de 0,5 ponto
  '/fora-da-tolerancia': [193, 0],
};
const servidor = http.createServer((req, res) => {
  const rota = req.url.split('?')[0];
  if (rota === '/foto.png') { res.writeHead(200, { 'Content-Type': 'image/png' }); res.end(png); return; }
  const p = PAGINAS[rota];
  res.writeHead(p ? 200 : 404, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(p ? pagina(...p) : '');
});

const rodar = (url) => new Promise((ok) => {
  const p = spawn(process.execPath, [path.join(__dirname, 'gate-responsivo.mjs'), '--url', url]);
  let out = '';
  p.stdout.on('data', (d) => { out += d; });
  p.stderr.on('data', (d) => { out += d; });
  const teto = setTimeout(() => p.kill('SIGTERM'), 240000);
  p.on('close', (status) => { clearTimeout(teto); ok({ status, out }); });
});

const CASOS = [
  ['320: o texto ganha, foto de 21% com manchete, apoio e botão ocupando o resto passa', '/texto-ganha', 0, /foto do her[oó]i 119px \(21\.0%\)[\s\S]*PASSA/],
  ['320: foto de 21% com a tela sobrando embaixo do botão continua reprovando', '/foto-pequena-sobra', 1, /menor suportado \(320x568\): foto do her[oó]i ocupa 119px[^\n]*m[ií]nimo 35%/],
  ['320: foto abaixo do piso de 20% reprova mesmo com o texto ocupando o resto', '/abaixo-do-piso', 1, /menor suportado \(320x568\): foto do her[oó]i ocupa 100px[^\n]*piso de 20%/],
  ['34,9% contra 35% passa pela tolerância de 0,5 ponto', '/tolerancia-34-9', 0, /foto do her[oó]i 198px \(34\.9%\)[\s\S]*PASSA/],
  ['33,98% fica fora da tolerância e reprova', '/fora-da-tolerancia', 1, /menor suportado \(320x568\): foto do her[oó]i ocupa 193px[^\n]*m[ií]nimo 35%/],
];

servidor.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${servidor.address().port}`;
  let falhas = 0;
  // dois navegadores por vez, no máximo (a máquina do usuário trava com carga alta)
  for (let i = 0; i < CASOS.length; i += 2) {
    const lote = CASOS.slice(i, i + 2);
    const res = await Promise.all(lote.map(([, rota]) => rodar(base + rota)));
    lote.forEach(([nome, , esperado, padrao], k) => {
      const { status, out } = res[k];
      const ok = status === esperado && (!padrao || padrao.test(out));
      if (!ok) { falhas++; console.log(`FALHA ${nome}: saída ${status}, esperado ${esperado}\n${out.slice(-2200)}`); }
      else console.log(`ok    ${nome}`);
    });
  }
  servidor.close();
  console.log(falhas ? `${falhas} falha(s)` : 'todos os controles da primeira tela em 320 passaram');
  process.exit(falhas ? 1 : 0);
});
