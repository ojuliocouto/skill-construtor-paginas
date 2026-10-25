/**
 * Vídeo de prova com os dois perfis ao mesmo tempo (corte 4 da auditoria de velocidade).
 *
 * `gravar-video.js` gravava o desktop e depois o celular: 85,4 s medidos. Os dois perfis não dependem um do outro (cada um tem o
 * PRÓPRIO contexto, com a própria gravação, no mesmo navegador). O que este teste prova, no Chromium de verdade:
 *  1. os dois perfis começam juntos (a página é pedida pelos dois quase ao mesmo tempo); com `--em-serie` o celular só
 *     começa depois que o desktop terminou;
 *  2. a gravação em paralelo é tão boa quanto a da fila: os dois vídeos existem, são WebM, têm duração dentro da faixa e
 *     batendo com as marcas de tempo, 7 quadros e prancha cada, e a rolagem chegou ao fim em ambos;
 *  3. a saída (e o video-info.json) tem os dois perfis na ordem de sempre, desktop e depois mobile;
 *  4. o tempo total em paralelo é bem menor que em fila.
 * Sem Playwright, avisa PULADO.
 */
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { acharPlaywright } = require('./video/achar-playwright.cjs');

const GRAVADOR = path.join(__dirname, 'gravar-video.js');
function rodar(args, tempoMs) {
  return new Promise((resolve) => {
    const t0 = Date.now();
    const f = spawn(process.execPath, args, { windowsHide: true });
    let stdout = '', stderr = '';
    f.stdout.on('data', (d) => { stdout += d; });
    f.stderr.on('data', (d) => { stderr += d; });
    const relogio = setTimeout(() => f.kill(), tempoMs);
    f.on('close', (status) => { clearTimeout(relogio); resolve({ status, stdout, stderr, segundos: (Date.now() - t0) / 1000 }); });
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
<section id="ultima"><p class="sobe">Fim da página</p></section>
<script>
const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) e.target.classList.add('v'); }), { threshold: 0.2 });
document.querySelectorAll('.sobe').forEach((n) => io.observe(n));
fetch('/abriu?perfil=' + (innerWidth < 600 ? 'mobile' : 'desktop'));
let avisou = false;
addEventListener('scroll', () => { if (!avisou && scrollY + innerHeight >= document.documentElement.scrollHeight - 2) { avisou = true; fetch('/chegou-ao-fim?perfil=' + (innerWidth < 600 ? 'mobile' : 'desktop')); } }, { passive: true });
</script></html>`;

const roteiro = {
  nome: 'teste do paralelo',
  duracao_minima_s: 12,
  passos: [
    { acao: 'abrir' }, { acao: 'esperar', ms: 800 }, { acao: 'print', nome: 'abertura' },
    { acao: 'rolar_pagina', passo: 0.6, espera_ms: 600, max_passos: 30, prints: 5 },
    { acao: 'print', nome: 'fim' },
  ],
};

(async () => {
  const pw = acharPlaywright();
  if (!pw) { console.log('PULADO: Playwright não encontrado (npm i -g playwright). Esta integração NÃO rodou.'); return; }
  let fins = new Set();
  let aberturas = {};
  const servidor = http.createServer((req, res) => {
    if (req.url.startsWith('/chegou-ao-fim')) { fins.add(new URL(req.url, 'http://x').searchParams.get('perfil')); res.writeHead(204); res.end(); return; }
    if (req.url.startsWith('/abriu')) {
      const perfil = new URL(req.url, 'http://x').searchParams.get('perfil');
      if (aberturas[perfil] === undefined) aberturas[perfil] = Date.now();
      res.writeHead(204); res.end(); return;
    }
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }); res.end(PAGINA);
  });
  await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
  const url = `http://127.0.0.1:${servidor.address().port}/`;
  const raiz = fs.mkdtempSync(path.join(os.tmpdir(), 'vídeo paralelo '));
  const arquivoRoteiro = path.join(raiz, 'roteiro.json');
  fs.writeFileSync(arquivoRoteiro, JSON.stringify(roteiro), 'utf8');

  const gravar = async (rotulo, extra) => {
    fins = new Set(); aberturas = {};
    const saida = path.join(raiz, rotulo);
    const r = await rodar([GRAVADOR, url, '--saida', saida, '--roteiro', arquivoRoteiro, '--perfis', 'desktop,mobile', ...extra], 240000);
    const info = JSON.parse(fs.readFileSync(path.join(saida, 'video-info.json'), 'utf8'));
    return { r, saida, info, fins: new Set(fins), distancia: Math.abs((aberturas.mobile || 0) - (aberturas.desktop || 0)) / 1000 };
  };

  // máquina de 3 núcleos ou mais: o padrão já é paralelo e é o que se testa; com menos, o teste força --paralelo (o padrão ali é a fila)
  const par = await gravar('paralelo', os.cpus().length >= 3 ? [] : ['--paralelo']);
  const ser = await gravar('serie', ['--em-serie']);

  for (const [rotulo, g] of [['paralelo', par], ['em fila', ser]]) {
    checa(`[${rotulo}] o gravador terminou com código 0`, g.r.status === 0, `código ${g.r.status}\n${(g.r.stdout + g.r.stderr).slice(-400)}`);
    checa(`[${rotulo}] os perfis saem na ordem de sempre: desktop e depois mobile`, Object.keys(g.info.perfis).join(',') === 'desktop,mobile', Object.keys(g.info.perfis).join(','));
    const linhas = g.r.stdout.split('\n');
    const iD = linhas.findIndex((l) => /^\s+desktop:/.test(l)), iM = linhas.findIndex((l) => /^\s+mobile:/.test(l));
    checa(`[${rotulo}] a saída imprime desktop antes de mobile`, iD >= 0 && iM > iD, `${iD},${iM}`);
    for (const perfil of ['desktop', 'mobile']) {
      const d = g.info.perfis[perfil];
      const video = path.join(g.saida, `video-${perfil}.webm`);
      checa(`[${rotulo}/${perfil}] vídeo WebM existe e tem conteúdo`, fs.existsSync(video) && fs.statSync(video).size > 0 && fs.readFileSync(video).subarray(0, 4).toString('hex') === '1a45dfa3');
      const webmS = d.duracaoWebmMs === null ? null : d.duracaoWebmMs / 1000;
      const marcasS = d.duracaoDasMarcasMs / 1000;
      checa(`[${rotulo}/${perfil}] duração do WebM na faixa de 10 a 90 s e batendo com as marcas (até 2,5 s)`, webmS !== null && webmS >= 10 && webmS <= 90 && Math.abs(webmS - marcasS) <= 2.5, `webm=${webmS} s, marcas=${marcasS.toFixed(1)} s`);
      checa(`[${rotulo}/${perfil}] sem falha, 7 quadros e prancha`, d.falha === null && d.quadros.length === 7 && !!d.prancha && fs.statSync(path.join(g.saida, d.prancha)).size > 0, `${d.falha} / ${d.quadros.length}`);
      checa(`[${rotulo}/${perfil}] a rolagem chegou ao fim da página`, g.fins.has(perfil));
      checa(`[${rotulo}/${perfil}] pasta temporária limpa`, !fs.existsSync(path.join(g.saida, `.gravando-${perfil}`)));
    }
  }

  checa('em paralelo os dois perfis abrem a página quase juntos (até 5 s de diferença)', par.distancia <= 5, `${par.distancia.toFixed(1)} s`);
  checa('com --em-serie o celular só abre depois de o desktop gravar (a duração mínima do roteiro é 12 s)', ser.distancia >= 11, `${ser.distancia.toFixed(1)} s`);
  checa('o tempo total em paralelo é bem menor que em fila', par.r.segundos < ser.r.segundos * 0.8, `${par.r.segundos.toFixed(1)} s contra ${ser.r.segundos.toFixed(1)} s`);

  servidor.close();
  console.log(`\nPasta do teste: ${raiz}`);
  process.exitCode = falhas ? 1 : 0;
})().catch((e) => { console.error('FALHA inesperada:', e.message); process.exit(1); });
