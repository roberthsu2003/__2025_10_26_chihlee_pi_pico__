"""
Secrets 設定檔
請填入您的 WiFi 與 MQTT Broker 資訊
"""

# WiFi 設定
SSID = "Your_WiFi_Name"
PASSWORD = "Your_WiFi_Password"

# MQTT Broker 設定
# 請使用 'hostname -I' 在 Raspberry Pi 上查詢 IP
# 例如: "192.168.1.100"
MQTT_BROKER = "192.168.1.XXX"
MQTT_PORT = 1883
MQTT_USER = None
MQTT_PASS = None
