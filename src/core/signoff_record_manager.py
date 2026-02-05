"""签署记录管理器模块。"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class SignoffRecord:
    """签署记录"""
    signoff_id: str
    milestone: str
    phase: str
    signers: List[Dict[str, Any]]
    status: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SignoffRecordManager:
    """签署记录管理器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.signoffs_dir = self.project_path / "state" / "signoffs"
        self.signoffs_dir.mkdir(parents=True, exist_ok=True)

    def _generate_signoff_id(self, milestone: str) -> str:
        """生成签署记录ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"SIG-{milestone}-{timestamp}"

    def save_signoff(self, milestone: str, phase: str, signers: List[Dict[str, Any]], status: str = "PENDING") -> str:
        """保存签署记录"""
        signoff_id = self._generate_signoff_id(milestone)

        record = SignoffRecord(
            signoff_id=signoff_id,
            milestone=milestone,
            phase=phase,
            signers=signers,
            status=status,
            created_at=datetime.now().isoformat()
        )

        file_path = self.signoffs_dir / f"{signoff_id}.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(record.to_dict(), f)

        return signoff_id

    def get_signoff(self, signoff_id: str) -> Optional[Dict[str, Any]]:
        """获取签署记录"""
        file_path = self.signoffs_dir / f"{signoff_id}.yaml"

        if file_path.exists():
            with open(file_path) as f:
                return yaml.safe_load(f)

        return None

    def list_signoffs(self) -> List[Dict[str, Any]]:
        """列出所有签署记录"""
        signoffs = []
        for file_path in self.signoffs_dir.glob("*.yaml"):
            with open(file_path) as f:
                signoffs.append(yaml.safe_load(f))
        return signoffs

    def update_signoff_status(self, signoff_id: str, status: str, signer: Dict[str, Any] = None):
        """更新签署记录状态"""
        record = self.get_signoff(signoff_id)
        if record:
            record["status"] = status

            if signer:
                for i, s in enumerate(record["signers"]):
                    if s.get("agent") == signer.get("agent"):
                        record["signers"][i] = signer
                        break

            file_path = self.signoffs_dir / f"{signoff_id}.yaml"
            with open(file_path, 'w') as f:
                yaml.dump(record, f)

    def check_all_signed(self, signoff_id: str) -> bool:
        """检查签署记录中所有签署者是否都已签署"""
        record = self.get_signoff(signoff_id)
        if record:
            return all(s.get("status") == "approved" for s in record.get("signers", []))
        return False
