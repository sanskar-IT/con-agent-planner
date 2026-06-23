"""
Backward compatibility re-export.

The canonical RAGRetriever now lives in retrieval.rag_retriever.
This module re-exports everything for existing imports.
"""

from retrieval.rag_retriever import RAGRetriever, RAG_CACHE  # noqa: F401
