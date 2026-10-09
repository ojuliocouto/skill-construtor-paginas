#!/usr/bin/env node
/**
 * Roda a suíte de testes da skill num comando só, igual em Windows, macOS e Linux.
 *
 *   node scripts/rodar-testes.mjs                 # todos os testes
 *   node scripts/rodar-testes.mjs --so-portateis  # só os que não precisam de navegador nem de Pillow/numpy
 *   node scripts/rodar-testes.mjs --lista         # só mostra o que rodaria, sem rodar
 *   node scripts/rodar-testes.mjs --filtro gate   # só os arquivos cujo nome contém "gate"
 *
 * Como funciona: lê a pasta scripts/ com readdirSync (nada de curinga de shell: o Windows não
 * expande `test-*.py`), acha `test-*.py`, `test-*.cjs` e `*.test.mjs`, roda um por vez e mostra
 * a saída de cada um. Os .py rodam pelo py.mjs (acha o Python da máquina e liga UTF-8). Sai
 * com código diferente de zero se QUALQUER teste falhar.
 *
 * Teste que não tem como rodar nesta máquina (falta arquivo local, rede, tela) se declara pulado
 * imprimindo uma linha "PULADO: <motivo>" e saindo com 0. O resumo conta os pulados e mostra o
 * motivo de cada um: pular nunca é passar calado.
 *
 * CRITÉRIO DE "PORTÁTIL" (--so-portateis). Portátil é o teste que roda numa máquina que tem só
 * Node e Python, sem nenhuma instalação extra. Fica FORA do conjunto portátil quem precisa de:
 *   - navegador: carrega o Playwright com o Chromium (direto, ou chamando um script .mjs/.js de
 *     gate visual que abre a página);
 *   - biblioteca de imagem: Pillow ou numpy (gate de imagens, prancha de animação, fotos de teste).
 * A lista está em PRECISAM abaixo, com o motivo de cada arquivo, e foi conferida rodando os
 * testes numa máquina sem Playwright e sem Pillow: o que falhou lá está na lista, o que passou
 * é portátil. Teste novo entra como portátil por padrão; se precisar de navegador ou imagem, é
 * só pôr o nome aqui.
 */
