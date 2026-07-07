"""
graph_store.py
--------------
Handles:
  1. Local Ollama (llama3.1:8b) initialization for zero-cost text -> graph extraction.
  2. LangChain's LLMGraphTransformer to turn raw research text chunks into
     graph Nodes / Relationships.
  3. A resilient connection to a remote Neo4j AuraDB instance, including the
     hard-won fixes for Aura Free Tier + local Windows SSL quirks.

Historical bottlenecks resolved here (do not "simplify" these away):
  - Neo4j connections using the plain "neo4j://" or "bolt://" scheme fail on
    some local Windows setups due to SSL handshake blocks. We MUST use the
    "neo4j+ssc://" scheme (SSL with self-signed-cert tolerance) instead.
  - Aura Free Tier instances are not always reachable on the default database
    name. Leaving `database` unset causes intermittent `DatabaseNotFound`
    errors during cold starts. We explicitly target the unique database id.
"""

import os
import logging
from typing import List, Optional

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from langchain_ollama import ChatOllama
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_neo4j import Neo4jGraph

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+ssc://fa59faf1.databases.neo4j.io")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# CRITICAL: This must stay pinned to the real Aura database id ("fa59faf1"),
# NOT "neo4j" (the default), or Aura Free Tier cold-starts will throw
# DatabaseNotFound errors intermittently.
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "fa59faf1")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def _validate_uri_scheme(uri: str) -> None:
    """Guard rail: fail loudly (not silently) if someone reverts the scheme."""
    if not uri.startswith("neo4j+ssc://") and not uri.startswith("bolt+ssc://"):
        logger.warning(
            "NEO4J_URI does not use the '+ssc' SSL scheme. "
            "On Windows this has historically caused SSL handshake failures. "
            "Expected something like 'neo4j+ssc://<db-id>.databases.neo4j.io'."
        )


class GraphStore:
    """
    Wraps a Neo4j AuraDB connection and a local Ollama-backed graph transformer.
    """

    def __init__(
        self,
        uri: str = NEO4J_URI,
        username: str = NEO4J_USERNAME,
        password: Optional[str] = NEO4J_PASSWORD,
        database: str = NEO4J_DATABASE,
        ollama_model: str = OLLAMA_MODEL,
        ollama_base_url: str = OLLAMA_BASE_URL,
    ):
        _validate_uri_scheme(uri)

        if not password:
            raise ValueError(
                "NEO4J_PASSWORD is not set. Populate your .env file before "
                "instantiating GraphStore."
            )

        self.uri = uri
        self.username = username
        self.password = password
        self.database = database

        # --- Local, zero-cost LLM for graph entity/relationship extraction ---
        self.llm = ChatOllama(
            model=ollama_model,
            base_url=ollama_base_url,
            temperature=0,
        )

        self.graph_transformer = LLMGraphTransformer(llm=self.llm)

        # --- Cloud graph store handle (LangChain wrapper) ---
        self.graph = Neo4jGraph(
            url=self.uri,
            username=self.username,
            password=self.password,
            database=self.database,
        )

        # --- Raw driver kept around for health checks / manual queries ---
        self._driver = GraphDatabase.driver(
            self.uri, auth=(self.username, self.password)
        )

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    def verify_connectivity(self) -> bool:
        """Pings the Aura instance. Returns True if reachable."""
        try:
            self._driver.verify_connectivity()
            logger.info("Neo4j AuraDB connection verified (db=%s).", self.database)
            return True
        except (ServiceUnavailable, AuthError) as exc:
            logger.error("Neo4j connectivity check failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Extraction pipeline
    # ------------------------------------------------------------------
    def extract_graph_from_chunks(self, text_chunks: List[str]) -> List:
        """
        Feeds raw research-paper text chunks into the local Ollama model via
        LLMGraphTransformer to extract (node, relationship) graph documents.

        This step is intentionally run locally (zero token/API cost) since
        research papers are dense and would otherwise consume large cloud
        token budgets and hit TPM/RPM rate limits.
        """
        documents = [Document(page_content=chunk) for chunk in text_chunks if chunk.strip()]

        if not documents:
            logger.warning("No non-empty text chunks provided for graph extraction.")
            return []

        logger.info("Extracting graph data from %d chunk(s) via local Ollama...", len(documents))
        graph_documents = self.graph_transformer.convert_to_graph_documents(documents)
        return graph_documents

    def push_to_neo4j(self, graph_documents: List) -> None:
        """Streams extracted GraphDocuments directly into the Aura cloud instance."""
        if not graph_documents:
            logger.info("Nothing to push — graph_documents list is empty.")
            return

        self.graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,
            include_source=True,
        )
        logger.info("Pushed %d graph document(s) to Neo4j Aura.", len(graph_documents))

    def run_pipeline(self, text_chunks: List[str]) -> List:
        """Convenience wrapper: extract locally, then push to the cloud graph."""
        graph_documents = self.extract_graph_from_chunks(text_chunks)
        self.push_to_neo4j(graph_documents)
        return graph_documents

    def close(self) -> None:
        self._driver.close()


if __name__ == "__main__":
    # Simple smoke test when running this file directly.
    store = GraphStore()
    ok = store.verify_connectivity()
    print(f"Neo4j Aura reachable: {ok}")
    store.close()