# 双Agent全自动协作框架 - 开发计划

## 版本信息
- **版本**: v1
- **创建日期**: 2026-01-31
- **作者**: Agent 1 (产品经理)
- **关联设计版本**: v2

## 1. 概述

### 1.1 开发目标
根据详细设计v2，实现双Agent全自动协作框架，总工时10天。

### 1.2 开发原则
- 按里程碑分阶段交付
- 每个里程碑有明确的交付物和检查项
- 代码提交时自动运行单元测试
- 集成测试在每个里程碑结束时执行

## 2. 里程碑计划

### 2.1 里程碑总览

| 里程碑 | 时间 | 目标 | 状态 |
|-------|------|------|------|
| M1: 框架就绪 | 第1-2天 | Agent核心组件可运行 | 待开始 |
| M2: 状态机完成 | 第3-4天 | 状态转换正常执行 | 待开始 |
| M3: 行为规则完成 | 第5-6天 | Agent 1/2行为规则全部实现 | 待开始 |
| M4: 文档生成完成 | 第7天 | 文档生成和检查正常 | 待开始 |
| M5: 异常处理完成 | 第8天 | 异常处理和恢复机制正常 | 待开始 |
| M6: 发布上线 | 第9-10天 | 全流程测试通过，部署验证通过 | 待开始 |

### 2.2 详细里程碑

#### M1: 框架就绪（第1-2天）

**目标**: Agent核心组件可运行，Git Monitor能检测变更

**交付物**:
- [ ] `src/core/git_monitor.py` - GitMonitor类
- [ ] `src/core/brain_engine.py` - BrainEngine类（框架）
- [ ] `src/core/task_executor.py` - TaskExecutor类（框架）
- [ ] `src/core/state_machine.py` - StateMachine类
- [ ] `src/cli/agent.py` - Agent主类（框架）
- [ ] 基础单元测试（覆盖率>80%）

**检查项**:
- [ ] GitMonitor能执行git fetch
- [ ] GitMonitor能识别新增提交
- [ ] StateMachine支持所有12个状态
- [ ] StateMachine支持状态转换
- [ ] BrainEngine能加载规则（空规则库）
- [ ] TaskExecutor能注册策略
- [ ] Agent能启动和停止
- [ ] 单元测试全部通过

**代码提交要求**:
```
feat(core): 实现GitMonitor类，支持远程变更检测
feat(core): 实现StateMachine类，支持状态转换
feat(core): 实现BrainEngine框架，支持规则加载
feat(cli): 实现Agent主类框架
test(core): GitMonitor单元测试
test(core): StateMachine单元测试
```

#### M2: 状态机完成（第3-4天）

**目标**: 状态转换正常执行，无死锁

**交付物**:
- [ ] 完整状态转换逻辑（11个转换规则）
- [ ] 状态持久化（StateManager增强）
- [ ] 状态冲突检测（乐观锁）
- [ ] 状态历史记录
- [ ] 集成测试（状态转换场景）

**检查项**:
- [ ] 支持所有状态转换：project_init → requirements_draft → requirements_review → requirements_approved → design_draft → design_review → design_approved → development → testing → deployment → completed
- [ ] 状态文件正确读写
- [ ] 乐观锁防止并发写入
- [ ] 状态历史可追溯
- [ ] 集成测试覆盖所有状态转换

**代码提交要求**:
```
feat(core): 实现完整状态转换逻辑
feat(core): 实现状态持久化和冲突检测
test(core): 状态转换集成测试
```

#### M3: 行为规则完成（第5-6天）

**目标**: Agent 1/2行为规则全部实现

**交付物**:
- [ ] Agent 1行为规则（5个）
  - [ ] create_requirements
  - [ ] signoff_requirements
  - [ ] review_design
  - [ ] execute_blackbox_test
  - [ ] execute_deployment
- [ ] Agent 2行为规则（5个）
  - [ ] review_requirements
  - [ ] signoff_requirements
  - [ ] create_design
  - [ ] implement_code
  - [ ] fix_bugs
- [ ] 任务执行策略（8个）
- [ ] Agent行为集成测试

**检查项**:
- [ ] Agent 1能自动创建需求文档
- [ ] Agent 2能自动评审需求
- [ ] Agent 1能自动签署需求
- [ ] Agent 2能自动创建设计文档
- [ ] Agent 1能自动评审设计
- [ ] Agent 2能自动开发代码
- [ ] Agent 1能自动执行黑盒测试
- [ ] Agent 2能自动修复Bug
- [ ] Agent 1能自动部署
- [ ] 集成测试覆盖Agent协作场景

**代码提交要求**:
```
feat(rules): 实现Agent 1行为规则
feat(rules): 实现Agent 2行为规则
feat(strategy): 实现任务执行策略
test(rules): Agent行为集成测试
```

#### M4: 文档生成完成（第7天）

