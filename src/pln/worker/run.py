from __future__ import annotations

import time
from collections.abc import Sequence

from ..config import Config
from ..inference.pipeline import AnalisadorComentarios
from ..logging_utils import obter_logger
from ..repository.base import RepositorioPln
from ..reputation.aggregate import agregar_reputacao
from ..schemas import AnaliseComentario, Avaliacao

logger = obter_logger(__name__)

class WorkerPln:
    def __init__(self, config: Config, repositorio: RepositorioPln, analisador: AnalisadorComentarios, ) -> None:
        self.config = config
        self.repositorio = repositorio
        self.analisador = analisador

    def processar_lote(self) -> dict:
        versao = self.analisador.classificador.versao
        pendentes = self.repositorio.buscar_avaliacoes_pendentes(versao_modelo=versao,limite=self.config.worker.tamanho_lote)
        if not pendentes:
            return {"pendentes": 0, "analisadas": 0, "profissionais": 0, "falhas": 0}

        analises, falhas = self._analisar_com_tolerancia(pendentes)
        if not analises:
            logger.warning("Lote de %d avaliacoes nao gerou analises", len(pendentes))
            return {
                "pendentes": len(pendentes),
                "analisadas": 0,
                "profissionais": 0,
                "falhas": falhas,
            }

        self.repositorio.salvar_analises(analises)
        profissionais = sorted({analise.profissional_id for analise in analises})
        self.recalcular_reputacoes(profissionais, versao)

        logger.info(
            "Lote processado: %d pendentes, %d analisadas, %d profissionais atualizados, %d falhas",
            len(pendentes),
            len(analises),
            len(profissionais),
            falhas,
        )
        return {"pendentes": len(pendentes),"analisadas": len(analises),"profissionais": len(profissionais),"falhas": falhas}

    def recalcular_reputacoes(self, profissional_ids: Sequence[int], versao_modelo: str | None = None) -> int:

        if not profissional_ids:
            return 0

        versao_modelo = versao_modelo or self.analisador.classificador.versao
        analises_por_profissional = self.repositorio.buscar_analises_por_profissional(
            profissional_ids
        )
        reputacoes = [
            agregar_reputacao(
                profissional_id=profissional_id,
                analises=analises,
                config=self.config.reputacao,
                versao_modelo=versao_modelo,
            )
            for profissional_id, analises in analises_por_profissional.items()
            if analises
        ]
        self.repositorio.salvar_reputacoes(reputacoes)
        self.repositorio.marcar_reindexacao([r.profissional_id for r in reputacoes])
        return len(reputacoes)

    def executar(self, continuo: bool = False) -> dict[str, int] | None:
        acumulado = {"lotes": 0, "analisadas": 0, "falhas": 0}

        while True:
            try:
                estatisticas = self.processar_lote()
                acumulado["lotes"] += 1
                acumulado["analisadas"] += estatisticas["analisadas"]
                acumulado["falhas"] += estatisticas["falhas"]
            except Exception:
                logger.exception("Falha ao processar lote; sera reprocessado na proxima rodada")
                estatisticas = {"pendentes": 0, "analisadas": 0}

            fila_cheia = estatisticas["pendentes"] >= self.config.worker.tamanho_lote

            if fila_cheia and estatisticas["analisadas"] == 0:
                fila_cheia = False

            if fila_cheia:
                continue
            if not continuo:
                return acumulado

            try:
                time.sleep(self.config.worker.intervalo_segundos)
            except KeyboardInterrupt:
                logger.info("Worker encerrado pelo usuario. Total: %s", acumulado)
                return acumulado


    def _analisar_com_tolerancia(self, avaliacoes: Sequence[Avaliacao]) -> tuple[list[AnaliseComentario], int]:
        try:
            return list(self.analisador.analisar(avaliacoes)), 0
        except Exception:  # noqa: BLE001
            logger.exception("Falha no lote; reprocessando avaliacao por avaliacao")

        analises: list[AnaliseComentario] = []
        falhas = 0
        for avaliacao in avaliacoes:
            try:
                analises.extend(self.analisador.analisar([avaliacao]))
            except Exception:
                falhas += 1
                logger.exception("Falha ao analisar avaliacao id=%s", avaliacao.avaliacao_reserva_id)
        return analises, falhas
