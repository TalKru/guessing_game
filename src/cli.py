# cli.py
# =========================
# Command-Line Interface for Guessing Number Game
#
# This script ties together the game logic and storage layers:
#   - Prompts the user for their name and optional commands.
#   - Manages the gameplay loop: input, validation, feedback display.
#   - On game completion, computes score, saves session, and displays leaderboard.

import sys
import time
from typing import Optional, List, Tuple
from game import PlayerSession
import storage

EXIT_COMMANDS = {'q', 'quit', 'exit'}


def prompt_player_name() -> str:
    name = input("Enter your name: ").strip()
    while not name:
        print("Name cannot be empty. Please enter your name.")
        name = input("Enter your name: ").strip()
    return name


def prompt_guess() -> Optional[str]:
    """
    Prompt the user for a 4-digit guess or an exit command.
    Returns the guess string or None if the user wants to quit.
    """
    guess = input("Enter your 4-digit guess (or 'q' to quit): ").strip()
    if guess.lower() in EXIT_COMMANDS:
        return None
    return guess


def validate_guess(guess: str) -> bool:
    """
    Checks that the guess is exactly 4 unique digits.
    Returns True if valid, False otherwise.
    """
    if len(guess) != 4:
        print("Invalid input: Guess must be exactly 4 digits.")
        return False
    if not guess.isdigit():
        print("Invalid input: Guess must only contain digits (0-9).")
        return False
    if len(set(guess)) != 4:
        print("Invalid input: Guess must have no duplicate digits.")
        return False
    return True


def display_feedback(feedback: str) -> None:
    """
    Prints the feedback string to the console, showing '+' '-' or spaces.
    """
    print(f"Feedback: [{feedback}]")


def display_leaderboard(top_sessions: List[Tuple[str, int, float, float, str]]) -> None:
    """
    Display the global top scores.
    """
    print("\n=== Global Leaderboard ===")
    header = f"{'Rank':<4}  {'Name':<10} {'Guesses':<7} {'Time(s)':<8} {'Score':<6} Played At"
    print(header)
    for idx, (name, guesses, tsec, score, played_at) in enumerate(top_sessions, start=1):
        line = f"{idx:<4}  {name:<10} {guesses:^7}  {tsec:^8.1f}  {score:^6.1f}  {played_at}"
        print(line)
    print("==========================\n")


def main():
    # Initialize the database
    storage.init_db()

    print("Welcome to the Guessing Number Game!")

    while True:
        player_name = prompt_player_name()
        session = PlayerSession(player_name)

        print(f"\nA new secret number has been generated. Start guessing, {player_name}!")

        # Gameplay loop
        while not session.solved:
            guess = prompt_guess()
            if guess is None:
                print("Exiting the game. Goodbye!")
                sys.exit(0)

            if not validate_guess(guess):
                continue

            feedback = session.make_guess(guess)
            display_feedback(feedback)

        # Game solved
        elapsed = session.elapsed_time
        score = session.calculate_score()
        print(f"\nCongratulations, {player_name}! You solved the puzzle in {session.guess_count} guesses and {elapsed:.1f} seconds.")
        print(f"Your score: {score:.1f} (lower is better)")

        # Save and show leaderboard
        storage.save_session(session)
        top_sessions = storage.get_top_n()
        display_leaderboard(top_sessions)

        # Prompt for replay
        again = input("Play again? (y/n): ").strip().lower()
        if again != 'y':
            print("Thanks for playing! Goodbye.")
            break


if __name__ == '__main__':
    main()
