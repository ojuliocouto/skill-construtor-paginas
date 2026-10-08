#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate de referências: sem pelo menos 6 prints REAIS lidos, o plano visual não começa.

Por que existe (v3, 02/10/2026). A página do aluno passou em todos os gates mecânicos e
mesmo assim saiu com cara de rascunho: a direção visual veio de um banco de CSV e de
memória, nunca de página de verdade. Decisão do dono: a skill depende de três coisas, a
`frontend-design`, os auditores e a pesquisa de referências reais. Este gate cobra a terceira.

O que conta como referência válida, uma por uma:
  - URL http(s) única (a mesma página duas vezes conta uma vez só)
  - tipo "mesmo-negocio" (página real do mesmo tipo de negócio) ou "design" (referência
    de design de alto nível); o conjunto precisa ter pelo menos 2 de cada
  - dois prints dentro do projeto: a primeira dobra e uma seção do meio, PNG de verdade,
    com pelo menos 320x300, que não está em branco e que não é cópia de outro print
  - a leitura escrita: o que a página faz bem em composição, tipografia, imagem e ritmo
    (cada item com frase de verdade) e o PRINCÍPIO que se leva dela (nunca frase nem layout)
  - se veio de capturar-referencias.mjs, `captura.estado` precisa ser "ok" (bloqueada, quebrada
    ou coberta reprovam, com o motivo); página curta de verdade (altura_pagina até 910 px) pode
    ter o print do meio igual ao da dobra
  - "lido": true, marcado por quem abriu os dois PNGs com os próprios olhos

O gate não sabe se a leitura é boa. Ele garante que ela existe e que os prints são reais;
a lente "comparacao-referencias" dos auditores é quem cobra se a página ficou no nível.

Uso:
    node scripts/py.mjs gate-referencias.py --projeto <dir>
    node scripts/py.mjs gate-referencias.py --projeto <dir> --json
