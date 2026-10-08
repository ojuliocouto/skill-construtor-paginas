#!/usr/bin/env python3
"""Gate da pasta de publicação: reprova se a pasta que vai para o ar carrega a casa junto.

Por que existe (02/10/2026, auditoria da v3): a pasta da página tinha 94 arquivos e 18 MB, dos
quais 17 eram entrega. Iam para o ar prints de 10 sites de terceiros, o briefing com as
pendências da cliente, a folha de contato, as fotos de origem, os gates e os JSON de auditoria.

Reprova (exit 1) se a pasta:
  - não existe ou não tem index.html;
  - tem pasta de trabalho (referencias, evidencias, prova, prova-hero, gates, relatorios,
    _descartadas, auditoria, node_modules);
  - tem .md, .json de auditoria (só manifest.json e *.webmanifest passam), briefing, Lighthouse,
    arquivo de ponto (.wave-auditoria.json, .DS_Store), fonte de build (tailwind.config.js,
    package.json, _input.css) ou arquivo começando com "_" (exceto _headers, _redirects e
    _routes.json, que a hospedagem lê);
  - tem QUALQUER arquivo que a página não referencia (é assim que print de terceiro, foto de
    origem e folha de contato aparecem, com qualquer nome);
  - (auditoria da v5, 03/10/2026) tem comentário interno no HTML publicado: <!-- -->, // ou
    /* */ dentro de <script> e /* */ dentro de <style>. Só o aviso de licença /*! ... */ passa.
    A v5 publicou "na v4, um setTimeout de 3 s..." e o nome do gate num comentário do script;
  - (auditoria da v5) com plano-visual.md ao lado da dist/, favicon e ícone de tela inicial que
    não saíram do SVG da identidade atual: o plano declara "Ícone do site: <motivo>", o
    `icones/icone.svg` tem o mesmo data-motivo, a página desenha esse motivo (algum
    data-desenho o cita) e o `icones/icones.json` gravado por scripts/gerar-icones.mjs tem o
    sha256 do SVG atual e dos PNG publicados. A v5 publicou o prumo da v3 (md5 igual) numa
    página que já desenhava a coluna vertebral.

Uso: node scripts/py.mjs gate-publicacao.py --dist <dir-do-projeto>/dist
"""
import argparse
import hashlib
import html as html_mod
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lancador import comando  # noqa: E402

PASTAS_DE_TRABALHO = {"referencias", "evidencias", "prova", "prova-hero", "gates", "relatorios",
                      "_descartadas", "auditoria", "node_modules", ".git"}
FONTES_DE_BUILD = {"tailwind.config.js", "package.json", "package-lock.json", "postcss.config.js"}
PERMITIDOS_COM_SUBLINHADO = {"_headers", "_redirects", "_routes.json"}
JSON_PERMITIDOS = {"manifest.json"}


