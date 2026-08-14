"""Normalizacoes de texto compartilhadas entre dataset, aspectos e inferencia."""

from __future__ import annotations

import re
import unicodedata

_ESPACOS = re.compile(r"\s+")
_REPETICAO = re.compile(r"(.)\1{2,}")
_PONTUACAO = re.compile(r"[^\w\s]", flags=re.UNICODE)
_LIMITE_ORACAO = re.compile(r"[.!?;,:]+")

NEGACOES = frozenset({"nao", "nunca", "nem", "jamais", "sem"})
_FIM_ESCOPO_NEGACAO = frozenset({"mas", "porem", "contudo", "todavia", "embora", "e", "ou"})
JANELA_NEGACAO_MODELO = 3

_ALCANCE_MAXIMO = 2 * JANELA_NEGACAO_MODELO
MARCADOR_LIMITE_ORACAO = "__limite_oracao__"

# Expressoes em que o negador NAO nega o termo seguinte: `nunca mais contrato` e
# uma rejeicao enfatica, nao a negacao de `mais`. Tratadas como token unico, elas
# deixam de disparar escopo de negacao e viram uma caracteristica propria.
EXPRESSOES_FIXAS: dict[str, str] = {
    "nunca mais": "nunca_mais",
    "nem sempre": "nem_sempre",
    "sem duvida": "sem_duvida",
    "sem falta": "sem_falta",
    "nada a reclamar": "nada_a_reclamar",
    "nada demais": "nada_demais",
}

_PADRAO_EXPRESSOES = re.compile(
    r"\b(?:"
    + "|".join(
        r"\s+".join(re.escape(parte) for parte in expressao.split())
        for expressao in sorted(EXPRESSOES_FIXAS, key=len, reverse=True)
    )
    + r")\b"
)

# Advertios de quantidade e intensificadores. `nao muito caprichoso` nega
# `caprichoso`, nao `muito` — marcar o intensificador gastava a janela e ainda
# criava caracteristicas sem polaridade propria.
_INTENSIFICADORES = frozenset(
    {
        "mais",
        "menos",
        "muito",
        "muita",
        "muitos",
        "muitas",
        "pouco",
        "pouca",
        "tao",
        "demais",
        "bem",
        "super",
        "bastante",
        "tanto",
        "tanta",
        "meio",
        "todo",
        "toda",
    }
)

# Palavras funcionais: nao recebem marcador e nao consomem a janela, para que
# `nao fez o que foi combinado` alcance `combinado` em vez de parar em `o que foi`.
_FUNCIONAIS = frozenset(
    {
        "o", "a", "os", "as", "um", "uma", "uns", "umas",
        "de", "do", "da", "dos", "das", "no", "na", "nos", "nas",
        "ao", "aos", "em", "por", "pelo", "pela", "pelos", "pelas",
        "com", "para", "pra", "pro", "que", "se",
        "meu", "minha", "meus", "minhas", "eu", "ele", "ela", "me", "mim", "lhe",
        "isso", "isto", "aquilo", "ja", "ainda", "foi", "era",
    }
)

# Tokens transparentes ao escopo da negacao: sao ignorados sem encerra-lo.
_TRANSPARENTES = _INTENSIFICADORES | _FUNCIONAIS

# Lista de descarte do vetorizador de palavras. E exatamente o conjunto de
# palavras sem carga de sentimento — nenhum negador entra aqui, senao `nao` sumiria
# junto e os marcadores NEG_ perderiam sentido. Os marcadores `NEG_x` sao tokens
# proprios e nao sao afetados.
PALAVRAS_DESCARTAVEIS: frozenset[str] = _FUNCIONAIS


def colapsar_espacos(texto: str) -> str:
    return _ESPACOS.sub(" ", texto).strip()


def remover_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def reduzir_alongamentos(texto: str) -> str:
    """`otimoooo` -> `otimoo`: mantem enfase sem explodir o vocabulario."""
    return _REPETICAO.sub(r"\1\1", texto)


def aplicar_expressoes_fixas(texto: str) -> str:
    return _PADRAO_EXPRESSOES.sub(
        lambda casamento: EXPRESSOES_FIXAS[colapsar_espacos(casamento.group(0))], texto
    )


def normalizar_para_busca(texto: str) -> str:
    sem_acento = remover_acentos(texto.lower())
    return colapsar_espacos(_PONTUACAO.sub(" ", sem_acento))


def normalizar_para_busca_com_limites(texto: str) -> str:
    """Normaliza preservando um marcador para limites de oracao."""
    sem_acento = aplicar_expressoes_fixas(remover_acentos(texto.lower()))
    com_limites = _LIMITE_ORACAO.sub(f" {MARCADOR_LIMITE_ORACAO} ", sem_acento)
    return colapsar_espacos(_PONTUACAO.sub(" ", com_limites))


def tokenizar(texto: str) -> list[str]:
    return normalizar_para_busca(texto).split()


def marcadores_negacao(tokens: list[str], janela: int = JANELA_NEGACAO_MODELO) -> list[str]:
    marcadores: list[str] = []
    for indice, token in enumerate(tokens):
        if token not in NEGACOES:
            continue
        vistos = 0
        for percorridos, seguinte in enumerate(tokens[indice + 1 :], start=1):
            if seguinte in NEGACOES or seguinte in _FIM_ESCOPO_NEGACAO:
                break
            if percorridos > _ALCANCE_MAXIMO:
                break
            if seguinte in _TRANSPARENTES:
                continue
            marcadores.append(f"NEG_{seguinte}")
            vistos += 1
            if vistos == janela:
                break
    return marcadores


def ha_negacao_no_escopo(
    tokens_anteriores: list[str], janela: int = JANELA_NEGACAO_MODELO
) -> bool:
    ultimo_limite = -1
    for indice, token in enumerate(tokens_anteriores):
        if token == MARCADOR_LIMITE_ORACAO or token in _FIM_ESCOPO_NEGACAO:
            ultimo_limite = indice

    contados = 0
    escopo = tokens_anteriores[ultimo_limite + 1 :]
    for percorridos, token in enumerate(reversed(escopo), start=1):
        if token in NEGACOES:
            return True
        if percorridos > _ALCANCE_MAXIMO:
            return False
        if token in _TRANSPARENTES:
            continue
        contados += 1
        if contados >= janela:
            return False
    return False


def normalizar_para_modelo(texto: str) -> str:
    base = aplicar_expressoes_fixas(remover_acentos(texto.lower()))
    tokens = normalizar_para_busca(base).split()

    marcadores: list[str] = []
    for oracao in _LIMITE_ORACAO.split(base):
        marcadores.extend(marcadores_negacao(normalizar_para_busca(oracao).split()))

    return " ".join([*tokens, *marcadores])
