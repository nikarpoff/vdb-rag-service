import weaviate
from app.core.config import settings
from app.core.logger import logger
from typing import List, Optional


class WeaviateService:
    def __init__(self):
        self.client: Optional[weaviate.Client] = None
        self._schema_created = False
    
    def connect(self) -> weaviate.Client:
        if self.client is None:
            self.client = weaviate.Client(
                url=settings.weaviate_url,
                additional_headers={
                    "X-OpenAI-Api-Key": settings.llm_api_key
                } if settings.llm_api_key else {}
            )
            logger.info(f"Connected to Weaviate at {settings.weaviate_url}")
        return self.client
    
    def create_schema(self):
        """Create documents schema if not exists."""
        if self._schema_created:
            return
        
        client = self.connect()
        
        if not client.schema.exists("Document"):
            client.schema.create_class({
                "class": "Document",
                "description": "Document for RAG system",
                "vectorizer": "text2vec-transformers",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "vectorizeClassName": False
                    }
                },
                "properties": [
                    {
                        "name": "doc_id",
                        "dataType": ["text"],
                        "description": "Document ID"
                    },
                    {
                        "name": "filename",
                        "dataType": ["text"],
                        "description": "Filename"
                    },
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Document content"
                    },
                    {
                        "name": "content_type",
                        "dataType": ["text"],
                        "description": "MIME type"
                    }
                ]
            })
            self._schema_created = True
    
    def add_document(self, doc_id: str, filename: str, content: str, content_type: str):
        """Add document to Weaviate."""
        client = self.connect()
        self.create_schema()
        
        client.data_object.create(
            class_name="Document",
            data_object={
                "doc_id": doc_id,
                "filename": filename,
                "content": content,
                "content_type": content_type
            }
        )
    
    def search(self, query: str, limit: int = 5) -> List[dict]:
        """Search documents by query."""
        client = self.connect()
        self.create_schema()
        
        results = client.query.get(
            "Document",
            ["doc_id", "filename", "content"]
        ).with_near_text({
            "concepts": [query]
        }).with_limit(limit).with_additional(["distance", "certainty"]).do()
        
        documents = results.get("data", {}).get("Get", {}).get("Document", [])
        
        return [
            {
                "doc_id": doc.get("doc_id", ""),
                "filename": doc.get("filename", ""),
                "content": doc.get("content", ""),
                "_distance": doc.get("_additional", {}).get("distance", 1.0),
            }
            for doc in documents
        ]
    
    def delete_document(self, doc_id: str):
        """Delete document by doc_id."""
        client = self.connect()
        
        results = client.query.get(
            "Document",
            ["id"]
        ).with_where({
            "path": ["doc_id"],
            "operator": "Equal",
            "valueText": doc_id
        }).do()
        
        objects = results.get("data", {}).get("Get", {}).get("Document", [])
        for obj in objects:
            client.data_object.delete(obj["id"])


weaviate_client = WeaviateService()
