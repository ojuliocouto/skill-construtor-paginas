"""Etapa PLANO (03/10/2026): o aluno aprova referências, visual, seções, copy, pixel e código
num documento único antes da primeira linha de código.

Decisão do dono: "seria bom se essa skill desse opções de visual e tipos de seções pro cara,
inclusive uma etapa de planejamento pra copy, pixel, código, referências". O gate-plano.py
reprova o PLANO.md incompleto; o gate-rastreamento.py reprova a dist/ sem os eventos que o
plano pediu. Cada mutante abaixo é um jeito real de pular a etapa.
"""
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
import zlib
import struct

AQUI = pathlib.Path(__file__).resolve().parent
GATE = AQUI / "gate-plano.py"
RASTREIO = AQUI / "gate-rastreamento.py"


def png(caminho, w=8, h=8):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    cru = b"".join(b"\x00" + b"\xff\xff\xff" * w for _ in range(h))
    def bloco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
    caminho.write_bytes(b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                        + bloco(b"IDAT", zlib.compress(cru)) + bloco(b"IEND", b""))


MINIS = ["dobra-split-imagem", "dobra-faixa-cheia", "dobra-tipografica", "caixas-iguais", "lista-editorial",
         "comparacao-assimetrica", "linha-do-tempo", "credencial-retrato", "oferta-bloco-unico",
         "faq-coluna-centrada", "fecho-faixa-cheia"]

PLANO = """# PLANO: Estúdio de teste

Pixel pedido: Meta e GA4

Momento assinatura: a coluna vertebral em SVG; seções: topo, avaliação, fecho; estados: torta -> alinhada

Ícone do site: a coluna vertebral em 32 px, em traço único

Material da cliente pedido:
- foto real da profissional
- número do WhatsApp
- depoimentos com autorização

## a. Referências

Marque com [x] as que você gosta.

- [x] Kins: ![Kins](referencias/kins-dobra.png) O que essa faz bem: foto do público em casa.
- [ ] Tia: ![Tia](referencias/tia-dobra.png) O que essa faz bem: split meio a meio.

## b. Visual

### Direção A: Prumo
![Direção A](plano/direcao-a.png)
Tipografia, paleta, imagem e ritmo.

### Direção B: Faixa
![Direção B](plano/direcao-b.png)
Tipografia, paleta, imagem e ritmo.

### Direção C: Caderno
![Direção C](plano/direcao-c.png)
Tipografia, paleta, imagem e ritmo.

As três lado a lado: ![Comparação](plano/direcoes.png)

Escolha: [x] A  [ ] B  [ ] C  [ ] misturar

## c. Seções

{minis}

### Ordem escolhida

1. Primeira dobra: split com imagem
2. Dor: lista editorial
3. Como funciona: linha do tempo
4. Fecho: faixa cheia

### Composição por seção

| Seção | Desktop | Celular | Animação |
|---|---|---|---|
| Primeira dobra | foto sangrando à direita, texto à esquerda | foto quadrada e cartão em arco | abertura-do-topo: a foto abre de cima para baixo |
| Dor | título fixo e frases com recuo alternado | frases em coluna | texto-em-linhas: uma frase depois da outra |
| Como funciona | coluna fixa e passos ao lado | coluna em faixa estreita | assinatura: a coluna se alinha com a rolagem |
| Fecho | texto à esquerda e coluna grande à direita | coluna pequena ao lado do título | assinatura: a coluna termina de se alinhar |

## d. Copy

| Seção | Frase | Linha do briefing que sustenta |
|---|---|---|
| Primeira dobra | Pilates com fisioterapeuta em Niterói | "pilates com fisioterapeuta" |
| Oferta | Aula experimental gratuita | "aula experimental gratuita" |
| Fecho | Fale no WhatsApp | PENDENTE: número do WhatsApp |

### Pendências do cliente

- Número do WhatsApp

## e. Pixel e rastreamento

Meta Pixel e GA4, IDs na conta da aluna. Eventos: clique_whatsapp, clique_cta, rolagem_50,
rolagem_90, envio_formulario.

## f. Código e publicação

HTML + Tailwind compilado. Endereço de teste com noindex e robots.txt bloqueando; og:image
absoluta no domínio final.

## g. Aprovação

- [x] a. Referências
- [x] b. Visual
- [x] c. Seções
- [x] d. Copy
- [x] e. Pixel e rastreamento
- [x] f. Código e publicação
"""


