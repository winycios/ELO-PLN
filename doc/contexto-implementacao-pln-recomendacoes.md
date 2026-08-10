# Contexto de implementação — PLN e descoberta de profissionais

## 1. Objetivo deste documento

Este documento consolida o contexto funcional e técnico para a implementação futura do módulo de Processamento de Linguagem Natural (PLN) da plataforma Elo.

O sistema principal é considerado concluído. O trabalho futuro deve acrescentar PLN e recomendação sem reescrever os fluxos atuais de usuários, profissionais, serviços, orçamentos, avaliações, busca, Redis e Elasticsearch.

Data de consolidação do contexto: **02 de agosto de 2026**.

## 2. Decisões já fechadas

1. A IA será implementada em Python.
2. Não será treinado um modelo de linguagem do zero.
3. A primeira versão utilizará um classificador supervisionado baseado em TF-IDF e regressão logística. O uso de um modelo neural pré-treinado para português brasileiro, como o BERTimbau, ficará reservado como evolução futura opcional.
4. O escopo acadêmico será reduzido a um classificador de sentimento.
5. O modelo classificará comentários como `POSITIVO`, `NEUTRO` ou `NEGATIVO`.
6. Extração de palavras-chave, inconsistência entre nota e comentário e resumo de reputação não exigirão modelos neurais na primeira versão.
7. O Elasticsearch continuará responsável pela recuperação rápida e ordenação dos profissionais.
8. O MySQL continuará sendo a fonte de verdade; o Elasticsearch será uma projeção de leitura.
9. A aplicação Java continuará sendo a API principal.
10. O modelo será executado localmente, sem dependência obrigatória de APIs externas de IA.
11. A tela terá dois mecanismos claramente separados:
    - `Recomendados para você`: recomendação contextual apoiada por PLN e com selos explicáveis;
    - `Em alta na sua região`: descoberta regional quantitativa, sem personalização e sem PLN.

## 3. Estado atual do sistema

O mecanismo atual de busca já indexa no Elasticsearch:

- identificação e nome do profissional;
- foto de perfil;
- habilitação e disponibilidade;
- média e quantidade de avaliações;
- quantidade de serviços concluídos;
- coordenadas e área de atendimento;
- cidade, estado e bairro;
- serviços, categorias, descrição, tags, preço, execução e experiência.

A busca atual já permite:

- texto com tolerância a erros;
- categoria geral;
- avaliação mínima;
- distância geográfica;
- ordenação por relevância textual, distância e avaliação;
- filtragem de profissionais e serviços ativos.

O mapeamento atual do índice é estrito (`dynamic: strict`). Novos campos de PLN não poderão ser enviados ao índice existente sem alterar o mapeamento. A implementação futura deverá criar uma nova versão do índice, reindexar os documentos e trocar a referência usada pela aplicação.

## 4. Separação dos carrosséis da tela inicial

### 4.1. Recomendados para você

Este será o único carrossel tratado como recomendação.

Seu objetivo é selecionar profissionais compatíveis com o contexto atual do cliente e explicar, de forma curta, por que eles foram apresentados.

#### Elegibilidade inicial

Antes de calcular qualquer escore, o profissional deverá:

- estar habilitado;
- estar disponível;
- possuir serviço ativo;
- atender à categoria solicitada, quando houver categoria;
- atender à localização do cliente, quando houver coordenadas;
- estar dentro do raio de atendimento configurado.

#### Sinais que poderão influenciar a ordenação

- nota média normalizada;
- volume de avaliações;
- sentimento agregado dos comentários;
- quantidade de serviços concluídos;
- taxa de resposta;
- demanda recente;
- distância do cliente;
- compatibilidade com a categoria atual.

Nesta versão reduzida não é obrigatório utilizar histórico completo de buscas, visualizações ou contratações do cliente. A expressão “para você” poderá representar uma recomendação **contextual**, baseada na categoria e localização atuais, além da reputação do profissional.

#### Informações exibidas no card

- dados já existentes do profissional;
- um selo contextual;
- uma justificativa curta;
- opcionalmente, dois ou três pontos fortes extraídos das avaliações.

Exemplo:

```text
Carlos
★ 4,9 (247)

[Requisitado]

Muito elogiado pela pontualidade e qualidade.
```

### 4.2. Em alta na sua região

Este carrossel não será personalizado e não utilizará o modelo de PLN.

Seu objetivo é apresentar profissionais populares em uma região com base apenas em indicadores quantitativos recentes.

