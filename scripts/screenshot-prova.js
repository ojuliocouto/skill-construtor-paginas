#!/usr/bin/env node
// Prova de entrega da skill construtor-paginas.
// Captura screenshots desktop + mobile do deploy real e, opcionalmente,
// testa a interação principal (clique) registrando o estado antes e depois.
// Confere tambem a IDENTIDADE DA PAGINA (gate 4.2b: title, description, favicon PNG
// quadrado, og:title, og:description, og:image) e sai com exit 1 se faltar item.
// Uso:
//   export NODE_PATH="$HOME/.npm-global/lib/node_modules"
//   node screenshot-prova.js <url> <outdir> [--click "<seletor css>"] [--sem-identidade]
// Sai com exit 1 e mensagem clara em QUALQUER falha: sem screenshot nao ha entrega.
// Nada de stack trace do node na cara de quem roda: TODA chamada de navegador
// mora dentro do try, e o erro sai traduzido em uma linha acionável.

const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

const md5 = (arquivo) =>
  crypto.createHash('md5').update(fs.readFileSync(arquivo)).digest('hex');

// Traduz erro de navegador em instrução acionável. O caso mais comum de longe:
// a pessoa rodou `npm install -g playwright` e esqueceu o download do chromium,
// e o erro cru dava a impressão de que a skill inteira tinha quebrado.
function explicarFalha(e) {
  const msg = String((e && e.message) || e);
  if (msg.includes("Executable doesn't exist")) {
    return 'FALHA: o navegador do Playwright nao foi baixado. Rode: npx playwright install chromium';
  }
  return `FALHA na prova de entrega: ${msg.split('\n')[0]}`;
}

function bloquear(e) {
  console.error(explicarFalha(e));
  console.error('ENTREGA BLOQUEADA: conserte a verificacao antes de declarar pronto.');
  process.exit(1);
}

// IDENTIDADE DA PÁGINA (gate 4.2b). Existe porque o item já estava escrito em
// checklist, com aviso de que "saiu zerado na 1a versão", e MESMO ASSIM uma página
// foi entregue sem favicon e sem nenhuma og tag: o <head> não aparece no print, e
// ler o PNG com os próprios olhos nunca ia pegar isso. Checklist não bloqueia,
// script bloqueia.
//
// Bloqueia: title, meta description, favicon PNG quadrado, og:title, og:description
//           e a TAG og:image (6 linhas de HTML, não dependem de domínio).
// Avisa (pendência declarada, não bloqueia): og:image com URL relativa ou que ainda
//           não responde, caso normal antes de existir domínio.
const TITULOS_VAZIOS = ['', 'document', 'untitled', 'index', 'vite + react', 'react app', 'home'];

