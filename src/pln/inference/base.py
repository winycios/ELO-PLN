from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ..schemas import Predicao


class ClassificadorSentimento(ABC):
    versao: str = "desconhecida"

    @abstractmethod
    def prever_lote(self, textos: Sequence[str]) -> list[Predicao]:
        """Classifica varios textos de uma vez. A nota **nao** entra como entrada."""

    def prever(self, texto: str) -> Predicao:
        return self.prever_lote([texto])[0]
