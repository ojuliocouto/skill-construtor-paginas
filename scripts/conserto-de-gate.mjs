/**
 * "Conserto:" de cada gate que reprova: UMA linha que diz o que mudar, no fim do laudo do gate no relatório do `rodar-gates.mjs`.
 *
 * Por que existe. O laudo diz O QUE está errado; a volta de correção custa porque quem corrige ainda tem que descobrir O QUE MUDAR.
 * Medido em 3 rodadas de gate com conserto entre elas: movimento e responsivo são 84% do tempo de uma rodada, e cada rodada a mais
 * é uma rodada inteira. Aqui cada reprovação ganha a linha.
 *
 * Como funciona. A tabela está AQUI, não nos gates: nenhum gate muda de comportamento nem de mensagem. Cada gate tem uma lista de
 * [padrão da mensagem, o que mudar]; o laudo é lido de cima para baixo, cada padrão que casa entra uma vez (a mesma falha repetida
 * 12 vezes não repete o conserto) e as frases saem juntas numa linha só. Sem padrão que case, vale o conserto padrão do gate.
 * Queda do servidor (saída 3), estouro de tempo (124) e gate que não executou (126) têm conserto próprio, antes de qualquer padrão.
 */

const LIMITE = 420;

/** [padrão, o que mudar]. A ordem é a de prioridade quando o laudo traz vários tipos de falha. */
const POR_GATE = {
  movimento: [
    [/rodaram com a seção fora da tela/, 'revele cada seção só quando ela entra na tela (IntersectionObserver), sem setTimeout que revela tudo e sem animation-delay (use quadro-chave parado no começo)'],
    [/seções abaixo da dobra animam ao chegar/, 'faça pelo menos 2 seções abaixo da dobra animarem ao chegar (a classe de entrada vem do observador quando a seção entra na tela)'],
    [/chegam parados/, 'observe cada item (o filho) e não o grupo, para ele entrar animando quando aparece a 300 px/s'],
    [/script bloqueado|script que demora 7 s|rede de segurança/, 'ponha a rede de segurança da receita-base no <head>: a classe js posta por script em linha e retirada por temporizador de 5 s se o script principal não confirmar'],
    [/parada no topo/, 'o que já está na primeira tela entra na carga: não espere o observador para o que está à vista'],
    [/depois de um salto/, 'aplique o estado final ao que já passou (receita-base, jaPassou) ao rolar ou saltar por âncora'],
    [/no fim da visita|continuam invisíveis/, 'tire o clip-path ou a opacidade 0 do próprio alvo do observador: o recorte de entrada vai no filho e o observador olha o pai'],
    [/scroll-behavior: smooth/, 'ponha scroll-behavior: auto dentro de @media (prefers-reduced-motion: reduce)'],
    [/prefers-reduced-motion: reduce[^\n]*em curso|em curso com prefers-reduced-motion/, 'dentro de @media (prefers-reduced-motion: reduce) ponha animation: none e transition: none nos elementos citados'],
  ],
  responsivo: [
    [/overflow horizontal/, 'ache o elemento mais largo que a tela (largura fixa, imagem sem max-width) e prenda-o a 100% da largura'],
    [/abaixo da dobra/, 'suba o botão do herói: menos texto ou foto menor no celular, para o CTA terminar dentro da primeira tela'],
    [/CTA camuflado/, 'dê ao botão contraste de pelo menos 3:1 com o fundo'],
    [/botao em mais de uma linha/, 'encurte o rótulo do botão ou reduza o padding e a fonte até caber em uma linha'],
    [/sem nenhum botao visivel/, 'repita o botão a cada 2 telas ou use a barra fixa do celular'],
    [/espaço fixo de/, 'reduza o cabeçalho e a barra fixos a no máximo 15% da tela no celular (some a barra quando há botão da página à vista)'],
    [/botões de ação na mesma tela/, 'deixe 1 botão de ação por tela no celular: a barra fixa some quando há botão da página à vista'],
    [/botão coberto ou encostado/, 'afaste o botão da barra fixa (mais de 8 px) ou ponha padding-bottom na seção'],
    [/foto do herói ocupa/, 'dê à foto do herói pelo menos a fração mínima da altura da primeira tela no celular, antes do texto longo'],
    [/alvo\(s\) de toque/, 'aumente a área de toque dos alvos citados para 44 px (padding ou min-height)'],
    [/texto de corpo < 14px/, 'suba o corpo de texto citado para pelo menos 14 px'],
    [/texto cortado/, 'tire a altura fixa ou o overflow hidden da caixa citada, para o texto caber inteiro'],
    [/elemento maior que o container/, 'limite o elemento citado à largura da caixa (max-width: 100%, min-width: 0)'],
  ],
  oclusao: [
    [/COBERTO/, 'mude o z-index ou a posição da camada que cobre o texto, ou tire a camada'],
    [/clip-path|recortada por/, 'tire o clip-path ou o clip do elemento citado, ou ponha o recorte no filho e não no texto'],
    [/CORTADO/, 'dê altura automática ou mais espaço à caixa do texto citado (sem altura fixa nem overflow hidden)'],
  ],
  simetria: [
    [/terminam com \d+ px de diferença/, 'prenda o último bloco da coluna curta ao rodapé (margin-top: auto com o grid esticado) ou estique o bloco mais curto até a mesma base; se a assimetria é pedida no plano, declare data-assimetrico="motivo"'],
    [/escada:|grade irregular|topos diferentes|alturas diferentes/, 'alinhe os itens paralelos na mesma linha, com a mesma altura de caixa (grid com itens esticados)'],
    [/texto em [\d, ]+ linhas|faixa de linhas/, 'deixe o texto das caixas na mesma faixa de linhas (no máximo 1 de diferença): encurte ou iguale as cópias'],
    [/passos lado a lado sem caixa|passos sem caixa/, 'ponha cada passo numa caixa, como os cartões vizinhos'],
    [/vazios entre dois blocos|conteúdo flutuando/, 'tire o buraco interno do card: prenda o último bloco ao rodapé (margin-top: auto) ou ajuste os espaços'],
    [/de diferença no topo/, 'alinhe os títulos dos cards vizinhos no mesmo topo (mesma altura de linha e de padding)'],
    [/lista vertical ao lado do título|à esquerda \+/, 'ponha o título acima da lista ou equilibre as duas colunas'],
  ],
  composicao: [
    [/mesmo esqueleto/, 'dê a cada seção seguida um tratamento próprio (layout diferente do vizinho); no máximo 2 com o mesmo esqueleto'],
    [/desenho sem data-desenho/, 'declare data-desenho="o que ele desenha" ligado ao conteúdo da seção'],
    [/ícone genérico de biblioteca|desenhe o assunto/, 'desenhe o assunto da seção no lugar do ícone de biblioteca'],
    [/desenho repetido/, 'use um desenho por assunto, sem repetir o mesmo traçado (ou declare data-icone-repetido-ok com o motivo, se for o logo)'],
    [/ninguém do público lê um retângulo|wireframe/, 'desenhe a cena (pessoa, aparelho com volume, gesto) no lugar do retângulo'],
    [/passa do último marco|termine a linha/, 'termine a linha do tempo no centro do último marco'],
    [/nenhuma figura humana/, 'ponha uma pessoa na primeira tela: foto real com autorização ou ilustração própria com data-figura="pessoa"'],
    [/3:1|traço fino|destaque/, 'suba o contraste do destaque ou do traço fino para pelo menos 3:1 contra o fundo'],
  ],
};

