from typing import Protocol, List

class EmbeddingService(Protocol):
    async def embed_text(self, texts: List[str], model: str) -> List[List[float]]:
        ...

