# YAML引用分析对比报告（Agent1梳理）

> 对照Agent2报告：docs/07-research/RESEARCH_YAML_REFERENCE_ANALYSIS.md

---

## 一、Agent2报告遗漏的问题

### 1. src/core/todo_queue_manager.py 被多处引用

| 文件 | 引用次数 | 问题 |
|------|----------|------|
| todo_commands.py | 5次 | 仍在使用废弃的TodoQueueManager |
| enhanced_commands.py | 1次 | 导入但可能未实际使用 |
| agent_commands.py | 1次 | 导入但可能未实际使用 |
| check_todo_on_startup.py | 1次 | 启动时检查旧队列 |
| notify_commands.py | 1次 | 通知中使用旧队列 |
| startup_commands.py | 2次 | 启动命令中使用旧队列 |
| agent_startup_checker.py | 1次 | Agent启动检查 |
| state_notifier.py | 1次 | 状态通知中使用 |

**问题**: v2.3.3已迁移到SQLite，但这些CLI命令仍在导入/调用废弃的TodoQueueManager

### 2. src/core/state_queue.py 废弃但未移除

- 文件仍存在: `state/state_queue.json`
- `state_commands.py` 仍在导入StateQueueManager

### 3. 更新的YAML文件清单

| 文件 | 状态 | 说明 |
|------|------|------|
| `agent_adhoc_todos.yaml` | ⚠️ 废弃 | 31处引用 |
| `todo_queue.yaml` | ⚠️ 废弃 | 17处引用 |
| `todo.yaml` | ⚠️ 废弃 | 1处引用 |
| `state_queue.yaml` | ⚠️ 废弃 | 1处引用 |
| `project_state.yaml` | ✅ 正常使用 | 项目状态 |
| `agent.identity` | ✅ 正常使用 | Agent身份 |
| `notification.yaml` | ✅ 正常使用 | 通知配置 |
| `skill_index.yaml` | ✅ 正常使用 | Skill索引 |
| `webhook.yaml` | ✅ 正常使用 | Webhook配置 |
| `config/*.yaml` | ✅ 正常使用 | 各类配置 |

---

## 二、核心问题总结

### 问题1: TodoQueueManager是废弃代码

v2.3.3已用SQLite替换YAML存储，但:
- 23处代码仍在导入TodoQueueManager
- 每次CLI启动都会初始化废弃的队列管理器
- 导致不必要的错误和警告

### 问题2: 废弃的YAML文件仍被检查

- `agent_startup_checker.py` 启动时检查 `todo_queue.yaml`
- `check_todo_on_startup.py` 检查旧队列
- 导致启动警告和错误

### 问题3: 测试用例大量跳过

- 很多测试因引用废弃YAML被标记skip
- 影响测试覆盖率

---

## 三、Agent1 vs Agent2 报告对比

| 类别 | Agent2报告 | Agent1补充 |
|------|-----------|-----------|
| src/引用 | 5处 | 23处（发现更多） |
| TodoQueueManager | 未强调 | 核心问题 |
| state_queue.py | 未提及 | 废弃但存在 |
| state_queue.json | - | 实际使用 |

---

## 四、建议改造方案

### 方案: 分阶段清理

#### Phase 1: 立即修复（高优先级）

1. **移除废弃YAML引用**
   - 从所有CLI命令中移除 `from todo_queue_manager import`
   - 替换为直接使用SQLite的todo_storage

2. **修复启动检查**
   - `agent_startup_checker.py` 不再检查 `todo_queue.yaml`
   - `check_todo_on_startup.py` 改为检查SQLite

3. **清理测试**
   - 恢复被skip的测试用例
   - 或标记为明确的废弃测试

#### Phase 2: 中期清理（中优先级）

1. **更新Skill文档**
   - 移除skill中对旧YAML的引用
   - 更新为SQLite存储说明

2. **更新用户文档**
   - 更新README和指南
   - 说明新的CLI用法

#### Phase 3: 长期清理（低优先级）

1. **移除废弃模块**
   - 删除 `todo_queue_manager.py`
   - 删除 `state_queue.py`
   - 清理备份文件

---

## 五、具体修复清单

### 高优先级（必须修复）

| 序号 | 文件 | 问题 | 修复方式 |
|------|------|------|----------|
| 1 | todo_commands.py | 导入废弃模块 | 移除导入，使用SQLite |
| 2 | enhanced_commands.py | 导入废弃模块 | 移除导入 |
| 3 | check_todo_on_startup.py | 检查废弃YAML | 改为检查SQLite |
| 4 | agent_startup_checker.py | 检查废弃YAML | 移除检查 |

### 中优先级

| 序号 | 文件 | 问题 | 修复方式 |
|------|------|------|----------|
| 5 | notify_commands.py | 导入废弃模块 | 移除导入 |
| 6 | startup_commands.py | 导入废弃模块 | 移除导入 |
| 7 | agent_commands.py | 导入废弃模块 | 移除导入 |

### 低优先级

| 序号 | 文件 | 问题 | 修复方式 |
|------|------|------|----------|
| 8 | Skills文档 | 引用旧YAML | 更新文档 |
| 9 | 测试用例 | 被skip | 恢复或标记 |

---

**报告人**: Agent1  
**日期**: 2026-02-20
