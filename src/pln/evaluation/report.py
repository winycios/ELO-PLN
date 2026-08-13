from __future__ import annotations

from ..config import Config
from ..dataset.prepare import carregar_split
from ..inference.base import ClassificadorSentimento
from ..io_utils import escrever_json, escrever_jsonl, ler_json
from ..logging_utils import obter_logger
from ..schemas import ExemploRotulado
from .metrics import calcular_metricas, formatar_metricas

logger = obter_logger(__name__)

FAIXA_ALTA = "ALTA"
FAIXA_MEDIA = "MEDIA"
FAIXA_BAIXA = "BAIXA"

FAIXAS_REVISAO = (FAIXA_MEDIA, FAIXA_BAIXA)

def classificar_faixa(confianca: float, confianca_minima: float, confianca_revisao: float) -> str:
    if confianca >= confianca_revisao:
        return FAIXA_ALTA
    if confianca >= confianca_minima:
        return FAIXA_MEDIA
    return FAIXA_BAIXA


def avaliar_classificador(classificador: ClassificadorSentimento, exemplos: list[ExemploRotulado],
                          confianca_minima: float = 0.55, confianca_revisao: float = 0.70) -> tuple[dict, list[dict]]:
    if not exemplos:
        raise ValueError("Conjunto de avaliacao vazio.")

    predicoes = classificador.prever_lote([exemplo.texto for exemplo in exemplos])
    verdadeiros = [exemplo.rotulo.value for exemplo in exemplos]
    preditos = [predicao.sentimento.value for predicao in predicoes]

    casos = [
        {
            "avaliacaoReservaId": exemplo.avaliacao_reserva_id,
            "profissionalId": exemplo.profissional_id,
            "nota": exemplo.nota,
            "texto": exemplo.texto,
            "esperado": exemplo.rotulo.value,
            "predito": predicao.sentimento.value,
            "confianca": round(predicao.confianca, 4),
            "faixaConfianca": classificar_faixa(predicao.confianca, confianca_minima, confianca_revisao),
            "acertou": exemplo.rotulo is predicao.sentimento,
            "probabilidades": {
                classe: round(valor, 4) for classe, valor in predicao.probabilidades.items()
            },
            "origemRotulo": exemplo.origem_rotulo,
            "versaoModelo": predicao.versao_modelo,
        }
        for exemplo, predicao in zip(exemplos, predicoes)
    ]
    return calcular_metricas(verdadeiros, preditos), casos

def resumir_confianca(casos: list[dict]) -> dict:
    resumo: dict[str, dict] = {}
    for faixa in (FAIXA_ALTA, FAIXA_MEDIA, FAIXA_BAIXA):
        da_faixa = [caso for caso in casos if caso["faixaConfianca"] == faixa]
        acertos = sum(1 for caso in da_faixa if caso["acertou"])
        resumo[faixa] = {
            "casos": len(da_faixa),
            "acertos": acertos,
            "erros": len(da_faixa) - acertos,
            "acuracia": round(acertos / len(da_faixa), 4) if da_faixa else None,
            "percentualDoSplit": round(100.0 * len(da_faixa) / len(casos), 2) if casos else 0.0,
        }
    return resumo


def gerar_relatorio(config: Config, classificador: ClassificadorSentimento, split: str = "teste",
                    maximo_erros: int = 25, confianca_revisao: float | None = None) -> dict:
    config.caminhos.preparar()
    exemplos = carregar_split(config, split)

    confianca_minima = config.modelo.confianca_minima
    confianca_revisao = (config.modelo.confianca_revisao if confianca_revisao is None else confianca_revisao)
    if not confianca_minima <= confianca_revisao:
        raise ValueError("Limiar de revisao deve ser maior ou igual a confianca minima "f"({confianca_revisao} < {confianca_minima}); a faixa MEDIA ficaria vazia.")

    metricas, casos = avaliar_classificador(classificador, exemplos, confianca_minima, confianca_revisao)
    erros = [caso for caso in casos if not caso["acertou"]]
    revisao = [caso for caso in casos if caso["faixaConfianca"] in FAIXAS_REVISAO]
    resumo_confianca = resumir_confianca(casos)

    metadados_dataset = {}
    caminho_meta = config.caminhos.splits / "metadata.json"
    if caminho_meta.exists():
        metadados_dataset = ler_json(caminho_meta)

    nome = f"{config.modelo.backend}-{config.modelo.versao}-{split}"

    caminho_revisao = config.caminhos.relatorios / f"revisao-confianca-{nome}.jsonl"
    escrever_jsonl(caminho_revisao, revisao)

    resultado = {
        "backend": config.modelo.backend,
        "versaoModelo": classificador.versao,
        "split": split,
        "datasetSintetico": metadados_dataset.get("sintetico", False),
        "versaoDataset": metadados_dataset.get("versaoDataset"),
        "seed": config.dataset.seed,
        "metricas": metricas,
        "limiares": {
            "confiancaMinima": confianca_minima,
            "confiancaRevisao": confianca_revisao,
        },
        "resumoConfianca": resumo_confianca,
        "casosRevisao": len(revisao),
        "arquivoRevisao": str(caminho_revisao),
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
    markdown += _secao_confianca(
        resumo_confianca,
        confianca_minima,
        confianca_revisao,
        len(revisao),
        caminho_revisao.name,
    )
    markdown += ["", f"## Erros ({len(erros)} no total, {min(len(erros), maximo_erros)} exibidos)", ""]
    for erro in erros[:maximo_erros]:
        markdown.append(
            f"- nota {erro['nota']} | esperado **{erro['esperado']}**, "
            f"predito **{erro['predito']}** ({erro['confianca']:.2f}, "
            f"faixa {erro['faixaConfianca']}): {erro['texto']!r}"
        )

    caminho_md = config.caminhos.relatorios / f"{nome}.md"
    caminho_md.write_text("\n".join(markdown) + "\n", encoding="utf-8")
    logger.info("Relatorio gravado em %s (macro-F1 %.4f)", caminho_md, metricas["macroF1"])
    logger.info("Fila de revisao: %d casos com confianca abaixo de %.2f em %s",len(revisao),confianca_revisao,caminho_revisao,)
    return resultado


def _secao_confianca(resumo: dict,confianca_minima: float,confianca_revisao: float,casos_revisao: int,arquivo_revisao: str,) -> list[str]:
    criterios = {
        FAIXA_ALTA: f"`confianca >= {confianca_revisao:.2f}`",
        FAIXA_MEDIA: f"`{confianca_minima:.2f} <= confianca < {confianca_revisao:.2f}`",
        FAIXA_BAIXA: f"`confianca < {confianca_minima:.2f}`",
    }
    linhas = [
        "",
        "## Confianca",
        "",
        "| Faixa | Criterio | Casos | % do split | Erros | Acuracia |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for faixa, valores in resumo.items():
        acuracia = "—" if valores["acuracia"] is None else f"{valores['acuracia']:.4f}"
        linhas.append(
            f"| {faixa} | {criterios[faixa]} | {valores['casos']} "
            f"| {valores['percentualDoSplit']:.2f}% | {valores['erros']} | {acuracia} |"
        )
    linhas += [
        "",
        f"Casos de confianca mediana ou baixa separados para revisao manual: "
        f"**{casos_revisao}** — `reports/{arquivo_revisao}`.",
    ]
    return linhas
