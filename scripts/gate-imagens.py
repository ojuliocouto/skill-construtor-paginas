"""GATE DE IMAGENS: licença completa, direito de imagem e aviso de "imagem ilustrativa", inclusive
na prévia do link (og-image).

Por que existe (02/10/2026, auditoria da v4 do estúdio, nota 6,5). A foto do herói era de um
estúdio real, com duas pessoas identificáveis; a Wikimedia Commons registrava a permissão da
fotógrafa, não a autorização de imagem das retratadas para anunciar outro negócio (no Brasil,
uso comercial de imagem sem autorização gera indenização sem prova de dano, Súmula 403 do STJ).
O crédito do rodapé dizia "Creative Commons BY-SA" sem a versão 3.0, sem link para a licença e
sem dizer que a versão retocada seguia a mesma licença. E o og-image, que é o que a visitante
vê primeiro no WhatsApp, saía sem "imagem ilustrativa". `imagens/LICENCAS.md` listava as
condições; nada conferia.

Lê `imagens/LICENCAS.md` (tabela com as colunas Arquivo publicado, Origem, Autor, Título,
Licença, Link da licença, Alteração, Pessoa identificável, Autorização de imagem, Aviso de
ilustrativa) e a `dist/`. Reprova (exit 1):
  1. imagem publicada na dist/ (inclusive o og-image) sem linha na tabela;
  2. licença sem link; Creative Commons sem versão (3.0, 4.0) ou com link fora de
     creativecommons.org, sem autor ou sem título;
  3. pessoa identificável sem autorização de imagem: prefira foto sem pessoa identificável ou
     ilustração própria (foto do cliente com autorização das retratadas passa);
  4. og-image que não é do cliente sem aviso de "imagem ilustrativa";
  5. crédito incompleto na página: para CC, autor, título, licença COM versão e link para a
     licença no HTML publicado; imagem CC BY-SA alterada sem "mesma licença" escrito;
  6. página com imagem que não é do cliente e sem "imagem ilustrativa" no texto;
  7. (auditoria da v5, 03/10/2026) título que não é o da fonte: quando a origem é uma URL com
     o título no endereço (Unsplash, Wikimedia), o Título da tabela tem de estar nele; e todo
     trecho entre aspas no crédito da página (na frase com o nome do autor) tem de ser o
     Título da tabela. A v5 publicou Foto "Sala de pilates com aparelhos" para uma foto que
     no Unsplash se chama "a room filled with lots of different types of equipment".
Ilustração própria (Origem com "ilustração própria" ou "desenho próprio") não pede link de
licença nem "imagem ilustrativa": é da página, não de terceiro.
Favicon, apple-touch-icon e fontes ficam de fora.

v3.5 (padrão da v7, 04/10/2026). A v7 do estúdio saiu muito melhor que a v6 com foto de banco
no lugar da ilustração chapada, e isso trouxe cinco regras que nenhum gate cobrava:
  8. FOTO REPETIDA ENTRE SEÇÕES: a mesma cena (mesma origem em LICENCAS.md, ou hash perceptual
     pHash de 64 bits a menos de 10 bits de distância) em duas seções reprova; os recortes da
     mesma foto dentro de UMA seção (arte dirigida para o celular) passam;
  9. NITIDEZ relativa (laplaciano da foto / da foto desfocada): abaixo de 2,5 reprova, abaixo de 6 avisa (foto borrada: o auditor mediu 8,6 a
     21,7 nos recortes de baixa profundidade de campo, contra mais de 1.000 nos nítidos), medida
     na maior variante legível de cada foto (avif não abre no Pillow: vale o webp ou jpg irmão);
 10. PESSOA IDENTIFICÁVEL DE BANCO (Unsplash, Pexels) sem autorização das retratadas deixou de
     bloquear a página de teste: vira AVISO "bloqueia tráfego real", desde que "imagem
     ilustrativa" esteja visível na primeira tela. Com `--trafego-real` volta a reprovar;
 11. AVISO NA PRIMEIRA TELA: com essa foto na página, "imagem ilustrativa" tem de estar dentro da
     primeira tela em 1440 e em 390 (com `--url`, medido pelo navegador; sem ele, a checagem é
     estática: o texto dentro do cabeçalho ou da primeira seção);
 12. FOTO REAL ANTES DE ILUSTRAÇÃO (só com `--url`): na primeira tela, em 1440 e em 390, a área
     de foto (img) é pelo menos 60% da área de imagem (foto + desenho em SVG). Acento pequeno
     passa; ilustração chapada como imagem principal reprova. `data-ilustracao-ok="motivo"` no
     SVG o tira da conta.
Mede com Pillow e numpy (`pip install pillow numpy`).

Uso: node scripts/py.mjs gate-imagens.py --projeto <dir> [--dist <dir>/dist] [--url <url>] [--trafego-real]
"""
import argparse
import html as html_mod
import json
import re
import subprocess
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".svg"}
LEGIVEIS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
LIMIAR_PHASH = 10          # distância de Hamming (de 64 bits) abaixo da qual duas fotos são a mesma cena
# Nitidez RELATIVA: detalhe fino da foto dividido pelo da mesma foto desfocada (raio 1,5).
# O laplaciano absoluto confunde pouco contraste com borrado (paleta bege nítida dava 8,6;
# medido na v7 em 04/10/2026). Desfocada com raio 2: 1,2 a 1,7. Nítidas: 18 a 42. Macias: 4 a 6.
NITIDEZ_REPROVA = 2.5      # abaixo disso a foto já está borrada (reprova)
NITIDEZ_AVISA = 6.0        # abaixo disso a foto está macia (aviso, decisão de quem constrói)
LADO_MEDIDA_NITIDEZ = 800  # mede sempre na mesma escala
LADO_MINIMO_NITIDEZ = 300  # miniatura e ícone não entram na medida de nitidez
FOTO_NA_DOBRA_MINIMA = 0.6
BANCOS = ("unsplash", "pexels", "pixabay")
AQUI = Path(__file__).resolve().parent
FORA = re.compile(r"^(favicon|apple-touch-icon|android-chrome|mstile)", re.I)
COLUNAS = {
    "arquivo": ("arquivo publicado", "arquivo"),
    "origem": ("origem",),
    "autor": ("autor",),
    "titulo": ("titulo",),
    "licenca": ("licenca",),
    "link": ("link da licença",),
    "alteracao": ("alteracao",),
    "pessoa": ("pessoa identificavel",),
    "autorizacao": ("autorização de imagem",),
    "aviso": ("aviso de ilustrativa",),
}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def sim(valor):
    return norm(valor).startswith(("sim", "yes"))


