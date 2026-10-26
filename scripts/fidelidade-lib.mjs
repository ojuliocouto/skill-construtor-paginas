/**
 * Contas do gate de fidelidade (3.7.0), sem navegador: o gate (`gate-fidelidade.mjs`) mede no Playwright e chama estas funções.
 *
 * De onde vem. No teste de aluno do CLONAR na 3.6.3 o aluno escreveu à mão um `medir.mjs` (50 elementos em 1440 e 390) e um
 * `comparar.py`, e foram eles que acharam TODOS os defeitos de fidelidade (herói 708 contra 723 px, margem 60 contra 45, bolinhas
 * nos logos, ícones 10% maiores). O `extrai-identidade.mjs` não os achava. Aqui a mesma ideia, sem nenhum dado do site:
 *   - os elementos-chave se pareiam pelo que eles SÃO (tag e texto, ou o nome do arquivo da imagem), não pela classe, que o clone pode trocar;
 *   - cada par se compara na caixa (x, y, largura, altura) e no estilo que se vê (fonte, peso, entrelinha, cor, fundo, canto);
 *   - o diff de pixels vira retângulos (células vizinhas diferentes juntas), cada um com o elemento da original que ele cobre.
 */

/** Propriedades de estilo comparadas, na ordem do laudo. */
export const PROPS = ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'color', 'backgroundColor', 'borderRadius', 'display'];

/** Limites padrão. Fora deles o gate reprova. Medidos no clone do aluno: 0,054% em 1440 e 0,183% em 390. */
export const LIMITES = { pixelsPct: 1.0, alturaPx: 4, caixaPx: 3, entrelinhaPx: 1, elementosComDiferenca: 0, faltando: 0 };

const ESTRUTURA = new Set(['section', 'header', 'footer', 'main', 'nav']);
const norm = (t) => String(t || '').replace(/\s+/g, ' ').trim().toLowerCase().slice(0, 80);

