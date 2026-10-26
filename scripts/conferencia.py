#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A rodada 2 do auditor como conferência dirigida (3.7.0). Funções que o `pacote-auditoria.py` usa.

Por que existe (teste de aluno da 3.6.2, 26/10/2026): a rodada 2 levou 662 s e 10 chamadas para devolver só "corrigido ou
não". O auditor recebia o pacote inteiro de novo e reabria a página. Agora ele recebe só o que decide o ciclo:
  - a lista NUMERADA dos achados críticos e altos da rodada 1 (`auditoria/abertos-rodada-1.json`);
  - o print novo de cada um, que a sessão tira depois do conserto (`auditoria/correcoes-rodada-1.json`), numa prancha só;
  - o diff da dist entre a versão auditada (a foto que a rodada 1 guardou em `auditoria/dist-rodada-1/`) e a de agora.
Médio e baixo não vão para a conferência: não seguram o ciclo, e o conserto deles se prova pelos gates.
"""
import datetime
import difflib
import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path

FOTO = Path("auditoria") / "dist-rodada-1"
ABERTOS = Path("auditoria") / "abertos-rodada-1.json"
CORRECOES = Path("auditoria") / "correcoes-rodada-1.json"
DIFF = Path("auditoria") / "diff-dist.txt"
PRANCHA = Path("auditoria") / "conferencia" / "prancha.jpg"
TEXTO = {".html", ".htm", ".css", ".js", ".mjs", ".svg", ".txt", ".json", ".xml", ".webmanifest"}
IMAGENS = (".png", ".jpg", ".jpeg", ".webp")
QUE_FECHAM = ("critico", "alto")
LIMITE_DIFF = 300   # linhas: o diff é para ler numa chamada


def _sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s or "")) if unicodedata.category(c) != "Mn").lower().strip()


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _arquivos(pasta):
    pasta = Path(pasta)
    return sorted(p.relative_to(pasta).as_posix() for p in pasta.rglob("*") if p.is_file())


def guardar_dist(raiz):
    """Rodada 1: guarda a dist auditada (texto inteiro, e o hash de todo arquivo). A rodada 2 compara com ela."""
    raiz = Path(raiz)
    dist = raiz / "dist"
    if not dist.is_dir():
        return None
    destino = raiz / FOTO
    destino.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for rel in _arquivos(dist):
        origem = dist / rel
        hashes[rel] = _sha(origem)
        if origem.suffix.lower() in TEXTO:
            alvo = destino / rel
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, alvo)
    (destino / "_hashes.json").write_text(json.dumps({"quando": datetime.datetime.now().isoformat(timespec="seconds"),
                                                       "hashes": hashes}, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino


def _linhas(texto):
    """Linhas do arquivo, com o CSS e o HTML minificados quebrados depois de `}`, `;` e `>`: o diff de uma linha de 16 KB não se lê."""
    saida = []
    for linha in texto.splitlines():
        if len(linha) > 300:
            saida.extend(p for p in re.split(r"(?<=[};>])", linha) if p.strip())
        else:
            saida.append(linha)
    return saida


def diff_da_dist(raiz):
    """Rodada 2: grava `auditoria/diff-dist.txt` (a dist auditada contra a de agora). Devolve (caminho, resumo) ou (None, motivo)."""
    raiz = Path(raiz)
    foto = raiz / FOTO
    manifesto = foto / "_hashes.json"
    if not manifesto.is_file():
        return None, "sem a foto da dist da rodada 1 (auditoria/dist-rodada-1/): o pacote da rodada 1 a grava; o auditor fica sem o diff"
    antes = json.loads(manifesto.read_text(encoding="utf-8")).get("hashes") or {}
    dist = raiz / "dist"
    agora = {rel: _sha(dist / rel) for rel in _arquivos(dist)} if dist.is_dir() else {}
    mudaram = sorted(r for r in antes if r in agora and antes[r] != agora[r])
    novos = sorted(r for r in agora if r not in antes)
    sumiram = sorted(r for r in antes if r not in agora)
    corpo = []
    for rel in mudaram:
        if Path(rel).suffix.lower() not in TEXTO or not (foto / rel).is_file():
            continue
        a = _linhas((foto / rel).read_text(encoding="utf-8", errors="replace"))
        b = _linhas((dist / rel).read_text(encoding="utf-8", errors="replace"))
        corpo.extend(difflib.unified_diff(a, b, fromfile=f"rodada-1/{rel}", tofile=f"agora/{rel}", n=1, lineterm=""))
    cortado = max(0, len(corpo) - LIMITE_DIFF)
    texto = ["# Diff da dist: a versão que a rodada 1 auditou contra a de agora", ""]
    texto += corpo[:LIMITE_DIFF]
    if cortado:
        texto.append(f"... (mais {cortado} linha(s) de diff; o arquivo inteiro está em dist/ e a versão auditada em auditoria/dist-rodada-1/)")
    texto += ["", "## Arquivos",
              f"- mudaram: {', '.join(mudaram) or 'nenhum'}",
              f"- novos: {', '.join(novos) or 'nenhum'}",
              f"- saíram: {', '.join(sumiram) or 'nenhum'}"]
    alvo = raiz / DIFF
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text("\n".join(texto) + "\n", encoding="utf-8")
    return alvo, f"{len(mudaram)} arquivo(s) mudaram, {len(novos)} novo(s), {len(sumiram)} saíram; {min(len(corpo), LIMITE_DIFF)} linha(s) de diff"


def abertos_da_rodada_1(raiz, blocos_do_texto):
    """Os achados críticos e altos da rodada 1, numerados na ordem em que o auditor os escreveu. Grava a lista para o `wave.py conferencia`."""
    raiz = Path(raiz)
    arq = next((raiz / "auditoria" / n for n in ("achados-rodada-1.json", "achados-rodada-1.md") if (raiz / "auditoria" / n).is_file()), None)
    if arq is None:
        return None
    abertos = []
    for bloco in blocos_do_texto(arq.read_text(encoding="utf-8-sig")):
        for a in bloco.get("achados") or []:
            if isinstance(a, dict) and _sem_acento(a.get("severidade")) in QUE_FECHAM:
                abertos.append({"n": len(abertos) + 1, "lente": bloco.get("lente"), "severidade": _sem_acento(a.get("severidade")),
                                "item": str(a.get("item") or "").strip(), "evidencia": str(a.get("evidencia") or "").strip(),
                                "fix": str(a.get("fix") or "").strip()})
    alvo = raiz / ABERTOS
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(json.dumps({"abertos": abertos}, ensure_ascii=False, indent=2), encoding="utf-8")
    return abertos


def correcoes(raiz, abertos, fresca):
    """Lê `auditoria/correcoes-rodada-1.json` (um print novo por achado). Sem o arquivo, grava o modelo numerado.
    `fresca(caminho)` diz se o print foi tirado com a dist de agora. Devolve (itens por n, problemas, modelo_criado)."""
    raiz = Path(raiz)
    arq = raiz / CORRECOES
    if not arq.is_file():
        modelo = [{"n": a["n"], "lente": a["lente"], "severidade": a["severidade"], "item": a["item"], "print": "", "recorte": "",
                   "o_que_mudou": ""} for a in abertos]
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(json.dumps(modelo, ensure_ascii=False, indent=2), encoding="utf-8")
        return {}, [f"preencha em {CORRECOES.as_posix()} o print NOVO de cada achado (\"print\": caminho no projeto, tirado depois do conserto; "
                    "\"recorte\": \"x,y,largura,altura\" opcional, em px do print) e o que mudou"], True
    try:
        lidos = json.loads(arq.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        return {}, [f"{CORRECOES.as_posix()} não é JSON: {e}"], False
    lidos = lidos.get("correcoes") if isinstance(lidos, dict) else lidos
    por_n = {c.get("n"): c for c in (lidos or []) if isinstance(c, dict)}
    itens, problemas = {}, []
    for a in abertos:
        c = por_n.get(a["n"]) or {}
        nome = str(c.get("print") or "").strip()
        p = (raiz / nome) if nome and not Path(nome).is_absolute() else Path(nome)
        if not nome:
            problemas.append(f"n={a['n']} ({a['item'][:60]}): sem print novo")
        elif not p.is_file() or p.suffix.lower() not in IMAGENS:
            problemas.append(f"n={a['n']}: o print '{nome}' não existe ou não é imagem ({', '.join(IMAGENS)})")
        elif not fresca(p):
            problemas.append(f"n={a['n']}: o print '{nome}' é de antes da última mudança da dist; tire de novo depois do conserto")
        else:
            itens[a["n"]] = {**a, "print": nome, "recorte": str(c.get("recorte") or "").strip(), "o_que_mudou": str(c.get("o_que_mudou") or "").strip()}
    return itens, problemas, False


def fonte_do_rotulo(tam):
    """A fonte com acento do `lado-a-lado.py` (a padrão do Pillow escreve "Rodap? sem Termos"). Sem ela, a padrão."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("lado_a_lado_conf", Path(__file__).resolve().parent / "lado-a-lado.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.fonte(tam)


