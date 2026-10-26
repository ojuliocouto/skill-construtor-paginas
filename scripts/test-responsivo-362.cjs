/** 3.6.2, itens 2 e 3: a dobra do celular no teste de aluno da 3.6.1 (Studio Equilíbrio, 25/10/2026).
 *
 *  Item 3. Em 320x568 o botão do herói reprovou duas vezes, a 10 px e depois a 1 px abaixo da dobra. A foto já tinha 0,5 ponto de
 *  tolerância desde a 3.6.1; o botão não. Agora o botão do herói tem tolerância de 12 px, SÓ em 320x568. Em 390 (tela de 844 e área
 *  visível de 664), 360 e 430 o botão cortado de verdade continua reprovando.
 *
 *  Item 2. O print `final-dobra-390.png` do projeto era o recorte das 663 primeiras linhas do print de página inteira em 390x844
 *  (`diff` com `provas/prova-mobile.png`: zero pixels diferentes) e mostrava o botão cortado. O gate media outra janela: 390x664, a área
 *  que o Safari mostra com as barras, e nela o botão termina em 630 (folga de 34 px). Janela do print e janela da medida eram duas.
 *  Agora (a) o gate GRAVA o print de cada janela que mediu (`--salvar-dobra <pasta>`), com a mesma largura, altura e dpr da medida;
 *  (b) quando o layout de 844 põe o botão abaixo da área visível de 664, o gate avisa que o print de página inteira não é a dobra do
 *  aparelho e diz onde está o print que é.
 *  Cada caso roda o gate de verdade num navegador. */
const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');

const temPlaywright = () => {
  try { require('playwright'); return true; } catch { /* segue */ }
  const r = spawnSync('npm', ['root', '-g'], { encoding: 'utf8', shell: process.platform === 'win32' });
  try { require(path.join((r.stdout || '').trim(), 'playwright')); return true; } catch { return false; }
};
if (!temPlaywright()) { console.log('PULADO: Playwright ausente, a dobra do celular NAO VERIFICADA'); process.exit(0); }

const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64');
// O botão tem 56 px de altura e fica em posição absoluta: o `top` de cada caso fixa onde ele termina, sem depender do texto.
const pagina = (css) => `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controle</title>`
  + '<style>body{margin:0;font:18px/1.5 Arial;color:#111;background:#fff}#topo{position:relative;min-height:100svh}.t{padding:0 20px}h1{font:700 28px/1.1 Arial;margin:16px 0 12px}p{margin:0 0 16px}'
  + '.botao{position:absolute;left:20px;display:block;height:56px;line-height:56px;padding:0 24px;background:#111;color:#fff;text-decoration:none;border-radius:12px}'
  + 'img{display:block;width:100%;object-fit:cover;height:38svh}'
  + `${css}</style></head><body>`
  + '<section id="topo"><img src="/foto.png" width="1200" height="1200" alt="Foto de controle"><div class="t"><h1>Suas costas, cuidadas.</h1>'
  + '<p>Apoio curto do topo.</p></div><a class="botao" href="#c">Ver como é</a></section>'
  + `<section><div class="t"><p>${'Texto corrido da seção seguinte. '.repeat(14)}</p></div></section></body></html>`;

