"""How the client and the server talk: one connection (Connection, encrypted with TLS), cut into
messages (encode, MessageBuffer).

TCP is a stream: over the internet, two messages sent quickly can arrive together in one
recv(), and one message can arrive in several pieces. So every message ends with a newline,
and MessageBuffer gives back only complete messages.

This file exists twice, as Server/server_protocol.py and Client/client_protocol.py (the client
is packaged without the Server folder). Both copies must stay identical: a test checks it.
"""
import re
import select
import ssl
import threading
import time

# Bump when the message format changes. The client sends it at login (NEW-USER_) and the
# server refuses clients with another version, so players get a clear "please update" message.
PROTOCOL_VERSION = "2"

SEPARATOR = b"\n"
MAX_MESSAGE_SIZE = 64 * 1024  # a message is never this long: protects the server's memory

# Same rule as the login screen (Client/client.py restricted_caracters)
USERNAME_PATTERN = re.compile(r"[a-zA-ZÀ-ÿ0-9]+")
# '|' separates fields; ',' separates lists of names; '#' and '+' are MQTT wildcards
# (kept out of names to be safe); control characters would break the framing.
FORBIDDEN_CHARS = re.compile(r"[|,#+\x00-\x1f\x7f]")


def encode(message: str) -> bytes:
    """Turn one message into bytes ready to send."""
    if "\n" in message:
        raise ValueError(f"A message cannot contain a newline: {message!r}")
    return message.encode("utf-8") + SEPARATOR


class MessageBuffer:
    """Collects received bytes and returns the complete messages."""

    def __init__(self):
        self._pending = b""

    @property
    def pending(self) -> bool:
        """True if part of a message was received but not its end."""
        return bool(self._pending)

    def feed(self, data: bytes) -> list[str]:
        """Add received bytes. Returns the messages completed by them (maybe none)."""
        self._pending += data
        *complete, self._pending = self._pending.split(SEPARATOR)
        if len(self._pending) > MAX_MESSAGE_SIZE:
            self._pending = b""
            raise ValueError("Message too long")
        # Cutting on b"\n" never splits a UTF-8 character, so each complete line decodes fine.
        return [line.decode("utf-8", errors="replace") for line in complete if line]


def is_valid_username(name: str) -> bool:
    return bool(USERNAME_PATTERN.fullmatch(name))


def is_valid_text_field(text: str, allow_empty: bool = False) -> bool:
    """For game names and passwords, which players can type freely."""
    if not text.strip():
        return allow_empty and text == ""
    return not FORBIDDEN_CHARS.search(text)


HANDSHAKE_TIMEOUT = 10.0  # seconds to set up the encryption of a new connection


