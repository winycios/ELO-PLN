from __future__ import annotations

from collections.abc import Sequence

from ..schemas import CLASSES_STR


def calcular_metricas(
    verdadeiros: Sequence[str],
    preditos: Sequence[str],
    classes: Sequence[str] = tuple(CLASSES_STR),
) -> dict:
    from sklearn.metrics import (
        accuracy_score,
        confusion_matrix,
        f1_score,
        precision_recall_fscore_support,
    )

    classes = list(classes)
    precisao, recall, f1, suporte = precision_recall_fscore_support(
        verdadeiros, preditos, labels=classes, zero_division=0
    )
    matriz = confusion_matrix(verdadeiros, preditos, labels=classes)

    return {
        "total": len(verdadeiros),
        "classes": classes,
        "acuracia": float(accuracy_score(verdadeiros, preditos)),
        "macroF1": float(f1_score(verdadeiros, preditos, labels=classes, average="macro", zero_division=0)),
        "microF1": float(f1_score(verdadeiros, preditos, labels=classes, average="micro", zero_division=0)),
        "f1Ponderado": float(
            f1_score(verdadeiros, preditos, labels=classes, average="weighted", zero_division=0)
        ),
        "porClasse": {
            classe: {
                "precisao": float(precisao[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "suporte": int(suporte[i]),
            }
            for i, classe in enumerate(classes)
        },
        "matrizConfusao": matriz.tolist(),
        "distribuicaoVerdadeira": {c: list(verdadeiros).count(c) for c in classes},
        "distribuicaoPredita": {c: list(preditos).count(c) for c in classes},
    }


def formatar_metricas(metricas: dict, titulo: str = "Metricas") -> str:
    linhas = [
        f"## {titulo}",
        "",
        f"- Exemplos avaliados: **{metricas['total']}**",
        f"- Acuracia: **{metricas['acuracia']:.4f}**",
        f"- **macro-F1: {metricas['macroF1']:.4f}**",
        f"- F1 ponderado: {metricas['f1Ponderado']:.4f}",
        "",
        "| Classe | Precisao | Recall | F1 | Suporte |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for classe, valores in metricas["porClasse"].items():
        linhas.append(
            f"| {classe} | {valores['precisao']:.4f} | {valores['recall']:.4f} "
            f"| {valores['f1']:.4f} | {valores['suporte']} |"
        )

    classes = metricas["classes"]
    linhas += ["", "Matriz de confusao (linha = verdadeiro, coluna = predito):", ""]
    linhas.append("| | " + " | ".join(classes) + " |")
    linhas.append("| --- |" + " ---: |" * len(classes))
    for indice, classe in enumerate(classes):
        valores = " | ".join(str(v) for v in metricas["matrizConfusao"][indice])
        linhas.append(f"| **{classe}** | {valores} |")

    linhas += [
        "",
        f"Distribuicao verdadeira: {metricas['distribuicaoVerdadeira']}",
        f"Distribuicao predita: {metricas['distribuicaoPredita']}",
    ]
    return "\n".join(linhas)

