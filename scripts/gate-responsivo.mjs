#!/usr/bin/env node
/**
 * GATE DE RESPONSIVIDADE: a oitava lente da wave, agora executavel.
 *
 * Por que existe (26/08/2026, falha real). A pagina foi entregue "responsiva" com base em UM
 * teste de 1440x900 e num item de checklist que dizia "conferir 320/375/768/1024/1280/1440".
 * O dono abriu no monitor dele e o CTA do heroi estava cortado. A medicao depois mostrou o
 * tamanho do buraco: o titulo quebrava em SEIS linhas e o CTA caia abaixo da dobra em
 * 1366x768, que e a tela de notebook mais comum do Brasil.
 *
 * Duas licoes viraram codigo aqui:
 *  1. Item de checklist nao bloqueia. Este gate reprova e sai com codigo 1.
 *  2. Responsividade nao e so LARGURA. O defeito nasceu da ALTURA: janela baixa com titulo
 *     grande empurra o CTA pra fora da dobra, e nenhum teste de largura pega isso.
 *
 * O que ele mede, em 13 telas reais (nao em breakpoints teoricos):
 *   - overflow horizontal (o classico que quebra mobile)
 *   - CTA principal acima da dobra (regra de pagina de venda: a acao aparece sem rolar)
 *   - alvo de toque >= 44px no mobile (WCAG / Apple HIG)
 *   - corpo de texto >= 14px no mobile (abaixo disso e ilegivel em uso real)
 *   - texto cortado pela caixa
 *   - imagem distorcida (proporcao do arquivo x proporcao renderizada)
 *   - botao em UMA linha nas telas de ate 768px (auditoria da v3, 02/10/2026: o botao principal
 *     quebrava em 2 linhas em 360 e 320px, com 68px de altura, e este gate dava PASSA)
 *   - celular: botao a no maximo 2 telas em qualquer ponto da rolagem (a mesma v3 tinha 6 telas
 *     sem botao nenhum entre o hero e o fecho; barra fixa ou botao repetido resolvem)
 *
 * Uso: node scripts/gate-responsivo.mjs --url <url>
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import path from 'node:path';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(execSync('npm root -g', { encoding: 'utf8' }).trim(), 'playwright')); }
    catch { console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}
const { chromium } = carregarPlaywright();

const args = process.argv.slice(2);
const URL_ALVO = args[args.indexOf('--url') + 1];
if (!URL_ALVO || URL_ALVO.startsWith('--')) {
  console.error('uso: node gate-responsivo.mjs --url <url>');
  process.exit(2);
}

/* Telas escolhidas por USO real, nao por breakpoint bonito. A 1366x768 esta aqui porque e a
   mais comum em notebook no Brasil e foi exatamente onde o defeito apareceu. */
const TELAS = [
  ['desktop grande',   1920, 1080, false],
  ['macbook 16',       1728, 1117, false],
  ['macbook 14',       1512,  982, false],
  ['desktop comum',    1440,  900, false],
  ['notebook comum',   1366,  768, false],
  ['laptop pequeno',   1280,  800, false],
  ['tablet paisagem',  1024,  768, false],
  ['tablet retrato',    768, 1024, false],
  ['iphone pro max',    430,  932, true],
  ['iphone padrao',     390,  844, true],
  ['android comum',     360,  740, true],
  ['menor suportado',   320,  568, true],
];

const falhas = [];
const avisos = [];

const luz = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
const lum = (r, g, b) => 0.2126 * luz(r) + 0.7152 * luz(g) + 0.0722 * luz(b);
const contraste = (a, b) => { const [x, y] = [a, b].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };

/** Media dos pixels REALMENTE renderizados numa faixa. Decodifica o PNG no proprio
 *  navegador via canvas, pra nao precisar de biblioteca de imagem. */
