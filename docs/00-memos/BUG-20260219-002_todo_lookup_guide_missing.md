# Bug报告：TODO存储位置文档缺失

**Bug ID**: BUG-20260219-002  
**版本**: v2.2.7  
**报告日期**: 2026-02-19  
**报告人**: Agent2  
**优先级**: high  
**类型**: 文档/配置问题  

---

## 问题描述

Agent2（当前用户）收到"查看TODO"指令后：
1. 尝试读取 `state/agent_adhoc_todos.yaml` - 文件不存在
2. 检查 `state/todos.db` - 不知道如何读取SQLite数据库
3. AGENTS.md 中只说明TODO存在于 `todos.db`，但未说明如何查询

**关键问题**：
- 系统已从YAML迁移到SQLite
- 文档未更新以说明Agent如何查询自己的TODO
- TODO_NOTIFY.md 规则存在但无实际查询工具

---

## 复现步骤

1. 切换到Agent2: `oc-collab switch 2`
2. 执行"查看TODO"指令
3. Agent无法确定TODO存储位置和查询方式

---

## 期望行为

Agent应能：
1. 自动获取分配给自己的TODO列表
2. 通过命令行工具查询TODO
3. 或者有明确的文档说明如何手动查询

---

## 修复建议

1. **更新AGENTS.md**：添加Agent查询TODO的说明
2. **提供CLI命令**：`oc-collab todo list --agent 2` 或类似命令
3. **或提供脚本**：查询 `todos.db` 的示例脚本

---

**状态**: completed  
**修复内容**:
- 更新 AGENTS.md，将 `state/agent_adhoc_todos.yaml` 改为 `state/todos.db`
- 添加 CLI 命令说明：`oc-collab todo list`
- 验证命令可正常查询当前Agent的TODO
