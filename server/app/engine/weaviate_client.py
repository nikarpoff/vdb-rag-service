from __future__ import annotations

import uuid
from typing import List, Optional

import weaviate
from app.core.config import settings
from app.core.logger import logger
from app.engine.embedding_service import get_embedding_service


class WeaviateService:
    def __init__(self) -> None:
        self.client = None
        self._schema_created = False
        self._embedding_service = get_embedding_service()

    def connect(self):
        if self.client is not None:
            return self.client

        if hasattr(weaviate, "connect_to_custom"):
            host, http_port = self._parse_host_port(settings.weaviate_url, 8080)
            grpc_host, grpc_port = self._parse_host_port(f"http://{settings.weaviate_grpc_url}", 50051)
            self.client = weaviate.connect_to_custom(
                http_host=host,
                http_port=http_port,
                http_secure=False,
                grpc_host=grpc_host,
                grpc_port=grpc_port,
                grpc_secure=False,
                headers={"X-OpenAI-Api-Key": settings.llm_api_key} if settings.llm_api_key else None,
            )
        else:
            self.client = weaviate.Client(
                url=settings.weaviate_url,
                additional_headers={"X-OpenAI-Api-Key": settings.llm_api_key} if settings.llm_api_key else {},
            )

        logger.info(f"Connected to Weaviate at {settings.weaviate_url}")
        return self.client

    @staticmethod
    def _parse_host_port(url: str, default_port: int) -> tuple[str, int]:
        clean = url.replace("https://", "").replace("http://", "")
        if ":" in clean:
            host, port = clean.rsplit(":", 1)
            return host, int(port)
        return clean, default_port

    def create_schema(self) -> None:
        if self._schema_created:
            return

        client = self.connect()

        if hasattr(client, "collections"):
            exists = client.collections.exists("DocumentChunk")
            if not exists:
                client.collections.create(
                    name="DocumentChunk",
                    description="Chunked documents for RAG search",
                    vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),
                    properties=[
                        weaviate.classes.config.Property(name="doc_id", data_type=weaviate.classes.config.DataType.TEXT),
                        weaviate.classes.config.Property(name="filename", data_type=weaviate.classes.config.DataType.TEXT),
                        weaviate.classes.config.Property(name="chunk_id", data_type=weaviate.classes.config.DataType.INT),
                        weaviate.classes.config.Property(name="content", data_type=weaviate.classes.config.DataType.TEXT),
                        weaviate.classes.config.Property(name="content_type", data_type=weaviate.classes.config.DataType.TEXT),
                    ],
                )
        else:
            if not client.schema.exists("DocumentChunk"):
                client.schema.create_class(
                    {
                        "class": "DocumentChunk",
                        "description": "Chunked documents for RAG search",
                        "vectorizer": "none",
                        "properties": [
                            {"name": "doc_id", "dataType": ["text"]},
                            {"name": "filename", "dataType": ["text"]},
                            {"name": "chunk_id", "dataType": ["int"]},
                            {"name": "content", "dataType": ["text"]},
                            {"name": "content_type", "dataType": ["text"]},
                        ],
                    }
                )

        self._schema_created = True

    def add_document_chunks(self, doc_id: str, filename: str, content_type: str, chunks: List[str]) -> int:
        self.create_schema()
        client = self.connect()

        vectors = self._embedding_service.embed_many(chunks)

        if hasattr(client, "collections"):
            collection = client.collections.get("DocumentChunk")
            with collection.batch.dynamic() as batch:
                for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
                    batch.add_object(
                        properties={
                            "doc_id": doc_id,
                            "filename": filename,
                            "chunk_id": idx,
                            "content": chunk,
                            "content_type": content_type,
                        },
                        vector=vector,
                        uuid=str(uuid.uuid4()),
                    )
        else:
            for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
                client.data_object.create(
                    class_name="DocumentChunk",
                    data_object={
                        "doc_id": doc_id,
                        "filename": filename,
                        "chunk_id": idx,
                        "content": chunk,
                        "content_type": content_type,
                    },
                    vector=vector,
                )

        return len(chunks)

    def search(self, query: str, limit: int = 5) -> List[dict]:
        self.create_schema()
        client = self.connect()
        query_vector = self._embedding_service.embed(query)

        if hasattr(client, "collections"):
            collection = client.collections.get("DocumentChunk")
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_properties=["doc_id", "filename", "content", "chunk_id"],
                return_metadata=["distance"],
            )
            return [
                {
                    "doc_id": obj.properties.get("doc_id", ""),
                    "filename": obj.properties.get("filename", ""),
                    "content": obj.properties.get("content", ""),
                    "chunk_id": obj.properties.get("chunk_id", -1),
                    "_distance": obj.metadata.distance if obj.metadata else 1.0,
                }
                for obj in response.objects
            ]

        results = (
            client.query.get("DocumentChunk", ["doc_id", "filename", "content", "chunk_id"])
            .with_near_vector({"vector": query_vector})
            .with_limit(limit)
            .with_additional(["distance"])
            .do()
        )
        documents = results.get("data", {}).get("Get", {}).get("DocumentChunk", [])
        return [
            {
                "doc_id": doc.get("doc_id", ""),
                "filename": doc.get("filename", ""),
                "content": doc.get("content", ""),
                "chunk_id": doc.get("chunk_id", -1),
                "_distance": doc.get("_additional", {}).get("distance", 1.0),
            }
            for doc in documents
        ]

    def delete_document(self, doc_id: str) -> None:
        client = self.connect()
        self.create_schema()

        if hasattr(client, "collections"):
            collection = client.collections.get("DocumentChunk")
            collection.data.delete_many(
                where=weaviate.classes.query.Filter.by_property("doc_id").equal(doc_id)
            )
            return

        result = (
            client.query.get("DocumentChunk", ["_additional { id }"])
            .with_where({"path": ["doc_id"], "operator": "Equal", "valueText": doc_id})
            .do()
        )
        objs = result.get("data", {}).get("Get", {}).get("DocumentChunk", [])
        for obj in objs:
            obj_id = obj.get("_additional", {}).get("id")
            if obj_id:
                client.data_object.delete(uuid=obj_id, class_name="DocumentChunk")


weaviate_client = WeaviateService()
