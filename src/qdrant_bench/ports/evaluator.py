from typing import Protocol, Dict, Any, List
from dataclasses import dataclass

@dataclass
class GroundTruth:
    # Map of query_index -> set of relevant_doc_ids
    relevant_items: Dict[int, set]

@dataclass
class EvaluationResult:
    scores: Dict[str, float]

class Evaluator(Protocol):
    def evaluate(self, predictions: List[Any], ground_truth: GroundTruth, latencies: List[float]) -> EvaluationResult:
        ...

