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

Captura feita com OUTRO conteúdo de dist conta como VELHA (foi capturada antes da última mudança da
página) e reprova: o auditor não pode julgar a versão anterior. O critério é o hash do conteúdo da
dist (`dist_hash.py`), não a data do arquivo: remontar a dist com o conteúdo igual não deixa nada velho
(achado A1 da auditoria de velocidade). Sem registro de hash, vale a data, como antes.

Uso:
    node scripts/py.mjs pacote-auditoria.py --projeto <dir> --url http://localhost:8765/ [--rodada 1|2] [--caminho criar|clonar|...]
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dist_hash  # noqa: E402  (a captura é velha quando o CONTEÚDO da dist mudou, não quando a data do arquivo mudou)
import conferencia  # noqa: E402  (3.7.0: a rodada 2 é conferência dirigida, com o print novo de cada achado e o diff da dist)

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
    """Listadas se existirem. 3.5.8 (N19): TODAS as referências (dobra e meio), as telas de 360 e 320 e as pranchas de animação por seção."""
    cand = [raiz / "plano-visual.md"]
    achados = [p for p in cand if p.is_file()]
    achados += achar_todos(raiz, "comparativo-*.jpg")[:3]
    if (raiz / "referencias").is_dir():
        achados += achar_todos(raiz / "referencias", "*-dobra.png") + achar_todos(raiz / "referencias", "*-meio.png")
    for nome in ("prova-mobile360.png", "prova-mobile320.png"):
        f = achar(raiz, nome)
        if f:
            achados.append(f)
    achados += [p for p in achar_todos(raiz, "*.png") if p.parent.name == "anim"]
    vistos, unicos = set(), []
    for p in achados:
        if p not in vistos:
            vistos.add(p)
            unicos.append(p)
    return unicos


ORCAMENTO = {1: (8, 12), 2: (3, 4)}   # 3.7.0: o mesmo do wave.py (teste de aluno da 3.6.2: 758 s e 21 chamadas; 662 s e 10)

# 3.7.0 (item 1b): a lente coberta por gate VERDE não se reaudita do zero. O auditor recebe o laudo e procura só o que o gate não
# mede. Gate vermelho ou sem registro não cobre nada: a lente é auditada inteira. As medidas vêm do `wave.py` (GATES).
COBERTURA = {
    "design-critic": (("composicao", "ritmo", "sem-kicker", "texto"),
                      "gosto, cara de IA além do que o gate conta (tells V1 a V20, os três visuais padrão), hierarquia e coerência com o plano visual"),
    "assets-auditor": (("imagens",), "se a foto casa com o título e com o público, o recorte na janela, logo de terceiro e foto que sugere ser do cliente"),
    "visual-auditor": (("simetria", "ritmo"), "hierarquia tipográfica, paleta contra o plano visual, espaçamento e grid de desktop"),
    "motion-auditor": (("movimento", "animacao"), "se cada animação tem ligação com o conteúdo, o momento assinatura e o mesmo fade em bloco"),
    "responsive-auditor": (("responsivo", "oclusao"), "hierarquia no celular, coluna sozinha, buraco e ordem do conteúdo, olhando os prints"),
    "cro-auditor": (("identidade", "rastreamento"), "oferta, message match, objeções respondidas, ordem das seções e ação ambígua"),
    "a11y-auditor": ((), ""),
    "content-auditor": (("verdade",), "o que a frase insinua, foto e alt contra o briefing, travessão e contato dígito por dígito"),
    "comparacao-referencias": ((), ""),
}
FOCO = "hierarquia, gosto, coerência com o briefing e cara de IA"


SKILL_RAIZ = Path(__file__).resolve().parent.parent
_ACHADO = {"item": "string", "severidade": "critico|alto|medio|baixo", "evidencia": "string", "fix": "string"}
_BLOCO = {"lente": "string", "aprovado": True, "score": 8.5, "achados": [_ACHADO]}
_CONFERENCIA = {"rodada": 2, "achados": [{"achado": "string (o item da rodada 1, com a lente)", "estado": "corrigido|não corrigido|regressão", "evidencia": "string"}]}
SCHEMA_LENTE = (
    "```json\n" + json.dumps(_BLOCO, ensure_ascii=False, indent=2) + "\n```\n"
    "Evidência é obrigatória e verificável (print, medida em px, contraste, alvo de toque, trecho com linha ou passo de reprodução); "
    "achado sem evidência é descartado. O fix nunca viola a regra da skill (nada de depoimento inventado, urgência falsa ou dado fora do briefing).\n"
    'Na lente `comparacao-referencias` o bloco leva mais dois campos: `"gosto": "bonito|correto"` (a página é bonita ou só correta?) '
    'e `"eixos_abaixo": {EIXOS}` (só os eixos que ficaram abaixo das referências; vazio se nenhum).'
)
SCHEMA_RODADA_2 = "```json\n" + json.dumps(_CONFERENCIA, ensure_ascii=False, indent=2) + "\n```"


