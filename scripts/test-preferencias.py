"""As regras de gosto da memória do dono não podem ficar só na memória.

Por que existe (02/10/2026, auditoria da v3 com nota 5,5): os itens 14 a 20 da memória de gosto
(todos do mesmo dia) nunca chegaram em `references/preferencias-de-design.md`, embora a memória
dissesse "espelhado na skill". A página seguiu os arquivos da skill e repetiu três desenhos que o
dono tinha reprovado horas antes. Este teste fecha o buraco: cada item numerado da memória precisa
de um par marcado `<!-- gosto:N -->` num dos arquivos de preferência.

- Itens genéricos (valem para qualquer página) moram em `preferencias-de-design.md`.
- Itens só do dono (foto e bio dele, nome de pessoa ou marca) moram SÓ em
  `preferencias-dono-ea.md`, que é local e fica fora do Git.

Quem clonou a skill não tem a memória do dono: o teste de sincronia pula com aviso, e os testes do
arquivo genérico continuam rodando.
"""
import os
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
GENERICO = RAIZ / "references" / "preferencias-de-design.md"
DONO = RAIZ / "references" / "preferencias-dono-ea.md"
# Itens da memória que falam de uma pessoa ou marca e por isso nunca vão para o arquivo genérico.
SO_DO_DONO = {18}
# Itens já genéricos que todo aluno recebe, com o mínimo que o texto precisa dizer.
GENERICOS_OBRIGATORIOS = {
    14: r"p[ií]lula",
    15: r"mesma altura",
    16: r"primeira dobra",
    17: r"um ou outro|escolha um",
    19: r"FAQ",
    20: r"[ií]cone",
}
MARCA = re.compile(r"<!--\s*gosto:(\d+)\s*-->")


def memoria():
    """A memória de gosto do dono, se esta máquina tiver uma. Nunca caminho fixo de usuário."""
    if os.environ.get("GOSTO_MEMORIA"):
        p = pathlib.Path(os.environ["GOSTO_MEMORIA"]).expanduser()
        return p if p.exists() else None
    achados = sorted(pathlib.Path.home().glob(".claude/projects/*/memory/feedback-gosto-visual-paginas-*.md"))
    return achados[0] if achados else None


def itens_da_memoria(texto):
    return sorted({int(m) for m in re.findall(r"(?m)^(\d+)\.\s+\*\*", texto)})


def marcas(p):
    return {int(n) for n in MARCA.findall(p.read_text(encoding="utf-8"))} if p.exists() else set()


class Generico(unittest.TestCase):
    def test_itens_genericos_de_02_10_estao_no_arquivo_do_aluno(self):
        texto = GENERICO.read_text(encoding="utf-8")
        tem = marcas(GENERICO)
        for n, padrao in GENERICOS_OBRIGATORIOS.items():
            self.assertIn(n, tem, f"item {n} da memória de gosto sem par em preferencias-de-design.md")
            # A marca fecha o item: o texto do item é o que vem antes dela, desde o último "- **".
            fim = re.search(rf"<!--\s*gosto:{n}\s*-->", texto).start()
            inicio = texto.rfind("- **", 0, fim)
            self.assertRegex(texto[inicio:fim], re.compile(padrao, re.I), f"item {n} sem o conteúdo esperado")

    def test_item_so_do_dono_nunca_no_generico(self):
        self.assertFalse(SO_DO_DONO & marcas(GENERICO), "item com nome de pessoa no arquivo do aluno")


class Sincronia(unittest.TestCase):
    def test_todo_item_numerado_da_memoria_tem_par(self):
        mem = memoria()
        if not mem:
            self.skipTest("PULADO: memória de gosto do dono não existe nesta máquina (aluno): sincronia pulada")
        if not DONO.exists():
            self.skipTest("PULADO: references/preferencias-dono-ea.md é local e fica fora do Git; sem ele o item só do dono não tem par")
        itens = itens_da_memoria(mem.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(itens), 10, "a leitura da memória não achou os itens numerados")
        tem = marcas(GENERICO) | marcas(DONO)
        faltam = [n for n in itens if n not in tem]
        self.assertEqual(faltam, [], f"itens da memória sem par nos arquivos de preferência: {faltam}")

    def test_item_do_dono_mora_no_arquivo_local(self):
        if not memoria() or not DONO.exists():
            self.skipTest("PULADO: sem memória ou sem preferencias-dono-ea.md local (arquivo do dono, fora do Git)")
        self.assertTrue(SO_DO_DONO <= marcas(DONO), "item só do dono ausente do arquivo local")


if __name__ == "__main__":
    unittest.main(verbosity=2)
