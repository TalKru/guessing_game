# tests/test_game.py
import pytest
import time as time_module
from game import pick_secret, evaluate_guess, PlayerSession


def test_pick_secret_length_and_uniqueness():
    secret = pick_secret()
    assert len(secret) == 4, "Secret should be 4 digits"
    assert secret.isdigit(), "Secret should contain only digits"
    assert len(set(secret)) == 4, "Secret digits should be unique"


@pytest.mark.parametrize(
    "secret, guess, expected_feedback",
    [
        ('1234', '1234', '++++'),  # all correct
        ('1234', '5678', '    '),  # all wrong
        ('1234', '4321', '----'),  # all digits right but wrong order
        ('1234', '1523', '+ --'),
        ('4321', '1234', '----'),
        ('0561', '0781', '+  +'),
        ('0001', '1000', '-++-'),
        ('9876', '6789', '----'),
        ('0123', '0123', '++++'),
        ('0123', '4567', '    ')
    ]
)
def test_evaluate_guess_various(secret, guess, expected_feedback):
    feedback = evaluate_guess(secret, guess)

    assert feedback == expected_feedback, (
        f"For secret={secret} and guess={guess}, "
        f"expected {expected_feedback} but got {feedback}"
    )

# def test_evaluate_guess_exact_match():
#     secret = '1234'
#     guess = '1234'
#     feedback = evaluate_guess(secret, guess)
#     assert feedback == '++++', "All digits correct should yield '++++'"


# def test_evaluate_guess_no_matches():
#     secret = '1234'
#     guess = '5678'
#     feedback = evaluate_guess(secret, guess)
#     assert feedback == '    ', "No matching digits should yield four spaces"


# def test_evaluate_guess_all_partial_matches():
#     secret = '1234'
#     guess = '4321'
#     # Each digit exists but in wrong position
#     feedback = evaluate_guess(secret, guess)
#     assert feedback == '----', f"Expected '----', got '{feedback}'"


# def test_evaluate_guess_mixed_matches():
#     secret = '1234'
#     guess = '1523'
#     # Position 0: '1' correct (+), pos1 '5' no match, pos2 '2' exists wrong(-), pos3 '3' exists wrong(-)
#     feedback = evaluate_guess(secret, guess)
#     assert feedback == '+ --', f"Expected '+ --', got '{feedback}'"


def test_player_session_flow_and_score(monkeypatch):
    # Create session and fix secret + time
    session = PlayerSession('Tester')
    session.secret = '5678'
    start = 1000.0
    monkeypatch.setattr(time_module, 'time', lambda: start)
    session.start_time = start

    # First guess (wrong)
    monkeypatch.setattr(time_module, 'time', lambda: start + 5)
    fb1 = session.make_guess('1234')
    assert fb1 == '    '
    assert session.guess_count == 1
    assert not session.solved

    # Second guess (partial)
    monkeypatch.setattr(time_module, 'time', lambda: start + 12)
    fb2 = session.make_guess('5167')
    # '5' is correct pos0(+), '6' and '7' partial(-)
    assert fb2 == '+ --', f"Expected '+ --', got '{fb2}'"
    assert session.guess_count == 2
    assert not session.solved

    # Third guess (correct)
    monkeypatch.setattr(time_module, 'time', lambda: start + 20)
    fb3 = session.make_guess('5678')
    assert fb3 == '++++'
    assert session.solved
    assert session.guess_count == 3

    # Test elapsed_time property
    elapsed = session.elapsed_time
    assert pytest.approx(elapsed, rel=1e-3) == (start + 20) - start

    # Test calculate_score: (3*5) + (elapsed_time/10)
    expected_score = (3 * 5) + ((elapsed) / 10)
    assert pytest.approx(session.calculate_score(), rel=1e-3) == expected_score

