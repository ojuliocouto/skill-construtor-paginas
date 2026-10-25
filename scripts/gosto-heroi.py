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

UMA RODADA SÓ (3.6.1). No teste de aluno da 3.6.0 a lente rodou duas vezes (9,3 e 7,9 min contra o teto de 5) e as duas
deram "generico" pelo mesmo motivo: a foto de banco, que só a cliente resolve. Agora: (1) o teto de 5 minutos e a rodada única
estão escritos no briefing do auditor; (2) o resultado com motivo que depende de material da cliente (foto real, logo,
depoimento) vira pendência registrada para a entrega e não manda rodar de novo; (3) o script RECUSA montar a lente uma
segunda vez depois que o resultado.json existe (saída 3).

Uso:
    node scripts/py.mjs gosto-heroi.py --projeto <dir> --heroi <dobra-1440.png> [--celular <dobra-390.png>]
         [--refs <ref1-dobra.png>,<ref2-dobra.png>] [--saida <pasta>]
    node scripts/py.mjs gosto-heroi.py --projeto <dir> --registrar [--saida <pasta>]   # lê o resultado.json do auditor

Sem --refs, usa as duas primeiras capturas "*-dobra.png" de <dir>/referencias/ em ordem de nome.
Sem --saida, grava em <dir>/auditoria/gosto-heroi/. Saída 0 com os caminhos; 2 sem Pillow, sem imagem ou com resultado
inválido; 3 quando a rodada única já foi usada.
"""
import argparse
import importlib.util
import json
import pathlib
import re
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

TETO DE {minutos} MINUTOS, DURO. Esta é a ÚNICA rodada da lente: não existe segunda.
No minuto {aviso}, pare de olhar e devolva o JSON com o que já viu. Passar de {minutos} minutos é falha da lente, não zelo.
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
7. O que dessa mudança depende de material que SÓ a cliente tem (foto real, logo, depoimento, autorização de imagem)?
   Liste em `depende_do_cliente`. Isso não é ajuste do herói: vira pendência da entrega. `uma_mudanca` traz só o que o
   construtor resolve sozinho, com o material que já existe.

Devolva só este JSON:
{{"gosto": "bonito|correto|generico", "tells": ["V18: ..."], "eixos_abaixo": ["composicao"],
  "gente_no_topo": true, "mesma_pasta": false, "uma_mudanca": "...", "depende_do_cliente": ["foto real da ..."],
  "duracao_min": 0, "chamadas": 0}}

Regra de uso (para quem lançou): a lente roda UMA vez. "correto" ou "generico" = aplicar `uma_mudanca` no HERÓI agora, antes de
construir as outras seções, SEM rodar a lente de novo. O que está em `depende_do_cliente` vira pendência registrada para a entrega
(`gosto-heroi.py --registrar` faz isso). A lente não manda reconstruir a página: o resto ainda não existe.
"""

# O que, no texto do auditor, só a cliente resolve: foto real, logo, depoimento, autorização de imagem. Serve de rede quando o
# auditor esquece o campo `depende_do_cliente`.
PADRAO_CLIENTE = re.compile(
    r"foto(?:s)? real|retrato(?:s)? real|imagem real|foto(?:s)? (?:da|do) (?:cliente|clínica|clinica|espaço|espaco|equipe)|"
    r"imagem(?:ns)? ilustrativa|foto(?:s)? (?:de|do) banco|banco de imagem|"
    r"logo (?:real|oficial|da cliente|do cliente|da clínica)|logotipo (?:real|oficial|da cliente|do cliente)|"
    r"depoimento(?:s)? (?:real|reais|verdadeiro)|material (?:real )?d[ao] cliente|autoriza[cç][aã]o de imagem",
    re.IGNORECASE)
GOSTOS_VALIDOS = ("bonito", "correto", "generico")


def _estado(saida):
    return saida / "resultado.json"


