# 详细设计文档：Bug触发Agent2自动修复功能

**版本**: v1  
**创建日期**: 2026-01-31  
**作者**: Agent 1 (产品经理)

## 1. 概述

### 1.1 功能简介
本设计文档描述了"测试阶段发现bug时自动触发Agent 2激活并回退到开发阶段"功能的详细实现方案。

### 1.2 模块位置
```
dual-agent-collaboration-system/
├── src/
│   └── core/
│       ├── phase_advance.py      # 新增功能实现
│       └── auto_engine.py        # 集成到自动执行流程
```

## 2. 架构设计

### 2.1 整体流程
```
┌─────────────────────────────────────────────────────────────────┐
│                        测试阶段 (testing)                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Agent 1 执行测试，发现 bug                               │    │
│  │  更新 state: test.issues_to_fix = [bug1, bug2, ...]      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  运行 oc-collab auto                                     │    │
│  │  或 Agent Auto Runner 守护进程                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  PhaseAdvanceEngine.detect_test_activate_agent_bugs_and2 │    │
│  │  ├─ 检测阶段是否为 testing                               │    │
│  │  ├─ 检测 issues_to_fix 是否非空                          │    │
│  │  └─ 检测通过则触发处理                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│              ┌───────────────┴───────────────┐                  │
│              ▼                               ▼                  │
│  ┌─────────────────────┐     ┌─────────────────────┐           │
│  │ 条件不满足: 无操作   │     │ 条件满足: 执行处理   │           │
│  │ 返回: triggered=0   │     │ ├─ 激活 Agent 2      │           │
│  └─────────────────────┘     │ ├─ 回退阶段到 dev    │           │
│                              │ └─ 记录历史          │           │
│                              └─────────────────────┘           │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  状态已更新: phase=development, agent2.current=true      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Agent 2 激活，开始修复 bug                              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 3. 类设计

### 3.1 PhaseAdvanceEngine 新增方法

#### 3.1.1 detect_test_activate_agent_bugs_and2

**方法签名**:
```python
def detect_test_activate_agent_bugs_and2(self) -> Dict[str, Any]:
    """
    检测测试阶段的 bug 并激活 Agent 2
    
    当测试阶段发现 issues_to_fix 时：
    1. 激活 Agent 2
    2. 将阶段回退到 development
    
    Returns:
        {
            "triggered": bool,           # 是否触发了处理
            "bugs_found": int,           # 发现的 bug 数量
            "bugs": List[str],           # bug 列表
            "reason": str,               # 触发原因
            "message": str,              # 用户友好的消息
            "error": str (可选)          # 错误信息
        }
    """
```

**实现逻辑**:

```python
def detect_test_activate_agent_bugs_and2(self) -> Dict[str, Any]:
    """
    检测测试阶段的 bug 并激活 Agent 2
    """
    state = self.state_manager.load_state()
    phase = state.get("phase", "")
    
    # 1. 只在测试阶段检测
    if phase != "testing":
        return {
            "triggered": False,
            "reason": "当前不在 testing 阶段",
            "message": f"阶段为 {phase}，无需处理"
        }
    
    # 2. 获取 bug 列表
    test_data = state.get("test", {})
    issues = test_data.get("issues_to_fix", [])
    
    # 3. 没有发现 bug，不触发
    if not issues or len(issues) == 0:
        return {
            "triggered": False,
            "reason": "无待修复的 bug",
            "message": "测试通过，无 bug 需要修复"
        }
    
    # 4. 检测到 bug，激活 Agent 2 并回退到开发阶段
    try:
        # 4.1 激活 Agent 2
        project_agents = state.get("project", {}).get("agents", {})
        for agent_id in project_agents:
            project_agents[agent_id]["current"] = (agent_id == "agent2")
        
        # 4.2 更新状态
        state["project"]["agents"] = project_agents
        state["phase"] = "development"
        state["updated_at"] = datetime.now().isoformat()
        
        # 4.3 保存状态
        self.state_manager.save_state(state)
        
        # 4.4 记录历史
        self.state_manager.add_history_entry(
            action="bug_detected_agent2_activated",
            agent_id="system",
            details=f"测试发现 {len(issues)} 个 bug，激活 Agent 2 回退到开发阶段修复"
        )
        
        return {
            "triggered": True,
            "bugs_found": len(issues),
            "bugs": issues,
            "reason": "测试发现 bug，触发 Agent 2 修复",
            "message": f"✓ 检测到 {len(issues)} 个 bug，激活 Agent 2 并回退到 development 阶段"
        }
    
    except Exception as e:
        return {
            "triggered": False,
            "error": str(e),
            "message": f"处理失败: {e}"
        }
