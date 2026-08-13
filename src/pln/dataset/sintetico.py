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
    "Pessoa de confiança e muito honesta",
    "Muito cuidadoso, protegeu os móveis antes de começar",
    "Trabalhou com segurança e usou equipamento de proteção",
    "Profissional experiente, dominou o serviço do início ao fim",
    "Sabe o que faz, conhecimento técnico impressionante",
    "Trouxe o material e as ferramentas adequadas",
    "Usou material de primeira, equipamento profissional",
    "Agenda flexível, conseguiu me encaixar no mesmo dia",
    "Atendeu no mesmo dia, disponibilidade imediata",
    "Deu garantia do serviço e voltou para revisar sem cobrar",
    "Orçamento detalhado, sem cobrança escondida",
    "Foi transparente do começo ao fim, informou o valor antes",
    "Cumpriu tudo o que prometeu, não deixou nada pendente",
    "Fez exatamente o que pedi, trabalho bem executado",
    "Chegou uniformizado, postura profissional exemplar",
    "Muito profissional, respeitou minha casa o tempo todo",
    "Super recomendo, virou meu profissional fixo",
    "Resolveu meu problema de primeira, indico a todos",
    "Identificou o problema rápido e consertou tudo",
    "Ótimo custo benefício, valeu cada centavo",
    "Comunicação clara, avisou com antecedência que estava a caminho",
    "Tirou todas as dúvidas com muita calma",
    "Serviço de primeira, acabamento perfeito e preço honesto",
    "Educado, pontual e muito organizado",
    "Trabalho caprichado, limpou tudo depois",
    "Chegou adiantado e terminou no prazo",
    "Honesto no orçamento e ágil na execução",
    "Excelente atendimento do início ao fim, nota dez",
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
    "Serviço ok, sem nada que se destaque",
    "Fez o que foi pedido, apenas isso",
    "O orçamento foi claro, mas o acabamento poderia ser melhor",
    "Chegou no horário, porém esqueceu parte do material",
    "Trabalho comum, dentro do que eu esperava",
    "Atendeu, cobrou o valor combinado e foi embora",
    "Serviço mediano, nada a reclamar nem a elogiar",
    "Foi educado, mas o serviço demorou mais do que o previsto",
    "Precisou de uma segunda visita, mas ficou pronto",
    "Material era simples, mas cumpriu a função",
    "A comunicação foi ok e o resultado também",
    "Fez o combinado, sem ir além",
    "Preço mediano para o tipo de serviço",
    "Chegou perto do horário marcado",
    "Trabalho aceitável, tirou o problema do momento",
    "Nada excepcional, mas deu para levar",
    "Cumpriu a agenda combinada, serviço padrão",
    "Deu para resolver, mas esperava um acabamento melhor",
    "Serviço entregue, sem mais comentários",
    "Nem melhor nem pior do que os outros que já contratei",
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
    "Não deu garantia e se recusou a voltar",
    "Sumiu depois do pagamento e não atendeu mais",
    "Cobrança escondida, o valor mudou no final",
    "Não foi transparente, orçamento enganoso",
    "Não fez o que foi combinado e deixou serviço pendente",
    "Prometeu e não fez, faltou parte do serviço",
    "Muito amador, não sabe o que faz",
    "Despreparado, sem experiência nenhuma",
    "Usou material vagabundo e ferramenta inadequada",
    "Faltou material e ainda quis que eu comprasse",
    "Difícil de agendar, cancelou em cima da hora",
    "Desmarcou em cima da hora sem nenhuma explicação",
    "Deixou fio exposto e risco de acidente na minha casa",
    "Não teve cuidado nenhum com a minha casa",
    "Desonesto, me enganou no valor",
    "Não passa confiança, mexeu nas minhas coisas",
    "Chegou sujo e ficou no celular o tempo todo",
    "Comportamento inadequado, falta de respeito",
    "Não recomendo, não vale a pena",
    "Nunca mais contrato, péssimo serviço",
    "O problema continuou depois que ele saiu",
    "Não resolveu o problema e ainda cobrou a mais",
    "Preço absurdo para um serviço incompleto",
    "Muito lento, levou o dia todo para algo simples",
    "Mal educado e desrespeitoso com a minha família",
    "Deixou entulho e não limpou nada",
    "Difícil de falar, não deu retorno nenhum",
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
