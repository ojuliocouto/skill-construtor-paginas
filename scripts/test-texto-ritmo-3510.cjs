/**
 * Controles da 3.5.10 (frente B) para dois gates de tela, em páginas locais controladas:
 *
 *  - P9  gate-texto.mjs: e-mail e endereço de site no começo de um item não são "começa com
 *        minúscula"; frase minúscula de verdade continua reprovando.
 *  - P18 gate-ritmo.mjs: "título centralizado" se mede pelo alinhamento real (text-align calculado
 *        e posição da primeira linha), não pelo centro da caixa do texto; um h2 largo alinhado à
 *        esquerda não é centralizado; a saída diz como mediu.
 *
 * Um navegador por vez (a máquina do usuário trava com carga alta).
 *
 * node scripts/test-texto-ritmo-3510.cjs                       todos os controles
 * GATES_FILTRO=ritmo node scripts/test-texto-ritmo-3510.cjs    só os que começam com "ritmo"
 */
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'texto-ritmo-3510-'));
const head = '<title>Página de controle</title><meta name="viewport" content="width=device-width,initial-scale=1">';
const estilo = '<style>body{margin:0;font:18px Arial;background:#fff;color:#111}section{padding:48px 32px;min-height:220px}h1,h2,h3{margin:0 0 16px}p{max-width:600px;line-height:1.6;margin:0 0 12px}ul{margin:0;padding:0;list-style:none}li{padding:10px 0}a,button{display:inline-block;padding:16px;background:#111;color:#fff;border:0;font:18px Arial}</style>';

function pagina(nome, corpo) {
  const arq = path.join(pasta, nome + '.html');
  fs.writeFileSync(arq, '<!doctype html><html lang="pt-BR"><head>' + head + estilo + '</head><body>' + corpo + '</body></html>');
  return pathToFileURL(arq).href;
}

// ---- páginas do gate-texto (P9)
const curta = '<section><h1>Página curta</h1><p>Texto normal com uma <em style="color:#24525A">palavra</em> só.</p></section>';
const emailsOk = pagina('emails-ok', curta
  + '<section><h2>Fale com a gente</h2>'
  + '<p>oi@torraclara.com.br</p>'
  + '<p><a href="mailto:oi@torraclara.com.br">oi@torraclara.com.br</a></p>'
  + '<ul><li>www.torraclara.com.br/privacidade</li><li>https://wa.me/5531900000000</li><li>torraclara.com.br</li>'
  + '<li>instagram.com/torraclara</li><li>Atendimento: segunda a sexta.</li></ul></section>');
const emailEFraseMinuscula = pagina('email-e-frase-minuscula', curta
  + '<section><h2>Contato</h2><p>oi@torraclara.com.br</p><p>até 4 pessoas por turma</p></section>');
// Frases minúsculas de verdade que se parecem com endereço: não podem virar brecha.
const parecidoComEndereco = pagina('parecido-com-endereco', curta
  + '<section><h2>Notas</h2><p>ok.agora segue o texto</p></section>');
const arrobaNoMeio = pagina('arroba-no-meio', curta
  + '<section><h2>Notas</h2><p>fale em oi@torraclara.com.br quando quiser</p></section>');
const soFraseMinuscula = pagina('so-frase-minuscula', curta + '<section><h2>Notas</h2><p>até 4 pessoas por turma</p></section>');

// ---- páginas do gate-ritmo (P18)
const caixa = (t) => `<article style="background:#eee;padding:16px"><h3>${t}</h3><p>Descrição curta do item paralelo.</p></article>`;
const cartoes = (titulo, attrH2 = '') => `<section><h2 ${attrH2}>${titulo}</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">${caixa('Um')}${caixa('Dois')}${caixa('Três')}</div></section>`;
const lista = (titulo) => `<section><h2>${titulo}</h2><ul><li>Primeira frase da lista.</li><li>Segunda frase da lista.</li><li>Terceira frase da lista.</li><li>Quarta frase da lista.</li></ul></section>`;
const ladoLista = (titulo) => `<section><div style="display:grid;grid-template-columns:1fr 2fr;gap:32px"><h2>${titulo}</h2><ul><li>Frase um da lista.</li><li>Frase dois da lista.</li><li>Frase três da lista.</li></ul></div></section>`;
const hero = '<section><h1>Título da página</h1><p>Subtítulo curto.</p><a href="#c">Ver como funciona</a></section>';
// h2 largo, alinhado à esquerda, em 2 linhas que quase enchem a largura: o centro da caixa do
// texto cai no meio da seção, mas ele NÃO é centralizado.
const TITULO_LARGO = 'Café especial torrado na semana do envio, com o nome do produtor e a data da torra em cada pacote que chega até a sua casa';
const largoEsq = `style="font:44px/1.2 Arial;max-width:none"`;
const centroDeVerdade = 'style="text-align:center"';
// Caixa do título centralizada na página por flex, com o texto alinhado à esquerda dentro dela.
const centroPorCaixa = (titulo) => `<section><div style="display:flex;justify-content:center;margin-bottom:80px"><h2>${titulo}</h2></div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">${caixa('Um')}${caixa('Dois')}${caixa('Três')}</div></section>`;

