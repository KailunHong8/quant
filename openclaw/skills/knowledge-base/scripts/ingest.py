#!/usr/bin/env python3
"""
Knowledge Base Ingestion
========================

Ingests content from multiple sources into the local SQLite knowledge base.
ALL external content is sanitized before embedding or storage.

Supported sources:
  --url        Web article
  --youtube    YouTube video (transcript extraction)
  --twitter    Twitter/X post or thread
  --text       Manual text (WeChat 朋友圈, 小红书, 抖音, any paste)

Usage:
  python ingest.py --url "https://example.com" --tags "finance,macro"
  python ingest.py --youtube "https://youtu.be/xxx" --tags "strategy"
  python ingest.py --text "笔记内容..." --type rednote --tags "xiaohongshu"
  python ingest.py --twitter "https://twitter.com/user/status/xxx"
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

# ─── Path setup ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from shared.sanitizer import sanitize, chunk_text
from shared.secret_redaction import redact_message
from shared.embeddings import embed_batch, vec_to_blob, get_provider
from shared import db as kbdb


DB_PATH = ROOT / "data" / "knowledge.db"


# ─── Content fetchers ─────────────────────────────────────────────────────────

def fetch_article(url: str) -> tuple[str, str]:
    """Fetch web article; returns (title, text)."""
    try:
        from readabilipy import simple_json_from_html_string
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; knowledge-bot/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        article = simple_json_from_html_string(html, use_readability=True)
        title = article.get("title", "") or url
        text = article.get("plain_text", "") or article.get("content", "") or ""
        return title, text
    except ImportError:
        # Fallback: basic HTML strip
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; knowledge-bot/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        import re
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        title = title_match.group(1).strip() if title_match else url
        return title, text


def fetch_youtube_transcript(url: str) -> tuple[str, str]:
    """Extract YouTube transcript; returns (title, transcript_text)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        import re
        video_id_match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
        if not video_id_match:
            raise ValueError(f"Cannot parse YouTube video ID from: {url}")
        video_id = video_id_match.group(1)

        # Try multiple languages (Chinese and English)
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["zh-Hans", "zh-Hant", "zh", "en"]
        )
        text = " ".join(entry["text"] for entry in transcript_list)
        title = f"YouTube:{video_id}"
        return title, text

    except ImportError:
        print("✗ youtube-transcript-api not installed. Run: pip install youtube-transcript-api")
        sys.exit(1)


