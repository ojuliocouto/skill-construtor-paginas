/**
 * Gate de movimento com as provas de estado em paralelo (corte 9 da auditoria de velocidade: o patch medido na 3.5.8 e nunca aplicado).
 *
 * O gate levava 256 s, 80% de espera de relógio de propósito. As provas que olham o ESTADO depois de uma espera fixa (conteúdo sem o
 * script, parada no topo, salto até o fim, movimento reduzido) não dependem do relógio da página e rodam juntas; as medidas de TEMPO
 * (a visita e a rolagem a 300 px/s) seguem sozinhas, uma por vez, porque com 3 ou 4 delas ao mesmo tempo o veredito mudou em
 * 4 de 7 execuções. Aqui, no Chromium de verdade:
 *  1. as 4 provas de "sem o script" (6 s de espera cada) levam bem menos que em fila;
 *  2. o veredito, o código de saída e o TEXTO inteiro da saída são os mesmos em paralelo e em fila (`--em-serie`), numa página que
 *     reprova em várias famílias de prova ao mesmo tempo (sem rede de segurança, rolagem suave, animação com movimento reduzido);
 *  3. a mesma conta numa página boa: PASSA nos dois modos.
 * O número do tempo (ms, s) é tirado antes de comparar: o resto tem que ser idêntico, na mesma ordem.
 */
const http = require('node:http');
const { spawn } = require('node:child_process');
const path = require('node:path');

const GATE = path.join(__dirname, 'gate-movimento.mjs');
const REDE = '<script>(function(d){d.classList.add("js");setTimeout(function(){if(!d.hasAttribute("data-js-ok"))d.classList.remove("js")},5000)})(document.documentElement)</script>';
const OK = 'document.documentElement.setAttribute("data-js-ok","");';
const TEXTO = '<section><h1>Controle</h1><p>Texto normal da página de controle.</p></section>';
const secoes = (comRede) => '<style>.js .revela{opacity:0;transform:translateY(20px);transition:opacity .6s,transform .6s}.js .revela.visivel{opacity:1;transform:none}@media (prefers-reduced-motion: reduce){.js .revela{transition:none}}.alta{min-height:1000px}</style>'
  + (comRede ? REDE : '<script>document.documentElement.classList.add("js")</script>') + TEXTO
  + [1, 2, 3].map((i) => `<section class="alta"><h2 class="revela">Seção ${i}</h2><p class="revela">Texto da seção ${i} que entra ao rolar a página.</p></section>`).join('')
  + '<script>' + OK + 'var els=document.querySelectorAll(".revela");var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("visivel");io.unobserve(e.target)}})});els.forEach(function(e){io.observe(e)});'
  + 'function jaPassou(){els.forEach(function(e){if(!e.classList.contains("visivel")&&e.getBoundingClientRect().bottom<=0){e.style.transition="none";e.classList.add("visivel");io.unobserve(e)}})}addEventListener("scroll",function(){requestAnimationFrame(jaPassou)},{passive:true});</script>';
const ENTRADA = '<style>@keyframes sobe{from{opacity:0;transform:translateY(24px)}to{opacity:1;transform:none}}.entra{animation:sobe 1.4s ease both}html{scroll-behavior:smooth}</style><section><h1 class="entra">Título que sobe</h1></section>';

const PAGINAS = {
  '/ok': secoes(true),
  // reprova em 3 famílias: sem a rede de segurança (provas de script), rolagem suave com movimento reduzido e animação em curso com movimento reduzido
  '/ruim': ENTRADA + secoes(false),
};

let falhas = 0;
const checa = (nome, ok, detalhe = '') => { console.log(`${ok ? 'ok   ' : 'FALHA'} ${nome}${detalhe ? ' -> ' + detalhe : ''}`); if (!ok) falhas++; };

