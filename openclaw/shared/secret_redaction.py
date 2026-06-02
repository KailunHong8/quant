"""
Secret Redaction
================

Scan any outbound message for credential-shaped strings and replace them
with [REDACTED] before the message goes to WhatsApp or any other channel.

Called as the final pass before every outbound message.
"""

import re
from typing import NamedTuple

# ─── Patterns ────────────────────────────────────────────────────────────────
# Each pattern: (label, regex)
# Order matters: more specific patterns first.

_PATTERNS = [
    # AWS
    ("aws_access_key",   r"(?<![A-Z0-9])(AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16}(?![A-Z0-9])"),
    ("aws_secret_key",   r"(?i)aws.{0,20}secret.{0,20}['\"]([A-Za-z0-9/+]{40})['\"]"),
    # OpenAI / Anthropic
    ("openai_key",       r"sk-[A-Za-z0-9]{20,60}"),
    ("anthropic_key",    r"sk-ant-[A-Za-z0-9\-]{20,80}"),
    # Generic bearer tokens
    ("bearer_token",     r"(?i)bearer\s+[A-Za-z0-9\-_.]{20,}"),
    # Generic API keys
    ("generic_api_key",  r"(?i)(api[_\-]?key|api[_\-]?secret|access[_\-]?token|private[_\-]?key)\s*[=:]\s*['\"]?([A-Za-z0-9\-_.]{20,})['\"]?"),
    # Private keys (PEM blocks)
    ("private_key_pem",  r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----"),
    # Passwords in connection strings
    ("conn_password",    r"(?i)://[^:]+:([^@]{8,})@"),
    # GitHub tokens
    ("github_token",     r"ghp_[A-Za-z0-9]{36}"),
    ("github_classic",   r"github_pat_[A-Za-z0-9_]{82}"),
]

_COMPILED = [(label, re.compile(pattern, re.DOTALL)) for label, pattern in _PATTERNS]


class RedactionResult(NamedTuple):
    text: str
    redacted_count: int
    redacted_labels: list[str]


def redact(text: str) -> RedactionResult:
    """
    Scan text for secrets and replace each with [REDACTED:<label>].
    Returns the cleaned text and a count of redactions.

    Always call this before sending any message to an external channel.
    """
    if not text:
        return RedactionResult(text="", redacted_count=0, redacted_labels=[])

    redacted_count = 0
    found_labels = []

    for label, pattern in _COMPILED:
        def _replace(m):
            nonlocal redacted_count
            redacted_count += 1
            found_labels.append(label)
            return f"[REDACTED:{label}]"

        text = pattern.sub(_replace, text)

    return RedactionResult(text=text, redacted_count=redacted_count, redacted_labels=found_labels)


def redact_message(message: str) -> str:
    """
    Convenience wrapper: returns only the cleaned text.
    Use this as the final step before any outbound message.
    """
    result = redact(message)
    if result.redacted_count > 0:
        # Append a footnote so the user knows something was stripped
        note = f"\n\n_(⚠️ {result.redacted_count} credential(s) auto-redacted from this message)_"
        return result.text + note
    return result.text


if __name__ == "__main__":
    # Quick smoke test
    test = """
    Here is your config:
    OPENAI_API_KEY = sk-abcdefghijklmnopqrstuvwxyz12345678901234
    AWS_KEY: AKIAIOSFODNN7EXAMPLE
    password: super_secret_pass@db.host.com
    Normal text stays unchanged.
    """
    out = redact_message(test)
    print(out)
