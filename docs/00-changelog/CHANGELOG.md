# CHANGELOG - oc-collab 双Agent协作框架

## v2.2.4 (2026-02-08)

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
