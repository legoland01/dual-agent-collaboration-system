#!/bin/bash
# 停止自动监控
set -e

PID_FILE="/tmp/auto_monitor.pid"
LOG_FILE="/tmp/auto_monitor.log"

stop_monitor() {
    local pid=$1
    if ps -p $pid > /dev/null 2>&1; then
        echo "停止监控 (PID: $pid)..."
        kill $pid 2>/dev/null || true
        sleep 1
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null || true
        fi
        echo "✓ 已停止"
    else
        echo "监控未运行"
    fi
}

# 检查 PID 文件
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if [ -n "$PID" ]; then
        stop_monitor $PID
    fi
    rm -f "$PID_FILE"
fi

# 也检查可能残留的进程
PIDS=$(pgrep -f "auto_monitor.py" 2>/dev/null || true)
if [ -n "$PIDS" ]; then
    echo "发现残留进程: $PIDS"
    for pid in $PIDS; do
        stop_monitor $pid
    done
fi

# 清理日志
if [ -f "$LOG_FILE" ]; then
    echo "日志保留在: $LOG_FILE"
fi
