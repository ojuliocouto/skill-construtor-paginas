/**
 * Linha "Conserto:" de todo gate que reprova (pedido do coordenador, depois da medida de 3 rodadas de gate com conserto entre elas).
 *
 * O `rodar-gates.mjs` imprime o laudo inteiro de cada gate que reprovou. O laudo diz O QUE está errado; a volta de correção
 * custa porque quem corrige ainda tem que descobrir O QUE MUDAR. Agora cada reprovação termina com UMA linha "Conserto: ...".
 * O que fica provado aqui, sem navegador:
 *  1. todo gate do catálogo tem um conserto padrão, e os cinco que mais reprovam (movimento, responsivo, oclusão, simetria,
 *     composição) têm conserto específico por tipo de falha;
 *  2. a linha é UMA linha, começa com "Conserto: ", não tem travessão e cabe na tela;
 *  3. cada tipo de falha dos cinco gates cai no conserto certo (texto real das mensagens dos gates);
 *  4. queda do servidor, estouro de tempo e gate que não executou têm conserto próprio;
 *  5. o relatório do `rodar-gates.mjs` traz a linha no fim do bloco de cada gate que reprovou, e só nele.
 */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const AQUI = __dirname;
const testes = [];
const teste = (nome, fn) => testes.push([nome, fn]);
const modulo = () => import(pathToFileURL(path.join(AQUI, 'conserto-de-gate.mjs')).href);
const rodarGates = () => import(pathToFileURL(path.join(AQUI, 'rodar-gates.mjs')).href);

teste('todo gate do catálogo tem conserto padrão: uma linha, "Conserto: ", sem travessão, até 320 caracteres', async () => {
  const { consertoDoGate } = await modulo();
  const { CATALOGO } = await rodarGates();
  for (const g of CATALOGO) {
    const linha = consertoDoGate(g.nome, 'FALHA: coisa qualquer\n', 1);
    assert.ok(linha.startsWith('Conserto: '), `${g.nome}: ${linha}`);
    assert.ok(!linha.includes('\n'), `${g.nome}: mais de uma linha`);
    assert.ok(!/[\u2014\u2013]/.test(linha), `${g.nome}: travessão`);
    assert.ok(linha.length <= 320, `${g.nome}: ${linha.length} caracteres`);
  }
});