async function conferirIdentidade(page) {
  const d = await page.evaluate(() => {
    const c = (sel) => document.querySelector(sel)?.getAttribute('content')?.trim() || '';
    const og = (p) => c(`meta[property="${p}"]`) || c(`meta[name="${p}"]`);
    const icones = [...document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]')]
      .map((l) => ({ rel: l.getAttribute('rel') || '', href: l.href || '', type: (l.getAttribute('type') || '').toLowerCase() }));
    return {
      title: (document.title || '').trim(),
      description: c('meta[name="description"]'),
      ogTitle: og('og:title'),
      ogDescription: og('og:description'),
      ogImage: og('og:image'),
      icones,
    };
  });

  const falhas = [];
  const linhas = [];
  const reprova = (m) => { falhas.push(m); linhas.push(`  REPROVA  ${m}`); };
  const ok = (m) => linhas.push(`  ok       ${m}`);
  const aviso = (m) => linhas.push(`  AVISO    ${m}`);

  if (TITULOS_VAZIOS.includes(d.title.toLowerCase())) reprova(`<title> ausente ou generico: "${d.title}"`);
  else ok(`title: "${d.title}"`);

  if (!d.description) reprova('<meta name="description"> ausente');
  else ok(`description: "${d.description.slice(0, 70)}${d.description.length > 70 ? '...' : ''}"`);

  // Favicon: PNG (muitos navegadores não leem SVG) e QUADRADO. Redimensionar
  // preservando proporção a partir de uma foto 3:2 devolve 32x21 e o navegador
  // distorce: recorte quadrado primeiro, depois redimensione.
  const png = d.icones
    .filter((i) => i.type.includes('png') || /\.png(\?|$)/i.test(i.href))
    .filter((i, n, arr) => arr.findIndex((x) => x.href === i.href) === n); // mesmo arquivo em icon + apple-touch-icon: conferir uma vez
  if (!d.icones.length) reprova('nenhum <link rel="icon"> na pagina');
  else if (!png.length) reprova(`favicon existe mas nao em PNG (${d.icones.map((i) => i.href.split('/').pop()).join(', ')})`);
  else {
    for (const ic of png) {
      const dim = await page.evaluate(
        (href) =>
          new Promise((res) => {
            const img = new Image();
            img.onload = () => res({ w: img.naturalWidth, h: img.naturalHeight });
            img.onerror = () => res(null);
            img.src = href;
          }),
        ic.href
      );
      const nome = ic.href.split('/').pop();
      if (!dim) reprova(`favicon nao carrega (404?): ${ic.href}`);
      else if (dim.w !== dim.h) reprova(`favicon NAO e quadrado: ${nome} tem ${dim.w}x${dim.h}. Recorte quadrado ANTES de redimensionar`);
      else ok(`favicon ${nome} ${dim.w}x${dim.h} (quadrado)`);
    }
  }

  if (!d.ogTitle) reprova('og:title ausente');
  else ok(`og:title: "${d.ogTitle.slice(0, 60)}"`);
  if (!d.ogDescription) reprova('og:description ausente');
  else ok('og:description presente');

  if (!d.ogImage) {
    reprova('og:image ausente (a TAG e obrigatoria sempre; so a URL absoluta pode ficar pendente)');
  } else if (!/^https?:\/\//i.test(d.ogImage)) {
    aviso(`og:image com URL relativa ("${d.ogImage}"): declarar como pendencia ate existir dominio`);
  } else {
    let status = 0;
    try {
      status = (await page.request.get(d.ogImage, { timeout: 15000 })).status();
    } catch { status = 0; }
    if (status === 200) ok(`og:image responde 200: ${d.ogImage}`);
    else aviso(`og:image ainda nao responde 200 (status ${status || 'sem resposta'}): ${d.ogImage}`);
  }

  console.log('IDENTIDADE DA PAGINA (gate 4.2b):');
  for (const l of linhas) console.log(l);
  return falhas;
}

// Estado observável da página, pra o clique ter prova além do pixel.
/** Passa a rolagem pela pagina INTEIRA antes de fotografar, e devolve quantos passos deu.
 *
 *  Existe porque em 27/08/2026 a prova de uma pagina real saiu com metade dos blocos em
 *  branco e o script imprimiu OK: conteudo com reveal por IntersectionObserver so entra
 *  quando a rolagem passa por ele, e o `fullPage` do Playwright NAO rola, ele expande o
 *  viewport. Resultado: fundo, cartao e sombra desenhados, e nenhuma letra dentro.
 *  O medidor de banda chapada nao pegava, porque o gradiente e o grao pintam a faixa.
 *
 *  Mata tambem o `scroll-behavior: smooth`, que faz a rolagem chegar atrasada e a medicao
 *  fotografar a faixa errada. Passar aqui tambem acorda imagem com loading="lazy".
 */
async function revelarPagina(page) {
  await page.addStyleTag({
    content: 'html,body{scroll-behavior:auto !important}',
  }).catch(() => { /* CSP pode barrar style tag: a rolagem abaixo ainda vale */ });

  const passos = await page.evaluate(async () => {
    const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
    const passo = Math.max(200, Math.round(window.innerHeight * 0.8));
    let n = 0;
    // A altura cresce conforme o conteudo entra: reler a cada volta, com teto de seguranca.
    for (let y = 0; y < document.documentElement.scrollHeight && n < 400; y += passo) {
      window.scrollTo(0, y);
      n++;
      await dorme(120);
    }
    window.scrollTo(0, document.documentElement.scrollHeight);
    await dorme(300);
    window.scrollTo(0, 0);
    await dorme(300);
    return n;
  });

  await page.waitForTimeout(700);
  return passos;
}

