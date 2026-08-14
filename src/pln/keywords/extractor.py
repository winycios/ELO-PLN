from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

from ..schemas import AspectoDetectado, Polaridade, Sentimento
from ..texto import (aplicar_expressoes_fixas, ha_negacao_no_escopo, normalizar_para_busca_com_limites)
from .aspects import ASPECTOS, JANELA_NEGACAO, NEGACOES, VERSAO_LEXICO


@dataclass(frozen=True, slots=True)
class _Entrada:
    aspecto: str
    termo: str
    polaridade_base: Polaridade | None  # None = neutro, herda do comentario
    padrao: re.Pattern[str]


def _compilar_entradas() -> list[_Entrada]:
    entradas: list[_Entrada] = []
    for aspecto in ASPECTOS:
        faixas = (
            (aspecto.positivos, Polaridade.POSITIVA),
            (aspecto.negativos, Polaridade.NEGATIVA),
            (aspecto.neutros, None),
        )
        for termos, polaridade in faixas:
            for termo in termos:
                termo_normalizado = aplicar_expressoes_fixas(termo)
                entradas.append(
                    _Entrada(
                        aspecto=aspecto.nome,
                        termo=termo,
                        polaridade_base=polaridade,
                        padrao=re.compile(rf"\b{re.escape(termo_normalizado)}\b"),
                    )
                )
    entradas.sort(key=lambda entrada: len(entrada.termo), reverse=True)
    return entradas


_ENTRADAS = _compilar_entradas()

_POLARIDADE_POR_SENTIMENTO = {
    Sentimento.POSITIVO: Polaridade.POSITIVA,
    Sentimento.NEGATIVO: Polaridade.NEGATIVA,
    Sentimento.NEUTRO: Polaridade.NEUTRA,
}

_INVERSA = {
    Polaridade.POSITIVA: Polaridade.NEGATIVA,
    Polaridade.NEGATIVA: Polaridade.POSITIVA,
    Polaridade.NEUTRA: Polaridade.NEUTRA,
}


class ExtratorAspectos:
    versao = VERSAO_LEXICO

    def extrair(self, texto: str, sentimento: Sentimento) -> list[AspectoDetectado]:
        aspectos, _ = self.extrair_com_evidencias(texto, sentimento)
        return aspectos

    def extrair_com_evidencias(
        self, texto: str, sentimento: Sentimento
    ) -> tuple[list[AspectoDetectado], dict[Polaridade, set[str]]]:
        """Extrai aspectos e separa evidencias cuja polaridade e explicita.

        Termos neutros que herdam o sentimento do comentario continuam no
        contrato de aspectos, mas nao podem votar na conciliacao do sentimento.
        """
        if not texto:
            return [], {}

        normalizado = normalizar_para_busca_com_limites(texto)
        ocupados = [False] * len(normalizado)
        encontrados: dict[tuple[str, Polaridade], AspectoDetectado] = {}
        evidencias: dict[Polaridade, set[str]] = defaultdict(set)

        for entrada in _ENTRADAS:
            for casamento in entrada.padrao.finditer(normalizado):
                inicio, fim = casamento.span()
                if any(ocupados[inicio:fim]):
                    continue
                for posicao in range(inicio, fim):
                    ocupados[posicao] = True

                polaridade = entrada.polaridade_base or _POLARIDADE_POR_SENTIMENTO[sentimento]
                if (
                    entrada.polaridade_base is not None
                    and self._tem_negacao_antes(normalizado, inicio)
                    and not self._termo_ja_negado(entrada.termo)
                ):
                    polaridade = _INVERSA[polaridade]

                if entrada.polaridade_base is not None:
                    evidencias[polaridade].add(entrada.aspecto)

                chave = (entrada.aspecto, polaridade)
                detectado = encontrados.get(chave)
                if detectado is None:
                    encontrados[chave] = AspectoDetectado(
                        aspecto=entrada.aspecto,
                        polaridade=polaridade,
                        ocorrencias=1,
                        termos=[entrada.termo],
                    )
                else:
                    detectado.ocorrencias += 1
                    if entrada.termo not in detectado.termos:
                        detectado.termos.append(entrada.termo)

        return (
            sorted(
                encontrados.values(),
                key=lambda a: (-a.ocorrencias, a.aspecto, a.polaridade.value),
            ),
            dict(evidencias),
        )

    @staticmethod
    def _tem_negacao_antes(texto_normalizado: str, inicio: int) -> bool:
        return ha_negacao_no_escopo(texto_normalizado[:inicio].split(), JANELA_NEGACAO)

    @staticmethod
    def _termo_ja_negado(termo: str) -> bool:
        return any(token in NEGACOES for token in aplicar_expressoes_fixas(termo).split())
