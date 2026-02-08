# PROPOSAL：oc-collab git commit 命令

**提案编号**: PROPOSAL-v2.2.3-002
**版本**: v1
**创建日期**: 2026-02-08
**创建人**: Agent 1 (产品经理)
**状态**: DRAFT

---

## 1. 背景

### 1.1 问题

| 问题 | 表现 | 影响 |
|------|------|------|
| Git 命令分散 | 用 `git add` + `git commit` + `git push` 三个命令 | 操作繁琐 |
| 规范不统一 | 有的用 git 命令，有的用 oc-collab | 难以追溯 |
| Commit 消息不规范 | 没有统一的消息格式 | 历史记录混乱 |

### 1.2 现状

| 工具 | 已有命令 |
|------|---------|
| git | `git add`, `git commit`, `git push` |
| oc-collab git | `sync`, `status`, `sync-state`, `warn` |

**缺失**: `oc-collab git commit`

---

## 2. 目标

### 2.1 核心目标

| 目标 | 实现方式 |
|------|----------|
| 统一操作入口 | 所有 Git 操作通过 oc-collab 完成 |
| 规范 commit 消息 | 提供 commit message 模板 |
| 强制签署状态 | 文档未签署时禁止 commit |

### 2.2 预期收益

| 收益 | 说明 |
|------|------|
| 操作简化 | 一个命令完成 add + commit |
| 消息规范 | 自动生成标准 commit message |
| 流程合规 | 未签署文档禁止提交 |

---

## 3. 功能需求

### 3.1 FR-GIT-001: 统一提交命令

**描述**: 创建 `oc-collab git commit` 命令。

**命令格式**:
```bash
oc-collab git commit [OPTIONS]
```

**选项**:
| 选项 | 说明 | 默认 |
|------|------|------|
| `-m, --message TEXT` | Commit 消息 | 交互式输入 |
| `-t, --type TYPE` | 类型 (feat/fix/docs/refactor) | 必填 |
| `-s, --scope SCOPE` | 范围 (docs/src/skills) | 必填 |
| `-y, --yes` | 跳过确认 | false |

**交互模式**:
```bash
$ oc-collab git commit

? Commit 类型: (feat/fix/docs/refactor/test)
? 范围: (docs/src/skills)
? 简短描述:
? 详细描述 (可选):
? 是否签署文档? (y/N)
```

### 3.2 FR-GIT-002: 强制签署检查

**描述**: 提交前检查文档签署状态。

**检查规则**:
| 文档状态 | 是否允许 commit |
|---------|----------------|
| APPROVED | ✅ 允许 |
| DRAFT | ❌ 拒绝，提示"文档未签署" |
| IN_REVIEW | ⚠️ 警告，建议评审后提交 |

**实现**:
```python
def check_document_signed():
    state = load_state()
    docs = get_modified_docs()
    
    for doc in docs:
        if doc.status == "DRAFT":
            raise Exception(f"⛔ 文档 {doc.name} 未签署 (状态: {doc.status})")
```

### 3.3 FR-GIT-003: 标准 commit 消息模板

**描述**: 根据 type 自动生成标准消息。

**模板**:
| 类型 | 格式 | 示例 |
|------|------|------|
| feat | `{type}({scope}): {subject}` | `feat(docs): 添加需求模板` |
| fix | `{type}({scope}): {subject}` | `fix(src): 修复 todo 同步 bug` |
| docs | `{type}({scope}): {subject}` | `docs: 更新评审指南` |
| refactor | `{type}({scope}): {subject}` | `refactor(core): 重构 signoff 逻辑` |
| test | `{type}({scope}): {subject}` | `test: 添加白盒测试` |

**完整消息格式**:
```
{type}({scope}): {subject}

{body}

{footer}
```

### 3.4 FR-GIT-004: 撤销提交

**描述**: 支持撤销最近的 commit。

**命令**:
```bash
oc-collab git undo   # 撤销最近一次 commit（保留更改）
oc-collab git undo --hard  # 彻底撤销（危险）
```

---

## 4. 非功能需求

### 4.1 兼容性

| 要求 | 说明 |
|------|------|
| 向后兼容 | 不影响现有 git 命令 |
| 独立运行 | 可在非 oc-collab 项目使用 |

### 4.2 可用性

| 要求 | 说明 |
|------|------|
| 交互友好 | 提供清晰的提示和帮助 |
| 错误友好 | 错误信息有解决方案 |

---

## 5. 工时预估

| 功能 | 工时 |
|------|------|
| FR-GIT-001: 统一提交命令 | 3h |
| FR-GIT-002: 强制签署检查 | 2h |
| FR-GIT-003: 标准消息模板 | 1h |
| FR-GIT-004: 撤销提交 | 2h |
| 测试 + 修复 | 2h |
| **总计** | **10h** |

---

## 6. 依赖关系

| 依赖 | 来源 |
|------|------|
| GitPython | 现有依赖 |
| oc-collab state | 现有代码 |

---

## 7. 实施路线图

### Phase 1: MVP（v2.2.3）

| 功能 | 工时 |
|------|------|
| FR-GIT-001: 统一提交命令 | 3h |
| FR-GIT-002: 强制签署检查 | 2h |

### Phase 2: 增强（v2.3.0）

| 功能 | 说明 |
|------|------|
| FR-GIT-003: 标准消息模板 | 规范 commit history |
| FR-GIT-004: 撤销提交 | 安全回滚 |

---

## 8. 相关文档

| 文档 | 说明 |
|------|------|
| COLLABORATION_GUIDE.md | Git 协作规范 |
| skills/oc_collab_collaboration_guide/ | 协作指南 skill |

---

## 9. 开放问题

| 问题 | 说明 | 负责人 |
|------|------|--------|
| commit 前是否强制 push？ | 可选配置 | 讨论 |
| 是否支持 emoji 前缀？ | 如 `✨`, `🐛`, `📝` | 讨论 |

---

## 签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品经理 | Agent 1 | 2026-02-08 | ✅ |

> **说明**: proposal 阶段，无需评审，作为后续设计输入

---

## 版本历史

| 版本 | 日期 | 作者 | 变更 |
|------|------|------|------|
| v1 | 2026-02-08 | Agent 1 | 初始版本 |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT（作为后续设计输入）
