# Bug 报告：todowrite命令无法可靠创建TODO

**Bug ID**: BUG-20260208-007
**严重程度**: P0
**状态**: 待修复
**发现人**: Agent 1
**发现日期**: 2026-02-08

---

## Bug描述

### 表现形式

| 场景 | 问题 |
|------|------|
| 执行 `todowrite --content "xxx" --priority high --agent 2` | 命令返回成功，但TODO未写入文件 |
| 检查 `state/agent_adhoc_todos.yaml` | 新TODO不存在 |
| 查看 `git status` | 文件未被修改 |
| 查看 `git log` | 提交历史中无新TODO |

### 重现场景

```bash
# 步骤1: 执行todowrite
$ oc-collab todowrite --content "测试TODO" --priority high --agent 2
✅ 待办已创建: [TODO-XXX] 测试TODO

# 步骤2: 检查文件
$ grep "TODO-XXX" state/agent_adhoc_todos.yaml
# 输出: 空（TODO不存在）

# 步骤3: 检查git status
$ git status --porcelain
# 输出: 无变化

# 步骤4: 检查文件行数
$ wc -l state/agent_adhoc_todos.yaml
# 执行前后行数不变
```

### 影响范围

| 影响 | 严重程度 |
|------|----------|
| TODO无法可靠创建 | P0 - 完全阻塞任务跟踪 |
| Agent协作失效 | P0 - 无法分配任务 |
| BUG跟踪失效 | P0 - 无法记录发现的BUG |

---

## 问题分析

### 根本原因

| 问题 | 可能原因 |
|------|----------|
| todowrite返回成功但文件未修改 | 1. save()方法未调用 |
| | 2. git add/commit未执行 |
| | 3. 文件路径错误 |
| | 4. save后被还原 |

### 相关组件

| 组件 | 说明 |
|------|------|
| `oc-collab todowrite` | CLI命令 |
| `state/agent_adhoc_todos.yaml` | TODO存储文件 |
| todowrite工具内部逻辑 | 待调查 |

### 测试用例

```python
def test_todowrite写入文件(self):
    """
    验证todowrite正确写入TODO到文件
    """
    import subprocess
    import yaml

    # 备份原文件
    subprocess.run(["cp", "state/agent_adhoc_todos.yaml", "/tmp/backup.yaml"], ...)

    try:
        # 执行todowrite
        result = subprocess.run([
            "python3", "-m", "src.cli.main", "todowrite",
            "--content", "测试TODO", "--priority", "high", "--agent", "2"
        ], capture_output=True, text=True)

        # 验证1：命令成功
        assert result.returncode == 0, f"todowrite失败: {result.stderr}"

        # 验证2：文件被修改
        result2 = subprocess.run(
            ["git", "status", "--porcelain", "state/agent_adhoc_todos.yaml"],
            capture_output=True, text=True
        )
        assert "M" in result2.stdout or "A" in result2.stdout, \
            "todowrite执行后文件未被修改"

        # 验证3：TODO存在
        with open("state/agent_adhoc_todos.yaml") as f:
            data = yaml.safe_load(f)
        assert any("测试TODO" in str(t) for t in data['adhoc_todos']), \
            "新TODO不存在于文件中"

    finally:
        subprocess.run(["cp", "/tmp/backup.yaml", "state/agent_adhoc_todos.yaml"])
```

---

## 临时解决方案

```bash
# 手动编辑 state/agent_adhoc_todos.yaml 添加TODO
# 或
# 直接使用 git 命令提交
```

---

## 根本解决方案

### 需要调查

| 问题 | 说明 |
|------|------|
| todowrite工具代码 | 检查save()和git操作是否正确执行 |
| 文件路径 | 确保写入正确路径 |
| 权限问题 | 确保有写权限 |
| 缓存问题 | 排除缓存导致的问题 |

### 修复方向

```python
# todowrite工具应该：
1. 正确解析参数
2. 读取现有TODO文件
3. 添加新TODO
4. 写入文件
5. git add
6. git commit
```

---

## 测试验证

```bash
# 修复后验证
python3 -m pytest tests/test_todowrite.py -v

# 手动验证
oc-collab todowrite --content "测试" --priority high --agent 2
grep "测试" state/agent_adhoc_todos.yaml
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
| `state/agent_adhoc_todos.yaml` | TODO存储文件 |
| `src/cli/main.py` | CLI入口 |
| `scripts/todowrite.py` | todowrite工具（待定位） |

---

## 相关BUG

| ID | 关联 | 状态 |
|----|------|------|
| BUG-20260208-005 | todowrite未写入文件 | 已"修复"但未验证 |
| BUG-20260208-007 | todowrite无法可靠工作 | 当前BUG |

---

**创建人**: Agent 1
**日期**: 2026-02-08
**状态**: 待修复
