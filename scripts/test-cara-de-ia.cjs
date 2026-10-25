/** Cara de IA (auditoria de 25/10/2026): as brechas que deixaram passar como "bonito" a página de produção.
 *
 *  A6  filete de 1 px só AVISAVA (gate-texto): agora reprova acima de 1,2 filete de enfeite por tela de 900 px.
 *  A7  data-icone-repetido-ok="1" valia sem motivo e o mesmo motivo podia repetir à vontade (gate-composicao).
 *  A8  a regex de público não via advogados, médicos, dentistas... (gate-composicao).
 *  Novo: o mesmo enfeite embaixo de quase todo h2 (gate-texto).
 *
 *  Fixtures em fixtures/cara-de-ia/: as 3 páginas reais da auditoria com as mesmas medidas (a de produção TEM que
 *  reprovar nos pontos acima; a torrefação e o ateliê TÊM que passar) e duas de calibração dos filetes (o "jornal de
 *  filetes" original reprova; a página aprovada pelo dono, com 20 filetes de tabela, passa). Os casos pequenos provam
 *  cada regra isolada. Filtro: `CARA_FILTRO=<prefixo> node scripts/test-cara-de-ia.cjs`. */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');

const FIX = path.join(__dirname, 'fixtures', 'cara-de-ia');
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64');
const pagina = (corpo, css = '') => `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Controle</title><style>body{margin:0;font:18px/1.6 Arial,sans-serif;background:#fff;color:#111}section{padding:40px 24px;min-height:300px}h1,h2{text-wrap:balance;max-width:520px}ul{list-style:none;padding:0}${css}</style></head><body data-viuva-ok="fora do assunto">${corpo}</body></html>`;
const secoes = (n, h2) => Array.from({ length: n }, (_, i) => `<section><h2${h2(i)}>Título de seção número ${i + 1}</h2><p>Texto da seção ${i + 1} com uma frase.</p></section>`).join('');
const tecla = (attrs) => `<svg viewBox="0 0 56 56" width="56" height="56" aria-hidden="true" ${attrs}><path d="M16 4H40A12 12 0 0 1 52 16V40A12 12 0 0 1 40 52H16A12 12 0 0 1 4 40V16A12 12 0 0 1 16 4Z" fill="none" stroke="#111" stroke-width="5"/></svg>`;
const marcador = (desenho, w = 20) => `<svg viewBox="0 0 20 20" width="${w}" height="${w}" aria-hidden="true"${desenho ? ` data-desenho="${desenho}"` : ''}><path d="M4 11l4 4 8-9" stroke="#111" stroke-width="2" fill="none"/></svg>`;
const itens = (n, desenho) => `<ul>${Array.from({ length: n }, (_, i) => `<li>${marcador(desenho)} Item de lista ${i + 1}</li>`).join('')}</ul>`;

const ROTAS = {
  // Enfeite de título.
  '/enfeite-borda': pagina(secoes(4, () => ' style="border-bottom:2px solid #c33;padding-bottom:8px"')),
  '/enfeite-irmao': pagina(secoes(4, () => '').replace(/<\/h2>/g, '</h2><span class="barra"></span>'), '.barra{display:block;width:48px;height:4px;background:#c33;margin-bottom:16px}'),
  '/enfeite-tres': pagina(secoes(6, (i) => (i < 3 ? ' class="t"' : '')), '.t::after{content:"";display:block;width:56px;height:3px;background:#c33;margin-top:16px}'),
  '/enfeite-variado': pagina(secoes(4, (i) => ` class="t${i}"`), '.t0::after,.t1::after,.t2::after,.t3::after{content:"";display:block;height:3px;background:#c33;margin-top:16px}.t0::after{width:20px}.t1::after{width:40px}.t2::after{width:60px}.t3::after{width:80px}'),
  // Exceção de ícone repetido com e sem motivo (A7).
  '/icone-motivo-escrito': pagina(`<section><h2>Três passos</h2><ol><li>${tecla('data-desenho="tecla neutra, marco do passo" data-icone-repetido-ok="a mesma tecla marca os três passos"')} Primeiro</li><li>${tecla('data-desenho="tecla neutra, marco do passo" data-icone-repetido-ok="a mesma tecla marca os três passos"')} Segundo</li></ol></section>`),
  '/icone-motivo-1': pagina(`<section><h2>Três passos</h2><ol><li>${tecla('data-desenho="tecla neutra, marco do passo" data-icone-repetido-ok="1"')} Primeiro</li><li>${tecla('data-desenho="tecla neutra, marco do passo" data-icone-repetido-ok="1"')} Segundo</li></ol></section>`),
  '/icone-motivo-vazio': pagina(`<section><h2>Três passos</h2><ol><li>${tecla('data-desenho="tecla neutra, marco do passo" data-icone-repetido-ok')} Primeiro</li><li>${tecla('data-desenho="tecla neutra, marco do passo" data-icone-repetido-ok')} Segundo</li></ol></section>`),
  // Mesmo motivo repetido (A7, V17 da auditoria).
  '/motivo-7': pagina(`<section><h2>O que vem no pacote</h2>${itens(7, 'folha da marca')}</section>`),
  '/motivo-6': pagina(`<section><h2>O que vem no pacote</h2>${itens(6, 'folha da marca')}</section>`),
  '/motivo-com-motivo-escrito-7': pagina(`<section><h2>Passos</h2><ol>${Array.from({ length: 7 }, (_, i) => `<li>${tecla('data-desenho="tecla neutra, marco do passo" data-icone-repetido-ok="a mesma tecla marca cada passo"')} Passo ${i + 1}</li>`).join('')}</ol></section>`),
  // Marcador de lista tipográfico, pequeno e sem data-desenho (a página aprovada pelo dono tem 27): não é motivo.
  '/marcador-de-lista-27': pagina(`<section><h2>Para quem é</h2>${itens(27, '')}</section>`),
  // Público de profissão com e sem gente no topo (A8).
  '/topo-sem-gente': pagina('<section><h1>Aprenda o sistema do zero</h1><p>Curso gravado e direto ao ponto.</p></section>'),
  '/topo-com-advogada': pagina('<section><h1>Aprenda o sistema do zero</h1><img src="/pixel.png" width="400" height="300" alt="Advogada analisando um processo no computador" style="width:400px;height:300px;background:#999"></section>'),
};

