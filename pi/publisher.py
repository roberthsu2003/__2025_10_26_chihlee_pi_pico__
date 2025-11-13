# publisher.py
import time
import paho.mqtt.client as mqtt


BROKER_HOST = "localhost"
TOPIC = "demo/temperature"

client = mqtt.Client(
    client_id="temperature-publisher",
    protocol=mqtt.MQTTv5,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
)
client.reconnect_delay_set(min_delay=1, max_delay=5)

try:
    client.connect(BROKER_HOST, port=1883, keepalive=60)
    client.loop_start()

    for value in range(25, 31):
        payload = f"{value} °C"
        info = client.publish(TOPIC, payload=payload, qos=1, retain=False)
        info.wait_for_publish(timeout=5)
        if info.is_published():
            print(f"已發布：{payload}")
        else:
            print(f"警告：{payload} 發佈超時")
        time.sleep(2)
finally:
    client.loop_stop()
    client.disconnect()