def montar_prancha(raiz, itens):
    """Uma imagem só com o print novo de cada achado (2 por linha, com o número). Sem Pillow devolve None e o briefing lista os prints."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    raiz = Path(raiz)
    larg, alt, faixa = 640, 420, 34
    fonte = fonte_do_rotulo(17)
    quadros = []
    for n in sorted(itens):
        it = itens[n]
        try:
            img = Image.open(raiz / it["print"]).convert("RGB")
        except (OSError, ValueError, SyntaxError):
            continue   # imagem que o Pillow não lê fica fora da prancha; o briefing lista o caminho dela
        if img.width < 2 or img.height < 2:
            continue
        rec = [int(x) for x in re.findall(r"\d+", it.get("recorte") or "")]
        if len(rec) == 4 and rec[2] > 0 and rec[3] > 0:
            img = img.crop((rec[0], rec[1], rec[0] + rec[2], rec[1] + rec[3]))
        escala = min(larg / img.width, alt / img.height)
        img = img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))))
        quadros.append((n, it, img))
    if not quadros:
        return None
    colunas = 2 if len(quadros) > 1 else 1
    linhas = (len(quadros) + colunas - 1) // colunas
    prancha = Image.new("RGB", (colunas * (larg + 20), linhas * (alt + faixa + 20)), (255, 255, 255))
    d = ImageDraw.Draw(prancha)
    for i, (n, it, img) in enumerate(quadros):
        x = (i % colunas) * (larg + 20)
        y = (i // colunas) * (alt + faixa + 20)
        d.text((x + 6, y + 8), f"{n}. [{it['severidade']}] {it['lente']}: {it['item']}"[:72], fill=(0, 0, 0), font=fonte)
        prancha.paste(img, (x, y + faixa))
    alvo = raiz / PRANCHA
    alvo.parent.mkdir(parents=True, exist_ok=True)
    prancha.save(alvo, quality=86)
    return alvo
