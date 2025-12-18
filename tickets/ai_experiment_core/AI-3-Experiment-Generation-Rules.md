# AI-3: Experiment Generation (Rule-Based)

**Role**: AI Engineer
**Context**: Simple heuristic optimizer to propose the next set of parameters.

## Requirements
1. **Generator Protocol**:
   - Define `ParameterGenerator` Protocol in `src/qdrant_bench/ports/generator.py`.
   - Method: `suggest_next(previous_runs: List[Run], base_config: ExperimentConfig) -> ExperimentConfig`.

2. **Rule-Based Implementation**:
   - Implement `RuleBasedGenerator` in `src/qdrant_bench/infrastructure/generators/rule_based.py`.
   - **Strategies**:
     - **Grid Search**: Iterate through a predefined list of values (e.g., m=[16, 32, 64]).
     - **Heuristic**: Simple logic like "If latency > 100ms, reduce m" or "If recall < 0.9, increase ef_construct".

## Acceptance Criteria
- [ ] `ParameterGenerator` interface defined.
- [ ] Rule-based generator can produce a list of valid Qdrant configurations.
- [ ] Logic handles basic constraints (valid ranges for m, ef).
