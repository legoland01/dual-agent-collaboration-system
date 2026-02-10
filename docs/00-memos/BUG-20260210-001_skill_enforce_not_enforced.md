# Bug报告：skill enforce未真正强制执行

**Bug编号**: BUG-20260210-001
**严重程度**: P1
**类型**: 功能缺陷
**状态**: IN_PROGRESS → 待测试验证

---

## 1. Bug描述

### 1.1 问题陈述

v2.2.6设计目标（FR-SKILL-001）：
> "在CLI命令执行前，强制检查相关Skill是否已加载"

但实际实现中，`skill enforce`只是提供了手动命令，**并未集成到CLI命令中自动执行**。

### 1.2 影响范围

| 命令 | 预期行为 | 实际行为 | 影响 |
|------|----------|----------|------|
| `oc-collab todowrite` | 自动检查相关Skill | 无检查 | Agent可能跳过Skill |
| `oc-collab signoff` | 自动检查相关Skill | 无检查 | Agent可能跳过Skill |
| `oc-collab phase-advance` | 自动检查相关Skill | 无检查 | Agent可能跳过Skill |

---

## 2. 重现步骤

### 2.1 步骤1：运行todowrite命令

```bash
$ oc-collab todowrite --content "测试" --agent 1
```

**预期**：应检查Agent1是否有权限执行todowrite，是否需要加载相关Skill

**实际**：直接执行，无任何Skill检查

### 2.2 步骤2：手动运行skill enforce

```bash
$ oc-collab skill enforce --before-action -a todowrite
✅ todowrite 所需的Skill已全部加载
```

**说明**：`skill enforce`命令本身可用，但需要Agent**主动调用**，而非自动触发。

---

## 3. 根本原因

### 3.1 代码分析

**v2.2.6实现**：
```python
# skill_commands.py
def skill_enforce(action: str, before_action: bool):
    # ✅ 命令存在
    result = enforcer.check_before_action(action)

# enhanced_commands.py
def todowrite_command(auto_check: bool, ...):
    # ❌ 没有调用 SkillEnforcer.check_before_action()
```

**问题**：`todowrite`命令没有集成`SkillEnforcer`。

### 3.2 设计缺陷

| 问题 | 说明 |
|------|------|
| 缺少集成 | SkillEnforcer没有集成到CLI命令中 |
| 依赖手动 | Agent必须主动调用`skill enforce` |
| 无强制 | "强制"设计变成了"可选"功能 |

---

## 4. 解决方案

### 4.1 已修复方案（集成到CLI命令）

在`todowrite`等命令中集成Skill检查：

```python
# enhanced_commands.py
def todowrite_command(..., auto_check: bool, ...):
    if auto_check:
        from ..core.skill_enforcer import SkillEnforcer
        enforcer = SkillEnforcer()
        skill_result = enforcer.check_before_action("todowrite")
        
        if skill_result["missing"]:
            click.echo(f"\n⚠️  缺少相关Skill (todowrite):")
            for skill in skill_result["missing"]:
                click.echo(f"   • {skill}")
            if skill_result["suggestions"]:
                click.echo(f"\n   建议: {skill_result['suggestions'][0]}")
            click.echo("")
```

### 4.2 默认行为

| 参数 | 行为 |
|------|------|
| `auto_check=True` (默认) | 检查Skill，缺失时警告 |
| `auto_check=False` | 跳过检查（紧急情况） |

### 4.3 已修改文件

| 文件 | 修改内容 |
|------|----------|
| `src/cli/enhanced_commands.py` | todowrite_command集成SkillEnforcer |
| `src/cli/main.py` | signoff_command集成SkillEnforcer |
| `src/cli/main.py` | advance_command集成SkillEnforcer |

---

## 5. 影响评估

### 5.1 风险

| 风险 | 可能性 | 影响 | 应对 |
|------|--------|------|------|
| Agent忘记调用skill enforce | 高 | 中 | 自动集成 |
| Skill检查导致执行延迟 | 低 | 低 | 纯内存操作 |

### 5.2 收益

| 收益 | 说明 |
|------|------|
| 防止遗漏 | Agent不会跳过Skill |
| 培养习惯 | 强制检查形成肌肉记忆 |
| 质量提升 | 确保按Skill执行 |

---

## 6. 修复优先级

| 优先级 | 原因 |
|--------|------|
| P0 | 核心功能未实现 |
| P1 | 影响协作规范执行 |
| P2 | 可手动规避 |

---

## 7. 验收标准

- [x] `todowrite` 命令自动检查相关Skill
- [x] `signoff` 命令自动检查相关Skill
- [x] `phase-advance` 命令自动检查相关Skill
- [x] 缺失Skill时给出警告
- [x] 支持 `--auto-check=False` 跳过检查
- [ ] 添加测试用例验证

---

## 8. 修复任务

| ID | 任务 | 负责人 | 工时 | 状态 |
|----|------|--------|------|------|
| FIX-001 | 集成SkillEnforcer到todowrite | Agent2 | 1h | DONE |
| FIX-002 | 集成SkillEnforcer到signoff | Agent2 | 1h | DONE |
| FIX-003 | 集成SkillEnforcer到phase-advance | Agent2 | 1h | DONE |
| FIX-004 | 添加测试用例 | Agent1 | 1h | PENDING |

---

## 9. 相关文档

| 文档 | 说明 |
|------|------|
| `src/core/skill_enforcer.py` | SkillEnforcer实现 |
| `src/cli/skill_commands.py` | skill enforce命令 |
| `src/cli/enhanced_commands.py` | todowrite命令 |
| `src/cli/main.py` | signoff和advance命令 |
| `docs/01-requirements/requirements_v2.2.6.md` | v2.2.6需求 |

---

## 10. 版本历史

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1 | 2026-02-10 | 创建Bug报告 | Agent 1 |
| v1.1 | 2026-02-10 | 完成FIX-001/002/003 | Agent 2 |

