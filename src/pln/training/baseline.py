from __future__ import annotations

import platform
import sys

from ..config import Config
from ..dataset.prepare import carregar_split
from ..io_utils import escrever_json, ler_json
from ..logging_utils import obter_logger
from ..schemas import CLASSES_STR, ExemploRotulado
from ..texto import normalizar_para_busca
from .metadata import montar_metadados

logger = obter_logger(__name__)

HIPERPARAMETROS = {
    "vetorizador": "TfidfVectorizer",
    "ngram_range": [1, 2],
    "min_df": 2,
    "sublinear_tf": True,
    "analyzer": "word",
    "classificador": "LogisticRegression",
    "C": 4.0,
    "max_iter": 1000,
    "class_weight": "balanced",
    "solver": "lbfgs",
}


def _construir_pipeline(seed: int):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    preprocessor=normalizar_para_busca,
                    ngram_range=tuple(HIPERPARAMETROS["ngram_range"]),
                    min_df=HIPERPARAMETROS["min_df"],
                    sublinear_tf=HIPERPARAMETROS["sublinear_tf"],
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    C=HIPERPARAMETROS["C"],
                    max_iter=HIPERPARAMETROS["max_iter"],
                    class_weight=HIPERPARAMETROS["class_weight"],
                    solver=HIPERPARAMETROS["solver"],
                    random_state=seed,
                ),
            ),
        ]
    )


def treinar(config: Config) -> dict:
    """Treina no split de treino, mede na validacao e versiona o artefato."""
    import joblib

    from ..evaluation.metrics import calcular_metricas

    config.caminhos.preparar()
    treino: list[ExemploRotulado] = carregar_split(config, "treino")
    validacao: list[ExemploRotulado] = carregar_split(config, "validacao")
    if not treino:
        raise ValueError("Split de treino vazio. Rode `elo-pln preparar` antes.")

    pipeline = _construir_pipeline(config.dataset.seed)
    pipeline.fit(
        [exemplo.texto for exemplo in treino],
        [exemplo.rotulo.value for exemplo in treino],
    )

    metricas_validacao = {}
    if validacao:
        preditos = pipeline.predict([exemplo.texto for exemplo in validacao])
        metricas_validacao = calcular_metricas(
            [exemplo.rotulo.value for exemplo in validacao], list(preditos), CLASSES_STR
        )
        logger.info("Validacao — macro-F1 %.4f", metricas_validacao["macroF1"])

    diretorio = config.caminhos.modelos / f"{config.modelo.versao}-baseline"
    diretorio.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, diretorio / "modelo.joblib")

    caminho_meta_dataset = config.caminhos.splits / "metadata.json"
    metadados = montar_metadados(
        config=config,
        backend="baseline",
        modelo_base="tfidf+logistic-regression",
        hiperparametros=HIPERPARAMETROS,
        metricas_validacao=metricas_validacao,
        metadados_dataset=ler_json(caminho_meta_dataset) if caminho_meta_dataset.exists() else {},
        extras={
            "python": sys.version.split()[0],
            "plataforma": platform.platform(),
            "vocabulario": len(pipeline.named_steps["tfidf"].vocabulary_),
        },
    )
    escrever_json(diretorio / "metadata.json", metadados)

    logger.info("Baseline gravado em %s", diretorio)
    return metadados
