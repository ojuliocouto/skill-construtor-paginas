#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pacote de evidência do auditor (v3.5.4): junta UMA vez o que o auditor precisa e confere que está tudo.

Por que existe: a rodada de auditoria era de 9 subagentes e cada um capturava as telas de novo.
Agora a sessão principal junta o pacote uma vez (as capturas que os gates e o passo h já
produzem) e o auditor só LÊ. Este script não captura nada: lista o que achou, o que falta e o
que está velho, grava `auditoria/pacote.json` (o manifesto que vai no prompt do auditor) e sai 1
se faltar item obrigatório.

Itens (caminho CRIAR; os outros caminhos dispensam o que não existe neles):
  url                  --url, endereço http(s) da página servida
  dist/index.html      a página publicável
  briefing             evidencias/briefing.md
  PLANO                PLANO.md                        (só CRIAR)
  sustentacao          evidencias/sustentacao.md       (só CRIAR)
  sintese              referencias/sintese.md          (só CRIAR)
  referencias          pelo menos 1 referencias/*-dobra.png
  prints               prova-desktop.png e prova-mobile.png (screenshot-prova.js)
  pranchas do vídeo    prancha-desktop.png e prancha-mobile.png (gravar-video.js)
  achados da rodada 1  auditoria/achados-rodada-1.(json|md)   (só com --rodada 2)
Opcionais, listados se existirem: plano-visual.md e comparativos.

Item mais velho que dist/index.html conta como VELHO (foi capturado antes da última mudança da
página) e reprova: o auditor não pode julgar a versão anterior.

Uso:
    node scripts/py.mjs pacote-auditoria.py --projeto <dir> --url http://localhost:8765/ [--rodada 1|2] [--caminho criar|clonar|...]
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

IGNORAR = {"node_modules", ".git", "dist", "__pycache__", "auditoria"}
CAMINHOS = ("criar", "clonar", "clonar-elevar", "melhorar", "variante")


def achar(raiz, nome):
    """Primeiro arquivo com esse nome, fora de dist/, node_modules e .git. Mais novo vence."""
    achados = [p for p in raiz.rglob(nome) if p.is_file() and not (IGNORAR & set(p.relative_to(raiz).parts[:-1]))]
    return max(achados, key=lambda p: p.stat().st_mtime) if achados else None


def achar_todos(raiz, padrao):
    return sorted(p for p in raiz.rglob(padrao) if p.is_file() and not (IGNORAR & set(p.relative_to(raiz).parts[:-1])))


def itens_obrigatorios(raiz, caminho, rodada):
    """Lista de (rotulo, arquivo ou None, existe_ok)."""
    it = []
    dist = raiz / "dist" / "index.html"
    it.append(("dist/index.html", dist if dist.is_file() else None))
    if caminho != "clonar":
        b = raiz / "evidencias" / "briefing.md"
        it.append(("evidencias/briefing.md", b if b.is_file() else None))
    if caminho == "criar":
        for rot in ("PLANO.md", "evidencias/sustentacao.md", "referencias/sintese.md"):
            f = raiz / rot
            it.append((rot, f if f.is_file() else None))
    dobras = achar_todos(raiz / "referencias", "*-dobra.png") if (raiz / "referencias").is_dir() else []
    it.append(("referencias/*-dobra.png", dobras[0] if dobras else None))
    for nome in ("prova-desktop.png", "prova-mobile.png", "prancha-desktop.png", "prancha-mobile.png"):
        it.append((nome, achar(raiz, nome)))
    if rodada == 2:
        f = next((raiz / "auditoria" / n for n in ("achados-rodada-1.json", "achados-rodada-1.md")
                  if (raiz / "auditoria" / n).is_file()), None)
        it.append(("auditoria/achados-rodada-1", f))
    return it


def opcionais(raiz):
    cand = [raiz / "plano-visual.md"]
    achados = [p for p in cand if p.is_file()]
    achados += achar_todos(raiz, "comparativo-*.jpg")[:3]
    return achados


ORCAMENTO = {1: (15, 30), 2: (8, 15)}


def briefing_do_auditor(rodada, url, itens, caminho):
    """Texto pronto para colar no prompt do auditor, com os caminhos do pacote e o orçamento da rodada (A27)."""
    minutos, chamadas = ORCAMENTO[rodada]
    lista = "\n".join(f"- `{rel}`" for rel in sorted(itens)) or "- (pacote vazio: rode o pacote-auditoria.py de novo)"
    conferencia = (
        "\nEsta é a RODADA 2: é só conferência dos achados da rodada 1 (`auditoria/achados-rodada-1.*`), item por item: "
        "corrigido, não corrigido, regressão. Não reabra as 9 lentes.\n" if rodada == 2 else "")
    return f"""# Briefing do auditor, rodada {rodada} (caminho {caminho})

Você é o auditor independente. Refute, não revise: ache o que está errado e diga onde, com a medida.
{conferencia}
## Pacote (já pronto: LEIA, não capture de novo)

Página servida: {url}

{lista}

O manifesto está em `auditoria/pacote.json`.

## Orçamento desta rodada

- **{minutos} minutos** e no máximo **{chamadas} chamadas de ferramenta** (rodada 1: 15 minutos e 30 chamadas; rodada 2: 8 minutos e 15 chamadas).
- **Proibido recapturar o que já está no pacote** (telas, pranchas, vídeo). Só abra a página para o que print não mostra:
  interação, foco, hover, script bloqueado. No máximo **6 capturas próprias**.
- O que não deu tempo de olhar volta como **"não verificado"**, por lente, em vez de estourar o tempo.
- A resposta é o **schema** (um bloco por lente), sem relatório longo.
- No fim, informe a duração em minutos e o número de chamadas que gastou: a sessão principal os registra com
  `wave.py registrar ... --duracao-min <minutos> --chamadas <n>`, e o `wave.py rodada` avisa se passou do orçamento.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", default=".")
    ap.add_argument("--url", default=None, help="endereço http(s) da página servida (obrigatório)")
    ap.add_argument("--rodada", type=int, choices=(1, 2), default=1)
    ap.add_argument("--caminho", choices=CAMINHOS, default="criar")
    ap.add_argument("--briefing-reflete-pedido", dest="reflete", choices=("sim", "nao"), default=None,
                    help="item obrigatório do checklist (A33): o evidencias/briefing.md reflete o ÚLTIMO pedido da pessoa? "
                         "Dispensado quando existe evidencias/pedidos.md (a data decide e o pacote avisa)")
    args = ap.parse_args()
    raiz = Path(args.projeto).resolve()
    if not raiz.is_dir():
        print(f"ERRO: projeto não existe: {raiz}", file=sys.stderr)
        return 2
    if not args.url:
        print("ERRO: --url é obrigatório: o auditor abre a página servida.", file=sys.stderr)
        return 2

    falta, velhos, itens = [], [], {}
    if not args.url.startswith(("http://", "https://")):
        falta.append(f"url (precisa começar com http:// ou https://, veio '{args.url}')")
    dist = raiz / "dist" / "index.html"
    marco = dist.stat().st_mtime if dist.is_file() else None

    print(f"\nPACOTE DO AUDITOR, rodada {args.rodada}, caminho {args.caminho}\n" + "=" * 74)
    print(f"  [ACHOU ] url                      {args.url}" if not falta else f"  [FALTA ] url                      {args.url}")
    for rotulo, arq in itens_obrigatorios(raiz, args.caminho, args.rodada):
        if arq is None or arq.stat().st_size == 0:
            print(f"  [FALTA ] {rotulo:<26} {'arquivo vazio: ' + arq.relative_to(raiz).as_posix() if arq else 'não encontrado'}")
            falta.append(rotulo)
            continue
        rel = arq.relative_to(raiz).as_posix()
        itens[rel] = {"bytes": arq.stat().st_size, "modificado": datetime.datetime.fromtimestamp(arq.stat().st_mtime).isoformat(timespec="seconds")}
        eh_captura = arq.suffix == ".png" and rotulo.startswith(("prova-", "prancha-"))
        if eh_captura and marco is not None and arq.stat().st_mtime < marco:
            print(f"  [VELHO ] {rotulo:<26} {rel} é anterior à dist/index.html: refaça a captura")
            velhos.append(rotulo)
        else:
            print(f"  [ACHOU ] {rotulo:<26} {rel}")
    for arq in opcionais(raiz):
        rel = arq.relative_to(raiz).as_posix()
        itens.setdefault(rel, {"bytes": arq.stat().st_size, "modificado": datetime.datetime.fromtimestamp(arq.stat().st_mtime).isoformat(timespec="seconds")})
        print(f"  [opcional] {rel}")

    # A33: o briefing reflete o último pedido da pessoa? Com `evidencias/pedidos.md` (registro de pedidos) a data decide e o
    # pacote AVISA; sem o registro, a pergunta é obrigatória (--briefing-reflete-pedido sim|nao).
    avisos = []
    if args.caminho == "criar":
        briefing_arq = raiz / "evidencias" / "briefing.md"
        pedidos = raiz / "evidencias" / "pedidos.md"
        if pedidos.is_file() and briefing_arq.is_file():
            if briefing_arq.stat().st_mtime < pedidos.stat().st_mtime:
                avisos.append("evidencias/briefing.md é mais antigo que o último pedido registrado (evidencias/pedidos.md): releia o briefing contra o que foi pedido por último antes de chamar o auditor")
            print("  [ACHOU ] briefing reflete o último pedido  (conferido pela data do evidencias/pedidos.md)")
        elif args.reflete == "sim":
            print("  [ACHOU ] briefing reflete o último pedido  sim (declarado)")
        elif args.reflete == "nao":
            print("  [FALTA ] briefing reflete o último pedido  não: releia o briefing contra o que a pessoa pediu por último e atualize antes de chamar o auditor")
            falta.append("briefing reflete o último pedido (resposta: não). Releia o briefing e atualize")
        else:
            print("  [FALTA ] briefing reflete o último pedido  sem resposta: rode de novo com --briefing-reflete-pedido `sim|nao`")
            falta.append("briefing reflete o último pedido da pessoa (--briefing-reflete-pedido `sim|nao`, ou registre os pedidos em evidencias/pedidos.md)")
    for av in avisos:
        print(f"  [AVISO ] {av}")

    completo = not falta and not velhos
    saida = raiz / "auditoria"
    saida.mkdir(exist_ok=True)
    (saida / "pacote.json").write_text(json.dumps({
        "quando": datetime.datetime.now().isoformat(timespec="seconds"),
        "rodada": args.rodada, "caminho": args.caminho, "url": args.url,
        "completo": completo, "faltando": falta, "velhos": velhos, "itens": itens,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    (saida / "briefing-do-auditor.md").write_text(briefing_do_auditor(args.rodada, args.url, itens, args.caminho), encoding="utf-8")
    print("=" * 74)
    if completo:
        print("  PACOTE COMPLETO. Cole auditoria/briefing-do-auditor.md no prompt do auditor (ele traz os caminhos e o orçamento):")
        print("  ele lê o pacote, não captura de novo.\n")
        return 0
    if falta:
        print(f"  PACOTE INCOMPLETO: FALTA {', '.join(falta)}. Gere o que falta uma vez e rode de novo.")
    if velhos:
        print(f"  PACOTE VELHO: {', '.join(velhos)} foi capturado antes da última mudança da página.")
    print("  Não chame o auditor com pacote incompleto: ele ia capturar por conta própria, de novo.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
