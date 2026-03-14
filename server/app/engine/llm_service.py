from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings
from app.core.logger import logger
from app.engine.weaviate_client import weaviate_client
from typing import List, Optional


SYSTEM_PROMPT = """
Ты - ассистент, который отвечает на вопросы пользователя на основе предоставленных документов.
Отвечай на русском языке. Если в контексте нет информации для ответа, честно скажи об этом
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
                temperature=0.7,
            )
            logger.info(f"LLM initialized: {settings.llm_model}")
        return self.llm
    
    def chat(self, message: str, context: List[str]) -> str:
        """Generate response using LLM with context."""
        llm = self.get_llm()
        
        context_text = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context)])
        
        user_prompt = f"""Контекст из документов: {context_text}. Вопрос пользователя: {message}. Ответ:"""
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Ошибка при генерации ответа: {str(e)}"
    
    def chat_with_retrieval(self, message: str) -> tuple[str, List[str]]:
        """Chat with automatic context retrieval from Weaviate."""
        try:
            # Search for relevant documents
            docs = weaviate_client.search(message, limit=3)
            context = [doc.get("content", "") for doc in docs]
            sources = [doc.get("filename", "") for doc in docs]
            
            if not context:
                return "В базе нет релевантных документов. Загрузите документы для получения ответов.", sources
            
            response = self.chat(message, context)
            return response, sources
        except Exception as e:
            return f"Ошибка при получении контекста: {str(e)}", []


llm_service = LLMService()
