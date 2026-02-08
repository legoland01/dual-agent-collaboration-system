# Bug 报告：todowrite未正确写入TODO到文件

**Bug ID**: BUG-20260208-005
**严重程度**: P1
**状态**: 待修复
**发现人**: Agent 1
**发现日期**: 2026-02-08

---

## Bug描述

### 表现形式

| 场景 | 问题 |
|------|------|
| 执行 `todowrite` 创建TODO | 命令返回成功但文件未更新 |
| 查看 `state/agent_adhoc_todos.yaml` | 新TODO不存在 |
| 查看 `git log` | 提交中没有新TODO |

### 重现场景

```bash
# 步骤1: 执行todowrite
todowrite --content "测试TODO" --priority P0 --agent 2
# 输出: TODO已创建: TODO-XXX

# 步骤2: 检查文件
cat state/agent_adhoc_todos.yaml | grep TODO-XXX
# 输出: 空（TODO不存在）

# 步骤3: 查看git status
git status
# 输出: state/agent_adhoc_todos.yaml 未被修改

# 步骤4: 查看git log
git log --oneline -1
# 输出: 之前的提交，不包含新TODO
```

### 影响范围

| 影响 | 严重程度 |
|------|----------|
| TODO无法持久化 | P1 - 丢失任务跟踪 |
| Agent无法看到新TODO | P1 - 阻塞协作 |
| git历史不完整 | P0 - 无法追溯 |

---

## 问题分析

### 根因分析

| 问题 | 原因 | 层级 |
|------|------|------|
| todowrite返回成功但文件未更新 | 工具内部逻辑问题 | 工具 |
| git add/commit未执行 | 工具未自动提交 | 工具 |

### 相关代码

```python
# todowrite工具可能的问题：
1. 成功返回但save失败
2. 未调用git add/commit
3. 写入错误的文件路径
```

---

## 临时解决方案

```bash
# 手动编辑文件添加TODO
# 或
# 使用git add/commit手动提交
```

---

## 测试用例

```python
def test_todowrite写入文件(self):
    """验证todowrite正确写入文件"""
    import yaml
    
    # 执行todowrite
    todowrite(...)
    
    # 读取文件
    with open('state/agent_adhoc_todos.yaml') as f:
        data = yaml.safe_load(f)
    
    # 验证TODO存在
    assert 'TODO-XXX' in [t['id'] for t in data['adhoc_todos']]
```

---

## 时间线

| 日期 | 事件 |
|------|------|
| 2026-02-08 | Agent 1 发现问题，创建Bug报告 |
| 2026-02-08 | Agent 2 调查并修复 |

---

## 关联文档

| 文档 | 说明 |
|------|------|
| `state/agent_adhoc_todos.yaml` | TODO文件 |
| `scripts/*.py` | todowrite工具脚本 |

---

**创建人**: Agent 1
**日期**: 2026-02-08
**状态**: 待修复
