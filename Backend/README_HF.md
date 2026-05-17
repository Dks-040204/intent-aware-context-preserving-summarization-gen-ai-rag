---
title: Contexto API
emoji: 🔬
colorFrom: purple
colorTo: orange
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Contexto — Intent-Aware Summarization API

FastAPI backend for [Contexto](https://github.com/Dks-040204/intent-aware-context-preserving-summarization-gen-ai-rag).

## Endpoints
- `GET /health` — health check
- `POST /auto-summarize` — summarize with intent + level + language + quality
- `POST /keywords` — keyword extraction
- `POST /batch-summarize` — batch mode

See `/docs` for the full interactive Swagger UI.
