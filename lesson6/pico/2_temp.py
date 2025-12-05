"""
範例 2: 內建溫溼度功能 (讀取與回報)
功能:
1. 連線 WiFi
2. 讀取 Pico 內建溫度感測器
3. 將溫度數據發送到 MQTT Broker
注意: Pico 內建只有溫度感測器，沒有濕度感測器。此範例將模擬濕度數據。
"""

import time
import machine
import json
import random
import wifi_connect
from secrets import MQTT_BROKER, MQTT_PORT

# 嘗試匯入 MQTT 套件
try:
    from umqtt.simple import MQTTClient
except ImportError:
    print("⚠️ 找不到 umqtt.simple，正在嘗試透過網路安裝...")
    if wifi_connect.connect_wifi():
        import mip
        mip.install("umqtt.simple")
        from umqtt.simple import MQTTClient
    else:
        raise Exception("無網路連線，無法安裝必要套件")

# 設定
TOPIC = "客廳/感測器"
CLIENT_ID = "pico_temp_sensor"

# 初始化內建溫度感測器 (ADC 4)
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

def read_temperature():
    """讀取內建溫度"""
    reading = sensor_temp.read_u16() * conversion_factor
    # 溫度計算公式: 27 - (voltage - 0.706)/0.001721
    temperature = 27 - (reading - 0.706) / 0.001721
    return round(temperature, 1)

def main():
    # 1. 連線 WiFi
    wlan = wifi_connect.connect_wifi()
    if not wlan:
        return

    # 2. 連線 MQTT
    print(f"📡 正在連線到 MQTT Broker: {MQTT_BROKER}...")
    try:
        client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print("✅ MQTT 連線成功")
    except Exception as e:
        print(f"❌ MQTT 連線失敗: {e}")
        return

    print("🚀 開始讀取溫度並回報...")

    # 3. 主迴圈
    count = 0
    try:
        while True:
            # 讀取溫度
            temp = read_temperature()

            # 模擬濕度 (因為 Pico 只有溫度感測器)
            # 產生 50% ~ 70% 之間的隨機值
            humi = round(random.uniform(50, 70), 1)

            # 準備傳送的資料
            payload = {
                "temperature": temp,
                "humidity": humi,
                "device": "Pico W (App 2)",
                "msg_id": count
            }

            # 發送 MQTT 訊息
            json_str = json.dumps(payload)
            print(f"發送: 溫度={temp}°C, 濕度={humi}%")
            client.publish(TOPIC, json_str)

            count += 1
            time.sleep(5)  # 每 5 秒更新一次

    except KeyboardInterrupt:
        print("\n程式停止")
        client.disconnect()

if __name__ == "__main__":
    main()
