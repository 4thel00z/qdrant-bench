# AI-4: Experiment Generation - LLM Judge (Implementation)

**Role**: AI Engineer
**Context**: Implement the LLM-driven optimizer.

## Requirements
1. **Dependencies**: `Pydantic AI`, `OpenAI` adapter (or similar).

2. **LLMGenerator**:
   - Class: `LLMParameterGenerator` in `src/qdrant_bench/infrastructure/generators/llm.py`.
   - Implement `ParameterGenerator` protocol.

3. **Prompting**:
   - System Prompt: You are an expert Qdrant DB administrator.
   - Context: Qdrant docs (HNSW params, Quantization types).
   - User Prompt: Here is the current config {...} and the resulting metrics {...}. The goal is F1 > 0.95. Suggest the next config.

4. **Structured Output**:
   - Use Pydantic models to enforce the output schema (valid Qdrant config structure).

## Acceptance Criteria
- [ ] `LLMParameterGenerator` implemented.
- [ ] Integration with Pydantic AI.
- [ ] Valid JSON config generation.

