import os
import sys
import tempfile

import pytest

# Server modules write logs when imported: send them to a temp folder so the
# committed Server/logs/*.log files are not modified by the tests.
os.environ["KABOOM_LOG_DIR"] = tempfile.mkdtemp(prefix="kaboom-test-logs-")
os.environ["KABOOM_DISABLE_MQTT"] = "1"

# Importing the server replaces sys.stderr / sys.excepthook with its file logger
# (ErrorLogger.setup_logging). Put pytest's back so test failures stay visible.
_stderr, _excepthook = sys.stderr, sys.excepthook
import server_utils, server_game, server_reception  # noqa: E402,F401  (loads the dictionaries once)
sys.stderr, sys.excepthook = _stderr, _excepthook

from harness import BadNetworkProxy, FakeClient, GuiClient, ServerProcess  # noqa: E402


@pytest.fixture
def server(tmp_path, request):
    """A fresh real server for each test (server state is global, so tests must not share it).
    Change its settings with @pytest.mark.server_env(KABOOM_ANIMATION_TIMEOUT="10")."""
    marker = request.node.get_closest_marker("server_env")
    srv = ServerProcess(tmp_path / "server-logs", **(marker.kwargs if marker else {}))
    yield srv
    srv.stop()


@pytest.fixture
def make_client(server):
    """make_client("bob") -> a connected FakeClient. Pass via=proxy to go through a BadNetworkProxy."""
    clients = []

    def _make(name, via=None, **kwargs):
        port = via.port if via else server.port
        client = FakeClient(port, name, **kwargs)
        clients.append(client)
        return client

    yield _make
    for client in clients:
        client.close()


@pytest.fixture
def make_proxy(server):
    proxies = []

    def _make(**kwargs):
        proxy = BadNetworkProxy(server.port, **kwargs)
        proxies.append(proxy)
        return proxy

    yield _make
    for proxy in proxies:
        proxy.close()


@pytest.fixture
def make_gui(server, tmp_path):
    """make_gui(session={...}) -> the real game client (off-screen), connected to the test server."""
    guis = []

    def _make(session=None, home=None, screen=None, env=None):
        gui = GuiClient(server.port, home or tmp_path / "home", session=session, screen=screen, env=env)
        guis.append(gui)
        return gui

    yield _make
    for gui in guis:
        gui.close()