def registrar(saida, projeto):
    """Lê o resultado.json do auditor, separa o que depende da cliente (pendência) do que o construtor aplica, e fecha a lente."""
    arq = _estado(saida)
    if not arq.is_file():
        print(f"sem resultado.json em {saida}: grave a resposta do auditor em {arq} antes de registrar.", file=sys.stderr)
        return 2
    try:
        r = json.loads(arq.read_text(encoding="utf-8").lstrip("\ufeff"))
    except ValueError as e:
        print(f"resultado.json não é JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(r, dict) or r.get("gosto") not in GOSTOS_VALIDOS:
        print(f"resultado.json sem \"gosto\" válido (bonito, correto ou generico); veio: {r.get('gosto') if isinstance(r, dict) else r!r}.", file=sys.stderr)
        return 2
    gosto = r["gosto"]
    cliente = [str(x).strip() for x in (r.get("depende_do_cliente") or []) if str(x).strip()] if isinstance(r.get("depende_do_cliente"), list) else []
    achados = [str(x) for x in (r.get("tells") or [])] if isinstance(r.get("tells"), list) else []
    texto = " ".join([str(r.get("uma_mudanca") or ""), *achados])
    if gosto != "bonito" and not cliente and PADRAO_CLIENTE.search(texto):
        achou = PADRAO_CLIENTE.search(texto).group(0)
        cliente = [f"material da cliente apontado pelo auditor ({achou}): {str(r.get('uma_mudanca') or '').strip()[:160]}"]
    dur = r.get("duracao_min")
    print(f"LENTE DE GOSTO NO HERÓI: {gosto}. Rodada única, fechada.")
    if isinstance(dur, (int, float)) and not isinstance(dur, bool) and dur > ORCAMENTO_MIN:
        print(f"  AVISO: o auditor passou do teto de {ORCAMENTO_MIN} min ({dur:g} min). Não reprova, mas o teto é duro.")
    if gosto == "bonito":
        print("  Nada a ajustar no herói. Siga para as imagens e as outras seções.")
        return 0
    if cliente:
        pend = projeto / "evidencias" / "pendencias-do-heroi.md"
        pend.parent.mkdir(parents=True, exist_ok=True)
        ja = pend.read_text(encoding="utf-8") if pend.is_file() else ""
        novas = [c for c in cliente if f"- {c}\n" not in ja]
        if novas or not ja:
            cabeca = "" if ja else "# Pendências do herói que só a cliente resolve\n\nVão em PENDÊNCIAS DECLARADAS da entrega (etapa 5, campo `pendencias`).\n\n"
            pend.write_text(ja + cabeca + "".join(f"- {c}\n" for c in novas), encoding="utf-8")
        print(f"  PENDÊNCIA DA CLIENTE registrada em {pend} ({len(cliente)} item(ns)):")
        for c in cliente:
            print(f"    - {c}")
        print("  O motivo do veredito depende de material que só a cliente tem: não rode a lente de novo, o resultado seria o mesmo.")
    mudanca = str(r.get("uma_mudanca") or "").strip()
    if mudanca and not (cliente and PADRAO_CLIENTE.search(mudanca) and not r.get("depende_do_cliente")):
        print("  Aplique no HERÓI, com o material que já existe, e siga para as outras seções, sem segunda rodada:")
        print(f"    {mudanca}")
    elif cliente:
        print("  Aplique no HERÓI só o que não depende da cliente (enquadramento, escala e recorte da imagem que já existe) e siga, sem segunda rodada.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Prancha e briefing da lente curta de gosto no herói (uma rodada só).")
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--heroi", help="print da dobra em 1440")
    ap.add_argument("--registrar", action="store_true", help="lê o resultado.json do auditor, registra a pendência da cliente e fecha a lente")
    ap.add_argument("--celular", help="print da dobra em 390")
    ap.add_argument("--refs", help="duas capturas de referência, separadas por vírgula")
    ap.add_argument("--saida", help="pasta de saída (padrão: <projeto>/auditoria/gosto-heroi)")
    ap.add_argument("--publico", help="público do briefing (padrão: lido de evidencias/briefing.md)")
    a = ap.parse_args()
    projeto = pathlib.Path(a.projeto)
    saida = pathlib.Path(a.saida) if a.saida else projeto / "auditoria" / "gosto-heroi"
    if a.registrar:
        sys.exit(registrar(saida, projeto))
    if not a.heroi:
        ap.error("--heroi é obrigatório (ou use --registrar)")
    if _estado(saida).is_file():
        print("A lente de gosto no herói roda 1 rodada só e ela já deu o resultado "
              f"({_estado(saida)}). A lente não roda de novo: se o motivo do veredito depende de material da cliente, ele já é pendência "
              "da entrega (gosto-heroi.py --registrar); o resto você aplica no herói.", file=sys.stderr)
        sys.exit(3)
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
    prancha = saida / "prancha.jpg"
    tamanho = montar(refs[:2], pathlib.Path(a.heroi), pathlib.Path(a.celular) if a.celular else None, prancha)
    briefing = saida / "briefing.md"
    briefing.write_text(BRIEFING.format(minutos=ORCAMENTO_MIN, aviso=ORCAMENTO_MIN - 1, chamadas=ORCAMENTO_CHAMADAS, prancha=prancha.resolve(),
                                        publico=publico or "não informado", dir_skill=AQUI.parent), encoding="utf-8")
    print(f"prancha: {prancha} ({tamanho[0]}x{tamanho[1]})")
    print(f"briefing: {briefing}")
    print(f"orçamento: {ORCAMENTO_MIN} min e até {ORCAMENTO_CHAMADAS} chamadas, 1 imagem")
    print("próximo passo: lance 1 subagente que não construiu a página com o conteúdo do briefing (rodada única, teto de "
          f"{ORCAMENTO_MIN} min); grave a resposta em " + str(saida / "resultado.json") + " e rode gosto-heroi.py --projeto <dir> --registrar")


if __name__ == "__main__":
    main()
