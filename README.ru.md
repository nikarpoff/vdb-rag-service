# RAG-SSW

Персональная RAG-система (Retrieval-Augmented Generation) для управления базой знаний с поиском документов и Q&A на основе LLM.

[English version](./README.md)

## Возможности

- **Загрузка документов**: Поддержка PDF, DOC, DOCX и TXT
- **Семантический поиск**: Поиск документов по векторному сходству
- **Q&A с LLM**: Задавайте вопросы и получайте ответы на основе контекста из документов
- **Тёмная тема**: Минималистичный интерфейс
- **Docker**: Простое развёртывание

## Архитектура

```
Клиент (React) <-> Сервер (FastAPI) <-> (OCR + Векторная БД)
```

### Компоненты

| Сервис | Технология | Порт |
|--------|------------|------|
| Frontend | React + Vite | 3000 |
| Backend | FastAPI | 8000 |
| Vector DB | Weaviate | 8080 |

## Быстрый старт

### Требования

- Docker & Docker Compose
- API ключ LLM (OpenAI, Anthropic и др.)

### Установка

1. Клонируйте репозиторий:
```bash
git clone <repo-url>
cd rag-ssw
```

2. Настройте переменные окружения:
```bash
cp server/.env.example server/.env
# Отредактируйте server/.env и добавьте LLM_API_KEY
```

3. Запустите сервисы:
```bash
docker-compose up --build
```

4. Откройте в браузере:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Weaviate: http://localhost:8080

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `LLM_API_KEY` | API ключ LLM | Обязательно |
| `LLM_MODEL` | Модель LLM | gpt-4 |
| `WEAVIATE_URL` | URL Weaviate | http://weaviate:8080 |

## API Endpoints

| Метод | Эндпоинт | Описание |
|--------|----------|---------|
| POST | /v1/documents | Загрузить документ |
| GET | /v1/documents | Список документов |
| GET | /v1/documents/{id} | Получить документ |
| DELETE | /v1/documents/{id} | Удалить документ |
| GET | /v1/retrieve?q= | Семантический поиск |
| POST | /v1/chat | Q&A с LLM |

## Разработка

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

## Технологии

- **Frontend**: React 18, Vite, Axios
- **Backend**: FastAPI, Python 3.11+
- **Vector DB**: Weaviate
- **OCR**: docling
- **LLM**: LangChain + OpenAI-совместимые API

## Лицензия

MIT
