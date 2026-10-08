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


# ----- v3.5.6: achados A3 a A6 do teste de ponta a ponta (Ateliê Veio, 08/10/2026) -----
BRIEFING_ATELIE = """# Briefing
1. O que vende: móveis sob medida de madeira maciça.
2. Visita técnica gratuita em Niterói; R$ 150 na zona sul do Rio, abatidos se fechar o projeto.
3. Garantia: 5 anos na estrutura.
4. Prazo: entrega montada em 30 a 45 dias
depois da aprovação.
"""

TABELA_ATELIE = """| Frase da página | Linha do briefing que sustenta |
|---|---|
| Ateliê | interpretação: nome da marca |
| Proteção | interpretação: título de seção |
| Garantia de 5 anos na estrutura. | "Garantia: 5 anos na estrutura" |
| Visita gratuita em Niterói; na zona sul do Rio, R$ 150, abatidos se fechar. | "Visita técnica gratuita em Niterói; R$ 150 na zona sul do Rio, abatidos se fechar o projeto" |
| Entrega montada em 30 a 45 dias depois da aprovação. | "entrega montada em 30 a 45 dias depois da aprovação" |
"""


class V356(unittest.TestCase):
    def projeto(self, corpo=None, tabela=TABELA_ATELIE, briefing=BRIEFING_ATELIE, plano=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        r = pathlib.Path(tmp.name)
        (r / "evidencias").mkdir()
        (r / "evidencias" / "briefing.md").write_text(briefing, encoding="utf-8")
        (r / "evidencias" / "sustentacao.md").write_text(tabela, encoding="utf-8")
        if corpo is not None:
            (r / "index.html").write_text(
                f"<!doctype html><html><head><title>Ateliê</title></head><body>{corpo}</body></html>", encoding="utf-8")
        if plano is not None:
            (r / "PLANO.md").write_text(plano, encoding="utf-8")
        return r

    def rodar(self, r, *extra):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = gate.main(["--projeto", str(r), *extra])
        return code, saida.getvalue()

    CORPO = "<h1>Ateliê</h1><section><h2>Proteção</h2><p>Garantia de 5 anos na estrutura.</p></section>"

    # A4: citação copiada tal e qual, atravessando ponto e vírgula e quebra de linha
    def test_a4_citacao_com_ponto_e_virgula_passa(self):
        corpo = self.CORPO + "<p>Visita gratuita em Niterói; na zona sul do Rio, R$ 150, abatidos se fechar.</p>"
        code, out = self.rodar(self.projeto(corpo))
        self.assertEqual(code, 0, out)

    def test_a4_citacao_atravessando_quebra_de_linha_passa(self):
        tabela = TABELA_ATELIE + '| Entrega em 30 a 45 dias. | "Prazo: entrega montada em 30 a 45 dias depois da aprovação" |\n'
        code, out = self.rodar(self.projeto(self.CORPO + "<p>Entrega em 30 a 45 dias.</p>", tabela=tabela))
        self.assertEqual(code, 0, out)

    def test_a4_mutante_citacao_alterada_continua_reprovando(self):
        tabela = TABELA_ATELIE.replace("R$ 150 na zona sul", "R$ 100 na zona sul")
        corpo = self.CORPO + "<p>Visita gratuita em Niterói; na zona sul do Rio, R$ 150, abatidos se fechar.</p>"
        code, out = self.rodar(self.projeto(corpo, tabela=tabela))
        self.assertEqual(code, 1, out)
        self.assertIn("não está no briefing", out)

    def test_a4_citacao_que_junta_duas_frases_que_nao_sao_vizinhas_reprova(self):
        tabela = TABELA_ATELIE + '| Garantia e prazo. | "5 anos na estrutura. Prazo: entrega montada" |\n'
        code, out = self.rodar(self.projeto(self.CORPO + "<p>Garantia e prazo.</p>", tabela=tabela))
        self.assertEqual(code, 1, out)

    # A5: crédito de imagem não é promessa; número em promessa fora do bloco continua exigindo linha
    CREDITO = ('<footer><ul class="creditos"><li>Aparas: “Wood shavings 2” por Shixart1985, '
               '<a rel="license" href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, via Wikimedia Commons.</li></ul></footer>')

    def test_a5_credito_dentro_do_bloco_marcado_passa(self):
        code, out = self.rodar(self.projeto(self.CORPO + self.CREDITO))
        self.assertEqual(code, 0, out)

    def test_a5_credito_com_atributo_data_credito_passa(self):
        c = '<footer><p data-credito>Foto: Maria 2020, CC BY-SA 4.0, via Wikimedia Commons.</p></footer>'
        code, out = self.rodar(self.projeto(self.CORPO + c))
        self.assertEqual(code, 0, out)

    def test_a5_linha_que_e_so_identificador_de_licenca_passa(self):
        code, out = self.rodar(self.projeto(self.CORPO + '<footer><p>CC BY-SA 4.0</p><p>CC0 1.0</p></footer>'))
        self.assertEqual(code, 0, out)

    def test_a5_mutante_promessa_com_numero_fora_do_bloco_reprova(self):
        code, out = self.rodar(self.projeto(self.CORPO + "<p>5 anos de garantia em tudo.</p>" + self.CREDITO))
        self.assertEqual(code, 1, out)
        self.assertIn("5 anos de garantia em tudo", out)

    def test_a5_mutante_promessa_escondida_em_frase_com_licenca_fora_do_bloco_reprova(self):
        code, out = self.rodar(self.projeto(self.CORPO + "<p>Garantia de 10 anos, CC BY 2.0.</p>"))
        self.assertEqual(code, 1, out)

    # A5b: rótulo curto herda a promessa já sustentada da MESMA seção, com o mesmo número e unidade
    BARRA = '<section><h2>Garantia de 5 anos na estrutura</h2><p>Garantia de 5 anos na estrutura.</p><span class="valor">{}</span></section>'

    def test_a5_rotulo_curto_herda_promessa_sustentada_na_mesma_secao(self):
        corpo = "<h1>Ateliê</h1>" + self.BARRA.format("5 anos")
        tabela = TABELA_ATELIE.replace("| Proteção | interpretação: título de seção |\n",
                                       "| Garantia de 5 anos na estrutura | \"Garantia: 5 anos na estrutura\" |\n")
        code, out = self.rodar(self.projeto(corpo, tabela=tabela))
        self.assertEqual(code, 0, out)

    def test_a5_mutante_rotulo_com_outro_numero_nao_herda(self):
        corpo = "<h1>Ateliê</h1>" + self.BARRA.format("10 anos")
        tabela = TABELA_ATELIE.replace("| Proteção | interpretação: título de seção |\n",
                                       "| Garantia de 5 anos na estrutura | \"Garantia: 5 anos na estrutura\" |\n")
        code, out = self.rodar(self.projeto(corpo, tabela=tabela))
        self.assertEqual(code, 1, out)
        self.assertIn("10 anos", out)

    def test_a5_mutante_rotulo_em_outra_secao_nao_herda(self):
        corpo = ("<h1>Ateliê</h1><section><h2>Proteção</h2><p>Garantia de 5 anos na estrutura.</p></section>"
                 '<section><h2>Equipe</h2><span class="valor">5 anos</span></section>')
        code, out = self.rodar(self.projeto(corpo))
        self.assertEqual(code, 1, out)

    # A6: a saída entrega a linha pronta, agrupada por seção
    def test_a6_falta_imprime_linha_pronta_por_secao(self):
        corpo = self.CORPO + "<section><h2>Prazos</h2><p>Desenho em 7 dias.</p></section>"
        code, out = self.rodar(self.projeto(corpo))
        self.assertEqual(code, 1, out)
        self.assertIn('| "Desenho em 7 dias." |', out)
        self.assertIn("Prazos", out)

    def test_a6_aviso_quando_plano_e_sustentacao_divergem_nao_reprova(self):
        plano = ("## d. Copy\n\n| Seção | Frase | Linha do briefing que sustenta |\n|---|---|---|\n"
                 '| Garantia | Garantia de 5 anos na estrutura. | "Garantia: 5 anos na estrutura" |\n')
        r = self.projeto(self.CORPO + "<p>Entrega montada em 30 a 45 dias depois da aprovação.</p>", plano=plano)
        code, out = self.rodar(r)
        self.assertEqual(code, 0, out)
        self.assertIn("AVISO", out)
        self.assertIn("PLANO", out)

    # A3: no passo da copy a página ainda não existe
    def test_a3_sem_pagina_confere_so_a_tabela(self):
        code, out = self.rodar(self.projeto(corpo=None))
        self.assertEqual(code, 0, out)
        self.assertIn("página ainda não existe: conferi só a tabela; rode de novo no passo f", out)
        self.assertNotIn("arquivo ausente", out)

    def test_a3_sem_pagina_ainda_reprova_citacao_falsa(self):
        tabela = TABELA_ATELIE + '| Garantia vitalícia. | "garantia vitalícia em tudo" |\n'
        code, out = self.rodar(self.projeto(corpo=None, tabela=tabela))
        self.assertEqual(code, 1, out)
        self.assertIn("não está no briefing", out)

    def test_a3_sem_pagina_e_sem_tabela_reprova(self):
        r = self.projeto(corpo=None, tabela="# vazio\n")
        code, out = self.rodar(r)
        self.assertEqual(code, 1, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
