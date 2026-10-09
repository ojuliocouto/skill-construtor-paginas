/** P12, P13 e P14 (3.5.10): texto que fica invisível e nenhum gate via. Achados da Torra Clara (3.5.8), reproduzidos em páginas
 *  locais e confirmados no Chromium do Playwright 1.61.1:
 *   - P12: clip-path de entrada recortando o PRÓPRIO alvo do IntersectionObserver. Com threshold 0,18 a razão de interseção do
 *     alvo todo recortado é 0, o observador nunca dispara e as linhas do rótulo da oferta nunca aparecem em 1440.
 *   - P13a: clip-path num span EM LINHA que quebra em 2 linhas: o Chromium recorta pela caixa da 1ª linha e a 2ª some. O
 *     gate-oclusao passava porque media o centro da caixa inteira e aceitava o pai como "dono" do ponto.
 *   - P13b: os fatos do herói com translateY(26px) ficavam abaixo da linha do rootMargin -6% e, com a página parada em 1440,
 *     nunca apareciam.
 *   - P14: depois de um salto (âncora, painel, voltar do WhatsApp), o que ficou acima da tela nunca é revelado.
 *  Cada caso ruim reprova com a mensagem certa, e a página com a receita certa passa.
 */
const http = require('node:http');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');

const temPlaywright = () => {
  try { require('playwright'); return true; } catch { /* segue */ }
  const r = spawnSync('npm', ['root', '-g'], { encoding: 'utf8', shell: process.platform === 'win32' });
  try { require(path.join((r.stdout || '').trim(), 'playwright')); return true; } catch { return false; }
};
if (!temPlaywright()) { console.log('PULADO: Playwright ausente, visibilidade do movimento NAO VERIFICADA'); process.exit(0); }

const BASE = '<style>body{margin:0;font:18px/1.5 Arial;color:#111;background:#fff}section{padding:24px}.alta{min-height:1000px}'
  + '.js .revela{opacity:0;transform:translateY(26px);transition:opacity .5s,transform .5s}.js .revela.visivel{opacity:1;transform:none}'
  + '.js .instantaneo,.js .instantaneo *{transition:none!important}'
  + '@media (prefers-reduced-motion: reduce){.js .revela{transition:none}}</style>'
  + '<script>document.documentElement.classList.add("js")</script>';
// Observador da receita-base. `passou` é o "já passou = estado final" (P14): o que está acima da tela depois de um salto entra
// no estado final, sem animação.
const observa = (sel, opcoes, comPassou) => '<script>var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("visivel");io.unobserve(e.target)}})},' + opcoes + ');'
  + 'var els=document.querySelectorAll("' + sel + '");els.forEach(function(e){io.observe(e)});'
  + (comPassou ? 'function passou(){els.forEach(function(e){if(!e.classList.contains("visivel")&&e.getBoundingClientRect().bottom<=0){e.classList.add("instantaneo","visivel");io.unobserve(e)}})}addEventListener("scroll",function(){requestAnimationFrame(passou)},{passive:true});passou();' : '')
  + '</script>';
const heroi = '<section><h1>Controle da página</h1><p>Topo da página de controle, com o botão logo abaixo.</p><a href="#c" style="display:inline-block;padding:16px;background:#111;color:#fff">Ver resultado</a></section>';
const secoes = (classe) => [1, 2, 3, 4].map((i) => `<section class="alta"><h2 class="${classe}">Seção ${i}</h2><p class="${classe}">Texto da seção ${i} que entra ao rolar a página.</p></section>`).join('');
const OPCOES = '{threshold:0.18,rootMargin:"0px 0px -6% 0px"}';

// P12: o rótulo da oferta. Ruim: clip-path de entrada no próprio alvo; bom: o alvo é o pai, o clip-path vai nos filhos.
const ROTULO_CSS = '<style>.js .linha-ruim{clip-path:inset(0 100% 0 0);transition:clip-path .7s}.js .linha-ruim.visivel{clip-path:inset(-4px)}'
  + '.js .linha-boa>*{display:block;clip-path:inset(0 100% 0 0);transition:clip-path .7s}.js .linha-boa.visivel>*{clip-path:inset(-4px)}</style>';
