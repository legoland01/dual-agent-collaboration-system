"""双代理认知免疫系统模块。"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import yaml
import re


CONFUSION_SIGNALS = [
    "我不明白",
    "不太清楚",
    "可能需要",
    "让我想想",
    "这个怎么做",
    "应该怎么做",
    "你怎么认为",
    "你希望我",
    "我不太确定",
    "这个任务是什么",
    "我需要更多信息",
    "这个需求不明确",
    "我有点困惑",
    "这不太对",
    "这不太合理"
]


RESPONSIBILITY_MATRIX = {
    "agent1": {
        "roles": ["产品经理", "产品负责人", "PM"],
        "responsibilities": [
            "编写需求文档 (requirements_*.md)",
            "评审设计文档",
            "签署需求和设计",
            "确认验收标准",
            "管理项目状态"
        ],
        "forbidden": [
            "直接修改代码",
            "签署开发相关文档"
        ]
    },
    "agent2": {
        "roles": ["开发负责人", "开发者", "开发"],
        "responsibilities": [
            "实现功能代码",
            "编写单元测试",
            "评审需求文档",
            "编写设计文档",
            "签署设计和测试"
        ],
        "forbidden": [
            "签署需求文档",
            "修改验收标准"
        ]
    }
}


@dataclass
class ImmuneResponse:
    """免疫响应"""
    detected: bool
    response_type: str
    message: str
    suggestions: List[str] = field(default_factory=list)


class CognitiveImmuneSystem:
    """双代理认知免疫系统"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.session_starter = SessionStarter(project_path)
        self.confusion_detector = ConfusionDetector()
        self.responsibility_detector = ResponsibilityDetector()

    def analyze_message(self, agent_id: str, message: str) -> ImmuneResponse:
        """分析消息，返回免疫响应"""
        response = self.confusion_detector.detect(message)

        if response.detected:
            response.suggestions = self._generate_suggestions(agent_id, response.response_type)

        return response

    def _generate_suggestions(self, agent_id: str, response_type: str) -> List[str]:
        """生成建议"""
        suggestions = []

        if response_type == "confusion":
            suggestions = [
                "请查看当前待办事项: oc-collab todo",
                "请查看项目状态: oc-collab status",
                "如需帮助请查看协作指南: cat skills/README.md"
            ]

        return suggestions


class SessionStarter:
    """会话起始引导器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def get_welcome_message(self, agent_id: str) -> str:
        """生成欢迎消息和上下文信息"""
        responsibilities = self._get_responsibilities(agent_id)

        message = f"""=== {agent_id} ===

当前项目: oc-collab
当前版本: v2.2.1

你的职责:
{self._format_responsibilities(responsibilities)}

当前待办事项:
  - 请查看: oc-collab todo

常用命令:
  - oc-collab status    查看状态
  - oc-collab review    评审
  - oc-collab signoff   签署
  - oc-collab todo       待办事项
"""
        return message

    def display_welcome(self, agent_id: str) -> str:
        """返回欢迎消息"""
        return self.get_welcome_message(agent_id)

    def _get_responsibilities(self, agent_id: str) -> Dict[str, Any]:
        """获取职责定义"""
        return RESPONSIBILITY_MATRIX.get(agent_id, {
            "roles": [],
            "responsibilities": ["未知角色"],
            "forbidden": []
        })

    def _format_responsibilities(self, data: Dict[str, Any]) -> str:
        """格式化职责列表"""
        lines = []
        for resp in data.get("responsibilities", []):
            lines.append(f"  - {resp}")
        return "\n".join(lines)


class ConfusionDetector:
    """困惑信号检测器"""

    def __init__(self):
        self.signals = CONFUSION_SIGNALS

    def detect(self, message: str) -> ImmuneResponse:
        """检测困惑信号"""
        message_lower = message.lower()

        for signal in self.signals:
            if signal.lower() in message_lower:
                return ImmuneResponse(
                    detected=True,
                    response_type="confusion",
                    message=f"检测到困惑信号: {signal}",
                    suggestions=[
                        "请明确当前任务目标",
                        "查看项目状态了解进度",
                        "参考协作指南"
                    ]
                )

        return ImmuneResponse(
            detected=False,
            response_type="none",
            message="未检测到困惑信号"
        )

    def is_confused(self, message: str) -> bool:
        """快速检查是否包含困惑信号"""
        message_lower = message.lower()
        return any(signal.lower() in message_lower for signal in self.signals)


class ResponsibilityDetector:
    """职责边界检测器"""

    def __init__(self):
        self.matrix = RESPONSIBILITY_MATRIX

    def check_responsibility(self, agent_id: str, action: str) -> Tuple[bool, str]:
        """检查职责边界"""
        agent_config = self.matrix.get(agent_id)

        if not agent_config:
            return False, f"未知 Agent: {agent_id}"

        forbidden = agent_config.get("forbidden", [])

        for f in forbidden:
            if f.lower() in action.lower():
                return False, f"该操作不在 {agent_id} 的职责范围内"

        return True, f"{agent_id} 可以执行此操作"

    def get_responsibilities(self, agent_id: str) -> Dict[str, Any]:
        """获取职责定义"""
        return self.matrix.get(agent_id, {})


class SkillLoader:
    """Skill 自动加载器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.skills_dir = self.project_path / "skills"

    def load_collaboration_guide(self) -> Dict[str, Any]:
        """加载协作指南"""
        guide_file = self.skills_dir / "collaboration_guide.md"

        if not guide_file.exists():
            return {
                "loaded": False,
                "message": "协作指南不存在"
            }

        try:
            with open(guide_file) as f:
                content = f.read()

            return {
                "loaded": True,
                "content": content,
                "message": "协作指南加载成功"
            }
        except Exception as e:
            return {
                "loaded": False,
                "message": f"加载失败: {e}"
            }

    def list_skills(self) -> List[str]:
        """列出可用 Skills"""
        if not self.skills_dir.exists():
            return []

        skills = []
        for item in self.skills_dir.iterdir():
            if item.is_dir() or item.suffix == ".md":
                skills.append(item.name)

        return skills
