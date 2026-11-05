"""Issue #24: the server waited a fixed time (3 s, 4.5 s at the end) for the explosion animation.

Now each screen answers ANIMATION-DONE_|round| when its explosion is over: the game goes on as
soon as every connected player is done, and never waits more than KABOOM_ANIMATION_TIMEOUT.
"""
import time

import pytest
from harness import FAST_RULES, assert_no_server_errors, make_both_ready, setup_lobby

TWO_LIVES = [1, 1, 2, 2, 3, 1, 0]  # 1 s per turn, 2 lives: rounds with explosions, then the end


def lobby(make_client, alice_time=0.0, bob_time=0.0):
    alice, bob = setup_lobby(make_client)
    alice.animation_time, bob.animation_time = alice_time, bob_time
    make_both_ready(alice, bob)
    return alice, bob


def time_to_next_turn(alice, bob) -> float:
    """Start a game where nobody answers; seconds between alice's TIME'S-UP and bob's turn."""
    alice.start_game("partie1", TWO_LIVES)
    alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|alice\|1\|")
    start = time.monotonic()
    alice.expect(r"SYLLABE_\|[^|]+\|bob\|", timeout=12)
    return time.monotonic() - start


@pytest.mark.server_env(KABOOM_ANIMATION_TIMEOUT="10")
def test_next_turn_comes_as_soon_as_animations_are_done(server, make_client):
    alice, bob = lobby(make_client, alice_time=0.2, bob_time=0.4)
    assert time_to_next_turn(alice, bob) < 1.2  # it was always 3 s
    assert_no_server_errors(server)


@pytest.mark.server_env(KABOOM_ANIMATION_TIMEOUT="10")
def test_next_turn_waits_for_the_slowest_screen(server, make_client):
    alice, bob = lobby(make_client, alice_time=0.0, bob_time=2.0)  # bob has a slow computer
    assert 1.9 < time_to_next_turn(alice, bob) < 3.0


@pytest.mark.server_env(KABOOM_ANIMATION_TIMEOUT="1.5")
def test_a_screen_that_never_answers_does_not_block_the_game(server, make_client):
    alice, bob = lobby(make_client, alice_time=0.0, bob_time=None)
    assert 1.4 < time_to_next_turn(alice, bob) < 2.5


@pytest.mark.server_env(KABOOM_ANIMATION_TIMEOUT="10")
def test_answer_for_an_old_round_is_ignored(server, make_client):
    alice, bob = lobby(make_client, alice_time=0.0, bob_time=None)
    alice.start_game("partie1", TWO_LIVES)
    alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|alice\|1\|")
    bob.send("ANIMATION-DONE_|0|")  # wrong round
    bob.expect_nothing(r"SYLLABE_\|[^|]+\|bob\|", seconds=1.5)
    bob.send("ANIMATION-DONE_|1|")
    bob.expect(r"SYLLABE_\|[^|]+\|bob\|", timeout=2)


@pytest.mark.server_env(KABOOM_ANIMATION_TIMEOUT="10")
def test_a_disconnected_player_is_not_waited_for(server, make_client):
    alice, bob = setup_lobby(make_client)
    carol = make_client("carol", animation_time=None)  # will drop: never answers
    carol.login()
    carol.open_join_menu()
    carol.expect(r"GAME_CREATED\|partie1\|")
    carol.join_game("partie1")
    alice.expect(r"GET-PLAYERS\|alice,bob,carol\|")
    make_both_ready(alice, bob)
    alice.start_game("partie1", TWO_LIVES)
    carol.expect(r"GAME_MESSAGE\|GAME-STARTED\|")
    carol.close()
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|carol\|")
    alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|alice\|")
    start = time.monotonic()
    alice.expect(r"SYLLABE_\|[^|]+\|bob\|", timeout=12)
    assert time.monotonic() - start < 1.5  # not the 10 s timeout


@pytest.mark.server_env(KABOOM_ANIMATION_TIMEOUT="10")
def test_results_come_right_after_the_last_explosion(server, make_client):
    alice, bob = lobby(make_client, alice_time=0.3, bob_time=0.3)
    alice.start_game("partie1", FAST_RULES)  # 1 life: alice's time's up ends the game
    alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|alice\|")
    start = time.monotonic()
    bob.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|", timeout=12)
    assert time.monotonic() - start < 1.3  # it was always 4.5 s
    assert_no_server_errors(server)


def test_time_is_up_carries_a_round_number(server, make_client):
    alice, bob = lobby(make_client)
    alice.start_game("partie1", TWO_LIVES)
    alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|alice\|1\|")
    alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|bob\|2\|", timeout=6)
