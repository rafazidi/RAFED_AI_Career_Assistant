# Architecture

## Request flow

1. React sends a message to `POST /api/chat`.
2. FastAPI validates the message.
3. The RAG service embeds the question with a multilingual Sentence Transformers model.
4. ChromaDB retrieves the closest profile document chunks.
5. The LLM service sends the question and retrieved context to a configured OpenAI-compatible API.
6. The API returns the answer and the retrieved source excerpts.

## Main design decisions

- Frontend and backend are separate applications.
- Secrets remain in the backend `.env` file.
- French and English are supported by multilingual embeddings and an explicit language field.
- Profile facts come from Markdown files in `knowledge_base/`.
- The assistant is instructed to acknowledge missing information rather than invent details.

## Next improvements

- Add conversation history with a clear retention policy.
- Add document upload and PDF ingestion with access controls.
- Add answer evaluation and retrieval quality tests.
- Add rate limiting, logging with personal-data minimization, and deployment hardening.
- Add job-offer comparison as a separate feature after the core assistant is validated.
