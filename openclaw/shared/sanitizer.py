"""
Content Sanitizer
=================

All external content (articles, YouTube, tweets, WeChat 朋友圈, 小红书, 抖音)
must pass through this module before embedding, storage, or LLM processing.

Security model (inspired by OpenClaw prompt #13 — Security and Safety):
- Detect prompt injection attempts and discard the content
- Truncate content to prevent context-window poisoning
- Strip zero-width characters and Unicode trickery used in injections
- Return clean text + a flag indicating whether content was suspicious

Never pass untrusted content verbatim to an LLM without calling sanitize() first.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional


# ─── Injection Signatures ───────────────────────────────────────────────────
# Any content containing these patterns is flagged as a suspected injection.
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"disregard\s+(all\s+)?previous",
    r"\bsystem\s*:",                       # "System: ..." instruction markers
    r"<\s*system\s*>",
    r"\boverride\b",
    r"\bjailbreak\b",
    r"\bbypass\b.*\brestrict",
    r"you\s+are\s+now\s+(a\s+)?.*bot",
    r"new\s+(role|persona|instructions?)\s*:",
    r"forget\s+(everything|all\s+previous)",
    r"(update|modify|rewrite|delete)\s+(your\s+)?(soul|identity|agents?|skill)\.?md",
    r"send\s+(this\s+)?(to\s+)?(everyone|all\s+contacts)",
    r"reveal\s+(your\s+)?(api\s+key|token|secret|password)",
    r"exfiltrat",
    r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
    r"do\s+anything\s+now",                # DAN pattern
    r"\bDAN\b",
]

_COMPILED_INJECTIONS = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in INJECTION_PATTERNS]

# Zero-width and invisible Unicode characters used to hide injections
INVISIBLE_CHARS = re.compile(
    r"[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060-\u2064\ufeff]"
)

# Maximum chunk size to prevent context poisoning
MAX_CONTENT_CHARS = 8000
MAX_CHUNK_CHARS = 500


@dataclass
class SanitizedContent:
    text: str
    was_truncated: bool
    injection_detected: bool
    injection_reason: Optional[str] = None


def sanitize(raw_text: str, max_chars: int = MAX_CONTENT_CHARS) -> SanitizedContent:
    """
    Sanitize external content before any LLM or storage use.

    Returns SanitizedContent with:
    - text: cleaned text (empty string if injection detected)
    - was_truncated: True if content was cut
    - injection_detected: True if a prompt injection was found
    - injection_reason: which pattern matched (for logging)

    Usage:
        result = sanitize(raw_external_text)
        if result.injection_detected:
            log_security_event(result.injection_reason)
            return  # discard — never store or forward

        safe_text = result.text
    """
    if not raw_text:
        return SanitizedContent(text="", was_truncated=False, injection_detected=False)

    # Step 1: Strip invisible/zero-width characters (common injection vector)
    text = INVISIBLE_CHARS.sub("", raw_text)

    # Step 2: Normalize Unicode (NFKC: collapse lookalike chars, e.g. ｉgnore → ignore)
    text = unicodedata.normalize("NFKC", text)

    # Step 3: Scan for injection patterns
    for pattern in _COMPILED_INJECTIONS:
        match = pattern.search(text)
        if match:
            return SanitizedContent(
                text="",
                was_truncated=False,
                injection_detected=True,
                injection_reason=f"Pattern matched: '{pattern.pattern[:60]}' at position {match.start()}"
            )

    # Step 4: Truncate to prevent context-window flooding
    was_truncated = len(text) > max_chars
    if was_truncated:
        text = text[:max_chars] + "\n[content truncated for security]"

    # Step 5: Strip leading/trailing whitespace
    text = text.strip()

    return SanitizedContent(text=text, was_truncated=was_truncated, injection_detected=False)


def sanitize_chunk(text: str) -> SanitizedContent:
    """Sanitize a single embedding chunk (smaller limit)."""
    return sanitize(text, max_chars=MAX_CHUNK_CHARS)


def chunk_text(text: str, chunk_size: int = MAX_CHUNK_CHARS, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks for embedding.
    Each chunk is sanitized independently.
    Returns only clean chunks (discards any that trigger injection detection).
    """
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        result = sanitize_chunk(chunk)
        if not result.injection_detected and result.text:
            chunks.append(result.text)
        start = end - overlap  # overlap for context continuity

    return chunks
