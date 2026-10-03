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

As lentes rodam como subagentes independentes quando o ambiente permite. Quando nao
permite, a mesma checagem roda em sequencia, uma lente por vez, e o registro diz isso.

Uso:
    python3 scripts/wave.py --projeto <dir> registrar <lente> --nota 8.5 \\
        --veredito aprovado --achados "o que olhou e o que encontrou"
    python3 scripts/wave.py --projeto <dir> gate <nome> --exit 0 --detalhe "..."
    python3 scripts/wave.py --projeto <dir> checar        # o AUDITOR MASTER
    python3 scripts/wave.py --projeto <dir> --caminho clonar checar   # clone fiel: sem gate de referencias
    python3 scripts/wave.py --projeto <dir> rodada --criticos 0 --altos 4 --pendencias-do-usuario 2 --regressoes 0
"""
import argparse
import datetime
import json
import math
import os
import sys
from pathlib import Path

REGISTRO = ".wave-auditoria.json"

# As NOVE lentes. Nenhuma e opcional: a que nao se aplica se registra com veredito
# "nao_aplicavel" e o motivo, e isso aparece no relatorio final. A exceção é a
# comparacao-referencias, que sempre se aplica.
LENTES = {
    "design-critic": "taste e anti-slop: tells visuais de IA, cara de template",
    "assets-auditor": "imagem, mockup e video reais (nao so texto, gradiente e SVG)",
    "visual-auditor": "hierarquia, paleta, espacamento e grid de desktop",
    "motion-auditor": "scroll reveal, hover, entrada do heroi, microinteracao",
    "responsive-auditor": "as 12 telas: overflow, CTA na dobra, toque 44px, texto legivel",
    "cro-auditor": "CTA, formulario, oferta, message match, Hook/Story/Offer",
    "a11y-auditor": "foco, label, alt, ARIA, contraste 4.5:1, zero emoji",
    "content-auditor": "dado inventado, claim sem fonte, travessao, consistencia de contato",
    "comparacao-referencias": "a pagina esta no nivel das referencias printadas no passo b?",
}
LENTE_REFERENCIAS = "comparacao-referencias"

# Gates EXECUTAVEIS que precisam estar verdes. Nao dependem de julgamento: rodam e saem 0 ou 1.
GATES = {
    "identidade": "screenshot-prova.js (title, description, favicon quadrado, og)",
    "oclusao": "gate-oclusao.mjs (texto coberto ou cortado)",
    "responsivo": "gate-responsivo.mjs (12 telas)",
    "uso-ferramentas": "uso-ferramentas.py (ferramenta viva foi usada)",
    "sem-kicker": "gate-sem-kicker.py (toda pagina sem kicker em caixa alta e sem numero decorativo)",
    "classes-mortas": "gate-classes-mortas.py (classe do codigo que nao existe no CSS gerado)",
    "referencias": "gate-referencias.py (6 prints reais lidos, 2 de cada tipo)",
    # Auditoria da v3 (02/10/2026): os quatro desenhos e afirmacoes que passaram por todos os
    # gates anteriores e derrubaram a pagina para 5,5 viraram medida.
    "simetria": "gate-simetria.mjs (itens paralelos em caixas iguais, colunas que terminam juntas)",
    "texto": "gate-texto.mjs (viuva em titulo e subtitulo de 320 a 1440, item em minuscula, italico colorido repetido)",
    "verdade": "gate-verdade.py (toda promessa com linha do briefing, inclusive nas metas)",
    "publicacao": "gate-publicacao.py (dist/ so com o que a pagina usa)",
    # Auditoria da v4 (02/10/2026, nota 6,5): defeitos que so aparecem na visita real ou fora
    # das telas e dos elementos que os gates mediam.
    "movimento": "gate-movimento.mjs (visita de 8 s parada no topo: nada anima fora da tela)",
    "composicao": "gate-composicao.mjs (mesmo esqueleto em mais de 2 secoes seguidas, icone de biblioteca)",
    "imagens": "gate-imagens.py (licenca com versao e link, direito de imagem, aviso no og-image)",
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


def gates_exigidos(caminho):
    # Clone fiel copia o texto da original: a fonte da verdade e a propria pagina, nao um briefing.
    return {g: d for g, d in GATES.items() if not (caminho == "clonar" and g in ("referencias", "verdade"))}

PISO_NOTA = 7.0
PISO_MEDIA = 8.0


def caminho(projeto):
    return Path(projeto) / REGISTRO


def carregar(projeto):
    p = caminho(projeto)
    if not p.exists():
        return {"lentes": {}, "gates": {}}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        d.setdefault("lentes", {})
        d.setdefault("gates", {})
        return d
    except (json.JSONDecodeError, OSError):
        return {"lentes": {}, "gates": {}}


def salvar(projeto, dados):
    caminho(projeto).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_registrar(args):
    if args.nota is not None and (not math.isfinite(args.nota) or not 0 <= args.nota <= 10):
        print("ERRO: nota precisa ser finita entre 0 e 10.", file=sys.stderr)
        return 2
    if args.lente not in LENTES:
        print(f"ERRO: lente desconhecida '{args.lente}'. Validas: {', '.join(sorted(LENTES))}",
              file=sys.stderr)
        return 2
    if args.lente == LENTE_REFERENCIAS and args.veredito == "nao_aplicavel":
        print("ERRO: a comparacao com as referencias sempre se aplica. No CLONAR, a referencia e a "
              "pagina original; nos outros caminhos, os prints do passo b.", file=sys.stderr)
        return 2
    if args.veredito != "nao_aplicavel" and (args.nota is None):
        print("ERRO: lente que rodou precisa de --nota", file=sys.stderr)
        return 2
    if len((args.achados or "").strip()) < 25:
        print("ERRO: --achados precisa dizer o que foi OLHADO e o que foi encontrado "
              "(>= 25 caracteres). 'ok' nao e auditoria.", file=sys.stderr)
        return 2
    d = carregar(args.projeto)
    d["lentes"][args.lente] = {
        "quando": datetime.datetime.now().isoformat(timespec="seconds"),
        "veredito": args.veredito,
        "nota": args.nota,
        "achados": args.achados.strip(),
        "origem": getattr(args, "origem", None) or "autoavaliacao",
    }
    salvar(args.projeto, d)
    print(f"lente registrada: {args.lente} -> {args.veredito} [{d['lentes'][args.lente]['origem']}]"
          + (f" (nota {args.nota})" if args.nota is not None else ""))
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

    gates_faltando = [g for g in exigidos if g not in gates]
    gates_vermelhos = [g for g, v in gates.items() if v.get("exit") != 0]

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
        else:
            print(f"    [{'verde ' if v['exit'] == 0 else 'VERMELHO'}] {nome:<18} {v['detalhe'][:50]}")

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
        print("         Reprovacao de lente e insumo do CICLO, nao trava do master.")
    if baixas:
        print("  SINAL: nota abaixo de %.1f: %s" % (PISO_NOTA, ", ".join(f"{l} ({n})" for l, n in baixas)))
    if notas and media < PISO_MEDIA:
        print(f"  SINAL: media {media:.2f} abaixo do piso {PISO_MEDIA}. Quem decide se isso entrega")
        print("         e `wave.py rodada`, e a nota vai DECLARADA na entrega.")

    if problemas:
        for p in problemas:
            print("  BLOQUEIA: " + p)
        print("\n  A ENTREGA ESTA BLOQUEADA. O master nao julga se a pagina esta bonita: ele")
        print("  julga se o PROCESSO aconteceu. Lente que nao rodou nao vira 'passou por")
        print("  omissao', e foi assim que uma pagina saiu testada em uma unica resolucao.\n")
        return 1

    print(f"  Todas as {len(LENTES)} lentes rodaram. Media {media:.2f}. Todos os gates verdes.")
    if na:
        print(f"  {len(na)} marcada(s) como nao aplicavel (o motivo esta no registro): {', '.join(na)}")
    print("  Processo completo. A decisao de entregar volta a ser sua.\n")
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
#      uso, mente pro visitante ou expoe o cliente. Isso nao se negocia com media.
#   2. NENHUMA REGRESSAO. Nenhuma lente pode ter caido em relacao a rodada anterior. Se
#      caiu, a correcao quebrou outra coisa e a rodada nao conta como avanco.
#   3. CONVERGENCIA ou PISO. Ou a media chegou ao piso (8,0), ou duas rodadas seguidas
#      subiram menos de 0,3: nesse ponto o retorno virou marginal e insistir e queimar
#      tempo pra caçar canto minusculo.
#
# Bateu 1 e 2 e convergiu? ENTREGA, com a nota real declarada na entrega. Nota 6,8 declarada
# e honesta; nota 6,8 escondida atras de "auditado" e que e nota do.
TETO_RODADAS = 4
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
        print("ERRO: --pendencias-do-usuario conta altos que dependem do cliente, entao precisa de "
              "--altos e nao pode ser maior que ele.")
        return 2
    altos_reais = None if altos_informados is None else altos_informados - pend
    # Fechar o ciclo sem os gates permitia imprimir ENTREGA para um processo incompleto.
    if cmd_checar(args) != 0:
        return 1
    hist = d.setdefault("rodadas", [])
    lentes = d.get("lentes", {})
    if not set(LENTES).issubset(lentes):
        print(f"ERRO: so {len(lentes)} de {len(LENTES)} lentes registradas. "
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
        "notas": {k: v.get("nota") for k, v in lentes.items()},
    }
    hist.append(atual)
    salvar(args.projeto, d)

    print(f"\nRODADA {atual['n']}  media {media:.2f}  criticos confirmados: {args.criticos}")
    print("=" * 74)
    for r in hist:
        print(f"  rodada {r['n']}: media {r['media']:.2f}, {r['criticos']} critico(s)")

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
    if getattr(args, "regressoes", 0):
        regrediu = [f"{args.regressoes} achado(s) confirmado(s) causado(s) por correcao da rodada anterior"]
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
        print("  SINAL (nao trava): notas que cairam em relacao a rodada anterior:")
        for c in caiu:
            print(f"    - {c}")
        print("  Auditor de cada rodada e sorteado de novo: nota que cai pode ser regua mais fina,")
        print("  nao pagina pior. O que trava e achado NOVO causado por correcao (--regressoes).")

    print("-" * 74)
    ref = lentes.get(LENTE_REFERENCIAS, {})
    if ref.get("veredito") == "reprovado":
        print("  VOLTA PRO PLANO VISUAL (passo c): a lente comparacao-referencias reprovou. A pagina")
        print("  nao esta no nivel das referencias printadas no passo b, e isso nao se resolve com")
        print("  nota alta nas outras lentes. Refaca o plano a partir das referencias e reconstrua.\n")
        return 1
    if args.criticos > 0:
        print(f"  CONTINUA: {args.criticos} critico(s) confirmado(s). Critico nao negocia com media.")
        print("  Corrija os criticos e rode a wave de novo.\n")
        return 1
    if regrediu:
        print("  CONTINUA: houve REGRESSAO, a correcao quebrou outra coisa:")
        for r in regrediu:
            print(f"    - {r}")
        print("  Conserte a regressao antes de seguir.\n")
        return 1
    vai_entregar = ((media >= PISO_MEDIA and all(n >= PISO_NOTA for n in notas)) or secou or convergiu
                    or len(hist) >= TETO_RODADAS)
    auto = sorted(l for l, v in lentes.items()
                  if v.get("veredito") != "nao_aplicavel" and v.get("origem") not in ORIGENS_INDEPENDENTES)
    if vai_entregar and auto:
        print(f"  AUDITORIA INDEPENDENTE PENDENTE: {len(auto)} lente(s) registradas como autoavaliacao")
        print(f"  ({', '.join(auto[:4])}{'...' if len(auto) > 4 else ''}). Nota de quem construiu nao libera entrega.")
        print("  Rode a rodada com um subagente auditor independente (ou em outra sessao, sem o historico")
        print("  da construcao) e registre cada lente com --origem subagente ou sessao-independente.\n")
        return 1
    if media >= PISO_MEDIA and all(n >= PISO_NOTA for n in notas):
        print(f"  ENTREGA: media {media:.2f} no piso e nenhuma lente abaixo de {PISO_NOTA}.\n")
        return 0
    if secou:
        print("  ENTREGA COM NOTA DECLARADA: zero critico e zero ALTO confirmados. O que sobrou")
        print(f"  e acabamento, e acabamento nao segura entrega. A media {media:.2f} vai escrita na")
        print("  entrega, com a lista do que ficou aberto.")
        if pend:
            print(f"  {pend} alto(s) dependem de dado que so o cliente tem: vao em PENDENCIAS DECLARADAS,")
            print("  um por linha, com o que falta e onde entra na pagina. A pagina nao recebe trafego")
            print("  enquanto o destino do lead estiver entre eles.")
        print()
        return 0
    if convergiu:
        print(f"  ENTREGA COM NOTA DECLARADA: zero critico, zero regressao, e a media parou de")
        print(f"  subir (ultimos ganhos: {ganho:+.2f}). Insistir aqui caça canto minusculo.")
        print(f"  A nota {media:.2f} VAI NA ENTREGA, escrita. Nota declarada e honesta;")
        print("  nota escondida atras de 'auditado' e que e nota do.\n")
        return 0
    if len(hist) >= TETO_RODADAS:
        print(f"  ENTREGA COM NOTA DECLARADA: teto de {TETO_RODADAS} rodadas atingido, sem critico")
        print(f"  e sem regressao. Media {media:.2f} vai declarada na entrega, junto com o que")
        print("  ficou em aberto e o custo estimado de cada item.\n")
        return 0
    faltam = TETO_RODADAS - len(hist)
    print(f"  CONTINUA: sem critico, mas a media ({media:.2f}) ainda sobe e o piso e {PISO_MEDIA}.")
    ganho_texto = f"{ganho:+.2f}" if ganho is not None else "primeira rodada, sem comparação"
    print(f"  Ganho da última rodada: {ganho_texto}. Restam {faltam} rodada(s) até o teto.\n")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", default=os.getcwd())
    ap.add_argument("--caminho", default="criar", choices=CAMINHOS,
                    help="clonar (clone fiel) dispensa o gate de referencias; os outros exigem")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("registrar", help="registra o resultado de UMA lente")
    r.add_argument("lente", choices=sorted(LENTES))
    r.add_argument("--nota", type=float)
    r.add_argument("--veredito", choices=["aprovado", "reprovado", "nao_aplicavel"], required=True)
    r.add_argument("--achados", required=True, help="o que foi olhado e o que foi encontrado")
    r.add_argument("--origem", choices=ORIGENS, default="autoavaliacao",
                   help="quem auditou: subagente independente, outra sessao, outra pessoa ou "
                        "autoavaliacao (padrao). Autoavaliacao nunca libera entrega")
    r.set_defaults(func=cmd_registrar)

    g = sub.add_parser("gate", help="registra o resultado de um gate executavel")
    g.add_argument("nome", choices=sorted(GATES))
    g.add_argument("--exit", dest="exit_code", type=int, required=True)
    g.add_argument("--detalhe", default="")
    g.set_defaults(func=cmd_gate)

    c = sub.add_parser("checar", help="AUDITOR MASTER: o processo aconteceu inteiro?")
    c.set_defaults(func=cmd_checar)

    ro = sub.add_parser("rodada", help="fecha a rodada e decide: roda de novo ou entrega?")
    ro.add_argument("--criticos", type=int, required=True,
                    help="quantos achados CRITICOS sobreviveram a verificacao adversarial")
    ro.add_argument("--altos", type=int, default=None,
                    help="quantos achados ALTOS sobreviveram. Zero critico + zero alto fecha o "
                         "ciclo mesmo sem o piso de media: o que sobra e acabamento")
    ro.add_argument("--pendencias-do-usuario", dest="pendencias_do_usuario", type=int, default=0,
                    help="quantos dos --altos so somem com dado que apenas o cliente tem (numero do "
                         "WhatsApp, foto do espaco, credencial). Nao contam como alto, vao declarados "
                         "na entrega e nunca apagam critico")
    ro.add_argument("--regressoes", type=int, default=0,
                    help="quantos achados confirmados desta rodada foram CAUSADOS por uma "
                         "correcao da rodada anterior. E isto que trava o ciclo, nao nota que "
                         "caiu: cada rodada sorteia auditor novo e a nota nao e calibrada")
    ro.set_defaults(func=cmd_rodada)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
