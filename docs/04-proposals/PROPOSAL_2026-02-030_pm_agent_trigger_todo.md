# Proposal: PM-Agent外部应用触发TODO通知方案

**提案编号**: PROPOSAL-2026-02-030  
**日期**: 2026-02-18  
**作者**: Agent2 (开发)  
**状态**: DRAFT

---

## 1. 背景

### 1.1 当前问题

v2.3.2实现了Question窗口交互方案，但存在以下局限：
- 用户必须手动告诉LLM "查看TODO" 才能触发
- 无法从外部应用自动触发通知
- 无法自动激活OpenCode窗口

### 1.2 期望场景

```
场景1: OpenCode已运行
  PM-Agent按钮点击 → iTerm2激活 → 自动输入"查看TODO" → 弹出question窗口

场景2: OpenCode未运行  
  PM-Agent按钮点击 → 启动iTerm2 → 执行opencode run "查看TODO" → 弹出question窗口
```

---

## 2. 技术方案

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     PM-Agent (外部Web应用)                       │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │ Agent1按钮  │  │ Agent2按钮  │  ...                        │
│  └──────┬──────┘  └──────┬──────┘                               │
└─────────┼────────────────┼──────────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   触发文件 (JSON)                                 │
│  state/trigger_agent2.json:                                    │
│  {                                                              │
│    "action": "notify_todo",                                    │
│    "agent_id": "agent2",                                       │
│    "timestamp": "2026-02-18T12:00:00"                         │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Agent Listen (oc-collab agent listen)               │
│  - 轮询检测触发文件                                             │
│  - 检测到触发后执行后续动作                                      │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AppleScript控制层                             │
│  1. 激活iTerm2窗口                                              │
│  2. 两种处理方式:                                               │
│     a) OpenCode已运行 → 输入"查看TODO" + 回车                   │
│     b) OpenCode未运行 → 执行opencode run "查看TODO"            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 触发文件格式

```json
{
  "action": "notify_todo",
  "agent_id": "agent1 | agent2 | agent3",
  "timestamp": "ISO8601时间戳",
  "source": "pm-agent"
}
```

### 2.3 AppleScript命令

**场景A: OpenCode已运行**
```applescript
tell application "iTerm2"
    activate
    delay 0.3
    tell current session of current window
        write text "查看TODO"
        keystroke return
    end tell
end tell
```

**场景B: OpenCode未运行**
```applescript
tell application "iTerm2"
    activate
    delay 0.3
    tell current session of current window
        write text "cd /path/to/project && opencode run \"查看TODO\""
        keystroke return
    end tell
end tell
```

---

## 3. PM-Agent实现需求

### 3.1 外部Web页面

| 组件 | 说明 |
|------|------|
| **Agent按钮列表** | 每个Agent对应一个按钮 |
| **点击事件** | 点击后写入触发文件到项目目录 |

### 3.2 触发文件写入

```
HTTP POST 或 文件系统写入
目标: /path/to/dual-agent-collaboration-system/state/trigger_{agent_id}.json
```

### 3.3 示例代码 (PM-Agent侧)

```javascript
// 点击Agent2按钮时
async function triggerAgent2Todo() {
  const triggerData = {
    action: "notify_todo",
    agent_id: "agent2",
    timestamp: new Date().toISOString(),
    source: "pm-agent"
  };
  
  // 写入触发文件（通过API或文件系统）
  await fetch('/api/trigger', {
    method: 'POST',
    body: JSON.stringify(triggerData)
  });
}
```

---

## 4. oc-collab实现需求

### 4.1 Agent Listen增强

在现有`agent listen`轮询中增加:
1. 检测 `state/trigger_*.json` 触发文件
2. 解析触发文件获取目标agent
3. 执行AppleScript激活iTerm2并输入命令

### 4.2 代码位置

```
src/core/agent_listener.py
  - 新增 _check_trigger_files() 方法
  - 新增 _activate_iterm2() 方法
```

---

## 5. 验收标准

- [ ] PM-Agent能够写入触发文件
- [ ] Agent Listen能检测到触发文件
- [ ] AppleScript能成功激活iTerm2
- [ ] 场景A: OpenCode已运行时自动输入"查看TODO"
- [ ] 场景B: OpenCode未运行时启动并输入命令

---

## 6. 分工

| 模块 | 负责方 |
|------|--------|
| 外部Web页面 | PM-Agent团队 |
| 触发文件写入 | PM-Agent团队 |
| Agent Listen增强 | oc-collab (Agent2) |
| AppleScript控制 | oc-collab (Agent2) |

---

## 7. 相关文档

- POC_OpenCode_TUI_Notification_Verification.md
- TODO_NOTIFY.md (instruction文件)
- PROPOSAL_2026-02-027_agent_notification_interaction.md
