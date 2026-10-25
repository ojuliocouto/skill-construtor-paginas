#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LENTE CURTA DE GOSTO NO HERÓI: prancha e briefing para um olhar independente de 5 minutos.

Por que existe (auditoria de 25/10/2026). O veredito de gosto chegava depois de 2 a 3 horas, no
auditor do passo g, quando a própria regra da skill já não deixa reconstruir. A página de produção
com 22 filetes, o mesmo traço em 9 de 10 títulos e nenhuma pessoa no topo saiu "bonito" no fim. A
autoavaliação do herói (passo e.1) falha: a skill mediu 7,78 na autoavaliação contra 5,5 do
auditor independente. Esta lente põe o veredito no ponto barato: o herói pronto, o resto ainda não.

O script NÃO julga. Ele monta UMA imagem (as 2 referências mais fortes em cima, o herói em 1440 e
em 390 embaixo, na mesma escala) e o briefing com orçamento, perguntas e schema de retorno. Quem
julga é um subagente que não construiu a página (references/auditores.md, "Lente curta do herói").

Uso:
    node scripts/py.mjs gosto-heroi.py --projeto <dir> --heroi <dobra-1440.png> [--celular <dobra-390.png>]
         [--refs <ref1-dobra.png>,<ref2-dobra.png>] [--saida <pasta>]

Sem --refs, usa as duas primeiras capturas "*-dobra.png" de <dir>/referencias/ em ordem de nome.
Sem --saida, grava em <dir>/auditoria/gosto-heroi/. Saída 0 com os caminhos; 2 sem Pillow ou sem imagem.
"""
import argparse
import importlib.util
import pathlib
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    print(f"precisa do Pillow: \"{sys.executable}\" -m pip install Pillow", file=sys.stderr)
    sys.exit(2)

AQUI = pathlib.Path(__file__).resolve().parent
LARGURA = 720            # cada quadro de desktop: 1440 em meia escala
ALTURA = 450             # a dobra de 1440x900 em meia escala
FAIXA = 40
ORCAMENTO_MIN = 5
ORCAMENTO_CHAMADAS = 6


def _fonte():
    spec = importlib.util.spec_from_file_location("lado_a_lado", AQUI / "lado-a-lado.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.fonte


def quadro(caminho, largura, altura):
    """Cabe a imagem em largura x altura pela largura e corta embaixo: a dobra é o que importa."""
    img = Image.open(caminho).convert("RGB")
    escala = largura / img.width
    img = img.resize((largura, max(1, round(img.height * escala))))
    if img.height < altura:
        fundo = Image.new("RGB", (largura, altura), (240, 240, 240))
        fundo.paste(img, (0, 0))
        return fundo
    return img.crop((0, 0, largura, altura))


def montar(refs, heroi, celular, destino):
    fonte = _fonte()(22)
    largura_cel = round(ALTURA * 390 / 844)
    total = LARGURA * 2 + 30
    altura = (ALTURA + FAIXA) * 2 + 30
    prancha = Image.new("RGB", (total, altura), (255, 255, 255))
    d = ImageDraw.Draw(prancha)
    linha = [(refs[0], f"Referência 1: {refs[0].stem}"), (refs[1], f"Referência 2: {refs[1].stem}")]
    for i, (img, rot) in enumerate(linha):
        x = i * (LARGURA + 30)
        d.text((x + 8, 8), rot[:60], fill=(0, 0, 0), font=fonte)
        prancha.paste(quadro(img, LARGURA, ALTURA), (x, FAIXA))
    y = ALTURA + FAIXA + 30
    d.text((8, y + 8), "Nosso herói, 1440", fill=(0, 0, 0), font=fonte)
    prancha.paste(quadro(heroi, LARGURA, ALTURA), (0, y + FAIXA))
    if celular:
        x = LARGURA + 30
        d.text((x + 8, y + 8), "Nosso herói, 390", fill=(0, 0, 0), font=fonte)
        prancha.paste(quadro(celular, largura_cel, ALTURA), (x, y + FAIXA))
    destino.parent.mkdir(parents=True, exist_ok=True)
    prancha.save(destino, quality=88)
    return prancha.size


BRIEFING = """# Lente curta de gosto no herói

Você NÃO construiu esta página. Olhe uma imagem só e responda.
Orçamento: {minutos} minutos e até {chamadas} chamadas de ferramenta. Não capture nada, não abra a página, não leia o código.

Imagem: `{prancha}`
Em cima, as 2 referências mais fortes do projeto. Embaixo, o herói da nossa página em 1440 e em 390.
Público do briefing: {publico}

