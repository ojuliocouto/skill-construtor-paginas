/**
 * Prova no navegador da receita `painel-de-cor`: serve o demo com um servidor do próprio Node e roda
 * `provar-painel.mjs` (cobre 100% da janela, solta no fim, foco e endereço, voltar, só clique simples
 * em link interno marcado, movimento reduzido, sem JavaScript, teto de tempo, token de marca, 390 e 360).
 * Confere também os tempos medidos: o painel cobre em 0,7 a 1,1 s e a sequência inteira termina em 3 s.
 * Sem Playwright, avisa e sai com 0 (NAO VERIFICADO).
 */
const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { acharPlaywright } = require('./video/achar-playwright.cjs');

const demo = path.join(path.resolve(__dirname, '..'), 'references', 'receitas', 'demo.html');
let falhas = 0;
const checar = (cond, msg) => { if (cond) console.log('ok   ' + msg); else { falhas++; console.log('FALHOU ' + msg); } };
if (!acharPlaywright()) { console.log('PULADO: Playwright ausente, prova do painel NAO VERIFICADA'); process.exit(0); }

const servidor = http.createServer((req, res) => { res.setHeader('content-type', 'text/html; charset=utf-8'); res.end(fs.readFileSync(demo)); });
servidor.listen(0, '127.0.0.1', () => {
  const porta = servidor.address().port;
  const saida = fs.mkdtempSync(path.join(os.tmpdir(), 'painel prova ação '));
  const filho = spawn(process.execPath, [path.join(__dirname, 'provar-painel.mjs'), '--url', `http://127.0.0.1:${porta}/demo.html`, '--saida', saida]);
  let texto = '';
  filho.stdout.on('data', (d) => { texto += d; });
  filho.stderr.on('data', (d) => { texto += d; });
  const limite = setTimeout(() => filho.kill(), 400000);
  filho.on('close', (status) => {
    clearTimeout(limite);
    servidor.close();
    checar(status === 0, 'provar-painel.mjs aprova o demo (saída ' + status + ')');
    if (status !== 0) console.log(texto.slice(-2000));
    let m = {};
    try { m = JSON.parse(fs.readFileSync(path.join(saida, 'painel-medidas.json'), 'utf8')); } catch { /* falha abaixo */ }
    const provas = m.provas || [];
    checar(provas.length >= 45 && provas.every((p) => p.ok), `${provas.length} provas, todas passaram`);
    for (const w of [1440, 390, 360]) {
      const t = m['tempos_' + w] || {};
      checar(t.cobre >= 700 && t.cobre <= 1100, `[${w}] o painel cobre a tela em ${t.cobre} ms (0,7 a 1,1 s)`);
      checar(t.sai > t.cobre && t.sai - t.cobre <= 600, `[${w}] a saída começa logo depois da pausa (${t.sai - t.cobre} ms)`);
      checar(fs.existsSync(path.join(saida, `painel-${w}-cobre.png`)), `[${w}] o quadro do painel cobrindo foi gravado`);
    }
    console.log(falhas ? falhas + ' falhas' : 'todos os testes passaram');
    process.exit(falhas ? 1 : 0);
  });
});
