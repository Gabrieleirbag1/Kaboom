import threading
from paho.mqtt import client as mqtt_client
from client_utils import *
from PyQt5.QtCore import QMetaObject, Qt
import threading

class Mqtt_Sub(threading.Thread):
    def __init__(self, topic : str = "test", label : QLabel = None, user : str = None): 
        threading.Thread.__init__(self)
        self.topic = topic
        self.label = label
        self.username = user
        self.running = True
        
    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"Connected to MQTT Broker! (topic {self.topic})")
            else:
                print("Failed to connect, return code %d\n", rc)
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
        self.client = client
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client
    
    def subscribe(self, client: mqtt_client, topic : str):
        # print("on_msg")

        def on_message(client, userdata, msg):
            message = str(msg.payload.decode()).split("|")
            if message[0] != self.username:
                QMetaObject.invokeMethod(self.label, "setText", Qt.QueuedConnection, Q_ARG(str, message[1]))
                # print(f"Received `{message[1]}` from `{message[0]}` user")
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic, {self.username} user")
        client.subscribe(self.topic)
        client.on_message = on_message
    
    def publish(self, msg : str = "message|hihi"):
        result = self.client.publish(self.topic, msg)
        # result: [0, 1]
        status = result[0]
        # if status == 0:
        #     print(f"Send `{msg}` to self.topic `{self.topic}`")
        # else:
        #     print(f"Failed to send message to topic {self.topic}")

    def stop_loop(self):
        self.running = False
        print("stopped mqtt loop")
        return not self.is_alive() # return True if the thread is not alive
    
    def run(self):
        # print("STARTED MQTT")
        client = self.connect_mqtt()
        self.subscribe(client, self.topic)
        while self.running:
            client.loop()
        client.disconnect()
        # print("ENDED MQTT")

if __name__ == '__main__':
    mqtt_sub = Mqtt_Sub()
    mqtt_sub.start()

