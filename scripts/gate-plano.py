#!/usr/bin/env python3
"""Gate da etapa PLANO: o PLANO.md tem tudo o que o aluno precisa aprovar antes do código.

Uso:
  python3 gate-plano.py --projeto <dir>          (lê <dir>/PLANO.md)
  python3 gate-plano.py --plano <dir>/PLANO.md

Reprova (exit 1) se faltar qualquer uma das 7 seções (a. Referências, b. Visual, c. Seções,
d. Copy, e. Pixel e rastreamento, f. Código e publicação, g. Aprovação), se o visual não tiver
3 direções com prévia PNG real e a comparação lado a lado, se a copy não tiver a coluna de
sustentação preenchida, se o pixel não declarar o pedido e os eventos, se houver ID real de
rastreamento no texto ou se alguma aprovação estiver desmarcada. Imagens se conferem no disco,
pelo cabeçalho PNG, relativas à pasta do PLANO.md.
"""
import argparse
import pathlib
import re
import sys
import unicodedata

SECOES = [
    ("a", "Referências"),
    ("b", "Visual"),
    ("c", "Seções"),
    ("d", "Copy"),
    ("e", "Pixel e rastreamento"),
    ("f", "Código e publicação"),
    ("g", "Aprovação"),
]
EVENTOS = ("clique_whatsapp", "clique_cta", "rolagem_50", "rolagem_90", "envio_formulario")
MIN_MINIATURAS = 10
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
# ID real: Meta Pixel tem 15 ou 16 dígitos; GA4 é G- e 8 a 12 letras ou números (G-XXXXXXXX é
# o modelo e passa).
ID_META = re.compile(r"(?<![\d.])\d{15,16}(?![\d.])")
ID_GA4 = re.compile(r"\bG-(?!X+\b)[A-Z0-9]{8,12}\b")


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def png_real(caminho):
    try:
        with open(caminho, "rb") as f:
            return f.read(8) == b"\x89PNG\r\n\x1a\n"
    except OSError:
        return False


def fatiar(texto):
    """Devolve {letra: corpo} para cada seção '## <letra>. <nome>' encontrada, e a ordem."""
    achadas, ordem = {}, []
    cabecalhos = list(re.finditer(r"(?m)^##\s+([a-g])\.\s+(.+?)\s*$", texto))
    for i, m in enumerate(cabecalhos):
        letra, nome = m.group(1), m.group(2)
        esperado = dict(SECOES).get(letra)
        if not esperado or sem_acento(nome) != sem_acento(esperado):
            continue
        fim = cabecalhos[i + 1].start() if i + 1 < len(cabecalhos) else len(texto)
        achadas[letra] = texto[m.end():fim]
        ordem.append(letra)
    return achadas, ordem


def imagens(corpo, base):
    return [(alvo, png_real(base / alvo)) for alvo in IMG.findall(corpo)]


def subsecoes(corpo):
    partes = list(re.finditer(r"(?m)^###\s+(.+?)\s*$", corpo))
    for i, m in enumerate(partes):
        fim = partes[i + 1].start() if i + 1 < len(partes) else len(corpo)
        yield m.group(1), corpo[m.end():fim]


