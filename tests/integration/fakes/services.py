"""Fake service implementations for testing"""

from dataclasses import dataclass, field


@dataclass
class FakeEmbeddingService:
    """Fake embedding service that returns deterministic embeddings"""

    embedding_dim: int = 384
    call_count: int = field(default=0, init=False)

    async def embed_text(self, texts: list[str], model: str) -> list[list[float]]:
        """Returns deterministic embeddings based on text hash"""
        self.call_count += 1

        return [[float((hash(text) % 1000 + i) % 100) / 100.0 for i in range(self.embedding_dim)] for text in texts]
