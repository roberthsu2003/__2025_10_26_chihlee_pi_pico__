import wifi_connect as wifi
import time
import json
import random
from umqtt.simple import MQTTClient

# MQTT 設定
MQTT_BROKER = "172.20.10.3"  # 公開測試用 Broker
MQTT_PORT = 1883
CLIENT_ID = "pico_w_publisher"
TOPIC = "living_room/sensor"  # 改用英文主題避免編碼問題
KEEPALIVE = 60  # 保持連線時間（秒）

# 嘗試連線 WiFi
wifi.connect()

# 顯示 IP
print("IP:", wifi.get_ip())

# 建立 MQTT 客戶端（加入 keepalive 設定）
client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, keepalive=KEEPALIVE)

def mqtt_connect():
    """連接 MQTT Broker"""
    print("正在連接 MQTT Broker...")
    client.connect()
    print(f"已連接到 {MQTT_BROKER}")

# 初始連線
mqtt_connect()

# 每隔 10 秒發布一次訊息
while True:
    # 產生亂數資料
    temperature = round(random.uniform(20.0, 35.0), 1)  # 溫度 20~35°C
    humidity = round(random.uniform(40.0, 80.0), 1)     # 濕度 40~80%
    light_status = random.choice(["on", "off"])         # 燈光狀態 (英文避免編碼問題)
    
    # 建立 JSON 資料
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "light_status": light_status
    }
    message = json.dumps(data)
    
    print("-" * 30)
    
    # 嘗試發布，如果失敗則重新連線
    try:
        client.publish(TOPIC, message)
        print("已發布訊息:")
        print(f"  temperature: {temperature}")
        print(f"  humidity: {humidity}")
        print(f"  light_status: {light_status}")
        print(f"Topic: {TOPIC}")
    except OSError as e:
        print(f"發布失敗: {e}")
        print("嘗試重新連線...")
        mqtt_connect()
        # 重新連線後再發布一次
        client.publish(TOPIC, message)
        print("重新連線後發布成功!")
    
    print("等待 10 秒後再次發布...")
    time.sleep(10)