def fetch_twitter(url: str) -> tuple[str, str]:
    """
    Fetch a tweet/thread. Uses FxTwitter API (read-only, no auth required).
    Returns (title, text).
    """
    import re
    match = re.search(r"(?:twitter\.com|x\.com)/[^/]+/status/(\d+)", url)
    if not match:
        raise ValueError(f"Cannot parse tweet ID from: {url}")
    tweet_id = match.group(1)

    api_url = f"https://api.fxtwitter.com/status/{tweet_id}"
    req = urllib.request.Request(api_url, headers={"User-Agent": "knowledge-bot/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())

    tweet = data.get("tweet", {})
    text = tweet.get("text", "")
    author = tweet.get("author", {}).get("name", "unknown")
    created = tweet.get("created_at", "")
    title = f"Tweet by @{author} ({created[:10] if created else ''})"
    return title, text


# ─── Main ingestion pipeline ──────────────────────────────────────────────────

def ingest(
    content_type: str,
    title: str,
    raw_text: str,
    url: str = "",
    language: str = "en",
    tags: list[str] = None,
    metadata: dict = None,
):
    """
    Full ingestion pipeline:
    1. Sanitize (injection detection, truncation)
    2. Chunk text
    3. Embed each chunk
    4. Store in SQLite
    """
    conn = kbdb.get_connection(DB_PATH)
    kbdb.initialize(DB_PATH)

    # ── 1. Sanitize ────────────────────────────────────────────────────────
    result = sanitize(raw_text)

    if result.injection_detected:
        print(f"INJECTION_DETECTED: {result.injection_reason}")
        kbdb.log_event(conn, "injection_detected", detail=result.injection_reason)
        conn.commit()
        conn.close()
        sys.exit(2)  # Exit code 2 = injection; caller must handle this

    if result.was_truncated:
        print(f"⚠ Content truncated at 8000 chars")

    clean_text = result.text
    if not clean_text.strip():
        print("✗ No content after sanitization")
        sys.exit(1)

    # ── 2. Duplicate check ─────────────────────────────────────────────────
    if url and kbdb.url_exists(conn, url):
        print(f"⚠ Already ingested: {url}")
        conn.close()
        return

    # ── 3. Chunk ───────────────────────────────────────────────────────────
    chunks = chunk_text(clean_text, chunk_size=400, overlap=40)
    if not chunks:
        print("✗ No chunks produced after sanitization")
        sys.exit(1)

    # ── 4. Embed ───────────────────────────────────────────────────────────
    print(f"⚡ Embedding {len(chunks)} chunks...")
    get_provider()  # ensure initialized
    embeddings = embed_batch(chunks)

    # ── 5. Store ───────────────────────────────────────────────────────────
    source_id = kbdb.insert_source(
        conn,
        source_type=content_type,
        title=title,
        url=url,
        language=language,
        metadata=metadata,
        tags=tags,
    )

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        kbdb.insert_chunk(
            conn,
            source_id=source_id,
            content=chunk,
            embedding_blob=vec_to_blob(emb),
            chunk_index=i,
        )

    kbdb.log_event(conn, "ingest_ok", source_id=source_id,
                   detail=f"type={content_type} chunks={len(chunks)}")
    conn.commit()
    conn.close()

    print(f"✓ Ingested: [{content_type}] {title!r} ({len(chunks)} chunks)")
    if url:
        print(f"  URL: {url}")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ingest content into knowledge base")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url",       help="Web article URL")
    group.add_argument("--youtube",   help="YouTube video URL")
    group.add_argument("--twitter",   help="Twitter/X post URL")
    group.add_argument("--text",      help="Manual text (paste)")

    parser.add_argument("--type",  default="manual",
                        choices=["article", "youtube", "twitter", "wechat", "rednote", "tiktok", "manual"],
                        help="Content type label (default: manual)")
    parser.add_argument("--tags",  default="", help="Comma-separated tags")
    parser.add_argument("--lang",  default="en", help="Language code (en, zh, etc.)")
    parser.add_argument("--title", default="", help="Override title")

    args = parser.parse_args()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    try:
        if args.url:
            print(f"⬇ Fetching: {args.url}")
            title, text = fetch_article(args.url)
            ingest("article", args.title or title, text,
                   url=args.url, language=args.lang, tags=tags)

        elif args.youtube:
            print(f"⬇ Fetching YouTube transcript: {args.youtube}")
            title, text = fetch_youtube_transcript(args.youtube)
            ingest("youtube", args.title or title, text,
                   url=args.youtube, language=args.lang, tags=tags)

        elif args.twitter:
            print(f"⬇ Fetching tweet: {args.twitter}")
            title, text = fetch_twitter(args.twitter)
            ingest("twitter", args.title or title, text,
                   url=args.twitter, language=args.lang, tags=tags)

        elif args.text:
            title = args.title or f"{args.type.capitalize()} entry {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
            ingest(args.type, title, args.text,
                   language=args.lang, tags=tags)

    except SystemExit:
        raise
    except Exception as e:
        print(f"✗ Ingestion failed: {e}")
        # Log without exposing secret-shaped strings
        safe_error = redact_message(str(e))
        conn = kbdb.get_connection(DB_PATH)
        kbdb.log_event(conn, "ingest_error", detail=safe_error)
        conn.commit()
        conn.close()
        sys.exit(1)


if __name__ == "__main__":
    main()
