#!/bin/bash

# 安裝 MQTT 監控應用程式為系統服務

echo "=================================================="
echo " 安裝 MQTT 監控應用程式系統服務"
echo "=================================================="
echo ""

# 檢查是否以 root 權限執行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 請使用 sudo 執行此腳本"
    echo "   使用方式: sudo bash install_service.sh"
    exit 1
fi

SERVICE_FILE="mqtt-monitor.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"

echo "📋 步驟 1/5: 複製服務檔案..."
cp "$SERVICE_FILE" "$SERVICE_PATH"
echo "✅ 服務檔案已複製到 $SERVICE_PATH"
echo ""

echo "📋 步驟 2/5: 重新載入 systemd..."
systemctl daemon-reload
echo "✅ systemd 已重新載入"
echo ""

echo "📋 步驟 3/5: 啟用服務（開機自動啟動）..."
systemctl enable mqtt-monitor.service
echo "✅ 服務已設定為開機自動啟動"
echo ""

echo "📋 步驟 4/5: 啟動服務..."
systemctl start mqtt-monitor.service
echo "✅ 服務已啟動"
echo ""

echo "📋 步驟 5/5: 檢查服務狀態..."
systemctl status mqtt-monitor.service --no-pager
echo ""

echo "=================================================="
echo " ✅ 安裝完成！"
echo "=================================================="
echo ""
echo "📱 現在可以開啟瀏覽器訪問："
echo "   - http://localhost:8080"
echo "   - http://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo "🔧 管理命令："
echo "   查看狀態: sudo systemctl status mqtt-monitor"
echo "   停止服務: sudo systemctl stop mqtt-monitor"
echo "   啟動服務: sudo systemctl start mqtt-monitor"
echo "   重啟服務: sudo systemctl restart mqtt-monitor"
echo "   查看日誌: sudo journalctl -u mqtt-monitor -f"
echo "   停用開機啟動: sudo systemctl disable mqtt-monitor"
echo ""
echo "=================================================="