async function mediaDoFundo(page, clip) {
  const png = await page.screenshot({ clip });
  return page.evaluate(async (b64) => {
    const img = new Image();
    img.src = 'data:image/png;base64,' + b64;
    await img.decode();
    const c = document.createElement('canvas');
    c.width = img.width; c.height = img.height;
    const g = c.getContext('2d');
    g.drawImage(img, 0, 0);
    const d = g.getImageData(0, 0, c.width, c.height).data;
    let r = 0, gg = 0, bb = 0, n = 0;
    for (let i = 0; i < d.length; i += 4) { r += d[i]; gg += d[i + 1]; bb += d[i + 2]; n++; }
    return [r / n, gg / n, bb / n];
  }, png.toString('base64'));
}
/** Espera a FAIXA QUE VAI SER MEDIDA parar de mudar, e devolve a media ja assentada.
 *
 *  Existe porque a espera fixa de 260ms daqui media pagina no meio do fade. Um bloco
 *  revelado com `transition: opacity 700ms` esta ~37% opaco aos 260ms, entao a faixa
 *  amostrada e a MISTURA do cartao com o que esta atras dele, uma cor que nao existe na
 *  paleta. Medido em 27/08/2026 num cartao branco revelado sobre fundo verde escuro:
 *  o gate lia rgb(80,115,90) e reprovava a 1.91:1 um botao cujo contraste real e 10.13:1.
 *  Reprovava 6 de 6. O incentivo ficava invertido: punia pagina com fade caprichado e
 *  passava pagina sem animacao nenhuma.
 *
 *  Por que NAO basta esperar `getAnimations()` terminarem: logo depois de rolar, o
 *  IntersectionObserver que dispara o reveal ainda nao rodou, entao nao existe animacao
 *  pra esperar, a espera volta na hora e a medida sai com o bloco em opacidade zero.
 *  Testado: esse caminho tambem reprovava 6 de 6, so que lendo o fundo de tras.
 *
 *  Medir o proprio alvo ate ele parar cobre os tres casos de uma vez, e mais: imagem
 *  preguicosa que chega depois, fonte que troca, poster de video. Duas leituras iguais
 *  seguidas (dentro da tolerancia) = a pintura assentou.
 */
async function fundoAssentado(page, clip, teto = 2500, tolerancia = 2) {
  const fim = Date.now() + teto;
  let anterior = await mediaDoFundo(page, clip);
  let iguais = 0;
  while (Date.now() < fim) {
    await page.waitForTimeout(120);
    const atual = await mediaDoFundo(page, clip);
    iguais = atual.every((v, i) => Math.abs(v - anterior[i]) <= tolerancia) ? iguais + 1 : 0;
    anterior = atual;
    if (iguais >= 2) break;
  }
  return anterior;
}

/* A CAIXA DO BOTAO PRECISA ASSENTAR ANTES DA FAIXA DE FUNDO SER RECORTADA.
   Defeito medido em 15/09/2026 na v8 da Operacao Claude Code: o gate reprovava o
   CTA com 2,41:1 e o pixel provou que 5 das 20 linhas da amostra de "fundo" eram o
   PROPRIO botao (#f94e03), porque a secao entrava com reveal translateY(14px) e o
   boundingBox era lido no meio da transicao. Assentado o fundo, a caixa ja tinha
   subido 14px e o recorte, preso na coordenada velha, invadia o botao. Medida certa
   no mesmo botao: 3,20:1. Ler a caixa DEPOIS que ela para de se mexer resolve, e
   vale pra qualquer pagina com animacao de entrada. */
async function caixaAssentada(el, teto = 2000, tolerancia = 1) {
  const fim = Date.now() + teto;
  let anterior = await el.boundingBox();
  let iguais = 0;
  while (Date.now() < fim) {
    await new Promise((r) => setTimeout(r, 100));
    const atual = await el.boundingBox();
    if (!atual) return anterior;
    iguais = (Math.abs(atual.y - anterior.y) <= tolerancia && Math.abs(atual.x - anterior.x) <= tolerancia)
      ? iguais + 1 : 0;
    anterior = atual;
    if (iguais >= 2) break;
  }
  return anterior;
}

const navegador = await chromium.launch();

console.log('\nGATE DE RESPONSIVIDADE  ' + URL_ALVO);
console.log('='.repeat(88));
console.log('tela'.padEnd(18) + 'dim'.padEnd(12) + 'overflow'.padEnd(10) + 'CTA'.padEnd(8) + 'toque'.padEnd(8) + 'texto'.padEnd(8) + 'imagem');
console.log('-'.repeat(88));

