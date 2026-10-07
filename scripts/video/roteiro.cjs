/**
 * Parte PURA do gravador de vídeo de prova: valida o roteiro, monta os passos e dá nome aos arquivos.
 * Sem navegador, sem disco: o que for testável sem Playwright mora aqui (test-roteiro-de-video.cjs).
 *
 * Roteiro = JSON simples: { "nome": "...", "passos": [ { "acao": "abrir" }, ... ] }
 *
 *   abrir                         abre a URL da página (tem que ser o primeiro passo)
 *   esperar          ms           pausa (0 a 10000)
 *   esperar_seletor  seletor      espera o elemento aparecer (até 20 s)
 *   clicar           seletor      clica (o mouse se move até lá antes)
 *   mover_mouse      seletor | x,y  leva o mouse até o elemento ou ao ponto
 *   rolar            y            rola a página até a posição y (pixels)
 *   rolar_pagina     passo, espera_ms, max_passos, prints   rola do topo ao fim em ritmo de leitura: a cada
 *                    passo (fração da altura da janela, 0,2 a 1, padrão 0,5) rola e espera espera_ms (300 a 3000,
 *                    padrão 1500), no máximo max_passos vezes (1 a 45, padrão 45); tira `prints` quadros espalhados
 *                    (0 a 8). Não chegar ao fim da página dentro de max_passos é FALHA, nunca vídeo pela metade.
 *   escolher         seletor + indice | valor   escolhe uma opção de <select> (o filtro)
 *   print            nome         tira um quadro (PNG) no meio da gravação: vira a prancha de quadros
 *
 * "duracao_minima_s" (opcional, 10 a 15): o vídeo só fecha depois desse tempo, contado desde o começo da gravação.
 *  Garante o piso quando a página carrega depressa; o teto depende da rede, e o gravador avisa se passar.
 *
 * Qualquer passo aceita "opcional": true. Se o elemento não existir, o passo é pulado e avisado
 * (assim o mesmo roteiro serve a painéis de domínios diferentes, com ou sem abas).
 */
const path = require('node:path');

const ACOES = ['abrir', 'esperar', 'esperar_seletor', 'clicar', 'mover_mouse', 'rolar', 'rolar_pagina', 'escolher', 'print'];
const MIN_PRINTS = 6;
// Faixa desta skill: 10 a 90 s (o criador-dash usa 10 a 15). Página de venda é longa: rolar do topo ao fim
// em ritmo de leitura leva de 30 a 70 s, e um vídeo de 15 s só mostraria o começo.
const FAIXA_S = { min: 10, max: 90 };
const PISO_S = { min: 10, max: 15 }; // faixa aceita em duracao_minima_s
const ROLAR_PAGINA_PADRAO = Object.freeze({ passo: 0.5, espera_ms: 1500, max_passos: 45, prints: 0 });
const ESPERA_MAX_MS = 10000;

// Custo médio de cada ação (ms) além das esperas explícitas: o mouse se move, a página responde.
const CUSTO_MS = { abrir: 2000, esperar: 0, esperar_seletor: 500, clicar: 500, mover_mouse: 500, rolar: 700, rolar_pagina: 0, escolher: 500, print: 300 };

const PERFIS = Object.freeze({
  desktop: Object.freeze({ viewport: Object.freeze({ width: 1440, height: 900 }), isMobile: false, hasTouch: false, deviceScaleFactor: 1 }),
  mobile: Object.freeze({ viewport: Object.freeze({ width: 390, height: 844 }), isMobile: true, hasTouch: true, deviceScaleFactor: 2 }),
});

const ehTexto = (v) => typeof v === 'string' && v.trim() !== '';
const ehNumero = (v) => typeof v === 'number' && Number.isFinite(v);
const configDeRolarPagina = (p) => ({ ...ROLAR_PAGINA_PADRAO, ...p });

function erroDoPasso(p, i) {
  const rotulo = `passo ${i + 1}`;
  if (!p || typeof p !== 'object' || Array.isArray(p)) return `${rotulo}: precisa ser um objeto com "acao"`;
  if (!ACOES.includes(p.acao)) return `${rotulo}: ação desconhecida "${p.acao}" (use: ${ACOES.join(', ')})`;
  switch (p.acao) {
    case 'esperar':
      if (!ehNumero(p.ms) || p.ms < 0 || p.ms > ESPERA_MAX_MS) return `${rotulo} (esperar): "ms" precisa ser um número de 0 a ${ESPERA_MAX_MS}`;
      break;
    case 'esperar_seletor': case 'clicar':
      if (!ehTexto(p.seletor)) return `${rotulo} (${p.acao}): falta "seletor"`;
      break;
    case 'mover_mouse':
      if (!ehTexto(p.seletor) && !(ehNumero(p.x) && ehNumero(p.y))) return `${rotulo} (mover_mouse): use "seletor" ou "x" e "y"`;
      break;
    case 'rolar':
      if (!ehNumero(p.y) || p.y < 0) return `${rotulo} (rolar): "y" precisa ser um número maior ou igual a 0`;
      break;
    case 'rolar_pagina': {
      const c = configDeRolarPagina(p);
      if (!(c.passo >= 0.2 && c.passo <= 1)) return `${rotulo} (rolar_pagina): "passo" precisa ser de 0,2 a 1 (fração da altura da janela)`;
      if (!(ehNumero(c.espera_ms) && c.espera_ms >= 300 && c.espera_ms <= 3000)) return `${rotulo} (rolar_pagina): "espera_ms" precisa ser de 300 a 3000`;
      if (!(Number.isInteger(c.max_passos) && c.max_passos >= 1 && c.max_passos <= 45)) return `${rotulo} (rolar_pagina): "max_passos" precisa ser um inteiro de 1 a 45`;
      if (!(Number.isInteger(c.prints) && c.prints >= 0 && c.prints <= 8)) return `${rotulo} (rolar_pagina): "prints" precisa ser um inteiro de 0 a 8`;
      break;
    }
    case 'escolher':
      if (!ehTexto(p.seletor)) return `${rotulo} (escolher): falta "seletor"`;
      if (!ehNumero(p.indice) && !ehTexto(p.valor)) return `${rotulo} (escolher): use "indice" ou "valor"`;
      break;
    case 'print':
      if (!ehTexto(p.nome)) return `${rotulo} (print): falta "nome" do quadro`;
      break;
    default: break;
  }
  return null;
}

