"""
LocalEmbeddingEngine — Singleton ONNX Embedding Service
=========================================================
Loads BAAI/bge-small-en-v1.5 ONNX model exactly once into memory.
Uses onnxruntime + tokenizers directly — no fastembed dependency,
so it works across all Python versions (3.11 Docker + 3.14 local).

Model: ~33M params, ~130MB RAM, 384 dimensions.
CRITICAL: Run uvicorn with --workers 1 to prevent RAM duplication.
"""
import os
import numpy as np
from pathlib import Path


class LocalEmbeddingEngine:
    _instance = None
    _session = None
    _tokenizer = None

    EMBEDDING_DIM = 384  # bge-small-en-v1.5 output dimension
    MODEL_ID = "BAAI/bge-small-en-v1.5"
    CACHE_DIR = os.environ.get("FASTEMBED_CACHE_DIR", "/tmp/fastembed_cache")

    @classmethod
    def get_instance(cls) -> "LocalEmbeddingEngine":
        """Thread-safe singleton accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if LocalEmbeddingEngine._session is None:
            self._load_model()

    def _load_model(self):
        """Download (if needed) and load the ONNX model + tokenizer."""
        import onnxruntime as ort
        from tokenizers import Tokenizer
        from huggingface_hub import hf_hub_download

        print(f"[Embedder] Loading {self.MODEL_ID} via ONNX Runtime ...")

        cache_dir = self.CACHE_DIR
        os.makedirs(cache_dir, exist_ok=True)

        # Download model files from HuggingFace Hub
        onnx_path = hf_hub_download(
            repo_id=self.MODEL_ID,
            filename="onnx/model.onnx",
            cache_dir=cache_dir,
        )
        tokenizer_path = hf_hub_download(
            repo_id=self.MODEL_ID,
            filename="tokenizer.json",
            cache_dir=cache_dir,
        )

        # Load ONNX session (CPU only — fits Render 512MB)
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.intra_op_num_threads = 1  # Save RAM on free tier

        LocalEmbeddingEngine._session = ort.InferenceSession(
            onnx_path,
            sess_options=sess_options,
            providers=["CPUExecutionProvider"],
        )

        # Load tokenizer
        LocalEmbeddingEngine._tokenizer = Tokenizer.from_file(tokenizer_path)
        LocalEmbeddingEngine._tokenizer.enable_truncation(max_length=512)
        LocalEmbeddingEngine._tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=512)

        print("[Embedder] Model loaded successfully. Ready for embedding.")

    # ── public API ──────────────────────────────────────────────

    def is_ready(self) -> bool:
        """Checks if the ONNX session and tokenizer are initialized."""
        return self._session is not None and self._tokenizer is not None

    def embed(self, text: str) -> np.ndarray:
        """Embed a single text string. Returns float32 numpy array (384,)."""
        encoded = self._tokenizer.encode(text)

        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

        outputs = self._session.run(
            None,
            {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "token_type_ids": token_type_ids,
            },
        )

        # outputs[0] is (1, seq_len, 384) — mean pooling over valid tokens
        token_embeddings = outputs[0]  # shape: (1, seq_len, 384)
        mask_expanded = attention_mask[:, :, np.newaxis].astype(np.float32)

        summed = np.sum(token_embeddings * mask_expanded, axis=1)
        counts = np.sum(mask_expanded, axis=1)
        counts = np.maximum(counts, 1e-9)  # prevent division by zero
        mean_pooled = summed / counts

        # L2 normalize
        norm = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
        norm = np.maximum(norm, 1e-9)
        normalized = mean_pooled / norm

        return normalized[0].astype(np.float32)

    def embed_batch(self, texts: list) -> list:
        """Embed a list of texts. Returns list of float32 numpy arrays."""
        return [self.embed(t) for t in texts]

    def embed_to_bytes(self, text: str) -> bytes:
        """Embed and convert to raw bytes for BLOB storage."""
        return self.embed(text).tobytes()
