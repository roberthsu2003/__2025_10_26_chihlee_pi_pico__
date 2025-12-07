# Lesson 7 - Raspberry Pi Pico W WiFi 連線模組

本課程提供一個簡潔易用的 WiFi 連線模組，適用於 **Raspberry Pi Pico W** 搭配 **MicroPython** 環境。

---

## 📁 檔案結構

```
lesson7/
├── wifi_connect.py   # WiFi 連線功能模組
├── main.py           # 主程式（測試範例）
└── README.md         # 說明文件
```

---

## 📝 程式邏輯說明

### 1. `wifi_connect.py` - WiFi 連線模組

這個模組封裝了所有 WiFi 相關的操作，提供以下功能：

#### 全域變數

```python
WIFI_SSID = "xxxx"        # WiFi 名稱
WIFI_PASSWORD = "xxx"     # WiFi 密碼
```

這是預設的 WiFi 連線資訊，使用者需要手動修改成自己的 WiFi 設定。

---

#### 函式說明

| 函式名稱 | 功能說明 | 回傳值 |
|----------|----------|--------|
| `connect()` | 連線到 WiFi | WLAN 物件 |
| `disconnect()` | 斷開 WiFi 連線 | 無 |
| `is_connected()` | 檢查是否已連線 | `True` / `False` |
| `get_ip()` | 取得目前的 IP 位址 | IP 字串或 `None` |
| `test_internet()` | 測試外部網路是否可用 | `True` / `False` |

---

#### `connect(ssid, password, retry)` 連線函式

**程式邏輯流程：**

```
開始
  │
  ▼
檢查是否已經連線？ ──是──► 直接回傳 WLAN 物件
  │
  否
  ▼
啟動 WLAN 介面（wlan.active(True)）
  │
  ▼
呼叫 wlan.connect(ssid, password)
  │
  ▼
迴圈等待連線（最多 retry 次，預設 20 次）
  │
  ├── 連線成功 ──► 印出 IP 資訊，回傳 WLAN 物件
  │
  └── 等待 1 秒後再次檢查
  │
  ▼
超過重試次數 ──► 拋出 RuntimeError 例外
```

**參數說明：**
- `ssid`：WiFi 名稱（預設使用全域變數 `WIFI_SSID`）
- `password`：WiFi 密碼（預設使用全域變數 `WIFI_PASSWORD`）
- `retry`：重試次數（預設 20 次，每次間隔 1 秒）

---

#### `disconnect()` 斷線函式

**程式邏輯：**
1. 取得 WLAN 物件
2. 如果目前已連線，則呼叫 `wlan.disconnect()` 並關閉 WLAN 介面
3. 如果未連線，則印出提示訊息

---

#### `is_connected()` 檢查連線狀態

**程式邏輯：**
- 直接回傳 `wlan.isconnected()` 的結果（`True` 或 `False`）

---

#### `get_ip()` 取得 IP 位址

**程式邏輯：**
1. 檢查是否已連線
2. 如果已連線，回傳 IP 位址（`wlan.ifconfig()[0]`）
3. 如果未連線，回傳 `None`

---

#### `test_internet(host, port, timeout)` 測試外部網路

**程式邏輯：**
1. 使用 `socket.getaddrinfo()` 解析目標主機
2. 建立 socket 連線並設定超時時間
3. 嘗試連線到目標（預設為 Google DNS 8.8.8.8:53）
4. 連線成功回傳 `True`，失敗回傳 `False`

**參數說明：**
- `host`：測試的主機位址（預設 `8.8.8.8`）
- `port`：測試的連接埠（預設 `53`）
- `timeout`：超時秒數（預設 `3` 秒）

---

### 2. `main.py` - 主程式

這是一個簡單的測試程式，示範如何使用 `wifi_connect` 模組：

```python
import wifi_connect

# 步驟 1：嘗試連線 WiFi
wifi_connect.connect()

# 步驟 2：顯示 IP 位址
print("IP:", wifi_connect.get_ip())

# 步驟 3：測試外部網路
if wifi_connect.test_internet():
    print("外部網路 OK")
else:
    print("外部網路無法連線")
```

**執行流程：**

```
1. 匯入 wifi_connect 模組
       │
       ▼
2. 呼叫 connect() 連線 WiFi
       │
       ▼
3. 取得並顯示 IP 位址
       │
       ▼
4. 測試外部網路連線
       │
       ├── 成功 ──► 印出 "外部網路 OK"
       │
       └── 失敗 ──► 印出 "外部網路無法連線"
```

---

## ⚙️ 如何修改 WiFi 設定

### 方法一：直接修改全域變數（推薦）

開啟 `wifi_connect.py`，找到第 12-13 行：

```python
# 修改前
WIFI_SSID = "xxxx"
WIFI_PASSWORD = "xxx"

# 修改後（範例）
WIFI_SSID = "MyHomeWiFi"
WIFI_PASSWORD = "my_secret_password_123"
```

> ⚠️ **注意事項：**
> - SSID 和密碼都要用**雙引號**包起來
> - 密碼請區分**大小寫**
> - 不要有多餘的空格

---

### 方法二：在 main.py 中指定參數

如果不想修改 `wifi_connect.py`，可以在呼叫 `connect()` 時直接傳入參數：

```python
import wifi_connect

# 直接傳入 SSID 和密碼
wifi_connect.connect(ssid="MyHomeWiFi", password="my_secret_password_123")

print("IP:", wifi_connect.get_ip())
```

這種方式的好處是不需要修改原始模組檔案。

---

### 方法三：建立獨立的設定檔（進階）

建立一個 `secrets.py` 檔案來存放敏感資訊：

```python
# secrets.py
WIFI_SSID = "MyHomeWiFi"
WIFI_PASSWORD = "my_secret_password_123"
```

然後在 `main.py` 中使用：

```python
import wifi_connect
import secrets

wifi_connect.connect(ssid=secrets.WIFI_SSID, password=secrets.WIFI_PASSWORD)
```

> 💡 **提示：** 使用獨立設定檔的好處是可以將 `secrets.py` 加入 `.gitignore`，避免將密碼上傳到版本控制系統。

---

## 🚀 快速開始

1. **修改 WiFi 設定**（參考上方說明）

2. **上傳檔案到 Pico W**
   - `wifi_connect.py`
   - `main.py`

3. **執行程式**
   - 在 Thonny 或其他 MicroPython IDE 中執行 `main.py`

4. **觀察輸出**
   ```
   啟動 WLAN...
   準備連線 SSID：MyHomeWiFi
   連線中... (1/20)
   連線中... (2/20)
   WiFi 連線成功！
   IP 資訊： ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')
   IP: 192.168.1.100
   外部網路 OK
   ```

---

## ❓ 常見問題

### Q1：連線失敗怎麼辦？

- 確認 SSID 和密碼是否正確
- 確認 Pico W 是否在 WiFi 訊號範圍內
- 嘗試增加 `retry` 參數：`wifi_connect.connect(retry=30)`

### Q2：如何連線到 5GHz WiFi？

Raspberry Pi Pico W **只支援 2.4GHz WiFi**，不支援 5GHz 頻段。

### Q3：外部網路測試失敗但 WiFi 已連線？

可能是路由器的網路設定問題，請確認路由器可以正常連接網際網路。

---

## 📚 參考資源

- [MicroPython network 模組文件](https://docs.micropython.org/en/latest/library/network.html)
- [Raspberry Pi Pico W 官方文件](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)

