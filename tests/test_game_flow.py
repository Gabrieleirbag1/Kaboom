"""End-to-end tests: the real server + headless players over real sockets.

The first group uses a direct local connection. The second group goes through BadNetworkProxy,
which behaves like the internet (messages merged together or cut into pieces): those used to
fail before messages ended with a newline (issue #9).
"""
import json
import re
import threading

import pytest
import server_utils
from harness import (FAST_RULES, SLOW_RULES, assert_no_server_errors, make_both_ready,
                     play_until_bob_wins, setup_lobby)
from server_protocol import PROTOCOL_VERSION


# --- Direct connection ----------------------------------------------------------------------

def test_login_rejects_duplicate_name(server, make_client):
    make_client("alice").login()
    other = make_client("alice")
    other.send(f"NEW-USER_|alice|pizza-avatar|{PROTOCOL_VERSION}")
    other.expect(r"NAME_ALREADY_USED\|")


def test_login_refuses_old_client_version(server, make_client):
    old = make_client("alice")
    old.send("NEW-USER_|alice|pizza-avatar")  # v1.1 clients send no version
    old.expect(rf"VERSION_MISMATCH\|{PROTOCOL_VERSION}\|")


# A '|' never reaches the server inside a name (it is already a field separator):
# the client checks it before sending, see test_protocol.py.
@pytest.mark.parametrize("name", ["al,ce", "jean_pierre", " "])
def test_login_refuses_invalid_names(server, make_client, name):
    player = make_client("x")
    player.send(f"NEW-USER_|{name}|pizza-avatar|{PROTOCOL_VERSION}")
    player.expect(r"NAME_INVALID\|")


@pytest.mark.parametrize("game", ["a,b", "a#b", "a+b", "   "])
def test_game_name_with_forbidden_character_is_refused(server, make_client, game):
    alice = make_client("alice")
    alice.login()
    alice.send(f"CHECK-GAME-NAME_|{game}||False|")
    alice.expect(r"CHECK_GAME\|GAME-NAME-INVALID\|")


def test_create_join_and_ready(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    assert_no_server_errors(server)


def test_full_game_ends_with_ranking(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    ranking = play_until_bob_wins(alice, bob)
    assert ranking == [["bob", "robot-ninja-avatar"], ["alice", None]]
    assert_no_server_errors(server)


def test_right_and_wrong_answers(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    alice.start_game("partie1", SLOW_RULES)
    syllable = alice.expect(r"SYLLABE_\|([^|]+)\|alice\|0\|").group(1)

    alice.answer("zzzzzz", syllable)
    alice.expect(r"GAME_MESSAGE\|WRONG\|")

    word = next(w for w in sorted(server_utils.Français_dictionnaire)
                if syllable in w and w.isascii() and w.isalpha())
    alice.answer(word, syllable)
    alice.expect(r"GAME_MESSAGE\|RIGHT\|alice\|")
    bob.expect(r"SYLLABE_\|[^|]+\|bob\|0\|")  # turn goes to bob
    assert_no_server_errors(server)


def test_game_names_with_underscore_and_accents(server, make_client):
    """The old client cut messages on '_' (manage_response): game names with '_' broke it."""
    alice, bob = setup_lobby(make_client, game="la_partie_de_Zoé")
    make_both_ready(alice, bob)
    assert_no_server_errors(server)


def test_bad_message_does_not_kill_the_connection(server, make_client):
    """Before, one malformed message crashed this player's server thread: the player was stuck."""
    alice = make_client("alice")
    alice.send("START-GAME_|alice")  # missing fields -> error on the server
    alice.login()                    # the connection still works


def test_eight_players_join_and_leave_at_the_same_time(server, make_client):
    """Many threads change the shared game lists at once: they must stay consistent (#9)."""
    alice = make_client("alice")
    alice.login()
    alice.create_game("bigparty")
    joiners = [make_client(f"joueur{i}") for i in range(7)]  # 1 + 7 = max players
    errors = []

    def join(player):
        try:
            player.login()
            player.open_join_menu()
            player.expect(r"GAME_CREATED\|bigparty\|")
            player.join_game("bigparty")
        except AssertionError as e:
            errors.append(e)

    def run_all(target):
        threads = [threading.Thread(target=target, args=(p,)) for p in joiners]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, errors

    run_all(join)
    for player in joiners:
        alice.expect(rf"JOIN_STATE\|GAME-JOINED\|bigparty\|[^\n]*\|{player.name}\|")
    run_all(lambda player: player.leave_game("bigparty"))
    for player in joiners:
        alice.expect(rf"LOBBY_STATE\|LEAVE-GAME\|bigparty\|{player.name}\|")

    # The game is back to 1 player for someone looking at the list.
    watcher = make_client("watcher")
    watcher.login()
    watcher.open_join_menu()
    watcher.expect(r"GAME_CREATED\|bigparty\|False\|1\|Français\|")
    assert_no_server_errors(server)


# --- Through a bad network (production-like) -------------------------------------------------

@pytest.mark.parametrize("name", ["alice", "Zoé"])
def test_login_when_packets_are_cut(server, make_client, make_proxy, name):
    """Over the internet one message can arrive in several pieces."""
    proxy = make_proxy(merge=False, split=True)
    make_client(name, via=proxy).login()


def test_accented_letter_cut_in_half(server, make_client):
    """'é' is 2 bytes in UTF-8: a packet can end between them."""
    player = make_client("Zoé")
    data = f"NEW-USER_|Zoé|pizza-avatar|{PROTOCOL_VERSION}\n".encode()
    middle = data.index("é".encode()) + 1
    player.send_bytes(data[:middle], gap=0.2)
    player.send_bytes(data[middle:])
    player.expect(r"NAME_CORRECT\|")


def test_two_quick_messages_are_both_handled(server, make_client, make_proxy):
    """Over the internet two messages sent close together can arrive as one packet.
    Here carol clicks Ready right after joining: the server used to drop the Ready."""
    proxy = make_proxy(merge=True, split=False, delay=0.1)
    alice, _ = setup_lobby(make_client, via=None)
    carol = make_client("carol", via=proxy, gap=0.3)  # slow enough that nothing else gets merged
    carol.login()
    carol.open_join_menu()
    carol.send("JOIN-GAME_|partie1|password|carol")
    carol.expect(r"JOIN_STATE\|GAME-JOINED\|partie1\|")
    carol.send("JOIN-GAME-AS-A-PLAYER_|carol|partie1|pizza-avatar", gap=0)
    carol.ready(creator=False)  # sent right after the join -> both arrive in one packet
    alice.expect(r"JOIN_STATE\|GET-PLAYERS\|alice,bob,carol\|")
    alice.expect(r"LOBBY_STATE\|READY\|carol\|True\|")


def test_full_game_over_bad_network(server, make_client, make_proxy):
    proxy = make_proxy(merge=True, split=True, seed=1)
    alice, bob = setup_lobby(make_client, via=proxy)
    make_both_ready(alice, bob)
    ranking = play_until_bob_wins(alice, bob, timeout=20)
    assert ranking[0][0] == "bob"
    assert_no_server_errors(server)


def test_proxy_cuts_and_merges_data():
    """Sanity check of the test tool itself."""
    from harness import BadNetworkProxy
    proxy = BadNetworkProxy(target_port=1, seed=3)
    pieces = proxy._cut(b"NEW-USER_|alice|pizza-avatar")
    assert len(pieces) >= 2 and b"".join(pieces) == b"NEW-USER_|alice|pizza-avatar"
    proxy.close()