class Connection:
    """One connection to the other side, encrypted with TLS when `context` is given (#19).

    Kaboom reads a connection in one thread while other threads send on it. Python's ssl sockets
    must not be used like that (reading can make OpenSSL write, and the two would mix). So the
    encryption runs in memory (ssl.SSLObject) under a lock, and this class does the network reads
    and writes itself. Without TLS the data just passes through, with the same methods.

    Use it like a socket: handshake() once, then recv() / sendall() / shutdown() / close().
    """

    def __init__(self, sock, context: ssl.SSLContext | None = None, server_side: bool = False,
                 server_hostname: str | None = None):
        self.sock = sock
        self.tls = context is not None
        self._lock = threading.Lock()       # the SSLObject and its memory buffers
        self._send_lock = threading.Lock()  # one sender at a time: data stays in order
        self._ready = threading.Event()     # set when the handshake is over (or failed)
        self._failed = False
        if self.tls:
            self._incoming, self._outgoing = ssl.MemoryBIO(), ssl.MemoryBIO()
            self._ssl = context.wrap_bio(self._incoming, self._outgoing, server_side=server_side,
                                         server_hostname=server_hostname)
        else:
            self._ready.set()

    def __repr__(self) -> str:
        try:
            peer = "%s:%s" % self.sock.getpeername()[:2]
        except (OSError, TypeError):
            peer = "closed"
        return f"<Connection {'tls' if self.tls else 'plain'} {peer}>"

    # --- socket-like methods ------------------------------------------------------------------
    def handshake(self, timeout: float = HANDSHAKE_TIMEOUT):
        """Set up the encryption (does nothing without TLS). Raises OSError (ssl.SSLError,
        TimeoutError...) if the other side doesn't speak TLS, has a bad certificate or is too slow."""
        if not self.tls:
            return
        deadline = time.monotonic() + timeout
        try:
            while True:
                with self._lock:
                    try:
                        self._ssl.do_handshake()
                        done = True
                    except ssl.SSLWantReadError:
                        done = False
                self._flush()
                if done:
                    return
                self._receive_raw(deadline)
        except BaseException:
            self._failed = True
            raise
        finally:
            self._ready.set()

    def recv(self, bufsize: int, timeout: float | None = None) -> bytes:
        """Like socket.recv(): b"" when the other side closed. `timeout` (seconds) raises
        TimeoutError if nothing arrives in time, without changing the socket's own timeout
        (which also applies to sending)."""
        deadline = None if timeout is None else time.monotonic() + timeout
        if not self.tls:
            if deadline is not None:
                self._wait_readable(deadline)
            return self.sock.recv(bufsize)
        self._wait_ready()
        while True:
            with self._lock:
                try:
                    data = self._ssl.read(bufsize)
                except ssl.SSLWantReadError:
                    data = None
                except (ssl.SSLZeroReturnError, ssl.SSLEOFError):  # closed (cleanly or not)
                    data = b""
            self._flush()  # reading can produce data to send (TLS 1.3 key updates)
            if data is not None:
                return data
            self._receive_raw(deadline)

    def sendall(self, data: bytes):
        """Like socket.sendall(). Safe to call from several threads, and while another reads."""
        if not self.tls:
            with self._send_lock:
                self.sock.sendall(data)
            return
        self._wait_ready()
        with self._send_lock:
            with self._lock:
                view = memoryview(data)
                while view:
                    view = view[self._ssl.write(view):]
                encrypted = self._outgoing.read()
            self.sock.sendall(encrypted)

    def peer_certificate(self) -> bytes | None:
        """The other side's certificate (DER bytes), None without TLS."""
        if not self.tls:
            return None
        with self._lock:  # never while another thread reads: OpenSSL may be in the middle of a message
            return self._ssl.getpeercert(binary_form=True)

    def settimeout(self, timeout: float | None):
        self.sock.settimeout(timeout)

    def gettimeout(self) -> float | None:
        return self.sock.gettimeout()

    def setsockopt(self, *args):
        self.sock.setsockopt(*args)

    def fileno(self) -> int:
        return self.sock.fileno()

    def shutdown(self, how: int):
        self.sock.shutdown(how)

    def close(self):
        self.sock.close()

    # --- internals ----------------------------------------------------------------------------
    def _wait_ready(self):
        """Senders wait for the handshake (the server may send to a client that is still
        setting up the encryption)."""
        if not self._ready.wait(HANDSHAKE_TIMEOUT + 5) or self._failed:
            raise ConnectionError("The encrypted connection is not set up")

    def _flush(self):
        """Send what OpenSSL wrote in the outgoing buffer, if anything."""
        if not self._outgoing.pending:
            return
        with self._send_lock:
            with self._lock:
                encrypted = self._outgoing.read()
            if encrypted:
                self.sock.sendall(encrypted)

    def _receive_raw(self, deadline: float | None):
        """Read encrypted bytes from the network into OpenSSL."""
        if deadline is not None:
            self._wait_readable(deadline)
        raw = self.sock.recv(65536)
        with self._lock:
            if raw:
                self._incoming.write(raw)
            else:
                self._incoming.write_eof()

    def _wait_readable(self, deadline: float):
        left = deadline - time.monotonic()
        if left <= 0:
            raise TimeoutError("timed out")
        fd = self.sock.fileno()
        if fd < 0:
            raise OSError("The connection is closed")
        if hasattr(select, "poll"):  # no limit on the number of open connections, unlike select()
            poller = select.poll()
            poller.register(fd, select.POLLIN)
            ready = poller.poll(left * 1000)
        else:  # Windows
            ready, _, _ = select.select([fd], [], [], left)
        if not ready:
            raise TimeoutError("timed out")
