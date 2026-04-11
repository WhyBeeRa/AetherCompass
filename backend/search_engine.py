import os
import json
import asyncio
import numpy as np
import google.generativeai as genai
from typing import List, Dict
from pydantic import BaseModel

from persistence import AetherVault

SEARCH_SYSTEM_PROMPT = """You are the Aether Semantic Search Engine.
Your job is to deeply understand a user's natural language query (intent) and match it against a provided list of AI tools.
You must not just do keyword matching; you must look at the 'job to be done' and the 'intents_mapped' for each tool.
Rank the tools by how well they solve the user's specific problem.
Take into account the 'trust_score' of the tools if multiple tools match.

You must return a STRICT JSON array of objects.
Each object should have:
- "tool_name": The exact name of the matched tool.
- "match_reason": A short 1-sentence explanation of why this is a good match for the query.
- "relevance_score": A score from 0 to 100 indicating how perfect the match is.

Only return tools that are reasonably relevant. Do not include tools that cannot solve the user's problem.
Return a maximum of 5 tools. If no tools match, return an empty array [].
"""

class RankedTool(BaseModel):
    tool_name: str
    match_reason: str
    relevance_score: int

class SearchEngineResponse(BaseModel):
    results: List[RankedTool]

class AetherSearchEngine:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        # Configure genai explicitly to use GEMINI_API_KEY if present
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SEARCH_SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.1, # Keep it deterministic
                response_mime_type="application/json",
                response_schema=SearchEngineResponse
            )
        )
        self.vault = AetherVault()

    async def _get_embedding(self, text: str) -> List[float]:
        """Fetch the embedding for a given text from Gemini."""
        try:
            # We use gemini-embedding-001 as the stable multilingual model
            result = await asyncio.to_thread(
                genai.embed_content,
                model="models/gemini-embedding-001",
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"[SearchEngine] Error generating embedding: {e}")
            return []

    async def semantic_search(self, query: str) -> List[Dict]:
        """
        Hybrid Search:
        1. Fast Keyword Search (SQLite LIKE)
        2. Vector Semantic Search (Cosine Similarity)
        3. Reciprocal Rank Fusion / Score Combining
        """
        tools = [dict(t) if not isinstance(t, dict) else t for t in self.vault.search_tools("")] # Get all tools for vector search
        if not tools:
            return []

        # FAST PATH: Literal matches (e.g. searching exact names)
        keyword_results = [dict(t) if not isinstance(t, dict) else t for t in self.vault.search_tools(query)]
        keyword_tool_names = {t["tool_name"].lower() for t in keyword_results}
        
        # If the query is very short, just rely on keyword
        if len(keyword_results) > 0 and len(query.split()) <= 2:
            for t in keyword_results:
                 t["match_reason"] = f"התאמה ישירה למילת החיפוש '{query}'"
                 t["relevance_score"] = 90
            keyword_results.sort(key=lambda x: x.get("trust_score", 0), reverse=True)
            return keyword_results[:5]

        # VECTOR SEARCH PATH
        query_embedding = await self._get_embedding(query)
        
        vector_scores = {}
        if query_embedding:
            # Convert query to numpy array
            q_vec = np.array(query_embedding)
            q_norm = np.linalg.norm(q_vec)
            
            if q_norm > 0:
                for t in tools:
                    emb = t.get("embedding") # get_tool / search_tools already parsed this from JSON
                    if emb:
                        t_vec = np.array(emb)
                        t_norm = np.linalg.norm(t_vec)
                        if t_norm > 0:
                            # Cosine Similarity: dot(A, B) / (norm(A) * norm(B))
                            sim = np.dot(q_vec, t_vec) / (q_norm * t_norm)
                            # Convert similarity to a 0-100 score
                            score = int((sim + 1) * 50) # map [-1, 1] to [0, 100]
                            # Boost slightly if it's high similarity
                            score = min(100, int(score * (1 + (sim * 0.2)))) if sim > 0.5 else score
                            vector_scores[t["tool_name"].lower()] = score
                            
        # HYBRID FUSION
        final_scores = []
        for t in tools:
            tool_name_lower = t["tool_name"].lower()
            
            # Base Vector Score (if embedding existed and calculation worked)
            v_score = vector_scores.get(tool_name_lower, 0)
            
            # Base Keyword Score
            k_score = 0
            if tool_name_lower in keyword_tool_names:
                k_score = 60 # Standard keyword match
                # Exact name match gets highest keyword score
                if query.lower() in tool_name_lower or tool_name_lower in query.lower():
                    k_score = 90
            
            # Combine - we take the max of either, plus a small bump if BOTH hit
            final_score = max(v_score, k_score)
            if v_score > 60 and k_score > 0:
                 final_score = min(100, final_score + 10)
                 
            # Add Trust Score signal (very small influence: 0-5 points max)
            trust_bump = (t.get("trust_score", 0) / 100.0) * 5
            final_score = min(100, int(final_score + trust_bump))
                 
            if final_score > 65: # Threshold for relevance
                final_scores.append((final_score, t))
                
        # Sort by final hybrid score
        final_scores.sort(key=lambda x: x[0], reverse=True)
        top_results = final_scores[:5]
        
        # Format the return objects
        formatted_results = []
        for score, t in top_results:
             # If we relied solely on keyword, update the reason
             if score == k_score and v_score < 60:
                 reason = f"התאמה נמצאה על בסיס מילות מפתח ('{query}')"
             else:
                 # It's a semantic vector match
                 reason = "התאמה נמצאה על בסיס חיפוש סמנטי (וקטורי) לכוונתך"
                 
                 # Try to find a better specific reason from the tool's intents
                 analysis = t.get("analysis", {})
                 intents = analysis.get("intents_mapped", [])
                 for intent in intents:
                      desc = intent.get("intent_description", "")
                      # If the vector algorithm matched highly, the primary intent is usually why
                      if desc:
                           reason = f"התאמה מדויקת לכוונת: {desc}"
                           break
                           
             t["match_reason"] = reason
             t["relevance_score"] = score
             formatted_results.append(t)
             
        # FALLBACK: If hybrid search found literally nothing, return at least keyword search again if available
        if not formatted_results and keyword_results:
             for t in keyword_results:
                 t["match_reason"] = "התאמה מהירה (לא נמצאה התאמה סמנטית מדויקת)"
                 t["relevance_score"] = 50
             keyword_results.sort(key=lambda x: x.get("trust_score", 0), reverse=True)
             return keyword_results[:5]

        return formatted_results
