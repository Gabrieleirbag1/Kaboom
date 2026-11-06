"""Live typing (#20): each player gets a throwaway broker account that only works for their game.

The letters a player types go to the other players of the game through the MQTT broker
(Mosquitto). Players never get a permanent password: this server logs into the broker as an
admin and, using Mosquitto's "dynamic security" plugin, creates
- one role per game, allowed only on that game's topic (kaboom/games/<random id>),
- one account per player in a game (random name and password), with that role.
The account is sent to the player (MQTT_ message) and deleted when they leave the game. Deleting
an account disconnects it at once. Leftovers from a crash are deleted when the server starts.

TypingAccess does the bookkeeping and BrokerAdmin talks to the broker, so the bookkeeping can be
tested without a broker.
"""
import json, logging, os, secrets, uuid
from dataclasses import dataclass
from typing import Callable
from server_logs import InfosLogger

infos_logger = InfosLogger()

PLAYER_PREFIX = "kaboom-p-"
ROLE_PREFIX = "kaboom-game-"
TOPIC_PREFIX = "kaboom/games/"
CONTROL_TOPIC = "$CONTROL/dynamic-security/v1"
RESPONSE_TOPIC = f"{CONTROL_TOPIC}/response"


@dataclass
class Account:
    game: str
    game_id: str
    username: str
    password: str
    ready: bool = False  # the broker confirmed it exists


def create_role_command(game_id: str) -> dict:
    """The role of one game: publish, receive and subscribe on its topic only (no wildcards)."""
    topic = TOPIC_PREFIX + game_id
    return {"command": "createRole", "rolename": ROLE_PREFIX + game_id, "acls": [
        {"acltype": "publishClientSend", "topic": topic, "priority": 0, "allow": True},
        {"acltype": "publishClientReceive", "topic": topic, "priority": 0, "allow": True},
        {"acltype": "subscribeLiteral", "topic": topic, "priority": 0, "allow": True},
    ]}


class TypingAccess:
    """Keeps one broker account per player in a game and one role per game.

    Every method runs with `lock` held (the server's state_lock): sync() is called by code that
    already holds it, and the broker's answers take it. Nothing here waits on the network.

    Args:
        admin: Object with send(commands: list[dict]), or None to turn live typing off.
        player_host / player_port / player_tls: Where the players connect to the broker.
        lock: Lock shared with the code that changes the players' state.
        notify: notify(player, message) sends a message to a player's current connection.
    """

    def __init__(self, admin, player_host: str, player_port: int, player_tls: bool,
                 lock, notify: Callable[[str, str], None]):
        self.admin = admin
        self.player_host = player_host
        self.player_port = player_port
        self.player_tls = player_tls
        self.lock = lock
        self.notify = notify
        self.topics: dict[str, str] = {}  # game name -> random id of its topic and role
        self.accounts: dict[str, Account] = {}  # player -> their account

    @property
    def enabled(self) -> bool:
        return self.admin is not None

    def sync(self, players_games: dict[str, str | None], game_names: set[str]) -> None:
        """Create and delete accounts and roles so they match the players' games.

        Args:
            players_games: Each logged-in player and their game (None in the menu).
            game_names: The games that exist."""
        if not self.enabled:
            return
        with self.lock:
            commands = []
            for player, account in list(self.accounts.items()):
                if players_games.get(player) != account.game or account.game not in game_names:
                    commands.append({"command": "deleteClient", "username": account.username})
                    del self.accounts[player]
            for game in list(self.topics):
                if game not in game_names:
                    commands.append({"command": "deleteRole", "rolename": ROLE_PREFIX + self.topics.pop(game)})
            for player, game in players_games.items():
                if game is None or game not in game_names or player in self.accounts:
                    continue
                if game not in self.topics:
                    self.topics[game] = secrets.token_hex(8)
                    commands.append(create_role_command(self.topics[game]))
                account = Account(game, self.topics[game], PLAYER_PREFIX + secrets.token_hex(8),
                                  secrets.token_urlsafe(24))
                self.accounts[player] = account
                commands.append({"command": "createClient", "username": account.username,
                                 "password": account.password, "correlationData": account.username,
                                 "roles": [{"rolename": ROLE_PREFIX + account.game_id, "priority": -1}]})
            if commands:
                self.admin.send(commands)

    def message(self, account: Account) -> str:
        return (f"MQTT_|{account.game}|{self.player_host}|{self.player_port}|{self.player_tls}|"
                f"{TOPIC_PREFIX}{account.game_id}|{account.username}|{account.password}|")

    def resend(self, player: str) -> None:
        """Send a player their account again (they reconnected and lost it)."""
        with self.lock:
            account = self.accounts.get(player)
            if account and account.ready:
                self.notify(player, self.message(account))

    def on_connected(self) -> None:
        """The admin connection is up: look for accounts and roles left by a crash."""
        self.admin.send([{"command": "listClients", "verbose": False, "count": -1, "offset": 0},
                         {"command": "listRoles", "verbose": False, "count": -1, "offset": 0}])

    def on_response(self, response: dict) -> None:
        """One answer of the broker to a command."""
        command, error = response.get("command"), response.get("error")
        with self.lock:
            if command == "createClient":
                username = response.get("correlationData")
                for player, account in self.accounts.items():
                    if account.username == username:
                        if error:
                            infos_logger.log_infos("[MQTT]", f"Account for {player} not created: {error}")
                        else:
                            account.ready = True
                            self.notify(player, self.message(account))
                        return
            elif error:
                infos_logger.log_infos("[MQTT]", f"{command} failed: {error}")
            elif command == "listClients":
                known = {account.username for account in self.accounts.values()}
                leftovers = [name for name in response.get("data", {}).get("clients", [])
                             if name.startswith(PLAYER_PREFIX) and name not in known]
                if leftovers:
                    infos_logger.log_infos("[MQTT]", f"Deleting {len(leftovers)} old player accounts")
                    self.admin.send([{"command": "deleteClient", "username": name} for name in leftovers])
            elif command == "listRoles":
                known = {ROLE_PREFIX + game_id for game_id in self.topics.values()}
                leftovers = [name for name in response.get("data", {}).get("roles", [])
                             if name.startswith(ROLE_PREFIX) and name not in known]
                if leftovers:
                    infos_logger.log_infos("[MQTT]", f"Deleting {len(leftovers)} old game roles")
                    self.admin.send([{"command": "deleteRole", "rolename": name} for name in leftovers])


