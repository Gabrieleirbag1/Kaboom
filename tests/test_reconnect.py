"""Issue #10: a player who loses the connection, or restarts the game, gets back to their seat.

At login the server gives each player a secret key. A new connection sending
RECONNECT_|name|key|version takes the seat back, as long as it is still held: during the game
the player was in, and for KABOOM_RECONNECT_GRACE seconds after the drop.
"""
import json
import time

import pytest
import server_utils
from harness import (SLOW_RULES, assert_no_server_errors, make_both_ready, play_until_bob_wins,
                     setup_lobby)


def word_with(syllable: str) -> str:
    return next(w for w in sorted(server_utils.Français_dictionnaire)
                if syllable in w and w.isascii() and w.isalpha())


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


def test_reconnect_in_the_lobby(server, make_client):
    alice, bob = setup_lobby(make_client)
    name, token = bob.name, bob.token
    bob.close()
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|bob\|")

    bob = make_client("bob-again", avatar="robot-ninja-avatar")
    bob.reconnect_as(name, token)
    bob.expect(r"RECONNECTED\|partie1\|alice\|\|False\|False\|0\|False\|")
    bob.expect(r"JOIN_STATE\|GET-PLAYERS\|alice,bob\|")
    alice.expect(r"LOBBY_STATE\|PLAYER-RECO\|bob\|False\|")

    make_both_ready(alice, bob)  # the new connection plays normally
    assert play_until_bob_wins(alice, bob)[0][0] == "bob"
    assert_no_server_errors(server)


def test_ready_state_is_kept(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    bob = drop_and_come_back(make_client, bob)
    bob.expect(r"RECONNECTED\|partie1\|alice\|[^\n]*\|True\|\n")  # last field: bob is still ready
    alice.expect(r"LOBBY_STATE\|PLAYER-RECO\|bob\|True\|")


def test_reconnect_during_a_game(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    alice.start_game("partie1", SLOW_RULES)  # 8 s per turn, 2 lives
    syllable = alice.expect(r"SYLLABE_\|([^|]+)\|alice\|0\|").group(1)

    bob = drop_and_come_back(make_client, bob)
    bob.expect(r"RECONNECTED\|partie1\|alice\|\|False\|True\|0\|True\|")
    state = bob.expect(r"GAME_MESSAGE\|GAME-STATE\|0\|(\{.*?\})\|alice\|([^|]+)\|")
    assert json.loads(state.group(1)) == {"alice": 2, "bob": 2}
    assert state.group(2) == syllable  # bob sees whose turn it is and the syllable

    alice.answer(word_with(syllable), syllable)
    syllable = bob.expect(r"SYLLABE_\|([^|]+)\|bob\|0\|", timeout=3).group(1)
    bob.answer(word_with(syllable), syllable)  # bob plays from his new connection
    bob.expect(r"GAME_MESSAGE\|RIGHT\|bob\|")
    assert_no_server_errors(server)


def test_creator_reconnects_and_starts_the_game(server, make_client):
    alice, bob = setup_lobby(make_client)
    alice = drop_and_come_back(make_client, alice)
    alice.expect(r"RECONNECTED\|partie1\|alice\|")
    bob.expect(r"LOBBY_STATE\|PLAYER-RECO\|alice\|")
    make_both_ready(alice, bob)
    assert play_until_bob_wins(alice, bob)[0][0] == "bob"
    assert_no_server_errors(server)


def test_reconnect_from_the_menu(server, make_client):
    alice = make_client("alice")
    alice.login()
    alice = drop_and_come_back(make_client, alice)
    alice.expect(r"RECONNECTED\|\|\|\|\|\|0\|False\|")
    alice.create_game("partie1")  # can play normally


@pytest.mark.parametrize("name, token", [("bob", "not-the-key"), ("nobody", "x"), ("bob", "")])
def test_wrong_key_or_unknown_player_is_refused(server, make_client, name, token):
    alice, bob = setup_lobby(make_client)
    thief = make_client("thief")
    thief.reconnect_as(name, token)
    thief.expect(r"RECONNECT_FAILED\|")
    alice.expect_nothing(r"PLAYER-RECO", seconds=0.5)


@pytest.mark.server_env(KABOOM_RECONNECT_GRACE="60")
def test_name_is_reserved_while_the_seat_is_held(server, make_client):
    alice, bob = setup_lobby(make_client)
    bob.close()
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|bob\|")
    other = make_client("bob")
    other.send("NEW-USER_|bob|pizza-avatar|2")
    other.expect(r"NAME_ALREADY_USED\|")


@pytest.mark.server_env(KABOOM_RECONNECT_GRACE="1")
def test_seat_is_freed_after_the_grace_period(server, make_client):
    alice, bob = setup_lobby(make_client)
    name, token = bob.name, bob.token
    bob.close()
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|bob\|")
    alice.expect(r"LOBBY_STATE\|LEAVE-GAME\|partie1\|bob\|", timeout=4)

    late = make_client("late")
    late.reconnect_as(name, token)
    late.expect(r"RECONNECT_FAILED\|")
    make_client("bob").login()  # the name is free again


@pytest.mark.server_env(KABOOM_RECONNECT_GRACE="60")
def test_quitting_frees_the_seat_at_once(server, make_client):
    alice, bob = setup_lobby(make_client)
    bob.send("QUIT_|")
    bob.close()
    alice.expect(r"LOBBY_STATE\|LEAVE-GAME\|partie1\|bob\|", timeout=3)


@pytest.mark.server_env(KABOOM_RECONNECT_GRACE="60")
def test_game_restarted_before_the_server_noticed(server, make_client):
    """The old connection is still open: the new one takes over and the old one is closed."""
    alice, bob = setup_lobby(make_client)
    restarted = make_client("bob-restarted", avatar="robot-ninja-avatar")
    restarted.reconnect_as("bob", bob.token)
    restarted.expect(r"RECONNECTED\|partie1\|")
    bob.expect(r"COMMAND_\|SESSION-TAKEN\|")  # the old game window stops reconnecting
    alice.expect(r"LOBBY_STATE\|PLAYER-RECO\|bob\|")
    alice.expect_nothing(r"PLAYER-DECO\|bob|LEAVE-GAME\|partie1\|bob", seconds=1.5)
    make_both_ready(alice, restarted)
    assert_no_server_errors(server)


def test_ping_gets_an_answer(server, make_client):
    player = make_client("alice")
    player.send("PING_|")
    player.expect(r"PONG_\|")


@pytest.mark.server_env(KABOOM_IDLE_TIMEOUT="2", KABOOM_RECONNECT_GRACE="60")
def test_silent_connection_counts_as_lost(server, make_client):
    """A connection can die without being closed (wifi lost): no PING_ for a while = lost."""
    alice, bob = setup_lobby(make_client)
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:  # alice keeps pinging, bob says nothing
        alice.send("PING_|", gap=0.5)
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|bob\|")
    bob = drop_and_come_back(make_client, bob)
    bob.expect(r"RECONNECTED\|partie1\|")


def test_reconnect_over_bad_network(server, make_client, make_proxy):
    proxy = make_proxy(merge=True, split=True, seed=4)
    alice, bob = setup_lobby(make_client, via=proxy)
    bob = drop_and_come_back(make_client, bob, via=proxy)
    bob.expect(r"RECONNECTED\|partie1\|", timeout=15)
    make_both_ready(alice, bob)
    assert play_until_bob_wins(alice, bob, timeout=20)[0][0] == "bob"
    assert_no_server_errors(server)
