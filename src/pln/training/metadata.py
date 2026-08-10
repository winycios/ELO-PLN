from __future__ import annotations

import sys
from importlib import metadata as _metadata
from typing import Any

from ..config import Config
from ..dataset.clean import REGRAS_LIMPEZA, VERSAO_LIMPEZA
from ..keywords.aspects import VERSAO_LEXICO
from ..schemas import agora_iso

PACOTES_RASTREADOS = ("scikit-learn", "numpy", "joblib")


def versoes_dependencias() -> dict[str, str]:
    versoes: dict[str, str] = {"python": sys.version.split()[0]}
    for pacote in PACOTES_RASTREADOS:
        try:
            versoes[pacote] = _metadata.version(pacote)
        except _metadata.PackageNotFoundError:
            continue
    return versoes


def montar_metadados(
    config: Config,
    backend: str,
    modelo_base: str,
    hiperparametros: dict[str, Any],
    metricas_validacao: dict[str, Any],
    metadados_dataset: dict[str, Any],
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "versaoModelo": config.modelo.versao,
        "backend": backend,
        "modeloBase": modelo_base,
        "treinadoEm": agora_iso(),
        "seed": config.dataset.seed,
        "versaoDataset": metadados_dataset.get("versaoDataset", config.dataset.versao_dataset),
        "datasetSintetico": metadados_dataset.get("sintetico", False),
        "tamanhoParticoes": metadados_dataset.get("tamanhoParticoes", {}),
        "distribuicaoTreino": metadados_dataset.get("distribuicaoTreino", {}),
        "versaoLimpeza": VERSAO_LIMPEZA,
        "regrasLimpeza": REGRAS_LIMPEZA,
        "versaoLexicoAspectos": VERSAO_LEXICO,
        "hiperparametros": hiperparametros,
        "metricasValidacao": metricas_validacao,
        "dependencias": versoes_dependencias(),
        **(extras or {}),
    }
