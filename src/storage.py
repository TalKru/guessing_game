# storage.py
# =========================
# Storage Module: Database Operations for Guessing Number Game
#
# This module handles all interactions with the SQLite database:
#   - init_db(): Create the 'scores' table and index if they don't exist.
#   - save_session(): Persist a completed PlayerSession to the database.
#   - get_top_n(): Retrieve the top N sessions ordered by best (lowest) score.

import sqlite3
import time
from typing import List, Tuple
from game import PlayerSession

# Database filename
DB_FILENAME = "scores.db"

# SQL statement to create the main scores table if it doesn't exist.
# Columns:
#   id           INTEGER PRIMARY KEY AUTOINCREMENT  -- unique row identifier
#   player_name  TEXT    NOT NULL                  -- user name
#   guesses      INTEGER NOT NULL                  -- number of guesses taken
#   time_seconds REAL    NOT NULL                  -- elapsed time in seconds
#   score        REAL    NOT NULL                  -- calculated score
#   played_at    TEXT    NOT NULL                  -- ISO-8601 timestamp of completion
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS scores (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name   TEXT    NOT NULL,
    guesses       INTEGER NOT NULL,
    time_seconds  REAL    NOT NULL,
    score         REAL    NOT NULL,
    played_at     TEXT    NOT NULL  -- ISO-8601 timestamp
);
"""

# SQL statement to create an index on (score, played_at) for fast leaderboard queries.
# ORDER BY score ASC (best/lowest first), played_at DESC (newest first for tie-breakers).
CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_scores_score_played_at
    ON scores(score ASC, played_at DESC);
"""

# SQL template for inserting a new session record.
# Uses positional placeholders (?) to prevent SQL injection and allow parameter binding.
INSERT_SESSION_SQL = """
INSERT INTO scores (player_name, guesses, time_seconds, score, played_at)
VALUES (?, ?, ?, ?, ?);
"""

# SQL template for selecting the top N records.
# Sort by score ascending (best first) and played_at descending to break ties by recency.
SELECT_TOP_N_SQL = """
SELECT player_name, guesses, time_seconds, score, played_at
FROM scores
ORDER BY score ASC, played_at DESC
LIMIT ?;
"""


def init_db(db_path: str = DB_FILENAME) -> None:
    """
    Initialize the SQLite database: create table and index if needed.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    cursor.execute(CREATE_INDEX_SQL)
    conn.commit()
    conn.close()


def save_session(session: PlayerSession, db_path: str = DB_FILENAME) -> None:
    """
    Save a completed PlayerSession to the database.
    Parameters:
        session: a PlayerSession instance that has been solved.
    """
    if not session.solved:
        raise ValueError("Cannot save session: game not solved yet.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Compute the played_at timestamp as ISO-8601
    played_at = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(session.start_time + session.elapsed_time))

    cursor.execute(
        INSERT_SESSION_SQL,
        (
            session.player_name,
            session.guess_count,
            session.elapsed_time,
            session.calculate_score(),
            played_at
        )
    )
    conn.commit()
    conn.close()


def get_top_n(n: int = 10, db_path: str = DB_FILENAME) -> List[Tuple[str, int, float, float, str]]:
    """
    Retrieve the top N sessions from the database.
    Returns a list of tuples:
        (player_name, guesses, time_seconds, score, played_at)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(SELECT_TOP_N_SQL, (n,))
    rows = cursor.fetchall()
    conn.close()
    return rows
