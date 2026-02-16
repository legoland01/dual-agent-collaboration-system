# 核心功能"不生效"问题分析与修复方案

**生成日期**: 2026-02-16  
**分析范围**: v2.2.9, v2.2.11 相关功能

---

## 问题一：Compliance检查静默跳过

### 现状

**文件**: `src/cli/enhanced_commands.py`  
**位置**: 第98-113行

```python
# v2.2.9: ComplianceEnforcer集成 - Agent1禁止执行todowrite
from ..core.compliance_enforcer import ComplianceEnforcer
try:
    context = ContextManager().load_context()
    current_agent_id = context.agent
    enforcer = ComplianceEnforcer(current_agent_id)
    compliance_result = enforcer.check("todowrite")

    if not compliance_result.allowed:
        click.echo(f"\n{compliance_result.message}\n")
        enforcer.record_violation(compliance_result)
        raise click.Abort()
except ContextNotFoundError:
    pass  # ⚠️ 问题：静默跳过
except Exception as e:
    click.echo(f"⚠️ 合规检查跳过: {e}")  # ⚠️ 问题：静默跳过
```

### 问题分析

| 场景 | 当前行为 | 期望行为 |
|------|----------|----------|
| ContextManager失败 | 静默跳过，允许执行 | 应提示"无法获取Agent上下文，需明确指定" |
| 任何异常 | 静默跳过，允许执行 | 应降级为警告，但记录日志 |

### 修复方案

```python
# 方案A：严格模式（推荐）
except ContextNotFoundError:
    click.echo("⚠️ 无法获取Agent上下文，请先运行 'oc-collab switch 1' 或 'oc-collab switch 2' 切换Agent")
    click.echo("   为确保角色合规，建议明确指定Agent")
    # 不阻断执行，但提示

# 方案B：记录模式
except (ContextNotFoundError, Exception) as e:
    # 记录到日志文件
    import logging
    logging.warning(f"合规检查跳过: {e}")
    click.echo(f"⚠️ 合合检查降级运行: {e}")
```

---

## 问题二：AutoBugDetector静默跳过

### 现状

**文件**: `src/cli/enhanced_commands.py`  
**位置**: 第177-210行

```python
# v2.2.15: AutoBugDetector集成 - 任务后自检
# 当 agent_id 为 None 时，尝试从 StateManager 获取活跃 Agent
if agent_id is None:
    try:
        from ..core.state_manager import StateManager
        state_mgr = StateManager(str(Path.cwd()))
        active_agent = state_mgr.get_active_agent()
        if active_agent and "agent" in active_agent:
            agent_id = int(active_agent.replace("agent", ""))
            click.echo(f"   ℹ️ 未指定Agent，使用活跃Agent: {active_agent}")
    except Exception:
        pass  # ⚠️ 问题：静默跳过

if agent_id:  # ⚠️ 问题：如果仍为None，整个自检被跳过
    from ..core.auto_bug_detector import AutoBugDetector
    # ... 自检逻辑
```

### 问题分析

| 场景 | 当前行为 | 期望行为 |
|------|----------|----------|
| 未指定agent_id且无活跃Agent | 静默跳过自检 | 应提示"无法确定Agent，跳过自检" |
| StateManager失败 | 静默跳过 | 应提示"获取Agent失败，跳过自检" |
| 自检执行失败 | 提示"自检跳过: {e}" | 应记录详细错误 |

### 修复方案

```python
# 第177-210行修改为：
# v2.2.15: AutoBugDetector集成 - 任务后自检

# 尝试获取agent_id
agent_detected = False
if agent_id is None:
    try:
        from ..core.state_manager import StateManager
        state_mgr = StateManager(str(Path.cwd()))
        active_agent = state_mgr.get_active_agent()
        if active_agent and "agent" in active_agent:
            agent_id = int(active_agent.replace("agent", ""))
            agent_detected = True
            click.echo(f"   ℹ️ 未指定Agent，使用活跃Agent: {active_agent}")
    except Exception as e:
        click.echo(f"   ⚠️ 获取Agent信息失败: {e}")

# 执行自检
if agent_id:
    from ..core.auto_bug_detector import AutoBugDetector
    try:
        detector = AutoBugDetector()
        bugs = detector.self_review(todo.id, agent_id)
        if bugs:
            click.echo(f"\n⚠️  自检发现问题:")
            # ... 原有逻辑
    except Exception as e:
        click.echo(f"   ⚠️ 自检执行失败: {e}")
else:
    # ⚠️ 明确提示跳过原因
    if agent_detected:
        click.echo("   ℹ️ 无活跃Agent，跳过自检")
    else:
        click.echo("   ℹ️ 无法确定Agent，跳过自检（可使用 --agent 指定）")
```

