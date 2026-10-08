/** O print do topo espera a animação de entrada acabar (achado A13, teste de ponta a ponta de 08/10/2026).
 *
 *  Defeito: no PNG do desktop faltavam a lista de fatos e o encaixe do herói (opacity 0 no meio da
 *  entrada), embora existissem na página. O aluno pensaria que o conteúdo sumiu.
 *
 *  Controle: página cujo bloco vermelho (200x100, no topo) entra com uma animação linear de 1,5 s que
 *  COMEÇA quando a rolagem volta ao topo (é o que a entrada de uma página real faz depois que o
 *  screenshot-prova.js percorre a página). O print só vale com o vermelho PURO (opacidade 1) e a
 *  saída tem de dizer quanto esperou. Segundo controle (A13, atualização): página cuja animação
 *  REINICIA quando a janela muda de tamanho, que é o que o `fullPage` do Playwright provoca (no teste
 *  do aluno, a entrada do herói voltou a opacidade 0 durante o print de página inteira). O print tem
 *  de sair com o estado final, não com a entrada recomeçada. Outra página, com uma animação infinita (um loop decorativo),
 *  não pode travar a prova: o teto de 4 s vale e a saída diz que ainda havia animação rodando.
 */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn } = require('node:child_process');
const { raizGlobal } = require('./npm-global.cjs');

function playwright() {
  try { return require('playwright'); } catch { return require(path.join(raizGlobal(), 'playwright')); }
}

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'espera-entrada-'));
const base = (corpo, estilo) => '<!doctype html><html lang="pt-BR"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controle</title>'
  + `<style>body{margin:0;font:18px Arial}.alvo{width:200px;height:100px;margin:20px;background:rgb(255,0,0)}${estilo}</style></head><body>${corpo}</body></html>`;
const PAGINAS = {
  // a entrada de 1,5 s começa quando a rolagem volta ao topo
  '/entrada': base('<div class="alvo" id="a"></div>' + Array.from({ length: 12 }, (_, i) => `<section style="height:600px"><p>Seção ${i}</p></section>`).join('')
    + '<script>var desceu=false;addEventListener("scroll",function(){if(scrollY>400)desceu=true;if(desceu&&scrollY===0&&!document.getElementById("a").classList.contains("entra")){document.getElementById("a").classList.add("entra");}});</script>',
  '.alvo{opacity:1}.alvo.entra{animation:entra 1.5s linear both}@keyframes entra{from{opacity:0}to{opacity:1}}'),
  // a entrada de 1,5 s roda no carregamento e REINICIA a cada resize (o fullPage redimensiona a janela)
  '/reinicia': base('<div class="alvo entra" id="a"></div>' + Array.from({ length: 12 }, (_, i) => `<section style="height:600px"><p>Seção ${i}</p></section>`).join('')
    + '<script>addEventListener("resize",function(){var a=document.getElementById("a");a.classList.remove("entra");void a.offsetWidth;a.classList.add("entra");});</script>',
  '.alvo.entra{animation:entra 1.5s linear both}@keyframes entra{from{opacity:0}to{opacity:1}}'),
  // animação infinita decorativa: o teto de 4 s tem que valer
  '/loop': base('<div class="alvo"></div><div class="gira" style="width:40px;height:40px;background:#00f"></div>' + Array.from({ length: 3 }, (_, i) => `<section style="height:600px"><p>Seção ${i}</p></section>`).join(''),
    '.gira{animation:g 1s linear infinite}@keyframes g{to{transform:translateX(100px)}}'),
  // sem animação nenhuma: não pode esperar à toa
  '/parada': base('<div class="alvo"></div><section style="height:900px"><p>Parada</p></section>', ''),
};
const servidor = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(PAGINAS[req.url.split('?')[0]] || PAGINAS['/parada']);
});

const rodar = (url, saida) => new Promise((resolve) => {
  const filho = spawn(process.execPath, [path.join(__dirname, 'screenshot-prova.js'), url, saida, '--sem-identidade']);
  let log = '';
  filho.stdout.on('data', (d) => { log += d; });
  filho.stderr.on('data', (d) => { log += d; });
  filho.on('close', (c) => resolve({ code: c, log }));
});

servidor.listen(0, '127.0.0.1', async () => {
  const porta = servidor.address().port;
  const { chromium } = playwright();
  const b = await chromium.launch();
  const p = await b.newPage();
  let falhas = 0;
  const checa = (nome, ok, detalhe = '') => { console.log(`  [${ok ? 'ok  ' : 'FALHA'}] ${nome}${detalhe ? ' -> ' + detalhe : ''}`); if (!ok) falhas++; };
  const pixel = async (arq, x, y) => p.evaluate(async ({ b64, x, y }) => {
    const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
    const g = c.getContext('2d'); g.drawImage(img, 0, 0);
    return Array.from(g.getImageData(x, y, 1, 1).data);
  }, { b64: fs.readFileSync(arq).toString('base64'), x, y });

  const e = await rodar(`http://127.0.0.1:${porta}/entrada`, path.join(pasta, 'entrada'));
  checa('prova da página com entrada de 1,5 s sai 0', e.code === 0, e.log.split('\n').slice(-3).join(' | '));
  const px = await pixel(path.join(pasta, 'entrada', 'prova-desktop.png'), 100, 70);
  checa('o bloco da entrada aparece COM a opacidade cheia no print do desktop', px[0] === 255 && px[1] === 0 && px[2] === 0, JSON.stringify(px));
  checa('a saída diz quanto esperou a entrada', /entrada\s+desktop: esperou \d+ ms/.test(e.log), (e.log.match(/entrada .*/) || [''])[0]);
  const ms = Number((e.log.match(/entrada\s+desktop: esperou (\d+) ms/) || [0, -1])[1]);
  checa('esperou de verdade (mais de 100 ms) e dentro do teto de 4 s', ms > 100 && ms <= 4300, String(ms));

  const r = await rodar(`http://127.0.0.1:${porta}/reinicia`, path.join(pasta, 'reinicia'));
  checa('prova da página que reinicia a entrada no resize sai 0', r.code === 0, r.log.split('\n').slice(-3).join(' | '));
  for (const nome of ['desktop', 'mobile']) {
    const arq = path.join(pasta, 'reinicia', `prova-${nome}.png`);
    const escala = nome === 'desktop' ? 1 : 2;
    const px2 = await pixel(arq, 100 * escala, 70 * escala);
    checa(`o bloco volta ao estado final no print ${nome}, mesmo com o resize que reinicia a entrada`, px2[0] === 255 && px2[1] === 0 && px2[2] === 0, JSON.stringify(px2));
  }

  const l = await rodar(`http://127.0.0.1:${porta}/loop`, path.join(pasta, 'loop'));
  checa('animação infinita não trava a prova (sai 0)', l.code === 0, l.log.split('\n').slice(-3).join(' | '));
  const msl = Number((l.log.match(/entrada\s+desktop: esperou (\d+) ms/) || [0, -1])[1]);
  checa('com animação infinita a espera não passa do teto', msl >= 0 && msl <= 400, String(msl));

  const q = await rodar(`http://127.0.0.1:${porta}/parada`, path.join(pasta, 'parada'));
  const msq = Number((q.log.match(/entrada\s+desktop: esperou (\d+) ms/) || [0, -1])[1]);
  checa('página sem animação quase não espera', q.code === 0 && msq >= 0 && msq < 600, String(msq));

  await b.close();
  servidor.close();
  console.log(falhas ? `\n  ${falhas} falha(s). Evidências: ${pasta}\n` : '\n  Print do topo espera a entrada.\n');
  process.exit(falhas ? 1 : 0);
});