const servidor = http.createServer((req, res) => {
  const rota = req.url.split('?')[0];
  if (rota === '/pixel.png') { res.writeHead(200, { 'Content-Type': 'image/png' }); res.end(png); return; }
  if (ROTAS[rota]) { res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }); res.end(ROTAS[rota]); return; }
  const arq = path.join(FIX, path.basename(rota));
  if (rota.endsWith('.html') && fs.existsSync(arq)) { res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }); res.end(fs.readFileSync(arq)); return; }
  res.writeHead(404); res.end('não achei');
});

function rodar(script, args) {
  return new Promise((ok) => {
    const p = spawn(process.execPath, [path.join(__dirname, script), ...args], { stdio: ['ignore', 'pipe', 'pipe'] });
    let saida = '';
    p.stdout.on('data', (d) => { saida += d; });
    p.stderr.on('data', (d) => { saida += d; });
    p.on('close', (codigo) => ok({ codigo, saida }));
  });
}

const PUB_ADV = 'Advogados que não dominam o sistema e sentem insegurança ao analisar processos';
const PUB_CAFE = 'Adultos de 28 a 55 anos que passam café em casa todo dia';
const PUB_ATELIE = 'Quem está montando ou reformando casa e não quer móvel planejado de MDF';
const NAO = (re) => new RegExp(`^(?![\\s\\S]*${re.source})[\\s\\S]*`);

