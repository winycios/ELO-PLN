# Elo — Módulo de PLN

Implementação em Python do módulo de Processamento de Linguagem Natural da plataforma Elo,
conforme `doc/contexto-implementacao-pln-recomendacoes.md`.

O módulo faz três coisas e só três:

1. **classifica o sentimento** de um comentário de avaliação (`POSITIVO`, `NEUTRO`, `NEGATIVO`);
2. **extrai aspectos** do comentário (pontualidade, resolução, qualidade, preço…);
3. **agrega a reputação textual** de cada profissional e monta um resumo por template.

Tudo roda **localmente**, sem chamada a API externa de IA. O MySQL continua sendo a fonte de
verdade, a aplicação Java continua sendo a API pública e o Elasticsearch continua sendo a
projeção de leitura — este módulo apenas produz dados derivados e sinaliza quem precisa ser
reindexado.

---

## 1. Como o módulo funciona

### 1.1. O fluxo, de ponta a ponta

```
Avaliação salva no MySQL pela API Java   (a avaliação nunca depende do PLN para ser salva)
        ↓
Worker Python encontra as pendentes      (as que ainda não têm análise para a versão do modelo)
        ↓
Classificação de sentimento              ← baseline TF-IDF + regressão logística
Extração de aspectos (léxico)            ← regras locais e auditáveis
Conciliação por evidências explícitas    ← proteção conservadora do baseline
Regra de inconsistência nota × texto     ← só aqui a nota é usada
        ↓
Grava avaliacao_analise_pln              (uma linha por avaliação)
        ↓
Reagrega profissional_reputacao_pln      (percentuais, sentimento médio, pontos fortes, resumo)
        ↓
Marca o profissional para reindexação    (fila lida pelo Java)
        ↓
Java reindexa no Elasticsearch e monta os carrosséis
```

O processamento é **assíncrono** por decisão do documento (seção 6.3): a avaliação é salva
imediatamente e analisada logo depois. Não existe FastAPI aqui — se o worker cair, nada se
perde, porque a próxima execução reencontra as avaliações sem análise.

### 1.2. As três etapas por dentro

**Sentimento.** O classificador recebe **apenas o texto**. A nota nunca entra como
característica — se entrasse, a regra de inconsistência seria circular. A primeira versão usa
TF-IDF de palavras e caracteres + regressão logística: um modelo supervisionado leve e
executado localmente. A normalização preserva os tokens originais e acrescenta marcadores de
escopo (`não chegou` gera `NEG_chegou`), enquanto os n-gramas de caracteres toleram parte dos
erros de digitação. Cada análise gravada carrega a `versao_modelo` que a produziu, o que permite
auditar e reprocessar. Uma integração neural é apenas possibilidade futura e não faz parte desta
implementação.

**Aspectos.** Um léxico controlado (`keywords/aspects.py`) casa termos sobre o texto
normalizado (minúsculas, sem acento, sem pontuação). Regras do casamento:

- sinônimos são consolidados no aspecto canônico — `pontual`, `pontualidade` e
  `chegou no horário` viram todos `PONTUALIDADE`;
- o `ATRASO` citado no documento é representado como `PONTUALIDADE` **negativa**: mesma
  dimensão, sinal invertido, para não aparecer duas vezes no resumo;
- expressões longas vencem palavras contidas nelas — `não respondeu` não conta também como
  `respondeu`;
- uma negação até 3 tokens antes inverte a polaridade (`não foi pontual`);
- termos neutros (`preço`, `atendimento`) herdam a polaridade do sentimento do comentário.
- falhas de solução são consolidadas em `RESOLUCAO` (`não corrigiu`, `problema continuou`).

**Conciliação.** Quando pelo menos dois aspectos canônicos distintos têm polaridade explícita
na mesma direção, não existe evidência explícita contrária e as probabilidades do classificador
permitem a troca, essas evidências podem corrigir a classe global. Termos neutros que herdaram
o sentimento não votam nessa etapa. A confiança retornada é recalculada sobre os escores
combinados, em vez de reutilizar uma probabilidade incompatível com a classe corrigida.

Há também extração por TF-IDF (`keywords/tfidf.py`), usada como apoio de calibração para
descobrir aspectos ainda ausentes do léxico — ela **não** alimenta o texto exibido ao usuário,
porque vocabulário livre não é revisável.

