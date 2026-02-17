# Proposal: Agent TODO实时通知与交互系统

**提案编号**: PROPOSAL-2026-02-027  
**日期**: 2026-02-17  
**作者**: Agent 1 (产品经理)  
**状态**: DRAFT

---

## 1. 背景

### 1.1 当前问题

v2.3.1实现了`agent listen`后台监听功能，但存在以下问题：
- 监听进程只能将通知写入日志文件
- 用户无法在opencode的prompt窗口中实时收到通知
- 用户无法直接与TODO进行交互（执行/推迟/拒绝）

### 1.2 期望场景

```
用户启动监听:
  nohup oc-collab agent listen --interval 3 > /dev/null &

Agent2创建TODO:
  oc-collab todowrite --content "实现功能X" --to 1

用户prompt窗口立即显示:
  ┌─────────────────────────────────────────┐
  │ 📬 新TODO: [TODO-2to1-025]            │
  │ 内容: 实现功能X                         │
  │ 来自: agent2                           │
  │                                        │
  │ 请选择: [执行] [推迟] [拒绝]           │
  └─────────────────────────────────────────┘
```

---

## 2. 技术方案

### 2.1 架构设计

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  oc-collab CLI  │────▶│  OpenCode Server │────▶│  Prompt Window   │
│  (agent listen) │     │  (HTTP API)      │     │  (交互UI)        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                        │
        │ POST /api/tui         │
        │ appendPrompt         │
        │ showToast            │
        ▼                      ▼
   ┌─────────────────────────────────────────┐
   │ 调用 opencode SDK 或直接HTTP调用         │
   │ - tui.appendPrompt() 添加交互选项       │
   │ - tui.showToast() 显示通知             │
   └─────────────────────────────────────────┘
```

### 2.2 依赖

- opencode server API (HTTP)
- 认证机制 (API Key)
- 可选: opencode SDK (@opencode-ai/sdk)

### 2.3 实现方式

#### 方式A: 直接HTTP调用

```python
import requests

def show_notification(todo_id, content, from_agent):
    """调用opencode server API显示通知"""
    url = "http://localhost:4096/api/tui/showToast"
    data = {
        "message": f"新TODO: [{todo_id}] {content}",
        "variant": "info"
    }
    requests.post(url, json=data, headers={"Authorization": "Bearer API_KEY"})

def append_interactive_prompt(todo_id, content):
    """往prompt窗口添加交互选项"""
    url = "http://localhost:4096/api/tui/appendPrompt"
    data = {
        "text": f"""📬 新TODO: [{todo_id}]
内容: {content}
请选择: [执行] [推迟] [拒绝]"""
    }
    requests.post(url, json=data, headers={"Authorization": "Bearer API_KEY"})
```

#### 方式B: 使用opencode SDK

```javascript
// 需要在Python中调用JS SDK
// 或使用subprocess调用node
```

---

## 3. 功能需求

### 3.1 F-NOTIFY-001: 终端实时通知

**描述**: 后台监听时，在opencode prompt窗口显示通知

**验收标准**:
- [ ] 监听到新TODO时，prompt窗口显示通知
- [ ] 通知包含TODO编号、内容、来自Agent
- [ ] 通知格式统一、可读

### 3.2 F-NOTIFY-002: 交互选项

**描述**: 在prompt窗口显示可点击的交互选项

**验收标准**:
- [ ] 显示"执行"/"推迟"/"拒绝"选项
- [ ] 用户点击选项后执行相应操作
- [ ] 操作结果反馈给用户

### 3.3 F-NOTIFY-003: 配置管理

**描述**: 管理opencode server连接配置

**验收标准**:
- [ ] 支持配置server地址和端口
- [ ] 支持配置API Key认证
- [ ] 支持启用/禁用通知功能

---

## 4. 版本规划

### v2.3.2: Agent通知与交互系统

| 功能 | 优先级 | 工时 |
|------|--------|------|
| F-NOTIFY-001 终端实时通知 | P0 | 4h |
| F-NOTIFY-002 交互选项 | P0 | 4h |
| F-NOTIFY-003 配置管理 | P1 | 2h |

**预计工时**: ~10h

---

## 5. 风险与应对

| 风险 | 应对措施 |
|------|----------|
| opencode server未运行 | 降级到终端通知，写入日志 |
| API认证失败 | 提示用户配置API Key |
| 网络延迟 | 本地缓存通知 |

---

## 6. 预期收益

- **实时性**: 用户立即知道有新TODO
- **交互性**: 直接在prompt窗口处理TODO
- **用户体验**: 无需查看日志文件
