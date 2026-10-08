"""Controles do gate de imagens: licença completa, direito de imagem e aviso na prévia do link.

Auditoria da v4 (02/10/2026): a foto do herói era de um estúdio real (ProBalance, Alameda, CA),
com duas pessoas identificáveis e só a permissão da fotógrafa; o crédito do rodapé dizia
"Creative Commons BY-SA" sem a versão 3.0, sem link para a licença e sem dizer que a versão
retocada seguia a mesma licença; e o og-image punha a instrutora ao lado de "Pilates com
fisioterapeuta" sem "imagem ilustrativa".
"""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

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
        # v3.5: pessoa identificável sem autorização deixou de bloquear a página de teste; vira
        # aviso de bloqueio para tráfego real (testado em GateImagensV35).
        self.assertNotIn("pessoa identificável sem autorização de imagem", problemas)
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

    # Auditoria da v5 (03/10/2026): o crédito dizia Foto "Sala de pilates com aparelhos", e o
    # título da foto no Unsplash é "a room filled with lots of different types of equipment".
    def test_titulo_inventado_no_credito_reprova(self):
        origem = "https://unsplash.com/photos/a-room-filled-with-lots-of-different-types-of-equipment-2sXYx7sd-kg"
        linha = SALA.replace("https://unsplash.com/photos/x", origem).replace("| Sala de pilates |", "| Sala de pilates com aparelhos |")
        og = OG_SALA.replace("| Sala de pilates |", "| Sala de pilates com aparelhos |")
        rodape = RODAPE_OK.replace("Foto: Ahmet Kurt", 'Foto "Sala de pilates com aparelhos": Ahmet Kurt')
        problemas = " | ".join(gate.checar(self.projeto([linha, og], rodape)))
        self.assertRegex(problemas, r"t[ií]tulo")
        self.assertIn("a room filled with lots", problemas)

    def test_titulo_real_da_fonte_passa(self):
        titulo = "a room filled with lots of different types of equipment"
        origem = "https://unsplash.com/photos/a-room-filled-with-lots-of-different-types-of-equipment-2sXYx7sd-kg"
        linha = SALA.replace("https://unsplash.com/photos/x", origem).replace("| Sala de pilates |", f"| {titulo} |")
        og = OG_SALA.replace("| Sala de pilates |", f"| {titulo} |")
        rodape = RODAPE_OK.replace("Foto: Ahmet Kurt", f'Foto "{titulo}": Ahmet Kurt')
        self.assertEqual(gate.checar(self.projeto([linha, og], rodape)), [])

    def test_aspas_no_credito_com_outro_titulo_reprova(self):
        rodape = RODAPE_OK.replace("Foto: Ahmet Kurt", 'Foto "Estúdio iluminado": Ahmet Kurt')
        problemas = " | ".join(gate.checar(self.projeto([SALA, OG_SALA], rodape)))
        self.assertIn("Estúdio iluminado", problemas)

    # ---- 3.5.8 (N7, N8): crédito casado com a foto, hífen do título real ----
    def tres_fotos_do_mesmo_autor(self, titulos, links=True, trocar=False):
        """Três fotos do Ahmet Kurt, cada uma com seu título. Devolve (linhas, rodapé, imagens)."""
        nomes = ["mesa", "estante", "cama"]
        slugs = ["Mesa_de_jantar_em_madeira_clara", "Estante_com_livros_antigos", "Cama_de_casal_com_cabeceira_alta"]
        linhas, itens = [], []
        for i, (n, sl, t) in enumerate(zip(nomes, slugs, titulos)):
            origem = f"https://commons.wikimedia.org/wiki/File:{sl}.jpg"
            linhas.append(f"| {n}-480/800.webp | {origem} | Ahmet Kurt | {t} | Unsplash License (sem versão numerada) | https://unsplash.com/license | recorte | não | não se aplica | sim |\n")
            itens.append((origem, t))
        linhas.append(OG_SALA.replace("composição própria com sala-800.webp", "composição própria com mesa-800.webp").replace("| Sala de pilates |", f"| {titulos[0]} |"))
        creditos = []
        for k, (origem, t) in enumerate(itens):
            citado = itens[(k + 1) % 3][1] if trocar else t
            ancora = f' <a href="{origem}">fonte</a>' if links else ""
            creditos.append(f'<li>Foto "{citado}", por Ahmet Kurt, Unsplash License.{ancora}</li>')
        rodape = "<footer><p>Imagem ilustrativa: nenhuma foto mostra a casa do cliente.</p><ul>" + "".join(creditos) + "</ul></footer>"
        imagens = tuple(f"imagens/{n}-{w}.webp" for n in nomes for w in (480, 800)) + ("og-image.jpg",)
        return linhas, rodape, imagens

    TITULOS3 = ["Mesa de jantar em madeira clara", "Estante com livros antigos", "Cama de casal com cabeceira alta"]

    def test_N7_tres_fotos_do_mesmo_autor_com_credito_certo_passam(self):
        linhas, rodape, imagens = self.tres_fotos_do_mesmo_autor(self.TITULOS3)
        self.assertEqual(gate.checar(self.projeto(linhas, rodape, imagens=imagens)), [])

    def test_N7_sem_link_de_origem_na_pagina_o_titulo_de_outra_foto_do_mesmo_autor_passa(self):
        linhas, rodape, imagens = self.tres_fotos_do_mesmo_autor(self.TITULOS3, links=False)
        self.assertEqual(gate.checar(self.projeto(linhas, rodape, imagens=imagens)), [])

    def test_N7_mutante_titulo_inventado_com_tres_fotos_do_mesmo_autor_continua_reprovando(self):
        linhas, rodape, imagens = self.tres_fotos_do_mesmo_autor(self.TITULOS3)
        for links in (True, False):
            linhas, rodape, imagens = self.tres_fotos_do_mesmo_autor(self.TITULOS3, links=links)
            rodape = rodape.replace('Foto "Estante com livros antigos"', 'Foto "Prateleira inventada"')
            problemas = " | ".join(gate.checar(self.projeto(linhas, rodape, imagens=imagens)))
            self.assertIn("Prateleira inventada", problemas, f"links={links}")

    def test_N7_mutante_credito_trocado_entre_fotos_do_mesmo_autor_reprova_quando_a_pagina_liga_o_credito_a_foto(self):
        linhas, rodape, imagens = self.tres_fotos_do_mesmo_autor(self.TITULOS3, trocar=True)
        problemas = " | ".join(gate.checar(self.projeto(linhas, rodape, imagens=imagens)))
        self.assertIn("entre aspas como título", problemas)

    def test_N8_titulo_real_com_hifen_passa_e_titulo_errado_com_hifen_continua_reprovando(self):
        origem = "https://commons.wikimedia.org/wiki/File:Close-up_of_a_carpenters_hand_sandpapering_the_wood.jpg"
        titulo = "Close-up of a carpenters hand sandpapering the wood"
        linha = SALA.replace("https://unsplash.com/photos/x", origem).replace("| Sala de pilates |", f"| {titulo} |")
        og = OG_SALA.replace("| Sala de pilates |", f"| {titulo} |")
        rodape = RODAPE_OK.replace("Foto: Ahmet Kurt", f'Foto "{titulo}": Ahmet Kurt')
        self.assertEqual(gate.checar(self.projeto([linha, og], rodape)), [])
        errado = "Close-up of a joiners hand sanding the plank"
        linha2 = linha.replace(f"| {titulo} |", f"| {errado} |")
        og2 = og.replace(f"| {titulo} |", f"| {errado} |")
        problemas = " | ".join(gate.checar(self.projeto([linha2, og2], rodape.replace(titulo, errado))))
        self.assertRegex(problemas, r"n[ãa]o é o da fonte")

    def test_ilustracao_propria_dispensa_link_de_licenca(self):
        linha = "| aula-1200.webp | ilustração própria, feita para esta página | Studio | Avaliação postural | própria | | nenhuma | não | não se aplica | não |\n"
        og = "| og-image.jpg | ilustração própria, feita para esta página | Studio | Avaliação postural | própria | | texto ao lado | não | não se aplica | não |\n"
        rodape = "<footer><p>Ilustrações feitas para esta página.</p></footer>"
        self.assertEqual(gate.checar(self.projeto([linha, og], rodape, imagens=("imagens/aula-1200.webp", "og-image.jpg"))), [])


