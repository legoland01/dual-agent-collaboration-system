# 详细设计：双代理认知免疫系统

**设计文档ID**: DETAIL-2026-02-M5
**版本**: v1
**日期**: 2026-02-05
**作者**: Agent 2 (开发负责人)
**状态**: DRAFT

---

## 1. 概述

### 1.1 功能描述

检测 Agent 的困惑信号，自动加载协作指南 Skill，提供职责边界提醒，动态仓库配置。

**核心功能**:
- 会话起始引导：Agent 新会话自动显示角色职责
- 困惑信号检测：检测 Agent 的困惑信号
- 协作指南 Skill 自动加载
- 职责边界提醒
- 动态仓库配置

### 1.2 相关需求

- FR-COGNITIVE-001: 会话起始引导
- FR-COGNITIVE-002: 困惑信号检测
- FR-COGNITIVE-003: 协作指南 Skill 自动加载
- FR-COGNITIVE-004: 职责边界提醒

---

## 2. 技术设计

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────┐
│              双代理认知免疫系统                           │
├─────────────────────────────────────────────────────────┤
│  检测层                                                  │
│  ├── 会话起始引导器 (SessionStarter)                     │
│  ├── 困惑信号检测器 (ConfusionDetector)                  │
│  ├── 职责边界检测器 (ResponsibilityDetector)             │
│  └── 仓库配置检测器 (RepositoryDetector)                 │
├─────────────────────────────────────────────────────────┤
│  响应层                                                  │
│  ├── Skill 自动加载器 (SkillLoader)                     │
│  └── 提醒生成器 (ReminderGenerator)                       │
├─────────────────────────────────────────────────────────┤
│  配置层                                                  │
│  ├── 协作指南 Skill                                      │
│  └── 职责定义配置                                        │
└─────────────────────────────────────────────────────────┘
```

### 2.2 会话起始引导

```python
class SessionStarter:
    """会话起始引导器"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_manager = StateManager(project_path)

    def get_welcome_message(self, agent_id: str) -> str:
        """生成欢迎消息和上下文信息"""
        state = self.state_manager.get_state()
        responsibilities = self._get_responsibilities(agent_id)

        message = f"""=== {agent_id} ===

当前项目: {state.get('project_name', 'unknown')}
当前阶段: {state.get('phase', 'unknown')}
当前里程碑: {state.get('milestone', 'unknown')}

你的职责:
{self._format_responsibilities(responsibilities)}

待办事项:
{self._format_todos(agent_id)}

常用命令:
  - oc-collab status    查看状态
  - oc-collab review    评审
  - oc-collab signoff   签署
"""
        return message

    def display_welcome(self, agent_id: str):
        """显示欢迎消息"""
        message = self.get_welcome_message(agent_id)
        click.echo(message)
```

### 2.3 困惑信号检测

```python
CONFUSION_SIGNALS = [
    "我不知道",
    "我不太清楚",
    "我不确定",
    "我不明白",
    "我需要更多信息",
    "怎么做",
    "请告诉我",
    "帮我",
]

class ConfusionDetector:
    """困惑信号检测器"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_manager = StateManager(project_path)

    def detect_confusion(self, message: str) -> ConfusionResult:
        """检测困惑信号"""
        confusions = []

        for signal in CONFUSION_SIGNALS:
            if signal.lower() in message.lower():
                confusions.append(signal)

        if confusions:
            return ConfusionResult(
                detected=True,
                signals=confusions,
                message="检测到困惑信号",
                suggestion=self._generate_suggestion(confusions)
            )

        return ConfusionResult(detected=False)

    def _generate_suggestion(self, confusions: List[str]) -> str:
        """生成建议"""
        suggestions = {
            "我不知道": "请参考协作指南 Skill: oc_collab_collaboration_guide",
            "我不确定": "请参考当前阶段的签署记录",
            "怎么做": "请参考详细设计文档",
        }

        for signal in confusions:
            if signal in suggestions:
                return suggestions[signal]

        return "请查看项目状态: oc-collab status"
```

### 2.3 职责边界检测

```python
AGENT_RESPONSIBILITIES = {
    "agent1": {
        "role": "产品经理",
        "responsibilities": [
            "编写和评审需求文档",
            "定义验收标准",
            "签署需求确认",
            "评审设计文档",
            "评审测试报告"
        ],
        "boundaries": [
            "不直接执行开发任务",
            "不绕过评审流程",
        ]
    },
    "agent2": {
        "role": "开发负责人",
        "responsibilities": [
            "评审需求文档",
            "编写详细设计",
            "代码实现",
            "编写单元测试",
            "签署技术确认"
        ],
        "boundaries": [
            "不修改需求文档",
            "不跳过测试流程",
        ]
    }
}

