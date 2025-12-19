import hashlib
from dataclasses import dataclass
from typing import Final

from qdrant_bench.ports.embedding_service import EmbeddingService


def stable_text_seed(text: str) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def deterministic_vector(text: str, embedding_dim: int) -> list[float]:
    seed = stable_text_seed(text) % 1000
    scale: Final[float] = 100.0

    return [float((seed + i) % 100) / scale for i in range(embedding_dim)]


@dataclass(frozen=True, slots=True)
class DeterministicEmbeddingAdapter(EmbeddingService):
    embedding_dim: int = 384

    async def embed_text(self, texts: list[str], model: str) -> list[list[float]]:
        embedding_dim = self.embedding_dim
        return [deterministic_vector(text=text, embedding_dim=embedding_dim) for text in texts]
