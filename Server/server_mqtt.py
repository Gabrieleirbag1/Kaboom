import threading
from paho.mqtt import client as mqtt_client
from server_utils import *
import threading

class Mqtt_Sub(threading.Thread):
    def __init__(self, topic : str = "test"): 
        threading.Thread.__init__(self)
        self.topic = topic
        self.running = True
        
    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, confs.client_id)
        client.username_pw_set(confs.username, confs.password)
        client.on_connect = on_connect
        client.connect(confs.broker, confs.port)
        return client
    
    def subscribe(self, client: mqtt_client, topic : str):
        def on_message(client, userdata, msg):
            pass
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        client.subscribe(self.topic)
        client.on_message = on_message
    
    def stop_loop(self):
        self.running = False
    
    def run(self):
        # time.sleep(3)
        client = self.connect_mqtt()
        self.subscribe(client, self.topic)
        while self.running:
            client.loop()
        client.disconnect()
        # print("end run")

if __name__ == '__main__':
    mqtt_sub = Mqtt_Sub()
    mqtt_sub.start()

