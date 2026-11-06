"""Issues #16 and #18: the game screen and windows on screens of different sizes.

The real game runs on virtual screens of common sizes. The players' squares must line up in rows
and columns, hearts and names must not overlap the avatar frames, nothing may move when the turn
changes, and every window must fit on the screen (the Rules window used to be taller than a
1080p screen, and grew when the sudden death skull was clicked).
"""
import time

import pytest
import server_utils
from harness import FakeClient

pytestmark = pytest.mark.gui

SCREENS = ["1920x1080", "1366x768", "1280x1024"]
GAME = "La partie de alice"
OTHERS = [("Bartholomew", "cactus-avatar"), ("c", "gameboy-avatar"), ("dede", "panneau-avatar"),
          ("Eve", "pizza-avatar"), ("Frankenstein", "reveil-avatar"), ("gus", "television-avatar")]
LONG_TURNS = [60, 60, 3, 2, 3, 1, 0]


def word_with(syllable: str) -> str:
    return next(w for w in sorted(server_utils.Français_dictionnaire)
                if syllable in w and w.isascii() and w.isalpha())


def size(screen: str) -> tuple[int, int]:
    width, height = screen.split("x")
    return int(width), int(height)


def with_language(tmp_path, language: str):
    """A config folder where the game's language is `language`."""
    settings = tmp_path / "home" / ".config" / "kaboom" / "settings"
    settings.mkdir(parents=True)
    (settings / "user_accessibility.csv").write_text(
        f"theme,#Fec2ff/#7bf8fc,NotSound\nlanguage,{language},NotSound\nanimations,yes,NotSound\nborders,yes,NotSound\n")
    return tmp_path / "home"


def logged_in(make_gui, screen, home=None):
    gui = make_gui(screen=screen, home=home)
    gui.wait_for(lambda st: st.get("login_visible"), timeout=60)
    gui.call("login", name="bob")
    gui.wait_for(lambda st: st["window_visible"])
    return gui


def center(rect):
    x, y, width, height = rect
    return x + width / 2, y + height / 2


def bottom(rect):
    return rect[1] + rect[3]


def overlap(a, b) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def full_game(server, make_gui, screen):
    """8 players (the real game is bob, the last one) in a running game, alice's turn.
    Returns (gui, alice, the other fake players, the syllable)."""
    alice = FakeClient(server.port, "alice", avatar="tasse-avatar")
    others = [FakeClient(server.port, name, avatar=avatar) for name, avatar in OTHERS]
    alice.login()
    alice.create_game(GAME)
    for player in others:
        player.login()
        player.open_join_menu()
        player.join_game(GAME)
    gui = logged_in(make_gui, screen)
    gui.call("join", game=GAME, player="bob")
    gui.wait_for(lambda st: len(st.get("labels", [])) == 8 and "bob" in st["labels"][7])
    for player in others:
        player.ready(creator=False)
    gui.call("ready")
    alice.ready(creator=True)
    alice.expect(r"LOBBY_STATE\|READY\|alice\|True\|")
    alice.start_game(GAME, LONG_TURNS)
    syllable = alice.expect(r"SYLLABE_\|([^|]+)\|alice\|").group(1)
    # The hearts are shown at the start, alice's turn (her bigger avatar) may come just after
    gui.wait_for(lambda st: st.get("hearts") == [3] * 8 and st.get("turn") == "alice's turn")
    return gui, alice, others, syllable