const rotulo = (classe) => `<section class="alta"><h2 class="revela">Oferta</h2><dl>${['Moagem', 'Tamanho', 'Frequência'].map((t) => `<div class="${classe}"><dt>${t}</dt><dd>Escolha do pacote</dd></div>`).join('')}</dl></section>`;

// P13b: fatos do herói na faixa de baixo da 1a tela de 1440x900, com translateY(26px): caixa em 853 a 878, linha do rootMargin em 846.
const fatos = (sel) => '<section style="height:827px;padding:0;box-sizing:border-box"><h1 style="margin:0;padding:24px">Café torrado na semana</h1><p style="padding:0 24px">Topo da página de controle.</p><a href="#c" style="display:inline-block;margin:0 24px;padding:16px;background:#111;color:#fff">Ver de onde vem</a></section>'
  + `<ul class="${sel}" style="margin:0;padding:0 24px;list-style:none;display:flex;gap:24px;height:25px;line-height:25px"><li>Torra na segunda</li><li>Envio na quarta</li><li>Sem fidelidade</li></ul>`;

// P13a: a linha do frete. Ruim: clip-path no span em linha; bom: o span vira bloco.
const frete = (css) => `<section><p style="width:200px">Prazo: <span style="${css}">frete de R$ 14,90 para 250 g, grátis acima de 500 g</span></p></section>`;

