from typing import List, Optional
from pathlib import Path
import yaml
from dataclasses import dataclass


class SkillIndexError(Exception):
    pass


@dataclass
class SkillIndexEntry:
    keywords: List[str]
    skill: str
    description: str = ""


class SkillIndex:
    def __init__(self, index_path: str = "config/skill_index.yaml"):
        self.index_path = Path(index_path)
        self.index: dict = self._load_index()
    
    def _load_index(self) -> dict:
        if not self.index_path.exists():
            return {"version": "1.0", "last_updated": "", "index": []}
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {"version": "1.0", "last_updated": "", "index": []}
        except Exception as e:
            raise SkillIndexError(f"加载索引失败: {e}")
    
    def _save_index(self) -> None:
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.index_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.index, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            raise SkillIndexError(f"保存索引失败: {e}")
    
    def add_entry(self, keywords: List[str], skill: str, description: str = "") -> bool:
        for entry in self.index.get("index", []):
            if entry.get("skill") == skill:
                return False
        
        entry = {
            "keywords": keywords,
            "skill": skill,
            "description": description
        }
        
        if "index" not in self.index:
            self.index["index"] = []
        self.index["index"].append(entry)
        self._save_index()
        return True
    
    def update_keywords(self, skill: str, keywords: List[str]) -> bool:
        for entry in self.index.get("index", []):
            if entry.get("skill") == skill:
                entry["keywords"] = keywords
                self._save_index()
                return True
        return False
    
    def get_all_skills(self) -> List[str]:
        return [entry.get("skill", "") for entry in self.index.get("index", [])]
    
    def get_skill_info(self, skill: str) -> Optional[dict]:
        for entry in self.index.get("index", []):
            if entry.get("skill") == skill:
                return entry
        return None
    
    def remove_entry(self, skill: str) -> bool:
        original_len = len(self.index.get("index", []))
        self.index["index"] = [e for e in self.index.get("index", []) if e.get("skill") != skill]
        if len(self.index["index"]) < original_len:
            self._save_index()
            return True
        return False
