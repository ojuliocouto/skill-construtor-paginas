/**
 * Controles da 3.5.12 para o gate-ritmo.mjs, em páginas locais controladas. Dois defeitos achados
 * na página Torra Clara depois da medição de alinhamento da 3.5.10 (P18):
 *
 *  1. FALSO "cartões" (o gate reprovava "Monte o seu plano" e "Dúvidas", vizinhas):
 *     - um configurador (coluna com 4 ou mais controles: radios, botões, campos) ao lado de um
 *       resumo (o rótulo do pedido) não é "cartões iguais": é um configurador;
 *     - duas colunas de perguntas (`details`) ou de itens (`li`) não são cartões: são lista.
 *     O que continua reprovando: duas seções vizinhas de cartões de verdade (mesmo com 1 botão
 *     ou 1 campo em cada cartão), dois configuradores vizinhos, duas listas em colunas vizinhas.
 *  2. Título curto centralizado com cartões a menos de 40 px abaixo era tratado como "título ao
 *     lado do conteúdo" (o 3º cartão fica à direita do título curto e começa logo abaixo dele).
 *     "Ao lado" exige sobreposição vertical de verdade; o título que está de lado de verdade
 *     (coluna esquerda, conteúdo à direita na mesma altura) continua "lado".
 *
 * Um navegador por vez (a máquina do usuário trava com carga alta).
 *
 * node scripts/test-ritmo-3512.cjs                 todos os controles
 * GATES_FILTRO=ritmo-lado node scripts/test-ritmo-3512.cjs   só os que começam com o texto
 */
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'ritmo-3512-'));
const head = '<title>Página de controle</title><meta name="viewport" content="width=device-width,initial-scale=1">';
const estilo = '<style>body{margin:0;font:18px Arial;background:#fff;color:#111}section{padding:48px 32px;min-height:220px}h1,h2,h3{margin:0 0 16px}p{max-width:600px;line-height:1.6;margin:0 0 12px}ul{margin:0;padding:0;list-style:none}li{padding:10px 0}a,button{display:inline-block;padding:16px;background:#111;color:#fff;border:0;font:18px Arial}details{border-top:1px solid #111;padding:14px 0}</style>';

function pagina(nome, corpo) {
  const arq = path.join(pasta, nome + '.html');
  fs.writeFileSync(arq, '<!doctype html><html lang="pt-BR"><head>' + head + estilo + '</head><body>' + corpo + '</body></html>');
  return pathToFileURL(arq).href;
}

const hero = '<section><h1>Título da página</h1><p>Subtítulo curto.</p><a href="#c">Ver como funciona</a></section>';
const caixa = (t, extra = '') => `<article style="background:#eee;padding:16px"><h3>${t}</h3><p>Descrição curta do item paralelo.</p>${extra}</article>`;
const cartoes = (titulo, extra = '') => `<section><h2>${titulo}</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">${caixa('Um', extra)}${caixa('Dois', extra)}${caixa('Três', extra)}</div></section>`;
const lista = (titulo) => `<section><h2>${titulo}</h2><ul><li>Primeira frase da lista.</li><li>Segunda frase da lista.</li><li>Terceira frase da lista.</li><li>Quarta frase da lista.</li></ul></section>`;
const ladoLista = (titulo) => `<section><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px"><h2>${titulo}</h2><ul><li>Frase um da lista.</li><li>Frase dois da lista.</li><li>Frase três da lista.</li></ul></div></section>`;
const splitImg = (titulo) => `<section><h2>${titulo}</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:center"><div style="background:#ccc;height:260px" role="img" aria-label="Foto de controle"></div><p>Texto ao lado do quadro, para a seção ler como split.</p></div></section>`;

// Configurador: coluna de escolhas (fieldsets com radios) ao lado de um resumo (o rótulo), com
// larguras PARECIDAS (a coluna da esquerda tem 1,25x a da direita: 80%), como na Torra Clara.
const radios = (nome, n) => Array.from({ length: n }, (_, i) => `<label style="display:inline-block;margin:0 8px 8px 0;border:1px solid #111;padding:10px"><input type="radio" name="${nome}" value="${i}"${i === 0 ? ' checked' : ''}> Opção ${i + 1}</label>`).join('');
const configurador = (titulo, extra = '') => `<section><h2 ${extra}>${titulo}</h2><p>O preço é o mesmo em qualquer frequência.</p>`
  + `<div style="display:grid;grid-template-columns:1.25fr 1fr;gap:32px"><form><fieldset><legend>Tamanho</legend>${radios('t', 3)}</fieldset><fieldset><legend>Moagem</legend>${radios('m', 4)}</fieldset></form>`
  + `<div style="background:#e8dcc0;padding:24px"><h3>Resumo do pedido</h3><dl><dt>Peso</dt><dd>500 g</dd><dt>Envio</dt><dd>A cada 30 dias</dd><dt>Moagem</dt><dd>Em grãos</dd></dl><a href="#c">Assinar</a></div></div></section>`;
