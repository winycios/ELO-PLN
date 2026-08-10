from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Iterator


def escrever_jsonl(caminho: Path, registros: Iterable[dict[str, Any]]) -> int:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with caminho.open("w", encoding="utf-8") as arquivo:
        for registro in registros:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
            total += 1
    return total


def anexar_jsonl(caminho: Path, registros: Iterable[dict[str, Any]]) -> int:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with caminho.open("a", encoding="utf-8") as arquivo:
        for registro in registros:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
            total += 1
    return total


def ler_jsonl(caminho: Path) -> Iterator[dict[str, Any]]:
    if not caminho.exists():
        return
    with caminho.open(encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha:
                yield json.loads(linha)


def escrever_json(caminho: Path, dados: Any) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def ler_json(caminho: Path) -> Any:
    return json.loads(caminho.read_text(encoding="utf-8"))
