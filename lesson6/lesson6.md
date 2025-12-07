# Lesson 6 專案分析文檔

> **專案名稱**: MQTT 感測器監控應用程式  
> **技術框架**: Flask + Socket.IO + MQTT  
> **部署環境**: Raspberry Pi (ARM64)  
> **文檔版本**: 1.0  
> **最後更新**: 2025-12-07

---

## 📋 目錄

1. [專案概述](#專案概述)
2. [系統架構](#系統架構)
3. [程式邏輯分析](#程式邏輯分析)
4. [可手動修改的部分](#可手動修改的部分)
5. [數據流程](#數據流程)
6. [實用修改範例](#實用修改範例)
7. [常見操作](#常見操作)

---

## 專案概述

### 🎯 專案目標

建立一個基於 Web 的 MQTT 即時監控系統，用於接收、顯示和儲存來自感測器的數據。

### ✨ 核心功能

- **即時監控**: 顯示電燈狀態、溫度、濕度
- **歷史圖表**: 雙 Y 軸折線圖顯示溫濕度趨勢
- **數據持久化**: 自動儲存為 CSV 和 Excel 格式
- **即時推送**: 使用 WebSocket 技術，無需重新整理頁面
- **MQTT 訂閱**: 訂閱感測器主題，接收即時數據

### 📁 專案結構

```
lesson6/
├── app_flask.py              # [核心] Flask 主應用程式
├── templates/
│   └── index.html            # [核心] 網頁前端介面
├── generate_test_data.py     # [工具] 測試數據生成器
├── test_mqtt_publish.py      # [工具] MQTT 測試發布工具
├── start.sh                  # [工具] 啟動腳本
├── sensor_data.csv           # [數據] CSV 格式數據儲存
├── sensor_data.xlsx          # [數據] Excel 格式數據儲存
├── pico/                     # [Pico] Raspberry Pi Pico W 程式
│   ├── main.py               # 基礎 LED 範例
│   ├── 3_integrated.py       # MQTT 感測器發布程式
│   └── wifi_connect.py       # WiFi 連線模組
├── README.md                 # [文檔] 主要說明文檔
├── PRD.md                    # [文檔] 產品需求文檔
└── 使用說明.md               # [文檔] 使用說明

標記說明:
[核心] - 系統核心檔案
[工具] - 輔助工具
[數據] - 數據檔案
[Pico] - Pico W 相關程式
[文檔] - 說明文檔
```

---

## 系統架構

### 整體架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                     Lesson 6 系統架構                        │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐        MQTT         ┌──────────────────┐
│              │  ─────────────────> │                  │
│  Pico W      │      主題:          │  MQTT Broker     │
│  感測器發布者 │    客廳/感測器       │  (Mosquitto)     │
│              │  ◄───────────────── │                  │
└──────────────┘    訂閱確認         └──────────────────┘
                                              │
                                              │ 訂閱主題
                                              ▼
                                     ┌──────────────────┐
                                     │  Flask 後端       │
                                     │  app_flask.py    │
                                     │                  │
                                     │  - MQTT 客戶端   │
                                     │  - 數據處理      │
                                     │  - CSV 儲存      │
                                     │  - WebSocket    │
                                     └──────────────────┘
                                              │
                                              │ WebSocket
                                              │ HTTP API
                                              ▼
                                     ┌──────────────────┐
                                     │  Web 前端        │
                                     │  index.html      │
                                     │                  │
                                     │  - Socket.IO     │
                                     │  - Chart.js      │
                                     │  - 即時更新      │
                                     └──────────────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │  使用者瀏覽器     │
                                     │  http://IP:8080  │
                                     └──────────────────┘
```

### 技術棧

| 層級 | 技術 | 用途 |
|------|------|------|
| **前端** | HTML5 + CSS3 + JavaScript | 網頁介面 |
| **圖表** | Chart.js 4.5+ | 雙 Y 軸歷史圖表 |
| **即時通訊** | Socket.IO Client 4.5+ | WebSocket 連線 |
| **後端框架** | Flask 3.1+ | Web 伺服器 |
| **WebSocket** | Flask-SocketIO 5.5+ | 即時數據推送 |
| **MQTT** | paho-mqtt 2.1+ | MQTT 客戶端 |
| **數據儲存** | CSV (內建), openpyxl | 數據持久化 |
| **通訊協定** | MQTT 3.1.1 | 訊息傳輸 |

---

## 程式邏輯分析

### 1️⃣ app_flask.py - Flask 主應用程式

#### 📌 程式結構

```python
# 主要組成部分:
1. 導入套件 (第 6-13 行)
2. 全域變數設定 (第 15-34 行)
3. CSV 檔案操作函數 (第 36-77 行)
4. MQTT 回調函數 (第 78-136 行)
5. Flask 路由 (第 158-176 行)
6. 主程式啟動 (第 177-188 行)
```

#### 🔍 詳細邏輯分析

##### **A. 全域變數 (第 18-31 行)**

```python
MQTT_BROKER = "localhost"     # MQTT Broker 位址
MQTT_PORT = 1883              # MQTT 埠號
MQTT_TOPIC = "客廳/感測器"     # 訂閱主題

sensor_data = []              # 儲存歷史數據 (最多 100 筆)
latest_data = {...}           # 最新一筆數據
mqtt_connected = False        # MQTT 連線狀態
```

**作用說明**:
- `sensor_data`: 記憶體中的數據緩存，限制 100 筆避免記憶體溢出
- `latest_data`: 提供給前端顯示的即時數據
- `mqtt_connected`: 前端顯示連線狀態

##### **B. CSV 載入函數 - load_from_csv() (第 36-63 行)**

**執行時機**: 應用程式啟動時 (第 152 行)

**邏輯流程**:
```
1. 檢查 sensor_data.csv 是否存在
   ├─ 是 → 繼續
   └─ 否 → 結束函數

2. 開啟 CSV 檔案讀取
   
3. 逐行讀取並轉換為字典格式
   {
     'timestamp': '2025-12-07 10:30:00',
     'light_status': '開',
     'temperature': 25.5,
     'humidity': 60.0
   }

4. 只保留最近 100 筆數據
   sensor_data = loaded_data[-100:]

5. 更新 latest_data 為最後一筆
```

##### **C. CSV 儲存函數 - save_to_csv() (第 65-76 行)**

**執行時機**: 每次收到 MQTT 訊息時 (第 129 行)

**邏輯流程**:
```
1. 檢查檔案是否存在
   ├─ 不存在 → 寫入標題行
   └─ 存在 → 直接附加數據

2. 以附加模式開啟檔案
   mode='a' (append)

3. 寫入新的一行數據
   格式: 時間戳記,電燈狀態,溫度,濕度
```

##### **D. MQTT 連線回調 - on_connect() (第 78-88 行)**

**執行時機**: MQTT 客戶端連線成功或失敗時

**邏輯流程**:
```
1. 檢查 reason_code
   ├─ 成功 (is_failure=False)
   │   ├─ 設定 mqtt_connected = True
   │   ├─ 訂閱主題 "客廳/感測器" (QoS=1)
   │   └─ 印出成功訊息
   │
   └─ 失敗 (is_failure=True)
       ├─ 設定 mqtt_connected = False
       └─ 印出錯誤訊息
```

**重要參數**:
- `qos=1`: 至少傳遞一次（訊息可能重複，但不會遺失）

##### **E. MQTT 訊息回調 - on_message() (第 90-135 行)**

**執行時機**: 收到 MQTT 訊息時

**詳細邏輯流程**:
```
1. 接收 MQTT payload (JSON 字串)
   └─ 解碼: message.payload.decode('utf-8')

2. 解析 JSON 數據
   └─ json.loads(payload)

3. 提取數據 (支援多種欄位名稱)
   ├─ 溫度: 'temperature' 或 'temp'
   ├─ 濕度: 'humidity' 或 'humi'
   └─ 電燈: 'light_status' 或 'light'

4. 生成時間戳記
   └─ datetime.now().strftime('%Y-%m-%d %H:%M:%S')

5. 更新全域變數 latest_data

6. 將數據加入 sensor_data 列表
   └─ 如果超過 100 筆，刪除最舊的

7. 儲存到 CSV 檔案
   └─ save_to_csv(csv_data)

8. 透過 WebSocket 推送到前端
   └─ socketio.emit('new_data', latest_data)
```

**錯誤處理**:
- 使用 `try-except` 捕捉 JSON 解析錯誤
- 使用 `.get()` 方法提供預設值，避免 KeyError

##### **F. MQTT 執行緒 - start_mqtt() (第 142-148 行)**

**執行方式**: 在背景執行緒中運行 (第 155-156 行)

**邏輯**:
```python
def start_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()  # 永久執行，監聽訊息
```

**重要說明**:
- `daemon=True`: 主程式結束時，此執行緒也會自動結束
- `loop_forever()`: 阻塞式執行，持續接收 MQTT 訊息

##### **G. Flask 路由**

**1. 主頁路由 (第 158-161 行)**
```python
@app.route('/')
def index():
    return render_template('index.html')
```
- 功能: 渲染網頁介面
- URL: `http://localhost:8080/`

**2. 最新數據 API (第 163-170 行)**
```python
@app.route('/api/latest')
def get_latest():
    return jsonify({
        **latest_data,            # 展開最新數據
        'mqtt_connected': mqtt_connected,
        'total_records': len(sensor_data)
    })
```
- 功能: 提供最新一筆數據的 JSON API
- URL: `http://localhost:8080/api/latest`
- 回傳格式:
  ```json
  {
    "light_status": "開",
    "temperature": 25.5,
    "humidity": 60.0,
    "timestamp": "2025-12-07 10:30:00",
    "mqtt_connected": true,
    "total_records": 50
  }
  ```

**3. 歷史數據 API (第 172-175 行)**
```python
@app.route('/api/history')
def get_history():
    return jsonify(sensor_data)
```
- 功能: 提供所有歷史數據（最多 100 筆）
- URL: `http://localhost:8080/api/history`
- 回傳格式: 數據陣列

##### **H. 主程式啟動 (第 177-188 行)**

**啟動流程**:
```
1. 載入歷史數據 (第 151-152 行)
   └─ load_from_csv()

2. 啟動 MQTT 執行緒 (第 155-156 行)
   └─ mqtt_thread.start()

3. 啟動 Flask 伺服器 (第 187 行)
   └─ socketio.run(app, host='0.0.0.0', port=8080)
```

**重要參數**:
- `host='0.0.0.0'`: 允許外部裝置存取
- `port=8080`: 使用 8080 埠號
- `debug=False`: 正式模式（避免重複啟動問題）
- `allow_unsafe_werkzeug=True`: 允許使用 Werkzeug 開發伺服器

---

### 2️⃣ index.html - 網頁前端介面

#### 📌 程式結構

```html
1. HTML 結構 (第 1-193 行)
   ├─ 狀態列 (第 35-43 行)
   ├─ 感測器卡片 (第 45-69 行)
   └─ 圖表容器 (第 71-74 行)

2. CSS 樣式 (第 9-150 行)
   ├─ 漸層背景
   ├─ 卡片樣式
   └─ 響應式設計

3. JavaScript 邏輯 (第 194-332 行)
   ├─ Socket.IO 連線
   ├─ Chart.js 圖表初始化
   ├─ 數據更新函數
   └─ API 呼叫
```

#### 🔍 詳細邏輯分析

##### **A. Socket.IO 連線 (第 196 行)**

```javascript
const socket = io();  // 自動連線到當前伺服器
```

**說明**:
- 自動建立 WebSocket 連線
- 與後端 Flask-SocketIO 通訊
- 用於接收即時數據推送

##### **B. Chart.js 圖表初始化 (第 199-251 行)**

**圖表配置**:
```javascript
{
    type: 'line',           // 折線圖
    data: {
        labels: [],         // X 軸標籤 (時間)
        datasets: [
            {
                label: '溫度 (°C)',
                yAxisID: 'y',    // 使用左側 Y 軸
                borderColor: '#ef4444',  // 紅色
            },
            {
                label: '濕度 (%)',
                yAxisID: 'y1',   // 使用右側 Y 軸
                borderColor: '#3b82f6',  // 藍色
            }
        ]
    },
    options: {
        scales: {
            y: {              // 左側 Y 軸 (溫度)
                position: 'left',
            },
            y1: {             // 右側 Y 軸 (濕度)
                position: 'right',
                grid: {
                    drawOnChartArea: false,  // 不繪製網格線
                }
            }
        }
    }
}
```

**重要特性**:
- **雙 Y 軸**: 溫度和濕度使用不同的 Y 軸刻度
- **互動模式**: `mode: 'index'` - 滑鼠懸停時顯示該時間點的所有數據
- **響應式**: 自動適應容器大小

##### **C. 數據更新函數 - updateDisplay() (第 254-285 行)**

**邏輯流程**:
```javascript
function updateDisplay(data) {
    // 1. 更新電燈狀態
    if (data.light_status === '開' || data.light_status === 'on') {
        lightDiv.className = 'light-status light-on';   // 黃色發光
        lightDiv.textContent = '🟡';
    } else {
        lightDiv.className = 'light-status light-off';  // 灰色
        lightDiv.textContent = '⚫';
    }
    
    // 2. 更新溫濕度數值 (保留小數點後一位)
    document.getElementById('temperature').textContent = 
        Number(data.temperature).toFixed(1);
    document.getElementById('humidity').textContent = 
        Number(data.humidity).toFixed(1);
    
    // 3. 更新時間戳記
    document.getElementById('updateTime').textContent = 
        `最後更新: ${data.timestamp || '未知'}`;
    
    // 4. 更新 MQTT 連線狀態
    if (data.mqtt_connected) {
        mqttLed.classList.add('connected');   // 綠色 LED
        mqttStatus.textContent = 'MQTT 已連線';
    } else {
        mqttLed.classList.remove('connected');  // 灰色 LED
        mqttStatus.textContent = 'MQTT 未連線';
    }
    
    // 5. 更新總記錄數
    document.getElementById('totalRecords').textContent = 
        data.total_records || 0;
}
```

##### **D. 圖表更新函數 - updateChart() (第 288-297 行)**

```javascript
function updateChart(history) {
    // 提取時間 (只顯示時:分:秒)
    const labels = history.map(d => 
        d.timestamp ? d.timestamp.split(' ')[1] : ''
    );
    
    // 提取溫度和濕度數據
    const temps = history.map(d => d.temperature);
    const humis = history.map(d => d.humidity);
    
    // 更新圖表
    chart.data.labels = labels;
    chart.data.datasets[0].data = temps;
    chart.data.datasets[1].data = humis;
    chart.update();  // 重新渲染
}
```

##### **E. WebSocket 監聽 (第 300-303 行)**

```javascript
socket.on('new_data', function(data) {
    console.log('收到新數據:', data);
    fetchLatest();  // 重新取得最新數據
});
```

**說明**:
- 監聽後端發送的 `new_data` 事件
- 收到訊息後立即更新顯示

##### **F. API 呼叫函數**

**1. fetchLatest() - 取得最新數據 (第 306-313 行)**
```javascript
function fetchLatest() {
    fetch('/api/latest')
        .then(response => response.json())
        .then(data => {
            updateDisplay(data);  // 更新顯示
        })
        .catch(error => console.error('錯誤:', error));
}
```

**2. fetchHistory() - 取得歷史數據 (第 316-323 行)**
```javascript
function fetchHistory() {
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            updateChart(data);  // 更新圖表
        })
        .catch(error => console.error('錯誤:', error));
}
```

##### **G. 初始化與定時更新 (第 326-330 行)**

```javascript
// 頁面載入時立即執行
fetchLatest();    // 取得最新數據
fetchHistory();   // 取得歷史數據

// 每 5 秒更新一次歷史圖表
setInterval(fetchHistory, 5000);
```

**說明**:
- 最新數據: 透過 WebSocket 即時推送，不需輪詢
- 歷史數據: 每 5 秒更新一次圖表

---

### 3️⃣ generate_test_data.py - 測試數據生成器

#### 📌 主要函數

##### **A. generate_test_data() (第 18-62 行)**

**功能**: 生成指定筆數的模擬測試數據

**邏輯**:
```python
def generate_test_data(count=50):
    # 1. 計算起始時間 (從幾小時前開始)
    base_time = datetime.now() - timedelta(hours=count//2)
    
    # 2. 設定基礎溫濕度
    base_temp = 25.0
    base_humi = 60.0
    
    # 3. 迴圈生成數據
    for i in range(count):
        # 計算時間戳記 (每 5 分鐘一筆)
        timestamp = base_time + timedelta(minutes=i * 5)
        
        # 生成溫度 (加上隨機波動)
        temperature = base_temp + random.uniform(-3, 3) + (i % 10) * 0.5
        
        # 生成濕度 (加上隨機波動)
        humidity = base_humi + random.uniform(-5, 5) + (i % 8) * 0.8
        
        # 模擬電燈狀態 (白天多關、晚上多開)
        hour = timestamp.hour
        if 6 <= hour <= 18:  # 白天
            light_status = "關" if random.random() > 0.3 else "開"
        else:                # 晚上
            light_status = "開" if random.random() > 0.3 else "關"
```

**生成規則說明**:
- **時間間隔**: 每 5 分鐘一筆數據
- **溫度範圍**: 約 22°C ~ 28°C
- **濕度範圍**: 約 55% ~ 65%
- **電燈規律**: 白天 70% 關閉，晚上 70% 開啟

##### **B. save_to_csv() (第 64-72 行)**

```python
def save_to_csv(data, filename='sensor_data.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['時間戳記', '電燈狀態', '溫度', '濕度']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()  # 寫入標題行
        writer.writerows(data)  # 寫入所有數據
```

**重要參數**:
- `mode='w'`: 覆寫模式（會刪除舊數據）
- `encoding='utf-8'`: 支援中文

##### **C. save_to_excel() (第 74-112 行)**

**功能**: 將數據儲存為 Excel 格式，並套用樣式

**特殊功能**:
```python
# 1. 設定標題樣式
from openpyxl.styles import Font, PatternFill
for cell in ws[1]:
    cell.font = Font(color="FFFFFF", bold=True)  # 白色粗體
    cell.fill = PatternFill(start_color="366092", 
                            end_color="366092", 
                            fill_type="solid")  # 藍色背景

# 2. 調整欄寬
ws.column_dimensions['A'].width = 20  # 時間戳記
ws.column_dimensions['B'].width = 12  # 電燈狀態
ws.column_dimensions['C'].width = 10  # 溫度
ws.column_dimensions['D'].width = 10  # 濕度
```

---

### 4️⃣ test_mqtt_publish.py - MQTT 測試工具

#### 📌 主要函數

##### **A. publish_test_data() (第 24-64 行)**

**功能**: 發布指定筆數的 MQTT 測試訊息

**邏輯流程**:
```python
def publish_test_data(client, count=10, interval=2):
    for i in range(count):
        # 1. 生成隨機測試數據
        data = {
            "temperature": round(20 + random.uniform(-5, 10), 2),  # 15-30°C
            "humidity": round(50 + random.uniform(-10, 20), 2),     # 40-70%
            "light_status": "開" if i % 2 == 0 else "關",
            "timestamp": datetime.now().isoformat(),
            "device": "測試裝置",
            "message_id": i + 1
        }
        
        # 2. 轉換為 JSON 字串
        json_data = json.dumps(data, ensure_ascii=False)
        
        # 3. 發布到 MQTT
        result = client.publish(TOPIC, json_data, qos=1)
        
        # 4. 等待間隔時間
        time.sleep(interval)
```

**參數說明**:
- `count`: 發布數據筆數（預設 10 筆）
- `interval`: 間隔時間（預設 2 秒）
- `qos=1`: 訊息至少傳遞一次

---

### 5️⃣ pico/3_integrated.py - Pico W 感測器程式

#### 📌 程式結構

```python
1. WiFi 連線 (第 44-47 行)
2. MQTT 連線 (第 49-57 行)
3. 主迴圈 (第 61-102 行)
   ├─ LED 切換 (每 2 秒)
   └─ 數據上傳 (每 5 秒)
```

#### 🔍 詳細邏輯

##### **A. 溫度讀取 (第 37-41 行)**

```python
def read_temperature():
    # 讀取 Pico W 內建溫度感測器 (ADC4)
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706) / 0.001721  # 轉換公式
    return round(temperature, 1)
```

**說明**:
- 使用 Pico W 內建的 RP2040 晶片溫度感測器
- 公式來自官方文檔

##### **B. 主迴圈邏輯 (第 71-102 行)**

```python
while True:
    current_time = time.time()

    # 1. 每 2 秒切換 LED (模擬電燈控制)
    if current_time - last_led_time >= led_interval:
        led.toggle()
        last_led_time = current_time

    # 2. 每 5 秒上傳數據
    if current_time - last_publish_time >= publish_interval:
        # 收集數據
        temp = read_temperature()
        humi = round(random.uniform(50, 70), 1)  # 模擬濕度
        is_on = led.value() == 1

        # 建立 JSON payload
        payload = {
            "temperature": temp,
            "humidity": humi,
            "light_status": "開" if is_on else "關",
            "device": "Pico W (App 3)",
            "uptime": current_time - start_time
        }

        # 發布 MQTT
        client.publish(TOPIC, json.dumps(payload))
        last_publish_time = current_time

    # 短暫暫停避免 CPU 滿載
    time.sleep(0.1)
```

**時間控制策略**:
- 使用非阻塞式設計
- LED 切換和數據上傳獨立計時
- 避免使用 `time.sleep()` 造成阻塞

---

## 可手動修改的部分

### 🔧 配置參數修改

#### 1. app_flask.py - MQTT 設定

**位置**: 第 18-21 行

```python
# MQTT 設定
MQTT_BROKER = "localhost"      # 可修改為遠端 Broker IP
MQTT_PORT = 1883               # 可修改埠號
MQTT_TOPIC = "客廳/感測器"     # 可修改訂閱主題
```

**修改範例**:

##### 範例 1: 使用遠端 MQTT Broker

```python
MQTT_BROKER = "broker.hivemq.com"  # 公開 MQTT Broker
MQTT_PORT = 1883
MQTT_TOPIC = "myproject/sensors"
```

##### 範例 2: 多房間監控

```python
MQTT_TOPIC = "家庭/+/感測器"  # + 為萬用字元
# 可訂閱: 家庭/客廳/感測器, 家庭/臥室/感測器 等
```

##### 範例 3: 使用安全連線

```python
MQTT_BROKER = "your-broker.com"
MQTT_PORT = 8883  # TLS/SSL 埠號
# 需額外設定憑證
```

#### 2. app_flask.py - CSV 檔案路徑

**位置**: 第 34 行

```python
CSV_FILE = 'sensor_data.csv'  # 可修改儲存路徑
```

**修改範例**:

```python
# 使用絕對路徑
CSV_FILE = '/home/pi/data/sensor_data.csv'

# 使用日期作為檔名
from datetime import datetime
CSV_FILE = f'sensor_data_{datetime.now().strftime("%Y%m%d")}.csv'

# 儲存到專用資料夾
import os
os.makedirs('data', exist_ok=True)
CSV_FILE = 'data/sensor_data.csv'
```

#### 3. app_flask.py - 數據保留筆數

**位置**: 第 54, 119 行

```python
# 只保留最近 100 筆
sensor_data = loaded_data[-100:]

# 可修改為其他數值
sensor_data = loaded_data[-200:]  # 保留 200 筆
sensor_data = loaded_data[-50:]   # 保留 50 筆
```

#### 4. app_flask.py - Flask 伺服器設定

**位置**: 第 187 行

```python
socketio.run(app, 
             host='0.0.0.0',   # 可修改為 '127.0.0.1' 僅本地存取
             port=8080,        # 可修改埠號
             debug=False)      # 可改為 True 啟用除錯模式
```

**修改範例**:

```python
# 僅本地存取
socketio.run(app, host='127.0.0.1', port=8080)

# 使用不同埠號
socketio.run(app, host='0.0.0.0', port=5000)

# 啟用除錯模式 (開發時使用)
socketio.run(app, host='0.0.0.0', port=8080, debug=True)
```

#### 5. index.html - 圖表更新頻率

**位置**: 第 330 行

```javascript
// 定期更新歷史圖表
setInterval(fetchHistory, 5000);  // 5000 毫秒 = 5 秒
```

**修改範例**:

```javascript
// 更快速更新 (每 2 秒)
setInterval(fetchHistory, 2000);

// 較慢更新 (每 10 秒)
setInterval(fetchHistory, 10000);

// 停用自動更新 (僅透過 WebSocket 更新)
// setInterval(fetchHistory, 5000);  // 註解掉這行
```

#### 6. index.html - 顏色配置

**位置**: CSS 樣式區域

```css
/* 背景漸層色 (第 18 行) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* 可修改為其他顏色 */
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);  /* 綠色 */
background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);  /* 橘色 */

/* 溫度線條顏色 (第 208 行) */
borderColor: '#ef4444',  /* 紅色 */
/* 可修改為 */
borderColor: '#f97316',  /* 橘色 */

/* 濕度線條顏色 (第 215 行) */
borderColor: '#3b82f6',  /* 藍色 */
/* 可修改為 */
borderColor: '#06b6d4',  /* 青色 */
```

#### 7. generate_test_data.py - 測試數據參數

**位置**: 第 122-123, 29-46 行

```python
# 主程式中
data = generate_test_data(count=50)  # 生成 50 筆

# 函數內部
base_temp = 25.0  # 基礎溫度
base_humi = 60.0  # 基礎濕度
```

**修改範例**:

```python
# 生成更多測試數據
data = generate_test_data(count=200)

# 修改溫濕度範圍
base_temp = 30.0  # 較熱的環境
base_humi = 80.0  # 較潮濕的環境

# 修改時間間隔 (第 37 行)
timestamp = base_time + timedelta(minutes=i * 10)  # 每 10 分鐘一筆
```

#### 8. test_mqtt_publish.py - 測試參數

**位置**: 第 82 行

```python
publish_test_data(client, count=10, interval=2)
```

**修改範例**:

```python
# 發布更多測試數據
publish_test_data(client, count=50, interval=1)

# 更慢的發布頻率
publish_test_data(client, count=10, interval=5)
```

#### 9. pico/3_integrated.py - Pico W 設定

**位置**: 第 28, 64-66 行

```python
TOPIC = "客廳/感測器"  # MQTT 主題

publish_interval = 5  # 每 5 秒上傳一次數據
led_interval = 2      # 每 2 秒切換一次 LED
```

**修改範例**:

```python
# 使用不同主題
TOPIC = "臥室/感測器"

# 更快的上傳頻率
publish_interval = 2  # 每 2 秒上傳

# 更慢的 LED 切換
led_interval = 5  # 每 5 秒切換
```

### 📝 數據格式修改

#### 1. MQTT 訊息格式 - 新增欄位

**位置**: app_flask.py 第 99-106 行

**原始格式**:
```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "light_status": "開"
}
```

**修改範例 - 新增氣壓欄位**:

**步驟 1**: 修改 `on_message()` 函數

```python
# 第 99-114 行，修改為:
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode('utf-8')
        data_dict = json.loads(payload)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temperature = data_dict.get('temperature', 0)
        humidity = data_dict.get('humidity', 0)
        light_status = data_dict.get('light_status', '未知')
        pressure = data_dict.get('pressure', 0)  # ✨ 新增氣壓
        
        latest_data = {
            'light_status': light_status,
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,  # ✨ 新增
            'timestamp': timestamp
        }
```

**步驟 2**: 修改 CSV 儲存

```python
# 第 70-76 行，修改為:
fieldnames = ['時間戳記', '電燈狀態', '溫度', '濕度', '氣壓']  # ✨ 新增

csv_data = {
    '時間戳記': timestamp,
    '電燈狀態': light_status,
    '溫度': temperature,
    '濕度': humidity,
    '氣壓': pressure  # ✨ 新增
}
```

**步驟 3**: 修改前端顯示

在 `index.html` 中新增氣壓卡片:

```html
<!-- 第 186 行後新增 -->
<div class="sensor-card">
    <div class="sensor-title">🌪️ 氣壓</div>
    <div>
        <span class="sensor-value" id="pressure">--</span>
        <span class="sensor-unit">hPa</span>
    </div>
</div>
```

```javascript
// 第 266-267 行後新增
document.getElementById('pressure').textContent = 
    Number(data.pressure || 0).toFixed(1);
```

#### 2. 修改電燈狀態顯示方式

**位置**: index.html 第 257-263 行

**原始邏輯**:
```javascript
if (data.light_status === '開' || data.light_status === 'on') {
    lightDiv.className = 'light-status light-on';
    lightDiv.textContent = '🟡';
} else {
    lightDiv.className = 'light-status light-off';
    lightDiv.textContent = '⚫';
}
```

**修改範例 - 新增閃爍狀態**:

```javascript
if (data.light_status === '開') {
    lightDiv.className = 'light-status light-on';
    lightDiv.textContent = '🟡';
} else if (data.light_status === '閃爍') {
    lightDiv.className = 'light-status light-blinking';
    lightDiv.textContent = '🔴';
} else {
    lightDiv.className = 'light-status light-off';
    lightDiv.textContent = '⚫';
}
```

同時需在 CSS 中新增樣式:

```css
.light-blinking {
    background: linear-gradient(135deg, #ff0000 0%, #ff6600 100%);
    box-shadow: 0 0 30px rgba(255, 0, 0, 0.5);
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 49% { opacity: 1; }
    50%, 100% { opacity: 0.3; }
}
```

### 🎨 介面樣式修改

#### 1. 修改背景顏色

**位置**: index.html 第 18 行

```css
/* 原始 - 紫色漸層 */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* 範例 1 - 綠色漸層 */
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);

/* 範例 2 - 藍色漸層 */
background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);

/* 範例 3 - 橘紅色漸層 */
background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);

/* 範例 4 - 單色 */
background: #1e293b;

/* 範例 5 - 暗色主題 */
background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
```

#### 2. 修改卡片樣式

**位置**: index.html 第 71-82 行

```css
.sensor-card {
    background: white;
    padding: 25px;
    border-radius: 15px;  /* 圓角大小 */
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);  /* 陰影 */
}
```

**修改範例**:

```css
/* 範例 1 - 更圓潤的卡片 */
.sensor-card {
    border-radius: 25px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}

/* 範例 2 - 半透明卡片 */
.sensor-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
}

/* 範例 3 - 暗色主題卡片 */
.sensor-card {
    background: #1e293b;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
```

#### 3. 修改字體大小

**位置**: index.html

```css
/* 感測器數值字體 (第 91-95 行) */
.sensor-value {
    font-size: 36px;  /* 可修改為 48px (更大) 或 28px (更小) */
}

/* 感測器單位字體 (第 97-101 行) */
.sensor-unit {
    font-size: 18px;  /* 可修改為 24px (更大) 或 14px (更小) */
}
```

### 🔐 安全性修改

#### 1. 限制存取來源

**位置**: app_flask.py 第 16 行

```python
# 原始 - 允許所有來源
socketio = SocketIO(app, cors_allowed_origins="*")

# 修改為僅允許特定來源
socketio = SocketIO(app, cors_allowed_origins=[
    "http://localhost:8080",
    "http://192.168.1.100:8080"
])
```

#### 2. 新增 MQTT 認證

**位置**: app_flask.py 第 138-140 行

```python
# 原始
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# 修改為使用帳號密碼
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set("your_username", "your_password")  # ✨ 新增
```

#### 3. 啟用 HTTPS

需要額外設定 SSL 憑證:

```python
# app_flask.py 第 187 行
socketio.run(app, 
             host='0.0.0.0', 
             port=8080,
             certfile='/path/to/cert.pem',     # ✨ 新增
             keyfile='/path/to/key.pem')       # ✨ 新增
```

---

## 數據流程

### 📊 完整數據流程圖

```
┌─────────────────────────────────────────────────────────────┐
│                     數據流程詳細說明                         │
└─────────────────────────────────────────────────────────────┘

[1] Pico W 感測器發送
    │
    ├─ 讀取溫度 (內建感測器)
    ├─ 生成濕度 (模擬數據)
    ├─ 檢測 LED 狀態
    └─ 建立 JSON payload
         │
         ▼
    {"temperature": 25.5, "humidity": 60.0, "light_status": "開"}
         │
         ▼
[2] MQTT Publish (QoS=1)
    │
    └─> 主題: "客廳/感測器"
         │
         ▼
[3] MQTT Broker (Mosquitto)
    │
    ├─ 接收訊息
    ├─ 儲存 (根據 QoS)
    └─ 轉發給訂閱者
         │
         ▼
[4] Flask 後端 (訂閱者)
    │
    ├─ on_message() 回調
    │   │
    │   ├─ 解析 JSON
    │   ├─ 提取數據
    │   ├─ 生成時間戳記
    │   └─ 更新全域變數
    │
    ├─ 儲存到 CSV
    │   └─> sensor_data.csv
    │
    └─ WebSocket 推送
         │
         ▼
    socketio.emit('new_data', latest_data)
         │
         ▼
[5] Web 前端 (瀏覽器)
    │
    ├─ Socket.IO 接收
    │   └─> socket.on('new_data', ...)
    │
    ├─ 呼叫 API
    │   ├─> GET /api/latest
    │   └─> GET /api/history
    │
    ├─ 更新顯示
    │   ├─ updateDisplay()  → 更新卡片數值
    │   └─ updateChart()    → 更新圖表
    │
    └─ 畫面呈現
         │
         ▼
[6] 使用者看到即時數據
```

### 🔄 數據更新機制

#### A. 即時更新 (WebSocket)

```
MQTT 訊息到達
    ↓
on_message() 觸發
    ↓
socketio.emit('new_data')  ← 後端推送
    ↓
socket.on('new_data')      ← 前端接收
    ↓
fetchLatest()              ← 呼叫 API
    ↓
updateDisplay()            ← 更新顯示
    ↓
畫面即時更新 (< 500ms)
```

#### B. 定時更新 (輪詢)

```
setInterval(fetchHistory, 5000)  ← 每 5 秒執行
    ↓
GET /api/history  ← 呼叫 API
    ↓
updateChart()     ← 更新圖表
    ↓
圖表重新渲染
```

### 📁 數據儲存流程

```
MQTT 訊息
    ↓
on_message() 處理
    ↓
建立 csv_data 字典
    ↓
save_to_csv(csv_data)
    ↓
檢查檔案是否存在
    ├─ 不存在 → 寫入標題行
    └─ 存在   → 直接附加
    ↓
以附加模式寫入
    ↓
sensor_data.csv 更新
    ↓
可用 Excel 開啟查看
```

---

## 實用修改範例

### 範例 1: 新增溫度警報功能

**需求**: 當溫度超過 30°C 時顯示警告

**修改步驟**:

**步驟 1**: 修改 `index.html` - 更新顯示函數

```javascript
// 在 updateDisplay() 函數中 (約第 266 行後)
function updateDisplay(data) {
    // ... 原有程式碼 ...
    
    // 更新溫度
    const tempValue = Number(data.temperature).toFixed(1);
    document.getElementById('temperature').textContent = tempValue;
    
    // ✨ 新增溫度警報邏輯
    const tempCard = document.querySelector('.sensor-card:nth-child(2)');
    if (tempValue > 30) {
        tempCard.style.backgroundColor = '#fee2e2';  // 淺紅色背景
        tempCard.style.border = '2px solid #ef4444';  // 紅色邊框
    } else {
        tempCard.style.backgroundColor = 'white';
        tempCard.style.border = 'none';
    }
}
```

**步驟 2**: 新增聲音警報 (選用)

```javascript
// 新增警報聲音函數
function playAlert() {
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZizYIGGm98OOjTQ0MUKn//7' + '...');  // 簡化版
    audio.play();
}

// 在溫度過高時呼叫
if (tempValue > 30) {
    playAlert();
}
```

### 範例 2: 新增資料匯出功能

**需求**: 下載歷史數據為 JSON 檔案

**修改步驟**:

**步驟 1**: 在 `index.html` 新增下載按鈕

```html
<!-- 在狀態列中新增按鈕 (第 163 行後) -->
<div class="status-bar">
    <!-- ... 原有內容 ... -->
    <button onclick="downloadData()" style="padding: 8px 16px; cursor: pointer;">
        📥 下載數據
    </button>
</div>
```

**步驟 2**: 新增 JavaScript 函數

```javascript
// 新增在 <script> 區塊中
function downloadData() {
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            // 轉換為 JSON 字串
            const json = JSON.stringify(data, null, 2);
            
            // 建立下載連結
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sensor_data_${new Date().toISOString()}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
        });
}
```

### 範例 3: 新增多主題訂閱

**需求**: 同時訂閱客廳和臥室的感測器

**修改步驟**:

**步驟 1**: 修改 `app_flask.py` - MQTT 設定

```python
# 第 21 行，修改為列表
MQTT_TOPICS = [
    ("客廳/感測器", 1),
    ("臥室/感測器", 1),
    ("廚房/感測器", 1)
]  # (主題, QoS) 格式
```

**步驟 2**: 修改連線回調

```python
# 第 78-88 行，修改為:
def on_connect(client, userdata, flags, reason_code, properties):
    global mqtt_connected
    if reason_code.is_failure:
        print(f"❌ MQTT 連線失敗: {reason_code}")
        mqtt_connected = False
    else:
        print(f"✅ MQTT 連線成功")
        mqtt_connected = True
        
        # ✨ 訂閱多個主題
        for topic, qos in MQTT_TOPICS:
            client.subscribe(topic, qos=qos)
            print(f"✅ 已訂閱主題: {topic}")
```

**步驟 3**: 修改訊息處理 (辨識房間)

```python
# 在 on_message() 中新增房間辨識
def on_message(client, userdata, message):
    try:
        # ✨ 提取房間名稱
        topic_parts = message.topic.split('/')
        room = topic_parts[0] if len(topic_parts) > 0 else "未知"
        
        payload = message.payload.decode('utf-8')
        data_dict = json.loads(payload)
        
        # ... 原有程式碼 ...
        
        latest_data = {
            'room': room,  # ✨ 新增房間資訊
            'light_status': light_status,
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': timestamp
        }
```

### 範例 4: 新增數據統計功能

**需求**: 顯示今日最高/最低溫度

**修改步驟**:

**步驟 1**: 在 `app_flask.py` 新增 API 路由

```python
# 在第 176 行後新增
@app.route('/api/stats')
def get_stats():
    """計算統計數據"""
    if not sensor_data:
        return jsonify({})
    
    temps = [d['temperature'] for d in sensor_data]
    humis = [d['humidity'] for d in sensor_data]
    
    return jsonify({
        'temp_max': max(temps),
        'temp_min': min(temps),
        'temp_avg': sum(temps) / len(temps),
        'humi_max': max(humis),
        'humi_min': min(humis),
        'humi_avg': sum(humis) / len(humis),
    })
```

**步驟 2**: 在 `index.html` 顯示統計

```html
<!-- 新增統計卡片 -->
<div class="sensor-card">
    <div class="sensor-title">📊 今日統計</div>
    <div style="font-size: 14px;">
        <p>最高溫: <strong id="tempMax">--</strong>°C</p>
        <p>最低溫: <strong id="tempMin">--</strong>°C</p>
        <p>平均溫: <strong id="tempAvg">--</strong>°C</p>
    </div>
</div>
```

```javascript
// 新增取得統計的函數
function fetchStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('tempMax').textContent = 
                Number(data.temp_max).toFixed(1);
            document.getElementById('tempMin').textContent = 
                Number(data.temp_min).toFixed(1);
            document.getElementById('tempAvg').textContent = 
                Number(data.temp_avg).toFixed(1);
        });
}

// 定期更新
setInterval(fetchStats, 10000);  // 每 10 秒
fetchStats();  // 初始載入
```

### 範例 5: 新增暗色主題切換

**需求**: 使用者可切換亮色/暗色主題

**修改步驟**:

**步驟 1**: 在 `index.html` 新增 CSS 變數

```css
/* 在 <style> 區塊開頭新增 */
:root {
    --bg-gradient-start: #667eea;
    --bg-gradient-end: #764ba2;
    --card-bg: white;
    --card-text: #333;
}

[data-theme="dark"] {
    --bg-gradient-start: #1a1a2e;
    --bg-gradient-end: #16213e;
    --card-bg: #1e293b;
    --card-text: white;
}

/* 修改原有樣式 */
body {
    background: linear-gradient(135deg, 
        var(--bg-gradient-start) 0%, 
        var(--bg-gradient-end) 100%);
}

.sensor-card {
    background: var(--card-bg);
    color: var(--card-text);
}
```

**步驟 2**: 新增切換按鈕和 JavaScript

```html
<!-- 新增切換按鈕 -->
<button onclick="toggleTheme()" style="position: fixed; top: 20px; right: 20px;">
    🌓 切換主題
</button>
```

```javascript
// 新增主題切換函數
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    
    // 儲存偏好設定
    localStorage.setItem('theme', newTheme);
}

// 載入儲存的主題
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
```

---

## 常見操作

### 🚀 啟動應用程式

#### 方式 1: 使用啟動腳本 (推薦)

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico/lesson6
bash start.sh
```

**腳本功能**:
- 自動檢查測試數據是否存在
- 若無數據則自動生成
- 顯示本機 IP 位址
- 啟動 Flask 應用程式

#### 方式 2: 手動啟動

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico/lesson6
uv run python app_flask.py
```

#### 方式 3: 背景執行

```bash
nohup uv run python app_flask.py > app.log 2>&1 &
```

**查看日誌**:
```bash
tail -f app.log
```

**停止背景程式**:
```bash
pkill -f "python app_flask.py"
```

### 📊 生成測試數據

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico/lesson6
uv run python generate_test_data.py
```

**修改數據筆數**:

編輯 `generate_test_data.py` 第 123 行:
```python
data = generate_test_data(count=100)  # 改為 100 筆
```

### 🧪 發送測試 MQTT 訊息

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico/lesson6
uv run python test_mqtt_publish.py
```

**修改測試參數**:

編輯 `test_mqtt_publish.py` 第 82 行:
```python
publish_test_data(client, count=20, interval=1)  # 20 筆，間隔 1 秒
```

### 📁 查看數據檔案

#### CSV 檔案

```bash
# 查看檔案內容
cat sensor_data.csv

# 查看最後 10 筆
tail -10 sensor_data.csv

# 統計資料筆數
wc -l sensor_data.csv
```

#### Excel 檔案

使用 LibreOffice 開啟:
```bash
libreoffice sensor_data.xlsx
```

### 🔍 除錯技巧

#### 1. 檢查 MQTT Broker 狀態

```bash
sudo systemctl status mosquitto
```

**啟動 Broker**:
```bash
sudo systemctl start mosquitto
```

#### 2. 監聽 MQTT 訊息

```bash
mosquitto_sub -h localhost -t "客廳/感測器" -v
```

**說明**:
- `-h localhost`: Broker 位址
- `-t "客廳/感測器"`: 訂閱主題
- `-v`: 顯示詳細訊息

#### 3. 手動發送 MQTT 訊息

```bash
mosquitto_pub -h localhost -t "客廳/感測器" \
  -m '{"temperature": 25.5, "humidity": 60.0, "light_status": "開"}'
```

#### 4. 檢查 Flask 應用程式日誌

如果使用背景執行:
```bash
tail -f app.log
```

如果直接執行:
- 直接在終端機查看輸出

#### 5. 檢查網路連線

```bash
# 查看本機 IP
hostname -I

# 測試埠號是否開啟
sudo netstat -tulnp | grep 8080
```

### 🔧 維護操作

#### 清除舊數據

```bash
# 備份現有數據
cp sensor_data.csv sensor_data_backup.csv

# 刪除舊數據
rm sensor_data.csv sensor_data.xlsx

# 重新生成測試數據
uv run python generate_test_data.py
```

#### 重新啟動應用程式

```bash
# 停止應用程式 (Ctrl+C)
# 或
pkill -f "python app_flask.py"

# 重新啟動
bash start.sh
```

#### 更新套件

```bash
cd /home/pi/Documents/GitHub/2025_10_26_chihlee_pi_pico
uv sync
```

### 📱 從其他裝置存取

#### 1. 查詢 Raspberry Pi IP 位址

```bash
hostname -I
```

例如顯示: `192.168.1.100`

#### 2. 確認防火牆設定

```bash
# 允許 8080 埠
sudo ufw allow 8080

# 檢查防火牆狀態
sudo ufw status
```

#### 3. 從其他裝置開啟瀏覽器

在同一網路下的其他裝置（手機、電腦）開啟:

```
http://192.168.1.100:8080
```

---

## 📚 附錄

### A. MQTT QoS 等級說明

| QoS | 名稱 | 說明 | 適用場景 |
|-----|------|------|---------|
| 0 | 最多一次 | 不保證傳遞，可能遺失 | 環境監測（可容忍遺失） |
| 1 | 至少一次 | 保證傳遞，可能重複 | **本專案使用**，一般感測器 |
| 2 | 恰好一次 | 保證傳遞且不重複 | 計費系統、重要指令 |

### B. 常用 MQTT 主題命名規則

```
家庭/房間/設備類型/設備ID
例如:
- 家庭/客廳/感測器/temp01
- 家庭/臥室/燈光/led01
- 家庭/廚房/開關/switch01

使用萬用字元:
- 家庭/+/感測器     # + 代表單層萬用
- 家庭/#            # # 代表多層萬用
```

### C. Chart.js 圖表類型

本專案使用 `line` (折線圖)，其他可用類型:

- `bar`: 長條圖
- `pie`: 圓餅圖
- `doughnut`: 甜甜圈圖
- `radar`: 雷達圖
- `scatter`: 散點圖

**修改範例** (改為長條圖):

```javascript
// index.html 第 200 行
const chart = new Chart(ctx, {
    type: 'bar',  // 改為長條圖
    // ... 其餘設定 ...
});
```

### D. 數據格式範例

#### MQTT 訊息格式 (JSON)

```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "light_status": "開",
  "timestamp": "2025-12-07T10:30:00",
  "device": "Pico W",
  "uptime": 3600
}
```

#### CSV 檔案格式

```csv
時間戳記,電燈狀態,溫度,濕度
2025-12-07 10:30:00,開,25.5,60.0
2025-12-07 10:35:00,關,25.3,59.8
```

#### API 回應格式

**GET /api/latest**:
```json
{
  "light_status": "開",
  "temperature": 25.5,
  "humidity": 60.0,
  "timestamp": "2025-12-07 10:30:00",
  "mqtt_connected": true,
  "total_records": 50
}
```

**GET /api/history**:
```json
[
  {
    "timestamp": "2025-12-07 10:30:00",
    "light_status": "開",
    "temperature": 25.5,
    "humidity": 60.0
  },
  ...
]
```

### E. 錯誤代碼說明

#### MQTT 錯誤代碼

| 代碼 | 說明 | 解決方式 |
|------|------|---------|
| 1 | 協定版本不正確 | 檢查 MQTT 版本 |
| 2 | 客戶端 ID 無效 | 更改客戶端 ID |
| 3 | 伺服器無法使用 | 檢查 Broker 是否運行 |
| 4 | 帳號或密碼錯誤 | 檢查認證資訊 |
| 5 | 未授權 | 檢查權限設定 |

#### HTTP 狀態碼

| 代碼 | 說明 | 常見原因 |
|------|------|---------|
| 200 | 成功 | 正常回應 |
| 404 | 找不到 | URL 錯誤或路由不存在 |
| 500 | 伺服器錯誤 | 後端程式錯誤 |
| 503 | 服務無法使用 | 伺服器未啟動 |

### F. 效能優化建議

#### 1. 減少記憶體使用

```python
# 在 app_flask.py 中減少保留筆數
sensor_data = loaded_data[-50:]  # 從 100 改為 50
```

#### 2. 減少網路流量

```javascript
// 在 index.html 中增加更新間隔
setInterval(fetchHistory, 10000);  // 從 5 秒改為 10 秒
```

#### 3. 優化圖表渲染

```javascript
// 在 Chart.js 設定中新增
options: {
    animation: false,  // 停用動畫
    responsive: true,
    maintainAspectRatio: false
}
```

### G. 安全性建議

1. **生產環境部署**:
   - 使用 HTTPS (443 埠)
   - 啟用 MQTT 認證
   - 限制 CORS 來源
   - 使用防火牆規則

2. **數據保護**:
   - 定期備份 CSV 檔案
   - 限制檔案存取權限
   - 加密敏感資料

3. **網路安全**:
   - 使用 VPN 遠端存取
   - 不要將內網服務直接暴露到公網
   - 定期更新系統和套件

---

## 🎓 學習資源

### 相關文檔

- [Flask 官方文檔](https://flask.palletsprojects.com/)
- [Socket.IO 官方文檔](https://socket.io/docs/)
- [Chart.js 官方文檔](https://www.chartjs.org/docs/)
- [MQTT 協定說明](https://mqtt.org/)
- [Paho MQTT Python](https://eclipse.dev/paho/index.php?page=clients/python/index.php)

### 進階主題

1. **資料庫整合**: 使用 SQLite 或 PostgreSQL 取代 CSV
2. **使用者認證**: 新增登入功能
3. **多房間監控**: 擴展為多房間系統
4. **行動應用**: 使用 React Native 開發 APP
5. **機器學習**: 使用 TensorFlow 進行預測

---

**文檔結束**

如有任何問題或建議，歡迎參考 `README.md` 或 `使用說明.md`。