import { spawnSync } from 'node:child_process';
import { readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = dirname(fileURLToPath(import.meta.url));
const TETO_POR_TESTE_MS = 20 * 60 * 1000;

// arquivo -> o que ele exige além de Node e Python.
const PRECISAM = {
  'test-capturar-referencias.cjs': 'navegador (captura páginas reais com o Playwright)',
  'test-medir-dobra.cjs': 'navegador (mede o aviso "imagem ilustrativa" na primeira tela)',
  'test-gerar-icones.cjs': 'navegador (gera os PNG dos ícones e confere as linhas de link impressas)',
  'test-og-image.cjs': 'navegador (gera e mede a og:image 1200x630)',
  'test-assinatura-demo.cjs': 'navegador (a receita da assinatura provada no demo, em escuro, claro e celular)',
  'test-espera-entrada.cjs': 'navegador (print do topo espera a animação de entrada)',
  'test-gates-visuais-responsivo.cjs': 'navegador (gates visuais: responsivo, oclusão, clique, identidade, vídeo)',
  'test-gates-visuais-composicao.cjs': 'navegador (gates visuais: composição e texto)',
  'test-gates-visuais-movimento.cjs': 'navegador (gates visuais: simetria e movimento)',
  'test-gates-v35.cjs': 'navegador e Pillow/numpy (gates visuais com fotos geradas)',
  'test-gravar-video-integracao.cjs': 'navegador (grava vídeo da página)',
  'test-linhas.cjs': 'navegador (mede linhas de texto na página)',
  'test-painel.cjs': 'navegador (prova do painel de cor)',
  'test-texto-ritmo-3510.cjs': 'navegador (gate-texto: e-mail e site fora da regra da maiúscula; gate-ritmo: título centralizado medido pelo alinhamento real)',
  'test-previa-direcoes.cjs': 'navegador (tira os prints das direções)',
  'test-print-cabecalho.cjs': 'navegador (print com cabeçalho fixo)',
  'test-receitas-navegador.cjs': 'navegador (prova as receitas de movimento)',
  'test-primeira-tela.cjs': 'navegador (primeira tela visível no celular, com as barras do navegador)',
  'test-visibilidade-movimento.cjs': 'navegador (texto invisível parado no topo, na visita e depois de um salto; linha recortada)',
  'test-servidor-fora.cjs': 'Playwright instalado (os gates o carregam antes de ler a URL); não abre navegador: servidor caído vira mensagem clara, saída 3',
  'test-animacao.py': 'Pillow e numpy (prancha de animação)',
  'test-imagens.py': 'Pillow e numpy (repetição e nitidez de foto)',
  'test-folha-assets.py': 'Pillow (monta a folha de contato numerada da busca de foto)',
};

function achar() {
  return readdirSync(AQUI)
    .filter((n) => /^test-.+\.(py|cjs)$/.test(n) || /\.test\.mjs$/.test(n))
    .sort();
}

function comando(arquivo) {
  const caminho = join(AQUI, arquivo);
  if (arquivo.endsWith('.py')) return [process.execPath, [join(AQUI, 'py.mjs'), caminho]];
  return [process.execPath, [caminho]];
}

function main() {
  const args = process.argv.slice(2);
  const soPortateis = args.includes('--so-portateis');
  const soLista = args.includes('--lista');
  const iF = args.indexOf('--filtro');
  const filtro = iF >= 0 ? args[iF + 1] : null;

  let arquivos = achar();
  if (filtro) arquivos = arquivos.filter((n) => n.includes(filtro));
  if (soPortateis) arquivos = arquivos.filter((n) => !PRECISAM[n]);
  if (arquivos.length === 0) { console.error('Nenhum teste encontrado.'); process.exit(2); }

  console.log(`Sistema: ${process.platform} | Node ${process.version} | ${arquivos.length} arquivo(s)${soPortateis ? ' (só portáteis)' : ''}`);
  if (soLista) {
    for (const n of arquivos) console.log(`  ${n}${PRECISAM[n] ? '   [precisa: ' + PRECISAM[n] + ']' : ''}`);
    process.exit(0);
  }

  const env = { ...process.env, PYTHONUTF8: process.env.PYTHONUTF8 || '1', PYTHONIOENCODING: process.env.PYTHONIOENCODING || 'utf-8' };
  const resultados = [];
  for (const arquivo of arquivos) {
    const [prog, argv] = comando(arquivo);
    console.log(`\n===== ${arquivo} =====`);
    const t0 = Date.now();
    const r = spawnSync(prog, argv, { encoding: 'utf8', env, cwd: AQUI, timeout: TETO_POR_TESTE_MS, maxBuffer: 256 * 1024 * 1024, windowsHide: true });
    const saida = `${r.stdout || ''}${r.stderr || ''}`;
    process.stdout.write(saida.endsWith('\n') || saida === '' ? saida : saida + '\n');
    const segundos = ((Date.now() - t0) / 1000).toFixed(1);
    const pulado = [...new Set((saida.match(/PULADO:[^\n']*/g) || []).map((l) => l.trim()))];
    let status = r.status;
    if (r.error) { status = r.error.code === 'ETIMEDOUT' ? 124 : 126; console.log(`ERRO ao rodar: ${r.error.message}`); }
    if (status === null) status = 1;
    console.log(`----- ${arquivo}: saída ${status} em ${segundos}s${pulado.length ? ` (${pulado.length} PULADO)` : ''}`);
    resultados.push({ arquivo, status, segundos, pulado });
  }

  // No CI o navegador está instalado de propósito: um teste que pula por falta de Playwright
  // seria um buraco que passa calado, então lá isso conta como falha.
  const estrito = Boolean(process.env.CI) && !soPortateis;
  for (const r of resultados) {
    if (estrito && r.status === 0 && r.pulado.some((l) => /playwright/i.test(l))) {
      r.status = 3;
      console.log(`FALHA em modo CI: ${r.arquivo} pulou por falta de Playwright, e no CI ele tem que existir.`);
    }
  }
  const falhas = resultados.filter((r) => r.status !== 0);
  const pulados = resultados.filter((r) => r.pulado.length);
  console.log('\n===== RESUMO =====');
  for (const r of resultados) console.log(`${r.status === 0 ? 'ok   ' : 'FALHA'} ${String(r.status).padStart(3)}  ${r.segundos.padStart(7)}s  ${r.arquivo}`);
  if (pulados.length) {
    console.log('\nPulados (nada foi provado nestes trechos):');
    for (const r of pulados) for (const l of r.pulado) console.log(`  ${r.arquivo}: ${l}`);
  }
  console.log(`\n${resultados.length - falhas.length} de ${resultados.length} arquivos com saída 0; ${falhas.length} com falha; ${pulados.length} com trecho pulado.`);
  process.exit(falhas.length ? 1 : 0);
}

main();