**目标**: 文档生成和检查正常

**交付物**:
- [ ] DocGenerator类
- [ ] QualityChecker类
- [ ] 模板文件
  - [ ] requirements_TEMPLATE.md
  - [ ] design_TEMPLATE.md
  - [ ] test_case_TEMPLATE.md
  - [ ] bug_report_TEMPLATE.md
  - [ ] test_report_TEMPLATE.md
  - [ ] deployment_report_TEMPLATE.md
- [ ] 文档生成测试

**检查项**:
- [ ] 能生成需求文档
- [ ] 能生成设计文档
- [ ] 能生成测试用例
- [ ] 能生成Bug报告
- [ ] 能生成测试报告
- [ ] 能生成部署报告
- [ ] 质量检查功能正常
- [ ] 重试机制正常（质量检查不通过时）

**代码提交要求**:
```
feat(core): 实现DocGenerator类
feat(core): 实现QualityChecker类
docs(templates): 添加文档模板文件
test(core): 文档生成测试
```

#### M5: 异常处理完成（第8天）

**目标**: 异常处理和恢复机制正常

**交付物**:
- [ ] ExceptionHandler类
- [ ] 异常分类体系
- [ ] 现场保存机制
- [ ] 恢复机制
- [ ] 通知机制
- [ ] 异常处理测试

**检查项**:
- [ ] 能处理Git冲突
- [ ] 能处理状态文件损坏
- [ ] 能处理网络中断
- [ ] 能处理权限不足
- [ ] 能处理超时
- [ ] 现场保存正常
- [ ] 恢复机制正常
- [ ] 通知发送正常

**代码提交要求**:
```
feat(core): 实现异常处理机制
feat(core): 实现现场保存和恢复
test(core): 异常处理测试
```

#### M6: 发布上线（第9-10天）

**目标**: 全流程测试通过，部署验证通过

**交付物**:
- [ ] 完整CLI命令
  - [ ] oc-collab auto
  - [ ] oc-collab todo
  - [ ] oc-collab work
- [ ] 配置文件
- [ ] 用户手册
- [ ] 全流程测试
- [ ] CI/CD配置

**检查项**:
- [ ] CLI命令可正常执行
- [ ] 77个黑盒测试用例全部通过
- [ ] 单元测试覆盖率>90%
- [ ] 集成测试全部通过
- [ ] 端到端测试通过
- [ ] 文档完整
- [ ] CI/CD正常运作

**代码提交要求**```
feat(cli): 实现oc-collab auto命令
feat(cli): 实现oc-collab todo命令
feat(cli): 实现oc-collab work命令
chore(ci): 配置CI/CD流程
test(e2e): 端到端测试
chore(release): 版本发布
```

## 3. 开发规范

### 3.1 代码规范
- 遵循PEP 8风格指南
- 使用类型注解
- 文档字符串完整
- 单元测试覆盖所有公开方法

### 3.2 Git提交规范
- 遵循Conventional Commits格式
- 每个功能一个提交
- 提交信息包含任务类型、范围和描述
- 示例: `feat(core): 实现GitMonitor类`

### 3.3 测试要求
- 单元测试覆盖率>80%（每个里程碑）
- 90%（最终发布）
- 集成测试覆盖主要场景
- 端到端测试覆盖完整流程

## 4. 进度跟踪

### 4.1 每日检查

| 日期 | 完成工作 | 遇到问题 | 第二天计划 |
|------|---------|---------|----------|
| | | | |

### 4.2 里程碑检查

| 里程碑 | 计划日期 | 实际日期 | 检查结果 |
|-------|---------|---------|---------|
| M1: 框架就绪 | 第1-2天 | 2026-01-31 | ✅ 通过 |
| M2: 状态机完成 | 第3-4天 | 2026-01-31 | ✅ 通过 |
| M3: 行为规则完成 | 第5-6天 | 2026-01-31 | ✅ 通过 |
| M4: 文档生成完成 | 第7天 | | 待开始 |
| M5: 异常处理完成 | 第8天 | | 待开始 |
| M6: 发布上线 | 第9-10天 | | 待开始 |

## 5. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|-----|:------:|:----:|---------|
| 技术难题 | 中 | 中 | 及时沟通，寻求支持 |
| 进度延迟 | 中 | 中 | 优先核心功能，非核心可延后 |
| 测试失败 | 中 | 中 | 及早测试，及早修复 |
| Git冲突 | 低 | 低 | 及时pull，小步提交 |

## 6. 签署确认

- **产品经理**: Agent 1  日期: 2026-01-31
- **开发**: Agent 2  日期: 2026-01-31

**计划状态**: M1阶段已完成

---

**下一步**:
1. ✅ M1阶段完成（框架就绪）
2. ⏳ 开始M2阶段开发（状态机完成）
3. Agent 1继续准备测试环境
