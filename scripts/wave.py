#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registro da WAVE de auditoria + AUDITOR MASTER.

Por que existe (26/08/2026, pedido do dono depois de uma falha em cadeia):

  "no final, depois dessas lanes que voce passa, eu preciso que um ultimo auditor master
   avalie se todas as waves foram feitas, foram executadas. Porque a gente nao pode pular
   sobre a gente pra fazer auditoria; todos tem que participar do processo."

Ele estava descrevendo um buraco real. A skill mandava rodar uma wave adversarial de lentes
independentes, eu declarei que caiu no "fallback manual", e o resultado foi que a lente de
responsividade nunca rodou de verdade: a pagina foi entregue testada em UMA resolucao, e o
defeito apareceu no monitor dele. Auto-declaracao de "rodei a auditoria" nao e auditoria.

A regra aqui e a mesma do gate de uso de ferramentas: **declaracao nao vale, registro com
evidencia vale.** Cada lente se registra com veredito, nota e achados. O MASTER (`checar`)
reprova se faltar qualquer lente ou se algum gate executável não estiver verde.
Notas e vereditos das lentes alimentam o ciclo `rodada`, que decide o encerramento.

Versao 3 (02/10/2026): entra a NONA lente, `comparacao-referencias`. Ela responde uma
pergunta so: a pagina esta no nivel das referencias printadas no passo b? Reprovada, o
ciclo nao fecha por nota nenhuma e manda voltar ao plano visual (passo c). Ela nao aceita
"nao aplicavel": no caminho CLONAR a referencia e a propria pagina original.

v3.5.4 (08/10/2026): a rodada de auditoria e UM subagente auditor independente que percorre as
nove lentes numa passada e devolve um bloco por lente; o registro aqui continua um por lente,
com a origem certa. Uma lente por subagente e modo opcional (auditoria profunda pedida pela
pessoa). Teto de 2 rodadas; a segunda e de conferencia. Quando nao ha subagente, a mesma
checagem roda em sequencia e o registro diz isso (autoavaliacao, que nao libera entrega).

Uso:
    node scripts/py.mjs wave.py --projeto <dir> registrar <lente> --nota 8.5 \\
        --veredito aprovado --achados "o que olhou e o que encontrou"
    node scripts/py.mjs wave.py --projeto <dir> gate <nome> --exit 0 --detalhe "..."
    node scripts/py.mjs wave.py --projeto <dir> checar        # o AUDITOR MASTER
    node scripts/py.mjs wave.py --projeto <dir> --caminho clonar checar   # clone fiel: sem gate de referencias
    node scripts/py.mjs wave.py --projeto <dir> rodada --criticos 0 --altos 4 --pendencias-do-usuario 2 --regressoes 0
    node scripts/py.mjs wave.py --projeto <dir> reabrir --motivo "<mudança grande que o dono pediu entre as rodadas>"

Registro em lote (3.6, corte 5 da auditoria de velocidade; 15 chamadas à mão custaram 3,7 min de modelo):
    node scripts/py.mjs wave.py --projeto <dir> gates-lote --arquivo gates/_wave-r3.json
        o `rodar-gates.mjs` grava o exit REAL de cada gate de uma rodada completa numa chamada só.
    node scripts/py.mjs wave.py --projeto <dir> registrar-lote --arquivo auditoria/resposta-rodada-1.json --origem subagente
        registra as lentes direto da resposta do auditor (o schema do briefing: um bloco por lente, em lista,
        em objeto `{"lentes": [...]}` ou soltos entre fences de markdown). Tudo ou nada: bloco ruim não grava nenhum.
    As duas usam as MESMAS regras do `gate` e do `registrar`; o lote nunca aceita o que o registro um a um recusa.

