"""Issues #14 / #22: the game must stay light on the computer.

Measured before the fix (1920x1080): the client used 2.7 GB of memory and a whole CPU core on every
screen after the title screen. The moving background rebuilt the window's style sheet and applied
it again about 60 times a second, and the style sheet grew without end (125 000 characters in a
game). Every animation frame was also kept at full size (500x500, 2667x1500 for the title screen)
although it is shown much smaller.
"""
import math
import time
from pathlib import Path

import pytest
from harness import FakeClient

pytestmark = pytest.mark.gui

SPRITES = Path(__file__).resolve().parent.parent / "Client" / "images" / "sprites"
SCREEN = (1366, 768)
MAX_IDLE_CPU = 40  # % of one core, measured while the player does nothing (it was ~100 %)
LONG_TURNS = [60, 60, 3, 2, 3, 1, 0]


# GStreamer can't decode MP3 files (the music) with these: like a computer without the plugins
NO_MP3_DECODER = {"GST_PLUGIN_FEATURE_RANK": ",".join(f"{name}:NONE" for name in (
    "mpg123audiodec", "avdec_mp3", "avdec_mp3float", "avdec_mp3adu", "avdec_mp3adufloat",
    "avdec_mp3on4", "avdec_mp3on4float", "mpegaudioparse", "mad", "flump3dec"))}


def menu(make_gui, env: dict | None = None):
    """The real game on a 1366x768 screen, logged in, on the main menu."""
    gui = make_gui(screen="x".join(map(str, SCREEN)), env=env)
    gui.wait_for(lambda st: st.get("login_visible"), timeout=60)
    gui.call("login", name="bob")
    gui.wait_for(lambda st: st["window_visible"])
    gui.call("menu")
    time.sleep(1)  # the menu is drawn
    return gui


def idle_cpu(gui, seconds: float = 4) -> tuple[float, dict, dict]:
    """CPU used (in % of one core) while nobody touches the game, and the measures before/after."""
    before = gui.call("perf")
    time.sleep(seconds)
    after = gui.call("perf")
    return (after["cpu_s"] - before["cpu_s"]) / seconds * 100, before, after


def busiest(before: dict, after: dict, seconds: float = 4) -> str:
    """The threads that used the most CPU between the two measures, to tell why the game is busy."""
    used = {name: (cpu - before["threads"].get(name, 0)) / seconds * 100 for name, cpu in after["threads"].items()}
    return ", ".join(f"{name}: {cpu:.0f} %" for name, cpu in sorted(used.items(), key=lambda item: -item[1])[:5])


def close(color: str, expected: str, tolerance: int = 12) -> bool:
    a, b = (bytes.fromhex(c.lstrip("#")) for c in (color, expected))
    return all(abs(x - y) <= tolerance for x, y in zip(a, b))


def test_the_menu_is_light_on_the_cpu_and_its_style_sheets_dont_grow(server, make_gui):
    gui = menu(make_gui)
    cpu, before, after = idle_cpu(gui)
    assert cpu < MAX_IDLE_CPU, f"{cpu:.0f} % of a core used by the menu while nobody plays ({busiest(before, after)})"
    assert after["window_sheet"] == before["window_sheet"], "the window's style sheet keeps changing"

    gui.call("hover_menu_buttons", times=5)  # their colors move when the mouse is over them
    hovered = gui.call("perf")
    assert hovered["window_sheet"] == before["window_sheet"]
    assert max(hovered["button_sheets"]) < 1000, hovered["button_sheets"]  # was 150 000 characters
    assert gui.errors() == ""


def test_changing_the_background_theme(server, make_gui):
    """#14 "after changing background": the new colors are shown and the game stays light."""
    gui = menu(make_gui)
    corners = [[3, 3], [SCREEN[0] - 4, SCREEN[1] - 4]]  # only background there (its first color)
    assert all(close(c, "#fec2ff") for c in gui.call("background_pixels", points=corners)["colors"])

    gui.call("theme", color1="#b7ffc7", color2="#8ccaff")
    time.sleep(0.5)
    colors = gui.call("background_pixels", points=corners)["colors"]
    assert all(close(c, "#b7ffc7") for c in colors), colors
    cpu, before, after = idle_cpu(gui)
    assert cpu < MAX_IDLE_CPU, f"{cpu:.0f} % of a core used after changing the theme ({busiest(before, after)})"
    assert after["window_sheet"] == before["window_sheet"]
    assert gui.errors() == ""