// Botão a 300 px do topo (termina em 356): dentro de todas as janelas. Cada caso troca o `top` numa largura só.
const BASE = '.botao{top:300px}';
const PAGINAS = {
  '/ok': BASE,
  // 320x568: o botão termina 10 px abaixo (578) e 1 px abaixo (569), como nas duas reprovações do teste de aluno
  '/320-10px': `${BASE}@media (max-width:330px){.botao{top:522px}}`,
  '/320-1px': `${BASE}@media (max-width:330px){.botao{top:513px}}`,
  // 13 px abaixo (581): passou do limite de 12 px
  '/320-13px': `${BASE}@media (max-width:330px){.botao{top:525px}}`,
  // 430x932 (iphone pro max): 5 px abaixo da tela, sem tolerância fora de 320
  '/430-5px': `${BASE}@media (min-width:420px) and (max-width:440px){.botao{top:881px}}`,
  // 390: o botão termina em 669 (5 px abaixo da área visível de 664, mas dentro da tela de 844): reprova na janela do Safari
  '/390-cortado': `${BASE}@media (min-width:385px) and (max-width:395px){.botao{top:613px}}`,
  // 390: o botão acompanha a altura da janela (85svh): termina em 565 na área de 664 (passa) e em 713 na tela de 844 (abaixo da área)
  '/390-so-no-844': `${BASE}@media (min-width:385px) and (max-width:395px){.botao{top:calc(85svh - 62px)}}`,
};
const servidor = http.createServer((req, res) => {
  const rota = req.url.split('?')[0];
  if (rota === '/foto.png') { res.writeHead(200, { 'Content-Type': 'image/png' }); res.end(png); return; }
  const css = PAGINAS[rota];
  res.writeHead(css !== undefined ? 200 : 404, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(css !== undefined ? pagina(css) : '');
});

const rodar = (url, extra = []) => new Promise((ok) => {
  const p = spawn(process.execPath, [path.join(__dirname, 'gate-responsivo.mjs'), '--url', url, ...extra]);
  let out = '';
  p.stdout.on('data', (d) => { out += d; });
  p.stderr.on('data', (d) => { out += d; });
  const teto = setTimeout(() => p.kill('SIGTERM'), 240000);
  p.on('close', (status) => { clearTimeout(teto); ok({ status, out }); });
});

const dimensoesPng = (arquivo) => {
  const b = fs.readFileSync(arquivo);
  return b.subarray(1, 4).toString('latin1') === 'PNG' ? [b.readUInt32BE(16), b.readUInt32BE(20)] : null;
};

const CASOS = [
  ['320: botão 10 px abaixo da dobra passa pela tolerância de 12 px, com aviso', '/320-10px', 0, /PASSA/, /aviso: [^\n]*menor suportado \(320x568\)[^\n]*10 px abaixo da dobra[^\n]*toler[aâ]ncia de 12 px/],
  ['320: botão 1 px abaixo da dobra passa pela tolerância', '/320-1px', 0, /PASSA/, /aviso: [^\n]*menor suportado \(320x568\)[^\n]*1 px abaixo da dobra/],
  ['320: botão 13 px abaixo da dobra reprova', '/320-13px', 1, /FALHA: menor suportado \(320x568\): CTA do heroi "Ver como [eé]" abaixo da dobra \(termina em 581px de 568px\)/],
  ['430: botão 5 px abaixo da tela reprova (a tolerância é só de 320)', '/430-5px', 1, /FALHA: iphone pro max \(430x932\): CTA do heroi "Ver como [eé]" abaixo da dobra/],
  ['390: botão cortado na janela do Safari (664) continua reprovando', '/390-cortado', 1, /390x664[^\n]*bot[aã]o principal "Ver como [eé]" termina em 669 px, fora da [aá]rea vis[ií]vel de 664/],
  ['390: botão que passa na janela do Safari mas aparece cortado no layout de 844 avisa onde está a dobra real', '/390-so-no-844', 0, /PASSA/,
    /aviso: [^\n]*iphone padrao \(390x844\)[^\n]*bot[aã]o termina em \d+ px[^\n]*[aá]rea vis[ií]vel de 664 px[^\n]*--salvar-dobra/],
];

servidor.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${servidor.address().port}`;
  let falhas = 0;
  // dois navegadores por vez, no máximo (a máquina do usuário trava com carga alta)
  for (let i = 0; i < CASOS.length; i += 2) {
    const lote = CASOS.slice(i, i + 2);
    const res = await Promise.all(lote.map(([, rota]) => rodar(base + rota)));
    lote.forEach(([nome, , esperado, padrao, aviso], k) => {
      const { status, out } = res[k];
      const ok = status === esperado && (!padrao || padrao.test(out)) && (!aviso || aviso.test(out));
      if (!ok) { falhas++; console.log(`FALHA ${nome}: saída ${status}, esperado ${esperado}\n${out.slice(-2600)}`); }
      else console.log(`ok    ${nome}`);
    });
  }

  // Item 2: o print da dobra é o da janela medida (largura, altura e dpr 2), uma por janela da primeira tela.
  const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'dobra-362-'));
  const { status, out } = await rodar(`${base}/ok`, ['--so-primeira-tela', '--salvar-dobra', pasta]);
  // 3.7.0: a dobra de 1440x900 também (a lente do herói pedia o print de 1440 e ele saía de outro comando)
  const esperados = [['dobra-390x664.png', 780, 1328], ['dobra-360x616.png', 720, 1232], ['dobra-375x553.png', 750, 1106], ['dobra-1440x900.png', 1440, 900]];
  const erros = [];
  if (status !== 0) erros.push(`o gate saiu com ${status}`);
  for (const [nome, w, h] of esperados) {
    const arq = path.join(pasta, nome);
    const dim = fs.existsSync(arq) ? dimensoesPng(arq) : null;
    if (!dim) erros.push(`${nome} não foi gravado`);
    else if (dim[0] !== w || dim[1] !== h) erros.push(`${nome} tem ${dim[0]}x${dim[1]}, esperado ${w}x${h} (a janela medida com dpr 2)`);
    if (!out.includes(nome)) erros.push(`a saída não diz onde está ${nome}`);
  }
  if (erros.length) { falhas++; console.log(`FALHA --salvar-dobra grava o print da janela medida: ${erros.join('; ')}\n${out.slice(-1500)}`); }
  else console.log('ok    --salvar-dobra grava o print de cada janela medida, com a largura, a altura e o dpr da medida');
  fs.rmSync(pasta, { recursive: true, force: true });

  servidor.close();
  console.log(falhas ? `${falhas} falha(s)` : 'todos os controles da dobra do celular passaram');
  process.exit(falhas ? 1 : 0);
});
