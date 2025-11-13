# subscriber.py
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
TOPIC = "demo/temperature"

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"已連線，原因碼：{reason_code}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"收到主題 {msg.topic}: {msg.payload.decode('utf-8')}")

client = mqtt.Client(protocol=mqtt.MQTTv5)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_HOST, port=1883, keepalive=60)
client.loop_forever()