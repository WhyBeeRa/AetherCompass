import os
import time
import random
import asyncio
import logging
from typing import Any, List, Optional, Dict, Union
from google import genai
from google.genai import types

logger = logging.getLogger("aether_llm_client")
logger.setLevel(logging.INFO)

# Ensure logging outputs to console
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [SafeGenAIClient] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

RETRYABLE_KEYWORDS = [
    "429", "quota", "resourceexhausted", "limit", "rate", "overloaded",
    "temp", "unavailable", "timeout", "503", "500", "internal error"
]

def is_retryable_error(exc: Exception) -> bool:
    err_str = str(exc).lower()
    exc_type = type(exc).__name__.lower()
    return any(kw in err_str or kw in exc_type for kw in RETRYABLE_KEYWORDS)


class SafeModelsWrapper:
    def __init__(self, safe_client: "SafeGenAIClient"):
        self._safe_client = safe_client

    def generate_content(
        self,
        model: str,
        contents: Any,
        config: Optional[types.GenerateContentConfig] = None,
        **kwargs
    ) -> Any:
        return self._safe_client._generate_content_sync(model, contents, config, **kwargs)

    def embed_content(
        self,
        model: str,
        contents: Any,
        config: Optional[types.EmbedContentConfig] = None,
        **kwargs
    ) -> Any:
        return self._safe_client._embed_content_sync(model, contents, config, **kwargs)


class SafeAioModelsWrapper:
    def __init__(self, safe_client: "SafeGenAIClient"):
        self._safe_client = safe_client

    async def generate_content(
        self,
        model: str,
        contents: Any,
        config: Optional[types.GenerateContentConfig] = None,
        **kwargs
    ) -> Any:
        return await self._safe_client._generate_content_async(model, contents, config, **kwargs)


class SafeAioWrapper:
    def __init__(self, safe_client: "SafeGenAIClient"):
        self.models = SafeAioModelsWrapper(safe_client)


class SafeGenAIClient:
    """
    Transparent drop-in replacement for google.genai.Client.
    Provides automatic retries with exponential backoff and model fallbacks for reliability.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not configured. Client calls will fail.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

        self.models = SafeModelsWrapper(self)
        self.aio = SafeAioWrapper(self)

        # Fallback model chains
        self.fallback_models = {
            "gemini-2.5-flash": ["gemini-1.5-flash", "gemini-1.5-pro"],
            "gemini-2.5-flash-lite": ["gemini-1.5-flash"],
            "text-embedding-004": []  # Embeddings don't have safe fallback as dimension changes would break DB schemas
        }

    def _generate_content_sync(
        self,
        model: str,
        contents: Any,
        config: Optional[types.GenerateContentConfig] = None,
        max_retries: int = 5,
        initial_delay: float = 2.0,
        factor: float = 2.0,
        max_delay: float = 60.0,
        **kwargs
    ) -> Any:
        if not self.client:
            raise ValueError("Google GenAI client is not initialized due to missing API key.")

        models_to_try = [model]
        if model in self.fallback_models:
            models_to_try.extend(self.fallback_models[model])

        last_exception = None

        for current_model in models_to_try:
            attempt = 1
            delay = initial_delay
            while attempt <= max_retries:
                try:
                    logger.info(
                        f"Calling generate_content (sync) with model '{current_model}' - Attempt {attempt}/{max_retries}"
                    )
                    return self.client.models.generate_content(
                        model=current_model,
                        contents=contents,
                        config=config,
                        **kwargs
                    )
                except Exception as e:
                    last_exception = e
                    if is_retryable_error(e) and attempt < max_retries:
                        jitter = random.uniform(0.8, 1.2)
                        wait_time = min(delay * jitter, max_delay)
                        logger.warning(
                            f"Retryable error from '{current_model}' (Attempt {attempt}): {e}. Retrying in {wait_time:.2f}s..."
                        )
                        time.sleep(wait_time)
                        delay *= factor
                        attempt += 1
                    else:
                        logger.error(
                            f"Failed call to '{current_model}' on Attempt {attempt}: {e}."
                        )
                        break  # Break retry loop to try the fallback model

            logger.warning(
                f"Model '{current_model}' failed all retry attempts. Trying next fallback model if available..."
            )

        raise last_exception or RuntimeError(
            f"All fallback models failed for content generation. Last error: {last_exception}"
        )

    async def _generate_content_async(
        self,
        model: str,
        contents: Any,
        config: Optional[types.GenerateContentConfig] = None,
        max_retries: int = 5,
        initial_delay: float = 2.0,
        factor: float = 2.0,
        max_delay: float = 60.0,
        **kwargs
    ) -> Any:
        if not self.client:
            raise ValueError("Google GenAI client is not initialized due to missing API key.")

        models_to_try = [model]
        if model in self.fallback_models:
            models_to_try.extend(self.fallback_models[model])

        last_exception = None

        for current_model in models_to_try:
            attempt = 1
            delay = initial_delay
            while attempt <= max_retries:
                try:
                    logger.info(
                        f"Calling generate_content (async) with model '{current_model}' - Attempt {attempt}/{max_retries}"
                    )
                    return await self.client.aio.models.generate_content(
                        model=current_model,
                        contents=contents,
                        config=config,
                        **kwargs
                    )
                except Exception as e:
                    last_exception = e
                    if is_retryable_error(e) and attempt < max_retries:
                        jitter = random.uniform(0.8, 1.2)
                        wait_time = min(delay * jitter, max_delay)
                        logger.warning(
                            f"Retryable error from '{current_model}' (async, Attempt {attempt}): {e}. Retrying in {wait_time:.2f}s..."
                        )
                        await asyncio.sleep(wait_time)
                        delay *= factor
                        attempt += 1
                    else:
                        logger.error(
                            f"Failed async call to '{current_model}' on Attempt {attempt}: {e}."
                        )
                        break  # Break retry loop to try the fallback model

            logger.warning(
                f"Model '{current_model}' (async) failed all retry attempts. Trying next fallback model if available..."
            )

        raise last_exception or RuntimeError(
            f"All fallback models failed for async content generation. Last error: {last_exception}"
        )

    def _embed_content_sync(
        self,
        model: str,
        contents: Any,
        config: Optional[types.EmbedContentConfig] = None,
        max_retries: int = 5,
        initial_delay: float = 2.0,
        factor: float = 2.0,
        max_delay: float = 60.0,
        **kwargs
    ) -> Any:
        if not self.client:
            raise ValueError("Google GenAI client is not initialized due to missing API key.")

        attempt = 1
        delay = initial_delay
        last_exception = None

        while attempt <= max_retries:
            try:
                logger.info(
                    f"Calling embed_content with model '{model}' - Attempt {attempt}/{max_retries}"
                )
                return self.client.models.embed_content(
                    model=model,
                    contents=contents,
                    config=config,
                    **kwargs
                )
            except Exception as e:
                last_exception = e
                if is_retryable_error(e) and attempt < max_retries:
                    jitter = random.uniform(0.8, 1.2)
                    wait_time = min(delay * jitter, max_delay)
                    logger.warning(
                        f"Retryable error from embedding model '{model}': {e}. Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)
                    delay *= factor
                    attempt += 1
                else:
                    logger.error(f"Failed call to embedding model '{model}' on Attempt {attempt}: {e}.")
                    break

        raise last_exception or RuntimeError(
            f"Embedding content failed after {max_retries} attempts. Last error: {last_exception}"
        )
