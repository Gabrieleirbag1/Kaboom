"""Live typing (#20) against a real Mosquitto broker with the dynamic security plugin.

The server must give each player an account that only works for their own game, delete it when
they leave, give it again after a reconnection, and clean up accounts left by a crash.

Needs mosquitto and mosquitto_ctrl (apt install mosquitto mosquitto-clients), else skipped.
KABOOM_MOSQUITTO_DIR=<folder> uses a copy unpacked from the .deb files instead (<folder>/usr/sbin/...).
KABOOM_REQUIRE_MOSQUITTO=1 (CI) fails instead of skipping.
"""
import json
import os
import queue
import re
import shutil
import socket
import subprocess
import threading
import time
import uuid
from pathlib import Path

import pytest
from paho.mqtt import client as mqtt_client

from harness import ServerProcess, assert_no_server_errors, free_port, make_both_ready, setup_lobby
from server_mqtt import PLAYER_PREFIX, ROLE_PREFIX

ADMIN, PASSWORD = "kaboom-admin", "test-admin-password"
LONG_TURNS = [20, 20, 2, 2, 3, 1, 0]  # the game keeps running during the test


def find_mosquitto() -> dict | None:
    root = os.environ.get("KABOOM_MOSQUITTO_DIR")
    if root:
        root = Path(root)
        broker, ctrl = root / "usr/sbin/mosquitto", root / "usr/bin/mosquitto_ctrl"
        lib_dirs = [root / "usr/lib/x86_64-linux-gnu", root / "usr/lib"]
    else:
        broker = Path(shutil.which("mosquitto") or "/usr/sbin/mosquitto")
        ctrl = Path(shutil.which("mosquitto_ctrl") or "/usr/bin/mosquitto_ctrl")
        lib_dirs = [Path("/usr/lib/x86_64-linux-gnu"), Path("/usr/lib/aarch64-linux-gnu"),
                    Path("/usr/lib/mosquitto"), Path("/usr/lib"), Path("/usr/local/lib")]
    plugin = next((d / "mosquitto_dynamic_security.so" for d in lib_dirs
                   if (d / "mosquitto_dynamic_security.so").exists()), None)
    if not (broker.exists() and ctrl.exists() and plugin):
        return None
    env = {**os.environ}
    if root:
        env["LD_LIBRARY_PATH"] = ":".join(str(d) for d in lib_dirs)
    return {"broker": str(broker), "ctrl": str(ctrl), "plugin": str(plugin), "env": env}


MOSQUITTO = find_mosquitto()


class Broker:
    """Mosquitto with dynamic security, set up like on the real server (deny by default)."""

    def __init__(self, folder: Path):
        self.port = free_port()
        dynsec = folder / "dynamic-security.json"
        subprocess.run([MOSQUITTO["ctrl"], "dynsec", "init", str(dynsec), ADMIN, PASSWORD],
                       env=MOSQUITTO["env"], check=True, capture_output=True)
        config = json.loads(dynsec.read_text())
        config["defaultACLAccess"] = {"publishClientSend": False, "publishClientReceive": False,
                                      "subscribe": False, "unsubscribe": True}
        dynsec.write_text(json.dumps(config))
        conf = folder / "mosquitto.conf"
        conf.write_text(f"""per_listener_settings false
allow_anonymous false
listener {self.port} 127.0.0.1
plugin {MOSQUITTO['plugin']}
plugin_opt_config_file {dynsec}
max_packet_size 2048
retain_available false
persistence false
""")
        self.log = open(folder / "mosquitto.log", "w")
        self.proc = subprocess.Popen([MOSQUITTO["broker"], "-c", str(conf)], env=MOSQUITTO["env"],
                                     stdout=self.log, stderr=subprocess.STDOUT)
        deadline = time.monotonic() + 10
        while True:
            try:
                socket.create_connection(("127.0.0.1", self.port), timeout=0.5).close()
                break
            except OSError:
                if time.monotonic() > deadline or self.proc.poll() is not None:
                    raise RuntimeError(f"Mosquitto did not start: {(folder / 'mosquitto.log').read_text()}")
                time.sleep(0.1)

    def ctrl(self, *args: str) -> str:
        """Run a mosquitto_ctrl dynsec command as the admin."""
        result = subprocess.run([MOSQUITTO["ctrl"], "-h", "127.0.0.1", "-p", str(self.port), "-u", ADMIN,
                                 "-P", PASSWORD, "dynsec", *args],
                                env=MOSQUITTO["env"], check=True, capture_output=True, text=True)
        return result.stdout

    def wait_until(self, check, timeout: float = 10):
        deadline = time.monotonic() + timeout
        while not check():
            assert time.monotonic() < deadline, "timeout"
            time.sleep(0.2)

    def stop(self):
        self.proc.terminate()
        self.proc.wait(5)
        self.log.close()


@pytest.fixture
def broker(tmp_path):
    if MOSQUITTO is None:
        if os.environ.get("KABOOM_REQUIRE_MOSQUITTO") == "1":
            pytest.fail("mosquitto, mosquitto_ctrl or the dynamic security plugin not found")
        pytest.skip("mosquitto not installed (apt install mosquitto mosquitto-clients)")
    b = Broker(tmp_path)
    yield b
    b.stop()


def start_server(broker: Broker, folder: Path) -> ServerProcess:
    return ServerProcess(folder / "server-logs", KABOOM_DISABLE_MQTT="0",
                         KABOOM_MQTT_USER=ADMIN, KABOOM_MQTT_PASSWORD=PASSWORD,
                         KABOOM_MQTT_ADMIN_HOST="127.0.0.1", KABOOM_MQTT_ADMIN_PORT=str(broker.port),
                         KABOOM_MQTT_ADMIN_TLS="False",
                         KABOOM_MQTT_PLAYER_HOST="127.0.0.1", KABOOM_MQTT_PLAYER_PORT=str(broker.port),
                         KABOOM_MQTT_PLAYER_TLS="False")


