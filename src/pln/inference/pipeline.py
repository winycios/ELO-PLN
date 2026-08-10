from __future__ import annotations

from collections.abc import Sequence

from ..config import Config
from ..dataset.clean import comentario_utilizavel, limpar_comentario
from ..keywords.extractor import ExtratorAspectos
from ..logging_utils import obter_logger
from ..schemas import AnaliseComentario, Avaliacao, Predicao
from .base import ClassificadorSentimento
from .inconsistency import possui_inconsistencia

logger = obter_logger(__name__)


class AnalisadorComentarios:
    def __init__(self,classificador: ClassificadorSentimento,config: Config,extrator: ExtratorAspectos | None = None,) -> None:
        self.classificador = classificador
        self.config = config
        self.extrator = extrator or ExtratorAspectos()

    def analisar(self, avaliacoes: Sequence[Avaliacao]) -> list[AnaliseComentario]:
        elegiveis: list[tuple[Avaliacao, str]] = []
        for avaliacao in avaliacoes:
            texto = limpar_comentario(avaliacao.comentario)
            if comentario_utilizavel(texto, self.config.dataset.tamanho_minimo_comentario):
                elegiveis.append((avaliacao, texto))

        if not elegiveis:
            return []

        predicoes = self.classificador.prever_lote([texto for _, texto in elegiveis])

        analises: list[AnaliseComentario] = []
        for (avaliacao, texto), predicao in zip(elegiveis, predicoes):
            analises.append(self._montar(avaliacao, texto, predicao))
        return analises

    def analisar_texto(self, texto: str, nota: int | None = None) -> dict:
        limpo = limpar_comentario(texto)
        predicao = self.classificador.prever(limpo)
        aspectos = self.extrator.extrair(limpo, predicao.sentimento)
        resultado = {
            **predicao.to_dict(),
            "aspectos": [aspecto.to_dict() for aspecto in aspectos],
        }
        if nota is not None:
            resultado["possuiInconsistencia"] = possui_inconsistencia(nota,predicao.sentimento,predicao.confianca,self.config.modelo.confianca_minima)
        return resultado

    def _montar(self, avaliacao: Avaliacao, texto: str, predicao: Predicao) -> AnaliseComentario:
        aspectos = self.extrator.extrair(texto, predicao.sentimento)
        return AnaliseComentario(
            avaliacao_reserva_id=avaliacao.avaliacao_reserva_id,
            profissional_id=avaliacao.profissional_id,
            sentimento=predicao.sentimento,
            confianca=predicao.confianca,
            possui_inconsistencia=possui_inconsistencia(
                avaliacao.nota,
                predicao.sentimento,
                predicao.confianca,
                self.config.modelo.confianca_minima,
            ),
            versao_modelo=predicao.versao_modelo,
            aspectos=aspectos,
        )
