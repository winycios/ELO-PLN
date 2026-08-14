from __future__ import annotations

import random

from ..schemas import Avaliacao, Sentimento
from ..texto import remover_acentos, tokenizar

VERSAO_CATALOGO = "catalogo-sintetico-v2"

PIVOS_OBRIGATORIOS: tuple[str, ...] = (
    "horario",
    "prazo",
    "qualidade",
    "acabamento",
    "preco",
    "valor",
    "orcamento",
    "atendimento",
    "educado",
    "limpo",
    "entulho",
    "comunicacao",
    "avisou",
    "problema",
    "resolveu",
    "material",
    "ferramenta",
    "seguranca",
    "cuidado",
    "experiencia",
    "agenda",
    "garantia",
    "confianca",
    "combinado",
    "postura",
    "celular",
    "recomendo",
    "indico",
    "demais",
    "servico",
)


_CATALOGO: dict[str, dict[Sentimento, tuple[str, ...]]] = {
    "PONTUALIDADE": {
        Sentimento.POSITIVO: (
            "Chegou no horário combinado e começou na hora",
            "Profissional pontual, não atrasou nem um minuto",
            "Chegou adiantado e ainda terminou antes do prazo",
            "Pontualidade exemplar, chegou exatamente no horário marcado",
            "Respeitou o horário do início ao fim",
            "Cumpriu o prazo prometido sem precisar cobrar",
            "Marcou para as oito e às oito estava na porta",
            "Nunca atrasou nas duas vezes que contratei",
        ),
        Sentimento.NEUTRO: (
            "Chegou perto do horário marcado, com uns minutos de diferença",
            "Atrasou um pouco, mas avisou antes",
            "O horário foi mais ou menos o combinado",
            "Chegou fora do horário, porém terminou no prazo",
            "Nem sempre pontual, mas na média está de bom tamanho",
            "Cumpriu o prazo, embora tenha remarcado uma vez",
            "Chegou atrasado, mas o serviço saiu no mesmo dia",
            "O prazo foi o que ele tinha falado, nem antes nem depois",
        ),
        Sentimento.NEGATIVO: (
            "Atrasou mais de duas horas e não avisou",
            "Não respeitou o horário combinado nenhuma vez",
            "Faltou no dia marcado sem justificativa",
            "Chegou muito depois do horário e ainda reclamou",
            "Não cumpriu o prazo prometido",
            "Marcou três vezes e não apareceu em nenhuma",
            "Pontualidade péssima, sempre atrasado",
            "Estourou o prazo e deixou o serviço parado",
        ),
    },
    "QUALIDADE": {
        Sentimento.POSITIVO: (
            "Trabalho de qualidade, acabamento impecável",
            "Serviço caprichado, acabamento perfeito",
            "Qualidade acima do que eu esperava",
            "Fez um ótimo trabalho, nada a reclamar",
            "Acabamento bem feito, não precisei refazer nada",
            "Sem dúvida um serviço de primeira qualidade",
            "Trabalho benfeito, ficou melhor do que estava antes",
            "A qualidade do serviço justifica o valor",
        ),
        Sentimento.NEUTRO: (
            "Qualidade dentro do esperado, nada excepcional",
            "O acabamento poderia ser melhor, mas resolve",
            "Nem sempre caprichado, trabalho comum e qualidade mediana",
            "Serviço aceitável, acabamento simples",
            "A qualidade é a mesma dos outros que já contratei",
            "Fez o trabalho, nada a reclamar nem a elogiar no acabamento",
            "Qualidade razoável para o que foi cobrado",
            "O serviço ficou ok, sem nada de especial no acabamento",
        ),
        Sentimento.NEGATIVO: (
            "Trabalho de baixa qualidade, precisei refazer tudo",
            "Acabamento malfeito, ficou pior do que estava",
            "Serviço sem qualidade nenhuma",
            "Qualidade péssima, tive que chamar outro profissional",
            "O acabamento não ficou bom e ele não quis corrigir",
            "Trabalho porco, nada caprichado",
            "Nunca mais contrato, péssimo serviço",
            "A qualidade não corresponde ao que foi prometido",
        ),
    },
    "PRECO": {
        Sentimento.POSITIVO: (
            "Preço justo pelo trabalho entregue",
            "Cobrou o valor combinado, nada a reclamar",
            "Ótimo custo benefício, valeu cada centavo",
            "Preço acessível para a qualidade do serviço",
            "Orçamento honesto e abaixo do que eu esperava",
            "Valor bem abaixo dos outros orçamentos que peguei",
            "Preço bom e ainda parcelou para mim",
            "Cobrou barato para o tamanho do serviço",
        ),
        Sentimento.NEUTRO: (
            "Preço na média do mercado",
            "O valor foi o combinado, nem caro nem barato",
            "Orçamento parecido com os outros que pedi",
            "Cobrou o preço de tabela, sem desconto",
            "Preço mediano para o tipo de serviço",
            "O valor deu para pagar, mas não achei barato",
            "Orçamento dentro do esperado, sem novidade",
            "Preço aceitável, o serviço acompanhou",
        ),
        Sentimento.NEGATIVO: (
            "Preço absurdo para um serviço incompleto",
            "Cobrou muito acima do orçamento combinado",
            "Valor caro demais pelo que entregou",
            "Cobrança escondida, o preço mudou no final",
            "Orçamento enganoso, apareceu taxa que ninguém falou",
            "Cobrou a mais e não soube explicar o valor",
            "Preço alto e serviço ruim, péssimo custo benefício",
            "Achei o valor abusivo para uma hora de trabalho",
        ),
    },
    "ATENDIMENTO": {
        Sentimento.POSITIVO: (
            "Atendimento excelente, muito educado e atencioso",
            "Tratou minha família com muito respeito",
            "Atencioso do começo ao fim, explicou tudo com calma",
            "Pessoa educada, atendimento nota dez",
            "Muito simpático e paciente com as minhas dúvidas",
            "Atendimento cordial, dá gosto de contratar",
            "Foi gentil mesmo quando pedi para refazer um detalhe",
            "Bom atendimento, se preocupou em me deixar satisfeito",
        ),
        Sentimento.NEUTRO: (
            "Atendimento normal, nada demais",
            "Foi educado, mas bem seco na conversa",
            "Atendeu bem, sem muita conversa",
            "Tratamento comum, cumpriu o papel dele",
            "Atendimento razoável, nem simpático nem grosso",
            "Foi correto no trato, só isso",
            "Educado na medida, atendimento padrão",
            "Atendeu, cobrou o combinado e foi embora",
        ),
        Sentimento.NEGATIVO: (
            "Péssimo atendimento, muito grosso",
            "Não foi educado, foi desrespeitoso com a minha família",
            "Atendimento horrível, respondeu torto o tempo todo",
            "Não teve paciência nenhuma para explicar",
            "Tratou mal quando pedi para revisar o serviço",
            "Atendimento ruim, parecia com pressa de ir embora",
            "Grosseiro, levantou a voz dentro da minha casa",
            "Nem cumprimentou, atendimento frio e desagradável",
        ),
    },
    "ORGANIZACAO": {
        Sentimento.POSITIVO: (
            "Deixou tudo limpo e organizado no final",
            "Recolheu o entulho e varreu o local",
            "Muito organizado, protegeu os móveis antes de começar",
            "Terminou e deixou o ambiente mais limpo do que achou",
            "Não deixou sujeira nenhuma",
            "Trabalho limpo, sem bagunça na casa",
            "Organizou as ferramentas e limpou tudo antes de sair",
            "Cuidadoso com a limpeza durante todo o serviço",
        ),
        Sentimento.NEUTRO: (
            "Limpou o básico, sobrou um pouco de poeira",
            "Deixou razoavelmente limpo, tive que passar pano depois",
            "Recolheu o entulho, mas deixou marcas na parede",
            "Organização mediana, nada fora do comum",
            "Limpou o principal, o resto ficou comigo",
            "Deixou o local aceitável, nem limpo nem sujo",
            "A bagunça foi a esperada para esse tipo de obra",
            "Limpeza dentro do normal para o serviço",
        ),
        Sentimento.NEGATIVO: (
            "Deixou muita sujeira e não terminou o trabalho",
            "Foi embora e deixou entulho espalhado pela casa",
            "Nenhum cuidado com a limpeza, sujou tudo",
            "Deixou bagunça e não limpou nada",
            "Não deixou o piso limpo e nem pediu desculpa",
            "Desorganizado, perdeu ferramenta dentro da minha casa",
            "Terminou e a casa ficou pior de sujeira do que antes",
            "Não protegeu nada, manchou o sofá de tinta",
        ),
    },
    "COMUNICACAO": {
        Sentimento.POSITIVO: (
            "Comunicação clara, avisou com antecedência que estava a caminho",
            "Respondeu todas as mensagens rapidamente",
            "Explicou cada etapa do serviço antes de executar",
            "Manteve contato durante todo o processo",
            "Tirou as dúvidas com muita calma pelo aplicativo",
            "Deu retorno rápido sempre que precisei",
            "Avisou quando ia atrasar, comunicação impecável",
            "Explicou o problema em termos que eu entendi",
        ),
        Sentimento.NEUTRO: (
            "A comunicação foi ok e o resultado também",
            "Nem sempre respondeu rápido, demorava algumas horas",
            "Explicou o básico, sem entrar em detalhe",
            "Avisou em cima da hora, mas avisou",
            "Comunicação simples, resolveu pelo telefone",
            "Deu retorno quando cobrei, não antes",
            "Bom trabalho, porém a comunicação poderia melhorar",
            "Falou o necessário, comunicação padrão",
        ),
        Sentimento.NEGATIVO: (
            "Não respondeu minhas mensagens durante o serviço",
            "Comunicação péssima, sumiu por três dias",
            "Não avisou que não vinha, fiquei esperando à toa",
            "Não explicou nada do que estava fazendo",
            "Difícil de falar, não deu retorno nenhum",
            "Deixou no vácuo depois que perguntei do prazo",
            "Comunicação confusa, mudava a versão a cada ligação",
            "Não avisou do atraso e ainda ficou bravo quando cobrei",
        ),
    },
    "RESOLUCAO": {
        Sentimento.POSITIVO: (
            "Resolveu meu problema de primeira",
            "Identificou a causa rápido e consertou tudo",
            "O problema não voltou mais depois que ele arrumou",
            "Resolveu o que outros dois não conseguiram",
            "Consertou e ainda ajustou outra coisa sem cobrar",
            "Problema resolvido no mesmo dia",
            "Achou o vazamento na hora e resolveu",
            "Solucionou tudo o que eu tinha pedido",
        ),
        Sentimento.NEUTRO: (
            "Resolveu, mas precisou de uma segunda visita",
            "O problema foi resolvido pela metade",
            "Consertou o principal, o resto continua",
            "Deu para resolver, mas esperava um acabamento melhor",
            "Resolveu o problema do momento, pode voltar",
            "Arrumou, só que demorou mais do que devia",
            "Solução provisória, resolveu por enquanto",
            "Trabalho aceitável, tirou o problema do momento",
        ),
        Sentimento.NEGATIVO: (
            "O problema continuou depois que ele saiu",
            "Não resolveu o problema e ainda cobrou a mais",
            "Consertou errado, piorou o que já estava ruim",
            "Voltou duas vezes e o problema segue igual",
            "Não conseguiu resolver e sumiu",
            "Disse que resolveu, mas no dia seguinte voltou tudo",
            "Não corrigiu o que estava combinado",
            "Problema nenhum foi resolvido, dinheiro jogado fora",
        ),
    },
    "MATERIAIS": {
        Sentimento.POSITIVO: (
            "Usou material de primeira e ferramenta profissional",
            "Trouxe todo o material e as ferramentas adequadas",
            "Material de primeira qualidade, equipamento novo e bem cuidado",
            "Comprou o material pelo preço de custo para mim",
            "Chegou com tudo o que precisava, não faltou nada",
            "Equipamento profissional, deu para ver a diferença",
            "Material bem escolhido e durável",
            "Usou peça original, nada genérico",
        ),
        Sentimento.NEUTRO: (
            "Material era simples, mas cumpriu a função",
            "Usou o material que eu comprei, sem reclamar",
            "Ferramenta básica, deu conta do serviço",
            "Material padrão, nada de especial",
            "Trouxe parte do material, o resto foi comigo",
            "Equipamento comum, funcionou",
            "O material foi o de sempre, preço de mercado",
            "Ferramenta antiga, mas ele soube usar",
        ),
        Sentimento.NEGATIVO: (
            "Usou material vagabundo e ferramenta inadequada",
            "Faltou material e ainda quis que eu comprasse",
            "Material de péssima qualidade, quebrou em uma semana",
            "Chegou sem ferramenta nenhuma",
            "Cobrou material de primeira e usou o mais barato",
            "Equipamento sucateado, quase não deu conta",
            "Trouxe peça genérica sem me avisar",
            "Não trouxe o material combinado e atrasou tudo",
        ),
    },
    "SEGURANCA": {
        Sentimento.POSITIVO: (
            "Trabalhou com segurança e usou equipamento de proteção",
            "Muito cuidadoso, não deixou nenhum risco na casa",
            "Isolou a área antes de começar, tudo seguro",
            "Cuidado exemplar com as crianças por perto",
            "Desligou a energia antes de mexer, bem seguro",
            "Deixou tudo em segurança, sem fio exposto",
            "Usou luva e óculos de proteção o tempo todo",
            "Preocupado com a segurança da minha família",
        ),
        Sentimento.NEUTRO: (
            "Trabalhou sem equipamento, mas não houve problema",
            "Segurança básica, nada demais",
            "Tomou o cuidado mínimo necessário",
            "Não usou proteção, porém foi cuidadoso",
            "Segurança dentro do comum para esse tipo de serviço",
            "Deixou tudo em ordem, sem risco aparente",
            "Cuidado normal, nem mais nem menos",
            "Fez com atenção, embora sem os equipamentos",
        ),
        Sentimento.NEGATIVO: (
            "Deixou fio exposto e risco de acidente na minha casa",
            "Nenhum cuidado com segurança, quase se acidentou",
            "Trabalhou sem proteção e quebrou o vidro da janela",
            "Deixou o gás vazando, um perigo",
            "Sem segurança nenhuma, subiu numa escada bamba",
            "Descuidado, derrubou material perto das crianças",
            "Deixou a instalação num risco enorme",
            "Não teve cuidado nenhum com a minha casa",
        ),
    },
    "EXPERIENCIA": {
        Sentimento.POSITIVO: (
            "Profissional experiente, dominou o serviço do início ao fim",
            "Sabe o que faz, conhecimento técnico impressionante",
            "Muita experiência, resolveu sem titubear",
            "Notou um detalhe que ninguém tinha visto",
            "Domina o assunto, explicou o porquê de cada escolha",
            "Trabalha na área há anos e se percebe",
            "Profissional preparado, serviço técnico bem executado",
            "Sem dúvida tem conhecimento de sobra para o que eu precisava",
        ),
        Sentimento.NEUTRO: (
            "Parece ter pouca experiência, mas se virou bem",
            "Conhecimento suficiente para o serviço",
            "Não é especialista, porém deu conta",
            "Experiência mediana, resolveu o básico",
            "Sabe o essencial, pediu ajuda no que não conhecia",
            "Profissional comum, sem grande diferencial técnico",
            "Aprendendo ainda, mas caprichou",
            "Domínio razoável do serviço",
        ),
        Sentimento.NEGATIVO: (
            "Muito amador, não sabe o que faz",
            "Despreparado, sem experiência nenhuma",
            "Não domina o serviço, ficou pesquisando no celular",
            "Falta conhecimento técnico, errou o básico",
            "Se dizia experiente, mas não sabia montar",
            "Profissional despreparado, estragou a peça",
            "Nenhuma experiência, tive que ensinar o serviço",
            "Amador demais, não indico para nada técnico",
        ),
    },
    "DISPONIBILIDADE": {
        Sentimento.POSITIVO: (
            "Agenda flexível, conseguiu me encaixar no mesmo dia",
            "Atendeu no mesmo dia, disponibilidade imediata",
            "Fácil de agendar, respondeu na hora",
            "Conseguiu vir no fim de semana para me atender",
            "Vem sem falta toda vez que eu chamo de novo",
            "Remarcou sem problema quando eu precisei",
            "Encaixou meu serviço mesmo com a agenda cheia",
            "Disponibilidade ótima, atendeu fora do horário comercial",
        ),
        Sentimento.NEUTRO: (
            "Demorou uns dias para conseguir a agenda",
            "Agendamento normal, dentro do prazo dele",
            "Precisou remarcar uma vez, mas foi",
            "Agenda apertada, consegui para a semana seguinte",
            "Disponibilidade média, como qualquer profissional",
            "Deu para marcar sem muita dificuldade",
            "A data foi a que ele tinha livre",
            "Cumpriu a agenda combinada, serviço padrão",
        ),
        Sentimento.NEGATIVO: (
            "Difícil de agendar, cancelou em cima da hora",
            "Desmarcou em cima da hora sem nenhuma explicação",
            "Remarcou três vezes e no fim não veio",
            "Nunca tem horário, impossível de agendar",
            "Cancelou no dia e não deu satisfação",
            "Sumiu depois de marcar e nunca mais deu sinal",
            "Marca a agenda numa data e aparece em outra",
            "Disponibilidade zero, demorou um mês para responder",
        ),
    },
    "GARANTIA": {
        Sentimento.POSITIVO: (
            "Deu garantia do serviço e voltou para revisar sem cobrar",
            "Ofereceu três meses de garantia por escrito",
            "Voltou para conferir o serviço uma semana depois",
            "Garantia respeitada, resolveu na hora quando chamei",
            "Disse que voltaria sem falta se desse problema, e cumpriu",
            "Garantiu o trabalho e ainda deixou o contato",
            "Voltou de graça para ajustar um detalhe",
            "Assumiu a garantia sem discussão",
        ),
        Sentimento.NEUTRO: (
            "Falou de garantia, mas não deu nada por escrito",
            "Garantia de trinta dias, o padrão",
            "Disse que voltaria se precisasse, não precisei",
            "Garantia informal, na base da palavra",
            "Cobriria só a mão de obra, o material não",
            "Não perguntei da garantia e ele não ofereceu",
            "Voltou para revisar, mas cobrou a visita",
            "Garantia dentro do que se espera",
        ),
        Sentimento.NEGATIVO: (
            "Não deu garantia e se recusou a voltar",
            "Prometeu garantia e sumiu quando deu problema",
            "Disse que a garantia tinha vencido em uma semana",
            "Não quis voltar para corrigir o próprio erro",
            "Garantia nenhuma, lavou as mãos",
            "Chamei dentro da garantia e nunca mais respondeu",
            "Voltou e cobrou de novo pelo mesmo conserto",
            "Se recusou a assumir o defeito que ele causou",
        ),
    },
    "TRANSPARENCIA": {
        Sentimento.POSITIVO: (
            "Foi transparente do começo ao fim, informou o valor antes",
            "Orçamento detalhado, sem cobrança escondida",
            "Sem dúvida uma pessoa de confiança e muito honesta",
            "Avisou que a peça não precisava trocar, poderia ter mentido",
            "Honesto no orçamento e ágil na execução",
            "Deixei a casa com ele tranquilo, passa confiança",
            "Explicou o que dava e o que não dava, bem sincero",
            "Transparente até no que poderia dar errado",
        ),
        Sentimento.NEUTRO: (
            "Passou o valor por telefone, sem detalhar muito",
            "Confiança normal, não tenho o que falar",
            "Foi honesto no preço, embora não tenha detalhado",
            "Orçamento simples, sem muita transparência",
            "Não tive motivo para desconfiar",
            "Falou o valor no final, mas era o combinado",
            "Transparência mediana, o básico foi dito",
            "Passa confiança o suficiente para o serviço",
        ),
        Sentimento.NEGATIVO: (
            "Desonesto, me enganou no valor",
            "Não foi transparente, orçamento enganoso",
            "Não passa confiança, mexeu nas minhas coisas",
            "Mentiu sobre a peça para cobrar mais caro",
            "Sumiu depois do pagamento e não atendeu mais",
            "Escondeu que ia cobrar a visita",
            "Falta de honestidade, inventou um problema que não existia",
            "Não confio, sumiu com a chave da minha casa",
        ),
    },
    "CUMPRIMENTO": {
        Sentimento.POSITIVO: (
            "Cumpriu tudo o que prometeu, não deixou nada pendente",
            "Fez exatamente o que pedi, trabalho bem executado",
            "Entregou o combinado e ainda ajustou um detalhe extra",
            "Cumpriu o combinado à risca",
            "Fez tudo o que estava no orçamento, item por item",
            "Prometeu e entregou sem falta, sem enrolação",
            "Nada ficou pendente no final do serviço",
            "Cumpriu o que foi contratado e um pouco mais",
        ),
        Sentimento.NEUTRO: (
            "Cumpriu o que foi contratado, sem surpresas",
            "Fez o combinado, sem ir além",
            "Fez o que foi pedido, apenas isso",
            "Entregou o essencial, faltou um detalhe pequeno",
            "Cumpriu a maior parte do combinado",
            "Serviço entregue, sem mais comentários",
            "Fez o serviço conforme o combinado",
            "Entregou dentro do que estava escrito, nada além",
        ),
        Sentimento.NEGATIVO: (
            "Não fez o que foi combinado e deixou serviço pendente",
            "Prometeu e não fez, faltou parte do serviço",
            "Deixou metade do combinado sem terminar",
            "Não cumpriu nada do que estava no orçamento",
            "Abandonou o serviço pela metade",
            "Combinou uma coisa e entregou outra",
            "Ficou muita coisa pendente e ele não voltou",
            "Não entregou o que prometeu e ainda quis receber tudo",
        ),
    },
    "APRESENTACAO": {
        Sentimento.POSITIVO: (
            "Chegou uniformizado, postura profissional exemplar",
            "Muito profissional, respeitou minha casa o tempo todo",
            "Apresentação impecável, chegou limpo e identificado",
            "Postura séria, focado no serviço do início ao fim",
            "Se apresentou com crachá, passou segurança",
            "Educado, discreto e respeitoso dentro de casa",
            "Trabalhou concentrado, nem tocou no celular",
            "Boa apresentação, dá para confiar de cara",
        ),
        Sentimento.NEUTRO: (
            "Chegou sem uniforme, mas trabalhou direito",
            "Postura comum, nada que chame atenção",
            "Apresentação simples, sem identificação",
            "Mexeu no celular algumas vezes, nada demais",
            "Vestimenta normal para o tipo de serviço",
            "Postura profissional na medida",
            "Não se identificou, porém foi correto",
            "Apresentação dentro do esperado",
        ),
        Sentimento.NEGATIVO: (
            "Chegou sujo e ficou no celular o tempo todo",
            "Comportamento inadequado, falta de respeito",
            "Sem uniforme, sem identificação e sem postura nenhuma",
            "Ficou fumando dentro da minha casa",
            "Postura péssima, atendeu ligação pessoal o serviço inteiro",
            "Apresentação horrível, parecia recém-acordado",
            "Desrespeitoso, entrou nos cômodos sem pedir",
            "Ficou reclamando da vida em vez de trabalhar",
        ),
    },
    "RECOMENDACAO": {
        Sentimento.POSITIVO: (
            "Super recomendo, virou meu profissional fixo",
            "Recomendo demais, já indiquei para três vizinhos",
            "Indico a todos, serviço de qualidade",
            "Vou chamar de novo com certeza",
            "Recomendo sem medo, trabalho honesto",
            "Contrataria de novo sem pensar duas vezes",
            "Salvei o contato, recomendo para quem precisar",
            "Recomendo para serviço grande, dá conta",
        ),
        Sentimento.NEUTRO: (
            "Recomendo com ressalvas, depende do que você precisa",
            "Talvez contrate de novo, ainda não sei",
            "Não recomendo nem deixo de recomendar",
            "Serve para serviço simples, para os grandes não sei",
            "Recomendaria se o prazo não fosse apertado",
            "Indico apenas se estiver sem pressa",
            "Nem indico nem desaconselho, foi normal",
            "Pode ser uma opção, existem outros parecidos",
        ),
        Sentimento.NEGATIVO: (
            "Não recomendo, não vale a pena",
            "Nunca mais chamo, foi um transtorno",
            "Jamais contrataria de novo",
            "Não indico para ninguém, perdi tempo e dinheiro",
            "Não recomendo esse serviço para ninguém",
            "Me arrependi de ter contratado, não indico",
            "Procure outro profissional, esse não vale",
            "Não vale a pena, recomendo procurar outra pessoa",
        ),
    },
    "RAPIDEZ": {
        Sentimento.POSITIVO: (
            "Rápido, eficiente e cobrou o combinado",
            "Resolveu tudo rapidinho, nem vi o tempo passar",
            "Muito ágil, terminou em metade do tempo previsto",
            "Serviço rápido e bem feito, sem correria",
            "Foi veloz sem perder a qualidade",
            "Terminou antes do previsto e ainda revisou",
            "Ágil na execução e honesto no orçamento",
            "Rápido no atendimento e rápido no serviço",
        ),
        Sentimento.NEUTRO: (
            "O trabalho foi feito, mas demorou um pouco",
            "Demorou o esperado para esse tipo de serviço",
            "Nem rápido nem lento, no ritmo normal",
            "Levou o tempo que tinha falado",
            "Foi educado, mas o serviço demorou mais do que o previsto",
            "Demorou, porém entregou no mesmo dia",
            "Ritmo tranquilo, sem pressa e sem atraso",
            "O tempo foi razoável para o tamanho do serviço",
        ),
        Sentimento.NEGATIVO: (
            "Muito lento, levou o dia todo para algo simples",
            "Demorou demais e o resultado ficou ruim",
            "Enrolou o serviço inteiro e não terminou",
            "Levou três dias para um serviço de duas horas",
            "Lentidão absurda, parava a cada dez minutos",
            "Demorou uma eternidade e ainda ficou pela metade",
            "Arrastou o serviço para cobrar mais horas",
            "Muito devagar, perdi o dia inteiro esperando",
        ),
    },
}


