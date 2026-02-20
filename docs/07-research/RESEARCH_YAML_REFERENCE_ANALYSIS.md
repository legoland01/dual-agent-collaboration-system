# oc-collab YAML文件引用完整梳理报告

> 生成日期: 2026-02-20  
> 用途: v2.3.3 SQLite迁移后的文档更新指南

---

## 摘要

本报告完整梳理了oc-collab系统中所有引用旧YAML文件（`agent_adhoc_todos.yaml`, `todo_queue.yaml`, `todo.yaml`, `state_queue.yaml`）的代码、测试和文档。

| YAML文件 | src/ | skills/ | tests/ | 总计 |
|----------|------|---------|--------|------|
| `agent_adhoc_todos.yaml` | 5 | 9 | 17 | 31 |
| `todo_queue.yaml` | 1 | 4 | 12 | 17 |
| `todo.yaml` | 0 | 0 | 1 | 1 |
| `state_queue.yaml` | 0 | 1 | 0 | 1 |

---

## 1. 核心模块引用 (src/)

### 1.1 migrate_commands.py
**路径**: `src/cli/migrate_commands.py`

| 行号 | 引用的YAML文件 | CLI指令 | 用途 |
|------|----------------|---------|------|
| 28 | `state/agent_adhoc_todos.yaml` | `oc-collab migrate to_sqlite` | 旧项目迁移路径 |
| 54 | `state/agent_adhoc_todos.yaml` | `oc-collab migrate preview` | 预览迁移结果 |
| 106 | `state/agent_adhoc_todos.yaml` | `oc-collab migrate status` | 查看迁移状态 |

### 1.2 data_migration.py
**路径**: `src/core/data_migration.py`

| 行号 | 引用的YAML文件 | 方法 | 用途 |
|------|----------------|------|------|
| 97 | `agent_adhoc_todos_{timestamp}.yaml` | `migrate()` | 备份文件名 |
| 112 | `state/agent_adhoc_todos.yaml` | `migrate()` | 错误提示 |
| 161 | `state/agent_adhoc_todos.yaml` | `preview()` | 错误提示 |
| 205 | `agent_adhoc_todos_*.yaml` | `list_backups()` | 备份文件匹配 |

### 1.3 agent_startup_checker.py
**路径**: `src/core/agent_startup_checker.py`

| 行号 | 引用的YAML文件 | 用途 |
|------|----------------|------|
| 4 | `todo_queue.yaml` | 文档注释（启动检查功能说明） |

---

## 2. Skill引用 (skills/)

### 2.1 oc_collab_todo_dependency_check
**路径**: `skills/oc_collab_todo_dependency_check/`

| 文件 | 行号 | 引用的YAML文件 | 用途 |
|------|------|----------------|------|
| skill.json | 44 | `agent_adhoc_todos.yaml` | required声明 |
| content.md | 39 | `state/agent_adhoc_todos.yaml` | 读取TODO数据 |
| content.md | 300 | `state/agent_adhoc_todos.yaml` | 数据源说明 |

**关联CLI指令**: `oc-collab todo-dep-check`

### 2.2 oc_collab_collaboration_guide
**路径**: `skills/oc_collab_collaboration_guide/`

| 文件 | 行号 | 引用的YAML文件 | 用途 |
|------|------|----------------|------|
| skill.json | 144 | `state/agent_adhoc_todos.yaml` | artifacts声明 |
| content.md | 601 | `state/agent_adhoc_todos.yaml` | 手动编辑场景 |
| content.md | 612-613 | `state/agent_adhoc_todos.yaml` | git add说明 |
| content.md | 692 | `state/agent_adhoc_todos.yaml` | 检查待办任务 |

**关联CLI指令**: `oc-collab collab-guide`

### 2.3 oc_collab_issue_tracker
**路径**: `skills/oc_collab_issue_tracker/`

| 文件 | 行号 | 引用的YAML文件 | 用途 |
|------|------|----------------|------|
| content.md | 96 | `state/agent_adhoc_todos.yaml` | TODO存储位置 |
| content.md | 314 | `state/agent_adhoc_todos.yaml` | BUG模板 |
| content.md | 352 | `agent_adhoc_todos.yaml` | 与YAML关系 |

