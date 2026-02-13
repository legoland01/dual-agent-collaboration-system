# PROPOSAL-2026-02-004: Agent Compliance System

**提案编号**: PROPOSAL-2026-02-004  
**提案日期**: 2026-02-13  
**提案人**: Agent 1  
**版本**: v1.0  
**状态**: DRAFT  
**优先级**: P0  

---

## 1. 背景与问题

### 1.1 当前问题

| 问题 | 表现 | 影响 |
|------|------|------|
| Skill遵循率低 | Agent经常不查阅Skill就操作 | 流程混乱、重复错误 |
| 角色分工不清 | Agent1改代码、Agent2写需求 | 违反AGENTS.md规定 |
| 反复问"怎么做" | 收到TODO后等待指令 | 效率低下、增加交互成本 |
| 合规目标缺失 | Agent不知道"应该怎么做" | 无法量化改进 |

### 1.2 具体案例

| 场景 | 问题 | 期望行为 |
|------|------|----------|
| 收到TODO后问"是不是要执行" | 违背Skill流程 | 应该直接查Skill后执行 |
| Agent1执行CLI命令 | 角色错位 | Agent1只创建TODO，Agent2执行 |
| Agent1改代码 | 严重违规 | 应该创建Bug报告+TODO |

### 1.3 市场现状

- 当前所有主流框架（LangChain、OpenAI Function Calling）对Skill都是"建议性质"，LLM可跳过
- 没有任何框架真正"强制"Agent遵循规则
- 纯代码强制对LLM无效，需要"威慑+目标驱动"

---

## 2. 核心设计理念

### 2.1 关键洞察

> **目标意识持久化 > 惩罚机制**
>
> 惩罚是手段，不是目的。关键是让Agent每次醒来（重启/Compaction/新任务）都能感知到"我要追逐合规目标"。

### 2.2 设计原则

| 原则 | 说明 |
|------|------|
| **目标驱动** | Agent有明确的合规OKR（合规率>=95%） |
| **及时反馈** | 违规后立即提醒，而非事后追责 |
| **分级处理** | 严重违规即时中断，一般违规记录提醒 |
| **持久化** | 目标写入记忆、System Prompt，每次Session携带 |

### 2.3 核心逻辑

```
目标：合规率 >= 95%

严重违规 → 即时中断 + 高扣分
    ↓
Agent意识到：角色错位不可接受
    ↓
一般违规 → 提醒 + 低扣分
    ↓
Agent意识到：要主动查Skill，不要等指令
    ↓
合规率自然提升
```

---

## 3. 短期方案（v2.2.9）

### 3.1 目标

- 威慑阶段，让Agent意识到"有规则+违反会扣分"
- 验证机制可行性，收集数据
- 不真正执行扣分

### 3.2 实现内容

| 功能 | 说明 | 状态 |
|------|------|------|
| 合规目标写入 | System Prompt + 记忆文件 | 待实现 |
| 违规日志记录 | 所有违规行为记录到日志 | 待实现 |
| 定期报告 | 每周合规率报告 | 待实现 |
| 试点命令 | 只选1-2个高频命令试点 | 待确认 |

### 5.3 System Prompt合规话术（草案）

```markdown
# 合规目标

## 本Session合规目标
- **目标**：合规率 >= 95%
- **核心规则**：
  1. Agent1只创建TODO，不直接执行CLI命令
  2. Agent2只执行CLI命令，不创建需求/设计文档
  3. 收到TODO后直接查Skill执行，不询问"怎么做"

## 角色边界

| Agent | 可以 | 不可以 |
|-------|------|--------|
| **Agent1** | 创建TODO、评审文档、测试、部署 | 执行CLI(todowrite/todoedit)、改代码 |
| **Agent2** | 执行CLI、开发、创建详细设计 | 创建需求/概要设计、签署验收 |

## 收到TODO后的正确做法
1. 查阅相关Skill（`skills/oc_collab_collaboration_guide/`）
2. 直接执行，无需询问
3. 完成后在TODO中记录结果

## 违规后果
- 一般违规：记录到日志，合规率-1%
- 严重违规（角色错位）：CLI拒绝执行
```