def foto_sintetica(caminho, semente, nitida=True, tamanho=(640, 480)):
    """Foto de controle: relevo de baixa frequência próprio de cada semente (é o que o pHash lê) e,
    quando nítida, ruído fino por cima (é o que a variância do laplaciano lê)."""
    rng = np.random.default_rng(semente)
    h, w = tamanho[1], tamanho[0]
    y, x = np.mgrid[0:h, 0:w].astype(np.float64)
    base = np.zeros((h, w))
    for _ in range(6):
        fx, fy = rng.uniform(0.5, 3.0, 2)
        fase = rng.uniform(0, 6.28, 2)
        base += rng.uniform(20, 40) * np.sin(2 * np.pi * fx * x / w + fase[0]) * np.cos(2 * np.pi * fy * y / h + fase[1])
    img = 128 + base
    if nitida:
        img = img + rng.normal(0, 12, (h, w))
    img = np.clip(img, 0, 255).astype(np.uint8)
    rgb = np.stack([img, img, img], axis=-1)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb).save(caminho, quality=95)


UNSPLASH = "Licença Unsplash | https://unsplash.com/license"


def linha(arquivo, origem, pessoa="não", autorizacao="não se aplica", alteracao="recorte"):
    return (f"| {arquivo} | {origem} | Fulana de Tal | | {UNSPLASH} | {alteracao} | {pessoa} | {autorizacao} | sim |\n")


