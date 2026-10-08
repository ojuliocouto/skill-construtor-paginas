#!/usr/bin/env python3
"""GATE DE ANIMAÇÃO: cada seção anima de verdade e cada uma anima o próprio conteúdo.

Por que existe (04/10/2026). O auditor deu à v6 nota 5,5 em movimento e à v7 nota 7,5. A v6 entrava
tudo com o mesmo fade; a v7 deu a cada seção uma animação ligada ao conteúdo (a foto abre, as vagas
se preenchem, as barras de horário crescem, a coluna se alinha com a rolagem) e provou com uma
prancha por seção. O gate-movimento mede a visita; ninguém media se a seção, vista de perto,
muda de fato nem se são todas a mesma animação.

Lê o `medidas.json` que o `prancha.py` grava (a % de pixels que mudou entre os quadros) e reprova:
  1. seção com menos de 2% dos pixels mudando entre o início e o fim, no desktop 1440 ou no
     celular 390 (a animação não aparece ou é só enfeite);
  2. mais de 2 seções com o mesmo TIPO de animação declarado (o tipo vem do `secoes.json`, que
     espelha a coluna Animação do PLANO.md); o tipo `assinatura` fica fora da conta, porque o
     momento assinatura aparece em 3 seções por regra do plano;
  3. seção sem tipo declarado;
  4. com `--plano`: menos pranchas que linhas na tabela Seção | Desktop | Celular | Animação.

Uso: node scripts/py.mjs gate-animacao.py --pasta <saida do anim.mjs> [--plano <dir>/PLANO.md] [--minimo 2]
"""
import argparse
import importlib.util
import json
import os
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lancador import comando  # noqa: E402

MINIMO_PADRAO = 2.0
MAXIMO_MESMO_TIPO = 2
AQUI = Path(__file__).resolve().parent


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower().strip()


def secoes_do_plano(caminho):
    spec = importlib.util.spec_from_file_location("gate_plano", AQUI / "gate-plano.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.linhas_da_composicao(Path(caminho).read_text(encoding="utf-8-sig")) or []


def avaliar(medidas, minimo=MINIMO_PADRAO, plano=None):
    problemas = []
    secoes = medidas.get("secoes", [])
    if not secoes:
        return ["medidas.json sem nenhuma seção: rode anim.mjs e prancha.py"], []
    tipos = {}
    for s in secoes:
        for chave, rotulo in (("desk", "desktop 1440"), ("mob", "celular 390")):
            v = s.get(chave, {}).get("ini_fim")
            if v is None:
                problemas.append(f"{s['nome']}: sem medida de {rotulo}")
            elif v < minimo:
                problemas.append(f"{s['nome']}: {rotulo}: só {v:.1f}% dos pixels mudam entre o início e o fim (mínimo {minimo:.1f}%): "
                                 "a animação não aparece nessa tela ou é só enfeite")
        tipo = (s.get("tipo") or "").strip()
        if not tipo:
            problemas.append(f"{s['nome']}: sem tipo de animação declarado (a coluna Animação do PLANO.md, antes dos dois pontos)")
        elif sem_acento(tipo) != "assinatura":
            tipos.setdefault(sem_acento(tipo), (tipo, []))[1].append(s["nome"])
    for chave, (tipo, nomes) in tipos.items():
        if len(nomes) > MAXIMO_MESMO_TIPO:
            problemas.append(f"{len(nomes)} seções com o mesmo tipo de animação ('{tipo}': {', '.join(nomes)}); "
                             f"no máximo {MAXIMO_MESMO_TIPO}: cada seção anima o próprio conteúdo")
    if plano is not None and len(plano) > len(secoes):
        problemas.append(f"o plano tem {len(plano)} seções na tabela de composição e só há {len(secoes)} pranchas: uma prancha por seção")
    return problemas, secoes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pasta", required=True)
    ap.add_argument("--plano")
    ap.add_argument("--minimo", type=float, default=MINIMO_PADRAO, help="% mínimo de pixels mudados entre início e fim")
    a = ap.parse_args()
    arq = Path(a.pasta) / "medidas.json"
    print("\nGATE DE ANIMAÇÃO  " + str(Path(a.pasta).resolve()))
    print("=" * 88)
    if not arq.is_file():
        print(f"  FALHA: falta {arq}: rode {comando('anim.mjs')} e depois {comando('prancha.py')}")
        print("\n  REPROVA: sem prova de animação.\n")
        return 1
    medidas = json.loads(arq.read_text(encoding="utf-8-sig"))
    plano = secoes_do_plano(a.plano) if a.plano else None
    problemas, secoes = avaliar(medidas, a.minimo, plano)
    print(f"{'seção':<22}{'desktop (início->fim)':<24}{'celular (início->fim)':<24}tipo")
    for s in secoes:
        d = s.get("desk", {}).get("ini_fim")
        m = s.get("mob", {}).get("ini_fim")
        print(f"{s['nome']:<22}{('%.1f%%' % d) if d is not None else '-':<24}{('%.1f%%' % m) if m is not None else '-':<24}{s.get('tipo') or '(sem tipo)'}")
    print("=" * 88)
    if problemas:
        for p in problemas:
            print("  FALHA: " + p)
        print(f"\n  REPROVA: {len(problemas)} problema(s) de animação.\n")
        return 1
    print(f"  PASSA: {len(secoes)} seções com pelo menos {a.minimo:.1f}% dos pixels mudando em 1440 e em 390, e nenhum tipo de animação em mais de {MAXIMO_MESMO_TIPO} seções.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
