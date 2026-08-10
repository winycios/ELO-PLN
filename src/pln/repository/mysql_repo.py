from __future__ import annotations

import json
import os
from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime, timezone

from .base import RepositorioPln
from ..config import Config
from ..logging_utils import obter_logger
from ..schemas import AnaliseComentario, Avaliacao, ReputacaoProfissional

logger = obter_logger(__name__)


def _datetime_mysql(valor: str | datetime) -> datetime:
    if isinstance(valor, datetime):
        resultado = valor
    else:
        resultado = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if resultado.tzinfo is not None:
        resultado = resultado.astimezone(timezone.utc).replace(tzinfo=None)
    return resultado


# A condicao entre o usuario avaliado e o profissional do servico exclui avaliacoes
# feitas pelo profissional sobre o cliente. A consulta ainda pode ser sobrescrita em
# implantacoes com outro schema, mantendo os mesmos aliases de saida.
SQL_AVALIACOES = os.environ.get(
    "ELO_PLN_SQL_AVALIACOES",
    """
    SELECT a.id_avaliacao_reserva AS avaliacao_reserva_id,
           p.usuario_id           AS profissional_id,
           a.qt_nota              AS nota,
           a.ds_comentario        AS comentario,
           a.dt_criacao           AS data_avaliacao
    FROM avaliacao_reserva a
             JOIN orcamento o
                  ON o.id_orcamento = a.fk_id_reserva
             JOIN servico s
                  ON s.id_servico = o.fk_id_servico
             JOIN profissional p
                  ON p.usuario_id = s.fk_id_profissional_usuario
    WHERE a.fk_id_usuario_avaliado = p.usuario_id
      AND a.ds_comentario IS NOT NULL
      AND TRIM(a.ds_comentario) <> ''
    """,
)

SQL_PENDENTES = """
                SELECT base.*
                FROM ({origem}) base
                         LEFT JOIN avaliacao_analise_pln p
                                   ON p.fk_id_avaliacao_reserva = base.avaliacao_reserva_id
                                       AND p.cd_versao_modelo = %s
                WHERE p.id_avaliacao_analise_pln IS NULL
                ORDER BY base.avaliacao_reserva_id
                    LIMIT %s \
                """

SQL_UPSERT_ANALISE = """
                     INSERT INTO avaliacao_analise_pln
                     (fk_id_avaliacao_reserva, fk_id_profissional, tp_sentimento, nr_confianca,
                      st_possui_inconsistencia, js_aspectos, cd_versao_modelo, dt_processamento)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
                     UPDATE
                         fk_id_profissional =
                     VALUES (fk_id_profissional), tp_sentimento =
                     VALUES (tp_sentimento), nr_confianca =
                     VALUES (nr_confianca), st_possui_inconsistencia =
                     VALUES (st_possui_inconsistencia), js_aspectos =
                     VALUES (js_aspectos), cd_versao_modelo =
                     VALUES (cd_versao_modelo), dt_processamento =
                     VALUES (dt_processamento) \
                     """

SQL_UPSERT_REPUTACAO = """
                       INSERT INTO profissional_reputacao_pln
                       (fk_id_profissional, qt_comentarios_processados,
                        qt_positivo, qt_neutro, qt_negativo,
                        nr_percentual_positivo, nr_percentual_neutro, nr_percentual_negativo,
                        nr_sentimento_medio, qt_inconsistencias, nr_taxa_inconsistencia,
                        js_pontos_fortes, js_pontos_fracos, ds_resumo, cd_versao_modelo, dt_atualizacao)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY
                       UPDATE
                           qt_comentarios_processados =
                       VALUES (qt_comentarios_processados), qt_positivo =
                       VALUES (qt_positivo), qt_neutro =
                       VALUES (qt_neutro), qt_negativo =
                       VALUES (qt_negativo), nr_percentual_positivo =
                       VALUES (nr_percentual_positivo), nr_percentual_neutro =
                       VALUES (nr_percentual_neutro), nr_percentual_negativo =
                       VALUES (nr_percentual_negativo), nr_sentimento_medio =
                       VALUES (nr_sentimento_medio), qt_inconsistencias =
                       VALUES (qt_inconsistencias), nr_taxa_inconsistencia =
                       VALUES (nr_taxa_inconsistencia), js_pontos_fortes =
                       VALUES (js_pontos_fortes), js_pontos_fracos =
                       VALUES (js_pontos_fracos), ds_resumo =
                       VALUES (ds_resumo), cd_versao_modelo =
                       VALUES (cd_versao_modelo), dt_atualizacao =
                       VALUES (dt_atualizacao) \
                       """

SQL_MARCAR_REINDEXACAO = """
                         INSERT INTO search_outbox
                             (fk_profissional_id, dt_criacao, dt_processamento, nr_tentativas)
                         SELECT %s,
                                NOW(3),
                                NULL,
                                0 WHERE NOT EXISTS (
           SELECT 1
             FROM search_outbox pendente
            WHERE pendente.fk_profissional_id = %s
                             AND pendente.dt_processamento IS NULL
                             ) \
                         """

