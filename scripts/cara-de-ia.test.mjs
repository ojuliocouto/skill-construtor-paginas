// Testes das réguas de "cara de IA" (auditoria de 25/10/2026, brechas A6, A7, A8 e enfeite de título).
// Rodar: node --test scripts/cara-de-ia.test.mjs
// Funções puras de propósito: as medidas vêm do navegador em gate-texto.mjs e gate-composicao.mjs;
// aqui se prova só a decisão. Os números dos casos são os medidos nas páginas reais da auditoria.
import test from "node:test";
import assert from "node:assert/strict";
import {
  julgarFiletes, FILETES_MINIMO, FILETES_POR_TELA_MAXIMO,
  motivoValido, motivoDoDesenho, contarMotivos, MOTIVO_REPETIDO_MAXIMO,
  julgarEnfeites, TITULOS_COM_O_MESMO_ENFEITE_MAXIMO,
  publicoDePessoas, pessoaNoTexto,
} from "./cara-de-ia.mjs";

// Filetes medidos em 1440x900 (enfeite = fora de dl e table; tabela = dentro de dl ou table).
const PAGINAS = {
  cursoAdvogados: { enfeite: 22, tabela: 0, alturaPagina: 11064 },   // produção, cara de template: reprova
  torrefacao: { enfeite: 1, tabela: 11, alturaPagina: 9754 },        // teste 3.5.8, a mais própria: passa
  atelie: { enfeite: 0, tabela: 0, alturaPagina: 9954 },             // teste 3.5.6: passa
  estudioV3: { enfeite: 11, tabela: 1, alturaPagina: 5398 },         // o "jornal de filetes" original: reprova
  estudioV7: { enfeite: 12, tabela: 20, alturaPagina: 15204 },       // aprovada pelo dono: passa
};

test("filetes: as páginas reais da auditoria caem do lado certo", () => {
  const j = (p) => julgarFiletes({ ...PAGINAS[p], alturaTela: 900 });
  assert.equal(j("cursoAdvogados").reprova, true);
  assert.equal(j("estudioV3").reprova, true);
  assert.equal(j("torrefacao").reprova, false);
  assert.equal(j("atelie").reprova, false);
  assert.equal(j("estudioV7").reprova, false);
});

test("filetes: a conta é por tela de 900 px e só de enfeite", () => {
  const r = julgarFiletes({ enfeite: 22, tabela: 0, alturaPagina: 11064, alturaTela: 900 });
  assert.equal(r.porTela.toFixed(2), "1.79");
  assert.equal(FILETES_POR_TELA_MAXIMO, 1.2);
  assert.equal(FILETES_MINIMO, 10);
  // tabela de rótulo e valor não conta: 30 filetes numa dl não reprovam
  assert.equal(julgarFiletes({ enfeite: 0, tabela: 30, alturaPagina: 3000, alturaTela: 900 }).reprova, false);
  // abaixo do mínimo absoluto não reprova, mesmo denso (página curta com 3 itens de lista)
  assert.equal(julgarFiletes({ enfeite: 9, tabela: 0, alturaPagina: 1800, alturaTela: 900 }).reprova, false);
  // 10 filetes em 2 telas reprova
  assert.equal(julgarFiletes({ enfeite: 10, tabela: 0, alturaPagina: 1800, alturaTela: 900 }).reprova, true);
  // o aviso antigo (10 ou mais filetes no total) continua
  assert.equal(julgarFiletes({ enfeite: 1, tabela: 11, alturaPagina: 9754, alturaTela: 900 }).aviso, true);
});

test("motivo de exceção: precisa de texto, não de marcador", () => {
  for (const ruim of ["1", "", "  ", "true", "sim", "ok", "OK", "repetido", "marco passo"]) assert.equal(motivoValido(ruim), false, JSON.stringify(ruim));
  for (const bom of ["marco de cada passo da linha do tempo", "a mesma tecla marca os três passos do método"]) assert.equal(motivoValido(bom), true, bom);
  assert.equal(motivoValido(null), false);
});

