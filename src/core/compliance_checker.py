"""
合规检查器模块

验证TODO操作符合规则，支持新编号格式和旧编号格式。
"""

import re
from typing import Tuple, Optional, Dict


class ComplianceChecker:
    """合规检查器"""
    
    def __init__(self, current_agent: str):
        """
        Args:
            current_agent: 当前Agent ID
        """
        self.current_agent = current_agent
    
    def check_todo_create(self, todo: Dict) -> Tuple[bool, str]:
        """
        检查TODO创建是否符合规则
        
        Args:
            todo: TODO数据
        
        Returns:
            (是否通过, 错误信息)
        """
        todo_id = todo.get("id", "")
        
        # 1. 编号格式检查
        if not self._check_format(todo_id):
            return False, f"无效的TODO编号格式: {todo_id}"
        
        # 2. 创建者/接收者关系检查
        parsed = self._parse_id(todo_id)
        if parsed and not self._check_creator_receiver(parsed):
            creator = parsed.get("creator")
            receiver = parsed.get("receiver")
            if creator != self.current_agent:
                return False, f"Agent{self.current_agent}不能创建非自己的TODO: {todo_id}"
            
            if creator == "1" and receiver not in ["1", "2"]:
                return False, "Agent1只能创建给自己的TODO"
        
        return True, ""
    
    def _check_format(self, todo_id: str) -> bool:
        """
        检查编号格式
        
        Args:
            todo_id: TODO编号
        
        Returns:
            是否有效
        """
        # 新格式: TODO-1to2-001
        if re.match(r'TODO-\d+to\d+-\d+', todo_id):
            return True
        # 旧格式: TODO-1-001
        if re.match(r'TODO-\d+-\d+', todo_id):
            return True
        return False
    
    def _parse_id(self, todo_id: str) -> Optional[Dict]:
        """
        解析编号
        
        Args:
            todo_id: TODO编号
        
        Returns:
            解析结果或None
        """
        # 新格式
        match = re.match(r'TODO-(\d+)to(\d+)-(\d+)', todo_id)
        if match:
            return {
                "creator": match.group(1),
                "receiver": match.group(2),
                "seq": int(match.group(3))
            }
        
        # 旧格式
        match = re.match(r'TODO-(\d+)-(\d+)', todo_id)
        if match:
            return {
                "creator": match.group(1),
                "receiver": match.group(1),
                "seq": int(match.group(2))
            }
        
        return None
    
    def _check_creator_receiver(self, parsed: Dict) -> bool:
        """
        检查创建者/接收者关系
        
        Args:
            parsed: 解析结果
        
        Returns:
            是否符合规则
        """
        creator = parsed.get("creator")
        receiver = parsed.get("receiver")
        
        # 任何Agent都可以创建TODO给任何人
        return True
    
    def validate_source(self, source: str) -> Tuple[bool, str]:
        """
        验证来源是否有效
        
        Args:
            source: 来源类型
        
        Returns:
            (是否有效, 错误信息)
        """
        valid_sources = ["REQUIREMENT", "BUG", "FEEDBACK", "MANUAL"]
        if source.upper() not in valid_sources:
            return False, f"无效的来源类型: {source}，有效值: {valid_sources}"
        return True, ""
    
    def validate_role(self, role: str) -> Tuple[bool, str]:
        """
        验证角色是否有效
        
        Args:
            role: 角色
        
        Returns:
            (是否有效, 错误信息)
        """
        valid_roles = [
            "PRODUCT_MANAGER",
            "DEVELOPMENT_LEAD",
            "FRONTEND_DEV",
            "BACKEND_DEV",
            "QA_ENGINEER"
        ]
        if role not in valid_roles:
            return False, f"无效的角色: {role}，有效值: {valid_roles}"
        return True, ""
