"""Utils模块测试"""

import pytest
import jinja2
from datetime import datetime
import os
import tempfile
from pathlib import Path


class TestDateUtils:
    """日期工具测试"""

    def test_get_current_time(self):
        """测试获取当前时间"""
        from src.utils.date import get_current_time
        result = get_current_time()
        assert isinstance(result, str)
        datetime.fromisoformat(result)

    def test_get_current_date(self):
        """测试获取当前日期"""
        from src.utils.date import get_current_date
        result = get_current_date()
        assert isinstance(result, str)
        assert len(result) == 10
        assert result[4] == "-"

    def test_format_time_valid(self):
        """测试格式化有效时间"""
        from src.utils.date import format_time
        result = format_time("2024-01-15T10:30:00")
        assert "2024-01-15" in result
        assert "10:30:00" in result

    def test_format_time_invalid(self):
        """测试格式化无效时间"""
        from src.utils.date import format_time
        result = format_time("invalid")
        assert result == "invalid"


class TestFileUtils:
    """文件工具测试"""

    def test_file_exists_false(self):
        """测试文件不存在"""
        from src.utils.file import file_exists
        assert file_exists("/nonexistent/file.txt") is False

    def test_file_exists_true(self):
        """测试文件存在"""
        from src.utils.file import file_exists
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            assert file_exists(tmp.name) is True
            os.unlink(tmp.name)

    def test_directory_exists_false(self):
        """测试目录不存在"""
        from src.utils.file import directory_exists
        assert directory_exists("/nonexistent/dir") is False

    def test_directory_exists_true(self):
        """测试目录存在"""
        from src.utils.file import directory_exists
        with tempfile.TemporaryDirectory() as tmpdir:
            assert directory_exists(tmpdir) is True

    def test_read_file_not_found(self):
        """测试读取不存在的文件"""
        from src.utils.file import read_file
        with pytest.raises(FileNotFoundError):
            read_file("/nonexistent/file.txt")

    def test_write_and_read_file(self):
        """测试写入和读取文件"""
        from src.utils.file import write_file, read_file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            content = "test content"
            write_file(str(test_file), content)
            result = read_file(str(test_file))
            assert result == content

    def test_list_files(self):
        """测试列出文件"""
        from src.utils.file import list_files
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file1.txt").touch()
            Path(tmpdir, "file2.txt").touch()
            files = list_files(tmpdir, "txt")
            assert "file1.txt" in files
            assert "file2.txt" in files

    def test_create_directory(self):
        """测试创建目录"""
        from src.utils.file import create_directory, directory_exists
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new" / "nested" / "dir"
            create_directory(str(new_dir))
            assert directory_exists(str(new_dir))

    def test_copy_file(self):
        """测试复制文件"""
        from src.utils.file import copy_file, file_exists
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "src.txt"
            dst = Path(tmpdir) / "dst.txt"
            src.write_text("content")
            copy_file(str(src), str(dst))
            assert file_exists(str(dst))
            assert dst.read_text() == "content"

    def test_remove_file(self):
        """测试删除文件"""
        from src.utils.file import remove_file, file_exists
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")
            assert file_exists(str(test_file))
            remove_file(str(test_file))
            assert file_exists(str(test_file)) is False


class TestEnvironmentUtils:
    """环境工具测试"""

    def test_get_python_command(self):
        """测试获取Python命令"""
        from src.utils.environment import get_python_command
        result = get_python_command()
        assert result in ["python", "python3"]

    def test_get_python_executable(self):
        """测试获取Python解释器路径"""
        from src.utils.environment import get_python_executable
        result = get_python_executable()
        assert isinstance(result, str)
        assert "python" in result.lower()

    def test_is_test_environment(self):
        """测试检测测试环境"""
        from src.utils.environment import is_test_environment
        result = is_test_environment()
        assert isinstance(result, bool)

    def test_get_environment_info(self):
        """测试获取环境信息"""
        from src.utils.environment import get_environment_info
        info = get_environment_info()
        assert "python_command" in info
        assert "python_executable" in info
        assert "is_test_environment" in info
        assert "python_version" in info
        assert "platform" in info


