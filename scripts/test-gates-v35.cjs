/**
 * Controles dos gates de tela da v3.5 (padrão da v7): ritmo, simetria com `data-assimetrico`,
 * responsivo com carrossel, aviso e foto na primeira tela do gate-imagens e a gravação de quadros
 * do anim.mjs. Páginas locais controladas isolam cada defeito; um processo pesado por vez.
 *
 * node scripts/test-gates-v35.cjs            todos os controles
 * GATES_FILTRO=ritmo node scripts/test-gates-v35.cjs   só os que começam com "ritmo"
 */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn, execFileSync } = require('node:child_process');

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'gates-v35-'));
// Foto de controle com textura (nítida) e uma versão lisa (borrada), geradas por PIL.
fs.writeFileSync(path.join(pasta, 'fazer-fotos.py'), [
  'import numpy as np, sys',
  'from PIL import Image',
  'rng = np.random.default_rng(7)',
  'pasta = sys.argv[1]',
  'ruido = rng.integers(0, 255, (600, 900, 3), dtype=np.uint8)',
  'Image.fromarray(ruido).save(pasta + "/foto-nitida.jpg", quality=95)',
  'Image.fromarray(np.full((600, 900, 3), 128, dtype=np.uint8)).save(pasta + "/foto-lisa.jpg", quality=95)',
].join('\n'));
execFileSync('python3', [path.join(pasta, 'fazer-fotos.py'), pasta]);

const head = '<title>Página de controle</title><meta name="viewport" content="width=device-width,initial-scale=1">';
const estilo = '<style>body{margin:0;font:18px Arial;background:#fff;color:#111}section{padding:48px 32px;min-height:220px}h1,h2,h3{margin:0 0 16px}p{max-width:600px;line-height:1.6;margin:0 0 12px}ul{margin:0;padding:0;list-style:none}li{padding:10px 0}a,button{display:inline-block;padding:16px;background:#111;color:#fff;border:0;font:18px Arial}</style>';

const caixa = (t) => `<article style="background:#eee;padding:16px"><h3>${t}</h3><p>Descrição curta do item paralelo.</p></article>`;
const cartoes = (titulo, extra = '', attr = '') => `<section ${attr}><h2 ${extra}>${titulo}</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">${caixa('Um')}${caixa('Dois')}${caixa('Três')}</div></section>`;
const lista = (titulo, extra = '') => `<section><h2 ${extra}>${titulo}</h2><ul><li>Primeira frase da lista.</li><li>Segunda frase da lista.</li><li>Terceira frase da lista.</li><li>Quarta frase da lista.</li></ul></section>`;
const assim = (titulo, extra = '') => `<section><h2 ${extra}>${titulo}</h2><div style="display:grid;grid-template-columns:2fr 1fr;gap:16px;align-items:start"><div style="background:#eee;padding:16px"><h3>Largo</h3><p>Bloco largo com mais texto para pesar mais que o vizinho estreito ao lado.</p></div><div style="padding:16px;margin-top:40px"><h3>Estreito</h3><p>Bloco estreito.</p></div></div></section>`;
const ladoLista = (titulo) => `<section><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px"><h2>${titulo}</h2><ul><li>Frase um da lista.</li><li>Frase dois da lista.</li><li>Frase três da lista.</li></ul></div></section>`;
const splitImg = (titulo) => `<section><h2>${titulo}</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:center"><img src="/foto-nitida.jpg" alt="Foto de controle" style="width:100%;height:260px;object-fit:cover"><p>Texto ao lado da foto, para a seção ler como split com imagem.</p></div></section>`;
const hero = '<section><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:center"><div><h1>Título da página</h1><p>Subtítulo curto.</p><a href="#c">Ver como funciona</a></div><img src="/foto-nitida.jpg" alt="Foto de controle" style="width:100%;height:320px;object-fit:cover"></div></section>';

