/** A receita da assinatura, provada no demo (segunda leva da 3.5.6: A15, A16, A17, A18, A20).
 *
 *  Serve o `references/receitas/demo.html` (e uma variante em fundo CLARO) e confere no navegador:
 *   - gate-movimento: o demo passa em desktop e celular (A20: nada de transição de CSS que termina depois que a pessoa
 *     saiu da seção; a cor da peça muda no mesmo laço do JS);
 *   - gate-composicao: nenhuma falha é da assinatura, em fundo escuro e em fundo claro (A16: o desenho repetido da
 *     assinatura leva data-assinatura; A17: o traço fino tem 3:1 nas duas cores; o encaixe não lê como wireframe). O demo
 *     inteiro tem outras falhas de composição porque é um mostruário de 15 receitas, e elas não entram aqui;
 *   - gate-simetria: o par "coluna + passos" e "título fixo + lista" declara data-assimetrico, então vira aviso (A18) e não
 *     há falha de simetria nas seções da assinatura nem do título fixo;
 *   - celular (390 px): a coluna da assinatura NÃO é sticky e o estado 2 acontece (as peças alinham quando a coluna sobe)
 *     (A15), e em 1440 px ela segue sticky.
 *  Sem Playwright, o teste avisa e sai com 0.
 */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { raizGlobal } = require('./npm-global.cjs');

function playwright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(raizGlobal(), 'playwright')); } catch { return null; }
  }
}
const pw = playwright();
if (!pw) { console.log('PULADO: Playwright ausente, a prova da assinatura no demo NAO VERIFICADA'); process.exit(0); }

const demo = fs.readFileSync(path.join(__dirname, '..', 'references', 'receitas', 'demo.html'), 'utf8');
const claro = demo
  .replace('.assin { background: var(--escuro) !important; color: var(--papel); }', '.assin { background: var(--papel) !important; color: var(--escuro); }')
  .replace(/class="coluna( entra-pecas)?"/g, (m) => m.replace('class="coluna', 'class="coluna sobre-claro'));
let falhas = 0;
const checa = (nome, ok, detalhe = '') => { console.log(`${ok ? 'OK   ' : 'FALHA'} ${nome}${detalhe ? ' -> ' + detalhe : ''}`); if (!ok) falhas++; };

const servidor = http.createServer((req, res) => {
  res.setHeader('content-type', 'text/html; charset=utf-8');
  res.end(req.url.startsWith('/claro') ? claro : demo);
});
const rodar = (script, args) => new Promise((resolve) => {
  const f = spawn(process.execPath, [path.join(__dirname, script), ...args]);
  let s = ''; f.stdout.on('data', (d) => { s += d; }); f.stderr.on('data', (d) => { s += d; });
  const t = setTimeout(() => f.kill(), 300000);
  f.on('close', (c) => { clearTimeout(t); resolve({ code: c, texto: s }); });
});

servidor.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${servidor.address().port}`;
  const mov = await rodar('gate-movimento.mjs', ['--url', base + '/demo.html']);
  checa('gate-movimento passa no demo (desktop e celular)', mov.code === 0, mov.code === 0 ? '' : 'saída inteira do gate abaixo');
  if (mov.code !== 0) console.log(mov.texto.split('\n').map((l) => '    | ' + l).join('\n'));
  const daAssinatura = (txt) => txt.split('\n').filter((l) => /FALHA/.test(l) && /encaixe|traço fino|destaque|contraste|Assinatura em três|Título que fica|lista vertical ao lado|passos/i.test(l));
  const escuro = await rodar('gate-composicao.mjs', ['--url', base + '/demo.html']);
  checa('gate-composicao: nenhuma falha da assinatura em fundo escuro', daAssinatura(escuro.texto).length === 0 && /menor contraste de traço fino ou destaque: \d/.test(escuro.texto), daAssinatura(escuro.texto).slice(0, 2).join(' | '));
  const claroR = await rodar('gate-composicao.mjs', ['--url', base + '/claro.html']);
  checa('gate-composicao: nenhuma falha da assinatura em fundo claro (.sobre-claro)', daAssinatura(claroR.texto).length === 0, daAssinatura(claroR.texto).slice(0, 2).join(' | '));
  const sim = await rodar('gate-simetria.mjs', ['--url', base + '/demo.html']);
  checa('gate-simetria: o par declarado vira aviso (data-assimetrico) e a assinatura/título fixo não reprovam', /AVISO \(data-assimetrico\)/.test(sim.texto) && daAssinatura(sim.texto).length === 0, daAssinatura(sim.texto).slice(0, 2).join(' | '));

  const b = await pw.chromium.launch();
  for (const [nome, larg, alt, movel] of [['celular 390', 390, 844, true], ['desktop 1440', 1440, 900, false]]) {
    const p = await b.newPage({ viewport: { width: larg, height: alt }, isMobile: movel, hasTouch: movel });
    await p.goto(base + '/demo.html', { waitUntil: 'load' });
    await p.waitForTimeout(500);
    const pos = await p.evaluate(() => getComputedStyle(document.querySelector('.assin-coluna')).position);
    checa(`${nome}: a coluna da assinatura é ${movel ? 'static (sem espaço fixo)' : 'sticky'}`, pos === (movel ? 'static' : 'sticky'), pos);
    if (movel) {
      // rola até a coluna ficar a 30% da altura da tela: o estado 2 tem que ter alinhado todas as peças
      await p.evaluate(() => { const c = document.querySelector('.assin-coluna').getBoundingClientRect(); window.scrollTo({ top: window.scrollY + c.top - window.innerHeight * 0.3, behavior: 'instant' }); });
      await p.waitForTimeout(900);
      const r = await p.evaluate(() => { const s = document.querySelector('svg[data-coluna="rolagem"]'); return { pecas: s.querySelectorAll('.peca').length, alinhadas: s.querySelectorAll('.peca.alinhada').length, altura: Math.round(s.getBoundingClientRect().height) }; });
      checa('celular 390: o estado 2 acontece (peças alinhadas quando a coluna sobe)', r.pecas > 0 && r.alinhadas === r.pecas, JSON.stringify(r));
      checa('celular 390: a coluna ocupa uma faixa baixa (até 130 px)', r.altura <= 130, String(r.altura));
    }
    await p.close();
  }
  await b.close();
  servidor.close();
  console.log(falhas ? `\n${falhas} falha(s).` : '\nAssinatura provada no demo.');
  process.exit(falhas ? 1 : 0);
});