def montar(raiz, texto=None, sem=()):
    for nome in ("referencias/kins-dobra.png", "referencias/tia-dobra.png", "plano/direcao-a.png",
                 "plano/direcao-b.png", "plano/direcao-c.png", "plano/direcoes.png"):
        if nome not in sem:
            png(raiz / nome)
    for m in MINIS:
        png(raiz / "plano" / "miniaturas" / f"{m}.png")
    if texto is None:
        minis = "\n".join(f"- {m}: ![{m}](plano/miniaturas/{m}.png) Quando usar: teste." for m in MINIS)
        texto = PLANO.format(minis=minis)
    (raiz / "PLANO.md").write_text(texto, encoding="utf-8")
    return texto


class GatePlano(unittest.TestCase):
    def rodar(self, mutar=None, sem=()):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = pathlib.Path(pasta)
            texto = montar(raiz, sem=sem)
            if mutar:
                (raiz / "PLANO.md").write_text(mutar(texto), encoding="utf-8")
            r = subprocess.run([sys.executable, str(GATE), "--projeto", str(raiz)], capture_output=True, text=True, encoding="utf-8")
            return r.returncode, r.stdout + r.stderr

    def test_plano_completo_passa(self):
        code, out = self.rodar()
        self.assertEqual(code, 0, out)
        self.assertIn("PASSA", out)

    def test_sem_secao_de_pixel_reprova(self):
        code, out = self.rodar(lambda t: t.replace("## e. Pixel e rastreamento", "## Outra coisa"))
        self.assertEqual(code, 1, out)
        self.assertIn("Pixel", out)

    def test_so_duas_previas_de_visual_reprova(self):
        code, out = self.rodar(sem=("plano/direcao-c.png",))
        self.assertEqual(code, 1, out)
        self.assertIn("direcao-c.png", out)

    def test_duas_direcoes_reprova(self):
        def corta(t):
            i, j = t.index("### Direção C"), t.index("As três lado a lado")
            return t[:i] + t[j:]
        code, out = self.rodar(corta)
        self.assertEqual(code, 1, out)

    def test_sem_comparacao_lado_a_lado_reprova(self):
        code, out = self.rodar(sem=("plano/direcoes.png",))
        self.assertEqual(code, 1, out)

    def test_copy_sem_sustentacao_reprova(self):
        code, out = self.rodar(lambda t: t.replace('| "aula experimental gratuita" |', "|  |"))
        self.assertEqual(code, 1, out)
        self.assertIn("sustent", out.lower())

    def test_copy_sem_coluna_de_sustentacao_reprova(self):
        code, out = self.rodar(lambda t: t.replace("| Linha do briefing que sustenta |", "| Observação |"))
        self.assertEqual(code, 1, out)

    def test_pendente_sem_lista_de_pendencias_reprova(self):
        code, out = self.rodar(lambda t: t.replace("### Pendências do cliente\n\n- Número do WhatsApp\n", ""))
        self.assertEqual(code, 1, out)

    def test_aprovacao_desmarcada_reprova(self):
        code, out = self.rodar(lambda t: t.replace("- [x] d. Copy", "- [ ] d. Copy"))
        self.assertEqual(code, 1, out)
        self.assertIn("Copy", out)

    def test_aprovacao_faltando_item_reprova(self):
        code, out = self.rodar(lambda t: t.replace("- [x] f. Código e publicação\n", ""))
        self.assertEqual(code, 1, out)

    def test_nenhuma_referencia_marcada_reprova(self):
        code, out = self.rodar(lambda t: t.replace("- [x] Kins", "- [ ] Kins"))
        self.assertEqual(code, 1, out)

    def test_referencia_sem_faz_bem_reprova(self):
        code, out = self.rodar(lambda t: t.replace("O que essa faz bem: split meio a meio.", ""))
        self.assertEqual(code, 1, out)

    def test_sem_ordem_escolhida_reprova(self):
        code, out = self.rodar(lambda t: t.replace("### Ordem escolhida", "### Ideias"))
        self.assertEqual(code, 1, out)

    def test_cardapio_sem_miniaturas_reprova(self):
        code, out = self.rodar(lambda t: "\n".join(l for l in t.splitlines() if "miniaturas/" not in l))
        self.assertEqual(code, 1, out)
        self.assertIn("miniatura", out.lower())

    def test_id_real_de_ga4_no_plano_reprova(self):
        code, out = self.rodar(lambda t: t.replace("Meta Pixel e GA4,", "Meta Pixel e GA4 (G-4K7Q2ZP9LM),"))
        self.assertEqual(code, 1, out)
        self.assertIn("ID", out)

    def test_id_real_de_meta_pixel_no_plano_reprova(self):
        code, out = self.rodar(lambda t: t.replace("Meta Pixel e GA4,", "Meta Pixel 1234567890123456 e GA4,"))
        self.assertEqual(code, 1, out)

    def test_eventos_faltando_reprova(self):
        code, out = self.rodar(lambda t: t.replace("rolagem_90, ", ""))
        self.assertEqual(code, 1, out)
        self.assertIn("rolagem_90", out)

    def test_sem_pixel_declarado_dispensa_eventos(self):
        def tira(t):
            t = t.replace("Pixel pedido: Meta e GA4", "Pixel pedido: nenhum")
            return t.replace("Eventos: clique_whatsapp, clique_cta, rolagem_50,\nrolagem_90, envio_formulario.",
                             "A aluna não vai anunciar agora; quando for, volta a esta seção.")
        code, out = self.rodar(tira)
        self.assertEqual(code, 0, out)

    def test_sem_linha_pixel_pedido_reprova(self):
        code, out = self.rodar(lambda t: t.replace("Pixel pedido: Meta e GA4\n", ""))
        self.assertEqual(code, 1, out)

    def test_codigo_sem_noindex_reprova(self):
        code, out = self.rodar(lambda t: t.replace("noindex", "sem índice"))
        self.assertEqual(code, 1, out)
        self.assertIn("noindex", out)

    # v3.5 (padrão da v7): o plano nomeia o momento assinatura, a composição de cada seção e o
    # material que só a cliente tem. A v6 era correta e genérica porque nada disso estava escrito.
    def test_sem_momento_assinatura_reprova(self):
        code, out = self.rodar(lambda t: re.sub(r"Momento assinatura:.*\n", "", t))
        self.assertEqual(code, 1, out)
        self.assertIn("Momento assinatura", out)

    # v3.5.6 (achado A8): o ícone do site é decidido no plano, não descoberto no passo e.4.
    def test_sem_icone_do_site_reprova(self):
        code, out = self.rodar(lambda t: re.sub(r"Ícone do site:.*\n", "", t))
        self.assertEqual(code, 1, out)
        self.assertIn("Ícone do site", out)

    def test_icone_do_site_com_modelo_nao_preenchido_reprova(self):
        code, out = self.rodar(lambda t: re.sub(r"Ícone do site:.*\n", "Ícone do site: <motivo>\n", t))
        self.assertEqual(code, 1, out)

    def test_momento_assinatura_em_duas_secoes_reprova(self):
        code, out = self.rodar(lambda t: t.replace("seções: topo, avaliação, fecho", "seções: topo, fecho"))
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"3 ou mais|pelo menos 3")

    def test_momento_assinatura_sem_estados_reprova(self):
        code, out = self.rodar(lambda t: t.replace("; estados: torta -> alinhada", ""))
        self.assertEqual(code, 1, out)
        self.assertIn("estados", out.lower())

    def test_momento_assinatura_estados_sem_mudanca_reprova(self):
        code, out = self.rodar(lambda t: t.replace("torta -> alinhada", "alinhada"))
        self.assertEqual(code, 1, out)

    def test_momento_assinatura_sem_elemento_reprova(self):
        code, out = self.rodar(lambda t: t.replace("Momento assinatura: a coluna vertebral em SVG;", "Momento assinatura: ;"))
        self.assertEqual(code, 1, out)
        self.assertIn("elemento", out.lower())

    def test_momento_assinatura_em_linhas_separadas_passa(self):
        def separa(t):
            return t.replace("Momento assinatura: a coluna vertebral em SVG; seções: topo, avaliação, fecho; estados: torta -> alinhada",
                             "Momento assinatura: a coluna vertebral em SVG\n- Seções: topo, avaliação, fecho\n- Estados: torta -> alinhada")
        code, out = self.rodar(separa)
        self.assertEqual(code, 0, out)

    def test_sem_tabela_de_composicao_reprova(self):
        def tira(t):
            i, j = t.index("### Composição por seção"), t.index("## d. Copy")
            return t[:i] + t[j:]
        code, out = self.rodar(tira)
        self.assertEqual(code, 1, out)
        self.assertIn("Composição", out)

    def test_tabela_de_composicao_com_celula_vazia_reprova(self):
        code, out = self.rodar(lambda t: t.replace("| frases em coluna |", "|  |"))
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"vazia|sem Celular")

    def test_tabela_de_composicao_com_menos_linhas_que_secoes_reprova(self):
        code, out = self.rodar(lambda t: re.sub(r"\| Dor \|.*\n", "", t))
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"uma linha por seção")

    def test_tres_secoes_com_a_mesma_animacao_reprova(self):
        def mesma(t):
            t = t.replace("texto-em-linhas: uma frase depois da outra", "revelar-ao-entrar: sobe")
            t = t.replace("abertura-do-topo: a foto abre de cima para baixo", "revelar-ao-entrar: sobe")
            return t.replace("assinatura: a coluna se alinha com a rolagem", "revelar-ao-entrar: sobe")
        code, out = self.rodar(mesma)
        self.assertEqual(code, 1, out)
        self.assertIn("revelar-ao-entrar", out)

    def test_duas_secoes_com_a_mesma_animacao_passa(self):
        def duas(t):
            t = t.replace("texto-em-linhas: uma frase depois da outra", "revelar-ao-entrar: sobe")
            return t.replace("abertura-do-topo: a foto abre de cima para baixo", "revelar-ao-entrar: sobe")
        code, out = self.rodar(duas)
        self.assertEqual(code, 0, out)

    # v3.5.10 (achado P4 da página Torra Clara): o tipo da animação de cada seção vem do repertório
    # (references/receitas-de-movimento.md) ou declara `criação nova: <motivo>`.
    def test_tipo_de_animacao_fora_do_repertorio_reprova(self):
        code, out = self.rodar(lambda t: t.replace("texto-em-linhas: uma frase depois da outra",
                                                   "frases em sequência: uma depois da outra"))
        self.assertEqual(code, 1, out)
        self.assertIn("repertório", out)
        self.assertIn("frases em sequência", out)
        self.assertIn("Dor", out)

    def test_caso_original_do_p4_continua_reprovando(self):
        # O plano da Torra Clara aprovado na 3.5.9 usava descrições soltas ("abertura da foto").
        code, out = self.rodar(lambda t: t.replace("abertura-do-topo: a foto abre de cima para baixo",
                                                   "abertura da foto: a foto abre de cima para baixo"))
        self.assertEqual(code, 1, out)
        self.assertIn("abertura da foto", out)

    def test_animacao_sem_dois_pontos_e_sem_receita_reprova(self):
        code, out = self.rodar(lambda t: t.replace("texto-em-linhas: uma frase depois da outra", "uma frase depois da outra"))
        self.assertEqual(code, 1, out)
        self.assertIn("repertório", out)

    def test_criacao_nova_com_motivo_passa(self):
        code, out = self.rodar(lambda t: t.replace(
            "texto-em-linhas: uma frase depois da outra",
            "criação nova: o rótulo se imprime linha a linha (nenhuma receita mostra um rótulo que responde à escolha)"))
        self.assertEqual(code, 0, out)

    def test_criacao_nova_sem_motivo_reprova(self):
        for cel in ("criação nova", "criação nova:", "criação nova: x", "criacao nova: sei lá"):
            code, out = self.rodar(lambda t, c=cel: t.replace("texto-em-linhas: uma frase depois da outra", c))
            self.assertEqual(code, 1, f"{cel!r}: {out}")
            self.assertIn("criação nova", out)

    def test_criacao_nova_disfarcada_de_receita_reprova(self):
        # Não vale colar o nome de uma receita dentro de "criação nova" nem inventar um nome parecido.
        for cel in ("criação nova texto-em-linhas: uma frase depois da outra", "texto-em-linhas-2: uma frase depois da outra",
                    "texto-em-linha: uma frase depois da outra"):
            code, out = self.rodar(lambda t, c=cel: t.replace("texto-em-linhas: uma frase depois da outra", c))
            self.assertEqual(code, 1, f"{cel!r}: {out}")

    def test_nome_de_receita_com_espacos_e_maiuscula_passa(self):
        code, out = self.rodar(lambda t: t.replace("texto-em-linhas: uma frase depois da outra", "Texto em linhas: uma frase depois da outra"))
        self.assertEqual(code, 0, out)

    def test_todo_nome_de_receita_do_repertorio_e_aceito(self):
        import re as _re
        nomes = _re.findall(r"(?m)^##\s+Receita:\s*(\S+)\s*$", (AQUI.parent / "references" / "receitas-de-movimento.md").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(nomes), 10)
        for n in nomes:
            code, out = self.rodar(lambda t, n=n: t.replace("texto-em-linhas: uma frase depois da outra", f"{n}: uma frase"))
            self.assertEqual(code, 0, f"{n}: {out}")

    def test_sem_material_da_cliente_reprova(self):
        code, out = self.rodar(lambda t: t.replace("Material da cliente pedido:", "Outra coisa:"))
        self.assertEqual(code, 1, out)
        self.assertIn("Material da cliente", out)

    def test_material_da_cliente_vazio_reprova(self):
        def vazio(t):
            return re.sub(r"Material da cliente pedido:\n(?:- .*\n)+", "Material da cliente pedido:\n\n", t)
        code, out = self.rodar(vazio)
        self.assertEqual(code, 1, out)

    def test_material_da_cliente_em_uma_linha_passa(self):
        def linha(t):
            return re.sub(r"Material da cliente pedido:\n(?:- .*\n)+",
                          "Material da cliente pedido: foto real da profissional; número do WhatsApp\n", t)
        code, out = self.rodar(linha)
        self.assertEqual(code, 0, out)

    def test_material_nenhum_sem_motivo_reprova(self):
        def nenhum(t):
            return re.sub(r"Material da cliente pedido:\n(?:- .*\n)+", "Material da cliente pedido: nenhum\n", t)
        code, out = self.rodar(nenhum)
        self.assertEqual(code, 1, out)

    def test_material_nenhum_com_motivo_passa(self):
        def nenhum(t):
            return re.sub(r"Material da cliente pedido:\n(?:- .*\n)+",
                          "Material da cliente pedido: nenhum, porque a página é institucional e o dono já mandou tudo no briefing\n", t)
        code, out = self.rodar(nenhum)
        self.assertEqual(code, 0, out)

    def test_sem_plano_reprova(self):
        with tempfile.TemporaryDirectory() as pasta:
            r = subprocess.run([sys.executable, str(GATE), "--projeto", pasta], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 1, r.stdout)


