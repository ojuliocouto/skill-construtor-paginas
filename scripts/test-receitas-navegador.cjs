/**
 * Prova no navegador das receitas de movimento: serve o demo com um servidor do próprio Node
 * (sem Python, sem porta fixa) e roda o `provar-receitas.mjs`. Cada bloco precisa mudar de pixel,
 * a página sem script não pode ter nada escondido e o texto com movimento reduzido tem que ser o mesmo.
 * Sem Playwright instalado, o teste avisa e sai com 0 (a prova fica NÃO VERIFICADA).
 */
const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');

const raiz = path.resolve(__dirname, '..');
const demo = path.join(raiz, 'references', 'receitas', 'demo.html');
let falhas = 0;
const checar = (cond, msg) => { if (cond) console.log('ok   ' + msg); else { falhas++; console.log('FALHOU ' + msg); } };

const temPlaywright = () => {
  try { require('playwright'); return true; } catch { /* segue */ }
  const r = spawnSync('npm', ['root', '-g'], { encoding: 'utf8', shell: process.platform === 'win32' });
  try { require(path.join((r.stdout || '').trim(), 'playwright')); return true; } catch { return false; }
};
if (!temPlaywright()) { console.log('PULADO: Playwright ausente, prova no navegador NAO VERIFICADA'); process.exit(0); }

const servidor = http.createServer((req, res) => {
  res.setHeader('content-type', 'text/html; charset=utf-8');
  res.end(fs.readFileSync(demo));
});
servidor.listen(0, '127.0.0.1', () => {
  const porta = servidor.address().port;
  const saida = fs.mkdtempSync(path.join(os.tmpdir(), 'receitas prova ação '));
  const filho = spawn(process.execPath, [path.join(__dirname, 'provar-receitas.mjs'), '--url', `http://127.0.0.1:${porta}/demo.html`, '--saida', saida]);
  let texto = '';
  filho.stdout.on('data', (d) => { texto += d; });
  filho.stderr.on('data', (d) => { texto += d; });
  const limite = setTimeout(() => filho.kill(), 420000);
  filho.on('close', (status) => { clearTimeout(limite); concluir(status, texto, saida); });
});

function concluir(status, saidaTexto, saida) {
  const r = { status };
  servidor.close();
  checar(r.status === 0, 'provar-receitas.mjs aprova o demo (saída ' + r.status + ')');
  if (r.status !== 0) console.log(saidaTexto.slice(-1500));
  let m = {};
  try { m = JSON.parse(fs.readFileSync(path.join(saida, 'medidas.json'), 'utf8')); } catch { /* falha abaixo */ }
  const blocos = m.blocos || [];
  checar(blocos.length === 34, '17 receitas medidas em 2 telas (' + blocos.length + ')');
  // P20 (3.5.10): na oferta longa a barra fica à vista com o rótulo da oferta, sem deixar telas sem botão
  checar(m.barra_oferta && m.barra_oferta.visivel === true && m.barra_oferta.rotulo === m.barra_oferta.esperado, 'barra fixa na oferta longa: à vista e com o rótulo da oferta (' + JSON.stringify(m.barra_oferta) + ')');
  checar(blocos.length > 0 && blocos.every((b) => b.ok && b.mudou >= m.minimo_mudou), 'todo bloco muda de pixel');
  // 3.5.11 (P5): variante de 3 fotos da produto-em-estados: mesmo quadro nas 3 seções, a cortina muda o quadro e o movimento reduzido já chega no final
  for (const tela of ['desk', 'mob']) {
    const e = (m.estados_fotos || {})[tela] || {};
    checar(e.mesma_posicao === true, 'variante de 3 fotos em ' + tela + ': os 3 quadros têm a mesma largura, altura e posição (' + JSON.stringify((e.quadros || [])[0]) + ')');
    checar((e.estados || []).length === 2 && e.estados.every((x) => x.mudou >= m.minimo_mudou), 'variante de 3 fotos em ' + tela + ': a cortina muda o quadro dos estados 2 e 3 (' + (e.estados || []).map((x) => x.mudou + '%').join(' e ') + ')');
    checar((e.reduzido || []).length === 3 && e.reduzido.every((x) => x.final && x.mudou < m.minimo_mudou), 'variante de 3 fotos em ' + tela + ': movimento reduzido chega no estado final');
  }
  checar(m.sem_script && m.sem_script.escondidos && m.sem_script.escondidos.length === 0, 'sem script nada fica escondido');
  checar(m.movimento_reduzido && m.movimento_reduzido.texto_igual === true, 'movimento reduzido mostra o mesmo texto');
  checar(m.lateral && !m.lateral.mob && !m.lateral.desk, 'nenhuma rolagem lateral');
  fs.rmSync(saida, { recursive: true, force: true });
  console.log(falhas ? falhas + ' falhas' : 'todos os testes passaram');
  process.exit(falhas ? 1 : 0);
}