@pytest.mark.parametrize("screen", SCREENS)
def test_game_screen_lines_up_and_fits(server, make_gui, screen):
    gui, alice, others, syllable = full_game(server, make_gui, screen)
    try:
        layout = gui.call("layout")
        players = layout["players"]
        width, height = size(screen)

        # The whole screen is used, nothing more: the buttons at the bottom are visible
        assert layout["window"] == [width, height]
        for button in ("rules_button", "ready_button", "start_button"):
            assert bottom(layout[button]) <= height, button

        # Squares in rows and columns:  1 . . 2 / 3 . . 4 / 7 5 6 8
        avatars = [center(player["avatar"]) for player in players]
        for row in ([0, 1], [2, 3], [6, 4, 5, 7]):
            assert max(avatars[i][1] for i in row) - min(avatars[i][1] for i in row) <= 1, row
        for column in ([0, 2, 6], [1, 3, 7]):
            assert max(avatars[i][0] for i in column) - min(avatars[i][0] for i in column) <= 1, column
        steps = [avatars[b][0] - avatars[a][0] for a, b in ((6, 4), (4, 5), (5, 7))]
        assert max(steps) - min(steps) <= 2, steps  # the bottom row is evenly spaced

        for i, player in enumerate(players):
            frame = player["border"] / 2  # the frame is drawn around the avatar, half outside
            assert player["hearts_count"] == 3 and player["hearts_visible"], (i, player)
            assert abs(center(player["hearts"])[0] - avatars[i][0]) <= 2, (i, player)  # centered
            assert player["hearts"][1] >= bottom(player["avatar"]) + frame, (i, player)  # under the frame
            assert bottom(player["name"]) <= player["avatar"][1] - frame, (i, player)  # above the frame
            assert not overlap(player["avatar"], layout["bomb_label"]), i
            assert bottom(player["hearts"]) <= height

        # The turn goes to the next player: their avatar grows, but nothing moves
        alice.answer(word_with(syllable), syllable)
        alice.expect(r"SYLLABE_\|[^|]+\|(?!alice\|)")
        deadline = time.monotonic() + 10
        while (after := gui.call("layout")["players"])[0]["border"] >= players[0]["border"]:
            assert time.monotonic() < deadline, "the real game didn't show the next turn"
            time.sleep(0.1)
        for before_center, after_center in zip(avatars, (center(p["avatar"]) for p in after)):
            assert abs(before_center[0] - after_center[0]) <= 1 and abs(before_center[1] - after_center[1]) <= 1
        for before_player, after_player in zip(players, after):  # 1 px: layout rounding
            assert all(abs(a - b) <= 1 for a, b in zip(before_player["hearts"][:2], after_player["hearts"][:2]))
        assert gui.errors() == ""
    finally:
        for player in [alice, *others]:
            player.close()


@pytest.mark.parametrize("language, screen", [("Français", "1366x768"), ("Deutsch", "1366x768"),
                                              ("Español", "1920x1080"), ("English", "1280x720")])
def test_rules_window_fits_and_keeps_its_size(server, make_gui, tmp_path, language, screen):
    """Clicking the skull (sudden death level) changes the text next to it: the window keeps its size."""
    gui = logged_in(make_gui, screen, home=with_language(tmp_path, language))
    size_before = gui.call("rules_window")["size"]
    width, height = size(screen)
    assert size_before[0] <= width and size_before[1] <= height, size_before
    for mode in (1, 2, 0):
        clicked = gui.call("click_skull")
        assert clicked["mode"] == mode
        assert clicked["size"] == size_before
    assert gui.errors() == ""


def test_windows_fit_on_a_small_screen(server, make_gui, tmp_path):
    screen = "1280x720"
    gui = make_gui(screen=screen, home=with_language(tmp_path, "Français"))
    gui.wait_for(lambda st: st.get("login_visible"), timeout=60)
    sizes = {"login": gui.call("screenshot", of="login", path=str(tmp_path / "login.png"))["size"],
             "avatars": gui.call("call", target="login.avatar_window", method="show")["size"]}
    gui.call("call", target="login.avatar_window", method="close")
    gui.call("login", name="bob")
    gui.wait_for(lambda st: st["window_visible"])
    gui.call("call", target="window", method="load_select_screen")
    sizes["menu"] = gui.call("screenshot", of="window", path=str(tmp_path / "menu.png"))["size"]
    sizes["creation"] = gui.call("call", target="window", method="create_game_widget") and \
        gui.call("screenshot", of="window.creation_game", path=str(tmp_path / "creation.png"))["size"]
    gui.call("open_settings")
    sizes["settings"] = gui.call("screenshot", of="window.settings_window", path=str(tmp_path / "settings.png"))["size"]
    width, height = size(screen)
    for name, (w, h) in sizes.items():
        assert w <= width and h <= height, (name, w, h)
    assert gui.errors() == ""