for (const [nome, w, h, mob] of TELAS) {
  const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  const page = await ctx.newPage();
  try { await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  await page.waitForTimeout(1200);

  const r = await page.evaluate((ehMobile) => {
    const doc = document.documentElement;
    const saida = { overflow: doc.scrollWidth - doc.clientWidth, toqueRuim: [], textoPequeno: [], cortado: [], distorcida: [], estouro: [] };

    // OVERFLOW INTERNO. O overflow do DOCUMENTO nao ve corte dentro de container que tem
    // `overflow-hidden`: ele zera o scrollWidth e o defeito fica invisivel pra qualquer
    // medicao de pagina. Foi assim que tres cards de depoimento com largura fixa de 390px
    // dentro de uma trilha de 342px sairam CORTADOS em todo celular, passando limpo por dois
    // gates (26/08/2026). Aqui a comparacao e filho x pai, nao pagina x viewport.
    for (const filho of document.querySelectorAll('article, figure, li > div, .card, [class*="rounded"]')) {
      const pai = filho.parentElement;
      if (!pai) continue;
      const csf = getComputedStyle(filho);
      // Decoracao SAI da caixa de proposito (bloco de cor com offset negativo, sangria,
      // faixa que atravessa a borda). O que e defeito e CONTEUDO estourando o container.
      if (filho.getAttribute('aria-hidden') === 'true') continue;
      if (csf.pointerEvents === 'none') continue;
      if (csf.position === 'absolute' || csf.position === 'fixed') continue;
      if (!(filho.innerText || '').trim()) continue;
      const cf = filho.getBoundingClientRect();
      const cp = pai.getBoundingClientRect();
      if (cf.width < 60 || cp.width < 60) continue;
      const sobra = Math.round(cf.right - cp.right);
      const sobraEsq = Math.round(cp.left - cf.left);
      // 2px de folga: sub-pixel de layout nao e defeito
      if (sobra > 2 || sobraEsq > 2) {
        const cs = getComputedStyle(pai);
        const escondido = cs.overflowX === 'hidden' || cs.overflow === 'hidden';
        saida.estouro.push(
          `${(filho.innerText || filho.tagName).replace(/\s+/g, ' ').trim().slice(0, 22)} ` +
          `(+${Math.max(sobra, sobraEsq)}px${escondido ? ', CORTADO pelo overflow-hidden do pai' : ''})`,
        );
      }
    }

    // BOTAO EM UMA LINHA. Conta as linhas do proprio texto do botao, palavra por palavra, pelo
    // topo de cada retangulo de texto. Altura do botao nao serve: padding grande engana.
    saida.botaoQuebrado = [];
    if (window.innerWidth <= 768) {
      for (const el of document.querySelectorAll('a, button, [data-cta]')) {
        const cs = getComputedStyle(el);
        const txt = (el.innerText || '').replace(/\s+/g, ' ').trim();
        const c = el.getBoundingClientRect();
        const temCaixa = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || el.hasAttribute('data-cta');
        if (!temCaixa || txt.length < 4 || txt.length > 60 || c.width < 40 || c.height < 20) continue;
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        const topos = [];
        const andar = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        for (let n = andar.nextNode(); n; n = andar.nextNode()) {
          const r = document.createRange();
          r.selectNodeContents(n);
          for (const ret of r.getClientRects()) {
            if (ret.width < 1) continue;
            if (!topos.some((t) => Math.abs(t - ret.top) < 4)) topos.push(ret.top);
          }
        }
        if (topos.length > 1) saida.botaoQuebrado.push(`"${txt.slice(0, 30)}" quebra em ${topos.length} linhas (${Math.round(c.height)}px)`);
      }
    }

    // CTA principal acima da dobra: regra de pagina de venda.
    const heroi = document.querySelector('section');
    const cta = heroi && heroi.querySelector('a[href^="#"], a[href^="tel:"], a[href^="http"], button');
    saida.ctaBottom = cta ? Math.round(cta.getBoundingClientRect().bottom) : null;
    saida.viewportH = window.innerHeight;

    // A lista de botoes candidatos sai daqui; a MEDICAO do fundo acontece fora do
    // evaluate, sobre o pixel renderizado (ver `mediaDoFundo`). getComputedStyle do pai
    // mente quando o fundo e video, foto ou gradiente, e foi assim que um CTA camuflado
    // passou por todo gate de acessibilidade.
    saida.botoes = [...document.querySelectorAll('a, button')]
      .filter((el) => {
        const cs = getComputedStyle(el);
        const txt = (el.innerText || '').trim();
        const c = el.getBoundingClientRect();
        return txt.length > 3 && txt.length < 44 && cs.backgroundColor !== 'rgba(0, 0, 0, 0)'
          && c.width >= 40 && c.height >= 20;
      })
      .slice(0, 12)
      .map((el) => {
        const c = el.getBoundingClientRect();
        return {
          texto: (el.innerText || '').trim().slice(0, 24),
          cor: getComputedStyle(el).backgroundColor,
          x: Math.round(c.x), y: Math.round(c.y), w: Math.round(c.width), h: Math.round(c.height),
        };
      });

    if (ehMobile) {
      // Alvo de toque: 44px e o minimo de Apple HIG e WCAG 2.5.5.
      for (const el of document.querySelectorAll('a, button, input, select, [role="button"]')) {
        const c = el.getBoundingClientRect();
        if (c.width < 2 || c.height < 2) continue;                 // escondido
        if (getComputedStyle(el).display === 'none') continue;
        // 0.5px de folga: 43.99 vira "44" no relatorio, e gate que acusa um numero e mostra
        // outro so confunde quem esta consertando.
        if (c.height < 43.5 && (el.innerText || '').trim().length > 1) {
          saida.toqueRuim.push(`${(el.innerText || '').trim().slice(0, 22)} (${Math.round(c.height)}px)`);
        }
      }
      // Corpo de texto legivel. LABEL nao e corpo: eyebrow em caixa alta com tracking
      // ("SAUDE E SEGURANCA NO TRABALHO") e convencao de design, fica legivel em 12px e
      // seria falso positivo aqui. O que importa e o texto que a pessoa LE por extenso.
      for (const el of document.querySelectorAll('p, li, dd')) {
        const t = (el.innerText || '').trim();
        if (t.length < 25) continue;
        const cs = getComputedStyle(el);
        const px = parseFloat(cs.fontSize);
        const ehLabel =
          cs.textTransform === 'uppercase' ||
          parseFloat(cs.letterSpacing) > 0.8 ||
          t === t.toUpperCase();
        if (ehLabel) continue;
        if (px < 14) saida.textoPequeno.push(`${t.slice(0, 22)} (${px.toFixed(0)}px)`);
      }
    }

    // Texto cortado pela propria caixa.
    // Conteudo SO para leitor de tela (sr-only: caixa de 1px com clip) nao e texto cortado: e
    // o padrao de acessibilidade do link "Pular para o conteudo". Reprovar isso empurrava o
    // aluno a apagar um recurso de acessibilidade (teste com aluno, 02/10/2026).
    const soLeitorDeTela = (el, cs) => {
      const c = el.getBoundingClientRect();
      const clip = (cs.clip || '').replace(/\s+/g, '');
      const clipPath = cs.clipPath || '';
      return (c.width <= 1.5 && c.height <= 1.5)
        || clip === 'rect(0px,0px,0px,0px)' || clip === 'rect(0,0,0,0)' || clip === 'rect(1px,1px,1px,1px)'
        || /inset\(50%\)/.test(clipPath);
    };
    for (const el of document.querySelectorAll('p, h1, h2, h3, li, span, a')) {
      const cs = getComputedStyle(el);
      if (cs.overflow !== 'hidden' && cs.overflowY !== 'hidden') continue;
      if (soLeitorDeTela(el, cs)) continue;
      if (cs.webkitLineClamp !== 'none') continue;                 // clamp e intencional
      if (el.scrollHeight - el.clientHeight > 4 && (el.innerText || '').trim().length > 8) {
        saida.cortado.push((el.innerText || '').trim().slice(0, 26));
      }
    }

    // Imagem distorcida: proporcao do arquivo x proporcao renderizada.
    for (const img of document.images) {
      if (!img.naturalWidth || !img.complete) continue;
      const c = img.getBoundingClientRect();
      if (c.width < 24 || c.height < 24) continue;
      const cs = getComputedStyle(img);
      if (cs.objectFit === 'cover' || cs.objectFit === 'contain') continue;  // fit resolve
      const rArq = img.naturalWidth / img.naturalHeight;
      const rRend = c.width / c.height;
      if (Math.abs(rArq - rRend) / rArq > 0.06) {
        saida.distorcida.push(`${img.src.split('/').pop()} (${rArq.toFixed(2)} -> ${rRend.toFixed(2)})`);
      }
    }
    return saida;
  }, mob);

  // CTA CONTRA O FUNDO, no pixel. Um botao tem DOIS contrastes e o segundo quase nunca e
  // medido: texto/botao (4,5:1) e BOTAO/FUNDO (3:1).
  r.ctaSemContraste = [];
  // ROLA ate cada botao antes de medir. A primeira versao media so o que ja estava na
  // viewport inicial, entao o CTA do FIM da pagina (justamente o que estava camuflado)
  // nunca era testado, e o gate passava com o defeito na tela.
  const alvos = await page.$$('a, button');
  for (const el of alvos) {
    const info = await el.evaluate((n) => {
      const cs = getComputedStyle(n);
      const txt = (n.innerText || '').trim();
      const c = n.getBoundingClientRect();
      if (txt.length < 4 || txt.length > 44) return null;
      if (cs.backgroundColor === 'rgba(0, 0, 0, 0)') return null;
      if (c.width < 40 || c.height < 20) return null;
      return { texto: txt.slice(0, 24), cor: cs.backgroundColor };
    });
    if (!info) continue;
    try {
      await el.scrollIntoViewIfNeeded();
      let cx = await caixaAssentada(el);
      if (!cx || cx.y < 30) continue;
      // Nada de prazo chutado aqui: mede ate a propria faixa parar de mudar.
      // E CONFERE a caixa DEPOIS de medir: se o botao andou enquanto a faixa
      // assentava, o recorte ficou preso na coordenada velha e pode ter pego o
      // proprio botao como "fundo". Nesse caso, mede de novo. Sem esta conferencia
      // a reprovacao aparecia so as vezes, o que e pior que aparecer sempre.
      let fundo = null;
      for (let tentativa = 0; tentativa < 3; tentativa++) {
        fundo = await fundoAssentado(page, {
          x: Math.round(cx.x), y: Math.round(cx.y) - 30,
          width: Math.min(Math.round(cx.width), w - Math.round(cx.x)), height: 20,
        });
        const depois = await el.boundingBox();
        if (!depois || (Math.abs(depois.y - cx.y) <= 2 && Math.abs(depois.x - cx.x) <= 2)) break;
        cx = depois;
      }
      if (!fundo) continue;
      const [br, bg, bb] = (info.cor.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).map(Number);
      const c = contraste(lum(br, bg, bb), lum(...fundo));
      if (c < 3) r.ctaSemContraste.push(`${info.texto} (${c.toFixed(2)}:1)`);
    } catch { /* elemento saiu da arvore: ignora */ }
  }
  // BOTAO A NO MAXIMO 2 TELAS (celular). Rola a pagina de verdade, um terco de tela por vez, e
  // pergunta em cada parada se ALGUM botao esta visivel na janela. Assim barra fixa que so
  // aparece depois do hero conta, e botao escondido no celular (hidden sm:inline-flex) nao conta.
  r.trechoSemBotao = null;
  if (mob) {
    const altura = await page.evaluate(() => document.documentElement.scrollHeight);
    const passo = Math.max(120, Math.round(h / 3));
    let inicio = null, pior = 0, piorInicio = 0;
    for (let y = 0; y <= Math.max(0, altura - h) + passo; y += passo) {
      const yy = Math.min(y, Math.max(0, altura - h));
      await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), yy);
      await page.waitForTimeout(160);
      const visivel = await page.evaluate(() => [...document.querySelectorAll('a, button, [data-cta]')].some((el) => {
        const cs = getComputedStyle(el);
        const txt = (el.innerText || '').trim();
        const temCaixa = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || el.hasAttribute('data-cta');
        if (!temCaixa || txt.length < 4 || txt.length > 60) return false;
        if (el.checkVisibility && !el.checkVisibility({ opacityProperty: true, visibilityProperty: true })) return false;
        const c = el.getBoundingClientRect();
        return c.width >= 40 && c.height >= 20 && c.bottom > 0 && c.top < window.innerHeight;
      }));
      if (visivel) { inicio = null; }
      else {
        if (inicio === null) inicio = yy;
        const trecho = yy - inicio + h;
        if (trecho > pior) { pior = trecho; piorInicio = inicio; }
      }
      if (yy >= altura - h) break;
    }
    if (pior > 2 * h) r.trechoSemBotao = { px: pior, telas: pior / h, de: piorInicio };
  }
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));

  const ctaOk = r.ctaBottom !== null && r.ctaBottom <= r.viewportH;
  const marca = (b) => (b ? 'ok  ' : 'FALHA');
  console.log(
    nome.padEnd(18) + `${w}x${h}`.padEnd(12) +
    marca(r.overflow === 0).padEnd(10) +
    marca(ctaOk).padEnd(8) +
    (mob ? marca(!r.toqueRuim.length) : '-   ').padEnd(8) +
    (mob ? marca(!r.textoPequeno.length) : '-   ').padEnd(8) +
    marca(!r.distorcida.length),
  );

  const onde = `${nome} (${w}x${h})`;
  if (r.overflow > 0) falhas.push(`${onde}: overflow horizontal de ${r.overflow}px`);
  if (r.ctaSemContraste?.length)
    falhas.push(`${onde}: CTA camuflado no fundo (< 3:1): ${r.ctaSemContraste.slice(0, 3).join(', ')}`);
  if (!ctaOk) falhas.push(`${onde}: CTA do heroi abaixo da dobra (termina em ${r.ctaBottom}px de ${r.viewportH}px)`);
  if (r.botaoQuebrado?.length) falhas.push(`${onde}: botao em mais de uma linha: ${r.botaoQuebrado.slice(0, 3).join(', ')}`);
  if (r.trechoSemBotao) falhas.push(`${onde}: ${r.trechoSemBotao.telas.toFixed(1)} telas sem nenhum botao visivel a partir de y ${r.trechoSemBotao.de} (maximo 2): barra fixa no celular ou botao repetido`);
  if (r.toqueRuim.length) falhas.push(`${onde}: ${r.toqueRuim.length} alvo(s) de toque < 44px: ${r.toqueRuim.slice(0, 3).join(', ')}`);
  if (r.textoPequeno.length) falhas.push(`${onde}: texto de corpo < 14px: ${r.textoPequeno.slice(0, 3).join(', ')}`);
  if (r.cortado.length) falhas.push(`${onde}: texto cortado pela caixa: ${r.cortado.slice(0, 3).join(', ')}`);
  if (r.estouro?.length)
    falhas.push(`${onde}: elemento maior que o container: ${[...new Set(r.estouro)].slice(0, 3).join(', ')}`);
  if (r.distorcida.length) avisos.push(`${onde}: imagem possivelmente distorcida: ${r.distorcida.slice(0, 2).join(', ')}`);

  await ctx.close();
}
await navegador.close();

console.log('='.repeat(88));
avisos.forEach((a) => console.log('  aviso: ' + a));
if (falhas.length) {
  falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${falhas.length} problema(s) de responsividade em ${TELAS.length} telas.`);
  console.log('  Duas lembrancas que custaram caro aqui:');
  console.log('   - ALTURA conta tanto quanto largura: janela baixa com titulo grande empurra o');
  console.log('     CTA pra fora da dobra, e teste de largura sozinho nunca pega isso.');
  console.log('   - um botao tem DOIS contrastes: o texto dentro dele E ele contra o fundo.');
  console.log('     Consertar so o primeiro ja produziu botao verde escuro em secao verde escura.\n');
  process.exit(1);
}
console.log(`  PASSA: ${TELAS.length} telas, nenhum problema de responsividade.\n`);