servidor.listen(0, '127.0.0.1', async () => {
  const u = (r) => `http://127.0.0.1:${servidor.address().port}${r}`;
  const casos = [
    // A página de produção reprova nos 4 pontos.
    ['producao-filetes-reprova', 'gate-texto.mjs', ['--url', u('/curso-advogados.html')], 1, /FALHA: [^\n]*22 filetes de 1 px[^\n]*1[.,]\d\d por tela[^\n]*máximo 1[.,]2/],
    ['producao-enfeite-de-titulo-reprova', 'gate-texto.mjs', ['--url', u('/curso-advogados.html')], 1, /FALHA: [^\n]*o mesmo enfeite em 9 de 10 títulos h2[^\n]*máximo 3/],
    ['producao-icone-repetido-sem-motivo-reprova', 'gate-composicao.mjs', ['--url', u('/curso-advogados.html'), '--publico', PUB_ADV], 1, /data-icone-repetido-ok sem motivo[^\n]*tecla neutra/],
    ['producao-motivo-repetido-reprova', 'gate-composicao.mjs', ['--url', u('/curso-advogados.html'), '--publico', PUB_ADV], 1, /motivo "sinal de mais do logo" repetido 16 vezes[^\n]*máximo 6/],
    ['producao-sem-gente-para-advogados-reprova', 'gate-composicao.mjs', ['--url', u('/curso-advogados.html'), '--publico', PUB_ADV], 1, /desktop 1440: nenhuma figura humana[\s\S]*celular 390: nenhuma figura humana/],
    // A torrefação e o ateliê passam nos dois gates.
    ['torrefacao-texto-passa', 'gate-texto.mjs', ['--url', u('/torrefacao.html')], 0, /aviso: 12 filetes[\s\S]*PASSA/],
    ['torrefacao-composicao-passa', 'gate-composicao.mjs', ['--url', u('/torrefacao.html'), '--publico', PUB_CAFE, '--produto-fisico'], 0, /PASSA/],
    ['atelie-texto-passa', 'gate-texto.mjs', ['--url', u('/atelie.html')], 0, /PASSA/],
    ['atelie-composicao-passa', 'gate-composicao.mjs', ['--url', u('/atelie.html'), '--publico', PUB_ATELIE, '--produto-fisico'], 0, /PASSA/],
    // Calibração dos filetes.
    ['calibracao-jornal-de-filetes-reprova', 'gate-texto.mjs', ['--url', u('/jornal-de-filetes.html')], 1, /FALHA: [^\n]*11 filetes de 1 px/],
    ['calibracao-aprovada-com-tabelas-passa', 'gate-texto.mjs', ['--url', u('/aprovada-com-tabelas.html')], 0, /aviso: 32 filetes[\s\S]*PASSA/],
    // Enfeite de título isolado.
    ['enfeite-borda-em-4-reprova', 'gate-texto.mjs', ['--url', u('/enfeite-borda')], 1, /o mesmo enfeite em 4 de 4 títulos h2[^\n]*borda embaixo/],
    ['enfeite-irmao-em-4-reprova', 'gate-texto.mjs', ['--url', u('/enfeite-irmao')], 1, /o mesmo enfeite em 4 de 4 títulos h2[^\n]*traço logo depois/],
    ['enfeite-em-3-passa', 'gate-texto.mjs', ['--url', u('/enfeite-tres')], 0, /PASSA/],
    ['enfeite-variado-passa', 'gate-texto.mjs', ['--url', u('/enfeite-variado')], 0, /PASSA/],
    // Exceção de ícone repetido.
    ['icone-motivo-escrito-passa', 'gate-composicao.mjs', ['--url', u('/icone-motivo-escrito')], 0, /PASSA/],
    ['icone-motivo-1-reprova', 'gate-composicao.mjs', ['--url', u('/icone-motivo-1')], 1, /data-icone-repetido-ok sem motivo \("1"\)/],
    ['icone-motivo-vazio-reprova', 'gate-composicao.mjs', ['--url', u('/icone-motivo-vazio')], 1, /data-icone-repetido-ok sem motivo \(""\)/],
    // Motivo repetido.
    ['motivo-7-reprova', 'gate-composicao.mjs', ['--url', u('/motivo-7')], 1, /motivo "folha da marca" repetido 7 vezes/],
    ['motivo-6-passa', 'gate-composicao.mjs', ['--url', u('/motivo-6')], 0, /PASSA/],
    ['motivo-com-motivo-escrito-continua-no-limite', 'gate-composicao.mjs', ['--url', u('/motivo-com-motivo-escrito-7')], 1, /motivo "tecla neutra" repetido 7 vezes/],
    ['marcador-de-lista-sem-desenho-passa', 'gate-composicao.mjs', ['--url', u('/marcador-de-lista-27')], 0, NAO(/repetido \d+ vezes/)],
    // Público de profissão.
    ['publico-advogadas-sem-gente-reprova', 'gate-composicao.mjs', ['--url', u('/topo-sem-gente'), '--publico', 'advogadas criminalistas'], 1, /nenhuma figura humana/],
    ['publico-medicos-sem-gente-reprova', 'gate-composicao.mjs', ['--url', u('/topo-sem-gente'), '--publico', 'médicos e dentistas'], 1, /nenhuma figura humana/],
    ['publico-advogadas-com-advogada-passa', 'gate-composicao.mjs', ['--url', u('/topo-com-advogada'), '--publico', 'advogadas criminalistas'], 0, /foto "Advogada analisando/],
  ];
  const filtro = process.env.CARA_FILTRO;
  const lista = filtro ? casos.filter((c) => c[0].startsWith(filtro)) : casos;
  // O mesmo gate na mesma URL roda uma vez só (os casos de produção leem a mesma saída).
  const cache = new Map();
  const falhas = [];
  for (const [nome, script, args, esperado, re] of lista) {
    const chave = script + ' ' + args.join(' ');
    if (!cache.has(chave)) cache.set(chave, rodar(script, args));
    const { codigo, saida } = await cache.get(chave);
    const ok = codigo === esperado && (!re || re.test(saida));
    console.log(`${ok ? 'ok   ' : 'FALHA'} ${nome} (saída ${codigo}, esperado ${esperado})`);
    if (!ok) { falhas.push(nome); console.log(saida.split('\n').filter((l) => /FALHA|aviso|PASSA|REPROVA|Error|erro/i.test(l)).slice(0, 14).map((l) => '      ' + l).join('\n')); }
  }
  servidor.close();
  console.log(`\n${lista.length - falhas.length} de ${lista.length} controles de cara de IA certos.`);
  process.exit(falhas.length ? 1 : 0);
});
