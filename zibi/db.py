from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


DATA_DIR = Path.home() / ".local" / "share" / "zibi"
DB_PATH = DATA_DIR / "history.db"


@dataclass(frozen=True)
class HistoryEntry:
    id: int
    content: str
    source: str
    created_at: str
    pinned: bool


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            source TEXT NOT NULL CHECK (source IN ('manual', 'file', 'pipe', 'copyp')),
            pinned INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        );

        CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at DESC, id DESC);
        CREATE INDEX IF NOT EXISTS idx_history_source ON history(source);
        """
    )
    conn.commit()


def add_history(
    content: str,
    source: str,
    *,
    max_entries: int,
    deduplicate_consecutive: bool,
) -> int | None:
    if source not in {"manual", "file", "pipe", "copyp"}:
        source = "manual"
    with connect() as conn:
        if deduplicate_consecutive:
            row = conn.execute("SELECT content FROM history ORDER BY id DESC LIMIT 1").fetchone()
            if row and row["content"] == content:
                return None

        cur = conn.execute("INSERT INTO history (content, source) VALUES (?, ?)", (content, source))
        prune_history(conn, max_entries)
        conn.commit()
        return int(cur.lastrowid)


def prune_history(conn: sqlite3.Connection, max_entries: int) -> int:
    rows = conn.execute(
        """
        SELECT id FROM history
        WHERE pinned = 0
        ORDER BY created_at DESC, id DESC
        LIMIT -1 OFFSET ?
        """,
        (max_entries,),
    ).fetchall()
    ids = [row["id"] for row in rows]
    if not ids:
        return 0
    placeholders = ",".join("?" for _ in ids)
    conn.execute(f"DELETE FROM history WHERE id IN ({placeholders})", ids)
    return len(ids)


def _entry_from_row(row: sqlite3.Row) -> HistoryEntry:
    return HistoryEntry(
        id=int(row["id"]),
        content=str(row["content"]),
        source=str(row["source"]),
        created_at=str(row["created_at"]),
        pinned=bool(row["pinned"]),
    )


def list_history(limit: int | None = None, *, pinned_only: bool = False) -> list[HistoryEntry]:
    sql = "SELECT id, content, source, created_at, pinned FROM history"
    params: list[int] = []
    if pinned_only:
        sql += " WHERE pinned = 1"
    sql += " ORDER BY created_at DESC, id DESC"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    with connect() as conn:
        return [_entry_from_row(row) for row in conn.execute(sql, params).fetchall()]


def get_entry_by_index(index: int) -> tuple[int, HistoryEntry] | None:
    if index < 1:
        return None
    entries = list_history()
    if index > len(entries):
        return None
    return index, entries[index - 1]


def search_history(query: str, limit: int = 50) -> list[HistoryEntry]:
    like = f"%{query}%"
    with connect() as conn:
        return [
            _entry_from_row(row)
            for row in conn.execute(
                """
                SELECT id, content, source, created_at, pinned
                FROM history
                WHERE content LIKE ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (like, limit),
            ).fetchall()
        ]


def set_pinned(entry_id: int, pinned: bool = True) -> None:
    with connect() as conn:
        conn.execute("UPDATE history SET pinned = ? WHERE id = ?", (1 if pinned else 0, entry_id))
        conn.commit()


def delete_history_entry(entry_id: int) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
        conn.commit()


def wipe_unpinned() -> int:
    with connect() as conn:
        cur = conn.execute("DELETE FROM history WHERE pinned = 0")
        conn.commit()
        return int(cur.rowcount)


def wipe_all() -> int:
    with connect() as conn:
        cur = conn.execute("DELETE FROM history")
        conn.commit()
        return int(cur.rowcount)


def count_history() -> int:
    with connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM history").fetchone()
        return int(row["count"])


def latest_entry() -> HistoryEntry | None:
    entries = list_history(1)
    return entries[0] if entries else None


def stats() -> dict[str, object]:
    with connect() as conn:
        total = int(conn.execute("SELECT COUNT(*) AS count FROM history").fetchone()["count"])
        pinned = int(conn.execute("SELECT COUNT(*) AS count FROM history WHERE pinned = 1").fetchone()["count"])
        avg_row = conn.execute("SELECT AVG(LENGTH(content)) AS avg_len FROM history").fetchone()
        avg_len = float(avg_row["avg_len"] or 0)
        by_source = {
            str(row["source"]): int(row["count"])
            for row in conn.execute(
                "SELECT source, COUNT(*) AS count FROM history GROUP BY source ORDER BY source"
            ).fetchall()
        }
        busy_row = conn.execute(
            """
            SELECT strftime('%w', created_at) AS weekday, COUNT(*) AS count
            FROM history
            GROUP BY weekday
            ORDER BY count DESC
            LIMIT 1
            """
        ).fetchone()
        contents = [str(row["content"]) for row in conn.execute("SELECT content FROM history").fetchall()]

    return {
        "total": total,
        "pinned": pinned,
        "avg_len": avg_len,
        "by_source": by_source,
        "busiest_day": str(busy_row["weekday"]) if busy_row else "",
        "contents": contents,
    }
