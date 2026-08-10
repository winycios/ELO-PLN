from __future__ import annotations

import re

from ..texto import colapsar_espacos, reduzir_alongamentos

VERSAO_LIMPEZA = "limpeza-v1"

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_URL = re.compile(r"https?://\S+|www\.\S+")
_TELEFONE = re.compile(r"(?:\(?\d{2}\)?\s?)?(?:9\s?)?\d{4}[-.\s]?\d{4}")
_DOCUMENTO = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b|\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
_NUMERO_LONGO = re.compile(r"\b\d{6,}\b")

REGRAS_LIMPEZA = [
    "substituicao de e-mails por <EMAIL>",
    "substituicao de URLs por <URL>",
    "substituicao de documentos (CPF/CNPJ) por <DOC>",
    "substituicao de telefones por <TELEFONE>",
    "substituicao de numeros com 6+ digitos por <NUM>",
    "reducao de caracteres repetidos (3+ -> 2)",
    "colapso de espacos em branco",
]


def anonimizar(texto: str) -> str:
    texto = _EMAIL.sub("<EMAIL>", texto)
    texto = _URL.sub("<URL>", texto)
    texto = _DOCUMENTO.sub("<DOC>", texto)
    texto = _TELEFONE.sub("<TELEFONE>", texto)
    texto = _NUMERO_LONGO.sub("<NUM>", texto)
    return texto


def limpar_comentario(texto: str | None) -> str:
    if not texto:
        return ""
    limpo = anonimizar(texto)
    limpo = reduzir_alongamentos(limpo)
    limpo = colapsar_espacos(limpo)
    return limpo


def comentario_utilizavel(texto: str, minimo_caracteres: int) -> bool:
    if not texto:
        return False
    if len(texto.strip()) < minimo_caracteres:
        return False
    return any(caractere.isalpha() for caractere in texto)