class BrokerAdmin:
    """The server's own connection to the broker, as the dynamic security admin.

    send() never waits: paho keeps the commands and sends them from its own thread (also after a
    reconnection, they are QoS 1)."""

    def __init__(self, host: str, port: int, tls: bool, username: str, password: str,
                 on_response: Callable[[dict], None], on_connected: Callable[[], None]):
        from paho.mqtt import client as mqtt_client
        self.host, self.port = host, port
        self.on_response = on_response
        self.on_connected = on_connected
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2,
                                         client_id=f"kaboom-server-{uuid.uuid4().hex}")
        self.client.username_pw_set(username, password)
        if tls:
            import certifi
            self.client.tls_set(ca_certs=certifi.where())
        self.client.reconnect_delay_set(1, 30)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def start(self) -> None:
        infos_logger.log_infos("[MQTT]", f"Connecting to the broker {self.host}:{self.port}")
        self.client.connect_async(self.host, self.port, keepalive=30)
        self.client.loop_start()

    def send(self, commands: list[dict]) -> None:
        self.client.publish(CONTROL_TOPIC, json.dumps({"commands": commands}), qos=1)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            infos_logger.log_infos("[MQTT]", f"The broker refused the admin login: {reason_code}")
            return
        infos_logger.log_infos("[MQTT]", "Connected to the broker as admin")
        client.subscribe(RESPONSE_TOPIC, qos=1)
        self.on_connected()

    def _on_message(self, client, userdata, msg):
        try:
            for response in json.loads(msg.payload).get("responses", []):
                self.on_response(response)
        except Exception:
            logging.exception("Bad answer from the broker")


def create_typing_access(confs, lock, notify: Callable[[str, str], None]) -> TypingAccess:
    """TypingAccess connected to the broker, or turned off (KABOOM_DISABLE_MQTT=1, or no password)."""
    access = TypingAccess(None, confs.mqtt_player_host, confs.mqtt_player_port, confs.mqtt_player_tls,
                          lock, notify)
    if os.environ.get("KABOOM_DISABLE_MQTT") == "1":
        return access
    if not confs.mqtt_admin_password:
        infos_logger.log_infos("[MQTT]", "KABOOM_MQTT_PASSWORD is not set: live typing is off")
        return access
    access.admin = BrokerAdmin(confs.mqtt_admin_host, confs.mqtt_admin_port, confs.mqtt_admin_tls,
                               confs.mqtt_admin_user, confs.mqtt_admin_password,
                               on_response=access.on_response, on_connected=access.on_connected)
    access.admin.start()
    return access
