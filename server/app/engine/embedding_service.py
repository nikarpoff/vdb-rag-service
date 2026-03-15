from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List

from app.core.config import settings
from app.core.logger import logger
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Local embedding generation based on a compact sentence-transformers model."""

    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading embedding model: {settings.embedding_model_name}")
            self._model = SentenceTransformer(settings.embedding_model_name)
        return self._model

    def embed(self, text: str) -> List[float]:
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def embed_many(self, texts: Iterable[str]) -> List[List[float]]:
        text_list = list(texts)
        if not text_list:
            return []

        vectors = self.model.encode(
            text_list,
            batch_size=settings.embedding_batch_size,
            normalize_embeddings=True,
        )
        return [vector.tolist() for vector in vectors]


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