def frases(rotulo: Sentimento) -> tuple[str, ...]:
    """Todas as frases do catalogo para uma classe, em ordem estavel."""
    return tuple(
        frase for eixo in _CATALOGO.values() for frase in eixo.get(rotulo, ())
    )


def catalogo_por_eixo() -> dict[str, dict[Sentimento, tuple[str, ...]]]:
    return _CATALOGO


def conferir_sobreposicao() -> dict[str, list[str]]:
    """Lista os pivos que NAO aparecem nas tres classes.

    Um pivo presente em uma classe so vira atalho lexical: foi exatamente assim
    que `preco` virou caracteristica positiva e `qualidade` virou negativa no
    catalogo v1. Retorna `{}` quando o catalogo esta saudavel.
    """
    # `tokenizar` e a mesma tokenizacao que o vetorizador de palavras enxerga,
    # entao a conferencia mede a sobreposicao real, nao uma aproximacao.
    por_classe = {
        rotulo: {palavra for frase in frases(rotulo) for palavra in tokenizar(frase)}
        for rotulo in Sentimento
    }

    faltantes: dict[str, list[str]] = {}
    for pivo in PIVOS_OBRIGATORIOS:
        ausentes = [
            rotulo.value for rotulo in Sentimento if pivo not in por_classe[rotulo]
        ]
        if ausentes:
            faltantes[pivo] = ausentes
    return faltantes


