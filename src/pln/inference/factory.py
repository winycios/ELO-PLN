
from __future__ import annotations

from ..config import Config
from ..logging_utils import obter_logger
from .base import ClassificadorSentimento

logger = obter_logger(__name__)


def carregar_classificador(config: Config) -> ClassificadorSentimento:
    from .baseline_model import ClassificadorBaseline  # noqa: PLC0415

    classificador = ClassificadorBaseline(config.diretorio_modelo)
    logger.info(
        "Classificador carregado: backend=%s versao=%s",
        config.modelo.backend,
        classificador.versao,
    )
    return classificador
