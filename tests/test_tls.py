"""Encrypted game connections (#19): the real server with TLS, and players who check its certificate.

The rest of the suite runs on plain connections, so it sees the messages exactly as sent.
KABOOM_TEST_TLS=1 runs all of it encrypted too (CI does both).
"""
import functools
import os
import shutil
import socket
import ssl
import threading
import time

import pytest
from harness import (FakeClient, ServerProcess, assert_no_server_errors, client_tls_context,
                     make_both_ready, make_certificate, play_until_bob_wins, setup_lobby,
                     shared_certificate, tls_server_env)
from server_protocol import PROTOCOL_VERSION, Connection, MessageBuffer, encode

TLS_SERVER = pytest.mark.server_env(**tls_server_env())


@pytest.fixture
def tls_client(make_client):
    return functools.partial(make_client, tls=True)


def server_log(server) -> str:
    return (server.log_dir / "infos.log").read_text(encoding="utf-8")


# --- The real server ------------------------------------------------------------------------

@TLS_SERVER
def test_full_game_over_tls(server, tls_client):
    alice, bob = setup_lobby(tls_client)
    make_both_ready(alice, bob)
    assert play_until_bob_wins(alice, bob)[0][0] == "bob"
    log = server_log(server)
    assert "Certificate loaded" in log
    assert "[RECEIVED] - NEW-USER_|alice|" in log  # the server reads the messages fine
    assert_no_server_errors(server)


@TLS_SERVER
def test_full_game_over_tls_and_a_bad_network(server, tls_client, make_proxy):
    """Encrypted records cut into pieces and merged together, like on the internet."""
    proxy = make_proxy(merge=True, split=True, seed=1)
    alice, bob = setup_lobby(tls_client, via=proxy)
    make_both_ready(alice, bob)
    assert play_until_bob_wins(alice, bob, timeout=20)[0][0] == "bob"
    assert_no_server_errors(server)


@TLS_SERVER
def test_client_without_tls_is_dropped(server, make_client, tls_client):
    old = make_client("old", tls=False)
    old.send(f"NEW-USER_|old|pizza-avatar|{PROTOCOL_VERSION}")
    with pytest.raises(AssertionError, match="connection closed"):
        old.expect(r"NAME_CORRECT", timeout=5)
    tls_client("alice").login()  # the server is fine
    assert "TLS handshake failed" in server_log(server)
    assert_no_server_errors(server)


@pytest.mark.server_env(**tls_server_env(), KABOOM_HANDSHAKE_TIMEOUT="1")
def test_silent_connection_does_not_block_logins(server, tls_client):
    silent = socket.create_connection(("127.0.0.1", server.port))  # connects, never says hello
    try:
        start = time.monotonic()
        tls_client("alice").login()
        assert time.monotonic() - start < 2
        silent.settimeout(5)
        try:
            assert silent.recv(100) == b""  # dropped after KABOOM_HANDSHAKE_TIMEOUT
        except ConnectionResetError:
            pass
    finally:
        silent.close()
    assert_no_server_errors(server)


@TLS_SERVER
def test_client_refuses_a_certificate_it_cannot_trust(server):
    with pytest.raises(ssl.SSLCertVerificationError):  # not from a known authority
        FakeClient(server.port, "x", tls=ssl.create_default_context())
    with pytest.raises(ssl.SSLCertVerificationError):  # valid, but for another name
        FakeClient(server.port, "x", tls=True, server_hostname="missclick.net")
    assert_no_server_errors(server)


def test_renewed_certificate_is_used_without_restart(tmp_path):
    ca = shared_certificate()
    first = make_certificate(tmp_path / "first", ca=(ca["ca"], ca["ca_key"]))
    second = make_certificate(tmp_path / "second", ca=(ca["ca"], ca["ca_key"]))
    live = tmp_path / "live"
    live.mkdir()
    cert, key = live / "fullchain.pem", live / "privkey.pem"
    stamp = [time.time_ns()]

    def install(source, target):  # like certbot's hook: new file, new date
        shutil.copyfile(source, target)
        stamp[0] += 1_000_000_000
        os.utime(target, ns=(stamp[0], stamp[0]))

    def served() -> bytes:
        client = FakeClient(server.port, "x", tls=True)
        try:
            return client.sock.peer_certificate()
        finally:
            client.close()

    def der(certificate) -> bytes:
        return ssl.PEM_cert_to_DER_cert(certificate["cert"].read_text())

    install(first["cert"], cert)
    install(first["key"], key)
    server = ServerProcess(tmp_path / "logs", **tls_server_env({"cert": cert, "key": key}))
    try:
        assert served() == der(first)
        install(second["cert"], cert)  # the hook copied the new certificate, not its key yet
        assert served() == der(first)  # the old pair is still used
        install(second["key"], key)
        assert served() == der(second)
        assert "keeping the old one" in server_log(server)
        assert_no_server_errors(server)
    finally:
        server.stop()


def test_server_without_its_certificate_does_not_start(tmp_path):
    missing = tmp_path / "nothing.pem"
    with pytest.raises(RuntimeError, match="Can't load the TLS certificate"):
        ServerProcess(tmp_path / "logs", **tls_server_env({"cert": missing, "key": missing}))


