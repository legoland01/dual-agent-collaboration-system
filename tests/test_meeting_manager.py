"""v2.2.0 M3 Meeting Manager 测试用例

基于 src/core/meeting_manager.py
"""
import pytest
import tempfile
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.meeting_manager import (
    MeetingManager,
    Meeting,
    MeetingAttachment,
    MeetingType,
    MeetingStatus,
    MeetingNotFoundError
)


class TestMeetingManagerBasic:
    """会议管理器基础测试。"""

    def test_initialize_meeting_manager(self, tmp_path):
        """测试初始化会议管理器。"""
        manager = MeetingManager(str(tmp_path))
        
        assert manager.project_path == tmp_path
        assert manager.meetings_dir == tmp_path / "meetings"
        assert manager.meetings_dir.exists()

    def test_create_meeting(self, tmp_path):
        """测试创建会议。"""
        manager = MeetingManager(str(tmp_path))
        meeting = manager.create_meeting(
            title="v2.2.0 需求讨论",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0",
            participants=["Agent 1", "Agent 2"]
        )
        
        assert meeting is not None
        assert meeting.meeting_id == "MTG-001"
        assert meeting.title == "v2.2.0 需求讨论"
        assert meeting.meeting_type == MeetingType.AGENT_DISCUSSION
        assert meeting.version == "v2.2.0"
        assert "Agent 1" in meeting.participants

    def test_create_customer_meeting(self, tmp_path):
        """测试创建客户会议。"""
        manager = MeetingManager(str(tmp_path))
        meeting = manager.create_meeting(
            title="产品需求评审",
            meeting_type=MeetingType.CUSTOMER_MEETING,
            version="v2.2.0"
        )
        
        assert meeting is not None
        assert meeting.meeting_type == MeetingType.CUSTOMER_MEETING

    def test_list_meetings(self, tmp_path):
        """测试列出会议。"""
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(title="Meeting 1", meeting_type=MeetingType.AGENT_DISCUSSION, version="v2.2.0")
        manager.create_meeting(title="Meeting 2", meeting_type=MeetingType.CUSTOMER_MEETING, version="v2.2.0")
        
        meetings = manager.list_meetings()
        assert len(meetings) == 2

    def test_get_meeting(self, tmp_path):
        """测试获取会议。"""
        manager = MeetingManager(str(tmp_path))
        meeting = manager.create_meeting(
            title="Test Meeting",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0"
        )
        
        retrieved = manager.get_meeting("MTG-001")
        assert retrieved.meeting_id == meeting.meeting_id


class TestMeetingFiltering:
    """会议过滤测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(title="M1", meeting_type=MeetingType.AGENT_DISCUSSION, version="v2.2.0")
        manager.create_meeting(title="M2", meeting_type=MeetingType.CUSTOMER_MEETING, version="v2.2.0")
        manager.create_meeting(title="M3", meeting_type=MeetingType.AGENT_DISCUSSION, version="v2.1.0")
        return manager

    def test_list_by_version(self, manager):
        """测试按版本列出会议。"""
        meetings = manager.list_meetings(version="v2.2.0")
        assert len(meetings) == 2

    def test_list_by_type(self, manager):
        """测试按类型列出会议。"""
        meetings = manager.list_meetings(meeting_type=MeetingType.AGENT_DISCUSSION)
        assert len(meetings) == 2

    def test_list_by_status(self, manager):
        """测试按状态列出会议。"""
        meetings = manager.list_meetings(status=MeetingStatus.DRAFT)
        assert len(meetings) == 3


class TestMeetingModification:
    """会议修改测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(
            title="Test Meeting",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0"
        )
        return manager

    def test_add_decision(self, manager):
        """测试添加决策。"""
        meeting = manager.add_decision("MTG-001", "采用分层通知机制")
        
        assert len(meeting.decisions) == 1
        assert "采用分层通知机制" in meeting.decisions

    def test_add_action_item(self, manager):
        """测试添加待办事项。"""
        meeting = manager.add_action_item("MTG-001", "创建设计文档")
        
        assert len(meeting.action_items) == 1
        assert "创建设计文档" in meeting.action_items

    def test_update_status(self, manager):
        """测试更新状态。"""
        meeting = manager.update_meeting_status("MTG-001", MeetingStatus.IN_PROGRESS)
        
        assert meeting.status == MeetingStatus.IN_PROGRESS


