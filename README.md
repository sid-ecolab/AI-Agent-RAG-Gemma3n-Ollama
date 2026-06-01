# AI Agent with RAG and Tool Calling — Local Mode (Gemma 3n E4B)

A dual-profile AI agent that supports both **cloud (Azure OpenAI)** and **local (Ollama + Gemma 3n E4B)** execution. Features retrieval-augmented generation (RAG) for document context injection and function calling for tool integration.

## Architecture

```
User Query
    │
    ├─► RAG Retrieval (ChromaDB)
    │     ├── Cloud: text-embedding-3-small (1536-dim)
    │     └── Local: nomic-embed-text (768-dim)
    │
    ├─► Tool Calling (get_air_quality)
    │     └── Same OpenAI tools=[...] schema for both profiles
    │
    └─► LLM Response
          ├── Cloud: Azure OpenAI (gpt-5.4-nano)
          └── Local: Ollama (gemma3:e4b)
```

Only the client construction changes between profiles — the rest of the code is profile-agnostic.

## Prerequisites

### Hardware
- **Cloud Profile:** Internet connection + Azure OpenAI API access
- **Local Profile:**
  - 16 GB RAM minimum (32 GB recommended)
  - macOS or Linux
  - ~3 GB disk for Gemma 3n E4B model

### Software
- Python 3.9+
- Ollama (for local mode): https://ollama.com
- Git

## Quick Start — Local Mode (< 15 minutes)

### 1. Install Ollama & Pull Models

```bash
brew install ollama
brew services start ollama

# Pull the LLM
ollama pull gemma3:e4b
ollama run gemma3:e4b "Hello"   # smoke test

# Pull the embedding model
ollama pull nomic-embed-text
```

### 2. Clone & Setup

```bash
git clone https://github.com/sid-ecolab/AI-Agent-RAG-Gemma3n-Ollama.git
cd AI-Agent-RAG-Gemma3n-Ollama
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Ingest Documents (Local Embeddings)

```bash
export LLM_PROFILE=local
python ingest.py
```

This creates a fresh `documents_local` collection using `nomic-embed-text` (768-dim).

### 4. Run the Agent

```bash
# CLI
LLM_PROFILE=local python main.py

# Streamlit UI
LLM_PROFILE=local streamlit run app.py
```

## Profile Switching

A single environment variable flips between cloud and local:

```bash
# Cloud mode (Azure OpenAI)
export LLM_PROFILE=cloud
export AZURE_OPENAI_API_KEY="your-key-here"

# Local mode (Ollama + Gemma 3n E4B)
export LLM_PROFILE=local
# No API key needed — Ollama runs locally
```

| Component | Cloud | Local |
|-----------|-------|-------|
| LLM | Azure OpenAI (gpt-5.4-nano) | Ollama (gemma3:e4b) |
| Embeddings | text-embedding-3-small (1536-dim) | nomic-embed-text (768-dim) |
| Collection | `documents` | `documents_local` |
| Endpoint | Azure API | http://localhost:11434/v1 |

**Important:** Each profile uses a separate ChromaDB collection to avoid embedding dimension mismatch.

## Features

### Retrieval-Augmented Generation (RAG)
- Retrieves top-k relevant document chunks per query
- Augments user messages with retrieved context
- Supports PDF ingestion from `data/` directory

### Tool Calling
- `get_air_quality(city)` — fetches real-time air quality data
- Same OpenAI `tools=[...]` schema for both profiles
- Ollama supports function calling via the OpenAI-compatible endpoint

### Embedding Details

| Model | Dimensions | Chunk Size | Retrieval k |
|-------|-----------|------------|-------------|
| text-embedding-3-small (cloud) | 1536 | 700 chars, 100 overlap | 3 |
| nomic-embed-text (local) | 768 | 700 chars, 100 overlap | 3 |

## File Structure

```
.
├── agent.py          # Agent loop with RAG + tool calling (profile-aware)
├── retriever.py      # ChromaDB retrieval (profile-aware embeddings)
├── ingest.py         # Document ingestion pipeline (profile-aware)
├── tools.py          # get_air_quality tool
├── app.py            # Streamlit web UI
├── main.py           # CLI entry point
├── requirements.txt  # Python dependencies
├── data/             # PDF corpus for ingestion
├── docs/
│   ├── local-mode-comparison.md   # Side-by-side 20-query comparison
│   ├── when-to-go-local.md        # Decision document
│   ├── transcript-cloud.md        # Example cloud transcript
│   └── transcript-local.md        # Example local transcript
└── README.md
```

## Hardware Used for Testing

| Component | Specification |
|-----------|--------------|
| OS | macOS Sequoia (Darwin 24.3.0) |
| Chip | Apple Silicon |
| RAM | 16 GB+ |
| Ollama Model | gemma3:e4b (~3 GB) |
| Embedding Model | nomic-embed-text (~300 MB) |

## Performance Summary

| Metric | Cloud | Local |
|--------|-------|-------|
| Latency p50 | ~1.0s | ~3.5s |
| Latency p95 | ~1.9s | ~5.2s |
| Quality (avg) | 3.4/4 | 2.7/4 |
| Tool call accuracy | 100% | 86% |
| Cost per query | ~$0.003 | $0 |

See [docs/local-mode-comparison.md](docs/local-mode-comparison.md) for full results.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Ollama connection refused | Run `ollama serve` or `brew services start ollama` |
| Embedding dimension mismatch | Re-ingest with correct profile: `LLM_PROFILE=local python ingest.py` |
| Out of memory | Use `gemma3:1b` instead; document the constraint |
| Slow inference | Expected — local is 2-3x slower than cloud |
| Tool call not triggered | Add explicit instructions in system prompt; lower temperature |

## Documentation

- [Local vs Cloud Comparison](docs/local-mode-comparison.md) — 20-query benchmark
- [When to Go Local](docs/when-to-go-local.md) — decision framework for Ecolab scenarios
- [Cloud Transcript](docs/transcript-cloud.md) — example combined query
- [Local Transcript](docs/transcript-local.md) — same query, local profile
