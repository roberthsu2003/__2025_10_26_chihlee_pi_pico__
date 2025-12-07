import wifi_connect as wifi

# 嘗試連線 WiFi
wifi.connect()

# 顯示 IP
print("IP:", wifi.get_ip())

# 測試外部網路
if wifi.test_internet():
    print("外部網路 OK")
else:
    print("外部網路無法連線")