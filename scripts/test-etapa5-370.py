"""3.7.0: a etapa 5 (entrega pronta) cobra o que o passo g mais rápido deixou para o fim.

1. A rodada intermediária pode pular o gate de movimento (`rodar-gates.mjs --sem-movimento`), a final nunca: com a marca de
   movimento pulado na wave, a etapa 5 recusa e diz o comando da rodada completa.
2. Rodada 1 sem crítico nem alto fecha sem rodada 2 de auditor e "os gates de novo bastam": a etapa 5 cobra todos os gates
   verdes registrados DEPOIS dessa rodada.
"""
import json
import pathlib
import tempfile
import unittest
import importlib.util

AQUI = pathlib.Path(__file__).resolve().parent
SCRIPT = AQUI / "gate-etapas.py"
spec = importlib.util.spec_from_file_location("wave_e5", AQUI / "wave.py")
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)


class Etapa5(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pasta = pathlib.Path(self.temp.name)
        (self.pasta / "briefing.txt").write_text("Documento de controle com informações confirmadas", encoding="utf-8")
        (self.pasta / "videos").mkdir()
        for n in ("video-desktop.webm", "video-mobile.webm"):
            (self.pasta / "videos" / n).write_bytes(bytes.fromhex("1a45dfa3") + b"\x00" * 64)

    def wave(self, gates_quando="2026-10-26T02:00:00", rodada_quando="2026-10-26T01:30:00", sem_rodada_2=False, pulado=False, exit_texto=0):
        gates = {n: {"exit": 0, "detalhe": "ok", "quando": gates_quando} for n in wave.GATES}
        gates["texto"]["exit"] = exit_texto
        if pulado:
            gates["movimento"]["pulado_em"] = gates_quando
            gates["movimento"]["pulado_motivo"] = "--sem-movimento"
        r = {"n": 1, "quando": rodada_quando, "desfecho": "ENTREGA_COM_RESSALVAS", "ressalvas": ["médios abertos"]}
        if sem_rodada_2:
            r["sem_rodada_2"] = True
        d = {"lentes": {n: {"nota": 8, "veredito": "aprovado", "origem": "subagente"} for n in wave.LENTES}, "gates": gates, "rodadas": [r]}
        (self.pasta / ".wave-auditoria.json").write_text(json.dumps(d), encoding="utf-8")

    def registrar5(self):
        doc = {"gates": "g", "auditores": "a", "claims": "c", "contato": "x", "prova": "prints lidos", "pendencias": ["nenhuma"],
               "passe_de_gosto": {"antes": 2, "depois": 0, "inspecao": "percorri a página"}, "arquivos": ["briefing.txt"],
               "video": {"desktop": "videos/video-desktop.webm", "mobile": "videos/video-mobile.webm"}}
        (self.pasta / "e.json").write_text(json.dumps(doc), encoding="utf-8")
        spec_ge = importlib.util.spec_from_file_location("ge370", SCRIPT)
        ge = importlib.util.module_from_spec(spec_ge)
        spec_ge.loader.exec_module(ge)
        try:
            ge.validar(self.pasta.resolve(), (self.pasta / "e.json").resolve(), "5", ge.PAGINAS["5"], "paginas")
            return 0, ""
        except ValueError as e:
            return 1, str(e)

    def test_movimento_pulado_na_ultima_rodada_completa_recusa_a_entrega(self):
        self.wave(pulado=True)
        code, out = self.registrar5()
        self.assertEqual(code, 1, out)
        self.assertIn("movimento", out)
        self.assertIn("rodar-gates.mjs", out)
        self.assertIn("--sem-movimento", out)

    def test_sem_marca_de_movimento_pulado_registra(self):
        self.wave()
        code, out = self.registrar5()
        self.assertEqual(code, 0, out)

    def test_sem_rodada_2_exige_os_gates_depois_da_rodada(self):
        self.wave(sem_rodada_2=True, gates_quando="2026-10-26T01:00:00", rodada_quando="2026-10-26T01:30:00")
        code, out = self.registrar5()
        self.assertEqual(code, 1, out)
        self.assertIn("depois", out)
        self.assertIn("rodar-gates.mjs", out)

    def test_sem_rodada_2_com_os_gates_verdes_depois_registra(self):
        self.wave(sem_rodada_2=True, gates_quando="2026-10-26T02:00:00", rodada_quando="2026-10-26T01:30:00")
        code, out = self.registrar5()
        self.assertEqual(code, 0, out)

    def test_sem_rodada_2_nao_cobra_de_novo_o_que_a_rodada_completa_nao_registra(self):
        self.wave(sem_rodada_2=True, gates_quando="2026-10-26T02:00:00", rodada_quando="2026-10-26T01:30:00")
        d = json.loads((self.pasta / ".wave-auditoria.json").read_text(encoding="utf-8"))
        for g in ("identidade", "uso-ferramentas"):
            d["gates"][g]["quando"] = "2026-10-26T01:00:00"
        (self.pasta / ".wave-auditoria.json").write_text(json.dumps(d), encoding="utf-8")
        code, out = self.registrar5()
        self.assertEqual(code, 0, out)

    def test_sem_rodada_2_com_gate_vermelho_recusa(self):
        self.wave(sem_rodada_2=True, exit_texto=1)
        code, out = self.registrar5()
        self.assertEqual(code, 1, out)
        self.assertIn("texto", out)


if __name__ == "__main__":
    unittest.main()
