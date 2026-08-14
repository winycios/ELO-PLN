from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import Config, carregar_config
from .logging_utils import configurar_logging, obter_logger

logger = obter_logger("pln.cli")


def _imprimir(dados) -> None:
    print(json.dumps(dados, ensure_ascii=False, indent=2))

def cmd_gerar_sinteticos(args, config: Config) -> int:
    from .dataset.extract import gerar_sinteticas

    total = gerar_sinteticas(config, args.quantidade, args.profissionais, args.proporcao_positivo, args.proporcao_neutro, )
    _imprimir({"avaliacoesGeradas": total, "sintetico": True})
    return 0


def cmd_extrair(args, config: Config) -> int:
    from .dataset.extract import extrair

    _imprimir({"avaliacoesExtraidas": extrair(config, args.limite)})
    return 0


def cmd_preparar(args, config: Config) -> int:
    from .dataset.prepare import preparar

    _imprimir(preparar(config, sintetico=args.sintetico))
    return 0


def cmd_exportar_revisao(args, config: Config) -> int:
    from .dataset.prepare import exportar_amostra_revisao

    caminho = exportar_amostra_revisao(config, args.tamanho)
    _imprimir({"arquivo": str(caminho)})
    return 0


def cmd_aplicar_revisao(args, config: Config) -> int:
    from .dataset.prepare import aplicar_revisao

    _imprimir(aplicar_revisao(config, Path(args.csv) if args.csv else None))
    return 0


def cmd_treinar_baseline(args, config: Config) -> int:
    from .training.baseline import treinar

    metadados = treinar(config)
    _imprimir({"versaoModelo": metadados["versaoModelo"], "metricasValidacao": metadados["metricasValidacao"].get("macroF1")})
    return 0


def cmd_avaliar(args, config: Config) -> int:
    from .evaluation.report import gerar_relatorio
    from .inference.factory import carregar_classificador

    classificador = carregar_classificador(config)
    resultado = gerar_relatorio(config, classificador, split=args.split, confianca_revisao=args.limiar_revisao)
    _imprimir(
        {
            "backend": resultado["backend"],
            "split": resultado["split"],
            "macroF1": resultado["metricas"]["macroF1"],
            "acuracia": resultado["metricas"]["acuracia"],
            "coberturaLexical": resultado["coberturaLexical"],
            "casosRevisao": resultado["casosRevisao"],
            "arquivoRevisao": resultado["arquivoRevisao"],
            "relatorio": str(config.caminhos.relatorios),
        }
    )
    return 0


def cmd_analisar(args, config: Config) -> int:
    from .inference.factory import carregar_classificador
    from .inference.pipeline import AnalisadorComentarios

    analisador = AnalisadorComentarios(carregar_classificador(config), config)
    _imprimir(analisador.analisar_texto(args.texto, args.nota))
    return 0


def cmd_worker(args, config: Config) -> int:
    from .inference.factory import carregar_classificador
    from .inference.pipeline import AnalisadorComentarios
    from .repository import criar_repositorio
    from .worker.run import WorkerPln

    analisador = AnalisadorComentarios(carregar_classificador(config), config)
    with criar_repositorio(config) as repositorio:
        worker = WorkerPln(config, repositorio, analisador)
        _imprimir(worker.executar(continuo=args.continuo))
    return 0


def cmd_reputacao(args, config: Config) -> int:
    from .inference.factory import carregar_classificador
    from .inference.pipeline import AnalisadorComentarios
    from .repository import criar_repositorio
    from .worker.run import WorkerPln

    analisador = AnalisadorComentarios(carregar_classificador(config), config)
    with criar_repositorio(config) as repositorio:
        worker = WorkerPln(config, repositorio, analisador)
        if args.profissional:
            ids = args.profissional
        else:
            ids = sorted(
                {
                    registro["profissional_id"]
                    for registro in _ler_analises_offline(config)
                }
            )
        total = worker.recalcular_reputacoes(ids)
    _imprimir({"profissionaisAtualizados": total})
    return 0


def cmd_exportar_es(args, config: Config) -> int:
    from .io_utils import escrever_jsonl, ler_jsonl
    from .reputation.es_document import documento_reputacao_pln
    from .schemas import ReputacaoProfissional

    origem = config.caminhos.dados_processados / "reputacoes.jsonl"
    if not origem.exists():
        print(f"Nenhuma reputacao agregada em {origem}. Rode `elo-pln worker` antes.", file=sys.stderr)
        return 1

    destino = config.caminhos.dados_processados / "es_reputacao.jsonl"
    total = escrever_jsonl(
        destino,
        (
            {
                "profissionalId": registro["profissional_id"],
                **documento_reputacao_pln(ReputacaoProfissional.from_dict(registro)),
            }
            for registro in ler_jsonl(origem)
        ),
    )
    _imprimir({"documentos": total, "arquivo": str(destino)})
    return 0


