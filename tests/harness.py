"""Tools to run the real Kaboom server and talk to it like a player, without the Qt client.

- ServerProcess: starts Server/server.py on a free local port, with logs in a temp folder
  and MQTT turned off.
- FakeClient: a headless player that sends the same messages as the real client.
- BadNetworkProxy: sits between a FakeClient and the server and behaves like a bad internet
  link (delay, messages merged together, messages cut into pieces). It reproduces bugs that
  normally only show up in production.
"""
import codecs
import json
import os
import random
import re
import select
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

from server_protocol import PROTOCOL_VERSION, encode

ROOT = Path(__file__).resolve().parent.parent
SERVER_DIR = ROOT / "Server"

# Rules sent with START-GAME_ (same order as the client's `rules` list):
# min time, max time, lifes, min syllable length, max syllable length, repetitions, death mode
FAST_RULES = [1, 1, 1, 2, 3, 1, 0]   # one life, 1 second per turn: a 2-player game ends in ~6 s
SLOW_RULES = [8, 8, 2, 2, 3, 1, 0]   # enough time to answer during a turn


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class ServerProcess:
    """The real server, running in a subprocess."""

    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.port = free_port()
        env = {
            **os.environ,
            "KABOOM_LOG_DIR": str(self.log_dir),
            "KABOOM_SOCKET_HOST": "127.0.0.1",
            "KABOOM_SOCKET_PORT": str(self.port),
            "KABOOM_DISABLE_MQTT": "1",
        }
        self._stderr = open(self.log_dir / "stderr.txt", "w")
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER_DIR / "server.py")],
            cwd=SERVER_DIR, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=self._stderr,
        )
        self._wait_until_listening()

    def _wait_until_listening(self, timeout: float = 20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError(f"Server exited early:\n{self.error_log()}")
            try:
                socket.create_connection(("127.0.0.1", self.port), timeout=0.5).close()
                return
            except OSError:
                time.sleep(0.1)
        raise RuntimeError("Server did not start listening in time")

    def error_log(self) -> str:
        """Everything the server wrote to errors.log and to stderr."""
        text = ""
        for name in ("errors.log", "stderr.txt"):
            path = self.log_dir / name
            if path.exists():
                text += path.read_text(encoding="utf-8", errors="replace")
        return text

    def stop(self):
        if self.proc.poll() is None:
            try:
                self.proc.stdin.write(b"/stop\n")
                self.proc.stdin.flush()
                self.proc.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                self.proc.kill()
                self.proc.wait()
        self._stderr.close()


class FakeClient:
    """A headless player. Sends the same messages as Client/client.py.

    Received data is kept as one text stream and `expect()` searches it with a regex, so this
    client is never fooled by merged or split packets: only the server is under test.
    """

    def __init__(self, port: int, name: str, avatar: str = "pizza-avatar", gap: float = 0.05):
        self.name = name
        self.avatar = avatar
        self.gap = gap  # pause after each message, like a human clicking
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=10)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._buffer = ""
        self._cond = threading.Condition()
        self._closed = False
        threading.Thread(target=self._read_loop, daemon=True).start()

    # --- low level -------------------------------------------------------------------------
    def _read_loop(self):
        decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        while True:
            try:
                data = self.sock.recv(65536)
            except OSError:
                data = b""
            with self._cond:
                if not data:
                    self._closed = True
                    self._cond.notify_all()
                    return
                self._buffer += decoder.decode(data)
                self._cond.notify_all()

    def send(self, message: str, gap: float | None = None):
        self.send_bytes(encode(message), gap)

    def send_bytes(self, data: bytes, gap: float | None = None):
        self.sock.sendall(data)
        time.sleep(self.gap if gap is None else gap)

    def expect(self, pattern: str, timeout: float = 10) -> re.Match:
        """Wait until `pattern` (a regex) appears in what the server sent, and remove it."""
        regex = re.compile(pattern)
        deadline = time.monotonic() + timeout
        with self._cond:
            while True:
                match = regex.search(self._buffer)
                if match:
                    self._buffer = self._buffer[:match.start()] + self._buffer[match.end():]
                    return match
                left = deadline - time.monotonic()
                if left <= 0 or self._closed:
                    state = "connection closed" if self._closed else "timeout"
                    raise AssertionError(
                        f"[{self.name}] {state} waiting for {pattern!r}. Unread data: {self._buffer!r}")
                self._cond.wait(left)

    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()

    # --- protocol (same messages as the Qt client) ------------------------------------------
    def login(self):
        self.send(f"NEW-USER_|{self.name}|{self.avatar}|{PROTOCOL_VERSION}")
        self.expect(r"NAME_CORRECT\|")

    def open_join_menu(self):
        self.send(f"GET-GAMES_|{self.name}|")

    def create_game(self, game: str, password: str = "", private: bool = False, langue: str = "Français"):
        self.send(f"CHECK-GAME-NAME_|{game}|{password}|{private}|")
        self.expect(rf"CHECK_GAME\|GAME-NAME-CORRECT\|{re.escape(game)}\|")
        self.send(f"CREATE-GAME_|{self.name}|{game}|{password}|{private}|{langue}|")

    def join_game(self, game: str, password: str = "password"):
        """Must be called after open_join_menu(), like the real client."""
        self.send(f"JOIN-GAME_|{game}|{password}|{self.name}")
        self.expect(rf"JOIN_STATE\|GAME-JOINED\|{re.escape(game)}\|[^|]*\|[^|]*\|[^|]*\|{re.escape(self.name)}\|")
        self.send(f"JOIN-GAME-AS-A-PLAYER_|{self.name}|{game}|{self.avatar}")

    def leave_game(self, game: str):
        self.send(f"LEAVE-GAME_|{game}|{self.name}")

    def ready(self, creator: bool, gap: float | None = None):
        kind = "READY-TO-PLAY_" if creator else "READY-TO-PLAY-JOIN_"
        self.send(f"{kind}|{self.name}", gap=gap)

    def start_game(self, game: str, rules: list[int]):
        self.send(f"START-GAME_|{self.name}|{game}|" + "|".join(map(str, rules)) + "|")

    def answer(self, word: str, syllable: str):
        self.send(f"NEW-SYLLABE_|{self.name}|{word}|{syllable}")