const CASOS = [
  // movimento (mensagens reais do gate-movimento.mjs)
  ['movimento', 'FALHA: desktop comum (1440x900): seção "Café": 3 animação(ões) rodaram com a seção fora da tela (aos 3.0 s, scrollY 0)', /IntersectionObserver|observador/i],
  ['movimento', 'FALHA: desktop comum (1440x900): só 0 de 3 seções abaixo da dobra animam ao chegar (mínimo 2): "A", "B" chegam paradas', /animem|animar|anim/i],
  ['movimento', 'FALHA: iphone padrao (390x844): 4 item(ns) chegam parados na tela a 300 px/s (terminaram de animar antes de entrar): div.item "Um" 120 ms antes', /cada item|filho/i],
  ['movimento', 'FALHA: desktop comum (1440x900): script bloqueado: 6 elemento(s) com texto ou imagem invisível(is) sem o script (h2.revela). Falta a rede de segurança', /rede de segurança/i],
  ['movimento', 'FALHA: iphone padrao (390x844): parada no topo por 4 s, 2 elemento(s) com texto da primeira tela continuam invisíveis', /primeira tela/i],
  ['movimento', 'FALHA: desktop comum (1440x900): depois de um salto até o fim (âncora, painel, voltar do WhatsApp), 3 elemento(s) que ficaram acima da tela continuam invisíveis', /estado final|já passou/i],
  ['movimento', 'FALHA: desktop comum (1440x900): no fim da visita, 1 elemento(s) com texto ou imagem continuam invisíveis (na tela por quase 1 s)', /clip-path|filho/i],
  ['movimento', 'FALHA: movimento reduzido: scroll-behavior: smooth em html com prefers-reduced-motion: reduce', /scroll-behavior: auto/],
  ['movimento', 'FALHA: movimento reduzido desktop comum (1440x900): 1 animação(ões) ou transição(ões) em curso com prefers-reduced-motion: reduce, acima de 200 ms', /animation: none/],
  // responsivo
  ['responsivo', 'FALHA: iphone padrao (390x844): overflow horizontal de 40px', /largura|max-width|100%/i],
  ['responsivo', 'FALHA: iphone padrao (390x844): CTA do heroi "Quero" abaixo da dobra (termina em 700px de 664px)', /suba|herói|primeira tela/i],
  ['responsivo', 'FALHA: iphone padrao (390x844): botao em mais de uma linha: a.botao', /uma linha|rótulo/i],
  ['responsivo', 'FALHA: iphone padrao (390x844): 3 alvo(s) de toque < 44px: a.menu', /44/],
  ['responsivo', 'FALHA: iphone padrao (390x844): texto de corpo < 14px: p.nota', /14/],
  ['responsivo', 'FALHA: iphone padrao (390x844): texto cortado pela caixa: h2', /altura|overflow/i],
  ['responsivo', 'FALHA: iphone padrao (390x844): espaço fixo de 200px (30.0% da tela, máximo 15%) em scrollY 0: somados: cabeçalho', /15%|fixo/i],
  ['responsivo', 'FALHA: iphone padrao (390x844): 2 botões de ação na mesma tela em scrollY 300 (A | B): no máximo 1 por tela', /1 botão|um botão/i],
  ['responsivo', 'FALHA: iphone padrao (390x844): 2.5 telas sem nenhum botao visivel a partir de y 100 (maximo 2): barra fixa no celular ou botao repetido', /botão/i],
  // oclusão
  ['oclusao', '[desktop] 12 blocos de texto analisados\n   COBERTO  "Quero" <- div.camada', /z-index|camada/i],
  ['oclusao', '[desktop] 12 blocos de texto analisados\n   CORTADO  "Título" (12px sobrando fora da caixa)', /altura|overflow|espaço/i],
  ['oclusao', '   CORTADO  "Linha" linha 2 de 3 recortada por clip-path em section.a', /clip-path/i],
  // simetria
  ['simetria', 'FALHA: desktop comum (1440x900): "A" (caixa div.a, termina em y 300) e "B" (caixa div.b, termina em y 420) terminam com 120 px de diferença', /margin-top: auto|mesma altura|esticar/i],
  ['simetria', 'FALHA: desktop comum (1440x900): escada: 3 caixas em 3 alturas e 3 colunas (x 10, 20, 30) a partir de "A"', /alinh|mesma linha|grade/i],
  ['simetria', 'FALHA: iphone padrao (390x844): texto em 5, 3 linhas nas caixas de "A" (máximo 1 linha de diferença)', /linhas|texto/i],
  ['simetria', 'FALHA: desktop comum (1440x900): 3 passos lado a lado sem caixa a partir de "Chame"', /caixa/i],
  ['simetria', 'FALHA: desktop comum (1440x900): "A" tem 80 px vazios entre dois blocos, o vizinho "B" tem 10 px (conteúdo flutuando no card)', /vazio|buraco|margin-top: auto/i],
  ['simetria', 'FALHA: desktop comum (1440x900): "T1" e "T2" com 12 px de diferença no topo (máximo 4)', /título|topo/i],
  // composição
  ['composicao', 'FALHA: mesmo esqueleto ("titulo+cartoes") em 4 seções seguidas: "A", "B", "C", "D" (máximo 2); dê a cada seção um tratamento próprio', /tratamento|esqueleto|layout/i],
  ['composicao', 'FALHA: desenho sem data-desenho (declare o que ele desenha, ligado ao conteúdo): svg', /data-desenho/],
  ['composicao', 'FALHA: ícone genérico de biblioteca: balão; desenhe o assunto da seção', /desenhe/i],
  ['composicao', 'FALHA: desenho repetido com o mesmo traçado "sinal de mais" 15 vezes', /repet|traçado|um desenho por/i],
  ['composicao', 'FALHA: desenho x: ninguém do público lê um retângulo; desenhe a cena (pessoa, aparelho com volume, gesto)', /cena|pessoa|wireframe/i],
  ['composicao', 'FALHA: desktop: nenhuma figura humana na primeira tela para um público de pessoas ("advogados")', /pessoa|figura/i],
  ['composicao', 'FALHA: destaque #aaa a 2.10:1 contra o fundo em "d" (mínimo 3:1 para o que carrega informação)', /3:1|contraste/i],
  // seo (3.8.0; mensagens reais do gate-seo.py)
  ['seo', 'REPROVA: HTML cru com 0 palavras visíveis, mínimo 300. SPA com #root vazio: buscador de IA não roda JavaScript [arquivo: dist/index.html]', /pré-renderize|pré-render/i],
  ['seo', 'REPROVA: robots.txt ausente [arquivo: dist/robots.txt]', /gerar-seo/],
  ['seo', 'REPROVA: 404.html ausente: no Cloudflare Pages é ele que faz a URL inexistente dar 404 [arquivo: dist/404.html]', /gerar-seo/],
  ['seo', 'REPROVA: meta robots "noindex, nofollow" bloqueia a indexação no domínio final [arquivo: dist/index.html]', /noindex/],
  ['seo', 'REPROVA: meta description ausente [arquivo: dist/index.html]', /description/],
  ['seo', 'REPROVA: canonical ausente [arquivo: dist/index.html]', /canonical/],
  ['seo', 'REPROVA: o mesmo data URI repetido 3 vezes (68,4 KB cada, 205,2 KB no total) [arquivo: dist/index.html]', /arquivo|data URI/i],
  ['seo', 'REPROVA: salto de nível h2→h4 em "Passo um" (sequência h1 h2 h4) [arquivo: dist/index.html]', /um nível por vez|nível/i],
  ['seo', 'REPROVA: JSON-LD ausente: sem dado estruturado [arquivo: dist/index.html]', /JSON-LD/],
  ['seo', 'REPROVA: Offer.price "9997" não aparece no texto visível [arquivo: dist/index.html]', /preço|price/i],
  ['seo', 'REPROVA: a página coleta dados (<form> ou campo) e não tem link de privacidade [arquivo: dist/index.html]', /privacidade/i],
];