def coletor():
    spec = importlib.util.spec_from_file_location("montar_dist", Path(__file__).with_name("montar-dist.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _norm(t):
    t = unicodedata.normalize("NFKD", str(t or "").lower())
    return " ".join("".join(c for c in t if not unicodedata.combining(c)).split())


def comentarios_internos(pagina):
    """Comentários que vão para o ar no HTML: <!-- -->, e // ou /* */ em <script> e <style>."""
    achados = []
    for m in re.finditer(r"<!--(.*?)-->", pagina, re.S):
        achados.append(("HTML", m.group(1)))
    for tag, miolo in re.findall(r"(?is)<(script|style)\b[^>]*>(.*?)</\1>", pagina):
        for m in re.finditer(r"/\*(?!!)(.*?)\*/", miolo, re.S):
            achados.append((tag, m.group(1)))
        if tag.lower() == "script":
            sem_textos = re.sub(r"(['\"`])(?:\\.|(?!\1).)*\1", "''", miolo)
            for m in re.finditer(r"(?m)(?:^|[\s;{}()])//(.*)$", sem_textos):
                achados.append(("script", m.group(1)))
    return [f"comentário interno no {onde} publicado: \"{' '.join(t.split())[:90]}\" (página pública não expõe a casa; tire do arquivo que vai para o ar)"
            for onde, t in achados if t.strip()]


def icones_coerentes(dist, pagina):
    """Favicon e ícone de tela inicial gerados do SVG da identidade atual (só com plano ao lado)."""
    projeto = dist.parent
    plano = projeto / "plano-visual.md"
    if not plano.is_file():
        return []
    m = re.search(r"(?im)^\W*[ií]cone do site\W*:\s*(.+)$", plano.read_text(encoding="utf-8-sig"))
    if not m:
        return ["plano-visual.md não declara \"Ícone do site: <motivo>\": o favicon é a identidade em 32 px e precisa ser decidido no plano"]
    motivo = m.group(1).strip().strip("*`. ")
    problemas = []
    svg = projeto / "icones" / "icone.svg"
    reg_arq = projeto / "icones" / "icones.json"
    if not svg.is_file() or not reg_arq.is_file():
        return [f"favicon sem origem na identidade atual: falta icones/icone.svg ou icones/icones.json; desenhe o motivo \"{motivo}\" em icones/icone.svg e gere os PNG com {comando('gerar-icones.mjs')}"]
    try:
        reg = json.loads(reg_arq.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return [f"icones/icones.json ilegível: gere de novo com {comando('gerar-icones.mjs')}"]
    mm = re.search(r'data-motivo="([^"]+)"', svg.read_text(encoding="utf-8-sig"))
    if not mm or _norm(mm.group(1)) != _norm(motivo):
        problemas.append(f"icones/icone.svg sem data-motivo=\"{motivo}\" (o motivo que o plano declara)")
    if _norm(reg.get("motivo")) != _norm(motivo):
        problemas.append(f"icones/icones.json gerado para \"{reg.get('motivo')}\", o plano declara \"{motivo}\": gere de novo")
    if reg.get("svg_sha256") != hashlib.sha256(svg.read_bytes()).hexdigest():
        problemas.append(f"icones/icone.svg mudou depois de gerar os PNG: rode {comando('gerar-icones.mjs')} de novo")
    desenhos = " | ".join(_norm(html_mod.unescape(d)) for d in re.findall(r'data-desenho="([^"]+)"', pagina))
    if _norm(motivo) not in desenhos:
        problemas.append(f"o ícone do site desenha \"{motivo}\", que a página não desenha em nenhum data-desenho: o favicon tem de ser a identidade atual, não a de uma versão anterior")
    for nome, sha in (reg.get("arquivos") or {}).items():
        alvo = dist / nome
        if alvo.is_file() and hashlib.sha256(alvo.read_bytes()).hexdigest() != sha:
            problemas.append(f"{nome} publicado não é o que {comando('gerar-icones.mjs')} gerou do icone.svg atual (cópia de outra versão?)")
    for ref in re.findall(r'<link[^>]+rel="(?:icon|apple-touch-icon)"[^>]*href="([^"]+)"', pagina):
        nome = ref.split("?")[0].lstrip("/")
        if nome not in (reg.get("arquivos") or {}):
            problemas.append(f"{nome} referenciado na página sem registro em icones/icones.json")
    return problemas


def checar(dist):
    dist = Path(dist).resolve()
    if not dist.is_dir():
        return [f"a pasta de publicação {dist} não existe: monte com {comando('montar-dist.py')}"]
    if not (dist / "index.html").is_file():
        return [f"{dist} não tem index.html"]
    problemas = []
    usados = coletor().referenciados(dist)
    for p in sorted(dist.rglob("*")):
        rel = p.relative_to(dist)
        partes = set(rel.parts)
        if p.is_dir():
            if p.name in PASTAS_DE_TRABALHO:
                problemas.append(f"pasta de trabalho na publicação: {rel}/")
            continue
        if partes & PASTAS_DE_TRABALHO:
            problemas.append(f"{rel}: dentro de pasta de trabalho")
            continue
        nome = p.name.lower()
        motivo = None
        if nome.startswith("."):
            motivo = "arquivo de ponto (registro local)"
        elif nome.startswith("_") and p.name not in PERMITIDOS_COM_SUBLINHADO:
            motivo = "arquivo de origem ou de build (começa com _)"
        elif nome in FONTES_DE_BUILD:
            motivo = "fonte de build"
        elif nome.endswith(".md"):
            motivo = "documento interno (.md)"
        elif nome.endswith(".json") and nome not in JSON_PERMITIDOS:
            motivo = "JSON de auditoria ou de trabalho (.json)"
        elif "briefing" in nome or "lighthouse" in nome:
            motivo = "briefing ou relatório"
        elif rel.as_posix() not in usados:
            motivo = "a página não usa este arquivo (print, origem, folha de contato ou sobra)"
        if motivo:
            problemas.append(f"{rel}: {motivo}")
    pagina = (dist / "index.html").read_text(encoding="utf-8-sig")
    problemas += comentarios_internos(pagina)
    problemas += icones_coerentes(dist, pagina)
    return problemas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dist", required=True)
    a = ap.parse_args(argv)
    problemas = checar(a.dist)
    print(f"\nGATE DA PASTA DE PUBLICAÇÃO  {a.dist}\n" + "=" * 76)
    if problemas:
        for p in problemas:
            print("  FALHA: " + p)
        print(f"\n  REPROVA: {len(problemas)} item(ns) que não são página. O deploy sai de dist/, montada")
        print(f"  por {comando('montar-dist.py')}, nunca da pasta do projeto.\n")
        return 1
    arquivos = [p for p in Path(a.dist).rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in arquivos)
    print(f"  PASSA: {len(arquivos)} arquivo(s), {total / 1024:.1f} KiB, todos usados pela página.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