const ROTAS = {
  '/ok': BASE + heroi + secoes('revela') + observa('.revela', OPCOES, true),
  '/rotulo-clip-no-alvo': BASE + ROTULO_CSS + heroi + secoes('revela') + rotulo('linha-ruim') + secoes('revela') + observa('.revela, .linha-ruim', OPCOES, true),
  '/rotulo-clip-no-filho': BASE + ROTULO_CSS + heroi + secoes('revela') + rotulo('linha-boa') + secoes('revela') + observa('.revela, .linha-boa', OPCOES, true),
  '/fatos-abaixo-da-margem': BASE + fatos('revela') + secoes('revela') + observa('.revela', OPCOES, true),
  // conserto: o que já está na primeira tela entra na carga (observador sem margem negativa para o herói)
  '/fatos-revelados-na-carga': BASE + fatos('revela') + secoes('revela') + observa('.revela', OPCOES, true)
    + '<script>document.querySelectorAll(".revela").forEach(function(e){var c=e.getBoundingClientRect();if(c.top<innerHeight&&c.bottom>0){e.classList.add("visivel");io.unobserve(e)}})</script>',
  '/salto-sem-passou': BASE + heroi + secoes('revela') + observa('.revela', OPCOES, false),
  '/salto-com-passou': BASE + heroi + secoes('revela') + observa('.revela', OPCOES, true),
  // carrossel lateral no celular (os depoimentos da Torra Clara): cartão à direita da janela, ainda não revelado, não está "na tela"
  '/carrossel': BASE + heroi + secoes('revela') + '<section class="alta"><h2 class="revela">Depoimentos</h2><ul style="display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:14px;list-style:none;padding:0">'
    + [1, 2, 3].map((i) => `<li class="revela" style="flex:none;width:min(82vw,330px);scroll-snap-align:start;background:#eee;padding:16px"><blockquote>Depoimento ${i} de quem assina há meses.</blockquote></li>`).join('')
    + '</ul></section>' + observa('.revela', OPCOES, true),
  '/frete-span-em-linha': BASE + heroi + frete('clip-path:inset(-4px)'),
  '/frete-span-em-bloco': BASE + heroi + frete('display:block;clip-path:inset(-4px)'),
};
const servidor = http.createServer((req, res) => {
  const corpo = ROTAS[req.url.split('?')[0]];
  res.writeHead(corpo ? 200 : 404, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(corpo ? `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controle</title></head><body>${corpo}</body></html>` : '');
});

const rodar = (script, argv) => new Promise((ok) => {
  const p = spawn(process.execPath, [path.join(__dirname, script), ...argv]);
  let out = '';
  p.stdout.on('data', (d) => { out += d; });
  p.stderr.on('data', (d) => { out += d; });
  const teto = setTimeout(() => p.kill('SIGTERM'), 240000);
  p.on('close', (status) => { clearTimeout(teto); ok({ status, out }); });
});
const MOV = (rota) => ['gate-movimento.mjs', ['--url', rota, '--espera', '1000', '--so-visibilidade']];
const CASOS = [
  ['movimento: página com a receita-base passa nas três provas novas', MOV('/ok'), 0, /^(?=[\s\S]*parada no topo por \d s: 0 elemento)(?=[\s\S]*fim da visita: 0 elemento)(?=[\s\S]*salto até o fim: 0 elemento)/],
  ['P12: clip-path de entrada no alvo do observador deixa o rótulo invisível na tela durante a visita', MOV('/rotulo-clip-no-alvo'), 1, /fim da visita[^\n]*continuam invis[ií]veis[^\n]*dt "Moagem"[^\n]*clip-path[^\n]*no filho/],
  ['P12: clip-path no filho, observador no pai, passa', MOV('/rotulo-clip-no-filho'), 0],
  ['P13b: fatos do herói abaixo da linha do rootMargin ficam invisíveis com a página parada', MOV('/fatos-abaixo-da-margem'), 1, /desktop comum \(1440x900\): parada no topo por \d s[^\n]*li "Torra na segunda"/],
  ['P13b: o que já está na primeira tela revelado na carga passa', MOV('/fatos-revelados-na-carga'), 0],
  ['P14: sem "já passou", o que ficou acima depois do salto continua invisível', MOV('/salto-sem-passou'), 1, /depois de um salto at[eé] o fim[^\n]*acima da tela continuam invis[ií]veis[^\n]*j[aá] passou/],
  ['P14: com "já passou = estado final", passa', MOV('/salto-com-passou'), 0],
  ['carrossel lateral: cartão fora da janela na horizontal não conta como invisível na tela', MOV('/carrossel'), 0],
  ['P13a: clip-path no span em linha corta a 2ª linha do frete', ['gate-oclusao.mjs', ['--url', '/frete-span-em-linha']], 1, /CORTADO[^\n]*"[^"]*" linha 2 de 3[^\n]*clip-path em span/],
  ['P13a: o span em bloco mostra as linhas inteiras', ['gate-oclusao.mjs', ['--url', '/frete-span-em-bloco']], 0],
];

servidor.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${servidor.address().port}`;
  const filtro = process.env.VIS_FILTRO;
  const casos = CASOS.filter(([nome]) => !filtro || nome.includes(filtro));
  let falhas = 0;
  // dois navegadores por vez, no máximo
  for (let i = 0; i < casos.length; i += 2) {
    const lote = casos.slice(i, i + 2);
    const res = await Promise.all(lote.map(([, [script, argv]]) => rodar(script, argv.map((a) => (a.startsWith('/') ? base + a : a)))));
    lote.forEach(([nome, , esperado, padrao], k) => {
      const { status, out } = res[k];
      const ok = status === esperado && (!padrao || padrao.test(out));
      if (!ok) { falhas++; console.log(`FALHA ${nome}: saída ${status}, esperado ${esperado}${padrao && !padrao.test(out) ? ', mensagem AUSENTE' : ''}\n${out.slice(-2000)}`); }
      else console.log(`ok    ${nome}`);
    });
  }
  servidor.close();
  console.log(falhas ? `${falhas} falha(s)` : 'todos os controles de visibilidade passaram');
  process.exit(falhas ? 1 : 0);
});
