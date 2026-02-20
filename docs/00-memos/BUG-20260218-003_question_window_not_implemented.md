# Bug报告：v2.3.2核心功能 - TODO通知和交互

**Bug ID**: BUG-20260218-003  
**版本**: v2.3.2  
**报告日期**: 2026-02-18  
**报告人**: Agent1  
**优先级**: **critical**  
**类型**: 核心功能验证  

---

## 问题概述

v2.3.2的核心功能是"TODO送达自动探知和Question窗口交互"。需要验证实现状态。

---

## 实现状态 (2026-02-18 更新)

### 已验证通过

| 验收标准 | 状态 | 测试/说明 |
|----------|------|------------|
| 生成TODO_NOTIFY.md instruction | ✅ 已实现 | test_instruction_file_generation |
| OpenCode加载instruction | ✅ 已配置 | opencode.json:4 |
| **同步更新OpenCode instruction** | ✅ 已实现 | online_puller.py:75-83 |
| agent listen轮询检测 | ✅ 已实现 | test_R023_agent_listen |
| 系统通知 | ✅ osascript | agent_commands.py:243 |

### 实际效果

1. **当前触发方式**：用户必须告诉LLM "查看TODO" 或 "我有新TODO"
2. **Question窗口**：LLM根据instruction自动调用question tool ✅
3. **自动触发**：POC验证显示TUI API（toast/append-prompt）有渲染bug ❌

### POC验证结论

| 方案 | 结果 | 说明 |
|------|------|------|
| TUI toast API | ❌ 不显示 | OpenCode bug |
| append-prompt API | ❌ 不显示 | OpenCode bug |
| instruction + question tool | ✅ 可用 | 需用户触发 |

### 当前工作流程

```
1. agent listen 检测到新TODO
2. notify_user() 更新 instruction 文件
3. 用户启动OpenCode（从opencode_src目录）
4. 用户告诉LLM: "查看TODO"
5. LLM读取instruction → 调用question tool → 弹出窗口
```

### 限制

- **不能自动弹出窗口**：必须用户手动告诉LLM才能触发
- **必须从正确目录启动**：OpenCode必须从opencode_src目录启动

---

## 测试验证

```bash
# 单元测试
pytest tests/test_v2_3_2_modules.py::TestOnlinePuller::test_instruction_file_generation -v
# ✅ PASSED

# E2E测试
pytest tests/test_v232_e2e.py -k "agent_listen or notify" -v
# ✅ 8 tests PASSED
```

---

## 根因分析

1. **Question窗口依赖OpenCode**：
   - POC验证了instruction机制可行
   - 但需要用户在OpenCode中加载instruction文件
   - 需要LLM主动调用question tool

2. **当前实现**：
   - 使用macOS系统通知作为替代方案
   - instruction文件已正确生成

---

## 后续行动

1. 用户需手动将`config/instructions/TODO_NOTIFY.md`配置到OpenCode
2. 或等待OpenCode修复toast API

---

## 验收标准

- [x] Instruction文件生成和同步 - 测试通过
- [x] OpenCode加载配置 - 已配置opencode.json
- [x] agent listen轮询检测 - 测试通过
- [x] 系统通知 - 已实现
- [x] Question窗口交互 - instruction机制就绪，需用户触发
- [ ] **自动弹出窗口** - OpenCode TUI API有bug，暂不支持

**状态**: ⚠️ **部分完成** - instruction机制可用，但不能自动触发（依赖OpenCode修复TUI API）

---

**状态**: documented  
**相关**: POC_OpenCode_TUI_Notification_Verification.md