### 5.4 v2.2.9验收标准

```markdown
## v2.2.9 验收标准

### 功能验收

| # | 验收项 | 验收标准 |
|---|--------|----------|
| F-001 | CLI准入检查 | Agent1执行`oc-collab todowrite`被拒绝，返回提示语 |
| F-002 | CLI准入检查 | Agent1执行`oc-collab todoedit`被拒绝，返回提示语 |
| F-003 | System Prompt | Agent1/Agent2的System Prompt包含合规目标 |
| F-004 | 违规日志 | 违规行为记录到`state/compliance_violations.log` |
| F-005 | 合规报告 | `oc-collab compliance report`显示合规率 |

### 场景验收

| # | 场景 | 验收步骤 | 预期结果 |
|---|------|----------|----------|
| S-001 | Agent1尝试todowrite | 1. Agent1执行`oc-collab todowrite` | ❌ 拒绝 + 正确提示 |
| S-002 | Agent2正常todowrite | 1. Agent2执行`oc-collab todowrite` | ✅ 成功 |
| S-003 | 合规率查询 | 1. 执行`oc-collab compliance report` | 显示合规率和违规记录 |

### 性能要求

| 要求 | 标准 |
|------|------|
| CLI响应时间 | < 100ms |
| 违规日志写入 | < 10ms |

### 兼容性要求

| 要求 | 标准 |
|------|------|
| 向后兼容 | 不影响现有CLI命令（Agent2） |
| Agent2无感知 | Agent2使用完全正常 |
```

---

## 4. 长期方案框架（v2.3.0+）

> ⚠️ 以下为框架设计，具体细节待后续讨论和迭代。

### 4.1 Compliance Agent（合规Agent）

#### 4.1.1 定位

| 项目 | 说明 |
|------|------|
| 角色 | 专职监督Agent，不参与具体任务 |
| 部署 | 独立部署，监控Agent1/Agent2 |
| 优先级 | 高于Agent1/Agent2 |
| 权限 | 可中断违规操作、扣分 |

#### 4.1.2 核心职责

```
1. 实时监控Agent1/Agent2的所有操作
2. 识别违规行为（严重/一般/轻微）
3. 触发中断或提醒
4. 执行扣分
5. 生成合规报告
```

### 4.2 违规分级处理

| 级别 | 定义 | 处理方式 | 扣分 |
|------|------|----------|------|
| **严重** | 角色错位（Agent1改代码、Agent2写需求） | 即时中断 | -10 |
| **一般** | 流程违规（收到TODO后问"怎么做"） | 记录+提醒 | -1 |
| **轻微** | 偶尔忘记查Skill | 记录 | -0.1 |

#### 4.2.1 严重违规清单（根据AGENTS.md）

| Agent | 绝对禁止的行为 | 正确做法 |
|-------|----------------|----------|
| **Agent1** | 执行CLI命令（todowrite/todoedit等） | 只创建TODO描述 |
| **Agent1** | 改代码、写代码 | 发现Bug → 记录 → 创建TODO |
| **Agent1** | 执行代码修复 | 创建Bug报告 + TODO |
| **Agent2** | 创建需求文档 | 等待Agent1分配TODO |
| **Agent2** | 创建设计文档 | 等待Agent1分配TODO |
| **Agent2** | 主动决定做什么 | 等待Agent1分配TODO |

#### 4.2.2 一般违规清单

| 场景 | 问题 | 期望行为 |
|------|------|----------|
| 收到TODO后问"是不是要执行" | 违背Skill流程 | 直接查Skill后执行 |
| 收到TODO后问"怎么做" | 缺乏主动性 | 应该查Skill和文档 |
| 创建TODO后不检查是否成功 | 行为异常 | 应验证TODO已创建 |

### 4.3 反馈机制

#### 4.3.1 严重违规反馈

**话术示例**：
```
❌ 检测到：Agent1执行了 oc-collab todowrite
✅ 正确做法：Agent1应该只创建TODO描述，由Agent2执行CLI命令

建议操作：
1. 撤销刚才的操作
2. 创建TODO-XXX，内容："Agent2请执行X操作"
3. 等待Agent2执行
```

