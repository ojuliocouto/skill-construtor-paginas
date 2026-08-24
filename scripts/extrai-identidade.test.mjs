// Testes das funcoes puras do extrator de identidade (caminho CLONAR).
// Rodar: node --test scripts/extrai-identidade.test.mjs
// Sao funcoes puras de proposito: a parte que depende do navegador (canvas,
// getComputedStyle) fica dentro do page.evaluate e e provada rodando o script
// contra paginas reais; o ranking e a limpeza de tokens ficam aqui.
import test from "node:test";
import assert from "node:assert/strict";
import {
  pixelParaHex,
  filtrarTokens,
  pontuarCta,
  ranquearCtas,
  classificarConfianca,
} from "./extrai-identidade.mjs";

// ---------------------------------------------------------------- pixelParaHex
test("pixelParaHex converte pixel do canvas em hex maiusculo", () => {
  assert.equal(pixelParaHex([250, 78, 4, 255]), "#FA4E04");
  assert.equal(pixelParaHex([0, 0, 0, 255]), "#000000");
  assert.equal(pixelParaHex([255, 255, 255, 255]), "#FFFFFF");
});

test("pixelParaHex arredonda canal fracionario", () => {
  assert.equal(pixelParaHex([249.6, 77.5, 3.4, 255]), "#FA4E03");
});

test("pixelParaHex devolve null para entrada invalida", () => {
  assert.equal(pixelParaHex(undefined), null);
  assert.equal(pixelParaHex([]), null);
  assert.equal(pixelParaHex(["a", "b", "c"]), null);
});

// --------------------------------------------------------------- filtrarTokens
test("filtrarTokens descarta vazio e prefixo de utilitario (caso real tailwindcss.com)", () => {
  const brutos = {
    "--tw-backdrop-blur": "",
    "--tw-leading": "",
    "--tw-font-weight": "600",
    "--lightningcss-light": "",
    "--lightningcss-dark": "",
    "--font-inter": '"inter", "inter Fallback"',
    "--color-slate-900": "#0F172A",
    "--espaco-vazio": "   ",
  };
  const limpos = filtrarTokens(brutos);
  assert.deepEqual(Object.keys(limpos).sort(), ["--color-slate-900", "--font-inter"]);
});

test("filtrarTokens preserva token de cor da marca em pagina classica", () => {
  const limpos = filtrarTokens({ "--laranja": "#FA4E04", "--primaria": "#2980A9" });
  assert.equal(limpos["--laranja"], "#FA4E04");
  assert.equal(limpos["--primaria"], "#2980A9");
});

test("filtrarTokens aceita entrada vazia ou nula", () => {
  assert.deepEqual(filtrarTokens({}), {});
  assert.deepEqual(filtrarTokens(null), {});
});

// ----------------------------------------------------------------- ranquearCtas
// Dados medidos na tailwindcss.com: o badge de versao do menu e o CTA de verdade.
const BADGE_V43 = {
  texto: "v4.3",
  tag: "a",
  largura: 42,
  altura: 20,
  fundoHex: "#0E1116",
  fundoAlfa: 0.05,
  corHex: "#020617",
  peso: 500,
  tamanhoPx: 12,
  dentroDoPrimeiroViewport: true,
};
const CTA_GET_STARTED = {
  texto: "Get started",
  tag: "a",
  largura: 148,
  altura: 44,
  fundoHex: "#0F172A",
  fundoAlfa: 1,
  corHex: "#FFFFFF",
  peso: 600,
  tamanhoPx: 16,
  dentroDoPrimeiroViewport: true,
};
const CONTEXTO = { fundoDoCorpo: "#FFFFFF" };

test("ranquearCtas poe o CTA real acima do badge de versao e mantem os dois na lista", () => {
  const lista = ranquearCtas([BADGE_V43, CTA_GET_STARTED], CONTEXTO);
  assert.equal(lista[0].texto, "Get started");
  assert.ok(
    lista.some((c) => c.texto === "v4.3"),
    "o badge tem que continuar na lista, so que ranqueado abaixo"
  );
  assert.ok(lista[0].pontuacao > lista[1].pontuacao);
});

test("ranquearCtas devolve pontuacao, motivos e confianca em cada candidato", () => {
  const [primeiro] = ranquearCtas([CTA_GET_STARTED], CONTEXTO);
  assert.equal(typeof primeiro.pontuacao, "number");
  assert.ok(Array.isArray(primeiro.motivos) && primeiro.motivos.length > 0);
  assert.ok(["alta", "media", "baixa"].includes(primeiro.confianca));
});

test("ranquearCtas penaliza texto longo de link em relacao a botao de 2 palavras", () => {
  const linkLongo = {
    ...CTA_GET_STARTED,
    texto: "Preciso ter CNPJ para contratar a API Oficial?",
    largura: 420,
  };
  const lista = ranquearCtas([linkLongo, CTA_GET_STARTED], CONTEXTO);
  assert.equal(lista[0].texto, "Get started");
});

test("ranquearCtas prefere quem esta no primeiro viewport", () => {
  const rodape = { ...CTA_GET_STARTED, texto: "Fale conosco", dentroDoPrimeiroViewport: false };
  const lista = ranquearCtas([rodape, CTA_GET_STARTED], CONTEXTO);
  assert.equal(lista[0].texto, "Get started");
});

test("pontuarCta nao da ponto de fundo solido quando o fundo e igual ao do corpo", () => {
  const iguais = { ...CTA_GET_STARTED, fundoHex: "#FFFFFF" };
  const comFundo = pontuarCta(CTA_GET_STARTED, CONTEXTO);
  const semFundo = pontuarCta(iguais, CONTEXTO);
  assert.ok(comFundo.pontuacao > semFundo.pontuacao);
  assert.ok(!semFundo.motivos.some((m) => m.includes("fundo sólido")));
});

test("pontuarCta nao da ponto de fundo solido quando o fundo e quase transparente", () => {
  const { motivos } = pontuarCta(BADGE_V43, CONTEXTO);
  assert.ok(!motivos.some((m) => m.includes("fundo sólido")));
});

test("ranquearCtas aceita lista vazia", () => {
  assert.deepEqual(ranquearCtas([], CONTEXTO), []);
  assert.deepEqual(ranquearCtas(null, CONTEXTO), []);
});

test("classificarConfianca separa palpite forte de palpite fraco", () => {
  assert.equal(classificarConfianca(11), "alta");
  assert.equal(classificarConfianca(6), "media");
  assert.equal(classificarConfianca(1), "baixa");
});
