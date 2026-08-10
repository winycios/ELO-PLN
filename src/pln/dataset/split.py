from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass

from ..schemas import ExemploRotulado
from ..texto import normalizar_para_busca


@dataclass(slots=True)
class Particoes:
    treino: list[ExemploRotulado]
    validacao: list[ExemploRotulado]
    teste: list[ExemploRotulado]

    def resumo(self) -> dict[str, int]:
        return {
            "treino": len(self.treino),
            "validacao": len(self.validacao),
            "teste": len(self.teste),
        }


def _chave_grupo(texto: str) -> str:
    return hashlib.sha1(normalizar_para_busca(texto).encode("utf-8")).hexdigest()


def dividir(
    exemplos: list[ExemploRotulado],
    seed: int,
    proporcao_treino: float = 0.70,
    proporcao_validacao: float = 0.15,
) -> Particoes:
    if not exemplos:
        return Particoes([], [], [])

    grupos: dict[str, list[ExemploRotulado]] = defaultdict(list)
    for exemplo in exemplos:
        grupos[_chave_grupo(exemplo.texto)].append(exemplo)

    por_classe: dict[str, list[list[ExemploRotulado]]] = defaultdict(list)
    for chave, itens in grupos.items():
        rotulos = [item.rotulo.value for item in itens]
        rotulo_grupo = max(set(rotulos), key=rotulos.count)
        por_classe[rotulo_grupo].append(itens)

    treino: list[ExemploRotulado] = []
    validacao: list[ExemploRotulado] = []
    teste: list[ExemploRotulado] = []

    for rotulo in sorted(por_classe):
        blocos = sorted(
            por_classe[rotulo],
            key=lambda itens: hashlib.sha1(
                f"{seed}:{_chave_grupo(itens[0].texto)}".encode()
            ).hexdigest(),
        )
        total = sum(len(bloco) for bloco in blocos)
        limite_treino = total * proporcao_treino
        limite_validacao = total * (proporcao_treino + proporcao_validacao)

        acumulado = 0
        for bloco in blocos:
            if acumulado < limite_treino:
                treino.extend(bloco)
            elif acumulado < limite_validacao:
                validacao.extend(bloco)
            else:
                teste.extend(bloco)
            acumulado += len(bloco)

    return Particoes(treino=treino, validacao=validacao, teste=teste)
