"""
MQTT 測試發布腳本
用於測試 Streamlit 應用程式的 MQTT 接收功能
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import random

# MQTT 設定
BROKER = "localhost"
PORT = 1883
TOPIC = "客廳/感測器"  # 與 config.py 中的設定一致

def on_connect(client, userdata, flags, reason_code, properties):
    """連線回調函數"""
    if reason_code.is_failure:
        print(f"❌ 連線失敗: {reason_code}")
    else:
        print(f"✅ 成功連接到 MQTT Broker")

def publish_test_data(client, count=10, interval=2):
    """
    發布測試數據
    
    Args:
        client: MQTT 客戶端
        count: 發布數據筆數
        interval: 間隔時間（秒）
    """
    print(f"\n開始發布 {count} 筆測試數據...")
    print(f"主題: {TOPIC}")
    print(f"間隔: {interval} 秒\n")
    
    for i in range(count):
        # 建立測試數據（JSON 格式）
        data = {
            "temperature": round(20 + random.uniform(-5, 10), 2),  # 15-30度
            "humidity": round(50 + random.uniform(-10, 20), 2),     # 40-70%
            "light_status": "開" if i % 2 == 0 else "關",
            "timestamp": datetime.now().isoformat(),
            "device": "測試裝置",
            "message_id": i + 1
        }
        
        # 轉換為 JSON 字串
        json_data = json.dumps(data, ensure_ascii=False)
        
        # 發布訊息
        result = client.publish(TOPIC, json_data, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"[{i+1}/{count}] ✅ 發布成功")
            print(f"   溫度: {data['temperature']}°C, 濕度: {data['humidity']}%, 電燈: {data['light_status']}")
        else:
            print(f"[{i+1}/{count}] ❌ 發布失敗")
        
        # 等待間隔時間
        if i < count - 1:
            time.sleep(interval)
    
    print(f"\n✅ 已發布所有測試數據！")

def main():
    """主程式"""
    try:
        # 建立 MQTT 客戶端
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        
        # 連線到 Broker
        print(f"正在連接到 {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        
        # 等待連線建立
        time.sleep(1)
        
        # 發布測試數據
        publish_test_data(client, count=10, interval=2)
        
        # 關閉連線
        client.loop_stop()
        client.disconnect()
        print("\n✅ MQTT 連線已關閉")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print(" MQTT 測試發布腳本")
    print("=" * 60)
    print(f"\n此腳本會發布測試數據到主題: {TOPIC}")
    print("請確保：")
    print("1. MQTT Broker 正在運行")
    print("2. Streamlit 應用程式正在運行並已連線 MQTT")
    print("\n按 Ctrl+C 可隨時中斷\n")
    
    time.sleep(2)
    main()

