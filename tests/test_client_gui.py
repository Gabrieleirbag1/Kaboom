"""Tests of the real game client (Client/client.py), running off-screen next to the test server.

They cover what the server tests can't see: what the player's screen shows after a reconnection
(#10), the heart and tombstone animations and their end signal (#24), and what quitting keeps.
Fake players (FakeClient) play the other seats.
"""
import os
import signal
import sys
import time

import pytest
import server_utils
from harness import make_both_ready, setup_lobby

pytestmark = pytest.mark.gui

LONG_TURNS = [60, 60, 3, 2, 3, 1, 0]       # nothing happens by itself during the test
SUDDEN_DEATH = [2, 2, 1, 2, 3, 1, 2]       # death mode 2: one life, 2 s per turn


def word_with(syllable: str) -> str:
    return next(w for w in sorted(server_utils.Français_dictionnaire)
                if syllable in w and w.isascii() and w.isalpha())


def green(name: str) -> str:
    return f"<font color='green'>{name}</font>"


def game_with_a_closed_client(make_client, rules, who="bob"):
    """alice (creator) and bob play; `who` closed their game (only the saved session is left).
    Returns (alice, bob, session of `who`, current syllable)."""
    alice, bob = setup_lobby(make_client)
    make_both_ready(alice, bob)
    alice.start_game("partie1", rules)
    syllable = bob.expect(r"SYLLABE_\|([^|]+)\|alice\|").group(1)
    gone = {"alice": alice, "bob": bob}[who]
    session = {"username": gone.name, "token": gone.token, "avatar": gone.avatar}
    gone.close()
    return alice, bob, session, syllable


@pytest.mark.parametrize("who", ["bob", "alice"])  # a player who joined, and the creator
def test_restarting_the_game_goes_straight_back_into_it(server, make_client, make_gui, who):
    alice, bob, session, syllable = game_with_a_closed_client(make_client, LONG_TURNS, who)
    other = bob if who == "alice" else alice
    gui = make_gui(session=session)
    seen = gui.wait_for(lambda st: st["window_visible"] and st.get("hearts", [0])[0] > 0)
    other.expect(rf"LOBBY_STATE\|PLAYER-RECO\|{who}\|True\|")

    assert not any(st.get("login_visible") for st in seen)  # no (black) login window
    state = seen[-1]
    assert state["ingame"]
    assert state["labels"][:2] == [green("alice"), green("bob")]
    assert state["hearts"][:2] == [3, 3]  # the creator used to get 0 hearts
    assert state["syllabe"] == syllable
    assert gui.errors() == ""


def test_connection_drop_reconnects_by_itself(server, make_client, make_gui):
    alice, bob, session, _ = game_with_a_closed_client(make_client, LONG_TURNS)
    gui = make_gui(session=session)
    gui.wait_for(lambda st: st["ingame"] and st.get("hearts", [0])[1] == 3)
    alice.expect(r"PLAYER-RECO\|bob\|")

    gui.call("drop_connection")
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|bob\|")
    alice.expect(r"LOBBY_STATE\|PLAYER-RECO\|bob\|True\|", timeout=20)
    state = gui.wait_for(lambda st: st["ingame"] and st.get("hearts", [0])[1] == 3)[-1]
    assert state["labels"][:2] == [green("alice"), green("bob")]
    assert gui.errors() == ""


def gui_in_lobby(make_client, make_gui):
    """alice (fake) creates a lobby, bob (the real client) logs in and joins it like a player."""
    alice = make_client("alice", avatar="tasse-avatar")
    alice.login()
    alice.create_game("partie1")
    gui = make_gui()
    gui.wait_for(lambda st: st["login_visible"])
    gui.call("login", name="bob")
    gui.wait_for(lambda st: st["window_visible"])
    gui.call("join", game="partie1", player="bob")
    alice.expect(r"JOIN_STATE\|GET-PLAYERS\|alice,bob\|")
    gui.wait_for(lambda st: st.get("labels", [""])[1] == "bob")
    return alice, gui


