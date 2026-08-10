"""Normalizacoes de texto compartilhadas entre dataset, aspectos e inferencia."""

from __future__ import annotations

import re
import unicodedata

_ESPACOS = re.compile(r"\s+")
_REPETICAO = re.compile(r"(.)\1{2,}")
_PONTUACAO = re.compile(r"[^\w\s]", flags=re.UNICODE)


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


def tokenizar(texto: str) -> list[str]:
    return normalizar_para_busca(texto).split()