**关联CLI指令**: `oc-collab issue-track`

### 2.4 oc_collab_bug_management_guide
**路径**: `skills/oc_collab_bug_management_guide/`

| 文件 | 行号 | 引用的YAML文件 | 用途 |
|------|------|----------------|------|
| content.md | 334 | `state/agent_adhoc_todos.yaml` | git add命令 |

**关联CLI指令**: `oc-collab bug-guide`

### 2.5 oc_collab_detailed_design_guide
**路径**: `skills/oc_collab_detailed_design_guide/`

| 文件 | 行号 | 引用的YAML文件 | 用途 |
|------|------|----------------|------|
| content.md | 158 | `state/todo_queue.yaml` | TODO队列设计 |
| content.md | 177 | `todo_queue.yaml` | TODO创建流程 |
| content.md | 179 | `todo_queue.yaml` | StateReceiver同步 |

**关联CLI指令**: `oc-collab design-guide`

### 2.6 oc_collab_test_acceptance_guide
**路径**: `skills/oc_collab_test_acceptance_guide/`

| 文件 | 行号 | 引用的YAML文件 | 用途 |
|------|------|----------------|------|
| content.md | 502 | `state/state_queue.json`, `state/todo_queue.yaml` | 队列独立问题 |

**关联CLI指令**: `oc-collab test-guide`

---

## 3. 测试用例 (tests/)

### 3.1 test_v232_e2e.py
**路径**: `tests/test_v232_e2e.py`

| 行号 | 测试用例 | 引用的YAML文件 | 状态 |
|------|----------|----------------|------|
| 68 | setup | `state/agent_adhoc_todos.yaml` | 正常 |
| 576 | 迁移相关 | `state/agent_adhoc_todos.yaml` | 正常 |
| 828 | 迁移相关 | `state/agent_adhoc_todos.yaml` | 正常 |
| 851 | 迁移相关 | `state/agent_adhoc_todos.yaml` | 正常 |

### 3.2 test_state_sync.py
**路径**: `tests/test_state_sync.py`

| 行号 | 测试用例 | 引用的YAML文件 | 状态 |
|------|----------|----------------|------|
| 44 | mock_todo_queue_file | `todo_queue.yaml` | 已跳过 |
| 95 | test_tc_sync_002 | `todo_queue.yaml` | **已标记skip** |
| 116 | test_tc_sync_003 | `todo_queue.yaml` | **已标记skip** |
| 173 | test_tc_sync_004 | `todo_queue.yaml` | **已标记skip** |

### 3.3 test_bug_20260210_001_skill_enforce_cli.py
**路径**: `tests/test_bug_20260210_001_skill_enforce_cli.py`

| 行号 | 测试用例 | 引用的YAML文件 | 状态 |
|------|----------|----------------|------|
| 150 | test_todo_updated | `state/agent_adhoc_todos.yaml` | **已标记skip** |

### 3.4 test_session_manager.py
**路径**: `tests/test_session_manager.py`

| 行号 | 测试用例 | 引用的YAML文件 | 状态 |
|------|----------|----------------|------|
| 224 | test_get_todo_items_reads_adhoc_yaml | `agent_adhoc_todos.yaml` | **已标记skip** |
| 255 | test_get_todo_items_adhoc_only_pending | `state/agent_adhoc_todos.yaml` | **已标记skip** |
| 299 | test_auto_discover_tasks_no_duplicate | `state/agent_adhoc_todos.yaml` | **已标记skip** |

### 3.5 test_v2_2_3.py
**路径**: `tests/test_v2_2_3.py`

| 行号 | 测试用例 | 引用的YAML文件 | 状态 |
|------|----------|----------------|------|
| 397-400 | test_load_empty_todo_yaml | `todo.yaml` | 正常 |

### 3.6 test_v2_3_2_modules.py
**路径**: `tests/test_v2_3_2_modules.py`

| 行号 | 测试用例 | 引用的YAML文件 | 状态 |
|------|----------|----------------|------|
| 555 | 迁移测试 | `state/agent_adhoc_todos.yaml` | 正常 |

### 3.7 test_session_manager_v2.py
**路径**: `tests/test_session_manager_v2.py`

