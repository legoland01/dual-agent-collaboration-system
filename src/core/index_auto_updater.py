import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from .skill_index import SkillIndex, SkillIndexError


class IndexAutoUpdater:
    def __init__(self, index: SkillIndex, skills_dir: str = "skills"):
        self.index = index
        self.skills_dir = Path(skills_dir)
    
    def on_skill_created(self, skill_path: str) -> bool:
        skill_path = Path(skill_path)
        if not skill_path.exists():
            return False
        
        keywords = self._extract_keywords(str(skill_path))
        skill_name = skill_path.stem
        
        description = self._extract_description(str(skill_path))
        
        return self.index.add_entry(keywords, skill_name, description)
    
    def on_skill_updated(self, skill_path: str) -> bool:
        skill_path = Path(skill_path)
        if not skill_path.exists():
            return False
        
        skill_name = skill_path.stem
        keywords = self._extract_keywords(str(skill_path))
        description = self._extract_description(str(skill_path))
        
        if self.index.update_keywords(skill_name, keywords):
            info = self.index.get_skill_info(skill_name)
            if info:
                info["description"] = description
                self.index._save_index()
            return True
        return False
    
    def sync_all(self) -> int:
        if not self.skills_dir.exists():
            return 0
        
        count = 0
        for skill_file in self.skills_dir.rglob("content.md"):
            if self.on_skill_created(str(skill_file)):
                count += 1
        
        return count
    
    def _extract_keywords(self, skill_path: str) -> List[str]:
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            keywords = set()
            
            keyword_patterns = [
                r'##\s+(\w+)',
                r'###\s+(\w+)',
                r'\*\*(\w+)\*\*',
            ]
            
            for pattern in keyword_patterns:
                matches = re.findall(pattern, content)
                keywords.update(matches)
            
            words = re.findall(r'\b[a-zA-Z_]{4,}\b', content.lower())
            common_words = {'skill', 'guide', 'content', 'version', 'update', 'create', 
                          'check', 'search', 'agent', 'command', 'error', 'file', 'test'}
            keywords.update(w for w in words if w not in common_words)
            
            return list(keywords)[:10]
        except Exception:
            return []
    
    def _extract_description(self, skill_path: str) -> str:
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.strip().startswith('#'):
                    if i + 1 < len(lines):
                        desc = lines[i + 1].strip()
                        if desc:
                            return desc[:100]
            return ""
        except Exception:
            return ""
