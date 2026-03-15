from __future__ import annotations

from typing import List, Optional

import httpx
from app.core.config import settings
from app.core.logger import logger
from app.engine.weaviate_client import weaviate_client
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

SYSTEM_PROMPT = """
Ты - ассистент, который отвечает на вопросы пользователя на основе предоставленных документов.
Отвечай на русском языке. Если в контексте нет информации для ответа, честно скажи об этом.
"""


class LLMService:
    def __init__(self):
        self.llm: Optional[ChatOpenAI] = None

    def get_llm(self) -> ChatOpenAI:
        if self.llm is None:
            self.llm = ChatOpenAI(
                model=settings.llm_model or "gpt-4",
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
                temperature=0.2,
            )
            logger.info(f"LLM initialized: {settings.llm_model}")
        return self.llm

    def _call_external_api(self, message: str, context_text: str) -> Optional[str]:
        if not settings.llm_external_endpoint:
            return None

        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {
                    "role": "user",
                    "content": f"Контекст из документов:\n{context_text}\n\nВопрос пользователя: {message}",
                },
            ],
            "temperature": 0.2,
        }

        headers = {"Content-Type": "application/json"}
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"

        try:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                response = client.post(settings.llm_external_endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content")
            )
            if content:
                return content
            logger.warning("External LLM API returned empty content, falling back to LangChain client")
        except Exception as exc:
            logger.warning(f"External LLM API call failed, fallback activated: {exc}")

        return None

    def chat(self, message: str, context: List[str]) -> str:
        context_text = "\n\n".join([f"Document {i + 1}:\n{doc}" for i, doc in enumerate(context)])

        api_response = self._call_external_api(message, context_text)
        if api_response is not None:
            return api_response

        llm = self.get_llm()
        user_prompt = f"""Контекст из документов: {context_text}. Вопрос пользователя: {message}. Ответ:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Ошибка при генерации ответа: {str(e)}"

    def chat_with_retrieval(self, message: str) -> tuple[str, List[str]]:
        try:
            docs = weaviate_client.search(message, limit=5)
            context = [doc.get("content", "") for doc in docs]
            sources = [doc.get("filename", "") for doc in docs]

            if not context:
                return "В базе нет релевантных документов. Загрузите документы для получения ответов.", sources

            response = self.chat(message, context)
            return response, sources
        except Exception as e:
            return f"Ошибка при получении контекста: {str(e)}", []


llm_service = LLMService()
