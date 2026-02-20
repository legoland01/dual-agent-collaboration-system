# Bug报告：Agent切换ID后身份迷失

**Bug ID**: BUG-20260218-003  
**版本**: v2.3.2  
**报告日期**: 2026-02-18  
**报告人**: Consultant  
**优先级**: high  
**类型**: 测试流程问题  

---

## 问题描述

执行E2E测试时，Agent2频繁使用 `oc-collab switch` 切换自己的agentID进行测试，结果切换次数过多后，Agent忘记自己当前的实际身份。

## 错误行为

```bash
# 测试过程中多次切换
oc-collab switch agent1
oc-collab switch agent2
oc-collab switch agent1
oc-collab switch agent2
# ... 多次后 ...

# 最终忘记自己是谁
# 当前agentID与实际行为不匹配
```

## 根因分析

1. **测试环境问题**：当前测试直接在生产环境执行
2. **测试设计问题**：测试脚本模拟多Agent互动，但物理上是同一Agent
3. **工具设计问题**：缺乏"临时测试身份"机制

## 修复方案 (v2.3.3)

### 实现的功能

1. **agent.identity 文件**
   - 路径: `state/agent.identity`
   - 内容:
   ```yaml
   agent_id: "1"
   locked: false
   set_at: "2026-02-20T10:00:00"
   ```

2. **AgentRegistry 新方法**
   - `set_agent_identity(agent_id, lock=True)` - 设置身份
   - `is_identity_locked()` - 检查是否锁定
   - `unlock_agent_identity()` - 解锁身份

3. **身份识别优先级**
   1. agent.identity 文件 (最优先)
   2. 环境变量 OC_AGENT_ID
   3. project_state.yaml
   4. Git config

### 测试验证

- test_BUG_20260219_002_agent_todo_isolation: ✅ PASSED
- 所有TODO测试: 208 passed, 9 skipped

---

**状态**: ✅ 已修复  
**修复时间**: 2026-02-20  
**修复人**: Agent2

## 验收标准

- [x] 实现agent.identity文件机制
- [x] 修复Agent身份识别优先级
- [x] 测试通过