test("motivo do desenho: a primeira oração, em minúscula", () => {
  assert.equal(motivoDoDesenho("Sinal de mais do logo, gigante e apagado atrás da calculadora"), "sinal de mais do logo");
  assert.equal(motivoDoDesenho("  sinal de mais do logo "), "sinal de mais do logo");
  assert.equal(motivoDoDesenho(""), "");
});

test("motivo repetido: mais de 6 do mesmo motivo reprova, lista o pior", () => {
  assert.equal(MOTIVO_REPETIDO_MAXIMO, 6);
  // 15 marcadores "sinal de mais do logo" + 1 gigante = 16 (página de produção)
  const curso = [...Array(15).fill("sinal de mais do logo"), "sinal de mais do logo, gigante e apagado", ...Array(6).fill("sinal de vezes do logo"), "sinal de vezes do logo, grande", "tela do sistema"];
  const r = contarMotivos(curso.map((d) => ({ chave: motivoDoDesenho(d), nome: d })));
  assert.deepEqual(r.map((x) => [x.chave, x.n]), [["sinal de mais do logo", 16], ["sinal de vezes do logo", 7]]);
  // 6 iguais ainda passa
  assert.deepEqual(contarMotivos(Array(6).fill({ chave: "seta", nome: "seta" })), []);
});

test("enfeite de título: o mesmo traço embaixo de 9 de 10 h2 reprova; até 3 passa", () => {
  assert.equal(TITULOS_COM_O_MESMO_ENFEITE_MAXIMO, 3);
  const traco = "::after 56x3 rgb(224, 122, 95)";
  const curso = [traco, traco, traco, traco, traco, traco, traco, "", traco, traco];
  const r = julgarEnfeites(curso);
  assert.equal(r.reprova, true);
  assert.equal(r.pior.n, 9);
  assert.equal(r.pior.total, 10);
  assert.equal(julgarEnfeites([traco, traco, traco, "", "", ""]).reprova, false);
  assert.equal(julgarEnfeites(Array(8).fill("")).reprova, false);
  // enfeites diferentes não se somam
  assert.equal(julgarEnfeites(["a", "b", "c", "d", "e"]).reprova, false);
});

test("público de pessoas: profissões no plural e no feminino", () => {
  const sim = [
    "advogados", "advogadas", "advogado criminalista", "Advogados que não dominam o SEEU", "médicos", "médicas", "medicos",
    "dentistas", "contadores", "contadoras", "nutricionistas", "corretores de imóveis", "corretoras", "psicólogas", "psicologos",
    "fisioterapeutas", "enfermeiras", "arquitetos", "engenheiras", "professoras", "veterinários", "farmacêuticas", "esteticistas",
    "cabeleireiras", "personal trainers", "terapeutas", "fonoaudiólogas", "mulheres de 35 a 60", "profissionais liberais",
    "donos de pequenas empresas", "Adultos de 28 a 55 anos que passam café em casa todo dia", "empresárias", "gestores", "consultoras",
  ];
  for (const p of sim) assert.equal(publicoDePessoas(p), true, p);
  const nao = ["Quem está montando ou reformando casa e não quer móvel planejado de MDF", "lojas de roupa", "", "restaurantes e bares"];
  for (const p of nao) assert.equal(publicoDePessoas(p), false, p);
});

test("pessoa no texto da foto ou do desenho: profissões também contam", () => {
  for (const alt of ["Advogada analisando um processo no computador", "Médico conversando com paciente", "Dentista no consultório", "Mão de um homem lixando uma peça de madeira", "com as mãos da pessoa que torra ao lado"]) assert.equal(pessoaNoTexto(alt), true, alt);
  for (const alt of ["Grãos de café cru antes da torra", "Mesa de jantar de madeira", "Tela do sistema com uma aba destacada"]) assert.equal(pessoaNoTexto(alt), false, alt);
});
