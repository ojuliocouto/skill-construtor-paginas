"""Bloqueia avanço sem artefatos de etapas anteriores ou após sua alteração.

Uso: python3 scripts/gate-etapas.py --projeto DIR registrar ETAPA --arquivo JSON
     python3 scripts/gate-etapas.py --projeto DIR checar ETAPA
O JSON contém campos obrigatórios e uma lista `arquivos` de evidências do projeto.
Valida presença, sequência e integridade. Julgamento de qualidade continua nas lentes.

Perfil `paginas` (v3, caminho CRIAR): 0 briefing, 1 referências (roda o
gate-referencias.py), 2 plano visual, 3 copy, 4 construção, 5 entrega.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

PAGINAS = {
    "0": ("briefing", "inventario", "pendencias_cliente"),
    "1": ("referencias",),
    "2": ("direcao", "tipografia", "paleta", "imagem", "ritmo", "assinatura", "referencias_usadas", "foto_publico", "secoes"),
    "3": ("copy", "aprovacao", "sustentacao"),
    "4": ("primeiro_bloco", "stack", "imagens"),
    "5": ("gates", "auditores", "claims", "contato", "passe_de_gosto", "prova", "pendencias"),
}


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
GENERICOS = r"balao|chat|calendario|agenda|check|visto|boneco|palito|estrela|coracao|lampada|foguete|alvo|engrenagem|cadeado|escudo|trofeu|medalha|sino|lupa|envelope|telefone|relogio|raio|polegar|joinha|aperto de mao|grafico subindo"


def normalizar(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def digest(p):
    if not p.is_file() or p.stat().st_size == 0:
        raise ValueError(f"Evidência ausente, vazia ou sem arquivo: {p.name}")
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validar(projeto, arquivo, etapa, campos, perfil):
    doc = json.loads(arquivo.read_text())
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
            raise ValueError("Etapa 2: secoes é uma lista de {secao, tratamento, referencia}, uma linha por seção (3 ou mais).")
        norm = [normalizar(s["tratamento"]) for s in secoes]
        for i in range(len(norm) - 2):
            if norm[i] == norm[i + 1] == norm[i + 2]:
                raise ValueError(f"Etapa 2: '{secoes[i]['tratamento']}' em 3 seções seguidas ({secoes[i]['secao']}, {secoes[i + 1]['secao']}, {secoes[i + 2]['secao']}): cada seção ganha um tratamento próprio.")
        for ic in doc.get("icones") or []:
            desenha = str((ic or {}).get("desenha") or "").strip() if isinstance(ic, dict) else ""
            if not desenha:
                raise ValueError("Etapa 2: icones é uma lista de {secao, desenha}.")
            if re.search(GENERICOS, normalizar(desenha)):
                raise ValueError(f"Etapa 2: ícone de biblioteca ('{desenha}'): desenhe o assunto da seção.")
    if perfil == "paginas" and etapa == "3":
        alvo = (projeto / str(doc["sustentacao"])).resolve()
        if not alvo.is_relative_to(projeto) or not alvo.is_file() or "|" not in alvo.read_text(encoding="utf-8"):
            raise ValueError("Etapa 3: sustentacao aponta para a tabela 'frase da página -> linha do briefing' (evidencias/sustentacao.md).")
    if "passe_de_gosto" in campos:
        passe = doc["passe_de_gosto"]
        if not isinstance(passe, dict) or type(passe.get("antes")) is not int or passe["antes"] < 0 or type(passe.get("depois")) is not int or passe["depois"] != 0 or not passe.get("inspecao"):
            raise ValueError("Passe de gosto exige contagem antes, depois igual a zero e inspeção descrita.")
    arquivos = doc.get("arquivos")
    if not isinstance(arquivos, list) or not arquivos:
        raise ValueError("Liste em arquivos as evidências reais desta etapa.")
    hashes = {}
    for nome in arquivos:
        p = (projeto / nome).resolve()
        if not p.is_relative_to(projeto) or p == arquivo or p.name == REGISTRO:
            raise ValueError("A evidência precisa estar dentro do projeto e não pode ser o próprio registro.")
        hashes[str(p.relative_to(projeto))] = digest(p)
    return hashes


def conferir(projeto, registro, etapas):
    for etapa in etapas:
        item = registro.get(etapa)
        if not isinstance(item, dict):
            raise ValueError(f"Etapa {etapa} não registrada. Conclua e registre antes de avançar.")
        for nome, esperado in item["hashes"].items():
            if digest(projeto / nome) != esperado:
                raise ValueError(f"Etapa {etapa}: evidência mudou ({nome}). Revalide esta etapa e as seguintes.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--projeto", type=Path, required=True)
    ap.add_argument("--perfil", choices=["paginas", "dash"], default="paginas")
    ap.add_argument("comando", choices=["registrar", "checar"])
    ap.add_argument("etapa")
    ap.add_argument("--arquivo", type=Path)
    args = ap.parse_args()
    projeto = args.projeto.resolve()
    etapas = PAGINAS if args.perfil == "paginas" else DASH
    try:
        if args.etapa not in etapas:
            raise ValueError("Etapa desconhecida para este perfil.")
        alvo = projeto / REGISTRO
        registro = json.loads(alvo.read_text()) if alvo.exists() else {}
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
            hashes[str(arquivo.relative_to(projeto))] = digest(arquivo)
            # Corrigir uma etapa invalida as seguintes; um resultado antigo não prova a versão nova.
            registro = {e: registro[e] for e in ordem[:indice]}
            registro[args.etapa] = {"hashes": hashes}
            alvo.write_text(json.dumps(registro, ensure_ascii=False, indent=2))
        print(f"PASSA: etapa {args.etapa}, sequência e integridade conferidas.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"BLOQUEIA: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
