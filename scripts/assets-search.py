#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assets Search: Videos, Fotos, Lottie, Ilustracoes para paginas web.

Busca assets visuais gratuitos para usar em backgrounds, heroes, secoes.

Uso:
  python3 assets-search.py "dark abstract"              # videos (padrao)
  python3 assets-search.py "technology" --type photo    # fotos
  python3 assets-search.py tech-dark                    # preset video
  python3 assets-search.py --type lottie "loading"      # lottie (links)
  python3 assets-search.py --type illustrations         # undraw/storyset
  python3 assets-search.py --type icons                 # lordicon/animated
  python3 assets-search.py --type openverse "team"      # FOTOS REAIS SEM CHAVE (licenca CC)
  python3 assets-search.py --type sem-chave             # todas as rotas sem chave
  python3 assets-search.py --presets                    # listar presets

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
import argparse
import urllib.request
import urllib.parse
import urllib.error


# ─── CONFIG ───────────────────────────────────────────────────────────────────

PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"
PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"

# Openverse: fotos reais com licenca Creative Commons, SEM chave de API.
OPENVERSE_IMAGE_URL = "https://api.openverse.org/v1/images/"
# Placeholder real (JPEG de verdade) pra mockup, tambem sem chave.
PICSUM_URL = "https://picsum.photos"
USER_AGENT = "construtor-paginas-assets-search/1.0"

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
            print("ERRO: API key invalida. Verifique sua PEXELS_API_KEY.", file=sys.stderr)
        else:
            print(f"ERRO HTTP {e.code}: {e.reason}", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"ERRO de conexao: {e.reason}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"ERRO inesperado: {e}", file=sys.stderr)
        return []


def format_videos(items: list, query: str) -> str:
    if not items:
        return "Nenhum video encontrado. Tente outra query ou preset."

    lines = []
    lines.append(f"{'='*70}")
    lines.append(f"  {len(items)} videos encontrados para: \"{query}\"")
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
        lines.append(f"     Licenca: Pexels License (uso gratuito, sem atribuicao obrigatoria)")
        lines.append(f"")
        lines.append(f"     USO RAPIDO:")
        lines.append(f"     <video autoPlay loop muted playsInline className=\"absolute inset-0 w-full h-full object-cover\">")
        lines.append(f"       <source src=\"{file_url}\" type=\"{f_type}\" />")
        lines.append(f"     </video>")
        lines.append("")

    lines.append(f"{'='*70}")
    lines.append("  Dicas de uso:")
    lines.append("  - Baixe e hospede no seu projeto (public/) para melhor performance")
    lines.append("  - Sempre adicione overlay escuro: <div class=\"absolute inset-0 bg-black/50\" />")
    lines.append("  - Use lazy loading: adicione loading=\"lazy\" ou carregue apos LCP")
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
            print("ERRO: API key invalida. Verifique PEXELS_API_KEY.", file=sys.stderr)
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
        lines.append(f"     USO RAPIDO:")
        lines.append(f"     <img src=\"{large}\" alt=\"{alt}\" className=\"w-full h-full object-cover\" />")
        lines.append("")

    lines.append(f"{'='*70}")
    lines.append("  Dicas: Baixe e otimize com squoosh.app ou tinypng.com antes de usar")
    lines.append("  Formato recomendado: WebP | Hero < 200KB | Secoes < 100KB")
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
        return "licenca desconhecida"
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
        pedacos.append("licenca %s (%s)" % (item["licenca"], item["licenca_url"]))
    else:
        pedacos.append("licenca %s" % item["licenca"])
    return ", ".join(pedacos)


def _normaliza_item_openverse(bruto: dict) -> dict:
    codigo = (bruto.get("license") or "").strip().lower()
    item = {
        "id": bruto.get("id", ""),
        "titulo": (bruto.get("title") or "Sem titulo").strip(),
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


def search_openverse(query: str, limit: int = 6, orientation: str = "landscape",
                     validar: bool = True) -> list:
    """Busca fotos com licenca Creative Commons na Openverse. NAO precisa de chave.

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
        "license_type": "commercial",  # so o que pode ir pra pagina de cliente
        "mature": "false",
    }
    aspecto = ASPECTO_POR_ORIENTACAO.get(orientation)
    if aspecto:
        params["aspect_ratio"] = aspecto

    url = OPENVERSE_IMAGE_URL + "?" + urllib.parse.urlencode(params)
    cabecalhos = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    try:
        req = urllib.request.Request(url, headers=cabecalhos)
        with urllib.request.urlopen(req, timeout=20) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(
            "ERRO Openverse: HTTP %s (%s). A busca sem chave nao respondeu agora, "
            "tente de novo em alguns segundos." % (e.code, e.reason),
            file=sys.stderr,
        )
        return []
    except urllib.error.URLError as e:
        print(
            "ERRO Openverse: sem conexao com api.openverse.org (%s). "
            "Verifique a internet ou o proxy." % (e.reason,),
            file=sys.stderr,
        )
        return []
    except ValueError as e:
        print("ERRO Openverse: resposta nao veio em JSON valido (%s)." % e, file=sys.stderr)
        return []
    except Exception as e:  # rede e API de terceiro: nunca derrubar o script
        print("ERRO Openverse inesperado: %s" % e, file=sys.stderr)
        return []

    if not isinstance(dados, dict):
        print("ERRO Openverse: resposta em formato inesperado.", file=sys.stderr)
        return []

    brutos = dados.get("results") or []
    if not isinstance(brutos, list):
        print("ERRO Openverse: campo 'results' em formato inesperado.", file=sys.stderr)
        return []

    itens = [
        _normaliza_item_openverse(b)
        for b in brutos
        if isinstance(b, dict) and (b.get("url") or "").strip()
    ]

    if not validar:
        return itens[:pedido]

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
    return vivos


def format_openverse(items: list, query: str, veio_de_fallback: bool = False) -> str:
    barra = "=" * 70
    linhas = []

    if not items:
        linhas.append(barra)
        linhas.append('  Nenhuma foto encontrada na Openverse para: "%s"' % query)
        linhas.append(barra)
        linhas.append("  Tente termos em ingles e mais concretos, ex: \"team meeting office\".")
        linhas.append("  Outras rotas sem chave: python3 assets-search.py --type sem-chave")
        linhas.append(barra)
        return "\n".join(linhas)

    linhas.append(barra)
    linhas.append('  %d fotos REAIS encontradas na Openverse para: "%s"' % (len(items), query))
    linhas.append("  Fonte sem chave de API. Licenca Creative Commons de uso comercial.")
    if veio_de_fallback:
        linhas.append("  (fallback automatico: sem foto vinda do Pexels, a busca veio daqui)")
    linhas.append(barra)
    linhas.append("")

    for i, item in enumerate(items, 1):
        dimensao = "%sx%s" % (item["largura"], item["altura"]) if item["largura"] else "dimensao nao informada"
        linhas.append("  %d. %s" % (i, item["titulo"]))
        linhas.append("     %s | Por: %s | Licenca: %s" % (dimensao, item["autor"], item["licenca"]))
        linhas.append("     Imagem:  %s" % item["url"])
        if item["thumbnail"]:
            linhas.append("     Thumb:   %s" % item["thumbnail"])
        if item["pagina_origem"]:
            linhas.append("     Origem:  %s" % item["pagina_origem"])
        if item["licenca_url"]:
            linhas.append("     Licenca: %s" % item["licenca_url"])
        linhas.append("")
        linhas.append("     CREDITO %s:" % ("OBRIGATORIO" if item["exige_credito"] else "recomendado"))
        linhas.append("     %s" % item["credito"])
        if "-ND" in item["licenca"].upper():
            linhas.append("     ATENCAO ND: nao pode recortar, filtrar nem sobrepor texto nessa foto.")
        linhas.append("")
        linhas.append("     USO RAPIDO (ja com o credito junto da imagem):")
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
    linhas.append("  ATRIBUICAO: em licenca CC BY, CC BY-SA e CC BY-ND o credito e OBRIGATORIO.")
    linhas.append("  Nao e cortesia, e condicao da licenca. Sem credito o uso e irregular.")
    linhas.append("  Onde por: legenda da foto, ou uma secao 'Creditos' no rodape da pagina.")
    linhas.append("  Modelo pronto e o que NAO fazer: references/assets-sem-chave.md")
    linhas.append("")
    linhas.append("  Baixe e otimize antes de publicar (hotlink de terceiro cai):")
    linhas.append("    # o -A e obrigatorio: alguns CDNs devolvem 403 pro curl pelado")
    linhas.append("    curl -L -A \"Mozilla/5.0\" -o public/img/hero.jpg \"<url da imagem>\"")
    linhas.append("    file public/img/hero.jpg   # confirme que veio imagem, nao HTML de erro")
    linhas.append("    Converta pra WebP | Hero < 200KB | Secoes < 100KB")
    linhas.append(barra)
    return "\n".join(linhas)


def print_aviso_fallback_openverse(motivo: str) -> None:
    print(
        "\n".join(
            [
                "",
                "  AVISO: caindo na Openverse (%s)." % motivo,
                "  A Openverse devolve FOTO REAL sem nenhuma chave de API.",
                "  Contrapartida: a licenca Creative Commons exige creditar o autor.",
                "  O credito de cada foto ja vem pronto na saida abaixo.",
                "  Detalhes: references/assets-sem-chave.md",
                "",
            ]
        ),
        file=sys.stderr,
    )


def buscar_fotos_com_fallback(query: str, limit: int = 6, orientation: str = "landscape") -> dict:
    """Busca fotos e NUNCA volta vazia por falta de chave.

    Com PEXELS_API_KEY: usa o Pexels (sem obrigacao de credito).
    Sem chave, ou com chave que nao achou nada: cai na Openverse.

    Devolve {"fonte": "pexels" | "openverse", "itens": [...]}.
    """
    tem_chave = bool(os.environ.get("PEXELS_API_KEY", "").strip())

    if tem_chave:
        itens = search_photos(query, limit=limit, orientation=orientation)
        if itens:
            return {"fonte": "pexels", "itens": itens}
        print_aviso_fallback_openverse(
            "o Pexels nao devolveu foto: chave invalida ou busca sem resultado"
        )
    else:
        print_aviso_fallback_openverse("PEXELS_API_KEY nao esta configurada")

    return {
        "fonte": "openverse",
        "itens": search_openverse(query, limit=limit, orientation=orientation),
    }


# ─── ROTAS SEM NENHUMA CHAVE ─────────────────────────────────────────────────

def show_sem_chave_resources() -> str:
    barra = "=" * 70
    linhas = []
    linhas.append(barra)
    linhas.append("  ASSETS SEM NENHUMA API KEY")
    linhas.append("  Nenhuma pagina precisa sair com retangulo cinza vazio.")
    linhas.append(barra)
    linhas.append("")

    linhas.append("  1. OPENVERSE: fotos reais, licenca Creative Commons (a melhor rota)")
    linhas.append("     python3 assets-search.py \"team meeting office\" --type openverse -n 6")
    linhas.append("     python3 assets-search.py \"sua busca\" --type photo   # cai aqui sozinho")
    linhas.append("     Credito ao autor OBRIGATORIO (CC BY / BY-SA). Sai pronto na busca.")
    linhas.append("")

    linhas.append("  2. PICSUM: JPEG real, sem tema, otimo pra mockup e placeholder")
    linhas.append("     %s/1600/900          # aleatorio" % PICSUM_URL)
    linhas.append("     %s/seed/hero/1600/900 # estavel (mesma foto sempre)" % PICSUM_URL)
    linhas.append("     %s/1600/900?grayscale&blur=2" % PICSUM_URL)
    linhas.append("     Nao use como foto de verdade do cliente: e foto generica.")
    linhas.append("")

    linhas.append("  3. UNDRAW: ilustracoes SVG tematicas, cor customizavel")
    linhas.append("     https://undraw.co/illustrations")
    linhas.append("     python3 assets-search.py --type illustrations \"team work\"")
    linhas.append("     Sem obrigacao de credito. Boas pra secao de features e vazio de dados.")
    linhas.append("")

    linhas.append("  4. GRADIENTE E PATTERN SVG (background, nunca sozinho como 'imagem')")
    linhas.append("     python3 assets-search.py --type backgrounds")
    linhas.append("")

    linhas.append(barra)
    linhas.append("  REGRA: pagina so com texto, gradiente e SVG generico REPROVA na")
    linhas.append("  auditoria visual da skill. Coloque foto real ou mockup de produto.")
    linhas.append("  Nunca use imagem de licenca desconhecida em pagina de cliente.")
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

    lines.append("  INSTALACAO:")
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
    lines.append("  ILUSTRACOES SVG: Fontes Gratuitas")
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

    lines.append("  USO RAPIDO em JSX:")
    lines.append("""  // SVG inline (melhor para animacoes CSS)
  import HeroIllustration from '@/public/illustrations/hero.svg'
  <Image src={HeroIllustration} alt="Hero" className="w-full max-w-lg" />

  // Com next/image (otimizado)
  import Image from 'next/image'
  <Image src="/illustrations/team.svg" alt="Team" width={500} height={400} />

  // Framer Motion na ilustracao
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
    lines.append("  ICONES ANIMADOS: Fontes e Integracao")
    lines.append(f"{'='*70}\n")

    lines.append("  LORDICON (icones animados Lottie, gratuitos):")
    lines.append("  Browse:  https://lordicon.com/icons")
    lines.append("  Estilo:  Flat, Outline, Lineal, Gradient")
    lines.append("  npm install lord-icon-element\n")

    lines.append("""  USO LordIcon:
  // No component (carregar script uma vez no layout)
  import Script from 'next/script'
  <Script src="https://cdn.lordicon.com/lordicon.js" />

  // Icone animado (trigger: hover, click, loop, morph)
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
    lines.append("  LUCIDE REACT (ja incluso no shadcn/ui):")
    lines.append("""  import { Zap, Shield, Globe } from 'lucide-react'
  <Zap className="w-8 h-8 text-indigo-500" />

  // Com animacao hover no container pai
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


# ─── NO API KEY ───────────────────────────────────────────────────────────────

def print_no_api_key(com_saida_alternativa: bool = True):
    linhas = [
        "",
        "  PEXELS_API_KEY nao encontrada.",
        "",
        "  O Pexels e opcional. Ele so evita a obrigacao de creditar o autor.",
        "  Chave gratuita (200 req/hora): https://www.pexels.com/api/",
        "  Depois de pegar a chave:",
        "",
        '      export PEXELS_API_KEY="sua-chave-aqui"',
        "",
    ]
    if com_saida_alternativa:
        linhas += [
            "  SEM CHAVE VOCE AINDA TEM FOTO REAL:",
            '      python3 assets-search.py "sua busca" --type openverse',
            "      python3 assets-search.py --type sem-chave",
            "",
            "  A Openverse devolve fotos reais com licenca Creative Commons.",
            "  Nesse caso creditar o autor NAO e opcional.",
            "  Modelo de credito pronto: references/assets-sem-chave.md",
            "",
        ]
    print("\n".join(linhas), file=sys.stderr)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Busca assets visuais: videos, fotos, Lottie, ilustracoes, icones, backgrounds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tipos disponiveis:
  video        Busca videos no Pexels (padrao): requer PEXELS_API_KEY
  photo        Busca fotos: usa Pexels se houver chave, senao CAI NA OPENVERSE
  openverse    Fotos reais com licenca Creative Commons, SEM chave (alias: cc)
  sem-chave    Lista todas as rotas que funcionam sem nenhuma API key
  lottie       Lista fontes e como usar animacoes Lottie
  illustrations Lista fontes e como usar ilustracoes SVG
  icons        Lista fontes e como usar icones animados
  backgrounds  Lista geradores de backgrounds SVG/patterns

Exemplos:
  python3 assets-search.py "dark abstract"
  python3 assets-search.py tech-dark
  python3 assets-search.py "minimal white" --type video --orientation landscape
  python3 assets-search.py "office team" --type photo -n 5
  python3 assets-search.py "team meeting office" --type openverse -n 5
  python3 assets-search.py --type sem-chave
  python3 assets-search.py "loading" --type lottie
  python3 assets-search.py --type illustrations "team work"
  python3 assets-search.py --type backgrounds
  python3 assets-search.py --presets
        """
    )
    parser.add_argument("query", nargs="?", default="", help="Termo de busca ou preset")
    parser.add_argument("--type", "-t",
        choices=["video", "photo", "openverse", "cc", "sem-chave",
                 "lottie", "illustrations", "icons", "backgrounds"],
        default="video",
        help="Tipo de asset (default: video)"
    )
    parser.add_argument("-n", "--limit", type=int, default=6, help="Numero de resultados (default: 6)")
    parser.add_argument("--orientation",
        choices=["landscape", "portrait", "square"],
        default="landscape",
        help="Orientacao do video/foto (default: landscape)"
    )
    parser.add_argument("--presets", action="store_true", help="Listar todos os presets de video")

    args = parser.parse_args()

    if args.presets:
        print("\nPresets de video disponiveis:\n")
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
        parser.error("Informe uma query ou preset. Use --presets para ver opcoes.")

    # Resolver preset
    query = PRESET_QUERIES.get(args.query, args.query)

    if args.type == "video":
        items = search_videos(query, limit=args.limit, orientation=args.orientation)
        print(format_videos(items, query))
    elif args.type in ("openverse", "cc"):
        items = search_openverse(query, limit=args.limit, orientation=args.orientation)
        print(format_openverse(items, query))
    elif args.type == "photo":
        resultado = buscar_fotos_com_fallback(
            query, limit=args.limit, orientation=args.orientation
        )
        if resultado["fonte"] == "openverse":
            print(format_openverse(resultado["itens"], query, veio_de_fallback=True))
        else:
            print(format_photos(resultado["itens"], query))


if __name__ == "__main__":
    main()
