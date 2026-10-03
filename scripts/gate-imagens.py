"""GATE DE IMAGENS: licença completa, direito de imagem e aviso de "imagem ilustrativa", inclusive
na prévia do link (og-image).

Por que existe (02/10/2026, auditoria da v4 do estúdio, nota 6,5). A foto do herói era de um
estúdio real, com duas pessoas identificáveis; a Wikimedia Commons registrava a permissão da
fotógrafa, não a autorização de imagem das retratadas para anunciar outro negócio (no Brasil,
uso comercial de imagem sem autorização gera indenização sem prova de dano, Súmula 403 do STJ).
O crédito do rodapé dizia "Creative Commons BY-SA" sem a versão 3.0, sem link para a licença e
sem dizer que a versão retocada seguia a mesma licença. E o og-image, que é o que a visitante
vê primeiro no WhatsApp, saía sem "imagem ilustrativa". `imagens/LICENCAS.md` listava as
condições; nada conferia.

Lê `imagens/LICENCAS.md` (tabela com as colunas Arquivo publicado, Origem, Autor, Título,
Licença, Link da licença, Alteração, Pessoa identificável, Autorização de imagem, Aviso de
ilustrativa) e a `dist/`. Reprova (exit 1):
  1. imagem publicada na dist/ (inclusive o og-image) sem linha na tabela;
  2. licença sem link; Creative Commons sem versão (3.0, 4.0) ou com link fora de
     creativecommons.org, sem autor ou sem título;
  3. pessoa identificável sem autorização de imagem: prefira foto sem pessoa identificável ou
     ilustração própria (foto do cliente com autorização das retratadas passa);
  4. og-image que não é do cliente sem aviso de "imagem ilustrativa";
  5. crédito incompleto na página: para CC, autor, título, licença COM versão e link para a
     licença no HTML publicado; imagem CC BY-SA alterada sem "mesma licença" escrito;
  6. página com imagem que não é do cliente e sem "imagem ilustrativa" no texto;
  7. (auditoria da v5, 03/10/2026) título que não é o da fonte: quando a origem é uma URL com
     o título no endereço (Unsplash, Wikimedia), o Título da tabela tem de estar nele; e todo
     trecho entre aspas no crédito da página (na frase com o nome do autor) tem de ser o
     Título da tabela. A v5 publicou Foto "Sala de pilates com aparelhos" para uma foto que
     no Unsplash se chama "a room filled with lots of different types of equipment".
Ilustração própria (Origem com "ilustração própria" ou "desenho próprio") não pede link de
licença nem "imagem ilustrativa": é da página, não de terceiro.
Favicon, apple-touch-icon e fontes ficam de fora.

Uso: python3 scripts/gate-imagens.py --projeto <dir> [--dist <dir>/dist]
"""
import argparse
import html as html_mod
import re
import sys
import unicodedata
from pathlib import Path

EXTENSOES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".svg"}
FORA = re.compile(r"^(favicon|apple-touch-icon|android-chrome|mstile)", re.I)
COLUNAS = {
    "arquivo": ("arquivo publicado", "arquivo"),
    "origem": ("origem",),
    "autor": ("autor",),
    "titulo": ("titulo",),
    "licenca": ("licenca",),
    "link": ("link da licenca",),
    "alteracao": ("alteracao",),
    "pessoa": ("pessoa identificavel",),
    "autorizacao": ("autorizacao de imagem",),
    "aviso": ("aviso de ilustrativa",),
}


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower())
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).split())


def sim(valor):
    return norm(valor).startswith(("sim", "yes"))


def ler_tabela(md):
    linhas = [l.strip() for l in md.splitlines() if l.strip().startswith("|")]
    for i, l in enumerate(linhas):
        cab = [norm(c) for c in l.strip("|").split("|")]
        if "licenca" in cab and any(c.startswith("arquivo") for c in cab):
            mapa = {}
            for chave, nomes in COLUNAS.items():
                for j, c in enumerate(cab):
                    if c in nomes:
                        mapa[chave] = j
                        break
            itens = []
            for l2 in linhas[i + 1:]:
                cel = [c.strip() for c in l2.strip("|").split("|")]
                if all(re.fullmatch(r":?-+:?", c) for c in cel if c):
                    continue
                if len(cel) < len(cab):
                    break
                itens.append({k: cel[j] for k, j in mapa.items()})
            return mapa, itens
    return {}, []


