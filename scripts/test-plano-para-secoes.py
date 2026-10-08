"""A23: o PLANO diz que a tabela de composição "vira" o secoes.json da prova de animação; este script a gera.

Dois jeitos de provar: uma tabela embutida aqui e o caso do projeto de teste do aluno (Ateliê Veio, negócio
fictício), COPIADO para `scripts/fixtures/atelie/` (a tabela do PLANO, o esqueleto de `<section>` do index.html e o
`secoes.json` que o aluno escreveu à mão, que é o gabarito do que o script tem de produzir sozinho). O teste só usa
o que está dentro do repositório.
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p2s", AQUI / "plano-para-secoes.py")
p2s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2s)

REAL = AQUI / "fixtures" / "atelie"

PLANO = """# PLANO: Estúdio

### Composição por seção

| Seção | Desktop | Celular | Animação |
|---|---|---|---|
| Primeira dobra | Texto à esquerda e foto à direita | Texto e foto | abertura-do-topo: título sobe em escada |
| Para quem é | Título à esquerda | Coluna única | texto-em-linhas: cada frase sobe |
| Depoimentos | Três cartões | Carrossel horizontal com encaixe | revelar-ao-entrar: cada cartão sobe |
| Como funciona | Encaixe fixo e passos | Encaixe em faixa | assinatura-em-tres-estados: as peças alinham com a rolagem (estado 2) |
| Dúvidas | Título e perguntas | Uma coluna | pergunta-que-abre: a resposta abre |
| Fecho | Texto e botão | Coluna | assinatura: as peças se alinham sozinhas (estado 3) |

## d. Copy
"""

HTML = """<body><section class="heroi"><h1>x</h1></section>
<section class="sec" id="para-quem"></section><section id="depoimentos"></section>
<section id="como-funciona"></section><section id="duvidas"><details><summary>P</summary></details></section>
<section class="sec fecho" id="fecho"></section></body>"""


class Gera(unittest.TestCase):
    def test_tabela_vira_lista_com_tipo_modo_e_clique(self):
        lista, avisos = p2s.gerar(PLANO, HTML)
        nomes = [s["nome"] for s in lista]
        self.assertEqual(nomes, ["01-primeira-dobra", "02-para-quem-e", "03-depoimentos", "04-como-funciona", "05-duvidas", "06-fecho"])
        por = {s["titulo"]: s for s in lista}
        self.assertEqual(por["Primeira dobra"]["tipo"], "abertura-do-topo")
        self.assertEqual(por["Primeira dobra"]["modo"], "heroi")
        self.assertEqual(por["Primeira dobra"]["seletor"], ".heroi")
        self.assertEqual(por["Para quem é"]["seletor"], "#para-quem")
        self.assertEqual(por["Como funciona"]["tipo"], "assinatura")
        self.assertEqual(por["Como funciona"]["modo"], "rolagem")
        self.assertNotIn("modo", por["Fecho"])
        self.assertEqual(por["Dúvidas"]["clique"], "#duvidas summary")
        self.assertTrue(any("carrossel" in a.lower() and "rolarHorizontal" in a for a in avisos), avisos)

    def test_o_que_nao_da_pra_inferir_vem_marcado_para_preencher(self):
        lista, avisos = p2s.gerar(PLANO, None)
        self.assertTrue(all(s["seletor"].startswith("PREENCHER") for s in lista))
        self.assertTrue(any("PREENCHER" in a for a in avisos))
        # a quantidade de seções do HTML diferente da tabela também não adivinha
        lista2, avisos2 = p2s.gerar(PLANO, HTML.replace('<section id="duvidas">', '<section id="duvidas"></section><section id="outra">'))
        self.assertTrue(all(s["seletor"].startswith("PREENCHER") for s in lista2))
        self.assertTrue(any("mesmo número" in a for a in avisos2), avisos2)

    def test_sem_tabela_levanta_erro_claro(self):
        with self.assertRaises(ValueError) as e:
            p2s.gerar("# PLANO sem a tabela\n", None)
        self.assertIn("Composição por seção", str(e.exception))

    def test_linha_de_comando_grava_o_json_e_o_anim_recusa_o_que_ficou_para_preencher(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = pathlib.Path(d)
            (raiz / "PLANO.md").write_text(PLANO, encoding="utf-8")
            saida = raiz / "plano" / "secoes.json"
            r = subprocess.run([sys.executable, str(AQUI / "plano-para-secoes.py"), "--projeto", str(raiz), "--saida", str(saida)],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            doc = json.loads(saida.read_text(encoding="utf-8"))
            self.assertEqual(len(doc), 6)
            self.assertIn("PREENCHER", r.stdout)
            self.assertIn("PREENCHER", (AQUI / "anim.mjs").read_text(encoding="utf-8"))


class ComOProjetoReal(unittest.TestCase):
    def test_gera_o_mesmo_que_o_aluno_escreveu_a_mao(self):
        plano = (REAL / "PLANO.md").read_text(encoding="utf-8-sig")
        html = (REAL / "index.html").read_text(encoding="utf-8-sig")
        lista, _ = p2s.gerar(plano, html)
        mao = json.loads((REAL / "secoes.json").read_text(encoding="utf-8-sig"))
        campos = ("seletor", "titulo", "tipo", "modo", "clique")
        recorte = lambda s: {k: s[k] for k in campos if k in s}
        self.assertEqual([recorte(s) for s in lista], [recorte(s) for s in mao])
        # o nome é livre (o aluno encurtou "Madeira e acabamento" para "madeira"): confere a numeração
        self.assertEqual([s["nome"][:3] for s in lista], [s["nome"][:3] for s in mao])


if __name__ == "__main__":
    unittest.main(verbosity=2)
