# tests/test_storage.py
# =========================
# Tests for the storage layer (SQLite) of the Guessing Number Game.
# These tests verify database initialization, data insertion, retrieval logic,
# and error handling when saving invalid sessions.

import os
import sqlite3
import pytest
import time as time_module

from game import PlayerSession
import storage


def test_init_db_creates_file_and_schema(tmp_path):
    """
    Verify that init_db():
      - Creates the database file if it does not exist.
      - Defines the 'scores' table with the correct columns.
      - Is safe to call multiple times without deleting existing data.
    """
    # tmp_path is a pytest fixture providing a temporary directory as a pathlib.Path
    # Define the path for our test database file under that temp directory
    db_file = tmp_path / "leaderboard.db"
    assert not db_file.exists(), "DB file should not exist before init"

    # First call to init_db should create both file and schema
    storage.init_db(db_path=str(db_file))  # convert Path to str for sqlite3
    assert db_file.exists(), "Database file must be created by init_db()"

    # Connect and inspect table schema: PRAGMA table_info returns metadata rows
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(scores);")
    columns_info = cursor.fetchall()  # list of tuples, each col: (cid, name, type, ...)
    # Extract the 'name' field at index 1 from each tuple
    column_names = [col[1] for col in columns_info]
    expected = ['id', 'player_name', 'guesses', 'time_seconds', 'score', 'played_at']
    for col in expected:
        assert col in column_names, f"Column '{col}' must be in scores table"
    conn.close()

    # Insert a dummy record manually to test idempotency of init_db
    conn = sqlite3.connect(str(db_file))
    conn.execute(
        "INSERT INTO scores(player_name, guesses, time_seconds, score, played_at)"
        " VALUES ('X', 1, 1.0, 1.0, '2025-01-01T00:00:00')"
    )
    conn.commit()
    conn.close()

    # Second call to init_db should not delete this record
    storage.init_db(db_path=str(db_file))
    conn = sqlite3.connect(str(db_file))
    count = conn.execute("SELECT COUNT(*) FROM scores;").fetchone()[0]
    conn.close()
    assert count == 1, "init_db() should preserve existing records"


def test_save_and_get_top_n(tmp_path, monkeypatch):
    """
    Test saving multiple solved sessions and retrieving the top N by score.
    We control the session times to produce predictable 'played_at' and scores.
    """
    # Setup fresh database file
    db_file = tmp_path / "leaderboard.db"
    storage.init_db(db_path=str(db_file))

    # Prepare players data: (name, number of guesses, elapsed seconds)
    players_data = [
        ('Alice', 3, 30.0),  # expected score 18.0
        ('Bob',   2, 40.0),  # expected score 14.0
        ('Cara',  4, 20.0),  # expected score 22.0
    ]

    base_time = 1_600_000_000.0  # fixed epoch for reproducibility
    for idx, (name, guesses, elapsed) in enumerate(players_data):
        session = PlayerSession(name)
        session.secret = '0000'       # secret is irrelevant for storage tests
        session.guess_count = guesses
        session.solved = True         # mark solved so save_session does not error

        # Monkeypatch time.time() to simulate session end at known timestamp
        # We set time() to return start + elapsed
        start = base_time + idx * 10
        # Each lambda captures default arg 'now' to ensure correct closure
        monkeypatch.setattr(time_module, 'time', lambda now=start + elapsed: now)
        session.start_time = start      # set start_time to start moment

        # Save the session into SQLite
        storage.save_session(session, db_path=str(db_file))

    # Retrieve the top 2 entries by lowest score (Bob then Alice)
    top_two = storage.get_top_n(n=2, db_path=str(db_file))
    assert len(top_two) == 2, "Should return exactly 2 records"

    # Unpack first and second tuples: (player_name, guesses, time_seconds, score, played_at)
    first_name, *_ = top_two[0]
    second_name, *_ = top_two[1]
    assert first_name == 'Bob',   "Player with lowest score (Bob) should be first"
    assert second_name == 'Alice',"Player with second lowest score (Alice) should be second"


def test_save_session_unsolved_raises(tmp_path):
    """
    Ensure that attempting to save a session that isn't marked solved
    raises a ValueError, as enforced by save_session().
    """
    # / is an overloaded operator in pathlib — it joins paths
    # This equivalent to os.path.join(str(tmp_path), "leaderboard.db").
    db_file = tmp_path / "leaderboard.db"
    storage.init_db(db_path=str(db_file))  # initialize empty database

    session = PlayerSession('Tester')
    # session.solved is a boolean attribute set by PlayerSession.make_guess()
    # It indicates whether the player has successfully guessed the secret.
    assert session.solved is False  # no guesses yet, so not solved

    # Using pytest.raises to assert that save_session() fails on unsolved sessions
    # The 'with' block captures the exception context as 'excinfo'
    with pytest.raises(ValueError) as excinfo:
        # Attempt to save without marking session.solved = True
        storage.save_session(session, db_path=str(db_file))
    # Verify the exception message contains 'not solved' to confirm correct error
    msg = str(excinfo.value)
    assert 'not solved' in msg.lower(), (
        "Error message should mention that the session is not solved"
    )
