/**
 * Controles da 3.5.13 para o gate-ritmo.mjs (auditoria da 3.5.11 e 3.5.12, achados 1, 3 e 6), em páginas
 * locais controladas. Cada controle reproduz o caso mínimo da auditoria, que na 3.5.12 PASSAVA e deve REPROVAR:
 *
 *  1. "configurador" decidido por contagem cega de controles. Agora só conta controle visível e interativo
 *     (8x8 px ou mais, sem display:none nem visibility:hidden; radio escondido conta pelo label visível),
 *     em pelo menos 2 grupos (fieldset, radiogroup, radios do mesmo name, campo), e só UMA coluna da fileira
 *     pode ter controles (a outra é o resumo).
 *  3. ul, ol e dl com caixa própria (fundo diferente do da seção, borda, sombra ou padding interno) são cartões.
 *  6. Enfeite à direita do título (aria-hidden, position absolute, sem texto nem mídia) não faz "título ao lado".
 *
 * Um navegador por vez. node scripts/test-ritmo-3513.cjs     (GATES_FILTRO=prefixo para um só)
 */
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'ritmo-3513-'));
const head = '<title>Página de controle</title><meta name="viewport" content="width=device-width,initial-scale=1">';
const estilo = '<style>body{margin:0;font:18px Arial;background:#fff;color:#111}section{padding:48px 32px;min-height:220px}h1,h2,h3{margin:0 0 16px}p{max-width:600px;line-height:1.6;margin:0 0 12px}ul{margin:0;padding:0;list-style:none}li{padding:10px 0}a,button{display:inline-block;padding:16px;background:#111;color:#fff;border:0;font:18px Arial}details{border-top:1px solid #111;padding:14px 0}</style>';
const FOTO = 'data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27400%27 height=%27260%27%3E%3Crect width=%27400%27 height=%27260%27 fill=%27%23ccc%27/%3E%3C/svg%3E';

function pagina(nome, corpo) {
  const arq = path.join(pasta, nome + '.html');
  fs.writeFileSync(arq, '<!doctype html><html lang="pt-BR"><head>' + head + estilo + '</head><body>' + corpo + '</body></html>');
  return pathToFileURL(arq).href;
}

const hero = '<section><h1>Título da página</h1><p>Subtítulo curto.</p><a href="#c">Ver como funciona</a></section>';
const caixa = (t, extra = '') => `<article style="background:#eee;padding:16px"><h3>${t}</h3><p>Descrição curta do item paralelo.</p>${extra}</article>`;
const lista = (titulo) => `<section><h2>${titulo}</h2><ul><li>Primeira frase da lista.</li><li>Segunda frase da lista.</li><li>Terceira frase da lista.</li><li>Quarta frase da lista.</li></ul></section>`;
const ladoLista = (titulo) => `<section><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px"><h2>${titulo}</h2><ul><li>Frase um da lista.</li><li>Frase dois da lista.</li><li>Frase três da lista.</li></ul></div></section>`;
const splitImg = (titulo) => `<section><h2>${titulo}</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:center"><img alt="Foto de controle" src="${FOTO}" style="width:100%;height:260px;background:#ccc"><p>Texto ao lado da foto, para a seção ler como split.</p></div></section>`;
const grade = (cols) => `<div style="display:grid;grid-template-columns:repeat(${cols.length},1fr);gap:16px">${cols.join('')}</div>`;
// Título centralizado de verdade (largura total, text-align center) com 3 cartões; `extra` entra só no 1º cartão.
const centroCartoes = (titulo, extra = '') => `<section><h2 style="text-align:center">${titulo}</h2>${grade([caixa('Um', extra), caixa('Dois'), caixa('Três')])}</section>`;

const chips = '<span><button type="button">A</button><button type="button">B</button><button type="button">C</button><button type="button">D</button></span>';
const escondidos = '<input type="checkbox" style="display:none"><input type="checkbox" style="display:none"><input type="checkbox" style="display:none"><input type="checkbox" style="display:none">';
const duasFieldsets = (n) => `<form><fieldset><legend>Tamanho</legend><label><input type="radio" name="t${n}"> Pequeno</label><label><input type="radio" name="t${n}"> Grande</label></fieldset><fieldset><legend>Moagem</legend><label><input type="radio" name="m${n}"> Fina</label><label><input type="radio" name="m${n}"> Grossa</label></fieldset></form>`;
const colunaComControles = (t, n) => `<div style="background:#eee;padding:16px"><h3>${t}</h3>${duasFieldsets(n)}</div>`;
const duasColunasComControles = (titulo, n) => `<section><h2 style="text-align:center">${titulo}</h2>${grade([colunaComControles('Plano A', n + 'a'), colunaComControles('Plano B', n + 'b')])}</section>`;

