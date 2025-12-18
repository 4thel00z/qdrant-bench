# AI-3: Experiment Generation - Rule Based (Implementation)

**Role**: AI Engineer
**Context**: Implement a simple strategy to suggest next parameters.

## Requirements
1. **Generator Protocol**:
   - Define `ParameterGenerator` in `src/qdrant_bench/ports/generator.py`.

2. **RuleBasedGenerator**:
   - Class: `RuleBasedGenerator` in `src/qdrant_bench/infrastructure/generators/rule_based.py`.
   - Logic:
     - Input: Current `Experiment` config + Result `metrics`.
     - Heuristic:
       - If `recall < 0.9`: Increase `m` (e.g. 16 -> 32) or `ef_construct`.
       - If `latency_p95 > 0.05`: Decrease `m` or enable `quantization`.
   - Output: New `Experiment` configuration (or dictionary of overrides).

## Acceptance Criteria
- [ ] Protocol defined.
- [ ] Heuristic logic implemented.
- [ ] Generator returns a valid config object.