for (const [gate, laudo, esperado] of CASOS) {
  teste(`conserto de ${gate} para: ${laudo.split('\n').pop().slice(0, 70)}`, async () => {
    const { consertoDoGate } = await modulo();
    const linha = consertoDoGate(gate, `\n${laudo}\n`, 1);
    assert.match(linha, esperado, linha);
    assert.ok(linha.startsWith('Conserto: ') && !linha.includes('\n'));
    const padrao = consertoDoGate(gate, 'FALHA: coisa que nenhum padrão conhece\n', 1);
    assert.notEqual(linha, padrao, 'caiu no conserto padrão em vez do específico');
  });
}

teste('seo: a linha de contagem de palavras (que aparece em todo laudo) não dispara o conserto de pré-render, só a reprovação dela', async () => {
  const { consertoDoGate } = await modulo();
  const so404 = consertoDoGate('seo', '  index.html: 386 palavras no HTML cru\nREPROVA: robots.txt ausente [arquivo: dist/robots.txt]\n', 1);
  assert.doesNotMatch(so404, /pré-render/i, so404);
  assert.match(so404, /gerar-seo/);
  const spa = consertoDoGate('seo', '  index.html: 0 palavras no HTML cru\nREPROVA: HTML cru com 0 palavras visíveis, mínimo 300. SPA com #root vazio [arquivo: dist/index.html]\n', 1);
  assert.match(spa, /pré-render/i, spa);
});

teste('duas falhas de tipos diferentes no mesmo laudo: uma linha só, com os dois consertos', async () => {
  const { consertoDoGate } = await modulo();
  const linha = consertoDoGate('responsivo', 'FALHA: x (390x844): overflow horizontal de 40px\nFALHA: x (390x844): 3 alvo(s) de toque < 44px: a\n', 1);
  assert.ok(!linha.includes('\n'));
  assert.match(linha, /44/);
  assert.match(linha, /largura|max-width|100%/i);
  assert.ok(linha.length <= 420, String(linha.length));
});

teste('a mesma falha repetida 12 vezes não repete o conserto', async () => {
  const { consertoDoGate } = await modulo();
  const um = consertoDoGate('responsivo', 'FALHA: a: 3 alvo(s) de toque < 44px: x\n', 1);
  const doze = consertoDoGate('responsivo', 'FALHA: a: 3 alvo(s) de toque < 44px: x\n'.repeat(12), 1);
  assert.equal(doze, um);
});

