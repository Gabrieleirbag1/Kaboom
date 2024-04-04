# python3.6

import threading
from paho.mqtt import client as mqtt_client
from client_utils import *

class Mqtt_Sub(threading.Thread):
    def __initi__(self) -> None:
        threading.Thread.__init__(self)

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client


    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            client.loop_stop()


        client.subscribe(topic)
        client.on_message = on_message


    def run(self):
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_forever()


if __name__ == '__main__':
    mqtt_sub = Mqtt_Sub()
    mqtt_sub.start()
