# trvcloud-knowledge-base
Project:  Enterprise RAG-powered AI Knowledge Assistant|

Development Milestones (Step-by-Step):

Phase 1: Authentication & Basic Web App

Set up Flask with basic home, login/logout using Okta OIDC.
Learn OIDC tokens, JWT parsing, user/session handling.

Phase 2: Data Storage & Management

Deploy PostgreSQL + PGVector.
Build a doc-upload endpoint (parse PDF/text docs, chunking, create/store embeddings).

Phase 3: Redis Integration

Use Redis to cache session data & common query responses.
Implement simple caching logic (recent queries, embeddings vectors).

Phase 4: AI / RAG Integration

Integrate Ollama (start with llama3 or gemma) for RAG-based question answering.
Fine-tune prompt engineering to improve answers.

Phase 5: UI & UX polish (optional)

Simple web UI (Bootstrap or Tailwind) to enhance usability.
Real-time search suggestions or advanced UI components.