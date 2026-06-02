"""
Embedding Generation
====================

Generates vector embeddings for knowledge-base chunks.
Supports multilingual content (Chinese/English) critical for:
- 小红书 / 抖音 / 朋友圈 content
- English articles and YouTube transcripts

Provider priority (auto-selects based on available credentials):
1. OpenAI text-embedding-3-small (1536-dim, multilingual)
2. AWS Bedrock Amazon Titan Text Embeddings v2 (1024-dim, multilingual)
3. sentence-transformers paraphrase-multilingual-MiniLM-L12-v2 (384-dim, local/offline)
"""

import os
import json
import struct
import hashlib
import numpy as np
from typing import Optional

# ─── Dimension constants ─────────────────────────────────────────────────────
DIM_OPENAI = 1536
DIM_BEDROCK_TITAN = 1024
DIM_LOCAL = 384

EMBEDDING_DIM = None  # Set after provider is initialized


# ─── Provider initialization ─────────────────────────────────────────────────

def _init_openai():
    try:
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY") or _load_openclaw_key("openai")
        if not key:
            return None
        client = OpenAI(api_key=key)
        # Quick probe
        client.embeddings.create(input="test", model="text-embedding-3-small")
        print("✓ Embeddings: OpenAI text-embedding-3-small")
        return ("openai", client, DIM_OPENAI)
    except Exception:
        return None


def _init_bedrock():
    try:
        import boto3
        import json as _json
        client = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
        # Quick probe
        body = _json.dumps({"inputText": "test"})
        client.invoke_model(modelId="amazon.titan-embed-text-v2:0", body=body)
        print("✓ Embeddings: AWS Bedrock Titan v2")
        return ("bedrock", client, DIM_BEDROCK_TITAN)
    except Exception:
        return None


def _init_local():
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("✓ Embeddings: local sentence-transformers (multilingual, offline)")
        return ("local", model, DIM_LOCAL)
    except Exception:
        return None


def _load_openclaw_key(provider: str) -> Optional[str]:
    """Try to load API key from ~/.openclaw/openclaw.json"""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(config_path) as f:
            config = json.load(f)
        if provider == "openai":
            return config.get("providers", {}).get("openai", {}).get("apiKey")
        if provider == "anthropic":
            return config.get("providers", {}).get("anthropic", {}).get("apiKey")
    except Exception:
        pass
    return None


_PROVIDER = None  # (name, client, dim)


def get_provider():
    global _PROVIDER, EMBEDDING_DIM
    if _PROVIDER:
        return _PROVIDER
    for init_fn in [_init_openai, _init_bedrock, _init_local]:
        result = init_fn()
        if result:
            _PROVIDER = result
            EMBEDDING_DIM = result[2]
            return _PROVIDER
    raise RuntimeError(
        "No embedding provider available.\n"
        "Install one of:\n"
        "  pip install openai          # OpenAI API\n"
        "  pip install boto3           # AWS Bedrock\n"
        "  pip install sentence-transformers  # Local/offline"
    )


# ─── Embedding functions ─────────────────────────────────────────────────────

def embed(text: str) -> np.ndarray:
    """
    Embed a single text string. Returns float32 numpy array.
    """
    name, client, dim = get_provider()

    if name == "openai":
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        vec = response.data[0].embedding
        return np.array(vec, dtype=np.float32)

    elif name == "bedrock":
        import boto3, json as _json
        body = _json.dumps({"inputText": text})
        resp = client.invoke_model(modelId="amazon.titan-embed-text-v2:0", body=body)
        result = _json.loads(resp["body"].read())
        return np.array(result["embedding"], dtype=np.float32)

    elif name == "local":
        vec = client.encode(text, normalize_embeddings=True)
        return vec.astype(np.float32)

    raise RuntimeError(f"Unknown provider: {name}")


def embed_batch(texts: list[str], batch_size: int = 32) -> list[np.ndarray]:
    """
    Embed a list of texts with batching.
    """
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        name, client, dim = get_provider()

        if name == "openai":
            resp = client.embeddings.create(input=batch, model="text-embedding-3-small")
            for item in resp.data:
                results.append(np.array(item.embedding, dtype=np.float32))

        elif name == "bedrock":
            # Bedrock doesn't batch — embed one at a time
            for text in batch:
                results.append(embed(text))

        elif name == "local":
            vecs = client.encode(batch, normalize_embeddings=True, show_progress_bar=False)
            results.extend([v.astype(np.float32) for v in vecs])

    return results


# ─── Serialization ───────────────────────────────────────────────────────────

def vec_to_blob(vec: np.ndarray) -> bytes:
    """Convert float32 numpy array to bytes for SQLite BLOB storage."""
    return vec.astype(np.float32).tobytes()


def blob_to_vec(blob: bytes) -> np.ndarray:
    """Convert SQLite BLOB back to float32 numpy array."""
    return np.frombuffer(blob, dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
