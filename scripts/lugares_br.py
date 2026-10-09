"""Lugares do Brasil (e alguns de fora) que se escrevem como nome de pessoa: duas ou mais palavras com maiúscula.

Quem usa: gate-imagens.py (achado P10 da 3.5.10: "Belo Horizonte" no alt de uma foto de banco foi lido como
nome de pessoa). Fica num módulo à parte para o gate não crescer com dados, e para a lista poder aumentar
sem mexer na lógica.

Como funciona `tira_lugares(texto)`: troca cada lugar conhecido por um espaço (sem acento e sem maiúscula
na comparação, palavra inteira), e troca também o que vem logo depois de uma palavra de lugar
("Sul de Minas", "Zona Sul", "Vale do Paraíba"). Nome de pessoa de verdade fica intacto.
"""
import re
import unicodedata


def _norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


# Capitais, cidades grandes e médias, cidades de Minas e do litoral que aparecem em página de serviço local,
# estados, regiões e alguns países. Só entram nomes com duas ou mais palavras ou com cara de nome próprio
# composto; cidade de uma palavra só ("Niterói") nem chega a ser lida como nome (o gate pede duas palavras).
_LUGARES = """
Belo Horizonte; Rio de Janeiro; São Paulo; Porto Alegre; Rio Branco; Boa Vista; Campo Grande; Santa Maria;
João Pessoa; Foz do Iguaçu; Ribeirão Preto; São José dos Campos; São José do Rio Preto; São Bernardo do Campo;
Santo André; São Caetano do Sul; Juiz de Fora; Montes Claros; Governador Valadares; Poços de Caldas;
Poço Fundo; Santo Antônio do Amparo; Campos do Jordão; Ouro Preto; Foz do Iguacu; Balneário Camboriú;
Florianópolis; Campos dos Goytacazes; Nova Friburgo; Volta Redonda; Barra Mansa; Angra dos Reis; Cabo Frio;
São Gonçalo; Duque de Caxias; Nova Iguaçu; São João de Meriti; Belford Roxo; São João del Rei; Sete Lagoas;
Divinópolis; Ipatinga; Uberlândia; Uberaba; Varginha; Pouso Alegre; Santa Rita do Sapucaí; Três Corações;
Lavras; Machado; Alfenas; Guaxupé; São Sebastião do Paraíso; Patos de Minas; Teófilo Otoni; Passos;
Feira de Santana; Vitória da Conquista; Porto Seguro; Campina Grande; Caruaru; Juazeiro do Norte;
Porto Velho; Cuiabá; Palmas; São Luís; Teresina; Natal; Maceió; Aracaju; Salvador; Recife; Fortaleza; Manaus;
Santa Catarina; Mato Grosso; Mato Grosso do Sul; Minas Gerais; Espírito Santo; Rio Grande do Sul;
Rio Grande do Norte; Rio de Janeiro; Distrito Federal; Rio Grande; Santa Cruz; Santa Luzia; Santa Bárbara;
Vila Velha; Vila Nova; Nova Lima; Nova Iorque; Nova York; Buenos Aires; Cidade do México; Cidade do Cabo;
Los Angeles; Las Vegas; San Francisco; Reino Unido; Estados Unidos; Costa Rica; Costa do Sauípe; Costa Verde;
Sul de Minas; Zona da Mata; Zona Sul; Zona Norte; Zona Leste; Zona Oeste; Região Metropolitana;
Grande Rio; Grande São Paulo; Grande Belo Horizonte; Baixada Fluminense; Região dos Lagos; Região Serrana;
Vale do Paraíba; Vale do Aço; Vale do Jequitinhonha; Serra da Mantiqueira; Serra da Canastra;
Alto Paraíso; Alto Paraíso de Goiás; Baixo Sul; Centro Histórico; Barra da Tijuca; Copacabana; Ipanema;
América do Sul; América do Norte; América Latina; Oriente Médio; Europa Ocidental
"""
LUGARES = {_norm(x.strip()) for x in re.split(r"[;\n]", _LUGARES) if x.strip()}

# Primeira palavra que, sozinha, indica lugar: "Sul de Minas", "Vale do Paraíba", "Zona Oeste", "Rio Grande".
_INICIO_DE_LUGAR = {"sul", "norte", "leste", "oeste", "centro", "zona", "vale", "serra", "costa", "baixada",
                    "regiao", "litoral", "ilha", "praia", "rio", "lago", "lagoa", "porto", "monte", "campos",
                    "cidade", "bairro", "estado", "grande", "alto", "baixo"}
# Palavra que, logo antes do nome, diz que ele é um lugar: "café em Vila Nova do Sul", "entrega para Nova Lima".
LOCATIVAS = {"em", "na", "no", "nas", "nos", "para", "pra", "perto", "arredores", "bairro", "cidade", "regiao", "municipio"}

_PALAVRA = r"[A-Za-zÀ-ÿ']+"
_NOME = re.compile(r"\b[A-ZÀ-Ý][a-zà-ÿ']{2,}(?:\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ý][a-zà-ÿ']{2,})+\b")


def eh_lugar(nome):
    """True se o trecho (duas ou mais palavras com maiúscula) é um lugar conhecido ou começa por palavra de lugar."""
    n = _norm(nome).strip()
    if n in LUGARES:
        return True
    primeira = n.split()[0] if n.split() else ""
    return primeira in _INICIO_DE_LUGAR and len(n.split()) >= 2


def tira_lugares(texto):
    """Troca por espaço cada lugar conhecido do texto. O resto, inclusive nome de pessoa, fica como estava."""
    # mais longos primeiro, para "Grande Belo Horizonte" sair antes de "Belo Horizonte"
    for lug in sorted(LUGARES, key=len, reverse=True):
        partes = [re.escape(p) for p in lug.split()]
        # a comparação ignora acento: o texto é normalizado só para achar a posição
        padrao = re.compile(r"(?<![\wÀ-ÿ])" + r"\s+".join(partes) + r"(?![\wÀ-ÿ])", re.I)
        texto = _tira_sem_acento(texto, padrao, lug)
    return texto


def _tira_sem_acento(texto, padrao, lug):
    # procura no texto sem acento (mesmo tamanho caractere a caractere), apaga no original
    sem = "".join(_norm(c) if len(_norm(c)) == 1 else c for c in texto)
    out, ult = [], 0
    for m in padrao.finditer(sem):
        out.append(texto[ult:m.start()])
        out.append(" ")
        ult = m.end()
    out.append(texto[ult:])
    return "".join(out)


def nomes_de_pessoa(texto):
    """Os trechos que parecem nome de pessoa (duas ou mais palavras com maiúscula), sem lugares e sem o que
    vem depois de 'em', 'na', 'no', 'para'... (locativa), na ordem em que aparecem."""
    achados = []
    limpo = tira_lugares(texto)
    for m in _NOME.finditer(limpo):
        nome = m.group(0)
        if eh_lugar(nome):
            continue
        # só vale a palavra COLADA no nome ("em Vila Nova"), não uma de antes de pontuação ("no  . Helena Duarte")
        colada = re.search(r"(" + _PALAVRA + r")[ \t]+$", limpo[:m.start()])
        if colada and _norm(colada.group(1)) in LOCATIVAS:
            continue
        achados.append(nome)
    return achados
