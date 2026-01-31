# 文档与代码变更追踪系统

## 目的

建立完整的文档-代码关联追踪，确保每次代码变更后所有相关文档同步更新。

## 文档分类

| 类别 | 目录 | 说明 | 更新频率 |
|------|------|------|---------|
| 需求文档 | `docs/01-requirements/` | 功能需求、设计要求 | 重大功能变更时 |
| 设计文档 | `docs/02-design/` | 详细设计、评审记录 | 架构变更时 |
| 测试文档 | `docs/03-test/` | 测试用例、执行结果 | 每次功能变更 |
| 变更记录 | `docs/04-changelog/` | 版本变更历史 | 每次代码变更 |
| 开发文档 | `docs/05-development/` | 里程碑验收标准 | 里程碑变更时 |
| 经验文档 | `docs/06-experience/` | 问题修复经验 | 每次bug修复 |
| 指南手册 | `docs/*.md` | 使用指南、协作流程 | 必要时 |

## 功能模块与文档映射

### CLI 基础功能 (`src/cli/main.py`)

| 功能 | 需求文档 | 设计文档 | 测试用例 | 使用手册 |
|------|----------|----------|----------|----------|
| init | requirements_cli_*.md | detailed_design_cli_*.md | test_e2e.py | 使用手册.md |
| status | - | - | test_e2e.py | 使用手册.md |
| switch | requirements_cli_*.md | - | test_e2e.py | 使用手册.md |
| review | requirements_*.md | design_review_*.md | test_e2e.py | 使用手册.md |
| signoff | requirements_*.md | - | test_e2e.py | 使用手册.md |
| sync | requirements_*.md | - | test_e2e.py | 使用手册.md |
| history | - | - | test_e2e.py | 使用手册.md |
| auto | requirements_fully_automated_*.md | detailed_design_fully_automated_*.md | test_e2e.py | 使用手册.md |
| todo | requirements_fully_automated_*.md | - | test_e2e.py | 使用手册.md |
| work | requirements_fully_automated_*.md | - | test_e2e.py | 使用手册.md |
| **remote** | requirements_cli_improvement_*.md | detailed_design_cli_improvement_*.md | test_e2e.py | 使用手册.md |
| **sync-all** | requirements_cli_improvement_*.md | detailed_design_cli_improvement_*.md | test_e2e.py | 使用手册.md |

### 核心模块 (`src/core/`)

| 模块 | 关联文档 | 测试文件 |
|------|----------|----------|
| state_manager.py | requirements_v*.md, detailed_design_*.md | test_state_manager*.py |
| git.py | requirements_*.md | test_e2e.py |
| git_monitor.py | requirements_fully_automated_*.md | test_git_monitor.py |
| workflow.py | requirements_*.md, design_review_*.md | test_workflow.py |
| auto_engine.py | requirements_fully_automated_*.md | test_e2e.py |
| detector.py | requirements_*.md | test_detector.py |

## 代码变更检查清单

每次代码变更后，必须检查以下项目：

### 必查项

- [ ] **变更记录** (`docs/04-changelog/change_log.md`)
  - 添加新条目：功能/修复/改进
  - 更新版本号

- [ ] **使用手册** (`docs/使用手册.md`)
  - 新增命令的使用说明
  - 更新命令参数示例

- [ ] **端到端测试** (`tests/test_e2e.py`)
  - 添加新功能的测试用例
  - 验证现有测试通过

### 条件检查项

| 变更类型 | 需要检查的文档 |
|----------|----------------|
| 新增 CLI 命令 | 需求文档、设计文档、测试用例、使用手册 |
| 修改 CLI 参数 | 使用手册、测试用例 |
| 新增核心模块 | 需求文档、设计文档、测试用例 |
| 修改业务流程 | 需求文档、设计文档、评审记录 |
| Bug 修复 | 经验文档、测试用例 |
| 性能优化 | 设计文档（可能需要更新） |

## 变更追踪模板

### 提交信息规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

Type 类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `test`: 测试更新
- `refactor`: 重构
- `chore`: 构建/工具

### 变更日志条目模板

```markdown
## [版本号] - YYYY-MM-DD

### 新功能
- 新增 `remote` 命令，支持多远程仓库管理 (#IssueID)
- 新增 `sync-all` 命令，一键同步到所有平台 (#IssueID)

### 改进
- `status` 命令增加配置文件兼容性处理 (#IssueID)

### 测试
- 新增 `test_remote_command` 端到端测试 (#IssueID)
```

## 文档更新流程

### 步骤 1：识别变更范围

```bash
# 查看变更文件
git diff --name-only HEAD~1

# 识别影响的功能
cat << EOF
变更文件分析：
- src/cli/*.py → 影响 CLI 命令
- src/core/*.py → 影响核心模块
- docs/*.md → 文档更新
EOF
```

### 步骤 2：更新变更记录

```bash
# 编辑 change_log.md
edit docs/04-changelog/change_log.md
```

### 步骤 3：更新测试用例

```bash
# 检查是否需要新增测试
grep -l "remote\|sync-all" tests/test_e2e.py || echo "需要添加测试"

# 新增测试用例
edit tests/test_e2e.py
```

### 步骤 4：更新使用手册

```bash
# 检查命令帮助信息
oc-collab remote --help
oc-collab sync-all --help

# 更新使用手册
edit docs/使用手册.md
```

### 步骤 5：更新需求/设计文档（重大变更）

```bash
# 新功能需要更新
ls docs/01-requirements/requirements_cli_improvement*.md
ls docs/02-design/detailed_design_cli_improvement*.md
```

## 当前代码变更清单

### 新增功能：多远程仓库管理

**代码变更文件：**
- `src/cli/main.py` - 新增 `remote`, `sync-all` 命令
- `src/core/git.py` - 新增 `push_all_remotes`, `get_all_remotes`, `add_remote`, `push_to_remote` 方法

**需要更新的文档：**

| 文档 | 状态 | 优先级 |
|------|------|--------|
| `docs/04-changelog/change_log.md` | 待更新 | P0 |
| `docs/使用手册.md` | 待更新 | P0 |
| `tests/test_e2e.py` | 待更新 | P0 |
| `docs/01-requirements/requirements_cli_improvement_v1.md` | 建议更新 | P1 |
| `docs/02-design/detailed_design_cli_improvement_v1.md` | 建议更新 | P1 |
| `docs/03-test/test_case_blackbox_*.md` | 建议更新 | P2 |

---

## 使用说明

本文件用于追踪代码与文档的对应关系。

**使用方法：**
1. 代码变更后，打开本文件
2. 找到对应的模块和功能
3. 按照"代码变更检查清单"逐项检查
4. 更新完成后在下方打勾确认

## 最后更新

2026-01-31
