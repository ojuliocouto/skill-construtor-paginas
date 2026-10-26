/** Erro de ferramenta no gate de movimento (3.7): a página que não abre no navegador não é defeito da página.
 *
 *  Defeito: quando o `page.goto` era interrompido (`net::ERR_ABORTED`, "interrupted by another navigation",
 *  `chrome-error://`, conexão derrubada, tempo esgotado), o gate caía com exceção e stack trace, e o
 *  "Conserto:" do relatório mandava mexer na animação da página, que nem chegou a abrir.
 *
 *  Agora: o gate tenta abrir de novo UMA vez; se falhar outra vez, imprime
 *  `ERRO DE FERRAMENTA: a página não abriu no navegador (<mensagem>): não é defeito da página; rode o gate de novo`
 *  e sai com 3 (não 1), sem stack trace. O rodar-gates trata saída diferente de 0 como reprova e o conserto do
 *  código 3 não culpa a animação.
 *
 *  Controle: um servidor que responde 200 ao primeiro pedido (a conferência de "no ar" do servidor-no-ar.mjs) e
 *  derruba a conexão em todos os seguintes. Segundo controle: derruba só os 2 pedidos seguintes à conferência e
 *  depois atende; o gate NÃO pode sair 3 (a segunda tentativa abre a página).
 *
 *  Precisa de navegador (Playwright): entra em PRECISAM no rodar-testes.mjs.
 */
const http = require('node:http');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');

const PAGINA = '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Controle</title></head><body>'
  + '<header><h1>Controle</h1></header><section><h2>Um</h2><p>Texto um.</p></section><section><h2>Dois</h2><p>Texto dois.</p></section></body></html>';

function subir(derrubar) {
  const estado = { pedidos: 0 };
  const servidor = http.createServer((req, res) => {
    estado.pedidos++;
    if (derrubar(estado.pedidos)) { req.socket.destroy(); return; }
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(PAGINA);
  });
  return new Promise((resolve) => servidor.listen(0, '127.0.0.1', () => resolve({ servidor, estado, url: `http://127.0.0.1:${servidor.address().port}/` })));
}

const gate = (url, extra = []) => new Promise((resolve) => {
  const filho = spawn(process.execPath, [path.join(__dirname, 'gate-movimento.mjs'), '--url', url, '--espera', '500', ...extra]);
  let log = '';
  filho.stdout.on('data', (d) => { log += d; });
  filho.stderr.on('data', (d) => { log += d; });
  filho.on('close', (c) => resolve({ code: c, log }));
});

(async () => {
  let falhas = 0;
  const checa = (nome, ok, detalhe = '') => { console.log(`  [${ok ? 'ok  ' : 'FALHA'}] ${nome}${detalhe ? ' -> ' + detalhe : ''}`); if (!ok) falhas++; };
  const fim = (r) => r.log.trim().split('\n').slice(-5).join(' | ').slice(0, 400);

  // 1. a página nunca abre (a conferência de servidor passa, o goto é derrubado)
  const a = await subir((n) => n > 1);
  let r = await gate(a.url, ['--so-celular']);
  checa('goto derrubado nas duas tentativas: saída 3, não 1', r.code === 3, `saída ${r.code}: ${fim(r)}`);
  checa('a linha começa com "ERRO DE FERRAMENTA: a página não abriu no navegador"', /ERRO DE FERRAMENTA: a página não abriu no navegador \(.+\): não é defeito da página; rode o gate de novo/.test(r.log), fim(r));
  checa('sem stack trace nem "    at " do node', !/\n\s+at .*\(.*:\d+:\d+\)/.test(r.log) && !/node:internal/.test(r.log), fim(r));
  checa('não diz REPROVA de movimento nem culpa a animação', !/REPROVA:|problema\(s\) de movimento/.test(r.log), fim(r));
  checa('tentou de novo: mais de 4 pedidos (a conferência, depois load e domcontentloaded, duas vezes)', a.estado.pedidos >= 5, `pedidos ${a.estado.pedidos}`);
  a.servidor.close();

  // 2. o conserto do código 3 não manda mexer na animação
  const { consertoDoGate } = await import(pathToFileURL(path.join(__dirname, 'conserto-de-gate.mjs')).href);
  const c = consertoDoGate('movimento', r.log, r.code);
  checa('o "Conserto:" do código 3 não manda mexer na animação da página', /^Conserto: /.test(c) && !/receitas-de-movimento|linhas FALHA/.test(c), c);

  // 3. cai nos 2 pedidos seguintes à conferência e depois atende: o gate abre a página e não sai 3
  const b = await subir((n) => n === 2 || n === 3);
  r = await gate(b.url, ['--so-celular']);
  checa('falha passageira: o gate abre a página e NÃO sai 3', r.code !== 3 && !/ERRO DE FERRAMENTA/.test(r.log), `saída ${r.code}: ${fim(r)}`);
  b.servidor.close();

  console.log(falhas ? `\n${falhas} falha(s)` : '\nTodos os testes passaram');
  process.exit(falhas ? 1 : 0);
})();
