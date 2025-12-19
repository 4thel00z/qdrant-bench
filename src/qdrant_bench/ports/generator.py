from collections.abc import Awaitable
from typing import Protocol

from qdrant_bench.domain.entities.core import Experiment, Run


class ParameterGenerator(Protocol):
    def suggest_next(
        self,
        previous_runs: list[Run],
        base_config: Experiment,
    ) -> Awaitable[Experiment]: ...
