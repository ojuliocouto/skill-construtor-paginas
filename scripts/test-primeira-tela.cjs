/** G22 (3.5.10): primeira tela VISÍVEL no celular, descontadas as barras do navegador.
 *
 *  Duas páginas reais passaram em todos os gates com o topo errado no celular:
 *   - v7 do Studio Equilíbrio (antes do conserto): foto quadrada de 390 px, botão em 810 de 844. Na área que o Safari mostra com
 *     as barras (390x664) o botão terminava 146 px abaixo da dobra; o gate media contra a janela cheia de 844.
 *   - Torra Clara (3.5.8): manchete de 4 linhas e o texto de apoio depois do botão; em 390x664 o apoio fica cortado na dobra e em
 *     360x616 fica fora.
 *  As páginas abaixo reproduzem os dois casos e o falso positivo do link da marca dentro do herói (o gate antigo escolhia o link
 *  "Torra Clara", com caixa 0x0, como botão do herói, e passava sempre). Rodam com `--so-primeira-tela` (só as telas visíveis).
 */
const http = require('node:http');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');

const temPlaywright = () => {
  try { require('playwright'); return true; } catch { /* segue */ }
  const r = spawnSync('npm', ['root', '-g'], { encoding: 'utf8', shell: process.platform === 'win32' });
  try { require(path.join((r.stdout || '').trim(), 'playwright')); return true; } catch { return false; }
};
if (!temPlaywright()) { console.log('PULADO: Playwright ausente, primeira tela NAO VERIFICADA'); process.exit(0); }

const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64');
const estilo = '<style>body{margin:0;font:18px/1.5 Arial;color:#111;background:#fff}section{padding:0 0 24px}.t{padding:0 20px}h1{font:700 40px/1.1 Arial;margin:16px 0 12px}p{margin:0 0 16px}'
  + '.botao{display:inline-block;padding:16px 24px;background:#111;color:#fff;text-decoration:none;border-radius:12px}.marca{display:inline-block;padding:10px 14px;background:#222;color:#fff;border-radius:10px}'
  + 'img{display:block;width:100%;height:auto;object-fit:cover}header{height:64px;padding:12px 20px;box-sizing:border-box}</style>';
