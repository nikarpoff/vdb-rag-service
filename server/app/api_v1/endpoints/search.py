from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel
from app.engine.weaviate_client import weaviate_client
from app.core.logger import logger

router = APIRouter(prefix="/retrieve", tags=["Search"])


class SearchResult(BaseModel):
    id: str
    filename: str
    score: float
    excerpt: str


@router.get("", response_model=List[SearchResult])
async def retrieve(query: str = Query(..., description="Search query")):
    try:
        results = weaviate_client.search(query, limit=5)
        
        search_results = []
        for result in results:
            distance = result.get("_distance", 1.0)
            score = max(0, 1 - distance)
            
            search_results.append(SearchResult(
                id=result.get("doc_id", ""),
                filename=result.get("filename", ""),
                score=round(score, 4),
                excerpt=result.get("content", "")[:200] + "..."
            ))
        
        logger.info(f"Search query: '{query}', found {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []
