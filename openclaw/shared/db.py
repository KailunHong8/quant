"""
Knowledge Base Database
=======================

SQLite schema for:
- sources:  ingested URLs and manual entries
- chunks:   text chunks with vector embeddings
- tags:     per-source tags
- events:   security and ingestion event log (append-only)

Design decisions:
- WAL mode for concurrent read/write safety
- Vectors stored as BLOB (float32 bytes), cosine similarity in Python
- event log is append-only; rows are never deleted or updated
- All writes go through this module; agent has NO direct write access
"""

import os
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "knowledge.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = Path(db_path or DEFAULT_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def initialize(db_path: Optional[Path] = None):
    """Create all tables. Safe to call multiple times (CREATE IF NOT EXISTS)."""
    conn = get_connection(db_path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sources (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            url         TEXT,
            title       TEXT,
            source_type TEXT NOT NULL,   -- article|youtube|twitter|wechat|rednote|tiktok|manual
            language    TEXT DEFAULT 'en',
            ingested_at TEXT NOT NULL,
            metadata    TEXT             -- JSON blob
        );

        CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);
        CREATE INDEX IF NOT EXISTS idx_sources_ingested ON sources(ingested_at);

        CREATE TABLE IF NOT EXISTS chunks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id   INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
            content     TEXT    NOT NULL,
            embedding   BLOB,            -- float32 vector bytes
            chunk_index INTEGER NOT NULL,
            created_at  TEXT    NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id);

        CREATE TABLE IF NOT EXISTS tags (
            source_id   INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
            tag         TEXT    NOT NULL,
            PRIMARY KEY (source_id, tag)
        );

        CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);

        CREATE TABLE IF NOT EXISTS events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type  TEXT    NOT NULL,  -- ingest_ok|ingest_error|injection_detected|redaction|query
            source_id   INTEGER REFERENCES sources(id),
            detail      TEXT,
            created_at  TEXT    NOT NULL
        );
    """)
    conn.commit()
    conn.close()


# ─── Source writes ────────────────────────────────────────────────────────────

def insert_source(
    conn: sqlite3.Connection,
    source_type: str,
    title: str = "",
    url: str = "",
    language: str = "en",
    metadata: Optional[dict] = None,
    tags: Optional[list[str]] = None,
) -> int:
    """Insert a new source; returns its id."""
    now = datetime.now(timezone.utc).isoformat()
    meta_json = json.dumps(metadata or {})
    cur = conn.execute(
        "INSERT INTO sources (url, title, source_type, language, ingested_at, metadata) VALUES (?,?,?,?,?,?)",
        (url, title, source_type, language, now, meta_json),
    )
    source_id = cur.lastrowid
    if tags:
        conn.executemany(
            "INSERT OR IGNORE INTO tags (source_id, tag) VALUES (?,?)",
            [(source_id, t.strip().lower()) for t in tags if t.strip()],
        )
    return source_id


def insert_chunk(
    conn: sqlite3.Connection,
    source_id: int,
    content: str,
    embedding_blob: bytes,
    chunk_index: int,
):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO chunks (source_id, content, embedding, chunk_index, created_at) VALUES (?,?,?,?,?)",
        (source_id, content, embedding_blob, chunk_index, now),
    )


def log_event(conn: sqlite3.Connection, event_type: str, detail: str = "", source_id: Optional[int] = None):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO events (event_type, source_id, detail, created_at) VALUES (?,?,?,?)",
        (event_type, source_id, detail, now),
    )


# ─── Queries ──────────────────────────────────────────────────────────────────

def search_chunks(
    conn: sqlite3.Connection,
    query_embedding_blob: bytes,
    top_k: int = 5,
    source_types: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
    min_similarity: float = 0.25,
) -> list[dict]:
    """
    Return top-k chunks by cosine similarity to the query embedding.
    Optionally filter by source_type or tag.
    """
    import numpy as np
    from .embeddings import blob_to_vec, cosine_similarity

    query_vec = blob_to_vec(query_embedding_blob)

    # Build filter SQL
    where_clauses = []
    params = []

    if source_types:
        placeholders = ",".join("?" * len(source_types))
        where_clauses.append(f"s.source_type IN ({placeholders})")
        params.extend(source_types)

    if tags:
        tag_placeholders = ",".join("?" * len(tags))
        where_clauses.append(f"s.id IN (SELECT source_id FROM tags WHERE tag IN ({tag_placeholders}))")
        params.extend(t.lower() for t in tags)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"""
        SELECT c.id, c.content, c.embedding, c.chunk_index,
               s.id as source_id, s.title, s.url, s.source_type, s.language
        FROM chunks c
        JOIN sources s ON c.source_id = s.id
        {where_sql}
        AND c.embedding IS NOT NULL
    """

    rows = conn.execute(sql, params).fetchall()

    scored = []
    for row in rows:
        vec = blob_to_vec(bytes(row["embedding"]))
        sim = cosine_similarity(query_vec, vec)
        if sim >= min_similarity:
            scored.append({
                "chunk_id": row["id"],
                "content": row["content"],
                "similarity": sim,
                "source_id": row["source_id"],
                "title": row["title"],
                "url": row["url"],
                "source_type": row["source_type"],
                "language": row["language"],
            })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]


def get_stats(conn: sqlite3.Connection) -> dict:
    row = conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM sources) as total_sources,
            (SELECT COUNT(*) FROM chunks)  as total_chunks,
            (SELECT COUNT(*) FROM events)  as total_events
    """).fetchone()

    type_counts = conn.execute(
        "SELECT source_type, COUNT(*) as cnt FROM sources GROUP BY source_type"
    ).fetchall()

    recent = conn.execute(
        "SELECT title, source_type, ingested_at FROM sources ORDER BY ingested_at DESC LIMIT 5"
    ).fetchall()

    return {
        "total_sources": row["total_sources"],
        "total_chunks": row["total_chunks"],
        "total_events": row["total_events"],
        "by_type": {r["source_type"]: r["cnt"] for r in type_counts},
        "recent": [dict(r) for r in recent],
    }


def url_exists(conn: sqlite3.Connection, url: str) -> bool:
    """Check if a URL has already been ingested (avoid duplicates)."""
    row = conn.execute("SELECT 1 FROM sources WHERE url = ? LIMIT 1", (url,)).fetchone()
    return row is not None
