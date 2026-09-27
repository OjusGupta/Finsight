"""Document loaders for FinSight RAG.

Loads project documentation, database schema docs, finance engine docs,
and API documentation into LangChain Document objects for indexing.
"""
from pathlib import Path
from langchain_core.documents import Document


# Directories containing FinSight knowledge
DOCS_DIR = Path(__file__).resolve().parents[4] / "docs"
DB_SCHEMA_DIR = Path(__file__).resolve().parents[4] / "database" / "schema"
DB_QUERIES_DIR = Path(__file__).resolve().parents[4] / "database" / "queries"


def _load_md_files(directory: Path, source_prefix: str) -> list[Document]:
    """Load all .md files from a directory into Documents."""
    docs = []
    if not directory.exists():
        return docs
    for fp in sorted(directory.glob("*.md")):
        text = fp.read_text(encoding="utf-8", errors="ignore")
        if text.strip():
            docs.append(Document(
                page_content=text,
                metadata={
                    "source": f"{source_prefix}/{fp.name}",
                    "file_name": fp.name,
                    "type": "documentation",
                },
            ))
    return docs


def _load_sql_files(directory: Path, source_prefix: str) -> list[Document]:
    """Load SQL schema/query files as reference documents."""
    docs = []
    if not directory.exists():
        return docs
    for fp in sorted(directory.glob("*.sql")):
        text = fp.read_text(encoding="utf-8", errors="ignore")
        if text.strip():
            docs.append(Document(
                page_content=text,
                metadata={
                    "source": f"{source_prefix}/{fp.name}",
                    "file_name": fp.name,
                    "type": "sql_schema",
                },
            ))
    return docs


def load_all_documents() -> list[Document]:
    """Load all FinSight knowledge documents for RAG indexing.

    Sources:
    - docs/*.md  — project documentation (architecture, design, reconciliation, etc.)
    - database/schema/*.sql  — PostgreSQL schema definitions
    - database/queries/*.sql  — analytical SQL queries
    """
    documents = []
    documents.extend(_load_md_files(DOCS_DIR, "docs"))
    documents.extend(_load_sql_files(DB_SCHEMA_DIR, "database/schema"))
    documents.extend(_load_sql_files(DB_QUERIES_DIR, "database/queries"))
    return documents