_SUFIXOS: dict[Sentimento, tuple[str, ...]] = {
    Sentimento.POSITIVO: ("", "", "", "!", "!!", " Obrigado!", " Valeu!", " Recomendo."),
    Sentimento.NEUTRO: ("", "", "", ".", "..", " É isso.", " Sem mais.", " No geral, ok."),
    Sentimento.NEGATIVO: ("", "", "", "!", "!!", " Não recomendo.", " Fica o aviso.", " Lamentável."),
}

_VOGAIS = "aeiou"


def _alongar_vogal(texto: str, aleatorio: random.Random) -> str:
    posicoes = [i for i, letra in enumerate(texto) if letra.lower() in _VOGAIS]
    if not posicoes:
        return texto
    posicao = aleatorio.choice(posicoes)
    repeticoes = aleatorio.randint(2, 3)
    return texto[:posicao] + texto[posicao] * repeticoes + texto[posicao + 1 :]


def _aplicar_ruido(texto: str, aleatorio: random.Random) -> str:
    sorteio = aleatorio.random()
    if sorteio < 0.35:
        return remover_acentos(texto)
    if sorteio < 0.60:
        return texto.lower()
    return _alongar_vogal(texto, aleatorio)


def gerar_avaliacoes(
    quantidade: int = 600,
    quantidade_profissionais: int = 30,
    seed: int = 42,
    proporcao_sem_comentario: float = 0.15,
    proporcao_inconsistente: float = 0.05,
    proporcao_positivo: float = 0.50,
    proporcao_neutro: float = 0.25,
    proporcao_ruido: float = 0.12,
) -> list[Avaliacao]:
    if proporcao_positivo + proporcao_neutro > 1.0:
        raise ValueError(
            "proporcao_positivo + proporcao_neutro nao pode passar de 1.0 "
            f"(recebido {proporcao_positivo} + {proporcao_neutro})."
        )

    aleatorio = random.Random(seed)
    avaliacoes: list[Avaliacao] = []
    limite_neutro = proporcao_positivo + proporcao_neutro

    for indice in range(1, quantidade + 1):
        profissional_id = aleatorio.randint(1, quantidade_profissionais)
        sorteio = aleatorio.random()
        if sorteio < proporcao_positivo:
            nota, rotulo_texto = aleatorio.choice([4, 5]), Sentimento.POSITIVO
        elif sorteio < limite_neutro:
            nota, rotulo_texto = 3, Sentimento.NEUTRO
        else:
            nota, rotulo_texto = aleatorio.choice([1, 2]), Sentimento.NEGATIVO

        comentario: str | None = aleatorio.choice(frases(rotulo_texto))

        if aleatorio.random() < proporcao_inconsistente:
            if nota >= 4:
                rotulo_texto = Sentimento.NEGATIVO
                comentario = aleatorio.choice(frases(rotulo_texto))
            elif nota <= 2:
                rotulo_texto = Sentimento.POSITIVO
                comentario = aleatorio.choice(frases(rotulo_texto))

        comentario += aleatorio.choice(_SUFIXOS[rotulo_texto])
        if aleatorio.random() < proporcao_ruido:
            comentario = _aplicar_ruido(comentario, aleatorio)

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
