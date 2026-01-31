# 详细设计文档：项目状态自动更新

## 文档信息

| 项目 | 内容 |
|------|------|
| 设计ID | DES-AUTO-UPDATE-001 |
| 需求ID | REQ-AUTO-UPDATE-001 |
| 版本 | v1 |
| 状态 | 待评审 |
| 创建日期 | 2026-01-31 |

## 1. 系统架构

### 1.1 组件图

```
┌─────────────────────────────────────────────────────────────┐
│              financial_case_generator_system                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 测试执行脚本  │  │ 开发脚本     │  │ 项目更新脚本     │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│         └─────────────────┴────────────────────┘            │
│                           │                                │
│                   ┌───────▼───────┐                        │
│                   │  状态更新模块  │                        │
│                   │ (state_updater│                        │
│                   └───────────────┘                        │
│                           │                                │
│                   ┌───────▼───────┐                        │
│                   │  oc-collab    │                        │
│                   │  project命令  │                        │
│                   └───────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   dual-agent-collaboration-system            │
├─────────────────────────────────────────────────────────────┤
│                   AutoCollaborationEngine                    │
│                           │                                │
│                   ┌───────▼───────┐                        │
│                   │  阶段推进器    │                        │
│                   │ (PhaseAdvance│                        │
│                   └───────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 项目内状态自动更新

### 2.1 状态更新模块

```python
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import yaml

@dataclass
class StateUpdateConfig:
    """状态更新配置"""
    state_file: str = "state/project_state.yaml"
    auto_commit: bool = True

