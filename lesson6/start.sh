#!/bin/bash

# MQTT 監控應用程式啟動腳本

echo "=================================================="
echo " 🚀 啟動 MQTT 監控應用程式"
echo "=================================================="
echo ""

# 切換到腳本所在目錄
cd "$(dirname "$0")"

# 檢查測試數據是否存在
if [ ! -f "sensor_data.csv" ]; then
    echo "📊 未找到測試數據，正在生成..."
    uv run python generate_test_data.py
    echo ""
fi

echo "🌐 啟動 Flask 應用程式..."
echo ""
echo "📱 請在瀏覽器中開啟以下網址："
echo "   - http://localhost:8080"
echo "   - http://172.20.10.3:8080"
echo ""
echo "💡 提示："
echo "   - 按 Ctrl+C 停止應用程式"
echo "   - 應用程式已載入歷史數據"
echo "   - 可在另一個終端執行 test_mqtt_publish.py 發送測試數據"
echo ""
echo "=================================================="
echo ""

# 啟動應用程式
uv run python app_flask.py