// Perguntas em duas colunas (details), cada coluna num contêiner.
const detalhe = (n) => `<details><summary>Pergunta ${n} sobre o plano?</summary><p>Resposta curta ${n}.</p></details>`;
const faqDuasColunas = (titulo) => `<section><h2>${titulo}</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:32px"><div>${[1, 2, 3, 4].map(detalhe).join('')}</div><div>${[5, 6, 7, 8].map(detalhe).join('')}</div></div></section>`;
// Itens em duas colunas (ul com li), cada coluna uma lista.
const listaDuasColunas = (titulo) => `<section><h2>${titulo}</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:32px"><ul><li>Primeiro item da lista.</li><li>Segundo item da lista.</li><li>Terceiro item da lista.</li></ul><ul><li>Quarto item da lista.</li><li>Quinto item da lista.</li><li>Sexto item da lista.</li></ul></div></section>`;
// Título curto, centralizado de verdade (caixa que se ajusta ao texto, no meio), com os 3 cartões
// 24 px abaixo: o 3º cartão fica à direita do título e começa menos de 40 px abaixo dele.
const centroCurto = (titulo) => `<section><h2 style="width:fit-content;margin:0 auto 24px;text-align:center">${titulo}</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">${caixa('Um')}${caixa('Dois')}${caixa('Três')}</div></section>`;
// Título numa coluna e cartões na outra, na mesma altura (o título está de lado de verdade).
const ladoDeVerdade = (titulo) => `<section><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px;align-items:start"><h2>${titulo}</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">${caixa('Um')}${caixa('Dois')}</div></div></section>`;
// Conteúdo à direita que começa logo ABAIXO da base do título (24 px): não é "ao lado".
const abaixoDoLado = (titulo) => `<section><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px;align-items:start"><h2 style="margin:0">${titulo}</h2><div style="margin-top:0"></div></div><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-top:24px"><div></div><div></div>${caixa('Um')}</div></section>`;

const P = {
  // 1. falso "cartões"
  configuradorEFaq: pagina('configurador-e-faq', hero + ladoLista('Situações') + cartoes('Três itens') + lista('Passos') + configurador('Monte o seu plano') + faqDuasColunas('Dúvidas antes de assinar') + splitImg('Fecho')),
  doisConfiguradores: pagina('dois-configuradores', hero + ladoLista('Situações') + configurador('Monte o plano') + configurador('Monte outro plano') + splitImg('Fecho')),
  duasFaqs: pagina('duas-faqs', hero + ladoLista('Situações') + faqDuasColunas('Dúvidas do plano') + faqDuasColunas('Dúvidas da entrega') + splitImg('Fecho')),
  duasListasEmColunas: pagina('duas-listas-em-colunas', hero + ladoLista('Situações') + listaDuasColunas('Benefícios') + listaDuasColunas('Detalhes') + splitImg('Fecho')),
  listaEmColunasEFaq: pagina('lista-em-colunas-e-faq', hero + ladoLista('Situações') + listaDuasColunas('Benefícios') + faqDuasColunas('Dúvidas') + splitImg('Fecho')),
  // cartões de verdade com 1 botão e 1 campo em cada cartão: continuam cartões
  cartoesComControlesVizinhos: pagina('cartoes-com-controles-vizinhos', hero + ladoLista('Situações')
    + cartoes('Planos', '<label><input type="radio" name="p"> Quero este</label><br><button type="button">Escolher</button>')
    + cartoes('Planos para empresas', '<label><input type="radio" name="q"> Quero este</label><br><button type="button">Escolher</button>') + splitImg('Fecho')),
  // cartões com lista de 3 itens dentro: continuam cartões (não são "lista")
  cartoesComListaDentro: pagina('cartoes-com-lista-dentro', hero + ladoLista('Situações')
    + cartoes('Planos', '<ul><li>Item um</li><li>Item dois</li><li>Item três</li></ul>')
    + cartoes('Mais planos', '<ul><li>Item um</li><li>Item dois</li><li>Item três</li></ul>') + splitImg('Fecho')),
  // 2. defeito vizinho
  centroCurtoEUmCartoes: pagina('centro-curto', hero + ladoLista('Situações') + centroCurto('Situações') + lista('Passos') + splitImg('Fecho')),
  doisCentrosCurtos: pagina('dois-centros-curtos', hero + ladoLista('Situações') + centroCurto('Situações') + lista('Passos') + centroCurto('Grupo ou particular') + splitImg('Fecho')),
  ladoDeVerdade: pagina('lado-de-verdade', hero + ladoDeVerdade('Quem somos') + lista('Passos') + splitImg('Fecho')),
  conteudoAbaixoNaoELado: pagina('conteudo-abaixo-nao-e-lado', hero + abaixoDoLado('Quem somos') + lista('Passos') + splitImg('Fecho')),
};

