"""Bloqueia avanço sem artefatos de etapas anteriores ou após sua alteração.

Uso: node scripts/py.mjs gate-etapas.py --projeto DIR registrar ETAPA --arquivo JSON
     node scripts/py.mjs gate-etapas.py --projeto DIR checar ETAPA
O JSON contém campos obrigatórios e uma lista `arquivos` de evidências do projeto.
Valida presença, sequência e integridade. Julgamento de qualidade continua nas lentes.

Perfil `paginas` (v3, caminho CRIAR): 0 briefing, 1 referências (roda o
gate-referencias.py), 2 plano visual, 3 copy, 4 construção, 5 entrega.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lancador import comando  # noqa: E402

PAGINAS = {
    "0": ("briefing", "inventario", "pendencias_cliente"),
    "1": ("referencias",),
    "2": ("direcao", "tipografia", "paleta", "imagem", "ritmo", "assinatura", "referencias_usadas", "foto_publico", "secoes"),
    "3": ("copy", "aprovacao", "sustentacao"),
    "4": ("primeiro_bloco", "stack", "imagens"),
    "5": ("gates", "auditores", "claims", "contato", "passe_de_gosto", "prova", "video", "pendencias"),
}


def desfecho_do_ciclo(projeto):
    """Lê o que o `wave.py rodada` gravou na última rodada: (desfecho, ressalvas), ou (None, []) se não há ciclo registrado."""
    arq = projeto / ".wave-auditoria.json"
    if not arq.is_file():
        return None, []
    try:
        rodadas = json.loads(arq.read_text(encoding="utf-8-sig")).get("rodadas") or []
    except (OSError, ValueError, AttributeError):
        return None, []
    if not rodadas or not isinstance(rodadas[-1], dict):
        return None, []
    return rodadas[-1].get("desfecho"), list(rodadas[-1].get("ressalvas") or [])


def videos_da_prova(projeto, doc):
    """Etapa 5: a prova leva o vídeo da rolagem (gravar-video.js) junto dos prints, em desktop e celular."""
    v = doc.get("video")
    if not isinstance(v, dict) or not all(str(v.get(k) or "").strip() for k in ("desktop", "mobile")):
        raise ValueError(f"Etapa 5: `video` é {{desktop, mobile}}, os dois .webm gravados por {comando('gravar-video.js')} (prova junto dos prints).")
    achados = {}
    for perfil in ("desktop", "mobile"):
        p = (projeto / str(v[perfil])).resolve()
        if not p.is_relative_to(projeto) or p.suffix.lower() != ".webm":
            raise ValueError(f"Etapa 5: o vídeo de {perfil} precisa ser um .webm dentro do projeto.")
        if not p.is_file() or p.stat().st_size == 0:
            raise ValueError(f"Etapa 5: vídeo de {perfil} ausente ou vazio ({p.name}). Grave com {comando('gravar-video.js')}.")
        with p.open("rb") as f:
            if f.read(4).hex() != "1a45dfa3":
                raise ValueError(f"Etapa 5: {p.name} não é um WebM (cabeçalho EBML ausente).")
        achados[p.relative_to(projeto).as_posix()] = digest(p)
    return achados


def gate_de_referencias(projeto):
    """A etapa 1 so registra se o gate-referencias.py passar no mesmo projeto."""
    spec = importlib.util.spec_from_file_location("gref", Path(__file__).with_name("gate-referencias.py"))
    gref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gref)
    validas, problemas = gref.checar(projeto)
    if problemas:
        raise ValueError("Etapa 1: gate de referências reprovou: " + " | ".join(problemas[-3:]))
DASH = {
    "1": ("ambiente",),
    "2": ("operacao", "inventario"),
    "2.5": ("numero_heroi", "pergunta", "exclusoes", "accent", "densidade", "tema"),
    "3": ("modo_dados",),
    "4": ("conta_confirmada", "infra"),
    "5": ("primeiro_render", "mapeamento"),
    "6": ("prova_publicada", "passe_de_gosto", "pendencias"),
    "7": ("contexto",),
}
REGISTRO = ".etapas-verificadas.json"
# Metáforas de biblioteca de ícone (sem acento, depois de normalizar). Mesma lista do gate-composicao.mjs.
GENERICOS = r"balao|chat|calendario|agenda|check|sinal de visto|boneco|palito|estrela|coracao|lampada|foguete|alvo|engrenagem|cadeado|escudo|trofeu|medalha|sino|lupa|envelope|telefone|relogio|raio|polegar|joinha|aperto de mao|grafico subindo"


def normalizar(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def digest(p):
    if not p.is_file() or p.stat().st_size == 0:
        raise ValueError(f"Evidência ausente, vazia ou sem arquivo: {p.name}")
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validar(projeto, arquivo, etapa, campos, perfil):
    doc = json.loads(arquivo.read_text(encoding="utf-8-sig"))
    if not isinstance(doc, dict):
        raise ValueError("A evidência da etapa precisa ser um objeto JSON.")
    for campo in campos:
        if campo not in doc or doc[campo] in (None, "", [], {}):
            raise ValueError(f"Etapa {etapa}: falta {campo}")
    if perfil == "paginas" and etapa == "0":
        for campo in ("nicho", "local", "publico", "oferta", "preco", "acao"):
            if not isinstance(doc["briefing"], dict) or not doc["briefing"].get(campo):
                raise ValueError(f"Briefing incompleto: {campo}. Fato ausente deve constar como pendente, nunca inventado.")
    if perfil == "paginas" and etapa == "1":
        gate_de_referencias(projeto)
    # Auditoria da v3 (02/10/2026): modelo de 25 anos de top cropped para mulheres de 35 a 60, e
    # "faz a avaliação e começa" com a avaliação pendente no briefing. As duas decisões passam a
    # deixar rastro conferível: público -> foto -> por quê, e a tabela de sustentação da copy.
    if perfil == "paginas" and etapa == "2":
        fp = doc["foto_publico"]
        if not isinstance(fp, list) or not all(isinstance(i, dict) and all(str(i.get(k) or "").strip() for k in ("publico", "foto", "porque")) for i in fp):
            raise ValueError("Etapa 2: foto_publico é uma lista de {publico, foto, porque}, uma linha por foto de pessoa.")
    # Auditoria da v4 (02/10/2026): Situações, Como funciona, Duas formas e Dúvidas com o mesmo
    # esqueleto (h2 à esquerda + grade de caixas) e ícones de biblioteca (balão, calendário com
    # check, boneco de palito). O plano dá a cada seção um tratamento próprio, tirado de uma
    # referência, e diz o que cada desenho desenha.
    if perfil == "paginas" and etapa == "2":
        secoes = doc["secoes"]
        if not isinstance(secoes, list) or len(secoes) < 3 or not all(isinstance(s, dict) and all(str(s.get(k) or "").strip() for k in ("secao", "tratamento", "referencia")) for s in secoes):
            raise ValueError("Etapa 2: `secoes` é uma lista de {`secao`, `tratamento`, `referencia`}, uma linha por seção (3 ou mais).")
        norm = [normalizar(s["tratamento"]) for s in secoes]
        for i in range(len(norm) - 2):
            if norm[i] == norm[i + 1] == norm[i + 2]:
                raise ValueError(f"Etapa 2: '{secoes[i]['tratamento']}' em 3 seções seguidas ({secoes[i]['secao']}, {secoes[i + 1]['secao']}, {secoes[i + 2]['secao']}): cada seção ganha um tratamento próprio.")
        # v3.5.6: o plano visual declara o ícone do site; o aluno não descobre a linha só no passo e.4.
        pv = projeto / "plano-visual.md"
        if pv.is_file() and not re.search(r"(?im)^\W*[ií]cone do site\W*:[ \t]*(?!<[^>]*>\s*$)\S", pv.read_text(encoding="utf-8-sig")):
            raise ValueError("Etapa 2: plano-visual.md não declara 'Ícone do site: <motivo>' (o que o favicon desenha em 32 px).")
        for ic in doc.get("icones") or []:
            desenha = str((ic or {}).get("desenha") or "").strip() if isinstance(ic, dict) else ""
            if not desenha:
                raise ValueError("Etapa 2: `icones` é uma lista de {`secao`, `desenha`}.")
            if re.search(GENERICOS, normalizar(desenha)):
                raise ValueError(f"Etapa 2: ícone de biblioteca ('{desenha}'): desenhe o assunto da seção.")
    if perfil == "paginas" and etapa == "3":
        alvo = (projeto / str(doc["sustentacao"])).resolve()
        if not alvo.is_relative_to(projeto) or not alvo.is_file() or "|" not in alvo.read_text(encoding="utf-8-sig"):
            raise ValueError("Etapa 3: sustentacao aponta para a tabela 'frase da página -> linha do briefing' (evidencias/sustentacao.md).")
    if "passe_de_gosto" in campos:
        passe = doc["passe_de_gosto"]
        if not isinstance(passe, dict) or type(passe.get("antes")) is not int or passe["antes"] < 0 or type(passe.get("depois")) is not int or passe["depois"] != 0 or not passe.get("inspecao"):
            raise ValueError("Passe de gosto exige contagem antes, depois igual a zero e inspeção descrita.")
    arquivos = doc.get("arquivos")
    if not isinstance(arquivos, list) or not arquivos:
        raise ValueError("Liste em arquivos as evidências reais desta etapa.")
    hashes = {}
    if perfil == "paginas" and etapa == "5":
        # A31 (b): a etapa 5 é a entrega pronta. Ciclo que terminou em NÃO ENTREGAR (ou que ainda continua, ou com
        # auditoria independente pendente) não vira entrega registrada; ENTREGA COM RESSALVAS registra e guarda as ressalvas.
        desfecho, _ress = desfecho_do_ciclo(projeto)
        if desfecho in ("NAO_ENTREGAR", "CONTINUA", "AUDITORIA_PENDENTE"):
            nome = {"NAO_ENTREGAR": "NÃO ENTREGAR (crítico ou regressão aberta)", "CONTINUA": "CONTINUA (o ciclo ainda não fechou)",
                    "AUDITORIA_PENDENTE": "AUDITORIA INDEPENDENTE PENDENTE"}[desfecho]
            raise ValueError(f"Etapa 5: o ciclo de auditoria terminou em {nome}: não se registra a entrega como pronta. "
                             f"Corrija e rode de novo o `wave.py rodada` (ou peça a rodada extra), depois registre a etapa 5.")
        hashes.update(videos_da_prova(projeto, doc))
    for nome in arquivos:
        p = (projeto / nome).resolve()
        if not p.is_relative_to(projeto) or p == arquivo or p.name == REGISTRO:
            raise ValueError("A evidência precisa estar dentro do projeto e não pode ser o próprio registro.")
        hashes[p.relative_to(projeto).as_posix()] = digest(p)
    return hashes


def conferir(projeto, registro, etapas):
    for etapa in etapas:
        item = registro.get(etapa)
        if not isinstance(item, dict):
            raise ValueError(f"Etapa {etapa} não registrada. Conclua e registre antes de avançar.")
        for nome, esperado in item["hashes"].items():
            if digest(projeto / nome) != esperado:
                # A22: diz exatamente o que refazer, na ordem: esta etapa e as registradas depois dela.
                ordem = list(registro)
                afetadas = [e for e in ordem if e >= etapa] or [etapa]
                passos = []
                for e in afetadas:
                    hs = (registro.get(e) or {}).get("hashes") or {}
                    json_da_etapa = list(hs)[-1] if hs else f"evidencias/etapa-{e}.json"
                    passos.append(f"{comando('gate-etapas.py')} --projeto {projeto.as_posix()} registrar {e} --arquivo {json_da_etapa}")
                raise ValueError(f"Etapa {etapa}: evidência mudou ({nome}). Revalide esta etapa e as seguintes. "
                                 f"Se a mudança foi de propósito, refaça, nesta ordem: " + " ; ".join(passos)
                                 + ". Antes, confira o JSON de cada etapa (ele aponta para o arquivo mudado) e, se o arquivo é "
                                 "evidência de uma ferramenta, registre de novo com uso-ferramentas.py.")


BRIEFING_NOMES = {"briefing.md", "briefing.txt"}


def revalidar(projeto, registro, etapas, perfil, motivo):
    """Mudança de briefing no meio (A32). Caminho curto, que NÃO pula etapa.

    Para cada etapa registrada, em ordem: se nada mudou, fica como está; se SÓ o arquivo do briefing mudou, o gate da etapa
    (`validar`) roda de novo sobre o JSON registrado e, passando, a etapa é re-registrada com o motivo gravado; se QUALQUER
    outra evidência mudou (inclusive o JSON da etapa), a etapa continua exigindo o gate dela (`registrar`) e nada é gravado.
    Devolve (registro novo, linhas do relatório); levanta ValueError quando bloqueia."""
    novo, linhas = {e: dict(v) for e, v in registro.items()}, []
    for e in [x for x in etapas if x in registro]:
        hashes = registro[e].get("hashes") or {}
        mudou = [n for n, h in hashes.items() if digest(projeto / n) != h]
        if not mudou:
            linhas.append(f"  etapa {e}: intacta (nada mudou nos arquivos dela)")
            continue
        fora = [n for n in mudou if Path(n).name not in BRIEFING_NOMES]
        jsons = [n for n in hashes if n.endswith(".json")]
        if fora or not jsons:
            alvo = (jsons[-1] if jsons else f"evidencias/etapa-{e}.json")
            raise ValueError(f"Etapa {e}: a evidência mudou além do briefing ({', '.join(fora or mudou)}); esta etapa continua exigindo o gate dela. "
                             f"Refaça e registre: {comando('gate-etapas.py')} --projeto {projeto.as_posix()} registrar {e} --arquivo {alvo}")
        arquivo = (projeto / jsons[-1]).resolve()
        refeitos = validar(projeto, arquivo, e, etapas[e], perfil)       # o gate da etapa roda de novo
        refeitos[jsons[-1]] = digest(arquivo)
        novo[e] = {**novo[e], "hashes": refeitos, "revalidada": {"motivo": motivo, "arquivos": mudou,
                                                                 "quando": datetime.datetime.now().isoformat(timespec="seconds")}}
        linhas.append(f"  etapa {e}: revalidada (só o briefing mudou: {', '.join(mudou)}; o gate da etapa rodou de novo e passou)")
        if "sustentacao" in (json.loads(arquivo.read_text(encoding="utf-8-sig")) if arquivo.is_file() else {}):
            linhas.append(f"    atenção: a copy depende do briefing: rode {comando('gate-verdade.py')} --projeto {projeto.as_posix()} para conferir a tabela contra o briefing novo")
    return novo, linhas


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--projeto", type=Path, required=True)
    ap.add_argument("--perfil", choices=["paginas", "dash"], default="paginas")
    ap.add_argument("comando", choices=["registrar", "checar", "revalidar"])
    ap.add_argument("etapa", nargs="?")
    ap.add_argument("--arquivo", type=Path)
    ap.add_argument("--motivo", default=None, help="só no revalidar: por que o briefing mudou (fica gravado em cada etapa revalidada)")
    args = ap.parse_args()
    projeto = args.projeto.resolve()
    etapas = PAGINAS if args.perfil == "paginas" else DASH
    if args.comando == "revalidar":
        if len((args.motivo or "").strip()) < 15:
            print("ERRO: revalidar exige --motivo com pelo menos 15 caracteres (o que o cliente pediu de diferente).", file=sys.stderr)
            return 2
        try:
            alvo = projeto / REGISTRO
            registro = json.loads(alvo.read_text(encoding="utf-8-sig")) if alvo.exists() else {}
            if not isinstance(registro, dict) or not registro:
                raise ValueError("Não há etapa registrada para revalidar.")
            novo, linhas = revalidar(projeto, registro, etapas, args.perfil, args.motivo.strip())
        except (OSError, ValueError, KeyError, TypeError) as e:
            print(f"BLOQUEIA: {e}")
            return 1
        print("REVALIDAR (mudança de briefing)\n" + "\n".join(linhas))
        if novo == registro:
            print("  nada mudou: não há o que revalidar.")
            return 0
        alvo.write_text(json.dumps(novo, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"PASSA: etapas revalidadas em ordem; motivo gravado: {args.motivo.strip()}")
        return 0
    if args.etapa is None:
        ap.error("registrar e checar pedem a etapa")
    try:
        if args.etapa not in etapas:
            raise ValueError("Etapa desconhecida para este perfil.")
        alvo = projeto / REGISTRO
        registro = json.loads(alvo.read_text(encoding="utf-8-sig")) if alvo.exists() else {}
        if not isinstance(registro, dict):
            raise ValueError("Registro de etapas inválido.")
        ordem = list(etapas)
        indice = ordem.index(args.etapa)
        conferir(projeto, registro, ordem[:indice + (args.comando == "checar")])
        if args.comando == "registrar":
            if args.arquivo is None:
                raise ValueError("Use --arquivo com o JSON da etapa concluída.")
            arquivo = (projeto / args.arquivo).resolve()
            if not arquivo.is_relative_to(projeto):
                raise ValueError("O JSON precisa estar dentro do projeto.")
            hashes = validar(projeto, arquivo, args.etapa, etapas[args.etapa], args.perfil)
            hashes[arquivo.relative_to(projeto).as_posix()] = digest(arquivo)
            # Corrigir uma etapa invalida as seguintes; um resultado antigo não prova a versão nova.
            registro = {e: registro[e] for e in ordem[:indice]}
            registro[args.etapa] = {"hashes": hashes}
            if args.perfil == "paginas" and args.etapa == "5":
                desfecho, ressalvas = desfecho_do_ciclo(projeto)
                if desfecho == "ENTREGA_COM_RESSALVAS":
                    registro[args.etapa]["desfecho"] = desfecho
                    registro[args.etapa]["ressalvas"] = ressalvas
            alvo.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"PASSA: etapa {args.etapa}, sequência e integridade conferidas.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"BLOQUEIA: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
