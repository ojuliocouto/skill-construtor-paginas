"""Gate de referências: sem 6 prints reais lidos, o plano visual não começa.

Os PNGs de teste são gerados aqui mesmo (zlib + struct), com ruído, para parecerem print de
verdade. Um PNG chapado de uma cor só imita print em branco, que é o defeito que o gate pega.
"""
import importlib.util
import json
import pathlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

AQUI = pathlib.Path(__file__).resolve().parent
SCRIPT = AQUI / "gate-referencias.py"
spec = importlib.util.spec_from_file_location("gref", SCRIPT)
gref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gref)


def png(caminho, largura=480, altura=320, semente=0, chapado=False):
    rnd = random.Random(semente)
    linhas = []
    for _ in range(altura):
        if chapado:
            linha = bytes([240, 240, 240]) * largura
        else:
            linha = rnd.randbytes(largura * 3)
        linhas.append(b"\x00" + linha)
    bruto = zlib.compress(b"".join(linhas), 6)

    def bloco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0)
    caminho.write_bytes(b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", ihdr) + bloco(b"IDAT", bruto) + bloco(b"IEND", b""))


NOTA = {
    "composicao": "Hero em duas colunas com a foto sangrando na borda direita",
    "tipografia": "Título serifado grande com corpo sem serifa de leitura calma",
    "imagem": "Foto de equipamento em luz natural, sem rosto de banco de imagem",
    "ritmo": "Seções alternam faixa cheia e bloco estreito, com muito respiro",
}


class GateReferencias(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = pathlib.Path(self.temp.name)
        (self.projeto / "referencias").mkdir()

    def montar(self, n=6, tipos=None, **sobrescrever):
        tipos = tipos or (["mesmo-negocio", "design"] * n)[:n]
        refs = []
        for i in range(n):
            dobra = self.projeto / "referencias" / f"{i:02d}-dobra.png"
            meio = self.projeto / "referencias" / f"{i:02d}-meio.png"
            png(dobra, semente=i * 2)
            png(meio, semente=i * 2 + 1)
            ref = {
                "url": f"https://exemplo{i}.com.br/",
                "tipo": tipos[i],
                "prints": {"dobra": f"referencias/{dobra.name}", "meio": f"referencias/{meio.name}"},
                "faz_bem": dict(NOTA),
                "principio": "Abrir com o objeto do ofício em foto grande, nunca com ícone em caixinha",
                "lido": True,
            }
            ref.update(sobrescrever)
            refs.append(ref)
        (self.projeto / "referencias" / "referencias.json").write_text(
            json.dumps({"referencias": refs}, ensure_ascii=False), encoding="utf-8")
        return refs

    def rodar(self, *extra):
        r = subprocess.run([sys.executable, str(SCRIPT), "--projeto", str(self.projeto), *extra],
                           capture_output=True, text=True, encoding="utf-8")
        return r.returncode, r.stdout + r.stderr

    def test_seis_prints_reais_lidos_passa(self):
        self.montar(6)
        code, out = self.rodar()
        self.assertEqual(code, 0, out)

    def test_cinco_referencias_reprova(self):
        self.montar(5)
        code, out = self.rodar()
        self.assertEqual(code, 1, out)
        self.assertIn("5 de 6", out)

    def test_sem_manifesto_reprova(self):
        code, out = self.rodar()
        self.assertEqual(code, 1, out)

    def test_print_ausente_nao_conta(self):
        self.montar(6)
        (self.projeto / "referencias" / "03-meio.png").unlink()
        code, out = self.rodar()
        self.assertEqual(code, 1, out)

    def test_print_em_branco_nao_conta(self):
        self.montar(6)
        png(self.projeto / "referencias" / "02-dobra.png", chapado=True)
        code, out = self.rodar()
        self.assertEqual(code, 1, out)
        self.assertIn("em branco", out)

    def test_mesmo_print_reaproveitado_nao_conta(self):
        self.montar(6)
        origem = (self.projeto / "referencias" / "00-dobra.png").read_bytes()
        (self.projeto / "referencias" / "05-dobra.png").write_bytes(origem)
        code, out = self.rodar()
        self.assertEqual(code, 1, out)

    def test_dobra_igual_ao_meio_nao_conta(self):
        self.montar(6)
        origem = (self.projeto / "referencias" / "01-dobra.png").read_bytes()
        (self.projeto / "referencias" / "01-meio.png").write_bytes(origem)
        code, _ = self.rodar()
        self.assertEqual(code, 1)

    def test_referencia_nao_lida_nao_conta(self):
        refs = self.montar(6)
        refs[4]["lido"] = False
        (self.projeto / "referencias" / "referencias.json").write_text(json.dumps({"referencias": refs}), encoding="utf-8")
        code, _ = self.rodar()
        self.assertEqual(code, 1)

    def test_leitura_rasa_nao_conta(self):
        refs = self.montar(6)
        refs[0]["faz_bem"]["tipografia"] = "bonita"
        (self.projeto / "referencias" / "referencias.json").write_text(json.dumps({"referencias": refs}), encoding="utf-8")
        code, out = self.rodar()
        self.assertEqual(code, 1, out)

    def test_url_repetida_nao_conta_duas_vezes(self):
        refs = self.montar(6)
        refs[5]["url"] = refs[0]["url"]
        (self.projeto / "referencias" / "referencias.json").write_text(json.dumps({"referencias": refs}), encoding="utf-8")
        code, _ = self.rodar()
        self.assertEqual(code, 1)

    def test_precisa_dos_dois_tipos(self):
        self.montar(6, tipos=["mesmo-negocio"] * 6)
        code, out = self.rodar()
        self.assertEqual(code, 1, out)
        self.assertIn("design", out)

    def test_print_fora_do_projeto_nao_conta(self):
        refs = self.montar(6)
        fora = pathlib.Path(tempfile.mkdtemp()) / "fora.png"
        png(fora, semente=99)
        refs[0]["prints"]["dobra"] = str(fora)
        (self.projeto / "referencias" / "referencias.json").write_text(json.dumps({"referencias": refs}), encoding="utf-8")
        code, _ = self.rodar()
        self.assertEqual(code, 1)

    def test_minimo_configuravel_nao_desce_de_seis(self):
        self.montar(4)
        code, out = self.rodar("--minimo", "3")
        self.assertEqual(code, 2, out)

    def test_funcao_valida_devolve_contagem(self):
        self.montar(7)
        validas, problemas = gref.checar(self.projeto)
        self.assertEqual(len(validas), 7)
        self.assertEqual(problemas, [])

    # ----- v3.5.6 (achados A1 e A2) -----
    def marcar(self, indice, **campos):
        arq = self.projeto / "referencias" / "referencias.json"
        doc = json.loads(arq.read_text(encoding="utf-8"))
        doc["referencias"][indice].update(campos)
        arq.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    def test_referencia_marcada_como_bloqueada_reprova(self):
        self.montar(8)
        self.marcar(2, captura={"estado": "bloqueada", "motivo": "HTTP 403: o site recusou o acesso automático"})
        code, out = self.rodar()
        self.assertEqual(code, 1, out)
        self.assertIn("bloqueada", out)
        self.assertIn("HTTP 403", out)

    def test_referencia_quebrada_e_coberta_reprovam_e_ok_passa(self):
        self.montar(8)
        self.marcar(1, captura={"estado": "quebrada", "motivo": "sem estilo"})
        self.marcar(3, captura={"estado": "coberta", "motivo": "modal cobre 77%"})
        self.marcar(4, captura={"estado": "ok", "motivo": ""})
        code, out = self.rodar()
        self.assertEqual(code, 1, out)
        self.assertIn("quebrada", out)
        self.assertIn("coberta", out)
        self.assertNotIn("exemplo4.com.br/: captura", out)

    def test_ruins_fora_do_manifesto_e_seis_boas_passa(self):
        self.montar(6)
        for i in range(6):
            self.marcar(i, captura={"estado": "ok", "motivo": ""})
        code, out = self.rodar()
        self.assertEqual(code, 0, out)

    def test_pagina_curta_de_verdade_pode_ter_meio_igual_a_dobra(self):
        self.montar(6)
        dobra = (self.projeto / "referencias" / "03-dobra.png").read_bytes()
        (self.projeto / "referencias" / "03-meio.png").write_bytes(dobra)
        self.marcar(3, altura_pagina=900)
        code, out = self.rodar()
        self.assertEqual(code, 0, out)

    def test_mutante_pagina_alta_com_meio_igual_a_dobra_continua_reprovando(self):
        self.montar(6)
        dobra = (self.projeto / "referencias" / "03-dobra.png").read_bytes()
        (self.projeto / "referencias" / "03-meio.png").write_bytes(dobra)
        self.marcar(3, altura_pagina=4200)
        code, out = self.rodar()
        self.assertEqual(code, 1, out)
        self.assertIn("print repetido", out)

    def test_mutante_pagina_curta_copiando_print_de_outra_referencia_reprova(self):
        self.montar(6)
        outra = (self.projeto / "referencias" / "00-dobra.png").read_bytes()
        (self.projeto / "referencias" / "03-meio.png").write_bytes(outra)
        self.marcar(3, altura_pagina=900)
        code, out = self.rodar()
        self.assertEqual(code, 1, out)
        self.assertIn("print repetido", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
