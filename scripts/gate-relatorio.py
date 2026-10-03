"""GATE DO RELATÓRIO: o relatório do construtor só afirma medida que um gate gravou.

Por que existe (02/10/2026, auditoria da v4 do estúdio). O auditor independente achou 10
afirmações do relatório do construtor que não se sustentavam: "fatos alinhados à base da foto"
(53 px abaixo), "cards com títulos centralizados" (títulos a 147 px), "no máximo 2 linhas em
768" (os h3 quebravam), "gate-responsivo PASSA" sem medir o que foi afirmado, "3 links wa.me"
(eram 2) e "Lighthouse 100" com um JSON anterior à dist/ final. Frase de relatório escrita de
memória protege o defeito.

Regra: toda linha do relatório que traz um número de medida (px, %, s, ms, KiB, KB, MB, :1,
telas, Lighthouse N) cita, entre crases, o arquivo de texto que o gravou, e o número aparece
nesse arquivo. Com `--dist`, o arquivo citado não pode ser anterior à dist/ publicada. Limite de
regra ("até 15%", "máximo 4 px", "pelo menos 35%") não é medida e fica de fora.

Reprova (exit 1): medida sem arquivo citado; arquivo citado inexistente ou só imagem; número
que não está no arquivo citado; medida anterior à dist/.

Uso: python3 scripts/gate-relatorio.py --relatorio <md> [--base <dir>] [--dist <dir>/dist]
"""
import argparse
import re
import sys
from pathlib import Path

UNIDADE = r"(?:px|%|ms|s|KiB|KB|MB|:1|telas?)"
MEDIDA = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)\s?(" + UNIDADE + r")(?![\w])")
LIGHTHOUSE = re.compile(r"Lighthouse\D{0,40}?\b(\d{2,3})\b", re.I)
LIMITE = re.compile(r"(at[eé]|m[aá]ximo|m[ií]nimo|limite|pelo menos|a partir de|acima de|abaixo de|menos de|mais de|[±≤≥<>])\s*(de\s+)?$", re.I)
TEXTO = {".txt", ".json", ".md", ".log", ".csv", ".tsv"}


def variantes(num):
    a = num.replace(",", ".")
    vs = {num, a, a.replace(".", ",")}
    if "." in a:
        inteiro, dec = a.split(".")
        vs |= {f"{inteiro}.{dec}0", f"{inteiro},{dec}0"}
        if set(dec) == {"0"}:
            vs.add(inteiro)
    return vs


def citados(linha, base, rel_dir):
    saida = []
    for tok in re.findall(r"`([^`]+)`", linha):
        if not re.search(r"[/.]", tok) or " " in tok.strip():
            continue
        for raiz in (base, rel_dir):
            p = Path(tok) if Path(tok).is_absolute() else Path(raiz) / tok
            if p.is_file():
                saida.append(p)
                break
    return saida


def medidas(linha):
    out = []
    for m in MEDIDA.finditer(linha):
        if LIMITE.search(linha[max(0, m.start() - 16):m.start()]):
            continue
        out.append((m.group(1), m.group(2), m.group(0)))
    for m in LIGHTHOUSE.finditer(linha):
        out.append((m.group(1), "", f"Lighthouse {m.group(1)}"))
    return out


def checar(relatorio, base=None, dist=None):
    relatorio = Path(relatorio)
    base = Path(base) if base else relatorio.parent
    problemas = []
    fim_dist = None
    if dist and Path(dist).is_dir():
        tempos = [p.stat().st_mtime for p in Path(dist).rglob("*") if p.is_file()]
        fim_dist = max(tempos) if tempos else None
    em_codigo = False
    for n, linha in enumerate(relatorio.read_text(encoding="utf-8").splitlines(), 1):
        if linha.strip().startswith("```"):
            em_codigo = not em_codigo
            continue
        if em_codigo:
            continue
        ms = medidas(linha)
        if not ms:
            continue
        arquivos = citados(linha, base, relatorio.parent)
        textos = [p for p in arquivos if p.suffix.lower() in TEXTO]
        resumo = linha.strip()[:90]
        if not arquivos:
            problemas.append(f"linha {n}: afirma {', '.join(m[2] for m in ms[:3])} sem citar o arquivo de medida: \"{resumo}\"")
            continue
        if not textos:
            problemas.append(f"linha {n}: cita só imagem; o número vem do arquivo de texto que o gate gravou: \"{resumo}\"")
            continue
        conteudo = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in textos)
        for num, _, bruto in ms:
            if not any(v in conteudo for v in variantes(num)):
                problemas.append(f"linha {n}: {bruto} não aparece em {', '.join(p.name for p in textos)}: \"{resumo}\"")
        if fim_dist:
            for p in textos:
                if p.suffix.lower() == ".md":
                    continue  # texto de referência (auditoria, licenças), não arquivo de medida
                if p.stat().st_mtime + 1 < fim_dist and not p.is_relative_to(Path(dist)):
                    problemas.append(f"linha {n}: {p.name} é anterior à dist/ final; meça de novo a versão entregue")
    return problemas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--relatorio", required=True)
    ap.add_argument("--base", help="pasta contra a qual os caminhos citados se resolvem (padrão: a do relatório)")
    ap.add_argument("--dist", help="dist/ publicada: medida mais antiga que ela reprova")
    a = ap.parse_args()
    problemas = checar(a.relatorio, a.base, a.dist)
    print("\nGATE DO RELATÓRIO  " + str(Path(a.relatorio).resolve()))
    print("=" * 80)
    if problemas:
        for p in problemas:
            print("  FALHA: " + p)
        print(f"\n  REPROVA: {len(problemas)} afirmação(ões) de medida sem o arquivo que a gravou.\n")
        return 1
    print("  PASSA: toda medida do relatório cita o arquivo do gate e o número está nele.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
