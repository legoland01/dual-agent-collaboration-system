#!/bin/bash
# 启动自动监控
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="${1:-/Users/liuzhen/Documents/河广/Product Development/chatGPT/Digital Law/Digital court/金融法院/法官数字助手/案卷材料样例/融资租赁/(2024)沪74民初721号/OpenCode Trial/financial_case_generator_system}"
INTERVAL="${2:-60}"

# 检查是否已运行
if [ -f /tmp/auto_monitor.pid ]; then
    PID=$(cat /tmp/auto_monitor.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "监控已在运行中 (PID: $PID)"
        exit 0
    fi
fi

echo "启动自动监控..."
echo "项目: $PROJECT_PATH"
echo "间隔: ${INTERVAL}秒"

cd "$PROJECT_PATH"
nohup python3 "$SCRIPT_DIR/scripts/auto_monitor.py" \
    --path "$PROJECT_PATH" \
    --interval $INTERVAL \
    > /tmp/auto_monitor.log 2>&1 &

sleep 2

if [ -f /tmp/auto_monitor.pid ]; then
    PID=$(cat /tmp/auto_monitor.pid)
    echo "✓ 监控已启动 (PID: $PID)"
    echo "日志: /tmp/auto_monitor.log"
else
    echo "✗ 启动失败"
    exit 1
fi
