"""SQLite 스키마.

블라인드 분석(8장)을 위한 핵심 설계:
  - 모든 정보는 '발생일(occurred_at)'과 '공개일(published_at)'을 따로 가진다.
  - 어떤 시점(as_of)의 분석에서도 공개일이 as_of 이후인 정보는 조회하지 않는다.
  - 사용자의 최초 판단(judgments)은 DB 트리거로 수정/삭제를 막는다.
날짜는 모두 ISO 문자열('YYYY-MM-DD')이며, 문자열 비교가 곧 날짜 비교다.
"""
import sqlite3

from . import config

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS events (
    id            INTEGER PRIMARY KEY,
    title         TEXT NOT NULL,
    category      TEXT NOT NULL,
    occurred_at   TEXT NOT NULL,          -- 실제 발생일
    published_at  TEXT NOT NULL,          -- 최초 공개일 (블라인드 필터의 기준)
    summary       TEXT,
    background    TEXT,                   -- 배경과 원인
    transmission  TEXT,                   -- 주식시장 영향 경로 (가능성)
    data_origin   TEXT NOT NULL DEFAULT 'user'
                  CHECK (data_origin IN ('seed', 'api', 'user')),
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_events_published ON events(published_at);

CREATE TABLE IF NOT EXISTS event_tickers (
    event_id  INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    ticker    TEXT NOT NULL,
    role      TEXT NOT NULL DEFAULT 'company'
              CHECK (role IN ('company', 'index', 'industry')),
    PRIMARY KEY (event_id, ticker)
);

CREATE TABLE IF NOT EXISTS sources (
    id            INTEGER PRIMARY KEY,
    event_id      INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name          TEXT NOT NULL,
    url           TEXT,
    kind          TEXT NOT NULL CHECK (kind IN ('official', 'filing', 'news', 'other')),
    published_at  TEXT NOT NULL
);

-- 전문가 분석: 실제 발언(original)과 AI 해석(ai_summary)을 구분해서 저장
CREATE TABLE IF NOT EXISTS analyses (
    id            INTEGER PRIMARY KEY,
    event_id      INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    kind          TEXT NOT NULL CHECK (kind IN ('original', 'ai_summary')),
    analyst_name  TEXT,
    institution   TEXT,
    stated_at     TEXT NOT NULL,          -- 발언일
    published_at  TEXT NOT NULL,          -- 공개일
    content       TEXT NOT NULL,
    direction     TEXT CHECK (direction IN ('up', 'down', 'neutral', 'unclear')),
    rationale     TEXT,
    horizon       TEXT,
    source_id     INTEGER REFERENCES sources(id),
    -- 실제 발언에는 출처가 반드시 있어야 한다 (존재하지 않는 발언 방지)
    CHECK (kind = 'ai_summary' OR source_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS prices (
    ticker  TEXT NOT NULL,
    date    TEXT NOT NULL,
    open REAL, high REAL, low REAL, close REAL, volume INTEGER,
    PRIMARY KEY (ticker, date)
);

-- 경제지표: 관측 대상일(observation_date)과 발표일(release_date)이 다르다
CREATE TABLE IF NOT EXISTS indicators (
    series_id         TEXT NOT NULL,
    observation_date  TEXT NOT NULL,
    release_date      TEXT NOT NULL,
    value             REAL,
    PRIMARY KEY (series_id, observation_date, release_date)
);

-- 사용자 최초 판단: 저장 후 수정/삭제 불가
CREATE TABLE IF NOT EXISTS judgments (
    id                   INTEGER PRIMARY KEY,
    event_id             INTEGER NOT NULL REFERENCES events(id),
    as_of                TEXT NOT NULL,   -- 사용자가 '어느 시점의 투자자'로 판단했는가
    direction            TEXT NOT NULL CHECK (direction IN ('up', 'down', 'neutral')),
    key_factors          TEXT NOT NULL,
    rationale            TEXT NOT NULL,
    expected_change_pct  REAL,
    horizon_days         INTEGER,
    confidence           INTEGER NOT NULL CHECK (confidence BETWEEN 1 AND 5),
    snapshot_json        TEXT,            -- 판단 당시 화면에 보였던 정보 기록
    created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TRIGGER IF NOT EXISTS judgments_no_update
BEFORE UPDATE ON judgments
BEGIN SELECT RAISE(ABORT, '최초 판단은 수정할 수 없습니다. 추가 의견은 judgment_notes에 저장하세요.'); END;
CREATE TRIGGER IF NOT EXISTS judgments_no_delete
BEFORE DELETE ON judgments
BEGIN SELECT RAISE(ABORT, '최초 판단은 삭제할 수 없습니다.'); END;

CREATE TABLE IF NOT EXISTS judgment_notes (
    id           INTEGER PRIMARY KEY,
    judgment_id  INTEGER NOT NULL REFERENCES judgments(id),
    note         TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS outcomes (
    judgment_id       INTEGER PRIMARY KEY REFERENCES judgments(id),
    evaluated_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actual_change_pct REAL,
    review_json       TEXT
);
"""


def get_conn(path=None) -> sqlite3.Connection:
    p = path if path is not None else config.DB_PATH
    if p != ":memory:":
        config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
