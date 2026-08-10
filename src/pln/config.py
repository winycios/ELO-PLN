from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def _env(nome: str, padrao: str) -> str:
    return os.environ.get(nome, padrao)


def _env_int(nome: str, padrao: int) -> int:
    return int(os.environ.get(nome, padrao))


def _env_float(nome: str, padrao: float) -> float:
    return float(os.environ.get(nome, padrao))


@dataclass(slots=True)
class ConfigCaminhos:
    raiz: Path = RAIZ
    dados_brutos: Path = field(default_factory=lambda: RAIZ / "data" / "raw")
    dados_processados: Path = field(default_factory=lambda: RAIZ / "data" / "processed")
    splits: Path = field(default_factory=lambda: RAIZ / "data" / "splits")
    modelos: Path = field(default_factory=lambda: RAIZ / "models")
    relatorios: Path = field(default_factory=lambda: RAIZ / "reports")

    @classmethod
    def em(cls, raiz: Path) -> "ConfigCaminhos":
        return cls(
            raiz=raiz,
            dados_brutos=raiz / "data" / "raw",
            dados_processados=raiz / "data" / "processed",
            splits=raiz / "data" / "splits",
            modelos=raiz / "models",
            relatorios=raiz / "reports",
        )

    def preparar(self) -> None:
        for caminho in (
            self.dados_brutos,
            self.dados_processados,
            self.splits,
            self.modelos,
            self.relatorios,
        ):
            caminho.mkdir(parents=True, exist_ok=True)


@dataclass(slots=True)
class ConfigDataset:
    seed: int = field(default_factory=lambda: _env_int("ELO_PLN_SEED", 42))
    proporcao_treino: float = 0.70
    proporcao_validacao: float = 0.15
    proporcao_teste: float = 0.15
    tamanho_minimo_comentario: int = field(
        default_factory=lambda: _env_int("ELO_PLN_MIN_CARACTERES", 3)
    )
    versao_dataset: str = field(default_factory=lambda: _env("ELO_PLN_VERSAO_DATASET", "v1"))


@dataclass(slots=True)
class ConfigModelo:
    backend: str = "baseline"
    versao: str = field(default_factory=lambda: _env("ELO_PLN_VERSAO_MODELO", "sentimento-ptbr-v1"))
    confianca_minima: float = field( default_factory=lambda: _env_float("ELO_PLN_CONFIANCA_MINIMA", 0.55) )


@dataclass(slots=True)
class ConfigReputacao:
    minimo_ocorrencias_aspecto: int = field(
        default_factory=lambda: _env_int("ELO_PLN_MIN_OCORRENCIAS_ASPECTO", 2)
    )
    minimo_comentarios_resumo: int = field(
        default_factory=lambda: _env_int("ELO_PLN_MIN_COMENTARIOS_RESUMO", 3)
    )
    maximo_pontos_fortes: int = field(default_factory=lambda: _env_int("ELO_PLN_MAX_PONTOS", 3))
    peso_avaliacao_inconsistente: float = field(
        default_factory=lambda: _env_float("ELO_PLN_PESO_INCONSISTENTE", 0.3)
    )


@dataclass(slots=True)
class ConfigWorker:
    repositorio: str = field(default_factory=lambda: _env("ELO_PLN_REPOSITORIO", "jsonl"))
    tamanho_lote: int = field(default_factory=lambda: _env_int("ELO_PLN_LOTE", 200))
    intervalo_segundos: int = field(default_factory=lambda: _env_int("ELO_PLN_INTERVALO", 60))


@dataclass(slots=True)
class ConfigMySQL:
    host: str = field(default_factory=lambda: _env("ELO_DB_HOST", "localhost"))
    porta: int = field(default_factory=lambda: _env_int("ELO_DB_PORT", 3306))
    banco: str = field(default_factory=lambda: _env("ELO_DB_NAME", "database_elo"))
    usuario: str = field(default_factory=lambda: _env("ELO_DB_USER", "root"))
    senha: str = field(default_factory=lambda: _env("ELO_DB_PASSWORD", ""))


@dataclass(slots=True)
class Config:
    caminhos: ConfigCaminhos = field(default_factory=ConfigCaminhos)
    dataset: ConfigDataset = field(default_factory=ConfigDataset)
    modelo: ConfigModelo = field(default_factory=ConfigModelo)
    reputacao: ConfigReputacao = field(default_factory=ConfigReputacao)
    worker: ConfigWorker = field(default_factory=ConfigWorker)
    mysql: ConfigMySQL = field(default_factory=ConfigMySQL)

    @property
    def diretorio_modelo(self) -> Path:
        return self.caminhos.modelos / f"{self.modelo.versao}-{self.modelo.backend}"


def carregar_config() -> Config:
    return Config()