// Projetos mínimos para o gate-imagens com --url: dist/index.html, dist/img/foto1-800.jpg e a
// tabela de licenças. O servidor entrega cada dist/ em /p/<nome>/.
const CAB = '| Arquivo publicado | Origem | Autor | Título | Licença | Link da licença | Alteração | Pessoa identificável | Autorização de imagem | Aviso de ilustrativa |\n|---|---|---|---|---|---|---|---|---|---|\n';
function projeto(nome, corpo, pessoa) {
  const raiz = path.join(pasta, nome);
  fs.mkdirSync(path.join(raiz, 'dist', 'img'), { recursive: true });
  fs.mkdirSync(path.join(raiz, 'imagens'), { recursive: true });
  fs.copyFileSync(path.join(pasta, 'foto-nitida.jpg'), path.join(raiz, 'dist', 'img', 'foto1-800.jpg'));
  fs.writeFileSync(path.join(raiz, 'imagens', 'LICENCAS.md'), '# Licenças\n\n' + CAB + `| img/foto1-800.jpg | https://unsplash.com/photos/o1 | Fulana de Tal | | Licença Unsplash | https://unsplash.com/license | recorte | ${pessoa ? 'sim' : 'não'} | ${pessoa ? 'não' : 'não se aplica'} | sim |\n`);
  fs.writeFileSync(path.join(raiz, 'dist', 'index.html'), '<!doctype html><html lang="pt-BR"><head>' + head + estilo + '<style>img{max-width:100%}.foto{display:block;width:700px;height:400px;object-fit:cover}</style></head><body>' + corpo + '</body></html>');
  return raiz;
}
const AVISO = '<p class="av">Imagem ilustrativa de banco de imagens.</p>';
const FOTO = '<img class="foto" src="img/foto1-800.jpg" alt="Foto de controle" width="700" height="400">';
const SVG_GRANDE = (extra = '') => `<svg ${extra} data-desenho="cena grande" width="600" height="400" viewBox="0 0 600 400"><circle cx="300" cy="200" r="190" fill="#8D5A3B"/><rect x="100" y="100" width="400" height="200" fill="#555"/></svg>`;
const projetos = {
  'img-aviso-na-dobra': projeto('img-aviso-na-dobra', '<section style="min-height:0;padding:20px">' + FOTO + AVISO + '<h1>Título</h1></section>', true),
  'img-aviso-abaixo-da-dobra': projeto('img-aviso-abaixo-da-dobra', '<section style="min-height:0;padding:20px">' + FOTO + '<div style="height:900px"></div>' + AVISO + '</section>', true),
  'img-aviso-so-no-celular': projeto('img-aviso-so-no-celular', '<style>@media (max-width:600px){.foto{height:900px}}</style><section style="min-height:0;padding:20px">' + FOTO + AVISO + '</section>', true),
  'img-ilustracao-domina': projeto('img-ilustracao-domina', '<section style="min-height:0;padding:20px"><div style="display:flex;gap:16px;align-items:flex-start">' + SVG_GRANDE() + '<img src="img/foto1-800.jpg" alt="Foto de controle" width="100" height="100" style="width:100px;height:100px"></div>' + AVISO + '</section>', false),
  'img-foto-com-acento-svg': projeto('img-foto-com-acento-svg', '<section style="min-height:0;padding:20px"><div style="display:flex;gap:16px;align-items:flex-start">' + FOTO + '<svg data-desenho="traço pequeno" width="60" height="200" viewBox="0 0 60 200"><path d="M30 0v200" stroke="#555" stroke-width="3"/><circle cx="30" cy="40" r="12" fill="#8D5A3B"/></svg></div>' + AVISO + '</section>', false),
  'img-ilustracao-marcada': projeto('img-ilustracao-marcada', '<section style="min-height:0;padding:20px"><div style="display:flex;gap:16px;align-items:flex-start">' + SVG_GRANDE('data-ilustracao-ok="coluna da assinatura, acento pedido no plano"') + '<img src="img/foto1-800.jpg" alt="Foto de controle" width="100" height="100" style="width:100px;height:100px"></div>' + AVISO + '</section>', false),
};

