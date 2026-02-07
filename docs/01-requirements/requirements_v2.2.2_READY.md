# 需求规格说明书：oc-collab v2.2.2

**版本**: v2.8
**创建日期**: 2026-02-07
**作者**: Agent 1 (产品经理)
**版本号**: 2.2.2
**状态**: DRAFT (待 Agent2 评审)

---

## 1. 概述

### 1.1 版本信息

| 项目 | 值 |
|------|-----|
| 当前版本 | v2.2.1 |
| 变更类型 | 协作规范 + Git 集成 |

### 1.2 变更动机

| 问题 | 描述 | 严重程度 | 解决方案 |
|------|------|----------|----------|
| Agent1 越权 | Agent1 触碰设计/代码 | P1 | 角色边界强制检查 |
| DRAFT 被评审 | DRAFT 文档被发起评审 | P1 | 文档状态阶段绑定 |
| 部分评审 | F-AUTO-004 被单独评审 | P1 | 完整性门禁 |
| Git 未同步 | auto_git_sync.py 未被调用 | P1 | Git 同步集成机制 |

### 1.3 v2.2.2 范围

| 功能 | 理由 | 工时 |
|------|------|------|
| F-PROC-001.1/.2/.3 | 解决协作规范根本问题 | 8h |
| F-GIT-001 (集成版) | 集成已有功能，非重写 | 4h |

**工时总计**: 12h

---

## 2. 功能需求

### 2.1 F-PROC-001: 协作流程规范强制执行

**需求编号**: FR-PROC-001

#### 2.1.1 角色边界强制检查

**描述**: Agent1/Agent2 尝试执行非本角色权限范围内的操作时，系统自动阻止。

**触发条件**:
- Agent1 尝试创建/修改 `docs/02-design/` 下的文件
- Agent1 尝试创建/修改 `src/` 下的代码文件
- Agent2 尝试修改 `docs/01-requirements/` 下的需求文档（评审除外）
- Agent2 尝试签署自己创建的需求文档

**用户界面示例**:
```
$ oc-collab design create F-PROC-001

⛔ 权限拒绝: Agent1 无法创建设计文档。
你的角色权限: 产品经理 (需求定义、评审发起、验收确认)
如需创建设计文档，请由 Agent2 执行。
```

**验收标准**:
- [ ] Agent1 无法创建/修改设计文档
- [ ] Agent1 无法创建/修改代码文件
- [ ] Agent2 无法修改需求文档（只能评审）
- [ ] 明确的错误提示，告知权限边界

#### 2.1.2 文档状态阶段绑定

**描述**: 文档状态与协作流程阶段强制绑定，DRAFT 状态无法进入评审。

**状态机**:
```
DRAFT (草稿)
  ↓ (Agent1: 发起评审)
REVIEW_PENDING (待评审)
  ↓ (Agent2: 完成评审 + 签署)
REVIEWED (已评审)
  ↓ (Agent1: 确认设计 + 签署)
APPROVED (已批准)
  ↓ (系统: 发布新版本)
ARCHIVED (已归档)
```

**用户界面示例**:
```
$ oc-collab review start requirements_v2.2.2_DRAFT.md

⛔ 无法发起评审: 文档状态为 DRAFT，请先确认为可评审版本。
当前状态: DRAFT
要求状态: REVIEW_PENDING 或 APPROVED
提示: 使用 oc-collab doc status 命令查看文档状态
```

**验收标准**:
- [ ] DRAFT 文档无法发起评审
- [ ] 已评审文档无法被同一 Agent 再次评审
- [ ] 归档文档无法修改
- [ ] 状态变更有完整审计日志

#### 2.1.3 完整性门禁

**描述**: 需求文档必须整体评审通过，不允许单独评审部分内容。

**用户界面示例**:
```
$ oc-collab review start F-AUTO-004 --section-only

⛔ 无法评审: 不允许部分评审。
requirements_v2.2.2_DRAFT.md 是一个完整的需求文档。
请评审完整文档: oc-collab review start requirements_v2.2.2_DRAFT.md
如需对特定章节提出意见，请在完整评审中注明。
```

**验收标准**:
- [ ] 无法只评审需求的某一章节
- [ ] 无法对提取出去的内容单独评审
- [ ] 评审必须针对完整文档

---

### 2.2 F-GIT-001: Git 同步集成机制

**需求编号**: FR-GIT-001

**背景**: `auto_git_sync.py` 已在 v2.2.1 中实现，问题是**未被调用**，而非缺失。

