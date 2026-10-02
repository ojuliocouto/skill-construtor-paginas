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
    origem e folha de contato aparecem, com qualquer nome).

Uso: python3 scripts/gate-publicacao.py --dist <dir-do-projeto>/dist
"""
import argparse
import importlib.util
import sys
from pathlib import Path

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


def checar(dist):
    dist = Path(dist).resolve()
    if not dist.is_dir():
        return [f"a pasta de publicação {dist} não existe: monte com scripts/montar-dist.py"]
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
        print("  por scripts/montar-dist.py, nunca da pasta do projeto.\n")
        return 1
    arquivos = [p for p in Path(a.dist).rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in arquivos)
    print(f"  PASSA: {len(arquivos)} arquivo(s), {total / 1024:.1f} KiB, todos usados pela página.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
