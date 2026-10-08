/** O print de página inteira tem que sair com o cabeçalho fixo NO TOPO.
 *
 *  Defeito que o dono viu no print da página do aluno (02/10/2026): o menu fixo e o
 *  "Pular para o conteúdo" apareceram por cima do título da primeira dobra. Medido no
 *  navegador real, em scrollY 0, o h1 estava livre: era ARTEFATO do fullPage, que pinta
 *  elemento fixed/sticky na posição da rolagem do momento da captura. Se a página (ou um
 *  script, ou a rolagem suave) não voltou ao topo, o cabeçalho sai no meio do print.
 *
 *  Controle: página com cabeçalho sticky vermelho que se rola sozinha para 500px logo
 *  depois que alguém chega ao fim dela. O print do screenshot-prova.js precisa mostrar o
 *  vermelho em y 0 a 60 e NÃO em y 520 a 580.
 */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn } = require('node:child_process');
const { raizGlobal } = require('./npm-global.cjs');

function playwright() {
  try { return require('playwright'); } catch {
    return require(path.join(raizGlobal(), 'playwright'));
  }
}

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'print-cabecalho-'));
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64');
const pagina = '<!doctype html><html lang="pt-BR"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controle</title></head>'
  + '<body style="margin:0;font:18px Arial">'
  + '<header style="position:sticky;top:0;height:64px;background:rgb(200,0,0);color:#fff;z-index:9">Menu fixo</header>'
  + '<a href="#c" style="position:fixed;top:16px;left:16px;transform:translateY(-200%);background:#00f;color:#fff;padding:12px">Pular para o conteúdo</a>'
  + '<main id="c"><h1 style="margin:80px 24px;font-size:48px">Título da primeira dobra</h1>'
  + Array.from({ length: 10 }, (_, i) => `<section style="height:600px;border-top:1px solid #ccc"><p>Seção ${i}</p></section>`).join('')
  + '</main><script>let foi=false;addEventListener("scroll",()=>{if(!foi&&scrollY+innerHeight>=document.documentElement.scrollHeight-4){foi=true;setTimeout(()=>scrollTo({top:500,behavior:"instant"}),650);}});</script>'
  + '</body></html>';

const servidor = http.createServer((req, res) => {
  if (req.url === '/icon.png') { res.writeHead(200, { 'Content-Type': 'image/png' }); res.end(png); return; }
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(pagina);
});

servidor.listen(0, '127.0.0.1', async () => {
  const url = `http://127.0.0.1:${servidor.address().port}/`;
  const saida = path.join(pasta, 'prova');
  const code = await new Promise((resolve) => {
    const filho = spawn(process.execPath, [path.join(__dirname, 'screenshot-prova.js'), url, saida, '--sem-identidade']);
    let log = '';
    filho.stdout.on('data', (d) => { log += d; });
    filho.stderr.on('data', (d) => { log += d; });
    filho.on('close', (c) => { fs.writeFileSync(path.join(pasta, 'prova.log'), log); resolve(c); });
  });
  let ok = code === 0;
  if (!ok) console.log(`FALHA: screenshot-prova saiu ${code} (log em ${pasta}/prova.log)`);
  const { chromium } = playwright();
  const b = await chromium.launch();
  const p = await b.newPage();
  for (const nome of ['desktop', 'mobile']) {
    const arq = path.join(saida, `prova-${nome}.png`);
    if (!fs.existsSync(arq)) { ok = false; console.log(`FALHA: ${arq} não existe`); continue; }
    const leitura = await p.evaluate(async (b64) => {
      const img = new Image();
      img.src = 'data:image/png;base64,' + b64;
      await img.decode();
      const c = document.createElement('canvas');
      c.width = img.width; c.height = img.height;
      const g = c.getContext('2d');
      g.drawImage(img, 0, 0);
      const escala = img.width > 1000 ? 1 : 2; // mobile sai em DPR 2
      const vermelho = (y) => { const d = g.getImageData(Math.round(img.width * 0.6), y * escala, 1, 1).data; return d[0] > 150 && d[1] < 60 && d[2] < 60; };
      return { topo: vermelho(30), meio: vermelho(550) };
    }, fs.readFileSync(arq).toString('base64'));
    const passou = leitura.topo && !leitura.meio;
    if (!passou) ok = false;
    console.log(`${passou ? 'OK' : 'FALHA'} ${nome}: cabeçalho no topo=${leitura.topo}, cabeçalho no meio do print=${leitura.meio}`);
  }
  await b.close();
  servidor.close();
  console.log(ok ? 'Print de página inteira com cabeçalho no lugar.' : `Print com cabeçalho fora do lugar. Evidências: ${pasta}`);
  process.exitCode = ok ? 0 : 1;
});
