from server_utils import *
from paho.mqtt import client as mqtt_client
import threading
from server_logs import ErrorLogger

ErrorLogger.setup_logging()

class Mqtt_Sub(threading.Thread):
    """Class that manages the MQTT subscriber.
    
    Attributes:
        topic (str): The topic to subscribe to.
        running (bool): Whether the subscriber is running.
    """
    def __init__(self, topic: str = "test"): 
        """Initializes the MQTT subscriber.
        
        Args:
            topic (str): The topic to subscribe to.
        """
        threading.Thread.__init__(self)
        self.topic = topic
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
        client.username_pw_set(confs.username, confs.password)
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
            pass
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        client.subscribe(self.topic)
        client.on_message = on_message
    
    def stop_loop(self):
        """Stop the MQTT loop
        
        Returns:
            bool: True if the thread is not alive"""
        self.running = False
    
    def run(self):
        """Run the MQTT loop"""
        infos_logger.log_infos("[MQTT]", f"Starting MQTT topic {self.topic}")
        client = self.connect_mqtt()
        self.subscribe(client, self.topic)
        while self.running:
            client.loop()
        client.disconnect()
        infos_logger.log_infos("[MQTT]", f"Stopping MQTT topic {self.topic}")

if __name__ == '__main__':
    mqtt_sub = Mqtt_Sub()
    mqtt_sub.start()

