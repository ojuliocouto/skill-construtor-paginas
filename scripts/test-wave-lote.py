"""Registro automático na wave (corte 5 da auditoria de velocidade).

Medido no Torra Clara: 15 chamadas de registro à mão, 3,7 min de modelo. Aqui:
  - `wave.py gates-lote --arquivo f.json` grava o exit REAL de vários gates numa chamada só
    (é o que o `rodar-gates.mjs` usa depois de uma rodada completa);
  - `wave.py registrar-lote --arquivo resposta.json --origem subagente` registra as lentes direto
    da resposta do auditor (o schema do briefing: um bloco por lente, solto, em lista ou em fence).
As duas operações são tudo ou nada: bloco ruim não deixa metade do registro gravado.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
WAVE = AQUI / "wave.py"

LENTES = ["design-critic", "assets-auditor", "visual-auditor", "motion-auditor", "responsive-auditor",
          "cro-auditor", "a11y-auditor", "content-auditor", "comparacao-referencias"]


def wave(projeto, *args):
    r = subprocess.run([sys.executable, str(WAVE), "--projeto", str(projeto), *args],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


def registro(projeto):
    p = pathlib.Path(projeto) / ".wave-auditoria.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"lentes": {}, "gates": {}}


def bloco(lente, aprovado=True, score=8.0, achados=None, **extra):
    b = {"lente": lente, "aprovado": aprovado, "score": score,
         "achados": [{"item": "botão pequeno", "severidade": "medio", "evidencia": "alvo de 38 px em 390", "fix": "subir para 44 px"}] if achados is None else achados}
    if lente == "comparacao-referencias":
        b.setdefault("gosto", "bonito")
        b.setdefault("eixos_abaixo", [])
    b.update(extra)
    return b


def nove(**por_lente):
    return [bloco(l, **por_lente.get(l, {})) for l in LENTES]


class Base(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.dir = pathlib.Path(t.name)
        self.proj = self.dir / "proj"
        self.proj.mkdir()

    def arquivo(self, conteudo, nome="entrada.json"):
        p = self.dir / nome
        p.write_text(conteudo if isinstance(conteudo, str) else json.dumps(conteudo, ensure_ascii=False), encoding="utf-8")
        return p


class GatesEmLote(Base):
    def test_grava_o_exit_real_de_cada_gate(self):
        f = self.arquivo({"gates": [
            {"nome": "texto", "exit": 0, "detalhe": "rodar-gates r2: PASSA em 7 s (gates/texto-r2.txt)"},
            {"nome": "simetria", "exit": 1, "detalhe": "rodar-gates r2: REPROVA (gates/simetria-r2.txt)"}]})
        code, saida = wave(self.proj, "gates-lote", "--arquivo", str(f))
        self.assertEqual(code, 0, saida)
        d = registro(self.proj)
        self.assertEqual(d["gates"]["texto"]["exit"], 0)
        self.assertEqual(d["gates"]["simetria"]["exit"], 1)
        self.assertIn("gates/simetria-r2.txt", d["gates"]["simetria"]["detalhe"])
        self.assertIn("2 gate(s)", saida)

    def test_nome_que_a_wave_nao_conhece_nao_grava_nada(self):
        f = self.arquivo({"gates": [{"nome": "texto", "exit": 0, "detalhe": ""}, {"nome": "inventado", "exit": 0, "detalhe": ""}]})
        code, saida = wave(self.proj, "gates-lote", "--arquivo", str(f))
        self.assertEqual(code, 2, saida)
        self.assertIn("inventado", saida)
        self.assertEqual(registro(self.proj)["gates"], {}, "metade do lote foi gravada")

    def test_exit_que_nao_e_inteiro_nao_grava_nada(self):
        f = self.arquivo({"gates": [{"nome": "texto", "exit": "0", "detalhe": ""}]})
        code, saida = wave(self.proj, "gates-lote", "--arquivo", str(f))
        self.assertEqual(code, 2, saida)
        self.assertEqual(registro(self.proj)["gates"], {})

    def test_lista_vazia_e_arquivo_ruim_sao_erro(self):
        self.assertEqual(wave(self.proj, "gates-lote", "--arquivo", str(self.arquivo({"gates": []})))[0], 2)
        self.assertEqual(wave(self.proj, "gates-lote", "--arquivo", str(self.arquivo("{ não é json")))[0], 2)
        self.assertEqual(wave(self.proj, "gates-lote", "--arquivo", str(self.dir / "nao-existe.json"))[0], 2)

    def test_gate_de_novo_troca_o_registro_antigo(self):
        wave(self.proj, "gates-lote", "--arquivo", str(self.arquivo({"gates": [{"nome": "texto", "exit": 1, "detalhe": "r1"}]})))
        wave(self.proj, "gates-lote", "--arquivo", str(self.arquivo({"gates": [{"nome": "texto", "exit": 0, "detalhe": "r2"}]}, "b.json")))
        self.assertEqual(registro(self.proj)["gates"]["texto"]["exit"], 0)


class LentesEmLote(Base):
    def lote(self, conteudo, *extra, origem="subagente"):
        f = self.arquivo(conteudo)
        args = ["registrar-lote", "--arquivo", str(f)]
        if origem:
            args += ["--origem", origem]
        return wave(self.proj, *args, *extra)

    def test_lista_de_nove_blocos_registra_as_nove_lentes_com_a_origem(self):
        code, saida = self.lote(nove())
        self.assertEqual(code, 0, saida)
        d = registro(self.proj)
        self.assertEqual(sorted(d["lentes"]), sorted(LENTES))
        l = d["lentes"]["visual-auditor"]
        self.assertEqual((l["veredito"], l["nota"], l["origem"]), ("aprovado", 8.0, "subagente"))
        self.assertIn("alvo de 38 px em 390", l["achados"])
        self.assertIn("médio", l["achados"].lower().replace("medio", "médio"))
        self.assertIn("9 lente(s)", saida)

    def test_blocos_soltos_dentro_de_fence_de_markdown_como_o_auditor_responde(self):
        texto = "Resultado da rodada 1.\n\n" + "\n\n".join(f"Lente {b['lente']}:\n```json\n{json.dumps(b, ensure_ascii=False, indent=2)}\n```" for b in nove()) + "\n\nFim."
        code, saida = self.lote(texto)
        self.assertEqual(code, 0, saida)
        self.assertEqual(len(registro(self.proj)["lentes"]), 9)

    def test_objeto_com_lentes_duracao_e_chamadas(self):
        code, saida = self.lote({"lentes": nove(), "duracao_min": 17.3, "chamadas": 29})
        self.assertEqual(code, 0, saida)
        l = registro(self.proj)["lentes"]["design-critic"]
        self.assertEqual((l["duracao_min"], l["chamadas"]), (17.3, 29))

    def test_a_linha_de_comando_manda_sobre_o_arquivo_na_duracao(self):
        code, saida = self.lote({"lentes": nove(), "duracao_min": 17.3, "chamadas": 29}, "--duracao-min", "20", "--chamadas", "31")
        self.assertEqual(code, 0, saida)
        l = registro(self.proj)["lentes"]["design-critic"]
        self.assertEqual((l["duracao_min"], l["chamadas"]), (20.0, 31))

    def test_aprovado_falso_vira_reprovado(self):
        self.lote(nove(**{"cro-auditor": {"aprovado": False, "score": 5.5}}))
        self.assertEqual(registro(self.proj)["lentes"]["cro-auditor"]["veredito"], "reprovado")

    def test_comparacao_guarda_gosto_e_eixos(self):
        self.lote(nove(**{"comparacao-referencias": {"aprovado": False, "gosto": "correto", "eixos_abaixo": ["imagem", "ritmo"]}}))
        l = registro(self.proj)["lentes"]["comparacao-referencias"]
        self.assertEqual((l["gosto"], l["eixos_abaixo"], l["veredito"]), ("correto", ["imagem", "ritmo"], "reprovado"))

    def test_regras_da_wave_valem_igual_no_lote_e_nada_e_gravado(self):
        # página só correta não aprova a comparação com as referências (mesma regra do registrar)
        code, saida = self.lote(nove(**{"comparacao-referencias": {"gosto": "correto", "aprovado": True}}))
        self.assertEqual(code, 2, saida)
        self.assertIn("comparacao-referencias", saida)
        self.assertEqual(registro(self.proj)["lentes"], {}, "o lote é tudo ou nada")

    def test_comparacao_sem_gosto_e_erro(self):
        blocos = nove()
        del blocos[-1]["gosto"]
        code, saida = self.lote(blocos)
        self.assertEqual(code, 2, saida)
        self.assertEqual(registro(self.proj)["lentes"], {})

    def test_nota_fora_de_faixa_lente_desconhecida_e_eixo_invalido_sao_erro(self):
        for ruim in (nove(**{"cro-auditor": {"score": 11}}),
                     [bloco("lente-que-nao-existe")],
                     nove(**{"comparacao-referencias": {"eixos_abaixo": ["cor-de-rosa"], "aprovado": False}})):
            code, saida = self.lote(ruim)
            self.assertEqual(code, 2, saida)
            self.assertEqual(registro(self.proj)["lentes"], {})

    def test_sem_origem_nao_registra(self):
        code, saida = self.lote(nove(), origem=None)
        self.assertNotEqual(code, 0)
        self.assertEqual(registro(self.proj)["lentes"], {})

    def test_lente_sem_achados_registra_com_texto_que_diz_isso(self):
        code, saida = self.lote(nove(**{"a11y-auditor": {"achados": []}}))
        self.assertEqual(code, 0, saida)
        txt = registro(self.proj)["lentes"]["a11y-auditor"]["achados"]
        self.assertGreaterEqual(len(txt), 25)
        self.assertIn("sem achados", txt)
        self.assertIn("1 lente(s) sem achados", saida)

    def test_lente_nao_verificada_recusa_o_lote_inteiro(self):
        code, saida = self.lote(nove(**{"motion-auditor": {"veredito": "nao_verificado"}}))
        self.assertEqual(code, 2, saida)
        self.assertIn("motion-auditor", saida)
        self.assertEqual(registro(self.proj)["lentes"], {})

    def test_nao_aplicavel_passa_sem_nota(self):
        b = nove()
        b[3] = {"lente": "motion-auditor", "veredito": "nao_aplicavel", "achados": "página sem animação nenhuma: nada a medir aqui"}
        code, saida = self.lote(b)
        self.assertEqual(code, 0, saida)
        self.assertEqual(registro(self.proj)["lentes"]["motion-auditor"]["veredito"], "nao_aplicavel")

    def test_conta_critico_e_alto_do_json_e_diz_que_ainda_precisa_confirmar(self):
        achados = [{"item": "a", "severidade": "critico", "evidencia": "e1", "fix": "f"},
                   {"item": "b", "severidade": "alto", "evidencia": "e2", "fix": "f"},
                   {"item": "c", "severidade": "alto", "evidencia": "e3", "fix": "f"}]
        code, saida = self.lote(nove(**{"cro-auditor": {"achados": achados}}))
        self.assertEqual(code, 0, saida)
        self.assertIn("1 crítico(s)", saida)
        self.assertIn("2 alto(s)", saida)
        self.assertIn("confirme", saida.lower())

    def test_lente_repetida_no_mesmo_lote_e_erro(self):
        code, saida = self.lote(nove() + [bloco("design-critic")])
        self.assertEqual(code, 2, saida)
        self.assertEqual(registro(self.proj)["lentes"], {})

    def test_o_que_o_registrar_um_a_um_grava_o_lote_grava_igual(self):
        # mesma lente, mesmo resultado: o lote é só a mesma conta feita uma vez
        proj2 = self.dir / "proj2"
        proj2.mkdir()
        code, _ = wave(proj2, "registrar", "visual-auditor", "--nota", "8.0", "--veredito", "aprovado", "--origem", "subagente",
                       "--achados", "botão pequeno: alvo de 38 px em 390 (fix: subir para 44 px)")
        self.assertEqual(code, 0)
        self.lote(nove())
        a = registro(proj2)["lentes"]["visual-auditor"]
        b = registro(self.proj)["lentes"]["visual-auditor"]
        for campo in ("veredito", "nota", "origem"):
            self.assertEqual(a[campo], b[campo], campo)

    def test_depois_do_lote_o_master_ve_as_nove_lentes(self):
        self.lote(nove())
        code, saida = wave(self.proj, "checar")
        self.assertIn("9/9 registradas", saida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
