# MQTT 感測器監控應用程式

根據 [PRD.md](PRD.md) 規格實作的感測器數據即時監控儀表板。

## 📋 專案說明

本專案實作一個基於 Web 的 MQTT 監控系統，用於即時顯示和記錄感測器數據。

### ⚠️ 技術變更說明

由於 Streamlit 及其依賴套件（pandas, pyarrow）與 Raspberry Pi ARM64 架構存在相容性問題（SIGILL 錯誤），專案改用 **Flask + Socket.IO** 實作，提供更好的效能和穩定性。

## ✨ 主要功能

- 💡 **即時電燈狀態顯示** - 大型圓形視覺化指示器
- 🌡️ **客廳溫度監控** - 即時數值顯示和歷史趨勢
- 💧 **客廳濕度監控** - 即時數值顯示和歷史趨勢
- 📈 **雙 Y 軸歷史圖表** - 互動式數據視覺化
- 💾 **自動數據儲存** - CSV 和 Excel 格式
- 🔄 **WebSocket 即時推送** - 無需手動重新整理
- 📱 **響應式設計** - 支援手機和桌面瀏覽器

## 🚀 快速開始

### 方式 1：使用啟動腳本（推薦）

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico/lesson6
bash start.sh
```

### 方式 2：手動啟動

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico/lesson6
uv run python app_flask.py
```

### 開啟網頁

在瀏覽器中訪問：
- 本地：http://localhost:8080
- 區域網路：http://172.20.10.3:8080

## 📊 測試數據

專案已包含 50 筆測試數據，啟動後即可看到完整的數據和圖表。

### 重新生成測試數據

```bash
uv run python generate_test_data.py
```

### 發送即時 MQTT 測試數據

在另一個終端機中執行：

```bash
uv run python test_mqtt_publish.py
```

## 📁 檔案結構

### ✅ 主要檔案（可用）

| 檔案 | 說明 |
|------|------|
| `app_flask.py` | **Flask 主應用程式**（推薦使用） |
| `templates/index.html` | 網頁前端介面 |
| `sensor_data.csv` | CSV 格式數據檔案 |
| `sensor_data.xlsx` | Excel 格式數據檔案 |
| `test_mqtt_publish.py` | MQTT 測試發布工具 |
| `generate_test_data.py` | 測試數據生成工具 |
| `start.sh` | 應用程式啟動腳本 |
| `PRD.md` | 產品需求文件 |
| `啟動應用程式.md` | 詳細使用說明 |
| `使用說明.md` | 技術細節和故障排除 |

### ⚠️ 已棄用檔案（相容性問題）

| 檔案 | 狀態 |
|------|------|
| `app.py` | ❌ Streamlit 版本（ARM 不相容） |
| `config.py`, `data_manager.py`, `mqtt_client.py` | ⚠️ 僅供 Streamlit 版本使用 |

## 🔧 MQTT 設定

### 確認 MQTT Broker 運行中

```bash
# 檢查 mosquitto 狀態
sudo systemctl status mosquitto

# 啟動 mosquitto
sudo systemctl start mosquitto

# 設定開機自動啟動
sudo systemctl enable mosquitto
```

### MQTT 訊息格式

發送到主題 `客廳/感測器` 的訊息應為 JSON 格式：

```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "light_status": "開"
}
```

支援的欄位名稱：
- 溫度：`temperature` 或 `temp`
- 濕度：`humidity` 或 `humi`
- 電燈：`light_status` 或 `light`

## 🔌 使用 Raspberry Pi Pico W 發送數據

### MicroPython 範例代碼

如果您使用 **Raspberry Pi Pico W**（帶 WiFi），可以使用以下代碼發送感測器數據：

#### 完整範例（含 DHT22 溫濕度感測器）

```python
# Raspberry Pi Pico W - MQTT 感測器發送範例
import network
import time
from umqtt.simple import MQTTClient
import ujson
import dht
from machine import Pin

# ===== 設定區 =====
WIFI_SSID = "你的WiFi名稱"
WIFI_PASSWORD = "你的WiFi密碼"
MQTT_BROKER = "172.20.10.3"  # 你的 Raspberry Pi IP
MQTT_TOPIC = "客廳/感測器"

# 硬體設定
dht_sensor = dht.DHT22(Pin(15))  # DHT22 接 GP15
led = Pin(16, Pin.OUT)           # LED 接 GP16

# WiFi 連線
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    print("連接 WiFi...")
    while not wlan.isconnected():
        time.sleep(1)
    print(f"✅ WiFi 已連線: {wlan.ifconfig()[0]}")

# 主程式
def main():
    connect_wifi()
    
    # 連接 MQTT
    client = MQTTClient("pico_sensor", MQTT_BROKER, 1883)
    client.connect()
    print("✅ MQTT 已連線")
    
    try:
        while True:
            # 讀取感測器
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            humi = dht_sensor.humidity()
            light = "開" if led.value() == 1 else "關"
            
            # 建立 JSON 數據
            data = {
                "temperature": temp,
                "humidity": humi,
                "light_status": light
            }
            
            # 發送 MQTT
            client.publish(MQTT_TOPIC, ujson.dumps(data))
            print(f"✅ 已發送: 溫度={temp}°C, 濕度={humi}%, 燈={light}")
            
            time.sleep(5)  # 每 5 秒發送一次
            
    except KeyboardInterrupt:
        print("已停止")
    finally:
        client.disconnect()

main()
```