# --- The Connection class -------------------------------------------------------------------

def connected_pair(server_sock=None) -> tuple[Connection, Connection]:
    """(client, server) Connections over a local socket pair, handshake done."""
    a, b = socket.socketpair()
    certificate = shared_certificate()
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(certificate["cert"], certificate["key"])
    client = Connection(a, client_tls_context(), server_hostname="127.0.0.1")
    server = Connection(server_sock(b) if server_sock else b, server_context, server_side=True)
    done = threading.Thread(target=server.handshake)
    done.start()
    client.handshake()
    done.join()
    return client, server


def test_reading_and_sending_from_several_threads_at_once():
    """Like the game: one thread reads while others send, on both sides."""
    senders, count = 3, 1500
    client, server = connected_pair()
    received = {"client": [], "server": []}
    errors = []

    def send(conn, side, sender):
        try:
            for i in range(count):
                conn.sendall(encode(f"{side}{sender}|{i}|" + "x" * (i % 300)))
        except Exception as e:  # noqa: BLE001  (reported below)
            errors.append(e)

    def read(conn, side):
        buffer = MessageBuffer()
        try:
            while len(received[side]) < senders * count:
                data = conn.recv(65536, timeout=20)
                assert data, "closed"
                received[side] += buffer.feed(data)
        except Exception as e:  # noqa: BLE001
            errors.append(e)

    threads = [threading.Thread(target=read, args=(client, "client")),
               threading.Thread(target=read, args=(server, "server"))]
    for sender in range(senders):
        threads += [threading.Thread(target=send, args=(client, "c", sender)),
                    threading.Thread(target=send, args=(server, "s", sender))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(60)
    assert not errors, errors
    for side, prefix in (("server", "c"), ("client", "s")):
        for sender in range(senders):
            numbers = [int(m.split("|")[1]) for m in received[side] if m.startswith(f"{prefix}{sender}|")]
            assert numbers == list(range(count))  # all there, in order
    client.close()
    server.close()


def test_what_travels_on_the_network_is_encrypted():
    class Recorder:
        """A socket that keeps what it receives."""
        def __init__(self, sock):
            self.sock, self.seen = sock, b""

        def recv(self, n):
            data = self.sock.recv(n)
            self.seen += data
            return data

        def __getattr__(self, name):
            return getattr(self.sock, name)

    recorders = []
    client, server = connected_pair(lambda s: recorders.append(Recorder(s)) or recorders[-1])
    client.sendall(encode("JOIN-GAME_|partie1|my-secret-password|alice"))
    assert server.recv(4096, timeout=5) == b"JOIN-GAME_|partie1|my-secret-password|alice\n"
    assert b"my-secret-password" not in recorders[0].seen and recorders[0].seen
    client.close()
    server.close()


def test_recv_timeout_leaves_the_connection_usable():
    client, server = connected_pair()
    with pytest.raises(TimeoutError):
        server.recv(4096, timeout=0.2)
    client.sendall(b"PING_|\n")
    assert server.recv(4096, timeout=5) == b"PING_|\n"
    client.close()
    try:  # closed by the other side (reset if it closed with data left unread, like the TLS tickets)
        assert server.recv(4096, timeout=5) == b""
    except ConnectionResetError:
        pass
    server.close()


# --- The real game client -------------------------------------------------------------------

def wait_for_client_log(gui, text: str, timeout: float = 20):
    log = gui.config_dir / "logs" / "infos.log"
    deadline = time.monotonic() + timeout
    while text not in (log.read_text(encoding="utf-8") if log.exists() else ""):
        assert time.monotonic() < deadline, gui.log()
        time.sleep(0.3)


@pytest.mark.gui
@TLS_SERVER
def test_real_client_logs_in_over_tls(server, make_gui):
    gui = make_gui(env={"KABOOM_SERVER_TLS": "True", "KABOOM_SERVER_CAFILE": str(shared_certificate()["ca"])})
    gui.wait_for(lambda st: st["login_visible"])
    wait_for_client_log(gui, "Connection established")
    gui.call("login", name="bob")
    gui.wait_for(lambda st: st["window_visible"])
    assert "[RECEIVED] - NEW-USER_|bob|" in server_log(server)
    assert gui.errors() == ""


@pytest.mark.gui
@TLS_SERVER
def test_real_client_refuses_a_server_it_cannot_trust(server, make_gui, tmp_path):
    other_ca = make_certificate(tmp_path / "other")["ca"]  # the server's certificate isn't from it
    gui = make_gui(env={"KABOOM_SERVER_TLS": "True", "KABOOM_SERVER_CAFILE": str(other_ca)})
    gui.wait_for(lambda st: st["login_visible"])
    wait_for_client_log(gui, "certificate is not valid")
    gui.call("login", name="bob")  # the player is told, instead of nothing happening
    state = gui.wait_for(lambda st: st["login_text"] != "")[-1]
    assert state["login_text"] == "Connection failed" and not state["window_visible"]
    assert "NEW-USER_" not in server_log(server)
    assert gui.errors() == ""
