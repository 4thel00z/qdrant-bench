from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class GroundTruth:
    # Map of query_index -> set of relevant_doc_ids
    relevant_items: dict[int, set]


@dataclass
class EvaluationResult:
    scores: dict[str, float]


class Evaluator(Protocol):
    def evaluate(
        self, predictions: list[Any], ground_truth: GroundTruth, latencies: list[float]
    ) -> EvaluationResult: ...
