from __future__ import annotations

import random

from ..schemas import Avaliacao, Sentimento

_POSITIVOS = [
    "Chegou no horário e realizou um ótimo trabalho",
    "Serviço de qualidade, recomendo demais",
    "Profissional pontual, educado e muito caprichoso",
    "Excelente atendimento, resolveu tudo rapidinho",
    "Trabalho impecável e preço justo",
    "Muito atencioso, explicou cada etapa do serviço",
    "Deixou tudo limpo e organizado no final",
    "Superou minhas expectativas, voltarei a contratar",
    "Rápido, eficiente e cobrou o combinado",
    "Adorei o resultado, acabamento perfeito",
    "Pontualidade exemplar e comunicação clara",
    "Preço acessível para a qualidade entregue",
]

_NEUTROS = [
    "Fez o serviço conforme o combinado",
    "Atendeu bem, nada demais",
    "O trabalho foi feito, mas demorou um pouco",
    "Serviço dentro do esperado",
    "Cumpriu o que foi contratado, sem surpresas",
    "Razoável, atendeu a necessidade básica",
    "Chegou um pouco atrasado mas resolveu",
    "Preço na média do mercado",
    "Bom trabalho, porém a comunicação poderia melhorar",
    "Nem ótimo nem ruim, ficou ok",
]

_NEGATIVOS = [
    "Atrasou mais de duas horas e nem avisou",
    "Serviço mal feito, tive que chamar outro profissional",
    "Não respondeu minhas mensagens durante o serviço",
    "Cobrou muito acima do orçamento combinado",
    "Deixou muita sujeira e não terminou o trabalho",
    "Péssimo atendimento, muito grosso",
    "Faltou no dia marcado sem justificativa",
    "Trabalho de baixa qualidade, precisei refazer",
    "Demorou demais e o resultado ficou ruim",
    "Não cumpriu o prazo prometido",
]

_SUFIXOS = {
    Sentimento.POSITIVO: ("", " Obrigado!", " Recomendo.", "!!!"),
    Sentimento.NEUTRO: ("", " ..."),
    Sentimento.NEGATIVO: ("", " Não recomendo.", " ...", "!!!"),
}


def gerar_avaliacoes(
    quantidade: int = 600,
    quantidade_profissionais: int = 30,
    seed: int = 42,
    proporcao_sem_comentario: float = 0.15,
    proporcao_inconsistente: float = 0.05,
) -> list[Avaliacao]:
    aleatorio = random.Random(seed)
    avaliacoes: list[Avaliacao] = []

    for indice in range(1, quantidade + 1):
        profissional_id = aleatorio.randint(1, quantidade_profissionais)
        sorteio = aleatorio.random()
        if sorteio < 0.65:
            nota, corpus, rotulo_texto = (
                aleatorio.choice([4, 5]),
                _POSITIVOS,
                Sentimento.POSITIVO,
            )
        elif sorteio < 0.85:
            nota, corpus, rotulo_texto = 3, _NEUTROS, Sentimento.NEUTRO
        else:
            nota, corpus, rotulo_texto = (
                aleatorio.choice([1, 2]),
                _NEGATIVOS,
                Sentimento.NEGATIVO,
            )

        comentario: str | None = aleatorio.choice(corpus) + aleatorio.choice(
            _SUFIXOS[rotulo_texto]
        )

        if aleatorio.random() < proporcao_inconsistente:
            if nota >= 4:
                comentario = aleatorio.choice(_NEGATIVOS)
                rotulo_texto = Sentimento.NEGATIVO
            elif nota <= 2:
                comentario = aleatorio.choice(_POSITIVOS)
                rotulo_texto = Sentimento.POSITIVO

        if aleatorio.random() < proporcao_sem_comentario:
            comentario = aleatorio.choice([None, "", "   "])

        avaliacoes.append(
            Avaliacao(
                avaliacao_reserva_id=indice,
                profissional_id=profissional_id,
                nota=nota,
                comentario=comentario,
                data_avaliacao=(
                    f"2026-0{aleatorio.randint(1, 8)}-"
                    f"{aleatorio.randint(10, 28)}T10:00:00"
                ),
                rotulo_sentimento=rotulo_texto,
            )
        )

    return avaliacoes
