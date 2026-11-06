"""Live typing accounts (#20): which broker accounts and roles the server creates and deletes.

TypingAccess is tested with a fake broker admin that only records the commands. The real broker
is in test_mqtt_broker.py.
"""
import threading

import pytest

from server_mqtt import PLAYER_PREFIX, ROLE_PREFIX, TOPIC_PREFIX, TypingAccess


class FakeAdmin:
    def __init__(self):
        self.sent = []

    def send(self, commands):
        self.sent.extend(commands)

    def take(self) -> list[dict]:
        sent, self.sent = self.sent, []
        return sent


@pytest.fixture
def setup():
    admin = FakeAdmin()
    notified = []
    access = TypingAccess(admin, "broker.example", 8883, True, threading.RLock(),
                          lambda player, message: notified.append((player, message)))
    return access, admin, notified


def confirm(access, commands, error=None):
    """The broker answers the createClient commands."""
    for command in commands:
        if command["command"] == "createClient":
            response = {"command": "createClient", "correlationData": command["correlationData"]}
            if error:
                response["error"] = error
            access.on_response(response)


def names(commands, kind):
    return [c.get("username") or c.get("rolename") for c in commands if c["command"] == kind]


def test_creating_a_game_makes_a_role_and_an_account(setup):
    access, admin, notified = setup
    access.sync({"alice": "g1"}, {"g1"})
    role, client = admin.take()

    assert role["command"] == "createRole" and role["rolename"].startswith(ROLE_PREFIX)
    topic = TOPIC_PREFIX + role["rolename"][len(ROLE_PREFIX):]
    # Only this game's topic, no wildcard: a player can't read or write the other games
    assert {acl["topic"] for acl in role["acls"]} == {topic}
    assert {acl["acltype"] for acl in role["acls"]} == {"publishClientSend", "publishClientReceive", "subscribeLiteral"}
    assert "#" not in topic and "+" not in topic and "g1" not in topic

    assert client["command"] == "createClient" and client["username"].startswith(PLAYER_PREFIX)
    assert client["roles"] == [{"rolename": role["rolename"], "priority": -1}]
    assert len(client["password"]) >= 24

    assert notified == []  # not before the broker confirms the account exists
    confirm(access, [client])
    assert notified == [("alice", f"MQTT_|g1|broker.example|8883|True|{topic}|{client['username']}|{client['password']}|")]


def test_each_player_of_a_game_gets_their_own_account(setup):
    access, admin, notified = setup
    access.sync({"alice": "g1"}, {"g1"})
    role, alice = admin.take()
    access.sync({"alice": "g1", "bob": "g1"}, {"g1"})
    (bob,) = admin.take()  # same game: no new role

    assert bob["command"] == "createClient"
    assert bob["roles"] == alice["roles"]
    assert bob["username"] != alice["username"] and bob["password"] != alice["password"]


def test_nothing_for_players_in_the_menu_or_unchanged_state(setup):
    access, admin, _ = setup
    access.sync({"alice": None, "bob": "deleted-game"}, set())
    assert admin.take() == []
    access.sync({"alice": "g1"}, {"g1"})
    admin.take()
    access.sync({"alice": "g1"}, {"g1"})
    assert admin.take() == []


def test_leaving_deletes_the_account_and_the_last_one_the_role(setup):
    access, admin, _ = setup
    access.sync({"alice": "g1", "bob": "g1"}, {"g1"})
    created = admin.take()
    role = names(created, "createRole")[0]
    alice, bob = names(created, "createClient")

    access.sync({"alice": "g1", "bob": None}, {"g1"})
    assert admin.take() == [{"command": "deleteClient", "username": bob}]

    access.sync({"alice": None, "bob": None}, set())  # last player left: the game is deleted
    assert admin.take() == [{"command": "deleteClient", "username": alice},
                            {"command": "deleteRole", "rolename": role}]


def test_a_new_game_with_the_same_name_gets_a_new_topic(setup):
    access, admin, _ = setup
    access.sync({"alice": "g1"}, {"g1"})
    first_role = names(admin.take(), "createRole")[0]
    access.sync({"alice": None}, set())
    admin.take()
    access.sync({"bob": "g1"}, {"g1"})
    second_role = names(admin.take(), "createRole")[0]
    assert first_role != second_role


def test_changing_game_replaces_the_account(setup):
    access, admin, _ = setup
    access.sync({"alice": "g1", "bob": "g1"}, {"g1"})
    old_alice = names(admin.take(), "createClient")[0]
    access.sync({"alice": "g2", "bob": "g1"}, {"g1", "g2"})
    commands = admin.take()
    assert names(commands, "deleteClient") == [old_alice]
    assert len(names(commands, "createRole")) == 1 and len(names(commands, "createClient")) == 1


def test_no_account_sent_to_a_player_who_left_or_on_error(setup):
    access, admin, notified = setup
    access.sync({"alice": "g1", "bob": "g1"}, {"g1"})
    alice, bob = [c for c in admin.take() if c["command"] == "createClient"]
    access.sync({"alice": "g1", "bob": None}, {"g1"})  # bob leaves before the broker answers
    confirm(access, [bob])
    confirm(access, [alice], error="Client already exists")
    assert notified == []


def test_resend_after_a_reconnection(setup):
    access, admin, notified = setup
    access.sync({"alice": "g1"}, {"g1"})
    created = admin.take()
    access.resend("alice")
    assert notified == []  # not confirmed yet: it will be sent when it is
    confirm(access, created)
    access.resend("alice")
    assert len(notified) == 2 and notified[0] == notified[1]
    access.resend("nobody")
    assert len(notified) == 2


def test_startup_deletes_only_unknown_kaboom_accounts(setup):
    access, admin, _ = setup
    access.sync({"alice": "g1"}, {"g1"})
    created = admin.take()
    role, alice = names(created, "createRole")[0], names(created, "createClient")[0]

    access.on_connected()
    assert [c["command"] for c in admin.take()] == ["listClients", "listRoles"]
    access.on_response({"command": "listClients", "data": {"clients": [alice, "kaboom-admin", PLAYER_PREFIX + "old"]}})
    access.on_response({"command": "listRoles", "data": {"roles": [role, "admin", ROLE_PREFIX + "old"]}})
    assert admin.take() == [{"command": "deleteClient", "username": PLAYER_PREFIX + "old"},
                            {"command": "deleteRole", "rolename": ROLE_PREFIX + "old"}]


def test_turned_off_without_a_broker():
    access = TypingAccess(None, "", 0, False, threading.RLock(), lambda *_: pytest.fail("nothing to send"))
    access.sync({"alice": "g1"}, {"g1"})
    access.resend("alice")
    assert access.accounts == {} and not access.enabled

