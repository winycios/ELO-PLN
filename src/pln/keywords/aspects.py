from __future__ import annotations

from dataclasses import dataclass, field

VERSAO_LEXICO = "lexico-aspectos-v1"

NEGACOES = frozenset({"nao", "nunca", "nem", "jamais", "sem"})
JANELA_NEGACAO = 3


@dataclass(frozen=True, slots=True)
class Aspecto:
    nome: str
    rotulo: str
    positivos: tuple[str, ...] = ()
    negativos: tuple[str, ...] = ()
    neutros: tuple[str, ...] = field(default=())


ASPECTOS: tuple[Aspecto, ...] = (
    Aspecto(
        nome="PONTUALIDADE",
        rotulo="Pontualidade",
        positivos=(
            "pontual",
            "pontualidade",
            "chegou no horario",
            "chegou na hora",
            "no horario combinado",
            "no horario",
            "dentro do prazo",
            "cumpriu o prazo",
            "cumpriu o horario",
            "chegou cedo",
        ),
        negativos=(
            "atrasou",
            "atraso",
            "atrasado",
            "chegou tarde",
            "fora do prazo",
            "nao cumpriu o prazo",
            "nao cumpriu o horario",
            "nao apareceu",
            "faltou no dia",
            "remarcou varias vezes",
            "horas de atraso",
        ),
    ),
    Aspecto(
        nome="QUALIDADE",
        rotulo="Qualidade",
        positivos=(
            "otimo trabalho",
            "excelente trabalho",
            "otimo servico",
            "excelente servico",
            "trabalho impecavel",
            "servico impecavel",
            "impecavel",
            "acabamento perfeito",
            "bem feito",
            "benfeito",
            "caprichoso",
            "capricho",
            "caprichado",
            "trabalho de qualidade",
            "servico de qualidade",
            "qualidade do servico",
            "qualidade do trabalho",
        ),
        negativos=(
            "mal feito",
            "malfeito",
            "baixa qualidade",
            "precisei refazer",
            "tive que refazer",
            "tive que chamar outro",
            "servico ruim",
            "trabalho ruim",
            "resultado ruim",
            "ficou ruim",
            "pessimo trabalho",
            "pessimo servico",
            "nao terminou o trabalho",
            "nao terminou o servico",
        ),
        neutros=("qualidade", "acabamento", "resultado"),
    ),
    Aspecto(
        nome="RESOLUCAO",
        rotulo="Resolução",
        positivos=(
            "resolveu meu problema",
            "resolveu o problema",
            "problema resolvido",
            "corrigiu meu problema",
            "corrigiu o problema",
            "resolveu tudo",
            "solucionou o problema",
            "consertou o problema",
        ),
        negativos=(
            "nao resolveu meu problema",
            "nao resolveu o problema",
            "nao resolveu",
            "nao corrigiu meu problema",
            "nao corrigiu o problema",
            "nao corrigiu",
            "nao solucionou",
            "problema nao resolvido",
            "problema continuou",
            "defeito continuou",
            "continua com problema",
            "tive que chamar novamente",
        ),
        neutros=("problema", "defeito"),
    ),
    Aspecto(
        nome="RAPIDEZ",
        rotulo="Rapidez",
        positivos=(
            "rapido",
            "rapidinho",
            "rapidez",
            "agil",
            "agilidade",
            "resolveu rapido",
            "eficiente",
            "eficiencia",
        ),
        negativos=(
            "demorou demais",
            "demorou muito",
            "demorou",
            "demora",
            "demorado",
            "muito lento",
            "lento",
        ),
    ),
    Aspecto(
        nome="ATENDIMENTO",
        rotulo="Atendimento",
        positivos=(
            "otimo atendimento",
            "excelente atendimento",
            "bom atendimento",
            "muito atencioso",
            "atencioso",
            "educado",
            "gentil",
            "simpatico",
            "prestativo",
            "cordial",
            "paciente",
        ),
        negativos=(
            "pessimo atendimento",
            "mal atendimento",
            "mal educado",
            "maleducado",
            "sem educacao",
            "muito grosso",
            "grosseiro",
            "rude",
            "antipatico",
        ),
        neutros=("atendimento",),
    ),
    Aspecto(
        nome="ORGANIZACAO",
        rotulo="Organização",
        positivos=(
            "deixou tudo limpo",
            "deixou tudo organizado",
            "muito organizado",
            "organizado",
            "organizacao",
            "limpou tudo",
        ),
        negativos=(
            "deixou muita sujeira",
            "deixou sujeira",
            "muita sujeira",
            "sujeira",
            "bagunca",
            "desorganizado",
        ),
    ),
    Aspecto(
        nome="PRECO",
        rotulo="Preço",
        positivos=(
            "preco justo",
            "valor justo",
            "preco acessivel",
            "preco honesto",
            "otimo custo beneficio",
            "custo beneficio",
            "cobrou o combinado",
            "barato",
        ),
        negativos=(
            "acima do orcamento",
            "cobrou a mais",
            "preco alto",
            "muito caro",
            "caro",
            "abusivo",
            "cobrou muito",
        ),
        neutros=("preco", "orcamento", "valor cobrado"),
    ),
    Aspecto(
        nome="COMUNICACAO",
        rotulo="Comunicação",
        positivos=(
            "comunicacao clara",
            "otima comunicacao",
            "explicou cada etapa",
            "explicou tudo",
            "explicou",
            "sempre respondeu",
            "respondeu rapido",
            "manteve contato",
        ),
        negativos=(
            "nao respondeu",
            "nao deu retorno",
            "sem retorno",
            "dificil de falar",
            "nao avisou",
            "nao respondia",
            "comunicacao poderia melhorar",
        ),
        neutros=("comunicacao",),
    ),
)

_POR_NOME = {aspecto.nome: aspecto for aspecto in ASPECTOS}


def rotulo_amigavel(nome_aspecto: str) -> str:
    aspecto = _POR_NOME.get(nome_aspecto)
    return aspecto.rotulo if aspecto else nome_aspecto.capitalize()


def obter_aspecto(nome: str) -> Aspecto | None:
    return _POR_NOME.get(nome)