#### Critérios iniciais

- profissional habilitado e disponível;
- serviço ativo;
- localização compatível;
- quantidade de solicitações recebidas nos últimos 30 dias;
- quantidade de serviços concluídos nos últimos 30 dias;
- demanda recente pela categoria na região.

O período de 30 dias é um valor inicial e deve permanecer configurável.

#### Significado do selo

O selo `Em alta` significa somente que o profissional ou serviço teve procura recente relevante na região. Ele não afirma que aquele profissional é a melhor escolha para o cliente.

Exemplo:

```text
Patrícia
★ 4,7 (198)
2,5 km

[Em alta]
```

## 5. Escopo reduzido da PLN

### 5.1. Classificador de sentimento da primeira versão

A primeira versão utilizará TF-IDF e regressão logística para produzir um classificador de sentimento com a seguinte entrada e saída:

Entrada:

```json
{
  "comentario": "Chegou no horário e realizou um ótimo trabalho"
}
```

Saída interna:

```json
{
  "sentimento": "POSITIVO",
  "confianca": 0.94,
  "versaoModelo": "sentimento-ptbr-v1"
}
```

A confiança será armazenada para auditoria e avaliação, mas não precisa ser exibida ao usuário.

### 5.2. Rotulagem inicial

Se não existir volume suficiente de comentários rotulados manualmente, as notas poderão gerar rótulos fracos:

- notas 1 e 2: `NEGATIVO`;
- nota 3: `NEUTRO`;
- notas 4 e 5: `POSITIVO`.

Essa associação é uma aproximação e não deverá ser utilizada como única avaliação da qualidade do modelo. Um conjunto de teste separado deverá ser revisado manualmente.

Comentários ausentes ou vazios não serão enviados ao modelo.

### 5.3. Palavras-chave

Na primeira versão, as palavras-chave poderão ser extraídas sem modelo neural, usando uma destas técnicas:

- TF-IDF;
- frequência normalizada;
- lista controlada de aspectos do domínio;
- combinação dessas estratégias.

Exemplos de aspectos úteis:

- pontualidade;
- qualidade;
- rapidez;
- atendimento;
- organização;
- preço;
- atraso;
- comunicação.

Sinônimos deverão ser consolidados em um aspecto canônico quando necessário. Por exemplo, `pontual`, `pontualidade` e `chegou no horário` poderão contribuir para o aspecto `PONTUALIDADE`.

### 5.4. Inconsistência entre nota e comentário

A inconsistência será uma regra derivada, e não uma acusação de fraude.

Regra inicial:

```text
nota >= 4 e sentimento NEGATIVO → possível inconsistência
nota <= 2 e sentimento POSITIVO → possível inconsistência
```

O indicador deverá ser usado apenas como sinal interno para reduzir o peso da avaliação na reputação textual. A interface não deverá chamar uma avaliação de falsa ou suspeita.

### 5.5. Resumo de reputação

Não será utilizado um modelo generativo na primeira versão. O resumo será montado com templates e aspectos agregados.

Exemplos:

```text
Profissional elogiado principalmente pela pontualidade e qualidade do serviço.
```

```text
Clientes destacam a qualidade do trabalho, com relatos pontuais de demora no atendimento.
```

O resumo só deverá mencionar um aspecto quando houver evidência mínima definida durante a calibração. Uma única avaliação não deverá determinar sozinha a reputação textual exibida.

## 6. Arquitetura de processamento proposta

Fluxo principal:

```text
Avaliação salva no MySQL
        ↓
Worker consulta avaliações ainda não processadas
        ↓
Worker Python local
        ↓
Classificação de sentimento
Extração de aspectos
Regra de inconsistência
        ↓
Resultado persistido no MySQL
        ↓
Agregação da reputação do profissional
        ↓
Registro na `search_outbox`
        ↓
Java consome a solicitação de reindexação
        ↓
Documento atualizado no Elasticsearch
        ↓
API Java consulta e monta os carrosséis
```

### 6.1. Responsabilidade do Python

- preparar datasets;
- treinar e avaliar os modelos;
- versionar o artefato treinado;
- executar inferência local;
- extrair aspectos simples;
- produzir resultados reproduzíveis.

### 6.2. Responsabilidade do Java

- continuar sendo a API pública;
- persistir avaliações e eventos;
- consultar resultados agregados;
- consumir a `search_outbox` e executar a reindexação;
- consultar Elasticsearch;
- aplicar regras de negócio dos selos;
- montar o contrato enviado ao aplicativo.

