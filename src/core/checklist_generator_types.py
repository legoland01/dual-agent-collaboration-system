from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class CheckStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class CheckItem:
    """检查项"""
    id: str
    title: str
    description: str
    status: CheckStatus = CheckStatus.PENDING
    details: str = ""
    requirements_id: Optional[str] = None