@pytest.fixture
def server(broker, tmp_path):
    """Replaces conftest's server: this one talks to the broker."""
    srv = start_server(broker, tmp_path)
    yield srv
    srv.stop()


def account(player, game: str) -> re.Match:
    """Wait for the MQTT_ message (live typing account) of `game`."""
    return player.expect(rf"MQTT_\|{re.escape(game)}\|([^|]*)\|(\d+)\|(True|False)\|([^|]*)\|([^|]*)\|([^|]*)\|")


class Typist:
    """A player's live typing connection, like Client/client_mqtt.py, with the account from MQTT_."""

    def __init__(self, access: re.Match):
        host, port, _tls, self.topic, self.username, self.password = access.groups()
        self.connacks, self.subacks, self.received = queue.Queue(), queue.Queue(), queue.Queue()
        self.disconnected = threading.Event()
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=f"test-{uuid.uuid4().hex}")
        client.username_pw_set(self.username, self.password)
        client.on_connect = lambda c, u, f, rc, p: self.connacks.put(rc)
        client.on_subscribe = lambda c, u, mid, rcs, p: self.subacks.put(rcs)
        client.on_message = lambda c, u, m: self.received.put((m.topic, m.payload.decode()))
        client.on_disconnect = lambda c, u, f, rc, p: self.disconnected.set()
        client.connect_async(host, int(port))
        client.loop_start()
        self.client = client

    def connected(self) -> bool:
        return not self.connacks.get(timeout=10).is_failure

    def subscribe(self, topic: str) -> bool:
        self.client.subscribe(topic)
        return not self.subacks.get(timeout=5)[0].is_failure

    def publish(self, text: str, topic: str | None = None):
        self.client.publish(topic or self.topic, text)

    def messages(self, seconds: float) -> list[tuple[str, str]]:
        time.sleep(seconds)
        out = []
        while not self.received.empty():
            out.append(self.received.get())
        return out

    def close(self):
        self.client.loop_stop()
        self.client.disconnect()


@pytest.fixture
def typists():
    made = []

    def _make(access):
        typist = Typist(access)
        made.append(typist)
        return typist

    yield _make
    for typist in made:
        typist.close()


def test_typing_reaches_only_the_players_of_the_game(server, make_client, typists):
    alice, bob = setup_lobby(make_client, game="g1")
    carol = make_client("carol")
    carol.login()
    carol.create_game("g2")
    a, b, c = typists(account(alice, "g1")), typists(account(bob, "g1")), typists(account(carol, "g2"))
    assert a.topic == b.topic != c.topic
    assert len({a.username, b.username, c.username}) == 3
    for typist in (a, b, c):
        assert typist.connected()
        assert typist.subscribe(typist.topic)

    a.publish("alice|bonjour")
    assert b.messages(1) == [(a.topic, "alice|bonjour")]

    # carol can't listen to game 1, or to every game
    assert not c.subscribe(a.topic)
    assert not c.subscribe("#")
    assert not c.subscribe("kaboom/games/+")
    # nor write on game 1's screens
    c.publish("carol|spam", topic=a.topic)
    assert b.messages(1) == []
    assert c.messages(0) == []

    logs = (server.log_dir / "infos.log").read_text(encoding="utf-8")
    assert "MQTT_|(live typing account)" in logs
    assert a.password not in logs and b.password not in logs  # never written in the server's log
    assert_no_server_errors(server)


def test_leaving_deletes_the_account(server, make_client, typists, broker):
    alice, bob = setup_lobby(make_client, game="g1")
    a_access, b_access = account(alice, "g1"), account(bob, "g1")
    a, b = typists(a_access), typists(b_access)
    assert a.connected() and b.connected()

    bob.leave_game("g1")
    assert b.disconnected.wait(5)  # deleting the account disconnects it at once
    assert not typists(b_access).connected()  # and the password doesn't work any more

    alice.leave_game("g1")  # last player: the game and its role are deleted
    broker.wait_until(lambda: PLAYER_PREFIX not in broker.ctrl("listClients")
                      and ROLE_PREFIX not in broker.ctrl("listRoles"))
    assert_no_server_errors(server)


def test_reconnect_during_a_game_gives_the_account_again(server, make_client, typists):
    alice, bob = setup_lobby(make_client, game="g1")
    first = account(bob, "g1").group(0)
    make_both_ready(alice, bob)
    alice.start_game("g1", LONG_TURNS)
    bob.expect(r"SYLLABE_\|")

    token = bob.token
    bob.close()
    back = make_client("bob-again", avatar=bob.avatar)
    back.reconnect_as("bob", token)
    back.expect(r"RECONNECTED\|g1\|")
    again = account(back, "g1")
    assert again.group(0) == first  # the seat was kept, so was the account
    assert typists(again).connected()
    assert_no_server_errors(server)


def test_leftover_accounts_are_deleted_at_start(broker, tmp_path):
    broker.ctrl("createClient", PLAYER_PREFIX + "old", "-p", "x")
    broker.ctrl("createRole", ROLE_PREFIX + "old")
    broker.ctrl("createClient", "someone-else", "-p", "x")  # not Kaboom's: kept
    server = start_server(broker, tmp_path)
    try:
        broker.wait_until(lambda: PLAYER_PREFIX + "old" not in broker.ctrl("listClients")
                          and ROLE_PREFIX + "old" not in broker.ctrl("listRoles"))
        clients = broker.ctrl("listClients")
        assert "someone-else" in clients and ADMIN in clients
        assert_no_server_errors(server)
    finally:
        server.stop()
