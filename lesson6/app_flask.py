"""
Flask 版本的 MQTT 監控應用程式
替代 Streamlit，解決 Raspberry Pi 相容性問題
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from datetime import datetime
import json
import threading
import csv
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# MQTT 設定
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "客廳/感測器"

# 全域數據儲存
sensor_data = []
latest_data = {
    'light_status': '未知',
    'temperature': 0,
    'humidity': 0,
    'timestamp': None
}
mqtt_connected = False

# CSV 檔案路徑
CSV_FILE = 'sensor_data.csv'

def load_from_csv():
    """從 CSV 檔案載入歷史數據"""
    global sensor_data
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                loaded_data = []
                for row in reader:
                    data_dict = {
                        'timestamp': row['時間戳記'],
                        'light_status': row['電燈狀態'],
                        'temperature': float(row['溫度']),
                        'humidity': float(row['濕度'])
                    }
                    loaded_data.append(data_dict)
                
                # 只保留最近 100 筆
                sensor_data = loaded_data[-100:]
                
                # 更新最新數據
                if sensor_data:
                    global latest_data
                    latest_data = sensor_data[-1].copy()
                
                print(f"✅ 已載入 {len(sensor_data)} 筆歷史數據")
        except Exception as e:
            print(f"⚠️  載入 CSV 檔案時發生錯誤: {e}")

def save_to_csv(data):
    """儲存數據到 CSV 檔案"""
    file_exists = os.path.exists(CSV_FILE)
    
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['時間戳記', '電燈狀態', '溫度', '濕度']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(data)

def on_connect(client, userdata, flags, reason_code, properties):
    """MQTT 連線回調"""
    global mqtt_connected
    if reason_code.is_failure:
        print(f"❌ MQTT 連線失敗: {reason_code}")
        mqtt_connected = False
    else:
        print(f"✅ MQTT 連線成功")
        mqtt_connected = True
        client.subscribe(MQTT_TOPIC, qos=1)
        print(f"✅ 已訂閱主題: {MQTT_TOPIC}")

def on_message(client, userdata, message):
    """MQTT 訊息回調"""
    global latest_data, sensor_data
    
    try:
        payload = message.payload.decode('utf-8')
        print(f"📨 收到訊息: {payload}")
        
        # 解析 JSON
        data_dict = json.loads(payload)
        
        # 提取數據
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temperature = data_dict.get('temperature', data_dict.get('temp', 0))
        humidity = data_dict.get('humidity', data_dict.get('humi', 0))
        light_status = data_dict.get('light_status', data_dict.get('light', '未知'))
        
        # 更新最新數據
        latest_data = {
            'light_status': light_status,
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': timestamp
        }
        
        # 儲存到列表
        sensor_data.append(latest_data.copy())
        
        # 只保留最近 100 筆
        if len(sensor_data) > 100:
            sensor_data.pop(0)
        
        # 儲存到 CSV
        csv_data = {
            '時間戳記': timestamp,
            '電燈狀態': light_status,
            '溫度': temperature,
            '濕度': humidity
        }
        save_to_csv(csv_data)
        
        # 透過 WebSocket 推送到前端
        socketio.emit('new_data', latest_data)
        
    except Exception as e:
        print(f"處理訊息錯誤: {e}")

# 啟動 MQTT 客戶端
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    """在背景執行緒中啟動 MQTT"""
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT 錯誤: {e}")

# 啟動前先載入歷史數據
print("📂 載入歷史數據...")
load_from_csv()

# 在背景執行緒中啟動 MQTT
mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

@app.route('/')
def index():
    """主頁"""
    return render_template('index.html')

@app.route('/api/latest')
def get_latest():
    """取得最新數據 API"""
    return jsonify({
        **latest_data,
        'mqtt_connected': mqtt_connected,
        'total_records': len(sensor_data)
    })

@app.route('/api/history')
def get_history():
    """取得歷史數據 API"""
    return jsonify(sensor_data)

if __name__ == '__main__':
    print("=" * 60)
    print(" Flask MQTT 監控應用程式")
    print("=" * 60)
    print(f" 啟動中...")
    print(f" MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f" MQTT Topic: {MQTT_TOPIC}")
    print(f" CSV 檔案: {CSV_FILE}")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)

