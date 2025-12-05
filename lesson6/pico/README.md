# Raspberry Pi Pico W 教學範例

本目錄包含 Raspberry Pi Pico W 的 MicroPython 範例程式碼，用於與 MQTT 伺服器 (Raspberry Pi) 進行通訊。

## 目錄結構

- `secrets.py`: 存放 WiFi 帳號密碼與 MQTT 伺服器 IP 的設定檔。
- `wifi_connect.py`: 負責 WiFi 連線的工具程式。
- [1_led.py](./1_led.py): **範例 1** - 控制 LED 閃爍並回報狀態。
- [2_temp.py](./2_temp.py): **範例 2** - 讀取內建溫度並回報。
- [3_integrated.py](./3_integrated.py): **範例 3** - 整合 LED 控制與溫度監控。

## 使用前準備

### 1. 硬體準備
- Raspberry Pi Pico W
- Micro USB 傳輸線

### 2. 軟體環境
- 請下載並安裝 [Thonny IDE](https://thonny.org/)。
- 確保 Pico W 已安裝最新的 MicroPython 韌體。

### 3. 修改設定檔
在執行任何程式前，請先開啟 `secrets.py` 並修改以下內容：

```python
# secrets.py
SSID = "您的_WiFi_名稱"
PASSWORD = "您的_WiFi_密碼"
MQTT_BROKER = "192.168.X.X"  # Raspberry Pi 的 IP 位址
```

> **如何查詢 Raspberry Pi 的 IP？**
> 在 Raspberry Pi 的終端機輸入：
> ```bash
> hostname -I
> ```

## 如何在 Pico 內安裝外部套件

在使用外部功能（如 MQTT）時，我們需要安裝對應的套件。在 Pico W 上，主要有兩種安裝方式：

### 方法一：使用 `mip` 自動安裝 (推薦)
這是 MicroPython 內建的套件管理工具 (類似 Python 的 pip)，可以直接從網路下載套件。
**注意：Pico W 必須先連上 WiFi 才能使用此功能。**

我們的範例程式碼 (如 [1_led.py](./1_led.py)) 已經內建了這段邏輯，第一次執行時會自動檢查並安裝：
```python
import wifi_connect
import mip

# 1. 確保連上 WiFi
# 2. 執行安裝
mip.install("umqtt.simple")
```

### 方法二：使用 Thonny IDE 介面安裝
適合初學者，透過圖形介面管理套件。

1. 將 Pico W 連接到電腦，並開啟 Thonny。
2. 點選上方選單的 **工具 (Tools)** > **管理套件 (Manage packages)**。
3. 在搜尋框輸入套件名稱 (例如 `umqtt.simple`)。
4. 點選 **搜尋 (Search)**。
5. 在搜尋結果中選擇對應的套件，點選 **安裝 (Install)**。
6. 安裝完成後，套件會被儲存在 Pico 的 `/lib` 資料夾中。

## 範例說明

### 範例 1: 開關燈功能 (1_led.py)
[點此查看程式碼](./1_led.py)

此程式會讓 Pico W 的內建 LED 每 2 秒閃爍一次，並將狀態 ("開" 或 "關") 發送到 MQTT Broker。
- **目的**: 學習如何控制 GPIO 以及基本的 MQTT 發布。
- **觀察**: 您可以在網頁介面上看到燈號狀態跟隨 Pico 的 LED 變化。

### 範例 2: 內建溫溼度功能 (2_temp.py)
[點此查看程式碼](./2_temp.py)

此程式讀取 Pico 內建的溫度感測器，並模擬濕度數據 (因為 Pico 只有溫度感測器)，每 5 秒上傳一次。
- **目的**: 學習讀取類比訊號 (ADC) 與轉換公式。
- **公式**: `27 - (voltage - 0.706) / 0.001721`

### 範例 3: 整合功能 (3_integrated.py)
[點此查看程式碼](./3_integrated.py)

結合了上述兩個功能。程式會同時處理 LED 閃爍 (每 2 秒) 與溫度上傳 (每 5 秒)。
- **目的**: 學習如何在一個迴圈中處理多個不同時間間隔的任務 (非阻塞式程式設計概念)。

## 常見問題

### 如何測試 WiFi 是否連線？
您可以在 Thonny 的互動視窗 (Shell) 輸入以下指令測試：

```python
import wifi_connect
wlan = wifi_connect.connect_wifi()
print(wlan.ifconfig())
```
如果成功，會顯示 IP 位址。

### 執行時出現 "ImportError: no module named 'umqtt'"？
這是因為您的 Pico 尚未安裝 MQTT 函式庫。
請參考上方的「如何在 Pico 內安裝外部套件」章節，使用 `mip` 或 Thonny 進行安裝。

### 為什麼網頁上沒有數據？
1. 檢查 `secrets.py` 中的 IP 是否正確。
2. 檢查 Raspberry Pi 上的 MQTT 服務是否已啟動。
3. 檢查 WiFi 是否連線成功 (看 Thonny 的輸出訊息)。
