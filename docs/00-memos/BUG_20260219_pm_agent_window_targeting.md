# Bug报告: PM-Agent触发TODO无法精确发送到目标Agent窗口

## 背景

v2.3.x实现了PM-Agent外部触发TODO通知功能：
1. 外部应用写入触发文件 `state/trigger_agent2.json`
2. agent listen检测到触发
3. 通过某种方式让OpenCode弹出question窗口

## 问题描述

**核心问题**: 无法精确地将"查看TODO"发送到目标Agent的OpenCode窗口。

当前有5个OpenCode窗口同时运行（4个iTerm2 + 1个Mac终端），每个窗口对应不同的agent。触发时消息被发送到错误的窗口。

## 尝试过的方案

### 方案1: AppleScript操作iTerm2
- **方法**: 使用AppleScript激活iTerm2窗口，输入"查看TODO"并按回车
- **结果**: 
  - 尝试了多种AppleScript变体
  - 问题: 第一次触发后显示滞后，需要发两次才能提交
  - 问题: 发送到front window，不是目标agent的窗口
- **代码位置**: `src/core/agent_listener.py` 早期版本

### 方案2: 剪贴板+粘贴
- **方法**: 
  1. pbcopy复制"查看TODO"到剪贴板
  2. AppleScript模拟Cmd+V粘贴
  3. 模拟回车提交
- **结果**: 成功率约50%，模式精确: 第1次→失败，第2次→显示第1次内容

### 方案3: OpenCode API直接发送
- **方法**: 调用 `POST /session/{session_id}/message`
- **结果**: 
  - 发现需要发两次才能提交（第一次输入文字，第二次触发提交）
  - 成功率提高到约80%
  - **核心问题**: 仍然发到错误窗口

### 方案4: 遍历所有端口和session组合
- **方法**: 遍历所有OpenCode端口 + 项目下所有session，尝试发送
- **结果**: 
  - 消息能发送成功
  - 但无法知道哪个端口/session对应哪个agent
  - 仍然发到错误窗口

## 根本原因

1. **端口与窗口无关联**: lsof只能看到端口号，无法知道该端口属于哪个iTerm2窗口
2. **session与agent无关联**: OpenCode的session数据库不记录agent身份
3. **多窗口并行运行**: 同一个项目有多个agent同时使用OpenCode

## 当前代码状态

`src/core/agent_listener.py` 中的 `_activate_iterm2_notify()` 方法:
- 使用异步线程发送HTTP请求
- 遍历所有端口和session组合尝试发送
- 能发送成功但发到错误窗口

## 待解决

1. 如何建立agent到session/窗口的映射?
2. 如何确定哪个端口属于哪个iTerm2窗口?
3. 或者: 是否需要改变触发机制，不依赖窗口焦点?

---

## 解决方案 (2026-02-19)

**采用微信模式**：
- PM-Agent维护Agent列表+状态（在线/离线）
- 收到TODO时显示红点提示
- 用户主动去Agent窗口输入"查看TODO"

**oc-collab无需新增功能**，复用现有：
- trigger机制通知PM-Agent
- `oc-collab todo list` Agent自己拉取

**状态**: ✅ 已解决，移交PM-Agent v1.2实现

## 相关文件

- `src/core/agent_listener.py` - 触发处理逻辑
- `src/core/todo_storage.py` - TODO存储
- `state/trigger_agent2.json` - 触发文件格式
- `~/.local/share/opencode/opencode.db` - OpenCode数据库
