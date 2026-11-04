"""End-to-end tests: the real server + headless players over real sockets.

The first group uses a direct local connection: it describes how the game works today
and must stay green.

The second group goes through BadNetworkProxy, which behaves like the internet (messages merged
together or cut into pieces). Those tests show the production-only bugs: they are marked
xfail until the message framing fix (issue #9). When that fix lands they will start passing,
and pytest will report them as XPASS -> remove the xfail marker.
"""
import ast
import re

import pytest
import server_utils
from harness import FAST_RULES, SLOW_RULES

NO_FRAMING = pytest.mark.xfail(
    strict=True, reason="server reads one message per recv(): no message framing yet (#9)")


def setup_lobby(make_client, game="partie1", creator_name="alice", joiner_name="bob", via=None):
    """alice creates `game`, bob joins it. Returns (alice, bob)."""
    alice = make_client(creator_name, via=via)
    alice.login()
    alice.create_game(game)

    bob = make_client(joiner_name, avatar="robot-ninja-avatar", via=via)
    bob.login()
    bob.open_join_menu()
    bob.expect(rf"GAME_CREATED\|{game}\|False\|1\|Français\|")
    bob.join_game(game)
    for player in (alice, bob):
        player.expect(rf"JOIN_STATE\|GET-PLAYERS\|{creator_name},{joiner_name}\|")
    return alice, bob


def make_both_ready(alice, bob):
    alice.ready(creator=True)
    bob.ready(creator=False)
    for player in (alice, bob):
        player.expect(r"LOBBY_STATE\|READY\|alice\|True\|")
        player.expect(r"LOBBY_STATE\|READY\|bob\|True\|")


def assert_no_server_errors(server):
    errors = server.error_log()
    assert "Traceback" not in errors and "Exception" not in errors, errors


# --- Direct connection: current behaviour ---------------------------------------------------

def test_login_rejects_duplicate_name(server, make_client):
    make_client("alice").login()
    other = make_client("alice")
    other.send("NEW-USER_|alice|pizza-avatar")
    other.expect(r"NAME_ALREADY_USED\|")


def test_create_join_and_ready(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    assert_no_server_errors(server)


def test_full_game_ends_with_ranking(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    alice.start_game("partie1", FAST_RULES)

    for player in (alice, bob):
        player.expect(r"GAME_MESSAGE\|GAME-STARTED\|partie1\|0\|")
        player.expect(r"GAME_MESSAGE\|LIFES-RULES\|1\|alice,bob\|")
        player.expect(r"SYLLABE_\|[^|]+\|alice\|0\|")
    # alice does not answer: her only life is lost, bob wins.
    alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|alice\|")
    ended = bob.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|(\[.*?\]\])\|", timeout=15)
    ranking = ast.literal_eval(ended.group(1))
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


# --- Through a bad network: production-only bugs ----------------------------------------------

@NO_FRAMING
def test_login_when_packets_are_cut(server, make_client, make_proxy):
    """Over the internet one message can arrive in several pieces."""
    proxy = make_proxy(merge=False, split=True)
    make_client("alice", via=proxy).login()


@NO_FRAMING
def test_two_quick_messages_are_both_handled(server, make_client, make_proxy):
    """Over the internet two messages sent close together can arrive as one packet.
    Here bob clicks Ready right after joining: the server drops the Ready."""
    proxy = make_proxy(merge=True, split=False, delay=0.1)
    alice, _ = setup_lobby(make_client, via=None)
    carol = make_client("carol", via=proxy, gap=0.3)  # slow enough that nothing else gets merged
    carol.login()
    carol.open_join_menu()
    carol.send("JOIN-GAME_|partie1|password|carol")
    carol.expect(r"JOIN_STATE\|GAME-JOINED\|partie1\|")
    carol.send("JOIN-GAME-AS-A-PLAYER_|carol|partie1|pizza-avatar", gap=0)
    carol.ready(creator=False)  # sent right after the join -> both arrive in one packet
    alice.expect(r"JOIN_STATE\|GET-PLAYERS\|alice,bob,carol\|")  # the join is handled...
    alice.expect(r"LOBBY_STATE\|READY\|carol\|True\|")         # ...but the Ready is lost


@NO_FRAMING
def test_full_game_over_bad_network(server, make_client, make_proxy):
    proxy = make_proxy(merge=True, split=True, seed=1)
    alice, bob = setup_lobby(make_client, via=proxy)
    make_both_ready(alice, bob)
    alice.start_game("partie1", FAST_RULES)
    bob.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|", timeout=20)


def test_proxy_cuts_and_merges_data():
    """Sanity check of the test tool itself."""
    from harness import BadNetworkProxy
    proxy = BadNetworkProxy(target_port=1, seed=3)
    pieces = proxy._cut(b"NEW-USER_|alice|pizza-avatar")
    assert len(pieces) >= 2 and b"".join(pieces) == b"NEW-USER_|alice|pizza-avatar"
    proxy.close()


@pytest.mark.parametrize("name", ["jean_pierre", "Zoé"])
def test_names_with_underscore_or_accents(server, make_client, name):
    """Names are sent as-is today. The Qt client splits messages on '_' (manage_response),
    so this test only checks the server side."""
    player = make_client(name)
    player.login()
    player.create_game(f"partie_{name}")
    other = make_client("bob")
    other.login()
    other.open_join_menu()
    other.expect(re.escape(f"GAME_CREATED|partie_{name}|False|1|Français|"))
