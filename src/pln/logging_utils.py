from __future__ import annotations

import logging
import os

_FORMATO = "%(asctime)s %(levelname)-7s %(name)s | %(message)s"


def configurar_logging(nivel: str | None = None) -> None:
    logging.basicConfig(
        level=(nivel or os.environ.get("ELO_PLN_LOG_LEVEL", "INFO")).upper(),
        format=_FORMATO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def obter_logger(nome: str) -> logging.Logger:
    return logging.getLogger(nome)


def resumir_texto(texto: str | None, limite: int = 24) -> str:
    if not texto:
        return "<vazio>"
    limpo = " ".join(texto.split())
    if len(limpo) <= limite:
        return f"<{len(limpo)} chars>"
    return f"{limpo[:limite]}... <{len(limpo)} chars>"