class StateUpdater:
    """状态更新器"""
    
    def __init__(self, project_path: str, config: Optional[StateUpdateConfig] = None):
        self.project_path = Path(project_path)
        self.config = config or StateUpdateConfig()
        self.state_file = self.project_path / self.config.state_file
    
    def load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """保存状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            yaml.dump(state, f)
    
    def update_test_stats(self, blackbox_cases: int = None, 
                          blackbox_passed: int = None,
                          whitebox_passed: int = None) -> bool:
        """更新测试统计"""
        state = self.load_state()
        
        test = state.get('test', {})
        if blackbox_cases is not None:
            test['blackbox_cases'] = blackbox_cases
        if blackbox_passed is not None:
            test['blackbox_passed'] = blackbox_passed
        if whitebox_passed is not None:
            test['whitebox_passed'] = whitebox_passed
        
        test['status'] = 'in_progress'
        state['test'] = test
        state['updated_at'] = datetime.now().isoformat()
        
        self.save_state(state)
        return True
    
    def update_development_status(self, status: str, branch: str = None) -> bool:
        """更新开发状态"""
        state = self.load_state()
        
        dev = state.get('development', {})
        dev['status'] = status
        if branch:
            dev['branch'] = branch
        dev['last_updated'] = datetime.now().isoformat()
        
        state['development'] = dev
        state['updated_at'] = datetime.now().isoformat()
        
        self.save_state(state)
        return True
    
    def update_deployment_status(self, status: str, version: str = None) -> bool:
        """更新部署状态"""
        state = self.load_state()
        
        deploy = state.get('deployment', {})
        deploy['status'] = status
        if version:
            deploy['version'] = version
        deploy['last_updated'] = datetime.now().isoformat()
        
        state['deployment'] = deploy
        state['updated_at'] = datetime.now().isoformat()
        
        self.save_state(state)
        return True
    
    def set_phase(self, phase: str) -> bool:
        """设置阶段"""
        state = self.load_state()
        state['phase'] = phase
        state['updated_at'] = datetime.now().isoformat()
        self.save_state(state)
        return True
```

### 2.2 项目更新命令

```python
@main.command("project")
@click.argument("action", type=click.Choice([
    "update", "advance", "set-phase", "status", "complete"
]))
@click.option("--type", "-t", type=click.Choice([
    "test", "development", "deployment"
]), help="更新类型")
@click.option("--value", "-v", help="更新值")
@click.option("--cases", type=int, help="测试用例数")
@click.option("--passed", type=int, help="通过数")
@click.option("--phase", help="目标阶段")
def project_command(action: str, type: str, value: str, cases: int, 
                    passed: int, phase: str):
    """项目管理命令。"""
    try:
        project_path = get_project_path()
        state_updater = StateUpdater(project_path)
        
        if action == "update":
            if type == "test":
                state_updater.update_test_stats(cases, passed)
                click.echo(f"✓ 测试统计已更新: 用例={cases}, 通过={passed}")
            elif type == "development":
                state_updater.update_development_status(value)
                click.echo(f"✓ 开发状态已更新: {value}")
            elif type == "deployment":
                state_updater.update_deployment_status(value)
                click.echo(f"✓ 部署状态已更新: {value}")
        
        elif action == "set-phase":
            if phase:
                state_updater.set_phase(phase)
                click.echo(f"✓ 阶段已设置为: {phase}")
        
        elif action == "status":
            state = state_updater.load_state()
            phase = state.get('phase', 'unknown')
            test = state.get('test', {})
            dev = state.get('development', {})
            click.echo(f"当前阶段: {phase}")
            click.echo(f"测试状态: {test.get('status', 'unknown')}")
            click.echo(f"开发状态: {dev.get('status', 'unknown')}")
        
        elif action == "complete":
            state_updater.update_development_status("completed")
            click.echo("✓ 开发任务已标记为完成")
            click.echo("请运行 'oc-collab auto' 或手动推进阶段")
        
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)
```

### 2.3 集成钩子示例

在 financial_case_generator_system 的测试脚本中添加：

```python
# run_tests.py
from scripts.state_updater import StateUpdater

def run_tests():
    results = pytest.main(["tests/", "-v"])
    
    # 更新状态
    updater = StateUpdater(".")
    updater.update_test_stats(
        blackbox_cases=total_cases,
        blackbox_passed=passed_cases
    )
    
    if passed_cases == total_cases:
        updater.update_development_status("completed")
    
    return results
```

---

## 3. auto 命令阶段自动推进

### 3.1 阶段推进器

```python
class PhaseAdvanceEngine:
    """阶段推进引擎"""
    
    PHASE_TRANSITIONS = {
        "development": {
            "condition": lambda s: s.get("development", {}).get("status") == "completed",
            "next_phase": "testing",
            "description": "开发完成，自动推进到测试阶段"
        },
        "testing": {
            "condition": lambda s: (
                s.get("test", {}).get("pm_signoff") and 
                s.get("test", {}).get("dev_signoff")
            ),
            "next_phase": "deployment",
            "description": "测试签署完成，自动推进到部署阶段"
        },
        "deployment": {
            "condition": lambda s: s.get("deployment", {}).get("status") == "completed",
            "next_phase": "completed",
            "description": "部署完成，项目已完成"
        }
    }
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.state_manager = StateManager(project_path)
    
    def check_and_advance(self) -> Dict[str, Any]:
        """
        检查条件并推进阶段
        
        Returns:
            {
                "advanced": bool,
                "from_phase": str,
                "to_phase": str,
                "reason": str
            }
        """
        state = self.state_manager.load_state()
        current_phase = state.get("phase", "")
        
        transition = self.PHASE_TRANSITIONS.get(current_phase)
        if not transition:
            return {
                "advanced": False,
                "from_phase": current_phase,
                "to_phase": current_phase,
                "reason": "当前阶段不支持自动推进"
            }
        
        condition = transition["condition"]
        if condition(state):
            next_phase = transition["next_phase"]
            reason = transition["description"]
            
            # 执行阶段推进
            self.state_manager.update_phase(next_phase)
            
            # 添加历史记录
            self.state_manager.add_history_entry(
                action="auto_phase_advance",
                agent_id="system",
                details=reason
            )
            
            return {
                "advanced": True,
                "from_phase": current_phase,
                "to_phase": next_phase,
                "reason": reason
            }
        
        return {
            "advanced": False,
            "from_phase": current_phase,
            "to_phase": current_phase,
            "reason": "条件未满足，无法推进"
        }
    
    def manual_advance(self, target_phase: str = None) -> Dict[str, Any]:
        """
        手动推进阶段
        
        Args:
            target_phase: 目标阶段（默认下一阶段）
        """
        state = self.state_manager.load_state()
        current_phase = state.get("phase", "")
        
        if target_phase is None:
            transition = self.PHASE_TRANSITIONS.get(current_phase)
            if transition:
                target_phase = transition["next_phase"]
            else:
                return {"success": False, "error": "无法确定下一阶段"}
        
        self.state_manager.update_phase(target_phase)
        
        return {
            "success": True,
            "from_phase": current_phase,
            "to_phase": target_phase
        }
```

### 3.2 增强 AutoCollaborationEngine

在 `AutoCollaborationEngine.run()` 中添加阶段推进检查：

```python
def run(self, max_iterations: int = None) -> Dict[str, Any]:
    # ... 现有代码 ...
    
    for i in range(max_iterations):
        self.current_iteration = i + 1
        
        # 1. 检查并推进阶段
        phase_result = self.phase_advance_engine.check_and_advance()
        if phase_result["advanced"]:
            self.execution_history.append({
                "action": "phase_advance",
                "from": phase_result["from_phase"],
                "to": phase_result["to_phase"],
                "reason": phase_result["reason"]
            })
        
        # 2. 检测状态
        state = self.detect_state()
        if state.get("completed"):
            break
        
        # 3. 执行任务
        agent = self.get_active_agent()
        result = self.execute_task(state, agent)
        self.execution_history.append(result)
        
        # 4. 同步 Git
        if result.get("git_synced"):
            self.sync_git()
        
        # 5. 检查完成
        if self.check_completion():
            break
    
    return self._generate_summary()
```

### 3.3 新增 CLI 命令

```python
@main.command("advance")
@click.option("--phase", "-p", help="目标阶段")
@click.option("--force", "-f", is_flag=True, help="强制推进")
def advance_command(phase: str, force: bool):
    """推进到下一阶段。"""
    try:
        project_path = get_project_path()
        phase_engine = PhaseAdvanceEngine(project_path)
        
        if phase:
            if force:
                result = phase_engine.manual_advance(phase)
                if result["success"]:
                    click.echo(f"✓ 已从 {result['from_phase']} 推进到 {result['to_phase']}")
            else:
                click.echo("使用 --force 强制推进到指定阶段")
        else:
            result = phase_engine.check_and_advance()
            if result["advanced"]:
                click.echo(f"✓ 自动推进: {result['from_phase']} → {result['to_phase']}")
                click.echo(f"  原因: {result['reason']}")
            else:
                click.echo(f"无法自动推进: {result['reason']}")
    
    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)
```

---

## 4. 使用示例

### 4.1 项目内使用

```bash
# 更新测试统计
oc-collab project update --type test --cases 100 --passed 95

# 更新开发状态
oc-collab project update --type development --value in_progress

# 标记开发完成
oc-collab project complete

# 设置特定阶段
oc-collab project set-phase testing

# 查看状态
oc-collab project status
```

### 4.2 dual-agent 使用

```bash
# 自动推进阶段（开发完成后）
oc-collab auto

# 手动推进
oc-collab advance

# 强制推进到指定阶段
oc-collab advance --phase testing --force
```

### 4.3 集成到脚本

```python
# run_tests.py
import pytest
from scripts.state_updater import StateUpdater

def main():
    # 执行测试
    results = pytest.main(["tests/", "-v", "--tb=short"])
    
    # 计算测试统计
    total = 100
    passed = 95
    
    # 更新状态
    updater = StateUpdater(".")
    updater.update_test_stats(blackbox_cases=total, blackbox_passed=passed)
    
    # 如果全部通过，标记开发完成
    if passed == total:
        updater.update_development_status("completed")
        print("✓ 开发完成，请运行 'oc-collab advance' 推进阶段")

if __name__ == "__main__":
    main()
```

---

## 5. 测试用例

### 5.1 单元测试

| 测试项 | 输入 | 预期输出 |
|-------|------|---------|
| 更新测试统计 | cases=100, passed=95 | blackbox_cases=100, blackbox_passed=95 |
| 更新开发状态 | status="completed" | development.status="completed" |
| 阶段自动推进 | development.status="completed" | phase="testing" |
| 条件不满足不推进 | development.status="in_progress" | phase不变 |

### 5.2 集成测试

| 测试项 | 说明 |
|-------|------|
| 测试脚本集成 | 测试执行后状态自动更新 |
| auto 命令 | 阶段自动推进功能 |

---

## 6. 实施计划

| 阶段 | 任务 | 优先级 |
|------|------|--------|
| 1 | 实现 StateUpdater | P0 |
| 2 | 实现 project 命令 | P0 |
| 3 | 实现 PhaseAdvanceEngine | P0 |
| 4 | 增强 auto 命令 | P0 |
| 5 | 集成到 financial_case_generator_system | P1 |
| 6 | 编写测试 | P1 |

---

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| v1 | 2026-01-31 | Agent 1 | 初始设计 |
