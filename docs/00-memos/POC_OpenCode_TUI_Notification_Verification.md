# POC验证报告：OpenCode TUI API实现TODO实时通知

**日期**: 2026-02-17  
**状态**: 技术验证完成，显示有bug  
**提案**: PROPOSAL_2026-02-027_agent_notification_interaction.md

---

## 一、背景

研究目标：验证能否通过OpenCode的TUI API实现TODO实时通知功能，让Agent创建的TODO能实时推送到用户的OpenCode界面。

---

## 二、技术验证

### 2.1 验证方法

1. 启动OpenCode Server：`opencode serve`
2. 调用TUI API：
   - `/tui/show-toast` - 显示toast通知
   - `/tui/append-prompt` - 追加文字到输入框
   - `/tui/execute-command` - 执行命令
3. 监控event stream验证推送

### 2.2 验证结果

| 验证项 | 结果 | 说明 |
|--------|------|------|
| API调用 | ✅ 成功 | 返回true |
| Event Stream | ✅ 收到推送 | 证明服务端推送成功 |
| TUI显示 | ❌ 失败 | 用户看不到通知 |

### 2.3 Event Stream证据

```
data: {"payload":{"type":"tui.toast.show","properties":{"message":"EVENT TEST","variant":"info"}}}
data: {"payload":{"type":"tui.prompt.append","properties":{"text":"TEST123"}}}
```

每次API调用都成功推送到TUI，但TUI没有渲染显示。

---

## 三、问题分析

### 3.1 根本原因

- API层面完全工作（event stream证明）
- TUI层面不渲染（可能是OpenCode的bug）
- 与终端类型无关（iTerm2和Mac Terminal都测试过）
- 这是OpenCode的已知问题（GitHub Issue #11786）

### 3.2 尝试过的方案

| 方案 | 结果 |
|------|------|
| iTerm2 + toast | ❌ 不显示 |
| Mac Terminal + toast | ❌ 不显示 |
| append-prompt | ❌ 不显示 |
| execute-command | ❌ 不显示 |
| AppleScript通知 | ❌ 系统通知也收不到 |

---

## 四、结论

### 4.1 技术可行性

✅ **API技术上完全可行**
- OpenCode提供了完整的TUI API
- Server正常推送
- 只需要解决显示问题

### 4.2 当前障碍

❌ **TUI渲染有bug**
- Issue #11786 "Better notifications on Desktop" 表明这是已知问题
- OpenCode团队正在改进通知功能

### 4.3 替代方案

在TUI显示问题解决前，可以：

1. **轮询文件** - TODO写入文件，Agent定期检查（已有）
2. **WebSocket长连接** - 用event stream（已验证可用）
3. **直接发消息到session** - 需要解决API格式问题
4. ✅ **Prompt窗口交互** - **已验证可行！**（2026-02-17验证）

---

## 五、后续建议

### 5.1 短期

1. ~~记录这个限制，继续推进其他开发~~
2. ✅ **使用Prompt窗口方案** - 已验证可用，实现TODO通知交互
3. 等待OpenCode修复toast问题

### 5.2 长期

1. 关注OpenCode更新
2. 或者用Web版opencode（可能显示更好）

---

## 六、Prompt窗口方案（已验证可行）

**验证日期**: 2026-02-17

**效果**: OpenCode弹出prompt窗口，让用户选择操作（接受/推迟/拒绝）

**技术方案**:
- 使用 `/tui/execute-command` 配合prompt机制
- 或通过session消息触发用户确认

**优点**:
- ✅ 用户验证有效
- ✅ 支持交互式选择
- ✅ 不依赖TUI toast

**实现建议**:
1. StateNotifier发现新TODO
2. 调用API触发OpenCode prompt窗口
3. 用户选择后执行相应操作

---

## 六、Question Tool交互方案（最终方案）

**验证日期**: 2026-02-17

**发现**: 通过分析OpenCode源代码，找到LLM触发question交互的机制

### 6.1 核心技术

OpenCode提供`question` tool，允许LLM在需要用户确认时弹出交互窗口。但这不是公开API，而是由LLM根据prompt规则自动判断何时调用。

### 6.2 如何让LLM主动询问

通过OpenCode的`instructions`机制：
1. 创建自定义instruction文件（`TODO_NOTIFY.md`）
2. 在instruction里告诉LLM：当收到新TODO时，使用question tool询问用户
3. 配置`opencode.json`加载这个instruction

### 6.3 实现文件

```
opencode_src/
├── instructions/
│   └── TODO_NOTIFY.md    # TODO通知处理instruction
└── opencode.json          # 加载instruction的配置
```

### 6.4 使用方式

1. 用户告诉LLM"你有一个新TODO"或类似信息
2. LLM根据instruction自动调用question tool
3. 用户在OpenCode的Questions区域选择操作

### 6.5 优点

- ✅ 不依赖TUI API（避免显示bug）
- ✅ 支持交互式选择（执行/推迟/拒绝）
- ✅ 用户体验好（原生OpenCode界面）
- ✅ 可自定义instruction规则

---

## 七、关联文档

- Proposal: `docs/04-proposals/PROPOSAL_2026-02-027_agent_notification_interaction.md`
- 研究: `docs/07-research/RESEARCH_Multi_Project_Collaboration.md`
- Roadmap: `docs/06-roadmap/ROADMAP_oc-collab.md`

---

**结论**: API可行，显示有bug，需要等待OpenCode修复或使用替代方案。
