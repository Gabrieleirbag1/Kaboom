"""Issue #15: the game crashed when a volume slider was moved too fast.

Each step of a dragged slider gave the new volume to every audio object and rewrote the settings
file (up to 5 times per step with the global slider). Now the volume reaches the audio system at
most every VOLUME_APPLY_MS and is saved once, when the slider is released or stops moving.
These tests drag the sliders of the real game (off-screen) much faster than a hand can.
"""
import time

import pytest

pytestmark = pytest.mark.gui

SLIDERS = {"sound_slider": "global", "musique_slider": "music",
           "ambiance_slider": "ambiance", "boutons_slider": "bouton"}
APPLY_SECONDS = 0.05  # VOLUME_APPLY_MS in client_windows.py
AUDIO_OBJECTS = 1 + 9 + 4  # music player, ambiance sounds, button sounds


def open_settings(make_gui, **kwargs):
    gui = make_gui(**kwargs)
    gui.wait_for(lambda st: st.get("login_visible"), timeout=60)
    gui.call("login", name="bob")
    gui.wait_for(lambda st: st["window_visible"])
    gui.call("open_settings")
    gui.call("count_sound")
    return gui


def assert_volumes(sound: dict, music: int, ambiance: int, bouton: int):
    """The audio objects really play at these volumes."""
    volume, default = sound["music"]
    assert volume == int(default * music / 100), sound["music"]
    for name, expected in (("ambiance", ambiance), ("bouton", bouton)):
        for volume, default in sound["effects"][name]:
            assert volume == pytest.approx(default * expected / 100, abs=0.01), (name, sound["effects"][name])


def test_dragging_the_sliders_very_fast(server, make_gui):
    gui = open_settings(make_gui)
    final = {}
    for slider, row in SLIDERS.items():
        before = gui.call("sound")
        drag = gui.call("drag_slider", slider=slider, moves=1500, timeout=120)
        after = gui.call("sound")  # also checks the game is still running
        final[row] = drag["value"]
        if row == "global":  # the other sliders follow the global one
            final.update(music=drag["value"], ambiance=drag["value"], bouton=drag["value"])

        assert after["saves"] - before["saves"] == 1, "saved once, when the slider is released"
        most = AUDIO_OBJECTS * (drag["seconds"] / APPLY_SECONDS + 2)
        assert after["audio"] - before["audio"] <= most, (after["audio"] - before["audio"], drag["seconds"])
        assert {name: int(value) for name, value in after["saved"].items()} == final
        assert_volumes(after, final["music"], final["ambiance"], final["bouton"])
    assert gui.errors() == ""


def test_keyboard_or_wheel_change_is_saved_once_it_stops(server, make_gui):
    gui = open_settings(make_gui)
    for value in range(80, 20, -1):  # holding the left arrow key
        gui.call("set_slider", slider="ambiance_slider", value=value)
    deadline = time.monotonic() + 3
    while (sound := gui.call("sound"))["saved"]["ambiance"] != "21":
        assert time.monotonic() < deadline, sound["saved"]
        time.sleep(0.1)
    assert sound["saves"] == 1
    assert_volumes(sound, 100, 21, 100)

    gui.call("set_slider", slider="boutons_slider", value=42)
    gui.call("close_settings")  # closed before the save delay: still saved
    sound = gui.call("sound")
    assert sound["saved"]["bouton"] == "42"
    assert_volumes(sound, 100, 21, 42)
    assert gui.errors() == ""


@pytest.mark.parametrize("content", ["", "global,100,notmuted\nmusic,1", "global,abc,notmuted\n" * 4])
def test_broken_volume_file_is_repaired_at_start(server, make_gui, tmp_path, content):
    """A volume file broken by an old crash used to stop the game from starting."""
    settings = tmp_path / "home" / ".config" / "kaboom" / "settings"
    settings.mkdir(parents=True)
    (settings / "user_sound_global.csv").write_text(content)
    gui = open_settings(make_gui, home=tmp_path / "home")
    assert gui.call("sound")["saved"] == {"global": "100", "music": "100", "ambiance": "100", "bouton": "100"}
