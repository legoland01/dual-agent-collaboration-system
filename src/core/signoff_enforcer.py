"""SignoffEnforcer: 强制签署检查器

FR-GIT-002: Git提交前强制验证签署是否完整
"""
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import yaml
from datetime import datetime


class SignoffEnforcerError(Exception):
    """SignoffEnforcer 错误"""
    pass


class SignoffNotFoundError(SignoffEnforcerError):
    """签署文件未找到"""
    pass


class SignoffIncompleteError(SignoffEnforcerError):
    """签署不完整"""
    pass


class SignoffEnforcer:
    """强制签署检查器"""
    
    URGENT_CASES = {
        "bug_fix": {
            "examples": ["修复阻塞协作的Bug"],
            "allow_force": True,
        },
        "security_patch": {
            "examples": ["修复安全漏洞"],
            "allow_force": True,
        },
        "hot_fix": {
            "examples": ["紧急发布修复"],
            "allow_force": True,
        },
        "docs_fix": {
            "examples": ["拼写错误、格式调整"],
            "allow_force": False,
        },
        "feature": {
            "examples": ["新功能开发"],
            "allow_force": False,
        },
    }
    
    def __init__(self, state_dir: Optional[str] = None):
        """
        初始化 SignoffEnforcer
        
        Args:
            state_dir: State目录路径，默认为项目根目录/state
        """
        self.state_dir = Path(state_dir) if state_dir else Path.cwd() / "state"
    
    def check_signoff_status(self, doc_path: str) -> Dict[str, Any]:
        """
        检查文档的签署状态
        
        Args:
            doc_path: 文档路径
            
        Returns:
            {
                "complete": bool,
                "missing_signers": List[str],
                "pending_signatures": List[str],
            }
        """
        doc = Path(doc_path)
        if not doc.exists():
            raise SignoffNotFoundError(f"文档不存在: {doc_path}")
        
        signoff_path = doc.parent / f"{doc.stem}_signoff.md"
        
        if not signoff_path.exists():
            return {
                "complete": False,
                "missing_signers": ["signoff文件不存在"],
                "pending_signatures": [],
            }
        
        try:
            with open(signoff_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            complete = "✅" in content or "通过" in content
            missing = []
            
            if "Agent 1" in content:
                agent1_section = content.split("Agent 1")[1].split("\n")[0] if len(content.split("Agent 1")) > 1 else ""
                if "✅" not in agent1_section:
                    missing.append("Agent 1")
            else:
                missing.append("Agent 1")
            
            if "Agent 2" in content:
                agent2_section = content.split("Agent 2")[1].split("\n")[0] if len(content.split("Agent 2")) > 1 else ""
                if "✅" not in agent2_section:
                    missing.append("Agent 2")
            else:
                missing.append("Agent 2")
            
            return {
                "complete": complete and len(missing) == 0,
                "missing_signers": missing,
                "pending_signatures": [],
            }
        except Exception as e:
            raise SignoffEnforcerError(f"读取签署文件失败: {str(e)}")
    
    def enforce_signoff(self, doc_path: str, force: bool = False) -> Tuple[bool, str]:
        """
        强制检查签署
        
        Args:
            doc_path: 文档路径
            force: 是否强制跳过检查
            
        Returns:
            (是否通过, 错误信息)
        """
        status = self.check_signoff_status(doc_path)
        
        if status["complete"]:
            return True, "签署完整"
        
        if force:
            return False, "警告: 强制跳过签署检查！请确保是紧急情况。"
        
        missing = ", ".join(status["missing_signers"])
        return False, f"签署不完整，缺少: {missing}"
    
    def is_urgent_case(self, commit_type: str) -> Tuple[bool, str]:
        """
        检查是否为紧急情况
        
        Args:
            commit_type: 提交类型
            
        Returns:
            (是否紧急, 原因)
        """
        commit_type = commit_type.lower()
        
        for case, config in self.URGENT_CASES.items():
            if any(keyword in commit_type for keyword in case.split("_")):
                return config["allow_force"], case
        
        return False, "非紧急情况"
    
    def log_force_commit(self, doc_path: str, reason: str) -> None:
        """
        记录强制提交日志
        
        Args:
            doc_path: 文档路径
            reason: 强制提交原因
        """
        log_path = self.state_dir / "force_commit_log.yaml"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "doc_path": doc_path,
            "reason": reason,
        }
        
        try:
            if log_path.exists():
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs = yaml.safe_load(f) or []
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                yaml.dump(logs, f, allow_unicode=True, sort_keys=False)
        except Exception:
            pass
