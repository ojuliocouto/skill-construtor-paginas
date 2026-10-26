/** A prova de tela REPROVA quando o print sai com imagem quebrada ou fonte que não carregou (3.7).
 *
 *  Defeito: o print saía "PASSA" com `<img>` quebrada e com `@font-face` apontando para arquivo
 *  inexistente: o PNG mostrava o ícone de imagem quebrada ou a fonte de reserva, e a prova só media
 *  a identidade do <head>. Agora o screenshot-prova.js confere, antes do print, `img.complete` com
 *  `naturalWidth === 0`, imagem que não terminou de carregar e `document.fonts` em erro, e a falha diz
 *  QUAL imagem (src) e QUAL fonte.
 *
 *  Precisa de navegador (Playwright): entra em PRECISAM no rodar-testes.mjs.
 *
 *  Fixtures locais mínimas (servidor Node na porta livre), todas com o <head> completo para a identidade passar:
 *   1. `<img src="nao-existe.png">` reprova (exit 1) e a saída traz o src;
 *   2. a mesma página com a imagem existente passa (exit 0);
 *   3. `@font-face` com arquivo inexistente e usada no texto reprova e traz o nome da fonte;
 *   4. `@font-face` com arquivo existente e usada passa;
 *   5. `@font-face` quebrada mas NÃO usada em lugar nenhum não reprova (a face fica "unloaded":
 *      o navegador nunca tentou baixar, então não há erro a apontar);
 *   6. o `provar.mjs --so prints` repassa: relatório REPROVA e o fim do laudo traz o src.
 */
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn } = require('node:child_process');

// PNG 1x1 vermelho (quadrado: serve de favicon e de imagem da página)
// PNG 1x1 em base64, partido em dois pedaços para o audit-secrets não confundir "EAAA..." com token da Meta.
const PNG = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB' + 'CAYAAAAfFcSJAAAADUlEQVR4nGP4z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg==', 'base64');
const FONTE = fs.readFileSync(path.join(__dirname, 'fixtures', 'larga.ttf'));

const pagina = (corpo, estilo = '') => '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
  + '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Pagina de controle dos recursos</title>'
  + '<meta name="description" content="Pagina de controle para a prova de imagens e fontes."><link rel="icon" type="image/png" href="/icone.png">'
  + '<meta property="og:title" content="Controle"><meta property="og:description" content="Controle da prova"><meta property="og:image" content="/icone.png">'
  + `<style>body{margin:0;font:18px Arial}${estilo}</style></head><body>${corpo}</body></html>`;
const SECAO = '<section style="height:300px"><p>Texto da página de controle.</p></section>';

const PAGINAS = {
  '/img-quebrada': pagina(`<h1>Título</h1><img src="nao-existe.png" alt="foto que não existe" width="120" height="80">${SECAO}`),
  '/img-boa': pagina(`<h1>Título</h1><img src="/icone.png" alt="foto" width="120" height="80">${SECAO}`),
  '/fonte-quebrada': pagina(`<h1 class="f">Título com a fonte</h1>${SECAO}`,
    '@font-face{font-family:"FonteQuebradaXyz";src:url("/fonte-que-nao-existe.woff2") format("woff2")}.f{font-family:"FonteQuebradaXyz",Arial}'),
  '/fonte-boa': pagina(`<h1 class="f">Título com a fonte</h1>${SECAO}`,
    '@font-face{font-family:"FonteBoaXyz";src:url("/larga.ttf") format("truetype")}.f{font-family:"FonteBoaXyz",Arial}'),
  '/fonte-quebrada-sem-uso': pagina(`<h1>Título</h1>${SECAO}`,
    '@font-face{font-family:"FonteSemUsoXyz";src:url("/fonte-que-nao-existe.woff2") format("woff2")}'),
};
const servidor = http.createServer((req, res) => {
  const rota = req.url.split('?')[0];
  if (rota === '/icone.png') { res.writeHead(200, { 'Content-Type': 'image/png' }); return res.end(PNG); }
  if (rota === '/larga.ttf') { res.writeHead(200, { 'Content-Type': 'font/ttf' }); return res.end(FONTE); }
  if (PAGINAS[rota]) { res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' }); return res.end(PAGINAS[rota]); }
  res.writeHead(404, { 'Content-Type': 'text/plain' }); res.end('nao existe');
});

const rodar = (script, args) => new Promise((resolve) => {
  const filho = spawn(process.execPath, [path.join(__dirname, script), ...args]);
  let log = '';
  filho.stdout.on('data', (d) => { log += d; });
  filho.stderr.on('data', (d) => { log += d; });
  filho.on('close', (c) => resolve({ code: c, log }));
});

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'recursos-prova-'));
servidor.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${servidor.address().port}`;
  let falhas = 0;
  const checa = (nome, ok, detalhe = '') => { console.log(`  [${ok ? 'ok  ' : 'FALHA'}] ${nome}${detalhe ? ' -> ' + detalhe : ''}`); if (!ok) falhas++; };
  const fim = (r) => r.log.trim().split('\n').slice(-6).join(' | ');
  const prova = (rota) => rodar('screenshot-prova.js', [base + rota, path.join(pasta, rota.slice(1))]);

  let r = await prova('/img-quebrada');
  checa('imagem quebrada reprova (exit 1)', r.code === 1, `exit ${r.code}: ${fim(r)}`);
  checa('a falha diz QUAL imagem (o src)', /nao-existe\.png/.test(r.log), fim(r));
  checa('a falha é de imagem, não de identidade', /imagem/i.test(r.log) && !/REPROVA\s+<title>|ausente/.test(r.log), fim(r));
  checa('os prints ficam salvos mesmo reprovando', fs.existsSync(path.join(pasta, 'img-quebrada', 'prova-desktop.png')));

  r = await prova('/img-boa');
  checa('a mesma página com a imagem existente passa (exit 0)', r.code === 0, `exit ${r.code}: ${fim(r)}`);

  r = await prova('/fonte-quebrada');
  checa('fonte que não carregou reprova (exit 1)', r.code === 1, `exit ${r.code}: ${fim(r)}`);
  checa('a falha diz QUAL fonte', /FonteQuebradaXyz/.test(r.log), fim(r));

  r = await prova('/fonte-boa');
  checa('fonte existente e usada passa (exit 0)', r.code === 0, `exit ${r.code}: ${fim(r)}`);

  r = await prova('/fonte-quebrada-sem-uso');
  checa('@font-face quebrada mas sem uso na página não reprova (o navegador nunca a baixou)', r.code === 0, `exit ${r.code}: ${fim(r)}`);

  // o provar.mjs só prints, contra a URL já servida
  const proj = path.join(pasta, 'proj');
  fs.mkdirSync(proj, { recursive: true });
  r = await rodar('provar.mjs', ['--projeto', proj, '--url', `${base}/img-quebrada`, '--so', 'prints', '--sem-registrar', '--tempo-max', '120']);
  checa('provar.mjs: o relatório REPROVA os prints com imagem quebrada (exit 1)', r.code === 1 && /REPROVA\s+prints/.test(r.log), `exit ${r.code}: ${fim(r)}`);
  checa('provar.mjs: o fim do laudo traz o src da imagem', /nao-existe\.png/.test(r.log), fim(r));

  servidor.close();
  console.log(falhas ? `\n${falhas} falha(s)` : '\nTodos os testes passaram');
  process.exit(falhas ? 1 : 0);
});
