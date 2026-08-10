from __future__ import annotations

from collections.abc import Sequence

EXPRESSOES: dict[str, tuple[str, str]] = {
    "PONTUALIDADE": ("pela pontualidade", "relatos de atraso"),
    "QUALIDADE": ("pela qualidade do serviço", "ressalvas quanto à qualidade"),
    "RAPIDEZ": ("pela rapidez", "relatos de demora"),
    "ATENDIMENTO": ("pelo atendimento", "ressalvas no atendimento"),
    "ORGANIZACAO": ("pela organização", "relatos de desorganização"),
    "PRECO": ("pelo preço justo", "ressalvas quanto ao preço"),
    "COMUNICACAO": ("pela comunicação", "falhas de comunicação"),
}


def _expressao(aspecto: str, positiva: bool) -> str:
    padrao = (f"pelo aspecto {aspecto.lower()}", f"ressalvas quanto a {aspecto.lower()}")
    return EXPRESSOES.get(aspecto, padrao)[0 if positiva else 1]


def _listar(itens: Sequence[str]) -> str:
    itens = list(itens)
    if not itens:
        return ""
    if len(itens) == 1:
        return itens[0]
    return f"{', '.join(itens[:-1])} e {itens[-1]}"


def gerar_resumo(
    pontos_fortes: Sequence[str],
    pontos_fracos: Sequence[str],
    percentual_positivo: float,
    comentarios_processados: int,
    minimo_comentarios: int = 3,
) -> str:

    if comentarios_processados < minimo_comentarios:
        return ""

    fortes = [_expressao(aspecto, positiva=True) for aspecto in pontos_fortes]
    fracos = [_expressao(aspecto, positiva=False) for aspecto in pontos_fracos]

    if fortes and fracos:
        return f"Clientes destacam o trabalho {_listar(fortes)}, com {_listar(fracos)}."
    if fortes:
        return f"Profissional elogiado principalmente {_listar(fortes)}."
    if fracos:
        return f"Clientes apontaram {_listar(fracos)}."

    if percentual_positivo >= 80:
        return "Avaliações majoritariamente positivas, sem um ponto forte predominante."
    if percentual_positivo <= 40:
        return "Avaliações majoritariamente negativas nos comentários recentes."
    return "Avaliações mistas nos comentários recentes."