def checar(caminho):
    erros = []
    if not caminho.exists():
        return [f"{caminho} não existe: a etapa PLANO não foi feita (modelo em references/plano.md)"]
    texto = caminho.read_text(encoding="utf-8")
    base = caminho.parent
    sec, ordem = fatiar(texto)

    for letra, nome in SECOES:
        if letra not in sec:
            erros.append(f"falta a seção '## {letra}. {nome}'")
    if ordem != sorted(ordem):
        erros.append(f"seções fora de ordem: {', '.join(ordem)}")

    for m in ID_META.finditer(texto):
        erros.append(f"ID real de Meta Pixel no plano ({m.group(0)}): o ID mora na conta do aluno e no projeto, nunca no documento")
    for m in ID_GA4.finditer(texto):
        erros.append(f"ID real de GA4 no plano ({m.group(0)}): use G-XXXXXXXX no texto")

    # a. Referências
    if "a" in sec:
        c = sec["a"]
        imgs = imagens(c, base)
        if not imgs:
            erros.append("Referências: nenhum print (![...](referencias/...png))")
        for alvo, ok in imgs:
            if not ok:
                erros.append(f"Referências: print {alvo} não existe ou não é PNG")
        itens = [l for l in c.splitlines() if IMG.search(l)]
        sem = [IMG.search(l).group(1) for l in itens if "faz bem" not in sem_acento(l)]
        for alvo in sem:
            erros.append(f"Referências: {alvo} sem 'o que essa faz bem'")
        if not re.search(r"(?mi)^\s*[-*]\s*\[x\]", c):
            erros.append("Referências: nenhuma marcada com [x]; o aluno marca as que gosta")

    # b. Visual
    if "b" in sec:
        c = sec["b"]
        direcoes = [(t, corpo) for t, corpo in subsecoes(c) if sem_acento(t).startswith("direcao")]
        if len(direcoes) < 3:
            erros.append(f"Visual: {len(direcoes)} direção(ões); são 3 ('### Direção A', B e C), cada uma com prévia")
        arquivos = set()
        for titulo, corpo in direcoes:
            imgs = imagens(corpo, base)
            if not imgs:
                erros.append(f"Visual: '{titulo}' sem prévia PNG da primeira dobra")
            for alvo, ok in imgs:
                arquivos.add(alvo)
                if not ok:
                    erros.append(f"Visual: prévia {alvo} não existe ou não é PNG (rode scripts/previa-direcoes.mjs)")
        if len(direcoes) >= 3 and len(arquivos) < 3:
            erros.append("Visual: as 3 direções apontam para a mesma prévia")
        lado = [alvo for alvo, _ in imagens(c, base) if alvo.endswith("direcoes.png")]
        if not lado or not png_real(base / lado[0]):
            erros.append("Visual: falta a comparação lado a lado plano/direcoes.png (scripts/previa-direcoes.mjs)")
        if not re.search(r"(?i)escolha:.*\[x\]", c):
            erros.append("Visual: a linha 'Escolha:' não tem nenhuma direção marcada com [x]")

    # c. Seções
    if "c" in sec:
        c = sec["c"]
        minis = [(a, ok) for a, ok in imagens(c, base) if "miniatura" in a]
        validas = [a for a, ok in minis if ok]
        if len(validas) < MIN_MINIATURAS:
            erros.append(f"Seções: {len(validas)} miniatura(s) no cardápio; mínimo {MIN_MINIATURAS} "
                         "(scripts/previa-direcoes.mjs --miniaturas)")
        for a, ok in minis:
            if not ok:
                erros.append(f"Seções: miniatura {a} não existe ou não é PNG")
        ordem_sub = [corpo for t, corpo in subsecoes(c) if sem_acento(t).startswith("ordem escolhida")]
        itens = re.findall(r"(?m)^\s*(?:\d+\.|[-*])\s+\S", ordem_sub[0]) if ordem_sub else []
        if len(itens) < 3:
            erros.append("Seções: falta '### Ordem escolhida' com pelo menos 3 seções montadas pelo aluno")

    # d. Copy
    if "d" in sec:
        c = sec["d"]
        linhas = [l.strip() for l in c.splitlines() if l.strip().startswith("|")]
        cab = linhas[0] if linhas else ""
        if not re.search(r"(?i)sustenta", cab):
            erros.append("Copy: falta a tabela com a coluna 'Linha do briefing que sustenta'")
        else:
            colunas = [x.strip() for x in cab.strip("|").split("|")]
            idx = next(i for i, x in enumerate(colunas) if re.search(r"(?i)sustenta", x))
            dados = [l for l in linhas[1:] if not re.fullmatch(r"\|?[\s:|-]+\|?", l)]
            if not dados:
                erros.append("Copy: a tabela não tem nenhuma frase")
            pendente = False
            for l in dados:
                cel = [x.strip() for x in l.strip("|").split("|")]
                valor = cel[idx] if idx < len(cel) else ""
                if not valor:
                    erros.append(f"Copy: frase sem sustentação: {l[:80]}")
                elif "PENDENTE" in valor.upper():
                    pendente = True
            pend = [corpo for t, corpo in subsecoes(c) if sem_acento(t).startswith("pendencias")]
            tem_lista = bool(pend and re.search(r"(?m)^\s*[-*]\s+\S", pend[0]))
            if pendente and not tem_lista:
                erros.append("Copy: frase PENDENTE sem a lista '### Pendências do cliente'")

    # e. Pixel e rastreamento
    pedido = re.search(r"(?mi)^pixel pedido:\s*(.+)$", texto)
    if not pedido:
        erros.append("Pixel: falta a linha 'Pixel pedido: Meta e GA4 | Meta | GA4 | nenhum'")
    if "e" in sec:
        c = sec["e"]
        nenhum = bool(pedido and re.search(r"(?i)nenhum|n[aã]o", pedido.group(1)))
        if not nenhum:
            for ev in EVENTOS:
                if ev not in c:
                    erros.append(f"Pixel: evento {ev} não declarado (references/rastreamento.md)")
            p = sem_acento(pedido.group(1)) if pedido else ""
            if "meta" in p and "meta" not in sem_acento(c):
                erros.append("Pixel: o pedido tem Meta e a seção não diz onde pegar o ID do Meta Pixel")
            if "ga4" in p and "ga4" not in sem_acento(c):
                erros.append("Pixel: o pedido tem GA4 e a seção não diz onde pegar o ID do GA4")
        elif len(c.strip()) < 20:
            erros.append("Pixel: 'nenhum' sem dizer por quê nem o que fazer quando for anunciar")

    # f. Código e publicação
    if "f" in sec:
        c = sem_acento(sec["f"])
        for termo in ("noindex", "robots", "og:image"):
            if termo not in c:
                erros.append(f"Código e publicação: falta {termo} (o que muda no domínio final)")

    # g. Aprovação
    if "g" in sec:
        c = sec["g"]
        caixas = re.findall(r"(?mi)^\s*[-*]\s*\[( |x)\]\s*(.+)$", c)
        nomes = {sem_acento(n) for _, n in caixas}
        for letra, nome in SECOES[:-1]:
            alvo = sem_acento(f"{letra}. {nome}")
            if not any(n.startswith(alvo) for n in nomes):
                erros.append(f"Aprovação: falta a caixa '- [ ] {letra}. {nome}'")
        for marca, nome in caixas:
            if marca != "x" and marca != "X":
                erros.append(f"Aprovação: '{nome.strip()}' desmarcada; sem tudo marcado, não constrói")
    return erros


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--projeto")
    g.add_argument("--plano")
    a = ap.parse_args()
    caminho = pathlib.Path(a.plano) if a.plano else pathlib.Path(a.projeto) / "PLANO.md"
    erros = checar(caminho.resolve())
    if erros:
        print(f"REPROVA: {len(erros)} problema(s) no {caminho.name}")
        for e in erros:
            print(f"  - {e}")
        return 1
    print(f"PASSA: {caminho.name} com as 7 seções, 3 direções com prévia, copy sustentada, pixel declarado e tudo aprovado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