### 6.3. FastAPI

FastAPI não é obrigatório na primeira versão. Para reduzir o escopo, o Python poderá funcionar como worker periódico ou consumidor de uma fila/outbox.

Uma API Python só deverá ser adicionada se houver necessidade real de inferência síncrona. O processamento assíncrono é preferível, pois a avaliação pode ser salva imediatamente e analisada logo depois.

## 7. Persistência integrada ao banco real

O schema principal é `database_elo`. As tabelas derivadas seguem a convenção de nomes existente
e possuem chaves estrangeiras para `avaliacao_reserva` e `profissional`.

### 7.1. Resultado por avaliação

Tabela: `avaliacao_analise_pln`.

Campos mínimos:

- `id_avaliacao_analise_pln`;
- `fk_id_avaliacao_reserva`, único;
- `fk_id_profissional`;
- `tp_sentimento`;
- `nr_confianca`;
- `st_possui_inconsistencia`;
- `js_aspectos`;
- `cd_versao_modelo`;
- `dt_processamento`.

Palavras-chave poderão ser armazenadas em JSON ou em uma tabela filha caso seja necessário consultá-las individualmente.

### 7.2. Agregado por profissional

Tabela: `profissional_reputacao_pln`.

Campos mínimos:

- `fk_id_profissional`, único;
- quantidade de comentários processados;
- quantidade e percentual por sentimento;
- sentimento médio normalizado;
- quantidade de inconsistências;
- aspectos positivos principais;
- aspectos negativos principais;
- resumo de reputação;
- versão do modelo;
- data da última atualização.

O agregado evita analisar todas as avaliações durante cada busca.

### 7.3. Reindexação

Não será criada uma segunda fila específica para PLN. Quando a reputação mudar, o worker Python
inserirá o profissional na tabela `search_outbox` já existente, desde que ainda não exista uma
solicitação pendente. A aplicação Java continuará responsável por consumir a outbox e atualizar
o documento no Elasticsearch.

## 8. Evolução do documento do Elasticsearch

O documento do profissional poderá receber uma estrutura semelhante a:

```json
{
  "reputacaoPln": {
    "comentariosProcessados": 42,
    "percentualPositivo": 88.1,
    "percentualNeutro": 7.1,
    "percentualNegativo": 4.8,
    "sentimentoMedio": 0.83,
    "taxaInconsistencia": 2.4,
    "pontosFortes": ["PONTUALIDADE", "QUALIDADE", "ATENDIMENTO"],
    "resumo": "Profissional elogiado pela pontualidade e qualidade.",
    "versaoModelo": "sentimento-ptbr-v1"
  },
  "metricasRecomendacao": {
    "taxaResposta": 0.96,
    "demandaUltimos30Dias": 18,
    "concluidosUltimos30Dias": 12
  }
}
```

Como o índice atual possui mapeamento estrito, recomenda-se:

1. criar uma nova versão do índice;
2. adicionar os novos mappings;
3. reindexar todos os profissionais;
4. validar contagem e documentos;
5. trocar a leitura para a nova versão;
6. manter possibilidade de rollback.

O uso de alias de índice deverá ser considerado para evitar acoplar a aplicação a cada número de versão.

## 9. Escore inicial de recomendação

Os pesos não são definitivos. Eles deverão ser tratados como calibração inicial e documentados nos resultados do TCC.

Uma fórmula reduzida possível é:

```text
Score_Contextual =
    0,45 × reputacao
  + 0,25 × proximidade
  + 0,15 × taxa_resposta
  + 0,15 × demanda_recente
```

Em que `reputacao` poderá combinar:

```text
Reputacao =
    0,50 × nota_media_normalizada
  + 0,20 × volume_avaliacoes_normalizado
  + 0,30 × sentimento_medio
  - penalizacao_inconsistencias
```

Todos os componentes deverão ser normalizados entre 0 e 1 antes da soma.

A categoria funciona inicialmente como critério de elegibilidade, e não como peso. Profissionais incompatíveis com a categoria não entram no conjunto candidato.

Se os dados de PLN ainda não estiverem disponíveis, o sistema deverá aplicar fallback para os sinais quantitativos existentes.

## 10. Selos e justificativas

O carrossel `Recomendados para você` poderá usar os seguintes selos:

### Melhor escolha