def cmd_info(args, config: Config) -> int:
    from .io_utils import ler_json

    diretorio = config.diretorio_modelo
    metadados = {}
    caminho_meta = diretorio / "metadata.json"
    if caminho_meta.exists():
        metadados = ler_json(caminho_meta)

    _imprimir(
        {
            "backend": config.modelo.backend,
            "versaoModelo": config.modelo.versao,
            "diretorioModelo": str(diretorio),
            "artefatoPresente": caminho_meta.exists(),
            "repositorio": config.worker.repositorio,
            "seed": config.dataset.seed,
            "versaoDataset": config.dataset.versao_dataset,
            "treinadoEm": metadados.get("treinadoEm"),
            "macroF1Validacao": metadados.get("metricasValidacao", {}).get("macroF1"),
            "datasetSintetico": metadados.get("datasetSintetico"),
        }
    )
    return 0


def _ler_analises_offline(config: Config):
    from .io_utils import ler_jsonl

    return ler_jsonl(config.caminhos.dados_processados / "analises.jsonl")



def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="elo-pln",description="PLN da plataforma Elo: sentimento, aspectos e reputacao textual.")
    parser.add_argument("--log", default=None, help="Nivel de log (DEBUG, INFO, WARNING).")
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("gerar-sinteticos", help="Cria avaliacoes sinteticas (modo offline).")
    p.add_argument("--quantidade", type=int, default=600)
    p.add_argument("--profissionais", type=int, default=30)
    p.add_argument("--proporcao-positivo", type=float, default=0.50, dest="proporcao_positivo",
                   help="Fatia de avaliacoes positivas. Ajuste para reproduzir a distribuicao real.")
    p.add_argument("--proporcao-neutro", type=float, default=0.25, dest="proporcao_neutro",
                   help="Fatia de neutras; o restante vira negativa.")
    p.set_defaults(func=cmd_gerar_sinteticos)

    p = sub.add_parser("extrair", help="Extrai avaliacoes com comentario do repositorio.")
    p.add_argument("--limite", type=int, default=None)
    p.set_defaults(func=cmd_extrair)

    p = sub.add_parser("preparar", help="Limpa, rotula e divide treino/validacao/teste.")
    p.add_argument("--sintetico", action="store_true", help="Marca o dataset como sintetico.")
    p.set_defaults(func=cmd_preparar)

    p = sub.add_parser("exportar-revisao", help="Exporta amostra do teste em CSV para revisao manual.")
    p.add_argument("--tamanho", type=int, default=200)
    p.set_defaults(func=cmd_exportar_revisao)

    p = sub.add_parser("aplicar-revisao", help="Aplica ao teste os rotulos revisados no CSV.")
    p.add_argument("--csv", default=None)
    p.set_defaults(func=cmd_aplicar_revisao)

    p = sub.add_parser("treinar-baseline", help="Treina TF-IDF + regressao logistica.")
    p.set_defaults(func=cmd_treinar_baseline)

    p = sub.add_parser("avaliar", help="Avalia o backend atual e gera relatorio.")
    p.add_argument("--split", default="teste", choices=["treino", "validacao", "teste"])
    p.add_argument(
        "--limiar-revisao",
        type=float,
        default=None,
        dest="limiar_revisao",
        help="Piso da faixa ALTA de confianca. Abaixo dele o caso vai para o arquivo ""de revisao manual (padrao: ELO_PLN_CONFIANCA_REVISAO ou 0.70).",
    )
    p.set_defaults(func=cmd_avaliar)

    p = sub.add_parser("analisar", help="Analisa um comentario avulso.")
    p.add_argument("--texto", required=True)
    p.add_argument("--nota", type=int, default=None, help="Habilita a regra de inconsistencia.")
    p.set_defaults(func=cmd_analisar)

    p = sub.add_parser("worker", help="Processa avaliacoes pendentes.")
    p.add_argument("--continuo", action="store_true", help="Laco periodico ate Ctrl+C.")
    p.set_defaults(func=cmd_worker)

    p = sub.add_parser("reputacao", help="Recalcula os agregados de reputacao.")
    p.add_argument("--profissional", type=int, nargs="*", default=None)
    p.set_defaults(func=cmd_reputacao)

    p = sub.add_parser("exportar-es", help="Gera os fragmentos reputacaoPln para o Elasticsearch.")
    p.set_defaults(func=cmd_exportar_es)

    p = sub.add_parser("info", help="Mostra a configuracao e o artefato ativo.")
    p.set_defaults(func=cmd_info)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    configurar_logging(args.log)
    config = carregar_config()
    try:
        return args.func(args, config)
    except (FileNotFoundError, ValueError, ImportError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