Formato do manifesto: references/pesquisa-de-referencias.md
"""
import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lancador import comando  # noqa: E402

MANIFESTO = Path("referencias") / "referencias.json"
MINIMO = 6
MINIMO_POR_TIPO = 2
TIPOS = ("mesmo-negocio", "design")
EIXOS = ("composicao", "tipografia", "imagem", "ritmo")
MIN_EIXO = 20
MIN_PRINCIPIO = 30
MIN_LARGURA, MIN_ALTURA = 320, 300
ALTURA_JANELA = 900


def ler_png(caminho):
    """Devolve (largura, altura, cores_distintas_na_amostra) ou levanta ValueError."""
    dados = caminho.read_bytes()
    if not dados.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("não é PNG")
    pos, largura, altura, idat = 8, None, None, []
    while pos + 8 <= len(dados):
        tam, tipo = struct.unpack(">I4s", dados[pos:pos + 8])
        corpo = dados[pos + 8:pos + 8 + tam]
        if tipo == b"IHDR":
            largura, altura = struct.unpack(">II", corpo[:8])
        elif tipo == b"IDAT":
            idat.append(corpo)
        elif tipo == b"IEND":
            break
        pos += 12 + tam
    if not largura or not idat:
        raise ValueError("PNG sem cabeçalho ou sem dados")
    try:
        bruto = zlib.decompressobj().decompress(b"".join(idat), 4_000_000)
    except zlib.error:
        raise ValueError("PNG corrompido")
    # Amostra espaçada do dado bruto: print em branco tem pouquíssimos valores distintos.
    passo = max(1, len(bruto) // 50_000)
    distintos = len(set(bruto[::passo]))
    return largura, altura, distintos


def conferir_print(projeto, rel, vistos, igual_permitido=None):
    if not rel or not isinstance(rel, str):
        return "print não informado"
    p = Path(rel)
    p = (projeto / p).resolve() if not p.is_absolute() else p.resolve()
    if not p.is_relative_to(projeto):
        return f"print fora do projeto ({rel})"
    if not p.is_file() or p.stat().st_size == 0:
        return f"print ausente ou vazio ({rel})"
    try:
        larg, alt, distintos = ler_png(p)
    except (ValueError, OSError) as e:
        return f"print inválido ({rel}): {e}"
    if larg < MIN_LARGURA or alt < MIN_ALTURA:
        return f"print pequeno demais ({rel}: {larg}x{alt})"
    if distintos < 12:
        return f"print em branco ou chapado ({rel})"
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h in vistos and vistos[h] != igual_permitido:
        return f"print repetido ({rel} é cópia de {vistos[h]})"
    vistos.setdefault(h, rel)
    return None


def conferir_referencia(projeto, ref, urls, vistos):
    """Devolve lista de problemas desta referência (vazia = válida)."""
    if not isinstance(ref, dict):
        return ["entrada que não é objeto"]
    problemas = []
    url = str(ref.get("url") or "").strip()
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.netloc:
        problemas.append("url precisa ser http(s) de uma página real")
    chave = url.rstrip("/").lower()
    if chave in urls:
        problemas.append("url repetida (a mesma página conta uma vez)")
    urls.add(chave)
    if ref.get("tipo") not in TIPOS:
        problemas.append(f"tipo precisa ser {' ou '.join(TIPOS)}")
    prints = ref.get("prints") if isinstance(ref.get("prints"), dict) else {}
    # Página curta de verdade (cabe numa janela de 900 px) tem o meio igual à dobra: não é cópia.
    altura = ref.get("altura_pagina")
    curta = isinstance(altura, (int, float)) and not isinstance(altura, bool) and 0 < altura <= ALTURA_JANELA + 10
    estado = (ref.get("captura") or {}).get("estado") if isinstance(ref.get("captura"), dict) else None
    if estado is not None and estado != "ok":
        motivo = str((ref.get("captura") or {}).get("motivo") or "").strip()
        problemas.append(f"captura {estado}" + (f" ({motivo})" if motivo else "") +
                         ": referência ruim, não conta; capture outra e tire esta com --limpar-ruins")
    for nome in ("dobra", "meio"):
        permitido = prints.get("dobra") if (nome == "meio" and curta) else None
        erro = conferir_print(projeto, prints.get(nome), vistos, permitido)
        if erro:
            problemas.append(f"{nome}: {erro}")
    faz_bem = ref.get("faz_bem") if isinstance(ref.get("faz_bem"), dict) else {}
    rasos = [e for e in EIXOS if len(str(faz_bem.get(e) or "").strip()) < MIN_EIXO]
    if rasos:
        problemas.append(f"leitura rasa ou ausente em: {', '.join(rasos)} (mínimo {MIN_EIXO} caracteres cada)")
    if len(str(ref.get("principio") or "").strip()) < MIN_PRINCIPIO:
        problemas.append(f"princípio ausente ou raso (mínimo {MIN_PRINCIPIO} caracteres)")
    if ref.get("lido") is not True:
        problemas.append('"lido" não está true: abra os dois PNGs antes de escrever a leitura')
    return problemas


def checar(projeto, minimo=MINIMO):
    """Devolve (validas, problemas_gerais). validas = lista de referências que passaram."""
    projeto = Path(projeto).resolve()
    alvo = projeto / MANIFESTO
    if not alvo.is_file():
        return [], [f"manifesto ausente: {MANIFESTO} (rode {comando('capturar-referencias.mjs')})"]
    try:
        doc = json.loads(alvo.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError) as e:
        return [], [f"manifesto ilegível: {e}"]
    refs = doc.get("referencias") if isinstance(doc, dict) else None
    if not isinstance(refs, list):
        return [], ['manifesto sem a lista "referencias"']
    urls, vistos, validas, gerais = set(), {}, [], []
    for i, ref in enumerate(refs, 1):
        erros = conferir_referencia(projeto, ref, urls, vistos)
        rotulo = (ref.get("url") if isinstance(ref, dict) else None) or f"#{i}"
        if erros:
            gerais.append(f"{rotulo}: " + "; ".join(erros))
        else:
            validas.append(ref)
    if len(validas) < minimo:
        gerais.append(f"{len(validas)} de {minimo} referências válidas")
    for tipo in TIPOS:
        n = sum(1 for r in validas if r.get("tipo") == tipo)
        if n < MINIMO_POR_TIPO:
            gerais.append(f"só {n} referência(s) válida(s) do tipo {tipo} (mínimo {MINIMO_POR_TIPO})")
    return validas, gerais


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", type=Path, required=True)
    ap.add_argument("--minimo", type=int, default=MINIMO)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.minimo < MINIMO:
        print(f"ERRO: o mínimo não desce de {MINIMO}. Menos referência é menos régua.", file=sys.stderr)
        return 2
    validas, problemas = checar(args.projeto, args.minimo)
    if args.json:
        print(json.dumps({"validas": len(validas), "problemas": problemas}, ensure_ascii=False, indent=2))
    else:
        print("\nGATE DE REFERÊNCIAS\n" + "=" * 72)
        for r in validas:
            print(f"  [ok   ] {r.get('tipo'):<13} {r.get('url')}")
        for p in problemas:
            print(f"  [FALTA] {p}")
        print("=" * 72)
        if problemas:
            print("  BLOQUEIA: sem 6 prints reais lidos (2 de cada tipo, no mínimo) o plano visual")
            print("  não começa. Capture mais páginas e escreva a leitura de cada uma.\n")
        else:
            print(f"  PASSA: {len(validas)} referências reais, com prints e leitura. Siga para o plano visual.\n")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
