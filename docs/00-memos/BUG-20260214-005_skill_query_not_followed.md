# BUG-20260214-005: Skill查询规则未得到遵循

**发现日期**: 2026-02-14  
**发现人**: Agent 1  
**严重度**: P1  
**状态**: CLOSED
**修复日期**: 2026-02-14  
**修复人**: Agent 2

---

## 问题描述

Skill查询规则"每次行动前先查询skill"经常得不到遵循，导致：
- 流程不规范
- 重复劳动
- 遗漏关键步骤

## 根因分析

**没有强制机制**

| 规则 | 实现状态 |
|------|----------|
| 有Skill文档 | ✅ |
| 有规则说明 | ✅ |
| 有强制执行 | ❌ **缺失** |

## v2.2.10 解决方案

### 1. 新增 skill-check 命令组

```
oc-collab skill check              # 检查所有Skill状态
oc-collab skill check --missing   # 只显示缺失的
oc-collab skill check --phase development  # 检查特定阶段
oc-collab skill verify todowrite  # 验证执行前所需Skill
oc-collab skill status            # 显示Agent合规状态摘要
```

### 2. SkillEnforcer已有集成

```python
# todowrite命令中已有Skill检查
skill_result = skill_enforcer.check_before_action("todowrite")
```

### 3. Agent启动时检查

```bash
oc-collab startup-check  # Agent启动自检，已实现
```

## 验证结果

```
✅ skill-check check 命令正常工作
✅ skill-check verify todowrite 显示必需Skill
✅ 所有必需Skill已加载
```

## 使用建议

| 场景 | 操作 |
|------|------|
| 执行任务前 | `oc-collab skill verify <action>` |
| 启动时 | `oc-collab startup-check` |
| 检查缺失 | `oc-collab skill check --missing` |

---

**状态**: CLOSED ✅
**备注**: v2.2.10提供skill-check命令组，Agent应主动使用"先查询再执行"模式