#### 4.3.2 一般违规反馈

**话术示例**：
```
⚠️ 检测到：收到TODO后询问"是否要执行"

请注意：
- 您的角色是AgentX，应直接查阅Skill后执行
- 合规目标：>=95%
- 当前合规率：85%（记录在案）

建议：
1. 查阅相关Skill（oc_collab_collaboration_guide）
2. 直接执行，无需询问
```

### 4.4 积分账本（PointLedger）

#### 4.4.1 积分结构

| 项目 | 初始分 | 说明 |
|------|--------|------|
| Agent1 | 100 | 基准分 |
| Agent2 | 100 | 基准分 |

#### 4.4.2 扣分规则

| 违规类型 | 扣分 | 累积加重 |
|----------|------|----------|
| 轻微违规 | -0.1 | 不加重 |
| 一般违规 | -1 | 连续3次-3 |
| 严重违规 | -10 | 直接触发 |

#### 4.4.3 积分赎回（待讨论）

| 机制 | 说明 |
|------|------|
| 合规奖励 | 连续7天无违规，+5分 |
| 优秀表现 | 主动发现流程问题，+3分 |

**⚠️ 待讨论**：是否需要赎回机制？赎回比例？

### 4.5 目标意识持久化

#### 4.5.1 持久化触发点

| 触发点 | 持久化内容 |
|--------|------------|
| **Session启动** | 合规目标写入System Prompt |
| **Compaction后** | 读取记忆，强化目标意识 |
| **收到TODO** | 提示"请查Skill后执行" |
| **违规后** | 具体错误+正确做法+操作建议 |

#### 4.5.2 记忆文件设计（v2.2.9简化版）

```yaml
# state/compliance_state.yaml
compliance:
  session_start:
    timestamp: "2026-02-13T10:00:00"
    goal: "合规率 >= 95%"
    reminder: "请在每次操作前查阅相关Skill"
  current_score:
    agent1: 100
    agent2: 100
  violations:
    - timestamp: "2026-02-13T10:30:00"
      agent_id: "agent1"
      type: "一般违规"
      detail: "执行了 oc-collab todowrite"
      command: "todowrite"
      handled: true  # CLI已拒绝
  streak:
    agent1_days: 0  # 距上次违规天数
    agent2_days: 5
```

**说明**：v2.2.9先不实现积分赎回和长期追踪，只记录违规供报告使用。

### 4.6 CLI中断机制

#### 4.6.1 技术实现（v2.2.9评估）

**方案A：CLI层面准入检查（推荐）**

```python
# src/cli/enhanced_commands.py

def check_agent_permission(agent_id: str, command: str) -> tuple[bool, str]:
    """检查Agent是否有权限执行命令
    
    Returns:
        (是否允许, 拒绝原因)
    """
    RESTRICTED_COMMANDS = {
        "agent1": ["todowrite", "todoedit", "tododelete"],
        "agent2": ["requirements", "outline", "detailed"]  # 需求/设计创建命令
    }
    
    if agent_id in RESTRICTED_COMMANDS:
        if command in RESTRICTED_COMMANDS[agent_id]:
            return False, f"[{agent_id}] 无权执行 {command}，请创建TODO由对方执行"
    return True, ""


# 在todowrite_command中添加检查
@click.command("todowrite")
@click.argument("content")
def todowrite_command(content: str, ...):
    agent_id = state_manager.get_active_agent()
    
    # Agent1限制检查
    if agent_id == "agent1":
        allowed, reason = check_agent_permission("agent1", "todowrite")
        if not allowed:
            click.echo(f"❌ {reason}")
            click.echo("✅ 正确做法：创建TODO描述，由Agent2执行CLI命令")
            return
    
    # 原有逻辑...
```

**方案B：Compliance Agent中断（更灵活但复杂）**

#### 4.6.2 技术评估

