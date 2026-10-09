#!/usr/bin/env node
/**
 * GATE DE RITMO: duas seções vizinhas nunca têm o mesmo esqueleto, e só uma pode ser
 * "título centralizado + cartões".
 *
 * Por que existe (04/10/2026, a v7 do estúdio contra a v6). A v6 estava correta e genérica: o
 * dono a reprovou. A v7 saiu muito melhor, e a diferença que se mede é o ritmo: cada seção
 * escolheu um esqueleto (posição do título x tipo de conteúdo) que a anterior não usou, e o molde
 * "título centralizado + cartões iguais" apareceu uma vez, não duas ou três. O gate-composicao só
 * reprova a TERCEIRA seção seguida com o mesmo esqueleto; a régua precisa ser a segunda.
 *
 * Por que é um gate à parte e não mais uma regra do gate-composicao: o composicao já cuida de
 * ícone, wireframe, linha do tempo e contraste (400 linhas) e guarda a assinatura em 5 tipos de
 * corpo. O ritmo precisa distinguir cartões iguais de comparação assimétrica (a assimetria
 * declarada no plano é o que quebra o molde), então tem a própria medida, e a decisão mora em
 * `ritmo-regras.mjs`, testada sem navegador.
 *
 * Esqueleto de cada seção (desktop 1440, depois de rolar a página inteira):
 *   título: à esquerda e em cima, centralizado, ou ao lado do conteúdo;
 *   corpo:  cartões (2 ou mais blocos de texto lado a lado de peso parecido, com caixa ou sem),
 *           assimétrico (blocos lado a lado de pesos muito diferentes: largo x estreito),
 *           configurador (3.5.12: uma coluna com 4 ou mais controles, radios, campos ou botões de
 *           escolha, ao lado de um resumo: não é "cartões iguais" mesmo com larguras parecidas),
 *           split com imagem, faixa de fotos, lista (3 ou mais itens empilhados, ou colunas de
 *           perguntas `details` ou de `li`: 3.5.12, duas colunas de FAQ não são cartões) ou texto.
 *
 * Como o título é classificado (3.5.10): pelo alinhamento real, não pelo centro da caixa do texto.
 *   lado:   há conteúdo (120 px ou mais de largura) à direita do título, na altura dele (3.5.12:
 *           sobreposição vertical de pelo menos 24 px ou 30% do título; conteúdo que só começa logo
 *           abaixo do título, como o 3º cartão de uma fileira sob um título curto, não é "ao lado");
 *   centro: `text-align` calculado centralizado E a primeira linha com o centro a menos de 40 px
 *           do centro da seção; ou texto à esquerda numa caixa que se ajusta ao texto (até 60%
 *           da seção) e está no meio da seção (flex ou margin auto);
 *   esq:    o resto (um h2 largo alinhado à esquerda é esq, mesmo com 2 linhas cheias).
 *   A saída mostra, para cada seção, `como mediu o título: ...` com text-align e posição da 1ª linha.
 *
 * Exceção declarada: `data-ritmo-ok="motivo"` na seção (o motivo aparece na saída).
 *
 * Uso: node scripts/gate-ritmo.mjs --url <url>
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import path from 'node:path';
import { exigirServidor } from './servidor-no-ar.mjs';
import { avaliarRitmo, CENTRO_CARTOES, MAXIMO_CENTRO_CARTOES } from './ritmo-regras.mjs';

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
  console.error('uso: node gate-ritmo.mjs --url <url>');
  process.exit(2);
}
// Dois blocos lado a lado pesam "parecido" quando o menor tem pelo menos 70% da largura do maior.
const PESO_PARECIDO = 0.7;

await exigirServidor(URL_ALVO);   // servidor caído: uma mensagem clara (saída 3), não ERR_CONNECTION_REFUSED (P11)
const navegador = await chromium.launch();
const ctx = await navegador.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();
try { await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
const altura = await page.evaluate(() => document.documentElement.scrollHeight);
for (let y = 0; y <= altura; y += 450) {
  await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await page.waitForTimeout(120);
}
await page.waitForTimeout(1200);
await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
await page.waitForTimeout(200);

const secoes = await page.evaluate((PESO) => {
  const visivel = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const c = el.getBoundingClientRect();
    return c.width > 1 && c.height > 1;
  };
  const rotulo = (el) => (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 40);
  const lado = (a, b) => (a.right <= b.left + 4 || b.right <= a.left + 4) && a.top < b.bottom && b.top < a.bottom;
  const MIDIA = ['IMG', 'PICTURE', 'VIDEO', 'CANVAS', 'svg', 'FIGURE'];
  const ehMidia = (el) => {
    if (MIDIA.includes(el.tagName)) return true;
    const c = el.getBoundingClientRect();
    const texto = (el.innerText || '').trim().length;
    // Coluna de ilustração (sticky ou não): quase sem texto e com mídia grande dentro.
    return texto < 40 && [...el.querySelectorAll('img, picture, video, canvas, svg')].some((m) => {
      const r = m.getBoundingClientRect(); return r.width >= 80 && r.height >= 80 && r.width * r.height >= c.width * c.height * 0.3;
    });
  };
  // Tipo da mídia de uma coluna: foto (img, picture, vídeo) ou desenho (svg, canvas), e se ela
  // fica fixa na rolagem. Uma foto ao lado do texto e um desenho fixo ao lado de passos são
  // esqueletos diferentes para quem lê, mesmo com o título na mesma posição.
  const tipoMidia = (f) => {
    const foto = f.matches('img, picture, video') || !!f.querySelector('img, picture, video');
    const fixa = [f, ...f.querySelectorAll('*')].some((n) => ['sticky', 'fixed'].includes(getComputedStyle(n).position));
    return (foto ? 'foto' : 'desenho') + (fixa ? ' fixo' : '');
  };
  // 3.5.13 (auditoria, achado 1): "configurador" é a coluna com controles que a visitante VÊ e usa, em grupos. Conta o controle
  // visível e interativo (8x8 px ou mais, sem display:none nem visibility:hidden); radio ou caixa escondido (1 px, opacidade 0)
  // conta pelo label visível. Conta GRUPOS (fieldset, radiogroup, radios do mesmo name, cada campo; botões e abas do mesmo
  // pai são um grupo), e o configurador precisa de 4 controles em 2 grupos ou mais. Só UMA coluna da fileira pode ter
  // controles: a outra é o resumo.
  const SELETOR_CONTROLE = 'input:not([type=hidden]), select, textarea, button, [role=radio], [role=checkbox], [role=tab], [role=switch], [role=option]';
  const grande = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const c = el.getBoundingClientRect();
    return c.width >= 8 && c.height >= 8;
  };
  const ehEscolha = (c) => ['radio', 'checkbox'].includes(c.type) || ['radio', 'checkbox', 'switch'].includes(c.getAttribute('role'));
  const rotuloVisivel = (c) => ehEscolha(c) && ([...(c.labels || [])].some(grande) || (c.closest('label') && grande(c.closest('label'))));
  const controlesVisiveis = (f) => {
    const todos = [...f.querySelectorAll(SELETOR_CONTROLE)];
    if (f.matches(SELETOR_CONTROLE)) todos.push(f);
    return todos.filter((c) => !c.closest('[hidden]') && (grande(c) || rotuloVisivel(c)));
  };
  const chaveDeGrupo = (c, ids) => {
    const id = (n) => { if (!ids.has(n)) ids.set(n, ids.size); return ids.get(n); };
    const grupo = c.closest('fieldset, [role=radiogroup], [role=tablist], [role=listbox], [role=group]');
    if (grupo) return 'g' + id(grupo);
    if (c.type === 'radio' && c.name) return 'r' + (c.form ? id(c.form) : '') + ':' + c.name;
    if (ehEscolha(c) || ['INPUT', 'SELECT', 'TEXTAREA'].includes(c.tagName)) return 'c' + id(c);
    return 'p' + id(c.parentElement || c);   // botões, abas e opções: o mesmo pai é um grupo só
  };
  const ehConfigurador = (ctls) => {
    const ids = new Map();
    return ctls.length >= 4 && new Set(ctls.map((c) => chaveDeGrupo(c, ids))).size >= 2;
  };
  // 3.5.13 (achado 3): coluna com caixa própria (fundo diferente do da seção, borda, sombra ou padding interno dos dois lados)
  // é cartão, seja qual for a tag (ul, ol, dl, div).
  const rgba = (v) => { const m = /rgba?\(([^)]+)\)/.exec(v || ''); if (!m) return [0, 0, 0, 0]; const n = m[1].split(',').map((x) => parseFloat(x)); return [n[0], n[1], n[2], n.length > 3 ? n[3] : 1]; };
  const fundoDe = (el) => { for (let n = el; n; n = n.parentElement) { const c = rgba(getComputedStyle(n).backgroundColor); if (c[3] > 0.05) return c.slice(0, 3).join(','); } return '255,255,255'; };
  const temCaixa = (f) => {
    const cs = getComputedStyle(f);
    const bg = rgba(cs.backgroundColor);
    if (bg[3] > 0.05 && bg.slice(0, 3).join(',') !== fundoDe(f.parentElement)) return true;
    if (['Top', 'Right', 'Bottom', 'Left'].some((l) => parseFloat(cs['border' + l + 'Width']) > 0 && cs['border' + l + 'Style'] !== 'none' && rgba(cs['border' + l + 'Color'])[3] > 0.05)) return true;
    if (cs.boxShadow && cs.boxShadow !== 'none') return true;
    const pad = (l) => parseFloat(cs['padding' + l]) || 0;
    return (pad('Top') >= 8 && pad('Bottom') >= 8) || (pad('Left') >= 8 && pad('Right') >= 8);
  };
  // Coluna de lista: a própria coluna é uma lista de linhas leves (ul/ol com 3 ou mais li, dl com 3 ou mais filhos, sem caixa
  // própria e sem título próprio nos itens) ou um grupo de 2 ou mais `details` (perguntas). Cartão com título, texto e uma lista
  // dentro NÃO é coluna de lista: os filhos dele são de tipos diferentes.
  const colunaDeLista = (f) => {
    if (temCaixa(f)) return false;
    const itens = [...f.children].filter(visivel);
    const tags = new Set(itens.map((i) => i.tagName));
    const temTitulo = itens.some((i) => i.querySelector('h1, h2, h3, h4, h5, h6'));
    if (['UL', 'OL'].includes(f.tagName)) return itens.length >= 3 && tags.size === 1 && tags.has('LI') && !temTitulo;
    if (f.tagName === 'DL') return itens.length >= 3 && !temTitulo;
    return itens.length >= 2 && tags.size === 1 && tags.has('DETAILS');
  };
  // Só uma coluna é o configurador; as outras (o resumo do pedido) não têm controles.
  const configuradorUnico = (colunas) => {
    const ctls = colunas.map(controlesVisiveis);
    const cfg = ctls.map((c, i) => (ehConfigurador(c) ? i : -1)).filter((i) => i >= 0);
    return cfg.length === 1 && ctls.every((c, i) => i === cfg[0] || c.length === 0);
  };
  const lista = [...document.querySelectorAll('section')]
    .filter((s) => visivel(s) && !s.parentElement.closest('section') && s.getBoundingClientRect().height >= 120);
  return lista.map((s, i) => {
    const excecao = s.getAttribute('data-ritmo-ok') || undefined;
    const h = [...s.querySelectorAll('h2')].find(visivel) || [...s.querySelectorAll('h1')].find(visivel);
    if (!h) return { nome: s.id || `seção ${i + 1}`, sig: `sem-titulo:${i}`, excecao };
    const hr = h.getBoundingClientRect(), sr = s.getBoundingClientRect();
    const todos = [...s.querySelectorAll('*')].filter((el) => visivel(el) && !el.contains(h) && !h.contains(el));

    // Posição do título. 3.5.10 (P18): "centralizado" se mede pelo alinhamento REAL, não pelo centro
    // da caixa que cobre todas as linhas (um h2 largo, alinhado à esquerda, em 2 linhas cheias,
    // tem essa caixa no meio da seção e foi chamado de centralizado). Mede-se o text-align
    // calculado e a posição da PRIMEIRA linha; a medida vai para a saída.
    const px = (n) => Math.round(n);
    const centroSecao = (sr.left + sr.right) / 2;
    const rg = document.createRange(); rg.selectNodeContents(h);
    const linhasTitulo = [...rg.getClientRects()].filter((r) => r.width > 1 && r.height > 1);
    const topoTitulo = Math.min(...linhasTitulo.map((r) => r.top));
    const l1 = linhasTitulo.filter((r) => Math.abs(r.top - topoTitulo) < r.height * 0.5);
    const l1E = Math.min(...l1.map((r) => r.left)), l1D = Math.max(...l1.map((r) => r.right));
    const centroL1 = (l1E + l1D) / 2;
    const alinhamento = getComputedStyle(h).textAlign;
    const alinhaCentro = /center/.test(alinhamento);
    let titulo = 'esq';
    let medida = '';
    // 3.5.12: "ao lado" exige sobreposição vertical de verdade com o título. A regra antiga aceitava
    // conteúdo que começava até 40 px ABAIXO da base do título, e o 3º cartão de uma fileira que
    // vem logo abaixo de um título curto centralizado ficava à direita dele e contava como "ao lado".
    const sobreposicaoMinima = Math.min(24, hr.height * 0.3);
    // 3.5.13 (achado 6): o conteúdo "ao lado" tem de estar numa COLUNA IRMÃ do título (mesma grade ou flex), em fluxo, visível para quem
    // lê e com texto ou mídia. Selo aria-hidden, enfeite em position absolute ou fixed e caixa vazia não fazem "título ao lado".
    const colunasIrmas = [];
    for (let a = h; a && a !== s; a = a.parentElement) {
      const p = a.parentElement;
      if (p && /grid|flex/.test(getComputedStyle(p).display)) colunasIrmas.push(...[...p.children].filter((k) => k !== a && visivel(k)));
    }
    const colunaValida = (k) => !['absolute', 'fixed'].includes(getComputedStyle(k).position) && !k.closest('[aria-hidden="true"]')
      && ((k.innerText || '').trim().length > 0 || MIDIA.includes(k.tagName) || !!k.querySelector('img, picture, video, canvas, svg'));
    const aoLado = colunasIrmas.filter(colunaValida).flatMap((k) => [k, ...k.querySelectorAll('*')]).filter(visivel);
    if (aoLado.some((el) => {
      const c = el.getBoundingClientRect();
      const sobreposto = Math.min(c.bottom, hr.bottom) - Math.max(c.top, hr.top);
      return c.width >= 120 && c.height >= 60 && c.left >= hr.right - 4 && sobreposto >= sobreposicaoMinima;
    })) {
      titulo = 'lado';
      medida = `há conteúdo ao lado do título (a partir de ${px(hr.right)} px)`;
    } else if (alinhaCentro && Math.abs(centroL1 - centroSecao) < 40) {
      titulo = 'centro';
      medida = `text-align ${alinhamento}; 1ª linha de ${px(l1E)} a ${px(l1D)} px, centro ${px(centroL1)} px (seção: centro ${px(centroSecao)} px)`;
    } else if (!alinhaCentro && hr.width <= sr.width * 0.6 && Math.abs((hr.left + hr.right) / 2 - centroSecao) < 40
      && Math.max(...linhasTitulo.map((r) => r.right)) - Math.min(...linhasTitulo.map((r) => r.left)) >= hr.width - 16) {
      // Texto alinhado à esquerda, mas numa caixa que se ajusta ao texto e está no meio da seção
      // (flex ou margin auto com a caixa estreita): na tela o título aparece centralizado.
      titulo = 'centro';
      medida = `text-align ${alinhamento}, mas a caixa do título (${px(hr.width)} px de ${px(sr.width)}) está centralizada na seção (centro ${px((hr.left + hr.right) / 2)} px)`;
    } else {
      medida = alinhaCentro
        ? `text-align ${alinhamento}, mas a 1ª linha (de ${px(l1E)} a ${px(l1D)} px, centro ${px(centroL1)} px) não está no centro da seção (${px(centroSecao)} px)`
        : `text-align ${alinhamento}; 1ª linha de ${px(l1E)} a ${px(l1D)} px, começa a ${px(l1E - sr.left)} px da borda da seção`;
    }

    // Corpo: a maior linha de blocos lado a lado. Se a linha também carrega o título numa das
    // colunas (herói: título e botão numa coluna, foto na outra), o bloco do título não conta
    // como conteúdo: só o que está ao lado dele.
    let melhor = null;
    const candidatos = [s, ...[...s.querySelectorAll('*')].filter((el) => visivel(el) && !h.contains(el) && el !== h)];
    for (const el of candidatos) {
      const filhos = [...el.children].filter((f) => visivel(f) && f.getBoundingClientRect().width >= 120 && f.getBoundingClientRect().height >= 20);
      if (filhos.length < 2) continue;
      const juntos = filhos.filter((a, k) => filhos.some((b, j) => j !== k && lado(a.getBoundingClientRect(), b.getBoundingClientRect())));
      const corpoDaLinha = juntos.filter((f) => !f.contains(h));
      if (corpoDaLinha.length < 1 || juntos.length < 2) continue;
      const temTitulo = juntos.length !== corpoDaLinha.length;
      if (!temTitulo && corpoDaLinha.length < 2) continue;
      if (temTitulo && corpoDaLinha.length < 2 && !corpoDaLinha.some(ehMidia)) continue;
      const c = el.getBoundingClientRect();
      const area = c.width * c.height;
      if (!melhor || area > melhor.area) melhor = { el, juntos: corpoDaLinha, area };
    }
    let corpo = 'texto';
    if (melhor) {
      const midias = melhor.juntos.filter(ehMidia);
      const textuais = melhor.juntos.filter((f) => !ehMidia(f));
      if (midias.length && textuais.length) corpo = 'split com ' + tipoMidia(midias[0]);
      else if (midias.length >= 2) corpo = 'faixa de fotos';
      else if (midias.length === 1) corpo = 'split com ' + tipoMidia(midias[0]); // título numa coluna, a mídia na outra
      else if (configuradorUnico(melhor.juntos)) corpo = 'configurador';
      else if (melhor.juntos.every(colunaDeLista)) corpo = 'lista';
      else {
        const larg = melhor.juntos.map((f) => f.getBoundingClientRect().width);
        corpo = Math.min(...larg) / Math.max(...larg) >= PESO ? 'cartões' : 'assimétrico';
      }
    } else if (todos.some((el) => ['IMG', 'PICTURE', 'VIDEO'].includes(el.tagName) && el.getBoundingClientRect().width >= sr.width * 0.6)) {
      corpo = 'faixa de fotos';
    } else if (todos.some((el) => ['UL', 'OL', 'DL'].includes(el.tagName) && [...el.children].filter(visivel).length >= 3) || s.querySelectorAll('details').length >= 3) {
      corpo = 'lista';
    }
    const nomes = { esq: 'título à esquerda', centro: 'título centralizado', lado: 'título ao lado do conteúdo' };
    return { nome: rotulo(h), sig: `${nomes[titulo]} + ${corpo}`, excecao, medida };
  });
}, PESO_PARECIDO);
await navegador.close();

const r = avaliarRitmo(secoes);
console.log('\nGATE DE RITMO  ' + URL_ALVO);
console.log('='.repeat(88));
console.log('Esqueleto de cada seção, na ordem da página (desktop 1440):');
secoes.forEach((s, i) => {
  console.log(`  ${String(i + 1).padStart(2)}. ${s.nome.padEnd(42)} ${s.sig.startsWith('sem-titulo') ? '(sem título)' : s.sig}${s.excecao ? `  [exceção: ${s.excecao}]` : ''}`);
  if (s.medida) console.log(`      como mediu o título: ${s.medida}`);
});
console.log(`medido: ${secoes.length} seções; "${CENTRO_CARTOES}" em ${r.centroCartoes} (máximo ${MAXIMO_CENTRO_CARTOES}); vizinhas iguais: ${r.falhas.filter((f) => /vizinhas/.test(f)).length}`);
console.log('='.repeat(88));
r.excecoes.forEach((e) => console.log('  exceção declarada (data-ritmo-ok): ' + e));
if (r.falhas.length) {
  r.falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${r.falhas.length} problema(s) de ritmo.\n`);
  process.exit(1);
}
console.log('  PASSA: nenhuma seção vizinha com o mesmo esqueleto e no máximo 1 "título centralizado + cartões".\n');