def _wave():
    import importlib.util
    spec = importlib.util.spec_from_file_location("wave_lentes", Path(__file__).resolve().parent / "wave.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lentes_da_skill():
    """As 9 lentes do wave.py (a fonte única), com o critério de cada uma em uma linha."""
    return dict(_wave().LENTES)


def schema_da_lente():
    """O schema de retorno da lente; os eixos vêm do wave.py, que os valida no registro."""
    return SCHEMA_LENTE.replace("{EIXOS}", json.dumps(list(_wave().EIXOS), ensure_ascii=False))


def laudo_do_gate(raiz, nome, registro):
    """O arquivo do laudo que o gate gravou (o `detalhe` da wave cita `gates/<nome>-rN.txt`); senão, o mais novo da pasta gates/."""
    m = re.search(r"\((gates/[^)\s]+\.txt)\)", str((registro or {}).get("detalhe") or ""))
    if m and (raiz / m.group(1)).is_file():
        return m.group(1)
    candidatos = sorted((raiz / "gates").glob(f"{nome}-r*.txt"), key=lambda p: p.stat().st_mtime) if (raiz / "gates").is_dir() else []
    candidatos = [c for c in candidatos if re.fullmatch(rf"{re.escape(nome)}-r\d+\.txt", c.name)]
    return candidatos[-1].relative_to(raiz).as_posix() if candidatos else None


def cobertura_dos_gates(raiz):
    """Por lente: [(gate, verde, laudo)] e o que procurar. Lê os gates da wave (`.wave-auditoria.json`)."""
    try:
        gates = json.loads((raiz / ".wave-auditoria.json").read_text(encoding="utf-8-sig")).get("gates") or {}
    except (OSError, ValueError, AttributeError):
        gates = {}
    saida = {}
    for lente, (nomes, procurar) in COBERTURA.items():
        lista = []
        for g in nomes:
            reg = gates.get(g)
            if not isinstance(reg, dict):
                lista.append((g, None, None))
            else:
                lista.append((g, reg.get("exit") == 0, laudo_do_gate(raiz, g, reg)))
        saida[lente] = (lista, procurar)
    return saida


def texto_da_cobertura(raiz):
    """A seção do briefing da rodada 1 que diz, lente por lente, o que os gates verdes já mediram."""
    medidas = _wave().GATES
    linhas = []
    laudos = []
    for lente, (lista, procurar) in cobertura_dos_gates(raiz).items():
        verdes = [(g, l) for g, v, l in lista if v]
        fora = [(g, v) for g, v, _l in lista if not v]
        if not lista:
            linhas.append(f"- `{lente}`: nenhum gate cobre esta lente: audite a lente inteira, pelo HTML e pelos prints.")
            continue
        partes = []
        if verdes:
            cob = "; ".join(f"`{g}` verde ({medidas.get(g, g)}" + (f", laudo `{l}`)" if l else ")") for g, l in verdes)
            partes.append(f"coberta por {cob}. Não remeça isso; procure só o que o gate não mede: {procurar}")
            laudos += [l for _g, l in verdes if l]
        if fora:
            estado = ", ".join(f"`{g}` {'vermelho' if v is False else 'sem registro'}" for g, v in fora)
            partes.append(f"{estado}: a parte desse gate fica com você, por inteiro")
        if not verdes:
            partes.insert(0, "nenhum gate verde: audite a lente inteira")
        linhas.append(f"- `{lente}`: " + ". ".join(partes) + ".")
    return "\n".join(linhas), laudos


def briefing_do_auditor(rodada, url, itens, caminho, raiz=None):
    """Texto pronto para colar no prompt do auditor: pasta do projeto, lentes, critérios, schema, todos os caminhos do pacote e o orçamento (A27, N19)."""
    minutos, chamadas = ORCAMENTO[rodada]
    lista = "\n".join(f"- `{rel}`" for rel in sorted(itens)) or "- (pacote vazio: rode o pacote-auditoria.py de novo)"
    conferencia = (
        "\nEsta é a RODADA 2: é só conferência dos achados da rodada 1 (`auditoria/achados-rodada-1.*`), item por item: "
        "corrigido, não corrigido, regressão. Não reabra as 9 lentes.\n" if rodada == 2 else "")
    pasta = Path(raiz).resolve().as_posix() if raiz else "(pasta do projeto)"
    ref = SKILL_RAIZ / "references"
    criterios = [ref / "auditores.md", ref / "preferencias-de-design.md", ref / "anti-vibe-coding.md"]
    criterios += sorted(ref.glob("preferencias-dono-*.md"))   # preferências locais do dono da skill, quando existem
    lentes = "\n".join(f"- `{n}`: {d}" for n, d in lentes_da_skill().items())
    criterios_txt = "\n".join(f"- `{c.as_posix()}`" for c in criterios)
    schema = SCHEMA_RODADA_2 if rodada == 2 else schema_da_lente()
    cobertura = ""
    if raiz is not None and rodada == 1:
        txt, _laudos = texto_da_cobertura(Path(raiz))
        cobertura = (f"\n## O que os gates verdes já mediram (não remeça)\n\nGate verde é medida, não opinião. A lente coberta não se reaudita do zero: "
                     f"leia o laudo só se precisar do número e procure só o que o gate não mede: {FOCO}.\n\n{txt}\n")
    return f"""# Briefing do auditor, rodada {rodada} (caminho {caminho})

Você é o auditor independente. Refute, não revise: ache o que está errado e diga onde, com a medida.
{conferencia}
## Pasta do projeto

`{pasta}`

Os caminhos do pacote abaixo são relativos a esta pasta.

## Pacote (já pronto: LEIA, não capture de novo)

Página servida: {url}

{lista}

O manifesto está em `auditoria/pacote.json`.

## Critérios (leia antes de julgar)

{criterios_txt}

Em `auditores.md`, cada lente tem a sua seção com o que reprova. As lentes:

{lentes}
{cobertura}
## Orçamento desta rodada

- **{minutos} minutos** e no máximo **{chamadas} chamadas de ferramenta**, teto rígido (rodada 1: 8 minutos e 12 chamadas; rodada 2, a conferência: 3 minutos e 4 chamadas).
- **Não capture nada novo.** Não abra a página no navegador, não tire print, não grave vídeo, não rode gate: o pacote já traz os
  prints, as pranchas do vídeo, os laudos dos gates, o briefing, o PLANO e o HTML. Você lê o pacote e julga.
- Leitura que cabe em {chamadas} chamadas: o `dist/index.html`; o briefing e o PLANO; a prova de desktop e a de celular; as duas pranchas
  do vídeo; a síntese e as 2 dobras de referência mais fortes. O resto, só se sobrar chamada.
- O que só a interação mostra (foco, hover) e o que não deu tempo de olhar volta como **"não verificado"** no achado da lente,
  em vez de estourar o tempo.
- **O orçamento de tempo conta até a resposta chegar**, não até a última ferramenta: escrever a resposta também gasta tempo
  (medido: 15,1 min de trabalho e mais 5,6 min só para escrever 9 blocos). Reserve os últimos minutos para a resposta e comece
  a escrever antes de esgotar o tempo.
- **Blocos curtos por lente:** no máximo 5 achados por lente (os mais graves primeiro; o resto vira uma linha "outros: ..."),
  cada um com a evidência em UMA linha (medida, seletor ou caminho do print), sem parágrafo de contexto.
- A resposta é o **schema** abaixo ({'um item por achado da rodada 1' if rodada == 2 else 'um bloco por lente'}), sem relatório longo.
- No fim, informe a duração em minutos e o número de chamadas que gastou: a sessão principal os registra com
  `wave.py registrar ... --duracao-min <minutos> --chamadas <n>`, e o `wave.py rodada` avisa se passou do orçamento.

## Schema de retorno

{schema}
"""


SCHEMA_CONFERENCIA = """```json
{
  "rodada": 2,
  "achados": [
    { "n": 1, "estado": "corrigido|não corrigido|regressão", "gravidade": "só na regressão: critico|alto|medio|baixo", "evidencia": "o recorte da prancha, a linha do diff ou a medida" }
  ],
  "duracao_min": 0,
  "chamadas": 0
}
```"""


def briefing_da_conferencia(raiz, url, itens, abertos, diff, prancha):
    """O briefing da rodada 2 (3.7.0): só os achados críticos e altos, com o print novo de cada um e o diff da dist. Sem nota nova."""
    minutos, chamadas = ORCAMENTO[2]
    linhas = []
    for a in abertos:
        it = itens.get(a["n"], {})
        linhas.append(f"{a['n']}. [{a['severidade']}] `{a['lente']}`: {a['item']}\n"
                      f"   - rodada 1: {a['evidencia'] or '(sem evidência escrita)'}; fix pedido: {a['fix'] or '(nenhum)'}\n"
                      f"   - o que mudou: {it.get('o_que_mudou') or '(a sessão não escreveu)'}\n"
                      f"   - print novo: `{it.get('print', '(falta)')}`" + (f" (recorte {it['recorte']})" if it.get("recorte") else ""))
    lista = "\n".join(linhas)
    onde_prancha = (f"`{Path(prancha).relative_to(raiz).as_posix()}` (o print novo de cada achado, numerado, numa imagem só)"
                    if prancha else "sem prancha (falta o Pillow): abra só os prints que a lista cita")
    onde_diff = f"`{conferencia.DIFF.as_posix()}`" if diff else "sem diff (a rodada 1 não guardou a dist auditada)"
    return f"""# Briefing do auditor, rodada 2: CONFERÊNCIA DIRIGIDA

Você é o mesmo auditor independente. Esta rodada NÃO é auditoria nova: confira só os {len(abertos)} achado(s) crítico(s) e alto(s)
da rodada 1 abaixo, um por um, e diga o estado de cada um. Médio e baixo não estão aqui: não seguram o ciclo e os gates os provam.

## Pasta do projeto

`{raiz.as_posix()}`

Página servida: {url} (não abra: tudo o que você precisa está nos dois arquivos abaixo).

## Orçamento desta rodada

- **{minutos} minutos** e no máximo **{chamadas} chamadas de ferramenta**, teto rígido.
- Leitura: 1) a prancha {onde_prancha}; 2) o diff da dist {onde_diff}. Sobra chamada para UM print da lista, se a prancha não bastar.
- **Não capture nada**, não abra a página, não reabra as 9 lentes, não procure achado novo fora do que o diff tocou.
- **Sem nota nova.** As notas da rodada 1 ficam. A resposta é só o estado de cada número.
- Regressão é só o que o diff tocou e o print mostra quebrado; diga a gravidade dela.
- O que você não conseguiu conferir fica fora da resposta: conta como aberto, com a severidade da rodada 1.

## Os achados abertos

{lista}

## Schema de retorno (um item por número)

{SCHEMA_CONFERENCIA}

A sessão registra com `wave.py --projeto <dir> conferencia --arquivo auditoria/resposta-rodada-2.json`.
"""


def main_rodada_2(args, raiz):
    """Rodada 2 (3.7.0): conferência dirigida. Obrigatórios: a dist, os achados da rodada 1 e o print novo de cada crítico e alto."""
    print(f"\nPACOTE DA CONFERÊNCIA (rodada 2), caminho {args.caminho}\n" + "=" * 74)
    falta, avisos = [], []
    if not args.url.startswith(("http://", "https://")):
        falta.append(f"url (precisa começar com http:// ou https://, veio '{args.url}')")
    if not (raiz / "dist" / "index.html").is_file():
        falta.append("dist/index.html")
    abertos = conferencia.abertos_da_rodada_1(raiz, _wave()._blocos_do_texto)
    if abertos is None:
        print("  [FALTA ] auditoria/achados-rodada-1.json: salve nele a resposta da rodada 1")
        falta.append("auditoria/achados-rodada-1")
        abertos = []
    elif not abertos:
        print("  A rodada 1 não tem achado crítico nem alto: não há rodada 2 de auditor. O `wave.py rodada` fecha o ciclo sem ela;")
        print("  corrija os médios que couberem, rode os gates de novo (rodada completa) e entregue com as ressalvas.\n")
        return 1
    corte = max((p.stat().st_mtime for p in (raiz / "auditoria").glob("achados-rodada-1.*")), default=0)

    def fresca(p):
        mt = p.stat().st_mtime
        return mt > corte and dist_hash.captura_fresca(raiz, raiz / "dist", mt)[0]

    itens, problemas, modelo = conferencia.correcoes(raiz, abertos, fresca)
    for a in abertos:
        estado = "ACHOU " if a["n"] in itens else "FALTA "
        print(f"  [{estado}] n={a['n']} [{a['severidade']}] {a['lente']}: {a['item'][:70]}")
    for pr in problemas:
        print(f"  [FALTA ] {pr}")
    falta += problemas
    diff, resumo = conferencia.diff_da_dist(raiz)
    if diff:
        print(f"  [ACHOU ] {conferencia.DIFF.as_posix():<26} {resumo}")
    else:
        avisos.append(resumo)
    prancha = conferencia.montar_prancha(raiz, itens) if not problemas else None
    if prancha:
        print(f"  [ACHOU ] {conferencia.PRANCHA.as_posix():<26} os {len(itens)} print(s) novos numa imagem só")
    for av in avisos:
        print(f"  [AVISO ] {av}")
    completo = not falta
    saida = raiz / "auditoria"
    saida.mkdir(exist_ok=True)
    pacote = {"quando": datetime.datetime.now().isoformat(timespec="seconds"), "rodada": 2, "caminho": args.caminho, "url": args.url,
              "conferencia": True, "completo": completo, "faltando": falta, "abertos": len(abertos),
              "itens": {**{it["print"]: {"n": n} for n, it in itens.items()},
                        **({conferencia.DIFF.as_posix(): {}} if diff else {}),
                        **({conferencia.PRANCHA.as_posix(): {}} if prancha else {})}}
    (saida / "pacote.json").write_text(json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
    (saida / "briefing-do-auditor.md").write_text(briefing_da_conferencia(raiz, args.url, itens, abertos, diff, prancha), encoding="utf-8")
    print("=" * 74)
    if completo:
        print("  PACOTE DA CONFERÊNCIA COMPLETO. Cole auditoria/briefing-do-auditor.md no prompt do MESMO auditor da rodada 1:")
        print("  3 minutos, 4 chamadas, sem nota nova. Grave a resposta em auditoria/resposta-rodada-2.json e rode `wave.py conferencia`.\n")
        return 0
    print(f"  PACOTE INCOMPLETO: FALTA {'; '.join(falta)}.")
    if modelo:
        print(f"  Gravei o modelo numerado em {conferencia.CORRECOES.as_posix()}: preencha o print novo de cada achado e rode de novo.")
    print("  Não chame o auditor com pacote incompleto.\n")
    return 1


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

    if args.rodada == 2:
        return main_rodada_2(args, raiz)

    falta, velhos, itens = [], [], {}
    if not args.url.startswith(("http://", "https://")):
        falta.append(f"url (precisa começar com http:// ou https://, veio '{args.url}')")
    dist = raiz / "dist" / "index.html"
    hash_da_dist = dist_hash.hash_pasta(raiz / "dist") if dist.is_file() else None

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
        fresca, motivo = (True, "") if not (eh_captura and hash_da_dist is not None) else dist_hash.captura_fresca(raiz, raiz / "dist", arq.stat().st_mtime)
        if not fresca:
            print(f"  [VELHO ] {rotulo:<26} {rel}: {motivo}; refaça a captura")
            velhos.append(rotulo)
        else:
            print(f"  [ACHOU ] {rotulo:<26} {rel}")
    for arq in opcionais(raiz):
        rel = arq.relative_to(raiz).as_posix()
        itens.setdefault(rel, {"bytes": arq.stat().st_size, "modificado": datetime.datetime.fromtimestamp(arq.stat().st_mtime).isoformat(timespec="seconds")})
        print(f"  [opcional] {rel}")
    # 3.7.0: os laudos dos gates verdes entram no pacote; a lente coberta por eles não se reaudita do zero.
    _txt, laudos = texto_da_cobertura(raiz)
    for rel in laudos:
        arq = raiz / rel
        itens.setdefault(rel, {"bytes": arq.stat().st_size, "modificado": datetime.datetime.fromtimestamp(arq.stat().st_mtime).isoformat(timespec="seconds")})
    if laudos:
        print(f"  [laudos ] {len(laudos)} laudo(s) de gate verde: a lente coberta só procura o que o gate não mede")

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
        "rodada": args.rodada, "caminho": args.caminho, "url": args.url, "dist_hash": hash_da_dist,
        "completo": completo, "faltando": falta, "velhos": velhos, "itens": itens,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    (saida / "briefing-do-auditor.md").write_text(briefing_do_auditor(args.rodada, args.url, itens, args.caminho, raiz), encoding="utf-8")
    print("=" * 74)
    if completo:
        conferencia.guardar_dist(raiz)   # 3.7.0: a dist auditada fica guardada para o diff da conferência
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
