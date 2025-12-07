# wifi_connect.py
# 作者：ChatGPT for 徐國堂老師
# 適用：Raspberry Pi Pico W（MicroPython）

import network
import time
import socket

# -------------------------------
# 你可以設定你的 WiFi 資訊
# -------------------------------
WIFI_SSID = "你的WiFi名稱"
WIFI_PASSWORD = "你的WiFi密碼"

# -------------------------------
# WiFi 連線函式
# -------------------------------
def connect(ssid=WIFI_SSID, password=WIFI_PASSWORD, retry=20):
    """
    連線到 WiFi。
    retry = 嘗試次數（每次間隔 1 秒）
    回傳：連線後的 WLAN 物件
    """
    wlan = network.WLAN(network.STA_IF)

    if wlan.isconnected():
        print("已經連線過 WiFi：", wlan.ifconfig())
        return wlan

    print("啟動 WLAN...")
    wlan.active(True)
    time.sleep(1)

    print(f"準備連線 SSID：{ssid}")
    wlan.connect(ssid, password)

    for i in range(retry):
        if wlan.isconnected():
            print("WiFi 連線成功！")
            print("IP 資訊：", wlan.ifconfig())
            return wlan

        print(f"連線中... ({i+1}/{retry})")
        time.sleep(1)

    raise RuntimeError("❌ WiFi 連線失敗，請檢查 SSID/密碼或距離")

# -------------------------------
# 斷線函式
# -------------------------------
def disconnect():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        wlan.disconnect()
        wlan.active(False)
        print("已斷線")
    else:
        print("目前沒有 WiFi 連線")

# -------------------------------
# 是否連線成功？
# -------------------------------
def is_connected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()

# -------------------------------
# 取得 IP 位址
# -------------------------------
def get_ip():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return wlan.ifconfig()[0]
    return None

# -------------------------------
# 測試連線到外部網站（例如 Google）
# -------------------------------
def test_internet(host="8.8.8.8", port=53, timeout=3):
    """
    使用 UDP 測試外部網路是否可連線
    """
    try:
        addr = socket.getaddrinfo(host, port)[0][-1]
        s = socket.socket()
        s.settimeout(timeout)
        s.connect(addr)
        s.close()
        return True
    except:
        return False