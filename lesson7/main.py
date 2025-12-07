import wifi_connect as wifi
import time
from umqtt.simple import MQTTClient

# MQTT 設定
MQTT_BROKER = "172.20.10.3"  # 公開測試用 Broker
MQTT_PORT = 1883
CLIENT_ID = "pico_w_publisher"
TOPIC = "pico/test"

# 嘗試連線 WiFi
wifi.connect()

# 顯示 IP
print("IP:", wifi.get_ip())

# 建立 MQTT 連線
print("正在連接 MQTT Broker...")
client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
client.connect()
print(f"已連接到 {MQTT_BROKER}")

# 每隔 10 秒發布一次訊息
counter = 0
while True:
    counter += 1
    message = f"Hello from Pico W! #{counter}"
    
    print("-" * 30)
    client.publish(TOPIC, message)
    print(f"已發布訊息: {message}")
    print(f"主題: {TOPIC}")
    
    print("等待 10 秒後再次發布...")
    time.sleep(10)