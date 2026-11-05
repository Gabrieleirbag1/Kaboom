"""How the client and the server cut the TCP stream into messages.

TCP is a stream: over the internet, two messages sent quickly can arrive together in one
recv(), and one message can arrive in several pieces. So every message ends with a newline,
and MessageBuffer gives back only complete messages.

This file exists twice, as Server/server_protocol.py and Client/client_protocol.py (the client
is packaged without the Server folder). Both copies must stay identical: a test checks it.
"""
import re

# Bump when the message format changes. The client sends it at login (NEW-USER_) and the
# server refuses clients with another version, so players get a clear "please update" message.
PROTOCOL_VERSION = "2"

SEPARATOR = b"\n"
MAX_MESSAGE_SIZE = 64 * 1024  # a message is never this long: protects the server's memory

# Same rule as the login screen (Client/client.py restricted_caracters)
USERNAME_PATTERN = re.compile(r"[a-zA-ZÀ-ÿ0-9]+")
# '|' separates fields; ',' separates lists of names; '#' and '+' are MQTT wildcards
# (the game name is used as the MQTT topic); control characters would break the framing.
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
