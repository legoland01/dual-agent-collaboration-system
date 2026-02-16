import re
from typing import List, Dict
from pathlib import Path


class TestSuggestionEngine:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, List[str]]:
        return {
            "todo": ["test_todo.py", "test_todo_sync.py", "test_todo_commands.py"],
            "同步": ["test_todo.py", "test_todo_sync.py", "test_todo_commands.py"],
            "失败": ["test_todo.py", "test_todo_sync.py"],
            "skill": ["test_skill.py", "test_skill_check.py", "test_skill_enforcer.py"],
            "signoff": ["test_signoff.py", "test_signoff_engine.py"],
            "deploy": ["test_deploy.py", "test_deployment.py"],
            "bug": ["test_bug.py", "test_bug_detector.py"],
            "requirements": ["test_requirements.py", "test_requirements_manager.py"],
            "coverage": ["test_coverage.py", "test_coverage_analyzer.py"],
            "index": ["test_skill_index.py", "test_search_engine.py"],
            "link": ["test_bug_test_linker.py", "test_linker.py"],
            "test": ["test_test_suggestion.py"],
        }
    
    def suggest_tests(self, bug_description: str, bug_id: str = "") -> List[str]:
        suggestions = []
        
        keywords = self._extract_keywords(bug_description)
        
        for keyword, tests in self.knowledge_base.items():
            if keyword in keywords:
                suggestions.extend(tests)
        
        if bug_id:
            bug_type = self._extract_bug_type(bug_id)
            if bug_type in self.knowledge_base:
                suggestions.extend(self.knowledge_base[bug_type])
        
        return list(set(suggestions))
    
    def _extract_keywords(self, text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r'\w+', text.lower())
    
    def _extract_bug_type(self, bug_id: str) -> str:
        bug_id_lower = bug_id.lower()
        
        type_mapping = {
            "todo": ["todo", "todowrite", "todo list"],
            "skill": ["skill", "enforce", "check"],
            "signoff": ["signoff", "sign off"],
            "deploy": ["deploy", "release", "pypi"],
            "bug": ["bug", "detector", "auto"],
            "requirements": ["requirements", "requirement"],
            "coverage": ["coverage", "test coverage"],
            "index": ["index", "search"],
            "link": ["link", "linker"],
        }
        
        for bug_type, kw_list in type_mapping.items():
            if any(kw in bug_id_lower for kw in kw_list):
                return bug_type
        
        return ""