def test_animations_are_kept_at_the_size_they_are_shown(server, make_gui):
    gui = menu(make_gui)
    loaded = gui.call("sprites")["sprites"]
    folders = {folder.name: len(list(folder.glob("*.png"))) for folder in SPRITES.iterdir() if folder.is_dir()}
    assert set(folders) - {"title_screen"} <= set(loaded)
    width, height = SCREEN
    for name, (frames, w, h) in loaded.items():
        if name == "title_screen":  # only needed on the title screen: freed once the player leaves it
            assert frames == 0, "the title screen animation is still in memory"
            continue
        assert frames == folders[name], f"{name}: {frames} frames loaded out of {folders[name]}"
        # The bomb and explosions fill a third of the screen, avatars and tombstones a sixth
        biggest = math.ceil(min(width, height) / (3 if name.startswith(("bombe", "explosion")) else 5.9))
        assert max(w, h) <= biggest, f"{name} is kept at {w}x{h}, shown at most at {biggest}x{biggest}"

    avatars = gui.call("sprites")["avatars"]  # pictures of the players (3000x3000 files)
    assert avatars, "no avatar picture loaded"
    for avatar, (w, h) in avatars.items():  # the biggest one shown is the winner's, a quarter of the width
        assert max(w, h) <= width // 4, f"{avatar} is kept at {w}x{h}"

    rss = gui.call("perf")["rss_mb"]
    assert rss < 700, f"the game uses {rss:.0f} MB of memory on the menu (it was 2 700 MB)"
    assert gui.errors() == ""


def test_the_lobby_and_the_game_are_light_on_the_cpu(server, make_gui):
    """The Rules / Ready / Start buttons' borders asked for a new repaint of the whole window while
    it was being painted: the lobby and the game repainted without stop (a whole core)."""
    gui = menu(make_gui)
    alice = FakeClient(server.port, "alice", avatar="tasse-avatar")
    try:
        alice.login()
        alice.create_game("partie1")
        gui.call("join", game="partie1", player="bob")
        gui.wait_for(lambda st: any("alice" in label for label in st.get("labels", [])))
        time.sleep(1)
        cpu, before, after = idle_cpu(gui)
        assert cpu < MAX_IDLE_CPU, f"{cpu:.0f} % of a core used in the lobby while nobody plays ({busiest(before, after)})"

        gui.call("ready")
        alice.expect(r"LOBBY_STATE\|READY\|bob\|True\|")
        alice.ready(creator=True)
        alice.expect(r"LOBBY_STATE\|READY\|alice\|True\|")
        alice.start_game("partie1", LONG_TURNS)
        gui.wait_for(lambda st: st.get("turn") == "alice's turn")
        time.sleep(1)
        cpu, before, after = idle_cpu(gui)
        assert cpu < MAX_IDLE_CPU, f"{cpu:.0f} % of a core used in a game while alice thinks ({busiest(before, after)})"
        assert gui.errors() == ""
    finally:
        alice.close()


def test_deactivate_effects_stops_the_moving_background(server, make_gui):
    """For slow computers: settings > graphics > "Deactivate effects" also stills the background."""
    gui = menu(make_gui)
    gui.call("deactivate_effects")
    time.sleep(0.5)
    middle = [[SCREEN[0] // 2, SCREEN[1] - 4]]  # the bottom edge's middle: only background there
    first = gui.call("background_pixels", points=middle)["colors"]
    cpu, before, after = idle_cpu(gui)
    assert gui.call("background_pixels", points=middle)["colors"] == first, "the background still moves"
    assert cpu < 15, f"{cpu:.0f} % of a core used with the effects turned off ({busiest(before, after)})"
    assert gui.errors() == ""


def test_music_that_cant_be_played_doesnt_use_the_cpu(server, make_gui):
    """The CI computer has no MP3 decoder. The music looped on the current file: Qt tried the
    "next" one (the same) after each failure, without end, and the game used more than a core."""
    gui = menu(make_gui, env=NO_MP3_DECODER)
    gui.call("deactivate_effects")  # only the music is left to use the CPU
    time.sleep(0.5)
    cpu, before, after = idle_cpu(gui)
    assert cpu < 15, f"{cpu:.0f} % of a core used when the music can't be played ({busiest(before, after)})"
    assert gui.errors() == ""


def test_join_menu_game_cards_are_shown(server, make_gui):
    """Each game of the join menu is a card (gradient + dark border), even before the mouse goes
    over it. It used to show only thanks to the style sheet that grew without end."""
    alice = FakeClient(server.port, "alice", avatar="tasse-avatar")
    try:
        alice.login()
        alice.create_game("Game of alice")
        gui = menu(make_gui)
        gui.call("open_join_menu")
        time.sleep(1)
        cards = gui.call("game_cards")["cards"]
        assert len(cards) == 1, cards
        background = gui.call("background_pixels", points=[[3, 3]])["colors"][0]
        assert close(cards[0]["inside"], "#c5baff", tolerance=25), cards  # the card's purple (public game)
        assert not close(cards[0]["inside"], background), cards
        assert all(int(cards[0]["border"][i:i + 2], 16) < 80 for i in (1, 3, 5)), cards  # dark border
        assert gui.errors() == ""
    finally:
        alice.close()
