/** Páginas locais controladas isolam defeitos sem depender de site de cliente. */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn, execFileSync } = require('node:child_process');

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'gates-visuais-'));
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=gray:s=320x180:r=10', '-t', '8', '-pix_fmt', 'yuv420p', path.join(pasta, 'controle.mp4')]);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', path.join(pasta, 'controle.mp4'), '-frames:v', '1', path.join(pasta, 'poster.png')]);
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64');
const head = '<title>Página de controle</title><meta name="description" content="Controle local de qualidade"><meta property="og:title" content="Controle"><meta property="og:description" content="Página de teste"><meta property="og:image" content="/icon.png"><link rel="icon" type="image/png" href="/icon.png"><link rel="apple-touch-icon" href="/icon.png">';
const style = '<style>body{margin:0;font:18px Arial;background:#fff;color:#111}section{padding:24px}button,a{display:inline-block;padding:16px;background:#111;color:white;border:0;font:18px Arial}p{max-width:600px;line-height:1.6}.kpi__value{font-size:40px}</style>';
const texto = '<section><h1>Controle da página</h1><p>Esta página permite verificar o resultado do gate com uma entrada conhecida e reproduzível.</p><button onclick="this.textContent=\'Resultado confirmado\'">Ver resultado</button></section>';
const servidor = http.createServer((req, res) => {
  if (['/controle.mp4', '/poster.png'].includes(req.url)) {
    res.writeHead(200, { 'Content-Type': req.url.endsWith('mp4') ? 'video/mp4' : 'image/png' });
    res.end(fs.readFileSync(path.join(pasta, req.url.slice(1)))); return;
  }
  if (req.url === '/icon.png') { res.writeHead(200, { 'Content-Type': 'image/png' }); res.end(png); return; }
  const rota = req.url.split('?')[0];
  let corpo = texto;
  if (rota === '/inerte') corpo = texto.replace('onclick="this.textContent=\'Resultado confirmado\'"', '');
  if (rota === '/coberto') corpo += '<div style="position:fixed;inset:0;background:white;z-index:100"></div>';
  if (rota === '/overflow') corpo += '<div style="width:3000px">Conteúdo que excede a janela</div>';
  if (rota === '/video') corpo += '<video src="/inexistente.mp4" width="320" height="180"></video>';
  if (rota === '/video-ok') corpo += '<link rel="preload" as="image" href="/poster.png" fetchpriority="high"><video src="/controle.mp4" poster="/poster.png" width="320" height="180"></video>';
  if (rota.startsWith('/dash')) corpo = '<h1>Painel 2026</h1><div class="kpi__value">' + (rota === '/dash-ok' ? 'R$ 150,00' : '&#8212;') + '</div>';
  res.writeHead(rota === '/erro' ? 500 : 200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end('<!doctype html><html lang="pt-BR"><head><meta name="viewport" content="width=device-width,initial-scale=1">' + (rota === '/sem-identidade' ? '' : head) + style + '</head><body>' + corpo + '</body></html>');
});

function rodar(nome, script, args, esperado) {
  return new Promise((resolve) => {
    const filho = spawn(process.execPath, [script, ...args], { cwd: pasta });
    let saida = '';
    filho.stdout.on('data', d => { saida += d; });
    filho.stderr.on('data', d => { saida += d; });
    const teto = setTimeout(() => filho.kill('SIGTERM'), 180000);
    filho.on('close', code => {
      clearTimeout(teto);
      fs.writeFileSync(path.join(pasta, nome + '.log'), saida);
      const passou = code === esperado;
      console.log(`${passou ? 'OK' : 'FALHA'} ${nome}: exit=${code}, esperado=${esperado}`);
      resolve(passou);
    });
  });
}

servidor.listen(0, '127.0.0.1', async () => {
  const url = `http://127.0.0.1:${servidor.address().port}`;
  const script = nome => path.join(__dirname, nome);
  const casos = [
    ['identidade-positiva', 'screenshot-prova.js', [url + '/ok', path.join(pasta, 'identidade-positiva')], 0],
    ['identidade-negativa', 'screenshot-prova.js', [url + '/sem-identidade', path.join(pasta, 'identidade-negativa')], 1],
    ['clique-inerte', 'screenshot-prova.js', [url + '/inerte', path.join(pasta, 'inerte'), '--click', 'button'], 1],
    ['clique-positivo', 'screenshot-prova.js', [url + '/ok', path.join(pasta, 'clique'), '--click', 'button'], 0],
    ['http-negativo', 'screenshot-prova.js', [url + '/erro', path.join(pasta, 'erro')], 1],
    ['oclusao-positiva', 'gate-oclusao.mjs', ['--url', url + '/ok'], 0],
    ['oclusao-negativa', 'gate-oclusao.mjs', ['--url', url + '/coberto'], 1],
    ['responsivo-positivo', 'gate-responsivo.mjs', ['--url', url + '/ok'], 0],
    ['responsivo-negativo', 'gate-responsivo.mjs', ['--url', url + '/overflow'], 1],
    ['video-ausente', 'gate-video.mjs', ['--url', url + '/ok', '--publico', pasta, '--frames', path.join(pasta, 'frames-ausente')], 0],
    ['video-positivo', 'gate-video.mjs', ['--url', url + '/video-ok', '--publico', pasta, '--frames', path.join(pasta, 'frames-positivo')], 0],
    ['video-negativo', 'gate-video.mjs', ['--url', url + '/video', '--publico', pasta, '--frames', path.join(pasta, 'frames-negativo')], 1],
  ];
  const dash = process.argv[2];
  if (dash) {
    casos.push(['dash-positivo', dash, [url + '/dash-ok', '--out', path.join(pasta, 'dash-ok')], 0]);
    casos.push(['dash-vazio', dash, [url + '/dash-vazio', '--out', path.join(pasta, 'dash-vazio')], 1]);
  }
  const resultados = [];
  const selecionados = casos.filter(([nome]) => !process.env.GATES_FILTRO || nome.startsWith(process.env.GATES_FILTRO));
  if (!selecionados.length) throw new Error('O filtro não selecionou nenhum controle.');
  // Duas execuções por vez evitam que falta de memória pareça defeito da página.
  for (let i = 0; i < selecionados.length; i += 2) {
    resultados.push(...await Promise.all(selecionados.slice(i, i + 2).map(([nome, arquivo, args, esperado]) =>
      rodar(nome, path.isAbsolute(arquivo) ? arquivo : script(arquivo), args, esperado))));
  }
  console.log(`Evidências: ${pasta}`);
  console.log(`${resultados.filter(Boolean).length}/${resultados.length} controles passaram`);
  servidor.close();
  process.exitCode = resultados.every(Boolean) ? 0 : 1;
});
