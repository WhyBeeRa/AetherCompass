"""
AetherSearchEngine — Zero-API Local Semantic Search
=====================================================
Pure local cosine similarity search using FastEmbed vectors.
NO Gemini API calls. NO external network requests during search.

Flow:
  1. Receive query → embed locally (~5ms)
  2. Load all tool vectors from SQLite
  3. Cosine similarity + Trust Score weighting
  4. Return top 5 results with match_reason from stored data
"""
import numpy as np
from typing import List, Dict

from persistence import AetherVault
from local_embedder import LocalEmbeddingEngine


class AetherSearchEngine:
    def __init__(self, embedder: LocalEmbeddingEngine, vault: AetherVault):
        self.embedder = embedder
        self.vault = vault

    async def semantic_search(self, query: str) -> List[Dict]:
        """
        Zero-API Semantic Search:
        1. Check if embedder is ready.
        2. Embed query locally via FastEmbed (~5ms).
        3. Cosine similarity against all stored tool vectors.
        4. Weighted ranking: 0.7 * similarity + 0.3 * trust_score.
        5. Return top 5 results with match_reason from stored data
        """
        # 0. CHECK IF ENGINE IS READY
        if not self.embedder.is_ready():
            raise RuntimeError("System initializing")

        # 1. EMBED QUERY LOCALLY
        query_vector = self.embedder.embed(query)
        q_norm = np.linalg.norm(query_vector)

        if q_norm == 0:
            return []

        # 2. LOAD ALL TOOL VECTORS FROM DB
        #    Returns: List[(tool_name, trust_score, vector, analysis_dict)]
        all_tools = self.vault.get_all_embeddings()

        if not all_tools:
            # Fallback to keyword search if no embeddings exist yet
            return self._keyword_fallback(query)

        # 3. COSINE SIMILARITY + TRUST SCORE WEIGHTING
        scored = []
        for tool_name, trust_score, tool_vector, analysis in all_tools:
            t_norm = np.linalg.norm(tool_vector)
            
            if q_norm == 0 or t_norm == 0:
                continue
                
            dot_prod = np.dot(query_vector, tool_vector)
            similarity = float(dot_prod / (q_norm * t_norm))

            # Weighted score: 70% semantic match + 30% trust
            # trust_score is 0-100, normalize to 0-1
            combined_score = 0.7 * similarity + 0.3 * (trust_score / 100.0)

            scored.append((combined_score, similarity, tool_name, trust_score, analysis))

        # 4. SORT & TOP 5
        scored.sort(key=lambda x: x[0], reverse=True)
        top_results = scored[:5]

        # 5. FORMAT RESPONSE (same API contract as before)
        formatted = []
        for combined, sim, tool_name, trust_score, analysis in top_results:
            # Only return tools with meaningful similarity (filter noise)
            if sim < 0.20:
                continue

            slug_id = tool_name.strip().lower().replace(' ', '-')

            # Build match_reason from pre-stored data (no LLM needed)
            summary = analysis.get("executive_summary", "")
            jobs = analysis.get("job_to_be_done", [])
            match_reason = summary if summary else (", ".join(jobs) if jobs else "Semantic match")

            # Primary intent from first job_to_be_done
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
            })

        return formatted

    def _keyword_fallback(self, query: str) -> List[Dict]:
        """
        Fallback when no embeddings exist.
        Uses basic keyword search from the vault.
        """
        results = self.vault.search_tools(query, include_inactive=False)
        fallback = []
        for r in results[:5]:
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
            })
        return fallback
