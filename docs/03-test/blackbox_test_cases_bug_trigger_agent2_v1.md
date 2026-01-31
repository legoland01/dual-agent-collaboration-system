# 黑盒测试用例：Bug触发Agent2自动修复功能

**版本**: v1  
**创建日期**: 2026-01-31  
**作者**: Agent 1 (产品经理)

## 1. 测试概述

### 1.1 测试目标
验证"测试阶段发现bug时自动触发Agent 2激活并回退到开发阶段"功能的正确性。

### 1.2 测试范围
- 检测逻辑正确性
- 状态更新正确性
- Agent 激活正确性
- 历史记录正确性

### 1.3 测试环境
- 项目路径: financial_case_generator_system
- 框架版本: oc-collab v2.0.0

## 2. 测试用例

### 2.1 正常流程测试

#### TC-BUG-001: 测试阶段发现单个Bug

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-001 |
| 用例名称 | 测试阶段发现单个Bug |
| 前置条件 | 阶段为 testing，Agent 1 活跃 |
| 输入 | issues_to_fix = ["BUG-001: KeyError 问题"] |
| 执行步骤 | 1. 设置 phase = testing<br>2. 设置 issues_to_fix = ["BUG-001: KeyError 问题"]<br>3. 运行 detect_test_activate_agent_bugs_and2() |
| 预期结果 | triggered = true<br>bugs_found = 1<br>phase = development<br>agent2.current = true |

#### TC-BUG-002: 测试阶段发现多个Bug

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-002 |
| 用例名称 | 测试阶段发现多个Bug |
| 前置条件 | 阶段为 testing，Agent 1 活跃 |
| 输入 | issues_to_fix = ["BUG-001: 问题1", "BUG-002: 问题2", "BUG-003: 问题3"] |
| 执行步骤 | 1. 设置 phase = testing<br>2. 设置 issues_to_fix 包含 3 个 bug<br>3. 运行 detect_test_activate_agent_bugs_and2() |
| 预期结果 | triggered = true<br>bugs_found = 3<br>phase = development<br>agent2.current = true<br>历史记录包含 bug 检测条目 |

#### TC-BUG-003: 测试阶段无Bug

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-003 |
| 用例名称 | 测试阶段无Bug |
| 前置条件 | 阶段为 testing |
| 输入 | issues_to_fix = [] |
| 执行步骤 | 1. 设置 phase = testing<br>2. 设置 issues_to_fix = []<br>3. 运行 detect_test_activate_agent_bugs_and2() |
| 预期结果 | triggered = false<br>reason = "无待修复的 bug"<br>phase 保持 testing<br>agent1.current = true（无变化） |

### 2.2 阶段条件测试

#### TC-BUG-004: 非测试阶段（开发阶段）

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-004 |
| 用例名称 | 非测试阶段不触发 |
| 前置条件 | 阶段为 development |
| 输入 | phase = development, issues_to_fix = ["BUG-001"] |
| 执行步骤 | 1. 设置 phase = development<br>2. 设置 issues_to_fix 包含 bug<br>3. 运行 detect_test_activate_agent_bugs_and2() |
| 预期结果 | triggered = false<br>reason = "当前不在 testing 阶段"<br>phase 保持 development<br>无 Agent 切换 |

#### TC-BUG-005: 非测试阶段（部署阶段）

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-005 |
| 用例名称 | 部署阶段不触发 |
| 前置条件 | 阶段为 deployment |
| 输入 | phase = deployment, issues_to_fix = ["BUG-001"] |
| 执行步骤 | 1. 设置 phase = deployment<br>2. 设置 issues_to_fix 包含 bug<br>3. 运行 detect_test_activate_agent_bugs_and2() |
| 预期结果 | triggered = false<br>phase 保持 deployment |

### 2.3 边界条件测试

#### TC-BUG-006: issues_to_fix 为 None

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-006 |
| 用例名称 | issues_to_fix 为 None |
| 前置条件 | 阶段为 testing |
| 输入 | issues_to_fix = null |
| 执行步骤 | 1. 设置 phase = testing<br>2. 设置 issues_to_fix = null<br>3. 运行 detect_test_activate_agent_bugs_and2() |
| 预期结果 | triggered = false<br>视为无 bug |