const foto = (css) => `<img src="/foto.png" width="1200" height="1200" alt="Foto de controle" style="${css}">`;
const apoio = '<p class="abre">Texto de apoio do topo, que diz o que é, para quem e como funciona, em duas linhas no celular.</p>';
const longo = '<p>' + 'Texto corrido da seção seguinte. '.repeat(40) + '</p>';
const ROTAS = {
  // faixa de foto, manchete curta, apoio e botão: tudo dentro de 390x664 e 360x616
  '/ok-faixa': `<section id="topo">${foto('aspect-ratio:11/8')}<div class="t"><h1>Suas costas, cuidadas de perto.</h1>${apoio}<a class="botao" href="#c">Ver como é</a></div></section>${longo}`,
  // v7 antiga: cabeçalho de 64 px, foto quadrada da largura da tela, legenda no fluxo; botão abaixo de 664
  '/foto-quadrada': `<header>Marca</header><section id="topo">${foto('aspect-ratio:1/1')}<div class="t"><p style="font-size:14px">Foto acima: imagem ilustrativa de banco de imagens.</p><h1>Suas costas, cuidadas de perto.</h1>${apoio}<a class="botao" href="#c">Ver como é</a></div></section>${longo}`,
  // Torra Clara: foto 5:4, manchete em 4 linhas, botão e o apoio DEPOIS do botão
  '/apoio-depois': `<section id="topo">${foto('aspect-ratio:5/4')}<div class="t"><h1 style="font-size:52px;line-height:1">Café torrado na semana em que sai para a sua casa.</h1><a class="botao" href="#c">Ver de onde vem</a>${apoio}</div></section>${longo}`,
  // o link da marca (com fundo, apontando para o próprio topo) vem antes do h1; o botão de verdade fica abaixo da dobra
  '/marca-no-heroi': `<section id="topo"><div class="t"><a class="marca" href="#topo">Torra Clara</a></div>${foto('aspect-ratio:3/4')}<div class="t"><h1>Café torrado na semana.</h1>${apoio}<a class="botao" href="#c">Ver de onde vem</a></div></section>${longo}`,
  // conflito resolvido: foto de 26% porque manchete, apoio e botão ocupam o resto; o texto ganha e a foto fica no piso
  '/texto-ganha': `<section id="topo">${foto('height:24svh')}<div class="t"><h1>Suas costas.</h1><p class="abre" style="height:calc(76svh - 167px)">Texto de apoio longo do topo, que ocupa o resto da tela.</p><a class="botao" href="#c">Ver como é</a></div></section>${longo}`,
  // foto de 26% com a tela sobrando embaixo: não há conflito, a foto é que está pequena
  '/foto-pequena-sobra': `<section id="topo">${foto('height:26svh')}<div class="t"><h1>Suas costas.</h1>${apoio}<a class="botao" href="#c">Ver como é</a></div></section>${longo}`,
  // botão a 4 px do pé da área visível: inteiro, mas colado na barra do navegador
  '/botao-colado': `<section id="topo" style="position:relative;height:100svh;padding:0"><div class="t" style="position:absolute;left:0;right:0;bottom:4px"><h1>Suas costas.</h1>${apoio}<a class="botao" href="#c">Ver como é</a></div></section>${longo}`,
};
const servidor = http.createServer((req, res) => {
  const rota = req.url.split('?')[0];
  if (rota === '/foto.png') { res.writeHead(200, { 'Content-Type': 'image/png' }); res.end(png); return; }
  const corpo = ROTAS[rota];
  res.writeHead(corpo ? 200 : 404, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(corpo ? `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controle</title>${estilo}</head><body>${corpo}</body></html>` : '');
});

const rodar = (url) => new Promise((ok) => {
  const p = spawn(process.execPath, [path.join(__dirname, 'gate-responsivo.mjs'), '--url', url, '--so-primeira-tela']);
  let out = '';
  p.stdout.on('data', (d) => { out += d; });
  p.stderr.on('data', (d) => { out += d; });
  const teto = setTimeout(() => p.kill('SIGTERM'), 180000);
  p.on('close', (status) => { clearTimeout(teto); ok({ status, out }); });
});

const CASOS = [
  ['faixa com manchete, apoio e botão dentro passa', '/ok-faixa', 0, /primeira tela vis[ií]vel 390x664[^\n]*manchete \d+ a \d+[^\n]*apoio \d+ a \d+[^\n]*bot[aã]o \d+ a \d+[^\n]*folga \d+ px/],
  ['v7 antiga: foto quadrada empurra o botão para fora de 390x664', '/foto-quadrada', 1, /390x664[^\n]*bot[aã]o principal "Ver como [eé]" termina em \d+ px, fora da [aá]rea vis[ií]vel de 664/],
  ['Torra Clara: apoio depois do botão fica fora da primeira tela', '/apoio-depois', 1, /texto de apoio[^\n]*fora da [aá]rea vis[ií]vel/],
  ['o link da marca para o próprio topo não é o botão principal', '/marca-no-heroi', 1, /bot[aã]o principal "Ver de onde vem" termina em/],
  ['texto ganha da foto: foto no piso de 20% com manchete, apoio e botão ocupando o resto passa', '/texto-ganha', 0, /foto \d+ px \([\d.]+%, piso [^\n]*o texto ocupa o resto\)/],
  ['foto pequena com a tela sobrando reprova', '/foto-pequena-sobra', 1, /foto do her[oó]i ocupa \d+ px da [aá]rea vis[ií]vel[^\n]*m[ií]nimo 35%/],
  ['botão colado no pé (menos de 8 px) reprova', '/botao-colado', 1, /bot[aã]o principal[^\n]*folga de \d px no p[eé] \(m[ií]nimo 8\)/],
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
      if (!ok) { falhas++; console.log(`FALHA ${nome}: saída ${status}, esperado ${esperado}\n${out.slice(-1800)}`); }
      else console.log(`ok    ${nome}`);
    });
  }
  servidor.close();
  console.log(falhas ? `${falhas} falha(s)` : 'todos os controles da primeira tela passaram');
  process.exit(falhas ? 1 : 0);
});