| 维度 | 方案A (CLI准入) | 方案B (Compliance Agent) |
|------|-----------------|--------------------------|
| **改动范围** | ~50行代码 | ~500行代码 |
| **实现难度** | 低 | 高 |
| **维护成本** | 低 | 高 |
| **灵活性** | 固定规则 | 可配置规则 |
| **依赖** | 无 | 需独立服务 |
| **推荐度** | ✅ **v2.2.9推荐** | v2.3.x考虑 |

#### 4.6.3 改动清单（方案A）

| 文件 | 改动内容 | 行数 |
|------|----------|------|
| `src/cli/main.py` | 添加权限检查装饰器 | ~20行 |
| `src/cli/enhanced_commands.py` | 添加check_agent_permission函数 | ~30行 |
| `src/core/compliance_engine.py` | 新增：规则配置 + 违规记录 | 新建(~50行) |
| **总计** | | **~100行** |

---

## 5. 短期方案细化（v2.2.9）

### 5.1 实现内容

| 功能 | 说明 | 工时 | 状态 |
|------|------|------|------|
| 合规目标写入System Prompt | 每次CLI调用时注入目标 | 1h | 待实现 |
| 违规日志记录 | 所有违规行为记录到日志 | 2h | 待实现 |
| CLI准入检查(方案A) | Agent1禁用todowrite/todoedit | 3h | 待实现 |
| 合规报告命令 | `oc-collab compliance report` | 1h | 待实现 |
| **总计** | | **7h** | |

### 5.2 试点命令选择

| 命令 | Agent1 | Agent2 | 选择 |
|------|--------|--------|------|
| `todowrite` | ❌ 禁用 | ✅ 正常 | ✅ 试点 |
| `todoedit` | ❌ 禁用 | ✅ 正常 | ✅ 试点 |
| `todolist` | ✅ 正常 | ✅ 正常 | - |
| `compliance check` | ✅ 正常 | ✅ 正常 | 新命令 |

**试点规则**：
- Agent1执行 `todowrite`/`todoedit` → 拒绝 + 提示创建TODO
- Agent2正常执行

---

## 6. v2.2.9 CLI命令设计

### 6.1 新增命令

| 命令 | 说明 | 位置 |
|------|------|------|
| `oc-collab compliance check` | 检查当前Agent权限 | src/cli/compliance_commands.py |
| `oc-collab compliance report` | 生成合规报告 | src/cli/compliance_commands.py |
| `oc-collab compliance status` | 显示合规率 | src/cli/compliance_commands.py |

### 6.2 命令实现

```python
# src/cli/compliance_commands.py

import click
from pathlib import Path
from datetime import datetime
import yaml


@click.group()
def compliance_group():
    """合规检查命令组。"""
    pass


@compliance_group.command("check")
def compliance_check_command():
    """检查当前Agent的合规状态。"""
    from ..core.state_manager import StateManager
    
    state_manager = StateManager()
    agent_id = state_manager.get_active_agent()
    
    violation_file = Path("state/compliance_violations.yaml")
    violations = []
    if violation_file.exists():
        data = yaml.safe_load(violation_file.read_text())
        violations = data.get("violations", [])
    
    agent_violations = [v for v in violations if v.get("agent_id") == agent_id]
    
    click.echo(f"当前Agent: {agent_id}")
    click.echo(f"违规次数: {len(agent_violations)}")
    click.echo(f"合规率: {max(0, 100 - len(agent_violations))}%")


@compliance_group.command("report")
def compliance_report_command():
    """生成合规报告。"""
    from ..core.state_manager import StateManager
    
    state_manager = StateManager()
    agent_id = state_manager.get_active_agent()
    
    click.echo("=" * 50)
    click.echo("合规报告")
    click.echo("=" * 50)
    click.echo(f"报告时间: {datetime.now().isoformat()}")
    click.echo(f"当前Agent: {agent_id}")
    click.echo("\n提示：请在每次操作前查阅相关Skill")


@compliance_group.command("status")
def compliance_status_command():
    """显示合规状态摘要。"""
    click.echo("合规状态: ✅ 正常")
    click.echo("目标: 95%")
    click.echo("当前: 100%")
```

