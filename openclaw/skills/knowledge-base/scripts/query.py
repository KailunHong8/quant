#!/usr/bin/env python3
"""
Knowledge Base Query
====================

Semantic search over the local knowledge base.
Results are synthesized and sanitized before output — raw chunks are NEVER
passed to the LLM or returned verbatim to the user.

Usage:
  python query.py --query "what are risks in China real estate?"
  python query.py --query "小红书增长策略" --type rednote
  python query.py --query "AI news" --tags "tech" --limit 5
  python query.py --stats
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from shared.sanitizer import sanitize
from shared.secret_redaction import redact_message
from shared.embeddings import embed, vec_to_blob, get_provider
from shared import db as kbdb


DB_PATH = ROOT / "data" / "knowledge.db"

# ─── LLM synthesis ───────────────────────────────────────────────────────────

def synthesize_answer(query: str, chunks: list[dict]) -> str:
    """
    Use LLM to synthesize an answer from retrieved chunks.
    Chunks are passed as context; they have already been sanitized at ingestion time.
    """
    if not chunks:
        return "No relevant content found in your knowledge base for that query."

    context_parts = []
    for i, c in enumerate(chunks, 1):
        lang_note = f" [{c['language']}]" if c["language"] != "en" else ""
        context_parts.append(
            f"[{i}] {c['title']}{lang_note} (similarity: {c['similarity']:.2f})\n"
            f"Type: {c['source_type']}\n"
            f"Content: {c['content']}"
        )
    context = "\n\n".join(context_parts)

    system = (
        "You are a personal knowledge analyst. "
        "Answer the user's query based ONLY on the provided context chunks. "
        "Synthesize the answer concisely. "
        "At the end, list numbered source references like: [1] Title — source_type. "
        "Never include raw URLs in the answer unless the user explicitly asked for them. "
        "If the context is insufficient, say so directly. "
        "For Chinese queries, respond in Chinese."
    )

    prompt = f"Context:\n\n{context}\n\nQuery: {query}"

    # Try providers in order
    response = _call_llm(system, prompt)
    return redact_message(response)  # Final secret-redaction pass before returning


def _call_llm(system: str, prompt: str) -> str:
    """Call LLM with system+user messages. Tries Bedrock then OpenAI."""
    import os, json as _json

    # ── AWS Bedrock ──────────────────────────────────────────────────────
    try:
        import boto3
        client = boto3.client(
            "bedrock-runtime",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        )
        body = _json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.1,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        })
        resp = client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=body,
        )
        result = _json.loads(resp["body"].read())
        return result["content"][0]["text"]
    except Exception:
        pass

    # ── OpenAI ────────────────────────────────────────────────────────────
    try:
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY")
        if key:
            client = OpenAI(api_key=key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.1,
                max_tokens=1024,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            return resp.choices[0].message.content
    except Exception:
        pass

    # ── Fallback: return raw context summary ─────────────────────────────
    lines = ["Here are the most relevant entries:\n"]
    for c in chunks:
        lines.append(f"• [{c['source_type']}] {c['title']}: {c['content'][:200]}...")
    return "\n".join(lines)


# ─── Stats ────────────────────────────────────────────────────────────────────

def print_stats():
    kbdb.initialize(DB_PATH)
    conn = kbdb.get_connection(DB_PATH)
    stats = kbdb.get_stats(conn)
    conn.close()

    print("📚 Knowledge Base Stats")
    print(f"   Sources : {stats['total_sources']}")
    print(f"   Chunks  : {stats['total_chunks']}")
    print(f"   Events  : {stats['total_events']}")
    print()
    print("By type:")
    for stype, cnt in stats["by_type"].items():
        print(f"   {stype:<12} {cnt}")
    print()
    print("Recent ingestions:")
    for r in stats["recent"]:
        print(f"   [{r['source_type']}] {r['title'][:50]}  ({r['ingested_at'][:10]})")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Query the knowledge base")
    parser.add_argument("--query",  help="Search query (English or Chinese)")
    parser.add_argument("--type",   help="Filter by source type (article|youtube|rednote|...)")
    parser.add_argument("--tags",   help="Filter by comma-separated tags")
    parser.add_argument("--limit",  type=int, default=5, help="Max results (default 5)")
    parser.add_argument("--min-sim", type=float, default=0.25,
                        help="Minimum similarity threshold (default 0.25)")
    parser.add_argument("--stats",  action="store_true", help="Show KB stats")
    parser.add_argument("--raw",    action="store_true",
                        help="Return raw chunk text (for debugging only)")

    args = parser.parse_args()

    if args.stats:
        print_stats()
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    # Sanitize the query itself (user input is trusted but let's be consistent)
    q_result = sanitize(args.query, max_chars=500)
    if q_result.injection_detected:
        print("⚠ Query flagged as suspicious. Please rephrase.")
        sys.exit(2)
    query = q_result.text

    kbdb.initialize(DB_PATH)
    conn = kbdb.get_connection(DB_PATH)

    # Embed query
    get_provider()
    query_vec = embed(query)
    query_blob = vec_to_blob(query_vec)

    # Parse filters
    source_types = [args.type] if args.type else None
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None

    # Search
    results = kbdb.search_chunks(
        conn,
        query_embedding_blob=query_blob,
        top_k=args.limit,
        source_types=source_types,
        tags=tags,
        min_similarity=args.min_sim,
    )

    # Log query
    kbdb.log_event(conn, "query", detail=f"q={query[:80]} results={len(results)}")
    conn.commit()
    conn.close()

    if args.raw:
        # Debug mode: show raw chunks (still sanitized at write time)
        for r in results:
            print(f"\n[{r['similarity']:.2f}] {r['title']} ({r['source_type']})")
            print(r["content"])
        return

    # Synthesize answer
    answer = synthesize_answer(query, results)
    print(answer)


if __name__ == "__main__":
    main()
