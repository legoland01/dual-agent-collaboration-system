# CHANGELOG - oc-collab 双Agent协作框架

## v2.2.7 (2026-02-10)

### 新增功能

| 功能ID | 功能描述 | 来源 |
|--------|----------|------|
| F-TEST-001 | Skill内容准确性测试 | requirements_v2.2.7.md |
| F-TEST-002 | Skill覆盖率统计 | requirements_v2.2.7.md |
| F-WEB-001 | Webhook配置管理 | requirements_v2.2.7.md |
| F-WEB-002 | 事件监听与崩溃恢复 | requirements_v2.2.7.md |

### 新增模块

| 模块 | 文件 | 功能 |
|------|------|------|
| SkillTester | src/core/skill_tester.py | Skill内容准确性验证 |
| ReferenceValidator | src/core/reference_validator.py | 引用关系验证 |
| CLIActionValidator | src/core/cli_action_validator.py | CLI命令验证 |
| CoverageCalculator | src/core/coverage_calculator.py | 覆盖率统计 |
| WebhookConfig | src/core/webhook_config.py | Webhook配置管理 |
| EventListener | src/core/event_listener.py | 事件监听+崩溃恢复 |

### 新增CLI命令

| 命令 | 功能 |
|------|------|
| `oc-collab skill test [--skill <id>]` | Skill内容准确性测试 |
| `oc-collab skill coverage [--skill <id>]` | Skill覆盖率统计 |
| `oc-collab webhook init` | 初始化Webhook配置 |
| `oc-collab webhook status` | 显示Webhook状态 |
| `oc-collab webhook start [--port <port>]` | 启动Webhook监听服务 |
| `oc-collab webhook stop` | 停止Webhook监听服务 |

### 核心目标

**构建质量保障体系与外部通知基础设施**

- Skill测试覆盖率统计
- Webhook事件监听
- 崩溃恢复机制

### 测试结果

- 单元测试: 26/26 PASSED
- 黑盒测试: 7/9 PASSED (2个跳过)

---

## v2.2.6 (2026-02-09)

### 新增功能

| 功能ID | 功能描述 | 来源 |
|--------|----------|------|
| F-AI-001 | todowrite参数自动检查 | requirements_v2.2.6.md |
| F-AI-002 | TODO上下文携带 | requirements_v2.2.6.md |
| F-AI-003 | 冲突检测 | requirements_v2.2.6.md |
| F-SKILL-001 | Skill关键词检索 | requirements_v2.2.6.md |
| F-SKILL-002 | Skill切片机制 | requirements_v2.2.6.md |
| F-SKILL-003 | Skill强制查找增强 | requirements_v2.2.6.md |

### 新增模块

| 模块 | 文件 | 功能 |
|------|------|------|
| AutoChecker | src/core/auto_checker.py | todowrite参数自动检查 |
| ContextCarrier | src/core/context_carrier.py | TODO上下文携带 |
| ConflictDetector | src/core/conflict_detector.py | 冲突检测 |
| SkillSearcher | src/core/skill_searcher.py | Skill关键词检索 |
| SkillSlicer | src/core/skill_slicer.py | Skill切片机制 |

### 新增CLI命令

| 命令 | 功能 |
|------|------|
| `oc-collab todowrite --auto-check` | 自动检查参数并携带上下文 |
| `oc-collab skill search --keywords <kw>` | 搜索Skill文档 |
| `oc-collab skill slice <skill>` | 查看Skill特定切片 |
| `oc-collab skill enforce` | Skill强制查找机制 |

### 核心目标

**解决Agent"找不到、看不懂、记不住"Skill的问题**

---

## v2.2.5 (2026-02-09)

### 新增功能

| 功能ID | 功能描述 | 来源 |
|--------|----------|------|
| FR-SKILL-001 | Skill强制加载检查 | requirements_v2.2.4.md |
| FR-GIT-002 | Git提交前签署验证 | requirements_v2.2.4.md |
| FR-AUTO-001 | 需求文档完整性检查 | requirements_v2.2.4.md |
| FR-AUTO-002 | 阶段推进门槛检查 | requirements_v2.2.4.md |

