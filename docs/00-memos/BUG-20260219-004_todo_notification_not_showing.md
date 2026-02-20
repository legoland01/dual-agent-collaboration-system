# BUG-20260219-004: TODO通知不显示

## 摘要
`agent listen` 命令无法检测到TODO，导致macOS通知不显示。

## 影响范围
- 所有使用 `oc-collab agent listen` 监听TODO通知的用户
- 影响M5（RetryWatcher）、M6（AutoTodoCreator）等依赖通知的功能

## 严重程度
- 优先级: P1（高）
- 分类: 功能缺陷

## 环境
- macOS
- Python 3.9.6
- oc-collab v2.3.3

## 重现步骤

1. Agent1 创建一个TODO给 Agent2
   ```bash
   oc-collab switch 1
   oc-collab todo add "测试通知" --to 2
   ```

2. 启动 Agent2 的监听
   ```bash
   oc-collab switch 2
   oc-collab agent listen --interval 5
   ```

3. 观察：没有收到macOS通知

## 问题根因

### 问题1: agent_id格式不匹配

`src/cli/agent_commands.py:233`
```python
todos = storage.list(receiver=agent_id, status='pending', unread_only=True)
```

`agent_id` 格式是 `"agent2"`（带前缀），但数据库存储时去掉了前缀，存的是 `"2"`。

数据库存储逻辑 (`todo_queue_manager.py:109-110`):
```python
'receiver': item.to_agent.replace('agent', '')  # "2" 去掉了前缀
```

查询时格式不匹配，导致找不到未读TODO。

### 问题2: TodoQueueManager.get_unread参数未处理

`src/core/todo_queue_manager.py:131`
```python
rows = storage.list(receiver=agent_id, status='pending')  # 传入 "agent2"
```

应该先去掉前缀再查询。

## 修复方案

### 修复1: agent_commands.py

```python
# 修复前
todos = storage.list(receiver=agent_id, status='pending', unread_only=True)

# 修复后
receiver = agent_id.replace('agent', '') if agent_id else None
todos = storage.list(receiver=receiver, status='pending', unread_only=True)
```

### 修复2: todo_queue_manager.py

```python
# 修复前
rows = storage.list(receiver=agent_id, status='pending')

# 修复后
receiver = agent_id.replace('agent', '') if agent_id else None
rows = storage.list(receiver=receiver, status='pending')
```

## 为什么测试没发现？

### 分析

1. **现有测试文件** (`tests/test_v2_3_3_e2e.py`, `tests/test_v2_3_3_e2e_full.py`)
   - 测试场景覆盖了TODO创建、签收、阶段推进等流程
   - 但没有测试 `agent listen` 命令的轮询功能

2. **测试覆盖缺口**
   - 没有针对 `agent_commands.py` 中 `poll_loop` 函数的单元测试
   - 没有测试 `TodoQueueManager.get_unread` 带 `agent_id` 参数的场景
   - 没有测试 `TodoStorage.list` 的 `receiver` 参数边界情况

3. **测试数据问题**
   - 测试中创建的TODO使用 `TodoQueueItem` 对象
   - `TodoQueueItem.from_dict` 会从todo_id解析agent（如 `TODO-1to2-001`）
   - 而实际使用中 `sender` 和 `receiver` 直接存储数字字符串
   - 测试数据格式与实际使用格式不一致

### 需要添加的测试

1. `test_agent_commands_listen.py` - 测试 `agent listen` 命令的轮询逻辑
2. `test_todo_queue_manager_get_unread.py` - 测试带agent_id参数的查询
3. `test_todo_storage_list_receiver.py` - 测试receiver参数的各种格式

## 修复验证

修复后测试通过：
```
✅ TODO创建成功
✅ 查询参数: agent_id=agent2, receiver=2
✅ 查询结果: 1个未读TODO
✅ macOS通知已发送!
```

## 相关文件

- `src/cli/agent_commands.py` - 命令行入口
- `src/core/todo_queue_manager.py` - TODO队列管理
- `src/core/todo_storage.py` - SQLite存储
- `src/core/agent_listener.py` - 监听服务

## 时间线

- 2026-02-19: 问题发现
- 2026-02-19: 修复完成
- 2026-02-19: 待测试用例补充

## 状态

- [x] 问题发现
- [x] 根因分析
- [x] 代码修复
- [ ] 测试用例补充
- [ ] 回归测试