def ler_tabela(md):
    linhas = [l.strip() for l in md.splitlines() if l.strip().startswith("|")]
    for i, l in enumerate(linhas):
        cab = [norm(c) for c in l.strip("|").split("|")]
        if "licenca" in cab and any(c.startswith("arquivo") for c in cab):
            mapa = {}
            for chave, nomes in COLUNAS.items():
                for j, c in enumerate(cab):
                    if c in [norm(n) for n in nomes]:
                        mapa[chave] = j
                        break
            itens = []
            for l2 in linhas[i + 1:]:
                cel = [c.strip() for c in l2.strip("|").split("|")]
                if all(re.fullmatch(r":?-+:?", c) for c in cel if c):
                    continue
                if len(cel) < len(cab):
                    break
                itens.append({k: cel[j] for k, j in mapa.items()})
            return mapa, itens
    return {}, []


def base(nome):
    stem = Path(nome).stem
    return re.sub(r"-\d{2,4}$", "", stem)


def texto_visivel(h):
    h = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", h)
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", h)).split())


def eh_cc(licenca):
    return bool(re.search(r"\bcc\b|creative commons", norm(licenca)))


def do_cliente(item):
    return any(norm(k) in norm(item.get("origem", "") + " " + item.get("licenca", "")) for k in ("do cliente", "da cliente", "própria do cliente"))


def propria(item):
    return any(norm(k) in norm(item.get("origem", "")) for k in ("ilustração própria", "desenho próprio", "ilustrações próprias"))


def titulo_da_url(origem):
    """Título legível no endereço da fonte (slug do Unsplash, nome do arquivo da Wikimedia)."""
    m = re.match(r"https?://\S+", origem or "")
    if not m:
        return ""
    ultimo = re.sub(r"[?#].*$", "", m.group(0)).rstrip("/").split("/")[-1]
    ultimo = re.sub(r"^(file|arquivo):", "", ultimo, flags=re.I)
    ultimo = re.sub(r"\.(jpe?g|png|webp|gif|tiff?)$", "", ultimo, flags=re.I)
    return norm(re.sub(r"[-_%]+", " ", ultimo))


