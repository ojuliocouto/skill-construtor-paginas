#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta original e sua versao LADO A LADO, na mesma escala, numa imagem so.

Por que este script existe, e por que ele NAO e um medidor:

Em 26/08/2026 entreguei um "clone melhorado" e o dono respondeu: "a pagina ficou quase igual a
original. eu nao te pedi pra fazer uma melhora visual?". Ele estava certo: o que eu tinha feito
era higiene (trocar icone por foto, reorganizar grid, otimizar peso), nao design.

Minha primeira reacao foi escrever um medidor de distancia visual por pixel (ritmo de
luminancia, altura, peso claro/escuro). Ele FALHOU no teste de calibracao, e falhou feio: deu
27,3% para a versao REPROVADA pelo dono e 26,3% para a versao corrigida. Ou seja, apontou a
versao boa como MAIS parecida com a original. Diferenca de pixel nao mede o que o olho chama de
"cara de igual": isso mora em composicao, escala tipografica, sobreposicao e profundidade, e
nao em histograma.

Entao o medidor foi descartado, e no lugar ficou o que funciona de verdade: **por os dois lado
a lado e OLHAR**. Quem julga e o olho, com a pergunta honesta: "o dono veria a diferenca sem eu
apontar?". O gate de elevacao (SKILL.md, secao CLONAR + ELEVAR) cobra os EIXOS que mudaram,
nomeados um a um. Este script so entrega a imagem que torna a pergunta respondivel.

Uso:
    python3 scripts/lado-a-lado.py <png-original> <png-sua-versao> <saida.jpg> [--rotulos "Original,V2"]
"""
import argparse
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("precisa do Pillow: pip3 install --user Pillow", file=sys.stderr)
    sys.exit(2)

FAIXA = 46  # altura da tarja de rotulo


def fonte(tam):
    for c in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(c, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def prepara(caminho, largura):
    im = Image.open(caminho).convert("RGB")
    altura = max(1, round(im.height * (largura / im.width)))
    return im.resize((largura, altura), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("original")
    ap.add_argument("versao")
    ap.add_argument("saida")
    ap.add_argument("--largura", type=int, default=760, help="largura de cada coluna")
    ap.add_argument("--rotulos", default="ORIGINAL,SUA VERSAO")
    args = ap.parse_args()

    rot_a, _, rot_b = args.rotulos.partition(",")
    a = prepara(args.original, args.largura)
    b = prepara(args.versao, args.largura)

    # Mesma escala nas duas colunas: escalar so uma faria a comparacao mentir.
    altura = max(a.height, b.height)
    folha = Image.new("RGB", (args.largura * 2 + 24, altura + FAIXA), (243, 247, 243))
    folha.paste(a, (0, FAIXA))
    folha.paste(b, (args.largura + 24, FAIXA))

    d = ImageDraw.Draw(folha)
    d.rectangle([0, 0, folha.width, FAIXA], fill=(12, 30, 18))
    f = fonte(21)
    d.text((16, 13), rot_a.strip().upper(), font=f, fill=(255, 255, 255))
    d.text((args.largura + 40, 13), (rot_b or "SUA VERSAO").strip().upper(), font=f, fill=(95, 169, 71))

    folha.save(args.saida, quality=86)
    print(f"lado a lado: {args.saida}  ({folha.width}x{folha.height})")
    print("\nAgora OLHE, e responda com honestidade:")
    print("  1. o dono veria a diferenca sem voce apontar?")
    print("  2. quantos EIXOS de elevacao voce consegue nomear olhando? (composicao, escala,")
    print("     profundidade, movimento, densidade, elemento de assinatura)")
    print("  Se a resposta 1 for 'nao', nao adianta a lista da resposta 2.\n")


if __name__ == "__main__":
    sys.exit(main())