/** Duração prevista do roteiro (ms): esperas explícitas mais o custo médio de cada ação (rolar_pagina fica de fora: depende da altura). */
function duracaoPrevistaMs(passos) {
  return (passos || []).reduce((soma, p) => soma + (p && p.acao === 'esperar' && ehNumero(p.ms) ? p.ms : 0) + (CUSTO_MS[p && p.acao] || 0), 0);
}

/** Pior caso de cada rolar_pagina (ms): max_passos vezes (espera + 300 ms da rolagem suave) mais 1,2 s no fim. */
function duracaoMaximaDaRolagemMs(passos) {
  return (passos || []).filter((p) => p && p.acao === 'rolar_pagina').reduce((s, p) => { const c = configDeRolarPagina(p); return s + c.max_passos * (c.espera_ms + 300) + 1200; }, 0);
}

/** @returns {{ok:boolean, erros:string[], avisos:string[]}} */
function validarRoteiro(r) {
  const erros = [];
  const avisos = [];
  if (!r || typeof r !== 'object' || !Array.isArray(r.passos) || r.passos.length === 0) {
    return { ok: false, erros: ['o roteiro precisa ter uma lista "passos" com pelo menos um passo'], avisos };
  }
  r.passos.forEach((p, i) => { const e = erroDoPasso(p, i); if (e) erros.push(e); });
  if (r.passos[0] && r.passos[0].acao !== 'abrir') erros.push('o primeiro passo precisa ser "abrir"');
  if (r.passos.slice(1).some((p) => p && p.acao === 'abrir')) avisos.push('há mais de um "abrir": o vídeo recarrega o painel');
  const prints = r.passos.reduce((n, p) => n + (p && p.acao === 'print' ? 1 : 0) + (p && p.acao === 'rolar_pagina' && ehNumero(p.prints) ? p.prints : 0), 0);
  if (prints < MIN_PRINTS) erros.push(`o roteiro precisa de no mínimo ${MIN_PRINTS} prints (tem ${prints}): quem revisa lê a prancha de quadros, não o vídeo`);
  if (r.duracao_minima_s !== undefined && !(ehNumero(r.duracao_minima_s) && r.duracao_minima_s >= PISO_S.min && r.duracao_minima_s <= PISO_S.max)) {
    erros.push(`"duracao_minima_s" precisa ser um número de ${PISO_S.min} a ${PISO_S.max} (o vídeo espera até esse tempo antes de fechar)`);
  }
  if (!erros.length) {
    const rola = r.passos.some((p) => p && p.acao === 'rolar_pagina');
    const s = duracaoPrevistaMs(r.passos) / 1000;
    const maxS = s + duracaoMaximaDaRolagemMs(r.passos) / 1000;
    // Sem rolar_pagina a duração é previsível e precisa cair na faixa; com ela, o fixo não pode passar do teto e o pior caso também não.
    if ((!rola && s < FAIXA_S.min) || maxS > FAIXA_S.max) erros.push(`duração prevista de ${(rola ? maxS : s).toFixed(1)} segundos fora da faixa de ${FAIXA_S.min} a ${FAIXA_S.max} segundos (ajuste as esperas e o ritmo de rolagem)`);
  }
  return { ok: erros.length === 0, erros, avisos };
}

/** Passos prontos pra executar: com ordem (1, 2, 3...), "opcional" explícito e uma cópia (o original não muda). */
function montarPassos(r) {
  return r.passos.map((p, i) => ({ ...p, ordem: i + 1, opcional: p.opcional === true }));
}

function nomeSeguro(texto) {
  const s = String(texto || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40);
  return s || 'quadro';
}
function conferirPerfil(perfil) {
  if (!PERFIS[perfil]) throw new Error(`perfil desconhecido: ${perfil} (use desktop ou mobile)`);
}
const nomeDoVideo = (perfil) => { conferirPerfil(perfil); return `video-${perfil}.webm`; };
const nomeDoPrint = (perfil, n, nome) => { conferirPerfil(perfil); return `${perfil}-${String(n).padStart(2, '0')}-${nomeSeguro(nome)}.png`; };
const caminhoDeSaida = (pasta, arquivo) => path.join(pasta, arquivo);

module.exports = { ACOES, MIN_PRINTS, FAIXA_S, PISO_S, PERFIS, ROLAR_PAGINA_PADRAO, configDeRolarPagina, validarRoteiro, duracaoPrevistaMs, duracaoMaximaDaRolagemMs, montarPassos, nomeDoVideo, nomeDoPrint, caminhoDeSaida };