def plano(s):
    """Texto comparável: sem acento, sem caixa e com hífen e sublinhado tratados como espaço (o endereço da
    fonte escreve 'Close-up' como 'Close-up_of'; o título real pode ter hífen). Vale dos dois lados."""
    return norm(re.sub(r"[-_]+", " ", str(s)))


_BLOCOS_DE_CREDITO = ("li", "p", "figcaption", "dd", "tr", "blockquote")


def unidade_do_credito(pagina, origem):
    """Texto do item de crédito (li, p, figcaption...) que traz o link para a origem desta foto, ou None quando
    a página não liga o crédito à foto por esse link. Casa o crédito com a foto pelo endereço da fonte, não
    pelo nome do autor: com várias fotos do mesmo autor, o nome não diz de qual foto é o crédito."""
    m = re.match(r"https?://\S+", origem or "")
    if not m:
        return None
    alvo = m.group(0).rstrip("/")
    baixo = pagina.lower()
    for ancora in re.finditer(r'href=["\']([^"\']+)["\']', pagina):
        if html_mod.unescape(ancora.group(1)).rstrip("/") != alvo:
            continue
        melhor_pos, melhor_tag = -1, None
        for tag in _BLOCOS_DE_CREDITO:
            pos = max(baixo.rfind(f"<{tag} ", 0, ancora.start()), baixo.rfind(f"<{tag}>", 0, ancora.start()))
            if pos > melhor_pos and baixo.find(f"</{tag}", pos, ancora.start()) == -1:
                melhor_pos, melhor_tag = pos, tag
        if melhor_tag is None:
            continue
        fim = baixo.find(f"</{melhor_tag}", ancora.start())
        if fim == -1:
            continue
        return texto_visivel(pagina[melhor_pos:fim])
    return None


def citacoes_do_credito(texto, autor):
    """Trechos entre aspas nas frases do texto da página que citam o autor."""
    if not autor.strip():
        return []
    achados = []
    for frase in re.split(r"(?<=[.!?])\s+", texto):
        if norm(autor) in norm(frase):
            achados += re.findall(r'["“]([^"”]{2,140})["”]', frase)
    return achados


