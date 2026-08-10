from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from ..config import ConfigReputacao
from ..schemas import (
    AnaliseComentario,
    Polaridade,
    ReputacaoProfissional,
    Sentimento,
)
from .summary import gerar_resumo


def _percentual(parte: int, total: int) -> float:
    return round(100.0 * parte / total, 2) if total else 0.0


def _aspectos_por_polaridade(
    analises: Sequence[AnaliseComentario],
    polaridade: Polaridade,
    minimo_avaliacoes: int,
    maximo: int,
) -> list[str]:

    avaliacoes_por_aspecto: dict[str, set[int]] = defaultdict(set)
    ocorrencias_por_aspecto: dict[str, int] = defaultdict(int)

    for analise in analises:
        for aspecto in analise.aspectos:
            if aspecto.polaridade is polaridade:
                avaliacoes_por_aspecto[aspecto.aspecto].add(analise.avaliacao_reserva_id)
                ocorrencias_por_aspecto[aspecto.aspecto] += aspecto.ocorrencias

    elegiveis = [
        (nome, len(avaliacoes), ocorrencias_por_aspecto[nome])
        for nome, avaliacoes in avaliacoes_por_aspecto.items()
        if len(avaliacoes) >= minimo_avaliacoes
    ]
    elegiveis.sort(key=lambda item: (-item[1], -item[2], item[0]))
    return [nome for nome, _, _ in elegiveis[:maximo]]


def agregar_reputacao(
    profissional_id: int,
    analises: Sequence[AnaliseComentario],
    config: ConfigReputacao,
    versao_modelo: str,
) -> ReputacaoProfissional:
    total = len(analises)
    contagem = {classe: 0 for classe in Sentimento}
    soma_ponderada = 0.0
    soma_pesos = 0.0
    inconsistencias = 0

    for analise in analises:
        contagem[analise.sentimento] += 1
        peso = (
            config.peso_avaliacao_inconsistente if analise.possui_inconsistencia else 1.0
        )
        soma_ponderada += analise.sentimento.valor_normalizado * peso
        soma_pesos += peso
        inconsistencias += int(analise.possui_inconsistencia)

    sentimento_medio = round(soma_ponderada / soma_pesos, 4) if soma_pesos else 0.0

    pontos_fortes = _aspectos_por_polaridade(
        analises,
        Polaridade.POSITIVA,
        config.minimo_ocorrencias_aspecto,
        config.maximo_pontos_fortes,
    )
    pontos_fracos = _aspectos_por_polaridade(
        analises,
        Polaridade.NEGATIVA,
        config.minimo_ocorrencias_aspecto,
        config.maximo_pontos_fortes,
    )

    percentual_positivo = _percentual(contagem[Sentimento.POSITIVO], total)

    return ReputacaoProfissional(
        profissional_id=profissional_id,
        comentarios_processados=total,
        quantidade_positivo=contagem[Sentimento.POSITIVO],
        quantidade_neutro=contagem[Sentimento.NEUTRO],
        quantidade_negativo=contagem[Sentimento.NEGATIVO],
        percentual_positivo=percentual_positivo,
        percentual_neutro=_percentual(contagem[Sentimento.NEUTRO], total),
        percentual_negativo=_percentual(contagem[Sentimento.NEGATIVO], total),
        sentimento_medio=sentimento_medio,
        quantidade_inconsistencias=inconsistencias,
        taxa_inconsistencia=_percentual(inconsistencias, total),
        pontos_fortes=pontos_fortes,
        pontos_fracos=pontos_fracos,
        resumo=gerar_resumo(
            pontos_fortes=pontos_fortes,
            pontos_fracos=pontos_fracos,
            percentual_positivo=percentual_positivo,
            comentarios_processados=total,
            minimo_comentarios=config.minimo_comentarios_resumo,
        ),
        versao_modelo=versao_modelo,
    )
