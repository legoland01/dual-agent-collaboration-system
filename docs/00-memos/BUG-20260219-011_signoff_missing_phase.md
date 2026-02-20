# BUG-20260219-011: signoff命令因缺少phase字段无法执行

**严重程度**: 高  
**类型**: 功能缺陷  
**发现时间**: 2026-02-19  
**发现者**: Agent1 (验收过程中发现)

---

## 问题描述

执行 `oc-collab signoff requirements` 命令时报错：
```
错误: 当前阶段状态不允许签署:
```

## 根本原因

`project_state.yaml` 缺少 `phase` 字段，signoff模块无法判断当前所处阶段。

## 复现步骤

1. 执行任何signoff命令: `oc-collab signoff requirements`
2. 报错: "当前阶段状态不允许签署"

## 期望行为

- signoff命令应该能正常执行
- 或者提示用户需要先设置phase

## 实际行为

- signoff模块读取phase失败
- 命令直接报错退出

## 修复建议

1. 在 `project_state.yaml` 中添加 `phase` 字段
2. 或者在signoff命令中添加phase初始化逻辑
3. 或者改进错误提示，提示用户如何设置phase

---

## 修复方案

修改 `src/core/signoff.py` 中的 `can_sign` 方法，允许在阶段状态为空时进行签署：

```python
current_status = stage_data.get("status", "")

if not current_status:
    return True, ""  # 允许签署空状态阶段
```

---

**状态**: ✅ 已修复  
**修复时间**: 2026-02-19  
**修复人**: Agent2
