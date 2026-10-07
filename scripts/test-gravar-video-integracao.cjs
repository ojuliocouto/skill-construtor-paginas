/**
 * Integração do gravador de vídeo de prova: grava de verdade (Chromium do Playwright) uma página
 * local mínima, numa pasta com ESPAÇO e ACENTO, e confere que:
 *  - o arquivo de vídeo existe, tem mais de 0 byte e é WebM;
 *  - a duração lida do próprio WebM cai dentro da faixa (sem ffprobe) e bate com a marca de tempo dos passos;
 *  - a rolagem foi do topo ao fim da página falsa (a própria página avisa o servidor quando chega ao fim), em desktop e celular;
 *  - saíram 7 quadros e a prancha;
 *  - uma rolagem que não chega ao fim dentro de max_passos reprova (vídeo pela metade nunca vale);
 *  - um roteiro inválido é recusado antes de abrir o navegador.
 * Sem Playwright, avisa que foi PULADO (não finge que passou).
 * Uso: node scripts/test-gravar-video-integracao.cjs
 */
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { acharPlaywright } = require('./video/achar-playwright.cjs');

const GRAVADOR = process.env.GRAVADOR || path.join(__dirname, 'gravar-video.js');
// Assíncrono de propósito: o servidor da página vive neste mesmo processo, e um spawnSync o travaria.
function rodar(args, tempoMs) {
  return new Promise((resolve) => {
    const f = spawn(process.execPath, args, { windowsHide: true });
    let stdout = '';
    let stderr = '';
    f.stdout.on('data', (d) => { stdout += d; });
    f.stderr.on('data', (d) => { stderr += d; });
    const relogio = setTimeout(() => f.kill(), tempoMs);
    f.on('close', (status) => { clearTimeout(relogio); resolve({ status, stdout, stderr }); });
  });
}

let falhas = 0;
const checa = (nome, ok, det = '') => { console.log(`${ok ? 'ok   ' : 'FALHA'} ${nome}${det ? ' -> ' + det : ''}`); if (!ok) falhas++; };

const PAGINA = `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>página falsa</title>
<style>body{font:20px system-ui;margin:0}h1{font-size:48px;margin:40px 30px}section{height:700px;padding:30px;border-top:1px solid #ccc}
.sobe{opacity:0;transform:translateY(30px);transition:opacity .8s,transform .8s}.sobe.v{opacity:1;transform:none}</style>
<h1>Página falsa de teste</h1>
<section><p class="sobe">Primeira seção</p></section><section><p class="sobe">Segunda seção</p></section>
<section><p class="sobe">Terceira seção</p></section><section><p class="sobe">Quarta seção</p></section>
<section><p class="sobe">Quinta seção</p></section><section id="ultima"><p class="sobe">Fim da página</p></section>
<script>
const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) e.target.classList.add('v'); }), { threshold: 0.2 });
document.querySelectorAll('.sobe').forEach((n) => io.observe(n));
let avisou = false;
addEventListener('scroll', () => { if (!avisou && scrollY + innerHeight >= document.documentElement.scrollHeight - 2) { avisou = true; fetch('/chegou-ao-fim?perfil=' + (innerWidth < 600 ? 'mobile' : 'desktop')); } }, { passive: true });
</script></html>`;

const roteiro = {
  nome: 'teste da rolagem',
  duracao_minima_s: 12,
  passos: [
    { acao: 'abrir' }, { acao: 'esperar', ms: 1200 }, { acao: 'print', nome: 'abertura' },
    { acao: 'rolar_pagina', passo: 0.5, espera_ms: 700, max_passos: 30, prints: 5 },
    { acao: 'print', nome: 'fim' },
  ],
};

