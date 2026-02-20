# Bug报告：验收测试发现的多个CLI命令Bug

**Bug ID**: BUG-20260218-002  
**版本**: v2.3.2  
**报告日期**: 2026-02-18  
**报告人**: Agent1  
**优先级**: high  
**类型**: 功能缺陷  

---

## 问题概述

v2.3.2验收测试发现多个CLI命令功能异常。

---

## Bug列表

### Bug 1: todo complete 命令报错

**现象**:
```bash
$ oc-collab todo complete TODO-2-003
❌ 操作失败: update_todo() takes 2 positional arguments but 3 were given
```

**根因**: `todo_commands.py` 调用 `update_todo()` 参数数量不匹配

---

### Bug 2: todo ack 显示成功但数据库未更新

**现象**:
```bash
$ oc-collab todo ack TODO-2-001
✅ TODO TODO-2-001 已确认
# 数据库验证: status仍为pending
```

**根因**: ack命令显示成功但未实际更新数据库

---

### Bug 3: todo mark-read 显示成功但数据库未更新

**现象**:
```bash
$ oc-collab todo mark-read TODO-1to1-004
✅ TODO TODO-1to1-004 已标记为已读
# 数据库验证: is_read仍为0
```

**根因**: mark-read命令显示成功但未实际更新数据库

---

### Bug 4: todowrite --source 参数不生效

**现象**:
```bash
$ oc-collab todowrite --content "测试来源" --source BUG
# 数据库验证: source字段为空，未存储"BUG"
```

**根因**: source参数未正确保存到数据库

---

### Bug 5: config set 命令报错

**现象**:
```bash
$ oc-collab config set test.key testvalue
TypeError: 'str' object does not support item assignment
```

**根因**: `config_manager.py` 中嵌套字典赋值逻辑错误

---

## 修复建议

1. 检查 `src/cli/todo_commands.py` 中 ack/complete/mark-read 实现
2. 检查 `src/core/todo_queue_manager.py` 中 update_todo 方法
3. 检查 todowrite 命令中 source 参数处理
4. 检查 `src/core/config_manager.py` 中 set 方法

---

## 验收标准

- [ ] todo complete 命令正常更新数据库
- [ ] todo ack 命令正常更新数据库
- [ ] todo mark-read 命令正常更新数据库
- [ ] todowrite --source 参数正常保存
- [ ] config set 命令正常执行

---

**状态**: pending  
**指派给**: Agent2
