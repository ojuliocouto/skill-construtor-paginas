"""A28 (parte 2): foto de banco com NOME de pessoa em alt, legenda ou depoimento reprova, salvo teste fictício declarado.

Auditoria real: retrato de banco em cada depoimento ("Marina Coutinho, Icaraí") contra a regra do briefing. Em projeto de cliente
real isso afirma que aquela pessoa é a Marina. Só olha a mensagem deste gate (não depende de Pillow nem de navegador).
"""
import importlib.util
import pathlib
import tempfile
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gate_imagens_nome", AQUI / "gate-imagens.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

CAB = "| Arquivo publicado | Origem | Autor | Título | Licença | Link da licença | Alteração | Pessoa identificável | Autorização de imagem | Aviso de ilustrativa |\n|---|---|---|---|---|---|---|---|---|---|\n"
BANCO = "| retrato-1.webp | https://unsplash.com/photos/x | Foto Sushi | Retrato | Unsplash License | https://unsplash.com/license | recorte | sim | não | sim |\n"
DOCLIENTE = "| retrato-1.webp | foto da cliente enviada por ela | Ana Cliente | Retrato | do cliente | - | nenhuma | sim | sim | não se aplica |\n"
FRASE = "foto de banco com nome de pessoa"


def pagina(depoimento, alt="Retrato ilustrativo de mulher sorrindo", legenda=""):
    leg = f"<figcaption>{legenda}</figcaption>" if legenda else ""
    return ("<!doctype html><html><head><title>Ateliê Veio, móveis sob medida</title></head><body><main><h1>Ateliê Veio</h1>"
            f"<section class=\"depoimentos\"><article class=\"depoimento\"><figure><img src=\"retrato-1.webp\" alt=\"{alt}\">{leg}</figure>"
            f"<blockquote>{depoimento}</blockquote></article></section><footer>Imagem ilustrativa: retratos de banco.</footer></main></body></html>")


class BancoComNome(unittest.TestCase):
    def projeto(self, html, linha=BANCO, briefing=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = pathlib.Path(tmp.name)
        (raiz / "imagens").mkdir()
        (raiz / "imagens" / "LICENCAS.md").write_text("# Licenças\n\n" + CAB + linha, encoding="utf-8")
        (raiz / "dist").mkdir()
        (raiz / "dist" / "retrato-1.webp").write_bytes(b"x")
        (raiz / "dist" / "index.html").write_text(html, encoding="utf-8")
        if briefing is not None:
            (raiz / "evidencias").mkdir()
            (raiz / "evidencias" / "briefing.md").write_text(briefing, encoding="utf-8")
        return raiz

    def avaliar(self, raiz):
        problemas, avisos = gate.avaliar(raiz)
        return [p for p in problemas if FRASE in p], [a for a in avisos if FRASE in a]

    def test_nome_no_depoimento_ao_lado_de_foto_de_banco_reprova(self):
        p, _ = self.avaliar(self.projeto(pagina("A mesa chegou montada. Marina Coutinho, Icaraí")))
        self.assertEqual(len(p), 1, p)
        self.assertIn("Marina Coutinho", p[0])
        self.assertIn("bloco de depoimento", p[0])
        self.assertIn("Negócio fictício de teste: sim", p[0])

    def test_nome_no_alt_reprova(self):
        p, _ = self.avaliar(self.projeto(pagina("A mesa chegou montada.", alt="Marina Coutinho sorrindo na sala")))
        self.assertTrue(p and "o alt" in p[0], p)

    def test_nome_na_legenda_reprova(self):
        p, _ = self.avaliar(self.projeto(pagina("A mesa chegou montada.", legenda="Eduardo Paes Leme, Ingá")))
        self.assertTrue(p and "a legenda" in p[0], p)

    def test_retrato_ilustrativo_sem_nome_passa(self):
        p, a = self.avaliar(self.projeto(pagina("A mesa chegou montada, de verdade.", alt="Retrato ilustrativo de mulher sorrindo")))
        self.assertEqual((p, a), ([], []))

    def test_teste_ficticio_declarado_em_campo_proprio_passa_e_diz_por_que(self):
        raiz = self.projeto(pagina("A mesa chegou montada. Marina Coutinho, Icaraí"), briefing="# Briefing\n\nNegócio fictício de teste: sim\n")
        p, a = self.avaliar(raiz)
        self.assertEqual(p, [])
        self.assertEqual(len(a), 1, a)
        self.assertIn("permitido porque o briefing declara teste fictício", a[0])

    def test_mutante_frase_solta_no_briefing_nao_vale_como_campo(self):
        # a frase dentro de um parágrafo (sem ser um campo "Rótulo: sim") não abre a exceção
        raiz = self.projeto(pagina("A mesa chegou montada. Marina Coutinho, Icaraí"),
                            briefing="# Briefing\n\nO cliente disse que este é um negócio fictício de teste, talvez.\n")
        p, _ = self.avaliar(raiz)
        self.assertEqual(len(p), 1)
        raiz2 = self.projeto(pagina("A mesa chegou montada. Marina Coutinho, Icaraí"), briefing="Negócio fictício de teste: não\n")
        self.assertEqual(len(self.avaliar(raiz2)[0]), 1)

    def test_foto_do_cliente_com_nome_passa(self):
        p, a = self.avaliar(self.projeto(pagina("A mesa chegou montada. Ana Cliente, Icaraí"), linha=DOCLIENTE))
        self.assertEqual((p, a), ([], []))

    def test_nome_do_proprio_negocio_no_alt_nao_conta(self):
        p, _ = self.avaliar(self.projeto(pagina("A mesa chegou montada.", alt="Oficina do Ateliê Veio")))
        self.assertEqual(p, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