async function lerEstado(page, el) {
  const pagina = await page.evaluate(() => ({
    scrollY: Math.round(window.scrollY),
    url: location.href,
  }));
  let texto;
  try {
    texto = ((await el.innerText({ timeout: 2000 })) || '')
      .replace(/\s+/g, ' ').trim().slice(0, 60);
  } catch {
    texto = '(elemento saiu da pagina)';
  }
  return { ...pagina, texto };
}

async function main() {
  const args = process.argv.slice(2);
  const url = args[0];
  const outdir = args[1];
  const clickIdx = args.indexOf('--click');
  const clickSel = clickIdx > -1 ? args[clickIdx + 1] : null;
  // --sem-identidade existe SO pro baseline do caminho MELHORAR (pagina de
  // terceiro, que ainda nao e sua). Na prova de entrega, usar esta flag e pular
  // o gate 4.2b.
  const semIdentidade = args.includes('--sem-identidade');

  // --check: verifica SO se o Playwright esta utilizavel e sai. Existe porque a
  // deteccao ingenua (node -e "require('playwright')") da FALSO NEGATIVO com o
  // pacote instalado global, ja que o node nao procura pacote global por padrao.
  // Esta checagem passa pela MESMA resolucao que a prova de entrega usa, entao o
  // que ela responde e exatamente o que vai valer na hora de entregar.
  const soChecar = args.includes('--check');

  if (!soChecar && (!url || !outdir)) {
    console.error('uso: node screenshot-prova.js <url> <outdir> [--click "<seletor>"] [--sem-identidade]');
    console.error('     node screenshot-prova.js --check   (verifica so o Playwright)');
    process.exit(1);
  }

  // Resolve o playwright do projeto, do NODE_PATH ou do root global do npm, pra
  // funcionar em qualquer maquina sem o usuario precisar exportar variavel.
  let chromium;
  try {
    ({ chromium } = require('playwright'));
  } catch (e) {
    try {
      const rootGlobal = require('child_process')
        .execSync('npm root -g', { encoding: 'utf8' })
        .trim();
      ({ chromium } = require(path.join(rootGlobal, 'playwright')));
    } catch (e2) {
      console.error('FALHA: playwright nao encontrado. Rodar: npm install -g playwright && npx playwright install chromium');
      process.exit(1);
    }
  }

  if (soChecar) {
    // Nao basta achar o PACOTE: a meia-instalacao mais comum e ter o playwright
    // instalado e ter esquecido o "npx playwright install chromium". Nesse estado
    // o require passa e a prova de entrega quebra depois, que e o pior momento.
    let exe = null;
    try {
      exe = chromium.executablePath();
    } catch (e) {
      // versoes antigas podem nao expor executablePath: cai no teste forte abaixo
    }
    if (exe && !fs.existsSync(exe)) {
      console.error('FALHA: o pacote playwright esta instalado, mas o navegador nao foi baixado.');
      console.error('Rode: npx playwright install chromium');
      process.exit(1);
    }
    if (!exe) {
      try {
        const b = await chromium.launch({ headless: true });
        await b.close();
      } catch (e) {
        console.error(explicarFalha(e));
        process.exit(1);
      }
    }
    console.log('OK: Playwright e o navegador estao instalados e utilizaveis.');
    process.exit(0);
  }

  fs.mkdirSync(outdir, { recursive: true });
  const shots = [];
  const cliquesInertes = [];
  let falhasIdentidade = [];
  let browser;

  try {
    // O launch mora DENTRO do try: com o chromium não baixado ele rejeita, e
    // fora daqui isso virava "triggerUncaughtException" com caminho interno.
    browser = await chromium.launch({ headless: true });

    // Mobile de verdade é isMobile + hasTouch + DPR 2, não janela estreita:
    // sem isso o ponteiro, o toque e a densidade continuam de desktop, e quem
    // roda acha que validou celular quando não validou.
    const viewports = [
      { name: 'desktop', width: 1440, height: 900, movel: false, dpr: 1 },
      { name: 'mobile', width: 390, height: 844, movel: true, dpr: 2 },
    ];
    for (const vp of viewports) {
      const page = await browser.newPage({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.movel,
        hasTouch: vp.movel,
        deviceScaleFactor: vp.dpr,
      });
      await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(async () => {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(4000);
      });
      await page.waitForTimeout(1500);

      // Sem esta passada, pagina com reveal por rolagem sai fotografada como casca vazia.
      const passos = await revelarPagina(page);
      console.log(`  reveal           ${vp.name}: ${passos} passos de rolagem antes do print`);

      if (vp.name === 'desktop' && !semIdentidade) {
        falhasIdentidade = await conferirIdentidade(page);
      }

      const file = path.join(outdir, `prova-${vp.name}.png`);
      await page.screenshot({ path: file, fullPage: true });
      shots.push(file);

      if (clickSel) {
        const el = page.locator(clickSel).first();
        await el.waitFor({ state: 'visible', timeout: 10000 });

        // O print de ANTES sai com a mesma configuração do de depois (mesma
        // janela, fullPage false). Comparar fullPage com viewport dava
        // diferença garantida e não provava nada sobre o clique.
        const fAntes = path.join(outdir, `prova-${vp.name}-pre-clique.png`);
        await page.screenshot({ path: fAntes, fullPage: false });
        const antes = await lerEstado(page, el);

        await el.click();
        await page.waitForTimeout(2500);

        const fDepois = path.join(outdir, `prova-${vp.name}-pos-clique.png`);
        await page.screenshot({ path: fDepois, fullPage: false });
        const depois = await lerEstado(page, el);
        shots.push(fAntes, fDepois);

        const iguais = md5(fAntes) === md5(fDepois);
        console.log(`clique "${clickSel}" em ${vp.name}:`);
        console.log(`  scrollY          ${antes.scrollY} -> ${depois.scrollY}`);
        console.log(
          `  URL              ${antes.url === depois.url ? `igual (${depois.url})` : `${antes.url} -> ${depois.url}`}`
        );
        console.log(`  texto do alvo    "${antes.texto}" -> "${depois.texto}"`);
        console.log(`  pixels do print  ${iguais ? 'IDENTICOS' : 'mudaram'}`);
        if (iguais) {
          console.log('ATENCAO: o print pos-clique e identico ao anterior. O clique pode nao ter surtido efeito visivel.');
          cliquesInertes.push(vp.name);
        }
      }
      await page.close();
    }
  } catch (e) {
    if (browser) await browser.close().catch(() => {});
    bloquear(e);
  }

  await browser.close();

  for (const f of shots) {
    const kb = Math.round(fs.statSync(f).size / 1024);
    if (kb < 5) {
      console.error(`FALHA: ${f} tem so ${kb}KB (pagina em branco?). ENTREGA BLOQUEADA.`);
      process.exit(1);
    }
    console.log(`${f} (${kb}KB)`);
  }

  if (falhasIdentidade.length) {
    console.error(
      `\nREPROVA na IDENTIDADE DA PAGINA (${falhasIdentidade.length} item(ns)):\n  - ` +
        falhasIdentidade.join('\n  - ')
    );
    console.error(
      'ENTREGA BLOQUEADA: identidade da pagina e GATE (4.2b), nao checklist. ' +
        'Corrija o <head> e rode de novo. Os prints ficaram salvos em ' + outdir + '.'
    );
    process.exit(1);
  }

  if (cliquesInertes.length) {
    console.log(
      `PRINTS CAPTURADOS COM RESSALVA: o clique nao mudou nada visivel em ${cliquesInertes.join(' e ')}. ` +
      'Confira o seletor e a interacao antes de declarar pronto.'
    );
  } else {
    console.log('OK: agora LEIA os PNGs com a tool Read antes de declarar pronto.');
  }
}

main().catch(bloquear);