class TestLockUtils:
    """锁工具测试"""

    def test_lock_manager_acquire_release(self):
        """测试LockManager获取和释放锁"""
        from src.utils.lock import LockManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LockManager(tmpdir)
            assert manager.is_locked() is False
            manager.acquire("test lock")
            assert manager.is_locked() is True
            manager.release()
            assert manager.is_locked() is False

    def test_lock_manager_get_lock_info(self):
        """测试获取锁信息"""
        from src.utils.lock import LockManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LockManager(tmpdir)
            manager.acquire("test lock")
            info = manager.get_lock_info()
            assert info is not None
            assert "created_at" in info
            assert "pid" in info
            assert info["description"] == "test lock"
            manager.release()

    def test_lock_manager_exists_error(self):
        """测试重复加锁抛出异常"""
        from src.utils.lock import LockManager, LockExistsError
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LockManager(tmpdir)
            manager.acquire("test lock")
            with pytest.raises(LockExistsError):
                manager.acquire("another lock")
            manager.release()

    def test_lock_manager_release_not_found(self):
        """测试释放不存在的锁抛出异常"""
        from src.utils.lock import LockManager, LockNotFoundError
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LockManager(tmpdir)
            with pytest.raises(LockNotFoundError):
                manager.release()

    def test_create_lock(self):
        """测试创建锁函数"""
        from src.utils.lock import create_lock, LockManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = create_lock(tmpdir, "test")
            assert isinstance(manager, LockManager)
            assert manager.is_locked() is True
            manager.release()

    def test_remove_lock(self):
        """测试移除锁函数"""
        from src.utils.lock import create_lock, remove_lock, LockManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LockManager(tmpdir)
            manager.acquire("test")
            remove_lock(tmpdir)
            assert manager.is_locked() is False


class TestYAMLUtils:
    """YAML工具测试"""

    def test_load_yaml_not_found(self):
        """测试加载不存在的YAML文件"""
        from src.utils.yaml import load_yaml
        with pytest.raises(FileNotFoundError):
            load_yaml("/nonexistent/file.yaml")

    def test_save_and_load_yaml(self):
        """测试保存和加载YAML"""
        from src.utils.yaml import save_yaml, load_yaml
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.yaml"
            data = {"key": "value", "number": 123}
            save_yaml(str(test_file), data)
            result = load_yaml(str(test_file))
            assert result == data


class TestTemplateRenderer:
    """模板渲染器测试"""

    def test_template_engine_init(self):
        """测试模板引擎初始化"""
        from src.templates.renderer import TemplateEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(tmpdir)
            assert engine.project_path == Path(tmpdir)

    def test_template_engine_render_string(self):
        """测试渲染模板字符串"""
        from src.templates.renderer import TemplateEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(tmpdir)
            result = engine.render_string("Hello {{ name }}!", {"name": "World"})
            assert result == "Hello World!"

    def test_template_engine_list_templates(self):
        """测试列出模板"""
        from src.templates.renderer import TemplateEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(tmpdir)
            templates = engine.list_templates()
            assert isinstance(templates, list)

    def test_template_engine_template_exists_false(self):
        """测试模板不存在"""
        from src.templates.renderer import TemplateEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(tmpdir)
            assert engine.template_exists("nonexistent.html") is False

    def test_render_template_function(self):
        """测试渲染模板函数"""
        from src.templates.renderer import render_template
        with tempfile.TemporaryDirectory() as tmpdir:
            template_file = Path(tmpdir) / "test.html"
            template_file.write_text("Hello {{ name }}!")
            result = render_template("test.html", {"name": "World"}, tmpdir)
            assert result == "Hello World!"

    def test_render_template_not_found(self):
        """测试模板文件不存在"""
        from src.templates.renderer import TemplateEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = TemplateEngine(tmpdir)
            with pytest.raises(ValueError):
                engine.render("nonexistent.html", {})
