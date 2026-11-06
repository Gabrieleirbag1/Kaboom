import threading, uuid
from paho.mqtt import client as mqtt_client
from client_utils import *
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

class Mqtt_Sub(threading.Thread):
    """Live typing (#20): shows what the other players of the game type, and sends what we type.

    The server gives each player their own broker account for the game (MQTT_ message, see
    client_utils.take_mqtt_access). This thread waits for it, connects, and connects again with a
    new account if the server sends one (after a reconnection).

    Attributes:
        game_name (str): The game whose account to use
        label (QLabel): The label to display the message
        username (str): The username of the user"""
    def __init__(self, topic: str = "test", label: QLabel = None, user: str = None):
        """Constructor of the Mqtt_Sub class

        Args:
            topic (str): The name of the game
            label (QLabel): The label to display the message
            user (str): The username of the user"""
        threading.Thread.__init__(self, daemon=True)
        self.game_name = topic
        self.label = label
        self.username = user
        self.running = True
        self.client: mqtt_client.Client | None = None
        self.topic: str | None = None  # given by the server with the account

    def connect_mqtt(self, access: dict):
        """Connect to the broker with the account given by the server (paho reconnects by itself).

        Args:
            access (dict): host, port, tls, topic, username, password"""
        self.disconnect()
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id=f"kaboom-{uuid.uuid4().hex}")
        client.username_pw_set(access["username"], access["password"])
        if access["tls"]:
            import certifi  # the .exe can't always find the system's certificates
            client.tls_set(ca_certs=certifi.where())
        client.reconnect_delay_set(1, 30)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        self.topic = access["topic"]
        client.connect_async(access["host"], access["port"], keepalive=30)
        client.loop_start()
        self.client = client

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            infos_logger.log_infos("[MQTT]", f"Failed to connect: {reason_code}")
            return
        infos_logger.log_infos("[MQTT]", f"Connected to the broker (game {self.game_name})")
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        """Shows the text typed by another player ("username|letters")."""
        sender, _, text = msg.payload.decode("utf-8", errors="replace").partition("|")
        if sender == self.username:
            return
        text = clean_typed_text(text)[:TYPED_TEXT_MAX]
        highlighted = highlight_syllable(text, syllabes[-1] if syllabes else "")
        QMetaObject.invokeMethod(self.label, "setText", Qt.QueuedConnection, Q_ARG(str, highlighted))

    def publish(self, msg: str = "message|hihi"):
        """Publish a message to the MQTT broker (dropped if not connected yet)

        Args:
            msg (str): The message to publish"""
        client, topic = self.client, self.topic
        if client is not None and topic:
            client.publish(topic, msg)

    def disconnect(self):
        if self.client is not None:
            self.client.disconnect()
            self.client.loop_stop()
            self.client = None

    def stop_loop(self) -> bool:
        """Stop the MQTT loop

        Returns:
            bool: True if the thread is not alive"""
        self.running = False
        return not self.is_alive() # return True if the thread is not alive

    def run(self):
        """Wait for the account, then stay connected until stop_loop()"""
        infos_logger.log_infos("[MQTT]", f"Waiting for the live typing account (game {self.game_name})")
        while self.running:
            access = take_mqtt_access(self.game_name)
            if access and not self.running:  # stopped meanwhile: leave it for the next window
                set_mqtt_access(access)
            elif access:
                self.connect_mqtt(access)
            time.sleep(0.2)
        self.disconnect()
        infos_logger.log_infos("[MQTT]", f"Stopping live typing (game {self.game_name})")
