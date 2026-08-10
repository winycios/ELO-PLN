from .base import RepositorioPln
from .jsonl_repo import JsonlRepositorio


def criar_repositorio(config) -> RepositorioPln:
    tipo = config.worker.repositorio.lower()
    if tipo == "jsonl":
        return JsonlRepositorio(config)
    if tipo == "mysql":
        from .mysql_repo import MySQLRepositorio

        return MySQLRepositorio(config)
    raise ValueError(f"Repositorio desconhecido: {tipo!r}. Use 'jsonl' ou 'mysql'.")


__all__ = ["RepositorioPln", "JsonlRepositorio", "criar_repositorio"]
