from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ..schemas import AnaliseComentario, Avaliacao, ReputacaoProfissional


class RepositorioPln(ABC):
    @abstractmethod
    def buscar_avaliacoes_pendentes(self, versao_modelo: str, limite: int) -> list[Avaliacao]:
        """Avaliacoes com comentario ainda sem analise para a versao de modelo dada."""

    @abstractmethod
    def buscar_avaliacoes_com_comentario(self, limite: int | None = None) -> list[Avaliacao]:
        """Todas as avaliacoes com comentario, usadas para montar o dataset."""

    @abstractmethod
    def salvar_analises(self, analises: Sequence[AnaliseComentario]) -> int:
        """Grava (ou substitui) o resultado por avaliacao. Idempotente por avaliacao."""

    @abstractmethod
    def buscar_analises_por_profissional(
            self, profissional_ids: Sequence[int]
    ) -> dict[int, list[AnaliseComentario]]:
        """Analises ja gravadas, agrupadas por profissional, para a agregacao."""

    @abstractmethod
    def salvar_reputacoes(self, reputacoes: Sequence[ReputacaoProfissional]) -> int:
        """Grava o agregado por profissional. Idempotente por profissional."""

    @abstractmethod
    def marcar_reindexacao(self, profissional_ids: Sequence[int]) -> int:
        """Sinaliza ao lado Java que estes profissionais mudaram e devem ir ao ES."""

    def fechar(self) -> None:
        """Libera recursos. Implementacoes sem conexao nao precisam sobrescrever."""

    def __enter__(self) -> "RepositorioPln":
        return self

    def __exit__(self, *_excecao) -> None:
        self.fechar()
