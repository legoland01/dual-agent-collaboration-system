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

### 0.2 重要考量：沙盒隔离

测试平台必须保证**测试数据不污染生产系统**：

| 原则 | 说明 |
|------|------|
| **数据库隔离** | 测试使用独立的SQLite/数据库，不使用生产数据 |
| **配置文件隔离** | 测试配置独立，不影响运行系统 |
| **状态隔离** | 测试前后清理状态，不残留脏数据 |
| **文件隔离** | 测试生成的临时文件在独立目录 |

**实现方式**：
```bash
# 测试模式：使用测试数据库
oc-collab test run --sandbox --db test.db

# 测试前后自动清理
oc-collab test run --sandbox --cleanup
```

### 0.3 测试环境部署条件管理

不同模块有不同的测试要求，需要在设计测试用例时确定：

| 模块 | 部署条件 | 测试依赖 |
|------|----------|----------|
| SQLite存储 | todos.db存在 | 无 |
| 监听进程 | agent listen运行中 | SQLite |
| 实时通知 | OpenCode服务运行 | 监听进程 |
| 配置管理 | config/notification.yaml存在 | 无 |

**测试用例前置条件**：

```yaml
# 测试用例元数据
test_case:
  id: T001
  module: F-STORE-001
  requires:
    - db: todos.db  # 需要数据库
  setup:
    - create table todos
  cleanup:
    - drop table todos
```

**CLI命令**：
```bash
# 检查测试环境是否就绪
oc-collab test check-env --version v2.3.2

# 查看模块测试依赖
oc-collab test deps --module F-STORE-001
```

### 0.2 测试平台能力

| 能力 | 说明 |
|------|------|
| **前端页面互动** | Web界面进行测试操作，而不是纯命令行 |
| **测试用例执行跟踪** | 记录每个用例的执行结果（本Proposal） |
| **页面截图对比** | 测试前/后截图，验证功能正常 |
| **智能页面验证** | 解读页面内容，判断是否符合预期 |
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
- **存在collusion风险**：自己测试自己的代码，可能不客观

### 1.2 核心问题：测试舞弊（Collusion）

| 风险 | 描述 |
|------|------|
| **自己测自己** | Agent2开发的功能自己测试，缺乏独立性 |
| **虚假通过** | 测试通过但实际有bug |
| **无法追溯** | 不知道是谁在什么时候跑了什么用例 |

### 1.3 解决方向：原始记录可追溯

每次测试执行必须记录：
- **谁**执行的（executed_by）
- **什么时候**执行的（executed_at）
- **执行了什么**用例（test_case_id）
- **结果如何**（result）
- **关联什么Bug**（bug_id）

这样可以：
- 追溯测试执行历史
- 审计测试独立性
- 防止collusion

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
-- test_cases表（测试用例）
CREATE TABLE test_cases (
    id TEXT PRIMARY KEY,                    -- T001, V315等
    title TEXT NOT NULL,                    -- 用例名称
    module TEXT NOT NULL,                    -- 功能模块ID
    version TEXT NOT NULL,                   -- 版本
    description TEXT,                        -- 用例描述
    test_steps TEXT,                        -- 测试步骤
    expected_result TEXT,                   -- 预期结果
    requires TEXT,                          -- 前置条件（JSON）
    setup TEXT,                             -- 初始化（JSON）
    cleanup TEXT,                           -- 清理（JSON）
    bug_id TEXT,                            -- 关联的bug（如BUG-20260217-001）
    created_by TEXT,                        -- 创建人
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- test_results表（测试执行结果）
CREATE TABLE test_results (
    id TEXT PRIMARY KEY,                    -- tr-001
    test_case_id TEXT NOT NULL,            -- 关联test_cases.id
    version TEXT NOT NULL,                  -- 版本
    result TEXT NOT NULL,                   -- PASS/FAIL/PENDING
    executed_by TEXT NOT NULL,               -- agent1/agent2
    executed_at TIMESTAMP NOT NULL,         -- 执行时间
    duration_seconds INTEGER,                -- 执行耗时
    error_message TEXT,                     -- 失败原因
    bug_id TEXT,                            -- 关联的bug（如测试发现BUG-20260217-001）
    notes TEXT                              -- 备注
);

-- 索引
CREATE INDEX idx_test_cases_version ON test_cases(version);
CREATE INDEX idx_test_cases_module ON test_cases(module);
CREATE INDEX idx_test_cases_bug ON test_cases(bug_id);
CREATE INDEX idx_test_results_case ON test_results(test_case_id);
CREATE INDEX idx_test_results_version ON test_results(version);
CREATE INDEX idx_test_results_bug ON test_results(bug_id);
```

#### 2.2.2 CLI命令

```bash
# === 测试用例管理 ===
# 创建测试用例
oc-collab test case create --id T001 --module F-STORE-001 --title "SQLite初始化" \
    --steps "1. 执行CLI 2. 检查db" --expected "db存在" --bug-id BUG-20260217-001

# 查看测试用例
oc-collab test case show T001

# 列出所有测试用例
oc-collab test case list --version v2.3.2

# 关联Bug
oc-collab test case link-bug --case T001 --bug BUG-20260217-001

# === 测试执行 ===
# 执行测试并记录结果
oc-collab test run --version v2.3.2 --record

# 执行单个测试用例
oc-collab test run --case T001 --sandbox

# 查看测试结果
oc-collab test results --version v2.3.2

# 统计通过率
oc-collab test stats --version v2.3.2

# 查看未执行的用例
oc-collab test pending --version v2.3.2

# 导出测试报告
oc-collab test report --version v2.3.2 --format markdown

# === 测试环境 ===
# 检查测试环境是否就绪
oc-collab test check-env --version v2.3.2

# 查看模块测试依赖
oc-collab test deps --module F-STORE-001
```

#### 2.2.3 前端页面互动（测试平台能力）

| 功能 | 说明 |
|------|------|
| **测试用例展示** | Web页面显示所有测试用例 |
| **执行操作** | 点击按钮执行测试用例 |
| **结果展示** | 实时显示执行结果 |
| **历史追溯** | 查看历史执行记录 |
| **通过率统计** | 可视化展示通过率 |

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

### 6.1 阶段1验收（防collusion核心）

- [ ] test_cases表创建成功（测试用例数据库化）
- [ ] test_results表创建成功（原始记录可追溯）
- [ ] 每次执行记录executed_by（谁执行）
- [ ] 每次执行记录executed_at（何时执行）
- [ ] 每次执行记录result（执行结果）
- [ ] 每次执行记录bug_id（关联Bug）
- [ ] `oc-collab test run --record` 执行并记录结果
- [ ] `oc-collab test results` 显示执行记录（含执行人、时间）
- [ ] `oc-collab test stats` 显示通过率统计

### 6.2 阶段2验收

- [ ] `oc-collab test pending` 显示未执行用例
- [ ] `oc-collab test report` 生成报告
- [ ] E2E测试文档模板包含结果列

### 6.3 防collusion验证

- [ ] 可追溯：查询某个Agent执行的所有测试
- [ ] 可审计：查询某个Bug相关的所有测试执行
- [ ] 无虚假：未记录的测试 = 未执行

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