3.5.9 (N27): mudança GRANDE pedida pelo dono ENTRE as rodadas (mexeu em metade da página) reabre a rodada 1 com `reabrir`,
uma vez por ciclo, registrada com o motivo. A rodada de conferência não é gasta com o que o dono pediu. Correção PEQUENA feita
depois da rodada 2 não reabre nada: em sessão não interativa o ciclo fecha em NÃO ENTREGAR, lista a correção e pede a rodada extra
na entrega (ver a mensagem de NÃO ENTREGAR e references/caminhos/criar.md).
"""
import argparse
import unicodedata
import datetime
import json
import math
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lancador import comando  # noqa: E402

REGISTRO = ".wave-auditoria.json"

# As NOVE lentes. Nenhuma e opcional: a que nao se aplica se registra com veredito
# "nao_aplicavel" e o motivo, e isso aparece no relatorio final. A exceção é a
# comparacao-referencias, que sempre se aplica.
LENTES = {
    "design-critic": "taste e anti-slop: tells visuais de IA, cara de template",
    "assets-auditor": "imagem, mockup e vídeo reais (não só texto, gradiente e SVG)",
    "visual-auditor": "hierarquia, paleta, espacamento e grid de desktop",
    "motion-auditor": "scroll reveal, hover, entrada do heroi, microinteracao",
    "responsive-auditor": "as 12 telas: overflow, CTA na dobra, toque 44px, texto legivel",
    "cro-auditor": "CTA, formulario, oferta, message match, Hook/Story/Offer",
    "a11y-auditor": "foco, label, alt, ARIA, contraste 4.5:1, zero emoji",
    "content-auditor": "dado inventado, claim sem fonte, travessao, consistencia de contato",
    "comparacao-referencias": "a página está no nível das referências printadas no passo b?",
}
LENTE_REFERENCIAS = "comparacao-referencias"
EIXOS = ("composicao", "tipografia", "imagem", "ritmo", "acabamento")   # os 5 de references/auditores.md (3.5.9, N23)
# Orçamento do auditor independente (A27, auditoria real: 51 min, 113 chamadas, mais de 200 arquivos na rodada 1).
# 3.7.0 (teste de aluno da 3.6.2: rodada 1 com 758 s e 21 chamadas, rodada 2 com 662 s e 10 chamadas, 35 min no passo g):
# a rodada 1 lê o pacote e julga, sem capturar nada (8 min, 12 chamadas); a rodada 2 é conferência dirigida dos achados
# críticos e altos, com o print novo de cada um e o diff da dist (3 min, 4 chamadas), sem nota nova.
ORCAMENTO = {1: (8, 12), 2: (3, 4)}
GOSTOS = ("bonito", "correto")

# Gates EXECUTAVEIS que precisam estar verdes. Nao dependem de julgamento: rodam e saem 0 ou 1.
GATES = {
    "identidade": "screenshot-prova.js (title, description, favicon quadrado, og)",
    "oclusao": "gate-oclusao.mjs (texto coberto ou cortado)",
    "responsivo": "gate-responsivo.mjs (12 telas)",
    "uso-ferramentas": "uso-ferramentas.py (ferramenta viva foi usada)",
    "sem-kicker": "gate-sem-kicker.py (toda página sem kicker em caixa alta e sem número decorativo)",
    "classes-mortas": "gate-classes-mortas.py (classe do código que não existe no CSS gerado)",
    "referencias": "gate-referencias.py (6 prints reais lidos, 2 de cada tipo)",
    # Auditoria da v3 (02/10/2026): os quatro desenhos e afirmacoes que passaram por todos os
    # gates anteriores e derrubaram a pagina para 5,5 viraram medida.
    "simetria": "gate-simetria.mjs (itens paralelos em caixas iguais, colunas que terminam juntas)",
    "texto": "gate-texto.mjs (viúva em título e subtítulo de 320 a 1440, item em minúscula, itálico colorido repetido)",
    "verdade": "gate-verdade.py (toda promessa com linha do briefing, inclusive nas metas)",
    "publicacao": "gate-publicacao.py (dist/ só com o que a página usa)",
    # Auditoria da v4 (02/10/2026, nota 6,5): defeitos que so aparecem na visita real ou fora
    # das telas e dos elementos que os gates mediam.
    "movimento": "gate-movimento.mjs (visita de 8 s parada no topo: nada anima fora da tela)",
    "composicao": "gate-composicao.mjs (mesmo esqueleto em mais de 2 seções seguidas, ícone de biblioteca)",
    "imagens": "gate-imagens.py (licença com versão e link, direito de imagem, aviso no og-image)",
    # Etapa PLANO (03/10/2026): o aluno aprova visual, secoes, copy, pixel e codigo antes do codigo.
    "plano": "gate-plano.py (PLANO.md com as 7 seções, 3 direções com prévia e tudo aprovado)",
    "rastreamento": "gate-rastreamento.py (pixel e eventos que o plano pediu ligados na dist/)",
    # Padrao da v7 (04/10/2026): o que separou a v7 da v6, a "correta e generica", virou medida.
    "ritmo": "gate-ritmo.mjs (nenhuma seção vizinha com o mesmo esqueleto, no máximo 1 título centralizado com cartões)",
    "animacao": "gate-animacao.py (cada seção muda 2% ou mais dos pixels em 1440 e 390, no máximo 2 com o mesmo tipo de animação)",
    # 3.7.0 (teste de aluno do CLONAR na 3.6.3): o clone se mede contra a original, nas duas larguras.
    "fidelidade": "gate-fidelidade.mjs (só CLONAR: elementos-chave em 1440 e 390, altura e diff de pixels contra a original)",
}

# Quem auditou. Nota de autoavaliacao (quem construiu olhando o proprio trabalho) NAO libera
# entrega: na v3 a autoavaliacao das 9 lentes deu media 7,78 e "tells 0", e o auditor
# independente deu 5,5 com 5 achados graves. Sem subagente no ambiente, a rodada independente
# roda em outra sessao (ou por outra pessoa) e se registra com --origem sessao-independente.
ORIGENS_INDEPENDENTES = ("subagente", "sessao-independente", "pessoa")
ORIGENS = ORIGENS_INDEPENDENTES + ("autoavaliacao",)

# Clone fiel (CLONAR) nao pesquisa referencia: a referencia e a original. Os outros caminhos
# que produzem ou refazem a pagina exigem o gate de referencias.
CAMINHOS = ("criar", "clonar", "clonar-elevar", "melhorar", "variante")


# 3.7.0 (teste de aluno do CLONAR na 3.6.3: clone com 0,054% de pixels diferentes e ENTREGA BLOQUEADA por 8 gates).
# No clone fiel a régua é a original. Três grupos:
#   FORA_DO_CLONE: perguntam pelo briefing, pelo PLANO, pelo pixel ou pelas 6 referências, que o clone não tem. Não rodam.
#   RESSALVA_POR_FIDELIDADE: medem gosto ou regra da skill que a ORIGINAL pode não seguir (animação, alvo de toque, viúva,
#     licença e "imagem ilustrativa" da foto da própria página, esqueleto e simetria). Rodam e, vermelhos, viram RESSALVA na
#     entrega: consertar seria trair a fidelidade.
#   o resto (fidelidade, oclusão, classes mortas, publicação, identidade, uso de ferramentas) bloqueia como sempre.
FORA_DO_CLONE = ("referencias", "verdade", "rastreamento", "plano", "ritmo", "animacao")
RESSALVA_POR_FIDELIDADE = ("movimento", "responsivo", "texto", "imagens", "simetria", "composicao", "sem-kicker")
SO_NO_CLONE = ("fidelidade",)


def gates_exigidos(caminho):
    # Clone fiel copia o texto da original: a fonte da verdade e a propria pagina, nao um briefing.
    # A etapa PLANO e do CRIAR: os outros caminhos partem de uma pagina que ja existe. Ritmo e animacao
    # tambem nao valem para o clone fiel: a composicao e a da original.
    return {g: d for g, d in GATES.items()
            if not (caminho == "clonar" and g in FORA_DO_CLONE)
            and not (caminho != "clonar" and g in SO_NO_CLONE)
            and not (caminho != "criar" and g == "plano")}


def gates_de_ressalva(caminho):
    """Gates que, vermelhos, viram ressalva declarada em vez de bloqueio (só no clone fiel)."""
    return set(RESSALVA_POR_FIDELIDADE) if caminho == "clonar" else set()


def _caminho_no_comando(args):
    """O conjunto de gates do clone fiel é outro: todo comando de rodar-gates que a wave sugere num clone leva --caminho clonar."""
    return " --caminho clonar" if getattr(args, "caminho", "criar") == "clonar" else ""


def _onde(detalhe):
    m = re.search(r"\((gates/[^)]+)\)", str(detalhe or ""))
    return m.group(1) if m else str(detalhe or "")[:60]


def ressalvas_de_fidelidade(gates, caminho):
    """As linhas de ressalva da entrega: cada gate de ressalva que ficou vermelho no clone."""
    return [f"gate {g} vermelho, ressalva por fidelidade: a original faz igual e o clone não corrige a original "
            f"({_onde((gates.get(g) or {}).get('detalhe'))})"
            for g in sorted(gates_de_ressalva(caminho)) if isinstance(gates.get(g), dict) and gates[g].get("exit") not in (0, None)]

PISO_NOTA = 7.0
PISO_MEDIA = 8.0


def caminho(projeto):
    return Path(projeto) / REGISTRO


def carregar(projeto):
    p = caminho(projeto)
    if not p.exists():
        return {"lentes": {}, "gates": {}}
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        d.setdefault("lentes", {})
        d.setdefault("gates", {})
        return d
    except (json.JSONDecodeError, OSError):
        return {"lentes": {}, "gates": {}}


def salvar(projeto, dados):
    caminho(projeto).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def _validar_lente(lente, nota, veredito, achados, gosto, eixos_txt, dur, cham):
    """As regras de UMA lente, sem gravar nada. Devolve (mensagem de erro ou None, lista de eixos).
    O `registrar` e o `registrar-lote` usam esta mesma conta: o lote nunca aceita o que o registro um a um recusa."""
    if nota is not None and (not math.isfinite(nota) or not 0 <= nota <= 10):
        return "nota precisa ser finita entre 0 e 10.", []
    if lente not in LENTES:
        return f"lente desconhecida '{lente}'. Validas: {', '.join(sorted(LENTES))}", []
    if lente == LENTE_REFERENCIAS and veredito == "nao_aplicavel":
        return ("a comparação com as referências sempre se aplica. No CLONAR, a referência e a "
                "página original; nos outros caminhos, os prints do passo b."), []
    if lente == LENTE_REFERENCIAS:
        # Auditoria da v5 (03/10/2026): 7,0 e "correta, mas vazia; o dono nao chamaria de foda".
        # A regua do dono depois da SobrAI e a pergunta "isso e bonito ou so esta correto?".
        if gosto not in GOSTOS:
            return ("a comparação com as referências responde --gosto bonito|correto: a página "
                    "é bonita no nível das referências, ou só está correta? Diga por que nos achados."), []
        if gosto == "correto" and veredito == "aprovado":
            return ("página só correta não aprova a comparação com as referências. Registre "
                    "--veredito reprovado e corrija os eixos abaixo das referências na página (--eixos-abaixo)."), []
    eixos = [e.strip() for e in (eixos_txt or "").split(",") if e.strip()]
    if any(e not in EIXOS for e in eixos):
        return f"--eixos-abaixo aceita {', '.join(EIXOS)} (separados por vírgula).", []
    if (dur is not None and (not math.isfinite(dur) or dur < 0)) or (cham is not None and cham < 0):
        return "--duracao-min e --chamadas não podem ser negativos.", []
    if veredito != "nao_aplicavel" and nota is None:
        return "lente que rodou precisa de --nota", []
    if len((achados or "").strip()) < 25:
        return ("--achados precisa dizer o que foi OLHADO e o que foi encontrado "
                "(>= 25 caracteres). 'ok' não e auditoria."), []
    return None, eixos


def _gravar_lente(d, lente, nota, veredito, achados, origem, gosto, eixos, dur, cham):
    d["lentes"][lente] = {
        "quando": datetime.datetime.now().isoformat(timespec="seconds"),
        "veredito": veredito,
        "nota": nota,
        "achados": achados.strip(),
        "origem": origem or "autoavaliacao",
    }
    if gosto:
        d["lentes"][lente]["gosto"] = gosto
    if eixos:
        d["lentes"][lente]["eixos_abaixo"] = eixos
    if dur is not None:
        d["lentes"][lente]["duracao_min"] = dur
    if cham is not None:
        d["lentes"][lente]["chamadas"] = cham


def cmd_registrar(args):
    gosto = getattr(args, "gosto", None)
    dur, cham = getattr(args, "duracao_min", None), getattr(args, "chamadas", None)
    erro, eixos = _validar_lente(args.lente, args.nota, args.veredito, args.achados, gosto,
                                 getattr(args, "eixos_abaixo", None), dur, cham)
    if erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    d = carregar(args.projeto)
    _gravar_lente(d, args.lente, args.nota, args.veredito, args.achados, getattr(args, "origem", None), gosto, eixos, dur, cham)
    salvar(args.projeto, d)
    print(f"lente registrada: {args.lente} -> {args.veredito} [{d['lentes'][args.lente]['origem']}]"
          + (f" (nota {args.nota})" if args.nota is not None else ""))
    return 0


def cmd_reabrir(args):
    """Mudança grande pedida pelo dono entre as rodadas: o histórico vai para `ciclos_anteriores` e a rodada 1 começa de novo.
    Uma vez por ciclo, com o motivo registrado. Lentes e gates também recomeçam: a página mudou e ninguém os mediu de novo."""
    d = carregar(args.projeto)
    motivo = (getattr(args, "motivo", None) or "").strip()
    if len(motivo) < 10:
        print("ERRO: --motivo precisa dizer o que o dono pediu (pelo menos uma frase curta).", file=sys.stderr)
        return 2
    if not d.get("rodadas"):
        print("ERRO: nenhuma rodada fechada ainda; a mudança entra na rodada 1 normalmente, não há o que reabrir.", file=sys.stderr)
        return 2
    if d.get("reaberturas"):
        print("ERRO: este ciclo já foi reaberto uma vez (" + d["reaberturas"][-1].get("motivo", "")[:80] + "). Reabrir de novo seria um laço sem fim. "
              "Feche o ciclo em ENTREGA COM RESSALVAS ou NÃO ENTREGAR e peça a rodada extra (--rodada-extra-pedida) na entrega.", file=sys.stderr)
        return 2
    d.setdefault("ciclos_anteriores", []).append({"rodadas": d.get("rodadas"), "lentes": d.get("lentes"), "gates": d.get("gates")})
    d["reaberturas"] = [{"quando": datetime.datetime.now().isoformat(timespec="seconds"), "motivo": motivo,
                         "rodadas_fechadas": len(d["rodadas"])}]
    d["rodadas"] = []
    d["lentes"] = {}
    d["gates"] = {}
    salvar(args.projeto, d)
    print("REABERTO: a rodada 1 começa de novo. Motivo registrado: " + motivo)
    print("  Refaça os gates e a wave inteira (as 9 lentes) na página como ela está agora. Isto vale UMA vez por ciclo.")
    return 0


def cmd_gate(args):
    if args.nome not in GATES:
        print(f"ERRO: gate desconhecido '{args.nome}'. Validos: {', '.join(sorted(GATES))}",
              file=sys.stderr)
        return 2
    d = carregar(args.projeto)
    d["gates"][args.nome] = {
        "quando": datetime.datetime.now().isoformat(timespec="seconds"),
        "exit": args.exit_code,
        "detalhe": (args.detalhe or "").strip(),
    }
    salvar(args.projeto, d)
    marca = "verde" if args.exit_code == 0 else f"VERMELHO (exit {args.exit_code})"
    print(f"gate registrado: {args.nome} -> {marca}")
    return 0


def _resolver_arquivo(projeto, caminho):
    """3.7.0: `--arquivo auditoria/x.json` é relativo à pasta do PROJETO (o que a skill escreve nos comandos). Absoluto fica como está;
    relativo que não existe no projeto mas existe na pasta de onde se chamou também vale (o jeito antigo)."""
    p = Path(caminho)
    if p.is_absolute():
        return p
    no_projeto = Path(projeto) / p
    if no_projeto.exists() or not p.exists():
        return no_projeto
    return p


def _ler_json_do_arquivo(caminho, projeto=None):
    alvo = _resolver_arquivo(projeto, caminho) if projeto is not None else Path(caminho)
    try:
        return alvo.read_text(encoding="utf-8-sig"), None
    except OSError as e:
        return None, f"não consegui ler {alvo}: {e.strerror or e}"


def cmd_gates_lote(args):
    """Grava vários gates de uma vez. Entrada: {"gates": [{"nome", "exit", "detalhe"}], "pulados": [{"nome", "motivo"}]}. Tudo ou nada.

    `pulados` (3.7.0): gate que a rodada completa NÃO rodou de propósito (o de movimento numa rodada intermediária, com
    `rodar-gates.mjs --sem-movimento`). O registro anterior dele fica, marcado com `pulado_em`; a próxima rodada que o roda limpa a
    marca. A etapa 5 recusa a entrega com a marca: a rodada final sempre roda o gate de movimento."""
    texto, erro = _ler_json_do_arquivo(args.arquivo, args.projeto)
    if erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    try:
        doc = json.loads(texto)
    except ValueError as e:
        print(f"ERRO: {args.arquivo} não é JSON: {e}", file=sys.stderr)
        return 2
    itens = doc.get("gates") if isinstance(doc, dict) else doc
    if not isinstance(itens, list) or not itens:
        print('ERRO: o arquivo precisa trazer {"gates": [{"nome": ..., "exit": 0, "detalhe": ...}]} com pelo menos um gate.', file=sys.stderr)
        return 2
    problemas = []
    pulados = (doc.get("pulados") if isinstance(doc, dict) else None) or []
    if not isinstance(pulados, list):
        pulados = [pulados]
    for i, it in enumerate(pulados, 1):
        if not isinstance(it, dict) or it.get("nome") not in GATES:
            problemas.append(f"pulado {i}: gate desconhecido '{it.get('nome') if isinstance(it, dict) else it}'. Validos: {', '.join(sorted(GATES))}")
    for i, it in enumerate(itens, 1):
        if not isinstance(it, dict) or it.get("nome") not in GATES:
            problemas.append(f"item {i}: gate desconhecido '{it.get('nome') if isinstance(it, dict) else it}'. Validos: {', '.join(sorted(GATES))}")
        elif type(it.get("exit")) is not int:
            problemas.append(f"item {i} ({it['nome']}): \"exit\" precisa ser um número inteiro (o exit real do gate)")
    if problemas:
        for p_ in problemas:
            print("ERRO: " + p_, file=sys.stderr)
        print("Nada foi gravado.", file=sys.stderr)
        return 2
    d = carregar(args.projeto)
    agora = datetime.datetime.now().isoformat(timespec="seconds")
    for it in itens:
        d["gates"][it["nome"]] = {"quando": agora, "exit": it["exit"], "detalhe": str(it.get("detalhe") or "").strip()}
    for it in pulados:
        reg = d["gates"].setdefault(it["nome"], {"exit": None, "detalhe": "nunca rodou"})
        reg["pulado_em"] = agora
        reg["pulado_motivo"] = str(it.get("motivo") or "pulado nesta rodada").strip()
    salvar(args.projeto, d)
    vermelhos = [it["nome"] for it in itens if it["exit"] != 0]
    print(f"{len(itens)} gate(s) registrado(s) na wave: {len(itens) - len(vermelhos)} verde(s)"
          + (f", {len(vermelhos)} VERMELHO(s): {', '.join(vermelhos)}" if vermelhos else ""))
    for it in pulados:
        print(f"  {it['nome']}: PULADO nesta rodada ({d['gates'][it['nome']]['pulado_motivo']}); o registro anterior fica e a rodada final roda ele.")
    return 0


def _achatar_blocos(doc):
    """Os blocos de lente (objetos com o campo `lente`) de um JSON: lista, objeto {"lentes": [...]} ou um bloco só."""
    if isinstance(doc, list):
        return [b for item in doc for b in _achatar_blocos(item)]
    if isinstance(doc, dict):
        if isinstance(doc.get("lentes"), list):
            return _achatar_blocos(doc["lentes"])
        if "lente" in doc:
            return [doc]
    return []


def _blocos_do_texto(texto):
    """Os blocos de lente do arquivo, na ordem. Aceita JSON puro ou a resposta do auditor: prosa com um bloco por lente entre fences."""
    try:
        return _achatar_blocos(json.loads(texto))
    except ValueError:
        pass
    dec = json.JSONDecoder()
    blocos, i = [], 0
    while i < len(texto):
        if texto[i] in "{[":
            try:
                obj, fim = dec.raw_decode(texto, i)
                blocos.extend(_achatar_blocos(obj))
                i = fim
                continue
            except ValueError:
                pass
        i += 1
    return blocos


def _achados_em_texto(achados, nota):
    """O texto do registro a partir dos achados do auditor (lista de {item, severidade, evidencia, fix} ou um texto)."""
    if isinstance(achados, str):
        return achados.strip()
    partes = []
    for a in achados or []:
        if isinstance(a, dict):
            sev = str(a.get("severidade") or "").strip()
            linha = (f"[{sev}] " if sev else "") + str(a.get("item") or "").strip()
            if str(a.get("evidencia") or "").strip():
                linha += ": " + str(a["evidencia"]).strip()
            if str(a.get("fix") or "").strip():
                linha += " (fix: " + str(a["fix"]).strip() + ")"
            if linha.strip():
                partes.append(linha.strip())
        elif str(a).strip():
            partes.append(str(a).strip())
    if partes:
        return "; ".join(partes)
    return f"sem achados: o auditor devolveu a lente com a lista de achados vazia (nota {nota})"


def _numero_ou_none(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _preparar_lente(b, dur, cham):
    """Um bloco do auditor virado em registro de lente. Devolve (registro, None) ou (None, mensagem de erro)."""
    lente = b.get("lente")
    veredito = b.get("veredito")
    if veredito in ("nao_verificado", "não verificado"):
        return None, ("voltou como NÃO VERIFICADA. Lente que ninguém olhou não vira registro: "
                      "a rodada precisa olhar de novo, ou a lente fica sem registro")
    if veredito not in ("aprovado", "reprovado", "nao_aplicavel"):
        if not isinstance(b.get("aprovado"), bool):
            return None, 'faltam "aprovado" (true/false) ou "veredito"'
        veredito = "aprovado" if b["aprovado"] else "reprovado"
    bruta = b.get("score", b.get("nota"))
    nota = _numero_ou_none(bruta)
    if bruta is not None and nota is None:
        return None, "a nota (score) precisa ser número"
    lista = b.get("achados") if isinstance(b.get("achados"), list) else []
    achados = _achados_em_texto(b.get("achados"), bruta)
    eixos = b.get("eixos_abaixo")
    erro, eixos_lista = _validar_lente(lente, nota, veredito, achados, b.get("gosto"),
                                       ",".join(eixos) if isinstance(eixos, list) else (eixos or ""), dur, cham)
    if erro:
        return None, erro
    sevs = [str(a.get("severidade") or "").lower() for a in lista if isinstance(a, dict)]
    return {"lente": lente, "nota": nota, "veredito": veredito, "achados": achados, "gosto": b.get("gosto"), "eixos": eixos_lista,
            "criticos": sum(1 for x in sevs if x in ("critico", "crítico")), "altos": sum(1 for x in sevs if x == "alto"),
            "sem_achados": achados.startswith("sem achados:") and not (isinstance(b.get("achados"), str) and b["achados"].strip())}, None


def cmd_registrar_lote(args):
    """Registra as lentes da resposta do auditor. Tudo ou nada: valida todos os blocos antes de gravar o primeiro."""
    texto, erro = _ler_json_do_arquivo(args.arquivo, args.projeto)
    if erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    blocos = _blocos_do_texto(texto)
    if not blocos:
        print(f'ERRO: não achei nenhum bloco de lente (objeto JSON com o campo "lente") em {args.arquivo}.', file=sys.stderr)
        return 2
    try:
        doc = json.loads(texto)
    except ValueError:
        doc = None
    topo = doc if isinstance(doc, dict) else {}
    dur = args.duracao_min if args.duracao_min is not None else _numero_ou_none(topo.get("duracao_min"))
    cham = args.chamadas if args.chamadas is not None else (topo.get("chamadas") if type(topo.get("chamadas")) is int else None)
    problemas, prontos, vistos = [], [], set()
    for i, b in enumerate(blocos, 1):
        rotulo = f"bloco {i} ({b.get('lente')})"
        if b.get("lente") in vistos:
            problemas.append(f"{rotulo}: a lente aparece mais de uma vez no mesmo lote")
            continue
        vistos.add(b.get("lente"))
        pronto, erro_bloco = _preparar_lente(b, dur, cham)
        if erro_bloco:
            problemas.append(f"{rotulo}: {erro_bloco}")
        else:
            prontos.append(pronto)
    if problemas:
        for p_ in problemas:
            print("ERRO: " + p_, file=sys.stderr)
        print("Nada foi gravado.", file=sys.stderr)
        return 2
    d = carregar(args.projeto)
    for r in prontos:
        _gravar_lente(d, r["lente"], r["nota"], r["veredito"], r["achados"], args.origem, r["gosto"], r["eixos"], dur, cham)
    salvar(args.projeto, d)
    print(f"{len(prontos)} lente(s) registrada(s) [{args.origem}]: " + ", ".join(f"{r['lente']} {r['veredito']}" for r in prontos))
    faltam = [l for l in LENTES if l not in d["lentes"]]
    if faltam:
        print(f"  Faltam {len(faltam)} lente(s) para fechar a rodada: {', '.join(faltam)}")
    vazias = sum(1 for r in prontos if r["sem_achados"])
    if vazias:
        print(f"  {vazias} lente(s) sem achados: o registro diz isso com todas as letras.")
    print(f"  Contados no JSON do auditor: {sum(r['criticos'] for r in prontos)} crítico(s) e {sum(r['altos'] for r in prontos)} alto(s). "
          "CONFIRME cada um (refute o achado) antes de passar os números ao `wave.py rodada --criticos N --altos N`.")
    return 0


def cmd_checar(args):
    """O AUDITOR MASTER. Nao julga design: julga se o PROCESSO aconteceu inteiro."""
    d = carregar(args.projeto)
    lentes, gates = d["lentes"], d["gates"]
    exigidos = gates_exigidos(getattr(args, "caminho", "criar"))

    faltando = [l for l in LENTES if l not in lentes]
    reprovadas = [l for l, v in lentes.items() if v.get("veredito") == "reprovado"]
    na = [l for l, v in lentes.items() if v.get("veredito") == "nao_aplicavel"]
    baixas = [(l, v["nota"]) for l, v in lentes.items()
              if v.get("nota") is not None and v["nota"] < PISO_NOTA]
    notas = [v["nota"] for v in lentes.values() if v.get("nota") is not None]
    media = sum(notas) / len(notas) if notas else 0.0

    caminho_ = getattr(args, "caminho", "criar")
    ressalva = gates_de_ressalva(caminho_)
    gates_faltando = [g for g in exigidos if g not in gates]
    # Gate que não se aplica ao caminho (o de referências de uma rodada antiga num clone) não bloqueia: só os exigidos contam.
    gates_vermelhos = [g for g, v in gates.items() if g in exigidos and g not in ressalva and v.get("exit") != 0]
    gates_ressalva = [g for g, v in gates.items() if g in exigidos and g in ressalva and v.get("exit") != 0]

    print("\nAUDITOR MASTER: o processo aconteceu inteiro?\n" + "=" * 76)
    print(f"  LENTES ({len(lentes)}/{len(LENTES)} registradas)")
    for nome in sorted(LENTES):
        v = lentes.get(nome)
        if not v:
            print(f"    [FALTA ] {nome:<20} {LENTES[nome]}")
            continue
        nota = f"{v['nota']}" if v.get("nota") is not None else "-"
        marca = {"aprovado": "ok    ", "reprovado": "REPROVA", "nao_aplicavel": "n/a   "}.get(v["veredito"], "?")
        orig = "auto" if v.get("origem") not in ORIGENS_INDEPENDENTES else "indep"
        print(f"    [{marca}] {nome:<20} nota {nota:<5} {orig:<5} {v['achados'][:46]}")

    print(f"\n  GATES EXECUTAVEIS ({len([g for g in gates if g in exigidos])}/{len(exigidos)} registrados)")
    for nome in sorted(exigidos):
        v = gates.get(nome)
        if not v:
            print(f"    [FALTA ] {nome:<18} {exigidos[nome]}")
        elif v["exit"] != 0 and nome in ressalva:
            print(f"    [RESSALVA] {nome:<17} ressalva por fidelidade (confira que a original faz igual): {v['detalhe'][:30]}")
        else:
            print(f"    [{'verde ' if v['exit'] == 0 else 'VERMELHO'}] {nome:<18} {v['detalhe'][:50]}")
    fora = sorted(g for g in gates if g not in exigidos)
    if fora:
        print(f"    (registrados que não se aplicam ao caminho {caminho_}, ignorados: {', '.join(fora)})")

    print("=" * 76)
    problemas = []
    if faltando:
        problemas.append(f"{len(faltando)} lente(s) NUNCA rodaram: {', '.join(faltando)}")
    if gates_faltando:
        problemas.append(f"{len(gates_faltando)} gate(s) executavel(is) sem registro: {', '.join(gates_faltando)}")
    if gates_vermelhos:
        problemas.append(f"gate(s) vermelho(s): {', '.join(gates_vermelhos)}")
    # NOTA NAO E ASSUNTO DO MASTER. Ele pergunta uma coisa so: "o processo aconteceu inteiro?".
    # Quem decide se a nota basta e o CICLO (`rodada`), que olha critico, regressao e gravidade
    # ao longo das rodadas. Enquanto o master tambem barrava por piso de nota, os dois gates se
    # contradiziam: o ciclo mandava ENTREGAR com nota declarada e o master travava a mesma
    # entrega pela mesma nota, e nao existia estado que satisfizesse os dois. Isso e o "ficar
    # travado" que o dono proibiu, so que escrito em dois arquivos diferentes.
    # Duas regras que valem sempre: cada gate responde UMA pergunta, e dois gates nunca
    # respondem a mesma.
    if reprovadas:
        print(f"  SINAL: lente(s) com veredito REPROVADO: {', '.join(reprovadas)}")
        print("         Reprovacao de lente e insumo do CICLO, não trava do master.")
    if baixas:
        print("  SINAL: nota abaixo de %.1f: %s" % (PISO_NOTA, ", ".join(f"{l} ({n})" for l, n in baixas)))
    if notas and media < PISO_MEDIA:
        print(f"  SINAL: média {media:.2f} abaixo do piso {PISO_MEDIA}. Quem decide se isso entrega")
        print("         e `wave.py rodada`, e a nota vai DECLARADA na entrega.")
    if gates_ressalva:
        print(f"  RESSALVA POR FIDELIDADE: {', '.join(gates_ressalva)} vermelho(s) no clone. Não bloqueia: se a original faz igual,")
        print("         corrigir seria trair a fidelidade (se só o clone tem, é defeito: conserte). A entrega declara cada um (o `rodada` grava nas ressalvas).")
    pulados = sorted(g for g, v in gates.items() if isinstance(v, dict) and v.get("pulado_em"))
    if pulados:
        print(f"  SINAL: {', '.join(pulados)} pulado(s) na última rodada completa (--sem-movimento). Vale para rodada intermediária;")
        print(f"         a rodada final (passo h) roda `{comando('rodar-gates.mjs')} --projeto {Path(args.projeto).as_posix()}{_caminho_no_comando(args)}` SEM a flag, e a etapa 5 cobra isso.")

    if problemas:
        for p in problemas:
            print("  BLOQUEIA: " + p)
        # 3.6.2: nenhum bloqueio fica sem o comando que destrava.
        print("\n  PRÓXIMO COMANDO:")
        proj = Path(args.projeto).as_posix()
        if faltando:
            print(f"    - lente que nunca rodou: registre a resposta do auditor com `{comando('wave.py')} --projeto {proj} registrar-lote "
                  "--arquivo auditoria/resposta-rodada-1.json --origem subagente` (ou uma lente: `wave.py --projeto <dir> registrar <lente> ...`)")
        if gates_faltando:
            print(f"    - gate sem registro: `{comando('rodar-gates.mjs')} --projeto {proj}{_caminho_no_comando(args)}` (a rodada completa registra sozinha na wave)")
        for g in gates_vermelhos:
            print(f"    - gate {g} vermelho: conserte e rode `{comando('rodar-gates.mjs')} --projeto {proj}{_caminho_no_comando(args)} --so {g} --registrar-conserto`")
        print("\n  A ENTREGA ESTA BLOQUEADA. O master não julga se a página está bonita: ele")
        print("  julga se o PROCESSO aconteceu. Lente que não rodou não vira 'passou por")
        print("  omissao', e foi assim que uma página saiu testada em uma única resolucao.\n")
        return 1

    print(f"  Todas as {len(LENTES)} lentes rodaram. Media {media:.2f}. "
          + (f"Todos os gates que bloqueiam verdes; {len(gates_ressalva)} ressalva(s) por fidelidade." if gates_ressalva else "Todos os gates verdes."))
    if na:
        print(f"  {len(na)} marcada(s) como não aplicável (o motivo está no registro): {', '.join(na)}")
    print("  Processo completo. A decisão de entregar volta a ser sua.\n")
    return 0



# ============================ O CICLO ============================
# Pedido do dono (27/08/2026), depois de duas rodadas de wave:
#   "se for o caso, tem que ter na skill, entao bora. so nao podemos ficar travados
#    ou com a skill nota do"
#
# As duas metades desse pedido brigam entre si, e e por isso que o criterio precisa ser
# escrito com cuidado:
#   - "nao ficar travado" = nao pode existir loop infinito de corrigir e re-auditar
#   - "nao ficar com nota do" = nao pode entregar qualquer coisa so pra sair do loop
#
# O que a pratica mostrou em DOIS projetos (esta pagina e a skill de dashboards): o painel
# adversarial NUNCA para de achar coisa. A nota sobe rapido nas primeiras rodadas e depois
# oscila, porque cada rodada encontra um canto novo e menor. Exigir media 8,0 como unica
# porta de saida transforma o processo num loop que so termina por cansaco.
#
# Entao a porta de saida tem TRES criterios, e o que manda e o primeiro:
#
#   1. ZERO CRITICO CONFIRMADO. Inegociavel, em qualquer rodada. Critico e o que quebra
#      uso, mente pro visitante ou expoe o cliente. Isso nao se negocia com média.
#   2. NENHUMA REGRESSAO. Nenhuma lente pode ter caido em relacao a rodada anterior. Se
#      caiu, a correcao quebrou outra coisa e a rodada nao conta como avanco.
#   3. CONVERGENCIA ou PISO. Ou a media chegou ao piso (8,0), ou duas rodadas seguidas
#      subiram menos de 0,3: nesse ponto o retorno virou marginal e insistir e queimar
#      tempo pra caçar canto minusculo.
#
# Bateu 1 e 2 e convergiu? ENTREGA, com a nota real declarada na entrega. Nota 6,8 declarada
# e honesta; nota 6,8 escondida atras de "auditado" e que e nota do.
# v3.5.4 (08/10/2026): o teto cai de 4 para 2. A regra do dono e "teto de 2 rodadas de corrigir e
# auditar" (laco de auditoria queimou token) e a skill e usada ao vivo em aula. Depois da segunda
# rodada o ciclo fecha SEMPRE: aprovado, "ENTREGA COM RESSALVAS" (nota real e o que sobrou) ou
# "NAO ENTREGAR" (critico ou regressao abertos, que o teto nao afrouxa). Terceira rodada so com
# --rodada-extra-pedida, que fica registrada, e ela tambem fecha sempre. Nunca ha quarta.
# REGRESSÃO TRIVIAL (3.6.1, teste de aluno da 3.6.0). O ciclo fechou em NÃO ENTREGAR por uma regressão de 1 minuto (o crédito de 4
# fotos que saíram da página continuava no rodapé) e a etapa g levou 41 min. "Trivial" aqui é testável, as três juntas:
#   1. um gate do catálogo (GATES) pega a regressão;
#   2. esse gate PASSA depois do conserto: o registro dele na wave tem exit 0 e hora igual ou posterior à da última lente
#      registrada (o conserto veio depois da auditoria);
#   3. a regressão não é achado crítico nem alto do auditor (a gravidade vem declarada, e crítico ou alto fecha o ciclo como sempre).
# Declara-se com `--regressao-trivial <gate>:<gravidade>` (gravidade: medio ou baixo), uma vez por regressão, e cada uma conta dentro
# de --regressoes. Quem não cumpre as três continua regressão aberta.
GRAVIDADES_QUE_FECHAM = ("critico", "alto")
GRAVIDADES_TRIVIAIS = ("medio", "baixo")


def _sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn").lower().strip()


def _ler_triviais(brutos):
    """['imagens:medio'] -> ([(gate, gravidade)], erro). Erro só para entrada malformada (gate fora do catálogo, gravidade desconhecida)."""
    lidos = []
    for bruto in brutos or []:
        gate, sep, grav = str(bruto).partition(":")
        gate, grav = gate.strip(), _sem_acento(grav)
        if not sep or not gate or not grav:
            return None, f"--regressao-trivial '{bruto}': o formato é <gate>:<gravidade> (por exemplo imagens:medio)."
        if gate not in GATES:
            return None, f"--regressao-trivial '{bruto}': gate desconhecido '{gate}'. Validos: {', '.join(sorted(GATES))}."
        if grav not in GRAVIDADES_QUE_FECHAM + GRAVIDADES_TRIVIAIS:
            return None, f"--regressao-trivial '{bruto}': gravidade '{grav}' desconhecida. Use médio ou baixo (crítico e alto não são triviais)."
        lidos.append((gate, grav))
    return lidos, None


def _classificar_triviais(d, triviais):
    """Separa as declaradas em (consertadas, abertas). Aberta traz o motivo, que vai impresso."""
    corte = max((v.get("quando") or "" for v in d.get("lentes", {}).values()), default="")
    consertadas, abertas = [], []
    for gate, grav in triviais:
        reg = d.get("gates", {}).get(gate)
        refaz = f"Conserte e rode `rodar-gates.mjs --so {gate} --registrar-conserto`, depois feche a rodada de novo."
        if grav in GRAVIDADES_QUE_FECHAM:
            motivo = f"{gate} ({grav}): achado crítico ou alto do auditor não é regressão trivial e fecha o ciclo"
        elif not isinstance(reg, dict):
            motivo = f"{gate} ({grav}): o gate não tem registro na wave. {refaz}"
        elif reg.get("exit") != 0:
            motivo = f"{gate} ({grav}): o gate ainda reprova (exit {reg.get('exit')}). {refaz}"
        elif not reg.get("quando") or reg["quando"] < corte:
            motivo = (f"{gate} ({grav}): o registro do gate é de antes da auditoria desta rodada ({reg.get('quando') or 'sem hora'} contra "
                      f"{corte}), então não prova o conserto. {refaz}")
        else:
            consertadas.append({"gate": gate, "gravidade": grav})
            continue
        abertas.append(motivo)
    return consertadas, abertas


# REGRESSÃO SEM GATE (3.6.2, teste de aluno da 3.6.1). Duas regressões da rodada 2 (coluna sozinha no celular com 340 px vazios e o
# link "pular para o conteúdo" sem tabindex) nenhum gate do catálogo pega. O `--regressao-trivial` exige gate, então o ciclo fechou em
# NÃO ENTREGAR e a etapa 5 ficou sem saída. Regressão sem gate, de gravidade média ou baixa, também não fecha o ciclo quando as TRÊS valem:
#   1. foi consertada (a declaração diz que sim, com o motivo escrito);
#   2. foi conferida num print novo: o caminho está declarado, o arquivo existe, é imagem e a data dele é POSTERIOR à da última lente;
#   3. não é achado crítico nem alto do auditor.
# Declara-se com `--regressao-trivial-sem-gate "<descrição>:<medio|baixo>:<caminho-do-print>"`, uma vez por regressão, e conta dentro de --regressoes.
EXTENSOES_DE_PRINT = (".png", ".jpg", ".jpeg", ".webp")
EXEMPLO_SEM_GATE = '--regressao-trivial-sem-gate "coluna sozinha no celular:medio:prints/celular-depois.png"'


def _ler_sem_gate(brutos):
    """['coluna sozinha:medio:prints/x.png'] -> ([(descricao, gravidade, caminho)], erro). A descrição pode ter dois pontos: separa-se pelo fim."""
    lidos = []
    for bruto in brutos or []:
        partes = str(bruto).rsplit(":", 2)
        formato = f"--regressao-trivial-sem-gate '{bruto}': o formato é <descrição>:<medio|baixo>:<caminho-do-print>. Exemplo: {EXEMPLO_SEM_GATE}."
        if len(partes) != 3:
            return None, formato
        desc, grav, caminho = partes[0].strip(), _sem_acento(partes[1]), partes[2].strip()
        if not desc or not caminho:
            return None, formato
        if grav not in GRAVIDADES_QUE_FECHAM + GRAVIDADES_TRIVIAIS:
            return None, (f"--regressao-trivial-sem-gate '{bruto}': gravidade '{grav}' desconhecida. Use médio ou baixo "
                          f"(crítico e alto não são triviais). Exemplo: {EXEMPLO_SEM_GATE}.")
        lidos.append((desc, grav, caminho))
    return lidos, None


def _classificar_sem_gate(projeto, d, declaradas):
    """Separa as declaradas sem gate em (consertadas, abertas). Aberta traz o motivo e o próximo comando."""
    corte = max((v.get("quando") or "" for v in d.get("lentes", {}).values()), default="")
    base = Path(projeto)
    consertadas, abertas = [], []
    for desc, grav, caminho in declaradas:
        refaz = ("Tire o print de novo (`node <dir-da-skill>/scripts/screenshot-prova.js ... --com-360 --com-320`, ou o viewport que "
                 f"mostrou o defeito), confira com os olhos e feche a rodada de novo com {EXEMPLO_SEM_GATE}.")
        if grav in GRAVIDADES_QUE_FECHAM:
            abertas.append(f"{desc} ({grav}): achado crítico ou alto do auditor não é regressão trivial e fecha o ciclo")
            continue
        arq = Path(caminho)
        arq = arq if arq.is_absolute() else base / arq
        if not arq.is_file():
            abertas.append(f"{desc} ({grav}): o print '{caminho}' não existe. {refaz}")
        elif arq.suffix.lower() not in EXTENSOES_DE_PRINT:
            abertas.append(f"{desc} ({grav}): '{caminho}' não é uma imagem de print ({', '.join(EXTENSOES_DE_PRINT)}). {refaz}")
        else:
            feito = datetime.datetime.fromtimestamp(arq.stat().st_mtime).isoformat(timespec="seconds")
            if feito <= corte:
                abertas.append(f"{desc} ({grav}): o print '{caminho}' é de {feito}, antes da última lente ({corte}), então não prova o conserto. {refaz}")
            else:
                consertadas.append({"descricao": desc, "gravidade": grav, "print": caminho, "print_em": feito})
    return consertadas, abertas


TETO_RODADAS = 2
RODADAS_EXTRAS_MAX = 1
GANHO_MINIMO = 0.3


def cmd_rodada(args):
    """Fecha a rodada atual e diz se roda de novo ou entrega."""
    d = carregar(args.projeto)
    for campo in ("criticos", "altos", "regressoes", "pendencias_do_usuario"):
        valor = getattr(args, campo, None)
        if valor is not None and (type(valor) is not int or valor < 0):
            print("ERRO: contagens precisam ser inteiros não negativos.")
            return 2
    for registro in d.get("lentes", {}).values():
        nota = registro.get("nota")
        if nota is not None and (type(nota) not in (int, float) or not math.isfinite(nota) or not 0 <= nota <= 10):
            print("ERRO: nota precisa ser finita entre 0 e 10.")
            return 2
    # PENDENCIA DO USUARIO (teste com aluno, 02/10/2026): achado ALTO que so some com dado que
    # apenas o cliente tem (numero do WhatsApp, foto do espaco, CREFITO, depoimento). Sem este
    # campo o criterio "zero alto" nunca fica verdadeiro e o ciclo so solta pelo teto. Ele NAO
    # conta como alto, mas nunca apaga critico e vai DECLARADO na entrega, item por item.
    pend = getattr(args, "pendencias_do_usuario", 0) or 0
    altos_informados = getattr(args, "altos", None)
    if pend and (altos_informados is None or pend > altos_informados):
        print("ERRO: --pendencias-do-usuario conta altos que dependem do cliente, então precisa de "
              "--altos e não pode ser maior que ele.")
        return 2
    altos_reais = None if altos_informados is None else altos_informados - pend
    triviais, erro_trivial = _ler_triviais(getattr(args, "regressao_trivial", None))
    if erro_trivial:
        print("ERRO: " + erro_trivial, file=sys.stderr)
        return 2
    sem_gate, erro_sem_gate = _ler_sem_gate(getattr(args, "regressao_trivial_sem_gate", None))
    if erro_sem_gate:
        print("ERRO: " + erro_sem_gate, file=sys.stderr)
        return 2
    declaradas = len(triviais) + len(sem_gate)
    if declaradas > (getattr(args, "regressoes", 0) or 0):
        print(f"ERRO: {declaradas} regressão(ões) triviais declaradas (--regressao-trivial e --regressao-trivial-sem-gate) para "
              f"{getattr(args, 'regressoes', 0) or 0} --regressoes: cada uma conta dentro de --regressoes, então ele não pode ser menor.",
              file=sys.stderr)
        return 2
    # Fechar o ciclo sem os gates permitia imprimir ENTREGA para um processo incompleto.
    if cmd_checar(args) != 0:
        return 1
    hist = d.setdefault("rodadas", [])
    lentes = d.get("lentes", {})
    extra_pedida = bool(getattr(args, "rodada_extra_pedida", False))
    # REFECHAR (3.6.2): a última rodada fechou em NÃO ENTREGAR só por regressão aberta e a regressão foi consertada depois. O mesmo
    # fechamento se refaz com a declaração (a rodada é substituída, não nasce outra): sem isto o ciclo ficava sem comando que destrave.
    # Crítico aberto não entra aqui: ele pede a rodada extra da pessoa.
    if len(hist) >= TETO_RODADAS and hist[-1].get("bloqueio") == "regressao" and (triviais or sem_gate):
        extra_pedida = extra_pedida or bool(hist[-1].get("rodada_extra_pedida"))
        hist.pop()
        refechando = True
    else:
        refechando = False
    if len(hist) >= TETO_RODADAS:
        if not extra_pedida:
            print(f"ERRO: o ciclo já fechou em {len(hist)} rodada(s), o teto é {TETO_RODADAS}. Terceira rodada só "
                  "se a pessoa pedir, com --rodada-extra-pedida. Entregue com a nota real e as ressalvas.",
                  file=sys.stderr)
            if hist[-1].get("bloqueio") == "regressao":
                print("  A última rodada fechou em NÃO ENTREGAR por regressão aberta. Se você já a consertou, refaça o MESMO fechamento "
                      "declarando-a: com gate no catálogo, `--regressao-trivial <gate>:<medio|baixo>` (depois de "
                      "`rodar-gates.mjs --so <gate> --registrar-conserto`); sem gate, " + EXEMPLO_SEM_GATE + ".", file=sys.stderr)
            return 2
        if len(hist) >= TETO_RODADAS + RODADAS_EXTRAS_MAX:
            print(f"ERRO: não existe rodada além de {TETO_RODADAS + RODADAS_EXTRAS_MAX}, nem a pedido. "
                  "Entregue com a nota real e as ressalvas.", file=sys.stderr)
            return 2
    if not set(LENTES).issubset(lentes):
        print(f"ERRO: só {len(lentes)} de {len(LENTES)} lentes registradas. "
              "Rode a wave inteira antes de fechar a rodada.", file=sys.stderr)
        return 2

    notas = [v["nota"] for v in lentes.values() if v.get("nota") is not None]
    media = sum(notas) / len(notas) if notas else 0.0
    atual = {
        "n": len(hist) + 1,
        "quando": datetime.datetime.now().isoformat(timespec="seconds"),
        "media": round(media, 2),
        "criticos": args.criticos,
        "altos": altos_informados,
        "pendencias_do_usuario": pend,
        "rodada_extra_pedida": extra_pedida,
        "notas": {k: v.get("nota") for k, v in lentes.items()},
    }
    if refechando:
        atual["refechada"] = True
    # A31 (a): lentes que NÃO foram medidas de novo desde a rodada anterior mantêm a nota dela; a média não é medida nova.
    if hist:
        corte = hist[-1].get("quando", "")
        atual["mantidas"] = sorted(k for k, v in lentes.items() if (v.get("quando") or "") <= corte)
    hist.append(atual)
    salvar(args.projeto, d)

    def fechar(code, desfecho, ressalvas=None):
        """Grava o desfecho da rodada (o gate-etapas.py registrar 5 lê daqui: NÃO ENTREGAR não vira entrega pronta)."""
        if desfecho == "CONTINUA" and atual["n"] < TETO_RODADAS and (ref.get("gosto") in GOSTOS):
            proj = Path(args.projeto).as_posix()
            print("  RODADA 2 = CONFERÊNCIA DIRIGIDA (3 min, 4 chamadas, sem nota nova). Salve os achados em auditoria/achados-rodada-1.json, corrija,")
            print("  tire o print novo de cada crítico e alto e junte o pacote:")
            print(f"    {comando('pacote-auditoria.py')} --projeto {proj} --url <url> --rodada 2")
            print(f"  Depois da resposta: {comando('wave.py')} --projeto {proj} conferencia --arquivo auditoria/resposta-rodada-2.json\n")
        atual["desfecho"] = desfecho
        if desfecho.startswith("ENTREGA"):
            fidel = ressalvas_de_fidelidade(d.get("gates", {}), getattr(args, "caminho", "criar"))
            if fidel:
                ressalvas = list(ressalvas or []) + fidel
                print("  Ressalvas por fidelidade (vão escritas na entrega):")
                for r_ in fidel:
                    print(f"    - {r_}")
        if ressalvas:
            atual["ressalvas"] = ressalvas
        salvar(args.projeto, d)
        return code

    print(f"\nRODADA {atual['n']}  média {media:.2f}  críticos confirmados: {args.criticos}")
    mant = atual.get("mantidas") or []
    if mant:
        print(f"  nota da rodada {atual['n'] - 1} mantida: {', '.join(mant)}")
        print(f"  média da rodada {atual['n']} mistura {len(lentes) - len(mant)} lente(s) medida(s) de novo e {len(mant)} nota(s) mantida(s) da rodada anterior: "
              "não é uma medida nova das lentes que ninguém olhou outra vez.")
    print("=" * 74)
    for r in hist:
        print(f"  rodada {r['n']}: média {r['media']:.2f}, {r['criticos']} crítico(s)")
    # A27: aviso (não reprovação) quando o auditor passou do orçamento da rodada.
    # 3.7.0: na rodada 2 as lentes de nota mantida guardam o gasto da rodada 1 e não entram na conta; vale o da conferência.
    mantidas_agora = set(atual.get("mantidas") or [])
    gastos = [v for k, v in lentes.items() if k not in mantidas_agora
              and (v.get("duracao_min") is not None or v.get("chamadas") is not None)]
    if atual["n"] >= 2:
        corte_conf = hist[-2].get("quando", "") if len(hist) >= 2 else ""
        gastos += [c for c in d.get("conferencias", []) if isinstance(c, dict) and (c.get("quando") or "") > corte_conf]
    if gastos:
        dur = max((v.get("duracao_min") or 0) for v in gastos)
        cham = max((v.get("chamadas") or 0) for v in gastos)
        max_min, max_cham = ORCAMENTO.get(atual["n"], ORCAMENTO[2])
        if dur > max_min or cham > max_cham:
            print(f"  AVISO: a rodada {atual['n']} passou do orçamento do auditor: {dur:g} min e {cham} chamadas contra "
                  f"{max_min} min e {max_cham} chamadas. Não reprova, mas o briefing manda devolver 'não verificado' por lente "
                  "em vez de estourar o tempo e proíbe recapturar o que já está no pacote.")

    # 2. REGRESSAO = achado NOVO causado por correcao minha, nao nota que caiu.
    #
    # A primeira versao disto comparava a nota de cada lente com a da rodada anterior. Parece
    # obvio e esta ERRADO, e custou uma rodada inteira pra ficar claro: cada rodada sorteia
    # auditores independentes, e a nota deles nao e uma medida calibrada, e um julgamento. Na
    # rodada 4 desta pagina a wave gastou 446 chamadas de ferramenta contra uma fracao disso nas
    # anteriores (a lente de a11y mediu contraste no pixel composto de 89 nos de texto, viewport
    # a viewport) e TODAS as oito notas cairam, com a media indo de 6,88 pra 6,19. A pagina nao
    # tinha piorado: a REGUA tinha ficado mais fina. Com o criterio antigo isso e regressao em
    # oito lentes e o ciclo nunca fecha, que e exatamente o "ficar travado" que o dono proibiu.
    #
    # O que e comparavel entre rodadas e o ACHADO, porque ele vem com medida e local. Entao
    # regressao passa a ser declarada: quantos achados confirmados desta rodada foram CAUSADOS
    # por uma correcao da rodada anterior. Isso e verificavel (da pra apontar o commit) e nao
    # depende de quem auditou. A queda de nota continua sendo impressa, como sinal, nunca como
    # trava.
    regrediu = []
    consertadas, abertas = _classificar_triviais(d, triviais)
    sg_consertadas, sg_abertas = _classificar_sem_gate(args.projeto, d, sem_gate)
    abertas = abertas + sg_abertas
    restantes = (getattr(args, "regressoes", 0) or 0) - len(consertadas) - len(sg_consertadas)
    if restantes > 0:
        regrediu = [f"{restantes} achado(s) confirmado(s) causado(s) por correção da rodada anterior"] + abertas
    if consertadas:
        atual["regressoes_triviais"] = consertadas
        salvar(args.projeto, d)
        print("-" * 74)
        print(f"  REGRESSÃO TRIVIAL CONSERTADA (não fecha o ciclo): {len(consertadas)}")
        for c in consertadas:
            print(f"    - gate {c['gate']} ({c['gravidade']}): verde depois da auditoria; sem crítico nem alto. Vai na entrega como regressão consertada.")
    if sg_consertadas:
        atual["regressoes_sem_gate"] = sg_consertadas
        salvar(args.projeto, d)
        print("-" * 74)
        print(f"  REGRESSÃO SEM GATE CONSERTADA (não fecha o ciclo): {len(sg_consertadas)}")
        for c in sg_consertadas:
            print(f"    - {c['descricao']} ({c['gravidade']}): print novo {c['print']} ({c['print_em']}), depois da última lente; sem crítico nem alto. "
                  "Vai na entrega como regressão consertada, sem gate do catálogo, com o print que a prova.")
    caiu = []
    if len(hist) >= 2:
        ant = hist[-2]["notas"]
        for k, v in atual["notas"].items():
            if v is not None and ant.get(k) is not None and v < ant[k] - 0.01:
                caiu.append(f"{k} {ant[k]} -> {v}")

    ganho = (hist[-1]["media"] - hist[-2]["media"]) if len(hist) >= 2 else None
    convergiu = (len(hist) >= 3
                 and (hist[-1]["media"] - hist[-2]["media"]) < GANHO_MINIMO
                 and (hist[-2]["media"] - hist[-3]["media"]) < GANHO_MINIMO)
    # Porta de saida que nao depende de nota nenhuma: a gravidade secou. Zero critico e zero
    # alto confirmados quer dizer que o que sobrou e acabamento, e acabamento nao segura entrega.
    # Sem isto, uma rodada com auditores mais duros pode empurrar a media pra baixo pra sempre.
    secou = args.criticos == 0 and altos_reais == 0

    if caiu:
        print("-" * 74)
        print("  SINAL (não trava): notas que cairam em relacao a rodada anterior:")
        for c in caiu:
            print(f"    - {c}")
        print("  Auditor de cada rodada é sorteado de novo: nota que cai pode ser régua mais fina,")
        print("  não é página pior. O que trava é achado NOVO causado por correção (--regressoes).")

    print("-" * 74)
    ref = lentes.get(LENTE_REFERENCIAS, {})
    teto_efetivo = TETO_RODADAS + (RODADAS_EXTRAS_MAX if any(r.get("rodada_extra_pedida") for r in hist) else 0)
    no_teto = len(hist) >= teto_efetivo
    ref_ruim = ref.get("veredito") == "reprovado" or ref.get("gosto") == "correto"
    eixos_ref = ref.get("eixos_abaixo") or list(EIXOS)
    if ref.get("gosto") not in GOSTOS:
        print("  SEM RESPOSTA DE GOSTO: a comparacao-referencias não respondeu se a página é bonita no nível das referências")
        print("  (--gosto bonito|correto). Sem isso a rodada não fecha.\n")
        return fechar(1, "CONTINUA")
    if ref_ruim and not no_teto and not secou:
        # A26: o teto é 2 rodadas e a segunda é só conferência, então reprovar esta lente NÃO manda reconstruir sozinha.
        quais = "os eixos abaixo das referências" if ref.get("eixos_abaixo") else "os 5 eixos (o auditor não disse quais ficaram abaixo; releia os achados da lente)"
        print("  ABAIXO DAS REFERÊNCIAS: a comparacao-referencias não respondeu que a página é bonita no nível")
        print(f"  das referências printadas no passo b (veredito: {ref.get('veredito')}, resposta: {ref.get('gosto')}).")
        print(f"  EIXOS a corrigir: {', '.join(eixos_ref)} ({quais}).")
        print("  CONTINUA: corrija esses eixos na página (cabe na correção entre as rodadas), refaça os gates que a correção toca")
        print("  (`rodar-gates.mjs --projeto <dir> --so <gate> --registrar-conserto`) e feche a rodada de conferência (`wave.py --projeto <dir> rodada --criticos <N> ...`).")
        print("  Nota alta nas outras lentes não compensa, e correta não basta.")
        print("  Refazer o plano visual e reconstruir é um ciclo novo: só se você pedir (custa mais que a rodada 2).\n")
        return fechar(1, "CONTINUA")
    # Na última rodada do ciclo a ordem é: 1) crítico ou regressão aberta = NÃO ENTREGAR; 2) senão, ENTREGA COM RESSALVAS
    # (a lente de referências reprovada entra na lista, com os eixos). "Voltar ao plano" nunca aparece como ordem (A30).
    if no_teto and args.criticos > 0:
        print(f"  NÃO ENTREGAR: crítico aberto. {args.criticos} crítico(s) confirmado(s) na rodada {len(hist)}, a última do ciclo.")
        print("  O teto de rodadas fecha o ciclo, não afrouxa crítico. Corrija o crítico, refaca os gates que ele")
        print("  toca e peça à pessoa uma rodada extra (--rodada-extra-pedida) ou entregue só depois de resolvido.")
        print("  Sessão não interativa (ninguém para autorizar a rodada extra): feche em NÃO ENTREGAR, liste na entrega cada correção")
        print("  feita DEPOIS do ciclo (achado, o que mudou, a medida que mostra o conserto) e peça a rodada extra por escrito. Nota de")
        print("  autoavaliação não libera. Se o dono pediu uma mudança GRANDE entre as rodadas, o certo era `wave.py reabrir --motivo`.\n")
        return fechar(1, "NAO_ENTREGAR")
    if no_teto and regrediu:
        print("  NÃO ENTREGAR: regressão aberta. A correção quebrou outra coisa e o ciclo não tem mais rodada:")
        for r in regrediu:
            print(f"    - {r}")
        print("  Conserte a regressão antes de entregar. O próximo comando depende de quem pega a regressão (médio ou baixo; crítico ou alto fecha o ciclo):")
        print("  - um gate do catálogo a pega (crédito de foto, folga de 2 px): conserte, rode só aquele gate")
        print("    (`rodar-gates.mjs --so <gate> --registrar-conserto`) e feche a MESMA rodada de novo com `--regressao-trivial <gate>:<gravidade>`.")
        print("  - nenhum gate a pega (coluna sozinha no celular, link sem tabindex): conserte, tire um print novo que mostre o conserto e feche a")
        print(f"    MESMA rodada de novo com {EXEMPLO_SEM_GATE}.")
        print("  Refechar substitui esta rodada, não abre a terceira. Crítico aberto não se refecha assim: pede a rodada extra da pessoa.\n")
        atual["bloqueio"] = "regressao"
        return fechar(1, "NAO_ENTREGAR")
    if args.criticos > 0:
        print(f"  CONTINUA: {args.criticos} crítico(s) confirmado(s). Crítico não negocia com média.")
        print("  Corrija os críticos e rode a wave de novo.\n")
        return fechar(1, "CONTINUA")
    if regrediu:
        print("  CONTINUA: houve REGRESSAO, a correção quebrou outra coisa:")
        for r in regrediu:
            print(f"    - {r}")
        print("  Conserte a regressão antes de seguir e rode a wave de novo. Se for média ou baixa e ela já estiver consertada, declare-a no")
        print("  fechamento: com gate no catálogo, `--regressao-trivial <gate>:<gravidade>`; sem gate, " + EXEMPLO_SEM_GATE + ".\n")
        return fechar(1, "CONTINUA")
    vai_entregar = ((media >= PISO_MEDIA and all(n >= PISO_NOTA for n in notas)) or secou or convergiu
                    or no_teto)
    auto = sorted(l for l, v in lentes.items()
                  if v.get("veredito") != "nao_aplicavel" and v.get("origem") not in ORIGENS_INDEPENDENTES)
    # 3.7.0 (item 1d): rodada 1 sem crítico nem alto confirmados não abre rodada 2 de auditor. Os gates de novo bastam.
    sem_conferencia = secou and not no_teto
    if vai_entregar and auto:
        print(f"  AUDITORIA INDEPENDENTE PENDENTE: {len(auto)} lente(s) registradas como autoavaliação")
        print(f"  ({', '.join(auto[:4])}{'...' if len(auto) > 4 else ''}). Nota de quem construiu não libera entrega.")
        print("  Rode a rodada com um subagente auditor independente (ou em outra sessão, sem o historico")
        print("  da construcao) e registre cada lente com --origem subagente ou sessao-independente.\n")
        return fechar(1, "AUDITORIA_PENDENTE")
    def avisar_sem_rodada_2():
        atual["sem_rodada_2"] = True
        print(f"  SEM RODADA 2 DE AUDITOR: a rodada {len(hist)} não achou crítico nem alto (o que sobra é médio e baixo).")
        print(f"  Corrija os médios e baixos que couberem, rode os gates de novo com a rodada completa (`{comando('rodar-gates.mjs')} --projeto {Path(args.projeto).as_posix()}{_caminho_no_comando(args)}`)")
        print("  e entregue com as ressalvas. A etapa 5 cobra todos os gates verdes registrados DEPOIS desta rodada.")
    if ref_ruim and (no_teto or sem_conferencia):
        if sem_conferencia:
            avisar_sem_rodada_2()
            print(f"  ENTREGA COM RESSALVAS: rodada {len(hist)}, sem crítico, sem alto e sem regressão.")
        else:
            print(f"  ENTREGA COM RESSALVAS: rodada {len(hist)}, a última do ciclo (teto {teto_efetivo}), sem crítico e sem regressão.")
        print(f"  Nota real: média {media:.2f}. Ela vai escrita na entrega, com o que sobrou:")
        ressalvas = [f"lente comparacao-referencias reprovada (resposta: {ref.get('gosto')}): eixos abaixo das referências: {', '.join(eixos_ref)}",
                     f"altos abertos: {altos_informados if altos_informados is not None else 'não informado'}" + (f" ({pend} dependem de dado do cliente)" if pend else "")]
        for r_ in ressalvas:
            print(f"    - {r_}")
        outras = [f"{k} (nota {v.get('nota')})" for k, v in sorted(lentes.items())
                  if k != LENTE_REFERENCIAS and (v.get("veredito") == "reprovado" or (v.get("nota") is not None and v["nota"] < PISO_NOTA))]
        if outras:
            ressalvas.append("outras lentes abaixo do piso ou reprovadas: " + ", ".join(outras))
            print("    - outras lentes abaixo do piso ou reprovadas: " + ", ".join(outras))
        print("    - refazer o plano visual e reconstruir é um ciclo novo: só se a pessoa pedir.\n")
        return fechar(0, "ENTREGA_COM_RESSALVAS", ressalvas)
    if media >= PISO_MEDIA and all(n >= PISO_NOTA for n in notas):
        if sem_conferencia:
            avisar_sem_rodada_2()
        print(f"  ENTREGA: média {media:.2f} no piso e nenhuma lente abaixo de {PISO_NOTA}.\n")
        return fechar(0, "ENTREGA")
    if secou:
        if sem_conferencia:
            avisar_sem_rodada_2()
        print("  ENTREGA COM NOTA DECLARADA: zero crítico e zero ALTO confirmados. O que sobrou")
        print(f"  é acabamento, e acabamento não segura entrega. A média {media:.2f} vai escrita na")
        print("  entrega, com a lista do que ficou aberto.")
        if pend:
            print(f"  {pend} alto(s) dependem de dado que só o cliente tem: vão em PENDENCIAS DECLARADAS,")
            print("  um por linha, com o que falta e onde entra na página. A página não recebe trafego")
            print("  enquanto o destino do lead estiver entre eles.")
        print()
        return fechar(0, "ENTREGA")
    if no_teto:
        print(f"  ENTREGA COM RESSALVAS: rodada {len(hist)}, a última do ciclo (teto {teto_efetivo}), sem crítico e sem regressão.")
        print(f"  Nota real: média {media:.2f}. Ela vai escrita na entrega, com o que sobrou:")
        ressalvas = [f"altos abertos: {altos_informados if altos_informados is not None else 'não informado'}"
                     + (f" ({pend} dependem de dado do cliente)" if pend else "") + f"; {altos_reais if altos_reais is not None else '?'} alto(s) de verdade"]
        print(f"    - {ressalvas[0]}")
        fracas = [f"{k} (nota {v.get('nota')}{', reprovada' if v.get('veredito') == 'reprovado' else ''})"
                  for k, v in sorted(lentes.items())
                  if v.get("veredito") == "reprovado" or (v.get("nota") is not None and v["nota"] < PISO_NOTA)]
        if fracas:
            ressalvas.append("lentes abaixo do piso ou reprovadas: " + ", ".join(fracas))
            print("    - lentes abaixo do piso ou reprovadas: " + ", ".join(fracas))
        print("    - o texto dos achados de cada lente esta em .wave-auditoria.json; copie para a entrega.")
        print("  Não existe terceira rodada sozinha: só se a pessoa pedir (--rodada-extra-pedida).\n")
        return fechar(0, "ENTREGA_COM_RESSALVAS", ressalvas)
    if convergiu:
        print(f"  ENTREGA COM NOTA DECLARADA: zero crítico, zero regressão, e a média parou de")
        print(f"  subir (últimos ganhos: {ganho:+.2f}). Insistir aqui caça canto minúsculo.")
        print(f"  A nota {media:.2f} VAI NA ENTREGA, escrita. Nota declarada e honesta;")
        print("  nota escondida atras de 'auditado' e que e nota do.\n")
        return fechar(0, "ENTREGA")
    faltam = teto_efetivo - len(hist)
    print(f"  CONTINUA: sem crítico, mas a média ({media:.2f}) ainda sobe e o piso é {PISO_MEDIA}.")
    ganho_texto = f"{ganho:+.2f}" if ganho is not None else "primeira rodada, sem comparação"
    print(f"  Ganho da última rodada: {ganho_texto}. Restam {faltam} rodada(s) até o teto.\n")
    return fechar(1, "CONTINUA")


# ============================ A CONFERÊNCIA (rodada 2) ============================
# 3.7.0, item 1c. No teste de aluno da 3.6.2 a rodada 2 levou 662 s e 10 chamadas e só devolveu "corrigido ou não", com nota
# nova de 9 lentes que ninguém mediu de novo. Agora ela é dirigida: o pacote numera os achados críticos e altos abertos
# (`auditoria/abertos-rodada-1.json`, do `pacote-auditoria.py --rodada 2`), com o print novo de cada um e o diff da dist; o
# auditor devolve um estado por número, SEM nota; e este comando conta o que ficou aberto e imprime o fechamento.
ESTADOS_CONFERENCIA = {"corrigido": "corrigido", "naocorrigido": "não corrigido", "regressao": "regressão"}   # chave sem acento e sem espaço
SEVERIDADES = ("critico", "alto", "medio", "baixo")


def _doc_da_conferencia(texto):
    try:
        doc = json.loads(texto)
    except ValueError:
        doc = None
        dec, i = json.JSONDecoder(), 0
        while i < len(texto):
            if texto[i] == "{":
                try:
                    obj, fim = dec.raw_decode(texto, i)
                    if isinstance(obj, dict) and isinstance(obj.get("achados"), list):
                        doc = obj
                        break
                    i = fim
                    continue
                except ValueError:
                    pass
            i += 1
    if isinstance(doc, list):
        doc = {"achados": doc}
    return doc if isinstance(doc, dict) and isinstance(doc.get("achados"), list) else None


def cmd_conferencia(args):
    """Lê a resposta da conferência (rodada 2), conta crítico, alto e regressão que ficaram abertos e diz o comando do fechamento."""
    d = carregar(args.projeto)
    hist = d.get("rodadas") or []
    proj = Path(args.projeto).as_posix()
    if not hist or hist[-1].get("desfecho") != "CONTINUA":
        print("ERRO: a conferência é a rodada 2 e só existe depois que a rodada 1 fechou em CONTINUA (crítico ou alto). "
              f"Feche a rodada 1 antes: `{comando('wave.py')} --projeto {proj} rodada --criticos <N> --altos <N> ...`.", file=sys.stderr)
        return 2
    lista_arq = Path(args.projeto) / "auditoria" / "abertos-rodada-1.json"
    try:
        abertos = json.loads(lista_arq.read_text(encoding="utf-8-sig")).get("abertos") or []
    except (OSError, ValueError, AttributeError):
        print(f"ERRO: não achei a lista numerada dos achados abertos ({lista_arq.as_posix()}). Ela sai do "
              f"`{comando('pacote-auditoria.py')} --projeto {proj} --url <url> --rodada 2`.", file=sys.stderr)
        return 2
    por_n = {a.get("n"): a for a in abertos if isinstance(a, dict) and type(a.get("n")) is int}
    texto, erro = _ler_json_do_arquivo(args.arquivo, args.projeto)
    if erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 2
    doc = _doc_da_conferencia(texto)
    if doc is None:
        print("ERRO: a resposta da conferência é o JSON do schema do briefing: `rodada` 2 e `achados`, um item por número, com `n`, `estado` e `evidencia`.", file=sys.stderr)
        return 2
    problemas, estados, regressoes = [], {}, []
    for i, it in enumerate(doc["achados"], 1):
        if not isinstance(it, dict):
            problemas.append(f"item {i}: precisa ser um objeto")
            continue
        estado = ESTADOS_CONFERENCIA.get(_sem_acento(it.get("estado") or "").replace(" ", ""))
        n = it.get("n")
        evid = str(it.get("evidencia") or "").strip()
        if estado is None:
            problemas.append(f"item {i}: estado '{it.get('estado')}' desconhecido. Use corrigido, não corrigido ou regressão")
        elif len(evid) < 10:
            problemas.append(f"item {i}: a evidência é obrigatória (o print novo, a medida ou a linha do diff)")
        elif estado == "regressão":
            grav = _sem_acento(it.get("gravidade") or it.get("severidade") or "")
            if grav not in SEVERIDADES:
                problemas.append(f"item {i}: regressão precisa de \"gravidade\" (crítico, alto, médio ou baixo)")
            else:
                regressoes.append({"n": n, "gravidade": grav, "evidencia": evid})
                if n in por_n:
                    estados[n] = estado
        elif n not in por_n:
            problemas.append(f"item {i}: n={n!r} não está na lista numerada dos achados abertos ({', '.join(str(k) for k in sorted(por_n))})")
        else:
            estados[n] = estado
    if problemas:
        for p_ in problemas:
            print("ERRO: " + p_, file=sys.stderr)
        print("Nada foi gravado.", file=sys.stderr)
        return 2
    nao_conferidos = sorted(n for n in por_n if n not in estados)
    abertos_sev = [_sem_acento(por_n[n].get("severidade")) for n in por_n if estados.get(n) != "corrigido" and estados.get(n) != "regressão"]
    criticos = abertos_sev.count("critico") + sum(1 for r in regressoes if r["gravidade"] == "critico")
    altos = abertos_sev.count("alto") + sum(1 for r in regressoes if r["gravidade"] == "alto")
    dur = args.duracao_min if args.duracao_min is not None else _numero_ou_none(doc.get("duracao_min"))
    cham = args.chamadas if args.chamadas is not None else (doc.get("chamadas") if type(doc.get("chamadas")) is int else None)
    registro = {"rodada": len(hist) + 1, "quando": datetime.datetime.now().isoformat(timespec="seconds"),
                "estados": {str(k): v for k, v in sorted(estados.items())}, "nao_conferidos": nao_conferidos,
                "regressoes": regressoes, "abertos": {"criticos": criticos, "altos": altos, "regressoes": len(regressoes)}}
    if dur is not None:
        registro["duracao_min"] = dur
    if cham is not None:
        registro["chamadas"] = cham
    d.setdefault("conferencias", []).append(registro)
    salvar(args.projeto, d)
    tem_nota = any(k in doc for k in ("score", "nota", "notas")) or any(isinstance(it, dict) and ("score" in it or "nota" in it) for it in doc["achados"])
    print(f"CONFERÊNCIA (rodada {registro['rodada']}): {len(por_n)} achado(s) crítico(s) e alto(s) na lista; "
          f"{sum(1 for v in estados.values() if v == 'corrigido')} corrigido(s), {sum(1 for v in estados.values() if v == 'não corrigido')} não corrigido(s), "
          f"{len(regressoes)} regressão(ões).")
    if nao_conferidos:
        print(f"  não conferido(s) pelo auditor: {', '.join(str(n) for n in nao_conferidos)}. Contam como abertos, com a severidade da rodada 1.")
    if tem_nota:
        print("  A conferência é sem nota nova: ignorei a nota da resposta. As notas da rodada 1 ficam e vão escritas na entrega.")
    max_min, max_cham = ORCAMENTO[2]
    if (dur or 0) > max_min or (cham or 0) > max_cham:
        print(f"  AVISO: a conferência gastou {dur if dur is not None else '?'} min e {cham if cham is not None else '?'} chamadas, contra {max_min} min e {max_cham} chamadas.")
    print("  Feche a rodada (confira cada achado aberto antes; regressão média ou baixa já consertada entra com --regressao-trivial ou --regressao-trivial-sem-gate):")
    print(f"    {comando('wave.py')} --projeto {proj} rodada --criticos {criticos} --altos {altos} --regressoes {len(regressoes)} --pendencias-do-usuario <N>")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", default=os.getcwd())
    ap.add_argument("--caminho", default="criar", choices=CAMINHOS,
                    help="clonar (clone fiel) dispensa o gate de referências; os outros exigem")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("registrar", help="registra o resultado de UMA lente")
    r.add_argument("lente", choices=sorted(LENTES))
    r.add_argument("--nota", type=float)
    r.add_argument("--veredito", choices=["aprovado", "reprovado", "nao_aplicavel"], required=True)
    r.add_argument("--achados", required=True, help="o que foi olhado e o que foi encontrado")
    r.add_argument("--gosto", choices=GOSTOS, default=None,
                   help="só na comparacao-referencias, obrigatório: a página é bonita no nível das "
                        "referências, ou só está correta? 'correto' reprova e volta ao plano visual")
    r.add_argument("--eixos-abaixo", dest="eixos_abaixo", default=None,
                   help="só na comparacao-referencias reprovada: os eixos abaixo das referências (`composicao`, `tipografia`, `imagem`, `ritmo`, `acabamento`)")
    r.add_argument("--duracao-min", dest="duracao_min", type=float, default=None,
                   help="minutos que o auditor levou na rodada (a maior duração entre as lentes vale no aviso de orçamento)")
    r.add_argument("--chamadas", type=int, default=None, help="chamadas de ferramenta do auditor na rodada")
    r.add_argument("--origem", choices=ORIGENS, default="autoavaliacao",
                   help="quem auditou: subagente independente, outra sessão, outra pessoa ou "
                        "autoavaliação (padrão). Autoavaliação nunca libera entrega")
    r.set_defaults(func=cmd_registrar)

    g = sub.add_parser("gate", help="registra o resultado de um gate executavel")
    g.add_argument("nome", choices=sorted(GATES))
    g.add_argument("--exit", dest="exit_code", type=int, required=True)
    g.add_argument("--detalhe", default="")
    g.set_defaults(func=cmd_gate)

    gl = sub.add_parser("gates-lote", help="registra vários gates de uma vez a partir de um JSON (o rodar-gates.mjs usa)")
    gl.add_argument("--arquivo", required=True, help='JSON {"gates": [{"nome": ..., "exit": 0, "detalhe": ...}]}')
    gl.set_defaults(func=cmd_gates_lote)

    rl = sub.add_parser("registrar-lote", help="registra as lentes direto da resposta do auditor (JSON do schema do briefing)")
    rl.add_argument("--arquivo", required=True, help="a resposta do auditor: lista, objeto {\"lentes\": [...]} ou blocos soltos entre fences")
    rl.add_argument("--origem", choices=ORIGENS, required=True, help="quem auditou (sem padrão: o lote declara de quem é a nota)")
    rl.add_argument("--duracao-min", dest="duracao_min", type=float, default=None, help="minutos do auditor (manda sobre o arquivo)")
    rl.add_argument("--chamadas", type=int, default=None, help="chamadas de ferramenta do auditor (manda sobre o arquivo)")
    rl.set_defaults(func=cmd_registrar_lote)

    cf = sub.add_parser("conferencia", help="rodada 2: lê a resposta da conferência dirigida (sem nota nova) e conta o que ficou aberto")
    cf.add_argument("--arquivo", required=True, help="a resposta do auditor no schema do briefing da rodada 2: um item por número, com `n`, `estado` e `evidencia`")
    cf.add_argument("--duracao-min", dest="duracao_min", type=float, default=None, help="minutos da conferência (manda sobre o arquivo)")
    cf.add_argument("--chamadas", type=int, default=None, help="chamadas de ferramenta da conferência (manda sobre o arquivo)")
    cf.set_defaults(func=cmd_conferencia)

    c = sub.add_parser("checar", help="AUDITOR MASTER: o processo aconteceu inteiro?")
    c.set_defaults(func=cmd_checar)

    ro = sub.add_parser("rodada", help="fecha a rodada e decide: roda de novo ou entrega?")
    ro.add_argument("--criticos", type=int, required=True,
                    help="quantos achados CRÍTICOS sobreviveram a verificação adversarial")
    ro.add_argument("--altos", type=int, default=None,
                    help="quantos achados ALTOS sobreviveram. Zero crítico + zero alto fecha o "
                         "ciclo mesmo sem o piso de media: o que sobra e acabamento")
    ro.add_argument("--pendencias-do-usuario", dest="pendencias_do_usuario", type=int, default=0,
                    help="quantos dos --altos só somem com dado que apenas o cliente tem (número do "
                         "WhatsApp, foto do espaço, credencial). Não contam como alto, vão declarados "
                         "na entrega e nunca apagam crítico")
    ro.add_argument("--regressoes", type=int, default=0,
                    help="quantos achados confirmados desta rodada foram CAUSADOS por uma "
                         "correção da rodada anterior. E isto que trava o ciclo, não nota que "
                         "caiu: cada rodada sorteia auditor novo e a nota não e calibrada")
    ro.add_argument("--regressao-trivial", dest="regressao_trivial", action="append", default=None, metavar="GATE:GRAVIDADE",
                    help="regressão TRIVIAL já consertada, uma por uso, e conta dentro de --regressoes. Só vale se um gate do catálogo "
                         "a pega, o gate está verde na wave com registro posterior à auditoria e a gravidade é medio ou baixo "
                         "(crítico ou alto fecha o ciclo). Exemplo: --regressao-trivial imagens:medio")
    ro.add_argument("--regressao-trivial-sem-gate", dest="regressao_trivial_sem_gate", action="append", default=None,
                    metavar="DESCRICAO:GRAVIDADE:PRINT",
                    help="regressão média ou baixa que NENHUM gate do catálogo pega, já consertada, uma por uso, e conta dentro de "
                         "--regressoes. Vale se o print do conserto existe (caminho no projeto ou absoluto), é imagem e é mais novo que a "
                         "última lente. Fica na entrega com o motivo e o print. Exemplo: " + EXEMPLO_SEM_GATE.replace("--regressao-trivial-sem-gate ", ""))
    ro.add_argument("--rodada-extra-pedida", dest="rodada_extra_pedida", action="store_true",
                    help="a PESSOA pediu uma terceira rodada. Fica registrada no historico; a terceira "
                         "também fecha sempre e nunca existe quarta")
    ro.set_defaults(func=cmd_rodada)

    rb = sub.add_parser("reabrir", help="mudança grande pedida pelo dono ENTRE as rodadas: reabre a rodada 1 (uma vez por ciclo)")
    rb.add_argument("--motivo", required=True, help="o que o dono pediu (fica registrado)")
    rb.set_defaults(func=cmd_reabrir)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