def base(nome):
    stem = Path(nome).stem
    return re.sub(r"-\d{2,4}$", "", stem)


def texto_visivel(h):
    h = re.sub(r"(?is)<(script|style|head)\b.*?</\1>", " ", h)
    return " ".join(html_mod.unescape(re.sub(r"<[^>]+>", " ", h)).split())


def eh_cc(licenca):
    return bool(re.search(r"\bcc\b|creative commons", norm(licenca)))


def do_cliente(item):
    return any(k in norm(item.get("origem", "") + " " + item.get("licenca", "")) for k in ("do cliente", "da cliente", "propria do cliente"))


def propria(item):
    return any(k in norm(item.get("origem", "")) for k in ("ilustracao propria", "desenho proprio", "ilustracoes proprias"))


def titulo_da_url(origem):
    """Título legível no endereço da fonte (slug do Unsplash, nome do arquivo da Wikimedia)."""
    m = re.match(r"https?://\S+", origem or "")
    if not m:
        return ""
    ultimo = re.sub(r"[?#].*$", "", m.group(0)).rstrip("/").split("/")[-1]
    ultimo = re.sub(r"^(file|arquivo):", "", ultimo, flags=re.I)
    ultimo = re.sub(r"\.(jpe?g|png|webp|gif|tiff?)$", "", ultimo, flags=re.I)
    return norm(re.sub(r"[-_%]+", " ", ultimo))


def citacoes_do_credito(texto, autor):
    """Trechos entre aspas nas frases do texto da página que citam o autor."""
    if not autor.strip():
        return []
    achados = []
    for frase in re.split(r"(?<=[.!?])\s+", texto):
        if norm(autor) in norm(frase):
            achados += re.findall(r'["“]([^"”]{2,140})["”]', frase)
    return achados