def play_sudden_death(alice, gui) -> str:
    """Both ready, alice starts a sudden death game. Returns the first syllable (alice's turn)."""
    gui.call("ready")
    alice.expect(r"LOBBY_STATE\|READY\|bob\|True\|")
    alice.ready(creator=True)
    alice.expect(r"LOBBY_STATE\|READY\|alice\|True\|")
    alice.start_game("partie1", SUDDEN_DEATH)
    syllable = alice.expect(r"SYLLABE_\|([^|]+)\|alice\|").group(1)
    gui.wait_for(lambda st: st.get("hearts", [0])[1] == 1)
    return syllable


def test_heart_and_tombstone_come_at_the_end_of_the_explosion_in_every_game(server, make_client, make_gui):
    """bob (the real client) dies in two sudden death games in a row. The heart goes and the
    tombstone appears when the explosion ends; the results come after the tombstone."""
    alice, gui = gui_in_lobby(make_client, make_gui)
    for game in range(2):
        syllable = play_sudden_death(alice, gui)
        alice.answer(word_with(syllable), syllable)  # alice is right, bob never answers
        alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|bob\|", timeout=10)
        exploded = time.monotonic()
        assert gui.state()["hearts"][1] == 1  # the heart stays during the explosion
        alice.expect(r"GAME_MESSAGE\|GAME-ENDED\|", timeout=10)
        results_after = time.monotonic() - exploded
        assert 1.3 < results_after < 4.5, results_after  # explosion + heart + tombstone, no 5 s timeout
        state = gui.wait_for(lambda st: not st["ingame"])[-1]
        assert state["avatars"][1].startswith("tombe"), state["avatars"]
    assert "Animation still running" not in (server.log_dir / "infos.log").read_text()
    assert gui.errors() == ""


def test_quitting_during_a_game_keeps_the_seat(server, make_client, make_gui, tmp_path):
    alice, bob, session, _ = game_with_a_closed_client(make_client, LONG_TURNS)
    gui = make_gui(session=session)
    gui.wait_for(lambda st: st["ingame"] and st.get("hearts", [0])[1] == 3)
    alice.expect(r"PLAYER-RECO\|bob\|")

    gui.call("quit")  # Alt+F4 + OK
    alice.expect(r"LOBBY_STATE\|PLAYER-DECO\|bob\|")
    alice.expect_nothing(r"LEAVE-GAME\|partie1\|bob", seconds=1)
    assert gui.session_file.exists()

    again = make_gui(home=tmp_path / "home")  # same config folder: starts the game again
    again.wait_for(lambda st: st["ingame"] and st.get("hearts", [0])[1] == 3)
    alice.expect(r"PLAYER-RECO\|bob\|True\|")


def test_quitting_after_the_game_frees_the_seat(server, make_client, make_gui):
    alice, gui = gui_in_lobby(make_client, make_gui)
    syllable = play_sudden_death(alice, gui)
    alice.answer(word_with(syllable), syllable)
    gui.wait_for(lambda st: not st["ingame"] and st.get("hearts") is not None, timeout=20)  # game over

    gui.call("quit")
    alice.expect(r"LOBBY_STATE\|LEAVE-GAME\|partie1\|bob\|", timeout=3)  # removed, not red
    assert not gui.session_file.exists()


def test_old_session_shows_the_login_window(server, make_gui):
    gui = make_gui(session={"username": "ghost", "token": "old-key", "avatar": "pizza-avatar"})
    state = gui.wait_for(lambda st: st["login_visible"])[-1]
    assert not state["window_visible"] and state["login_text"] == ""
    assert not gui.session_file.exists()
    gui.call("login", name="zoe")
    gui.wait_for(lambda st: st["window_visible"] and not st["login_visible"])
    assert gui.session_file.exists()


@pytest.mark.skipif(sys.platform == "win32", reason="freezes the server with SIGSTOP")
def test_login_still_works_after_the_server_froze(server, make_gui):
    """Like a server paused in the debugger: the client must not stay stuck on the login window."""
    gui = make_gui()
    gui.wait_for(lambda st: st["login_visible"])
    os.kill(server.proc.pid, signal.SIGSTOP)
    time.sleep(17)  # more than the 15 s after which the client thinks the connection is lost
    os.kill(server.proc.pid, signal.SIGCONT)
    time.sleep(3)
    gui.call("login", name="zoe")
    gui.wait_for(lambda st: st["window_visible"] and not st["login_visible"], timeout=30)
