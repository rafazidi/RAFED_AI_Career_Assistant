from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings


class RAGService:
    """Small local RAG index using Sentence Transformers + ChromaDB."""

    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None
        self._client = chromadb.PersistentClient(path=str(settings.absolute_chroma_dir))
        self._collection = self._client.get_or_create_collection(
            name="rafed_profile",
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    def index_documents(self, documents: list[dict[str, str]]) -> int:
        if not documents:
            return 0

        ids = [item["id"] for item in documents]
        texts = [item["text"] for item in documents]
        metadatas = [
            {
                "filename": item["filename"],
                "source": item.get("source", "profile"),
            }
            for item in documents
        ]
        embeddings = self.model.encode(texts, normalize_embeddings=True).tolist()

        # Replace matching IDs so re-indexing an edited file updates its chunks.
        self._collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return len(documents)

    def replace_source_documents(
        self, source: str, documents: list[dict[str, str]]
    ) -> int:
        existing = self._collection.get(
            where={"source": source},
            include=["metadatas"],
        )
        existing_ids = set(existing.get("ids") or [])

        if documents:
            ids = [item["id"] for item in documents]
            texts = [item["text"] for item in documents]
            metadatas = [
                {"filename": item["filename"], "source": source}
                for item in documents
            ]
            embeddings = self.model.encode(texts, normalize_embeddings=True).tolist()
            self._collection.upsert(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings,
            )
            existing_ids.difference_update(ids)

        if existing_ids:
            self._collection.delete(ids=list(existing_ids))
        return len(documents)

    def search(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        if self._collection.count() == 0:
            return []

        embedding = self.model.encode([query], normalize_embeddings=True).tolist()
        result = self._collection.query(
            query_embeddings=embedding,
            n_results=min(top_k or settings.top_k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        matches: list[dict[str, Any]] = []
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        for doc, meta in zip(docs, metas):
            matches.append({
                "text": doc or "",
                "filename": (meta or {}).get("filename", "document"),
            })
        return matches


rag_service = RAGService()


def split_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    """Simple character-based chunker; keeps this starter project easy to inspect."""
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        if end < len(cleaned):
            boundary = cleaned.rfind("\n", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return chunks


def load_knowledge_documents(folder: Path) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    for path in sorted(folder.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        for index, chunk in enumerate(split_text(content)):
            documents.append({
                "id": f"{path.stem}-{index}",
                "filename": path.name,
                "text": chunk,
            })
    return documents