Condição inicial: maior escore contextual entre os candidatos elegíveis e reputação mínima configurada.

Justificativa possível:

```text
Boa combinação de reputação, proximidade e experiência.
```

### Requisitado

Condição inicial: demanda recente acima de um percentil regional definido.

Justificativa possível:

```text
Muito procurado recentemente para este tipo de serviço.
```

### Perto e popular

Condição inicial: baixa distância e demanda regional alta.

Justificativa possível:

```text
Bem avaliado e bastante procurado perto de você.
```

### Talento da região

Condição inicial: menor volume histórico, mas boa reputação textual, proximidade e compatibilidade.

Justificativa possível:

```text
Profissional da região com avaliações positivas recentes.
```

### Regra de prioridade

Um profissional deverá receber no máximo um selo por card. A ordem de prioridade e os limiares deverão ser definidos após observar a distribuição real dos dados.

O selo `Em alta` fica reservado ao segundo carrossel e não participa do motor de recomendação.

## 11. Contrato de resposta sugerido

O contrato final poderá ser entregue por um endpoint específico de descoberta da tela inicial. O caminho definitivo será decidido durante a implementação.

Exemplo:

```json
{
  "recomendadosParaVoce": [
    {
      "profissionalId": 15,
      "nome": "Carlos Oliveira",
      "fotoPerfil": "https://...",
      "categoria": "Eletricista",
      "avaliacao": 4.9,
      "quantidadeAvaliacoes": 247,
      "precoInicial": 80.0,
      "distanciaKm": 2.1,
      "selo": "REQUISITADO",
      "justificativa": "Muito procurado recentemente e elogiado pela pontualidade.",
      "pontosFortes": ["Pontualidade", "Qualidade"]
    }
  ],
  "emAltaNaRegiao": [
    {
      "profissionalId": 27,
      "nome": "Patrícia Lima",
      "fotoPerfil": "https://...",
      "categoria": "Diarista",
      "avaliacao": 4.7,
      "quantidadeAvaliacoes": 198,
      "distanciaKm": 2.5,
      "selo": "EM_ALTA"
    }
  ]
}
```

O segundo grupo não deverá conter justificativa personalizada nem campos derivados da PLN.

## 12. Treinamento e avaliação acadêmica

### 12.1. Classificador adotado

A primeira versão utilizará um classificador supervisionado simples e executável localmente:

- TF-IDF;
- regressão logística ou classificador linear equivalente.

Essa abordagem atende ao objetivo de demonstrar a classificação automática de sentimentos sem adicionar a complexidade operacional de um modelo neural. O BERTimbau poderá ser avaliado futuramente caso surjam volume de dados, infraestrutura e necessidade de maior compreensão contextual.

### 12.2. Separação dos dados

Os dados deverão ser divididos em treino, validação e teste. O conjunto de teste deverá permanecer congelado durante os ajustes.

Uma amostra do teste deverá ser revisada manualmente para reduzir o impacto dos rótulos fracos derivados das notas.

### 12.3. Métricas mínimas

- macro-F1;
- precisão por classe;
- recall por classe;
- F1 por classe;
- matriz de confusão;
- distribuição das classes.

Acurácia isolada não será suficiente, especialmente se houver maioria de avaliações positivas.

### 12.4. Reprodutibilidade

Deverão ser registrados:

- versão do dataset;
- regras de limpeza;
- seed;
- técnica e algoritmo utilizados;
- hiperparâmetros;
- métricas;
- versão do artefato final;
- dependências Python.

## 13. Organização sugerida do projeto Python

```text
pln/
├── README.md
├── pyproject.toml
├── data/
│   ├── raw/
│   ├── processed/
│   └── splits/
├── src/
│   ├── dataset/
│   ├── training/
│   ├── evaluation/
│   ├── inference/
│   ├── keywords/
│   └── worker/
├── models/
└── tests/
```

Dados reais, artefatos grandes e credenciais não deverão ser versionados diretamente no Git.

## 14. Fases de implementação

### Fase 1 — Preparação

- extrair avaliações com comentário;
- anonimizar dados desnecessários;
- definir esquema das classes;
- preparar treino, validação e teste;
- revisar manualmente o teste.

### Fase 2 — Classificador de sentimento

- implementar TF-IDF e classificador linear;
- registrar métricas;
- analisar erros por classe.

### Fase 3 — Consolidação do modelo

- validar o classificador com dados revisados;
- registrar hiperparâmetros e dependências;
- selecionar e versionar o artefato final.

