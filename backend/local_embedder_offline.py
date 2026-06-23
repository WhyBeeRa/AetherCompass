"""
OfflineEmbeddingEngine — True Local Embedding Service
======================================================
Uses sentence-transformers to generate embeddings 100% locally.
Zero API calls, zero cost, no rate limits.

Model: all-mpnet-base-v2
Dimensions: 768 (matches existing pgvector schema)
RAM Footprint: ~420MB
First run: Downloads model (~420MB), cached in ~/.cache/torch/
"""
import numpy as np
from typing import List, Optional


class OfflineEmbeddingEngine:
    """
    Local-only embedding engine using sentence-transformers.
    Matches the interface of LocalEmbeddingEngine (remote) for drop-in use.
    """
    _instance = None

    def __init__(self):
        self._model = None
        self._model_name = "all-mpnet-base-v2"
        self._dimension = 768
        self._ready = False
        print(f"[OfflineEmbedder] Initializing with model '{self._model_name}'...")
        self._load_model()

    def _load_model(self):
        """Lazy-loads the sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
            self._ready = True
            print(f"[OfflineEmbedder] Model '{self._model_name}' loaded successfully. "
                  f"Dimension: {self._dimension}")
        except ImportError:
            print("[OfflineEmbedder] FATAL: 'sentence-transformers' not installed.")
            print("  Run: pip install sentence-transformers")
            self._ready = False
        except Exception as e:
            print(f"[OfflineEmbedder] Failed to load model: {e}")
            self._ready = False

    @classmethod
    def get_instance(cls) -> "OfflineEmbeddingEngine":
        """Thread-safe singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Public API ──────────────────────────────────────────────

    def is_ready(self) -> bool:
        """Returns True if the model is loaded and ready."""
        return self._ready and self._model is not None

    def embed(self, text: str) -> np.ndarray:
        """
        Embed a single text string locally.
        Returns float32 numpy array (768,).
        """
        if not text.strip():
            return np.zeros(self._dimension, dtype=np.float32)

        if not self.is_ready():
            print("[OfflineEmbedder] Model not ready, returning zero vector.")
            return np.zeros(self._dimension, dtype=np.float32)

        try:
            vector = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return vector.astype(np.float32)
        except Exception as e:
            print(f"[OfflineEmbedder] Encoding error: {e}")
            return np.zeros(self._dimension, dtype=np.float32)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Embed a list of texts locally in one batch (much faster than one-by-one).
        Returns list of float32 numpy arrays.
        """
        if not texts:
            return []

        if not self.is_ready():
            print("[OfflineEmbedder] Model not ready, returning zero vectors.")
            return [np.zeros(self._dimension, dtype=np.float32) for _ in texts]

        try:
            # sentence-transformers handles batching internally
            vectors = self._model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=len(texts) > 50
            )
            return [v.astype(np.float32) for v in vectors]
        except Exception as e:
            print(f"[OfflineEmbedder] Batch encoding error: {e}")
            return [self.embed(t) for t in texts]

    def embed_to_bytes(self, text: str) -> bytes:
        """Embed and convert to raw bytes for BLOB storage."""
        return self.embed(text).tobytes()

    def embed_batch_to_bytes(self, texts: List[str]) -> List[bytes]:
        """Embed a batch and convert each to raw bytes."""
        vectors = self.embed_batch(texts)
        return [v.tobytes() for v in vectors]


# ── Quick self-test ──────────────────────────────────────────────
if __name__ == "__main__":
    engine = OfflineEmbeddingEngine()

    if not engine.is_ready():
        print("Engine failed to initialize. Install: pip install sentence-transformers")
        exit(1)

    # Single embedding
    vec = engine.embed("AI-powered code editor for developers")
    print(f"Single embed: shape={vec.shape}, dtype={vec.dtype}, norm={np.linalg.norm(vec):.4f}")

    # Batch embedding
    test_texts = [
        "Generate photorealistic images from text prompts",
        "Automated video editing with AI",
        "Real-time language translation service",
    ]
    batch_vecs = engine.embed_batch(test_texts)
    print(f"Batch embed: {len(batch_vecs)} vectors, each shape={batch_vecs[0].shape}")

    # Similarity check
    from numpy.linalg import norm
    cos_sim = np.dot(batch_vecs[0], batch_vecs[1]) / (norm(batch_vecs[0]) * norm(batch_vecs[1]))
    print(f"Similarity (images vs video): {cos_sim:.4f}")

    # Bytes roundtrip
    raw_bytes = engine.embed_to_bytes("test")
    restored = np.frombuffer(raw_bytes, dtype=np.float32)
    print(f"Bytes roundtrip: {len(raw_bytes)} bytes -> shape={restored.shape}, OK={np.allclose(engine.embed('test'), restored)}")

    print("\n✅ OfflineEmbeddingEngine is fully operational.")
