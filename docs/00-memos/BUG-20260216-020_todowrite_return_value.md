# BUG报告：todowrite缺乏明确的成功/失败返回值

**Bug ID**: BUG-20260216-020
**严重程度**: P1
**状态**: open
**发现时间**: 2026-02-16
**发现者**: Agent1

---

## 问题描述

当前`todowrite`命令只输出信息，没有明确的返回值。成功/失败需要解析输出内容判断，导致：

1. **自动化脚本无法可靠判断执行结果**
   - 只能解析输出字符串判断成功/失败
   - 容易被错误信息误导

2. **测试用例无法可靠验证**
   - pytest需要检查returncode判断成功/失败
   - 当前无法做到

3. **集成其他工具困难**
   - 无法判断todo是否真正创建成功
   - 流程控制无法基于返回值

---

## 当前调用todowrite的模块分析

| 模块 | 文件 | 调用方式 | 问题 |
|------|------|----------|------|
| session_manager.py | session_manager.py:237,248,257 | `todo_manager.add_todo()` | 无返回值判断 |
| auto_checker.py | auto_checker.py:1 | 验证参数 | 只验证输入，不判断创建结果 |
| skill_enforcer.py | skill_enforcer.py:121 | 行动检查 | 不检查todo是否创建成功 |
| compliance_enforcer.py | compliance_enforcer.py:4 | Agent权限控制 | 不检查执行结果 |
| main.py | main.py:1576 | CLI入口 | 无返回值 |
| 测试用例 | tests/test_todowrite_complete.py | subprocess调用 | 只能检查stdout |

---

## 修改清单

### 1. todowrite命令返回值设计

**文件**: `src/cli/enhanced_commands.py`

**修改内容**:
```python
# 返回值设计
class TodoWriteResult:
    success: bool
    todo_id: Optional[str]
    message: str
    error: Optional[str]

# CLI返回码
# 0 = 成功
# 1 = 参数错误
# 2 = 执行失败
# 3 = Agent权限不足
```

### 2. 各模块需要的修改

#### 2.1 session_manager.py (3处)
- 位置: 第237, 248, 257行
- 修改: 检查`add_todo()`返回值，判断是否成功
- 失败处理: 记录日志或抛出异常

#### 2.2 auto_checker.py
- 位置: 整个文件
- 修改: 验证后检查todo是否创建成功
- 失败处理: 返回验证失败原因

#### 2.3 skill_enforcer.py
- 位置: 第121, 136, 197行
- 修改: 行动前检查，行动后验证结果
- 失败处理: 阻止后续操作

#### 2.4 compliance_enforcer.py
- 位置: 第141, 160行
- 修改: Agent1禁止时返回错误码
- 失败处理: 阻止执行

#### 2.5 main.py
- 位置: 第1576行
- 修改: 根据todowrite结果设置进程退出码
- 失败处理: 返回非0退出码

#### 2.6 测试用例
- 文件: tests/test_todowrite_complete.py
- 修改: 检查returncode而非解析stdout
- 期望: 成功=0, 失败=非0

---

## 建议的实现方式

### 方案A: 返回码 (推荐)

```bash
# 成功
$ oc-collab todowrite --content "test"
echo $?
→ 0

# 失败
$ oc-collab todowrite --content ""
echo $?
→ 1
```

### 方案B: JSON输出

```bash
$ oc-collab todowrite --content "test" --json
{"success": true, "todo_id": "TODO-1-001", "message": "创建成功"}
```

---

## 影响范围

- 所有调用todowrite的地方都需要更新
- 测试用例需要重写
- 现有脚本可能需要调整

---

## 优先级建议

**P1**: 必须实现
- 自动化测试需要可靠的返回值
- 防止脚本无法判断执行结果

---

**创建时间**: 2026-02-16
**状态**: open
