#!/usr/bin/env node
/**
 * GERA A og:image (1200x630) com o título, a foto e, quando a foto não é do cliente, o aviso "Imagem ilustrativa"
 * (achado A29, teste de ponta a ponta de 08/10/2026: nenhum comando gerava a imagem que a skill exige; o aluno usou Pillow
 * com a Helvetica do sistema e o auditor notou depois que a fonte não era a da marca).
 *
 * Renderiza pelo navegador (Playwright), então não depende de fonte instalada: a fonte da marca entra por @font-face a partir
 * do arquivo em `fonts/` do projeto (woff2, woff, ttf ou otf). Sem nenhuma, usa a fonte do sistema COMO RESERVA e diz isso.
 *
 * Uso: node scripts/gerar-og-image.mjs --projeto <dir> --titulo "<título>" [--foto <arquivo>] [--ilustrativa]
 *        [--fonte <arquivo da fonte>] [--cor-fundo "#1f2622"] [--cor-texto "#f4f1ea"] [--saida og-image.jpg] [--html-saida og.html]
 *   --ilustrativa  a foto é de banco (não é do cliente): põe a faixa "Imagem ilustrativa" na base (o gate-imagens.py exige
 *                  esse aviso na prévia do link, que é a primeira coisa que a visitante vê no WhatsApp)
 *   --foto         relativa ao projeto; vai à direita, recortada para preencher (object-fit: cover)
 *   --fonte        a fonte do TÍTULO (a do corpo costuma vir antes em ordem alfabética). Sem ela, usa o primeiro arquivo de
 *                  <projeto>/fonts/ e, se houver mais de um, AVISA qual escolheu (3.5.10)
 *   --cor-fundo, --cor-texto   as cores da paleta do plano visual. Sem elas, usa verde escuro e off-white que NÃO são da marca e AVISA (3.5.10)
 * Saída: <projeto>/<saida> (JPEG 1200x630). O endereço da og:image na página é absoluto no domínio final (ver o passo f).
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(raizGlobalNpm(), 'playwright')); }
    catch { console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}

const args = process.argv.slice(2);
const valor = (n, p = null) => { const i = args.indexOf(n); return i >= 0 && args[i + 1] !== undefined && !args[i + 1].startsWith('--') ? args[i + 1] : p; };
const projeto = path.resolve(valor('--projeto', '.'));
const titulo = (valor('--titulo', '') || '').trim();
const ilustrativa = args.includes('--ilustrativa');
// 3.5.10 (P7): as cores padrão NÃO são da marca de ninguém. Sem --cor-fundo ou --cor-texto o script usa estas e AVISA no fim.
const COR_FUNDO_PADRAO = '#1f2622', COR_TEXTO_PADRAO = '#f4f1ea';
const corFundoArg = valor('--cor-fundo'), corTextoArg = valor('--cor-texto');
const corFundo = corFundoArg || COR_FUNDO_PADRAO;
const corTexto = corTextoArg || COR_TEXTO_PADRAO;
const saida = path.resolve(projeto, valor('--saida', 'og-image.jpg'));
const htmlSaida = valor('--html-saida');
if (!titulo) { console.error('uso: node gerar-og-image.mjs --projeto <dir> --titulo "<título>" [--foto <arquivo>] [--ilustrativa] [--fonte <arquivo>]'); process.exit(2); }

const MIME = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.avif': 'image/avif' };
const FORMATO = { '.woff2': 'woff2', '.woff': 'woff', '.ttf': 'truetype', '.otf': 'opentype' };
const dataUrl = (arq, mime) => `data:${mime};base64,${fs.readFileSync(arq).toString('base64')}`;
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

let foto = null;
const fotoArg = valor('--foto');
if (fotoArg) {
  const arq = path.resolve(projeto, fotoArg);
  if (!fs.existsSync(arq)) { console.error(`a foto não existe: ${arq}`); process.exit(1); }
  const mime = MIME[path.extname(arq).toLowerCase()];
  if (!mime) { console.error(`formato de foto sem suporte: ${path.extname(arq)} (use png, jpg, webp, gif ou avif)`); process.exit(1); }
  foto = dataUrl(arq, mime);
}

let fonteArq = null;
let fonteEscolhidaSemArg = null; // (3.5.10) quando o script escolheu entre várias, o aviso diz entre quantas
const fonteArg = valor('--fonte');
if (fonteArg) {
  fonteArq = path.resolve(projeto, fonteArg);
  if (!fs.existsSync(fonteArq)) { console.error(`a fonte não existe: ${fonteArq}`); process.exit(1); }
} else if (fs.existsSync(path.join(projeto, 'fonts'))) {
  const achadas = fs.readdirSync(path.join(projeto, 'fonts')).filter((n) => FORMATO[path.extname(n).toLowerCase()]).sort();
  if (achadas.length) fonteArq = path.join(projeto, 'fonts', achadas[0]);
  if (achadas.length > 1) fonteEscolhidaSemArg = achadas.length;
}
const fontFace = fonteArq
  ? `@font-face{font-family:'MarcaOG';src:url(${dataUrl(fonteArq, 'application/octet-stream')}) format('${FORMATO[path.extname(fonteArq).toLowerCase()] || 'truetype'}');font-weight:100 900;}`
  : '';
const familia = fonteArq ? "'MarcaOG'" : "system-ui,-apple-system,'Segoe UI',Arial,sans-serif";

// O título cabe em até 4 linhas: reduz o corpo conforme o tamanho do texto.
const tam = titulo.length <= 28 ? 76 : titulo.length <= 48 ? 64 : titulo.length <= 72 ? 54 : 46;
const html = `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>${fontFace}
html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:${corFundo}}
.og{position:relative;width:1200px;height:630px;display:grid;grid-template-columns:${foto ? '620px 580px' : '1fr'};font-family:${familia};color:${corTexto}}
.txt{padding:72px 56px ${ilustrativa ? 120 : 72}px 72px;display:flex;align-items:center}
h1{margin:0;font-size:${tam}px;line-height:1.08;font-weight:700;letter-spacing:-.01em}
.foto{height:630px}.foto img{width:100%;height:100%;object-fit:cover;display:block}
.aviso{position:absolute;left:0;right:0;bottom:0;height:64px;background:#111;color:#fff;display:flex;align-items:center;padding:0 72px;font-size:28px;font-family:${familia}}
</style></head><body><div class="og"><div class="txt"><h1>${esc(titulo)}</h1></div>${foto ? `<div class="foto"><img alt="" src="${foto}"></div>` : ''}${ilustrativa ? '<div class="aviso">Imagem ilustrativa</div>' : ''}</div></body></html>`;
if (htmlSaida) fs.writeFileSync(path.resolve(projeto, htmlSaida), html.replace(/data:[^"')]{200,}/g, 'data:...'), 'utf8');

const { chromium } = carregarPlaywright();
const navegador = await chromium.launch();
try {
  const pagina = await navegador.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await pagina.setContent(html, { waitUntil: 'load' });
  await pagina.evaluate(() => document.fonts.ready);
  fs.mkdirSync(path.dirname(saida), { recursive: true });
  await pagina.screenshot({ path: saida, type: 'jpeg', quality: 88, clip: { x: 0, y: 0, width: 1200, height: 630 } });
} finally { await navegador.close(); }

console.log(`og:image gravada em ${path.relative(process.cwd(), saida).split(path.sep).join('/') || saida} (1200x630)`);
console.log(fonteArq
  ? `fonte da marca: ${path.relative(projeto, fonteArq).split(path.sep).join('/')}`
  : 'ATENÇÃO fonte: não achei fonte em fonts/ e usei a fonte do sistema como RESERVA; baixe a da marca (scripts/baixar-fontes.mjs) e rode de novo');
if (fonteEscolhidaSemArg) {
  console.log(`ATENÇÃO fonte: havia ${fonteEscolhidaSemArg} arquivos em fonts/ e nenhum --fonte; usei ${path.relative(projeto, fonteArq).split(path.sep).join('/')} (o primeiro em ordem alfabética), que pode ser a fonte do CORPO. Passe --fonte fonts/<arquivo da fonte do título>.`);
}
const faltaram = [!corFundoArg && '--cor-fundo', !corTextoArg && '--cor-texto'].filter(Boolean);
if (faltaram.length) {
  console.log(`ATENÇÃO cores: sem ${faltaram.join(' e ')} usei ${[!corFundoArg && `fundo ${COR_FUNDO_PADRAO}`, !corTextoArg && `texto ${COR_TEXTO_PADRAO}`].filter(Boolean).join(' e ')}, que NÃO são da marca. Passe ${faltaram.join(' e ')} com as cores da paleta do plano-visual.md.`);
}
console.log(ilustrativa ? 'aviso "Imagem ilustrativa" na base (foto de banco)' : 'sem aviso: use --ilustrativa se a foto não for do cliente');
