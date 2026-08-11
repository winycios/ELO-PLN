from __future__ import annotations

import csv
from pathlib import Path

from ..config import Config
from ..io_utils import escrever_json, escrever_jsonl, ler_json, ler_jsonl
from ..logging_utils import obter_logger
from ..schemas import Avaliacao, ExemploRotulado, Sentimento
from . import clean, split as split_mod, weak_labels

logger = obter_logger(__name__)

ARQUIVO_BRUTO = "avaliacoes.jsonl"
ARQUIVO_AMOSTRA_REVISAO = "teste_amostra_revisao.csv"


def _caminho_split(config: Config, nome: str) -> Path:
    return config.caminhos.splits / f"{nome}.jsonl"


def carregar_avaliacoes(config: Config) -> list[Avaliacao]:
    caminho = config.caminhos.dados_brutos / ARQUIVO_BRUTO
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo bruto nao encontrado: {caminho}. "
            "Rode `elo-pln extrair` (MySQL) ou `elo-pln gerar-sinteticos` (offline)."
        )
    return [Avaliacao.from_dict(registro) for registro in ler_jsonl(caminho)]


def construir_exemplos(
    avaliacoes: list[Avaliacao],
    config: Config,
    usar_rotulos_texto: bool = False,
) -> list[ExemploRotulado]:
    exemplos: list[ExemploRotulado] = []
    descartados = 0

    for avaliacao in avaliacoes:
        texto = clean.limpar_comentario(avaliacao.comentario)
        if not clean.comentario_utilizavel(texto, config.dataset.tamanho_minimo_comentario):
            descartados += 1
            continue
        rotulo_texto = avaliacao.rotulo_sentimento if usar_rotulos_texto else None
        exemplos.append(
            ExemploRotulado(
                avaliacao_reserva_id=avaliacao.avaliacao_reserva_id,
                profissional_id=avaliacao.profissional_id,
                texto=texto,
                rotulo=rotulo_texto or weak_labels.rotulo_fraco(avaliacao.nota),
                nota=avaliacao.nota,
                origem_rotulo=("sintetico" if rotulo_texto else "fraco"),
            )
        )

    logger.info(
        "Exemplos construidos: %d utilizaveis, %d descartados (sem comentario ou curtos demais)",
        len(exemplos),
        descartados,
    )
    return exemplos


def preparar(config: Config, sintetico: bool = False) -> dict:
    config.caminhos.preparar()

    avaliacoes = carregar_avaliacoes(config)
    exemplos = construir_exemplos(avaliacoes, config, usar_rotulos_texto=sintetico)

    particoes = split_mod.dividir(
        exemplos,
        seed=config.dataset.seed,
        proporcao_treino=config.dataset.proporcao_treino,
        proporcao_validacao=config.dataset.proporcao_validacao,
    )

    for nome, itens in (
        ("treino", particoes.treino),
        ("validacao", particoes.validacao),
        ("teste", particoes.teste),
    ):
        escrever_jsonl(_caminho_split(config, nome), (item.to_dict() for item in itens))

    metadados = {
        "versaoDataset": config.dataset.versao_dataset,
        "sintetico": sintetico,
        "seed": config.dataset.seed,
        "versaoLimpeza": clean.VERSAO_LIMPEZA,
        "regrasLimpeza": clean.REGRAS_LIMPEZA,
        "mapaRotuloFraco": {str(k): v.value for k, v in weak_labels.MAPA_NOTA_ROTULO.items()},
        "rotulosSinteticosPeloTexto": sum(
            1 for exemplo in exemplos if exemplo.origem_rotulo == "sintetico"
        ),
        "totalAvaliacoesBrutas": len(avaliacoes),
        "totalExemplos": len(exemplos),
        "tamanhoParticoes": particoes.resumo(),
        "distribuicaoGeral": weak_labels.distribuicao(exemplos),
        "distribuicaoTreino": weak_labels.distribuicao(particoes.treino),
        "distribuicaoValidacao": weak_labels.distribuicao(particoes.validacao),
        "distribuicaoTeste": weak_labels.distribuicao(particoes.teste),
        "rotulosManuaisNoTeste": sum(
            1 for item in particoes.teste if item.origem_rotulo == "manual"
        ),
    }
    escrever_json(config.caminhos.splits / "metadata.json", metadados)
    logger.info("Particoes: %s", metadados["tamanhoParticoes"])
    return metadados


def carregar_split(config: Config, nome: str) -> list[ExemploRotulado]:
    caminho = _caminho_split(config, nome)
    if not caminho.exists():
        raise FileNotFoundError(f"Split '{nome}' nao encontrado em {caminho}. Rode `elo-pln preparar`.")
    return [ExemploRotulado.from_dict(registro) for registro in ler_jsonl(caminho)]


# --------------------------------------------------------------------------- #
# Revisao manual do conjunto de teste
# --------------------------------------------------------------------------- #


def exportar_amostra_revisao(config: Config, tamanho: int = 200) -> Path:
    teste = carregar_split(config, "teste")
    amostra = teste[:tamanho]
    caminho = config.caminhos.splits / ARQUIVO_AMOSTRA_REVISAO
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["avaliacao_reserva_id", "nota", "texto", "rotulo_fraco", "rotulo_revisado"])
        for exemplo in amostra:
            escritor.writerow(
                [
                    exemplo.avaliacao_reserva_id,
                    exemplo.nota,
                    exemplo.texto,
                    exemplo.rotulo.value,
                    exemplo.rotulo.value,
                ]
            )
    logger.info("Amostra para revisao manual: %d linhas em %s", len(amostra), caminho)
    return caminho


def aplicar_revisao(config: Config, caminho_csv: Path | None = None) -> dict:
    caminho_csv = caminho_csv or (config.caminhos.splits / ARQUIVO_AMOSTRA_REVISAO)
    if not caminho_csv.exists():
        raise FileNotFoundError(f"CSV de revisao nao encontrado: {caminho_csv}")

    revisados: dict[int, Sentimento] = {}
    with caminho_csv.open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            revisados[int(linha["avaliacao_reserva_id"])] = Sentimento(
                linha["rotulo_revisado"].strip().upper()
            )

    teste = carregar_split(config, "teste")
    alterados = 0
    for exemplo in teste:
        novo = revisados.get(exemplo.avaliacao_reserva_id)
        if novo is None:
            continue
        if novo != exemplo.rotulo:
            alterados += 1
        weak_labels.marcar_revisao_manual(exemplo, novo)

    escrever_jsonl(_caminho_split(config, "teste"), (item.to_dict() for item in teste))

    caminho_meta = config.caminhos.splits / "metadata.json"
    if caminho_meta.exists():
        metadados = ler_json(caminho_meta)
        metadados["rotulosManuaisNoTeste"] = len(revisados)
        metadados["divergenciasRotuloFraco"] = alterados
        metadados["distribuicaoTeste"] = weak_labels.distribuicao(teste)
        escrever_json(caminho_meta, metadados)

    logger.info(
        "Revisao aplicada: %d rotulos manuais, %d divergiam do rotulo fraco",
        len(revisados),
        alterados,
    )
    return {"revisados": len(revisados), "divergencias": alterados}
