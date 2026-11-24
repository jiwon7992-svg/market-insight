"""사건 조회/추가. 모든 조회는 as_of(기준 시점)를 지원한다.

as_of=None  → 현재 기준(모든 정보 조회 가능)
as_of='YYYY-MM-DD' → 공개일(published_at)이 as_of 이하인 정보만 반환 (미래 정보 차단)
"""
import sqlite3
from datetime import date

from .config import CATEGORIES


def _validate_date(s: str) -> str:
    return date.fromisoformat(s).isoformat()  # 형식이 틀리면 ValueError


def visible_events(conn, as_of=None, category=None, keyword=None, limit=None):
    sql = "SELECT * FROM events WHERE 1=1"
    params = []
    if as_of is not None:
        sql += " AND published_at <= ?"
        params.append(_validate_date(as_of))
    if category:
        sql += " AND category = ?"
        params.append(category)
    if keyword:
        sql += " AND (title LIKE ? OR summary LIKE ? OR id IN " \
               "(SELECT event_id FROM event_tickers WHERE ticker LIKE ?))"
        like = f"%{keyword}%"
        params += [like, like, like]
    sql += " ORDER BY published_at DESC, id DESC"
    if limit:
        sql += " LIMIT ?"
        params.append(int(limit))
    return conn.execute(sql, params).fetchall()


def tickers_of(conn, event_id: int):
    rows = conn.execute(
        "SELECT ticker, role FROM event_tickers WHERE event_id = ? ORDER BY role, ticker",
        (event_id,),
    ).fetchall()
    return [(r["ticker"], r["role"]) for r in rows]


def add_event(conn, title, category, occurred_at, published_at,
              summary="", background="", transmission="",
              tickers=(), data_origin="user") -> int:
    title = title.strip()
    if not title:
        raise ValueError("사건 제목을 입력하세요.")
    if category not in CATEGORIES:
        raise ValueError(f"알 수 없는 사건 종류: {category}")
    occurred_at, published_at = _validate_date(occurred_at), _validate_date(published_at)
    cur = conn.execute(
        "INSERT INTO events (title, category, occurred_at, published_at, summary, "
        "background, transmission, data_origin) VALUES (?,?,?,?,?,?,?,?)",
        (title, category, occurred_at, published_at, summary, background,
         transmission, data_origin),
    )
    eid = cur.lastrowid
    for t in tickers:
        ticker, role = t if isinstance(t, tuple) else (t, "company")
        ticker = ticker.strip().upper()
        if ticker:
            conn.execute(
                "INSERT OR IGNORE INTO event_tickers (event_id, ticker, role) VALUES (?,?,?)",
                (eid, ticker, role),
            )
    conn.commit()
    return eid


def parse_tickers(text: str):
    """'NVDA, spy' → ['NVDA', 'SPY']"""
    return [t.strip().upper() for t in text.replace(";", ",").split(",") if t.strip()]
