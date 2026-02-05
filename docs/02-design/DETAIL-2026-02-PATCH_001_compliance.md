# 详细设计：流程合规检查机制 (PATCH-001)

**设计文档ID**: DETAIL-2026-02-PATCH_001
**版本**: v1
**日期**: 2026-02-05
**作者**: Agent 2 (开发负责人)
**状态**: DRAFT
**叠加设计**: DETAIL-2026-02-M1 ~ DETAIL-2026-02-M5

---

## 1. 概述

### 1.1 功能描述

修复 BUG-20260205-001：Agent 流程合规性不足。实现流程合规检查机制，使 Agent 能够自主维持正确的流程状态。

### 1.2 与现有设计的关系

```
┌─────────────────────────────────────────────────────────┐
│              v2.2.1 现有设计架构                         │
├─────────────────────────────────────────────────────────┤
│  DETAIL-M1: 签署自动同步                                │
│  DETAIL-M2: 变更载体明确化                              │
│  DETAIL-M3: 签署流程改进                                │
│  DETAIL-M4: 动态 Checklist                             │
│  DETAIL-M5: 双代理认知免疫系统                          │
├─────────────────────────────────────────────────────────┤
│              PATCH-001 叠加扩展                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 流程合规检查机制 (FR-COMPLIANCE-001)             │   │
│  │ ├── 状态合规检查 → 复用/扩展 M3 state_validator  │   │
│  │ ├── 主动流程推理 → 新增 workflow_inference.py     │   │
│  │ └── 流程规范持久化 → 扩展 M5 session_manager     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 技术设计

### 2.1 叠加架构

```python
# src/core/workflow_inference.py (新增)

class WorkflowInferenceEngine:
    """主动流程推理引擎"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_manager = StateManager(project_path)
        self.workflow_engine = WorkflowEngine(project_path)
        self.validator = StateValidator(project_path)

    def infer_next_action(self) -> InferenceResult:
        """
        根据当前状态推理下一步应该执行的操作
        
        推理逻辑:
        1. 获取当前项目状态
        2. 查询 oc-collab 流程规范
        3. 匹配当前状态与规范
        4. 推导出应该执行的操作
        """
        current_state = self.state_manager.load_state()
        phase = current_state.get("phase", "unknown")

        # 流程状态机
        PHASE_SEQUENCE = {
            "requirements": ["design", "development", "testing"],
            "design": ["development", "testing"],
            "development": ["testing"],
            "testing": ["deployment"],
        }

        # 推理下一步
        if phase in PHASE_SEQUENCE:
            next_phases = PHASE_SEQUENCE[phase]
            return InferenceResult(
                current_phase=phase,
                next_phases=next_phases,
                suggestion=self._generate_suggestion(phase, next_phases),
                compliance_check=self._run_compliance_check(phase)
            )

        return InferenceResult(unknown=True)

    def _generate_suggestion(self, current_phase: str, next_phases: List[str]) -> str:
        """生成主动提示"""
        if len(next_phases) == 1:
            return f"当前阶段: {current_phase}\n建议: 进入 {next_phases[0]} 阶段"
        else:
            return f"当前阶段: {current_phase}\n可选: {' / '.join(next_phases)}"

    def _run_compliance_check(self, phase: str) -> ComplianceResult:
        """运行合规检查"""
        return self.validator.validate_phase_transition(phase)
```

### 2.2 扩展 StateValidator

```python
# src/core/state_validator.py (扩展)

class ComplianceRule(Enum):
    DRAFT_CANNOT_REVIEW = "DRAFT 状态不能评审"
    DRAFT_CANNOT_SIGNOFF = "DRAFT 状态不能签署"
    REVIEW_REQUIRES_READY = "评审前必须 READY"
    PHASE_SEQUENCE_REQUIRED = "必须按流程顺序执行"

class ExtendedStateValidator(StateValidator):
    """扩展的状态验证器 - 支持流程合规检查"""

    COMPLIANCE_RULES = {
        ComplianceRule.DRAFT_CANNOT_REVIEW: True,
        ComplianceRule.DRAFT_CANNOT_SIGNOFF: True,
        ComplianceRule.REVIEW_REQUIRES_READY: True,
        ComplianceRule.PHASE_SEQUENCE_REQUIRED: True,
    }

    def validate_compliance(self, action: str, context: dict) -> ComplianceResult:
        """
        验证操作是否符合 oc-collab 流程规范
        
        Args:
            action: 要执行的操作 (e.g., "review", "signoff", "advance")
            context: 操作上下文
        
        Returns:
            ComplianceResult: 包含验证结果和建议
        """
        violations = []
        warnings = []

        # 检查文档状态
        if action in ["review", "signoff"]:
            doc_status = context.get("document_status")
            if doc_status == "DRAFT":
                if self.COMPLIANCE_RULES[ComplianceRule.DRAFT_CANNOT_REVIEW if action == "review" else ComplianceRule.DRAFT_CANNOT_SIGNOFF]:
                    violations.append(f"{doc_status} 状态不能执行 {action}")

        # 检查阶段顺序
        if action == "advance":
            current_phase = context.get("current_phase")
            target_phase = context.get("target_phase")
            if not self._is_valid_phase_sequence(current_phase, target_phase):
                violations.append(f"阶段顺序不正确: {current_phase} → {target_phase}")

        return ComplianceResult(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings
        )
```

### 2.3 扩展 SessionManager (流程规范持久化)

```python
# src/core/session_manager.py (扩展)

class ExtendedSessionManager(SessionManager):
    """扩展的会话管理器 - 支持流程规范持久化"""

    def __init__(self, project_path: str):
        super().__init__(project_path)
        self.process_guide_path = Path(project_path) / "skills" / "oc_collab_process_guide"

    def load_process_guide(self) -> str:
        """加载流程规范指南"""
        guide_file = self.process_guide_path / "process_guide.md"

        if guide_file.exists():
            with open(guide_file) as f:
                return f.read()

        return self._get_default_process_guide()

    def _get_default_process_guide(self) -> str:
        """获取默认流程规范"""
        return """