const servidor = http.createServer((req, res) => {
  const rota = req.url.split('?')[0];
  const mp = rota.match(/^\/p\/([^/]+)\/(.*)$/);
  if (mp && projetos[mp[1]]) {
    const arq = path.join(projetos[mp[1]], 'dist', mp[2] || 'index.html');
    if (!fs.existsSync(arq)) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': arq.endsWith('.jpg') ? 'image/jpeg' : 'text/html; charset=utf-8' });
    res.end(fs.readFileSync(arq)); return;
  }
  if (rota.endsWith('.jpg')) { res.writeHead(200, { 'Content-Type': 'image/jpeg' }); res.end(fs.readFileSync(path.join(pasta, rota.slice(1)))); return; }
  let corpo = '<main><h1>Página simples</h1></main>';
  // gate-ritmo: duas seções vizinhas com o mesmo esqueleto, mais de 1 "título centralizado + cartões".
  if (rota === '/ritmo-variado') corpo = hero + ladoLista('Situações') + cartoes('Três itens') + assim('Duas formas', 'style="text-align:center"') + lista('Passos') + lista('Dúvidas', 'style="text-align:center"') + splitImg('Fecho');
  if (rota === '/ritmo-vizinhas') corpo = hero + cartoes('Primeiro bloco') + cartoes('Segundo bloco') + lista('Passos');
  if (rota === '/ritmo-centro-cartoes') corpo = hero + cartoes('Situações', 'style="text-align:center"') + lista('Passos') + cartoes('Grupo ou particular', 'style="text-align:center"') + splitImg('Fecho');
  if (rota === '/ritmo-excecao') corpo = hero + cartoes('Primeiro bloco', '', 'data-ritmo-ok="duas grades de preço pedidas pelo cliente"') + cartoes('Segundo bloco', '', 'data-ritmo-ok="duas grades de preço pedidas pelo cliente"') + lista('Passos');
  if (rota === '/ritmo-assimetrico-nao-e-cartao') corpo = hero + cartoes('Situações', 'style="text-align:center"') + lista('Passos') + assim('Para quem é', 'style="text-align:center"') + splitImg('Fecho');
  // sobreposicao.mjs: título fixo (sticky) dividindo o grid com um bloco de largura total.
  const ul = '<ul>' + Array.from({ length: 14 }, (_, i) => `<li style="height:80px;border-bottom:1px solid #ddd">Frase ${i + 1} da lista longa.</li>`).join('') + '</ul>';
  const largo = '<p class="largo" style="background:#fde;padding:24px;margin:0">Frase de impacto em largura total.</p>';
  if (rota === '/sticky-no-mesmo-grid') corpo = '<section style="min-height:0"><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px"><h2 id="t" style="position:sticky;top:20px;align-self:start;grid-row:1/-1;grid-column:1">Título fixo</h2><div style="grid-column:2">' + ul + '</div><div style="grid-column:1/-1">' + largo + '</div></div></section>' + '<div style="height:800px"></div>';
  if (rota === '/sticky-grid-termina-antes') corpo = '<section style="min-height:0"><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px"><h2 id="t" style="position:sticky;top:20px;align-self:start">Título fixo</h2><div>' + ul + '</div></div>' + largo + '</section>' + '<div style="height:800px"></div>';
  // gate-responsivo com carrossel: filhos de contêiner com overflow-x auto e scroll-snap-type não
  // são estouro; a página inteira continua sem rolagem lateral.
  const trilha = (estilo) => `<section style="padding:24px 16px;min-height:0"><h2>Aparelhos</h2><div class="trilha" style="display:flex;gap:16px;overflow-x:auto;${estilo}">${[1, 2, 3, 4].map((n) => `<figure style="flex:0 0 300px;margin:0;background:#eee;padding:12px"><h3>Aparelho ${n}</h3><p>Descrição do aparelho ${n}.</p></figure>`).join('')}</div></section>`;
  const cta = '<section><h1>Controle da página</h1><button>Ver resultado</button></section>';
  if (rota === '/carrossel-snap') corpo = cta + trilha('scroll-snap-type:x mandatory');
  if (rota === '/carrossel-sem-snap') corpo = cta + trilha('');
  if (rota === '/carrossel-snap-e-pagina-vaza') corpo = cta + trilha('scroll-snap-type:x mandatory') + '<div style="width:3000px">Conteúdo que excede a janela</div>';
  // gate-simetria com data-assimetrico: a assimetria declarada no plano (par de comparação, foto
  // deslocada, título fixo) vira aviso; a mesma falha em elemento NÃO marcado continua reprovando.
  const caixaH = (t, extra = '') => `<article style="background:#eee;padding:16px${extra}"><h3>${t}</h3><p>Descrição curta do item paralelo.</p></article>`;
  const alturas = (attr) => `<section><h2>Duas formas</h2><div ${attr} style="display:flex;gap:16px;align-items:flex-start">${caixaH('Um', ';flex:1')}${caixaH('Dois', ';flex:1')}${caixaH('Três com um título bem mais longo que os outros para quebrar em mais linhas no card', ';flex:1')}</div></section>`;
  if (rota === '/assim-sem-marca') corpo = alturas('');
  if (rota === '/assim-marcado') corpo = alturas('data-assimetrico="comparação com pesos diferentes, pedida no plano"');
  if (rota === '/assim-marca-em-outro-lugar') corpo = alturas('') + '<p data-assimetrico="outra coisa">Outro trecho marcado, sem relação com a grade.</p>';
  const colunas = (attr) => `<section ${attr} style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start"><div><h1>Título</h1><p>Texto curto.</p></div><div style="height:620px;background:#ccd"></div></section>`;
  if (rota === '/assim-colunas-sem-marca') corpo = colunas('');
  if (rota === '/assim-colunas-marcado') corpo = colunas('data-assimetrico="foto deslocada para cima, de propósito"');
  const ladoTitulo = (attr) => `<section ${attr} style="display:grid;grid-template-columns:1fr 1fr;gap:32px"><h2>Como funciona</h2><ol><li style="height:60px">Chame no WhatsApp</li><li style="height:60px">Combine o dia</li><li style="height:60px">Faça a aula</li></ol></section>`;
  if (rota === '/assim-lado-titulo-marcado') corpo = ladoTitulo('data-assimetrico="título fixo ao lado, pedido no plano"');
  // anim.mjs: uma seção que muda de cor ao entrar na tela (animada) e outra que não muda (parada).
  if (rota === '/anim') {
    corpo = '<style>.bloco{height:520px;margin:40px;background:#fff;transition:background 700ms}.bloco.vai{background:#1b3a5c}.faixa{height:900px}</style>'
      + '<div class="faixa"><h1>Topo</h1></div>'
      + '<section id="animada" style="min-height:700px"><div class="bloco"></div></section>'
      + '<div class="faixa"></div>'
      + '<section id="parada" style="min-height:700px"><div style="height:520px;margin:40px;background:#ddd"></div></section>'
      + '<div class="faixa"></div>'
      + '<script>new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)e.target.classList.add("vai")})}).observe(document.querySelector(".bloco"))</script>';
  }
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end('<!doctype html><html lang="pt-BR"><head>' + head + estilo + '</head><body>' + corpo + '</body></html>');
});

