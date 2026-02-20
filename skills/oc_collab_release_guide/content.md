# oc-collab 发布流程指南

## 全局背景

### 发布流程概览

```
oc-collab → test-agent → conf-man → pm-agent → 用户
```

| 系统 | 职责 |
|------|------|
| oc-collab | 版本协调、生成版本清单、记录代码hash |
| test-agent | 测试执行、生成测试报告 |
| conf-man | 版本登记、依赖锁定、发布协调 |
| pm-agent | 触发发布、用户通知 |

### 完整数据流

```
oc-collab          test-agent          conf-man            pm-agent
   │                   │                   │                  │
   │---version create-->│                   │                  │
   │<--manifest-------|                   │                  │
   │                   |                   |                  │
   │                   |---test run------->│                  │
   │                   │<--test_report----│                  │
   │                   |                   |                  |
   │                   |---register------->│                  │
   │                   |                   |                  |
   │                   |                   |---release------->│
   │                   |                   │<--completed-----│
```

---

## 你的任务

作为 oc-collab (Agent1/2)，你需要实现以下功能：

### 1. 版本创建命令

**命令**: `oc-collab version create <版本号>`

**功能**:
1. 确认要发布的代码版本
2. 记录每个模块的Git commit hash
3. 生成统一的版本清单 (version_manifest.yaml)

**输出**:
```yaml
# version_manifest.yaml
version: "2.3.0"
components:
  - name: "opencode-collaboration"
    path: "dual-agent-collaboration-system"
    hash: "abc123..."
  - name: "opencode-pm-agent-backend"
    path: "pm-agent/backend"
    hash: "def456..."
  - name: "@opencode/pm-agent-web"
    path: "pm-agent/frontend"
    hash: "ghi789..."
  - name: "test-agent"
    path: "test-agent"
    hash: "jkl012..."
created_at: "2026-02-20T10:00:00Z"
```

### 2. 分发测试任务

**功能**:
1. 将 version_manifest.yaml 传递给 test-agent
2. 触发 test-agent 执行测试

### 3. 实现方式

- 在 `src/cli/` 下创建 `version_commands.py`
- 在 `src/core/` 下创建 `version_manager.py`
- 参考现有的 deploy_commands.py 实现风格

---

## SOP结构

| SOP要素 | 内容 |
|---------|------|
| **1. 触发条件** | 用户要求发布新版本 |
| **2. 操作步骤** | 生成版本清单 → 记录代码hash → 分发测试任务 |
| **3. 输出产物** | version_manifest.yaml |
| **4. 验收标准** | 包含所有模块的hash，可追溯到代码 |

---

## 相关文档

- 完整发布流程: `../../HQ/docs/04-releases/RELEASE_PROCESS.md`
- 发布管理Skill: `../../HQ/skills/hq_release_management/content.md`

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-02-20 | 初始版本 |

---

**维护者**: agent5 (Consultant)
**更新日期**: 2026-02-20
