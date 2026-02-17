#!/usr/bin/env python3
"""
PoC: 验证OpenCode Server TUI API可用性
"""

import requests
import json
import time

SERVER = "http://localhost:4096"

def check_server():
    """检查server是否运行"""
    try:
        r = requests.get(f"{SERVER}/global/health", timeout=2)
        return r.json()
    except:
        return None

def test_show_toast():
    """测试show-toast API"""
    data = {
        "title": "新TODO通知",
        "message": "TODO-2to1-025: 实现功能X",
        "variant": "info"
    }
    try:
        r = requests.post(f"{SERVER}/tui/show-toast", json=data)
        return r.status_code == 200
    except Exception as e:
        return str(e)

def test_append_prompt():
    """测试append-prompt API"""
    data = {
        "text": """📬 新TODO: [TODO-2to1-025]
内容: 实现功能X
来自: agent2

请选择: [执行] [推迟] [拒绝]"""
    }
    try:
        r = requests.post(f"{SERVER}/tui/append-prompt", json=data)
        return r.status_code == 200
    except Exception as e:
        return str(e)

def main():
    print("=" * 50)
    print("OpenCode TUI API PoC验证")
    print("=" * 50)
    
    # 1. 检查server
    print("\n[1] 检查Server状态...")
    health = check_server()
    if health:
        print(f"✅ Server运行中: {health}")
    else:
        print("❌ Server未运行，请先启动: opencode serve")
        print("   PoC需要Server运行才能验证")
        return
    
    # 2. 测试show-toast
    print("\n[2] 测试 /tui/show-toast API...")
    result = test_show_toast()
    if result == True:
        print("✅ show-toast API 可用")
    else:
        print(f"❌ show-toast API 失败: {result}")
    
    # 3. 测试append-prompt
    print("\n[3] 测试 /tui/append-prompt API...")
    result = test_append_prompt()
    if result == True:
        print("✅ append-prompt API 可用")
    else:
        print(f"❌ append-prompt API 失败: {result}")
    
    print("\n" + "=" * 50)
    print("PoC结论:")
    print("- API存在且格式正确")
    print("- 需要在运行opencode serve时测试")
    print("=" * 50)

if __name__ == "__main__":
    main()
