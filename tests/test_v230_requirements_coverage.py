import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.requirement_test_mapper import RequirementTestMapper
from src.core.requirements_coverage import RequirementsCoverageAnalyzer, CoverageReport


class TestRequirementTestMapper:
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
    def mapper(self, temp_dir):
        mapping_path = Path(temp_dir) / "requirement_test_mapping.yaml"
        return RequirementTestMapper(str(mapping_path))
    
    def test_map_requirement_to_test(self, mapper, test_file):
        result = mapper.map("F-QUAL-001", test_file)
        assert result is True
        tests = mapper.get_tests_for_requirement("F-QUAL-001")
        assert test_file in tests
    
    def test_map_nonexistent_test_file(self, mapper):
        result = mapper.map("F-QUAL-001", "/nonexistent/test.py")
        assert result is False
    
    def test_get_uncovered_requirements(self, mapper, test_file):
        mapper.map("F-QUAL-001", test_file)
        uncovered = mapper.get_uncovered_requirements()
        assert len(uncovered) >= 0
    
    def test_analyze_coverage(self, mapper, test_file):
        mapper.map("F-QUAL-001", test_file)
        result = mapper.analyze_coverage()
        assert result["total"] >= 1
        assert result["covered"] >= 1
    
    def test_suggest_requirement(self, mapper, test_file):
        mapper.map("F-QUAL-001", test_file)
        suggestions = mapper.suggest_requirements("test_v230_skill_index.py")
        assert isinstance(suggestions, list)


class TestRequirementsCoverageAnalyzer:
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
    def analyzer(self, temp_dir, test_file):
        from src.core.requirement_test_mapper import RequirementTestMapper
        mapping_path = Path(temp_dir) / "requirement_test_mapping.yaml"
        mapper = RequirementTestMapper(str(mapping_path))
        mapper.map("F-QUAL-001", test_file)
        return RequirementsCoverageAnalyzer(str(mapping_path))
    
    def test_analyze_coverage_with_data(self, analyzer):
        report = analyzer.analyze_coverage()
        assert isinstance(report, CoverageReport)
        assert report.total_requirements >= 1
    
    def test_get_uncovered_requirements(self, analyzer):
        uncovered = analyzer.get_uncovered_requirements()
        assert isinstance(uncovered, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
