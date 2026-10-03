"""Controles do gate de imagens: licença completa, direito de imagem e aviso na prévia do link.

Auditoria da v4 (02/10/2026): a foto do herói era de um estúdio real (ProBalance, Alameda, CA),
com duas pessoas identificáveis e só a permissão da fotógrafa; o crédito do rodapé dizia
"Creative Commons BY-SA" sem a versão 3.0, sem link para a licença e sem dizer que a versão
retocada seguia a mesma licença; e o og-image punha a instrutora ao lado de "Pilates com
fisioterapeuta" sem "imagem ilustrativa".
"""
import importlib.util
import pathlib
import tempfile
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gate_imagens", AQUI / "gate-imagens.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

CABECALHO = "| Arquivo publicado | Origem | Autor | Título | Licença | Link da licença | Alteração | Pessoa identificável | Autorização de imagem | Aviso de ilustrativa |\n|---|---|---|---|---|---|---|---|---|---|\n"
SALA = "| sala-480/800.webp | https://unsplash.com/photos/x | Ahmet Kurt | Sala de pilates | Unsplash License (sem versão numerada) | https://unsplash.com/license | recorte | não | não se aplica | sim |\n"
OG_SALA = "| og-image.jpg | composição própria com sala-800.webp | Ahmet Kurt | Sala de pilates | Unsplash License (sem versão numerada) | https://unsplash.com/license | recorte e texto | não | não se aplica | sim |\n"
RODAPE_OK = "<footer><p>Imagem ilustrativa: a sala não é do estúdio. Foto: Ahmet Kurt, Unsplash (<a href=\"https://unsplash.com/license\">Unsplash License</a>).</p></footer>"
V4_LINHA = "| hero-aula-v4-480/720.webp | https://commons.wikimedia.org/wiki/File:Pilates_Teacher.jpg | Anne Kohler | Pilates Teacher | CC BY-SA 3.0 | https://creativecommons.org/licenses/by-sa/3.0/ | retoque na alça | sim | não | sim |\n"
V4_OG = "| og-image.jpg | composição com hero-aula-v4 | Anne Kohler | Pilates Teacher | CC BY-SA 3.0 | https://creativecommons.org/licenses/by-sa/3.0/ | recorte e texto | sim | não | não |\n"
V4_RODAPE = "<footer><p>Imagens ilustrativas, nenhuma mostra o estúdio. Aula de pilates: Anne Kohler, Wikimedia Commons, licença Creative Commons BY-SA, com retoque na alça.</p><a href=\"https://commons.wikimedia.org/wiki/File:Pilates_Teacher.jpg\">Ver a foto original e a licença</a></footer>"


class GateImagens(unittest.TestCase):
    def projeto(self, linhas, rodape, imagens=("imagens/sala-480.webp", "imagens/sala-800.webp", "og-image.jpg")):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = pathlib.Path(tmp.name)
        (raiz / "imagens").mkdir()
        (raiz / "imagens" / "LICENCAS.md").write_text("# Licenças\n\n" + CABECALHO + "".join(linhas), encoding="utf-8")
        dist = raiz / "dist"
        (dist / "imagens").mkdir(parents=True)
        (dist / "fonts").mkdir()
        for nome in (*imagens, "favicon.png", "apple-touch-icon.png", "fonts/f.woff2"):
            (dist / nome).write_bytes(b"x")
        (dist / "index.html").write_text(f"<!doctype html><html><body><main><h1>Página</h1></main>{rodape}</body></html>", encoding="utf-8")
        return raiz

    def test_positivo_foto_sem_pessoa_e_og_com_aviso(self):
        self.assertEqual(gate.checar(self.projeto([SALA, OG_SALA], RODAPE_OK)), [])

    def test_caso_real_da_v4_reprova_nos_tres_pontos(self):
        raiz = self.projeto([V4_LINHA, V4_OG], V4_RODAPE, imagens=("imagens/hero-aula-v4-480.webp", "og-image.jpg"))
        problemas = " | ".join(gate.checar(raiz))
        self.assertIn("pessoa identificável sem autorização de imagem", problemas)
        self.assertIn("og-image.jpg", problemas)
        self.assertRegex(problemas, r"aviso de .imagem ilustrativa.")
        self.assertRegex(problemas, r"CC BY-SA 3\.0")
        self.assertIn("https://creativecommons.org/licenses/by-sa/3.0/", problemas)
        self.assertIn("mesma licença", problemas)

    def test_imagem_publicada_sem_linha(self):
        problemas = gate.checar(self.projeto([SALA], RODAPE_OK))
        self.assertTrue(any("og-image.jpg" in p and "sem linha" in p for p in problemas), problemas)

    def test_cc_sem_versao_ou_sem_link(self):
        linha = SALA.replace("Unsplash License (sem versão numerada)", "Creative Commons BY").replace("https://unsplash.com/license", "")
        problemas = " | ".join(gate.checar(self.projeto([linha, OG_SALA], RODAPE_OK)))
        self.assertIn("versão", problemas)
        self.assertIn("link da licença", problemas)

    def test_pagina_sem_aviso_de_ilustrativa(self):
        problemas = gate.checar(self.projeto([SALA, OG_SALA], RODAPE_OK.replace("Imagem ilustrativa: a sala", "A sala")))
        self.assertTrue(any("ilustrativa" in p and "página" in p for p in problemas), problemas)


if __name__ == "__main__":
    unittest.main(verbosity=2)
