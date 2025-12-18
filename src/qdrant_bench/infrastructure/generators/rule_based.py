import copy
import dataclasses

from qdrant_bench.domain.entities.core import Experiment, Run, RunStatus
from qdrant_bench.ports.generator import ParameterGenerator


class RuleBasedGenerator(ParameterGenerator):
    def __init__(self, strategy: str = "heuristic"):
        """
        strategy: 'heuristic' or 'grid'
        """
        self.strategy = strategy
        self.grid_params = {
            "m": [16, 24, 32, 48, 64],
            "ef_construct": [100, 200, 300, 400]
        }
        self.grid_index = 0

    async def suggest_next(self, previous_runs: list[Run], base_config: Experiment) -> Experiment:
        """Suggest next config - pure function (no mutation)"""
        if self.strategy == "grid":
            return self.grid_search(previous_runs, base_config)

        return self.heuristic_search(previous_runs, base_config)

    def grid_search(self, previous_runs: list[Run], base_config: Experiment) -> Experiment:
        """Simple grid search through predefined parameter space"""
        m_values = self.grid_params["m"]
        ef_values = self.grid_params["ef_construct"]
        total_combinations = len(m_values) * len(ef_values)

        if self.grid_index >= total_combinations:
            self.grid_index = 0

        m_idx = self.grid_index // len(ef_values)
        ef_idx = self.grid_index % len(ef_values)

        m_value = m_values[m_idx]
        ef_value = ef_values[ef_idx]

        new_vector_config = copy.deepcopy(base_config.vector_config)
        new_vector_config.setdefault("hnsw_config", {})
        new_vector_config["hnsw_config"]["m"] = m_value
        new_vector_config["hnsw_config"]["ef_construct"] = ef_value

        self.grid_index += 1

        return dataclasses.replace(base_config, vector_config=new_vector_config)

    def heuristic_search(self, previous_runs: list[Run], base_config: Experiment) -> Experiment:
        """Heuristic-based parameter adjustment"""
        if not previous_runs:
            return base_config

        latest = find_latest_completed_run(previous_runs)

        if not latest:
            return base_config

        new_vector_config = apply_heuristic_rules(
            metrics=latest.metrics,
            current_config=base_config.vector_config
        )

        return dataclasses.replace(base_config, vector_config=new_vector_config)


def find_latest_completed_run(runs: list[Run]) -> Run | None:
    """Pure function - find latest completed run"""
    completed = [r for r in runs if r.status == RunStatus.COMPLETED]

    if not completed:
        return None

    return max(completed, key=lambda r: r.start_time or 0) if completed else None


def apply_heuristic_rules(metrics: dict, current_config: dict) -> dict:
    """Pure function - apply tuning rules"""
    recall = metrics.get("recall", 0.0)
    p95_latency = metrics.get("p95_latency", 0.0)

    hnsw = current_config.get("hnsw_config", {})
    current_m = hnsw.get("m", 16)
    current_ef = hnsw.get("ef_construct", 100)

    new_m, new_ef = apply_tuning_rules(
        recall=recall,
        latency=p95_latency,
        current_m=current_m,
        current_ef=current_ef
    )

    return {
        **current_config,
        "hnsw_config": {
            **hnsw,
            "m": new_m,
            "ef_construct": new_ef
        }
    }


def apply_tuning_rules(
    recall: float,
    latency: float,
    current_m: int,
    current_ef: int
) -> tuple[int, int]:
    """Pure function - determine new parameters"""
    if recall < 0.85 and current_m < 64:
        return (current_m + 8, current_ef)

    if recall < 0.85 and current_ef < 400:
        return (current_m, current_ef + 100)

    if latency > 0.1 and current_m > 16:
        return (max(16, current_m - 8), current_ef)

    if latency > 0.1 and current_ef > 100:
        return (current_m, max(100, current_ef - 50))

    return (current_m, current_ef)
