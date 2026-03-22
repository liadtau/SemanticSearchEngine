# Semantic Code Search Engine

An advanced Retrieval-Augmented Generation (RAG) agent that ingests compressed Python codebases, semantically parses them, and allows users to query codebase logic using natural language.

## Architecture

1. **AST Parsing (Tree-sitter)**: Extracts Python source files and chunks them contextually by `class` and `function` structures while preventing directory traversal attacks.
2. **Local Vector Embeddings (Jina AI & ChromaDB)**: Generates numeric semantic vector embeddings for each chunk using the `sentence-transformers` library (specifically `jina-embeddings-v2-base-code`) and stores them locally in ChromaDB.
3. **Conversational LLM RAG (TinyLlama)**: Synthesizes search results into natural language agent replies using the lightweight 1.1B parameter `TinyLlama` model running completely locally via HuggingFace `transformers`. No paid LLM APIs are utilized.
4. **React Frontend UI**: A ChatGPT-style intuitive web interface built with React, Vite, and TailwindCSS to interact with the Python codebase with full syntax highlighting.

## Prerequisites
- **Git**
- **Docker & Docker Compose**
- **Make**

## How to Run

A convenient Makefile is provided to easily manage and configure the Docker instances.

1. **Build the application**:
   ```bash
   make build
   ```

2. **Start the services**:
   ```bash
   make up
   ```
   *The very first search initialization event will take several minutes as PyTorch, ChromaDB, and the underlying AI models (Jina Embeddings ~0.5GB, TinyLlama ~2.2GB) are initialized locally for the container.*

3. **Access the UI**:
   Launch a Chromium or WebKit browser natively to [http://localhost:5173](http://localhost:5173). 
   *Note: The backend API runs securely on `localhost:8000`.*

4. **Monitor the logs**:
   ```bash
   make logs
   ```

5. **Stop the services**:
   ```bash
   make down
   ```

6. **Tear down completely (including vector persistence)**:
   ```bash
   make clean
   ```

## Workflow Guide
1. Upload a compressed application archive (`.zip`, `.tar`, `.tar.gz`).
2. Check the Status logs, "Extracting, Chunking & Embedding..."
3. Ask contextual questions like *"Where is authentication handled?"* or *"How do I add two numbers?"* into the Semantic RAG Agent dialogue area on the right panel.
4. Expand the generated citations via the accordions mapping `File: path (Lines X-Y)` alongside dynamic syntax coloring and `Relevance %` match likelihood scoring!
