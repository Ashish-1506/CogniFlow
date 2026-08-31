from typing import Any
from uuid import uuid4

import chromadb
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions


class LongTermMemory:
    """Persistent semantic memory backed by a local Chroma collection."""

    def __init__(
        self,
        persist_dir: str,
        embedding_model: str = "all-MiniLM-L6-v2",
        embedding_function: EmbeddingFunction | None = None,
    ):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_function = embedding_function or (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="cogniflow_facts",
            embedding_function=self.embedding_function,
        )

    def store_fact(
        self, user_id: str, fact: str, metadata: dict[str, Any] | None = None
    ) -> None:
        if not fact.strip():
            raise ValueError("fact must not be empty")

        fact_metadata = {"user_id": user_id, **(metadata or {})}
        self.collection.add(
            ids=[str(uuid4())],
            documents=[fact],
            metadatas=[fact_metadata],
        )

    def query_relevant_facts(
        self, user_id: str, query: str, top_k: int = 3
    ) -> list[str]:
        if top_k < 1 or not query.strip():
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"user_id": user_id},
        )
        return results.get("documents", [[]])[0]