def checar(projeto, dist=None):
    projeto = Path(projeto)
    dist = Path(dist) if dist else projeto / "dist"
    problemas = []
    lic = projeto / "imagens" / "LICENCAS.md"
    if not lic.is_file():
        return [f"falta {lic}: toda imagem publicada precisa de origem, autor, licença e link"]
    mapa, itens = ler_tabela(lic.read_text(encoding="utf-8"))
    faltam = [c for c in COLUNAS if c not in mapa]
    if faltam:
        return [f"LICENCAS.md sem as colunas {', '.join(faltam)} (cabeçalho: Arquivo publicado | Origem | Autor | Título | Licença | Link da licença | Alteração | Pessoa identificável | Autorização de imagem | Aviso de ilustrativa)"]
    index = dist / "index.html"
    pagina = index.read_text(encoding="utf-8") if index.is_file() else ""
    texto = texto_visivel(pagina)
    texto_n = norm(texto)
    hrefs = set(re.findall(r'href="([^"]+)"', pagina))

    publicadas = sorted(p for p in dist.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSOES
                        and "fonts" not in p.relative_to(dist).parts and not FORA.match(p.name))
    usados = []
    for p in publicadas:
        rel = p.relative_to(dist).as_posix()
        achou = [it for it in itens if base(p.name) in it["arquivo"] or p.name in it["arquivo"]]
        if not achou:
            problemas.append(f"{rel}: imagem publicada sem linha em imagens/LICENCAS.md")
            continue
        usados.append((rel, achou[0]))

    vistos = set()
    algum_terceiro = False
    for rel, it in usados:
        chave = id(it)
        og = Path(rel).stem.startswith("og-image")
        cliente = do_cliente(it)
        algum_terceiro |= not cliente and not propria(it)
        if og and not cliente and not propria(it) and not sim(it["aviso"]):
            problemas.append(f"{rel}: prévia do link sem aviso de \"imagem ilustrativa\" (a foto não é do cliente e é a primeira coisa que a visitante vê no WhatsApp)")
        if chave in vistos:
            continue
        vistos.add(chave)
        nome = it["arquivo"]
        licenca, link = it["licenca"], it["link"].strip()
        if not licenca:
            problemas.append(f"{nome}: sem licença")
        if not cliente and not propria(it) and not re.match(r"https?://", link):
            problemas.append(f"{nome}: sem link da licença (http...)")
        if eh_cc(licenca):
            versao = re.search(r"\d\.\d", licenca)
            if not versao:
                problemas.append(f"{nome}: Creative Commons sem versão da licença (3.0, 4.0): \"{licenca}\"")
            if link and "creativecommons.org" not in link:
                problemas.append(f"{nome}: link da licença CC fora de creativecommons.org: {link}")
            if not it["autor"].strip() or not it["titulo"].strip():
                problemas.append(f"{nome}: crédito CC exige autor e título")
            # Crédito no HTML publicado: autor, título, licença com versão e link para a licença.
            curta = re.sub(r"\s+", " ", re.sub(r"(?i)creative commons|licen[cç]a", "CC", licenca)).strip()
            m = re.search(r"(?i)\bCC\s*(BY(?:-[A-Z]{2})*|0)\s*(\d\.\d)", curta)
            exigida = f"CC {m.group(1).upper()} {m.group(2)}" if m else licenca
            for oque, valor in (("autor", it["autor"]), ("título", it["titulo"])):
                if valor.strip() and norm(valor) not in texto_n:
                    problemas.append(f"{nome}: crédito na página sem o {oque} (\"{valor}\")")
            if m and not re.search(re.escape(m.group(1)) + r"\s*" + re.escape(m.group(2)), texto, re.I):
                problemas.append(f"{nome}: crédito na página sem a licença com versão (\"{exigida}\")")
            if link and link not in hrefs:
                problemas.append(f"{nome}: a página não tem link para a licença ({link})")
            alterada = norm(it["alteracao"]) not in ("", "nenhuma", "nao", "-")
            if alterada and re.search(r"BY-?\s?SA", licenca, re.I) and "mesma licenca" not in texto_n:
                problemas.append(f"{nome}: versão alterada de CC BY-SA sem \"mesma licença\" escrito no crédito da página")
        slug = titulo_da_url(it.get("origem", ""))
        titulo = it.get("titulo", "").strip()
        if titulo and len(slug.split()) >= 3 and norm(titulo) not in slug:
            problemas.append(f"{nome}: Título \"{titulo}\" não é o da fonte (o endereço diz \"{slug}\"): use o título real ou crédito sem título entre aspas")
        for citado in citacoes_do_credito(texto, it.get("autor", "")):
            if norm(citado) != norm(titulo):
                problemas.append(f"{nome}: o crédito da página cita \"{citado}\" entre aspas como título, e o título da fonte é \"{titulo or slug}\"")
        if sim(it["pessoa"]) and not sim(it["autorizacao"]):
            problemas.append(f"{nome}: pessoa identificável sem autorização de imagem: prefira foto sem pessoa identificável ou ilustração própria; a licença do autor não cobre a imagem de quem aparece")
    if algum_terceiro and "ilustrativa" not in texto_n:
        problemas.append("página: imagem que não é do cliente sem \"imagem ilustrativa\" no texto publicado")
    return problemas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--dist")
    a = ap.parse_args()
    problemas = checar(a.projeto, a.dist)
    print("\nGATE DE IMAGENS  " + str(Path(a.projeto).resolve()))
    print("=" * 80)
    if problemas:
        for p in problemas:
            print("  FALHA: " + p)
        print(f"\n  REPROVA: {len(problemas)} problema(s) de licença, imagem ou aviso.\n")
        return 1
    print("  PASSA: toda imagem publicada com licença completa, sem pessoa identificável sem autorização,")
    print("  crédito completo na página e aviso de imagem ilustrativa, inclusive na prévia do link.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
