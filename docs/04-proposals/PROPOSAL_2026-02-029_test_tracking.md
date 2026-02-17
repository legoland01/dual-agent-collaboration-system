# Proposal: 测试用例执行跟踪系统

**Proposal ID**: PROPOSAL-2026-02-029  
**创建日期**: 2026-02-17  
**作者**: Agent 1  
**目标**: 建立测试用例执行跟踪机制，防控虚假测试  
**关联**: 测试平台（后续功能）

---

## 0. 背景说明

### 0.1 测试平台愿景

oc-collab各模块之间有深度依赖：
- CLI命令依赖core模块
- core模块依赖数据库
- 通知功能依赖OpenCode API

因此，测试必须在**所有模块都部署完成的测试平台**上进行，才能真实反映模块间集成问题。

### 0.2 测试平台能力

| 能力 | 说明 |
|------|------|
| **前端页面互动** | Web界面进行测试操作，而不是纯命令行 |
| **测试用例执行跟踪** | 记录每个用例的执行结果（本Proposal） |
| **测试环境管理** | 管理测试环境配置 |
| **测试数据管理** | 准备和清理测试数据 |
| **测试报告生成** | 自动生成测试报告 |

### 0.3 与本Proposal的关系

本Proposal是**测试平台**的组成部分，主要负责"测试用例执行跟踪"能力。

```
测试平台
├── 测试用例执行跟踪系统 (本Proposal) ← 当前
├── 测试环境管理
├── 测试数据管理
└── 测试报告生成
```

---

## 1. 问题陈述

### 1.1 现状

当前oc-collab测试管理存在以下问题：
- 测试用例设计有文档记录
- 测试执行无跟踪机制
- Bug漏到生产环境（如ACK命令bug）

### 1.2 影响

- 虚假测试：用例设计完成即标记"完成"，实际未执行
- 无法追溯：谁在什么时候跑了什么用例不清楚
- 质量隐患：设计100%覆盖，实际执行0%

---

## 2. 解决方案

### 2.1 目标

建立测试用例执行跟踪系统：
- 每个用例执行后记录结果
- 持久化存储，可追溯
- 统计通过率、执行率

### 2.2 技术方案

#### 2.2.1 数据库设计（SQLite）

```sql
-- test_results表（新增）
CREATE TABLE test_results (
    id TEXT PRIMARY KEY,                    -- tr-001
    test_case_id TEXT NOT NULL,             -- T001, V315等
    test_case_title TEXT,                   -- 用例名称
    version TEXT NOT NULL,                  -- v2.3.2
    module TEXT,                            -- F-STORE-001等
    result TEXT NOT NULL,                   -- PASS/FAIL/PENDING
    executed_by TEXT NOT NULL,              -- agent1/agent2
    executed_at TIMESTAMP NOT NULL,         -- 执行时间
    duration_seconds INTEGER,               -- 执行耗时
    error_message TEXT,                    -- 失败原因
    notes TEXT                             -- 备注
);

-- 索引
CREATE INDEX idx_test_results_version ON test_results(version);
CREATE INDEX idx_test_results_case_id ON test_results(test_case_id);
CREATE INDEX idx_test_results_executed_by ON test_results(executed_by);
```

#### 2.2.2 CLI命令

```bash
# 执行测试并记录结果
oc-collab test run --version v2.3.2 --record

# 查看测试结果
oc-collab test results --version v2.3.2

# 统计通过率
oc-collab test stats --version v2.3.2

# 查看未执行的用例
oc-collab test pending --version v2.3.2

# 导出测试报告
oc-collab test report --version v2.3.2 --format markdown
```

#### 2.2.3 测试文档模板更新

在E2E测试文档中增加结果列：

```markdown
| 序号 | 测试场景 | 测试步骤 | 预期结果 | 执行结果 | 执行人 | 执行时间 |
|------|----------|----------|----------|----------|--------|----------|
| T001 | Agent1创建TODO | ... | TODO-1to2-xxx | ✅ PASS | agent1 | 2026-02-17 |
| T002 | Agent2创建TODO | ... | TODO-2to1-xxx | ❌ FAIL | agent1 | 2026-02-17 |
```

---

## 3. 实施计划

### 3.1 阶段1：基础功能（v2.3.3）

| 功能 | 工时 | 优先级 |
|------|------|--------|
| 数据库表设计 | 1h | P0 |
| test run --record命令 | 2h | P0 |
| test results命令 | 1h | P0 |
| test stats命令 | 1h | P1 |

**工时**: ~5h

### 3.2 阶段2：增强功能（v2.3.4）

| 功能 | 工时 | 优先级 |
|------|------|--------|
| test pending命令 | 1h | P1 |
| test report命令 | 1h | P1 |
| 测试文档模板更新 | 0.5h | P1 |

**工时**: ~2.5h

### 3.3 阶段3：自动化（未来）

| 功能 | 工时 | 优先级 |
|------|------|--------|
| CI/CD集成 | 8h | P2 |
| 覆盖率仪表盘 | 4h | P2 |

**工时**: ~12h

---

## 4. 成本估算

| 阶段 | 工时 | 优先级 |
|------|------|--------|
| 阶段1 | 5h | P0 |
| 阶段2 | 2.5h | P1 |
| 阶段3 | 12h | P2 |
| **总计** | **~19.5h** | |

---

## 5. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 增加开发负担 | 可能被抵制 | 短期手动+长期自动化 |
| 执行记录繁琐 | 执行率下降 | 简化流程，自动化记录 |

---

## 6. 验收标准

### 6.1 阶段1验收

- [ ] test_results表创建成功
- [ ] `oc-collab test run --record` 执行并记录结果
- [ ] `oc-collab test results` 显示执行记录
- [ ] `oc-collab test stats` 显示通过率统计

### 6.2 阶段2验收

- [ ] `oc-collab test pending` 显示未执行用例
- [ ] `oc-collab test report` 生成报告
- [ ] E2E测试文档模板包含结果列

---

## 7. 替代方案

### 7.1 方案A：纯文档模式

- 保持当前文档记录方式
- 优点：简单
- 缺点：无法防控虚假测试

### 7.2 方案B：数据库模式（推荐）

- 使用SQLite存储测试结果
- 优点：可追溯、可统计
- 缺点：需要开发

---

## 8. 决策点

1. 是否采用数据库方案？
2. 阶段1是否纳入v2.3.3计划？
3. 优先级排序？

---

**状态**: DRAFT  
**等待评审**: Agent 2 + Consultant
