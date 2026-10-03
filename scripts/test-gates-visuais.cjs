/** Páginas locais controladas isolam defeitos sem depender de site de cliente. */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn, execFileSync } = require('node:child_process');

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'gates-visuais-'));
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=gray:s=320x180:r=10', '-t', '8', '-pix_fmt', 'yuv420p', path.join(pasta, 'controle.mp4')]);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', path.join(pasta, 'controle.mp4'), '-frames:v', '1', path.join(pasta, 'poster.png')]);
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64');
const head = '<title>Página de controle</title><meta name="description" content="Controle local de qualidade"><meta property="og:title" content="Controle"><meta property="og:description" content="Página de teste"><meta property="og:image" content="/icon.png"><link rel="icon" type="image/png" href="/icon.png"><link rel="apple-touch-icon" href="/icon.png">';
const style = '<style>body{margin:0;font:18px Arial;background:#fff;color:#111}section{padding:24px}button,a{display:inline-block;padding:16px;background:#111;color:white;border:0;font:18px Arial}p{max-width:600px;line-height:1.6}.kpi__value{font-size:40px}</style>';
const texto = '<section><h1>Controle da página</h1><p>Esta página permite verificar o resultado do gate com uma entrada conhecida e reproduzível.</p><button onclick="this.textContent=\'Resultado confirmado\'">Ver resultado</button></section>';
const servidor = http.createServer((req, res) => {
  if (['/controle.mp4', '/poster.png'].includes(req.url)) {
    res.writeHead(200, { 'Content-Type': req.url.endsWith('mp4') ? 'video/mp4' : 'image/png' });
    res.end(fs.readFileSync(path.join(pasta, req.url.slice(1)))); return;
  }
  if (req.url === '/icon.png') { res.writeHead(200, { 'Content-Type': 'image/png' }); res.end(png); return; }
  const rota = req.url.split('?')[0];
  let corpo = texto;
  if (rota === '/inerte') corpo = texto.replace('onclick="this.textContent=\'Resultado confirmado\'"', '');
  if (rota === '/coberto') corpo += '<div style="position:fixed;inset:0;background:white;z-index:100"></div>';
  if (rota === '/overflow') corpo += '<div style="width:3000px">Conteúdo que excede a janela</div>';
  if (rota === '/video') corpo += '<video src="/inexistente.mp4" width="320" height="180"></video>';
  if (rota === '/video-ok') corpo += '<link rel="preload" as="image" href="/poster.png" fetchpriority="high"><video src="/controle.mp4" poster="/poster.png" width="320" height="180"></video>';
  // Relatorio do aluno: o 1o elemento do seletor estava escondido no viewport e o clique
  // dava "locator.waitFor: Timeout"; e link wa.me sem numero passava como OK.
  if (rota === '/primeiro-oculto') corpo = texto.replace('<button', '<button style="display:none">Menu</button><button');
  if (rota === '/todos-ocultos') corpo = texto.replace('<button', '<button style="display:none"');
  if (rota === '/wame-sem-numero') corpo += '<a href="https://wa.me/?text=Ol%C3%A1">Chamar no WhatsApp</a>';
  // Link "Pular para o conteudo" no padrao sr-only (clip 1px) reprovava as 12 telas como
  // "texto cortado", empurrando o aluno a apagar um recurso de acessibilidade.
  if (rota === '/sr-only') corpo = '<a href="#c" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border-width:0">Pular para o conteúdo</a>' + texto;
  // Auditoria da v3 (02/10/2026): o botão principal quebrava em 2 linhas em 360 e 320 px e o
  // gate passava; no celular eram 6 telas sem botão nenhum entre o hero e o fecho.
  const longo = '<p>' + 'Texto corrido de seção para ocupar a tela do celular sem nenhum botão no meio. '.repeat(6) + '</p>';
  if (rota === '/botao-duas-linhas') corpo = texto.replace('Ver resultado', 'Agendar aula experimental grátis pelo WhatsApp');
  if (rota === '/sem-cta-longo') corpo = texto + longo.repeat(14);
  // A barra fixa só aparece quando o botão do herói sai da tela (auditoria da v4: barra sempre
  // visível somava 3 botões na mesma tela e cobria o botão da página).
  const barra = '<div style="height:80px"></div><a id="barra" href="#c" style="position:fixed;left:12px;right:12px;bottom:12px;text-align:center;visibility:hidden">Agendar agora</a><script>var b=document.getElementById("barra"),h=document.querySelector("section button, section a");addEventListener("scroll",function(){b.style.visibility=h.getBoundingClientRect().bottom<0?"visible":"hidden"},{passive:true})</script>';
  if (rota === '/cta-fixo') corpo = texto + longo.repeat(14) + barra;
  // Auditoria da v4 no celular: cabeçalho fixo com botão + barra fixa = 152 px (18% da tela em
  // 390, 28,3% em 320), 3 botões na mesma tela, barra cobrindo botão e foto fora da 1a tela.
  if (rota === '/fixos-demais') corpo = '<header style="position:sticky;top:0;height:100px;background:#ddd">Marca</header>' + texto + longo.repeat(14) + '<div style="position:fixed;left:0;right:0;bottom:0;height:90px;background:#222"></div>';
  if (rota === '/dois-botoes') corpo = texto.replace('</button>', '</button> <a href="#c">Agendar</a>');
  if (rota === '/botao-coberto') corpo = texto + (longo.repeat(2) + '<a href="#c">Agendar no meio</a>').repeat(6) + '<a href="#c" style="position:fixed;left:0;right:0;bottom:0;text-align:center">Agendar agora</a>';
  const foto = '<img src="/poster.png" width="320" height="180" alt="Foto de controle" style="display:block;width:100%;height:40vh;object-fit:cover">';
  if (rota === '/hero-foto-ok') corpo = '<section><h1>Controle da página</h1>' + foto + '<button>Ver resultado</button><p>Esta página permite verificar o resultado do gate.</p></section>' + longo;
  if (rota === '/hero-foto-baixa') corpo = '<section><h1>Controle da página</h1><p>' + 'Texto longo antes da foto do herói, que empurra a imagem para baixo da dobra. '.repeat(5) + '</p><button>Ver resultado</button>' + foto + '</section>' + longo;
  // gate-simetria (auditoria da v3): escada de itens soltos, alturas diferentes, passos ao lado
  // do título e colunas que terminam 200 px uma antes da outra.
  const caixa = (t, extra = '') => `<article style="background:#eee;padding:16px${extra}"><h3>${t}</h3><p>Descrição curta do item paralelo.</p></article>`;
  if (rota === '/grade-ok') corpo = texto + '<section><h2>Três itens</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">' + caixa('Um') + caixa('Dois') + caixa('Três com um título bem mais longo que os outros para quebrar') + '</div></section>';
  if (rota === '/grade-escada') corpo = texto + '<section><h2>Itens soltos</h2><ul style="list-style:none;padding:0"><li style="margin-left:0;width:50%;height:120px">Primeira situação comum</li><li style="margin-left:25%;width:50%;height:90px">Segunda situação comum</li><li style="margin-left:45%;width:50%;height:120px">Terceira situação comum</li></ul></section>';
  if (rota === '/grade-alturas') corpo = texto + '<section><h2>Três itens</h2><div style="display:flex;gap:16px;align-items:flex-start">' + caixa('Um', ';flex:1') + caixa('Dois', ';flex:1') + caixa('Três com um título bem mais longo que os outros para quebrar em mais linhas no card', ';flex:1') + '</div></section>';
  if (rota === '/passos-ao-lado') corpo = texto + '<section style="display:grid;grid-template-columns:1fr 1fr;gap:32px"><h2>Como funciona</h2><ol><li style="height:60px">Chame no WhatsApp</li><li style="height:60px">Combine o dia</li><li style="height:60px">Faça a aula</li></ol></section>';
  if (rota === '/colunas-desbalanceadas') corpo = '<section style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start"><div><h1>Título</h1><p>Texto curto.</p><button>Ver resultado</button></div><div style="height:620px;background:#ccd"></div></section>';
  // Auditoria da v4: "Duas formas" tinha as caixas com a mesma altura e o título de uma 147 px
  // acima do da outra (ícone e nota com margin-top:auto); o gate media só a caixa.
  const card = (miolo) => `<article style="display:flex;flex-direction:column;background:#eee;padding:16px">${miolo}</article>`;
  const par = (a, b) => texto + '<section><h2>Duas formas</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">' + card(a) + card(b) + '</div></section>';
  if (rota === '/cards-ok') corpo = par('<div style="height:200px;background:#ccd"></div><h3>Em grupo</h3><p>Até quatro pessoas por turma.</p>', '<div style="height:200px;background:#ccd"></div><h3>Particular</h3><p>Aula individual.</p>');
  if (rota === '/cards-titulo-desalinhado') corpo = par('<div style="height:260px;background:#ccd"></div><h3>Em grupo</h3><p>Até quatro pessoas por turma.</p>', '<div style="height:80px;width:80px;margin:auto auto 0;background:#ccd"></div><h3>Particular</h3><p>Aula individual.</p><p style="margin-top:auto">O valor vem pelo WhatsApp.</p>');
  if (rota === '/cards-buraco') corpo = par('<h3>Em grupo</h3><p>Até quatro pessoas por turma.</p><div style="height:220px;background:#ccd"></div>', '<h3>Particular</h3><p>Aula individual.</p><p style="margin-top:auto">O valor de cada forma vem pelo WhatsApp.</p>');
  // gate-composicao (auditoria da v4): 4 seções seguidas com o mesmo esqueleto (h2 à esquerda +
  // grade de caixas), ícones de biblioteca (balão, calendário com check, boneco de palito).
  const grade3 = (n) => `<section><h2>Seção em grade ${n}</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">${caixa('Um')}${caixa('Dois')}${caixa('Três')}</div></section>`;
  const desenho = (d, miolo = '<path d="M8 40c10-20 30-20 40 0"/>') => `<svg data-desenho="${d}" width="56" height="56" viewBox="0 0 56 56" aria-hidden="true" fill="none" stroke="#111">${miolo}</svg>`;
  if (rota === '/composicao-repetida') corpo = texto + grade3(1) + grade3(2) + grade3(3);
  if (rota === '/composicao-variada') corpo = texto + grade3(1)
    + '<section><div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:center"><div><h2>Seção em split</h2><p>Texto ao lado da imagem.</p></div><img src="/poster.png" width="320" height="180" alt="Imagem de controle" style="width:100%;height:auto"></div></section>'
    + '<section style="text-align:center"><h2>Seção em lista</h2>' + desenho('coluna vertebral de perfil') + '<ul style="list-style:none;padding:0"><li>Primeira linha da lista</li><li>Segunda linha da lista</li><li>Terceira linha da lista</li></ul></section>'
    + grade3(4);
  if (rota === '/icone-generico') corpo = texto + '<section><h2>Ícones</h2>' + desenho('balão de conversa com três pontos') + '</section>';
  if (rota === '/icone-sem-desenho') corpo = texto + '<section><h2>Ícones</h2><svg width="56" height="56" viewBox="0 0 56 56" aria-hidden="true"><path d="M8 40h40"/></svg></section>';
  if (rota === '/icone-repetido') corpo = texto + '<section><h2>Ícones</h2>' + desenho('duas pessoas lado a lado') + '<p>Entre os dois.</p>' + desenho('aluna e instrutora') + '</section>';
  // gate-texto (auditoria da v3): viúva em título, item em minúscula e itálico colorido repetido.
  const curta = '<section><h1>Página curta</h1><p>Texto normal com uma <em style="color:#24525A">palavra</em> só.</p><dl><dt>Em grupo</dt><dd>Até 4 pessoas</dd></dl></section>';
  if (rota === '/texto-ok') corpo = curta;
  if (rota === '/viuva') corpo = curta + '<h2 style="width:9ch;font:32px/1.2 monospace">aaaa bbbb c</h2>';
  // Auditoria da v4: o gate media só h1 e h2 e só até 360 px; em 320 o h2 do fecho e dois h3
  // ficavam com palavra sozinha, e em 768 os 3 h3 dos passos também.
  if (rota === '/viuva-h3-320') corpo = curta + '<style>@media (max-width:340px){.t3{width:9ch}}</style><h3 class="t3" style="font:24px/1.2 monospace">Aaaa bbbb c</h3>';
  if (rota === '/viuva-titulo-card') corpo = curta.replace('<dt>Em grupo</dt>', '<dt style="width:9ch;font:24px/1.2 monospace">Aaaa bbbb c</dt>');
  if (rota === '/minuscula') corpo = curta.replace('Até 4 pessoas', 'até 4 pessoas');
  if (rota === '/italicos') corpo = curta + '<h2>Outro <em style="color:#24525A">título</em></h2><h2>Mais <em style="color:#24525A">um</em></h2>';
  // gate-movimento (auditoria da v4): um setTimeout de 3 s revelava todas as seções com a página
  // parada no topo; a visita que lê o topo por 8 s chegava em seções já reveladas e paradas.
  const secoesMov = (extra, comMovimento = true) => '<style>.js .revela{opacity:0;transform:translateY(20px);transition:opacity .6s,transform .6s}.js .revela.visivel{opacity:1;transform:none}.alta{min-height:1000px}</style><script>document.documentElement.classList.add("js")</script>'
    + texto + [1, 2, 3].map((i) => `<section class="alta"><h2 class="${comMovimento ? 'revela' : ''}">Seção ${i}</h2><p class="${comMovimento ? 'revela' : ''}">Texto da seção ${i} que entra ao rolar a página.</p></section>`).join('')
    + '<script>var els=document.querySelectorAll(".revela");var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("visivel");io.unobserve(e.target)}})});els.forEach(function(e){io.observe(e)});' + extra + '</script>';
  if (rota === '/movimento-ok') corpo = secoesMov('');
  if (rota === '/movimento-temporizador') corpo = secoesMov('setTimeout(function(){els.forEach(function(e){e.classList.add("visivel")})},3000);');
  if (rota === '/movimento-parado') corpo = secoesMov('', false);
  if (rota.startsWith('/dash')) corpo ='<h1>Painel 2026</h1><div class="kpi__value">' + (rota === '/dash-ok' ? 'R$ 150,00' : '&#8212;') + '</div>';
  res.writeHead(rota === '/erro' ? 500 : 200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end('<!doctype html><html lang="pt-BR"><head><meta name="viewport" content="width=device-width,initial-scale=1">' + (rota === '/sem-identidade' ? '' : head) + style + '</head><body>' + corpo + '</body></html>');
});

function rodar(nome, script, args, esperado, padrao) {
  return new Promise((resolve) => {
    const filho = spawn(process.execPath, [script, ...args], { cwd: pasta });
    let saida = '';
    filho.stdout.on('data', d => { saida += d; });
    filho.stderr.on('data', d => { saida += d; });
    const teto = setTimeout(() => filho.kill('SIGTERM'), 180000);
    filho.on('close', code => {
      clearTimeout(teto);
      fs.writeFileSync(path.join(pasta, nome + '.log'), saida);
      const casou = !padrao || padrao.test(saida);
      const passou = code === esperado && casou;
      console.log(`${passou ? 'OK' : 'FALHA'} ${nome}: exit=${code}, esperado=${esperado}${padrao ? `, mensagem ${casou ? 'presente' : 'AUSENTE'}` : ''}`);
      resolve(passou);
    });
  });
}

servidor.listen(0, '127.0.0.1', async () => {
  const url = `http://127.0.0.1:${servidor.address().port}`;
  const script = nome => path.join(__dirname, nome);
  const casos = [
    ['identidade-positiva', 'screenshot-prova.js', [url + '/ok', path.join(pasta, 'identidade-positiva')], 0],
    ['identidade-negativa', 'screenshot-prova.js', [url + '/sem-identidade', path.join(pasta, 'identidade-negativa')], 1],
    ['clique-inerte', 'screenshot-prova.js', [url + '/inerte', path.join(pasta, 'inerte'), '--click', 'button'], 1],
    ['clique-positivo', 'screenshot-prova.js', [url + '/ok', path.join(pasta, 'clique'), '--click', 'button'], 0],
    ['http-negativo', 'screenshot-prova.js', [url + '/erro', path.join(pasta, 'erro')], 1],
    ['clique-primeiro-oculto', 'screenshot-prova.js', [url + '/primeiro-oculto', path.join(pasta, 'primeiro-oculto'), '--click', 'button'], 0],
    ['clique-todos-ocultos', 'screenshot-prova.js', [url + '/todos-ocultos', path.join(pasta, 'todos-ocultos'), '--click', 'button'], 1, /existe mas est[aá] oculto/],
    ['wame-sem-numero', 'screenshot-prova.js', [url + '/wame-sem-numero', path.join(pasta, 'wame')], 0, /sem n[uú]mero/],
    ['oclusao-positiva', 'gate-oclusao.mjs', ['--url', url + '/ok'], 0],
    ['oclusao-negativa', 'gate-oclusao.mjs', ['--url', url + '/coberto'], 1],
    ['responsivo-positivo', 'gate-responsivo.mjs', ['--url', url + '/ok'], 0],
    ['responsivo-negativo', 'gate-responsivo.mjs', ['--url', url + '/overflow'], 1],
    ['responsivo-sr-only', 'gate-responsivo.mjs', ['--url', url + '/sr-only'], 0],
    ['responsivo-botao-duas-linhas', 'gate-responsivo.mjs', ['--url', url + '/botao-duas-linhas'], 1, /quebra em \d linhas/],
    ['responsivo-sem-cta-longo', 'gate-responsivo.mjs', ['--url', url + '/sem-cta-longo'], 1, /sem nenhum bot[aã]o/],
    ['responsivo-cta-fixo', 'gate-responsivo.mjs', ['--url', url + '/cta-fixo'], 0],
    ['responsivo-fixos-demais', 'gate-responsivo.mjs', ['--url', url + '/fixos-demais'], 1, /espa[cç]o fixo/],
    ['responsivo-dois-botoes', 'gate-responsivo.mjs', ['--url', url + '/dois-botoes'], 1, /bot[oõ]es de a[cç][aã]o na mesma tela/],
    ['responsivo-botao-coberto', 'gate-responsivo.mjs', ['--url', url + '/botao-coberto'], 1, /coberto ou encostado/],
    ['responsivo-hero-foto-ok', 'gate-responsivo.mjs', ['--url', url + '/hero-foto-ok'], 0],
    ['responsivo-hero-foto-baixa', 'gate-responsivo.mjs', ['--url', url + '/hero-foto-baixa'], 1, /foto do her[oó]i/],
    ['simetria-positiva', 'gate-simetria.mjs', ['--url', url + '/grade-ok'], 0],
    ['simetria-pagina-simples', 'gate-simetria.mjs', ['--url', url + '/ok'], 0],
    ['simetria-escada', 'gate-simetria.mjs', ['--url', url + '/grade-escada'], 1, /escada/],
    ['simetria-alturas', 'gate-simetria.mjs', ['--url', url + '/grade-alturas'], 1, /alturas diferentes/],
    ['simetria-passos-ao-lado', 'gate-simetria.mjs', ['--url', url + '/passos-ao-lado'], 1, /lista vertical ao lado do t[ií]tulo/],
    ['simetria-colunas', 'gate-simetria.mjs', ['--url', url + '/colunas-desbalanceadas'], 1, /colunas desbalanceadas/],
    ['simetria-cards-ok', 'gate-simetria.mjs', ['--url', url + '/cards-ok'], 0],
    ['simetria-cards-titulo', 'gate-simetria.mjs', ['--url', url + '/cards-titulo-desalinhado'], 1, /t[ií]tulos de cards vizinhos desalinhados/],
    ['simetria-cards-buraco', 'gate-simetria.mjs', ['--url', url + '/cards-buraco'], 1, /buraco interno/],
    ['composicao-variada', 'gate-composicao.mjs', ['--url', url + '/composicao-variada'], 0],
    ['composicao-repetida', 'gate-composicao.mjs', ['--url', url + '/composicao-repetida'], 1, /mesmo esqueleto/],
    ['composicao-icone-generico', 'gate-composicao.mjs', ['--url', url + '/icone-generico'], 1, /gen[eé]rico/],
    ['composicao-icone-sem-desenho', 'gate-composicao.mjs', ['--url', url + '/icone-sem-desenho'], 1, /sem data-desenho/],
    ['composicao-icone-repetido', 'gate-composicao.mjs', ['--url', url + '/icone-repetido'], 1, /repetido/],
    ['texto-positivo', 'gate-texto.mjs', ['--url', url + '/texto-ok'], 0],
    ['texto-viuva', 'gate-texto.mjs', ['--url', url + '/viuva'], 1, /vi[uú]va/],
    ['texto-viuva-h3-320', 'gate-texto.mjs', ['--url', url + '/viuva-h3-320'], 1, /menor suportado.*h3/],
    ['texto-viuva-titulo-card', 'gate-texto.mjs', ['--url', url + '/viuva-titulo-card'], 1, /vi[uú]va: dt/],
    ['texto-minuscula', 'gate-texto.mjs', ['--url', url + '/minuscula'], 1, /min[uú]scula: <dd> "at[eé] 4/],
    ['texto-italicos', 'gate-texto.mjs', ['--url', url + '/italicos'], 1, /it[aá]lico colorido/],
    ['movimento-positivo', 'gate-movimento.mjs', ['--url', url + '/movimento-ok'], 0],
    ['movimento-temporizador', 'gate-movimento.mjs', ['--url', url + '/movimento-temporizador'], 1, /fora da tela/],
    ['movimento-parado', 'gate-movimento.mjs', ['--url', url + '/movimento-parado'], 1, /animam ao chegar/],
    ['identidade-360','screenshot-prova.js', [url + '/ok', path.join(pasta, 'identidade-360'), '--com-360'], 0, /topo +mobile360: scrollY 0/],
    ['video-ausente', 'gate-video.mjs', ['--url', url + '/ok', '--publico', pasta, '--frames', path.join(pasta, 'frames-ausente')], 0],
    ['video-positivo', 'gate-video.mjs', ['--url', url + '/video-ok', '--publico', pasta, '--frames', path.join(pasta, 'frames-positivo')], 0],
    ['video-negativo', 'gate-video.mjs', ['--url', url + '/video', '--publico', pasta, '--frames', path.join(pasta, 'frames-negativo')], 1],
  ];
  const dash = process.argv[2];
  if (dash) {
    casos.push(['dash-positivo', dash, [url + '/dash-ok', '--out', path.join(pasta, 'dash-ok')], 0]);
    casos.push(['dash-vazio', dash, [url + '/dash-vazio', '--out', path.join(pasta, 'dash-vazio')], 1]);
  }
  const resultados = [];
  const selecionados = casos.filter(([nome]) => !process.env.GATES_FILTRO || nome.startsWith(process.env.GATES_FILTRO));
  if (!selecionados.length) throw new Error('O filtro não selecionou nenhum controle.');
  // Duas execuções por vez evitam que falta de memória pareça defeito da página.
  for (let i = 0; i < selecionados.length; i += 2) {
    resultados.push(...await Promise.all(selecionados.slice(i, i + 2).map(([nome, arquivo, args, esperado, padrao]) =>
      rodar(nome, path.isAbsolute(arquivo) ? arquivo : script(arquivo), args, esperado, padrao))));
  }
  console.log(`Evidências: ${pasta}`);
  console.log(`${resultados.filter(Boolean).length}/${resultados.length} controles passaram`);
  servidor.close();
  process.exitCode = resultados.every(Boolean) ? 0 : 1;
});