### Fase 4 — Processamento local

- implementar inferência em lote;
- extrair palavras-chave/aspectos;
- aplicar regra de inconsistência;
- criar resumo por template;
- persistir resultados no MySQL.

### Fase 5 — Integração Java e Elasticsearch

- publicar a reindexação na `search_outbox` após atualizar a reputação;
- consumir a `search_outbox` no Java;
- agregar reputação por profissional;
- criar nova versão do índice;
- reindexar profissionais;
- implementar fallback sem PLN.

### Fase 6 — Carrosséis

- implementar recomendação contextual e selos no primeiro carrossel;
- implementar popularidade regional no segundo;
- impedir uso de PLN no segundo grupo;
- validar textos e explicações com o aplicativo.

### Fase 7 — Validação do TCC

- executar avaliação offline do classificador;
- registrar exemplos qualitativos;
- validar clareza dos selos e justificativas;
- documentar limitações e ameaças à validade.

### Evolução futura — Modelo neural

Fora do escopo inicial do TCC, o classificador poderá evoluir para um modelo pré-treinado em português, tendo o BERTimbau como candidato. Essa evolução poderá incluir:

- ampliação e revisão manual do conjunto de comentários reais;
- fine-tuning do BERTimbau para as classes `POSITIVO`, `NEUTRO` e `NEGATIVO`;
- avaliação do custo de treinamento e inferência no hardware disponível;
- versionamento do novo artefato sem alterar o contrato de saída;
- ativação do novo backend por configuração, preservando o classificador atual como alternativa operacional.

## 15. Critérios de aceite

### PLN

- o modelo roda localmente;
- recebe comentário e devolve classe, confiança e versão;
- possui artefato treinado e versionado;
- possui teste congelado e métricas reproduzíveis;
- não depende da nota durante a inferência;
- falhas no worker não impedem o salvamento da avaliação.

### Recomendados para você

- contém apenas profissionais elegíveis;
- usa reputação textual quando disponível;
- funciona com fallback quantitativo;
- cada card possui no máximo um selo;
- selo e justificativa são coerentes com os sinais utilizados;
- não expõe probabilidade bruta ou indicador de inconsistência.

### Em alta na sua região

- não utiliza histórico pessoal do cliente;
- não utiliza sentimento ou palavras-chave;
- usa somente localização e métricas quantitativas recentes;
- apresenta o selo `Em alta` com significado regional;
- continua funcionando mesmo que o módulo Python esteja indisponível.

### Dados e operação

- MySQL permanece como fonte de verdade;
- documentos do Elasticsearch podem ser reconstruídos;
- resultados registram versão do modelo;
- reindexação possui estratégia de migração e rollback;
- logs não expõem comentários ou dados pessoais desnecessários.

## 16. Itens deliberadamente fora do escopo inicial

- treinamento de um modelo de linguagem do zero;
- modelo generativo para escrever resumos livres;
- chat com IA;
- detecção automática de fraude;
- recomendação baseada em todo o histórico comportamental do cliente;
- aprendizado online em tempo real;
- reordenação neural em cada requisição;
- múltiplos modelos neurais para sentimento, palavras-chave e resumo;
- exposição pública do escore interno completo.

## 17. Pontos que deverão ser confirmados antes de implementar

1. Quantidade de avaliações com comentários disponível para treino.
2. Distribuição das notas e tamanho de cada classe.
3. Hardware local disponível para treinamento e inferência do classificador inicial.
4. Período final de popularidade regional, inicialmente 30 dias.
5. Fonte da localização usada na tela inicial.
6. Quantidade de profissionais em cada carrossel.
7. Limiares e prioridade dos selos.
8. Forma de persistência das palavras-chave.
9. Nome e versionamento do novo índice Elasticsearch.

## 18. Resultado esperado

Ao final, a plataforma deverá apresentar dois blocos independentes:

```text
Recomendados para você
→ contexto atual + reputação quantitativa + PLN
→ selo e justificativa explicável

Em alta na sua região
→ popularidade regional recente
→ sem personalização e sem PLN
```

O valor acadêmico estará na implementação da classificação automática de sentimentos e na utilização desse resultado como um sinal explicável de reputação dentro de uma recomendação contextual, sem ampliar desnecessariamente o escopo do TCC. A adoção futura de um modelo neural poderá aprofundar a capacidade de compreensão contextual sem exigir alterações no contrato já definido.
