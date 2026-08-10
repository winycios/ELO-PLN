from __future__ import annotations

from collections.abc import Sequence

from ..texto import normalizar_para_busca

# Palavras muito frequentes em avaliacoes e sem valor discriminativo.
STOPWORDS_PT = [
    "a", "as", "ao", "aos", "com", "como", "da", "das", "de", "do", "dos", "e",
    "ela", "ele", "em", "essa", "esse", "eu", "foi", "for", "isso", "ja", "la",
    "mais", "mas", "me", "meu", "minha", "muito", "na", "nao", "nas", "no",
    "nos", "o", "os", "ou", "para", "pela", "pelo", "por", "que", "se", "ser",
    "seu", "sua", "tambem", "tem", "um", "uma", "voce", "vou",
]


def termos_relevantes(
    documentos: Sequence[str],
    top_n: int = 10,
    min_df: int = 2,
    ngramas: tuple[int, int] = (1, 2),
) -> list[list[tuple[str, float]]]:
    from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: PLC0415

    if not documentos:
        return []

    normalizados = [normalizar_para_busca(doc) for doc in documentos]
    vetorizador = TfidfVectorizer(
        ngram_range=ngramas,
        min_df=min(min_df, len(normalizados)),
        stop_words=STOPWORDS_PT,
        sublinear_tf=True,
    )
    matriz = vetorizador.fit_transform(normalizados)
    vocabulario = vetorizador.get_feature_names_out()

    resultado: list[list[tuple[str, float]]] = []
    for indice in range(matriz.shape[0]):
        linha = matriz.getrow(indice).toarray().ravel()
        melhores = linha.argsort()[::-1][:top_n]
        resultado.append(
            [(str(vocabulario[i]), float(linha[i])) for i in melhores if linha[i] > 0]
        )
    return resultado


def termos_do_profissional(comentarios: Sequence[str], top_n: int = 8) -> list[tuple[str, float]]:
    if not comentarios:
        return []
    documentos = [" ".join(comentarios), *comentarios]
    return termos_relevantes(documentos, top_n=top_n, min_df=1)[0]