function rodar(nome, script, args, esperado, padrao) {
  return new Promise((resolve) => {
    const filho = spawn(script.endsWith('.py') ? 'python3' : process.execPath, [script, ...args], { cwd: pasta });
    let saida = '';
    filho.stdout.on('data', (d) => { saida += d; });
    filho.stderr.on('data', (d) => { saida += d; });
    const teto = setTimeout(() => filho.kill('SIGTERM'), 180000);
    filho.on('close', (code) => {
      clearTimeout(teto);
      fs.writeFileSync(path.join(pasta, nome + '.log'), saida);
      const casou = !padrao || padrao.test(saida);
      const passou = code === esperado && casou;
      console.log(`${passou ? 'OK' : 'FALHA'} ${nome}: exit=${code}, esperado=${esperado}${padrao ? `, mensagem ${casou ? 'presente' : 'AUSENTE'}` : ''}`);
      if (!passou) console.log(saida.split('\n').slice(0, 14).map((l) => '    ' + l).join('\n'));
      resolve(passou);
    });
  });
}

/** anim.mjs -> prancha.py -> gate-animacao.py contra uma página de controle. */
async function cadeia(nome, url, secoes, esperado, padrao) {
  const saida = path.join(pasta, 'anim-' + nome);
  fs.mkdirSync(saida, { recursive: true });
  const json = path.join(saida, 'secoes.json');
  fs.writeFileSync(json, JSON.stringify(secoes));
  const passos = [
    [path.join(__dirname, 'anim.mjs'), ['--url', url, '--saida', saida, '--secoes', json], 0],
    [path.join(__dirname, 'prancha.py'), ['--pasta', saida, '--secoes', json], 0],
    [path.join(__dirname, 'gate-animacao.py'), ['--pasta', saida], esperado],
  ];
  let ok = true;
  for (const [i, [arq, args, esp]] of passos.entries()) {
    const ultimo = i === passos.length - 1;
    ok = (await rodar(`${nome}-${i + 1}`, arq, args, esp, ultimo ? padrao : undefined)) && ok;
    if (!ok) break;
  }
  return ok;
}

