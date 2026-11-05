"""Unit tests for the message framing shared by the client and the server."""
from pathlib import Path

import pytest
from server_protocol import (MAX_MESSAGE_SIZE, MessageBuffer, encode, is_valid_text_field,
                             is_valid_username)

ROOT = Path(__file__).resolve().parent.parent


def test_client_and_server_copies_are_identical():
    server = (ROOT / "Server" / "server_protocol.py").read_text(encoding="utf-8")
    client = (ROOT / "Client" / "client_protocol.py").read_text(encoding="utf-8")
    assert server == client, "Copy Server/server_protocol.py to Client/client_protocol.py"


def test_encode_adds_a_newline():
    assert encode("NEW-USER_|Zoé|pizza") == "NEW-USER_|Zoé|pizza\n".encode()


def test_encode_refuses_a_newline_inside():
    with pytest.raises(ValueError):
        encode("a\nb")


def test_one_message():
    assert MessageBuffer().feed(b"NAME_CORRECT|\n") == ["NAME_CORRECT|"]


def test_merged_messages_are_separated():
    assert MessageBuffer().feed(b"A|1|\nB|2|\n") == ["A|1|", "B|2|"]


def test_message_cut_in_pieces_is_rebuilt():
    buffer = MessageBuffer()
    assert buffer.feed(b"GAME_MESSAGE|GAME") == []
    assert buffer.feed(b"-STARTED|p|0|\nSYLL") == ["GAME_MESSAGE|GAME-STARTED|p|0|"]
    assert buffer.feed(b"ABE_|ou|alice|0|\n") == ["SYLLABE_|ou|alice|0|"]


def test_accented_letter_cut_in_half():
    data = "CREATE-GAME_|Zoé|partie|\n".encode()
    middle = data.index("é".encode()) + 1
    buffer = MessageBuffer()
    assert buffer.feed(data[:middle]) == []
    assert buffer.feed(data[middle:]) == ["CREATE-GAME_|Zoé|partie|"]


def test_empty_lines_are_ignored():
    assert MessageBuffer().feed(b"\n\nA|\n\n") == ["A|"]


def test_too_long_message_is_refused():
    with pytest.raises(ValueError):
        MessageBuffer().feed(b"x" * (MAX_MESSAGE_SIZE + 1))


@pytest.mark.parametrize("name, valid", [
    ("alice", True), ("Zoé", True), ("joueur42", True),
    ("", False), ("al|ce", False), ("al,ce", False), ("jean_pierre", False), ("a b", False),
])
def test_is_valid_username(name, valid):
    assert is_valid_username(name) is valid


@pytest.mark.parametrize("text, valid", [
    ("la_partie de Zoé !", True), ("", False), ("   ", False),
    ("a|b", False), ("a,b", False), ("a#b", False), ("a+b", False), ("a\tb", False),
])
def test_is_valid_text_field(text, valid):
    assert is_valid_text_field(text) is valid


def test_empty_password_is_allowed():
    assert is_valid_text_field("", allow_empty=True)
    assert not is_valid_text_field("  ", allow_empty=True)
