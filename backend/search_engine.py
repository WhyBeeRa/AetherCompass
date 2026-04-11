import os
import json
import asyncio
import numpy as np
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from persistence import AetherVault

SEARCH_SYSTEM_PROMPT = """You are the Aether Semantic Search Engine, an AI expert in matching user needs to AI tools.
Your job is to deeply understand a user's natural language query (intent) and match it against a provided list of AI tools.

You will be given:
1. A user query (the intent).
2. A list of candidate tools with their name, summary, and specific 'jobs to be done'.

Your mission:
- Filter out tools that are NOT relevant to the query.
- Rank the remaining tools by how well they solve the specific problem.
- For each tool, provide a 'match_reason' in HEBREW (עברית) explaining exactly why it fits the user's need.
- Assign a 'relevance_score' (0-100) reflecting the match quality.

You must return a STRICT JSON object matching the provided schema.
Rank results by relevance_score descending. Max 5 tools. If no tools match, return an empty array.
"""

class RankedTool(BaseModel):
    tool_name: str = Field(description="The exact name of the tool provided in the candidates.")
    match_reason: str = Field(description="A short 1-sentence explanation in HEBREW (עברית) of why this tool matches.")
    relevance_score: int = Field(ge=0, le=100, description="Score defining how well the tool matches the intent.")

class SearchEngineResponse(BaseModel):
    results: List[RankedTool]

class AetherSearchEngine:
    def __init__(self):
        # Build client using the new SDK
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model_id = "gemini-2.5-flash"
        self.vault = AetherVault()

    async def _get_embedding(self, text: str) -> List[float]:
        """Fetch the embedding for a given text from Gemini."""
        if not self.client:
            return []
        try:
            # We must use the same model as the one used for indexing (gemini-embedding-001)
            result = self.client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"[SearchEngine] Error generating embedding: {e}")
            return []

    async def semantic_search(self, query: str) -> List[Dict]:
        """
        AI-Powered Hybrid Search:
        1. Fast Keyword/Vector candidate retrieval.
        2. LLM-based Reranking and Reasoning.
        """
        # Fetch all tools from vault (29-31 tools is small enough to handle)
        all_tools = self.vault.search_tools("", include_inactive=False)
        if not all_tools:
            return []

        # 1. RETRIEVE CANDIDATES (Vector Search)
        query_embedding = await self._get_embedding(query)
        candidates = []

        if query_embedding:
            q_vec = np.array(query_embedding)
            q_norm = np.linalg.norm(q_vec)
            
            for t in all_tools:
                emb = t.get("embedding")
                if emb:
                    # Handle potential size mismatch if model changed
                    t_vec = np.array(emb)
                    if t_vec.shape == q_vec.shape:
                        t_norm = np.linalg.norm(t_vec)
                        if q_norm > 0 and t_norm > 0:
                            sim = np.dot(q_vec, t_vec) / (q_norm * t_norm)
                            candidates.append((sim, t))
        
        # Sort by similarity and pick top 15
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_candidates = [c[1] for c in candidates[:15]]
        
        # If no vector match, try keyword search as fallback for candidates
        if not top_candidates:
             top_candidates = self.vault.search_tools(query)[:10]

        if not top_candidates:
            return []

        # 2. RERANK & EXPLAIN (The Gemini Step)
        if not self.client:
            # Fallback if no API key
            return top_candidates[:5]

        # Prepare tools context for the LLM
        tools_context = []
        for t in top_candidates:
            analysis = t.get("analysis", {})
            tools_context.append({
                "name": t["tool_name"],
                "summary": analysis.get("executive_summary", ""),
                "jobs": analysis.get("job_to_be_done", [])
            })

        rerank_prompt = f"""
        USER INTENT: "{query}"
        
        CANDIDATE TOOLS:
        {json.dumps(tools_context, ensure_ascii=False)}
        
        Pick the most relevant tools (max 5) and explain why in Hebrew.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=rerank_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SEARCH_SYSTEM_PROMPT,
                    temperature=0.0,
                    response_mime_type="application/json",
                    response_schema=SearchEngineResponse
                )
            )
            
            ai_results = response.parsed.results
            
            # 3. FINAL MERGE
            final_formatted = []
            # Create a lookup for data from the original tool objects
            tool_lookup = {t["tool_name"].lower(): t for t in top_candidates}
            
            for res in ai_results:
                original_tool = tool_lookup.get(res.tool_name.lower())
                if original_tool:
                    # Update with AI insights
                    original_tool["match_reason"] = res.match_reason
                    original_tool["relevance_score"] = res.relevance_score
                    final_formatted.append(original_tool)
            
            return final_formatted

        except Exception as e:
            print(f"[SearchEngine] Gemini Reranking failed: {e}")
            # Fallback to simple top 5 if LLM fails
            for t in top_candidates[:5]:
                t["match_reason"] = "התאמה נמצאה על בסיס חיפוש סמנטי (ללא הסבר מעמיק)"
                t["relevance_score"] = 70
            return top_candidates[:5]