SQL_ANALISES_POR_PROFISSIONAL = """
                                SELECT fk_id_avaliacao_reserva  AS avaliacao_reserva_id,
                                       fk_id_profissional       AS profissional_id,
                                       tp_sentimento            AS sentimento,
                                       nr_confianca             AS confianca,
                                       st_possui_inconsistencia AS possui_inconsistencia,
                                       js_aspectos              AS aspectos,
                                       cd_versao_modelo         AS versao_modelo,
                                       dt_processamento         AS data_processamento
                                FROM avaliacao_analise_pln
                                WHERE fk_id_profissional IN ({placeholders}) \
                                """


class MySQLRepositorio(RepositorioPln):
    def __init__(self, config: Config) -> None:
        try:
            import pymysql
            from pymysql.cursors import DictCursor
        except ImportError as erro:
            raise ImportError(
                "PyMySQL nao instalado. Rode: pip install -e '.[mysql]'"
            ) from erro

        self.config = config
        self.conexao = pymysql.connect(
            host=config.mysql.host,
            port=config.mysql.porta,
            user=config.mysql.usuario,
            password=config.mysql.senha,
            database=config.mysql.banco,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=False,
        )
        logger.info("Conectado ao MySQL %s:%s/%s", config.mysql.host, config.mysql.porta, config.mysql.banco)

    # ---------------------------------------------------------------- leitura

    def buscar_avaliacoes_com_comentario(self, limite: int | None = None) -> list[Avaliacao]:
        sql = SQL_AVALIACOES + (f" LIMIT {int(limite)}" if limite else "")
        with self.conexao.cursor() as cursor:
            cursor.execute(sql)
            return [self._linha_para_avaliacao(linha) for linha in cursor.fetchall()]

    def buscar_avaliacoes_pendentes(self, versao_modelo: str, limite: int) -> list[Avaliacao]:
        with self.conexao.cursor() as cursor:
            cursor.execute(SQL_PENDENTES.format(origem=SQL_AVALIACOES), (versao_modelo, limite))
            return [self._linha_para_avaliacao(linha) for linha in cursor.fetchall()]

    def buscar_analises_por_profissional(
            self, profissional_ids: Sequence[int]
    ) -> dict[int, list[AnaliseComentario]]:
        if not profissional_ids:
            return {}
        placeholders = ", ".join(["%s"] * len(profissional_ids))
        agrupado: dict[int, list[AnaliseComentario]] = defaultdict(list)
        with self.conexao.cursor() as cursor:
            cursor.execute(
                SQL_ANALISES_POR_PROFISSIONAL.format(placeholders=placeholders),
                tuple(profissional_ids),
            )
            for linha in cursor.fetchall():
                analise = AnaliseComentario.from_dict(
                    {
                        **linha,
                        "possui_inconsistencia": bool(linha["possui_inconsistencia"]),
                        "aspectos": json.loads(linha["aspectos"] or "[]"),
                        "data_processamento": str(linha["data_processamento"]),
                    }
                )
                agrupado[analise.profissional_id].append(analise)
        return dict(agrupado)

    # ----------------------------------------------------------------- escrita

    def salvar_analises(self, analises: Sequence[AnaliseComentario]) -> int:
        if not analises:
            return 0
        parametros = [
            (
                a.avaliacao_reserva_id,
                a.profissional_id,
                a.sentimento.value,
                round(a.confianca, 4),
                int(a.possui_inconsistencia),
                json.dumps([asp.to_dict() for asp in a.aspectos], ensure_ascii=False),
                a.versao_modelo,
                _datetime_mysql(a.data_processamento),
            )
            for a in analises
        ]
        with self.conexao.cursor() as cursor:
            cursor.executemany(SQL_UPSERT_ANALISE, parametros)
        self.conexao.commit()
        return len(parametros)

    def salvar_reputacoes(self, reputacoes: Sequence[ReputacaoProfissional]) -> int:
        if not reputacoes:
            return 0
        parametros = [
            (
                r.profissional_id,
                r.comentarios_processados,
                r.quantidade_positivo,
                r.quantidade_neutro,
                r.quantidade_negativo,
                r.percentual_positivo,
                r.percentual_neutro,
                r.percentual_negativo,
                r.sentimento_medio,
                r.quantidade_inconsistencias,
                r.taxa_inconsistencia,
                json.dumps(r.pontos_fortes, ensure_ascii=False),
                json.dumps(r.pontos_fracos, ensure_ascii=False),
                r.resumo,
                r.versao_modelo,
                _datetime_mysql(r.data_atualizacao),
            )
            for r in reputacoes
        ]
        with self.conexao.cursor() as cursor:
            cursor.executemany(SQL_UPSERT_REPUTACAO, parametros)
        self.conexao.commit()
        return len(parametros)

    def marcar_reindexacao(self, profissional_ids: Sequence[int]) -> int:
        if not profissional_ids:
            return 0
        with self.conexao.cursor() as cursor:
            cursor.executemany(SQL_MARCAR_REINDEXACAO, [(pid, pid) for pid in profissional_ids])
        self.conexao.commit()
        return len(profissional_ids)

    def fechar(self) -> None:
        self.conexao.close()

    @staticmethod
    def _linha_para_avaliacao(linha: dict) -> Avaliacao:
        return Avaliacao(
            avaliacao_reserva_id=int(linha["avaliacao_reserva_id"]),
            profissional_id=int(linha["profissional_id"]),
            nota=int(linha["nota"]),
            comentario=linha.get("comentario"),
            data_avaliacao=str(linha.get("data_avaliacao") or ""),
        )