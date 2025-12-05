"""
範例 1: 開關燈功能 (LED 控制與回報)
功能:
1. 連線 WiFi
2. 控制 Pico 內建 LED 閃爍 (模擬開關燈)
3. 將燈的狀態 ("開"/"關") 發送到 MQTT Broker
"""

import time
import machine
import json
import wifi_connect
from secrets import MQTT_BROKER, MQTT_PORT

# 嘗試匯入 MQTT 套件，如果沒有則自動安裝
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
CLIENT_ID = "pico_led_control"
LED_PIN = "LED"  # Pico W 使用 "LED"

# 初始化 LED
led = machine.Pin(LED_PIN, machine.Pin.OUT)

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
        print("請檢查 secrets.py 中的 IP 設定是否正確")
        return

    print("🚀 開始執行 LED 閃爍與回報...")

    # 3. 主迴圈
    count = 0
    try:
        while True:
            # 切換 LED 狀態
            led.toggle()

            # 取得目前狀態
            is_on = led.value() == 1
            status_text = "開" if is_on else "關"

            # 準備傳送的資料
            payload = {
                "light_status": status_text,
                "device": "Pico W (App 1)",
                "msg_id": count
            }

            # 發送 MQTT 訊息
            print(f"發送: LED {status_text}")
            client.publish(TOPIC, json.dumps(payload))

            count += 1
            time.sleep(2)  # 每 2 秒切換一次

    except KeyboardInterrupt:
        print("\n程式停止")
        client.disconnect()
        led.off()

if __name__ == "__main__":
    main()
