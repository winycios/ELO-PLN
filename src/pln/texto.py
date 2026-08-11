"""Normalizacoes de texto compartilhadas entre dataset, aspectos e inferencia."""

from __future__ import annotations

import re
import unicodedata

_ESPACOS = re.compile(r"\s+")
_REPETICAO = re.compile(r"(.)\1{2,}")
_PONTUACAO = re.compile(r"[^\w\s]", flags=re.UNICODE)
_LIMITE_ORACAO = re.compile(r"[.!?;,:]+")

NEGACOES = frozenset({"nao", "nunca", "nem", "jamais", "sem"})
_FIM_ESCOPO_NEGACAO = frozenset({"mas", "porem", "contudo", "todavia"})
JANELA_NEGACAO_MODELO = 3
MARCADOR_LIMITE_ORACAO = "__limite_oracao__"


def colapsar_espacos(texto: str) -> str:
    return _ESPACOS.sub(" ", texto).strip()


def remover_acentos(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def reduzir_alongamentos(texto: str) -> str:
    """`otimoooo` -> `otimoo`: mantem enfase sem explodir o vocabulario."""
    return _REPETICAO.sub(r"\1\1", texto)


def normalizar_para_busca(texto: str) -> str:
    sem_acento = remover_acentos(texto.lower())
    return colapsar_espacos(_PONTUACAO.sub(" ", sem_acento))


def normalizar_para_busca_com_limites(texto: str) -> str:
    """Normaliza preservando um marcador para limites de oracao."""
    sem_acento = remover_acentos(texto.lower())
    com_limites = _LIMITE_ORACAO.sub(f" {MARCADOR_LIMITE_ORACAO} ", sem_acento)
    return colapsar_espacos(_PONTUACAO.sub(" ", com_limites))


def tokenizar(texto: str) -> list[str]:
    return normalizar_para_busca(texto).split()


def normalizar_para_modelo(texto: str) -> str:
    """Normaliza o texto e acrescenta marcadores locais de negacao.

    Os tokens originais sao preservados. Os marcadores permitem ao TF-IDF
    diferenciar `chegou` de `nao chegou` sem tentar implementar semantica em
    uma regressao logistica.
    """
    tokens = tokenizar(texto)
    marcadores: list[str] = []

    texto_sem_acento = remover_acentos(texto.lower())
    for oracao in _LIMITE_ORACAO.split(texto_sem_acento):
        tokens_oracao = normalizar_para_busca(oracao).split()
        for indice, token in enumerate(tokens_oracao):
            if token not in NEGACOES:
                continue
            vistos = 0
            for seguinte in tokens_oracao[indice + 1 :]:
                if seguinte in NEGACOES or seguinte in _FIM_ESCOPO_NEGACAO:
                    break
                if seguinte in {"e", "ou"}:
                    continue
                marcadores.append(f"NEG_{seguinte}")
                vistos += 1
                if vistos == JANELA_NEGACAO_MODELO:
                    break

    return " ".join([*tokens, *marcadores])
