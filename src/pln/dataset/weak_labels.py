from __future__ import annotations

from ..schemas import ExemploRotulado, Sentimento

MAPA_NOTA_ROTULO: dict[int, Sentimento] = {
    1: Sentimento.NEGATIVO,
    2: Sentimento.NEGATIVO,
    3: Sentimento.NEUTRO,
    4: Sentimento.POSITIVO,
    5: Sentimento.POSITIVO,
}


def rotulo_fraco(nota: int) -> Sentimento:
    try:
        return MAPA_NOTA_ROTULO[int(nota)]
    except KeyError as erro:
        raise ValueError(f"Nota fora do intervalo esperado de 1 a 5: {nota!r}") from erro


def marcar_revisao_manual(exemplo: ExemploRotulado, rotulo_revisado: Sentimento) -> ExemploRotulado:
    exemplo.rotulo = rotulo_revisado
    exemplo.origem_rotulo = "manual"
    return exemplo


def distribuicao(exemplos: list[ExemploRotulado]) -> dict[str, int]:
    contagem = {classe.value: 0 for classe in Sentimento}
    for exemplo in exemplos:
        contagem[exemplo.rotulo.value] += 1
    return contagem
