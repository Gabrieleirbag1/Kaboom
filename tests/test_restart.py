"""Issue #13: playing several games in a row in the same lobby.

Players reported having to delete the lobby and create a new one to play again, mostly in
production. These tests replay the lobby after a game ends, also over a bad network.
"""
import server_utils
from harness import (FAST_RULES, SLOW_RULES, assert_no_server_errors, make_both_ready,
                     play_until_bob_wins, setup_lobby)


def word_with(syllable: str) -> str:
    return next(w for w in sorted(server_utils.Français_dictionnaire)
                if syllable in w and w.isascii() and w.isalpha())


def test_second_game_in_the_same_lobby(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    assert play_until_bob_wins(alice, bob)[0][0] == "bob"

    make_both_ready(alice, bob)
    assert play_until_bob_wins(alice, bob)[0][0] == "bob"
    assert_no_server_errors(server)


def test_second_game_over_bad_network(server, make_client, make_proxy):
    proxy = make_proxy(merge=True, split=True, seed=2)
    alice, bob = setup_lobby(make_client, via=proxy)
    for _ in range(2):
        make_both_ready(alice, bob)
        assert play_until_bob_wins(alice, bob, timeout=20)[0][0] == "bob"
    assert_no_server_errors(server)


def test_ready_clicked_right_after_the_game_ends_is_kept(server, make_client):
    """The end-of-game reset must not erase a Ready sent just after GAME-ENDED."""
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    alice.start_game("partie1", FAST_RULES)
    bob.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|", timeout=15)
    bob.ready(creator=False, gap=0)  # as fast as possible
    alice.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|")
    alice.expect(r"LOBBY_STATE\|READY\|bob\|True\|")

    alice.ready(creator=True)
    alice.expect(r"LOBBY_STATE\|READY\|alice\|True\|")
    alice.start_game("partie1", SLOW_RULES)
    # Both players must be in the new game (if bob's Ready was lost, only alice is listed).
    alice.expect(r"GAME_MESSAGE\|LIFES-RULES\|2\|alice,bob\|")
    assert_no_server_errors(server)


def test_answers_still_work_in_the_second_game(server, make_client):
    """A right answer must end the turn at once in the second game too (no leftover game state)."""
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    play_until_bob_wins(alice, bob)

    make_both_ready(alice, bob)
    alice.start_game("partie1", SLOW_RULES)  # 8 s per turn
    syllable = alice.expect(r"SYLLABE_\|([^|]+)\|alice\|0\|").group(1)
    alice.answer(word_with(syllable), syllable)
    alice.expect(r"GAME_MESSAGE\|RIGHT\|alice\|")
    syllable = bob.expect(r"SYLLABE_\|([^|]+)\|bob\|0\|", timeout=3).group(1)  # not after 8 s
    bob.answer(word_with(syllable), syllable)
    bob.expect(r"GAME_MESSAGE\|RIGHT\|bob\|")
    alice.expect(r"SYLLABE_\|[^|]+\|alice\|0\|", timeout=3)
    assert_no_server_errors(server)


def test_player_waiting_during_a_game_joins_when_it_ends(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    alice.start_game("partie1", FAST_RULES)
    alice.expect(r"GAME_MESSAGE\|GAME-STARTED\|partie1\|")

    carol = make_client("carol", avatar="cactus-avatar")
    carol.login()
    carol.open_join_menu()
    carol.send("JOIN-GAME_|partie1|password|carol")
    carol.expect(r"JOIN_STATE\|ALREADY-IN-GAME\|partie1\|")
    carol.expect(r"JOIN_STATE\|GAME-JOINED\|partie1\|[^\n]*\|carol\|", timeout=15)  # game ended
    carol.send("JOIN-GAME-AS-A-PLAYER_|carol|partie1|cactus-avatar")
    alice.expect(r"JOIN_STATE\|GET-PLAYERS\|alice,bob,carol\|")

    make_both_ready(alice, bob)
    carol.ready(creator=False)
    alice.expect(r"LOBBY_STATE\|READY\|carol\|True\|")
    alice.start_game("partie1", SLOW_RULES)
    alice.expect(r"GAME_MESSAGE\|LIFES-RULES\|2\|alice,bob,carol\|")
    assert_no_server_errors(server)


def test_new_creator_can_start_the_next_game(server, make_client):
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    play_until_bob_wins(alice, bob)

    alice.leave_game("partie1")
    bob.expect(r"LOBBY_STATE\|NEW-CREATOR\|partie1\|bob\|")

    carol = make_client("carol")
    carol.login()
    carol.open_join_menu()
    carol.expect(r"GAME_CREATED\|partie1\|False\|1\|")
    carol.join_game("partie1")
    bob.expect(r"JOIN_STATE\|GET-PLAYERS\|bob,carol\|")

    bob.ready(creator=True)   # bob is the creator now
    carol.ready(creator=False)
    bob.expect(r"LOBBY_STATE\|READY\|bob\|True\|")
    bob.expect(r"LOBBY_STATE\|READY\|carol\|True\|")
    bob.start_game("partie1", SLOW_RULES)
    bob.expect(r"GAME_MESSAGE\|LIFES-RULES\|2\|bob,carol\|")
    assert_no_server_errors(server)


# --- Connection drops during a game (common in production, rare locally) ---------------------

def three_player_lobby(make_client):
    alice, bob = setup_lobby(make_client)
    carol = make_client("carol", avatar="cactus-avatar")
    carol.login()
    carol.open_join_menu()
    carol.expect(r"GAME_CREATED\|partie1\|")
    carol.join_game("partie1")
    alice.expect(r"JOIN_STATE\|GET-PLAYERS\|alice,bob,carol\|")
    make_both_ready(alice, bob)
    carol.ready(creator=False)
    alice.expect(r"LOBBY_STATE\|READY\|carol\|True\|")
    return alice, bob, carol


def test_restart_after_a_player_dropped_during_the_game(server, make_client):
    alice, bob, carol = three_player_lobby(make_client)
    alice.start_game("partie1", FAST_RULES)
    carol.expect(r"GAME_MESSAGE\|GAME-STARTED\|partie1\|")
    carol.close()  # connection lost
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|carol\|")
    alice.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|", timeout=25)
    alice.expect(r"LOBBY_STATE\|LEAVE-GAME\|partie1\|carol\|", timeout=10)

    make_both_ready(alice, bob)
    alice.start_game("partie1", SLOW_RULES)
    alice.expect(r"GAME_MESSAGE\|LIFES-RULES\|2\|alice,bob\|")
    assert_no_server_errors(server)


def test_restart_after_the_creator_dropped_during_the_game(server, make_client):
    alice, bob, carol = three_player_lobby(make_client)
    alice.start_game("partie1", FAST_RULES)
    bob.expect(r"GAME_MESSAGE\|GAME-STARTED\|partie1\|")
    alice.close()  # the creator's connection is lost
    bob.expect(r"LOBBY_STATE\|PLAYER-DECO\|alice\|")
    bob.expect(r"GAME_MESSAGE\|GAME-ENDED\|partie1\|", timeout=25)
    bob.expect(r"LOBBY_STATE\|NEW-CREATOR\|partie1\|bob\|", timeout=10)

    bob.ready(creator=True)
    carol.ready(creator=False)
    bob.expect(r"LOBBY_STATE\|READY\|bob\|True\|")
    bob.expect(r"LOBBY_STATE\|READY\|carol\|True\|")
    bob.start_game("partie1", SLOW_RULES)
    bob.expect(r"GAME_MESSAGE\|LIFES-RULES\|2\|bob,carol\|")
    assert_no_server_errors(server)
