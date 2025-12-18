from typing import Protocol


class EmbeddingService(Protocol):
    async def embed_text(self, texts: list[str], model: str) -> list[list[float]]: ...
