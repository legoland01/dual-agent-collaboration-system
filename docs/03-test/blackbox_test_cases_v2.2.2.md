# oc-collab v2.2.2 黑盒测试用例

**版本**: v1
**创建日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**基于**: requirements_v2.2.2_READY.md (APPROVED)
**覆盖范围**: F-PROC-001 + F-GIT-001

---

## 测试信息

- **版本**: v2.2.2
- **测试类型**: 黑盒测试
- **优先级**: P0 (核心功能)

---

## Part A: F-PROC-001 协作规范强制执行

### TC-PROC-001: Agent1 无法操作设计文档

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-001 |
| 用例名称 | Agent1 角色边界检查 - 设计文档 |
| 优先级 | P0 |
| 前置条件 | Agent1 身份，已登录项目 |
| 测试步骤 | 1. 执行 `oc-collab design create F-TEST-001`<br>2. 观察错误消息 |
| 预期结果 | 显示权限拒绝错误消息，命令失败 |
| 对应需求 | F-PROC-001.1 |

### TC-PROC-002: Agent1 无法操作代码文件

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-002 |
| 用例名称 | Agent1 角色边界检查 - 代码文件 |
| 优先级 | P0 |
| 前置条件 | Agent1 身份，已登录项目 |
| 测试步骤 | 1. 执行 `echo "test" > src/test_file.py`<br>2. 执行 `oc-collab edit src/test_file.py` |
| 预期结果 | 显示权限拒绝错误消息 |
| 对应需求 | F-PROC-001.1 |

### TC-PROC-003: Agent2 无法修改需求文档

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-003 |
| 用例名称 | Agent2 角色边界检查 - 需求文档 |
| 优先级 | P0 |
| 前置条件 | Agent2 身份，已登录项目 |
| 测试步骤 | 1. 执行 `oc-collab requirements edit requirements_v2.2.2_DRAFT.md` |
| 预期结果 | 显示权限拒绝错误消息 |
| 对应需求 | F-PROC-001.1 |

### TC-PROC-004: Agent2 无法签署自己创建的文档

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-004 |
| 用例名称 | Agent2 角色边界检查 - 自签署 |
| 优先级 | P0 |
| 前置条件 | Agent2 身份，文档状态为 REVIEW_PENDING |
| 测试步骤 | 1. 执行 `oc-collab signoff requirements_v2.2.2_DRAFT.md` |
| 预期结果 | 显示利益冲突错误消息 |
| 对应需求 | F-PROC-001.1 |

### TC-PROC-005: DRAFT 文档无法发起评审

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-005 |
| 用例名称 | 文档状态阶段绑定 - DRAFT |
| 优先级 | P0 |
| 前置条件 | 文档状态为 DRAFT |
| 测试步骤 | 1. 执行 `oc-collab review start requirements_v2.2.2_DRAFT.md` |
| 预期结果 | 显示状态错误，无法发起评审 |
| 对应需求 | F-PROC-001.2 |

### TC-PROC-006: 已评审文档无法重复评审

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-006 |
| 用例名称 | 文档状态阶段绑定 - 已评审 |
| 优先级 | P0 |
| 前置条件 | 文档状态为 REVIEWED |
| 测试步骤 | 1. 执行 `oc-collab review start requirements_v2.2.2.md` |
| 预期结果 | 显示重复评审错误 |
| 对应需求 | F-PROC-001.2 |

### TC-PROC-007: 归档文档无法编辑

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-007 |
| 用例名称 | 文档状态阶段绑定 - ARCHIVED |
| 优先级 | P1 |
| 前置条件 | 文档状态为 ARCHIVED |
| 测试步骤 | 1. 执行 `oc-collab requirements edit requirements_v1.0.0.md` |
| 预期结果 | 显示归档错误，无法编辑 |
| 对应需求 | F-PROC-001.2 |

### TC-PROC-008: 不允许部分评审

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-008 |
| 用例名称 | 完整性门禁 - 部分评审 |
| 优先级 | P0 |
| 前置条件 | 需求文档包含多个章节 |
| 测试步骤 | 1. 执行 `oc-collab review start requirements_v2.2.2_DRAFT.md --section-only "第2章"` |
| 预期结果 | 显示完整性错误，拒绝部分评审 |
| 对应需求 | F-PROC-001.3 |

### TC-PROC-009: 合规检查命令可用

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-PROC-009 |
| 用例名称 | 合规检查 - 命令可用性 |
| 优先级 | P0 |
| 前置条件 | 无 |
| 测试步骤 | 1. 执行 `oc-collab compliance --help`<br>2. 检查命令选项 |
| 预期结果 | 命令可用，显示帮助信息 |
| 对应需求 | F-PROC-001 |

---

## Part B: F-GIT-001 Git 同步集成

### TC-GIT-001: phase_advance 自动同步

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-GIT-001 |
| 用例名称 | Git 同步集成 - phase_advance |
| 优先级 | P0 |
| 前置条件 | 有未提交的修改 |
| 测试步骤 | 1. 修改文档<br>2. 执行 `oc-collab phase-advance --sync`<br>3. 检查 Git 状态 |
| 预期结果 | 自动执行 git add → commit → push |
| 对应需求 | F-GIT-001 |

### TC-GIT-002: todo done 自动同步状态

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-GIT-002 |
| 用例名称 | Git 同步集成 - todo done |
| 优先级 | P0 |
| 前置条件 | 有待办任务，有未提交的修改 |
| 测试步骤 | 1. 执行 `oc-collab todo done 1`<br>2. 检查 Git 状态 |
| 预期结果 | 自动执行 git add → commit |
| 对应需求 | F-GIT-001 |

### TC-GIT-003: 未同步警告

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-GIT-003 |
| 用例名称 | Git 同步集成 - 未同步警告 |
| 优先级 | P0 |
| 前置条件 | 有未提交的修改 |
| 测试步骤 | 1. 修改文档<br>2. 执行 `oc-collab todo done 1` |
| 预期结果 | 显示未同步警告 |
| 对应需求 | F-GIT-001 |

### TC-GIT-004: git sync 命令可用

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-GIT-004 |
| 用例名称 | Git 同步集成 - 命令可用性 |
| 优先级 | P0 |
| 前置条件 | 无 |
| 测试步骤 | 1. 执行 `oc-collab git sync --help` |
| 预期结果 | 命令可用，显示帮助信息 |
| 对应需求 | F-GIT-001 |

### TC-GIT-005: git status 命令可用

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-GIT-005 |
| 用例名称 | Git 同步集成 - status 命令 |
| 优先级 | P1 |
| 前置条件 | 无 |
| 测试步骤 | 1. 执行 `oc-collab git status` |
| 预期结果 | 显示同步状态 |
| 对应需求 | F-GIT-001 |

---

## 测试命令

```bash
# 运行所有 v2.2.2 黑盒测试
oc-collab test --version v2.2.2

# 运行 F-PROC-001 测试
oc-collab test --filter "TC-PROC-*"

# 运行 F-GIT-001 测试
oc-collab test --filter "TC-GIT-*"
```

---

## 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 作者 | Agent 1 | 2026-02-08 | ✅ |
| 评审 | | | |
| 执行 | | | |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT

