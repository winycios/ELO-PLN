from __future__ import annotations

from ..config import Config
from ..dataset.prepare import carregar_split
from ..inference.base import ClassificadorSentimento
from ..io_utils import escrever_json, ler_json
from ..logging_utils import obter_logger
from ..schemas import ExemploRotulado
from .metrics import calcular_metricas, formatar_metricas

logger = obter_logger(__name__)


def avaliar_classificador(
    classificador: ClassificadorSentimento,
    exemplos: list[ExemploRotulado],
) -> tuple[dict, list[dict]]:
    if not exemplos:
        raise ValueError("Conjunto de avaliacao vazio.")

    predicoes = classificador.prever_lote([exemplo.texto for exemplo in exemplos])
    verdadeiros = [exemplo.rotulo.value for exemplo in exemplos]
    preditos = [predicao.sentimento.value for predicao in predicoes]

    erros = [
        {
            "avaliacaoReservaId": exemplo.avaliacao_reserva_id,
            "nota": exemplo.nota,
            "texto": exemplo.texto,
            "esperado": exemplo.rotulo.value,
            "predito": predicao.sentimento.value,
            "confianca": round(predicao.confianca, 4),
            "origemRotulo": exemplo.origem_rotulo,
        }
        for exemplo, predicao in zip(exemplos, predicoes)
        if exemplo.rotulo != predicao.sentimento
    ]
    return calcular_metricas(verdadeiros, preditos), erros


def gerar_relatorio(
    config: Config,
    classificador: ClassificadorSentimento,
    split: str = "teste",
    maximo_erros: int = 25,
) -> dict:
    config.caminhos.preparar()
    exemplos = carregar_split(config, split)
    metricas, erros = avaliar_classificador(classificador, exemplos)

    metadados_dataset = {}
    caminho_meta = config.caminhos.splits / "metadata.json"
    if caminho_meta.exists():
        metadados_dataset = ler_json(caminho_meta)

    nome = f"{config.modelo.backend}-{config.modelo.versao}-{split}"
    resultado = {
        "backend": config.modelo.backend,
        "versaoModelo": classificador.versao,
        "split": split,
        "datasetSintetico": metadados_dataset.get("sintetico", False),
        "versaoDataset": metadados_dataset.get("versaoDataset"),
        "seed": config.dataset.seed,
        "metricas": metricas,
        "totalErros": len(erros),
        "exemplosErro": erros[:maximo_erros],
    }
    escrever_json(config.caminhos.relatorios / f"{nome}.json", resultado)

    markdown = [
        f"# Avaliacao — {config.modelo.backend} ({classificador.versao})",
        "",
        f"- Split: `{split}`",
        f"- Versao do dataset: `{metadados_dataset.get('versaoDataset')}`",
        f"- Seed: `{config.dataset.seed}`",
        f"- Rotulos manuais no teste: {metadados_dataset.get('rotulosManuaisNoTeste', 0)}",
        "",
    ]
    if resultado["datasetSintetico"]:
        markdown += [
            "> **Atencao:** dataset sintetico. As metricas abaixo servem apenas para",
            "> validar o pipeline e nao devem ser reportadas como resultado do TCC.",
            "",
        ]
    markdown.append(formatar_metricas(metricas, titulo="Metricas"))
    markdown += ["", f"## Erros ({len(erros)} no total, {min(len(erros), maximo_erros)} exibidos)", ""]
    for erro in erros[:maximo_erros]:
        markdown.append(
            f"- nota {erro['nota']} | esperado **{erro['esperado']}**, "
            f"predito **{erro['predito']}** ({erro['confianca']:.2f}): {erro['texto']!r}"
        )

    caminho_md = config.caminhos.relatorios / f"{nome}.md"
    caminho_md.write_text("\n".join(markdown) + "\n", encoding="utf-8")
    logger.info("Relatorio gravado em %s (macro-F1 %.4f)", caminho_md, metricas["macroF1"])
    return resultado

