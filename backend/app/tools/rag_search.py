"""RAG search tool — callable from LangGraph tool-calling in a future step."""

from app.rag.retriever import KnowledgeRetriever
from app.schemas.knowledge import KnowledgeSearchHit


def rag_search_tool(
    retriever: KnowledgeRetriever,
    query: str,
    top_k: int = 5,
) -> list[KnowledgeSearchHit]:
    return retriever.search(query, top_k)
