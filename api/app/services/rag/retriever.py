from typing import List
from langchain_core.documents import Document
from app.services.rag.store import get_vector_store

async def search_similar_tickets(
    query: str, 
    organization_id: str, 
    limit: int = 5
) -> List[Document]:
    """
    Search for similar tickets within the organization.
    """
    store = get_vector_store()
    
    # Filter by organization_id in metadata
    # PGVector supports filter args
    filter_dict = {"organization_id": organization_id}
    
    # Async similarity search
    docs = await store.asimilarity_search(
        query, 
        k=limit,
        filter=filter_dict
    )
    
    return docs
