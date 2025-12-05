"""
WiFi 連線工具
負責處理 WiFi 連線與狀態檢查
"""
import network
import time
from secrets import SSID, PASSWORD

def connect_wifi():
    """
    連線到 WiFi

    Returns:
        wlan: network.WLAN 物件
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # 檢查是否已連線
    if wlan.isconnected():
        print(f"✅ WiFi 已連線: {SSID}")
        print(f"   IP 位址: {wlan.ifconfig()[0]}")
        return wlan

    print(f"📡 正在連線到 WiFi: {SSID} ...")
    wlan.connect(SSID, PASSWORD)

    # 等待連線 (最多 10 秒)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("   等待連線...")
        time.sleep(1)

    # 檢查最終狀態
    if wlan.status() != 3:
        print(f"❌ WiFi 連線失敗")
        return None
    else:
        print(f"✅ WiFi 連線成功")
        print(f"   IP 位址: {wlan.ifconfig()[0]}")
        return wlan

def test_connection():
    """測試 WiFi 連線狀態"""
    wlan = connect_wifi()
    if wlan and wlan.isconnected():
        print("網路測試: 正常")
        return True
    else:
        print("網路測試: 失敗")
        return False
