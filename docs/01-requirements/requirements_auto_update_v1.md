# 需求文档：项目状态自动更新

## 文档信息

| 项目 | 内容 |
|------|------|
| 需求ID | REQ-AUTO-UPDATE-001 |
| 版本 | v1 |
| 状态 | 待评审 |
| 创建日期 | 2026-01-31 |

## 1. 概述

### 1.1 背景

当前 dual-agent 协作系统存在以下问题：
1. 项目状态需要手动更新，无法反映真实进度
2. 测试执行后测试数据不会自动更新到状态文件
3. 开发完成后阶段不会自动推进到测试阶段

### 1.2 目标

实现两个自动化功能：
1. **项目内测试/开发脚本自动更新状态** - 在 financial_case_generator_system 中集成状态更新
2. **auto 命令自动推进阶段** - 在 dual-agent 中增强自动阶段推进

### 1.3 范围

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 状态更新钩子脚本 | P0 | financial_case_generator_system 集成 |
| auto 命令阶段推进 | P0 | dual-agent 自动推进阶段 |
| 阶段转换规则 | P1 | 定义阶段自动转换条件 |

## 2. 功能需求

### 2.1 项目内状态自动更新 (F-PROJECT-AUTO-001)

#### 2.1.1 描述

在 financial_case_generator_system 中添加状态更新钩子，当以下事件发生时自动更新状态：
- 测试执行完成后更新测试数据
- 开发任务完成后更新开发状态
- 部署完成后更新部署状态

#### 2.1.2 验收标准

| 编号 | 标准 |
|------|------|
| AC-001 | 测试用例执行后自动更新 `test.blackbox_cases` |
| AC-002 | 测试通过后自动更新 `test.blackbox_passed` |
| AC-003 | 开发完成后自动更新 `development.status` |
| AC-004 | 提供 CLI 命令：`oc-collab project update --test --passed 10` |

#### 2.1.3 优先级

**P0** - 必须实现

---

### 2.2 auto 命令自动阶段推进 (F-AUTO-PHASE-001)

#### 2.2.1 描述

增强 `oc-collab auto` 命令，实现阶段自动推进：
- 开发完成后自动推进到 testing 阶段
- 测试签署后自动推进到 deployment 阶段
- 部署完成后自动推进到 completed 阶段

#### 2.2.2 验收标准

| 编号 | 标准 |
|------|------|
| AC-010 | `development.status == completed` 时自动推进到 testing |
| AC-011 | `test` 签署完成后自动推进到 deployment |
| AC-012 | `deployment.status == completed` 时自动推进到 completed |
| AC-013 | 阶段推进时自动添加历史记录 |

#### 2.2.3 优先级

**P0** - 必须实现

---

## 3. 阶段转换规则

### 3.1 自动转换矩阵

| 当前阶段 | 条件 | 下一阶段 |
|---------|------|---------|
| development | development.status == completed | testing |
| testing | test.pm_signoff && test.dev_signoff | deployment |
| deployment | deployment.status == completed | completed |

### 3.2 手动触发

| 命令 | 说明 |
|------|------|
| `oc-collab project advance` | 手动推进到下一阶段 |
| `oc-collab project set-phase testing` | 设置特定阶段 |

---

## 4. 非功能需求

### 4.1 性能需求

| 需求 | 说明 |
|------|------|
| PRF-001 | 状态更新应在 1 秒内完成 |
| PRF-002 | 阶段推进不影响其他操作 |

### 4.2 可用性需求

| 需求 | 说明 |
|------|------|
| USA-001 | 阶段推进时提供明确反馈 |
| USA-002 | 推进失败时提供原因说明 |

---

## 5. 依赖关系

| 依赖 | 说明 |
|------|------|
| oc-collab CLI | 状态更新命令 |
| StateManager | 状态读写 |

---

## 6. 约束

| 约束 | 说明 |
|------|------|
| CON-001 | 不破坏现有状态文件结构 |
| CON-002 | 保持向后兼容 |

---

## 7. 附录

### 7.1 相关文档

- `docs/01-requirements/requirements_auto_features_v1.md` - 智能同步功能

### 7.2 术语表

| 术语 | 定义 |
|------|------|
| 阶段推进 | 将项目状态从一个阶段移动到下一个阶段 |
| 状态更新 | 更新状态文件中的具体数值 |

---

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| v1 | 2026-01-31 | Agent 1 | 初始版本 |
