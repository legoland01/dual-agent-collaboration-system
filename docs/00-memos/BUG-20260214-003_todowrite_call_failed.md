# BUG-20260214-003: todowrite工具调用失败

**发现日期**: 2026-02-14  
**发现人**: Agent 1  
**严重度**: P1  
**状态**: CLOSED
**修复日期**: 2026-02-14  
**修复人**: Agent 2

---

## 问题描述

调用`todowrite`工具创建TODO时，工具返回错误，TODO未成功创建。

## 复现步骤

1. 调用todowrite工具创建TODO
2. 工具返回错误：`Invalid input: expected string, received undefined`
3. TODO未写入agent_adhoc_todos.yaml

## 根因分析

```
BUG-007: TODO编号冲突
    │
    └── agent_adhoc_todos.yaml文件损坏
            │
            └── 多余TODO-358条目导致YAML解析错误
                    │
                    └── save_todos()时检测到ID重复报错
```

## 解决方案

**根本修复**: 恢复agent_adhoc_todos.yaml文件，删除重复的TODO-358条目。

**验证**: todowrite命令现在可以正常创建TODO。

## 验证结果

```
✅ TODO-341创建成功
✅ TODO-342创建成功
✅ TODO-343创建成功
```

---

**状态**: CLOSED ✅
**备注**: BUG-007同时修复，YAML文件结构已恢复正常