**Inconsistência.** `nota ≥ 4` com texto negativo, ou `nota ≤ 2` com texto positivo. É um
**sinal interno**: reduz o peso daquela avaliação na reputação textual e nada mais. Não é
acusação de fraude, não vai para o contrato da API e não aparece na interface. A marcação só
acontece quando o modelo está acima da confiança mínima — sem esse piso, predições incertas
gerariam inconsistências em massa.

**Reputação.** Agregação por profissional com duas travas do documento:

- avaliações inconsistentes entram com peso `0,3` (configurável) no sentimento médio;
- um aspecto só vira ponto forte/fraco se aparecer em pelo menos N **avaliações distintas** —
  um comentário que repete "pontual, muito pontual" não promove o aspecto sozinho.
- se um aspecto for selecionado como ponto forte, ele não será repetido nos pontos fracos.

**Resumo.** Templates fechados (`reputation/summary.py`), sem modelo generativo. Quando não há
evidência suficiente, o resumo sai vazio — o que não é erro: o Java simplesmente omite a linha
do card e cai no fallback quantitativo.

---

## 2. Instalação

```bash
cd pln
python -m venv .venv && source .venv/bin/activate   # ou reaproveite o venv do projeto
pip install -e .            # baseline + worker  (scikit-learn, leve)
pip install -e '.[dev]'     # + pytest
pip install -e '.[mysql]'   # + PyMySQL — só para rodar contra o banco
```

## 3. Rodando sem banco de dados (5 minutos)

O modo offline usa arquivos JSONL em `data` no lugar do MySQL e dados sintéticos no lugar das
avaliações reais. Serve para exercitar todo o pipeline antes de existir volume real:

```bash
elo-pln gerar-sinteticos --quantidade 800 --profissionais 25   # popula data/raw/
elo-pln preparar --sintetico                                   # limpa, rotula, divide
elo-pln treinar-baseline                                       # models/sentimento-ptbr-v1-baseline/
elo-pln avaliar --split teste                                  # reports/*.md e *.json
elo-pln worker                                                 # analisa e agrega reputação
elo-pln exportar-es                                            # fragmentos para o Elasticsearch
```

> ⚠️ Os dados sintéticos vêm de templates e **superestimam** qualquer classificador. Seu
> rótulo descreve o texto, inclusive quando a nota foi intencionalmente invertida para testar
> inconsistência. O
> `metadata.json` e o relatório marcam o dataset como sintético justamente para que essas
> métricas nunca sejam reportadas como resultado do TCC.

Análise avulsa, para inspeção manual:

```bash
$ elo-pln analisar --texto "Não chegou no horário, e não corrigiu meu problema" --nota 1
{
  "sentimento": "NEGATIVO",
  "confianca": 0.8158,
  "versaoModelo": "sentimento-ptbr-v2",
  "comentario": "Não chegou no horário, e não corrigiu meu problema",
  "nota": 1,
  "aspectos": [
    {"aspecto": "PONTUALIDADE", "polaridade": "NEGATIVA", "ocorrencias": 1, "termos": ["chegou no horario"]},
    {"aspecto": "RESOLUCAO",    "polaridade": "NEGATIVA", "ocorrencias": 1, "termos": ["nao corrigiu meu problema"]}
  ],
  "possuiInconsistencia": false
}
```

## 4. Rodando com dados reais

```bash
# 1. Crie as tabelas de PLN
mysql -u root -p database_elo < src/pln/repository/script.sql

# 2. Aponte o módulo para o banco
export ELO_PLN_REPOSITORIO=mysql
export ELO_DB_HOST=localhost ELO_DB_NAME=database_elo ELO_DB_USER=... ELO_DB_PASSWORD=...

# 3. Extraia e prepare (os comentários já saem anonimizados do passo de extração)
elo-pln extrair
elo-pln preparar

# 4. Revisão manual do teste — obrigatória, porque os rótulos vêm da nota
elo-pln exportar-revisao --tamanho 200     # gera data/splits/teste_amostra_revisao.csv
#    ... revise a coluna `rotulo_revisado` em uma planilha ...
elo-pln aplicar-revisao

# 5. Treinamento e avaliação do classificador
elo-pln treinar-baseline
elo-pln avaliar --split teste

# 6. Worker em produção
elo-pln worker --continuo
```

