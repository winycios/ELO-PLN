"""Inferencia local: classificacao de sentimento e montagem da analise completa."""

from .base import ClassificadorSentimento
from .factory import carregar_classificador
from .pipeline import AnalisadorComentarios

__all__ = ["ClassificadorSentimento", "carregar_classificador", "AnalisadorComentarios"]
