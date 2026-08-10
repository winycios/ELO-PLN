from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from ..config import Config
from ..io_utils import escrever_jsonl, ler_jsonl
from ..logging_utils import obter_logger
from ..schemas import AnaliseComentario, Avaliacao, ReputacaoProfissional, agora_iso
from .base import RepositorioPln

logger = obter_logger(__name__)


class JsonlRepositorio(RepositorioPln):
    def __init__(self, config: Config) -> None:
        self.config = config
        config.caminhos.preparar()
        self.arquivo_avaliacoes: Path = config.caminhos.dados_brutos / "avaliacoes.jsonl"
        self.arquivo_analises: Path = config.caminhos.dados_processados / "analises.jsonl"
        self.arquivo_reputacoes: Path = config.caminhos.dados_processados / "reputacoes.jsonl"
        self.arquivo_reindexacao: Path = (
            config.caminhos.dados_processados / "reindexacao_pendente.jsonl"
        )

    # ---------------------------------------------------------------- leitura

    def _carregar_avaliacoes(self) -> list[Avaliacao]:
        return [Avaliacao.from_dict(registro) for registro in ler_jsonl(self.arquivo_avaliacoes)]

    def _carregar_analises(self) -> list[AnaliseComentario]:
        return [AnaliseComentario.from_dict(r) for r in ler_jsonl(self.arquivo_analises)]

    def buscar_avaliacoes_com_comentario(self, limite: int | None = None) -> list[Avaliacao]:
        avaliacoes = [a for a in self._carregar_avaliacoes() if a.tem_comentario]
        return avaliacoes[:limite] if limite else avaliacoes

    def buscar_avaliacoes_pendentes(self, versao_modelo: str, limite: int) -> list[Avaliacao]:
        ja_analisadas = {
            analise.avaliacao_reserva_id
            for analise in self._carregar_analises()
            if analise.versao_modelo == versao_modelo
        }
        pendentes = [
            avaliacao
            for avaliacao in self._carregar_avaliacoes()
            if avaliacao.tem_comentario and avaliacao.avaliacao_reserva_id not in ja_analisadas
        ]
        return pendentes[:limite]

    def buscar_analises_por_profissional( self, profissional_ids: Sequence[int]) -> dict[int, list[AnaliseComentario]]:
        alvo = set(profissional_ids)
        agrupado: dict[int, list[AnaliseComentario]] = defaultdict(list)
        for analise in self._carregar_analises():
            if analise.profissional_id in alvo:
                agrupado[analise.profissional_id].append(analise)
        return dict(agrupado)

    # ----------------------------------------------------------------- escrita

    def salvar_analises(self, analises: Sequence[AnaliseComentario]) -> int:
        if not analises:
            return 0
        # Idempotencia por `avaliacao_reserva_id`, equivalente ao UNIQUE da tabela.
        existentes = {a.avaliacao_reserva_id: a for a in self._carregar_analises()}
        for analise in analises:
            existentes[analise.avaliacao_reserva_id] = analise
        escrever_jsonl(
            self.arquivo_analises,
            (item.to_dict() for item in sorted(existentes.values(), key=lambda a: a.avaliacao_reserva_id)),
        )
        return len(analises)

    def salvar_reputacoes(self, reputacoes: Sequence[ReputacaoProfissional]) -> int:
        if not reputacoes:
            return 0
        existentes = {
            registro["profissional_id"]: registro for registro in ler_jsonl(self.arquivo_reputacoes)
        }
        for reputacao in reputacoes:
            existentes[reputacao.profissional_id] = reputacao.to_dict()
        escrever_jsonl(
            self.arquivo_reputacoes,
            (existentes[chave] for chave in sorted(existentes)),
        )
        return len(reputacoes)

    def marcar_reindexacao(self, profissional_ids: Sequence[int]) -> int:
        if not profissional_ids:
            return 0
        pendentes = {
            registro["profissional_id"]: registro for registro in ler_jsonl(self.arquivo_reindexacao)
        }
        for profissional_id in profissional_ids:
            pendentes[profissional_id] = {
                "profissional_id": profissional_id,
                "solicitado_em": agora_iso(),
                "processado": False,
            }
        escrever_jsonl(self.arquivo_reindexacao, (pendentes[c] for c in sorted(pendentes)))
        return len(profissional_ids)

    def gravar_avaliacoes(self, avaliacoes: Sequence[Avaliacao]) -> int:
        """Auxiliar do modo offline: popula a base bruta (dados sinteticos ou export)."""
        return escrever_jsonl(self.arquivo_avaliacoes, (a.to_dict() for a in avaliacoes))