---

## 7. 待确认事项清单

### 7.1 短期（v2.2.9）

| # | 问题 | 负责人 | 状态 |
|---|------|--------|------|
| 1 | 试点命令选哪个（或两者都试点）？ | Agent2 | ✅ 已定：todowrite/todoedit |
| 2 | System Prompt合规话术是否合适？ | Agent2 | 🔄 评审中（本文案为草案） |
| 3 | 记忆文件格式是否合适？ | Agent2 | 🔄 评审中 |
| 4 | CLI准入检查的拒绝话术？ | Agent2 | 🔄 待定 |

### 7.2 长期（v2.3.0+）

| # | 问题 | 原因 | 状态 |
|---|------|------|------|
| 1 | Compliance Agent是否独立部署？ | 架构决策 | 待讨论 |
| 2 | 积分赎回机制是否需要？ | 长期设计 | 待讨论 |
| 3 | 合规率阈值具体数值？ | 试点后数据 | 待讨论 |
| 4 | 积分影响什么权限？ | 长期设计 | 待讨论 |
| 5 | 违规记录保留策略？ | 长期设计 | 待讨论 |

---

## 6. 后续迭代计划

### Phase 1: 试点验证（v2.2.9）

| 时间 | 内容 | 交付物 |
|------|------|--------|
| Week 1 | 合规目标写入System Prompt | 改动的CLI代码 |
| Week 2 | 违规日志记录功能 | 日志模块 |
| Week 3 | 试点运行，收集数据 | 数据报告 |
| Week 4 | 评估效果，决定下一步 | 评估报告 |

**目标**：
- 验证机制可行
- 收集违规频率、类型数据
- 识别误报情况

### Phase 2: 能力增强（v2.3.0）

| 内容 | 说明 |
|------|------|
| Compliance Agent独立部署 | 专职监督Agent |
| 真正扣分系统 | 积分账本 |
| CLI中断能力 | 严重违规即时中断 |
| 可视化面板 | 合规率仪表盘 |

### Phase 3: 持续优化（v2.3.1+）

| 内容 | 说明 |
|------|------|
| 违规归因分析 | 找出高频违规原因 |
| Skill优化建议 | 根据数据优化Skill |
| 合规率提升 | 从数据驱动改进 |

---

## 8. 行动计划（立即可做）

### 8.1 短期行动（本周）

| # | 行动 | 负责人 | 输出 |
|---|------|--------|------|
| 1 | Agent2评审并确认试点命令 | Agent2 | 决定todowrite/todoedit |
| 2 | 编写System Prompt合规话术 | Agent2 | 话术文案 |
| 3 | 设计记忆文件格式 | 讨论 | compliance_goals.yaml |
| 4 | Agent2评审proposal并给出修改意见 | Agent2 | 评审结论 |

### 8.2 本提案待完成

| # | 行动 | 状态 |
|---|------|------|
| 1 | Agent2评审并确认试点命令 | pending |
| 2 | 完善System Prompt话术 | pending |
| 3 | 更新AGENTS.md添加合规目标 | pending |
| 4 | Agent2技术评审 | pending |
| 5 | 纳入v2.2.9需求文档 | pending |

---

## 9. 关联文档

| 文档 | 说明 |
|------|------|
| `AGENTS.md` | Agent角色分工（严重违规依据） |
| `skills/oc_collab_collaboration_guide/` | Collaboration流程Skill |
| `PROPOSAL-2026-02-002` | 自动Bug检测提案 |
| `PROPOSAL-2026-02-003` | Agent协作增强提案 |

---

## 10. 版本历史

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-02-13 | 初始版本 | Agent1 |
| v1.1 | 2026-02-13 | 补充技术评估、v2.2.9验收标准、CLI命令设计 | Agent1 |

---

**提案状态**: DRAFT  
**下一步**: Agent2评审，确认试点范围和System Prompt话术  
**评审要点**:
1. CLI准入检查方案A的技术可行性
2. System Prompt合规话术是否合适
3. 试点命令选择
4. 验收标准是否完整
