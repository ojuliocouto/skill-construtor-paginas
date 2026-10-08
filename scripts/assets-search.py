#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assets Search: Videos, Fotos, Lottie, Ilustracoes para paginas web.

Busca assets visuais gratuitos para usar em backgrounds, heroes, secoes.

Uso:
  node scripts/py.mjs assets-search.py "dark abstract"              # videos (padrao)
  node scripts/py.mjs assets-search.py "technology" --type photo    # fotos
  node scripts/py.mjs assets-search.py tech-dark                    # preset video
  node scripts/py.mjs assets-search.py --type lottie "loading"      # lottie (links)
  node scripts/py.mjs assets-search.py --type illustrations         # undraw/storyset
  node scripts/py.mjs assets-search.py --type icons                 # lordicon/animated
  node scripts/py.mjs assets-search.py --type openverse "team"      # FOTOS REAIS SEM CHAVE (licenca CC)
  node scripts/py.mjs assets-search.py "team" --type photo --folha prova/fotos.png   # + UMA imagem com todas as miniaturas numeradas
  node scripts/py.mjs assets-search.py --type sem-chave             # todas as rotas sem chave
  node scripts/py.mjs assets-search.py --presets                    # listar presets

Sem PEXELS_API_KEY o script NAO fica sem imagem: "--type photo" cai
automaticamente na Openverse, que devolve fotos reais com licenca Creative
Commons e sem chave nenhuma. A contrapartida e creditar o autor.
Detalhes e modelo de credito: references/assets-sem-chave.md

Setup opcional (so pra usar o Pexels, que dispensa credito):
  export PEXELS_API_KEY="sua-chave-aqui"
  # Chave gratis em: https://www.pexels.com/api/