// Radios escondidos (sr-only) com label visível: o configurador da Torra Clara pode ser feito assim.
const radiosSrOnly = (nome, n) => Array.from({ length: n }, (_, i) => `<label style="display:inline-block;margin:0 8px 8px 0;border:1px solid #111;padding:10px"><input type="radio" name="${nome}" style="position:absolute;opacity:0;width:1px;height:1px"> Opção ${i + 1}</label>`).join('');
const configuradorSrOnly = (titulo) => `<section><h2>${titulo}</h2>`
  + `<div style="display:grid;grid-template-columns:1.25fr 1fr;gap:32px"><form><fieldset><legend>Tamanho</legend>${radiosSrOnly('t', 3)}</fieldset><fieldset><legend>Moagem</legend>${radiosSrOnly('m', 4)}</fieldset></form>`
  + `<div style="background:#e8dcc0;padding:24px"><h3>Resumo do pedido</h3><dl><dt>Peso</dt><dd>500 g</dd><dt>Envio</dt><dd>A cada 30 dias</dd></dl><a href="#c">Assinar</a></div></div></section>`;

// 3. listas com caixa própria
const itemCartao = '<li><h3>Título do item</h3></li><li><p>Texto do item.</p></li><li><a href="#c">Ver mais</a></li>';
const ulLeve = '<ul><li>Item um, linha leve.</li><li>Item dois, linha leve.</li><li>Item três, linha leve.</li></ul>';
const ulCartao = (estilo) => `<ul style="${estilo}">${itemCartao}</ul>`;
const dlCartao = (estilo) => `<dl style="margin:0;${estilo}"><dt>Origem</dt><dd>Minas</dd><dt>Altitude</dt><dd>1.200 m</dd><dt>Notas</dt><dd>Chocolate</dd></dl>`;
const centroColunas = (titulo, colunas) => `<section><h2 style="text-align:center">${titulo}</h2>${grade(colunas)}</section>`;

// 6. título curto centralizado (caixa que se ajusta ao texto) com um enfeite à direita, na altura dele
const centroComEnfeite = (titulo, enfeite) => `<section style="position:relative"><h2 style="width:fit-content;margin:0 auto 24px;text-align:center">${titulo}</h2>${enfeite}${grade([caixa('Um'), caixa('Dois'), caixa('Três')])}</section>`;
const seloAria = '<span aria-hidden="true" style="position:absolute;right:32px;top:48px;width:200px;height:90px;background:#c60;color:#fff">NOVO</span>';
const seloAbsoluto = '<div style="position:absolute;right:32px;top:48px;width:200px;height:90px;background:#c60;color:#fff;padding:8px">Edição limitada</div>';
const seloVazio = '<div style="position:absolute;right:32px;top:48px;width:200px;height:90px;background:#c60"></div>';