class ResponsibilityDetector:
    """职责边界检测器"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_manager = StateManager(project_path)

    def check_responsibility(self, agent_id: str, action: str) -> ResponsibilityResult:
        """检查职责边界"""
        agent = AGENT_RESPONSIBILITIES.get(agent_id, {})
        responsibilities = agent.get("responsibilities", [])
        boundaries = agent.get("boundaries", [])

        # 检查是否越界
        for boundary in boundaries:
            if boundary in action:
                return ResponsibilityResult(
                    violated=True,
                    message=f"⚠️ 职责边界提醒: {boundary}",
                    suggestion=f"这是 {agent.get('role', '未知')} 的职责范围"
                )

        # 检查是否在职责范围内
        for resp in responsibilities:
            if resp in action:
                return ResponsibilityResult(
                    valid=True,
                    message=f"✓ {resp} - 在职责范围内"
                )

        return ResponsibilityResult(unknown=True)
```

---

## 3. 实现方案

### 3.1 认知免疫系统核心

```python
class CognitiveImmuneSystem:
    """双代理认知免疫系统"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.confusion_detector = ConfusionDetector(project_path)
        self.responsibility_detector = ResponsibilityDetector(project_path)
        self.repository_detector = RepositoryDetector(project_path)
        self.skill_loader = SkillLoader(project_path)

    def analyze_message(self, agent_id: str, message: str) -> ImmuneResponse:
        """分析消息，返回免疫响应"""
        responses = []

        # 1. 检测困惑信号
        confusion = self.confusion_detector.detect_confusion(message)
        if confusion.detected:
            responses.append(confusion)

        # 2. 检测职责边界
        responsibility = self.responsibility_detector.check_responsibility(agent_id, message)
        if responsibility.violated:
            responses.append(responsibility)

        return ImmuneResponse(responses=responses)
```

### 3.2 CLI 集成

```bash
# 查看当前 Agent 职责
oc-collab agent responsibilities

# 查看职责边界
oc-collab agent boundaries

# 检测困惑信号
oc-collab agent detect --message "我不知道怎么做"

# 加载协作指南
oc-collab agent load-skill collaboration

# 动态查看仓库配置
oc-collab repo status
```

### 3.3 Skill 自动加载

```python
class SkillLoader:
    """Skill 自动加载器"""

    SKILLS = {
        "collaboration": "skills/oc_collab_collaboration_guide/",
        "workflow": "skills/oc_collab_workflow/",
        "signoff": "skills/oc_collab_signoff/",
    }

    def load_skill(self, skill_name: str) -> LoadResult:
        """加载 Skill"""
        skill_path = self.SKILLS.get(skill_name)

        if skill_path and Path(skill_path).exists():
            # 加载 Skill 内容
            skill_content = self._read_skill(skill_path)
            return LoadResult(success=True, content=skill_content)

        return LoadResult(success=False, message=f"Skill {skill_name} 不存在")
```

---

## 4. 测试用例

### 4.1 困惑检测测试

```python
def test_confusion_detection():
    """测试困惑信号检测"""
    detector = ConfusionDetector(project_path)

    result = detector.detect_confusion("我不知道怎么做")
    assert result.detected is True
    assert "我不知道" in result.signals

    result = detector.detect_confusion("我来实现这个功能")
    assert result.detected is False
```

### 4.2 职责边界测试

```python
def test_responsibility_boundary():
    """测试职责边界检测"""
    detector = ResponsibilityDetector(project_path)

    # Agent 1 不应该执行开发任务
    result = detector.check_responsibility("agent1", "我来写代码")
    assert result.violated is True

    # Agent 2 应该执行开发任务
    result = detector.check_responsibility("agent2", "我来写代码")
    assert result.valid is True
```

---

## 5. 验收标准

| 标准 | 验证方式 |
|------|----------|
| 困惑信号检测准确 | CLI 测试 |
| 职责边界检测准确 | CLI 测试 |
| Skill 加载成功 | CLI 测试 |
| 提醒消息清晰 | 代码审查 |

---

**设计版本**: v1
**创建日期**: 2026-02-05
**状态**: DRAFT
