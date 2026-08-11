from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Sentimento(str, Enum):
    POSITIVO = "POSITIVO"
    NEUTRO = "NEUTRO"
    NEGATIVO = "NEGATIVO"

    @property
    def valor_normalizado(self) -> float:
        return _VALOR_NORMALIZADO[self]


_VALOR_NORMALIZADO = {
    Sentimento.NEGATIVO: 0.0,
    Sentimento.NEUTRO: 0.5,
    Sentimento.POSITIVO: 1.0,
}

CLASSES = [Sentimento.NEGATIVO, Sentimento.NEUTRO, Sentimento.POSITIVO]
CLASSES_STR = [c.value for c in CLASSES]


class Polaridade(str, Enum):

    POSITIVA = "POSITIVA"
    NEGATIVA = "NEGATIVA"
    NEUTRA = "NEUTRA"


def agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(slots=True)
class Avaliacao:

    avaliacao_reserva_id: int
    profissional_id: int
    nota: int
    comentario: str | None = None
    data_avaliacao: str | None = None
    rotulo_sentimento: Sentimento | None = None

    @property
    def tem_comentario(self) -> bool:
        return bool(self.comentario and self.comentario.strip())

    def to_dict(self) -> dict[str, Any]:
        dados = asdict(self)
        if self.rotulo_sentimento is None:
            dados.pop("rotulo_sentimento")
        else:
            dados["rotulo_sentimento"] = self.rotulo_sentimento.value
        return dados

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> "Avaliacao":
        return cls(
            avaliacao_reserva_id=int(dados["avaliacao_reserva_id"]),
            profissional_id=int(dados["profissional_id"]),
            nota=int(dados["nota"]),
            comentario=dados.get("comentario"),
            data_avaliacao=dados.get("data_avaliacao"),
            rotulo_sentimento=(
                Sentimento(dados["rotulo_sentimento"])
                if dados.get("rotulo_sentimento")
                else None
            ),
        )


@dataclass(slots=True)
class ExemploRotulado:

    avaliacao_reserva_id: int
    profissional_id: int
    texto: str
    rotulo: Sentimento
    nota: int
    origem_rotulo: str = "fraco"

    def to_dict(self) -> dict[str, Any]:
        dados = asdict(self)
        dados["rotulo"] = self.rotulo.value
        return dados

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> "ExemploRotulado":
        return cls(
            avaliacao_reserva_id=int(dados["avaliacao_reserva_id"]),
            profissional_id=int(dados["profissional_id"]),
            texto=dados["texto"],
            rotulo=Sentimento(dados["rotulo"]),
            nota=int(dados["nota"]),
            origem_rotulo=dados.get("origem_rotulo", "fraco"),
        )


@dataclass(slots=True)
class Predicao:

    sentimento: Sentimento
    confianca: float
    versao_modelo: str
    probabilidades: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sentimento": self.sentimento.value,
            "confianca": round(self.confianca, 4),
            "versaoModelo": self.versao_modelo,
        }


@dataclass(slots=True)
class AspectoDetectado:
    aspecto: str
    polaridade: Polaridade
    ocorrencias: int = 1
    termos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "aspecto": self.aspecto,
            "polaridade": self.polaridade.value,
            "ocorrencias": self.ocorrencias,
            "termos": self.termos,
        }

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> "AspectoDetectado":
        return cls(
            aspecto=dados["aspecto"],
            polaridade=Polaridade(dados["polaridade"]),
            ocorrencias=int(dados.get("ocorrencias", 1)),
            termos=list(dados.get("termos", [])),
        )


@dataclass(slots=True)
class AnaliseComentario:

    avaliacao_reserva_id: int
    profissional_id: int
    sentimento: Sentimento
    confianca: float
    possui_inconsistencia: bool
    versao_modelo: str
    comentario: str = ""
    nota: int | None = None
    aspectos: list[AspectoDetectado] = field(default_factory=list)
    data_processamento: str = field(default_factory=agora_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "avaliacao_reserva_id": self.avaliacao_reserva_id,
            "profissional_id": self.profissional_id,
            "sentimento": self.sentimento.value,
            "confianca": round(self.confianca, 4),
            "possui_inconsistencia": self.possui_inconsistencia,
            "versao_modelo": self.versao_modelo,
            "comentario": self.comentario,
            "nota": self.nota,
            "aspectos": [a.to_dict() for a in self.aspectos],
            "data_processamento": self.data_processamento,
        }

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> "AnaliseComentario":
        return cls(
            avaliacao_reserva_id=int(dados["avaliacao_reserva_id"]),
            profissional_id=int(dados["profissional_id"]),
            sentimento=Sentimento(dados["sentimento"]),
            confianca=float(dados["confianca"]),
            possui_inconsistencia=bool(dados["possui_inconsistencia"]),
            versao_modelo=dados["versao_modelo"],
            comentario=dados.get("comentario", ""),
            nota=int(dados["nota"]) if dados.get("nota") is not None else None,
            aspectos=[AspectoDetectado.from_dict(a) for a in dados.get("aspectos", [])],
            data_processamento=dados.get("data_processamento", agora_iso()),
        )


@dataclass(slots=True)
class ReputacaoProfissional:
    profissional_id: int
    comentarios_processados: int
    quantidade_positivo: int
    quantidade_neutro: int
    quantidade_negativo: int
    percentual_positivo: float
    percentual_neutro: float
    percentual_negativo: float
    sentimento_medio: float
    quantidade_inconsistencias: int
    taxa_inconsistencia: float
    pontos_fortes: list[str]
    pontos_fracos: list[str]
    resumo: str
    versao_modelo: str
    data_atualizacao: str = field(default_factory=agora_iso)

    def to_dict(self) -> dict[str, Any]:
        dados = asdict(self)
        dados["pontos_fortes"] = list(self.pontos_fortes)
        dados["pontos_fracos"] = list(self.pontos_fracos)
        return dados

    @classmethod
    def from_dict(cls, dados: dict[str, Any]) -> "ReputacaoProfissional":
        return cls(**dados)
