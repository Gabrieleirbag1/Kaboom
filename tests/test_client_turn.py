"""Issue #17: it must be obvious when it's your turn.

On your turn: a big pulsing "Your turn!", a glowing word box with the cursor in it, and if the
game is in the background, its taskbar icon flashes with a chime. On someone else's turn: "Bob's
turn" and a dimmed word box saying Bob is playing.
"""
import pytest
import server_utils
from harness import FakeClient

pytestmark = pytest.mark.gui

LONG_TURNS = [60, 60, 3, 2, 3, 1, 0]
SUDDEN_DEATH = [2, 2, 1, 2, 3, 1, 2]  # one life, 2 s per turn


def word_with(syllable: str) -> str:
    return next(w for w in sorted(server_utils.Français_dictionnaire)
                if syllable in w and w.isascii() and w.isalpha())


def game_with_bob(server, make_gui, rules):
    """alice (fake) and bob (the real game) in a running game, alice's turn.
    Returns (gui, alice, syllable)."""
    alice = FakeClient(server.port, "alice", avatar="tasse-avatar")
    alice.login()
    alice.create_game("partie1")
    gui = make_gui(screen="1366x768")
    gui.wait_for(lambda st: st.get("login_visible"), timeout=60)
    gui.call("login", name="bob")
    gui.wait_for(lambda st: st["window_visible"])
    gui.call("join", game="partie1", player="bob")
    alice.expect(r"JOIN_STATE\|GET-PLAYERS\|alice,bob\|")
    gui.call("count_turn_cues")
    gui.call("ready")
    alice.expect(r"LOBBY_STATE\|READY\|bob\|True\|")
    alice.ready(creator=True)
    alice.expect(r"LOBBY_STATE\|READY\|alice\|True\|")
    alice.start_game("partie1", rules)
    syllable = alice.expect(r"SYLLABE_\|([^|]+)\|alice\|").group(1)
    return gui, alice, syllable


def bobs_turn(gui, alice, syllable) -> dict:
    """alice gives a right word: bob's turn. Returns bob's game state."""
    alice.answer(word_with(syllable), syllable)
    return gui.wait_for(lambda st: st.get("turn") == "Your turn!", timeout=10)[-1]


def test_your_turn_and_the_others(server, make_gui):
    gui, alice, syllable = game_with_bob(server, make_gui, LONG_TURNS)
    try:
        state = gui.wait_for(lambda st: st.get("turn") == "alice's turn")[-1]
        assert state["placeholder"] == "alice is playing…"
        assert not (state["my_turn"] or state["turn_glow"] or state["box_glow"])

        state = bobs_turn(gui, alice, syllable)
        assert state["turn_glow"] and state["box_glow"]
        assert state["my_turn"] and state["box_focus"]  # bob can type right away
        assert state["placeholder"] == "Enter your word"
        assert state["active"] and state["alerts"] == 0 and state["chimes"] == 0  # he's looking

        syllable = alice.expect(r"SYLLABE_\|([^|]+)\|bob\|").group(1)
        gui.call("answer", word=word_with(syllable))
        alice.expect(r"SYLLABE_\|[^|]+\|alice\|")  # bob was right: back to alice
        state = gui.wait_for(lambda st: st.get("turn") == "alice's turn")[-1]
        assert not (state["my_turn"] or state["turn_glow"] or state["box_glow"])
        assert gui.errors() == ""
    finally:
        alice.close()


def test_taskbar_flashes_when_the_game_is_in_the_background(server, make_gui):
    gui, alice, syllable = game_with_bob(server, make_gui, LONG_TURNS)
    try:
        assert gui.call("focus", on=False)["active"] is False  # bob alt-tabbed to another window
        state = bobs_turn(gui, alice, syllable)
        assert state["alerts"] == 1 and state["chimes"] == 1
        assert state["turn_glow"] and state["box_glow"]
        assert gui.errors() == ""
    finally:
        alice.close()


def test_nobodys_turn_once_the_bomb_exploded_and_after_the_game(server, make_gui):
    gui, alice, syllable = game_with_bob(server, make_gui, SUDDEN_DEATH)
    try:
        bobs_turn(gui, alice, syllable)
        alice.expect(r"GAME_MESSAGE\|TIME'S-UP\|bob\|", timeout=10)  # bob doesn't answer
        state = gui.wait_for(lambda st: st.get("turn") == "")[-1]
        assert not (state["turn_glow"] or state["box_glow"] or state["my_turn"])
        alice.expect(r"GAME_MESSAGE\|GAME-ENDED\|", timeout=10)
        state = gui.wait_for(lambda st: not st["ingame"])[-1]
        assert state["turn"] == "" and not state["turn_glow"] and not state["box_glow"]
        assert state["placeholder"] == "Enter your word"
        assert gui.errors() == ""
    finally:
        alice.close()
