from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ..io_utils import ler_json
from ..schemas import Predicao, Sentimento
from ..texto import colapsar_espacos
from .base import ClassificadorSentimento

ARQUIVO_MODELO = "modelo.joblib"
ARQUIVO_METADADOS = "metadata.json"


class ClassificadorBaseline(ClassificadorSentimento):
    def __init__(self, diretorio: Path) -> None:
        import joblib

        caminho_modelo = diretorio / ARQUIVO_MODELO
        if not caminho_modelo.exists():
            raise FileNotFoundError(
                f"Artefato do baseline nao encontrado em {caminho_modelo}. "
                "Rode `elo-pln treinar-baseline`."
            )
        self.pipeline = joblib.load(caminho_modelo)
        self.metadados = (
            ler_json(diretorio / ARQUIVO_METADADOS)
            if (diretorio / ARQUIVO_METADADOS).exists()
            else {}
        )
        self.versao = self.metadados.get("versaoModelo", diretorio.name)
        self.classes = [str(classe) for classe in self.pipeline.classes_]

    def prever_lote(self, textos: Sequence[str]) -> list[Predicao]:
        if not textos:
            return []
        limpos = [colapsar_espacos(texto or "") for texto in textos]
        probabilidades = self.pipeline.predict_proba(limpos)

        predicoes: list[Predicao] = []
        for linha in probabilidades:
            distribuicao = {classe: float(p) for classe, p in zip(self.classes, linha)}
            classe_vencedora = max(distribuicao, key=distribuicao.get)
            predicoes.append(
                Predicao(
                    sentimento=Sentimento(classe_vencedora),
                    confianca=distribuicao[classe_vencedora],
                    versao_modelo=self.versao,
                    probabilidades=distribuicao,
                )
            )
        return predicoes
