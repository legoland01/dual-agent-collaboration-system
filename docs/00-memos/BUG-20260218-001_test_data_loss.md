# Bug报告：测试过程中误删在用数据

**Bug ID**: BUG-20260218-001  
**版本**: v2.3.2  
**报告日期**: 2026-02-18  
**报告人**: Agent1  
**优先级**: high  
**类型**: 测试流程问题  

---

## 问题描述

执行v2.3.2验收测试时，测试脚本直接清空了 `state/todos.db` 中的所有数据（包括其他在用TODO），导致原有数据丢失。

## 错误行为

```bash
# 测试前置条件 - 错误做法
sqlite3 state/todos.db "DELETE FROM todos; DELETE FROM agent_status; DELETE FROM notifications;"
```

这导致：
- TODO-2to1-001（验收任务）被删除
- 其他在用TODO丢失

## 根因分析

1. **测试环境问题**：缺少独立的沙箱测试数据库
2. **测试脚本问题**：使用全表删除而非按条件清理
3. **流程问题**：未明确规定测试数据保护规则

## 修复建议

### 短期（立即）
测试脚本只清理测试过程创建的TODO，不删除原有数据：
```bash
# 正确做法：只删除测试创建的TODO
sqlite3 state/todos.db "DELETE FROM todos WHERE content LIKE '测试%';"
```

### 长期
1. 创建独立测试数据库 `state/todos_test.db`
2. 测试时使用 `--test-db` 参数切换
3. 在测试文档中明确数据保护规则

## 验收标准

- [ ] 更新测试设计文档，添加数据保护规则
- [ ] 测试只清理自己创建的数据
- [ ] 考虑沙箱测试环境

---

**状态**: pending  
**指派给**: Agent1 (测试负责人)
