"""Issue #10: a player who loses the connection, or restarts the game, during a running game gets
back to their seat.

At login the server gives each player a secret key. A new connection sending
RECONNECT_|name|key|version takes the seat back while the player's game is running. Outside a
running game (menu, lobby, game over) a dropped player is removed at once: there is nothing to
come back to.
"""
import json
import time

import pytest
import server_utils
from harness import (FAST_RULES, SLOW_RULES, assert_no_server_errors, make_both_ready,
                     play_until_bob_wins, setup_lobby)

LONG_TURNS = [20, 20, 2, 2, 3, 1, 0]  # the game keeps running during the test


def word_with(syllable: str) -> str:
    return next(w for w in sorted(server_utils.Français_dictionnaire)
                if syllable in w and w.isascii() and w.isalpha())


def running_game(make_client, rules=LONG_TURNS, via=None):
    """alice (creator) and bob in a running game; returns (alice, bob, first syllable)."""
    alice, bob = setup_lobby(make_client, via=via)
    make_both_ready(alice, bob)
    alice.start_game("partie1", rules)
    syllable = alice.expect(r"SYLLABE_\|([^|]+)\|alice\|0\|", timeout=10).group(1)
    return alice, bob, syllable


def drop_and_come_back(make_client, player, via=None):
    """Close `player`'s connection, open a new one and reconnect with the saved key."""
    name, token = player.name, player.token
    player.close()
    back = make_client(f"{name}-again", avatar=player.avatar, via=via)
    back.reconnect_as(name, token)
    return back


def test_login_gives_a_secret_key(server, make_client):
    alice, bob = make_client("alice"), make_client("bob")
    alice.login()
    bob.login()
    assert len(alice.token) >= 16 and alice.token != bob.token


# --- During a running game: the seat is kept ---------------------------------------------------

def test_reconnect_during_a_game(server, make_client):
    alice, bob, syllable = running_game(make_client, rules=SLOW_RULES)
    bob = drop_and_come_back(make_client, bob)
    bob.expect(r"RECONNECTED\|partie1\|alice\|\|False\|True\|0\|True\|")  # in game, ready
    bob.expect(r"JOIN_STATE\|GET-PLAYERS\|alice,bob\|[^|]*\|True,True\|")
    state = bob.expect(r"GAME_MESSAGE\|GAME-STATE\|0\|(\{.*?\})\|alice\|([^|]+)\|")
    assert json.loads(state.group(1)) == {"alice": 2, "bob": 2}
    assert state.group(2) == syllable  # bob sees whose turn it is and the syllable
    alice.expect(r"LOBBY_STATE\|PLAYER-RECO\|bob\|True\|")

    alice.answer(word_with(syllable), syllable)
    syllable = bob.expect(r"SYLLABE_\|([^|]+)\|bob\|0\|", timeout=3).group(1)
    bob.answer(word_with(syllable), syllable)  # bob plays from his new connection
    bob.expect(r"GAME_MESSAGE\|RIGHT\|bob\|")
    assert_no_server_errors(server)


