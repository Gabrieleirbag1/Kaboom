"""Unit tests for the server's pure helper functions (no network)."""
import server_utils
from server_confs import Configurations
from server_reception import Reception


def test_convert_word_removes_accents_and_uppercase():
    assert server_utils.convert_word("Éléphant") == "elephant"
    assert server_utils.convert_word("ÇA") == "ca"


def test_bool_convert():
    assert server_utils.bool_convert("False") is False
    assert server_utils.bool_convert("True") is True
    # Anything that is not exactly "False" counts as True (current behaviour).
    assert server_utils.bool_convert("false") is True


def test_get_csv_returns_first_column_and_skips_empty_lines(tmp_path):
    csv_file = tmp_path / "words.csv"
    csv_file.write_text("maison,house\n\nchat\n\"guillemets\"\n", encoding="utf-8")
    assert server_utils.get_csv(str(csv_file)) == ["maison", "chat", "guillemets"]


def test_read_words_from_file_loads_syllables():
    syllables = server_utils.read_words_from_file("Français")
    assert len(syllables) > 1000
    assert all("," not in s and "\n" not in s for s in syllables)


def test_read_words_from_file_falls_back_to_english():
    assert server_utils.read_words_from_file("Klingon") == server_utils.read_words_from_file("English")


def test_dictionaries_are_loaded_for_each_language():
    assert "maison" in server_utils.Français_dictionnaire
    assert "water" in server_utils.English_dictionnaire


def test_check_syllabe():
    assert Reception.check_syllabe(None, "maison", "ai") is True
    assert Reception.check_syllabe(None, "maison", "ou") is False


def test_configurations_read_from_file():
    confs = Configurations()
    assert confs.socket_port == 22222
    assert confs.socket_host == "0.0.0.0"


def test_configurations_env_override(monkeypatch):
    monkeypatch.setenv("KABOOM_SOCKET_HOST", "127.0.0.1")
    monkeypatch.setenv("KABOOM_SOCKET_PORT", "4242")
    confs = Configurations()
    assert (confs.socket_host, confs.socket_port) == ("127.0.0.1", 4242)
