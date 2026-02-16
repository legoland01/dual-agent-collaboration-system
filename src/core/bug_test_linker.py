from typing import List, Optional
from pathlib import Path
import yaml
from dataclasses import dataclass
from datetime import datetime


class BugLinkError(Exception):
    pass


@dataclass
class BugTestLink:
    bug_id: str
    test_files: List[str]
    created_at: str
    updated_at: Optional[str] = None


class BugTestLinker:
    def __init__(self, links_path: str = "config/bug_test_links.yaml"):
        self.links_path = Path(links_path)
        self.links: dict = self._load_links()
    
    def _load_links(self) -> dict:
        if not self.links_path.exists():
            return {"version": "1.0", "last_updated": "", "links": []}
        
        try:
            with open(self.links_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {"version": "1.0", "last_updated": "", "links": []}
        except Exception as e:
            raise BugLinkError(f"加载关联数据失败: {e}")
    
    def _save_links(self) -> None:
        try:
            self.links_path.parent.mkdir(parents=True, exist_ok=True)
            self.links["last_updated"] = datetime.now().isoformat()
            with open(self.links_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.links, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            raise BugLinkError(f"保存关联数据失败: {e}")
    
    def link(self, bug_id: str, test_file: str) -> bool:
        if not Path(test_file).exists():
            raise BugLinkError(f"测试文件不存在: {test_file}")
        
        for link in self.links.get("links", []):
            if link.get("bug_id") == bug_id:
                if test_file not in link.get("test_files", []):
                    link["test_files"].append(test_file)
                    link["updated_at"] = datetime.now().isoformat()
                    self._save_links()
                return True
        
        new_link = {
            "bug_id": bug_id,
            "test_files": [test_file],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if "links" not in self.links:
            self.links["links"] = []
        self.links["links"].append(new_link)
        self._save_links()
        return True
    
    def unlink(self, bug_id: str, test_file: str) -> bool:
        for link in self.links.get("links", []):
            if link.get("bug_id") == bug_id:
                if test_file in link.get("test_files", []):
                    link["test_files"].remove(test_file)
                    link["updated_at"] = datetime.now().isoformat()
                    self._save_links()
                return True
        return False
    
    def get_tests_for_bug(self, bug_id: str) -> List[str]:
        for link in self.links.get("links", []):
            if link.get("bug_id") == bug_id:
                return link.get("test_files", [])
        return []
    
    def get_bugs_without_tests(self) -> List[str]:
        result = []
        for link in self.links.get("links", []):
            if not link.get("test_files"):
                result.append(link.get("bug_id", ""))
        return result
    
    def get_all_links(self) -> List[dict]:
        return self.links.get("links", [])
    
    def _create_test_template(self, bug_id: str) -> str:
        test_name = f"test_{bug_id.lower().replace('-', '_')}"
        template = f'''"""
Test for {bug_id}
"""
import pytest

def {test_name}():
    """Test case for {bug_id}"""
    pass
'''
        return template
