"""Issue #21: the connection icon shows the ping measured with the game server (PING_/PONG_), not
with the system's `ping` command: a compiled game (Steam, .deb, setup.exe) must not depend on it.
"""
import time

import pytest

pytestmark = pytest.mark.gui


def wait_pings(gui, check, timeout=20):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        reply = gui.call("pings")
        if check(reply["pings"]):
            return reply
        time.sleep(0.25)
    raise AssertionError(f"Pings seen: {gui.call('pings')['pings']}\n{gui.log()}")


def test_ping_comes_from_the_game_server(make_gui):
    gui = make_gui()
    gui.wait_for(lambda st: st.get("login_visible"), timeout=60)
    gui.call("record_pings")
    # A PING_ goes every 5 s: a round trip shows within one interval
    reply = wait_pings(gui, lambda pings: any(ms > 0 for ms, _ in pings), timeout=12)
    assert all(working for _, working in reply["pings"])
    assert all(ms < 1000 for ms, _ in reply["pings"] if ms > 0)  # the local test server answers at once
    assert reply["icon_ok"]


def test_lost_connection_resets_the_ping(make_gui):
    gui = make_gui()
    gui.wait_for(lambda st: st.get("login_visible"), timeout=60)
    gui.call("record_pings")
    wait_pings(gui, lambda pings: any(ms > 0 for ms, _ in pings), timeout=12)
    gui.call("drop_connection")
    # Back to "no ping" (grey icon); the reconnection then measures it again
    wait_pings(gui, lambda pings: pings[-1][0] == 0.0 or [0.0, True] in pings)
    assert gui.errors() == ""
