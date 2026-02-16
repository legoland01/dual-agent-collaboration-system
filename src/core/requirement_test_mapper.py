from typing import List, Optional
from pathlib import Path
import yaml
from datetime import datetime


class RequirementTestMapper:
    def __init__(self, mapping_path: str = "config/requirement_test_mapping.yaml"):
        self.mapping_path = Path(mapping_path)
        self.mappings = self._load_mappings()
    
    def _load_mappings(self) -> dict:
        if not self.mapping_path.exists():
            return {"version": "1.0", "last_updated": "", "mappings": []}
        
        try:
            with open(self.mapping_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {"version": "1.0", "last_updated": "", "mappings": []}
        except Exception:
            return {"version": "1.0", "last_updated": "", "mappings": []}
    
    def _save_mappings(self) -> None:
        try:
            self.mapping_path.parent.mkdir(parents=True, exist_ok=True)
            self.mappings["last_updated"] = datetime.now().isoformat()
            with open(self.mapping_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.mappings, f, allow_unicode=True, sort_keys=False)
        except Exception:
            pass
    
    def map(self, requirement_id: str, test_file: str) -> bool:
        if not Path(test_file).exists():
            return False
        
        for mapping in self.mappings.get("mappings", []):
            if mapping.get("requirement_id") == requirement_id:
                if test_file not in mapping.get("test_files", []):
                    mapping["test_files"].append(test_file)
                    self._save_mappings()
                return True
        
        new_mapping = {
            "requirement_id": requirement_id,
            "test_files": [test_file],
            "coverage": 0,
            "created_at": datetime.now().isoformat()
        }
        
        if "mappings" not in self.mappings:
            self.mappings["mappings"] = []
        self.mappings["mappings"].append(new_mapping)
        self._save_mappings()
        return True
    
    def get_tests_for_requirement(self, requirement_id: str) -> List[str]:
        for mapping in self.mappings.get("mappings", []):
            if mapping.get("requirement_id") == requirement_id:
                return mapping.get("test_files", [])
        return []
    
    def get_uncovered_requirements(self) -> List[str]:
        return [m["requirement_id"] for m in self.mappings.get("mappings", []) if not m.get("test_files")]
    
    def get_all_mappings(self) -> List[dict]:
        return self.mappings.get("mappings", [])
    
    def analyze_coverage(self) -> dict:
        mappings = self.mappings.get("mappings", [])
        total = len(mappings)
        covered = sum(1 for m in mappings if m.get("test_files"))
        
        return {
            "total": total,
            "covered": covered,
            "uncovered": total - covered,
            "coverage_percentage": (covered / total * 100) if total > 0 else 0.0
        }
    
    def suggest_requirements(self, test_file: str) -> list:
        suggestions = []
        mappings = self.mappings.get("mappings", [])
        
        test_name = test_file.lower()
        for mapping in mappings:
            req_id = mapping.get("requirement_id", "")
            if any(keyword in test_name for keyword in req_id.lower().replace("-", "_").split("_")):
                suggestions.append(req_id)
        
        return suggestions
