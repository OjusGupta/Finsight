"""Text splitter configuration for FinSight RAG.

Uses RecursiveCharacterTextSplitter with settings tuned for
mixed markdown/SQL content typical of FinSight documentation.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Chunk size tuned for embedding models (~512 tokens ≈ 1500 chars)
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n## ", "\n### ", "\n---", "\n\n", "\n", " "],
)


def split_documents(documents: list[Document]) -> list[Document]:
    """Split documents into chunks suitable for embedding."""
    return _splitter.split_documents(documents)