class TestMeetingSummary:
    """会议纪要测试。"""

    @pytest.fixture
    def manager(self, tmp_path):
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(
            title="v2.2.0 需求讨论",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0",
            participants=["Agent 1", "Agent 2"]
        )
        manager.add_decision("MTG-001", "资源锁超时采用分层通知机制")
        manager.add_decision("MTG-001", "Story 与 Feature 为正交关系")
        manager.add_action_item("MTG-001", "创建概要设计文档")
        return manager

    def test_generate_summary(self, manager):
        """测试生成会议纪要。"""
        summary = manager.generate_summary("MTG-001")
        
        assert summary is not None
        assert "# v2.2.0 需求讨论" in summary
        assert "关键决策" in summary
        assert "待办事项" in summary
        assert "资源锁超时采用分层通知机制" in summary

    def test_meeting_completed_after_summary(self, manager):
        """测试生成纪要后会议状态变为完成。"""
        manager.generate_summary("MTG-001")
        
        meeting = manager.get_meeting("MTG-001")
        assert meeting.status == MeetingStatus.COMPLETED
        assert meeting.summary is not None


class TestMeetingAttachments:
    """会议附件测试。"""

    def test_upload_attachment(self, tmp_path):
        """测试上传附件。"""
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(
            title="Test Meeting",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0"
        )
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        attachment = manager.upload_attachment("MTG-001", str(test_file))
        
        assert attachment is not None
        assert attachment.filename == "test.txt"
        assert attachment.file_type == "txt"

    def test_list_attachments(self, tmp_path):
        """测试列出附件。"""
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(
            title="Test Meeting",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0"
        )
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        manager.upload_attachment("MTG-001", str(test_file))
        
        meeting = manager.get_meeting("MTG-001")
        assert len(meeting.attachments) == 1


class TestMeetingVersion:
    """会议版本测试。"""

    def test_get_meetings_by_version(self, tmp_path):
        """测试获取指定版本的会议。"""
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(title="M1", meeting_type=MeetingType.AGENT_DISCUSSION, version="v2.2.0")
        manager.create_meeting(title="M2", meeting_type=MeetingType.CUSTOMER_MEETING, version="v2.1.0")
        
        meetings = manager.get_meetings_by_version("v2.2.0")
        assert len(meetings) == 1


class TestMeetingSummaryData:
    """会议摘要数据测试。"""

    def test_get_meeting_summary(self, tmp_path):
        """测试获取会议摘要。"""
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(title="M1", meeting_type=MeetingType.AGENT_DISCUSSION, version="v2.2.0")
        manager.create_meeting(title="M2", meeting_type=MeetingType.CUSTOMER_MEETING, version="v2.2.0")
        
        summary = manager.get_meeting_summary()
        
        assert summary["total_meetings"] == 2
        assert summary["by_version"]["v2.2.0"] == 2
        assert summary["by_type"]["agent_discussion"] == 1


class TestExport:
    """导出测试。"""

    def test_export_meetings(self, tmp_path):
        """测试导出会议数据。"""
        manager = MeetingManager(str(tmp_path))
        manager.create_meeting(
            title="Test Meeting",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0"
        )
        
        data = manager.export_meetings()
        
        assert "meetings" in data
        assert "summary" in data
        assert len(data["meetings"]) == 1


class TestErrorHandling:
    """错误处理测试。"""

    def test_get_nonexistent_meeting(self, tmp_path):
        """测试获取不存在的会议。"""
        manager = MeetingManager(str(tmp_path))
        
        with pytest.raises(MeetingNotFoundError):
            manager.get_meeting("MTG-999")


class TestMeetingDataClass:
    """会议数据类测试。"""

    def test_meeting_to_dict(self):
        """测试会议转字典。"""
        meeting = Meeting(
            meeting_id="MTG-001",
            title="Test Meeting",
            meeting_type=MeetingType.AGENT_DISCUSSION,
            version="v2.2.0",
            participants=["Agent 1"]
        )
        
        data = meeting.to_dict()
        
        assert data["meeting_id"] == "MTG-001"
        assert data["title"] == "Test Meeting"
        assert data["meeting_type"] == "agent_discussion"

    def test_meeting_from_dict(self):
        """测试从字典创建会议。"""
        data = {
            "meeting_id": "MTG-001",
            "title": "Test Meeting",
            "meeting_type": "agent_discussion",
            "version": "v2.2.0",
            "participants": ["Agent 1"],
            "decisions": [],
            "action_items": [],
            "attachments": [],
            "status": "draft",
            "summary": None
        }
        
        meeting = Meeting.from_dict(data)
        
        assert meeting.meeting_id == "MTG-001"
        assert meeting.meeting_type == MeetingType.AGENT_DISCUSSION


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
