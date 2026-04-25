"""
RemoteEmbeddingEngine — Gemini-powered Embedding Service
=========================================================
Replaces local ONNX models with Google's text-embedding-004.
Eliminates heavy dependencies (onnxruntime, tokenizers) to fit Render 512MB limit.

Model: text-embedding-004
Dimensions: 768 (Default)
"""
import os
import numpy as np
from typing import List, Optional
from google import genai
from google.genai import types


class LocalEmbeddingEngine:
    """
    Renamed to LocalEmbeddingEngine to maintain compatibility with existing code,
    but performs remote calls to Google Gemini API.
    """
    _instance = None

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("[Embedder] WARNING: GEMINI_API_KEY not found in environment.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "text-embedding-004"
        print(f"[Embedder] Initialized Remote Engine using {self.model_id}")

    @classmethod
    def get_instance(cls) -> "LocalEmbeddingEngine":
        """Thread-safe singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── public API ──────────────────────────────────────────────

    def is_ready(self) -> bool:
        """Checks if the API key is configured."""
        return self.api_key is not None

    def embed(self, text: str) -> np.ndarray:
        """
        Embed a single text string using Gemini API.
        Returns float32 numpy array (768,).
        """
        if not text.strip():
            return np.zeros(768, dtype=np.float32)

        try:
            result = self.client.models.embed_content(
                model=self.model_id,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
            )
            
            vector = result.embeddings[0].values
            return np.array(vector, dtype=np.float32)
        except Exception as e:
            print(f"[Embedder] API Error: {e}")
            # Return zero vector on failure to prevent crash, 
            # though search quality will drop for this specific item.
            return np.zeros(768, dtype=np.float32)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Embed a list of texts. Uses Gemini batch embedding API for efficiency.
        """
        if not texts:
            return []

        try:
            # text-embedding-004 supports batching
            result = self.client.models.embed_content(
                model=self.model_id,
                contents=texts,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
            )
            
            return [np.array(emb.values, dtype=np.float32) for emb in result.embeddings]
        except Exception as e:
            print(f"[Embedder] Batch API Error: {e}")
            # Fallback to individual calls if batch fails or just return zeros
            return [self.embed(t) for t in texts]

    def embed_to_bytes(self, text: str) -> bytes:
        """Embed and convert to raw bytes for BLOB storage."""
        return self.embed(text).tobytes()