(async () => {
  const pw = acharPlaywright();
  if (!pw) { console.log('PULADO: Playwright não encontrado (npm i -g playwright). Esta integração NÃO rodou.'); return; }
  const fins = new Set();
  const servidor = http.createServer((req, res) => {
    if (req.url.startsWith('/chegou-ao-fim')) { fins.add(new URL(req.url, 'http://x').searchParams.get('perfil')); res.writeHead(204); res.end(); return; }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(PAGINA);
  });
  await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${servidor.address().port}/`;
  const raiz = fs.mkdtempSync(path.join(os.tmpdir(), 'vídeo de prova '));
  const saida = path.join(raiz, 'saída com espaço');
  const arquivoRoteiro = path.join(raiz, 'roteiro de teste.json');
  fs.writeFileSync(arquivoRoteiro, JSON.stringify(roteiro), 'utf8');

  const r = await rodar([GRAVADOR, url, '--saida', saida, '--roteiro', arquivoRoteiro, '--perfis', 'desktop,mobile'], 240000);
  console.log((r.stdout || '').split('\n').filter((l) => /desktop:|mobile:|FALHA|aviso/.test(l)).join('\n') + (r.stderr || '').slice(0, 300));
  checa('o gravador terminou com código 0', r.status === 0, `código ${r.status}`);

  let info = null;
  try { info = JSON.parse(fs.readFileSync(path.join(saida, 'video-info.json'), 'utf8')); } catch (_) { /* segue */ }
  for (const perfil of ['desktop', 'mobile']) {
    const video = path.join(saida, `video-${perfil}.webm`);
    const existe = fs.existsSync(video);
    checa(`[${perfil}] o vídeo existe, em pasta com espaço e acento`, existe, video);
    const bytes = existe ? fs.statSync(video).size : 0;
    checa(`[${perfil}] o vídeo tem mais de 0 byte`, bytes > 0, `${bytes} bytes`);
    const cab = existe ? fs.readFileSync(video).subarray(0, 4).toString('hex') : '';
    checa(`[${perfil}] o arquivo é WebM (cabeçalho EBML)`, cab === '1a45dfa3', cab);
    const d = info && info.perfis && info.perfis[perfil];
    checa(`[${perfil}] video-info.json descreve o vídeo`, !!d && d.formato === 'webm' && d.bytes === bytes);
    if (d) {
      const webmS = d.duracaoWebmMs === null ? null : d.duracaoWebmMs / 1000;
      const marcasS = d.duracaoDasMarcasMs / 1000;
      checa(`[${perfil}] duração lida do WebM está na faixa de 10 a 90 s`, webmS !== null && webmS >= 10 && webmS <= 90, `webm=${webmS} s, marcas=${marcasS.toFixed(1)} s`);
      checa(`[${perfil}] a duração do WebM bate com a marca de tempo dos passos (até 2,5 s)`, webmS !== null && Math.abs(webmS - marcasS) <= 2.5, `${webmS} x ${marcasS.toFixed(1)}`);
      checa(`[${perfil}] a gravação não falhou`, d.falha === null, String(d.falha));
      checa(`[${perfil}] saíram 7 quadros (abertura, 5 da rolagem, fim)`, d.quadros.length === 7 && d.quadros.every((q) => fs.statSync(path.join(saida, 'quadros', q)).size > 0), d.quadros.join(', '));
      checa(`[${perfil}] a prancha foi montada`, !!d.prancha && fs.statSync(path.join(saida, d.prancha)).size > 0, d.prancha);
    }
    checa(`[${perfil}] a rolagem chegou ao fim da página (a página avisou o servidor)`, fins.has(perfil));
    checa(`[${perfil}] a pasta temporária de gravação foi limpa`, !fs.existsSync(path.join(saida, `.gravando-${perfil}`)));
  }

  // Rolagem curta demais: não chega ao fim, e isso reprova (nunca vídeo pela metade).
  const curto = path.join(raiz, 'curto.json');
  fs.writeFileSync(curto, JSON.stringify({ ...roteiro, passos: roteiro.passos.map((p) => (p.acao === 'rolar_pagina' ? { ...p, max_passos: 2, prints: 0 } : p)).concat([1, 2, 3, 4, 5, 6].map((n) => ({ acao: 'print', nome: 'extra ' + n }))) }), 'utf8');
  const r3 = await rodar([GRAVADOR, url, '--saida', path.join(raiz, 'saida3'), '--roteiro', curto, '--perfis', 'desktop'], 120000);
  checa('rolagem que não chega ao fim da página sai com código 1 e diz por quê', r3.status === 1 && /sem chegar ao fim/.test(r3.stdout + r3.stderr), `código ${r3.status}`);

  // Roteiro inválido: recusado antes de abrir o navegador (código 2, nenhuma pasta de vídeo).
  const ruim = path.join(raiz, 'ruim.json');
  fs.writeFileSync(ruim, JSON.stringify({ passos: [{ acao: 'clicar', seletor: 'a' }] }), 'utf8');
  const r2 = await rodar([GRAVADOR, url, '--saida', path.join(raiz, 'saida2'), '--roteiro', ruim], 30000);
  checa('roteiro inválido é recusado com código 2', r2.status === 2 && /Roteiro inválido/.test(r2.stderr), `código ${r2.status}`);

  servidor.close();
  console.log(`\nPasta de saída do teste: ${saida}`);
  process.exitCode = falhas ? 1 : 0;
})().catch((e) => { console.error('FALHA inesperada:', e.message); process.exit(1); });