# oc-collab 流程规范

## 核心流程
1. 需求阶段 → 评审 → 签署
2. 设计阶段 → 评审 → 签署
3. 开发阶段 → 实现 → 测试
4. 测试阶段 → 验收 → 签署

## 关键规则
- DRAFT 状态不能评审
- 评审前必须 READY
- 必须按流程顺序执行
- 签署后自动同步
        """

    def get_welcome_message(self, agent_id: str) -> str:
        """生成欢迎信息 - 包含流程规范提示"""
        message = super().get_welcome_message(agent_id)

        # 添加流程状态提示
        project_info = self.get_project_info()
        phase = project_info.get("phase", "unknown")

        workflow_status = self._get_workflow_status(phase)
        message += f"\n当前流程状态: {workflow_status}"

        return message

    def _get_workflow_status(self, phase: str) -> str:
        """获取工作流状态"""
        return f"[{phase.upper()}] - 下一步: {self._get_next_phase_suggestion(phase)}"

    def _get_next_phase_suggestion(self, phase: str) -> str:
        """获取下一阶段建议"""
        PHASE_NEXT = {
            "requirements": "设计阶段",
            "design": "开发阶段",
            "development": "测试阶段",
            "testing": "部署阶段",
            "unknown": "请先初始化项目",
        }
        return PHASE_NEXT.get(phase, phase.upper())
```

---

## 3. CLI 集成

### 3.1 新增命令

```python
# src/cli/main.py (添加)

@main.command("workflow")
def workflow_command():
    """查看当前工作流状态和推理"""
    try:
        project_path = get_project_path()
        inference_engine = WorkflowInferenceEngine(project_path)

        result = inference_engine.infer_next_action()

        if result.unknown:
            click.echo("⚠️ 无法确定当前流程状态")
            click.echo("请先初始化项目: oc-collab project init")
        else:
            click.echo(f"当前阶段: {result.current_phase}")
            click.echo(f"\n建议: {result.suggestion}")

            if result.compliance_check.valid:
                click.echo("\n✅ 流程合规")
            else:
                click.echo("\n⚠️ 流程不合规:")
                for violation in result.compliance_check.violations:
                    click.echo(f"  - {violation}")

    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)
```

### 3.2 命令示例

```bash
# 查看当前流程状态和推理
oc-collab workflow

# 查看合规检查结果
oc-collab workflow --check

# 查看下一步建议
oc-collab workflow --suggest
```

---

## 4. 与现有模块的集成关系

| 现有模块 | PATCH-001 叠加方式 |
|----------|-------------------|
| state_validator.py | 扩展 `validate_phase_transition()` |
| state_machine.py | 复用状态机逻辑 |
| session_manager.py | 扩展 `load_process_guide()` |
| workflow.py | 复用 `infer_next_action()` |

---

## 5. 测试用例

### 5.1 流程推理测试

```python
def test_infer_next_action():
    """测试主动流程推理"""
    engine = WorkflowInferenceEngine(project_path)

    result = engine.infer_next_action()

    if result.current_phase == "requirements":
        assert "design" in result.next_phases
        assert "建议" in result.suggestion
```

### 5.2 合规检查测试

```python
def test_compliance_check_draft():
    """测试 DRAFT 状态合规检查"""
    validator = ExtendedStateValidator(project_path)

    result = validator.validate_compliance(
        action="review",
        context={"document_status": "DRAFT"}
    )

    assert result.valid is False
    assert any("DRAFT" in v for v in result.violations)
```

---

## 6. 验收标准

| 标准 | 验证方式 |
|------|----------|
| DRAFT 状态不能执行评审 | CLI 测试 |
| 需求签署后自动提示进入设计阶段 | 集成测试 |
| 会话开始时自动加载流程规范 | CLI 测试 |
| workflow 命令正确推理下一步 | CLI 测试 |

---

**设计版本**: v1
**创建日期**: 2026-02-05
**状态**: DRAFT

**叠加说明**: 本设计基于 v2.2.1 现有设计 (M1-M5)，仅扩展必要模块，不影响已有功能。
