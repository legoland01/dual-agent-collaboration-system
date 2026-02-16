from typing import List
from pathlib import Path
import yaml
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CoverageReport:
    total_requirements: int
    covered_requirements: int
    uncovered_requirements: List[str]
    coverage_percentage: float


class RequirementsCoverageAnalyzer:
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
    
    def analyze_coverage(self) -> CoverageReport:
        mappings = self.mappings.get("mappings", [])
        
        total = len(mappings)
        covered = sum(1 for m in mappings if m.get("test_files"))
        uncovered = [m["requirement_id"] for m in mappings if not m.get("test_files")]
        
        coverage_percentage = (covered / total * 100) if total > 0 else 0.0
        
        return CoverageReport(
            total_requirements=total,
            covered_requirements=covered,
            uncovered_requirements=uncovered,
            coverage_percentage=coverage_percentage
        )
    
    def get_uncovered_requirements(self) -> List[str]:
        return [m["requirement_id"] for m in self.mappings.get("mappings", []) if not m.get("test_files")]