const P = {
  escondidosNaoFazemConfigurador: pagina('escondidos', hero + ladoLista('Situações') + centroCartoes('Primeiro bloco') + lista('Passos') + centroCartoes('Segundo bloco', escondidos) + splitImg('Fecho')),
  chipsNaoFazemConfigurador: pagina('chips', hero + ladoLista('Situações') + centroCartoes('Primeiro bloco') + lista('Passos') + centroCartoes('Segundo bloco', chips) + splitImg('Fecho')),
  duasColunasComControles: pagina('duas-colunas-controles', hero + ladoLista('Situações') + duasColunasComControles('Primeiro bloco', 'x') + lista('Passos') + duasColunasComControles('Segundo bloco', 'y') + splitImg('Fecho')),
  configuradorEscondidoComLabel: pagina('configurador-sr-only', hero + ladoLista('Situações') + configuradorSrOnly('Monte o plano') + lista('Passos') + splitImg('Fecho')),
  ulComoCartao: pagina('ul-cartao', hero + ladoLista('Situações')
    + centroColunas('Primeiro bloco', [ulCartao('background:#eee;padding:16px'), ulCartao('background:#eee;padding:16px'), ulCartao('background:#eee;padding:16px')]) + lista('Passos')
    + centroColunas('Segundo bloco', [ulCartao('border:1px solid #111;padding:16px'), ulCartao('border:1px solid #111;padding:16px'), ulCartao('border:1px solid #111;padding:16px')]) + splitImg('Fecho')),
  dlComoCartao: pagina('dl-cartao', hero + ladoLista('Situações')
    + centroColunas('Primeiro bloco', [dlCartao('box-shadow:0 2px 8px #0003;padding:16px'), dlCartao('box-shadow:0 2px 8px #0003;padding:16px'), dlCartao('box-shadow:0 2px 8px #0003;padding:16px')]) + lista('Passos')
    + centroColunas('Segundo bloco', [dlCartao('background:#eee;padding:16px'), dlCartao('background:#eee;padding:16px'), dlCartao('background:#eee;padding:16px')]) + splitImg('Fecho')),
  ulSemCaixaContinuaLista: pagina('ul-sem-caixa', hero + ladoLista('Situações')
    + centroColunas('Primeiro bloco', [ulLeve, ulLeve, ulLeve]) + lista('Passos')
    + centroColunas('Segundo bloco', [ulLeve, ulLeve, ulLeve]) + splitImg('Fecho')),
  ulComTituloNosItensSemCaixa: pagina('ul-com-titulo', hero + ladoLista('Situações')
    + centroColunas('Primeiro bloco', [ulCartao(''), ulCartao(''), ulCartao('')]) + lista('Passos')
    + centroColunas('Segundo bloco', [ulCartao(''), ulCartao(''), ulCartao('')]) + splitImg('Fecho')),
  enfeiteAria: pagina('enfeite-aria', hero + ladoLista('Situações') + centroComEnfeite('Primeiro bloco', seloAria) + lista('Passos') + centroComEnfeite('Segundo bloco', seloAria) + splitImg('Fecho')),
  enfeiteAbsoluto: pagina('enfeite-absoluto', hero + ladoLista('Situações') + centroComEnfeite('Primeiro bloco', seloAbsoluto) + lista('Passos') + centroComEnfeite('Segundo bloco', seloAbsoluto) + splitImg('Fecho')),
  enfeiteVazio: pagina('enfeite-vazio', hero + ladoLista('Situações') + centroComEnfeite('Primeiro bloco', seloVazio) + lista('Passos') + centroComEnfeite('Segundo bloco', seloVazio) + splitImg('Fecho')),
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

const DOIS_CENTROS = /2 seções no formato "título centralizado \+ cartões"/;
const casos = [
  // 1. configurador
  ['ritmo3513-quatro-inputs-invisiveis-nao-fazem-configurador', P.escondidosNaoFazemConfigurador, 1, [DOIS_CENTROS]],
  ['ritmo3513-quatro-chips-no-mesmo-grupo-continuam-cartoes', P.chipsNaoFazemConfigurador, 1, [DOIS_CENTROS]],
  ['ritmo3513-duas-colunas-com-controles-nao-sao-configurador', P.duasColunasComControles, 1, [DOIS_CENTROS]],
  ['ritmo3513-radios-escondidos-com-label-visivel-continuam-configurador', P.configuradorEscondidoComLabel, 0, [/PASSA/, /Monte o plano\s+título à esquerda \+ configurador/]],
  // 3. lista com caixa própria é cartão
  ['ritmo3513-ul-com-caixa-e-cartao', P.ulComoCartao, 1, [DOIS_CENTROS]],
  ['ritmo3513-dl-com-caixa-e-cartao', P.dlComoCartao, 1, [DOIS_CENTROS]],
  ['ritmo3513-ul-com-titulo-nos-itens-e-cartao-mesmo-sem-caixa', P.ulComTituloNosItensSemCaixa, 1, [DOIS_CENTROS]],
  ['ritmo3513-ul-sem-caixa-continua-lista', P.ulSemCaixaContinuaLista, 0, [/PASSA/, /Primeiro bloco\s+título centralizado \+ lista/]],
  // 6. enfeite ao lado do título
  ['ritmo3513-enfeite-aria-hidden-nao-e-lado', P.enfeiteAria, 1, [DOIS_CENTROS], [/título ao lado do conteúdo \+ cartões/]],
  ['ritmo3513-enfeite-absoluto-nao-e-lado', P.enfeiteAbsoluto, 1, [DOIS_CENTROS], [/título ao lado do conteúdo \+ cartões/]],
  ['ritmo3513-enfeite-vazio-nao-e-lado', P.enfeiteVazio, 1, [DOIS_CENTROS], [/título ao lado do conteúdo \+ cartões/]],
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
