import copy
from typing import Any

import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from qdrant_bench.domain.entities.core import Experiment, Run
from qdrant_bench.ports.generator import ParameterGenerator


class QdrantConfig(BaseModel):
    optimizer_config: dict[str, Any] = Field(description="The optimizer configuration for Qdrant collection")
    vector_config: dict[str, Any] = Field(
        description="The vector configuration for Qdrant collection (HNSW, quantization, etc.)"
    )
    reasoning: str = Field(description="Explanation of why these parameters were chosen based on previous results")


class LLMParameterGenerator(ParameterGenerator):
    def __init__(self, model_name: str = "openai:gpt-4o"):
        self.agent = Agent(
            model_name,
            output_type=QdrantConfig,
            system_prompt="""You are an expert Qdrant Database Administrator and Performance Tuning Specialist.
            Your goal is to suggest the next optimal configuration for a vector search benchmark experiment.
            You will be provided with the base configuration and a history of previous runs with their metrics.
            Tuning Context & Best Practices:
                - HNSW `m`: Higher = better recall but more RAM/CPU. Typical range: 16-64.
                - HNSW `ef_construct`: Higher = better index quality but slower indexing. Typical range: 100-512.
                - Quantization (Scalar/Product/Binary): Use for memory reduction. Trade-off: Precision loss.
                - Optimizers: `indexing_threshold` controls when HNSW is built.
            Analyze the trade-offs (Recall vs Latency vs RAM) and propose the next step.
           """,
        )

    async def suggest_next(self, previous_runs: list[Run], base_config: Experiment) -> Experiment:
        # Prepare context for the LLM
        history_context = []
        for run in previous_runs:
            history_context.append(
                {
                    "run_id": str(run.id),
                    "status": run.status,
                    "metrics": run.metrics,
                    # In a real scenario, we'd need to link the run back to the specific config used
                    # if it differed from the base_config (e.g. if we save the config on the run).
                    # For now, assuming previous runs might have varied slightly or we are evolving the base.
                }
            )

        prompt = (
            f"Base Configuration:\n"
            f"Optimizer Config: {base_config.optimizer_config}\n"
            f"Vector Config: {base_config.vector_config}\n\n"
            f"Run History:\n{history_context}\n\n"
            f"Goal: Maximize Recall while keeping p95 latency under 50ms (example goal)."
        )

        with logfire.span("LLM Parameter Generation"):
            result = await self.agent.run(prompt)
            suggestion = result.output

            logfire.info(f"LLM Suggestion: {suggestion.reasoning}")

            # Create new experiment config based on suggestion
            new_config = copy.deepcopy(base_config)
            new_config.optimizer_config = suggestion.optimizer_config
            new_config.vector_config = suggestion.vector_config

            return new_config