SNIPPET = """<script>window.RASTREIO = { metaPixel: "", ga4: "" };</script>
<script>
(function () {
  var c = window.RASTREIO || {};
  if (c.metaPixel) { /* connect.facebook.net/en_US/fbevents.js */ fbq('init', c.metaPixel); }
  if (c.ga4) { /* www.googletagmanager.com/gtag/js */ gtag('config', c.ga4); }
  document.addEventListener('click', function (e) { var a = e.target.closest('[data-evento]'); });
  var marcos = { 50: 'rolagem_50', 90: 'rolagem_90' };
})();
</script>"""

PAGINA = """<!doctype html><html lang="pt-BR"><head><title>T</title>{snippet}</head><body>
<a href="#oferta" data-evento="clique_cta">Ver como funciona</a>
<a href="https://wa.me/5521999999999" data-evento="clique_whatsapp">Agendar pelo WhatsApp</a>
<form data-evento="envio_formulario"><input name="n"><button>Enviar</button></form>
</body></html>"""


class GateRastreamento(unittest.TestCase):
    def rodar(self, html, pedido="meta,ga4"):
        with tempfile.TemporaryDirectory() as pasta:
            dist = pathlib.Path(pasta) / "dist"
            dist.mkdir()
            (dist / "index.html").write_text(html, encoding="utf-8")
            r = subprocess.run([sys.executable, str(RASTREIO), "--dist", str(dist), "--pedido", pedido],
                               capture_output=True, text=True, encoding="utf-8")
            return r.returncode, r.stdout + r.stderr

    def test_pagina_ligada_passa(self):
        code, out = self.rodar(PAGINA.format(snippet=SNIPPET))
        self.assertEqual(code, 0, out)

    def test_sem_snippet_reprova(self):
        code, out = self.rodar(PAGINA.format(snippet=""))
        self.assertEqual(code, 1, out)

    def test_whatsapp_sem_evento_reprova(self):
        code, out = self.rodar(PAGINA.format(snippet=SNIPPET).replace(' data-evento="clique_whatsapp"', ""))
        self.assertEqual(code, 1, out)
        self.assertIn("clique_whatsapp", out)

    def test_sem_cta_marcado_reprova(self):
        code, out = self.rodar(PAGINA.format(snippet=SNIPPET).replace(' data-evento="clique_cta"', ""))
        self.assertEqual(code, 1, out)

    def test_formulario_sem_evento_reprova(self):
        code, out = self.rodar(PAGINA.format(snippet=SNIPPET).replace(' data-evento="envio_formulario"', ""))
        self.assertEqual(code, 1, out)

    def test_sem_rolagem_reprova(self):
        code, out = self.rodar(PAGINA.format(snippet=SNIPPET.replace("rolagem_90", "rolagem_x")))
        self.assertEqual(code, 1, out)

    def test_so_ga4_pedido_nao_exige_meta(self):
        sem_meta = SNIPPET.replace("fbq('init', c.metaPixel);", "").replace("connect.facebook.net/en_US/fbevents.js", "")
        code, out = self.rodar(PAGINA.format(snippet=sem_meta), pedido="ga4")
        self.assertEqual(code, 0, out)

    def test_nenhum_pedido_passa_sem_nada(self):
        code, out = self.rodar("<html><body><a href='https://wa.me/1'>x</a></body></html>", pedido="nenhum")
        self.assertEqual(code, 0, out)

    def test_le_o_pedido_do_plano(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = pathlib.Path(pasta)
            (raiz / "dist").mkdir()
            (raiz / "dist" / "index.html").write_text(PAGINA.format(snippet=""), encoding="utf-8")
            (raiz / "PLANO.md").write_text("Pixel pedido: Meta e GA4\n", encoding="utf-8")
            r = subprocess.run([sys.executable, str(RASTREIO), "--dist", str(raiz / "dist"), "--plano",
                                str(raiz / "PLANO.md")], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 1, r.stdout)

    def test_snippet_da_referencia_passa_no_gate_e_sem_comentario(self):
        # O snippet que o aluno copia de references/rastreamento.md tem que passar nos dois gates
        # que a dist/ enfrenta: o de rastreamento e o de comentário interno da publicação.
        import importlib.util
        import re
        ref = (AQUI.parent / "references" / "rastreamento.md").read_text(encoding="utf-8")
        snippet = re.search(r"```html\n(.*?)```", ref, re.S).group(1)
        pagina = PAGINA.format(snippet=snippet)
        code, out = self.rodar(pagina)
        self.assertEqual(code, 0, out)
        spec = importlib.util.spec_from_file_location("pub", AQUI / "gate-publicacao.py")
        pub = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pub)
        self.assertEqual(pub.comentarios_internos(pagina), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
