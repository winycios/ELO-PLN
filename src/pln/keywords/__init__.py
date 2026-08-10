"""Extracao de palavras-chave e aspectos sem modelo neural adicional."""

from .aspects import ASPECTOS, rotulo_amigavel
from .extractor import ExtratorAspectos

__all__ = ["ASPECTOS", "ExtratorAspectos", "rotulo_amigavel"]
