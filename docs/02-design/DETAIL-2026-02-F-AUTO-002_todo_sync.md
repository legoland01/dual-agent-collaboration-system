# 详细设计文档：F-AUTO-002 任务状态自动同步

**功能编号**: F-AUTO-002
**版本**: v1
**创建日期**: 2026-02-07
**作者**: Agent 1 (产品经理)
**状态**: DRAFT

---

## 1. 概述

### 1.1 功能描述

F-AUTO-002 实现 todowrite / todoedit 操作后自动同步到 `state/agent_adhoc_todos.yaml` 文件。

### 1.2 需求来源

v2.2.1 发布后发现 todowrite 只更新内存不持久化，导致跨会话任务丢失。

### 1.3 验收标准

- [ ] `todowrite` / `todoedit` 操作后自动同步到文件
- [ ] 同步时有明确提示（"✓ 已同步到文件"）
- [ ] 支持查看同步历史

---

## 2. 技术设计

### 2.1 当前实现分析

当前 `oc-collab todowrite` 命令：
- 更新内存中的 todo 列表
- 不自动写入文件
- 需要手动调用其他命令或直接编辑文件

### 2.2 修改范围

#### 2.2.1 修改的文件

| 文件 | 修改内容 |
|------|----------|
| `oc_collab/commands/todowrite.py` | 添加文件同步逻辑 |
| `oc_collab/commands/todoedit.py` | 添加文件同步逻辑 |
| `oc_collab/state/todo_manager.py` | 添加持久化方法 |

#### 2.2.2 新增文件

| 文件 | 说明 |
|------|------|
| `oc_collab/sync/file_sync.py` | 文件同步工具类 |

### 2.3 类设计

```python
class FileSync:
    """文件同步工具类"""
    
    @staticmethod
    def sync_to_file(data: dict, file_path: str) -> bool:
        """将数据同步到文件"""
        pass
    
    @staticmethod
    def backup_file(file_path: str) -> str:
        """备份原文件"""
        pass
```

### 2.4 方法签名

#### 2.4.1 todowrite.py 修改

```python
def execute_add(
    agent_id: str,
    content: str,
    priority: str = "P2",
    depends_on: Optional[str] = None,
    auto_sync: bool = True
) -> dict:
    """添加待办事项
    
    Args:
        agent_id: Agent ID
        content: 任务内容
        priority: 优先级
        depends_on: 依赖任务ID
        auto_sync: 是否自动同步到文件
    
    Returns:
        添加的任务信息
    """
    # 1. 验证参数
    # 2. 创建任务
    # 3. 同步到文件（如果 auto_sync=True）
    # 4. 显示确认消息
```

#### 2.4.2 todoedit.py 修改

```python
def execute_edit(
    task_id: str,
    agent_id: str,
    status: Optional[str] = None,
    auto_sync: bool = True
) -> dict:
    """编辑待办事项
    
    Args:
        task_id: 任务ID
        agent_id: Agent ID
        status: 新状态
        auto_sync: 是否自动同步到文件
    
    Returns:
        编辑后的任务信息
    """
    # 1. 验证参数
    # 2. 更新任务
    # 3. 同步到文件（如果 auto_sync=True）
    # 4. 显示确认消息
```

### 2.5 同步流程

```
用户执行 todowrite 命令
    ↓
解析命令参数
    ↓
验证参数有效性
    ↓
更新内存中的 todo 列表
    ↓
调用 FileSync.sync_to_file()
    ↓
写入 state/agent_adhoc_todos.yaml
    ↓
显示 "✓ 已同步到文件"
```

### 2.6 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 文件写入失败 | 显示错误信息，不中断程序 |
| 文件权限不足 | 显示权限错误提示 |
| YAML 解析错误 | 回滚到备份文件 |

---

## 3. 用户界面

### 3.1 命令行输出

```
$ oc-collab todo add "测试 F-AUTO-002" --agent agent1

✓ 已添加任务: TODO-NEW
内容: 测试 F-AUTO-002
优先级: P2
状态: pending
✓ 已同步到文件: state/agent_adhoc_todos.yaml
```

```
$ oc-collab todo done 1 --agent agent1

✓ 已更新任务: TODO-001
状态: completed
✓ 已同步到文件: state/agent_adhoc_todos.yaml
```

### 3.2 同步历史查看

```bash
oc-collab todo history
```

输出：
```
同步历史:
2026-02-07 14:30:05 - TODO-001 created - agent1
2026-02-07 14:30:10 - TODO-001 status→completed - agent1
2026-02-07 14:30:15 - TODO-002 created - agent1
```

---

## 4. 测试用例

### 4.1 单元测试

| 测试用例 | 输入 | 预期输出 |
|----------|------|----------|
| 添加任务自动同步 | todowrite add "test" | 文件中包含新任务 |
| 编辑任务自动同步 | todoedit done 1 | 文件中状态已更新 |
| 禁用自动同步 | todowrite add "test" --no-sync | 文件不更新 |
| 同步失败处理 | 文件只读 | 显示错误，不中断 |

### 4.2 集成测试

| 测试场景 | 步骤 | 预期结果 |
|----------|------|----------|
| 跨会话持久化 | 添加任务 → 重启 → 查看 | 任务仍然存在 |
| 批量操作同步 | 批量编辑任务 | 所有任务同步成功 |

---

## 5. 工时预估

| 任务 | 预估时间 |
|------|----------|
| FileSync 工具类 | 0.5h |
| todowrite 修改 | 0.5h |
| todoedit 修改 | 0.5h |
| 单元测试 | 0.5h |
| **总计** | **2h** |

---

## 6. 风险与注意事项

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 文件写入性能 | 低 | 中 | 使用批量写入 |
| YAML 格式损坏 | 低 | 高 | 备份原文件 |

---

## 7. 依赖关系

- 无外部依赖
- 基于现有 todowrite/todoedit 实现

---

## 8. 签署确认

### Agent 1 确认

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-07 | ⏳ pending |

### Agent 2 技术评审

| 评审项 | 结论 |
|--------|------|
| 设计合理性 | ⏳ pending |
| 实现复杂度 | ⏳ pending |
| 测试覆盖 | ⏳ pending |

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | pending |

---

**文档版本**: v1
**创建日期**: 2026-02-07
**状态**: DRAFT
