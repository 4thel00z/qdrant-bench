from typing import Any

import numpy as np

from qdrant_bench.ports.evaluator import EvaluationResult, Evaluator, GroundTruth


class StandardEvaluator(Evaluator):
    def evaluate(self, predictions: list[Any], ground_truth: GroundTruth, latencies: list[float]) -> EvaluationResult:
        # predictions: List of Qdrant Search Responses (ScoredPoint)

        recall_scores = []
        precision_scores = []

        for i, prediction in enumerate(predictions):
            # Prediction is a list of ScoredPoint
            retrieved_ids = {point.id for point in prediction}
            relevant_ids = ground_truth.relevant_items.get(i, set())

            if not relevant_ids:
                continue

            # Calculate Intersection
            intersection = retrieved_ids.intersection(relevant_ids)

            # Recall = (Relevant & Retrieved) / Relevant
            recall = len(intersection) / len(relevant_ids)
            recall_scores.append(recall)

            # Precision = (Relevant & Retrieved) / Retrieved
            precision = len(intersection) / len(retrieved_ids) if retrieved_ids else 0.0
            precision_scores.append(precision)

        avg_recall = np.mean(recall_scores) if recall_scores else 0.0
        avg_precision = np.mean(precision_scores) if precision_scores else 0.0
        f1 = (
            2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0.0
        )

        # Latency Metrics
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        qps = len(latencies) / sum(latencies) if latencies else 0.0

        return EvaluationResult(
            scores={
                "recall": float(avg_recall),
                "precision": float(avg_precision),
                "f1": float(f1),
                "p50_latency": float(p50),
                "p95_latency": float(p95),
                "p99_latency": float(p99),
                "qps": float(qps),
            }
        )
