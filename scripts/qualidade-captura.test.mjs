// Testes do classificador de captura de referência (achados A1 e A2 do teste de ponta a ponta).
// Rodar: node --test scripts/qualidade-captura.test.mjs
// Função pura de propósito: as medidas (status, texto, estilo, altura, cobertura) vêm do
// navegador em capturar-referencias.mjs; aqui se prova só a decisão.
import test from "node:test";
import assert from "node:assert/strict";
import { classificar, ESTADOS, resumirBoas, proximoPrefixo, acharReferencia } from "./qualidade-captura.mjs";

const TEXTO_BOM = "Móveis sob medida em madeira maciça. ".repeat(40);
const base = { http: 200, titulo: "Ateliê", texto: TEXTO_BOM, temEstilo: true, altura: 4200, janela: 900, cobertura: 0 };

test("página renderizada de verdade é ok", () => {
  assert.equal(classificar(base).estado, "ok");
  assert.deepEqual(ESTADOS, ["ok", "bloqueada", "quebrada", "coberta", "vazia"]);
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

// ---- 3.5.8, achado N1: dobra em branco e meio com foto que não carregou não são "ok" ----
test("N1: dobra quase toda de uma cor só é vazia, com o motivo e a porcentagem", () => {
  const r = classificar({ ...base, dominanciaDobra: 0.99 });
  assert.equal(r.estado, "vazia");
  assert.match(r.motivo, /dobra/);
  assert.match(r.motivo, /99%/);
  assert.ok(ESTADOS.includes("vazia"));
});

test("N1: dobra com mais de 80% de uma cor só segue ok, mas leva aviso (minimalista de verdade passa)", () => {
  const r = classificar({ ...base, dominanciaDobra: 0.88 });
  assert.equal(r.estado, "ok");
  assert.match(r.aviso, /88%/);
  assert.equal(classificar({ ...base, dominanciaDobra: 0.5 }).aviso, undefined);
});

test("N1: meio de uma cor só com foto que não carregou é vazia; meio de texto sobre fundo liso sem foto pendente é ok", () => {
  const r = classificar({ ...base, dominanciaMeio: 0.9, imagensSemCarregar: 4 });
  assert.equal(r.estado, "vazia");
  assert.match(r.motivo, /meio/);
  assert.match(r.motivo, /4 foto/);
  assert.equal(classificar({ ...base, dominanciaMeio: 0.9, imagensSemCarregar: 0 }).estado, "ok");
  assert.equal(classificar({ ...base, dominanciaMeio: 0.5, imagensSemCarregar: 6 }).estado, "ok");
});

test("N1: meio inteiro de uma cor só (97% ou mais) é vazia mesmo sem foto pendente", () => {
  assert.equal(classificar({ ...base, dominanciaMeio: 0.985, imagensSemCarregar: 0 }).estado, "vazia");
});

test("N1: vazia não vence bloqueada, quebrada nem coberta (o motivo mais grave aparece)", () => {
  assert.equal(classificar({ ...base, http: 403, dominanciaDobra: 1 }).estado, "bloqueada");
  assert.equal(classificar({ ...base, temEstilo: false, dominanciaDobra: 1 }).estado, "quebrada");
  assert.equal(classificar({ ...base, cobertura: 0.9, dominanciaDobra: 1 }).estado, "coberta");
});

test("N1: sem as medidas novas (manifesto e chamadas antigas) o resultado não muda", () => {
  assert.equal(classificar(base).estado, "ok");
  assert.equal(classificar(base).aviso, undefined);
});

test("N1: resumirBoas não conta vazia", () => {
  assert.equal(resumirBoas([{ captura: { estado: "vazia" } }, { captura: { estado: "ok" } }]), 1);
});

// ---- 3.5.8, achado N2: numeração segue do maior prefixo já usado ----
test("N2: proximoPrefixo segue do maior número visto nas pastas, não do tamanho do manifesto", () => {
  assert.equal(proximoPrefixo([]), 1);
  assert.equal(proximoPrefixo(["01-a-dobra.png", "02-a-meio.png", "13-b-dobra.png"]), 14);
  assert.equal(proximoPrefixo(["referencias.json", "abc.png", "7-x.png"]), 8);
  // mutante: contar quantos arquivos existem (o defeito original) daria 4, e 4 já está em uso na vida real
  assert.notEqual(proximoPrefixo(["01-a.png", "02-a.png", "13-b.png"]), 4);
});

// ---- 3.5.8, achado N3: remover uma referência ok que não serve ----
test("N3: acharReferencia casa por endereço exato (com ou sem barra final) e por trecho único; trecho ambíguo recusa", () => {
  const refs = [{ url: "https://a.com/" }, { url: "https://b.com/x" }, { url: "https://b.com/y" }];
  assert.equal(acharReferencia(refs, "https://a.com").url, "https://a.com/");
  assert.equal(acharReferencia(refs, "a.com").url, "https://a.com/");
  assert.equal(acharReferencia(refs, "b.com").erro, "ambigua");
  assert.equal(acharReferencia(refs, "c.com").erro, "nenhuma");
  assert.equal(acharReferencia(refs, "https://b.com/y").url, "https://b.com/y");
});

// ---- 3.5.10, achado P1: tela de bloqueio de robô com cabeçalho do site não é ok ----
test("P1: 'We couldn't verify the security of your connection' é bloqueada (Um Coffee, 3.5.8 marcou ok)", () => {
  const texto = "Compre Aqui Clube de Assinatura Cursos Sobre nós Máquinas Clique aqui! We couldn't verify the security of your connection. Access to this content has been restricted. Contact your internet service provider for help.";
  const r = classificar({ ...base, titulo: "Um Coffee Co", texto, altura: 900 });
  assert.equal(r.estado, "bloqueada");
  assert.match(r.motivo, /bloqueio|desafio/);
});

test("P1: variantes comuns de bloqueio de robô (Cloudflare, Akamai, Incapsula, PerimeterX) são bloqueada", () => {
  const variantes = [
    "Performance & security by Cloudflare. Ray ID: 8a1b2c3d4e5f",
    "Access Denied. Reference #18.2f6b3e17.1696243200.1a2b3c4d",
    "Request unsuccessful. Incapsula incident ID: 123000540000-4567",
    "Press & Hold to confirm you are a human (and not a bot).",
    "Our systems have detected unusual traffic from your computer network.",
    "Sorry, you have been blocked. You are unable to access this site.",
    "Please verify you are a human to continue. Security check in progress.",
    "Too many requests. You are being rate limited.",
    "Why have I been blocked? This website is using a security service to protect itself from online attacks.",
    "Não foi possível verificar a segurança da sua conexão. O acesso foi restrito.",
    "Detectamos atividade incomum na sua rede. Confirme que você não é um robô.",
  ];
  for (const texto of variantes) {
    const r = classificar({ ...base, titulo: "Site", texto: "Início Contato " + texto, altura: 900 });
    assert.equal(r.estado, "bloqueada", texto);
  }
});

test("P1: a frase forte pega mesmo quando o cabeçalho e o rodapé do site passam de 800 caracteres", () => {
  const texto = "Menu ".repeat(200) + "We couldn't verify the security of your connection. " + "Rodapé ".repeat(100);
  assert.ok(texto.length > 800);
  assert.equal(classificar({ ...base, titulo: "Loja", texto, altura: 900 }).estado, "bloqueada");
});

test("P1: mutante: página longa e boa que fala de segurança de conexão em outro contexto continua ok", () => {
  const texto = TEXTO_BOM + " Nossa política: protegemos a segurança da sua conexão com criptografia. " + TEXTO_BOM;
  assert.equal(classificar({ ...base, texto }).estado, "ok");
});