class GateImagensV35(unittest.TestCase):
    """Padrão da v7 (04/10/2026): foto repetida entre seções, foto borrada, pessoa identificável
    de banco como aviso de tráfego real e aviso de ilustrativa na primeira tela."""

    def projeto(self, secoes, linhas, fotos, extra_head="", rodape="<footer><p>Imagem ilustrativa de banco de imagens.</p></footer>"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        raiz = pathlib.Path(tmp.name)
        (raiz / "imagens").mkdir()
        (raiz / "imagens" / "LICENCAS.md").write_text("# Licenças\n\n" + CABECALHO + "".join(linhas), encoding="utf-8")
        dist = raiz / "dist"
        for nome, (semente, nitida) in fotos.items():
            foto_sintetica(dist / "img" / nome, semente, nitida)
        corpo = "".join(secoes)
        (dist / "index.html").write_text(f"<!doctype html><html><head><title>t</title>{extra_head}</head><body>{corpo}{rodape}</body></html>", encoding="utf-8")
        return raiz

    def sec(self, nome, *imgs, texto=""):
        tags = "".join(f'<img src="img/{i}" alt="foto" width="640" height="480">' for i in imgs)
        return f'<section id="{nome}"><h2>{nome}</h2>{tags}<p>{texto}</p></section>'

    def foto_ok(self, n):
        return linha(f"img/foto{n}-800.jpg", f"https://unsplash.com/photos/origem{n}")

    def test_fotos_diferentes_em_secoes_diferentes_passam(self):
        raiz = self.projeto([self.sec("a", "foto1-800.jpg"), self.sec("b", "foto2-800.jpg")],
                            [self.foto_ok(1), self.foto_ok(2)], {"foto1-800.jpg": (1, True), "foto2-800.jpg": (2, True)})
        problemas, avisos = gate.avaliar(raiz)
        self.assertEqual(problemas, [], problemas)

    def test_mesma_foto_com_arquivos_diferentes_em_duas_secoes_reprova(self):
        # a v7 antes da correção: "seis fotos que eram duas salas e foto repetida"
        raiz = self.projeto([self.sec("a", "foto1-800.jpg"), self.sec("b", "foto9-800.jpg")],
                            [self.foto_ok(1), self.foto_ok(9)], {"foto1-800.jpg": (1, True), "foto9-800.jpg": (1, True)})
        problemas, _ = gate.avaliar(raiz)
        self.assertTrue(any("repetida" in p and "foto1" in p and "foto9" in p for p in problemas), problemas)

    def test_mesmo_arquivo_em_duas_secoes_reprova(self):
        raiz = self.projeto([self.sec("a", "foto1-800.jpg"), self.sec("b", "foto1-800.jpg")],
                            [self.foto_ok(1)], {"foto1-800.jpg": (1, True)})
        problemas, _ = gate.avaliar(raiz)
        self.assertTrue(any("repetida" in p and "a" in p and "b" in p for p in problemas), problemas)

    def test_mesma_origem_em_secoes_diferentes_reprova(self):
        # recortes da mesma foto de banco em duas seções: arquivos e pHash diferentes, mesma cena
        raiz = self.projeto([self.sec("a", "foto1-800.jpg"), self.sec("b", "foto2-800.jpg")],
                            [linha("img/foto1-800.jpg", "https://unsplash.com/photos/mesma"),
                             linha("img/foto2-800.jpg", "https://unsplash.com/photos/mesma")],
                            {"foto1-800.jpg": (1, True), "foto2-800.jpg": (2, True)})
        problemas, _ = gate.avaliar(raiz)
        self.assertTrue(any("repetida" in p and "mesma" in p for p in problemas), problemas)

    def test_recortes_da_mesma_foto_na_mesma_secao_passam(self):
        raiz = self.projeto([self.sec("topo", "foto1-800.jpg", "foto2-800.jpg")],
                            [linha("img/foto1-800.jpg", "https://unsplash.com/photos/mesma"),
                             linha("img/foto2-800.jpg", "https://unsplash.com/photos/mesma")],
                            {"foto1-800.jpg": (1, True), "foto2-800.jpg": (2, True)})
        problemas, _ = gate.avaliar(raiz)
        self.assertEqual(problemas, [], problemas)

    def test_foto_borrada_reprova_com_a_variancia(self):
        raiz = self.projeto([self.sec("a", "foto1-800.jpg")], [self.foto_ok(1)], {"foto1-800.jpg": (1, False)})
        problemas, _ = gate.avaliar(raiz)
        self.assertTrue(any("nitidez" in p and "foto1" in p and "borrada" in p for p in problemas), problemas)

    def test_foto_nitida_de_pouco_contraste_nao_reprova(self):
        # paleta bege: detalhe fino de amplitude baixa. O laplaciano absoluto dá < 100 e a foto está nítida.
        raiz = self.projeto([self.sec("a", "foto1-800.jpg")], [self.foto_ok(1)], {"foto1-800.jpg": (1, True)})
        caminho = raiz / "dist" / "img" / "foto1-800.jpg"
        a = np.asarray(Image.open(caminho).convert("L"), dtype=np.float64)
        suave = np.clip(128 + (a - 128) * 0.15, 0, 255).astype(np.uint8)
        Image.fromarray(np.stack([suave] * 3, axis=-1)).save(caminho, quality=95)
        self.assertLess(gate.variancia_laplaciano(np, Image.open(caminho)), 100)
        problemas, _ = gate.avaliar(raiz)
        self.assertFalse(any("nitidez" in p for p in problemas), problemas)

    def test_foto_macia_e_so_aviso(self):
        from PIL import ImageFilter
        raiz = self.projeto([self.sec("a", "foto1-800.jpg")], [self.foto_ok(1)], {"foto1-800.jpg": (1, True)})
        caminho = raiz / "dist" / "img" / "foto1-800.jpg"
        Image.open(caminho).filter(ImageFilter.GaussianBlur(1.2)).save(caminho, quality=95)
        r = gate.razao_nitidez(np, ImageFilter, Image.open(caminho).convert("RGB"))
        self.assertTrue(gate.NITIDEZ_REPROVA <= r < gate.NITIDEZ_AVISA, r)
        problemas, avisos = gate.avaliar(raiz)
        self.assertFalse(any("nitidez" in p for p in problemas), problemas)
        self.assertTrue(any("macia" in a and "foto1" in a for a in avisos), avisos)

    def test_foto_nitida_passa(self):
        raiz = self.projeto([self.sec("a", "foto1-800.jpg")], [self.foto_ok(1)], {"foto1-800.jpg": (1, True)})
        problemas, _ = gate.avaliar(raiz)
        self.assertEqual(problemas, [], problemas)

    def test_nitidez_e_medida_na_maior_variante_legivel(self):
        # avif não abre no Pillow: a medida usa o webp ou jpg irmão e não derruba nem passa em silêncio
        raiz = self.projeto([self.sec("a", "foto1-800.jpg")], [self.foto_ok(1)], {"foto1-800.jpg": (1, True)})
        (raiz / "dist" / "img" / "foto1-800.avif").write_bytes(b"x")
        problemas, _ = gate.avaliar(raiz)
        self.assertEqual(problemas, [], problemas)

    def test_pessoa_de_banco_com_aviso_na_primeira_secao_e_so_aviso(self):
        raiz = self.projeto([self.sec("topo", "foto1-800.jpg", texto="Imagem ilustrativa de banco de imagens."), self.sec("b", "foto2-800.jpg")],
                            [linha("img/foto1-800.jpg", "https://unsplash.com/photos/o1", pessoa="sim", autorizacao="não: a licença Unsplash não cobre as retratadas"),
                             self.foto_ok(2)],
                            {"foto1-800.jpg": (1, True), "foto2-800.jpg": (2, True)})
        problemas, avisos = gate.avaliar(raiz)
        self.assertEqual(problemas, [], problemas)
        self.assertTrue(any("tráfego real" in a and "foto1" in a for a in avisos), avisos)

    def test_pessoa_de_banco_com_trafego_real_reprova(self):
        raiz = self.projeto([self.sec("topo", "foto1-800.jpg", texto="Imagem ilustrativa de banco de imagens.")],
                            [linha("img/foto1-800.jpg", "https://unsplash.com/photos/o1", pessoa="sim", autorizacao="não")],
                            {"foto1-800.jpg": (1, True)})
        problemas, _ = gate.avaliar(raiz, trafego_real=True)
        self.assertTrue(any("pessoa identificável sem autorização" in p for p in problemas), problemas)

    def test_pessoa_de_banco_sem_aviso_na_primeira_tela_reprova(self):
        raiz = self.projeto([self.sec("topo", "foto1-800.jpg"), self.sec("b", "foto2-800.jpg")],
                            [linha("img/foto1-800.jpg", "https://unsplash.com/photos/o1", pessoa="sim", autorizacao="não"), self.foto_ok(2)],
                            {"foto1-800.jpg": (1, True), "foto2-800.jpg": (2, True)})
        problemas, _ = gate.avaliar(raiz)
        self.assertTrue(any("primeira tela" in p and "imagem ilustrativa" in p for p in problemas), problemas)

    def test_cli_imprime_aviso_e_sai_zero(self):
        raiz = self.projeto([self.sec("topo", "foto1-800.jpg", texto="Imagem ilustrativa de banco de imagens.")],
                            [linha("img/foto1-800.jpg", "https://unsplash.com/photos/o1", pessoa="sim", autorizacao="não")],
                            {"foto1-800.jpg": (1, True)})
        r = subprocess.run([sys.executable, str(AQUI / "gate-imagens.py"), "--projeto", str(raiz)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("AVISO", r.stdout)
        self.assertIn("tráfego real", r.stdout)
        r2 = subprocess.run([sys.executable, str(AQUI / "gate-imagens.py"), "--projeto", str(raiz), "--trafego-real"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r2.returncode, 1, r2.stdout)


class AssinaturaEmFoto(GateImagensV35):
    """3.5.9 (N22): o momento assinatura em FOTO real repete a MESMA foto em 3 seções. data-assinatura (na <figure> ou na <img>)
    libera essa foto; a mesma foto sem a marca continua reprovando, e a marca em fotos diferentes reprova."""

    def fig(self, nome, arquivo, marca=True):
        m = " data-assinatura" if marca else ""
        return f'<section id="{nome}"><h2>{nome}</h2><figure{m}><img src="img/{arquivo}" alt="foto" width="640" height="480"></figure></section>'

    def avaliar(self, secoes, n_fotos=2):
        fotos = {f"foto{i}-800.jpg": (i, True) for i in range(1, n_fotos + 1)}
        raiz = self.projeto(secoes, [self.foto_ok(i) for i in range(1, n_fotos + 1)], fotos)
        return gate.avaliar(raiz)[0]

    def test_mesma_foto_em_tres_secoes_com_a_marca_na_figure_passa(self):
        p = self.avaliar([self.fig("topo", "foto1-800.jpg"), self.fig("meio", "foto1-800.jpg"), self.fig("fecho", "foto1-800.jpg")], 1)
        self.assertEqual(p, [], p)

    def test_marca_na_propria_img_tambem_libera(self):
        img = '<section id="{n}"><h2>{n}</h2><img data-assinatura src="img/foto1-800.jpg" alt="foto" width="640" height="480"></section>'
        p = self.avaliar([img.format(n="topo"), img.format(n="meio"), img.format(n="fecho")], 1)
        self.assertEqual(p, [], p)

    def test_mesma_foto_em_tres_secoes_sem_a_marca_continua_reprovando(self):
        p = self.avaliar([self.fig("topo", "foto1-800.jpg", False), self.fig("meio", "foto1-800.jpg", False), self.fig("fecho", "foto1-800.jpg", False)], 1)
        self.assertTrue(any("repetida" in x for x in p), p)

    def test_a_mesma_foto_solta_numa_seção_sem_a_marca_reprova(self):
        p = self.avaliar([self.fig("topo", "foto1-800.jpg"), self.fig("meio", "foto1-800.jpg"), self.fig("outra", "foto1-800.jpg", False)], 1)
        self.assertTrue(any("repetida" in x and "outra" in x for x in p), p)

    def test_marca_em_duas_fotos_diferentes_reprova(self):
        p = self.avaliar([self.fig("topo", "foto1-800.jpg"), self.fig("meio", "foto1-800.jpg"), self.fig("fecho", "foto2-800.jpg")], 2)
        self.assertTrue(any("data-assinatura em 2 fotos diferentes" in x for x in p), p)

    def test_foto_diferente_sem_marca_ao_lado_da_assinatura_passa(self):
        p = self.avaliar([self.fig("topo", "foto1-800.jpg"), self.fig("meio", "foto1-800.jpg"), self.fig("fecho", "foto2-800.jpg", False)], 2)
        self.assertEqual(p, [], p)


class DobraAviso(unittest.TestCase):
    """N9: a mensagem diferencia 'fora da primeira tela' de 'texto não achado'."""

    def test_aviso_fora_da_primeira_tela_mantem_a_mensagem(self):
        problemas = []
        gate.checar_dobra({"desk": {"foto": 0, "desenho": 0, "aviso": False, "avisoNaPagina": True}}, True, problemas)
        self.assertTrue(any("fora da primeira tela" in p for p in problemas), problemas)

    def test_aviso_que_nao_existe_na_pagina_diz_que_o_texto_nao_foi_achado(self):
        problemas = []
        gate.checar_dobra({"desk": {"foto": 0, "desenho": 0, "aviso": False, "avisoNaPagina": False}}, True, problemas)
        self.assertEqual(len(problemas), 1, problemas)
        self.assertIn("não achei o texto", problemas[0])
        self.assertIn("imagens ilustrativas", problemas[0])
        self.assertNotIn("fora da primeira tela", problemas[0])

    def test_aviso_na_tela_nao_reprova(self):
        problemas = []
        gate.checar_dobra({"desk": {"foto": 100, "desenho": 0, "aviso": True, "avisoNaPagina": True}}, True, problemas)
        self.assertEqual(problemas, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
