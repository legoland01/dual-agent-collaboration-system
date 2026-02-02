"""会议管理模块 - v2.2.0 M3 会议管理

提供会议创建、导入、列表、详情、纪要生成等功能。
"""
import uuid
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import json
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class MeetingType(Enum):
    """会议类型枚举。"""
    AGENT_DISCUSSION = "agent_discussion"  # Agent 间讨论
    CUSTOMER_MEETING = "customer_meeting"  # 产品经理与客户讨论


class MeetingStatus(Enum):
    """会议状态枚举。"""
    DRAFT = "draft"          # 草稿
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    ARCHIVED = "archived"    # 已归档


@dataclass
class MeetingAttachment:
    """会议附件。"""
    filename: str
    file_path: str
    file_type: str  # mp3, wav, txt, pdf, etc.
    upload_time: str = field(default_factory=lambda: datetime.now().isoformat())
    size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "upload_time": self.upload_time,
            "size": self.size
        }


@dataclass
class Meeting:
    """会议。"""
    meeting_id: str
    title: str
    meeting_type: MeetingType
    version: str
    participants: List[str] = field(default_factory=list)
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    decisions: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    attachments: List[MeetingAttachment] = field(default_factory=list)
    status: MeetingStatus = MeetingStatus.DRAFT
    summary: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meeting_id": self.meeting_id,
            "title": self.title,
            "meeting_type": self.meeting_type.value,
            "version": self.version,
            "participants": self.participants,
            "date": self.date,
            "decisions": self.decisions,
            "action_items": self.action_items,
            "attachments": [a.to_dict() for a in self.attachments],
            "status": self.status.value,
            "summary": self.summary,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Meeting":
        return cls(
            meeting_id=data["meeting_id"],
            title=data["title"],
            meeting_type=MeetingType(data["meeting_type"]),
            version=data["version"],
            participants=data.get("participants", []),
            date=data.get("date", datetime.now().isoformat()),
            decisions=data.get("decisions", []),
            action_items=data.get("action_items", []),
            attachments=[
                MeetingAttachment(**a) for a in data.get("attachments", [])
            ],
            status=MeetingStatus(data.get("status", "draft")),
            summary=data.get("summary"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )


class MeetingManagerError(Exception):
    """会议管理异常基类。"""
    pass


class MeetingNotFoundError(MeetingManagerError):
    """会议未找到异常。"""
    pass


class MeetingManager:
    """会议管理器。"""

    DEFAULT_MEETINGS_DIR = "meetings"
    MEETINGS_FILE = "meetings.yaml"

    def __init__(
        self,
        project_path: str,
        meetings_dir: Optional[str] = None,
        meetings_file: Optional[str] = None
    ):
        """初始化会议管理器。

        Args:
            project_path: 项目路径
            meetings_dir: 会议附件目录
            meetings_file: 会议数据文件
        """
        self.project_path = Path(project_path)
        self.meetings_dir = self.project_path / (meetings_dir or self.DEFAULT_MEETINGS_DIR)
        self.meetings_file = self.project_path / (meetings_file or self.MEETINGS_FILE)
        self.meetings: Dict[str, Meeting] = {}
        self._ensure_directories()
        self._load_meetings()

    def _ensure_directories(self) -> None:
        """确保目录存在。"""
        self.meetings_dir.mkdir(parents=True, exist_ok=True)

    def _load_meetings(self) -> None:
        """加载会议数据。"""
        if self.meetings_file.exists():
            try:
                with open(self.meetings_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if data and "meetings" in data:
                    for meeting_data in data.get("meetings", []):
                        meeting = Meeting.from_dict(meeting_data)
                        self.meetings[meeting.meeting_id] = meeting
            except Exception as e:
                logger.warning(f"加载会议数据失败: {e}")

    def _save_meetings(self) -> None:
        """保存会议数据。"""
        data = {
            "meetings": [m.to_dict() for m in self.meetings.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.meetings_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)

    def create_meeting(
        self,
        title: str,
        meeting_type: MeetingType,
        version: str,
        participants: Optional[List[str]] = None,
        date: Optional[str] = None
    ) -> Meeting:
        """创建会议。

        Args:
            title: 会议标题
            meeting_type: 会议类型
            version: 关联版本
            participants: 参与者
            date: 会议日期

        Returns:
            创建的会议
        """
        meeting_id = f"MTG-{len(self.meetings) + 1:03d}"
        meeting = Meeting(
            meeting_id=meeting_id,
            title=title,
            meeting_type=meeting_type,
            version=version,
            participants=participants or [],
            date=date or datetime.now().isoformat()
        )
        self.meetings[meeting_id] = meeting
        self._save_meetings()
        logger.info(f"创建会议: {meeting_id} - {title}")
        return meeting

    def get_meeting(self, meeting_id: str) -> Meeting:
        """获取会议。

        Args:
            meeting_id: 会议 ID

        Returns:
            会议

        Raises:
            MeetingNotFoundError: 会议未找到
        """
        if meeting_id not in self.meetings:
            raise MeetingNotFoundError(f"会议未找到: {meeting_id}")
        return self.meetings[meeting_id]

    def list_meetings(
        self,
        version: Optional[str] = None,
        status: Optional[MeetingStatus] = None,
        meeting_type: Optional[MeetingType] = None
    ) -> List[Meeting]:
        """列出会议。

        Args:
            version: 版本过滤
            status: 状态过滤
            meeting_type: 类型过滤

        Returns:
            会议列表
        """
        meetings = list(self.meetings.values())
        
        if version:
            meetings = [m for m in meetings if m.version == version]
        if status:
            meetings = [m for m in meetings if m.status == status]
        if meeting_type:
            meetings = [m for m in meetings if m.meeting_type == meeting_type]
        
        return sorted(meetings, key=lambda m: m.date, reverse=True)

    def add_decision(self, meeting_id: str, decision: str) -> Meeting:
        """添加决策。

        Args:
            meeting_id: 会议 ID
            decision: 决策内容

        Returns:
            更新后的会议

        Raises:
            MeetingNotFoundError: 会议未找到
        """
        meeting = self.get_meeting(meeting_id)
        meeting.decisions.append(decision)
        meeting.updated_at = datetime.now().isoformat()
        self._save_meetings()
        logger.info(f"添加决策: {meeting_id} - {decision[:50]}...")
        return meeting

    def add_action_item(self, meeting_id: str, action_item: str) -> Meeting:
        """添加待办事项。

        Args:
            meeting_id: 会议 ID
            action_item: 待办事项

        Returns:
            更新后的会议

        Raises:
            MeetingNotFoundError: 会议未找到
        """
        meeting = self.get_meeting(meeting_id)
        meeting.action_items.append(action_item)
        meeting.updated_at = datetime.now().isoformat()
        self._save_meetings()
        logger.info(f"添加待办: {meeting_id} - {action_item[:50]}...")
        return meeting

    def upload_attachment(
        self,
        meeting_id: str,
        file_path: str,
        target_dir: Optional[str] = None
    ) -> MeetingAttachment:
        """上传附件。

        Args:
            meeting_id: 会议 ID
            file_path: 源文件路径
            target_dir: 目标目录

        Returns:
            创建的附件

        Raises:
            MeetingNotFoundError: 会议未找到
        """
        meeting = self.get_meeting(meeting_id)
        
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        target_directory = self.meetings_dir / meeting_id / (target_dir or "attachments")
        target_directory.mkdir(parents=True, exist_ok=True)
        
        target_path = target_directory / source_path.name
        
        import shutil
        shutil.copy2(source_path, target_path)
        
        file_type = source_path.suffix.lower().lstrip(".")
        attachment = MeetingAttachment(
            filename=source_path.name,
            file_path=str(target_path),
            file_type=file_type,
            size=target_path.stat().st_size
        )
        
        meeting.attachments.append(attachment)
        meeting.updated_at = datetime.now().isoformat()
        self._save_meetings()
        
        logger.info(f"上传附件: {meeting_id} - {source_path.name}")
        return attachment

    def generate_summary(self, meeting_id: str) -> str:
        """生成会议纪要。

        Args:
            meeting_id: 会议 ID

        Returns:
            会议纪要内容

        Raises:
            MeetingNotFoundError: 会议未找到
        """
        meeting = self.get_meeting(meeting_id)
        
        summary_parts = [
            f"# {meeting.title}",
            "",
            f"**会议编号**: {meeting.meeting_id}",
            f"**日期**: {meeting.date}",
            f"**参与者**: {', '.join(meeting.participants) if meeting.participants else '无'}",
            f"**版本**: {meeting.version}",
            f"**状态**: {meeting.status.value}",
            "",
            "---",
            "",
            "## 关键决策",
            ""
        ]
        
        for decision in meeting.decisions:
            summary_parts.append(f"- {decision}")
        
        summary_parts.extend([
            "",
            "## 待办事项",
            ""
        ])
        
        for item in meeting.action_items:
            summary_parts.append(f"- [ ] {item}")
        
        if meeting.attachments:
            summary_parts.extend([
                "",
                "## 附件",
                ""
            ])
            for attachment in meeting.attachments:
                summary_parts.append(f"- [{attachment.filename}]({attachment.file_path})")
        
        summary = "\n".join(summary_parts)
        meeting.summary = summary
        meeting.status = MeetingStatus.COMPLETED
        meeting.updated_at = datetime.now().isoformat()
        self._save_meetings()
        
        logger.info(f"生成会议纪要: {meeting_id}")
        return summary

    def update_meeting_status(
        self,
        meeting_id: str,
        status: MeetingStatus
    ) -> Meeting:
        """更新会议状态。

        Args:
            meeting_id: 会议 ID
            status: 新状态

        Returns:
            更新后的会议

        Raises:
            MeetingNotFoundError: 会议未找到
        """
        meeting = self.get_meeting(meeting_id)
        meeting.status = status
        meeting.updated_at = datetime.now().isoformat()
        self._save_meetings()
        logger.info(f"更新状态: {meeting_id} -> {status.value}")
        return meeting

    def get_meetings_by_version(self, version: str) -> List[Meeting]:
        """获取指定版本的所有会议。

        Args:
            version: 版本号

        Returns:
            会议列表
        """
        return self.list_meetings(version=version)

    def get_meeting_summary(self) -> Dict[str, Any]:
        """获取会议管理摘要。

        Returns:
            摘要信息
        """
        by_status = {}
        by_version = {}
        by_type = {}
        
        for meeting in self.meetings.values():
            by_status[meeting.status.value] = by_status.get(meeting.status.value, 0) + 1
            by_version[meeting.version] = by_version.get(meeting.version, 0) + 1
            by_type[meeting.meeting_type.value] = by_type.get(meeting.meeting_type.value, 0) + 1
        
        return {
            "total_meetings": len(self.meetings),
            "by_status": by_status,
            "by_version": by_version,
            "by_type": by_type,
            "meetings_dir": str(self.meetings_dir)
        }

    def export_meetings(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """导出会议数据。

        Args:
            output_path: 输出路径（可选）

        Returns:
            会议数据字典
        """
        data = {
            "meetings": [m.to_dict() for m in self.meetings.values()],
            "summary": self.get_meeting_summary(),
            "exported_at": datetime.now().isoformat()
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True)
        
        return data


if __name__ == "__main__":
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MeetingManager(tmpdir)
        
        meeting = manager.create_meeting(
            title="v2.2.0 需求讨论",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0",
            participants=["Agent 1", "Agent 2"]
        )
        print(f"创建会议: {meeting.meeting_id}")
        
        manager.add_decision(
            meeting.meeting_id,
            "资源锁超时采用分层通知机制"
        )
        
        manager.add_action_item(
            meeting.meeting_id,
            "创建概要设计文档"
        )
        
        summary = manager.generate_summary(meeting.meeting_id)
        print(f"\n会议纪要:\n{summary}")
        
        summary_data = manager.get_meeting_summary()
        print(f"\n摘要: {summary_data}")
