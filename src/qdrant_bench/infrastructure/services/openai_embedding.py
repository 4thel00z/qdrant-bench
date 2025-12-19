import logfire
from openai import AsyncOpenAI

from qdrant_bench.ports.embedding_service import EmbeddingService


class OpenAIEmbeddingAdapter(EmbeddingService):
    def __init__(self, api_key: str, base_url: str | None = None):
        if base_url:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
            return

        self.client = AsyncOpenAI(api_key=api_key)

    async def embed_text(self, texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
        with logfire.span("OpenAI Embedding Generation", model=model, batch_size=len(texts)):
            try:
                response = await self.client.embeddings.create(input=texts, model=model)
                return [data.embedding for data in response.data]
            except Exception as e:
                logfire.error(f"Failed to generate embeddings: {e}")
                raise