function rodar(args) {
  return new Promise((resolve) => {
    const t0 = Date.now();
    const f = spawn(process.execPath, [GATE, ...args], { windowsHide: true });
    let saida = '';
    f.stdout.on('data', (d) => { saida += d; });
    f.stderr.on('data', (d) => { saida += d; });
    const relogio = setTimeout(() => f.kill(), 540000);
    f.on('close', (status) => { clearTimeout(relogio); resolve({ status, saida, segundos: (Date.now() - t0) / 1000 }); });
  });
}
const semTempos = (s) => s.replace(/\b\d+(\.\d+)? ms\b/g, 'N ms').replace(/aos \d+(\.\d+)? s/g, 'aos N s').replace(/scrollY \d+/g, 'scrollY N');

const servidor = http.createServer((req, res) => {
  const corpo = PAGINAS[req.url.split('?')[0]];
  if (!corpo) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>controle</title></head><body>${corpo}</body></html>`);
});

servidor.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${servidor.address().port}`;
  try {
    // 1. a velocidade das 4 provas de "sem o script" (a espera de 6 s de cada uma)
    const soScriptPar = await rodar(['--url', base + '/ok', '--so-prova-script']);
    const soScriptSer = await rodar(['--url', base + '/ok', '--so-prova-script', '--em-serie']);
    checa('provas de script em paralelo: PASSA (saída 0)', soScriptPar.status === 0, soScriptPar.saida.slice(-300));
    checa('provas de script em fila: PASSA (saída 0)', soScriptSer.status === 0);
    checa('as 4 provas de script em paralelo levam bem menos que em fila', soScriptPar.segundos < soScriptSer.segundos * 0.7, `${soScriptPar.segundos.toFixed(1)} s contra ${soScriptSer.segundos.toFixed(1)} s`);
    checa('o texto das provas de script é o mesmo, na mesma ordem', semTempos(soScriptPar.saida) === semTempos(soScriptSer.saida), `\n${semTempos(soScriptPar.saida)}\n---\n${semTempos(soScriptSer.saida)}`);

    // 2. página que reprova em várias famílias: mesmo veredito, mesmo texto, mesma ordem
    const ruimPar = await rodar(['--url', base + '/ruim', '--espera', '500']);
    const ruimSer = await rodar(['--url', base + '/ruim', '--espera', '500', '--em-serie']);
    checa('página ruim: reprova nos dois modos (saída 1)', ruimPar.status === 1 && ruimSer.status === 1, `${ruimPar.status} / ${ruimSer.status}`);
    checa('página ruim: o gate achou as 3 famílias de defeito (script, rolagem suave, animação com movimento reduzido)',
      /script bloqueado: [1-9]/.test(ruimPar.saida) && /scroll-behavior: smooth em/.test(ruimPar.saida) && /animação CSS de sobe em h1\.entra/.test(ruimPar.saida), ruimPar.saida.slice(-600));
    checa('página ruim: o texto inteiro da saída é idêntico em paralelo e em fila (mesmas falhas, na mesma ordem)', semTempos(ruimPar.saida) === semTempos(ruimSer.saida), `\n${semTempos(ruimPar.saida)}\n---\n${semTempos(ruimSer.saida)}`);

    // 3. página boa: PASSA nos dois
    const okPar = await rodar(['--url', base + '/ok', '--espera', '500']);
    checa('página boa: PASSA em paralelo (a conta da rolagem a 300 px/s não foi estragada)', okPar.status === 0, okPar.saida.slice(-500));
    checa('página boa: nenhuma linha FALHA na saída', !/FALHA/.test(okPar.saida), okPar.saida.split('\n').filter((l) => /FALHA/.test(l)).join(' | '));
    console.log(`\nTempos: ruim ${ruimPar.segundos.toFixed(0)} s em paralelo contra ${ruimSer.segundos.toFixed(0)} s em fila; boa ${okPar.segundos.toFixed(0)} s em paralelo.`);
  } finally {
    servidor.close();
  }
  process.exitCode = falhas ? 1 : 0;
});
