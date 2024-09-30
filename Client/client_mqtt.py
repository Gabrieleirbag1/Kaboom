import threading
from paho.mqtt import client as mqtt_client
from client_utils import *
from client_logs import ErrorLogger

ErrorLogger.setup_logging()

class Mqtt_Sub(threading.Thread):
    """Class to manage the MQTT subscription
    
    Attributes:
        topic (str): The topic to subscribe to (default "test")
        label (QLabel): The label to display the message
        user (str): The username of the user"""
    def __init__(self, topic: str = "test", label: QLabel = None, user: str = None): 
        """Constructor of the Mqtt_Sub class
        
        Args:
            topic (str): The topic to subscribe to (default "test")
            label (QLabel): The label to display the message
            user (str): The username of the user"""
        threading.Thread.__init__(self)
        self.topic = topic
        self.label = label
        self.username = user
        self.running = True
        
    def connect_mqtt(self) -> mqtt_client:
        """Connect to the MQTT broker
        
        Returns:
            mqtt_client: The MQTT client"""
        def on_connect(client, userdata, flags, rc):
            """Function to connect to the MQTT broker
            
            Args:
                client (mqtt_client): The MQTT client
                userdata (object): The userdata
                flags (dict): The flags
                rc (int): The return code"""
            if rc == 0:
                infos_logger.log_infos("[MQTT]", f"Connected to MQTT Broker! (topic {self.topic})")
            else:
                infos_logger.log_infos("[MQTT]", "Failed to connect, return code %d\n", rc)
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, confs.client_id)
        self.client = client
        client.username_pw_set(confs.user, confs.password)
        client.on_connect = on_connect
        client.connect(confs.broker, confs.port)
        return client
    
    def subscribe(self, client: mqtt_client, topic : str):
        """Subscribe to a topic
        
        Args:
            client (mqtt_client): The MQTT client
            topic (str): The topic to subscribe to (default "test")"""
        # print("on_msg")
        def on_message(client, userdata, msg):
            """Function to handle the message received from the MQTT broker
            
            Args:
                client (mqtt_client): The MQTT client
                userdata (object): The userdata
                msg (object): The message received"""
            message = str(msg.payload.decode()).split("|")
            if message[0] != self.username:
                QMetaObject.invokeMethod(self.label, "setText", Qt.QueuedConnection, Q_ARG(str, message[1]))
                # print(f"Received `{message[1]}` from `{message[0]}` user")
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic, {self.username} user")
        client.subscribe(self.topic)
        client.on_message = on_message
    
    def publish(self, msg: str = "message|hihi"):
        """Publish a message to the MQTT broker
        
        Args:
            msg (str): The message to publish"""
        result = self.client.publish(self.topic, msg)
        # result: [0, 1]
        status = result[0]
        # if status == 0:
        #     print(f"Send `{msg}` to self.topic `{self.topic}`")
        # else:
        #     print(f"Failed to send message to topic {self.topic}")

    def stop_loop(self) -> bool:
        """Stop the MQTT loop
        
        Returns:
            bool: True if the thread is not alive"""
        self.running = False
        return not self.is_alive() # return True if the thread is not alive
    
    def run(self):
        """Run the MQTT loop"""
        infos_logger.log_infos("[MQTT]", f"Starting MQTT topic {self.topic}")
        client = self.connect_mqtt()
        self.subscribe(client, self.topic)
        while self.running:
            client.loop()
        client.disconnect()
        infos_logger.log_infos("[MQTT]", f"Stopping MQTT topic {self.topic}")