const ritmoLargoEsqUmCentro = pagina('ritmo-largo-esq-um-centro',
  hero + cartoes(TITULO_LARGO, largoEsq) + lista('Passos') + cartoes('Grupo ou particular', centroDeVerdade) + ladoLista('Dúvidas'));
const ritmoDoisCentrosDeVerdade = pagina('ritmo-dois-centros-de-verdade',
  hero + cartoes('Situações', centroDeVerdade) + lista('Passos') + cartoes('Grupo ou particular', centroDeVerdade) + ladoLista('Dúvidas'));
const ritmoCentroPorCaixa = pagina('ritmo-centro-por-caixa',
  hero + centroPorCaixa('Situações') + lista('Passos') + cartoes('Grupo ou particular', centroDeVerdade) + ladoLista('Dúvidas'));
// text-align center, mas numa caixa estreita encostada à esquerda: o título não está centralizado
// na página (o gate antigo bastava ver text-align: center para chamar de centralizado).
const ritmoCentradoNoCantinho = pagina('ritmo-centrado-no-cantinho',
  hero + `<section><h2 style="text-align:center;width:300px;margin-bottom:80px">Situações</h2><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">${caixa('Um')}${caixa('Dois')}${caixa('Três')}</div></section>`
  + lista('Passos') + cartoes('Grupo ou particular', centroDeVerdade) + ladoLista('Dúvidas'));

function rodar(nome, gate, url, esperado, padroes = [], proibidos = []) {
  return new Promise((resolve) => {
    const filho = spawn(process.execPath, [path.join(__dirname, gate), '--url', url], { cwd: pasta });
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
  // P9: e-mail e endereço de site no começo do item não são "minúscula".
  ['texto-email-e-site-passam', 'gate-texto.mjs', emailsOk, 0, [/PASSA/]],
  // o caso ruim original continua reprovando, e só pelo que é frase de verdade
  ['texto-frase-minuscula-continua-reprovando', 'gate-texto.mjs', soFraseMinuscula, 1, [/min[uú]scula: <p> "at[eé] 4 pessoas/]],
  ['texto-email-nao-aparece-na-falha-da-frase', 'gate-texto.mjs', emailEFraseMinuscula, 1,
    [/min[uú]scula: <p> "at[eé] 4 pessoas/], [/oi@torraclara/]],
  ['texto-ponto-no-meio-nao-e-brecha', 'gate-texto.mjs', parecidoComEndereco, 1, [/min[uú]scula: <p> "ok\.agora/]],
  ['texto-frase-que-so-cita-email-no-meio-reprova', 'gate-texto.mjs', arrobaNoMeio, 1, [/min[uú]scula: <p> "fale em oi@/]],
  // P18: título centralizado se mede pelo alinhamento real.
  ['ritmo-h2-largo-a-esquerda-nao-e-centralizado', 'gate-ritmo.mjs', ritmoLargoEsqUmCentro, 0,
    [/PASSA/, /text-align/, /1ª linha/], [/2 seções no formato/]],
  ['ritmo-dois-centralizados-de-verdade-continua-reprovando', 'gate-ritmo.mjs', ritmoDoisCentrosDeVerdade, 1,
    [/2 seções no formato "título centralizado \+ cartões"/, /text-align center/]],
  ['ritmo-caixa-centralizada-por-flex-conta-como-centralizada', 'gate-ritmo.mjs', ritmoCentroPorCaixa, 1,
    [/2 seções no formato "título centralizado \+ cartões"/]],
  ['ritmo-text-align-center-na-caixa-do-canto-nao-e-da-pagina', 'gate-ritmo.mjs', ritmoCentradoNoCantinho, 0,
    [/PASSA/, /não está no centro da seção/], [/2 seções no formato/]],
];

(async () => {
  const filtro = process.env.GATES_FILTRO;
  const selecionados = casos.filter(([nome]) => !filtro || nome.startsWith(filtro));
  if (!selecionados.length) throw new Error('O filtro não selecionou nenhum controle.');
  const resultados = [];
  for (const [nome, gate, url, esperado, padroes, proibidos] of selecionados) {
    resultados.push(await rodar(nome, gate, url, esperado, padroes, proibidos));
  }
  console.log(`Evidências: ${pasta}`);
  console.log(`${resultados.filter(Boolean).length}/${resultados.length} controles passaram`);
  process.exitCode = resultados.every(Boolean) ? 0 : 1;
})();
