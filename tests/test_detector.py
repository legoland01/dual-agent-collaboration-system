"""ProjectDetector 单元测试。"""
import tempfile
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.detector import ProjectDetector, detect_project_type, PROJECT_TYPE_PYTHON, PROJECT_TYPE_TYPESCRIPT, PROJECT_TYPE_MIXED, PROJECT_TYPE_AUTO


class TestProjectTypeConstants:
    """项目类型常量测试。"""

    def test_python_type(self):
        """测试Python项目类型常量。"""
        assert PROJECT_TYPE_PYTHON == "PYTHON"

    def test_typescript_type(self):
        """测试TypeScript项目类型常量。"""
        assert PROJECT_TYPE_TYPESCRIPT == "TYPESCRIPT"

    def test_mixed_type(self):
        """测试混合项目类型常量。"""
        assert PROJECT_TYPE_MIXED == "MIXED"

    def test_auto_type(self):
        """测试自动检测项目类型常量。"""
        assert PROJECT_TYPE_AUTO == "AUTO"


class TestProjectDetector:
    """项目检测器测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_initialization(self, temp_dir):
        """测试初始化。"""
        detector = ProjectDetector(temp_dir)
        assert detector.project_path == Path(temp_dir)

    def test_detect_python_project(self, temp_dir):
        """测试Python项目检测。"""
        Path(temp_dir, "pyproject.toml").touch()

        detector = ProjectDetector(temp_dir)
        result = detector.detect()

        assert result == PROJECT_TYPE_PYTHON

    def test_detect_typescript_project(self, temp_dir):
        """测试TypeScript项目检测。"""
        Path(temp_dir, "package.json").touch()
        Path(temp_dir, "tsconfig.json").touch()

        detector = ProjectDetector(temp_dir)
        result = detector.detect()

        assert result == PROJECT_TYPE_TYPESCRIPT

    def test_detect_mixed_project(self, temp_dir):
        """测试混合项目检测。"""
        Path(temp_dir, "pyproject.toml").touch()
        Path(temp_dir, "package.json").touch()

        detector = ProjectDetector(temp_dir)
        result = detector.detect()

        assert result == PROJECT_TYPE_MIXED

    def test_detect_auto_project(self, temp_dir):
        """测试自动检测（无特征文件）。"""
        detector = ProjectDetector(temp_dir)
        result = detector.detect()

        assert result == PROJECT_TYPE_AUTO

    def test_is_python_project_true(self, temp_dir):
        """测试是Python项目。"""
        Path(temp_dir, "requirements.txt").touch()

        detector = ProjectDetector(temp_dir)
        assert detector.is_python_project() == True

    def test_is_python_project_false(self, temp_dir):
        """测试不是Python项目。"""
        detector = ProjectDetector(temp_dir)
        assert detector.is_python_project() == False

    def test_is_typescript_project_true(self, temp_dir):
        """测试是TypeScript项目。"""
        Path(temp_dir, "tsconfig.json").touch()

        detector = ProjectDetector(temp_dir)
        assert detector.is_typescript_project() == True

    def test_is_typescript_project_false(self, temp_dir):
        """测试不是TypeScript项目。"""
        detector = ProjectDetector(temp_dir)
        assert detector.is_typescript_project() == False

    def test_get_detection_details(self, temp_dir):
        """测试获取检测详情。"""
        Path(temp_dir, "pyproject.toml").touch()

        detector = ProjectDetector(temp_dir)
        details = detector.get_detection_details()

        assert "python_score" in details
        assert "typescript_score" in details
        assert details["python_score"] == 1
        assert details["typescript_score"] == 0

    def test_count_python_indicators(self, temp_dir):
        """测试统计Python特征文件。"""
        Path(temp_dir, "pyproject.toml").touch()
        Path(temp_dir, "requirements.txt").touch()

        detector = ProjectDetector(temp_dir)
        count = detector._count_python_indicators()

        assert count == 2

    def test_count_typescript_indicators(self, temp_dir):
        """测试统计TypeScript特征文件。"""
        Path(temp_dir, "package.json").touch()

        detector = ProjectDetector(temp_dir)
        count = detector._count_typescript_indicators()

        assert count == 1

    def test_all_python_indicators(self, temp_dir):
        """测试所有Python特征文件。"""
        for indicator in ProjectDetector.PYTHON_INDICATORS:
            Path(temp_dir, indicator).touch()

        detector = ProjectDetector(temp_dir)
        result = detector.detect()

        assert result == PROJECT_TYPE_PYTHON
        assert detector._count_python_indicators() == len(ProjectDetector.PYTHON_INDICATORS)

    def test_all_typescript_indicators(self, temp_dir):
        """测试所有TypeScript特征文件。"""
        for indicator in ProjectDetector.TYPESCRIPT_INDICATORS:
            Path(temp_dir, indicator).touch()

        detector = ProjectDetector(temp_dir)
        result = detector.detect()

        assert result == PROJECT_TYPE_TYPESCRIPT
        assert detector._count_typescript_indicators() == len(ProjectDetector.TYPESCRIPT_INDICATORS)

    def test_multiple_python_indicators(self, temp_dir):
        """测试多个Python特征文件。"""
        Path(temp_dir, "pyproject.toml").touch()
        Path(temp_dir, "setup.py").touch()
        Path(temp_dir, "requirements.txt").touch()

        detector = ProjectDetector(temp_dir)
        assert detector.is_python_project() is True
        assert detector._count_python_indicators() == 3

    def test_detection_priority_mixed(self, temp_dir):
        """测试混合项目优先级。"""
        Path(temp_dir, "pyproject.toml").touch()
        Path(temp_dir, "package.json").touch()
        Path(temp_dir, "tsconfig.json").touch()

        detector = ProjectDetector(temp_dir)
        result = detector.detect()

        assert result == PROJECT_TYPE_MIXED

    def test_detection_empty_path(self, temp_dir):
        """测试空目录检测。"""
        detector = ProjectDetector(temp_dir)
        result = detector.detect()

        assert result == PROJECT_TYPE_AUTO

    def test_detection_details_empty(self, temp_dir):
        """测试空目录检测详情。"""
        detector = ProjectDetector(temp_dir)
        details = detector.get_detection_details()

        assert details["python_score"] == 0
        assert details["typescript_score"] == 0

    def test_python_indicators_constant(self):
        """测试Python特征常量。"""
        assert "pyproject.toml" in ProjectDetector.PYTHON_INDICATORS
        assert "setup.py" in ProjectDetector.PYTHON_INDICATORS
        assert "requirements.txt" in ProjectDetector.PYTHON_INDICATORS
        assert "setup.cfg" in ProjectDetector.PYTHON_INDICATORS
        assert "Pipfile" in ProjectDetector.PYTHON_INDICATORS

    def test_typescript_indicators_constant(self):
        """测试TypeScript特征常量。"""
        assert "package.json" in ProjectDetector.TYPESCRIPT_INDICATORS
        assert "tsconfig.json" in ProjectDetector.TYPESCRIPT_INDICATORS


class TestDetectProjectType:
    """detect_project_type 函数测试。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_detect_project_type_function_python(self, temp_dir):
        """测试项目类型检测函数（Python）。"""
        Path(temp_dir, "pyproject.toml").touch()

        result = detect_project_type(str(temp_dir))
        assert result == PROJECT_TYPE_PYTHON

    def test_detect_project_type_function_auto(self, temp_dir):
        """测试项目类型检测函数（自动）。"""
        result = detect_project_type(str(temp_dir))
        assert result == PROJECT_TYPE_AUTO

    def test_detect_project_type_function_mixed(self, temp_dir):
        """测试项目类型检测函数（混合）。"""
        Path(temp_dir, "pyproject.toml").touch()
        Path(temp_dir, "package.json").touch()

        result = detect_project_type(str(temp_dir))
        assert result == PROJECT_TYPE_MIXED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