O `SELECT` de `repository/mysql_repo.py:SQL_AVALIACOES` já segue o schema real: parte de
`avaliacao_reserva`, percorre `orcamento` e `servico` e mantém apenas avaliações cujo usuário
avaliado é o profissional contratado. Ele ainda pode ser sobrescrito por
`ELO_PLN_SQL_AVALIACOES` em outra implantação. O módulo escreve nas tabelas derivadas de PLN e
publica pedidos de reindexação na `search_outbox` existente.

## 5. Comandos

| Comando | O que faz |
| --- | --- |
| `gerar-sinteticos` | Popula `data/raw` com avaliações sintéticas (modo offline) |
| `extrair` | Lê avaliações com comentário do repositório e anonimiza |
| `preparar` | Limpa, aplica rótulo fraco e divide treino/validação/teste |
| `exportar-revisao` / `aplicar-revisao` | Ciclo de revisão manual do conjunto de teste |
| `treinar-baseline` | TF-IDF de palavras/caracteres + regressão logística |
| `avaliar` | Métricas + relatório Markdown/JSON em `reports` |
| `analisar` | Analisa um comentário avulso |
| `worker` | Processa pendentes, agrega reputação, marca reindexação |
| `reputacao` | Recalcula os agregados sem reprocessar comentários |
| `exportar-es` | Gera os fragmentos `reputacaoPln` |
| `info` | Mostra configuração, artefato ativo e macro-F1 de validação |

## 6. Configuração

Tudo por variável de ambiente (`src/pln/config.py`). Nenhum limiar fica escondido no meio das
regras.

| Variável | Padrão | Para que serve |
| --- | --- | --- |
| `ELO_PLN_VERSAO_MODELO` | `sentimento-ptbr-v2` | Versão gravada em cada análise |
| `ELO_PLN_VERSAO_DATASET` | `v2` | Versão do conjunto preparado |
| `ELO_PLN_SEED` | `42` | Reprodutibilidade (split e treino) |
| `ELO_PLN_REPOSITORIO` | `jsonl` | `jsonl` (offline) ou `mysql` |
| `ELO_PLN_LOTE` | `200` | Tamanho do lote do worker |
| `ELO_PLN_INTERVALO` | `60` | Segundos entre rodadas no modo `--contínuo` |
| `ELO_PLN_CONFIANCA_MINIMA` | `0.55` | Piso para marcar inconsistência |
| `ELO_PLN_MIN_ASPECTOS_CONCILIACAO` | `2` | Aspectos explícitos distintos exigidos para corrigir a classe |
| `ELO_PLN_FATOR_EVIDENCIA_ASPECTO` | `2.0` | Multiplicador por aspecto explícito concordante |
| `ELO_PLN_PESO_INCONSISTENTE` | `0.3` | Peso de uma avaliação inconsistente na reputação |
| `ELO_PLN_MIN_OCORRENCIAS_ASPECTO` | `2` | Avaliações distintas para um aspecto virar ponto forte |
| `ELO_PLN_MIN_COMENTARIOS_RESUMO` | `3` | Mínimo de comentários para exibir resumo textual |
| `ELO_PLN_MAX_PONTOS` | `3` | Máximo de pontos fortes/fracos |
| `ELO_DB_HOST`, `ELO_DB_PORT`, `ELO_DB_NAME`, `ELO_DB_USER`, `ELO_DB_PASSWORD` | — | Conexão MySQL |

Os valores acima são **calibração inicial**, como o documento pede — devem ser reajustados
depois de observar a distribuição real dos dados e documentados nos resultados do TCC.

## 7. Estrutura

```
pln/
├── data/                        # raw, processed, splits (fora do Git)
├── models/                      # artefatos treinados + metadata.json (fora do Git)
├── reports/                     # relatórios de avaliação (fora do Git)
├── src/pln/
│   ├── config.py                # todos os limiares configuráveis
│   ├── schemas.py               # contratos de dados (Avaliacao, Analise, Reputacao…)
│   ├── texto.py                 # normalizações compartilhadas
│   ├── dataset/                 # extract, clean, weak_labels, split, prepare, sintetico
│   ├── training/                # baseline e metadata (reprodutibilidade)
│   ├── evaluation/              # metrics, report
│   ├── inference/               # base, baseline_model, inconsistency, pipeline
│   ├── keywords/                # aspects (léxico), extractor, tfidf
│   ├── reputation/              # aggregate, summary, es_document
│   ├── repository/              # base, jsonl_repo, mysql_repo, script.sql
│   ├── worker/                  # run.py
│   └── cli.py
└── tests/
```

