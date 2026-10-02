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
const servidor = http.createServer((req, res) => {
  const n = Number((req.url.match(/\d+/) || ['0'])[0]);
  const blocos = Array.from({ length: 8 }, (_, i) =>
    `<section style="height:700px;background:${cores[(i + n) % 3]};padding:60px;font:32px Georgia">Seção ${i + 1} da página ${n}</section>`).join('');
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html lang="pt-BR"><head><title>Referência ${n}</title></head><body style="margin:0">${blocos}</body></html>`);
});

let falhas = 0;
const checa = (nome, ok, detalhe = '') => {
  console.log(`  [${ok ? 'ok  ' : 'FALHA'}] ${nome}${detalhe ? ' -> ' + detalhe : ''}`);
  if (!ok) falhas++;
};

servidor.listen(0, '127.0.0.1', async () => {
  const porta = servidor.address().port;
  const r = await rodar('node', [path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', projeto, '--tipo', 'design',
    `http://127.0.0.1:${porta}/1`, `http://127.0.0.1:${porta}/2`]);
  checa('captura sai 0', r.status === 0, (r.stderr || '').split('\n')[0]);
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
    `http://127.0.0.1:${porta}/1`]);
  const doc2 = JSON.parse(fs.readFileSync(manifesto, 'utf8'));
  checa('recapturar a mesma url não duplica a entrada', again.status === 0 && doc2.referencias.length === 2,
    String(doc2.referencias.length));
  const gate = await rodar('python3', [path.join(AQUI, 'gate-referencias.py'), '--projeto', projeto]);
  checa('gate reprova enquanto a leitura não existe', gate.status === 1, String(gate.status));
  servidor.close();
  fs.rmSync(projeto, { recursive: true, force: true });
  console.log(falhas ? `\n  ${falhas} falha(s).\n` : '\n  Captura confiável.\n');
  process.exit(falhas ? 1 : 0);
});
