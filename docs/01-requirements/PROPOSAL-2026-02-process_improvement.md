# 需求提案: 流程自动化与防错机制

**提案编号**: PROPOSAL-2026-02
**提案日期**: 2026-02-10
**提案来源**: BUG-20260210-003
**关联Bug**: BUG-20260210-003 (Agent跳过提交流程)
**状态**: DRAFT (待需求分析)

---

## 1. 背景与问题

### 1.1 问题描述

在v2.2.7发布过程中，Agent2跳过了"提交黑盒测试结果给Agent1验收"的流程环节，直接执行了发布操作。

### 1.2 影响分析

| 影响项 | 说明 | 严重程度 |
|--------|------|----------|
| 流程完整性 | 缺少Agent1对黑盒测试结果的验收环节 | 中 |
| 代码质量 | 发布前未获得最终验收确认 | 中 |
| 规范遵从 | 违反了AGENTS.md规定的Agent分工原则 | 低 |

### 1.3 根因分析

1. **流程意识不足**: Agent2过于关注任务完成，忽视了流程规范
2. **缺少自动化检查**: 系统没有强制要求完成验收TODO后才能发布
3. **角色混淆**: Agent2同时承担了Agent1的验收职责

---

## 2. 解决方案

### 2.1 方案A: 发布前自动化检查 (推荐)

**实现方式**: 在发布流程中增加检查脚本

```bash
# 发布前检查
python scripts/pre_release_check.py
```

**检查内容**:
1. 是否有未完成的验收TODO (TODO.status == pending 且 phase in [testing, blackbox_testing])
2. 是否有未修复的Bug (docs/00-memos/BUG-*.md status != FIXED)
3. 单元测试是否通过
4. CHANGELOG是否更新

**优点**:
- 简单直接
- 不改变现有流程
- 易于实现

**缺点**:
- 需要人工运行检查脚本
- 脚本可能被跳过

### 2.2 方案B: Git Hook + CI/CD检查

**实现方式**: 使用pre-commit hook和CI pipeline

```yaml
# .github/workflows/release-check.yml
name: Release Check
on:
  push:
    tags:
      - 'v*'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check验收TODO
        run: |
          # 检查是否有pending的验收TODO
          # 如果有，退出并报错
```

**优点**:
- 强制执行
- 不可跳过
- 与CI/CD集成

**缺点**:
- 实现复杂度较高
- 需要配置CI/CD

### 2.3 方案C: TODO状态机增强

**实现方式**: 增强TODO状态流转逻辑

**流转规则**:
```
testing阶段:
  pending → submitted (Agent2提交)
  submitted → approved (Agent1验收)
  submitted → rejected (Agent1打回)

release阶段:
  只有 approved 状态的TODO才能触发发布
```

**优点**:
- 流程清晰
- 状态明确
- 易于追踪

**缺点**:
- 需要修改核心流程逻辑
- 复杂度较高

---

## 3. 推荐方案

**推荐**: 方案A + 方案C

- 短期: 方案A (发布前自动化检查脚本)
- 长期: 方案C (TODO状态机增强)

---

## 4. 工时估算

| 任务 | 工时 | 说明 |
|------|------|------|
| 发布前检查脚本 | 4h | pre_release_check.py |
| Git Hook集成 | 2h | pre-commit hook |
| TODO状态机增强 | 8h | todowrite状态流转增强 |
| 测试 | 2h | 单元测试+集成测试 |
| **合计** | **16h** | |

---

## 5. 验收标准

- [ ] 发布前自动检查所有待验收TODO
- [ ] 强制要求Agent1验收后才能发布
- [ ] 提供清晰的错误提示
- [ ] 兼容现有流程

---

## 6. 关联文档

| 文档 | 关联 |
|------|------|
| AGENTS.md | 核心流程规范 |
| BUG-20260210-003 | Bug报告 |
| TEMPLATE_requirements.md | 需求模板 |

---

## 7. 签署

### Agent 2 提案

| 角色 | 签署人 | 状态 | 日期 |
|------|--------|------|------|
| 提案人 | Agent 2 | ✅ 已提案 | 2026-02-10 |

### Agent 1 评审

| 角色 | 签署人 | 状态 | 日期 |
|------|--------|------|------|
| 产品负责人 | Agent 1 | ⏳ 待评审 | - |

---

**创建人**: Agent 2
**日期**: 2026-02-10
**状态**: DRAFT
