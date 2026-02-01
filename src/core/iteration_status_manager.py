"""迭代状态管理模块。

功能：
1. 管理多迭代状态隔离
2. 验证迭代状态与实际进度一致
3. 重置指定阶段状态
"""
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import yaml


logger = logging.getLogger(__name__)


class IterationStatus(Enum):
    """迭代状态。"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PhaseStatus(Enum):
    """阶段状态。"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"


@dataclass
class IterationState:
    """迭代状态。"""
    version: str
    status: str = IterationStatus.PENDING.value
    start_date: str = ""
    end_date: str = ""
    requirements: str = PhaseStatus.PENDING.value
    design: str = PhaseStatus.PENDING.value
    development: str = PhaseStatus.PENDING.value
    testing: str = PhaseStatus.PENDING.value
    deployment: str = PhaseStatus.PENDING.value
    history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "requirements": self.requirements,
            "design": self.design,
            "development": self.development,
            "testing": self.testing,
            "deployment": self.deployment,
            "history": self.history
        }


class IterationStatusManager:
    """迭代状态管理器。"""
    
    PHASES = ["requirements", "design", "development", "testing", "deployment"]
    
    def __init__(self, state_path: str):
        """初始化。
        
        Args:
            state_path: state.yaml 文件路径
        """
        self.state_path = state_path
        self.state = self._load_state()
        self.current_iteration = self._get_current_iteration()
    
    def _load_state(self) -> Dict:
        """加载状态文件。"""
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"加载状态文件失败: {e}")
            return {}
    
    def _save_state(self):
        """保存状态文件。"""
        try:
            with open(self.state_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.state, f, allow_unicode=True, sort_keys=False)
        except IOError as e:
            logger.error(f"保存状态文件失败: {e}")
    
    def _get_current_iteration(self) -> Optional[str]:
        """获取当前迭代版本。"""
        return self.state.get("iteration", {}).get("current")
    
    def get_iteration_state(self, version: str = None) -> Optional[IterationState]:
        """获取指定迭代的状态。"""
        target_version = version or self.current_iteration
        if not target_version:
            return None
        
        iterations = self.state.get("iterations", {})
        if target_version in iterations:
            data = iterations[target_version]
            return IterationState(**data)
        return None
    
    def get_current_state(self) -> Optional[IterationState]:
        """获取当前迭代状态。"""
        return self.get_iteration_state()
    
    def start_iteration(self, version: str) -> IterationState:
        """开始新迭代，初始化状态。"""
        if "iterations" not in self.state:
            self.state["iterations"] = {}
        
        now = datetime.now().isoformat()
        new_iteration = IterationState(
            version=version,
            status=IterationStatus.IN_PROGRESS.value,
            start_date=now
        )
        
        self.state["iterations"][version] = new_iteration.to_dict()
        self.state["iteration"] = {
            "current": version,
            "status": "in_progress"
        }
        
        self.current_iteration = version
        self._save_state()
        
        logger.info(f"开始新迭代: {version}")
        return new_iteration
    
    def complete_iteration(self, version: str = None) -> bool:
        """完成迭代。"""
        target_version = version or self.current_iteration
        if not target_version:
            logger.error("没有当前迭代")
            return False
        
        now = datetime.now().isoformat()
        if target_version in self.state.get("iterations", {}):
            self.state["iterations"][target_version]["status"] = IterationStatus.COMPLETED.value
            self.state["iterations"][target_version]["end_date"] = now
            self.state["iterations"][target_version]["status"] = IterationStatus.COMPLETED.value
            self.state["iteration"]["status"] = "completed"
            
            self._save_state()
            logger.info(f"迭代已完成: {target_version}")
            return True
        
        return False
    
    def update_phase_status(self, phase: str, status: str, version: str = None) -> bool:
        """更新阶段状态。"""
        if phase not in self.PHASES:
            logger.error(f"未知阶段: {phase}")
            return False
        
        target_version = version or self.current_iteration
        if not target_version:
            logger.error("没有当前迭代")
            return False
        
        if target_version in self.state.get("iterations", {}):
            self.state["iterations"][target_version][phase] = status
            
            self._save_state()
            logger.info(f"迭代 {target_version} 的 {phase} 状态已更新为 {status}")
            return True
        
        return False
    
    def reset_phase(self, phase: str, version: str = None) -> bool:
        """重置指定阶段状态为 pending。"""
        return self.update_phase_status(phase, PhaseStatus.PENDING.value, version)
    
    def archive_iteration(self, version: str) -> bool:
        """归档迭代。"""
        if version in self.state.get("iterations", {}):
            self.state["iterations"][version]["status"] = IterationStatus.ARCHIVED.value
            
            if self.state.get("iteration", {}).get("current") == version:
                self.state["iteration"]["current"] = None
                self.state["iteration"]["status"] = "archived"
            
            self._save_state()
            logger.info(f"迭代已归档: {version}")
            return True
        
        return False
    
    def switch_iteration(self, version: str) -> bool:
        """切换到指定迭代。"""
        if version in self.state.get("iterations", {}):
            self.state["iteration"]["current"] = version
            self.state["iteration"]["status"] = self.state["iterations"][version]["status"]
            self.current_iteration = version
            
            self._save_state()
            logger.info(f"已切换到迭代: {version}")
            return True
        
        logger.error(f"迭代不存在: {version}")
        return False
    
    def get_progress(self, version: str = None) -> Dict:
        """获取迭代进度。"""
        target_version = version or self.current_iteration
        if not target_version:
            return {"error": "没有当前迭代"}
        
        iteration = self.get_iteration_state(target_version)
        if not iteration:
            return {"error": f"迭代不存在: {target_version}"}
        
        completed_phases = 0
        total_phases = len(self.PHASES)
        
        for phase in self.PHASES:
            status = getattr(iteration, phase)
            if status in [PhaseStatus.COMPLETED.value, PhaseStatus.APPROVED.value]:
                completed_phases += 1
        
        return {
            "version": target_version,
            "overall_status": iteration.status,
            "phases": {
                phase: getattr(iteration, phase) for phase in self.PHASES
            },
            "progress_percent": (completed_phases / total_phases) * 100,
            "completed_phases": completed_phases,
            "total_phases": total_phases
        }
    
    def get_all_iterations(self) -> List[Dict]:
        """获取所有迭代信息。"""
        iterations = self.state.get("iterations", {})
        return [
            {"version": k, **v} for k, v in iterations.items()
        ]
    
    def validate_consistency(self, version: str = None) -> Dict:
        """验证迭代状态与实际进度一致。"""
        target_version = version or self.current_iteration
        if not target_version:
            return {"valid": False, "reason": "没有当前迭代"}
        
        iteration = self.get_iteration_state(target_version)
        if not iteration:
            return {"valid": False, "reason": f"迭代不存在: {target_version}"}
        
        issues = []
        
        for phase in self.PHASES:
            status = getattr(iteration, phase)
            
            if status == PhaseStatus.IN_PROGRESS.value:
                issues.append({
                    "phase": phase,
                    "status": status,
                    "issue": "阶段状态为进行中，请确保工作已完成后再更新状态"
                })
        
        return {
            "valid": len(issues) == 0,
            "version": target_version,
            "issues": issues
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = IterationStatusManager("state/project_state.yaml")
    
    print("当前迭代状态:")
    print(manager.get_current_state())
    
    print("\n进度:")
    print(manager.get_progress())
    
    print("\n一致性验证:")
    print(manager.validate_consistency())
