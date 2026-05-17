# ── Hugging Face Spaces  –  Contexto FastAPI Backend ──────────────────────────
# Base image: slim Python (HF Spaces runs on CPU by default)
FROM python:3.10-slim

# HF Spaces requires port 7860
EXPOSE 7860

# System deps for faiss-cpu, lxml, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements_hf.txt ./requirements.txt

# Install Python deps  (no CUDA → CPU-only torch, much smaller)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Pre-download the T5 model so it is cached in the image
# (avoids cold-start download on first request)
RUN python -c "from transformers import T5Tokenizer, T5ForConditionalGeneration; \
    T5Tokenizer.from_pretrained('t5-small'); \
    T5ForConditionalGeneration.from_pretrained('t5-small')" || true

# Set env so transformers uses /app/.cache (writable in HF Spaces)
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV HF_HOME=/app/.cache/huggingface

# Run on port 7860  (HF Spaces requirement)
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
