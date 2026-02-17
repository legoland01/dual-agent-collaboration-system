# Bug报告: agent listen后台运行时无终端通知

**Bug编号**: BUG-20260217-003
**发现日期**: 2026-02-17
**发现者**: Agent 1 (产品经理)
**状态**: OPEN
**优先级**: P0
**类型**: 功能缺陷

---

## 1. Bug描述

### 问题陈述

`oc-collab agent listen` 后台运行时，只将通知写入日志文件，不会在终端实时显示通知。

### 复现步骤

1. 启动后台监听: `nohup oc-collab agent listen --interval 3 > logs/agent_listen.log &`
2. Agent2创建TODO给Agent1
3. 查看日志文件可以看到通知，但终端没有实时通知

### 预期行为

后台监听应该在终端实时显示通知，或者通过系统通知（如macOS的Notification Center）

---

## 2. 解决方案

### 建议方案

1. 保持日志记录功能
2. 增加终端实时输出（stdout）
3. 或使用系统通知（如 `osascript` for macOS Notification Center）

### 验收标准

- [ ] 后台监听运行时，新TODO在终端实时显示通知
- [ ] 日志文件仍然保留通知记录
