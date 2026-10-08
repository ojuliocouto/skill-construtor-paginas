// Testes do classificador de captura de referência (achados A1 e A2 do teste de ponta a ponta).
// Rodar: node --test scripts/qualidade-captura.test.mjs
// Função pura de propósito: as medidas (status, texto, estilo, altura, cobertura) vêm do
// navegador em capturar-referencias.mjs; aqui se prova só a decisão.
import test from "node:test";
import assert from "node:assert/strict";
import { classificar, ESTADOS, resumirBoas } from "./qualidade-captura.mjs";

const TEXTO_BOM = "Móveis sob medida em madeira maciça. ".repeat(40);
const base = { http: 200, titulo: "Ateliê", texto: TEXTO_BOM, temEstilo: true, altura: 4200, janela: 900, cobertura: 0 };

test("página renderizada de verdade é ok", () => {
  assert.equal(classificar(base).estado, "ok");
  assert.deepEqual(ESTADOS, ["ok", "bloqueada", "quebrada", "coberta"]);
});

test("HTTP 403, 401 e 429 são bloqueada; 404 e 500 são quebrada", () => {
  for (const http of [401, 403, 429]) assert.equal(classificar({ ...base, http }).estado, "bloqueada", String(http));
  for (const http of [404, 410, 500, 502]) assert.equal(classificar({ ...base, http }).estado, "quebrada", String(http));
  assert.match(classificar({ ...base, http: 403 }).motivo, /403/);
});

test("texto de bloqueio dominando a página é bloqueada, mesmo com HTTP 200", () => {
  const casos = [
    ["403 Forbidden", "Forbidden. You don't have permission to access this resource."],
    ["Access Denied", "Access Denied. You don't have permission to access this server."],
    ["Just a moment...", "Verificando se você é humano. Este processo é automático."],
    ["Attention Required! | Cloudflare", "Please enable cookies. Sorry, you have been blocked."],
    ["", "Checking your browser before accessing the site. Please complete the captcha."],
    ["", "Acesso negado. Seu acesso a este site foi bloqueado."],
  ];
  for (const [titulo, texto] of casos) {
    const r = classificar({ ...base, titulo, texto, altura: 900 });
    assert.equal(r.estado, "bloqueada", `${titulo} | ${texto}`);
  }
});

test("mutante: a palavra captcha ou forbidden dentro de uma página longa e boa NÃO reprova", () => {
  const texto = TEXTO_BOM + " Política de privacidade: protegido por captcha. Forbidden words list. " + TEXTO_BOM;
  assert.equal(classificar({ ...base, texto }).estado, "ok");
});

test("sem folha de estilo aplicada é quebrada", () => {
  const r = classificar({ ...base, temEstilo: false });
  assert.equal(r.estado, "quebrada");
  assert.match(r.motivo, /estilo/);
});

test("altura igual à da janela com quase nada de texto é quebrada; página curta de verdade com conteúdo é ok", () => {
  assert.equal(classificar({ ...base, altura: 900, texto: "Entrar" }).estado, "quebrada");
  assert.equal(classificar({ ...base, altura: 900, texto: TEXTO_BOM }).estado, "ok");
});

test("modal cobrindo mais de 40% da janela é coberta; 40% ou menos passa", () => {
  const r = classificar({ ...base, cobertura: 0.62 });
  assert.equal(r.estado, "coberta");
  assert.match(r.motivo, /62%/);
  assert.equal(classificar({ ...base, cobertura: 0.4 }).estado, "ok");
  assert.equal(classificar({ ...base, cobertura: 0.1 }).estado, "ok");
});

test("bloqueada vence quebrada, que vence coberta", () => {
  assert.equal(classificar({ ...base, http: 403, temEstilo: false, cobertura: 1 }).estado, "bloqueada");
  assert.equal(classificar({ ...base, temEstilo: false, cobertura: 1 }).estado, "quebrada");
});

test("resumirBoas conta só as ok; manifesto antigo sem captura conta como ok", () => {
  const refs = [{ captura: { estado: "ok" } }, { captura: { estado: "bloqueada" } }, {}, { captura: { estado: "coberta" } }];
  assert.equal(resumirBoas(refs), 2);
});