/** Conserto padrão: vale quando nenhum padrão casa, e para os gates fora da tabela acima. */
const PADRAO = {
  movimento: 'leia as linhas FALHA acima, cada uma diz a seção e o que mudar; as receitas estão em references/receitas-de-movimento.md',
  responsivo: 'leia as linhas FALHA acima, cada uma diz a tela e o elemento; corrija todas e rode só este gate com --so responsivo',
  oclusao: 'leia a lista COBERTO e CORTADO acima, cada linha diz o texto e quem o cobre ou corta; corrija a camada ou a caixa',
  simetria: 'leia as linhas FALHA acima, cada uma nomeia os dois blocos que não combinam; iguale a altura, a base ou o número de linhas',
  composicao: 'leia as linhas FALHA acima, cada uma diz a seção ou o desenho; mude o tratamento da seção citada',
  texto: 'leia as linhas FALHA acima, cada uma cita o texto e a largura de tela; reescreva ou ajuste a largura para não deixar palavra sozinha na última linha',
  ritmo: 'dê a uma das duas seções vizinhas citadas outra estrutura (posição do título e tipo de corpo diferentes) e mantenha no máximo 1 título centralizado com cartões',
  imagens: 'leia as linhas FALHA acima: troque a foto repetida ou borrada, ou complete a licença e o crédito em imagens/LICENCAS.md e no HTML',
  'sem-kicker': 'tire o rótulo em caixa alta acima do título, a numeração 01/02/03 ou o número gigante citado; diga a ideia no próprio título',
  'classes-mortas': 'apague a classe citada do HTML ou escreva a regra dela no CSS, e recompile o CSS',
  verdade: 'ligue a promessa citada a uma linha do briefing em evidencias/sustentacao.md, ou tire a promessa da página',
  publicacao: 'rode montar-dist.py de novo e tire da dist o arquivo que a página não usa',
  rastreamento: 'ponha na dist o pixel e os eventos que o PLANO.md pediu (references/rastreamento.md), ou declare "Pixel pedido: nenhum"',
  plano: 'complete o PLANO.md no que o gate cita (seção, prévia, aprovação ou tipo de animação) e refaça a aprovação',
  referencias: 'faltam referências lidas: abra cada print, escreva faz_bem, princípio e lido: true no manifesto, ou capture mais endereços',
  animacao: 'a seção citada muda menos de 2% dos pixels: dê a ela uma animação visível, ou ajuste o tipo da animação no PLANO.md',
  video: 'confira o vídeo da página no gate-video (formato, tamanho, duração) e regrave o que o laudo cita',
  sobreposicao: 'o elemento fixo cobre o bloco largo citado: mude o z-index, a posição ou a largura de um dos dois',
};

