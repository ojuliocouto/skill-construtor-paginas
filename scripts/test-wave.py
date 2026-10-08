"""Controles do ciclo com entradas reais do registro, sem serviços externos."""
import argparse
import contextlib
import importlib.util
import io
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("wave", pathlib.Path(__file__).with_name("wave.py"))
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)


class Ciclo(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name

    def executar(self, nota=8, criticos=0, regressoes=0, gates=True, altos=1, pendencias=0, origem="subagente", gosto="bonito"):
        lentes = {n: {"nota": nota, "veredito": "aprovado", "origem": origem,
                      "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES}
        if gosto:
            lentes["comparacao-referencias"]["gosto"] = gosto
        wave.salvar(self.projeto, {
            "lentes": lentes,
            "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES} if gates else {},
        })
        with contextlib.redirect_stdout(io.StringIO()):
            return wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=criticos, altos=altos,
                                                      regressoes=regressoes, pendencias_do_usuario=pendencias))

    def test_positivo_piso(self):
        self.assertEqual(self.executar(), 0)

    def test_negativo_critico(self):
        self.assertEqual(self.executar(criticos=1), 1)

    def test_negativo_regressao(self):
        self.assertEqual(self.executar(regressoes=1), 1)

    def test_primeira_rodada_baixa_orienta_sem_excecao(self):
        self.assertEqual(self.executar(nota=6), 1)

    def test_nota_infinita_nao_aprova(self):
        self.assertNotEqual(self.executar(nota=float("inf")), 0)

    def test_contagem_negativa_nao_aprova(self):
        self.assertNotEqual(self.executar(criticos=-1), 0)

    def test_alto_que_depende_do_cliente_nao_segura_o_ciclo(self):
        # Relatorio do aluno: numero do WhatsApp e prova social so a cliente tem. Sem o campo,
        # "zero alto" nunca fica verdadeiro e so o teto de rodadas solta.
        self.assertEqual(self.executar(nota=6, altos=2, pendencias=2), 0)

    def test_pendencia_do_usuario_nao_apaga_alto_de_verdade(self):
        self.assertEqual(self.executar(nota=6, altos=3, pendencias=2), 1)

    def test_pendencia_maior_que_altos_e_erro(self):
        self.assertNotEqual(self.executar(nota=6, altos=1, pendencias=2), 0)

    def test_pendencia_vai_para_o_historico(self):
        self.executar(nota=6, altos=2, pendencias=2)
        rodada = wave.carregar(self.projeto)["rodadas"][-1]
        self.assertEqual(rodada.get("pendencias_do_usuario"), 2)

    def test_sem_gates_nao_entrega(self):
        self.assertNotEqual(self.executar(gates=False), 0)

    # v3: a nona lente compara a página com as referências printadas no passo b.
    def test_nona_lente_comparacao_com_referencias_existe(self):
        self.assertIn("comparacao-referencias", wave.LENTES)
        self.assertEqual(len(wave.LENTES), 9)
        self.assertIn("referencias", wave.GATES)

    def test_abaixo_das_referencias_volta_pro_plano_mesmo_com_nota_alta(self):
        wave.salvar(self.projeto, {
            "lentes": {n: {"nota": 9, "veredito": "aprovado", "origem": "subagente",
                           "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES},
            "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES},
        })
        d = wave.carregar(self.projeto)
        d["lentes"]["comparacao-referencias"]["veredito"] = "reprovado"
        d["lentes"]["comparacao-referencias"]["gosto"] = "correto"
        wave.salvar(self.projeto, d)
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=0, altos=0,
                                                      regressoes=0, pendencias_do_usuario=0))
        self.assertEqual(code, 1)
        self.assertIn("plano visual", saida.getvalue().lower())

    def test_comparacao_com_referencias_nao_aceita_nao_aplicavel(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code = wave.cmd_registrar(argparse.Namespace(projeto=self.projeto, lente="comparacao-referencias",
                                                         veredito="nao_aplicavel", nota=None,
                                                         achados="Não comparei porque não tinha referência"))
        self.assertEqual(code, 2)

    def test_caminho_clonar_nao_exige_gate_de_referencias(self):
        wave.salvar(self.projeto, {
            "lentes": {n: {"nota": 9, "veredito": "aprovado", "origem": "subagente",
                           "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES},
            "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES if n != "referencias"},
        })
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wave.cmd_checar(argparse.Namespace(projeto=self.projeto, caminho="clonar")), 0)
            self.assertEqual(wave.cmd_checar(argparse.Namespace(projeto=self.projeto, caminho="criar")), 1)

    # Auditoria da v3 (02/10/2026): autoavaliação de 9 lentes deu média 7,78 e "tells 0"; o auditor
    # independente deu 5,5 e achou 5 graves. Nota de quem construiu não libera entrega.
    def test_autoavaliacao_nao_libera_entrega(self):
        saida = io.StringIO()
        wave.salvar(self.projeto, {
            "lentes": {n: {"nota": 9, "veredito": "aprovado", "origem": "autoavaliacao", "gosto": "bonito",
                           "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES},
            "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES},
        })
        with contextlib.redirect_stdout(saida):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=0, altos=0,
                                                      regressoes=0, pendencias_do_usuario=0))
        self.assertNotEqual(code, 0)
        self.assertIn("independente", saida.getvalue().lower())

    def test_lente_sem_origem_conta_como_autoavaliacao(self):
        self.assertNotEqual(self.executar(nota=9, altos=0, origem=None), 0)

    def test_subagente_independente_libera(self):
        self.assertEqual(self.executar(nota=9, altos=0, origem="subagente"), 0)

    def test_registrar_grava_a_origem(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = wave.cmd_registrar(argparse.Namespace(projeto=self.projeto, lente="design-critic", veredito="aprovado",
                                                         nota=8.0, origem="subagente",
                                                         achados="Olhei o print 1440 e contei os tells"))
        self.assertEqual(code, 0)
        self.assertEqual(wave.carregar(self.projeto)["lentes"]["design-critic"]["origem"], "subagente")

    def test_gates_novos_da_auditoria_da_v3(self):
        for g in ("simetria", "texto", "verdade", "publicacao"):
            self.assertIn(g, wave.GATES, g)

    def test_gates_novos_da_auditoria_da_v4(self):
        for g in ("movimento", "composicao", "imagens"):
            self.assertIn(g, wave.GATES, g)

    def test_gates_da_etapa_plano(self):
        for g in ("plano", "rastreamento"):
            self.assertIn(g, wave.GATES, g)
        self.assertIn("plano", wave.gates_exigidos("criar"))
        self.assertNotIn("plano", wave.gates_exigidos("clonar"))
        self.assertIn("rastreamento", wave.gates_exigidos("clonar"))

    # v3.5 (04/10/2026): ritmo e animação viraram gates exigidos; o clone fiel copia a composição
    # da original e não responde por eles.
    def test_gates_do_padrao_da_v7(self):
        for g in ("ritmo", "animacao"):
            self.assertIn(g, wave.GATES, g)
            self.assertIn(g, wave.gates_exigidos("criar"))
            self.assertIn(g, wave.gates_exigidos("melhorar"))
            self.assertNotIn(g, wave.gates_exigidos("clonar"))

    # Auditoria da v5 (03/10/2026): 7,0, "correta, mas vazia; o dono não chamaria de foda". A
    # régua do dono depois da SobrAI (9,05 nas lentes e "que página FEIA") é a pergunta "isso é
    # bonito ou só está correto?", e nenhum registro a fazia. A nona lente responde por escrito.
    def registrar_ref(self, **kw):
        base = dict(projeto=self.projeto, lente="comparacao-referencias", veredito="aprovado", nota=8.5,
                    origem="subagente", achados="Comparei a dobra com Kins, Tia e Parsley lado a lado")
        base.update(kw)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return wave.cmd_registrar(argparse.Namespace(**base))

    def test_comparacao_sem_resposta_de_gosto_e_erro(self):
        self.assertEqual(self.registrar_ref(), 2)

    def test_so_correto_nao_aprova(self):
        self.assertEqual(self.registrar_ref(gosto="correto"), 2)

    def test_bonito_aprovado_grava(self):
        self.assertEqual(self.registrar_ref(gosto="bonito"), 0)
        self.assertEqual(wave.carregar(self.projeto)["lentes"]["comparacao-referencias"]["gosto"], "bonito")

    def test_pagina_so_correta_volta_ao_plano(self):
        saida = io.StringIO()
        self.executar(nota=9, altos=0, gosto="correto")
        with contextlib.redirect_stdout(saida):
            code = self.executar(nota=9, altos=0, gosto="correto")
        self.assertEqual(code, 1)

    def test_rodada_sem_a_pergunta_de_gosto_nao_entrega(self):
        self.assertEqual(self.executar(nota=9, altos=0, gosto=None), 1)


class TetoDeDuasRodadas(unittest.TestCase):
    """v3.5.4: o ciclo fecha SEMPRE na segunda rodada; terceira só se a pessoa pedir."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name

    def preparar(self, nota=6.0, origem="subagente"):
        wave.salvar(self.projeto, {
            "lentes": {n: {"nota": nota, "veredito": "aprovado", "origem": origem, "gosto": "bonito",
                           "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES},
            "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES},
            "rodadas": [],
        })

    def rodar(self, criticos=0, altos=3, regressoes=0, extra=False):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(saida):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=criticos, altos=altos,
                                                      regressoes=regressoes, pendencias_do_usuario=0,
                                                      rodada_extra_pedida=extra))
        return code, saida.getvalue()

    def test_teto_e_dois(self):
        self.assertEqual(wave.TETO_RODADAS, 2)

    def test_primeira_rodada_com_alto_continua(self):
        self.preparar()
        code, _ = self.rodar()
        self.assertEqual(code, 1)

    def test_segunda_rodada_fecha_com_ressalvas_e_nota_real(self):
        self.preparar()
        self.rodar()
        code, texto = self.rodar()
        self.assertEqual(code, 0)
        self.assertIn("ENTREGA COM RESSALVAS", texto)
        self.assertIn("6.00", texto)

    def test_ressalvas_listam_o_que_sobrou(self):
        self.preparar()
        self.rodar()
        code, texto = self.rodar(altos=3)
        self.assertIn("3 alto(s)", texto)
        self.assertIn("design-critic", texto)

    def test_segunda_rodada_com_critico_nao_entrega(self):
        self.preparar()
        self.rodar()
        code, texto = self.rodar(criticos=1)
        self.assertEqual(code, 1)
        self.assertIn("NÃO ENTREGAR: crítico aberto", texto)
        self.assertNotIn("RESSALVAS", texto)

    def test_segunda_rodada_com_regressao_nao_entrega(self):
        self.preparar()
        self.rodar()
        code, texto = self.rodar(regressoes=1)
        self.assertEqual(code, 1)
        self.assertIn("NÃO ENTREGAR", texto)

    def test_segunda_rodada_com_autoavaliacao_continua_pendente(self):
        self.preparar(origem="autoavaliacao")
        self.rodar()
        code, texto = self.rodar()
        self.assertEqual(code, 1)
        self.assertIn("AUDITORIA INDEPENDENTE PENDENTE", texto)

    def test_segunda_rodada_com_referencias_reprovada_entrega_com_ressalvas_e_lista_a_lente(self):
        # A30: na última rodada, sem crítico nem regressão, a lente de referências reprovada vira RESSALVA (não "volta ao plano")
        self.preparar()
        d = wave.carregar(self.projeto)
        d["lentes"]["comparacao-referencias"].update(veredito="reprovado", gosto="correto", eixos_abaixo=["imagem"])
        wave.salvar(self.projeto, d)
        self.rodar()
        code, texto = self.rodar()
        self.assertEqual(code, 0, texto)
        self.assertIn("ENTREGA COM RESSALVAS", texto)
        self.assertIn("comparacao-referencias", texto)
        self.assertNotIn("VOLTA PRO PLANO VISUAL", texto)

    def test_terceira_rodada_sem_pedido_e_recusada_e_nao_grava(self):
        self.preparar()
        self.rodar()
        self.rodar()
        code, texto = self.rodar()
        self.assertEqual(code, 2)
        self.assertIn("--rodada-extra-pedida", texto)
        self.assertEqual(len(wave.carregar(self.projeto)["rodadas"]), 2)

    def test_terceira_rodada_pedida_roda_fecha_e_fica_registrada(self):
        self.preparar()
        self.rodar()
        self.rodar()
        code, texto = self.rodar(extra=True)
        self.assertEqual(code, 0)
        self.assertIn("ENTREGA COM RESSALVAS", texto)
        d = wave.carregar(self.projeto)
        self.assertEqual(len(d["rodadas"]), 3)
        self.assertTrue(d["rodadas"][-1].get("rodada_extra_pedida"))

    def test_quarta_rodada_nunca_mesmo_com_pedido(self):
        self.preparar()
        self.rodar()
        self.rodar()
        self.rodar(extra=True)
        code, _ = self.rodar(extra=True)
        self.assertEqual(code, 2)

    def test_flag_existe_na_linha_de_comando(self):
        import subprocess, sys
        fonte = pathlib.Path(__file__).with_name("wave.py").read_text(encoding="utf-8")
        self.assertIn("--rodada-extra-pedida", fonte)


class TerceiraLeva(unittest.TestCase):
    """A26 (lente de referências não manda reconstruir sozinha) e A27 (orçamento do auditor)."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name

    def montar(self, ref_reprovada=False, eixos=None, duracao=None, chamadas=None, rodadas_antes=0):
        lentes = {n: {"nota": 9, "veredito": "aprovado", "origem": "subagente", "gosto": "bonito",
                      "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES}
        if ref_reprovada:
            lentes["comparacao-referencias"].update(veredito="reprovado", gosto="correto")
            if eixos:
                lentes["comparacao-referencias"]["eixos_abaixo"] = eixos
        if duracao is not None:
            lentes["cro-auditor"]["duracao_min"] = duracao
        if chamadas is not None:
            lentes["cro-auditor"]["chamadas"] = chamadas
        dados = {"lentes": lentes, "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES}}
        if rodadas_antes:
            dados["rodadas"] = [{"n": i + 1, "media": 7.0, "criticos": 0, "altos": 1, "notas": {}} for i in range(rodadas_antes)]
        wave.salvar(self.projeto, dados)

    def rodar(self):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=0, altos=0, regressoes=0, pendencias_do_usuario=0))
        return code, saida.getvalue()

    # --- A26
    def test_lente_de_referencias_reprovada_lista_os_eixos_e_manda_corrigir_a_pagina(self):
        self.montar(ref_reprovada=True, eixos=["tipografia", "imagem"])
        code, out = self.rodar()
        self.assertEqual(code, 1)
        self.assertIn("tipografia", out)
        self.assertIn("imagem", out)
        self.assertNotIn("composicao", out.split("EIXOS")[-1] if "EIXOS" in out else "")
        self.assertRegex(out.lower(), r"corrija esses eixos na página")
        self.assertNotRegex(out, r"(?i)refa[cç]a o plano a partir das refer[eê]ncias e reconstrua")
        self.assertRegex(out.lower(), r"ciclo novo: só se você pedir")

    def test_lente_reprovada_sem_eixos_pede_os_quatro_e_continua_barrando_a_entrega(self):
        self.montar(ref_reprovada=True)
        code, out = self.rodar()
        self.assertEqual(code, 1)
        for eixo in ("composicao", "tipografia", "imagem", "ritmo"):
            self.assertIn(eixo, out)

    def test_registrar_aceita_e_valida_eixos_abaixo(self):
        base = dict(projeto=self.projeto, lente="comparacao-referencias", veredito="reprovado", nota=5.0, origem="subagente",
                    gosto="correto", achados="Comparei a dobra com Kins, Tia e Parsley lado a lado")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(wave.cmd_registrar(argparse.Namespace(**base, eixos_abaixo="tipografia,imagem")), 0)
            self.assertEqual(wave.cmd_registrar(argparse.Namespace(**base, eixos_abaixo="cor")), 2)
        self.assertEqual(wave.carregar(self.projeto)["lentes"]["comparacao-referencias"]["eixos_abaixo"], ["tipografia", "imagem"])

    def test_o_que_ja_barrava_continua_barrando(self):
        # crítico, regressão e auditoria independente pendente seguem barrando a entrega
        self.montar()
        for kw in (dict(criticos=2, regressoes=0), dict(criticos=0, regressoes=1)):
            with contextlib.redirect_stdout(io.StringIO()):
                code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, altos=0, pendencias_do_usuario=0, **kw))
            self.assertEqual(code, 1, kw)
            self.montar()

    # --- A27
    def registrar(self, **extra):
        base = dict(projeto=self.projeto, lente="cro-auditor", veredito="aprovado", nota=8.0, origem="subagente",
                    achados="Li o pacote e conferi o botão principal nas duas telas", gosto=None)
        base.update(extra)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return wave.cmd_registrar(argparse.Namespace(**base))

    def test_registrar_guarda_duracao_e_chamadas(self):
        self.assertEqual(self.registrar(duracao_min=12.5, chamadas=22), 0)
        l = wave.carregar(self.projeto)["lentes"]["cro-auditor"]
        self.assertEqual((l["duracao_min"], l["chamadas"]), (12.5, 22))
        self.assertEqual(self.registrar(duracao_min=-1, chamadas=3), 2)
        self.assertEqual(self.registrar(duracao_min=5, chamadas=-3), 2)

    def test_rodada_1_acima_do_orcamento_avisa_sem_reprovar(self):
        self.montar(duracao=51, chamadas=113)
        code, out = self.rodar()
        self.assertIn("AVISO", out)
        self.assertIn("51", out)
        self.assertIn("113", out)
        self.assertRegex(out, r"15 min")
        self.assertRegex(out, r"30 chamadas")
        self.assertNotIn("ERRO", out)

    def test_dentro_do_orcamento_nao_avisa(self):
        self.montar(duracao=14, chamadas=30)
        _, out = self.rodar()
        self.assertNotIn("orçamento", out)

    def test_rodada_2_tem_orcamento_menor(self):
        self.montar(duracao=10, chamadas=20, rodadas_antes=1)
        _, out = self.rodar()
        self.assertIn("orçamento", out)
        self.assertRegex(out, r"8 min")
        self.assertRegex(out, r"15 chamadas")

    def test_sem_informar_nada_nao_avisa_nem_quebra(self):
        self.montar()
        code, out = self.rodar()
        self.assertNotIn("orçamento", out)


class NotasMantidasEDesfecho(unittest.TestCase):
    """A31 (a): na rodada 2 só as lentes com achado corrigido ou regressão ganham nota nova; as outras mostram 'nota da rodada 1 mantida'.
    (b): cada rodada grava o desfecho para o gate-etapas.py ler."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name

    def rodar(self, **kw):
        base = dict(projeto=self.projeto, criticos=0, altos=0, regressoes=0, pendencias_do_usuario=0)
        base.update(kw)
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = wave.cmd_rodada(argparse.Namespace(**base))
        return code, saida.getvalue()

    def montar(self, quando):
        lentes = {n: {"nota": 7, "veredito": "aprovado", "origem": "subagente", "gosto": "bonito", "quando": quando,
                      "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES}
        dados = wave.carregar(self.projeto)
        dados["lentes"] = lentes
        dados["gates"] = {n: {"exit": 0, "detalhe": "ok"} for n in wave.GATES}
        wave.salvar(self.projeto, dados)

    def test_rodada_2_marca_as_notas_mantidas_e_nao_diz_que_mediu_de_novo(self):
        self.montar("2026-10-08T10:00:00")
        self.rodar(altos=3)
        d = wave.carregar(self.projeto)
        for n in ("cro-auditor", "a11y-auditor"):          # só duas lentes foram medidas de novo
            d["lentes"][n]["quando"] = "2999-01-01T00:00:00"
            d["lentes"][n]["nota"] = 8
        wave.salvar(self.projeto, d)
        code, out = self.rodar(altos=1)
        self.assertIn("nota da rodada 1 mantida", out)
        self.assertIn("2 lente(s) medida(s) de novo", out)
        self.assertNotIn("cro-auditor", out.split("nota da rodada 1 mantida")[1].split("\n")[0])
        self.assertRegex(out, r"média da rodada 2 .*mistura")
        h = wave.carregar(self.projeto)["rodadas"][-1]
        self.assertEqual(len(h["mantidas"]), len(wave.LENTES) - 2)

    def test_rodada_1_nao_tem_nota_mantida(self):
        self.montar("2026-10-08T10:00:00")
        _, out = self.rodar(altos=3)
        self.assertNotIn("mantida", out)

    def test_cada_rodada_grava_o_desfecho(self):
        self.montar("2026-10-08T10:00:00")
        self.rodar(criticos=2, altos=3)
        self.rodar(criticos=1, altos=3)
        h = wave.carregar(self.projeto)["rodadas"]
        self.assertEqual(h[0]["desfecho"], "CONTINUA")
        self.assertEqual(h[1]["desfecho"], "NAO_ENTREGAR")

    def test_entrega_com_ressalvas_grava_a_lista(self):
        self.montar("2026-10-08T10:00:00")
        self.rodar(altos=3)
        d = wave.carregar(self.projeto)
        d["lentes"]["comparacao-referencias"].update(veredito="reprovado", gosto="correto", eixos_abaixo=["imagem"])
        wave.salvar(self.projeto, d)
        code, _ = self.rodar(altos=3)
        h = wave.carregar(self.projeto)["rodadas"][-1]
        self.assertEqual((code, h["desfecho"]), (0, "ENTREGA_COM_RESSALVAS"))
        self.assertTrue(any("comparacao-referencias" in r for r in h["ressalvas"]))


class CasoRealA30(unittest.TestCase):
    """A30: no teste real, a rodada 2 (1 crítico, 2 regressões) imprimiu VOLTA PRO PLANO VISUAL em vez de NÃO ENTREGAR."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name
        lentes = {n: {"nota": 7, "veredito": "aprovado", "origem": "subagente", "gosto": "bonito",
                      "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES}
        lentes["comparacao-referencias"].update(veredito="reprovado", gosto="correto", nota=5, eixos_abaixo=["tipografia", "imagem"])
        wave.salvar(self.projeto, {"lentes": lentes, "gates": {n: {"exit": 0, "detalhe": "ok"} for n in wave.GATES}})

    def rodada(self, criticos, altos, pend, reg):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=criticos, altos=altos, regressoes=reg, pendencias_do_usuario=pend))
        return code, saida.getvalue()

    def test_numeros_do_caso_real_rodada_2_e_nao_entregar_e_nunca_volta_ao_plano(self):
        c1, o1 = self.rodada(2, 9, 3, 0)
        self.assertEqual(c1, 1)
        self.assertIn("CONTINUA", o1)
        self.assertIn("EIXOS a corrigir: tipografia, imagem", o1)
        self.assertNotIn("VOLTA PRO PLANO", o1)
        c2, o2 = self.rodada(1, 6, 4, 2)
        self.assertEqual(c2, 1)
        self.assertIn("NÃO ENTREGAR", o2)
        self.assertNotIn("VOLTA PRO PLANO", o2)
        self.assertNotRegex(o2, r"(?i)refa[cç]a o plano a partir")

    def test_ultima_rodada_sem_critico_nem_regressao_vira_ressalva_com_a_lente_e_os_eixos(self):
        self.rodada(2, 9, 3, 0)
        c2, o2 = self.rodada(0, 3, 0, 0)
        self.assertEqual(c2, 0, o2)
        self.assertIn("ENTREGA COM RESSALVAS", o2)
        self.assertIn("comparacao-referencias", o2)
        self.assertIn("tipografia, imagem", o2)
        self.assertNotIn("VOLTA PRO PLANO", o2)

    def test_so_uma_regressao_na_ultima_rodada_tambem_e_nao_entregar(self):
        self.rodada(0, 3, 0, 0)
        c2, o2 = self.rodada(0, 3, 0, 1)
        self.assertEqual(c2, 1)
        self.assertIn("NÃO ENTREGAR", o2)
        self.assertIn("regressão", o2)


class CincoEixosEReabrir(unittest.TestCase):
    """3.5.9: N23 (acabamento é o quinto eixo) e N27 (mudança grande do dono entre as rodadas reabre a rodada 1, uma vez)."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name

    def montar(self, nota=7, gosto="bonito"):
        lentes = {n: {"nota": nota, "veredito": "aprovado", "origem": "subagente", "gosto": "bonito",
                      "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES}
        lentes["comparacao-referencias"]["gosto"] = gosto
        d = wave.carregar(self.projeto)
        d["lentes"] = lentes
        d["gates"] = {n: {"exit": 0, "detalhe": "ok"} for n in wave.GATES}
        wave.salvar(self.projeto, d)

    def rodada(self, criticos=0, altos=1, reg=0, extra=False):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=criticos, altos=altos, regressoes=reg,
                                                      pendencias_do_usuario=0, rodada_extra_pedida=extra))
        return code, saida.getvalue()

    def reabrir(self, motivo="o dono pediu foto real no lugar do desenho em três seções"):
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = wave.cmd_reabrir(argparse.Namespace(projeto=self.projeto, motivo=motivo))
        return code, err.getvalue()

    def test_N23_registrar_aceita_acabamento_e_guarda(self):
        base = dict(projeto=self.projeto, lente="comparacao-referencias", veredito="reprovado", nota=5.0, origem="subagente",
                    gosto="correto", achados="Comparei a dobra com as referências lado a lado")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(wave.cmd_registrar(argparse.Namespace(**base, eixos_abaixo="imagem,acabamento")), 0)
            self.assertEqual(wave.cmd_registrar(argparse.Namespace(**base, eixos_abaixo="imagem,brilho")), 2)
        self.assertEqual(wave.carregar(self.projeto)["lentes"]["comparacao-referencias"]["eixos_abaixo"], ["imagem", "acabamento"])

    def test_N23_os_cinco_eixos_sao_os_do_auditores_md(self):
        ref = (pathlib.Path(__file__).resolve().parent.parent / "references" / "auditores.md").read_text(encoding="utf-8")
        self.assertRegex(ref, r"composição, tipografia, imagem, ritmo,\s+acabamento")
        self.assertEqual(wave.EIXOS, ("composicao", "tipografia", "imagem", "ritmo", "acabamento"))

    def test_N27_nao_entregar_na_rodada_2_ensina_o_que_fazer_em_sessao_nao_interativa(self):
        self.montar()
        self.rodada()
        self.montar()
        code, out = self.rodada(criticos=1)
        self.assertEqual(code, 1)
        self.assertIn("NÃO ENTREGAR", out)
        self.assertRegex(out, r"Sessão não interativa")
        self.assertIn("liste na entrega cada correção", out)
        self.assertIn("wave.py reabrir --motivo", out)

    def test_N27_reabrir_zera_o_ciclo_registra_o_motivo_e_nao_gasta_a_rodada_de_conferencia(self):
        self.montar()
        self.rodada()
        code, _ = self.reabrir()
        self.assertEqual(code, 0)
        d = wave.carregar(self.projeto)
        self.assertEqual(d["rodadas"], [])
        self.assertEqual(d["lentes"], {})
        self.assertEqual(d["gates"], {})
        self.assertEqual(len(d["ciclos_anteriores"]), 1)
        self.assertIn("foto real", d["reaberturas"][0]["motivo"])
        # a nova rodada 1 e a rodada 2 de conferência existem de novo, sem pedir rodada extra
        self.montar(nota=6)
        c1, o1 = self.rodada()
        self.assertIn("RODADA 1", o1)
        self.montar(nota=8)
        c2, o2 = self.rodada()
        self.assertIn("RODADA 2", o2)
        self.assertNotIn("ERRO", o2)

    def test_N27_so_uma_reabertura_por_ciclo(self):
        self.montar()
        self.rodada()
        self.assertEqual(self.reabrir()[0], 0)
        self.montar()
        self.rodada()
        code, err = self.reabrir("outra mudança grande que o dono pediu")
        self.assertEqual(code, 2)
        self.assertIn("já foi reaberto uma vez", err)
        self.assertEqual(len(wave.carregar(self.projeto)["ciclos_anteriores"]), 1)

    def test_N27_reabrir_exige_motivo_e_uma_rodada_fechada(self):
        self.assertEqual(self.reabrir()[0], 2)   # nada fechado: não há o que reabrir
        self.montar()
        self.rodada()
        self.assertEqual(self.reabrir("curto")[0], 2)
        self.assertEqual(self.reabrir("")[0], 2)
        self.assertEqual(wave.carregar(self.projeto).get("reaberturas"), None)

    def test_N27_sem_reabrir_a_rodada_3_continua_exigindo_o_pedido_da_pessoa(self):
        self.montar()
        self.rodada()
        self.montar()
        self.rodada()
        self.montar()
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=0, altos=1, regressoes=0, pendencias_do_usuario=0))
        self.assertEqual(code, 2)
        self.assertIn("--rodada-extra-pedida", err.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
