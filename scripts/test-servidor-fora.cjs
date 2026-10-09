/**
 * P11 (3.5.10): servidor caído tem que virar mensagem clara, não stack trace.
 *
 * No teste de ponta a ponta da Torra Clara os gates estouraram com `net::ERR_CONNECTION_REFUSED` quando o servidor local
 * caiu, e quem lia achava que a página estava quebrada. Aqui cada gate de navegador roda contra uma porta onde NADA ouve:
 * tem que parar ANTES de abrir o navegador, com saída 3 e uma mensagem que começa com "servidor fora do ar em <url>", diz
 * como subir de novo e não traz o erro cru do Playwright nem pilha de chamadas. E contra um servidor que responde (até 404)
 * a conferência passa.
 *
 * Precisa do Playwright instalado (os gates o carregam antes de ler os argumentos), mas não abre nenhum navegador.
 */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const http = require('node:http');
const net = require('node:net');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const AQUI = __dirname;
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'servidor fora çá '));
const temFfmpeg = spawnSync('ffprobe', ['-version'], { encoding: 'utf8' }).status === 0;

function portaFechada() {
  return new Promise((resolve) => {
    const s = net.createServer();
    s.listen(0, '127.0.0.1', () => { const { port } = s.address(); s.close(() => resolve(port)); });
  });
}

fs.writeFileSync(path.join(tmp, 'secoes.json'), JSON.stringify([{ nome: 'hero', seletor: 'header' }]), 'utf8');
fs.mkdirSync(path.join(tmp, 'saida'), { recursive: true });
fs.mkdirSync(path.join(tmp, 'publico'), { recursive: true });
fs.writeFileSync(path.join(tmp, 'index.html'), '<html></html>', 'utf8');

const GATES = [
  ['gate-oclusao.mjs', (u) => ['--url', u]],
  ['gate-responsivo.mjs', (u) => ['--url', u]],
  ['gate-movimento.mjs', (u) => ['--url', u]],
  ['gate-texto.mjs', (u) => ['--url', u]],
  ['gate-ritmo.mjs', (u) => ['--url', u]],
  ['gate-simetria.mjs', (u) => ['--url', u]],
  ['gate-composicao.mjs', (u) => ['--url', u, '--projeto', tmp]],
  ['sobreposicao.mjs', (u) => ['--url', u, '--fixo', '#a', '--contra', '#b']],
  ['anim.mjs', (u) => ['--url', u, '--saida', path.join(tmp, 'saida'), '--secoes', path.join(tmp, 'secoes.json')]],
  ['medir-dobra.mjs', (u) => ['--url', u]],
];
if (temFfmpeg) GATES.push(['gate-video.mjs', (u) => ['--url', u, '--publico', path.join(tmp, 'publico')]]);

let falhas = 0;
const checa = (nome, cond, detalhe = '') => {
  if (cond) console.log(`ok   ${nome}`);
  else { falhas++; console.log(`FALHA ${nome}${detalhe ? `\n  ${String(detalhe).split('\n').slice(0, 6).join('\n  ')}` : ''}`); }
};

(async () => {
  const porta = await portaFechada();
  const url = `http://127.0.0.1:${porta}/`;
  for (const [arquivo, args] of GATES) {
    const r = spawnSync(process.execPath, [path.join(AQUI, arquivo), ...args(url)], { encoding: 'utf8', timeout: 60000, cwd: tmp });
    const saida = `${r.stdout || ''}${r.stderr || ''}`;
    checa(`${arquivo}: servidor fora sai com 3`, r.status === 3, `saída ${r.status}\n${saida}`);
    checa(`${arquivo}: diz "servidor fora do ar em ${url}"`, saida.includes(`servidor fora do ar em ${url}`), saida);
    checa(`${arquivo}: diz como subir de novo`, /servidor-gzip\.py/.test(saida) && /URL: http/.test(saida), saida);
    checa(`${arquivo}: sem erro cru do Playwright nem pilha de chamadas`, !/ERR_CONNECTION_REFUSED|page\.goto|\n\s+at /.test(saida), saida);
  }

  // a conferência em si
  const mod = await import(pathToFileURL(path.join(AQUI, 'servidor-no-ar.mjs')).href);
  const vivo = http.createServer((req, res) => { res.statusCode = 404; res.end('nada aqui'); });
  await new Promise((r) => vivo.listen(0, '127.0.0.1', r));
  const urlViva = `http://127.0.0.1:${vivo.address().port}/`;
  const ok = await mod.conferirServidor(urlViva, { tentativas: 1 });
  checa('conferirServidor: servidor que responde (mesmo 404) está no ar', ok.ok === true, JSON.stringify(ok));
  vivo.close();
  const fora = await mod.conferirServidor(url, { tentativas: 2, esperaMs: 50 });
  checa('conferirServidor: porta sem ninguém está fora do ar, com o motivo', fora.ok === false && /recusad/.test(fora.motivo), JSON.stringify(fora));
  const arquivoLocal = await mod.conferirServidor(pathToFileURL(path.join(tmp, 'index.html')).href, { tentativas: 1 });
  checa('conferirServidor: file:// não tem servidor para conferir', arquivoLocal.ok === true);
  const msg = mod.mensagemServidorFora(url, 'nada ouve nessa porta (conexão recusada)');
  checa('a mensagem não tem travessão', !msg.includes('—'));
  checa('a mensagem diz que não é veredito sobre a página', /não é veredito sobre a página/.test(msg));

  process.exitCode = falhas ? 1 : 0;
  console.log(falhas ? `\n${falhas} falha(s)` : '\nTudo verde.');
})().catch((e) => { console.error('FALHA inesperada:', e.stack); process.exit(1); });