/** Nome-base da imagem sem pasta, sem query e sem o hash do empacotador (`logo.DqJRMuTx.svg` vira `logo`). */
export function nomeDaImagem(src) {
  const semQuery = String(src || '').split(/[?#]/)[0];
  const base = decodeURIComponent(semQuery.split('/').pop() || '');
  return base.replace(/\.[a-z0-9]{2,5}$/i, '').replace(/[.-][A-Za-z0-9_]{6,12}$/, '').toLowerCase();
}

/** Chave de pareamento de um elemento medido: o que ele é, não a classe que ele tem. */
export function chaveBase(e) {
  if (e.tag === 'img') return /^data:/i.test(e.src || '') ? `img|embutida:${norm(e.texto)}` : `img|${nomeDaImagem(e.src)}`;
  const t = norm(e.texto);
  if (t && e.tag !== 'section' && e.tag !== 'header' && e.tag !== 'footer' && e.tag !== 'main' && e.tag !== 'nav') return `${e.tag}|${t}`;
  return `${e.tag}#`;
}

/** Chaves com o número da ocorrência (o segundo "Saiba mais" é outro elemento). */
export function comChaves(lista) {
  const vistos = new Map();
  return lista.map((e) => {
    const b = chaveBase(e);
    const n = (vistos.get(b) || 0) + 1;
    vistos.set(b, n);
    return { ...e, chave: `${b}@${n}` };
  });
}

const px = (v) => { const m = /^(-?[\d.]+)px$/.exec(String(v || '').trim()); return m ? Number(m[1]) : null; };
const familia = (v) => String(v || '').split(',')[0].replace(/["']/g, '').trim().toLowerCase();

/** Diferença de estilo de um par, já em texto do laudo, ou null. */
function difDeProp(p, a, b, lim) {
  if (p === 'fontFamily') return familia(a) === familia(b) ? null : `fonte ${familia(a)} contra ${familia(b)}`;
  if (p === 'lineHeight') {
    const x = px(a), y = px(b);
    if (x !== null && y !== null) return Math.abs(x - y) > lim.entrelinhaPx ? `entrelinha ${a} contra ${b}` : null;
    return a === b ? null : `entrelinha ${a} contra ${b}`;
  }
  if (p === 'fontSize') { const x = px(a), y = px(b); return x !== null && y !== null && Math.abs(x - y) < 0.3 ? null : (a === b ? null : `fonte de ${a} contra ${b}`); }
  const nomes = { fontWeight: 'peso', color: 'cor', backgroundColor: 'fundo', borderRadius: 'canto', display: 'display' };
  return a === b ? null : `${nomes[p] || p} ${a} contra ${b}`;
}

/** Mesmo lugar: centro a até 8 px e tamanho a até 8 px (o par de quem mudou de texto ou de arquivo). */
const mesmoLugar = (a, b) => Math.abs(a.rect[0] + a.rect[2] / 2 - (b.rect[0] + b.rect[2] / 2)) <= 8 && Math.abs(a.rect[1] + a.rect[3] / 2 - (b.rect[1] + b.rect[3] / 2)) <= 8
  && Math.abs(a.rect[2] - b.rect[2]) <= 8 && Math.abs(a.rect[3] - b.rect[3]) <= 8;

/**
 * Compara as duas listas medidas (original e clone, na mesma largura).
 * Primeiro pareia pela chave (tag e texto, ou o nome da imagem); quem sobra se pareia pela tag no mesmo lugar, e aí o texto
 * diferente vira diferença ("texto ... contra ..."): é o caso da original que mudou depois do clone, ou da imagem embutida.
 * `temPixel(rect)` (opcional) diz se o diff de pixels tem célula diferente dentro da caixa: diferença de estilo SEM pixel
 * diferente não se vê, e fica como aviso (`invisivel: true`), fora da conta que reprova.
 * Devolve { pares, faltando: [chave], diferencas: [{chave, rotulo, itens, y, invisivel}] }.
 */
export function compararElementos(original, clone, lim = LIMITES, temPixel = null) {
  const o = comChaves(original);
  const listaC = comChaves(clone);
  const c = new Map(listaC.map((e) => [e.chave, e]));
  const usados = new Set();
  const faltando = [];
  const diferencas = [];
  let pares = 0;
  const casados = [];
  const sobra = [];
  for (const a of o) {
    const b = c.get(a.chave);
    if (b) { usados.add(b.chave); casados.push([a, b]); } else sobra.push(a);
  }
  for (const a of sobra) {
    const b = listaC.find((x) => !usados.has(x.chave) && x.tag === a.tag && mesmoLugar(a, x));
    if (b) { usados.add(b.chave); casados.push([a, b]); } else faltando.push(a.chave);
  }
  for (const [a, b] of casados) {
    pares++;
    const itens = [];
    // Só o texto que se lê (innerText): aria-label e title não aparecem na tela. Contêiner (seção, cabeçalho) não compara texto:
    // a diferença já sai no filho que a tem.
    const ta = String(a.visivel ?? '').replace(/\s+/g, ' ').trim(), tb = String(b.visivel ?? '').replace(/\s+/g, ' ').trim();
    if (a.tag !== 'img' && !ESTRUTURA.has(a.tag) && ta && tb && norm(ta) !== norm(tb)) itens.push(`texto "${ta.slice(0, 40)}" contra "${tb.slice(0, 40)}"`);
    const [ax, ay, aw, ah] = a.rect; const [bx, by, bw, bh] = b.rect;
    const caixa = [['x', ax, bx], ['y', ay, by], ['largura', aw, bw], ['altura', ah, bh]].filter(([, p, q]) => Math.abs(p - q) > lim.caixaPx);
    if (caixa.length) itens.push(`caixa ${caixa.map(([n, p, q]) => `${n} ${Math.round(p)} contra ${Math.round(q)}`).join(', ')}`);
    for (const p of PROPS) {
      if (a.estilo?.[p] === undefined && b.estilo?.[p] === undefined) continue;
      const d = difDeProp(p, a.estilo?.[p], b.estilo?.[p], lim);
      if (d) itens.push(d);
    }
    const textoMudou = itens.length && itens[0].startsWith('texto ');
    if (itens.length) diferencas.push({ chave: a.chave, rotulo: rotulo(a), itens, y: ay, invisivel: Boolean(temPixel && !textoMudou && !temPixel(a.rect) && !temPixel(b.rect)) });
  }
  return { pares, faltando, diferencas };
}

/** Como o elemento aparece no laudo: tag e começo do texto, ou o nome da imagem. */
export function rotulo(e) {
  if (e.tag === 'img') return `img "${nomeDaImagem(e.src)}"`;
  const t = String(e.texto || '').replace(/\s+/g, ' ').trim();
  return t ? `${e.tag} "${t.slice(0, 40)}${t.length > 40 ? '...' : ''}"` : `${e.tag} (${e.chave?.split('@')[1] || 1}º)`;
}

/**
 * Células diferentes (grade de `celula` px) viram retângulos: células vizinhas (8 lados) se juntam numa caixa só.
 * `mascara` é um Uint8Array (ou array) de colunas x linhas da grade, 1 = a célula tem pixel diferente.
 * Devolve [{x, y, largura, altura, celulas}] em px, maiores primeiro.
 */
export function retangulos(mascara, colunas, linhas, celula) {
  const visto = new Uint8Array(colunas * linhas);
  const caixas = [];
  for (let i = 0; i < colunas * linhas; i++) {
    if (!mascara[i] || visto[i]) continue;
    let x0 = Infinity, y0 = Infinity, x1 = -1, y1 = -1, n = 0;
    const pilha = [i]; visto[i] = 1;
    while (pilha.length) {
      const k = pilha.pop(); const cx = k % colunas; const cy = (k - cx) / colunas;
      n++; x0 = Math.min(x0, cx); y0 = Math.min(y0, cy); x1 = Math.max(x1, cx); y1 = Math.max(y1, cy);
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const nx = cx + dx, ny = cy + dy;
        if (nx < 0 || ny < 0 || nx >= colunas || ny >= linhas) continue;
        const j = ny * colunas + nx;
        if (mascara[j] && !visto[j]) { visto[j] = 1; pilha.push(j); }
      }
    }
    caixas.push({ x: x0 * celula, y: y0 * celula, largura: (x1 - x0 + 1) * celula, altura: (y1 - y0 + 1) * celula, celulas: n });
  }
  return caixas.sort((a, b) => b.largura * b.altura - a.largura * a.altura);
}

/** O menor elemento da original que contém o centro do retângulo (para o laudo dizer ONDE fica a diferença). */
export function dentroDe(caixa, elementos) {
  const cx = caixa.x + caixa.largura / 2, cy = caixa.y + caixa.altura / 2;
  let melhor = null;
  for (const e of elementos) {
    const [x, y, w, h] = e.rect;
    if (cx >= x && cx <= x + w && cy >= y && cy <= y + h && (!melhor || w * h < melhor.rect[2] * melhor.rect[3])) melhor = e;
  }
  return melhor;
}

/** Veredito de uma largura. `m` = { pixelsPct, alturaOriginal, alturaClone, comparacao }. Devolve [falha em texto]. */
export function falhasDaLargura(nome, m, lim = LIMITES) {
  const f = [];
  if (Math.abs(m.alturaOriginal - m.alturaClone) > lim.alturaPx) f.push(`${nome}: altura da página ${m.alturaOriginal} px na original contra ${m.alturaClone} px no clone`);
  if (m.pixelsPct > lim.pixelsPct) f.push(`${nome}: ${fmtPct(m.pixelsPct)} dos pixels diferentes (limite ${fmtPct(lim.pixelsPct)}); os retângulos abaixo dizem onde`);
  if (m.comparacao.faltando.length > lim.faltando) f.push(`${nome}: ${m.comparacao.faltando.length} elemento(s) da original sem par no clone: ${m.comparacao.faltando.slice(0, 6).map((k) => k.replace(/@1$/, '')).join('; ')}`);
  const vistas = m.comparacao.diferencas.filter((d) => !d.invisivel);
  if (vistas.length > lim.elementosComDiferenca) f.push(`${nome}: ${vistas.length} elemento(s) com caixa, texto ou estilo diferente da original, com pixel diferente na caixa: ${vistas.slice(0, 4).map((d) => d.rotulo).join('; ')}`);
  return f;
}

export const fmtPct = (v) => `${(Math.round(v * 1000) / 1000).toString().replace('.', ',')}%`;