function rodar(nome, url, esperado, padroes = [], proibidos = []) {
  return new Promise((resolve) => {
    const filho = spawn(process.execPath, [path.join(__dirname, 'gate-ritmo.mjs'), '--url', url], { cwd: pasta });
    let saida = '';
    filho.stdout.on('data', (d) => { saida += d; });
    filho.stderr.on('data', (d) => { saida += d; });
    const teto = setTimeout(() => filho.kill('SIGTERM'), 180000);
    filho.on('close', (code) => {
      clearTimeout(teto);
      fs.writeFileSync(path.join(pasta, nome + '.log'), saida);
      const faltou = padroes.filter((p) => !p.test(saida));
      const apareceu = proibidos.filter((p) => p.test(saida));
      const passou = code === esperado && !faltou.length && !apareceu.length;
      console.log(`${passou ? 'OK' : 'FALHA'} ${nome}: exit=${code}, esperado=${esperado}`
        + (faltou.length ? `, mensagem AUSENTE ${faltou.join(' ')}` : '') + (apareceu.length ? `, mensagem PROIBIDA ${apareceu.join(' ')}` : ''));
      if (!passou) console.log(saida.split('\n').slice(0, 30).map((l) => '    ' + l).join('\n'));
      resolve(passou);
    });
  });
}

const casos = [
  // 1. o que a Torra Clara tem: configurador ao lado do resumo, depois perguntas em 2 colunas
  ['ritmo-configurador-ao-lado-do-resumo-nao-e-cartoes', P.configuradorEFaq, 0, [/PASSA/, /configurador/], [/"título à esquerda \+ cartões"/, /vizinhas iguais: [1-9]/]],
  ['ritmo-faq-em-duas-colunas-e-lista-nao-cartoes', P.configuradorEFaq, 0, [/título à esquerda \+ lista/]],
  // o que continua reprovando
  ['ritmo-dois-configuradores-vizinhos-reprovam', P.doisConfiguradores, 1, [/seções vizinhas com o mesmo esqueleto \("título à esquerda \+ configurador"\)/]],
  ['ritmo-duas-faqs-em-colunas-vizinhas-reprovam', P.duasFaqs, 1, [/seções vizinhas com o mesmo esqueleto \("título à esquerda \+ lista"\)/]],
  ['ritmo-duas-listas-em-colunas-vizinhas-reprovam', P.duasListasEmColunas, 1, [/seções vizinhas com o mesmo esqueleto \("título à esquerda \+ lista"\)/]],
  ['ritmo-lista-em-colunas-e-faq-vizinhas-reprovam', P.listaEmColunasEFaq, 1, [/seções vizinhas com o mesmo esqueleto/]],
  ['ritmo-cartoes-com-botao-e-campo-continuam-cartoes', P.cartoesComControlesVizinhos, 1, [/seções vizinhas com o mesmo esqueleto \("título à esquerda \+ cartões"\)/]],
  ['ritmo-cartoes-com-lista-dentro-continuam-cartoes', P.cartoesComListaDentro, 1, [/seções vizinhas com o mesmo esqueleto \("título à esquerda \+ cartões"\)/]],
  // 2. defeito vizinho
  ['ritmo-lado-titulo-curto-centralizado-nao-e-lado', P.centroCurtoEUmCartoes, 0, [/PASSA/, /título centralizado \+ cartões/], [/título ao lado do conteúdo \+ cartões/]],
  ['ritmo-lado-dois-titulos-curtos-centralizados-reprovam', P.doisCentrosCurtos, 1, [/2 seções no formato "título centralizado \+ cartões"/]],
  ['ritmo-lado-titulo-de-lado-de-verdade-continua-lado', P.ladoDeVerdade, 0, [/PASSA/, /título ao lado do conteúdo \+ cartões/, /há conteúdo ao lado do título/]],
  ['ritmo-lado-conteudo-abaixo-do-titulo-nao-e-lado', P.conteudoAbaixoNaoELado, 0, [/PASSA/], [/QUEM SOMOS.*título ao lado/i]],
];

(async () => {
  const filtro = process.env.GATES_FILTRO;
  const selecionados = casos.filter(([nome]) => !filtro || nome.startsWith(filtro));
  if (!selecionados.length) throw new Error('O filtro não selecionou nenhum controle.');
  const resultados = [];
  for (const [nome, url, esperado, padroes, proibidos] of selecionados) {
    resultados.push(await rodar(nome, url, esperado, padroes, proibidos));
  }
  console.log(`Evidências: ${pasta}`);
  console.log(`${resultados.filter(Boolean).length}/${resultados.length} controles passaram`);
  process.exitCode = resultados.every(Boolean) ? 0 : 1;
})();