---

## 问题三：StateNotifier静默跳过

### 现状

**文件**: `src/cli/enhanced_commands.py`  
**位置**: 第164-175行

```python
# v2.2.9: StateNotifier集成 - 发送Webhook通知
try:
    if notifier.notify_todo_created(todo.id, todo.content, f"agent{current_agent}"):
        click.echo("   🔔 Webhook通知已发送")
    else:
        click.echo("   ℹ️ Webhook未配置（静默跳过）")  # ⚠️ 静默一词误导
except (ContextNotFoundError, Exception):
    click.echo("   ℹ️ Webhook通知跳过（上下文不存在）")
```

### 问题分析

| 场景 | 当前行为 | 期望行为 |
|------|----------|----------|
| Webhook未配置 | 显示"静默跳过" | 改为"Webhook未配置，通知不可用" |
| 发送失败 | 显示"上下文不存在" | 显示具体错误原因 |

### 修复方案

```python
# 第164-175行修改为：
# v2.2.9: StateNotifier集成 - 发送Webhook通知
try:
    result = notifier.notify_todo_created(todo.id, todo.content, f"agent{current_agent}")
    if result:
        click.echo("   🔔 Webhook通知已发送")
    else:
        # 明确告知用户
        click.echo("   ⚠️ Webhook未配置，通知功能不可用")
        click.echo("      如需启用通知，请配置 config/webhook.yaml")
except Exception as e:
    click.echo(f"   ⚠️ Webhook通知失败: {e}")
```

---

## 问题四：Skill强制执行验证

### 验证结果 ✅ 已确认

**问题**: v2.2.11 需求要求"移除--auto-check可选参数"，但实际**未移除**

| 命令 | 文件位置 | --auto-check 状态 | SkillEnforcer调用 |
|------|----------|-------------------|-------------------|
| todowrite | enhanced_commands.py:57 | ⚠️ 仍存在 | ✅ 已调用 (line 76) |
| signoff | main.py:245 | ⚠️ 仍存在 | ✅ 已调用 (line 252) |
| phase-advance | main.py:1328 | ⚠️ 仍存在 | ✅ 已调用 (line 1335) |

### 修复方案

```python
# 方案A：移除参数（推荐，符合v2.2.11需求）
# 删除 @click.option("--auto-check/--no-auto-check"...) 这行

# 方案B：如果需要保留，至少默认强制
@click.option("--auto-check/--no-auto-check", default=True, ...)  # 确保默认开启
```

### 验证命令

```bash
# 检查各命令是否仍有 --auto-check
grep -n "auto.check" src/cli/enhanced_commands.py src/cli/main.py
```

---

## 修复优先级

| 优先级 | 问题 | 修复难度 | 影响 |
|--------|------|----------|------|
| **P0** | Compliance静默跳过 | 低 | 高（角色混乱） |
| **P1** | AutoBugDetector静默跳过 | 低 | 中（功能失效） |
| **P2** | StateNotifier提示优化 | 低 | 低（体验优化） |
| **P3** | Skill强制执行验证 | 中 | 高（功能核心） |

---

## 修复检查清单

- [ ] 问题一：Compliance检查 - 添加明确提示
- [ ] 问题二：AutoBugDetector - 添加明确提示
- [ ] 问题三：StateNotifier - 优化提示文案
- [ ] 问题四：Skill强制执行 - 验证是否生效
- [ ] 补充测试：各场景的E2E测试