"""

import os
import sys
import json
import re
import time
import html as _html
import argparse
import urllib.request
import urllib.parse
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lancador import comando  # noqa: E402


# ─── CONFIG ───────────────────────────────────────────────────────────────────

PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"
PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"

# Openverse: fotos reais com licenca Creative Commons, SEM chave de API.
OPENVERSE_IMAGE_URL = "https://api.openverse.org/v1/images/"
# Placeholder real (JPEG de verdade) pra mockup, tambem sem chave.
PICSUM_URL = "https://picsum.photos"
USER_AGENT = "construtor-paginas-assets-search/1.0"
# Wikimedia Commons: segunda rota de foto com licença, sem chave, quando a Openverse não responde.
COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
COMMONS_USER_AGENT = "construtor-paginas-assets-search/3.5.8 (page-building skill; licensed photo search)"
PAUSA_COMMONS = 1.0          # segundos antes de cada chamada: a Commons limita quem insiste (HTTP 429)
TETO_ESPERA_COMMONS = 30     # nunca dorme mais que isso por causa de Retry-After
# So entra o que uma pagina de cliente pode usar com credito: CC0, CC BY, CC BY-SA e dominio publico.
# NC (nao comercial), ND (sem derivadas), GFDL e "uso livre" de cada pais ficam de fora.
LICENCA_COMMONS_OK = re.compile(r"^(CC0(\s|$)|CC[ -]BY(-SA)?\s*\d|Public domain|PD[ -])", re.I)

# 3.5.8 (N6): a Commons só serve miniatura nestas larguras; outra (480, 1500) volta HTTP 400.
LARGURAS_COMMONS = (500, 960, 1280, 1920)
# 3.5.8 (N5): títulos que a busca por palavra de móvel e ofício traz e não servem a página de cliente:
# prova policial (prefixo EFTA + número), casa de boneca, reboque de cavalo e acervo de museu.
ACERVO_RUIM_COMMONS = re.compile(
    r"^EFTA[\s_-]?\d|\bdoll[ '_-]?s?[ _-]?house\b|\b(?:horse|livestock|cattle)[ _-]trailer\b|\b(?:museum|museu|museo|mus[ée]e)\b", re.I)

# Openverse usa "aspect_ratio", o resto do script usa "orientation".
ASPECTO_POR_ORIENTACAO = {
    "landscape": "wide",
    "portrait": "tall",
    "square": "square",
}

# Rotulos de licenca legiveis. O que nao estiver aqui vira "CC <CODIGO> <versao>".
ROTULOS_DE_LICENCA = {
    "cc0": "CC0 1.0 (dominio publico)",
    "pdm": "Public Domain Mark 1.0 (dominio publico)",
}

# Licencas que dispensam credito. Todas as outras EXIGEM atribuicao.
LICENCAS_SEM_CREDITO_OBRIGATORIO = {"cc0", "pdm"}


PRESET_QUERIES = {
    # Videos escuros / tech
    "tech-dark":       "technology dark abstract",
    "tech-blue":       "technology blue particles abstract",
    "tech-purple":     "abstract purple digital technology",
    "particles":       "particles abstract background dark",
    "matrix":          "digital data flow dark background",
    "waves-dark":      "dark waves abstract motion",
    "mesh-dark":       "dark mesh gradient abstract",
    "neon":            "neon light abstract background",
    "space":           "space stars dark background",
    "circuit":         "circuit board technology abstract",

    # Videos claros / minimal
    "minimal-white":   "minimal white abstract background",
    "waves-light":     "white waves abstract minimal",
    "smoke":           "white smoke abstract minimal",
    "liquid":          "liquid abstract colorful motion",
    "gradient-light":  "gradient abstract colorful background",

    # Videos natureza / atmosfera
    "nature":          "nature landscape serene aerial",
    "forest":          "forest trees nature calm",
    "ocean":           "ocean waves water blue",
    "mountain":        "mountain landscape aerial cinematic",
    "sky":             "sky clouds timelapse aerial",
    "rain":            "rain drops window bokeh",
    "fire":            "fire flames dark abstract",

    # Videos produto / business
    "office":          "modern office workspace business",
    "laptop":          "laptop computer modern workspace",
    "city":            "city aerial night lights",
    "coffee":          "coffee cafe minimal lifestyle",
    "hands-typing":    "hands typing keyboard computer",

    # Fotos hero
    "hero-dark":       "dark abstract background minimal",
    "hero-light":      "light minimal clean background",
    "hero-gradient":   "gradient colorful abstract background",
    "hero-tech":       "technology abstract dark neon",
    "hero-business":   "business professional team modern",
    "hero-product":    "product modern minimal showcase",
}


# ─── PEXELS VIDEO SEARCH ─────────────────────────────────────────────────────

def search_videos(query: str, limit: int = 8, orientation: str = "landscape") -> list:
    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        print_no_api_key()
        return []

    params = urllib.parse.urlencode({
        "query": query,
        "per_page": limit,
        "orientation": orientation,
        "size": "medium",
    })
    url = f"{PEXELS_VIDEO_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={"Authorization": api_key})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("videos", [])
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("ERRO: API key inválida. Verifique sua PEXELS_API_KEY.", file=sys.stderr)
        else:
            print(f"ERRO HTTP {e.code}: {e.reason}", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"ERRO de conexão: {e.reason}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"ERRO inesperado: {e}", file=sys.stderr)
        return []


def format_videos(items: list, query: str) -> str:
    if not items:
        return "Nenhum vídeo encontrado. Tente outra query ou preset."

    lines = []
    lines.append(f"{'='*70}")
    lines.append(f"  {len(items)} vídeos encontrados para: \"{query}\"")
    lines.append(f"{'='*70}\n")

    for i, video in enumerate(items, 1):
        vid_id    = video.get("id", "")
        url       = video.get("url", "")
        duration  = video.get("duration", 0)
        width     = video.get("width", 0)
        height    = video.get("height", 0)
        author    = video.get("user", {}).get("name", "?")

        # Pegar o melhor arquivo de video
        files = video.get("video_files", [])
        best_hd  = next((f for f in files if f.get("quality") == "hd"  and f.get("width", 0) >= 1280), None)
        best_sd  = next((f for f in files if f.get("quality") == "sd"  and f.get("width", 0) >= 640), None)
        best_4k  = next((f for f in files if f.get("quality") == "uhd"), None)
        best     = best_hd or best_sd or best_4k or (files[0] if files else {})

        file_url = best.get("link", "")
        f_width  = best.get("width", 0)
        f_height = best.get("height", 0)
        f_type   = best.get("file_type", "video/mp4")

        # Preview image
        preview = next((p.get("picture") for p in video.get("video_pictures", [])[:1]), "")

        lines.append(f"  {i}. ID: {vid_id} | {width}x{height} | {duration}s | Por: {author}")
        lines.append(f"     Pexels: {url}")
        if file_url:
            lines.append(f"     Download ({f_width}x{f_height}): {file_url}")
        if preview:
            lines.append(f"     Preview img: {preview}")
        lines.append(f"     Licença: Pexels License (uso gratuito, sem atribuição obrigatória)")
        lines.append(f"")
        lines.append(f"     USO RÁPIDO:")
        lines.append(f"     <vídeo autoPlay loop muted playsInline className=\"absolute inset-0 w-full h-full object-cover\">")
        lines.append(f"       <source src=\"{file_url}\" type=\"{f_type}\" />")
        lines.append(f"     </video>")
        lines.append("")

    lines.append(f"{'='*70}")
    lines.append("  Dicas de uso:")
    lines.append("  - Baixe e hospede no seu projeto (public/) para melhor performance")
    lines.append("  - Sempre adicione overlay escuro: <div class=\"absolute inset-0 bg-black/50\" />")
    lines.append("  - Use lazy loading: adicione loading=\"lazy\" ou carregue após LCP")
    lines.append("  - Comprima com HandBrake ou ffmpeg antes de subir (alvo: < 5MB)")
    lines.append(f"{'='*70}")
    return "\n".join(lines)


# ─── PEXELS PHOTO SEARCH ─────────────────────────────────────────────────────

def search_photos(query: str, limit: int = 8, orientation: str = "landscape") -> list:
    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        print_no_api_key()
        return []

    params = urllib.parse.urlencode({
        "query": query,
        "per_page": limit,
        "orientation": orientation,
    })
    url = f"{PEXELS_PHOTO_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={"Authorization": api_key})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("photos", [])
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("ERRO: API key inválida. Verifique PEXELS_API_KEY.", file=sys.stderr)
        else:
            print(f"ERRO HTTP {e.code}: {e.reason}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return []


def format_photos(items: list, query: str) -> str:
    if not items:
        return "Nenhuma foto encontrada."

    lines = []
    lines.append(f"{'='*70}")
    lines.append(f"  {len(items)} fotos encontradas para: \"{query}\"")
    lines.append(f"{'='*70}\n")

    for i, photo in enumerate(items, 1):
        photo_id    = photo.get("id", "")
        url         = photo.get("url", "")
        author      = photo.get("photographer", "?")
        width       = photo.get("width", 0)
        height      = photo.get("height", 0)
        alt         = photo.get("alt", "")
        src         = photo.get("src", {})

        original = src.get("original", "")
        large2x  = src.get("large2x", "")
        large    = src.get("large", "")
        medium   = src.get("medium", "")

        lines.append(f"  {i}. ID: {photo_id} | {width}x{height} | Por: {author}")
        if alt:
            lines.append(f"     Alt: {alt}")
        lines.append(f"     Pexels: {url}")
        lines.append(f"     Large (1280px): {large}")
        lines.append(f"     Large2x (2x): {large2x}")
        lines.append(f"     Original: {original}")
        lines.append(f"     Medium: {medium}")
        lines.append(f"")
        lines.append(f"     USO RÁPIDO:")
        lines.append(f"     <img src=\"{large}\" alt=\"{alt}\" className=\"w-full h-full object-cover\" />")
        lines.append("")

    lines.append(f"{'='*70}")
    lines.append("  Dicas: Baixe e otimize com squoosh.app ou tinypng.com antes de usar")
    lines.append("  Formato recomendado: WebP | Hero < 200KB | Seções < 100KB")
    lines.append(f"{'='*70}")
    return "\n".join(lines)


# ─── OPENVERSE: FOTOS REAIS SEM NENHUMA CHAVE ────────────────────────────────
#
# A Openverse (mantida pela WordPress Foundation) indexa fotos com licenca
# Creative Commons e responde sem API key. E a rota padrao quando o aluno ainda
# nao configurou PEXELS_API_KEY: a pagina sai com FOTO REAL, nao com retangulo
# vazio. O preco e a atribuicao: em licenca CC BY / BY-SA o credito ao autor
# nao e opcional, e parte da licenca.


def _rotulo_de_licenca(codigo: str, versao: str) -> str:
    codigo = (codigo or "").strip().lower()
    versao = str(versao or "").strip()
    if not codigo:
        return "licença desconhecida"
    if codigo in ROTULOS_DE_LICENCA:
        return ROTULOS_DE_LICENCA[codigo]
    partes = ["CC", codigo.upper()]
    if versao:
        partes.append(versao)
    return " ".join(partes)


def _url_da_licenca(bruto: dict) -> str:
    url = (bruto.get("license_url") or "").strip()
    if url:
        return url
    codigo = (bruto.get("license") or "").strip().lower()
    versao = str(bruto.get("license_version") or "").strip()
    if codigo == "cc0":
        return "https://creativecommons.org/publicdomain/zero/1.0/"
    if codigo == "pdm":
        return "https://creativecommons.org/publicdomain/mark/1.0/"
    if codigo and versao:
        return "https://creativecommons.org/licenses/%s/%s/" % (codigo, versao)
    return ""


def _monta_credito(item: dict) -> str:
    """Credito no padrao TASL (titulo, autor, fonte, licenca)."""
    pedacos = ['"%s"' % item["titulo"]]
    if item["autor_url"]:
        pedacos.append("por %s (%s)" % (item["autor"], item["autor_url"]))
    else:
        pedacos.append("por %s" % item["autor"])
    if item["pagina_origem"]:
        pedacos.append("via %s" % item["pagina_origem"])
    if item["licenca_url"]:
        pedacos.append("licença %s (%s)" % (item["licenca"], item["licenca_url"]))
    else:
        pedacos.append("licença %s" % item["licenca"])
    return ", ".join(pedacos)


def _normaliza_item_openverse(bruto: dict) -> dict:
    codigo = (bruto.get("license") or "").strip().lower()
    item = {
        "id": bruto.get("id", ""),
        "titulo": (bruto.get("title") or "Sem título").strip(),
        "url": (bruto.get("url") or "").strip(),
        "thumbnail": (bruto.get("thumbnail") or "").strip(),
        "autor": (bruto.get("creator") or "autor desconhecido").strip(),
        "autor_url": (bruto.get("creator_url") or "").strip(),
        "licenca": _rotulo_de_licenca(codigo, bruto.get("license_version")),
        "licenca_url": _url_da_licenca(bruto),
        "largura": bruto.get("width") or 0,
        "altura": bruto.get("height") or 0,
        "pagina_origem": (bruto.get("foreign_landing_url") or "").strip(),
        "exige_credito": codigo not in LICENCAS_SEM_CREDITO_OBRIGATORIO,
    }
    item["credito"] = _monta_credito(item)
    return item


def _abrir_url(req, timeout=20):
    """Unico ponto de rede deste script para API: os testes trocam esta funcao pela rede simulada."""
    return urllib.request.urlopen(req, timeout=timeout)


def _imagem_esta_viva(url: str, timeout: int = 8) -> bool:
    """Confere se a URL ainda entrega imagem de verdade.

    A Openverse indexa acervos de terceiros (Flickr, StockSnap). Foto apagada
    na origem continua no indice e devolve 410. Link morto na pagina e o mesmo
    defeito que nao ter imagem nenhuma, entao esse resultado e descartado.
    """
    cabecalhos = {"User-Agent": USER_AGENT, "Accept": "image/*"}

    def confere(req):
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            tipo = (resp.headers.get("Content-Type") or "").lower()
            status = getattr(resp, "status", 200) or 200
            return status < 400 and tipo.startswith("image/")

    try:
        return confere(urllib.request.Request(url, headers=cabecalhos, method="HEAD"))
    except urllib.error.HTTPError as e:
        # HEAD barrado no servidor nao quer dizer imagem morta: tenta um GET curto.
        if e.code not in (403, 405, 501):
            return False
    except Exception:
        return False

    try:
        parciais = dict(cabecalhos)
        parciais["Range"] = "bytes=0-0"
        return confere(urllib.request.Request(url, headers=parciais))
    except Exception:
        return False


def _busca_openverse(query: str, limit: int = 6, orientation: str = "landscape",
                     validar: bool = True):
    """Busca fotos com licenca Creative Commons na Openverse. NAO precisa de chave.

    Devolve (itens, falhou, motivo): `falhou` e True quando a Openverse nao respondeu (rede, HTTP,
    resposta fora do formato), e fica False quando ela respondeu, mesmo sem resultado.

    Devolve uma lista de dicts com url da imagem, autor, licenca e link da
    licenca. Em qualquer erro devolve lista vazia e explica o motivo no stderr,
    sem estourar traceback na cara de quem esta construindo a pagina.

    Com validar=True (padrao) cada URL e conferida antes de entrar na lista, pra
    nenhum link morto virar imagem quebrada na pagina.
    """
    try:
        pedido = int(limit)
    except (TypeError, ValueError):
        pedido = 6
    pedido = max(1, min(pedido, 20))
    # Pede folga pra compensar os links mortos que serao descartados.
    quantidade = min(20, pedido * 3) if validar else pedido

    params = {
        "q": query,
        "page_size": quantidade,
        # commercial E modification: pagina de cliente SEMPRE corta, redimensiona e
        # sobrepoe texto, o que cria obra derivada. So "commercial" deixa passar
        # licenca ND (NoDerivatives), que proibe exatamente isso. Verificado: a busca
        # devolvia CC BY-ND, que o aluno usaria sem saber que estava violando.
        "license_type": "commercial,modification",
        "mature": "false",
    }
    aspecto = ASPECTO_POR_ORIENTACAO.get(orientation)
    if aspecto:
        params["aspect_ratio"] = aspecto

    url = OPENVERSE_IMAGE_URL + "?" + urllib.parse.urlencode(params)
    cabecalhos = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    try:
        req = urllib.request.Request(url, headers=cabecalhos)
        with _abrir_url(req, timeout=20) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(
            "ERRO Openverse: HTTP %s (%s). A busca sem chave não respondeu agora, "
            "tente de novo em alguns segundos." % (e.code, e.reason),
            file=sys.stderr,
        )
        return [], True, "HTTP %s" % e.code
    except urllib.error.URLError as e:
        print(
            "ERRO Openverse: sem conexão com api.openverse.org (%s). "
            "Verifique a internet ou o proxy." % (e.reason,),
            file=sys.stderr,
        )
        return [], True, "sem conexão com api.openverse.org (%s)" % (e.reason,)
    except ValueError as e:
        print("ERRO Openverse: resposta não veio em JSON valido (%s)." % e, file=sys.stderr)
        return [], True, "resposta fora do formato"
    except Exception as e:  # rede e API de terceiro: nunca derrubar o script
        print("ERRO Openverse inesperado: %s" % e, file=sys.stderr)
        return [], True, "erro inesperado"

    if not isinstance(dados, dict):
        print("ERRO Openverse: resposta em formato inesperado.", file=sys.stderr)
        return [], True, "resposta fora do formato"

    brutos = dados.get("results") or []
    if not isinstance(brutos, list):
        print("ERRO Openverse: campo 'results' em formato inesperado.", file=sys.stderr)
        return [], True, "resposta fora do formato"

    itens = [
        _normaliza_item_openverse(b)
        for b in brutos
        if isinstance(b, dict) and (b.get("url") or "").strip()
    ]

    if not validar:
        return itens[:pedido], False, ""

    vivos, mortos = [], 0
    for item in itens:
        if len(vivos) >= pedido:
            break
        if _imagem_esta_viva(item["url"]):
            vivos.append(item)
        else:
            mortos += 1

    if mortos:
        print(
            "AVISO Openverse: %d resultado(s) com link morto na origem foram "
            "descartados." % mortos,
            file=sys.stderr,
        )
    return vivos, False, ""


def search_openverse(query: str, limit: int = 6, orientation: str = "landscape",
                     validar: bool = True) -> list:
    """Busca fotos na Openverse; lista vazia em qualquer falha (o motivo vai para o stderr)."""
    return _busca_openverse(query, limit=limit, orientation=orientation, validar=validar)[0]


# ─── WIKIMEDIA COMMONS: SEGUNDA ROTA SEM CHAVE ───────────────────────────────
#
# Quando a Openverse nao responde (rede, proxy, API fora do ar), a Commons tem fotos com licenca
# aberta e uma API que tambem dispensa chave. Mesmo formato de saida e mesmos campos de licenca.

def _sem_html(texto: str) -> str:
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", texto or ""))).strip()


def _url_absoluta(url: str) -> str:
    url = (url or "").strip()
    return "https:" + url if url.startswith("//") else url


def url_commons_na_largura(url: str, largura: int, largura_original: int = 0) -> str:
    """URL da miniatura da Commons na largura padrão (500, 960, 1280 ou 1920) mais próxima que não seja menor que a pedida.
    Devolve "" quando a URL não é de miniatura ou quando a foto original é mais estreita que a largura (a Commons responde 400)."""
    achado = re.search(r"/thumb/.+/(\d+)px-[^/?]+", url or "")
    if not achado:
        return ""
    alvo = next((w for w in LARGURAS_COMMONS if w >= largura), LARGURAS_COMMONS[-1])
    if largura_original and alvo > largura_original:
        return ""
    return url[:achado.start(1)] + str(alvo) + url[achado.end(1):]


def _normaliza_item_commons(pagina: dict):
    """Item no mesmo formato da Openverse, ou None se a licenca nao serve para pagina de cliente."""
    infos = pagina.get("imageinfo") or []
    if not isinstance(infos, list) or not infos or not isinstance(infos[0], dict):
        return None
    info = infos[0]
    meta = info.get("extmetadata") or {}

    def valor(chave):
        v = meta.get(chave)
        return (v.get("value") if isinstance(v, dict) else "") or ""

    licenca = _sem_html(valor("LicenseShortName"))
    if not LICENCA_COMMONS_OK.search(licenca):
        return None
    url = (info.get("thumburl") or info.get("url") or "").strip()
    if not url:
        return None
    artista = valor("Artist")
    achado = re.search(r'href="([^"]+)"', artista)
    titulo = re.sub(r"^File:", "", pagina.get("title") or "").rsplit(".", 1)[0].replace("_", " ").strip()
    codigo = re.sub(r"[ ]+", "-", licenca.lower())
    item = {
        "id": str(pagina.get("pageid") or ""),
        "titulo": titulo or "Sem título",
        "url": url,
        "thumbnail": url_commons_na_largura(url, 500, info.get("width") or 0),
        "autor": _sem_html(artista) or "autor desconhecido",
        "autor_url": _url_absoluta(achado.group(1)) if achado else "",
        "licenca": licenca,
        "licenca_url": _url_absoluta(valor("LicenseUrl")),
        "largura": info.get("width") or 0,
        "altura": info.get("height") or 0,
        "pagina_origem": (info.get("descriptionurl") or "").strip(),
        "exige_credito": valor("AttributionRequired").strip().lower() == "true" or not licenca.upper().startswith(("CC0", "PUBLIC", "PD")),
    }
    item["credito"] = _monta_credito(item)
    return item


def _orientacao_bate(item: dict, orientation: str) -> bool:
    larg, alt = item.get("largura") or 0, item.get("altura") or 0
    if not larg or not alt:
        return True
    if orientation == "landscape":
        return larg >= alt * 1.15
    if orientation == "portrait":
        return alt >= larg * 1.15
    return 0.85 <= larg / alt <= 1.15


def search_commons(query: str, limit: int = 6, orientation: str = "landscape", autor: str = "",
                   categoria: str = "", filtrar_acervo: bool = True) -> list:
    """Busca fotos na Wikimedia Commons (sem chave). Lista vazia em qualquer falha, com o motivo no stderr.

    Pausa antes da chamada e, em HTTP 429, espera o Retry-After (teto de TETO_ESPERA_COMMONS s) e tenta
    UMA vez: a Commons limita quem insiste, e laco de retentativa so piora o bloqueio.

    3.5.8: `autor` e `categoria` estreitam a busca (a Commons rende por AUTOR ou por CATEGORIA de acervo; busca por
    palavra solta de movel traz museu e lixo); `filtrar_acervo` tira prova policial, casa de boneca, reboque e museu.
    """
    try:
        pedido = int(limit)
    except (TypeError, ValueError):
        pedido = 6
    pedido = max(1, min(pedido, 20))
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": ("%s%s%s filetype:bitmap" % (
            query, (" " + autor.strip()) if autor and autor.strip() else "",
            (' incategory:"%s"' % categoria.strip().replace('"', "")) if categoria and categoria.strip() else "")),
        "gsrnamespace": "6", "gsrlimit": str(min(50, pedido * 4)),
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1280",
        "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist|AttributionRequired|ObjectName",
        "origin": "*",
    }
    url = COMMONS_API_URL + "?" + urllib.parse.urlencode(params)
    cabecalhos = {"User-Agent": COMMONS_USER_AGENT, "Accept": "application/json"}
    dados = None
    for tentativa in (1, 2):
        time.sleep(PAUSA_COMMONS)
        try:
            with _abrir_url(urllib.request.Request(url, headers=cabecalhos), timeout=25) as resp:
                dados = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and tentativa == 1:
                try:
                    espera = int(float((e.headers or {}).get("Retry-After", "5")))
                except (TypeError, ValueError):
                    espera = 5
                espera = max(1, min(espera, TETO_ESPERA_COMMONS))
                print("AVISO Wikimedia Commons: HTTP 429 (limite de chamadas). Espero %d s e tento uma vez." % espera,
                      file=sys.stderr)
                time.sleep(espera)
                continue
            print("ERRO Wikimedia Commons: HTTP %s (%s)%s" % (
                e.code, e.reason, ". Ela limita quem insiste: espere um minuto antes de tentar de novo." if e.code == 429 else "."),
                file=sys.stderr)
            return []
        except urllib.error.URLError as e:
            print("ERRO Wikimedia Commons: sem conexão com commons.wikimedia.org (%s)." % (e.reason,), file=sys.stderr)
            return []
        except ValueError as e:
            print("ERRO Wikimedia Commons: resposta não veio em JSON válido (%s)." % e, file=sys.stderr)
            return []
        except Exception as e:  # rede e API de terceiro: nunca derrubar o script
            print("ERRO Wikimedia Commons inesperado: %s" % e, file=sys.stderr)
            return []

    paginas = ((dados or {}).get("query") or {}).get("pages") if isinstance(dados, dict) else None
    if isinstance(paginas, dict):
        paginas = list(paginas.values())
    if not isinstance(paginas, list):
        print("ERRO Wikimedia Commons: resposta em formato inesperado.", file=sys.stderr)
        return []
    paginas = sorted((p for p in paginas if isinstance(p, dict)), key=lambda p: p.get("index") or 0)
    itens = [i for i in (_normaliza_item_commons(p) for p in paginas) if i]
    if filtrar_acervo:
        bons = [i for i in itens if not ACERVO_RUIM_COMMONS.search(i["titulo"])]
        if len(bons) != len(itens):
            print("AVISO Wikimedia Commons: %d resultado(s) descartado(s) por serem acervo que não serve a página de cliente "
                  "(prova policial, casa de boneca, reboque, museu). Para ver tudo: --sem-filtro. "
                  "Busque por autor (--autor) ou por categoria (--categoria) quando a palavra solta rende pouco." % (len(itens) - len(bons)),
                  file=sys.stderr)
        itens = bons
    certos = [i for i in itens if _orientacao_bate(i, orientation)]
    resto = [i for i in itens if i not in certos]
    return (certos + resto)[:pedido]


def buscar_foto_sem_chave(query: str, limit: int = 6, orientation: str = "landscape") -> dict:
    """Foto com licenca, sem chave: Openverse primeiro; se ela nao responde ou nao acha, a Wikimedia Commons.

    Devolve {"fonte": "openverse" | "commons", "itens": [...], "motivo": "<por que a segunda rota>"}.
    """
    itens, falhou, motivo = _busca_openverse(query, limit=limit, orientation=orientation)
    if itens:
        return {"fonte": "openverse", "itens": itens, "motivo": ""}
    porque = "a Openverse não respondeu (%s)" % motivo if falhou else "a Openverse não achou foto para essa busca"
    print("AVISO: %s; tentando a Wikimedia Commons." % porque, file=sys.stderr)
    return {"fonte": "commons", "itens": search_commons(query, limit=limit, orientation=orientation), "motivo": porque}


def format_openverse(items: list, query: str, veio_de_fallback: bool = False,
                     fonte: str = "Openverse", motivo: str = "") -> str:
    barra = "=" * 70
    linhas = []

    if not items:
        linhas.append(barra)
        linhas.append('  Nenhuma foto encontrada na %s para: "%s"' % (fonte, query))
        linhas.append(barra)
        linhas.append("  Tente termos em ingles e mais concretos, ex: \"team meeting office\".")
        linhas.append(f"  Outras rotas sem chave: {comando('assets-search.py')} --type sem-chave")
        linhas.append(barra)
        return "\n".join(linhas)

    linhas.append(barra)
    linhas.append('  %d fotos REAIS encontradas na %s para: "%s"' % (len(items), fonte, query))
    linhas.append("  Rota que respondeu: %s%s" % (fonte, " (%s)" % motivo if motivo else ""))
    linhas.append("  Fonte sem chave de API. Licença aberta de uso comercial (credite o autor).")
    if veio_de_fallback:
        linhas.append("  (fallback automático: sem foto vinda do Pexels, a busca veio daqui)")
    linhas.append(barra)
    linhas.append("")

    for i, item in enumerate(items, 1):
        dimensao = "%sx%s" % (item["largura"], item["altura"]) if item["largura"] else "dimensão não informada"
        linhas.append("  %d. %s" % (i, item["titulo"]))
        linhas.append("     %s | Por: %s | Licença: %s" % (dimensao, item["autor"], item["licenca"]))
        linhas.append("     Imagem:  %s" % item["url"])
        if item["thumbnail"]:
            linhas.append("     %s %s" % ("Miniatura (500 px):" if "/500px-" in item["thumbnail"] else "Thumb:   ", item["thumbnail"]))
        grande = url_commons_na_largura(item["url"], 1920, item["largura"]) if "/thumb/" in item["url"] else ""
        if grande and "/1920px-" in grande and "/1920px-" not in item["url"]:
            linhas.append("     Versão 1920 px (herói): %s" % grande)
            linhas.append("     (a Commons só serve miniatura em 500, 960, 1280 ou 1920 px; outra largura dá HTTP 400)")
        if item["pagina_origem"]:
            linhas.append("     Origem:  %s" % item["pagina_origem"])
        if item["licenca_url"]:
            linhas.append("     Licença: %s" % item["licenca_url"])
        linhas.append("")
        linhas.append("     CRÉDITO %s:" % ("OBRIGATÓRIO" if item["exige_credito"] else "recomendado"))
        linhas.append("     %s" % item["credito"])
        if "-ND" in item["licenca"].upper():
            linhas.append("     ATENÇÃO ND: não pode recortar, filtrar nem sobrepor texto nessa foto.")
        linhas.append("")
        linhas.append("     USO RÁPIDO (já com o crédito junto da imagem):")
        linhas.append('     <figure class="relative">')
        linhas.append(
            '       <img src="%s" alt="%s" loading="lazy" class="w-full h-full object-cover" />'
            % (item["url"], item["titulo"])
        )
        linhas.append('       <figcaption class="text-xs opacity-60 mt-1">')
        if item["licenca_url"]:
            linhas.append(
                '         Foto de <a href="%s">%s</a>, <a href="%s">%s</a>'
                % (item["autor_url"] or item["pagina_origem"], item["autor"], item["licenca_url"], item["licenca"])
            )
        else:
            linhas.append("         Foto de %s, %s" % (item["autor"], item["licenca"]))
        linhas.append("       </figcaption>")
        linhas.append("     </figure>")
        linhas.append("")

    linhas.append(barra)
    linhas.append("  ATRIBUIÇÃO: em licença CC BY, CC BY-SA e CC BY-ND o crédito é OBRIGATÓRIO.")
    linhas.append("  Não é cortesia, é condição da licença. Sem crédito o uso é irregular.")
    linhas.append("  Onde pôr: legenda da foto, ou uma seção 'Créditos' no rodapé da página.")
    linhas.append("  Modelo pronto e o que NÃO fazer: references/assets-sem-chave.md")
    linhas.append("")
    linhas.append("  Baixe e otimize antes de publicar (hotlink de terceiro cai):")
    linhas.append("    # o -A é obrigatório: alguns CDNs devolvem 403 pro curl pelado")
    linhas.append("    curl -L -A \"Mozilla/5.0\" -o public/img/hero.jpg \"<url da imagem>\"")
    linhas.append("    file public/img/hero.jpg   # confirme que veio imagem, não HTML de erro")
    linhas.append("    Converta pra WebP | Hero < 200KB | Seções < 100KB")
    linhas.append(barra)
    return "\n".join(linhas)


def print_aviso_fallback_openverse(motivo: str) -> None:
    print(
        "\n".join(
            [
                "",
                "  AVISO: caindo na Openverse (%s)." % motivo,
                "  A Openverse devolve FOTO REAL sem nenhuma chave de API.",
                "  Contrapartida: a licença Creative Commons exige creditar o autor.",
                "  O crédito de cada foto já vem pronto na saída abaixo.",
                "  Detalhes: references/assets-sem-chave.md",
                "",
            ]
        ),
        file=sys.stderr,
    )


def buscar_fotos_com_fallback(query: str, limit: int = 6, orientation: str = "landscape") -> dict:
    """Busca fotos e NUNCA volta vazia por falta de chave.

    Com PEXELS_API_KEY: usa o Pexels (sem obrigação de crédito).
    Sem chave, ou com chave que nao achou nada: cai na Openverse.

    Devolve {"fonte": "pexels" | "openverse" | "commons", "itens": [...]}. Se a Openverse nao
    responde, a segunda rota e a Wikimedia Commons (com o motivo em "motivo").
    """
    tem_chave = bool(os.environ.get("PEXELS_API_KEY", "").strip())

    if tem_chave:
        itens = search_photos(query, limit=limit, orientation=orientation)
        if itens:
            return {"fonte": "pexels", "itens": itens}
        print_aviso_fallback_openverse(
            "o Pexels não devolveu foto: chave inválida ou busca sem resultado"
        )
    else:
        print_aviso_fallback_openverse("PEXELS_API_KEY não está configurada")

    return buscar_foto_sem_chave(query, limit=limit, orientation=orientation)


# ─── ROTAS SEM NENHUMA CHAVE ─────────────────────────────────────────────────

def show_sem_chave_resources() -> str:
    barra = "=" * 70
    linhas = []
    linhas.append(barra)
    linhas.append("  ASSETS SEM NENHUMA API KEY")
    linhas.append("  Nenhuma página precisa sair com retangulo cinza vazio.")
    linhas.append(barra)
    linhas.append("")

    linhas.append("  1. OPENVERSE: fotos reais, licença Creative Commons (a melhor rota)")
    linhas.append(f"     {comando('assets-search.py')} \"team meeting office\" --type openverse -n 6")
    linhas.append(f"     {comando('assets-search.py')} \"sua busca\" --type photo   # cai aqui sozinho")
    linhas.append("     Crédito ao autor OBRIGATÓRIO (CC BY / BY-SA). Sai pronto na busca.")
    linhas.append("")

    linhas.append("  2. PICSUM: JPEG real, sem tema, otimo pra mockup e placeholder")
    linhas.append("     %s/1600/900          # aleatorio" % PICSUM_URL)
    linhas.append("     %s/seed/hero/1600/900 # estavel (mesma foto sempre)" % PICSUM_URL)
    linhas.append("     %s/1600/900?grayscale&blur=2" % PICSUM_URL)
    linhas.append("     Não use como foto de verdade do cliente: e foto generica.")
    linhas.append("")

    linhas.append("  3. UNDRAW: ilustrações SVG tematicas, cor customizavel")
    linhas.append("     https://undraw.co/illustrations")
    linhas.append(f"     {comando('assets-search.py')} --type illustrations \"team work\"")
    linhas.append("     Sem obrigação de crédito. Boas pra seção de features e vazio de dados.")
    linhas.append("")

    linhas.append("  4. GRADIENTE E PATTERN SVG (background, nunca sozinho como 'imagem')")
    linhas.append(f"     {comando('assets-search.py')} --type backgrounds")
    linhas.append("")

    linhas.append(barra)
    linhas.append("  REGRA: página só com texto, gradiente e SVG generico REPROVA na")
    linhas.append("  auditoria visual da skill. Coloque foto real ou mockup de produto.")
    linhas.append("  Nunca use imagem de licença desconhecida em página de cliente.")
    linhas.append("  Guia completo: references/assets-sem-chave.md")
    linhas.append(barra)
    return "\n".join(linhas)


# ─── LOTTIE ANIMATIONS ────────────────────────────────────────────────────────

def show_lottie_resources(query: str = "") -> str:
    encoded = urllib.parse.quote(query) if query else ""
    lines = []
    lines.append(f"{'='*70}")
    lines.append("  LOTTIE ANIMATIONS: Fontes Gratuitas")
    lines.append(f"{'='*70}\n")

    if query:
        lines.append(f"  Buscar '{query}' em:\n")
        lines.append(f"  LottieFiles:  https://lottiefiles.com/search?q={encoded}&category=animation")
        lines.append(f"  LottieFiles:  https://lottiefiles.com/free-animations")
        lines.append("")

    lines.append("  INSTALAÇÃO:")
    lines.append("  npm install @lottiefiles/react-lottie-player")
    lines.append("  # ou: npm install lottie-react\n")

    lines.append("  USO: react-lottie-player:")
    lines.append("""  'use client'
  import { Player } from '@lottiefiles/react-lottie-player'

  // Com URL direta do LottieFiles
  <Player
    autoplay loop
    src="https://assets10.lottiefiles.com/packages/lf20_XXXXX.json"
    style={{ width: 300, height: 300 }}
  />

  // Com arquivo local (baixe o .json em public/animations/)
  <Player autoplay loop src="/animations/loading.json" style={{ width: 200 }} />""")

    lines.append("")
    lines.append("  USO: lottie-react (alternativa mais leve):")
    lines.append("""  'use client'
  import Lottie from 'lottie-react'
  import animationData from '@/public/animations/my-animation.json'

  <Lottie
    animationData={animationData}
    loop={true}
    style={{ width: 300, height: 300 }}
  />""")

    lines.append("")
    lines.append("  CATEGORIAS POPULARES para sites:")
    categories = [
        ("loading/spinner",  "https://lottiefiles.com/search?q=loading&category=animation"),
        ("success/checkmark","https://lottiefiles.com/search?q=success+check&category=animation"),
        ("rocket/launch",    "https://lottiefiles.com/search?q=rocket+launch&category=animation"),
        ("404 error",        "https://lottiefiles.com/search?q=404+error&category=animation"),
        ("empty state",      "https://lottiefiles.com/search?q=empty+state&category=animation"),
        ("celebrate",        "https://lottiefiles.com/search?q=celebration+confetti&category=animation"),
        ("dashboard/charts", "https://lottiefiles.com/search?q=dashboard+chart&category=animation"),
        ("AI/robot",         "https://lottiefiles.com/search?q=artificial+intelligence+robot&category=animation"),
    ]
    for cat, url in categories:
        lines.append(f"  - {cat:25s} {url}")

    lines.append(f"\n{'='*70}")
    return "\n".join(lines)


# ─── ILLUSTRATIONS ────────────────────────────────────────────────────────────

def show_illustration_resources(query: str = "") -> str:
    encoded = urllib.parse.quote(query) if query else "team"
    lines = []
    lines.append(f"{'='*70}")
    lines.append("  ILUSTRAÇÕES SVG: Fontes Gratuitas")
    lines.append(f"{'='*70}\n")

    lines.append("  UNDRAW (open source, customizavel por cor):")
    lines.append(f"  Browse: https://undraw.co/illustrations")
    if query:
        lines.append(f"  Buscar: https://undraw.co/search/{encoded}")
    lines.append(f"  API:    https://undraw.co/api/illustrations?q={encoded}&color=6366f1")
    lines.append("  Uso: Baixe o SVG > salve em public/illustrations/ > <img src=\"/illustrations/hero.svg\" />")
    lines.append("")

    lines.append("  STORYSET (animadas com Freepik):")
    lines.append(f"  Browse:  https://storyset.com")
    lines.append(f"  Buscar:  https://storyset.com/search?q={encoded}")
    lines.append("  Tipos: People, Technology, Business, Education, Web, App")
    lines.append("  Formatos: SVG, PNG, animado (Lottie)")
    lines.append("")

    lines.append("  ICONS8 ILLUSTRATIONS (pack cohesivo):")
    lines.append("  Browse: https://icons8.com/illustrations")
    lines.append("")

    lines.append("  BLUSH (customizaveis, premium):")
    lines.append("  Browse: https://blush.design")
    lines.append("")

    lines.append("  USO RÁPIDO em JSX:")
    lines.append("""  // SVG inline (melhor para animações CSS)
  import HeroIllustration from '@/public/illustrations/hero.svg'
  <Image src={HeroIllustration} alt="Hero" className="w-full max-w-lg" />

  // Com next/image (otimizado)
  import Image from 'next/image'
  <Image src="/illustrations/team.svg" alt="Team" width={500} height={400} />

  // Framer Motion na ilustração
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.8, ease: "backOut" }}
  >
    <Image src="/illustrations/hero.svg" alt="..." width={500} height={400} />
  </motion.div>""")

    lines.append(f"\n{'='*70}")
    return "\n".join(lines)


# ─── ANIMATED ICONS ──────────────────────────────────────────────────────────

def show_icon_resources() -> str:
    lines = []
    lines.append(f"{'='*70}")
    lines.append("  ÍCONES ANIMADOS: Fontes e Integracao")
    lines.append(f"{'='*70}\n")

    lines.append("  LORDICON (ícones animados Lottie, gratuitos):")
    lines.append("  Browse:  https://lordicon.com/icons")
    lines.append("  Estilo:  Flat, Outline, Lineal, Gradient")
    lines.append("  npm install lord-icon-element\n")

    lines.append("""  USO LordIcon:
  // No component (carregar script uma vez no layout)
  import Script from 'next/script'
  <Script src="https://cdn.lordicon.com/lordicon.js" />

  // Ícone animado (trigger: hover, click, loop, morph)
  <lord-icon
    src="https://cdn.lordicon.com/XXXXX.json"
    trigger="hover"
    colors="primary:#6366f1,secondary:#a855f7"
    style={{ width: 60, height: 60 }}
  />""")

    lines.append("")
    lines.append("  PHOSPHOR ICONS (SVG estatico mas premium):")
    lines.append("  npm install @phosphor-icons/react")
    lines.append("""  import { Rocket, Lightning, Star } from '@phosphor-icons/react'
  <Rocket size={32} weight="duotone" color="#6366f1" />""")

    lines.append("")
    lines.append("  LUCIDE REACT (já incluso no shadcn/ui):")
    lines.append("""  import { Zap, Shield, Globe } from 'lucide-react'
  <Zap className="w-8 h-8 text-indigo-500" />

  // Com animação hover no container pai
  <div className="group">
    <Zap className="w-8 h-8 text-indigo-500 group-hover:scale-125 group-hover:text-indigo-400 transition-all duration-300" />
  </div>""")

    lines.append(f"\n{'='*70}")
    return "\n".join(lines)


# ─── BACKGROUND RESOURCES ────────────────────────────────────────────────────

def show_background_resources() -> str:
    lines = []
    lines.append(f"{'='*70}")
    lines.append("  BACKGROUNDS: Patterns, SVG, Gradientes")
    lines.append(f"{'='*70}\n")

    lines.append("  GERADORES ONLINE:")
    resources = [
        ("SVG Backgrounds",    "https://www.svgbackgrounds.com",            "SVG patterns para background-image"),
        ("Hero Patterns",      "https://heropatterns.com",                  "Patterns CSS customizaveis"),
        ("CSS Gradient",       "https://cssgradient.io",                    "Gradientes CSS visuais"),
        ("Mesh Gradient",      "https://meshgradient.in",                   "Mesh gradients para download"),
        ("Haikei",             "https://app.haikei.app",                    "Blobs, waves, gradients SVG"),
        ("MagicPattern",       "https://www.magicpattern.design/tools",     "Patterns e backgrounds premium"),
        ("BGjar",              "https://bgjar.com",                         "Backgrounds SVG animados"),
        ("Fffuel",             "https://fffuel.co",                         "Tools SVG gratuitas"),
        ("Grainy Gradients",   "https://grainy-gradients.vercel.app",       "Noise texture + gradient"),
    ]
    for name, url, desc in resources:
        lines.append(f"  {name:20s} {url}")
        lines.append(f"  {'':20s} -> {desc}")
        lines.append("")

    lines.append("  USO DE PATTERN SVG COMO BACKGROUND CSS:")
    lines.append("""  /* Cole o SVG inline no CSS */
  .hero-pattern {
    background-color: #0f172a;
    background-image: url("data:image/svg+xml,%3Csvg...");
  }

  /* Ou use arquivo em public/ */
  .hero-bg {
    background-image: url('/patterns/dots.svg');
    background-size: 20px 20px;
  }""")

    lines.append("")
    lines.append("  NOISE TEXTURE (subtileza premium):")
    lines.append("""  /* Gera com: https://grainy-gradients.vercel.app */
  .noise-overlay::after {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.04;
    background-image: url('/textures/noise.png');
    background-repeat: repeat;
  }""")

    lines.append(f"\n{'='*70}")
    return "\n".join(lines)


# ─── FOLHA DE CONTATO (3.5.8): todas as miniaturas numa imagem só ─────────────
#
# Quem escolhe a foto não deveria abrir resultado por resultado (21 min no teste de 3.5.6). Com
# `--folha arquivo.png` o script baixa a miniatura de cada resultado e monta UMA grade com o número
# de cada item, o mesmo número da lista em texto. Respeita a pausa entre chamadas e o HTTP 429 do
# resto do script: espera o Retry-After (teto TETO_ESPERA_COMMONS) e tenta UMA vez; se não vier,
# a célula fica com o número e o aviso "sem miniatura", e a folha sai mesmo assim.

PAUSA_MINIATURA_COMMONS = PAUSA_COMMONS   # a Commons limita quem baixa muita miniatura de uma vez
PAUSA_MINIATURA = 0.3                     # as outras rotas: educação com o servidor de terceiro
FOLHA_CELULA = (400, 300)                 # largura x altura de cada miniatura na grade
FOLHA_MARGEM = 12


def urls_das_miniaturas(items: list, tipo: str) -> list:
    """Uma URL de miniatura (ou "") por item, na ordem da lista: o índice + 1 é o número impresso."""
    urls = []
    for item in items:
        if tipo == "pexels-foto":
            src = item.get("src") or {}
            urls.append(src.get("medium") or src.get("small") or src.get("large") or "")
        elif tipo == "pexels-video":
            fotos = item.get("video_pictures") or []
            urls.append((fotos[0].get("picture") if fotos and isinstance(fotos[0], dict) else "") or item.get("image") or "")
        else:
            urls.append(item.get("thumbnail") or item.get("url") or "")
    return urls


def _baixar_miniatura(url: str):
    """Bytes da miniatura, ou (None, motivo). Pausa antes; em HTTP 429 espera o Retry-After e tenta uma vez."""
    commons = "wikimedia.org" in url or "wikipedia.org" in url
    cabecalhos = {"User-Agent": COMMONS_USER_AGENT if commons else USER_AGENT, "Accept": "image/*"}
    motivo = ""
    for tentativa in (1, 2):
        time.sleep(PAUSA_MINIATURA_COMMONS if commons else PAUSA_MINIATURA)
        try:
            with _abrir_url(urllib.request.Request(url, headers=cabecalhos), timeout=25) as resp:
                return resp.read(), ""
        except urllib.error.HTTPError as e:
            if e.code == 429 and tentativa == 1:
                try:
                    espera = int(float((e.headers or {}).get("Retry-After", "5")))
                except (TypeError, ValueError):
                    espera = 5
                espera = max(1, min(espera, TETO_ESPERA_COMMONS))
                print("AVISO miniatura: HTTP 429 (limite de chamadas). Espero %d s e tento uma vez." % espera, file=sys.stderr)
                time.sleep(espera)
                continue
            motivo = "HTTP %s" % e.code
            break
        except Exception as e:  # rede de terceiro: uma miniatura que falha não derruba a folha
            motivo = str(getattr(e, "reason", e))[:60]
            break
    return None, motivo


def _numero_grande(numero: int, altura: int = 72):
    """Imagem RGBA com o número em branco sobre fundo escuro, feita só com a fonte padrão da PIL.

    A fonte padrão é um bitmap minúsculo: desenha pequeno e amplia (NEAREST) até a altura pedida. Assim
    o número sai legível em qualquer versão da PIL e em qualquer sistema, sem depender de fonte instalada.
    """
    from PIL import Image, ImageDraw, ImageFont
    fonte = ImageFont.load_default()
    texto = str(numero)
    caixa = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), texto, font=fonte)
    larg, alt = max(1, caixa[2] - caixa[0]), max(1, caixa[3] - caixa[1])
    pequeno = Image.new("L", (larg + 4, alt + 4), 0)
    ImageDraw.Draw(pequeno).text((2 - caixa[0], 2 - caixa[1]), texto, fill=255, font=fonte)
    escala = max(1, altura // (alt + 4))
    grande = pequeno.resize(((larg + 4) * escala, (alt + 4) * escala), Image.NEAREST)
    fundo = Image.new("RGBA", grande.size, (20, 20, 20, 235))
    fundo.paste((255, 255, 255, 255), mask=grande)
    return fundo


def montar_folha(miniaturas: list, destino: str, colunas: int = 0) -> dict:
    """Monta a grade. `miniaturas` = lista de bytes ou None, na ordem dos itens (número = posição + 1).

    Devolve {"arquivo", "colunas", "linhas", "sem_miniatura": [números]}. Exige a Pillow.
    """
    import io
    from PIL import Image, ImageDraw, ImageFont
    total = len(miniaturas)
    if total == 0:
        raise ValueError("nenhum resultado para montar a folha")
    colunas = colunas or (min(total, 3) if total <= 6 else 4)
    linhas = (total + colunas - 1) // colunas
    cw, ch = FOLHA_CELULA
    m = FOLHA_MARGEM
    folha = Image.new("RGB", (colunas * (cw + m) + m, linhas * (ch + m) + m), (235, 235, 235))
    sem = []
    for idx, dados in enumerate(miniaturas):
        x = m + (idx % colunas) * (cw + m)
        y = m + (idx // colunas) * (ch + m)
        celula = Image.new("RGB", (cw, ch), (60, 60, 60))
        ok = False
        if dados:
            try:
                img = Image.open(io.BytesIO(dados))
                img.load()
                img = img.convert("RGB")
                img.thumbnail((cw, ch))
                celula.paste(img, ((cw - img.width) // 2, (ch - img.height) // 2))
                ok = True
            except Exception:
                ok = False
        if not ok:
            sem.append(idx + 1)
            d = ImageDraw.Draw(celula)
            d.text((cw // 2 - 36, ch // 2 - 5), "sem miniatura", fill=(230, 230, 230), font=ImageFont.load_default())
        folha.paste(celula, (x, y))
        etiqueta = _numero_grande(idx + 1)
        folha.paste(etiqueta, (x, y), etiqueta)
    pasta = os.path.dirname(os.path.abspath(destino))
    os.makedirs(pasta, exist_ok=True)
    folha.save(destino, "PNG")
    return {"arquivo": destino, "colunas": colunas, "linhas": linhas, "sem_miniatura": sem}


def gerar_folha(items: list, tipo: str, destino: str) -> None:
    """Baixa as miniaturas e grava a folha; avisa no stdout (uma linha) ou no stderr (se faltar a Pillow)."""
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("AVISO --folha: precisa da Pillow (pip install pillow). A lista em texto acima continua valendo.", file=sys.stderr)
        return
    if not items:
        print("AVISO --folha: a busca não devolveu resultados, então não há folha para montar.", file=sys.stderr)
        return
    baixadas = []
    for url in urls_das_miniaturas(items, tipo):
        dados, motivo = _baixar_miniatura(url) if url else (None, "sem URL de miniatura")
        baixadas.append(dados)
        if dados is None:
            print("AVISO --folha: sem miniatura no item %d (%s)." % (len(baixadas), motivo), file=sys.stderr)
    r = montar_folha(baixadas, destino)
    falta = (" Sem miniatura nos números: %s." % ", ".join(str(n) for n in r["sem_miniatura"])) if r["sem_miniatura"] else ""
    print("\nFolha de contato: %s (%d miniaturas em %d x %d; o número de cada uma é o da lista acima).%s"
          % (destino, len(baixadas), r["colunas"], r["linhas"], falta))


# ─── NO API KEY ───────────────────────────────────────────────────────────────

def print_no_api_key(com_saida_alternativa: bool = True):
    linhas = [
        "",
        "  PEXELS_API_KEY não encontrada.",
        "",
        "  O Pexels é opcional. Ele só evita a obrigação de creditar o autor.",
        "  Chave gratuita (200 req/hora): https://www.pexels.com/api/",
        "  Depois de pegar a chave:",
        "",
        '      export PEXELS_API_KEY="sua-chave-aqui"',
        "",
    ]
    if com_saida_alternativa:
        linhas += [
            "  SEM CHAVE VOCÊ AINDA TEM FOTO REAL:",
            f'      {comando("assets-search.py")} "sua busca" --type openverse',
            f"      {comando('assets-search.py')} --type sem-chave",
            "",
            "  A Openverse devolve fotos reais com licença Creative Commons.",
            "  Nesse caso creditar o autor NÃO é opcional.",
            "  Modelo de crédito pronto: references/assets-sem-chave.md",
            "",
        ]
    print("\n".join(linhas), file=sys.stderr)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Busca assets visuais: vídeos, fotos, Lottie, ilustrações, ícones, backgrounds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tipos disponíveis:
  video        Busca vídeos no Pexels (padrão): requer PEXELS_API_KEY
  photo        Busca fotos: usa Pexels se houver chave, senão CAI NA OPENVERSE
  openverse    Fotos reais com licença Creative Commons, SEM chave (alias: cc)
  commons      Fotos reais da Wikimedia Commons, SEM chave (2ª rota, entra sozinha se a Openverse cair)
  sem-chave    Lista todas as rotas que funcionam sem nenhuma API key
  lottie       Lista fontes e como usar animações Lottie
  illustrations Lista fontes e como usar ilustrações SVG
  icons        Lista fontes e como usar ícones animados
  backgrounds  Lista geradores de backgrounds SVG/patterns

Exemplos:
  node scripts/py.mjs assets-search.py "dark abstract"
  node scripts/py.mjs assets-search.py tech-dark
  node scripts/py.mjs assets-search.py "minimal white" --type video --orientation landscape
  node scripts/py.mjs assets-search.py "office team" --type photo -n 5
  node scripts/py.mjs assets-search.py "office team" --type photo -n 8 --folha prova/fotos.png   # folha de contato numerada
  node scripts/py.mjs assets-search.py "team meeting office" --type openverse -n 5
  node scripts/py.mjs assets-search.py --type sem-chave
  node scripts/py.mjs assets-search.py "loading" --type lottie
  node scripts/py.mjs assets-search.py --type illustrations "team work"
  node scripts/py.mjs assets-search.py --type backgrounds
  node scripts/py.mjs assets-search.py --presets
        """
    )
    parser.add_argument("query", nargs="?", default="", help="Termo de busca ou preset")
    parser.add_argument("--type", "-t",
        choices=["video", "photo", "openverse", "cc", "commons", "sem-chave",
                 "lottie", "illustrations", "icons", "backgrounds"],
        default="video",
        help="Tipo de asset (default: vídeo)"
    )
    parser.add_argument("-n", "--limit", type=int, default=6, help="Número de resultados (default: 6)")
    parser.add_argument("--orientation",
        choices=["landscape", "portrait", "square"],
        default="landscape",
        help="Orientacao do video/foto (default: landscape)"
    )
    parser.add_argument("--presets", action="store_true", help="Listar todos os presets de vídeo")
    parser.add_argument("--autor", default="", help="Commons: estreita a busca pelo nome do autor (ex.: Shixart1985)")
    parser.add_argument("--categoria", default="", help='Commons: estreita a busca pela categoria do acervo (ex.: "Wooden furniture")')
    parser.add_argument("--sem-filtro", action="store_true", help="Commons: não descarta prova policial, casa de boneca, reboque e museu")
    parser.add_argument("--folha", default="", metavar="ARQUIVO.png",
        help="Fotos e vídeos: baixa as miniaturas dos resultados e monta UMA imagem em grade com o número de cada item (o mesmo da lista)")

    args = parser.parse_args()

    if args.presets:
        print("\nPresets de vídeo disponíveis:\n")
        for key, val in PRESET_QUERIES.items():
            print(f"  {key:20s} -> \"{val}\"")
        print()
        return

    # Tipos que nao precisam de query ou API key
    if args.type == "sem-chave":
        print(show_sem_chave_resources())
        return
    if args.type == "backgrounds":
        print(show_background_resources())
        return
    if args.type == "icons":
        print(show_icon_resources())
        return
    if args.type == "lottie":
        print(show_lottie_resources(args.query))
        return
    if args.type == "illustrations":
        print(show_illustration_resources(args.query))
        return

    # Videos e fotos precisam de query
    if not args.query:
        parser.error("Informe uma query ou preset. Use --presets para ver opções.")

    # Resolver preset
    query = PRESET_QUERIES.get(args.query, args.query)
    if (args.autor or args.categoria or args.sem_filtro) and args.type != "commons":
        print("AVISO: --autor, --categoria e --sem-filtro só valem com --type commons (a rota da Wikimedia Commons).", file=sys.stderr)

    if args.type == "video":
        items = search_videos(query, limit=args.limit, orientation=args.orientation)
        print(format_videos(items, query))
        if args.folha:
            gerar_folha(items, "pexels-video", args.folha)
    elif args.type in ("openverse", "cc"):
        items = search_openverse(query, limit=args.limit, orientation=args.orientation)
        print(format_openverse(items, query))
        if args.folha:
            gerar_folha(items, "openverse", args.folha)
    elif args.type == "commons":
        items = search_commons(query, limit=args.limit, orientation=args.orientation, autor=args.autor,
                               categoria=args.categoria, filtrar_acervo=not args.sem_filtro)
        print(format_openverse(items, query, fonte="Wikimedia Commons"))
        if args.folha:
            gerar_folha(items, "commons", args.folha)
    elif args.type == "photo":
        resultado = buscar_fotos_com_fallback(
            query, limit=args.limit, orientation=args.orientation
        )
        if resultado["fonte"] in ("openverse", "commons"):
            print(format_openverse(resultado["itens"], query, veio_de_fallback=True,
                                   fonte="Wikimedia Commons" if resultado["fonte"] == "commons" else "Openverse",
                                   motivo=resultado.get("motivo", "")))
        else:
            print(format_photos(resultado["itens"], query))
        if args.folha:
            gerar_folha(resultado["itens"], "pexels-foto" if resultado["fonte"] == "pexels" else "openverse", args.folha)


if __name__ == "__main__":
    main()
