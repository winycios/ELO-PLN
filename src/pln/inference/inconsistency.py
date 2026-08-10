from __future__ import annotations

from ..schemas import Sentimento

NOTA_ALTA = 4
NOTA_BAIXA = 2


def possui_inconsistencia(nota: int,sentimento: Sentimento,confianca: float,confianca_minima: float = 0.0,) -> bool:
    if confianca < confianca_minima:
        return False
    if nota >= NOTA_ALTA and sentimento is Sentimento.NEGATIVO:
        return True
    if nota <= NOTA_BAIXA and sentimento is Sentimento.POSITIVO:
        return True
    return False
