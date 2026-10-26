"""3.7.0 (26/10/2026): o passo g do teste de aluno da 3.6.2 levou 35 min (2113 s, 47% da página de 74 min).

Rodada 1 do auditor: 758 s e 21 chamadas; rodada 2: 662 s e 10 chamadas, e ela só devolveu "corrigido ou não".
Aqui se prova, no wave.py:
  1. o orçamento novo: rodada 1 com 8 min e 12 chamadas, rodada 2 (conferência dirigida) com 3 min e 4 chamadas;
  2. rodada 1 sem crítico nem alto não abre rodada 2 de auditor: o ciclo fecha e a entrega segue com as ressalvas;
  3. a conferência (rodada 2) não dá nota nova: `wave.py conferencia` conta o que ficou aberto e diz o comando do fechamento;
  4. `registrar-lote --arquivo` e `gates-lote --arquivo` acham o arquivo relativo à pasta do projeto;
  5. a rodada intermediária sem o gate de movimento fica marcada, para a etapa 5 exigir a rodada final com ele.
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("wave370", pathlib.Path(__file__).with_name("wave.py"))
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)


def ns(**kw):
    return argparse.Namespace(**kw)


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name

    def montar(self, nota=8, origem="subagente", ref_ruim=False, duracao=None, chamadas=None, rodadas=None, quando="2026-10-26T01:00:00"):
        lentes = {n: {"nota": nota, "veredito": "aprovado", "origem": origem, "gosto": "bonito", "quando": quando,
                      "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES}
        if ref_ruim:
            lentes["comparacao-referencias"].update(veredito="reprovado", gosto="correto", eixos_abaixo=["composicao", "tipografia"])
        if duracao is not None:
            lentes["cro-auditor"]["duracao_min"] = duracao
        if chamadas is not None:
            lentes["cro-auditor"]["chamadas"] = chamadas
        d = {"lentes": lentes, "gates": {n: {"exit": 0, "detalhe": "ok", "quando": quando} for n in wave.GATES}}
        if rodadas:
            d["rodadas"] = rodadas
        wave.salvar(self.projeto, d)

    def rodada(self, **kw):
        base = dict(projeto=self.projeto, criticos=0, altos=0, regressoes=0, pendencias_do_usuario=0)
        base.update(kw)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = wave.cmd_rodada(ns(**base))
        return code, out.getvalue()


class Orcamento370(Base):
    def test_orcamento_novo_das_duas_rodadas(self):
        self.assertEqual(wave.ORCAMENTO, {1: (8, 12), 2: (3, 4)})

    def test_rodada_1_acima_de_8_min_ou_12_chamadas_avisa(self):
        self.montar(duracao=12.6, chamadas=21)   # a rodada 1 da 3.6.2: 758 s e 21 chamadas
        _, out = self.rodada(altos=1)
        self.assertIn("AVISO", out)
        self.assertRegex(out, r"8 min")
        self.assertRegex(out, r"12 chamadas")

    def test_rodada_1_dentro_do_teto_nao_avisa(self):
        self.montar(duracao=8, chamadas=12)
        _, out = self.rodada(altos=1)
        self.assertNotIn("orçamento", out)

    def test_rodada_2_nao_cobra_o_gasto_da_rodada_1_das_notas_mantidas(self):
        # As lentes da rodada 1 guardam 8 min e 12 chamadas; na rodada 2 elas são notas mantidas e não entram na conta.
        self.montar(duracao=8, chamadas=12, rodadas=[{"n": 1, "quando": "2026-10-26T01:30:00", "media": 8, "criticos": 1, "altos": 2, "notas": {}}])
        _, out = self.rodada()
        self.assertNotIn("passou do orçamento", out)

    def test_rodada_2_cobra_o_gasto_da_conferencia(self):
        self.montar(rodadas=[{"n": 1, "quando": "2026-10-26T01:30:00", "media": 8, "criticos": 1, "altos": 2, "notas": {}}])
        d = wave.carregar(self.projeto)
        d["conferencias"] = [{"rodada": 2, "quando": "2026-10-26T01:40:00", "duracao_min": 11, "chamadas": 10}]
        wave.salvar(self.projeto, d)
        _, out = self.rodada()
        self.assertIn("passou do orçamento", out)
        self.assertRegex(out, r"3 min")
        self.assertRegex(out, r"4 chamadas")


class SemRodada2(Base):
    """Item 1d: sem crítico nem alto na rodada 1, não há rodada 2 de auditor."""

    def test_rodada_1_sem_critico_nem_alto_fecha_sem_rodada_2(self):
        self.montar(nota=6.5)
        code, out = self.rodada()
        self.assertEqual(code, 0, out)
        r = wave.carregar(self.projeto)["rodadas"][-1]
        self.assertTrue(r.get("sem_rodada_2"))
        self.assertIn(r["desfecho"], ("ENTREGA", "ENTREGA_COM_RESSALVAS"))
        self.assertIn("sem rodada 2 de auditor", out.lower())
        self.assertIn("rodar-gates.mjs", out)

    def test_referencias_abaixo_sem_critico_nem_alto_entrega_com_ressalvas_e_lista_os_eixos(self):
        self.montar(ref_ruim=True)
        code, out = self.rodada()
        self.assertEqual(code, 0, out)
        r = wave.carregar(self.projeto)["rodadas"][-1]
        self.assertEqual(r["desfecho"], "ENTREGA_COM_RESSALVAS")
        self.assertTrue(r.get("sem_rodada_2"))
        self.assertTrue(any("comparacao-referencias" in x and "composicao" in x for x in r["ressalvas"]), r["ressalvas"])

    def test_alto_na_rodada_1_continua_abrindo_a_conferencia(self):
        self.montar(nota=7)   # média abaixo do piso de 8: o alto segura o ciclo
        code, out = self.rodada(altos=1)
        self.assertEqual(code, 1, out)
        self.assertEqual(wave.carregar(self.projeto)["rodadas"][-1]["desfecho"], "CONTINUA")

    def test_continua_da_rodada_1_diz_os_comandos_da_conferencia(self):
        for kw in (dict(criticos=1), dict(altos=1)):
            self.montar(nota=7)
            code, out = self.rodada(**kw)
            self.assertEqual(code, 1, out)
            self.assertIn("pacote-auditoria.py", out)
            self.assertIn("--rodada 2", out)
            self.assertIn("conferencia --arquivo auditoria/resposta-rodada-2.json", out)

    def test_critico_na_rodada_1_continua(self):
        self.montar()
        code, _ = self.rodada(criticos=1)
        self.assertEqual(code, 1)

    def test_alto_que_so_o_cliente_resolve_nao_abre_rodada_2(self):
        self.montar()
        code, out = self.rodada(altos=2, pendencias_do_usuario=2)
        self.assertEqual(code, 0, out)
        self.assertTrue(wave.carregar(self.projeto)["rodadas"][-1].get("sem_rodada_2"))

    def test_autoavaliacao_continua_pendente(self):
        self.montar(origem="autoavaliacao")
        code, _ = self.rodada()
        self.assertEqual(code, 1)
        self.assertEqual(wave.carregar(self.projeto)["rodadas"][-1]["desfecho"], "AUDITORIA_PENDENTE")

    def test_sem_resposta_de_gosto_continua(self):
        self.montar()
        d = wave.carregar(self.projeto)
        d["lentes"]["comparacao-referencias"].pop("gosto")
        wave.salvar(self.projeto, d)
        code, _ = self.rodada()
        self.assertEqual(code, 1)


class Conferencia(Base):
    """Item 1c: a rodada 2 confere os achados abertos e não dá nota nova."""

    def abertos(self):
        aud = pathlib.Path(self.projeto, "auditoria")
        aud.mkdir(exist_ok=True)
        (aud / "abertos-rodada-1.json").write_text(json.dumps({"abertos": [
            {"n": 1, "lente": "responsive-auditor", "severidade": "critico", "item": "toque de 30 px no menu"},
            {"n": 2, "lente": "content-auditor", "severidade": "alto", "item": "regra inventada"},
            {"n": 3, "lente": "assets-auditor", "severidade": "alto", "item": "fotos sem autorização"},
        ]}), encoding="utf-8")

    def resposta(self, itens, extra=None):
        doc = {"rodada": 2, "achados": itens, "duracao_min": 2.5, "chamadas": 4}
        doc.update(extra or {})
        p = pathlib.Path(self.projeto, "auditoria", "resposta-rodada-2.json")
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        return "auditoria/resposta-rodada-2.json"

    def conferir(self, arquivo, **kw):
        out = io.StringIO()
        base = dict(projeto=self.projeto, arquivo=arquivo, duracao_min=None, chamadas=None)
        base.update(kw)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = wave.cmd_conferencia(ns(**base))
        return code, out.getvalue()

    def test_conta_o_que_ficou_aberto_e_diz_o_comando_do_fechamento(self):
        self.montar(rodadas=[{"n": 1, "quando": "2026-10-26T01:30:00", "media": 7, "criticos": 1, "altos": 2, "notas": {}, "desfecho": "CONTINUA"}])
        self.abertos()
        arq = self.resposta([
            {"n": 1, "estado": "corrigido", "evidencia": "menu com 44 px no print novo"},
            {"n": 2, "estado": "não corrigido", "evidencia": "a frase segue no dist/index.html linha 210"},
            {"n": 3, "estado": "regressão", "gravidade": "medio", "evidencia": "inicial em círculo cortada em 320"},
        ])
        cwd = os.getcwd()
        os.chdir(tempfile.gettempdir())   # o arquivo é relativo ao projeto, não à pasta de onde se chama
        try:
            code, out = self.conferir(arq)
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0, out)
        self.assertIn("--criticos 0 --altos 1 --regressoes 1", out)
        c = wave.carregar(self.projeto)["conferencias"][-1]
        self.assertEqual((c["duracao_min"], c["chamadas"]), (2.5, 4))
        self.assertEqual(c["abertos"]["altos"], 1)

    def test_achado_que_o_auditor_nao_conferiu_fica_aberto(self):
        self.montar(rodadas=[{"n": 1, "quando": "2026-10-26T01:30:00", "media": 7, "criticos": 1, "altos": 2, "notas": {}, "desfecho": "CONTINUA"}])
        self.abertos()
        arq = self.resposta([{"n": 2, "estado": "corrigido", "evidencia": "frase removida, diff linha 210"},
                             {"n": 3, "estado": "corrigido", "evidencia": "inicial no lugar da foto"}])
        code, out = self.conferir(arq)
        self.assertEqual(code, 0, out)
        self.assertIn("--criticos 1 --altos 0", out)
        self.assertIn("não conferido", out)

    def test_estado_invalido_nao_grava_nada(self):
        self.montar(rodadas=[{"n": 1, "quando": "2026-10-26T01:30:00", "media": 7, "criticos": 1, "altos": 2, "notas": {}, "desfecho": "CONTINUA"}])
        self.abertos()
        arq = self.resposta([{"n": 1, "estado": "quase", "evidencia": "olhei rapidamente o print"}])
        code, out = self.conferir(arq)
        self.assertEqual(code, 2, out)
        self.assertNotIn("conferencias", wave.carregar(self.projeto))

    def test_nota_na_conferencia_e_ignorada_com_aviso(self):
        self.montar(rodadas=[{"n": 1, "quando": "2026-10-26T01:30:00", "media": 7, "criticos": 1, "altos": 2, "notas": {}, "desfecho": "CONTINUA"}])
        self.abertos()
        arq = self.resposta([{"n": i, "estado": "corrigido", "evidencia": "conferido no print novo"} for i in (1, 2, 3)],
                            extra={"score": 9.1})
        code, out = self.conferir(arq)
        self.assertEqual(code, 0, out)
        self.assertIn("sem nota nova", out)
        self.assertEqual(wave.carregar(self.projeto)["lentes"]["cro-auditor"]["nota"], 8)

    def test_sem_rodada_1_fechada_nao_ha_conferencia(self):
        self.montar()
        self.abertos()
        arq = self.resposta([{"n": 1, "estado": "corrigido", "evidencia": "conferido no print novo"}])
        code, out = self.conferir(arq)
        self.assertEqual(code, 2, out)

    def test_linha_de_comando_tem_conferencia(self):
        import subprocess, sys
        r = subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name("wave.py")), "conferencia", "--help"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--arquivo", r.stdout)


class ArquivoRelativoAoProjeto(Base):
    def test_registrar_lote_acha_o_arquivo_pela_pasta_do_projeto(self):
        self.montar()
        aud = pathlib.Path(self.projeto, "auditoria")
        aud.mkdir(exist_ok=True)
        blocos = [{"lente": n, "aprovado": True, "score": 8, "gosto": "bonito",
                   "achados": [{"item": "olhei o pacote", "severidade": "baixo", "evidencia": "print 1440", "fix": "nada"}]} for n in wave.LENTES]
        (aud / "resposta-rodada-1.json").write_text(json.dumps(blocos), encoding="utf-8")
        cwd = os.getcwd()
        os.chdir(tempfile.gettempdir())
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = wave.cmd_registrar_lote(ns(projeto=self.projeto, arquivo="auditoria/resposta-rodada-1.json",
                                                  origem="subagente", duracao_min=None, chamadas=None))
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0)

    def test_gates_lote_acha_o_arquivo_pela_pasta_do_projeto(self):
        g = pathlib.Path(self.projeto, "gates")
        g.mkdir()
        (g / "_wave-r1.json").write_text(json.dumps({"gates": [{"nome": "texto", "exit": 0, "detalhe": "ok"}]}), encoding="utf-8")
        cwd = os.getcwd()
        os.chdir(tempfile.gettempdir())
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = wave.cmd_gates_lote(ns(projeto=self.projeto, arquivo="gates/_wave-r1.json"))
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0)


class MovimentoPulado(Base):
    """Item 2: a rodada intermediária sem o gate de movimento fica marcada na wave."""

    def lote(self, doc):
        p = pathlib.Path(self.projeto, "lote.json")
        p.write_text(json.dumps(doc), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return wave.cmd_gates_lote(ns(projeto=self.projeto, arquivo=str(p)))

    def test_pulado_marca_e_rodada_com_ele_limpa(self):
        self.montar()
        self.assertEqual(self.lote({"gates": [{"nome": "texto", "exit": 0, "detalhe": "ok"}],
                                    "pulados": [{"nome": "movimento", "motivo": "--sem-movimento: animação igual à da rodada 1"}]}), 0)
        g = wave.carregar(self.projeto)["gates"]["movimento"]
        self.assertEqual(g["exit"], 0)
        self.assertIn("pulado_em", g)
        self.assertIn("--sem-movimento", g["pulado_motivo"])
        self.assertEqual(self.lote({"gates": [{"nome": "movimento", "exit": 0, "detalhe": "rodou"}]}), 0)
        self.assertNotIn("pulado_em", wave.carregar(self.projeto)["gates"]["movimento"])

    def test_checar_avisa_que_falta_a_rodada_final_com_movimento(self):
        self.montar()
        self.lote({"gates": [{"nome": "texto", "exit": 0, "detalhe": "ok"}], "pulados": [{"nome": "movimento", "motivo": "--sem-movimento"}]})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = wave.cmd_checar(ns(projeto=self.projeto, caminho="criar"))
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("movimento", out.getvalue())
        self.assertIn("rodada final", out.getvalue())

    def test_pulado_desconhecido_e_erro(self):
        self.montar()
        self.assertEqual(self.lote({"gates": [{"nome": "texto", "exit": 0}], "pulados": [{"nome": "inexistente"}]}), 2)


if __name__ == "__main__":
    unittest.main()