class _Regioes(HTMLParser):
    """Divide o corpo em regiões (cada <section> de topo; header, footer e nav fora delas) e anota,
    por região, as imagens que ela usa e o texto que ela mostra."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.profundidade = 0
        self.n = 0
        self.regiao = "(fora de seção)"
        self.ordem = []
        self.imagens = {}
        self.texto = {}
        self.cabeca = False
        self.ignorar = 0

    def _abre(self, chave):
        self.regiao = chave
        if chave not in self.ordem:
            self.ordem.append(chave)
            self.imagens[chave] = []
            self.texto[chave] = []

    def _ref(self, valor):
        for parte in re.split(r",", valor or ""):
            alvo = parte.strip().split(" ")[0]
            if alvo and not alvo.startswith("data:"):
                nome = Path(urlparse(alvo).path).name
                if Path(nome).suffix.lower() in EXTENSOES:
                    self.imagens[self.regiao].append(nome)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "head":
            self.cabeca = True
        if tag in ("script", "style"):
            self.ignorar += 1
        if self.cabeca:
            return
        if not self.ordem:
            self._abre("(fora de seção)")
        if tag == "section":
            if self.profundidade == 0:
                self.n += 1
                self._abre(a.get("id") or f"seção {self.n}")
            self.profundidade += 1
        elif tag in ("header", "footer", "nav") and self.profundidade == 0:
            self._abre(tag)
        if tag in ("img", "source"):
            self._ref(a.get("src") or a.get("data-src"))
            self._ref(a.get("srcset"))
        for m in re.finditer(r"url\(['\"]?([^'\")]+)", a.get("style") or ""):
            self._ref(m.group(1))

    def handle_endtag(self, tag):
        if tag == "head":
            self.cabeca = False
        if tag in ("script", "style") and self.ignorar:
            self.ignorar -= 1
        if tag == "section" and self.profundidade:
            self.profundidade -= 1
            if self.profundidade == 0:
                self.regiao = "(fora de seção)"
                if self.regiao not in self.ordem:
                    self._abre(self.regiao)
        elif tag in ("header", "footer", "nav") and self.profundidade == 0:
            self.regiao = "(fora de seção)"
            if self.regiao not in self.ordem:
                self._abre(self.regiao)

    def handle_data(self, data):
        if self.cabeca or self.ignorar or not self.ordem:
            return
        self.texto[self.regiao].append(data)


def regioes_da_pagina(pagina):
    r = _Regioes()
    r.feed(pagina)
    return r


def aviso_na_primeira_regiao(r):
    """Checagem estática do aviso na primeira tela: o texto está no cabeçalho ou na primeira seção."""
    for chave in r.ordem:
        if "ilustrativa" in norm(" ".join(r.texto[chave])):
            return True
        if chave not in ("header", "nav", "(fora de seção)"):
            return False
    return False


def carregar_medidas():
    try:
        import numpy as np
        from PIL import Image
        return np, Image
    except ImportError:
        return None, None


def phash(np, Image, img):
    """pHash de 64 bits: DCT 2D de 32x32 em cinza, os 8x8 de baixa frequência contra a mediana."""
    a = np.asarray(img.convert("L").resize((32, 32), Image.LANCZOS), dtype=np.float64)
    k = np.arange(32)
    dct = np.cos(np.pi * (2 * k[None, :] + 1) * k[:, None] / 64.0)
    d = (dct @ a @ dct.T)[:8, :8].flatten()
    return d > np.median(d[1:])


def variancia_laplaciano(np, img):
    g = np.asarray(img.convert("L"), dtype=np.float64)
    if min(g.shape) < 3:
        return 0.0
    c = g[1:-1, 1:-1]
    lap = g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:] - 4 * c
    return float(lap.var())


def razao_nitidez(np, ImageFilter, img):
    """Laplaciano da foto / laplaciano da mesma foto desfocada, numa escala fixa."""
    im = img.convert("RGB")
    if max(im.size) > LADO_MEDIDA_NITIDEZ:
        f = LADO_MEDIDA_NITIDEZ / max(im.size)
        im = im.resize((max(3, round(im.size[0] * f)), max(3, round(im.size[1] * f))))
    base_ = variancia_laplaciano(np, im)
    borrada = variancia_laplaciano(np, im.filter(ImageFilter.GaussianBlur(1.5)))
    return base_ / max(borrada, 1e-6)


def maior_variante(Image, caminhos):
    """A maior variante que o Pillow abre (avif não abre: vale o webp ou jpg irmão)."""
    abertas = []
    for c in caminhos:
        if c.suffix.lower() not in LEGIVEIS:
            continue
        try:
            im = Image.open(c)
            im.load()
            abertas.append((im.size[0] * im.size[1], c, im))
        except Exception:
            continue
    if not abertas:
        return None, None
    abertas.sort(key=lambda x: x[0], reverse=True)
    return abertas[0][1], abertas[0][2]


def origem_normalizada(origem):
    m = re.search(r"https?://\S+", origem or "")
    return re.sub(r"[?#].*$", "", m.group(0)).rstrip("/").lower() if m else ""


def checar_fotos(dist, usados, regioes, problemas, avisos):
    """Regras 8 e 9: foto repetida entre seções e nitidez."""
    np, Image = carregar_medidas()
    if np is None:
        problemas.append("faltam pillow e numpy para medir repetição e nitidez das fotos: pip install pillow numpy")
        return
    por_base = {}
    for rel, it in usados:
        if Path(rel).stem.startswith("og-image") or propria(it):
            continue
        por_base.setdefault(base(Path(rel).name), {"item": it, "arquivos": []})["arquivos"].append(dist / rel)
    secoes_de = {}
    for chave in regioes.ordem:
        for nome in regioes.imagens[chave]:
            secoes_de.setdefault(base(nome), set()).add(chave)
    lidas = {}
    for b, info in sorted(por_base.items()):
        caminho, im = maior_variante(Image, info["arquivos"])
        if im is None:
            if any(c.suffix.lower() in LEGIVEIS for c in info["arquivos"]) or not any(c.suffix.lower() == ".svg" for c in info["arquivos"]):
                avisos.append(f"{b}: nenhuma variante legível pelo Pillow; repetição e nitidez não medidas")
            continue
        lidas[b] = (caminho, im)
        if max(im.size) >= LADO_MINIMO_NITIDEZ:
            from PIL import ImageFilter
            r = razao_nitidez(np, ImageFilter, im)
            if r < NITIDEZ_REPROVA:
                problemas.append(f"{b}: foto borrada, nitidez relativa {r:.1f} em {caminho.name} (mínimo {NITIDEZ_REPROVA}): "
                                 "troque pela foto nítida ou por outro recorte")
            elif r < NITIDEZ_AVISA:
                avisos.append(f"{b}: foto macia, nitidez relativa {r:.1f} em {caminho.name} (nítida fica acima de {NITIDEZ_AVISA}): "
                              "confira no print se o assunto está em foco; desfoque de fundo proposital pode ficar")
    # Cenas: mesma origem em LICENCAS.md ou pHash a menos de LIMIAR_PHASH bits.
    nomes = sorted(lidas)
    pai = {b: b for b in nomes}

    def raiz(b):
        while pai[b] != b:
            pai[b] = pai[pai[b]]
            b = pai[b]
        return b
    motivo = {}
    hashes = {b: phash(np, Image, lidas[b][1]) for b in nomes}
    for i, a in enumerate(nomes):
        for b in nomes[i + 1:]:
            oa = origem_normalizada(por_base[a]["item"].get("origem", ""))
            ob = origem_normalizada(por_base[b]["item"].get("origem", ""))
            d = int((hashes[a] != hashes[b]).sum())
            why = None
            if oa and oa == ob:
                why = f"a mesma origem {oa}"
            elif d < LIMIAR_PHASH:
                why = f"pHash a {d} bits de distância (limiar {LIMIAR_PHASH})"
            if why:
                pai[raiz(a)] = raiz(b)
                motivo[(a, b)] = why
    grupos = {}
    for b in nomes:
        grupos.setdefault(raiz(b), []).append(b)
    for membros in grupos.values():
        secoes = set()
        for b in membros:
            secoes |= secoes_de.get(b, set())
        if len(secoes) < 2:
            continue
        razoes = sorted({v for (x, y), v in motivo.items() if x in membros and y in membros})
        quem = ", ".join(f"{b} (em {', '.join(sorted(secoes_de.get(b, set())))})" for b in membros)
        problemas.append(f"foto repetida entre seções {', '.join(sorted(secoes))}: {quem}"
                         + (f"; {'; '.join(razoes)}" if razoes else "; o mesmo arquivo")
                         + ": cada seção usa uma foto e uma cena que as outras não usaram")


def medir_dobra(url):
    """Mede, no navegador, aviso e áreas de foto e desenho na primeira tela (1440 e 390)."""
    r = subprocess.run(["node", str(AQUI / "medir-dobra.mjs"), "--url", url], capture_output=True, text=True, timeout=180, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[-400:])
    return json.loads(r.stdout)


def checar_dobra(medida, precisa_aviso, problemas):
    for tela, m in medida.items():
        rotulo = "desktop 1440" if tela == "desk" else "celular 390"
        if precisa_aviso and not m["aviso"]:
            if m.get("avisoNaPagina") is False:
                problemas.append(f"{rotulo}: não achei o texto 'imagem ilustrativa' (nem 'imagens ilustrativas') visível na página neste tamanho de tela "
                                 "(foto de banco com pessoa identificável só passa como ponte com o aviso visível sem rolar)")
            else:
                problemas.append(f"{rotulo}: 'imagem ilustrativa' fora da primeira tela (foto de banco com pessoa identificável só passa "
                                 "como ponte com o aviso visível sem rolar)")
        total = m["foto"] + m["desenho"]
        if total > 0 and m["foto"] / total < FOTO_NA_DOBRA_MINIMA:
            problemas.append(f"{rotulo}: foto é {100 * m['foto'] / total:.0f}% da imagem da primeira tela (mínimo {100 * FOTO_NA_DOBRA_MINIMA:.0f}%): "
                             "foto real, do cliente ou de banco livre como ponte, antes de ilustração chapada; ilustração só como acento")


# ---- A28: foto de banco com NOME de pessoa em alt, legenda ou depoimento --------------------------------------
# Em projeto de cliente real, "Marina Coutinho" no depoimento ao lado de um retrato de banco afirma que aquela pessoa é a
# Marina: afirmação falsa. Exceção única e explícita: o briefing declara `Negócio fictício de teste: sim`.
NOME_PROPRIO = re.compile(r"\b[A-ZÀ-Ý][a-zà-ÿ]{2,}(?:\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ý][a-zà-ÿ]{2,})+\b")
BLOCO_DEPOIMENTO = re.compile(r"depoimento|testemunho|testimonial|review|avalia[cç]|cliente-diz|citacao", re.I)
CAMPO_TESTE = re.compile(r"(?im)^\s*[-*]?\s*neg[oó]cio\s+fict[ií]cio\s+de\s+teste\s*:\s*(sim|true|verdadeiro)\b")
VAZIOS_HTML = {"img", "br", "meta", "link", "input", "source", "hr", "wbr", "area", "base", "col", "embed", "track"}


class _No:
    def __init__(self, tag, attrs, pai):
        self.tag, self.attrs, self.pai, self.filhos, self.pedacos = tag, dict(attrs), pai, [], []

    def texto(self):
        return re.sub(r"\s+", " ", " ".join(self.pedacos + [f.texto() for f in self.filhos])).strip()


def _arvore(html_txt):
    raiz = _No("raiz", [], None)

    class P(HTMLParser):
        atual = raiz

        def handle_starttag(self, tag, attrs):
            n = _No(tag, attrs, self.atual)
            self.atual.filhos.append(n)
            if tag not in VAZIOS_HTML:
                self.atual = n

        def handle_endtag(self, tag):
            n = self.atual
            while n is not raiz and n.tag != tag:
                n = n.pai
            if n is not raiz:
                self.atual = n.pai

        def handle_data(self, data):
            if self.atual.tag not in ("script", "style"):
                self.atual.pedacos.append(data)

    P(convert_charrefs=True).feed(html_txt)
    return raiz


def _todos(no):
    yield no
    for f in no.filhos:
        yield from _todos(f)


def banco_com_nome(pagina, usados, briefing_txt):
    """Devolve (problemas, avisos): foto que não é do cliente nem própria com nome de pessoa atribuído."""
    if not pagina:
        return [], []
    arvore = _arvore(pagina)
    nos = list(_todos(arvore))
    titulo = " ".join(n.texto() for n in nos if n.tag == "title").lower()
    achados = []
    for img in (n for n in nos if n.tag == "img"):
        src = img.attrs.get("src") or ""
        for rel, it in usados:
            if Path(rel).name not in src and base(Path(rel).name) not in Path(src).name:
                continue
            if do_cliente(it) or propria(it):
                continue
            contextos = [("o alt", img.attrs.get("alt") or "")]
            n = img.pai
            fig = None
            while n is not None and n.tag != "raiz":
                if n.tag == "figure":
                    fig = n
                    break
                n = n.pai
            if fig is not None:
                for f in _todos(fig):
                    if f.tag == "figcaption":
                        contextos.append(("a legenda", f.texto()))
            n = img.pai
            while n is not None and n.tag != "raiz":
                if n.tag in ("blockquote", "article") or BLOCO_DEPOIMENTO.search(" ".join([n.attrs.get("class") or "", n.attrs.get("id") or ""])):
                    contextos.append(("o bloco de depoimento", n.texto()))
                    break
                n = n.pai
            for onde, txt in contextos:
                for m in NOME_PROPRIO.finditer(txt):
                    nome_prop = m.group(0)
                    if nome_prop.lower() in titulo or any(w.lower() in titulo for w in nome_prop.split() if len(w) > 4):
                        continue  # o nome do próprio negócio, no título da página
                    achados.append((rel, onde, nome_prop))
                    break
    if not achados:
        return [], []
    if CAMPO_TESTE.search(briefing_txt or ""):
        nomes = "; ".join(sorted({f"{r} com \"{n}\"" for r, _o, n in achados}))
        return [], [f"foto de banco com nome de pessoa ({nomes}): permitido porque o briefing declara teste fictício ('Negócio fictício de teste: sim')"]
    problemas = []
    for rel, onde, nome_prop in dict.fromkeys(achados):
        problemas.append(f"{rel}: foto de banco com nome de pessoa atribuído em {onde} (\"{nome_prop}\"): em projeto de cliente real é afirmação falsa "
                         "(a pessoa da foto não é essa); use retrato ilustrativo sem nome, ou a foto do cliente com autorização. "
                         "Só passa se o evidencias/briefing.md declarar, num campo próprio, 'Negócio fictício de teste: sim'")
    return problemas, []


def avaliar(projeto, dist=None, trafego_real=False, url=None):
    """Devolve (problemas, avisos). Problema reprova (exit 1); aviso não reprova."""
    projeto = Path(projeto)
    dist = Path(dist) if dist else projeto / "dist"
    problemas, avisos = [], []
    lic = projeto / "imagens" / "LICENCAS.md"
    if not lic.is_file():
        return [f"falta {lic}: toda imagem publicada precisa de origem, autor, licença e link"], avisos
    mapa, itens = ler_tabela(lic.read_text(encoding="utf-8-sig"))
    faltam = [c for c in COLUNAS if c not in mapa]
    if faltam:
        return [f"LICENCAS.md sem as colunas {', '.join(faltam)} (cabeçalho: Arquivo publicado | Origem | Autor | Título | Licença | Link da licença | Alteração | Pessoa identificável | Autorização de imagem | Aviso de ilustrativa)"], avisos
    index = dist / "index.html"
    pagina = index.read_text(encoding="utf-8-sig") if index.is_file() else ""
    texto = texto_visivel(pagina)
    texto_n = norm(texto)
    hrefs = set(re.findall(r'href="([^"]+)"', pagina))

    publicadas = sorted(p for p in dist.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSOES
                        and "fonts" not in p.relative_to(dist).parts and not FORA.match(p.name))
    usados = []
    for p in publicadas:
        rel = p.relative_to(dist).as_posix()
        achou = [it for it in itens if base(p.name) in it["arquivo"] or p.name in it["arquivo"]]
        if not achou:
            problemas.append(f"{rel}: imagem publicada sem linha em imagens/LICENCAS.md")
            continue
        usados.append((rel, achou[0]))

    vistos = set()
    pessoas_sem_autorizacao = []
    algum_terceiro = False
    for rel, it in usados:
        chave = id(it)
        og = Path(rel).stem.startswith("og-image")
        cliente = do_cliente(it)
        algum_terceiro |= not cliente and not propria(it)
        if og and not cliente and not propria(it) and not sim(it["aviso"]):
            problemas.append(f"{rel}: prévia do link sem aviso de \"imagem ilustrativa\" (a foto não é do cliente e é a primeira coisa que a visitante vê no WhatsApp)")
        if chave in vistos:
            continue
        vistos.add(chave)
        nome = it["arquivo"]
        licenca, link = it["licenca"], it["link"].strip()
        if not licenca:
            problemas.append(f"{nome}: sem licença")
        if not cliente and not propria(it) and not re.match(r"https?://", link):
            problemas.append(f"{nome}: sem link da licença (http...)")
        if eh_cc(licenca):
            versao = re.search(r"\d\.\d", licenca)
            if not versao:
                problemas.append(f"{nome}: Creative Commons sem versão da licença (3.0, 4.0): \"{licenca}\"")
            if link and "creativecommons.org" not in link:
                problemas.append(f"{nome}: link da licença CC fora de creativecommons.org: {link}")
            if not it["autor"].strip() or not it["titulo"].strip():
                problemas.append(f"{nome}: crédito CC exige autor e título")
            # Crédito no HTML publicado: autor, título, licença com versão e link para a licença.
            curta = re.sub(r"\s+", " ", re.sub(r"(?i)creative commons|licen[cç]a", "CC", licenca)).strip()
            m = re.search(r"(?i)\bCC\s*(BY(?:-[A-Z]{2})*|0)\s*(\d\.\d)", curta)
            exigida = f"CC {m.group(1).upper()} {m.group(2)}" if m else licenca
            for oque, valor in (("autor", it["autor"]), ("título", it["titulo"])):
                if valor.strip() and norm(valor) not in texto_n:
                    problemas.append(f"{nome}: crédito na página sem o {oque} (\"{valor}\")")
            if m and not re.search(re.escape(m.group(1)) + r"\s*" + re.escape(m.group(2)), texto, re.I):
                problemas.append(f"{nome}: crédito na página sem a licença com versão (\"{exigida}\")")
            if link and link not in hrefs:
                problemas.append(f"{nome}: a página não tem link para a licença ({link})")
            alterada = norm(it["alteracao"]) not in ("", "nenhuma", "nao", "-")
            if alterada and re.search(r"BY-?\s?SA", licenca, re.I) and norm("mesma licença") not in texto_n:
                problemas.append(f"{nome}: versão alterada de CC BY-SA sem \"mesma licença\" escrito no crédito da página")
        slug = titulo_da_url(it.get("origem", ""))
        titulo = it.get("titulo", "").strip()
        if titulo and len(slug.split()) >= 3 and plano(titulo) not in plano(slug):
            problemas.append(f"{nome}: Título \"{titulo}\" não é o da fonte (o endereço diz \"{slug}\"): use o título real ou crédito sem título entre aspas")
        # N7: com a página ligando o crédito à foto pelo link da origem, vale o título desta foto; sem esse link,
        # o crédito pode ser de qualquer foto do mesmo autor (aceita o título de uma delas, reprova o que não é de nenhuma).
        unidade = unidade_do_credito(pagina, it.get("origem", ""))
        if unidade is not None:
            titulos_aceitos, onde_citar = {plano(titulo)}, unidade
        else:
            titulos_aceitos = {plano(o["titulo"]) for o in itens if norm(o.get("autor", "")) == norm(it.get("autor", ""))} | {plano(titulo)}
            onde_citar = texto
        for citado in citacoes_do_credito(onde_citar, it.get("autor", "")):
            if plano(citado) not in titulos_aceitos:
                problemas.append(f"{nome}: o crédito da página cita \"{citado}\" entre aspas como título, e o título da fonte é \"{titulo or slug}\"")
        if sim(it["pessoa"]) and not sim(it["autorizacao"]):
            pessoas_sem_autorizacao.append(nome)
            if trafego_real:
                problemas.append(f"{nome}: pessoa identificável sem autorização de imagem: prefira foto sem pessoa identificável ou ilustração própria; a licença do autor não cobre a imagem de quem aparece")
            else:
                avisos.append(f"{nome}: pessoa identificável sem autorização das retratadas: bloqueia tráfego real (a licença do banco não cobre quem aparece). "
                              "Serve à página de teste com \"imagem ilustrativa\" na primeira tela; antes de anunciar, entra a foto da cliente com autorização (--trafego-real reprova)")
    briefing = projeto / "evidencias" / "briefing.md"
    pb, ab = banco_com_nome(pagina, usados, briefing.read_text(encoding="utf-8-sig") if briefing.is_file() else "")
    problemas += pb
    avisos += ab
    if algum_terceiro and "ilustrativa" not in texto_n:
        problemas.append("página: imagem que não é do cliente sem \"imagem ilustrativa\" no texto publicado")

    regioes = regioes_da_pagina(pagina)
    medida = None
    if url:
        try:
            medida = medir_dobra(url)
        except Exception as e:  # navegador ausente ou página fora do ar: sem medida não há aprovação
            problemas.append(f"não consegui medir a primeira tela em {url}: {e}")
    if pessoas_sem_autorizacao and not trafego_real:
        if medida:
            checar_dobra({t: {**m, "foto": 0, "desenho": 0} for t, m in medida.items()}, True, problemas)
        elif not aviso_na_primeira_regiao(regioes):
            problemas.append("foto com pessoa identificável sem autorização, e \"imagem ilustrativa\" fora da primeira tela "
                             "(não está no cabeçalho nem na primeira seção; rode com --url para medir no navegador)")
    if medida:
        checar_dobra({t: {**m, "aviso": True} for t, m in medida.items()}, False, problemas)
    if usados:
        checar_fotos(dist, usados, regioes, problemas, avisos)
    return problemas, avisos


def checar(projeto, dist=None):
    return avaliar(projeto, dist)[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--dist")
    ap.add_argument("--url", help="página servida da dist/: mede no navegador o aviso e a foto na primeira tela")
    ap.add_argument("--trafego-real", action="store_true",
                    help="página que vai receber anúncio: pessoa identificável sem autorização reprova")
    a = ap.parse_args()
    problemas, avisos = avaliar(a.projeto, a.dist, a.trafego_real, a.url)
    print("\nGATE DE IMAGENS  " + str(Path(a.projeto).resolve()))
    print("=" * 80)
    for av in avisos:
        print("  AVISO: " + av)
    if problemas:
        for p in problemas:
            print("  FALHA: " + p)
        print(f"\n  REPROVA: {len(problemas)} problema(s) de licença, imagem ou aviso.\n")
        return 1
    print("  PASSA: toda imagem publicada com licença completa, crédito completo na página, aviso de imagem")
    print("  ilustrativa (inclusive na prévia do link), nenhuma foto repetida entre seções e nenhuma borrada."
          + (f" {len(avisos)} aviso(s) acima." if avisos else "") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