#### TC-BUG-007: test 字段不存在

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-007 |
| 用例名称 | test 字段不存在 |
| 前置条件 | 阶段为 testing |
| 输入 | test 字段不存在 |
| 执行步骤 | 1. 设置 phase = testing<br>2. 删除 test 字段<br>3. 运行 detect_test_activate_agent_bugs_and2() |
| 预期结果 | triggered = false |

#### TC-BUG-008: project.agents 不存在

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-008 |
| 用例名称 | agents 字段不存在 |
| 前置条件 | 阶段为 testing，存在 bug |
| 输入 | project.agents = null |
| 执行步骤 | 1. 设置 phase = testing<br>2. 设置 issues_to_fix 包含 bug<br>3. 删除 project.agents<br>4. 运行 detect_test_activate_agent_bugs_and2() |
| 预期结果 | triggered = false<br>返回错误信息 |

### 2.4 集成测试

#### TC-BUG-009: 集成到 auto 命令

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-009 |
| 用例名称 | oc-collab auto 集成 |
| 前置条件 | 项目处于 testing 阶段，存在 bug |
| 输入 | 运行 oc-collab auto --force |
| 预期结果 | 执行历史包含 bug 检测条目<br>阶段更新为 development<br>Agent 2 被激活 |

#### TC-BUG-010: 集成到守护进程

| 项目 | 内容 |
|------|------|
| 用例编号 | TC-BUG-010 |
| 用例名称 | Agent Auto Runner 守护进程 |
| 前置条件 | 守护进程运行中 |
| 输入 | 测试阶段发现 bug |
| 预期结果 | 守护进程执行 oc-collab auto<br>阶段自动更新 |

## 3. 测试数据

### 3.1 测试项目状态 - 发现Bug

```yaml
version: 2.0.0
phase: testing
project:
  name: 测试项目
  agents:
    agent1:
      role: 产品经理
      current: true
    agent2:
      role: 开发
      current: false
test:
  status: in_progress
  blackbox_cases: 22
  blackbox_passed: 20
  issues_to_fix:
    - "BUG-001: KeyError: '证据归属规划表'"
    - "BUG-002: 0.5子任务输出格式异常"
    - "BUG-003: PDF 渲染字体缺失"
```

### 3.2 测试项目状态 - 测试通过

```yaml
version: 2.0.0
phase: testing
project:
  agents:
    agent1:
      current: true
    agent2:
      current: false
test:
  status: in_progress
  issues_to_fix: []
```

## 4. 测试执行

### 4.1 执行命令

```bash
# 进入测试项目
cd /path/to/financial_case_generator_system

# 手动测试
python3 -c "
from src.core.phase_advance import PhaseAdvanceEngine
engine = PhaseAdvanceEngine('.')
result = engine.detect_test_activate_agent_bugs_and2()
print(result)
"

# 验证状态
oc-collab project status

# 检查历史记录
oc-collab history
```

### 4.2 预期输出

**成功触发**:
```
{'triggered': True, 'bugs_found': 2, 'bugs': ['BUG-001', 'BUG-002'], 'reason': '测试发现 bug，触发 Agent 2 修复', 'message': '✓ 检测到 2 个 bug，激活 Agent 2 并回退到 development 阶段'}
```

**无需处理**:
```
{'triggered': False, 'reason': '无待修复的 bug', 'message': '测试通过，无 bug 需要修复'}
```

## 5. 测试结果记录

### 5.1 测试执行记录

| 用例编号 | 执行日期 | 执行人 | 结果 | 备注 |
|----------|----------|--------|------|------|
| TC-BUG-001 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-002 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-003 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-004 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-005 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-006 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-007 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-008 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-009 | 2026-01-31 | Agent 1 | - | 待执行 |
| TC-BUG-010 | 2026-01-31 | Agent 1 | - | 待执行 |

## 6. 回归测试

### 6.1 需要回归的测试用例
- TC-AUTO-001: 自动推进阶段
- TC-PHASE-001: 阶段状态检查
- TC-SIGN-001: 签署功能

### 6.2 回归测试执行
在完成本功能测试后，需执行回归测试确保不影响现有功能。
