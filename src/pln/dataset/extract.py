from __future__ import annotations

from ..config import Config
from ..io_utils import escrever_jsonl
from ..logging_utils import obter_logger
from ..repository import criar_repositorio
from ..schemas import Avaliacao
from .clean import anonimizar
from .prepare import ARQUIVO_BRUTO

logger = obter_logger(__name__)


def extrair(config: Config, limite: int | None = None) -> int:
    config.caminhos.preparar()
    with criar_repositorio(config) as repositorio:
        avaliacoes = repositorio.buscar_avaliacoes_com_comentario(limite=limite)

    anonimizadas = [
        Avaliacao(
            avaliacao_reserva_id=avaliacao.avaliacao_reserva_id,
            profissional_id=avaliacao.profissional_id,
            nota=avaliacao.nota,
            comentario=anonimizar(avaliacao.comentario or ""),
            data_avaliacao=avaliacao.data_avaliacao,
        )
        for avaliacao in avaliacoes
    ]

    caminho = config.caminhos.dados_brutos / ARQUIVO_BRUTO
    total = escrever_jsonl(caminho, (item.to_dict() for item in anonimizadas))
    logger.info("Extraidas %d avaliacoes com comentario para %s", total, caminho)
    return total


def gerar_sinteticas(config: Config, quantidade: int = 600, quantidade_profissionais: int = 30, proporcao_positivo: float = 0.50, proporcao_neutro: float = 0.25, ) -> int:
    from ..repository.jsonl_repo import JsonlRepositorio
    from .sintetico import conferir_sobreposicao, gerar_avaliacoes

    config.caminhos.preparar()
    avaliacoes = gerar_avaliacoes(
        quantidade=quantidade,
        quantidade_profissionais=quantidade_profissionais,
        seed=config.dataset.seed,
        proporcao_positivo=proporcao_positivo,
        proporcao_neutro=proporcao_neutro,
    )
    total = JsonlRepositorio(config).gravar_avaliacoes(avaliacoes)
    logger.warning(
        "Geradas %d avaliacoes SINTETICAS. Servem para exercitar o pipeline, "
        "nunca para metricas do TCC.",
        total,
    )
    return total