#### 簡化測試版（無需感測器）

```python
# Pico W - MQTT 測試版本
import network
import time
from umqtt.simple import MQTTClient
import ujson
import random

WIFI_SSID = "你的WiFi名稱"
WIFI_PASSWORD = "你的WiFi密碼"
MQTT_BROKER = "172.20.10.3"  # Raspberry Pi IP

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print(f"✅ WiFi: {wlan.ifconfig()[0]}")

connect_wifi()
client = MQTTClient("pico_test", MQTT_BROKER, 1883)
client.connect()

count = 0
while True:
    data = {
        "temperature": round(20 + random.uniform(0, 10), 2),
        "humidity": round(50 + random.uniform(0, 20), 2),
        "light_status": "開" if count % 2 == 0 else "關"
    }
    client.publish("客廳/感測器", ujson.dumps(data))
    print(f"✅ 已發送: {data}")
    count += 1
    time.sleep(5)
```

### 硬體連接

如果使用 DHT22 溫濕度感測器：

```
DHT22 溫濕度感測器：
├─ VCC  → Pico 3V3 (Pin 36)
├─ DATA → Pico GP15 (Pin 20)
└─ GND  → Pico GND (Pin 38)

LED（電燈模擬）：
├─ 正極 → Pico GP16 (Pin 21)
└─ 負極 → GND + 220Ω 電阻
```

### 需要的函式庫

在 Pico 上需要安裝 MQTT 函式庫：

```bash
# 使用 mpremote 安裝
mpremote mip install umqtt.simple
```

或在 Thonny IDE 中：
1. 工具 → 管理套件
2. 搜尋 `umqtt.simple`
3. 安裝

### 使用步驟

1. **修改代碼設定**：
   - WiFi SSID 和密碼
   - MQTT_BROKER 改為你的 Raspberry Pi IP 地址

2. **上傳到 Pico W**：
   - 使用 Thonny IDE 或其他工具

3. **執行程式**：
   - Pico 會每 5 秒自動發送一次數據
   - Flask 應用程式網頁會即時更新顯示

4. **查看結果**：
   - 打開 http://localhost:8080 或 http://你的Pi的IP:8080
   - 即可看到 Pico 發送的數據

## 📈 效能比較

| 項目 | Streamlit 版本 | Flask 版本 |
|------|---------------|-----------|
| ARM 相容性 | ❌ 不相容（SIGILL） | ✅ 完全相容 |
| 記憶體佔用 | ~300MB | ~50MB |
| 啟動速度 | 5-10 秒 | < 1 秒 |
| 即時更新 | 需重新整理 | WebSocket 自動推送 |
| CPU 佔用 | 高 | 低 |

## 🐛 常見問題

### Q1: 應用程式無法啟動

確認已安裝必要套件：
```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico
uv sync
```

### Q2: 網頁無法開啟

檢查防火牆設定：
```bash
sudo ufw allow 8080
```

### Q3: 無法連線 MQTT

```bash
# 確認 mosquitto 正在運行
sudo systemctl status mosquitto

# 測試 MQTT 連線
mosquitto_sub -h localhost -t "客廳/感測器" -v
```

### Q4: 沒有顯示數據

1. 檢查測試數據檔案是否存在：`ls -lh sensor_data.csv`
2. 重新生成測試數據：`uv run python generate_test_data.py`
3. 查看應用程式日誌，確認是否成功載入數據

## 🛠️ 技術棧

- **後端框架**：Flask 3.1.2
- **即時通訊**：Flask-SocketIO 5.5.1
- **MQTT 客戶端**：paho-mqtt 2.1.0+
- **數據儲存**：CSV（標準庫）+ Excel（openpyxl）
- **前端技術**：HTML5 + JavaScript + Chart.js
- **WebSocket**：Socket.IO 4.5.4

## 📖 進階使用

詳細的使用說明和技術細節請參閱：
- [啟動應用程式.md](啟動應用程式.md) - 快速啟動指南
- [使用說明.md](使用說明.md) - 完整技術文檔和故障排除
- [PRD.md](PRD.md) - 產品需求規格

## 📝 數據儲存

數據自動儲存到以下檔案：
- `sensor_data.csv` - CSV 格式（應用程式使用）
- `sensor_data.xlsx` - Excel 格式（人工查看）

包含欄位：
- 時間戳記
- 電燈狀態
- 溫度（°C）
- 濕度（%）

## 🎯 背景運行

如需背景運行應用程式：

```bash
# 啟動
nohup uv run python app_flask.py > app.log 2>&1 &

# 查看日誌
tail -f app.log

# 停止
pkill -f "python app_flask.py"
```

## 📜 授權

本專案遵循 [LICENSE](../LICENSE) 中的授權條款。

## 🙏 致謝

感謝使用本專案！如有問題或建議，歡迎提出 Issue。