const CONSERTO_GENERICO = 'leia o laudo acima, corrija o que ele cita e rode só este gate com --so <nome>';

function limpar(s) { return String(s).replace(/\s+/g, ' ').trim(); }

/**
 * A linha "Conserto: ..." de um gate que reprovou.
 * @param {string} nome    nome do gate no catálogo (movimento, responsivo, ...)
 * @param {string} laudo   texto que o gate imprimiu
 * @param {number} codigo  saída do gate
 */
export function consertoDoGate(nome, laudo, codigo) {
  const texto = String(laudo || '');
  let frase = null;
  if (codigo === 3 || /servidor fora do ar em|net::ERR_CONNECTION_REFUSED/.test(texto)) {
    frase = 'o servidor da página caiu e o gate não opinou: suba o servidor de novo (servidor-gzip.py imprime a URL) e repita só este gate';
  } else if (codigo === 124 || /Estourou o tempo máximo/.test(texto)) {
    frase = `o gate estourou o tempo: rode --so ${nome} --paralelo 1 para ver se a página trava ou se foi carga da máquina, e só então suba --tempo-max`;
  } else if (codigo === 126 || /não consegui iniciar o gate|gate não executou/.test(texto)) {
    frase = 'o gate nem executou: rode checar-ferramentas.py (Playwright, Python, Pillow) e conserte a instalação antes de repetir';
  } else {
    const achadas = [];
    for (const [padrao, mudar] of POR_GATE[nome] || []) {
      if (padrao.test(texto) && !achadas.includes(mudar)) achadas.push(mudar);
    }
    frase = achadas.length ? achadas.slice(0, 3).join('; ') : (PADRAO[nome] || CONSERTO_GENERICO);
  }
  let linha = `Conserto: ${limpar(frase)}`;
  if (linha.length > LIMITE) linha = `${linha.slice(0, LIMITE - 3).replace(/[;, ]+\S*$/, '')}...`;
  return linha;
}
