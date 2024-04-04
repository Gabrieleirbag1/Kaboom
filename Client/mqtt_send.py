# python 3.6

import time, threading
from paho.mqtt import client as mqtt_client
from client_utils import *

class Mqtt_Sender(threading.Thread):

    def __init__(self) -> None: 
        threading.Thread.__init__(self)

    def connect_mqtt(self):
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


    def publish(self, client):
        msg_count = 1
        while True:
            time.sleep(1)
            msg = f"messages: {msg_count}"
            result = client.publish(topic, msg)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{msg}` to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")
            msg_count += 1
            if msg_count > 5:
                break


    def run(self):
        client = self.connect_mqtt()
        client.loop_start()
        self.publish(client)
        client.loop_stop()


if __name__ == '__main__':
    mqtt_send = Mqtt_Sender()
    mqtt_send.start()