### 新增模块

| 模块 | 文件 | 功能 |
|------|------|------|
| SkillEnforcer | src/core/skill_enforcer.py | 强制检查Skill加载 |
| SignoffEnforcer | src/core/signoff_enforcer.py | Git提交前签署验证 |
| RequirementsChecker | src/core/requirements_checker.py | 需求文档完整性检查 |
| PhaseAdvance | src/core/phase_advance.py | 阶段推进门槛检查 |

### 新增CLI命令

| 命令 | 功能 |
|------|------|
| `oc-collab skill check` | 检查Skill加载状态 |
| `oc-collab check requirements` | 检查需求文档完整性 |
| `oc-collab check completeness` | 简要完整性检查 |

### Bug修复

| Bug ID | 描述 | 状态 |
|--------|------|------|
| BUG-20260208-003 | SessionManager识别v2.2.x项目结构 | ✅ 已修复 |
| BUG-20260208-004 | signoff.py不支持v2.2.x结构 | ✅ 已修复 |
| BUG-20260208-005 | todowrite无法可靠创建TODO | ✅ 非Bug（误报） |
| BUG-20260208-006 | signoff.py字段名'test'不匹配v2.2.4的'testing' | ✅ 已修复 |
| BUG-20260208-008 | 角色边界检查在工具层未生效 | ✅ 临时方案（脚本辅助） |

### 改进

- Skill更新：TODO标注"已修复"规范
- Skill更新：任务交接检查清单
- Skill更新：Agent Bug处理权限划分

### 测试

- 新增单元测试：34 tests passed
- 新增E2E测试：5 tests passed
- 测试覆盖率：85%

---

## v2.2.5 (2026-02-09)

### 新增功能

| 功能ID | 功能描述 | 来源 |
|--------|----------|------|
| FR-OWNER-001 | 文件Owner机制 | requirements_v2.2.5.md |
| FR-STATE-001 | 状态识别修复 | requirements_v2.2.5.md |
| FR-SIGN-001 | signoff修复 | requirements_v2.2.5.md |
| FR-PROC-001 | 版本结束后需求分析流程 | requirements_v2.2.5.md |
| FR-PROC-002 | 评审机制优化 | requirements_v2.2.5.md |

### Bug修复

| Bug ID | 描述 | 状态 |
|--------|------|------|
| BUG-20260208-003 | SessionManager识别v2.2.x项目结构 | ✅ 已修复 |
| BUG-20260208-004 | signoff.py不支持v2.2.x结构 | ✅ 已修复 |
| BUG-20260208-006 | signoff.py字段名不匹配 | ✅ 已修复 |

### 改进

- Skill更新：文件Owner管理机制
- Skill更新：状态识别与修复流程
- Skill更新：signoff修复规范

---

## v2.2.3 (2026-02-08)

### 新增功能

| 功能ID | 功能描述 |
|--------|----------|
| F-CONTEXT-001 | .a文件机制 |
| F-TASK-001 | 任务状态同步 |
| F-UI-001 | 状态增强显示 |

### Bug修复

| Bug ID | 描述 |
|--------|------|
| BUG-20260208-001 | v2.2.3 CLI命令未完全实现 |
| BUG-20260208-002 | TODO任务不同步问题 |

---

## v2.2.2 (2026-02-08)

### 新增功能

- 合规检查引擎 (F-PROC-001)
- 角色边界检查 (F-PROC-001.1)
- 状态追踪机制 (F-PROC-002)

---

## v2.2.1 (2026-02-07)

### 改进

- 完善signoff签署流程
- 优化CLI命令输出

---

## v2.2.0 (2026-02-07)

### 重大变更

- 双Agent协作框架初始版本
- Agent 1: 产品经理职责
- Agent 2: 开发负责人职责
- 四阶段流程：requirements → design → development → testing → deployment

---

## 版本规则

```
主版本.次版本.修订版本

主版本（Major）：不兼容的 API 变更
次版本（Minor）：新增功能（向后兼容）
修订版本（Patch）：Bug 修复（向后兼容）
```

---

**更新日期**: 2026-02-08
