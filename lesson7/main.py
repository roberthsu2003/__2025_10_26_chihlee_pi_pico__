import wifi_connect

# 嘗試連線 WiFi
wifi_connect.connect()

# 顯示 IP
print("IP:", wifi_connect.get_ip())

# 測試外部網路
if wifi_connect.test_internet():
    print("外部網路 OK")
else:
    print("外部網路無法連線")