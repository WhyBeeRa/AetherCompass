FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the ONNX model during build (avoids cold start download)
RUN python -c "\
from huggingface_hub import hf_hub_download; \
hf_hub_download('BAAI/bge-small-en-v1.5', 'onnx/model.onnx', cache_dir='/tmp/fastembed_cache'); \
hf_hub_download('BAAI/bge-small-en-v1.5', 'tokenizer.json', cache_dir='/tmp/fastembed_cache'); \
print('Model pre-downloaded successfully.')"

# Copy all backend source code
COPY . .

EXPOSE 8000

# CRITICAL: --workers 1 prevents RAM duplication of the embedding model (~130MB)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
