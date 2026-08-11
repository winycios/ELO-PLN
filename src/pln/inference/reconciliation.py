from __future__ import annotations

from ..schemas import Polaridade, Predicao, Sentimento

_SENTIMENTO_POR_POLARIDADE = {
    Polaridade.POSITIVA: Sentimento.POSITIVO,
    Polaridade.NEGATIVA: Sentimento.NEGATIVO,
}


def conciliar_com_aspectos(
    predicao: Predicao,
    evidencias: dict[Polaridade, set[str]],
    minimo_aspectos: int = 2,
    fator_evidencia: float = 2.0,
) -> Predicao:
    positivas = evidencias.get(Polaridade.POSITIVA, set())
    negativas = evidencias.get(Polaridade.NEGATIVA, set())
    if positivas and negativas:
        return predicao

    if len(positivas) >= minimo_aspectos:
        polaridade = Polaridade.POSITIVA
        quantidade = len(positivas)
    elif len(negativas) >= minimo_aspectos:
        polaridade = Polaridade.NEGATIVA
        quantidade = len(negativas)
    else:
        return predicao

    alvo = _SENTIMENTO_POR_POLARIDADE[polaridade]
    if not predicao.probabilidades:
        return predicao

    escores = dict(predicao.probabilidades)
    if alvo.value not in escores:
        return predicao
    escores[alvo.value] *= fator_evidencia**quantidade

    vencedor = max(escores, key=escores.get)
    if vencedor != alvo.value:
        return predicao

    total = sum(escores.values())
    probabilidades = {
        classe: valor / total for classe, valor in escores.items()
    }
    return Predicao(
        sentimento=alvo,
        confianca=probabilidades[alvo.value],
        versao_modelo=predicao.versao_modelo,
        probabilidades=probabilidades,
    )
