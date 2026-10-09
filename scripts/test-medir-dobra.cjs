/** medir-dobra.mjs (achado N9, 3.5.8): "Imagens ilustrativas" no plural conta como aviso, e a medida separa
 *  "aviso fora da primeira tela" de "o texto não existe na página". Páginas locais, navegador do Playwright. */
const http = require('node:http');
const path = require('node:path');
const { spawn } = require('node:child_process');

const rodar = (cmd, argv) => new Promise((ok) => {
  const p = spawn(cmd, argv, { env: process.env });
  let out = '', err = '';
  p.stdout.on('data', (d) => { out += d; });
  p.stderr.on('data', (d) => { err += d; });
  p.on('close', (status) => ok({ status, stdout: out, stderr: err }));
});
const pagina = (corpo) => `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>t</title><style>body{margin:0;font:18px Georgia}.alta{height:2400px}</style></head><body>${corpo}</body></html>`;
const ROTAS = {
  '/singular': pagina('<p>Imagem ilustrativa</p><div class="alta"></div>'),
  '/plural': pagina('<p>Imagens ilustrativas, nenhuma mostra a casa da cliente.</p><div class="alta"></div>'),
  '/embaixo': pagina('<div class="alta"></div><p>Imagens ilustrativas</p>'),
  '/nenhum': pagina('<p>Foto de banco, sem aviso nenhum.</p><div class="alta"></div>'),
  '/parecido': pagina('<p>Ilustração da cena e imagem decorativa.</p><div class="alta"></div>'),
  // G22 (3.5.10): o topo da v7 antiga. Legenda de 14 px no fluxo entre a foto e a manchete; a medida diz onde terminam manchete,
  // apoio e botão e onde está a legenda (a v7 passou porque a medida só tinha área de foto e "existe o aviso").
  '/topo-legenda-no-fluxo': pagina('<section id="topo"><img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" style="display:block;width:100%;height:300px"><p style="font-size:14px;margin:8px 16px">Foto acima: imagem ilustrativa de banco de imagens.</p><h1 style="margin:16px">Suas costas, cuidadas de perto.</h1><p style="margin:16px">Texto de apoio do topo com mais de quarenta letras para contar.</p><a href="#c" style="display:inline-block;margin:16px;padding:16px;background:#111;color:#fff">Ver como é</a></section><div class="alta"></div>'),
  '/topo-legenda-sobre-a-foto': pagina('<section id="topo"><figure style="position:relative;margin:0"><img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" style="display:block;width:100%;height:300px"><figcaption style="position:absolute;top:8px;right:8px;font-size:12px">Imagem ilustrativa</figcaption></figure><h1 style="margin:16px">Suas costas, cuidadas de perto.</h1><a href="#c" style="display:inline-block;margin:16px;padding:16px;background:#111;color:#fff">Ver como é</a></section><div class="alta"></div>'),
};
let falhas = 0;
const checa = (nome, ok, detalhe = '') => { console.log(`  [${ok ? 'ok  ' : 'FALHA'}] ${nome}${detalhe ? ' -> ' + detalhe : ''}`); if (!ok) falhas++; };

const servidor = http.createServer((req, res) => {
  const corpo = ROTAS[req.url.split('?')[0]];
  res.writeHead(corpo ? 200 : 404, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(corpo || '');
});
servidor.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${servidor.address().port}`;
  const medir = async (rota) => {
    const r = await rodar('node', [path.join(__dirname, 'medir-dobra.mjs'), '--url', base + rota]);
    try { return JSON.parse(r.stdout); } catch { return { erro: r.stderr || r.stdout }; }
  };
  const [singular, plural, embaixo, nenhum, parecido] = await Promise.all([medir('/singular'), medir('/plural'), medir('/embaixo'), medir('/nenhum'), medir('/parecido')]);
  const [noFluxo, sobreFoto] = await Promise.all([medir('/topo-legenda-no-fluxo'), medir('/topo-legenda-sobre-a-foto')]);
  for (const t of ['desk', 'mob']) {
    const m = noFluxo[t] || {};
    const faixa = (f) => Array.isArray(f) && f.length === 2 && f.every(Number.isFinite) && f[0] < f[1];
    checa(`${t}: diz onde estão a manchete, o apoio e o botão do topo`, faixa(m.manchete) && faixa(m.apoio) && faixa(m.botao) && m.manchete[1] < m.apoio[0] && m.apoio[1] < m.botao[1], JSON.stringify(m));
    checa(`${t}: legenda de 14 px no fluxo entre a foto e a manchete`, m.legenda && m.legenda.fonte === 14 && m.legenda.sobreFoto === false && m.legenda.entreFotoEManchete === true, JSON.stringify(m.legenda));
    const s2 = (sobreFoto[t] || {}).legenda;
    checa(`${t}: legenda de 12 px sobre a foto (absoluta) não está no fluxo`, s2 && s2.fonte === 12 && s2.sobreFoto === true && s2.entreFotoEManchete === false, JSON.stringify(s2));
  }
  for (const t of ['desk', 'mob']) {
    checa(`${t}: singular conta como aviso`, singular[t] && singular[t].aviso === true, JSON.stringify(singular[t] || singular));
    checa(`${t}: plural "Imagens ilustrativas" conta como aviso na primeira tela`, plural[t] && plural[t].aviso === true && plural[t].avisoNaPagina === true, JSON.stringify(plural[t] || plural));
    checa(`${t}: aviso mais abaixo: fora da tela, mas existe na página`, embaixo[t] && embaixo[t].aviso === false && embaixo[t].avisoNaPagina === true, JSON.stringify(embaixo[t] || embaixo));
    checa(`${t}: sem o texto em lugar nenhum: avisoNaPagina falso`, nenhum[t] && nenhum[t].aviso === false && nenhum[t].avisoNaPagina === false, JSON.stringify(nenhum[t] || nenhum));
    checa(`${t}: "ilustração" e "imagem decorativa" soltas NÃO contam como aviso`, parecido[t] && parecido[t].aviso === false && parecido[t].avisoNaPagina === false, JSON.stringify(parecido[t] || parecido));
  }
  servidor.close();
  console.log(falhas ? `\n  ${falhas} falha(s).\n` : '\n  Medida do aviso confiável.\n');
  process.exit(falhas ? 1 : 0);
});