async function unidade() {
  // A decisão do ritmo sem navegador.
  const resultados = [];
  const confere = (nome, ok, detalhe) => { console.log(`${ok ? 'OK' : 'FALHA'} ${nome}${ok ? '' : ': ' + detalhe}`); resultados.push(ok); };
  let m;
  try { m = await import(path.join(__dirname, 'ritmo-regras.mjs')); }
  catch (e) { confere('ritmo-regras-existe', false, e.message); return resultados; }
  const s = (nome, sig, excecao) => ({ nome, sig, excecao });
  const a = m.avaliarRitmo([s('A', 'x'), s('B', 'y'), s('C', 'x')]);
  confere('ritmo-unidade-nao-vizinhas-passa', a.falhas.length === 0, JSON.stringify(a));
  const b = m.avaliarRitmo([s('A', 'x'), s('B', 'x')]);
  confere('ritmo-unidade-vizinhas-reprova', b.falhas.length === 1 && /vizinhas/.test(b.falhas[0]), JSON.stringify(b));
  const c = m.avaliarRitmo([s('A', m.CENTRO_CARTOES), s('B', 'y'), s('C', m.CENTRO_CARTOES)]);
  confere('ritmo-unidade-dois-centro-cartoes-reprova', c.falhas.length === 1 && /no m[aá]ximo 1/.test(c.falhas[0]), JSON.stringify(c));
  const d = m.avaliarRitmo([s('A', m.CENTRO_CARTOES), s('B', 'y')]);
  confere('ritmo-unidade-um-centro-cartoes-passa', d.falhas.length === 0, JSON.stringify(d));
  const e = m.avaliarRitmo([s('A', 'x', 'motivo'), s('B', 'x')]);
  confere('ritmo-unidade-excecao-passa', e.falhas.length === 0 && e.excecoes.length === 1, JSON.stringify(e));
  const f = m.avaliarRitmo([s('A', 'sem-titulo:0'), s('B', 'sem-titulo:0')]);
  confere('ritmo-unidade-sem-titulo-nao-compara', f.falhas.length === 0, JSON.stringify(f));
  return resultados;
}

