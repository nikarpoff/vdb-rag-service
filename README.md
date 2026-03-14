# RAG-SSW

A personal RAG (Retrieval-Augmented Generation) system for managing your knowledge base with document search and LLM-powered Q&A.

[Русская версия](./README.ru.md)

## Features

- **Document Upload**: Support for PDF, DOC, DOCX, and TXT files
- **Semantic Search**: Find relevant documents using vector similarity
- **Q&A with LLM**: Ask questions and get answers based on your document context
- **Dark Theme UI**: Minimalist, clean interface
- **Docker Deployment**: Easy deployment with Docker Compose

## Architecture

```
Client (React) <-> Server (FastAPI) <-> (OCR + Vector DB)
```

### Components

| Service | Technology | Port |
|---------|------------|------|
| Frontend | React + Vite | 3000 |
| Backend | FastAPI | 8000 |
| Vector DB | Weaviate | 8080 |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- LLM API Key (OpenAI, Anthropic, etc.)

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd rag-ssw
```

2. Configure environment:
```bash
cp server/.env.example server/.env
# Edit server/.env and add your LLM_API_KEY
```

3. Start services:
```bash
docker-compose up --build
```

4. Open in browser:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Weaviate: http://localhost:8080

## Environment Variables

| Variable | Description | Default |
|---------|-------------|---------|
| `LLM_API_KEY` | Your LLM API key | Required |
| `LLM_MODEL` | LLM model name | gpt-4 |
| `WEAVIATE_URL` | Weaviate URL | http://weaviate:8080 |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /v1/documents | Upload document |
| GET | /v1/documents | List documents |
| GET | /v1/documents/{id} | Get document |
| DELETE | /v1/documents/{id} | Delete document |
| GET | /v1/retrieve?q= | Semantic search |
| POST | /v1/chat | Q&A with LLM |

## Development

### Backend
```bash
cd server
uv sync
uvicorn main:app --reload
```

### Frontend
```bash
cd client
npm install
npm run dev
```

## Tech Stack

- **Frontend**: React 18, Vite, Axios
- **Backend**: FastAPI, Python 3.11+
- **Vector DB**: Weaviate
- **OCR**: docling
- **LLM**: LangChain + OpenAI-compatible APIs

## License

MIT
