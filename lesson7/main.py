import wifi_connect as wifi
import time

# 嘗試連線 WiFi
wifi.connect()

# 顯示 IP
print("IP:", wifi.get_ip())

# 每隔 10 秒測試一次外部網路
while True:
    print("-" * 30)
    if wifi.test_internet():
        print("外部網路 OK")
    else:
        print("外部網路無法連線")
    
    print("等待 10 秒後再次測試...")
    time.sleep(10)