from langchain_postgres import PGVector
from langchain_core.embeddings import Embeddings
from app.config import get_settings
from app.services.rag.embeddings import get_embeddings

def get_vector_store() -> PGVector:
    settings = get_settings()
    embeddings = get_embeddings()
    
    # Connection string must be sync for some drivers, but async for others?
    # langchain-postgres usually wants a connection string or engine.
    # We use the sync psycopg connection string for simplicity if possible,
    # or the async engine.
    # checking documentation: PGVector in langchain_postgres uses async engine usually.
    
    # We will use the connection string from settings.
    # Note: langchain-postgres might require 'psycopg' (v3) driver in the URL.
    connection_url = str(settings.DATABASE_URL)
    
    # Monkeypatch PGVector to avoid MissingGreenlet error
    # langchain-postgres attempts to sync-create tables in __post_init__
    original_init = PGVector.create_tables_if_not_exists
    PGVector.create_tables_if_not_exists = lambda self: None
    
    try:
        return PGVector(
            embeddings=embeddings,
            collection_name="tickets_vector_store",
            connection=connection_url,
            use_jsonb=True,
            create_extension=False,
        )
    finally:
        PGVector.create_tables_if_not_exists = original_init

