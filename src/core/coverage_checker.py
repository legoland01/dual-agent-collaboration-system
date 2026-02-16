from typing import List, Optional
from pathlib import Path
import yaml
from datetime import datetime


class CoverageChecker:
    def __init__(self):
        from .bug_test_linker import BugTestLinker
        from .requirement_test_mapper import RequirementTestMapper
        self.bug_linker = BugTestLinker()
        self.req_mapper = RequirementTestMapper()
    
    def check_bug_coverage(self) -> dict:
        all_links = self.bug_linker.get_all_links()
        unlinked_bugs = self.bug_linker.get_bugs_without_tests()
        
        total = len(all_links)
        linked = total - len(unlinked_bugs)
        coverage = (linked / total * 100) if total > 0 else 100.0
        
        return {
            "total_bugs": total,
            "linked_bugs": linked,
            "unlinked_bugs": unlinked_bugs,
            "coverage": coverage,
            "passed": len(unlinked_bugs) == 0
        }
    
    def check_requirement_coverage(self) -> dict:
        result = self.req_mapper.analyze_coverage()
        
        if isinstance(result, dict):
            return {
                "total_requirements": result.get("total", result.get("total_requirements", 0)),
                "covered_requirements": result.get("covered", result.get("covered_requirements", 0)),
                "uncovered_requirements": result.get("uncovered", result.get("uncovered_requirements", [])),
                "coverage": result.get("coverage_percentage", result.get("coverage", 0)),
                "passed": result.get("uncovered", result.get("uncovered_requirements", [])) == []
            }
        
        return {
            "total_requirements": result.total_requirements,
            "covered_requirements": result.covered_requirements,
            "uncovered_requirements": result.uncovered_requirements,
            "coverage": result.coverage_percentage,
            "passed": len(result.uncovered_requirements) == 0
        }
    
    def check_all(self) -> dict:
        bug_result = self.check_bug_coverage()
        req_result = self.check_requirement_coverage()
        
        return {
            "bug_coverage": bug_result,
            "requirement_coverage": req_result,
            "all_passed": bug_result["passed"] and req_result["passed"]
        }
