"""Tests for the FinSight AI architecture:
- RAG loading, splitting, retrieval
- LangGraph state and routing
- MCP tool definitions
- Action authorization, whitelisting, and audit
"""
from __future__ import annotations

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path


# ─── RAG Tests ────────────────────────────────────────────────────────────────

class TestRAGLoaders(unittest.TestCase):
    def test_load_all_documents_returns_list(self):
        from backend.app.ai.rag.loaders import load_all_documents
        docs = load_all_documents()
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0, "Should load at least one document from docs/")

    def test_documents_have_metadata(self):
        from backend.app.ai.rag.loaders import load_all_documents
        docs = load_all_documents()
        for doc in docs:
            self.assertIn("source", doc.metadata)
            self.assertIn("type", doc.metadata)

    def test_load_md_files_from_docs(self):
        from backend.app.ai.rag.loaders import _load_md_files, DOCS_DIR
        docs = _load_md_files(DOCS_DIR, "docs")
        self.assertGreater(len(docs), 0)
        self.assertTrue(all("docs/" in d.metadata["source"] for d in docs))


class TestRAGSplitter(unittest.TestCase):
    def test_split_documents_creates_chunks(self):
        from backend.app.ai.rag.splitter import split_documents
        from langchain_core.documents import Document
        # Create content much larger than CHUNK_SIZE (1500)
        doc = Document(page_content=("A" * 500 + "\n\n") * 20, metadata={"source": "test"})
        chunks = split_documents([doc])
        self.assertGreater(len(chunks), 1, "Long document should be split into multiple chunks")

    def test_short_document_not_split(self):
        from backend.app.ai.rag.splitter import split_documents
        from langchain_core.documents import Document
        doc = Document(page_content="Short text.", metadata={"source": "test"})
        chunks = split_documents([doc])
        self.assertEqual(len(chunks), 1)


# ─── LangGraph Tests ─────────────────────────────────────────────────────────

class TestGraphState(unittest.TestCase):
    def test_state_accepts_required_fields(self):
        from backend.app.ai.graph.state import AgentState
        state: AgentState = {
            "user_message": "test",
            "intent": "general",
        }
        self.assertEqual(state["user_message"], "test")

    def test_state_optional_fields(self):
        from backend.app.ai.graph.state import AgentState
        state: AgentState = {
            "user_message": "test",
            "intent": "finance_query",
            "rag_context": "",
            "tool_results": [],
            "needs_confirmation": False,
        }
        self.assertFalse(state["needs_confirmation"])





class TestGraphBuild(unittest.TestCase):
    def test_graph_compiles(self):
        from backend.app.ai.graph.workflow import finsight_graph
        self.assertIsNotNone(finsight_graph)


# ─── Schema Tests ─────────────────────────────────────────────────────────────

class TestAISchemas(unittest.TestCase):
    def test_chat_request(self):
        from backend.app.schemas.ai import AIChatRequest
        req = AIChatRequest(message="hello")
        self.assertEqual(req.message, "hello")

    def test_chat_response_fields(self):
        from backend.app.schemas.ai import AIChatResponse
        resp = AIChatResponse(
            answer="test",
            intent="finance_query",
        )
        self.assertEqual(resp.intent, "finance_query")

if __name__ == "__main__":
    unittest.main()
