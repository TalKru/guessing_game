# game.py
# Core logic for Guessing Number Game
# =================================================================================
# Core Module: Game Logic and Session Tracking
#
# This module encapsulates the core functionality of the Guessing Number Game:
#   - pick_secret(): Generates a 4-digit secret without duplicate digits.
#   - evaluate_guess(): Compares a user guess to the secret and returns
#       a positional feedback string of '+' (correct digit & position),
#       '-' (correct digit, wrong position), or ' ' (no match).
#   - PlayerSession:
#       * Manages a single game session for a player.
#       * Tracks player name, secret number, start time, and guess count.
#       * Provides make_guess() to process guesses and detect victory.
#       * Exposes elapsed_time and calculate_score() for performance metrics.


import random
import time
from typing import Optional

# Scoring constants
GUESS_WEIGHT = 5      # cost per guess
TIME_DIVISOR = 10     # divisor to scale time into score impact


def pick_secret() -> str:
    """
    Generate a 4-digit secret number with no duplicate digits.
    Digits may include '0'.
    Steps:
      1. Create a list of digit characters '0' through '9'.
      2. Randomly select 4 unique digits from this list.
      3. Join the selected digits into a single string.
    Returns:
        A 4-character string, e.g. '5271'.
    """
    all_digits = []
    for d in range(10):  # 0-9
        all_digits.append(str(d))

    # use random.sample to pick 4 unique digits
    # random.sample returns a new list of length 4
    selected_digits = random.sample(all_digits, 4)

    # convert the list of characters into a string
    secret_number = ''.join(selected_digits)
    return secret_number


def evaluate_guess(secret: str, guess: str) -> str:
    """
    Evaluate a guess against the secret.
    For each position i:
      '+' if guess[i] == secret[i]
      '-' if guess[i] is in secret but at a different position
      ' ' (space) otherwise

    Returns a 4-character string showing feedback in positional order.
    """
    feedback = []
    for i, digit in enumerate(guess):
        if digit == secret[i]:
            feedback.append('+')
        elif digit in secret:
            feedback.append('-')
        else:
            feedback.append(' ')

    return ''.join(feedback)


class PlayerSession:
    """
    Tracks a single playthrough: player name, secret, start time, and guesses.
    """
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.secret = pick_secret()
        self.start_time = time.time()
        self.guess_count = 0
        self.solved = False
        self.last_feedback: Optional[str] = None

    def make_guess(self, guess: str) -> str:
        """
        Process a guess string: increment count, evaluate feedback.
        If guess matches secret, mark session as solved.
        Returns feedback string.
        """
        self.guess_count += 1
        self.last_feedback = evaluate_guess(self.secret, guess)
        if self.last_feedback == '++++':  # if all positions correct
            self.solved = True
        return self.last_feedback

    # @property decorator provides a way to define methods that can be accessed like attributes,
    # allowing for access to an object's data
    @property
    def elapsed_time(self) -> float:
        """
        Returns elapsed time in seconds since session start.
        """
        return time.time() - self.start_time

    def calculate_score(self) -> float:
        """
        Compute final score: lower is better.

        Formula:
            score = (guess_count * GUESS_WEIGHT)
                  + (elapsed_time / TIME_DIVISOR)

        How each part contributes:
          - Each guess adds GUESS_WEIGHT points:
              1 guess → 5 points, 4 guesses → 20 points, etc.
          - Every TIME_DIVISOR seconds adds 1 point:
              10 s → 1 point, 30 s → 3 points, 125 s → 12.5 points.

        Returns:
            A float representing the total score.
        """
        raw_score = (self.guess_count * GUESS_WEIGHT) + (self.elapsed_time / TIME_DIVISOR)
        return raw_score



