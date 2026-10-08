#!/usr/bin/env python3
"""Monta a prancha de prova de animação de cada seção e mede, no pixel, o quanto ela mudou.

Por que existe (04/10/2026). A v7 do estúdio só pôde afirmar "cada seção anima o próprio conteúdo"
porque cada seção ganhou uma prancha: 3 quadros de desktop em cima, 3 de celular embaixo, e embaixo
de cada linha a porcentagem de pixels que mudou entre os quadros. Foi o que separou a v7 da v6, em
que tudo entrava com o mesmo fade. Este script promove essa prova para a skill, sem nenhum caminho
fixo: os quadros vêm do `anim.mjs` e a lista de seções, de um JSON.

Entrada: `<pasta>/quadros/<nome>-desk-1..3.png` e `<nome>-mob-1..3.png` (início, meio e fim) e o
`secoes.json` (lista de {nome, titulo, tipo}; o tipo é o da coluna Animação do PLANO.md).
Saída: `<pasta>/<nome>.png` (a prancha) e `<pasta>/medidas.json`, lido pelo gate-animacao.py:
  {"limiar_nivel": 12, "secoes": [{"nome", "titulo", "tipo",
     "desk": {"ini_meio", "meio_fim", "ini_fim"}, "mob": {...}}]}
Um pixel "mudou" quando o cinza dele varia mais de 12 níveis (de 255) entre os dois quadros.

Uso: node scripts/py.mjs prancha.py --pasta <saida> --secoes <secoes.json> [--so <nome>] [--limiar 12]
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("faltam pillow e numpy: pip install pillow numpy", file=sys.stderr)
    sys.exit(2)

TELAS = (("desk", "desktop 1440", 620), ("mob", "celular 390", 300))
FONTES = ("/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf")


def fonte(tamanho):
    for f in FONTES:
        if Path(f).exists():
            return ImageFont.truetype(f, tamanho)
    return ImageFont.load_default()


def dif(a, b, limiar):
    """Percentual de pixels cujo cinza variou mais que `limiar` níveis."""
    if a.size != b.size:
        b = b.resize(a.size)
    x = np.asarray(a.convert("L"), dtype=np.int16)
    y = np.asarray(b.convert("L"), dtype=np.int16)
    return round(float((np.abs(x - y) > limiar).mean() * 100), 2)


def quadros_da_secao(pasta, nome):
    faltam, quadros = [], {}
    for tag, _, _ in TELAS:
        ims = []
        for i in (1, 2, 3):
            f = pasta / "quadros" / f"{nome}-{tag}-{i}.png"
            if f.is_file():
                ims.append(Image.open(f).convert("RGB"))
            else:
                faltam.append(f.name)
        quadros[tag] = ims
    return quadros, faltam


def montar(pasta, sec, quadros, medidas):
    f1, f2 = fonte(22), fonte(17)
    linhas = []
    for tag, _, larg in TELAS:
        linhas.append((tag, [im.resize((larg, max(1, round(im.height * larg / im.width)))) for im in quadros[tag]]))
    W = 3 * 620 + 4 * 24
    H = 70 + max(i.height for i in linhas[0][1]) + 60 + max(i.height for i in linhas[1][1]) + 80
    prancha = Image.new("RGB", (W, H), "#F4F4F4")
    d = ImageDraw.Draw(prancha)
    d.text((24, 20), f"{sec.get('titulo') or sec['nome']}  |  animação: {sec.get('tipo') or 'não declarada'}", fill="#222222", font=f1)
    y = 70
    rotulos = ("início", "meio", "fim")
    for tag, ims in linhas:
        nome_tela = next(n for t, n, _ in TELAS if t == tag)
        x = (W - (sum(i.width for i in ims) + 2 * 24)) // 2
        for k, im in enumerate(ims):
            prancha.paste(im, (x, y))
            d.rectangle((x - 1, y - 1, x + im.width, y + im.height), outline="#888888")
            d.text((x, y + im.height + 6), f"{nome_tela}: {rotulos[k]}", fill="#444444", font=f2)
            x += im.width + 24
        m = medidas[tag]
        d.text((24, y + ims[0].height + 30),
               f"pixels que mudaram: início->meio {m['ini_meio']:.1f}%, meio->fim {m['meio_fim']:.1f}%, início->fim {m['ini_fim']:.1f}%",
               fill="#222222", font=f2)
        y += ims[0].height + 70
    saida = pasta / f"{sec['nome']}.png"
    prancha.save(saida)
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pasta", required=True, help="a mesma --saida do anim.mjs")
    ap.add_argument("--secoes", required=True, help="seções.json (nome, título, tipo)")
    ap.add_argument("--so", help="refaz só esta seção e mantém as outras do medidas.json")
    ap.add_argument("--limiar", type=int, default=12, help="níveis de cinza (de 255) para um pixel contar como mudado")
    a = ap.parse_args()
    pasta = Path(a.pasta)
    secoes = json.loads(Path(a.secoes).read_text(encoding="utf-8-sig"))
    destino = pasta / "medidas.json"
    atuais = {}
    if a.so and destino.is_file():
        atuais = {s["nome"]: s for s in json.loads(destino.read_text(encoding="utf-8-sig"))["secoes"]}
    erros = []
    for sec in secoes:
        if a.so and sec["nome"] != a.so:
            continue
        quadros, faltam = quadros_da_secao(pasta, sec["nome"])
        if faltam:
            erros.append(f"{sec['nome']}: faltam os quadros {', '.join(faltam)} (rode anim.mjs)")
            continue
        medidas = {}
        for tag, _, _ in TELAS:
            q = quadros[tag]
            medidas[tag] = {"ini_meio": dif(q[0], q[1], a.limiar), "meio_fim": dif(q[1], q[2], a.limiar), "ini_fim": dif(q[0], q[2], a.limiar)}
        saida = montar(pasta, sec, quadros, medidas)
        atuais[sec["nome"]] = {"nome": sec["nome"], "titulo": sec.get("titulo") or sec["nome"], "tipo": sec.get("tipo", ""), **medidas}
        print(f"{saida.name}: desktop {medidas['desk']['ini_fim']}%  celular {medidas['mob']['ini_fim']}%  (início->fim)")
    ordem = [s["nome"] for s in secoes]
    lista = [atuais[n] for n in ordem if n in atuais]
    destino.write_text(json.dumps({"limiar_nivel": a.limiar, "secoes": lista}, ensure_ascii=False, indent=2), encoding="utf-8")
    if erros:
        for e in erros:
            print("FALHA: " + e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
