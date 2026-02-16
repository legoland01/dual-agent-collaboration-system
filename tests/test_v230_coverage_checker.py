import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.coverage_checker import CoverageChecker


class TestCoverageChecker:
    @pytest.fixture
    def temp_dir(self):
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp, ignore_errors=True)
    
    @pytest.fixture
    def test_file(self, temp_dir):
        test_path = Path(temp_dir) / "test_example.py"
        test_path.write_text("# test file")
        return str(test_path)
    
    @pytest.fixture
    def checker(self, temp_dir, test_file):
        from src.core.bug_test_linker import BugTestLinker
        from src.core.requirement_test_mapper import RequirementTestMapper
        
        bug_path = Path(temp_dir) / "bug_test_links.yaml"
        req_path = Path(temp_dir) / "requirement_test_mapping.yaml"
        
        bug_linker = BugTestLinker(str(bug_path))
        bug_linker.link("BUG-20260215-001", test_file)
        
        req_mapper = RequirementTestMapper(str(req_path))
        req_mapper.map("F-QUAL-001", test_file)
        
        return CoverageChecker()
    
    def test_check_bug_coverage(self, checker):
        result = checker.check_bug_coverage()
        assert "total_bugs" in result
        assert "coverage" in result
        assert "passed" in result
    
    def test_check_requirement_coverage(self, checker):
        result = checker.check_requirement_coverage()
        assert "total_requirements" in result
        assert "coverage" in result
        assert "passed" in result
    
    def test_check_all(self, checker):
        result = checker.check_all()
        assert "bug_coverage" in result
        assert "requirement_coverage" in result
        assert "all_passed" in result
    
    def test_p0_bug_check(self, checker):
        result = checker.check_bug_coverage()
        assert result["passed"] is True
    
    def test_signoff_bug_check(self, checker):
        result = checker.check_bug_coverage()
        assert "passed" in result
    
    def test_integrate_signoff(self, checker):
        result = checker.check_all()
        assert result is not None
    
    def test_signoff_requirement_check(self, checker):
        result = checker.check_requirement_coverage()
        assert "passed" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