class BadNetworkProxy:
    """A TCP proxy that behaves like a bad internet connection.

    For every chunk it forwards, it:
      - waits `delay` seconds and gathers anything else sent meanwhile (`merge=True`), so two
        messages sent close together arrive as one packet;
      - cuts the data into 2 to `max_pieces` pieces sent separately (`split=True`), so one
        message arrives in several packets (sometimes in the middle of an accented letter).
    Clients connect to `proxy.port` instead of the server's port.
    """

    def __init__(self, target_port: int, merge: bool = True, split: bool = True,
                 delay: float = 0.1, max_pieces: int = 3, seed: int = 0):
        self.target_port = target_port
        self.merge, self.split = merge, split
        self.delay, self.max_pieces = delay, max_pieces
        self._rng = random.Random(seed)
        self._listener = socket.create_server(("127.0.0.1", 0))
        self.port = self._listener.getsockname()[1]
        self._sockets: list[socket.socket] = [self._listener]
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while True:
            try:
                downstream, _ = self._listener.accept()
            except OSError:
                return
            upstream = socket.create_connection(("127.0.0.1", self.target_port))
            for s in (downstream, upstream):
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self._sockets += [downstream, upstream]
            threading.Thread(target=self._pump, args=(downstream, upstream), daemon=True).start()
            threading.Thread(target=self._pump, args=(upstream, downstream), daemon=True).start()

    def _pump(self, src: socket.socket, dst: socket.socket):
        eof = False
        while not eof:
            try:
                data = src.recv(65536)
            except OSError:
                break
            if not data:
                break
            if self.merge:
                deadline = time.monotonic() + self.delay
                while (left := deadline - time.monotonic()) > 0:
                    try:
                        ready, _, _ = select.select([src], [], [], left)
                        more = src.recv(65536) if ready else None
                    except (OSError, ValueError):  # socket closed at teardown
                        more = b""
                    if more is None:
                        break
                    if not more:
                        eof = True
                        break
                    data += more
            try:
                for piece in self._cut(data):
                    dst.sendall(piece)
                    time.sleep(0.03)  # long enough for the receiver to read pieces separately
            except OSError:
                break
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass

    def _cut(self, data: bytes) -> list[bytes]:
        if not self.split or len(data) < 2:
            return [data]
        count = min(len(data), self._rng.randint(2, self.max_pieces))
        cuts = sorted(self._rng.sample(range(1, len(data)), count - 1))
        return [data[a:b] for a, b in zip([0, *cuts], [*cuts, len(data)])]

    def close(self):
        for s in self._sockets:
            try:
                s.close()
            except OSError:
                pass


# --- Common game flows used by the tests ---------------------------------------------------------

def setup_lobby(make_client, game="partie1", creator_name="alice", joiner_name="bob", via=None):
    """alice creates `game`, bob joins it. Returns (alice, bob)."""
    alice = make_client(creator_name, via=via)
    alice.login()
    alice.create_game(game)

    bob = make_client(joiner_name, avatar="robot-ninja-avatar", via=via)
    bob.login()
    bob.open_join_menu()
    bob.expect(rf"GAME_CREATED\|{re.escape(game)}\|False\|1\|Français\|")
    bob.join_game(game)
    for player in (alice, bob):
        player.expect(rf"JOIN_STATE\|GET-PLAYERS\|{creator_name},{joiner_name}\|")
    return alice, bob


def make_both_ready(alice, bob):
    """alice is the creator, bob joined."""
    alice.ready(creator=True)
    bob.ready(creator=False)
    for player in (alice, bob):
        player.expect(rf"LOBBY_STATE\|READY\|{alice.name}\|True\|")
        player.expect(rf"LOBBY_STATE\|READY\|{bob.name}\|True\|")


def play_until_bob_wins(alice, bob, game="partie1", timeout=15):
    """Start a FAST_RULES game where alice never answers. Returns the final ranking."""
    alice.start_game(game, FAST_RULES)
    for player in (alice, bob):
        player.expect(rf"GAME_MESSAGE\|GAME-STARTED\|{re.escape(game)}\|0\|", timeout=timeout)
    alice.expect(rf"GAME_MESSAGE\|TIME'S-UP\|{alice.name}\|", timeout=timeout)
    ended = bob.expect(rf"GAME_MESSAGE\|GAME-ENDED\|{re.escape(game)}\|(.*)\|\n", timeout=timeout)
    alice.expect(rf"GAME_MESSAGE\|GAME-ENDED\|{re.escape(game)}\|", timeout=timeout)
    return json.loads(ended.group(1))


def assert_no_server_errors(server):
    errors = server.error_log()
    assert "Traceback" not in errors and "Exception" not in errors, errors