| 行号 | 测试用例 | 引用的YAML文件 | 状态 |
|------|----------|----------------|------|
| 176 | 说明 | `state/agent_adhoc_todos.yaml` | 正常 |
| 192 | 备份 | `state/agent_adhoc_todos.yaml` | 正常 |
| 212 | git status | `state/agent_adhoc_todos.yaml` | 正常 |
| 221 | 读取 | `state/agent_adhoc_todos.yaml` | 正常 |
| 231 | 恢复 | `state/agent_adhoc_todos.yaml` | 正常 |

### 3.8 test_state_notifier_e2e.py
**路径**: `tests/test_state_notifier_e2e.py`

| 行号 | 测试用例 | 引用的YAML文件 | 状态 |
|------|----------|----------------|------|
| 245 | 说明注释 | `todo_queue.yaml` | 正常 |
| 261 | 队列路径 | `todo_queue.yaml` | 正常 |
| 317 | 队列路径 | `todo_queue.yaml` | 正常 |
| 386 | 队列路径 | `todo_queue.yaml` | 正常 |
| 426 | 队列路径 | `todo_queue.yaml` | 正常 |

---

## 4. 文档引用 (docs/)

### 4.1 需求文档 (docs/01-requirements/)
- requirements_v2.3.2.md
- CORE_ARCHITECTURE.md

### 4.2 设计文档 (docs/02-design/)
- DETAIL_v2.3.2.md (多处引用)
- DETAIL_v2.3.1.md
- DETAIL_pm_agent.md
- OUTLINE_pm_agent.md

### 4.3 备忘录 (docs/00-memos/)
- BUG-20260219-001.md
- BUG-20260219-002.md
- BUG-20260215-015.md
- BUG-20260215-017.md
- MEMO_yaml_to_sqlite_migration.md
- ACCEPTANCE_v2.3.2_SQLite_Migration.md

### 4.4 路线图 (docs/06-roadmap/)
- ROADMAP_oc-collab.md

### 4.5 研究文档 (docs/07-research/)
- RESEARCH_Multi_Project_Collaboration.md
- RESEARCH_20260216_skill_slice_analysis.md

---

## 5. 需更新的内容汇总

### 5.1 必须更新相关）
| 类别 | 文件（功能 | 优先级 |
|------|------|--------|
| Skill | oc_collab_todo_dependency_check | **高** |
| Skill | oc_collab_collaboration_guide | **高** |
| Skill | oc_collab_issue_tracker | **高** |
| Skill | oc_collab_bug_management_guide | **中** |
| Skill | oc_collab_detailed_design_guide | **中** |
| Skill | oc_collab_test_acceptance_guide | **低** |

### 5.2 建议更新（文档相关）
| 类别 | 文件 | 优先级 |
|------|------|--------|
| 文档 | docs/01-requirements/* | **中** |
| 文档 | docs/02-design/* | **中** |
| 文档 | docs/00-memos/BUG-*.md | **低** |

### 5.3 保留兼容
| 文件 | 原因 |
|------|------|
| migrate_commands.py | 旧项目迁移引导 |
| data_migration.py | 旧项目迁移引导 |

---

## 6. 新的TODO存储机制

v2.3.3已迁移到SQLite，新的存储方式：

| 存储项 | 文件路径 | 类型 |
|--------|----------|------|
| TODO数据 | `state/todos.db` | SQLite |
| Agent身份 | `state/agent.identity` | YAML |
| 项目状态 | `state/project_state.yaml` | YAML |

**正确的CLI指令**：
- `oc-collab todo list` - 查看TODO
- `oc-collab todowrite` - 创建TODO
- `oc-collab todo complete` - 完成TODO
- `oc-collab switch` - 切换Agent身份

---

## 7. 附录：CLI指令对照表

### 7.1 TODO相关指令
| 旧指令 | 新指令 | 说明 |
|--------|--------|------|
| 读取YAML | `oc-collab todo list` | 查看TODO列表 |
| 手动编辑YAML | `oc-collab todowrite` | 创建TODO |

### 7.2 迁移相关指令
| 旧指令 | 新指令 | 说明 |
|--------|--------|------|
| - | `oc-collab migrate to_sqlite` | 迁移旧项目 |

---

**报告结束**
