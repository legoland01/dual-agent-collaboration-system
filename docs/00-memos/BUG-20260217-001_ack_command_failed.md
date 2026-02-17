# Bug报告：ACK命令执行失败

**Bug ID**: BUG-20260217-001  
**版本**: v2.3.2  
**报告日期**: 2026-02-17  
**报告人**: Agent 1  
**优先级**: medium  

---

## 问题描述

`oc-collab todo ack <todo_id>` 命令执行失败。

## 错误信息

```
❌ 确认失败: 'int' object has no attribute 'replace'
```

## 复现步骤

1. 执行 `oc-collab todo ack TODO-2to1-030`
2. 命令返回错误：`'int' object has no attribute 'replace'`

## 预期行为

TODO应该被标记为已确认（acknowledged），状态更新成功。

## 实际行为

命令报错，TODO状态未更新。

## 根因分析

初步判断：
- ack命令内部调用了某个时间处理方法
- 该方法期望接收字符串类型，但实际收到int类型
- 可能是时间戳格式处理问题

## 修复建议

1. 检查 `src/core/todo_sync_manager.py` 或相关文件的ack实现
2. 检查时间戳处理逻辑，确保类型正确
3. 添加类型检查或转换

## 验收标准

- [ ] `oc-collab todo ack <todo_id>` 命令执行成功
- [ ] TODO状态正确更新为acknowledged
- [ ] 错误信息友好提示

---

**状态**: pending
