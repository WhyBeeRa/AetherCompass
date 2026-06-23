"""
AetherSearchEngine — Production-ready Database Vector Search
=====================================================
Semantic search powered by PostgreSQL + pgvector.
Runs search, filtering, and combined-score ranking entirely in the database.
"""
import numpy as np
import json
import psycopg2
import psycopg2.extras
from typing import List, Dict

from persistence import AetherVault
from local_embedder import LocalEmbeddingEngine


class AetherSearchEngine:
    def __init__(self, embedder: LocalEmbeddingEngine, vault: AetherVault):
        self.embedder = embedder
        self.vault = vault

    async def semantic_search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Production Vector Search:
        1. Check if embedder is ready.
        2. Embed query via Gemini Remote Embeddings API.
        3. Query PostgreSQL using the cosine distance operator <=> and combined score logic in SQL.
        4. Return top results.
        """
        # 0. CHECK IF ENGINE IS READY
        if not self.embedder.is_ready():
            raise RuntimeError("System initializing")

        # 1. EMBED QUERY
        query_vector = self.embedder.embed(query)
        if query_vector is None or len(query_vector) == 0 or np.linalg.norm(query_vector) == 0:
            return []

        # Convert to list for pgvector parameter passing
        query_list = query_vector.tolist()

        # 2. RUN VECTOR SIMILARITY QUERY DIRECTLY IN POSTGRES
        conn = self.vault._get_conn()
        c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # Cosine similarity = 1 - cosine distance (operator <=>)
            # Combined score: 70% similarity + 30% normalized trust score
            c.execute("""
                SELECT tool_name, trust_score, analysis_json, is_active,
                       (1 - (embedding <=> %s::vector)) as similarity,
                       (0.7 * (1 - (embedding <=> %s::vector)) + 0.3 * (trust_score / 100.0)) as combined_score
                FROM verified_tools
                WHERE is_active = 1 AND embedding IS NOT NULL AND (1 - (embedding <=> %s::vector)) >= 0.20
                ORDER BY combined_score DESC
                LIMIT %s
            """, (query_list, query_list, query_list, limit))
            rows = c.fetchall()
        except Exception as e:
            print(f"[Search Engine] DB error during vector search: {e}")
            rows = []
        finally:
            conn.close()

        if not rows:
            # Fallback to keyword search if no results found or DB error/no vectors
            return self._keyword_fallback(query, limit)

        # 3. FORMAT RESPONSE
        formatted = []
        for row in rows:
            tool_name = row['tool_name']
            trust_score = row['trust_score']
            analysis_json = row['analysis_json']
            analysis = json.loads(analysis_json) if analysis_json else {}
            sim = row['similarity']
            combined = row['combined_score']
            is_active = row['is_active']

            slug_id = tool_name.strip().lower().replace(' ', '-')
            summary = analysis.get("executive_summary", "")
            jobs = analysis.get("job_to_be_done", [])
            match_reason = summary if summary else (", ".join(jobs) if jobs else "Semantic match")
            primary_intent = jobs[0] if jobs else "AI Tool"

            formatted.append({
                "id": slug_id,
                "tool_name": tool_name,
                "title": tool_name.title(),
                "trust_score": trust_score,
                "analysis": analysis,
                "match_reason": match_reason,
                "primary_intent": primary_intent,
                "relevance_score": int(combined * 100),
                "similarity": round(sim, 4),
                "metrics": analysis.get("metrics", {}),
                "summary": summary,
                "is_active": is_active
            })

        return formatted

    def _keyword_fallback(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Fallback when no embeddings exist.
        Uses basic keyword search from the vault.
        """
        results = self.vault.search_tools(query, include_inactive=False)
        fallback = []
        for r in results[:limit]:
            analysis = r.get("analysis", {})
            summary = analysis.get("executive_summary", "")
            if not summary and not analysis.get("job_to_be_done"):
                continue
            if "Seeded from Data Ingestion" in summary:
                continue

            jobs = analysis.get("job_to_be_done", [])
            fallback.append({
                "id": r.get("id", ""),
                "tool_name": r["tool_name"],
                "title": r["tool_name"].title(),
                "trust_score": r.get("trust_score", 0),
                "analysis": analysis,
                "match_reason": summary or "Match found based on keyword search",
                "primary_intent": jobs[0] if jobs else "AI Tool",
                "relevance_score": 60,
                "similarity": 0.0,
                "metrics": analysis.get("metrics", {}),
                "summary": summary,
                "is_active": r.get("is_active", True)
            })
        return fallback
