"""Controles do gate de verdade: promessa da página só com linha do briefing que sustente.

Caso real (02/10/2026, auditoria da v3): o passo 3 dizia "Você chega, faz a avaliação postural e
começa" e a meta description dizia "Aula experimental gratuita, com avaliação postural", quando o
briefing deixava em aberto se a avaliação é gratuita e se acontece no mesmo dia. O copy.md
afirmava "texto não afirma o mesmo dia, só a ordem". Era o crítico da v1 voltando.
"""
import contextlib
import importlib.util
import io
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("gate_verdade", pathlib.Path(__file__).with_name("gate-verdade.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

BRIEFING = """# Briefing
1. O que vende: pilates com fisioterapeuta, aulas em grupo de até 4 pessoas e aulas particulares.
2. Onde: Niterói (RJ). Bairro e endereço: PENDENTE.
4. Oferta: aula experimental gratuita. Antes da primeira aula, avaliação postural com fisioterapeuta.
5. Preço: Preço das aulas regulares: PENDENTE. Se a avaliação é gratuita: PENDENTE, a página não afirma.
6. Ação: agendar a aula experimental pelo WhatsApp. Número: PENDENTE.
"""

NAO_AFIRMAR = """
## Não afirmar (pendências)
- Endereço: `\\bRua\\b|Avenida|bairro`
- Preço: `R\\$`
- Avaliação grátis ou no mesmo dia: `gratuit\\w*[^.]{0,80}avalia|avalia[^.]{0,80}(gr[aá]tis|gratuit)|mesmo dia|chega[^.]{0,60}avalia[^.]{0,60}come[cç]a`
- Número do WhatsApp: `\\(\\d{2}\\)`
"""


def html(corpo, meta="A aula experimental é gratuita. Antes da primeira aula, avaliação postural com fisioterapeuta."):
    return (f'<!doctype html><html><head><title>Studio | Pilates</title><meta name="description" content="{meta}">'
            f'<meta property="og:description" content="{meta}"></head><body>{corpo}'
            '<section hidden><p>Depoimento grátis escondido.</p></section><script>var x="grátis";</script></body></html>')


TABELA_OK = """# Sustentação
| Frase da página | Linha do briefing que sustenta |
|---|---|
| A aula experimental é gratuita. | "Oferta: aula experimental gratuita" |
| Antes da primeira aula, avaliação postural com fisioterapeuta. | "Antes da primeira aula, avaliação postural com fisioterapeuta" |
| Turmas de até 4 pessoas. | "aulas em grupo de até 4 pessoas" |
| Studio | interpretação: nome da marca |
| Studio \\| Pilates | interpretação: nome da marca no title |
"""

CORPO_OK = "<h1>Studio</h1><p>Turmas de até 4 pessoas.</p><p>A aula experimental é gratuita.</p><p>Você conhece o estúdio.</p>"


class Verdade(unittest.TestCase):
    def montar(self, corpo=CORPO_OK, tabela=TABELA_OK, nao_afirmar=NAO_AFIRMAR, meta=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        r = pathlib.Path(self.tmp.name)
        (r / "evidencias").mkdir()
        (r / "evidencias" / "briefing.md").write_text(BRIEFING, encoding="utf-8")
        (r / "evidencias" / "sustentacao.md").write_text(tabela + nao_afirmar, encoding="utf-8")
        (r / "index.html").write_text(html(corpo) if meta is None else html(corpo, meta), encoding="utf-8")
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = gate.main(["--projeto", str(r)])
        return code, saida.getvalue()

    def test_positivo(self):
        code, out = self.montar()
        self.assertEqual(code, 0, out)

    def test_caso_real_da_v3_reprova(self):
        corpo = CORPO_OK + "<li><h3>Avaliação e primeira aula</h3><p>Você chega, faz a avaliação postural e começa.</p></li>"
        code, out = self.montar(corpo=corpo, meta="Aula experimental gratuita, com avaliação postural antes da primeira aula.")
        self.assertEqual(code, 1)
        self.assertIn("faz a avaliação postural e começa", out)
        self.assertIn("Aula experimental gratuita, com avaliação postural", out)

    def test_promessa_sem_linha_na_tabela(self):
        code, out = self.montar(corpo=CORPO_OK + "<p>Primeira semana com 50% de desconto.</p>")
        self.assertEqual(code, 1)
        self.assertIn("sem linha de sustentação", out)

    def test_promessa_sustentada_por_interpretacao(self):
        tabela = TABELA_OK + "| Resultado em 30 dias. | interpretação: o público quer rapidez |\n"
        code, out = self.montar(corpo=CORPO_OK + "<p>Resultado em 30 dias.</p>", tabela=tabela)
        self.assertEqual(code, 1)
        self.assertIn("interpretação não sustenta promessa", out)

    def test_citacao_que_nao_esta_no_briefing(self):
        tabela = TABELA_OK + '| Avaliação gratuita para todas. | "avaliação gratuita para todas as alunas" |\n'
        code, out = self.montar(corpo=CORPO_OK + "<p>Avaliação gratuita para todas.</p>", tabela=tabela,
                                nao_afirmar=NAO_AFIRMAR.replace("gratuit\\w*[^.]{0,80}avalia|", ""))
        self.assertEqual(code, 1)
        self.assertIn("não está no briefing", out)

    def test_citacao_de_frase_pendente(self):
        tabela = TABELA_OK + '| A avaliação é gratuita. | "Se a avaliação é gratuita" |\n'
        code, out = self.montar(corpo=CORPO_OK + "<p>A avaliação é gratuita.</p>", tabela=tabela,
                                nao_afirmar=NAO_AFIRMAR.replace("avalia[^.]{0,80}(gr[aá]tis|gratuit)|", ""))
        self.assertEqual(code, 1)
        self.assertIn("PENDENTE", out)

    def test_meta_description_precisa_estar_na_tabela(self):
        code, out = self.montar(meta="Pilates em Niterói para quem tem dor.")
        self.assertEqual(code, 1)
        self.assertIn("meta", out)

    def test_cada_pendencia_do_briefing_pede_um_padrao(self):
        code, out = self.montar(nao_afirmar="\n## Não afirmar (pendências)\n- Preço: `R\\$`\n")
        self.assertEqual(code, 1)
        self.assertIn("pendência", out)

    def test_sem_tabela_reprova(self):
        code, out = self.montar(tabela="# vazio\n")
        self.assertEqual(code, 1)

    # Auditoria da v5 (03/10/2026): o briefing diz que o estúdio é da fisioterapeuta Carla
    # Mendes, e a página só citava o nome no rodapé ("Fisioterapeuta: Carla Mendes.").
    def montar_dono(self, corpo):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        r = pathlib.Path(self.tmp.name)
        (r / "evidencias").mkdir()
        (r / "evidencias" / "briefing.md").write_text(BRIEFING + "\nProfissional citada no briefing: Carla Mendes, fisioterapeuta.\n", encoding="utf-8")
        (r / "evidencias" / "sustentacao.md").write_text(TABELA_OK + NAO_AFIRMAR, encoding="utf-8")
        (r / "index.html").write_text(html(corpo), encoding="utf-8")
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = gate.main(["--projeto", str(r)])
        return code, saida.getvalue()

    def test_dono_citado_so_no_rodape_reprova(self):
        code, out = self.montar_dono(CORPO_OK + "<footer><p>Fisioterapeuta: Carla Mendes.</p></footer>")
        self.assertEqual(code, 1, out)
        self.assertIn("Carla Mendes", out)
        self.assertIn("rodapé", out)

    def test_dono_no_corpo_da_pagina_passa(self):
        code, out = self.montar_dono(CORPO_OK + "<section><p>O Studio é da fisioterapeuta Carla Mendes.</p></section><footer><p>Fisioterapeuta: Carla Mendes.</p></footer>")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
