#!/usr/bin/env node
/**
 * GATE DE TEXTO NA TELA: viúva em título, minúscula no começo de item e itálico colorido repetido.
 *
 * Por que existe (02/10/2026, auditoria da página do estúdio, nota 5,5). Três coisas que o dono
 * já tinha cobrado passaram por todos os gates porque nenhum media texto RENDERIZADO:
 *  - palavra sozinha na última linha de h1 e h2 ("Como marcar a sua aula / experimental"),
 *    que já tinha sido achado ALTO dele em outra página;
 *  - descrição começando com minúscula ("até 4 pessoas por turma", "só você e a profissional");
 *  - a fórmula "serifa + uma palavra em itálico colorida" em 3 de 7 títulos, o tell do
 *    "jornal de filetes".
 * Quebra de linha só existe no navegador, na largura real: por isso é Playwright, em 6 telas.
 *
 * Reprova (exit 1):
 *  1. título (h1, h2, h3, h4, dt, summary ou [data-titulo]) com mais de uma linha cuja última
 *     linha tem UMA palavra só, em 7 telas de 320 a 1440 (a 320 entrou na auditoria da v4).
 *     Vale também (auditoria da v5) para parágrafo na fonte do título e parágrafo dentro de
 *     caixa de grade (li ou article com irmãos do mesmo tipo); texto corrido de seção não.
 *  2. item de texto visível (bloco com texto próprio: p, li, dd, dt, td, legenda, botão, rótulo)
 *     que começa com letra minúscula. Exceção declarada: `data-minuscula-ok` (marca que se
 *     escreve assim, por exemplo). Fora da regra (3.5.10): item cuja primeira palavra é um e-mail
 *     ou um endereço de site (oi@torraclara.com.br, www.site.com.br, https://wa.me/...).
 *  3. mais de uma palavra ou trecho em itálico com cor diferente do texto em volta, na página.
 *  4. (auditoria de 25/10/2026, A6) "JORNAL DE FILETES": em 1440x900, 10 ou mais filetes de 1 px de ENFEITE e mais
 *     de 1,2 por tela de 900 px. Filete dentro de dl ou table é linha de tabela de rótulo e valor e não conta.
 *     Calibrado em páginas reais (tabela em cara-de-ia.mjs): a de produção que o auditor chamou de "bonito" tem 1,79
 *     por tela e o "jornal de filetes" original 1,83 (reprovam); a aprovada pelo dono tem 0,71 e a torrefação 0,09
 *     (passam). A contagem crua não serve: a aprovada tem 32 filetes, 20 deles de tabela.
 *  5. (auditoria de 25/10/2026) O MESMO ENFEITE EMBAIXO DE QUASE TODO TÍTULO: o mesmo traço, sublinhado, borda,
 *     glifo ou barrinha irmã em mais de 3 h2 (medido em 1440x900). A página de produção tinha o mesmo traço de 56x3
 *     embaixo de 9 dos 10 h2. Enfeites diferentes não se somam.
 * Avisa (não reprova): 10 ou mais filetes de 1 px no total, contando os de tabela.
 *
 * Uso: node scripts/gate-texto.mjs --url <url>
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import path from 'node:path';
import { exigirServidor } from './servidor-no-ar.mjs';
import { julgarFiletes, julgarEnfeites, FILETES_POR_TELA_MAXIMO, TITULOS_COM_O_MESMO_ENFEITE_MAXIMO } from './cara-de-ia.mjs';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(raizGlobalNpm(), 'playwright')); }
    catch { console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}
const { chromium } = carregarPlaywright();

const args = process.argv.slice(2);
const URL_ALVO = args[args.indexOf('--url') + 1];
if (!URL_ALVO || URL_ALVO.startsWith('--')) {
  console.error('uso: node gate-texto.mjs --url <url>');
  process.exit(2);
}
const TELAS = [
  ['desktop comum', 1440, 900, false],
  ['notebook comum', 1366, 768, false],
  ['tablet retrato', 768, 1024, false],
  ['iphone pro max', 430, 932, true],
  ['iphone padrao', 390, 844, true],
  ['android comum', 360, 740, true],
  // Auditoria da v4: em 320 o h2 do fecho ficou "Marque / a sua aula / experimental" e o gate,
  // que parava em 360, dava PASSA.
  ['menor suportado', 320, 568, true],
];

await exigirServidor(URL_ALVO);   // servidor caído: uma mensagem clara (saída 3), não ERR_CONNECTION_REFUSED (P11)
const navegador = await chromium.launch();
const falhas = [];
const avisos = new Set();
const medidas = [];
console.log('\nGATE DE TEXTO NA TELA  ' + URL_ALVO);
console.log('='.repeat(80));

for (const [nome, w, h, mob] of TELAS) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.waitForTimeout(400);

  const r = await page.evaluate(() => {
    const out = { viuvas: [], minusculas: [], italicos: [], filetes: 0, filetesTabela: 0, altura: document.documentElement.scrollHeight, enfeites: [] };
    const visivel = (el) => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      if (el.closest('[hidden], [aria-hidden="true"], script, style, noscript')) return false;
      const c = el.getBoundingClientRect();
      return c.width > 1 && c.height > 1;
    };
    const curto = (t) => t.replace(/\s+/g, ' ').trim().slice(0, 40);

    // 1. viúva em título: h1 e h2, e também os subtítulos (h3, h4) e os títulos de card (dt,
    //    summary de pergunta e o que for marcado com data-titulo). Na v4 os 3 h3 dos passos
    //    quebravam com palavra sozinha em 768 e o gate só olhava h1 e h2.
    const viuva = (t) => {
      const palavras = [];
      const andar = document.createTreeWalker(t, NodeFilter.SHOW_TEXT);
      for (let n = andar.nextNode(); n; n = andar.nextNode()) {
        const re = /\S+/g; let m;
        while ((m = re.exec(n.textContent))) {
          const rg = document.createRange();
          rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
          const rr = rg.getClientRects()[0];
          if (rr && rr.width > 0) palavras.push({ p: m[0], top: rr.top, bottom: rr.bottom });
        }
      }
      // Pedaços da mesma palavra (palavra com <em> no meio) não contam como duas.
      const linhas = [];
      for (const pw of palavras) {
        const l = linhas.find((x) => Math.abs(x.top - pw.top) < (pw.bottom - pw.top) * 0.5);
        if (l) l.n++; else linhas.push({ top: pw.top, n: 1, ult: pw.p });
        if (l) l.ult = pw.p;
      }
      linhas.sort((a, b) => a.top - b.top);
      return linhas.length >= 2 && linhas[linhas.length - 1].n === 1 ? { ult: linhas[linhas.length - 1].ult, n: linhas.length } : null;
    };
    for (const t of document.querySelectorAll('h1, h2, h3, h4, dt, summary, [data-titulo]')) {
      if (t.closest('[data-viuva-ok]')) continue;
      if (!visivel(t)) continue;
      const v = viuva(t);
      if (v) out.viuvas.push(`${t.tagName.toLowerCase()} "${curto(t.innerText)}" termina com "${v.ult}" sozinha (${v.n} linhas)`);
    }
    // 1b (auditoria da v5): parágrafo na FONTE DO TÍTULO (o texto das situações era Newsreader de
    // 22 px e ficava com "depois." sozinho em 768) e parágrafo de CAIXA de grade (o 1o passo
    // terminava com "experimental." sozinho em 360 e 320). Texto corrido de seção fica de fora.
    const h1 = [...document.querySelectorAll('h1, h2')].find(visivel);
    const familia = (el) => getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim().toLowerCase();
    // Só conta como "fonte do título" quando ela é diferente da fonte do corpo.
    const fonteTitulo = h1 && familia(h1) !== familia(document.body) ? familia(h1) : null;
    const emCaixa = (el) => {
      const item = el.closest('li, article');
      if (!item || !item.parentElement) return false;
      return [...item.parentElement.children].filter((f) => f.tagName === item.tagName && visivel(f)).length >= 2;
    };
    for (const p of document.querySelectorAll('p, dd, blockquote')) {
      if (p.closest('[data-viuva-ok], footer') || !visivel(p)) continue;
      const serifa = fonteTitulo && familia(p) === fonteTitulo;
      const caixa = emCaixa(p);
      if (!serifa && !caixa) continue;
      const v = viuva(p);
      if (v) out.viuvas.push(`${p.tagName.toLowerCase()} "${curto(p.innerText)}" termina com "${v.ult}" sozinha (${v.n} linhas, ${serifa ? 'na fonte do título' : 'texto de caixa'})`);
    }

    // 2. item de texto que começa com minúscula
    // 3.5.10 (P9): e-mail e endereço de site se escrevem em minúscula (oi@torraclara.com.br,
    // www.site.com.br/privacidade, https://wa.me/55...) e ficam fora da regra. Vale só quando a
    // PRIMEIRA palavra do item é o próprio endereço: "ok.agora segue" e "fale em oi@x.com" seguem
    // reprovando, porque o domínio precisa terminar num sufixo conhecido (.com, .br, .io...).
    const TLD = '(?:com|net|org|edu|gov|io|app|dev|me|co|biz|info|shop|store|site|online|tech|ai|tv|cc|xyz|br|pt|us|uk|es|ar)';
    const EMAIL = new RegExp('^[\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)*\\.' + TLD + '$', 'i');
    const SITE = new RegExp('^(?:https?://\\S+|(?:www\\.)?[a-z0-9-]+(?:\\.[a-z0-9-]+)*\\.' + TLD + '(?:/\\S*)?)$', 'i');
    const enderecoNoComeco = (txt) => {
      const primeira = txt.split(/\s+/)[0].replace(/[.,;:!?)\]]+$/, '');
      return EMAIL.test(primeira) || SITE.test(primeira);
    };
    const BLOCO = ['block', 'flex', 'grid', 'list-item', 'inline-block', 'inline-flex', 'table-cell', 'flow-root'];
    const CONTEINER_DE_FRASE = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'P', 'A', 'BUTTON', 'LABEL', 'SUMMARY', 'DT', 'DD', 'LI', 'FIGCAPTION', 'TD', 'TH', 'SPAN', 'STRONG', 'EM'];
    for (const el of document.querySelectorAll('body *')) {
      if (!visivel(el) || el.closest('[data-minuscula-ok]')) continue;
      const cs = getComputedStyle(el);
      if (!BLOCO.includes(cs.display)) continue;
      const proprio = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
      if (!proprio) continue;
      const txt = (el.innerText || '').trim();
      if (!txt) continue;
      const pai = el.parentElement;
      if (pai && CONTEINER_DE_FRASE.includes(pai.tagName) && !(pai.innerText || '').trim().startsWith(txt.slice(0, 12))) continue;
      const m = txt.match(/\p{L}|\p{N}/u);
      if (!m || /\p{N}/u.test(m[0])) continue;
      if (enderecoNoComeco(txt)) continue;
      if (cs.textTransform === 'uppercase' || cs.textTransform === 'capitalize') continue;
      if (m[0] !== m[0].toUpperCase() && m[0] === m[0].toLowerCase()) out.minusculas.push(`<${el.tagName.toLowerCase()}> "${curto(txt)}"`);
    }

    // 3. itálico colorido
    for (const el of document.querySelectorAll('body *')) {
      if (!visivel(el)) continue;
      const cs = getComputedStyle(el);
      const pai = el.parentElement;
      if (!pai || cs.fontStyle !== 'italic' || getComputedStyle(pai).fontStyle === 'italic') continue;
      if (!(el.innerText || '').trim()) continue;
      if (cs.color !== getComputedStyle(pai).color) out.italicos.push(`"${curto(el.innerText)}" em <${pai.tagName.toLowerCase()}>`);
    }

    // aviso: filetes de 1 px
    for (const el of document.querySelectorAll('body *')) {
      if (!visivel(el)) continue;
      const cs = getComputedStyle(el);
      const lados = ['Top', 'Right', 'Bottom', 'Left'].filter((l) => cs['border' + l + 'Style'] !== 'none' && parseFloat(cs['border' + l + 'Width']) > 0 && parseFloat(cs['border' + l + 'Width']) <= 1.5);
      if (lados.length >= 1 && lados.length <= 2) { out.filetes++; if (el.closest('dl, table')) out.filetesTabela++; }
    }

    // 5. enfeite de título: o que se desenha junto de cada h2 visível ('' quando nada).
    const transparente = (c) => !c || c === 'transparent' || c === 'rgba(0, 0, 0, 0)';
    const px = (v) => Math.round(parseFloat(v) || 0);
    for (const h of document.querySelectorAll('h2')) {
      if (!visivel(h)) continue;
      const partes = [];
      for (const ps of ['::before', '::after']) {
        const s = getComputedStyle(h, ps);
        if (!s.content || s.content === 'none' || s.content === 'normal' || s.display === 'none') continue;
        const texto = s.content.replace(/^["']|["']$/g, '').trim();
        const desenhado = px(s.width) > 0 && px(s.height) > 0 && (!transparente(s.backgroundColor) || s.backgroundImage !== 'none' || px(s.borderTopWidth) > 0 || px(s.borderBottomWidth) > 0);
        if (texto) partes.push(`glifo ${ps} "${texto.slice(0, 12)}"`);
        else if (desenhado) partes.push(`traço ${ps} de ${px(s.width)}x${px(s.height)} px ${transparente(s.backgroundColor) ? s.borderBottomColor : s.backgroundColor}`);
      }
      const cs = getComputedStyle(h);
      if (cs.borderBottomStyle !== 'none' && parseFloat(cs.borderBottomWidth) > 0) partes.push(`borda embaixo de ${cs.borderBottomWidth} ${cs.borderBottomColor}`);
      if ((cs.textDecorationLine || '').includes('underline')) partes.push(`sublinhado ${cs.textDecorationColor}`);
      for (const [irmao, lado] of [[h.nextElementSibling, 'depois'], [h.previousElementSibling, 'antes']]) {
        if (!irmao || !visivel(irmao) || (irmao.innerText || '').trim() || irmao.querySelector('img, svg, video, canvas')) continue;
        const c = irmao.getBoundingClientRect();
        if (c.height <= 8 && c.width <= 240) partes.push(`traço logo ${lado} do título, ${Math.round(c.width)}x${Math.round(c.height)} px ${getComputedStyle(irmao).backgroundColor}`);
      }
      out.enfeites.push(partes.join(' + '));
    }
    return out;
  });

  const onde = `${nome} (${w}x${h})`;
  const lista = r.viuvas.map((v) => `viúva: ${v}`)
    .concat(r.minusculas.map((v) => `começa com minúscula: ${v}`))
    .concat(r.italicos.length > 1 ? [`${r.italicos.length} trechos em itálico colorido (máximo 1): ${r.italicos.slice(0, 3).join(', ')}`] : []);
  if (r.filetes >= 10) avisos.add(`${r.filetes} filetes de 1 px (${onde}): sinal do "jornal de filetes", conferir no print`);
  // A6 e enfeite de título: medidos no desktop comum (1440x900), onde o "jornal" se lê e a tela tem 900 px.
  if (nome === 'desktop comum') {
    const enfeite = r.filetes - r.filetesTabela;
    const j = julgarFiletes({ enfeite, tabela: r.filetesTabela, alturaPagina: r.altura, alturaTela: h });
    const virgula = (x) => x.toFixed(2).replace('.', ',');
    medidas.push(`filetes de enfeite: ${enfeite} em ${virgula(j.telas)} telas de 900 px (${virgula(j.porTela)} por tela; máximo ${virgula(FILETES_POR_TELA_MAXIMO)}); de tabela (dl, table), fora da conta: ${r.filetesTabela}`);
    if (j.reprova) lista.push(`${enfeite} filetes de 1 px de enfeite em ${virgula(j.telas)} telas de 900 px, ${virgula(j.porTela)} por tela (máximo ${virgula(FILETES_POR_TELA_MAXIMO)}): é o "jornal de filetes"; separe por cor de superfície e espaço, não por fio (os ${r.filetesTabela} de tabela não contam)`);
    const e = julgarEnfeites(r.enfeites);
    medidas.push(`enfeite de título: ${e.pior ? `o mais repetido em ${e.pior.n} de ${e.pior.total} h2 (${e.pior.assinatura})` : 'nenhum h2 com enfeite'}; máximo ${TITULOS_COM_O_MESMO_ENFEITE_MAXIMO}`);
    if (e.reprova) lista.push(`o mesmo enfeite em ${e.pior.n} de ${e.pior.total} títulos h2 (${e.pior.assinatura}; máximo ${TITULOS_COM_O_MESMO_ENFEITE_MAXIMO}): o traço embaixo de todo título é cara de template; a hierarquia vem do tamanho, do peso e do espaço`);
  }
  console.log(`${onde.padEnd(32)} ${lista.length ? 'FALHA (' + lista.length + ')' : 'ok'}`);
  for (const l of lista) falhas.push(`${onde}: ${l}`);
  await ctx.close();
}
await navegador.close();

console.log('='.repeat(80));
medidas.forEach((m) => console.log('  medido em 1440x900: ' + m));
avisos.forEach((a) => console.log('  aviso: ' + a));
if (falhas.length) {
  falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${falhas.length} problema(s) de texto na tela.`);
  console.log('  Viúva: text-wrap: balance no título ou ajuste da copy. Minúscula: primeira letra maiúscula');
  console.log('  em todo item. Itálico colorido: no máximo um trecho na página. Filete: separar por cor e espaço.');
  console.log('  Enfeite de título: tirar o traço repetido; a hierarquia vem de tamanho, peso e espaço.\n');
  process.exit(1);
}
console.log(`  PASSA: ${TELAS.length} telas (320 a 1440), sem viúva em título nem subtítulo, sem item em minúscula, itálico contido, filetes e enfeite de título dentro do limite.\n`);