servidor.listen(0, '127.0.0.1', async () => {
  const url = `http://127.0.0.1:${servidor.address().port}`;
  const script = (nome) => path.join(__dirname, nome);
  const casos = [
    ['ritmo-variado', 'gate-ritmo.mjs', ['--url', url + '/ritmo-variado'], 0],
    ['ritmo-vizinhas', 'gate-ritmo.mjs', ['--url', url + '/ritmo-vizinhas'], 1, /seções vizinhas com o mesmo esqueleto/],
    ['ritmo-centro-cartoes', 'gate-ritmo.mjs', ['--url', url + '/ritmo-centro-cartoes'], 1, /2 seções no formato "título centralizado \+ cartões"/],
    ['ritmo-excecao', 'gate-ritmo.mjs', ['--url', url + '/ritmo-excecao'], 0, /exceção declarada/],
    ['ritmo-assimetrico-nao-e-cartao', 'gate-ritmo.mjs', ['--url', url + '/ritmo-assimetrico-nao-e-cartao'], 0],
    // sobreposicao.mjs
    ['sobreposicao-sticky-no-mesmo-grid-reprova', 'sobreposicao.mjs', ['--url', url + '/sticky-no-mesmo-grid', '--fixo', '#t', '--contra', '.largo'], 1, /interse[cç][aã]o m[aá]xima \d+ px²/],
    ['sobreposicao-grid-termina-antes-passa', 'sobreposicao.mjs', ['--url', url + '/sticky-grid-termina-antes', '--fixo', '#t', '--contra', '.largo'], 0, /interse[cç][aã]o m[aá]xima 0 px²/],
    ['sobreposicao-seletor-inexistente-reprova', 'sobreposicao.mjs', ['--url', url + '/sticky-grid-termina-antes', '--fixo', '#nada', '--contra', '.largo'], 1, /n[aã]o existe/],
    // gate-responsivo: carrossel
    ['responsivo-carrossel-com-encaixe-passa', 'gate-responsivo.mjs', ['--url', url + '/carrossel-snap'], 0, /carrossel com encaixe/],
    ['responsivo-carrossel-sem-encaixe-reprova', 'gate-responsivo.mjs', ['--url', url + '/carrossel-sem-snap'], 1, /elemento maior que o container/],
    ['responsivo-carrossel-e-pagina-que-vaza-reprova', 'gate-responsivo.mjs', ['--url', url + '/carrossel-snap-e-pagina-vaza'], 1, /overflow horizontal/],
    // gate-simetria: data-assimetrico
    ['simetria-sem-marca-reprova', 'gate-simetria.mjs', ['--url', url + '/assim-sem-marca'], 1, /alturas diferentes/],
    ['simetria-marcado-vira-aviso', 'gate-simetria.mjs', ['--url', url + '/assim-marcado'], 0, /AVISO \(data-assimetrico\).*alturas diferentes/],
    ['simetria-marca-em-outro-lugar-reprova', 'gate-simetria.mjs', ['--url', url + '/assim-marca-em-outro-lugar'], 1, /alturas diferentes/],
    ['simetria-colunas-sem-marca-reprova', 'gate-simetria.mjs', ['--url', url + '/assim-colunas-sem-marca'], 1, /colunas desbalanceadas/],
    ['simetria-colunas-marcado-vira-aviso', 'gate-simetria.mjs', ['--url', url + '/assim-colunas-marcado'], 0, /AVISO \(data-assimetrico\).*terminam com/],
    ['simetria-lado-titulo-marcado-vira-aviso', 'gate-simetria.mjs', ['--url', url + '/assim-lado-titulo-marcado'], 0, /AVISO \(data-assimetrico\).*lista vertical ao lado do t[ií]tulo/],
    // gate-imagens com --url: aviso na primeira tela e foto antes de ilustração.
    ['imagens-aviso-na-dobra', 'gate-imagens.py', ['--projeto', projetos['img-aviso-na-dobra'], '--url', url + '/p/img-aviso-na-dobra/'], 0, /AVISO.*tr[aá]fego real/],
    ['imagens-aviso-abaixo-da-dobra', 'gate-imagens.py', ['--projeto', projetos['img-aviso-abaixo-da-dobra'], '--url', url + '/p/img-aviso-abaixo-da-dobra/'], 1, /desktop 1440: 'imagem ilustrativa' fora da primeira tela/],
    ['imagens-aviso-so-no-celular', 'gate-imagens.py', ['--projeto', projetos['img-aviso-so-no-celular'], '--url', url + '/p/img-aviso-so-no-celular/'], 1, /celular 390: 'imagem ilustrativa' fora da primeira tela/],
    ['imagens-ilustracao-domina', 'gate-imagens.py', ['--projeto', projetos['img-ilustracao-domina'], '--url', url + '/p/img-ilustracao-domina/'], 1, /foto é \d+% da imagem da primeira tela/],
    ['imagens-foto-com-acento-svg', 'gate-imagens.py', ['--projeto', projetos['img-foto-com-acento-svg'], '--url', url + '/p/img-foto-com-acento-svg/'], 0],
    ['imagens-ilustracao-marcada', 'gate-imagens.py', ['--projeto', projetos['img-ilustracao-marcada'], '--url', url + '/p/img-ilustracao-marcada/'], 0],
  ];
  const resultados = [...await unidade()];
  if (!process.env.GATES_FILTRO || 'animacao'.startsWith(process.env.GATES_FILTRO)) {
    const todas = [{ nome: '01-animada', titulo: 'Animada', seletor: '#animada', modo: 'entrada', tipo: 'cor ao entrar' },
                   { nome: '02-parada', titulo: 'Parada', seletor: '#parada', modo: 'entrada', tipo: 'nenhuma' }];
    resultados.push(await cadeia('animacao-secao-animada', url + '/anim', [todas[0]], 0, /PASSA/));
    resultados.push(await cadeia('animacao-secao-parada', url + '/anim', todas, 1, /02-parada: desktop 1440: só 0\.0% dos pixels/));
  }
  const filtro = process.env.GATES_FILTRO;
  const selecionados = casos.filter(([nome]) => !filtro || nome.startsWith(filtro));
  for (const [nome, arquivo, args, esperado, padrao] of selecionados) {
    resultados.push(await rodar(nome, path.isAbsolute(arquivo) ? arquivo : script(arquivo), args, esperado, padrao));
  }
  console.log(`Evidências: ${pasta}`);
  console.log(`${resultados.filter(Boolean).length}/${resultados.length} controles passaram`);
  servidor.close();
  process.exitCode = resultados.every(Boolean) ? 0 : 1;
});
