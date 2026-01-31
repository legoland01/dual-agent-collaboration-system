# 需求规格说明书：Bug触发Agent2自动修复功能

**版本**: v1  
**创建日期**: 2026-01-31  
**作者**: Agent 1 (产品经理)

## 1. 背景

在当前的双Agent协作框架中，测试阶段发现的问题（BUG）需要手动触发开发阶段修复。这导致：
- Agent 1 测试发现 bug 后，需要人工介入推进流程
- Agent 2 不会自动激活
- 自动化程度不够高

## 2. 需求概述

### 2.1 功能名称
- **功能名称**: Bug触发Agent2自动修复功能
- **功能编号**: FEATURE-006
- **优先级**: 高

### 2.2 目标
实现测试阶段发现bug时，自动触发Agent 2激活并回退到开发阶段进行修复。

## 3. 功能需求

### 3.1 自动检测Bug
**需求编号**: FR-BUG-001

**描述**: 系统自动检测测试阶段的 `issues_to_fix` 字段

**触发条件**:
- 项目阶段为 `testing`
- `test.issues_to_fix` 字段存在且不为空

**输入**:
```yaml
test:
  status: in_progress
  issues_to_fix:
    - "BUG-001: KeyError 问题"
    - "BUG-002: 健壮性问题"
```

**预期行为**:
- 检测到 bug 列表不为空
- 返回检测结果

### 3.2 自动激活Agent 2
**需求编号**: FR-BUG-002

**描述**: 检测到 bug 后自动激活 Agent 2

**触发条件**:
- FR-BUG-001 检测通过
- 当前活跃 Agent 不是 Agent 2

**输入**:
```yaml
project:
  agents:
    agent1:
      role: 产品经理
      current: true
    agent2:
      role: 开发
      current: false
```

**预期行为**:
- 将 Agent 2 设置为当前活跃 Agent
```yaml
project:
  agents:
    agent1:
      current: false
    agent2:
      current: true
```

### 3.3 自动回退阶段
**需求编号**: FR-BUG-003

**描述**: 检测到 bug 后自动将阶段回退到 development

**触发条件**:
- FR-BUG-001 检测通过
- 当前阶段为 `testing`

**输入**:
```yaml
phase: testing
```

**预期行为**:
- 更新阶段为 `development`
```yaml
phase: development
```

### 3.4 记录历史
**需求编号**: FR-BUG-004

**描述**: 自动记录 bug 检测和 Agent 2 激活的历史

**触发条件**:
- FR-BUG-001、FR-BUG-002、FR-BUG-003 执行成功

**预期行为**:
```yaml
history:
  - id: "xxx"
    timestamp: "2026-01-31T22:00:00"
    action: "bug_detected_agent2_activated"
    agent_id: "system"
    details: "测试发现 2 个 bug，激活 Agent 2 回退到开发阶段修复"
```

### 3.5 无Bug时无操作
**需求编号**: FR-BUG-005

**描述**: 测试通过（无 bug）时，不触发任何操作

**触发条件**:
- 项目阶段为 `testing`
- `test.issues_to_fix` 字段为空或不存在

**输入**:
```yaml
test:
  status: in_progress
  issues_to_fix: []
```

**预期行为**:
- 返回无需处理
- 不改变阶段
- 不改变活跃 Agent

## 4. 非功能需求

### 4.1 性能需求
| 指标 | 要求 |
|------|------|
| 检测延迟 | < 1秒 |
| 状态更新延迟 | < 1秒 |

### 4.2 可靠性需求
- 状态更新需要原子性操作
- 需要记录详细日志

### 4.3 兼容性需求
- 保持与现有阶段推进逻辑的兼容
- 不影响现有的签署流程

## 5. 接口需求

### 5.1 新增方法
```python
class PhaseAdvanceEngine:
    def detect_test_activate_agent_bugs_and2(self) -> Dict[str, Any]:
        """
        检测测试阶段的 bug 并激活 Agent 2
        
        Returns:
            {
                "triggered": bool,
                "bugs_found": int,
                "bugs": List[str],
                "reason": str,
                "message": str
            }
        """
```

### 5.2 集成到自动执行
```python
class AutoCollaborationEngine:
    def run(self, max_iterations: int = 10) -> Dict[str, Any]:
        # 1. 检查并自动推进阶段
        phase_result = self.phase_advance_engine.check_and_advance()
        
        # 1.5 检测测试阶段的 bug 并激活 Agent 2
        bug_result = self.phase_advance_engine.detect_test_activate_agent_bugs_and2()
        
        # 2. ...
```

## 6. 验收标准

### 6.1 功能验收
- [ ] 测试阶段发现 bug 时，Agent 2 自动激活
- [ ] 测试阶段发现 bug 时，阶段自动回退到 development
- [ ] 测试通过时，不触发任何操作
- [ ] 操作记录自动添加到历史

### 6.2 集成验收
- [ ] `oc-collab auto` 命令集成新功能
- [ ] 守护进程模式正常工作

## 7. 依赖关系

### 7.1 前置依赖
- 需求签署功能 (FEATURE-001)
- 阶段推进功能 (FEATURE-003)
- 状态管理功能 (FEATURE-002)

### 7.2 被依赖功能
- Agent 2 工作监听器
- Bug 修复任务执行器

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 误触发 | Agent 2 被错误激活 | 严格检查 `issues_to_fix` 不为空 |
| 状态不一致 | 阶段和 Agent 状态不匹配 | 使用事务性更新 |

## 9. 里程碑

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| 需求评审 | 2026-01-31 | 需求文档 |
| 设计完成 | 2026-01-31 | 设计文档 |
| 开发完成 | 2026-01-31 | 代码和测试 |
| 测试完成 | 2026-01-31 | 测试报告 |
| 发布 | 2026-01-31 | 合并到 main |

## 10. 附录

### 10.1 术语表
| 术语 | 定义 |
|------|------|
| issues_to_fix | 测试阶段记录待修复问题的字段 |
| Agent 1 | 产品经理角色 |
| Agent 2 | 开发角色 |

### 10.2 参考资料
- 《需求规格说明书 v2》(requirements_fully_automated_v2.md)
- 《详细设计文档 v2》(detailed_design_fully_automated_v2.md)
