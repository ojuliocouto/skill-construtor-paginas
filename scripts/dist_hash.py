# -*- coding: utf-8 -*-
"""Hash do CONTEÚDO da `dist/` e o registro de quando ela mudou de verdade.

Por que existe (auditoria de velocidade, achado A1). `montar-dist.py` regravava a `index.html` em
toda rodada de gates, mesmo com o conteúdo igual. A data do arquivo mudava, o `pacote-auditoria.py`
dizia PACOTE VELHO nos 4 itens de captura e o `gate-relatorio.py` acusava medida "anterior à dist/".
Refazer a prova custa 191,7 s de máquina mais as voltas do modelo, e a dist era idêntica.

Regra: captura velha é captura feita com OUTRO conteúdo de dist, não captura feita antes da última
gravação do arquivo.

Como funciona.
  - `hash_pasta(pasta)`: sha256 de uma lista ordenada de `caminho NUL sha256-do-arquivo`. A data do
    arquivo não entra. O `gates-cache.mjs` calcula o mesmo hash em Node (o teste confere os dois).
  - `registrar(projeto, dist)`: o `montar-dist.py` chama depois de montar. Grava em
    `<projeto>/gates/_dist-hash.json` uma linha `{hash, desde}` só quando o conteúdo mudou; montar de
    novo o mesmo conteúdo não abre linha nova e guarda a primeira data.
  - `captura_fresca(projeto, dist, mtime)`: acha o hash que a dist tinha na hora da captura (a última
    linha com `desde` até essa hora) e compara com o hash de hoje. Igual: fresca, mesmo que a data da
    dist seja mais nova. Diferente: velha.
  - Sem registro, ou com a dist mexida à mão depois do último registro, vale a regra antiga da data
    (a captura tem que ser mais nova que o arquivo mais novo da dist). Nunca aprova por falta de dado.
"""
import hashlib
import json
import os
import time
from pathlib import Path

REGISTRO = "_dist-hash.json"
MAX_HISTORICO = 40


def _sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def arquivos_da_pasta(pasta):
    """Caminhos relativos (POSIX) dos arquivos da pasta, em ordem. Não segue pasta ligada por link."""
    pasta = Path(pasta)
    achados = []
    for atual, subpastas, nomes in os.walk(pasta, followlinks=False):
        subpastas.sort()
        for nome in nomes:
            p = Path(atual) / nome
            if p.is_file():
                achados.append(p.relative_to(pasta).as_posix())
    return sorted(achados)


def hash_pasta(pasta):
    """Hash do conteúdo: o mesmo conteúdo dá o mesmo hash, com qualquer data e em qualquer ordem de criação."""
    pasta = Path(pasta)
    h = hashlib.sha256()
    for rel in arquivos_da_pasta(pasta):
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(_sha256_arquivo(pasta / rel).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def caminho_registro(projeto):
    return Path(projeto) / "gates" / REGISTRO


def carregar_registro(projeto):
    p = caminho_registro(projeto)
    try:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        hist = [e for e in d.get("historico", [])
                if isinstance(e, dict) and isinstance(e.get("hash"), str) and isinstance(e.get("desde"), (int, float))]
        return {"historico": hist}
    except (OSError, ValueError, AttributeError):
        return {"historico": []}


def _salvar_registro(projeto, dados):
    p = caminho_registro(projeto)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def registrar(projeto, dist, agora=None):
    """Anota o hash de hoje da dist. Devolve (hash, mudou). Só abre linha nova quando o conteúdo mudou."""
    h = hash_pasta(dist)
    dados = carregar_registro(projeto)
    hist = dados["historico"]
    if hist and hist[-1]["hash"] == h:
        return h, False
    hist.append({"hash": h, "desde": float(time.time() if agora is None else agora)})
    dados["historico"] = hist[-MAX_HISTORICO:]
    try:
        _salvar_registro(projeto, dados)
    except OSError:
        pass   # sem permissão para gravar: a regra antiga da data segue valendo
    return h, True


def _mais_novo_da_dist(dist):
    tempos = []
    for rel in arquivos_da_pasta(dist):
        try:
            tempos.append((Path(dist) / rel).stat().st_mtime)
        except OSError:
            pass
    return max(tempos) if tempos else None


def hash_na_hora(historico, quando):
    """O hash que a dist tinha em `quando`: a última linha cujo `desde` não passa dessa hora. None se a captura é anterior ao registro."""
    ativo = None
    for e in historico:
        if e["desde"] <= quando:
            ativo = e["hash"]
    return ativo


def captura_fresca(projeto, dist, mtime_captura):
    """(fresca, motivo). Fresca = a captura foi feita com o mesmo CONTEÚDO de dist que existe hoje."""
    dist = Path(dist)
    if not dist.is_dir():
        return True, "sem dist para comparar"
    atual = hash_pasta(dist)
    hist = list(carregar_registro(projeto)["historico"])
    if not hist or hist[-1]["hash"] != atual:
        # Sem registro, ou a dist foi mexida fora do montar-dist: o arquivo mais novo da dist é a melhor data da mudança.
        desde = _mais_novo_da_dist(dist)
        if desde is None:
            return True, "dist vazia"
        hist.append({"hash": atual, "desde": desde})
    ativo = hash_na_hora(hist, mtime_captura)
    if ativo is None:
        # captura anterior a todo registro (projeto montado antes do registro existir): só a regra antiga da data decide
        mais_novo = _mais_novo_da_dist(dist)
        if mais_novo is None or mtime_captura >= mais_novo:
            return True, "sem registro desse momento; a data da captura é posterior à do arquivo mais novo da dist"
        return False, "sem registro desse momento e a captura é anterior ao arquivo mais novo da dist"
    if ativo == atual:
        return True, "mesmo conteúdo de dist"
    return False, "o conteúdo da dist mudou depois desta captura"
