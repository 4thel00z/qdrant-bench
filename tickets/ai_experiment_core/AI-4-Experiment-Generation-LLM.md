# AI-4: Experiment Generation (LLM Judge)

**Role**: AI Engineer
**Context**: Intelligent optimizer using an LLM to guide the search.

## Requirements
1. **LLM Implementation**:
   - Implement `LLMParameterGenerator` in `src/qdrant_bench/infrastructure/generators/llm.py`.
   - Use `Pydantic AI` to structure the interaction.

2. **Prompt Engineering**:
   - **Context**: Inject Qdrant tuning best practices (HNSW trade-offs, Quantization effects).
   - **Input**: JSON history of previous `Run` metrics (F1, Latency, RAM).
   - **Goal**: "Maximize F1 while keeping Latency < 50ms".
   - **Output**: Valid JSON configuration for the next run.

3. **Integration**:
   - Use the `EncodingService` (OpenAI adapter) or a separate LLM adapter if needed.

## Acceptance Criteria
- [ ] `LLMParameterGenerator` implemented using Pydantic AI.
- [ ] Prompt includes sufficient context for the LLM to make reasoning decisions.
- [ ] Output is validated against Qdrant configuration schemas.