## 8. Persistência

O módulo cria duas tabelas derivadas e integra-se à outbox existente (`repository/schema.sql`):

- **`avaliacao_analise_pln`** — uma linha por avaliação: sentimento, confiança, inconsistência,
  aspectos em JSON, versão do modelo. Único por `fk_id_avaliacao_reserva`, gravado com `UPSERT`.
- **`profissional_reputacao_pln`** — o agregado que o Elasticsearch consome. Existe para que a
  busca não precise percorrer todas as avaliações.
- **`search_outbox`** — outbox já existente no banco real. O Python inclui o profissional quando
  sua reputação muda; a aplicação Java consome o registro e atualiza o Elasticsearch.

## 9. Integração com Java e Elasticsearch

`reputation/es_document.py` é o contrato de handoff: define o objeto `reputacaoPln` e o mapping correspondente.

```json
{
  "reputacaoPln": {
    "comentariosProcessados": 42,
    "percentualPositivo": 88.1,
    "percentualNeutro": 7.1,
    "percentualNegativo": 4.8,
    "sentimentoMedio": 0.83,
    "taxaInconsistencia": 2.4,
    "pontosFortes": ["PONTUALIDADE", "QUALIDADE"],
    "pontosFracos": [],
    "resumo": "Profissional elogiado principalmente pela pontualidade e pela qualidade do serviço.",
    "versaoModelo": "sentimento-ptbr-v1",
    "dataAtualizacao": "2026-08-10T15:12:48+00:00"
  }
}
```

## 10. Avaliação e reprodutibilidade

`elo-pln avaliar` produz macro-F1, precisão/recall/F1 por classe, matriz de confusão,
distribuição das classes e exemplos de erro. **A acurácia é calculada mas não é o critério** —
com maioria de avaliações positivas ela mascara o desempenho nas classes minoritárias. A
macro-F1 e os resultados de `NEUTRO` e `NEGATIVO` devem receber atenção especial.

Todo artefato treinado carrega um `metadata.json` ao lado dos pesos, com versão do dataset,
regras de limpeza, seed, modelo-base, hiperparâmetros, métricas de validação, versão do léxico
de aspectos e versões das dependências. Se o artefato for copiado para outra máquina, o rastro
vai junto.

Cuidados já embutidos no pipeline:

- o conjunto de teste é separado antes de qualquer ajuste e fica congelado;
- comentários textualmente idênticos ficam todos do mesmo lado da divisão, senão o teste mede
  memorização;
- a divisão é determinística por hash + seed, sem depender do estado global do `random`;
- `class_weight="balanced"` no baseline, para não premiar o classificador que responde sempre
  `POSITIVO`.

## 11. Privacidade

- a anonimização (e-mail, telefone, CPF/CNPJ, URL, números longos) acontece **na extração**,
  antes de o texto tocar o disco em `data/raw`;
- os logs registram apenas identificadores e métricas, nunca o comentário;
- `data`, `models` e `reports` estão no `.gitignore` — dados reais e artefatos grandes não
  são versionados.

## 12. Estado atual e o que falta

**Implementado (Fases 1 a 4 do documento, escopo Python da seção 6.1):** preparação de dataset,
classificador TF-IDF de palavras/caracteres + regressão logística, avaliação, inferência local,
extração de aspectos, conciliação por evidências explícitas, regra de
inconsistência, resumo por template, agregação de reputação, worker, persistência (MySQL e
offline) e o contrato do documento do Elasticsearch.

**Não implementado, porque é código Java (Fases 5 e 6):** publicação do evento/outbox após a
avaliação, consumo da fila de reindexação, criação da nova versão do índice e reindexação,
score de recomendação, regras de selo e montagem do contrato dos carrosséis. Este repositório
não contém o projeto Java; a seção 9 acima define exatamente o que o lado Java precisa consumir.

**Pendências do documento (seção 17) que continuam abertas** e devem ser confirmadas com dados
reais antes do treinamento definitivo: volume de comentários disponível, distribuição das notas,
hardware para treino, janela de popularidade regional, limiares e prioridade dos selos, forma final de
persistência das palavras-chave e nome/versionamento do novo índice.

Uma integração com modelo neural permanece somente como possibilidade futura documentada e não
faz parte do escopo implementado.
