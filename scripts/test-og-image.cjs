/** A29: `gerar-og-image.mjs` gera a og:image de 1200x630 com o título, a foto e o aviso "imagem ilustrativa" (foto de banco).
 *
 *  Mede o arquivo (cabeçalho JPEG: 1200x630) e, por pixel, o aviso: a faixa escura da base só existe com --ilustrativa e o
 *  HTML renderizado traz o texto. A fonte da marca vem de `fonts/` (aqui, a fonte de teste `fixtures/larga.ttf`); sem fonte o
 *  script usa a do sistema e DIZ que é reserva.
 */
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const zlib = require('node:zlib');
const { spawnSync } = require('node:child_process');
const { raizGlobal } = require('./npm-global.cjs');

function playwright() {
  try { return require('playwright'); } catch { return require(path.join(raizGlobal(), 'playwright')); }
}
let falhas = 0;
const checa = (nome, ok, d = '') => { console.log(`${ok ? 'ok   ' : 'FALHA'} ${nome}${d ? ' -> ' + d : ''}`); if (!ok) falhas++; };

function png(w, h, rgb) {
  const crc = (buf) => { let c, tabela = []; for (let n = 0; n < 256; n++) { c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; tabela[n] = c >>> 0; } let r = 0xffffffff; for (const b of buf) r = tabela[(r ^ b) & 255] ^ (r >>> 8); return (r ^ 0xffffffff) >>> 0; };
  const bloco = (tipo, dados) => { const t = Buffer.from(tipo), l = Buffer.alloc(4); l.writeUInt32BE(dados.length); const c = Buffer.alloc(4); c.writeUInt32BE(crc(Buffer.concat([t, dados]))); return Buffer.concat([l, t, dados, c]); };
  const linha = Buffer.concat([Buffer.from([0]), Buffer.from(Array.from({ length: w }, () => rgb).flat())]);
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 2;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), bloco('IHDR', ihdr), bloco('IDAT', zlib.deflateSync(Buffer.concat(Array.from({ length: h }, () => linha)))), bloco('IEND', Buffer.alloc(0))]);
}
function tamanhoJpeg(arq) {
  const b = fs.readFileSync(arq);
  let i = 2;
  while (i < b.length) { if (b[i] !== 0xff) { i++; continue; } const m = b[i + 1]; const len = b.readUInt16BE(i + 2); if (m >= 0xc0 && m <= 0xc3) return { h: b.readUInt16BE(i + 5), w: b.readUInt16BE(i + 7) }; i += 2 + len; }
  return null;
}
const rodar = (args) => spawnSync(process.execPath, [path.join(__dirname, 'gerar-og-image.mjs'), ...args], { encoding: 'utf8' });

(async () => {
  const proj = fs.mkdtempSync(path.join(os.tmpdir(), 'og-prova-'));
  fs.mkdirSync(path.join(proj, 'fonts'));
  fs.copyFileSync(path.join(__dirname, 'fixtures', 'larga.ttf'), path.join(proj, 'fonts', 'marca.ttf'));
  fs.writeFileSync(path.join(proj, 'foto.png'), png(400, 300, [200, 160, 90]));
  const { chromium } = playwright();
  const b = await chromium.launch();
  const p = await b.newPage();
  const pixel = async (arq, x, y) => p.evaluate(async ({ b64, x, y }) => {
    const img = new Image(); img.src = 'data:image/jpeg;base64,' + b64; await img.decode();
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const g = c.getContext('2d'); g.drawImage(img, 0, 0);
    return Array.from(g.getImageData(x, y, 1, 1).data);
  }, { b64: fs.readFileSync(arq).toString('base64'), x, y });

  // 1. foto de banco: 1200x630, aviso na base, fonte da marca
  const r1 = rodar(['--projeto', proj, '--titulo', 'Móveis sob medida em madeira maciça', '--foto', 'foto.png', '--ilustrativa', '--saida', 'og-banco.jpg', '--html-saida', 'og-banco.html']);
  checa('sai 0 com foto de banco', r1.status === 0, (r1.stderr || '').split('\n')[0]);
  const t1 = tamanhoJpeg(path.join(proj, 'og-banco.jpg'));
  checa('o arquivo tem 1200x630', t1 && t1.w === 1200 && t1.h === 630, JSON.stringify(t1));
  const html1 = fs.readFileSync(path.join(proj, 'og-banco.html'), 'utf8');
  checa('o aviso "imagem ilustrativa" está no texto renderizado', /Imagem ilustrativa/.test(html1));
  const base = await pixel(path.join(proj, 'og-banco.jpg'), 900, 610);
  checa('a faixa do aviso na base é escura (pixel)', base[0] < 60 && base[1] < 60 && base[2] < 60, JSON.stringify(base));
  checa('a saída diz que usou a fonte da marca de fonts/', /fonte da marca.*marca\.ttf/i.test(r1.stdout), r1.stdout.split('\n').find((l) => /fonte/i.test(l)) || '');
  checa('o título está no HTML', /Móveis sob medida em madeira maciça/.test(html1));

  // 2. foto do cliente: sem aviso
  const r2 = rodar(['--projeto', proj, '--titulo', 'Móveis sob medida', '--foto', 'foto.png', '--saida', 'og-cliente.jpg', '--html-saida', 'og-cliente.html']);
  checa('sai 0 com foto do cliente', r2.status === 0, (r2.stderr || '').split('\n')[0]);
  checa('sem --ilustrativa não há aviso no HTML', !/Imagem ilustrativa/.test(fs.readFileSync(path.join(proj, 'og-cliente.html'), 'utf8')));
  const base2 = await pixel(path.join(proj, 'og-cliente.jpg'), 900, 610);
  checa('sem aviso a base NÃO é a faixa escura', base2[0] > 100, JSON.stringify(base2));

  // 3. sem fonte em fonts/: usa a do sistema e diz que é reserva
  fs.rmSync(path.join(proj, 'fonts', 'marca.ttf'));
  const r3 = rodar(['--projeto', proj, '--titulo', 'Móveis sob medida', '--foto', 'foto.png', '--ilustrativa', '--saida', 'og-reserva.jpg']);
  checa('sem fonte da marca, sai 0 e diz que usou a do sistema como reserva', r3.status === 0 && /reserva/i.test(r3.stdout) && /fonte do sistema/i.test(r3.stdout), r3.stdout.split('\n').find((l) => /fonte/i.test(l)) || r3.stderr.split('\n')[0]);

  // 4. título vazio ou foto que não existe: erro claro
  const r4 = rodar(['--projeto', proj, '--titulo', '', '--saida', 'x.jpg']);
  checa('título vazio é recusado', r4.status === 2, String(r4.status));
  const r5 = rodar(['--projeto', proj, '--titulo', 'Oi', '--foto', 'nao-existe.png', '--saida', 'x.jpg']);
  checa('foto que não existe é recusada com o caminho', r5.status === 1 && /nao-existe\.png/.test(r5.stderr), r5.stderr.split('\n')[0]);

  await b.close();
  console.log(falhas ? `\n${falhas} falha(s). ${proj}` : '\nog:image gerada e medida.');
  process.exit(falhas ? 1 : 0);
})();
