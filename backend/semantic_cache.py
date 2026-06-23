import numpy as np
from typing import Optional, Dict
from persistence import AetherVault
from local_embedder import LocalEmbeddingEngine

class AetherSemanticCache:
    def __init__(self, embedder: LocalEmbeddingEngine, vault: AetherVault, similarity_threshold: float = 0.85):
        self.embedder = embedder
        self.vault = vault
        self.similarity_threshold = similarity_threshold

    def check_cache(self, query: str) -> Optional[Dict]:
        """
        Checks if the query has a semantically similar match in the cache
        that maps to an approved (is_active = 1) tool.
        Returns the tool details if found, otherwise None.
        """
        # 1. Embed query
        query_vector = self.embedder.embed(query)
        q_norm = np.linalg.norm(query_vector)
        if q_norm == 0:
            return None

        # 2. Get all cache entries
        cache_entries = self.vault.get_all_semantic_cache()
        if not cache_entries:
            return None

        # 3. Find closest semantically
        best_similarity = -1.0
        best_tool_name = None
        best_query = None

        for cached_query, cached_vector, tool_name in cache_entries:
            c_norm = np.linalg.norm(cached_vector)
            if c_norm == 0:
                continue
            similarity = float(np.dot(query_vector, cached_vector) / (q_norm * c_norm))
            if similarity > best_similarity:
                best_similarity = similarity
                best_tool_name = tool_name
                best_query = cached_query

        print(f"[Semantic Cache] Best match for '{query}': '{best_query}' with similarity {best_similarity:.4f}")

        # 4. Check if it meets the threshold
        if best_similarity >= self.similarity_threshold and best_tool_name:
            # Check if the tool is approved (active)
            tool_data = self.vault.get_tool(best_tool_name)
            if tool_data and tool_data.get("is_active"):
                print(f"[Semantic Cache] HIT! Bypassing agents and returning cached tool '{best_tool_name}'.")
                return tool_data
            else:
                print(f"[Semantic Cache] Match found ('{best_tool_name}') but tool is not active/approved.")
        
        return None

    def save_cache(self, query: str, tool_name: str):
        """
        Saves a query to the cache, generating its embedding.
        """
        try:
            embedding_bytes = self.embedder.embed_to_bytes(query)
            self.vault.save_semantic_cache(query, embedding_bytes, tool_name)
        except Exception as e:
            print(f"[Semantic Cache Error] Failed to save query cache: {e}")
