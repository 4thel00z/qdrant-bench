# BE-3: Encoding Client Adapter

**Role**: Backend Engineer
**Context**: We need to generate dense vectors for the seeded data using an OpenAI-compatible API.

## Requirements
1. Create a Port for `EmbeddingService`.
2. Implement an Adapter using the official async OpenAI client library (`openai`) to talk to an OpenAI-compatible embedding endpoint.
3. Ensure it supports batching if necessary for performance.
4. Handle rate limits and retries gracefully (async).

## Acceptance Criteria
- [ ] `EmbeddingService` Protocol defined.
- [ ] OpenAI-compatible adapter implemented.
- [ ] Integration test with a mock or real endpoint.

