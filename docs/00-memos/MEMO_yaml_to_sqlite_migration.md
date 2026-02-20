# TODO 存储从 YAML 迁移到 SQLite - 改造完成

## 状态：✅ 已完成

## 修改的模块

| 模块 | 文件 | 状态 |
|------|------|------|
| TodoQueueManager | `src/core/todo_queue_manager.py` | ✅ 已改用 SQLite |
| SessionManager | `src/core/session_manager.py` | ✅ 已改用 SQLite |
| ConflictDetector | `src/core/conflict_detector.py` | ✅ 已改用 SQLite |
| ContextCarrier | `src/core/context_carrier.py` | ✅ 已改用 SQLite |
| TodoSyncManager | `src/core/todo_sync_manager.py` | ✅ 之前已改用 SQLite |

## 删除的文件

- `state/agent_adhoc_todos.yaml` - ✅ 已删除

## 测试结果

- V231 (16个): 全部通过
- V232 (18个): 15通过，3失败（与迁移无关）
- CLI回归 (70个): 63通过，3失败（agent listen超时、signoff skill），4跳过

## 剩余问题

失败的测试与 SQLite 迁移无关：
- `agent listen` 超时 - 测试设计问题
- `signoff` - Skill 未加载问题