teste('queda do servidor, estouro de tempo e gate que não executou têm conserto próprio', async () => {
  const { consertoDoGate } = await modulo();
  assert.match(consertoDoGate('texto', 'servidor fora do ar em http://127.0.0.1:1/: nada ouve nessa porta', 3), /servidor/i);
  assert.match(consertoDoGate('movimento', 'Estourou o tempo máximo de 900 s e foi interrompido (conta como reprovado).', 124), /--so movimento --paralelo 1/);
  assert.match(consertoDoGate('ritmo', 'não consegui iniciar o gate: spawn ENOENT', 126), /checar-ferramentas/);
  assert.match(consertoDoGate('ritmo', 'gate não executou: x', 126), /checar-ferramentas/);
});

teste('gate desconhecido ainda recebe uma linha (nunca fica sem)', async () => {
  const { consertoDoGate } = await modulo();
  const linha = consertoDoGate('gate-que-nao-existe', 'qualquer coisa', 1);
  assert.ok(linha.startsWith('Conserto: ') && !linha.includes('\n'));
});

// ---- o relatório do rodar-gates ----
function rodar(args) {
  const r = spawnSync(process.execPath, [path.join(AQUI, 'rodar-gates.mjs'), ...args], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' }, windowsHide: true, timeout: 120000 });
  return { codigo: r.status, saida: `${r.stdout || ''}${r.stderr || ''}` };
}

teste('o relatório traz UMA linha "Conserto:" no fim do bloco de cada gate que reprovou, e nenhuma para quem passou', async () => {
  const { CATALOGO } = await rodarGates();
  const falsos = fs.mkdtempSync(path.join(os.tmpdir(), 'cons çá '));
  const proj = fs.mkdtempSync(path.join(os.tmpdir(), 'cons proj çá '));
  fs.mkdirSync(path.join(proj, 'dist'));
  fs.writeFileSync(path.join(proj, 'index.html'), '<html></html>');
  fs.writeFileSync(path.join(proj, 'PLANO.md'), 'Pixel pedido: nenhum\n');
  fs.writeFileSync(path.join(proj, 'dist', 'index.html'), '<html></html>');
  for (const g of CATALOGO) {
    const alvo = path.join(falsos, g.arquivo);
    const corpo = {
      simetria: 'FALHA: desktop comum (1440x900): 3 passos lado a lado sem caixa a partir de "Chame"',
      texto: 'viúva em "Título"',
    }[g.nome];
    if (g.arquivo.endsWith('.py')) fs.writeFileSync(alvo, 'import sys\nprint("ok")\n');
    else fs.writeFileSync(alvo, corpo ? `console.log(${JSON.stringify(corpo)});\nprocess.exit(1);\n` : 'console.log("ok");\n');
  }
  const r = rodar(['--projeto', proj, '--scripts-dir', falsos, '--url', 'http://127.0.0.1:1/', '--sem-montar', '--sem-registrar', '--so', 'simetria,texto,ritmo']);
  assert.equal(r.codigo, 1, r.saida);
  const linhas = r.saida.split('\n').filter((l) => l.startsWith('Conserto: '));
  assert.equal(linhas.length, 2, `esperava 2 linhas de conserto (simetria e texto), veio ${linhas.length}:\n${r.saida}`);
  const bloco = (nome) => r.saida.slice(r.saida.indexOf(`### ${nome}`));
  const blocoSimetria = bloco('simetria').split(/\n### /)[0];
  assert.match(blocoSimetria.trimEnd().split('\n').pop(), /^Conserto: .*caixa/, 'a linha de conserto é a ÚLTIMA do bloco');
  assert.ok(!bloco('ritmo').startsWith('### ritmo'), 'ritmo passou: não tem bloco de falha');
});

(async () => {
  let falhas = 0;
  for (const [nome, fn] of testes) {
    try { await fn(); console.log(`ok   ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome}\n  ${String(e && e.stack || e).split('\n').slice(0, 6).join('\n  ')}`); }
  }
  console.log(`\n${testes.length - falhas} de ${testes.length} testes passaram.`);
  process.exit(falhas ? 1 : 0);
})();
