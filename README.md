# Guessing Number Game

A simple command-line game where the computer picks a unique 4-digit number and the player tries to guess it. After each guess, feedback is provided:

* **`+`** for each digit that is correct and in the right position.
* **`-`** for each digit that is correct but in the wrong position.
* **` ` (space)** for digits that are not in the secret number.

The player’s performance is scored based on number of guesses and time taken. All sessions are recorded in an SQLite database, and a global leaderboard shows top performers.

---

## Project Structure

```
guessing_game/
├── src/
│   ├── __init__.py
│   ├── game.py           # Core game logic and session tracking
│   ├── storage.py        # SQLite - DB
│   └── cli.py            # Command-line interface (user interaction)
├── tests/
│   ├── test_game.py      # Unit tests for game logic and session class
│   └── test_storage.py   # Tests for database operations and leaderboard
├── pytest.ini            # pytest config
├── requirements.txt      
└── README.md             
```

---

## Getting Started

1. **Create and activate a virtual environment** (optional but recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .\.venv\Scripts\activate  # Windows
   ```

2. **Install dependencies** (Only for tests):

   ```bash
   pip install pytest
   ```
   OR
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game**:

   ```bash
   python src\cli.py 
   ```

4. **Run the test suite, in command line**:

   ```bash
   pytest
   ```

---

## Design Overview

### `game.py`

* **`pick_secret()`**: Uses `random.sample` to generate a 4-digit string without duplicates.
* **`evaluate_guess(secret, guess)`**: Returns a 4-character feedback string of `+`, `-`, or space for each digit position.
* **`PlayerSession`**: Tracks a single playthrough, including:

  * Player name and secret number
  * Start time and guess count
  * Methods to process guesses (`make_guess`) and compute elapsed time and final score

### `storage.py`

* Uses SQLite (via Python’s `sqlite3`) to store all completed sessions in `scores.db`.
* **`init_db()`**: Creates the `scores` table and indexes if not present.
* **`save_session(session)`**: Inserts a solved `PlayerSession`, enforcing the solved state.
* **`get_top_n(n)`**: Fetches the lowest-`score` records, tied by most recent play date.

> **Why SQLite?** A lightweight, serverless database, SQL querying—without the overhead of external servers.

### `cli.py`

* Entry point to run the game in a terminal.
* Prompts for player name, collects/validates guesses, displays feedback, and handles exit commands.
* On completion, shows stats, records the session, and prints the global leaderboard.

---

## Testing Strategy

Automated tests are written using **pytest**:

* **`tests/test_game.py`**

  * Verifies secret generation (length & uniqueness).
  * Checks feedback logic for exact, partial, mixed, and no-match scenarios.
  * Tests `PlayerSession` flow, including state transitions and score calculation (using `monkeypatch` to control timing).

* **`tests/test_storage.py`**

  * Ensures `init_db()` creates the database file and schema.
  * Validates saving sessions with controlled timestamps, then retrieves the top leaderboard entries in correct order.
  * Confirms that attempting to save an unsolved session raises a `ValueError`.

Run `pytest` to see all tests pass. Coverage can be extended if needed.

---

**Enjoy playing and analyzing your performance!**
   ```bash
   Version: 1.0.1
   Author: Tal Kruchinin
   Date: 07.08.2025
   ```