Critério: `{dir_skill}/references/anti-vibe-coding.md` (tells V1 a V20) e os três visuais padrão de IA:
creme com serifa e terracota; quase preto com um acento ácido; "jornal de filetes".

Responda nesta ordem:
1. Que tells V1 a V20 aparecem no herói? Cite o número e o que você viu.
2. Eixo por eixo contra as referências (composição, tipografia, imagem, acabamento): "no nível" ou "abaixo", com o porquê.
3. Há gente do público no topo? Se o público é de pessoas e não há, diga.
4. Um designer exigente poria este herói na mesma pasta das referências?
5. O herói é bonito, só correto ou genérico (cara de template)?
6. A UMA mudança que mais sobe o herói, concreta (o que sai, o que entra).

Devolva só este JSON:
{{"gosto": "bonito|correto|generico", "tells": ["V18: ..."], "eixos_abaixo": ["composicao"],
  "gente_no_topo": true, "mesma_pasta": false, "uma_mudanca": "...", "duracao_min": 0, "chamadas": 0}}

Regra de uso (para quem lançou): "correto" ou "generico" = corrigir o HERÓI agora, antes de construir as
outras seções, e rodar esta lente uma vez mais. Ela não manda reconstruir a página: o resto ainda não existe.
"""


def main():
    ap = argparse.ArgumentParser(description="Prancha e briefing da lente curta de gosto no herói.")
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--heroi", required=True, help="print da dobra em 1440")
    ap.add_argument("--celular", help="print da dobra em 390")
    ap.add_argument("--refs", help="duas capturas de referência, separadas por vírgula")
    ap.add_argument("--saida", help="pasta de saída (padrão: <projeto>/auditoria/gosto-heroi)")
    ap.add_argument("--publico", help="público do briefing (padrão: lido de evidencias/briefing.md)")
    a = ap.parse_args()
    projeto = pathlib.Path(a.projeto)
    if a.refs:
        refs = [pathlib.Path(r.strip()) for r in a.refs.split(",") if r.strip()]
    else:
        refs = sorted((projeto / "referencias").glob("*-dobra.png"))[:2]
    if len(refs) < 2:
        print(f"faltam referências: preciso de 2 capturas de dobra (achei {len(refs)}). Passe --refs <a.png>,<b.png> "
              f"ou capture as referências no passo b.", file=sys.stderr)
        sys.exit(2)
    faltando = [str(p) for p in [*refs[:2], pathlib.Path(a.heroi), *( [pathlib.Path(a.celular)] if a.celular else [])] if not p.is_file()]
    if faltando:
        print("imagem não encontrada: " + ", ".join(faltando), file=sys.stderr)
        sys.exit(2)
    publico = a.publico
    if not publico:   # 1o o etapa-0.json (o mesmo que o gate-composicao lê), depois a linha "Para quem:" do briefing.md
        try:
            import json
            publico = json.loads((projeto / "evidencias" / "etapa-0.json").read_text(encoding="utf-8").lstrip("\ufeff"))["briefing"]["publico"]
        except (OSError, ValueError, KeyError, TypeError):
            publico = None
    if not publico:
        try:
            for linha in (projeto / "evidencias" / "briefing.md").read_text(encoding="utf-8").splitlines():
                if "para quem" in linha.lower() and ":" in linha:
                    publico = linha.split(":", 1)[1].strip(" *")
                    break
        except OSError:
            publico = None
    saida = pathlib.Path(a.saida) if a.saida else projeto / "auditoria" / "gosto-heroi"
    prancha = saida / "prancha.jpg"
    tamanho = montar(refs[:2], pathlib.Path(a.heroi), pathlib.Path(a.celular) if a.celular else None, prancha)
    briefing = saida / "briefing.md"
    briefing.write_text(BRIEFING.format(minutos=ORCAMENTO_MIN, chamadas=ORCAMENTO_CHAMADAS, prancha=prancha.resolve(),
                                        publico=publico or "não informado", dir_skill=AQUI.parent), encoding="utf-8")
    print(f"prancha: {prancha} ({tamanho[0]}x{tamanho[1]})")
    print(f"briefing: {briefing}")
    print(f"orçamento: {ORCAMENTO_MIN} min e até {ORCAMENTO_CHAMADAS} chamadas, 1 imagem")
    print("próximo passo: lance 1 subagente que não construiu a página com o conteúdo do briefing; "
          "grave a resposta em " + str(saida / "resultado.json"))


if __name__ == "__main__":
    main()
