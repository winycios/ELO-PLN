from __future__ import annotations

from ..schemas import ReputacaoProfissional

CAMPO = "reputacaoPln"

MAPPING_REPUTACAO_PLN = {
    CAMPO: {
        "type": "object",
        "dynamic": "strict",
        "properties": {
            "comentariosProcessados": {"type": "integer"},
            "percentualPositivo": {"type": "float"},
            "percentualNeutro": {"type": "float"},
            "percentualNegativo": {"type": "float"},
            "sentimentoMedio": {"type": "float"},
            "taxaInconsistencia": {"type": "float"},
            "pontosFortes": {"type": "keyword"},
            "pontosFracos": {"type": "keyword"},
            "resumo": {"type": "text", "index": False},
            "versaoModelo": {"type": "keyword"},
            "dataAtualizacao": {"type": "date"},
        },
    }
}


def documento_reputacao_pln(reputacao: ReputacaoProfissional) -> dict:
    return {
        CAMPO: {
            "comentariosProcessados": reputacao.comentarios_processados,
            "percentualPositivo": reputacao.percentual_positivo,
            "percentualNeutro": reputacao.percentual_neutro,
            "percentualNegativo": reputacao.percentual_negativo,
            "sentimentoMedio": reputacao.sentimento_medio,
            "taxaInconsistencia": reputacao.taxa_inconsistencia,
            "pontosFortes": list(reputacao.pontos_fortes),
            "pontosFracos": list(reputacao.pontos_fracos),
            "resumo": reputacao.resumo,
            "versaoModelo": reputacao.versao_modelo,
            "dataAtualizacao": reputacao.data_atualizacao,
        }
    }
