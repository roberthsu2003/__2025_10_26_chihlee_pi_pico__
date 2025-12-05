"""
範例 3: 整合功能 (LED 控制 + 溫溼度回報)
功能:
1. 同時執行 LED 閃爍與溫度讀取
2. 將所有狀態整合在一個 MQTT 訊息中發送
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
CLIENT_ID = "pico_integrated"
LED_PIN = "LED"

# 硬體初始化
led = machine.Pin(LED_PIN, machine.Pin.OUT)
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)

def read_temperature():
    """讀取內建溫度"""
    reading = sensor_temp.read_u16() * conversion_factor
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

    print("🚀 開始執行整合應用程式...")

    # 3. 主迴圈
    # 為了同時處理 LED 閃爍(快)和溫度上傳(慢)，我們使用非同步的概念或簡單的計時器
    last_publish_time = 0
    publish_interval = 5  # 每 5 秒上傳一次數據

    led_interval = 2      # 每 2 秒切換一次 LED
    last_led_time = 0

    start_time = time.time()

    try:
        while True:
            current_time = time.time()

            # 處理 LED (模擬工作狀態指示燈)
            if current_time - last_led_time >= led_interval:
                led.toggle()
                last_led_time = current_time
                print(f"[{current_time}] LED 切換")

            # 處理數據上傳
            if current_time - last_publish_time >= publish_interval:
                # 收集所有數據
                temp = read_temperature()
                humi = round(random.uniform(50, 70), 1)
                is_on = led.value() == 1

                payload = {
                    "temperature": temp,
                    "humidity": humi,
                    "light_status": "開" if is_on else "關",
                    "device": "Pico W (App 3)",
                    "uptime": current_time - start_time
                }

                print(f"[{current_time}] 發送整合數據: {payload}")
                client.publish(TOPIC, json.dumps(payload))

                last_publish_time = current_time

            # 短暫暫停避免 CPU 滿載，但不能太長以免錯過時間點
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n程式停止")
        client.disconnect()
        led.off()

if __name__ == "__main__":
    main()