```

### 3.2 AutoCollaborationEngine 集成

**修改位置**: `src/core/auto_engine.py` 的 `run()` 方法

**修改内容**:

```python
def run(self, max_iterations: Optional[int] = None) -> Dict[str, Any]:
    """执行自动协作流程。"""
    # ... 前置代码 ...
    
    for i in range(max_iterations):
        self.current_iteration = i + 1
        
        if not self.is_running:
            break
        
        # 1. 检查并自动推进阶段
        phase_result = self.phase_advance_engine.check_and_advance()
        if phase_result["advanced"]:
            self.execution_history.append({
                "action": "phase_advance",
                "from": phase_result["from_phase"],
                "to": phase_result["to_phase"],
                "reason": phase_result["reason"]
            })
        
        # 1.5 检测测试阶段的 bug 并激活 Agent 2 (新增)
        bug_result = self.phase_advance_engine.detect_test_activate_agent_bugs_and2()
        if bug_result.get("triggered"):
            self.execution_history.append({
                "action": "bug_detected_agent2_activated",
                "bugs_count": bug_result.get("bugs_found"),
                "bugs": bug_result.get("bugs", [])
            })
        
        # 2. 检测状态
        # ... 后续代码 ...
```

## 4. 数据结构

### 4.1 状态文件变更

**变更前**:
```yaml
phase: testing
test:
  status: in_progress
  issues_to_fix:
    - "BUG-001: 问题1"
    - "BUG-002: 问题2"
project:
  agents:
    agent1:
      current: true
    agent2:
      current: false
```

**变更后**:
```yaml
phase: development
test:
  status: passed
  issues_to_fix:
    - "BUG-001: 问题1"
    - "BUG-002: 问题2"
project:
  agents:
    agent1:
      current: false
    agent2:
      current: true
history:
  - action: bug_detected_agent2_activated
    agent_id: system
    details: "测试发现 2 个 bug，激活 Agent 2 回退到开发阶段修复"
```

### 4.2 返回值结构

**成功返回**:
```json
{
  "triggered": true,
  "bugs_found": 2,
  "bugs": ["BUG-001: 问题1", "BUG-002: 问题2"],
  "reason": "测试发现 bug，触发 Agent 2 修复",
  "message": "✓ 检测到 2 个 bug，激活 Agent 2 并回退到 development 阶段"
}
```

**无需处理返回**:
```json
{
  "triggered": false,
  "reason": "无待修复的 bug",
  "message": "测试通过，无 bug 需要修复"
}
```

**不在测试阶段返回**:
```json
{
  "triggered": false,
  "reason": "当前不在 testing 阶段",
  "message": "阶段为 development，无需处理"
}
```

**错误返回**:
```json
{
  "triggered": false,
  "error": "状态文件写入失败",
  "message": "处理失败: 状态文件写入失败"
}
```

## 5. 异常处理

### 5.1 异常场景

| 场景 | 处理方式 | 记录 |
|------|----------|------|
| 状态文件读取失败 | 返回错误 | 日志 |
| 状态文件写入失败 | 返回错误 | 日志 |
| 项目结构不完整 | 返回错误 | 日志 |
| agents 字段不存在 | 返回错误 | 日志 |

### 5.2 日志记录

```python
import logging

logger = logging.getLogger(__name__)

# 成功触发
logger.info(f"Bug 检测触发: {len(issues)} 个 bug，Agent 2 已激活")

# 无需处理
logger.info(f"Bug 检测跳过: 无待修复的 bug")

# 错误
logger.error(f"Bug 检测失败: {e}")
```

## 6. 测试用例

### 6.1 正常流程测试

| 用例编号 | 用例描述 | 输入 | 预期输出 |
|----------|----------|------|----------|
| TC-BUG-001 | 测试阶段发现 bug | phase=testing, issues_to_fix=[bug1, bug2] | triggered=true, phase=development, agent2=true |
| TC-BUG-002 | 测试阶段无 bug | phase=testing, issues_to_fix=[] | triggered=false, 无状态变更 |
| TC-BUG-003 | 非测试阶段 | phase=development, issues_to_fix=[bug1] | triggered=false, 无状态变更 |

### 6.2 边界条件测试

| 用例编号 | 用例描述 | 输入 | 预期输出 |
|----------|----------|------|----------|
| TC-BUG-004 | issues_to_fix 为 None | phase=testing, issues_to_fix=null | triggered=false |
| TC-BUG-005 | test 字段不存在 | phase=testing, test=null | triggered=false |
| TC-BUG-006 | project.agents 不存在 | phase=testing, agents=null | 返回错误 |

## 7. 安全性考虑

### 7.1 状态完整性
- 使用原子性写入确保状态一致性
- 写入前备份状态

### 7.2 权限控制
- 系统自动操作，无需用户权限验证
- 记录操作来源为 "system"

## 8. 性能考虑

### 8.1 时间复杂度
- 检测逻辑: O(1) - 直接读取字段
- 状态更新: O(1) - 简单字段修改

### 8.2 资源消耗
- 内存: O(1) - 仅存储状态引用
- 磁盘: O(1) - 状态文件写入

## 9. 兼容性

### 9.1 向后兼容
- 不影响现有阶段推进逻辑
- 不修改现有数据结构
- 保持历史记录格式一致

### 9.2 依赖
- PhaseAdvanceEngine 现有功能
- StateManager 现有功能
- 无外部依赖

## 10. 部署说明

### 10.1 部署步骤
1. 部署更新的 `phase_advance.py`
2. 部署更新的 `auto_engine.py`
3. 重启 Agent Auto Runner 守护进程

### 10.2 验证步骤
1. 创建一个处于 testing 阶段的测试项目
2. 添加 bug 到 issues_to_fix
3. 运行 `oc-collab auto`
4. 验证阶段变为 development
5. 验证 Agent 2 被激活
