#!/usr/bin/env python3
"""Gate de SEO: reprova a página que o buscador, o buscador de IA ou o link compartilhado leem mal, sem executar JavaScript.

Por que existe (27/10/2026): auditoria de SEO em duas páginas reais da IAutomate, com as skills
seo-audit (Corey Haines) e seo (Addy Osmani) mais Lighthouse.
  - sales.juliocouto.com.br: Lighthouse SEO 83. O robots.txt, o sitemap.xml e qualquer URL
    inexistente devolviam a home com 200 (soft 404). Sem meta description, sem canonical, zero
    JSON-LD. O logo PNG em base64 repetido 3 vezes pesava 281 KB de um HTML de 364 KB. A foto PNG
    tinha 1,4 MB. O vídeo de 3,6 MB era o LCP no celular (3,8 s). Havia h4 logo depois de h2.
    Depois da correção: SEO 100 e 231 KB no celular.
  - SobrAI (juliocouto.com.br/sobrai/): SEO 66 por `noindex, nofollow` esquecido. SPA (Vite/React)
    com o HTML cru de 1,8 KB e 0 palavras (`<div id="root">` vazio): buscador de IA não roda
    JavaScript. Depois do pré-render: 1.710 palavras no HTML cru e SEO 100.
  - Decisão de produto: página de venda precisa ranquear mesmo vivendo de anúncio e indicação.

Dois modos, pela URL final:
  - PRÉVIA (sem URL final): o que só existe no domínio vira `PENDÊNCIA:` impressa e não reprova.
    `noindex` é permitido, que é como a página de teste nasce (criar.md, passo e).
  - DOMÍNIO (com URL final): tudo reprova.
A URL final vem de `--url-final` ou da linha `Domínio final: https://...` (ou `URL final:`) na
seção f do PLANO.md. `a definir` e o modelo sem trocar (`<...>`) contam como sem URL final.

Regras (limiar entre parênteses). Cada página `*.html` da pasta, menos o 404.html, passa por 1 a 12
e 16; as de 13 a 15 olham a raiz do domínio.
   1. HTML cru (sem script, style, noscript e template): no mínimo 300 palavras visíveis.
   2. `<html lang>` presente.
   3. `<title>` presente, de 15 a 65 caracteres.
   4. meta description presente, de 70 a 160 caracteres.
   5. meta robots sem `noindex` nem `nofollow` (na PRÉVIA o `noindex` é pendência).
   6. [domínio] canonical absoluto `https://` e igual à URL final (a barra final não conta; página
      que não é a index tem o canonical dela, no mesmo domínio); `og:url`, se existir, igual ao canonical.
   7. [domínio] `og:image` absoluta `https://`. Na PRÉVIA basta existir (relativa é pendência).
   8. Exatamente um `<h1>` com texto; os títulos não pulam nível descendo (h2 para h4 reprova).
   9. JSON-LD válido com `@type` (vale `@graph`). Todo `Question.name` de FAQPage e todo
      `Offer.price` precisam estar no texto visível (preço em forma brasileira: 9997 casa com 9.997).
  10. Todo `<img>` com `alt` (vazio vale) e com `width` e `height`. Data URI acima de 20 KB reprova;
      o mesmo data URI repetido 2 vezes ou mais reprova (a partir de 1 KB: abaixo disso não pesa).
  11. `index.html` de até 300 KB. Imagem local de até 500 KB; PNG e JPG acima de 200 KB avisam.
      Vídeo local acima de 1 MB com `autoplay` e sem `preload="none"` reprova.
  12. Google Fonts por `<link rel="stylesheet">` sem `media="print"` com `onload` nem preload: aviso.
  13. [raiz] robots.txt existe, não é HTML, no domínio não bloqueia tudo para `User-agent: *` e traz
      uma linha `Sitemap:` absoluta.
  14. [raiz] sitemap.xml existe, é XML com `<urlset>` e, no domínio, tem a URL final num `<loc>`.
  15. [raiz] 404.html existe e tem `noindex` (no Cloudflare Pages é a existência dele que faz a URL
      inexistente dar 404 em vez de devolver a home com 200).
  16. Página com `<form>` ou campo de formulário tem link de privacidade (href ou texto com
      "privacidade" ou "privacy"). Quiz feito só de botões não precisa.
Na PRÉVIA o sitemap.xml e o 404.html que faltam são pendência (o criar.md manda a página de teste
sem sitemap); o robots.txt faltando reprova nos dois modos.

Uso: node scripts/py.mjs gate-seo.py --dist <dir> [--raiz <dir>] [--url-final <https://...>] [--plano <PLANO.md>]
  --raiz: pasta que vai na RAIZ do domínio, onde ficam robots.txt, sitemap.xml e 404.html (padrão: --dist).
          Página em subcaminho (/sobrai/) tem robots e sitemap no site principal.
Saída: 0 passa, 1 reprova, 2 erro de uso. Linhas `REPROVA:`, `PENDÊNCIA:` e `AVISO:`, e uma linha final `SEO: ...`.
Só biblioteca padrão do Python, sem navegador.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

KB = 1024
MIN_PALAVRAS = 300
TITULO = (15, 65)
DESCRICAO = (70, 160)
LIMITE_DATA_URI = 20 * KB
PISO_DA_REPETICAO = 1 * KB
LIMITE_HTML = 300 * KB
LIMITE_IMAGEM = 500 * KB
AVISO_IMAGEM = 200 * KB
LIMITE_VIDEO = 1024 * KB

EXT_IMAGEM = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg"}
EXT_PESADA = {".png", ".jpg", ".jpeg"}
EXT_VIDEO = {".mp4", ".webm", ".mov", ".m4v", ".ogv"}
CAMPOS_QUE_NAO_COLETAM = {"hidden", "submit", "button", "reset", "image"}
DATA_URI = re.compile(r"(?<![\w-])data:[\w.+/-]+(?:;[\w.=+-]+)*,[^\s\"'()<>]+")
RAIZ_VAZIA = re.compile(r"""<div\b[^>]*\bid\s*=\s*["']?(?:root|app)["']?[^>]*>\s*</div>""", re.I)


# ------------------------------------------------------------------------ pequenas ferramentas
def kb(n):
    return f"{n / KB:.1f}".replace(".", ",") + " KB"


def mb(n):
    return f"{n / (KB * KB):.1f}".replace(".", ",") + " MB"


def sem_barra(url):
    return str(url or "").strip().rstrip("/")


def sem_acento(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def compacto(t):
    """Texto para comparar: sem espaço nenhum (o nbsp e a quebra de linha inclusos) e sem diferença de caixa."""
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", str(t or ""))).casefold()


def espaco_simples(t):
    return " ".join(str(t or "").split())


def ler(caminho):
    return Path(caminho).read_text(encoding="utf-8-sig", errors="replace")


def contar_palavras(texto):
    return sum(1 for t in texto.split() if re.search(r"\w", t))


# ------------------------------------------------------------------------ leitura do HTML cru
class Pagina(HTMLParser):
    """Lê a página como um robô que não executa JavaScript: o que está no HTML é o que existe."""
    IGNORA = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.titulo = None
        self.metas, self.links, self.imgs, self.videos, self.fontes = [], [], [], [], []
        self.titulos = []         # (nível, texto)
        self.jsonld = []          # texto cru de cada <script type="application/ld+json">
        self.ancoras = []         # (href, texto)
        self.tem_form = False
        self.tem_campo = False
        self.partes = []          # texto visível
        self._ign = 0
        self._head = 0
        self._svg = 0
        self._em_titulo = False
        self._titulo_buf = []
        self._h = None
        self._a = None
        self._ld = None
        self._em_video = 0

    def _texto_visivel(self):
        return self._ign == 0 and self._head == 0 and not self._em_titulo

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = (a.get("lang") or "").strip() or self.lang
        elif tag == "head":
            self._head += 1
        elif tag == "body":
            self._head = 0
        elif tag == "svg":
            self._svg += 1
        if tag == "script" and (a.get("type") or "").strip().lower() == "application/ld+json":
            self._ld = []
        if tag in self.IGNORA:
            self._ign += 1
            return
        if self._svg and tag in ("title", "desc"):
            self._ign += 1
            return
        if self._ign:
            return
        if tag == "title":
            self._em_titulo = True
            self._titulo_buf = []
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "video":
            self.videos.append({"attrs": a, "fontes": []})
            self._em_video += 1
        elif tag == "source":
            self.fontes.append(a)
            if self._em_video:      # <source> só pertence a um vídeo enquanto o <video> está aberto
                self.videos[-1]["fontes"].append(a)
        elif re.fullmatch(r"h[1-6]", tag):
            self._h = (int(tag[1]), [])
        elif tag == "a":
            self._a = (a.get("href") or "", [])
        elif tag == "form":
            self.tem_form = True
        elif tag == "textarea" or tag == "select":
            self.tem_campo = True
        elif tag == "input" and (a.get("type") or "text").strip().lower() not in CAMPOS_QUE_NAO_COLETAM:
            self.tem_campo = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in ("meta", "link", "img", "input", "source", "br", "hr"):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "head":
            self._head = max(0, self._head - 1)
        elif tag == "svg":
            self._svg = max(0, self._svg - 1)
        elif tag == "video":
            self._em_video = max(0, self._em_video - 1)
        if tag == "script" and self._ld is not None:
            self.jsonld.append("".join(self._ld))
            self._ld = None
        if tag in self.IGNORA or (self._svg and tag in ("title", "desc")):
            self._ign = max(0, self._ign - 1)
            return
        if self._ign:
            return
        if tag == "title" and self._em_titulo:
            self._em_titulo = False
            if self.titulo is None:
                self.titulo = espaco_simples("".join(self._titulo_buf))
        elif re.fullmatch(r"h[1-6]", tag) and self._h:
            self.titulos.append((self._h[0], espaco_simples("".join(self._h[1]))))
            self._h = None
        elif tag == "a" and self._a:
            self.ancoras.append((self._a[0], espaco_simples("".join(self._a[1]))))
            self._a = None

    def handle_data(self, data):
        if self._ld is not None:
            self._ld.append(data)
            return
        if self._em_titulo:
            self._titulo_buf.append(data)
            return
        if self._ign:
            return
        if self._h:
            self._h[1].append(data)
        if self._a:
            self._a[1].append(data)
        if self._texto_visivel():
            self.partes.append(data)

    @property
    def texto(self):
        return " ".join(self.partes)

    def meta(self, chave):
        """Conteúdo do primeiro <meta name|property=chave>, ou None."""
        for m in self.metas:
            if (m.get("name") or m.get("property") or "").strip().lower() == chave:
                return (m.get("content") or "").strip()
        return None

    def canonical(self):
        for l in self.links:
            if "canonical" in (l.get("rel") or "").lower().split():
                return (l.get("href") or "").strip()
        return None


def ler_pagina(caminho):
    p = Pagina()
    p.feed(ler(caminho))
    p.close()
    return p


# ------------------------------------------------------------------------ resultado
class Resultado:
    def __init__(self):
        self.reprovas, self.pendencias, self.avisos, self.info = [], [], [], []

    def reprova(self, msg, arquivo):
        self.reprovas.append(f"{msg} [arquivo: {arquivo}]")

    def pendencia(self, rotulo, msg, arquivo):
        self.pendencias.append((rotulo, f"{msg} [arquivo: {arquivo}]"))

    def aviso(self, msg, arquivo):
        self.avisos.append(f"{msg} [arquivo: {arquivo}]")


# ------------------------------------------------------------------------ URL final
def url_do_plano(plano):
    """A linha `Domínio final: https://...` da seção f do PLANO.md. None = sem URL final (modo prévia)."""
    plano = Path(plano)
    if not plano.is_file():
        return None
    texto = ler(plano)
    m = re.search(r"(?ms)^##\s*f\..*?(?=^##\s*[a-z]\.|\Z)", texto)
    trecho = m.group(0) if m else texto
    achado = re.search(r"(?im)^[\s>*_-]*(?:dom[ií]nio final|url final)[\s*_]*:[\s*_]*(.*)$", trecho)
    if not achado:
        return None
    valor = achado.group(1).strip().strip("*_` ")
    if not valor or valor.startswith("<"):
        return None       # modelo do plano.md sem trocar
    primeiro = valor.split()[0].strip("`*<>")
    if primeiro.lower().startswith("http://"):
        raise ValueError(f"o Domínio final do PLANO.md precisa começar com https:// (veio {primeiro})")
    if primeiro.lower().startswith("https://"):
        return primeiro
    return None


# ------------------------------------------------------------------------ regras de página
def achar_local(ref, pasta_da_pagina, dist, raiz):
    ref = (ref or "").strip()
    if not ref or ref.startswith(("#", "data:", "mailto:", "tel:", "javascript:", "//")) or re.match(r"^[a-z][a-z0-9+.-]*:", ref, re.I):
        return None
    ref = unquote(ref.split("#")[0].split("?")[0])
    if not ref:
        return None
    candidatos = [dist / ref.lstrip("/"), raiz / ref.lstrip("/")] if ref.startswith("/") else [pasta_da_pagina / ref]
    for c in candidatos:
        if c.is_file():
            return c
    return None


def referencias_de_imagem(p):
    refs = []
    for img in p.imgs:
        refs += [img.get("src"), img.get("data-src")]
        for chave in ("srcset", "data-srcset"):
            refs += [parte.strip().split()[0] for parte in (img.get(chave) or "").split(",") if parte.strip()]
    for s in p.fontes:
        for parte in (s.get("srcset") or "").split(","):
            if parte.strip():
                refs.append(parte.strip().split()[0])
    for v in p.videos:
        refs.append(v["attrs"].get("poster"))
    for chave in ("og:image", "twitter:image"):
        refs.append(p.meta(chave))
    return [r for r in refs if r]


def formas_do_preco(valor):
    """Padrões (regex) de como um preço aparece num texto brasileiro."""
    q = valor.quantize(Decimal("0.01"))
    inteiro = int(q)
    centavos = int((q - inteiro) * 100)
    milhar = f"{inteiro:,}".replace(",", ".")
    antes = r"(?<![\d.,])"
    if centavos == 0:
        formas = "|".join(sorted({re.escape(milhar), str(inteiro)}, key=len, reverse=True))
        return re.compile(antes + "(?:" + formas + r")(?:[.,]00)?(?![\d]|[.,]\d)"), sorted({milhar, str(inteiro)})
    formas_txt = sorted({f"{milhar},{centavos:02d}", f"{inteiro},{centavos:02d}", f"{inteiro}.{centavos:02d}"})
    return re.compile(antes + "(?:" + "|".join(re.escape(f) for f in formas_txt) + r")(?!\d)"), formas_txt


def nos(no):
    if isinstance(no, dict):
        yield no
        for v in no.values():
            yield from nos(v)
    elif isinstance(no, list):
        for v in no:
            yield from nos(v)


def tipos_do_no(no):
    t = no.get("@type")
    t = t if isinstance(t, list) else [t]
    return [str(x).rsplit("/", 1)[-1] for x in t if x]


def checar_jsonld(p, nome, res):
    if not p.jsonld:
        res.reprova("JSON-LD ausente: sem dado estruturado o buscador não entende o que a página vende (sales 27/10/2026: zero JSON-LD)", nome)
        return
    validos, algum_tipo = [], False
    for bruto in p.jsonld:
        try:
            dados = json.loads(bruto.strip())
        except json.JSONDecodeError as e:
            res.reprova(f"JSON-LD inválido ({e.msg}, linha {e.lineno} coluna {e.colno})", nome)
            continue
        validos.append(dados)
        algum_tipo = algum_tipo or any(tipos_do_no(n) for n in nos(dados))
    if validos and not algum_tipo:
        res.reprova("JSON-LD sem @type em nenhum objeto (aceita @graph)", nome)
    texto_compacto = compacto(p.texto)
    texto = unicodedata.normalize("NFC", p.texto).replace("\xa0", " ")
    for dados in validos:
        for no in nos(dados):
            tipos = tipos_do_no(no)
            if "Question" in tipos and isinstance(no.get("name"), str) and no["name"].strip():
                if compacto(no["name"]) not in texto_compacto:
                    res.reprova(f'FAQPage com a pergunta "{espaco_simples(no["name"])}" que não aparece no texto visível (o JSON-LD só pode repetir o que a página mostra)', nome)
            if "Offer" in tipos and "price" in no:
                bruto = str(no["price"]).strip()
                try:
                    valor = Decimal(bruto)
                    if not valor.is_finite():
                        raise InvalidOperation
                except InvalidOperation:
                    res.reprova(f'Offer.price "{bruto}" não é um número', nome)
                    continue
                padrao, formas = formas_do_preco(valor)
                if not padrao.search(texto):
                    res.reprova(f'Offer.price "{bruto}" não aparece no texto visível (formas aceitas: {", ".join(formas)})', nome)


def checar_titulos(p, nome, res):
    com_texto = [t for n, t in p.titulos if n == 1 and t]
    if not com_texto:
        res.reprova("nenhum <h1> com texto: a página precisa de exatamente um", nome)
    elif len(com_texto) > 1:
        res.reprova(f"mais de um <h1> ({len(com_texto)} encontrados): a página precisa de exatamente um", nome)
    niveis = [n for n, _ in p.titulos]
    for i in range(1, len(niveis)):
        if niveis[i] > niveis[i - 1] + 1:
            recorte = niveis if len(niveis) <= 24 else niveis[max(0, i - 6):i + 4]
            seq = ("… " if len(niveis) > 24 and i > 6 else "") + " ".join(f"h{n}" for n in recorte) + (" …" if len(niveis) > 24 else "")
            res.reprova(f'salto de nível h{niveis[i - 1]}→h{niveis[i]} em "{p.titulos[i][1][:60]}" (sequência {seq}): títulos descem um nível por vez', nome)


def checar_imagens(p, nome, html_cru, pasta, dist, raiz, res):
    for img in p.imgs:
        alvo = (img.get("src") or img.get("data-src") or "(sem src)")
        alvo = alvo if not alvo.startswith("data:") else "data URI"
        if "alt" not in img:
            res.reprova(f"<img> sem alt ({alvo}): imagem decorativa leva alt=\"\"", nome)
        faltam = [c for c in ("width", "height") if not (img.get(c) or "").strip()]
        if faltam:
            res.reprova(f"<img> sem width e height (falta: {', '.join(faltam)}) em {alvo}: sem as medidas a página pula quando a imagem carrega", nome)
    contagem = Counter(DATA_URI.findall(html_cru))
    for uri, vezes in contagem.items():
        cabeca, _, carga = uri.partition(",")
        tam = max(0, len(carga) * 3 // 4 - carga.count("=")) if ";base64" in cabeca else len(unquote(carga))
        if tam > LIMITE_DATA_URI:
            res.reprova(f"data URI de {kb(tam)} (limite de {LIMITE_DATA_URI // KB} KB): vira arquivo e entra com <img src>", nome)
        if vezes >= 2 and tam >= PISO_DA_REPETICAO:
            res.reprova(f"o mesmo data URI repetido {vezes} vezes ({kb(tam)} cada, {kb(tam * vezes)} no total): "
                        f"vira um arquivo só (sales 27/10/2026: logo em base64 3 vezes = 281 KB de um HTML de 364 KB)", nome)


def checar_peso(p, nome, html_bytes, pasta, dist, raiz, res):
    if html_bytes > LIMITE_HTML:
        res.reprova(f"{nome} com {kb(html_bytes)}, limite de {LIMITE_HTML // KB} KB: tire o que é base64 ou CSS repetido do HTML", nome)
    vistos = set()
    for ref in referencias_de_imagem(p):
        arq = achar_local(ref, pasta, dist, raiz)
        if not arq or arq in vistos or arq.suffix.lower() not in EXT_IMAGEM:
            continue
        vistos.add(arq)
        tam = arq.stat().st_size
        converter = ", converta para WebP/AVIF" if arq.suffix.lower() in EXT_PESADA else ""
        if tam > LIMITE_IMAGEM:
            res.reprova(f"{arq.name} com {kb(tam)}, limite de {LIMITE_IMAGEM // KB} KB por imagem{converter}", arq)
        elif arq.suffix.lower() in EXT_PESADA and tam > AVISO_IMAGEM:
            res.aviso(f"{arq.name} com {kb(tam)} em {arq.suffix.lower()[1:].upper()}: converta para WebP/AVIF", arq)
    for v in p.videos:
        a = v["attrs"]
        if "autoplay" not in a or (a.get("preload") or "").strip().lower() == "none":
            continue
        for ref in [a.get("src")] + [s.get("src") for s in v["fontes"]]:
            arq = achar_local(ref, pasta, dist, raiz)
            if arq and arq.suffix.lower() in EXT_VIDEO and arq.stat().st_size > LIMITE_VIDEO:
                res.reprova(f'vídeo {arq.name} de {mb(arq.stat().st_size)} com autoplay e sem preload="none": vira o LCP no celular '
                            f"(vídeo de 3,6 MB como LCP no celular, sales 27/10/2026, 3,8 s)", arq)


def checar_fontes(p, nome, res):
    pre = {(l.get("href") or "").strip() for l in p.links
           if "preload" in (l.get("rel") or "").lower().split() and (l.get("as") or "").lower() == "style"}
    for l in p.links:
        href = (l.get("href") or "").strip()
        if "stylesheet" not in (l.get("rel") or "").lower().split() or "fonts.googleapis.com" not in href:
            continue
        sem_bloqueio = (l.get("media") or "").strip().lower() == "print" and bool(l.get("onload"))
        if not sem_bloqueio and href not in pre:
            res.aviso('Google Fonts carregado por <link rel="stylesheet"> bloqueia a renderização (render-blocking): '
                      'use media="print" com onload ou um preload', nome)
            return


def checar_pagina(caminho, dist, raiz, url_final, res, eh_index):
    nome = Path(caminho)
    pasta = nome.parent
    html_cru = ler(caminho)
    html_bytes = nome.stat().st_size
    p = Pagina()
    p.feed(html_cru)
    p.close()
    previa = url_final is None

    # 1. HTML cru
    palavras = contar_palavras(p.texto)
    res.info.append(f"  {nome.name}: {palavras} palavras no HTML cru")
    if palavras < MIN_PALAVRAS:
        spa = (" SPA com #root vazio: buscador de IA não roda JavaScript, e o HTML cru é o que ele lê; pré-renderize a página "
               "(SobrAI 27/10/2026: 0 palavras antes, 1.710 depois do pré-render)") if RAIZ_VAZIA.search(html_cru) else ""
        res.reprova(f"HTML cru com {palavras} palavras visíveis, mínimo {MIN_PALAVRAS}.{spa}", nome)
    # 2. lang
    if not p.lang:
        res.reprova("<html lang> ausente: diga o idioma da página (pt-BR)", nome)
    # 3. title
    if not p.titulo:
        res.reprova("<title> ausente", nome)
    elif not TITULO[0] <= len(p.titulo) <= TITULO[1]:
        res.reprova(f'<title> com {len(p.titulo)} caracteres, esperado de {TITULO[0]} a {TITULO[1]}: "{p.titulo[:70]}"', nome)
    # 4. description
    desc = p.meta("description")
    if desc is None or not desc:
        res.reprova("meta description ausente (sales 27/10/2026: o Lighthouse SEO caiu para 83 por isso)", nome)
    elif not DESCRICAO[0] <= len(desc) <= DESCRICAO[1]:
        res.reprova(f"meta description com {len(desc)} caracteres, esperado de {DESCRICAO[0]} a {DESCRICAO[1]}", nome)
    # 5. robots
    robots = p.meta("robots")
    if robots:
        fichas = set(re.split(r"[,\s]+", robots.lower()))
        if fichas & {"noindex", "nofollow", "none"}:
            if previa:
                res.pendencia("meta robots", f'meta robots "{robots}" sai no domínio final (página de teste nasce com noindex)', nome)
            else:
                res.reprova(f'meta robots "{robots}" bloqueia a indexação no domínio final (SobrAI 27/10/2026: SEO 66 por noindex, nofollow esquecido)', nome)
    # 6. canonical e og:url
    canon = p.canonical()
    if previa:
        if not canon:
            res.pendencia("canonical", "canonical ausente: entra no domínio final, absoluto e igual à URL final", nome)
        elif not canon.lower().startswith("https://"):
            res.pendencia("canonical", f'canonical "{canon}" não é https:// absoluto: ajuste no domínio final', nome)
    else:
        if not canon:
            res.reprova("canonical ausente (sales 27/10/2026: sem canonical)", nome)
        elif not canon.lower().startswith("https://"):
            res.reprova(f'canonical "{canon}" não é endereço https:// absoluto', nome)
        elif eh_index and sem_barra(canon) != sem_barra(url_final):
            res.reprova(f'canonical "{canon}" diferente da URL final "{url_final}"', nome)
        elif not eh_index and urlparse(canon).netloc.lower() != urlparse(url_final).netloc.lower():
            res.reprova(f'canonical "{canon}" em domínio diferente do da URL final "{url_final}"', nome)
        ogurl = p.meta("og:url")
        if canon and ogurl and sem_barra(ogurl) != sem_barra(canon):
            res.reprova(f'og:url "{ogurl}" diferente do canonical "{canon}"', nome)
    # 7. og:image
    og = p.meta("og:image")
    if not og:
        res.reprova("og:image ausente: o link compartilhado sai sem imagem", nome)
    elif not og.lower().startswith("https://"):
        if previa:
            res.pendencia("og:image", f'og:image "{og}" é relativa: vira endereço https:// absoluto no domínio final', nome)
        else:
            res.reprova(f'og:image "{og}" não é endereço https:// absoluto', nome)
    # 8. títulos
    checar_titulos(p, nome, res)
    # 9. JSON-LD
    checar_jsonld(p, nome, res)
    # 10 e 11. imagens e peso
    checar_imagens(p, nome, html_cru, pasta, dist, raiz, res)
    checar_peso(p, nome, html_bytes, pasta, dist, raiz, res)
    # 12. fontes
    checar_fontes(p, nome, res)
    # 16. privacidade
    if p.tem_form or p.tem_campo:
        if not any(re.search(r"privacidade|privacy", sem_acento(f"{h} {t}")) for h, t in p.ancoras):
            res.reprova('a página coleta dados (<form> ou campo) e não tem link de privacidade: '
                        'ponha um link com "privacidade" ou "privacy" no href ou no texto', nome)
    return palavras


# ------------------------------------------------------------------------ regras da raiz do domínio
def grupos_do_robots(texto):
    grupos, atual, depois_de_ua, sitemaps = [], None, False, []
    for linha in texto.splitlines():
        linha = linha.split("#", 1)[0].strip()
        if ":" not in linha:
            continue
        campo, valor = (s.strip() for s in linha.split(":", 1))
        campo = campo.lower()
        if campo == "user-agent":
            if atual is None or not depois_de_ua:
                atual = {"agentes": [], "regras": []}
                grupos.append(atual)
            atual["agentes"].append(valor.lower())
            depois_de_ua = True
            continue
        depois_de_ua = False
        if campo == "sitemap":
            sitemaps.append(valor)
        elif campo in ("allow", "disallow") and atual is not None:
            atual["regras"].append((campo, valor))
    return grupos, sitemaps


def checar_robots(raiz, url_final, res):
    arq = raiz / "robots.txt"
    if not arq.is_file():
        res.reprova("robots.txt ausente", arq)
        return
    texto = ler(arq)
    if texto.lstrip().startswith("<"):
        res.reprova("robots.txt é HTML (a hospedagem devolveu a home no lugar do arquivo: soft 404, sales 27/10/2026)", arq)
        return
    grupos, sitemaps = grupos_do_robots(texto)
    regras = [r for g in grupos if "*" in g["agentes"] for r in g["regras"]]
    bloqueia = ("disallow", "/") in regras and ("allow", "/") not in regras
    if bloqueia:
        if url_final is None:
            res.pendencia("robots.txt", "robots.txt com Disallow: / para User-agent: * sai no domínio final", arq)
        else:
            res.reprova("robots.txt bloqueia o site inteiro (User-agent: * com Disallow: /) no domínio final", arq)
    if url_final is not None and not any(re.match(r"https?://", s, re.I) for s in sitemaps):
        res.reprova("robots.txt sem linha Sitemap: com endereço absoluto (https://...)", arq)


def checar_sitemap(raiz, url_final, res):
    arq = raiz / "sitemap.xml"
    if not arq.is_file():
        msg = "sitemap.xml ausente: gere com gerar-seo.py quando houver a URL final"
        if url_final is None:
            res.pendencia("sitemap.xml", msg, arq)
        else:
            res.reprova(msg, arq)
        return
    texto = ler(arq)
    comeco = texto.lstrip()[:300].lower()
    if comeco.startswith("<!doctype html") or "<html" in comeco:
        res.reprova("sitemap.xml não é XML válido (é HTML: a hospedagem devolveu a home, soft 404, sales 27/10/2026)", arq)
        return
    if re.search(r"<!doctype|<!entity", texto, re.I):
        res.reprova("sitemap.xml com DOCTYPE ou ENTITY: sitemap não usa, e o gate não abre", arq)
        return
    try:
        raiz_xml = ET.fromstring(arq.read_bytes())
    except ET.ParseError as e:
        res.reprova(f"sitemap.xml não é XML válido ({e})", arq)
        return
    if raiz_xml.tag.rsplit("}", 1)[-1] != "urlset":
        res.reprova(f"sitemap.xml sem <urlset> (a raiz é <{raiz_xml.tag.rsplit('}', 1)[-1]}>)", arq)
        return
    locs = [(e.text or "").strip() for e in raiz_xml.iter() if e.tag.rsplit("}", 1)[-1] == "loc"]
    if url_final is not None and sem_barra(url_final) not in {sem_barra(l) for l in locs}:
        res.reprova(f'sitemap.xml não tem a URL final "{url_final}" em nenhum <loc> ({len(locs)} <loc> encontrados)', arq)


def checar_404(raiz, url_final, res):
    arq = raiz / "404.html"
    if not arq.is_file():
        msg = "404.html ausente: no Cloudflare Pages é ele que faz a URL inexistente dar 404; sem ele devolve a home com 200 (soft 404, sales 27/10/2026)"
        if url_final is None:
            res.pendencia("404.html", msg, arq)
        else:
            res.reprova(msg, arq)
        return
    robots = (ler_pagina(arq).meta("robots") or "").lower()
    if "noindex" not in robots:
        res.reprova('404.html sem noindex: ponha <meta name="robots" content="noindex">', arq)


# ------------------------------------------------------------------------ comando
def checar(dist, raiz=None, url_final=None):
    dist = Path(os.path.abspath(dist))
    raiz = Path(os.path.abspath(raiz)) if raiz else dist
    res = Resultado()
    palavras_da_index = None
    if not (dist / "index.html").is_file():
        res.reprova(f"{dist} não tem index.html", dist)
    paginas = sorted(p for p in dist.glob("*.html") if p.name.lower() != "404.html")
    for pagina in paginas:
        n = checar_pagina(pagina, dist, raiz, url_final, res, pagina.name == "index.html")
        if pagina.name == "index.html":
            palavras_da_index = n
    checar_robots(raiz, url_final, res)
    checar_sitemap(raiz, url_final, res)
    checar_404(raiz, url_final, res)
    return res, palavras_da_index


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dist", required=True)
    ap.add_argument("--raiz")
    ap.add_argument("--url-final")
    ap.add_argument("--plano")
    a = ap.parse_args(argv)
    if not Path(a.dist).is_dir():
        print(f"ERRO: a pasta {a.dist} não existe.")
        return 2
    if a.raiz and not Path(a.raiz).is_dir():
        print(f"ERRO: a pasta da raiz {a.raiz} não existe.")
        return 2
    try:
        url_final = a.url_final or (url_do_plano(a.plano) if a.plano else None)
    except ValueError as e:
        print(f"ERRO: {e}")
        return 2
    if url_final is not None and not url_final.lower().startswith("https://"):
        print(f"ERRO: a URL final precisa começar com https:// (veio {url_final}).")
        return 2
    modo = "prévia" if url_final is None else "domínio"
    res, palavras = checar(a.dist, a.raiz, url_final)
    print(f"\nGATE DE SEO  {a.dist}  (modo {modo}{'' if url_final is None else ', URL final ' + url_final})\n" + "=" * 76)
    for linha in res.info:
        print(linha)
    for r in res.reprovas:
        print("REPROVA: " + r)
    for _, p in res.pendencias:
        print("PENDÊNCIA: " + p)
    for av in res.avisos:
        print("AVISO: " + av)
    rotulos = list(dict.fromkeys(r for r, _ in res.pendencias))
    print(f"SEO: gate-seo {'reprova' if res.reprovas else 'passa'} no modo {modo} | palavras no HTML cru "
          f"{'n/d' if palavras is None else palavras} | pendências: {', '.join(rotulos) if rotulos else 'nenhuma'}")
    return 1 if res.reprovas else 0


if __name__ == "__main__":
    sys.exit(main())