**现有代码**:
```python
# src/core/auto_git_sync.py 已存在
class AutoGitSyncEngine:
    def detect_changes(self) -> List[str]: ...
    def auto_add(self) -> Dict[str, Any]: ...
    def auto_commit(self) -> Dict[str, Any]: ...
    def auto_push(self) -> Dict[str, Any]: ...
    def sync_all(self) -> Dict[str, Any]: ...
```

**集成方案**:

| 触发点 | 行为 |
|--------|------|
| `oc-collab phase-advance` | 调用 `auto_git_sync.sync_all()` |
| `oc-collab todo done` | 调用 `auto_git_sync.auto_add()` + `auto_commit()` |

**CLI 命令**:
```bash
# 手动触发同步
oc-collab git sync

# 同步并显示状态
oc-collab git sync --status
```

**未同步警告示例**:
```
$ oc-collab todo done 1

⚠️  警告: 您有未同步的修改。
  - state/agent_adhoc_todos.yaml 已修改
  - docs/01-requirements/requirements_v2.2.2_READY.md 已修改

建议: 执行 oc-collab git sync --status 查看详情
```

**验收标准**:
- [ ] `oc-collab phase-advance` 自动调用 `auto_git_sync.sync_all()`
- [ ] `oc-collab todo done` 自动调用 `auto_git_sync.auto_add()` + `auto_commit()`
- [ ] `oc-collab git sync` 命令可用
- [ ] 未同步修改时显示警告
- [ ] sync 失败时有明确错误提示

**工时预估**:
| 功能 | 预估时间 |
|------|----------|
| phase_advance 集成 | 1h |
| todo done 集成 | 1h |
| CLI 封装 | 1h |
| 未同步警告 | 1h |
| **总计** | **4h** |

---

## 3. 非功能需求

### 3.1 性能需求

| 需求项 | 要求 |
|--------|------|
| 角色边界检查延迟 | ≤ 100ms |
| Git 同步操作 | ≤ 5s |

### 3.2 安全需求

| 需求项 | 要求 |
|--------|------|
| 敏感信息 | 不在错误消息中暴露 |
| Git 凭据 | 通过现有 Git 机制管理 |

### 3.3 可用性需求

| 需求项 | 要求 |
|--------|------|
| 错误提示 | 提供清晰的错误提示和解决建议 |
| 权限提示 | 告知角色权限边界 |

---

## 4. 验收标准汇总

| 功能 | 验收项 | 状态 |
|------|--------|------|
| F-PROC-001.1 | Agent1 无法触碰设计/代码文件 | ⏳ |
| F-PROC-001.1 | Agent2 无法修改需求文档 | ⏳ |
| F-PROC-001.2 | DRAFT 文档无法发起评审 | ⏳ |
| F-PROC-001.2 | 状态变更有完整审计日志 | ⏳ |
| F-PROC-001.3 | 不允许部分评审 | ⏳ |
| F-GIT-001 | phase_advance 自动 sync | ⏳ |
| F-GIT-001 | todo done 自动 git | ⏳ |
| F-GIT-001 | git sync 命令可用 | ⏳ |
| F-GIT-001 | 未同步警告 | ⏳ |

---

## 5. 依赖关系

| 依赖项 | 来源 |
|--------|------|
| auto_git_sync.py | v2.2.1 已实现 |
| phase_advance.py | 现有代码 |
| todowrite/todoedit | 现有代码 |

---

## 6. 风险分析

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 权限检查误判 | 低 | 中 | 完善规则覆盖所有场景 |
| Git 同步冲突 | 低 | 低 | Git 自动处理合并 |
| 迁移兼容性 | 低 | 低 | 保留旧接口 |

---

## 7. 签署确认

### Agent 1 确认

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-07 | ✅ |

### Agent 2 技术评审

| 评审项 | 结论 |
|--------|------|
| F-PROC-001 设计 | ✅ 通过（建议补充身份检测说明） |
| F-GIT-001 集成方案 | ✅ 通过 |
| 范围合理性 | ✅ 通过 |
| 工时合理性 | ✅ 通过（12h 合理） |

#### 评审意见

| 建议项 | 说明 |
|--------|------|
| Agent 身份检测 | 明确如何检测 Agent1/Agent2（环境变量 vs 对话指定） |
| 回滚策略 | phase_advance sync 失败时如何处理 |
| 冲突处理 | Git sync 冲突时如何处理 |

#### 总体评价

v2.7 相比之前版本有重大改进：
- F-GIT-001 明确是"集成"（4h），不是"重写"（9h）
- 范围缩小到 2 个核心功能（12h）
- 完全采纳批判性评审建议

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-07 | ✅ |

---

**文档版本**: v2.7
**创建日期**: 2026-02-07
**修订日期**: 2026-02-07
**状态**: DRAFT (待 Agent2 评审)