def test_creator_reconnects_during_a_game_and_starts_the_next(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    alice.start_game("partie1", FAST_RULES)
    bob.expect(r"GAME_MESSAGE\|GAME-STARTED\|")
    alice = drop_and_come_back(make_client, alice)
    alice.expect(r"RECONNECTED\|partie1\|alice\|")
    bob.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|", timeout=15)
    make_both_ready(alice, bob)  # still the creator: can start the next game
    assert play_until_bob_wins(alice, bob)[0][0] == "bob"
    assert_no_server_errors(server)


def test_name_is_reserved_while_the_game_runs(server, make_client):
    alice, bob, _ = running_game(make_client)
    bob.close()
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|bob\|")
    other = make_client("bob")
    other.send("NEW-USER_|bob|pizza-avatar|2")
    other.expect(r"NAME_ALREADY_USED\|")


def test_seat_is_freed_when_the_game_ends(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    alice.start_game("partie1", FAST_RULES)
    bob.expect(r"GAME_MESSAGE\|GAME-STARTED\|")
    name, token = bob.name, bob.token
    bob.close()
    alice.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|", timeout=15)
    alice.expect(r"LOBBY_STATE\|LEAVE-GAME\|partie1\|bob\|", timeout=2)  # not shown in red anymore

    late = make_client("late")
    late.reconnect_as(name, token)
    late.expect(r"RECONNECT_FAILED\|")
    make_client("bob").login()  # the name is free again


@pytest.mark.parametrize("name, token", [("bob", "not-the-key"), ("nobody", "x"), ("bob", "")])
def test_wrong_key_or_unknown_player_is_refused(server, make_client, name, token):
    alice, bob, _ = running_game(make_client)
    thief = make_client("thief")
    thief.reconnect_as(name, token)
    thief.expect(r"RECONNECT_FAILED\|")
    alice.expect_nothing(r"PLAYER-RECO", seconds=0.5)


def test_game_restarted_before_the_server_noticed(server, make_client):
    """The old connection is still open: the new one takes over and the old one is closed."""
    alice, bob, _ = running_game(make_client)
    restarted = make_client("bob-restarted", avatar="robot-ninja-avatar")
    restarted.reconnect_as("bob", bob.token)
    restarted.expect(r"RECONNECTED\|partie1\|")
    bob.expect(r"COMMAND_\|SESSION-TAKEN\|")  # the old game window stops reconnecting
    alice.expect(r"LOBBY_STATE\|PLAYER-RECO\|bob\|")
    alice.expect_nothing(r"PLAYER-DECO\|bob|LEAVE-GAME\|partie1\|bob", seconds=1.5)
    assert_no_server_errors(server)


def test_reconnect_over_bad_network(server, make_client, make_proxy):
    proxy = make_proxy(merge=True, split=True, seed=4)
    alice, bob, _ = running_game(make_client, via=proxy)
    bob = drop_and_come_back(make_client, bob, via=proxy)
    bob.expect(r"RECONNECTED\|partie1\|", timeout=15)
    bob.expect(r"GAME_MESSAGE\|GAME-STATE\|", timeout=15)
    assert_no_server_errors(server)


# --- Outside a running game: removed at once, no reconnection -----------------------------------

def test_dropped_in_the_lobby_is_removed_at_once(server, make_client):
    alice, bob = setup_lobby(make_client)
    name, token = bob.name, bob.token
    bob.close()
    alice.expect(r"LOBBY_STATE\|LEAVE-GAME\|partie1\|bob\|", timeout=2)
    back = make_client("bob-again")
    back.reconnect_as(name, token)
    back.expect(r"RECONNECT_FAILED\|")
    make_client("bob").login()  # the name is free


def test_no_reconnection_from_the_menu(server, make_client):
    alice = make_client("alice")
    alice.login()
    back = drop_and_come_back(make_client, alice)
    back.expect(r"RECONNECT_FAILED\|")


def test_restarted_in_the_lobby_before_the_server_noticed(server, make_client):
    """The old connection is still open but no game runs: it is closed, the player is removed and
    can log in again right away (instead of "name already used")."""
    alice, bob = setup_lobby(make_client)
    restarted = make_client("bob-restarted")
    restarted.reconnect_as("bob", bob.token)
    restarted.expect(r"RECONNECT_FAILED\|")
    bob.expect(r"COMMAND_\|SESSION-TAKEN\|")
    alice.expect(r"LOBBY_STATE\|LEAVE-GAME\|partie1\|bob\|", timeout=2)
    restarted.send("NEW-USER_|bob|pizza-avatar|2")
    restarted.expect(r"NAME_CORRECT\|")


def test_ping_gets_an_answer(server, make_client):
    player = make_client("alice")
    player.send("PING_|")
    player.expect(r"PONG_\|")


@pytest.mark.server_env(KABOOM_IDLE_TIMEOUT="2")
def test_silent_connection_counts_as_lost(server, make_client):
    """A connection can die without being closed (wifi lost): no PING_ for a while = lost."""
    alice, bob = setup_lobby(make_client)
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:  # alice keeps pinging, bob says nothing
        alice.send("PING_|", gap=0.5)
    alice.expect(r"LOBBY_STATE\|LEAVE-GAME\|partie1\|bob\|")
