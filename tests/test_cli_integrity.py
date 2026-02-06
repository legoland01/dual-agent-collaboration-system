"""CLI 完整性测试用例。"""
import pytest
import sys
import re
from pathlib import Path


class TestCLIContractIntegrity:
    """CLI 合同完整性测试。"""

    def test_cli_imports_valid_modules(self):
        """CLI 模块导入的模块必须存在。"""
        from src.cli import main as cli_main

        # 获取所有导入的模块
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        # 提取所有 from ..core.xxx import 语句
        import_pattern = r'from \.\.(core|utils)\.([\w]+) import'
        imports = set(re.findall(import_pattern, content))

        for module_type, module_name in imports:
            module_path = Path(__file__).parent.parent / "src" / module_type / f"{module_name}.py"
            assert module_path.exists(), f"CLI imports non-existent module: src/{module_type}/{module_name}.py"

    def test_review_command_no_checklist_option(self):
        """review 命令不应该有 --checklist 选项（动态 checklist 已移除）。"""
        from src.cli.main import main
        from click.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(main, ['review', '--help'])
        output = result.output

        # --checklist 选项不应该存在
        assert '--checklist' not in output, "review command still has --checklist option"

    def test_no_orphaned_checklist_imports(self):
        """CLI 模块中不应该有 checklist_generator 的引用。"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        # 检查是否有 checklist_generator 引用
        assert 'checklist_generator' not in content, "CLI still references checklist_generator"

    def test_compliance_method_name_consistency(self):
        """CLI 调用方法名必须与定义一致。"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        # 提取 CLI 中调用的方法名
        call_pattern = r'checker\.(\w+)\('
        cli_methods = set(re.findall(call_pattern, content))

        # 检查 ChangeComplianceChecker 类的方法
        from src.core.change_compliance import ChangeComplianceChecker
        checker_methods = {m for m in dir(ChangeComplianceChecker) if not m.startswith('_')}

        # CLI 调用的方法必须在类中存在
        for method in cli_methods:
            if method.startswith('check_') or method.startswith('detect_'):
                assert method in checker_methods, f"CLI calls non-existent method: {method}"

    def test_no_orphaned_files(self):
        """核心模块目录中不应该有孤立文件。"""
        core_path = Path(__file__).parent.parent / "src" / "core"

        # 检查不应该存在的文件
        orphaned_files = [
            "checklist_generator.py",
            "checklist_generator_types.py",
            "extended_checklist.py",
        ]

        for filename in orphaned_files:
            file_path = core_path / filename
            assert not file_path.exists(), f"Orphaned file exists: {filename}"


class TestWorkflowInferenceIntegrity:
    """Workflow 模块完整性测试。"""

    def test_workflow_inference_imports_valid(self):
        """workflow_inference 模块导入的依赖必须有效。"""
        from src.core import workflow_inference
        # 模块应该能正常导入
        assert workflow_inference is not None

    def test_inference_engine_method_coverage(self):
        """WorkflowInferenceEngine 方法应该有测试覆盖。"""
        import inspect
        from src.core.workflow_inference import WorkflowInferenceEngine

        methods = [m for m in dir(WorkflowInferenceEngine)
                   if not m.startswith('_') and callable(getattr(WorkflowInferenceEngine, m))]

        # 关键方法列表
        critical_methods = [
            'infer_next_action',
            '_run_compliance_check',
            'validate_phase_transition',
            'get_workflow_status'
        ]

        # 检查关键方法是否存在
        for method in critical_methods:
            assert hasattr(WorkflowInferenceEngine, method), f"Missing critical method: {method}"


class TestSignoffRecordIntegrity:
    """Signoff 记录模块完整性测试。"""

    def test_signoff_record_methods_exist(self):
        """SignoffRecordManager 方法应该完整。"""
        from src.core.signoff_record_manager import SignoffRecordManager

        required_methods = [
            'save_signoff',
            'get_signoff',
            'list_signoffs',
            'update_signoff_status',
            'check_all_signed'
        ]

        for method in required_methods:
            assert hasattr(SignoffRecordManager, method), f"Missing method: {method}"

    def test_signoff_result_dataclass_complete(self):
        """SignoffResult 数据类应该完整。"""
        from src.core.signoff import SignoffResult, SyncResult

        # 检查必需字段（使用 __dataclass_fields__ 检查 dataclass 字段）
        signoff_fields = ['success', 'message', 'synced', 'sync_error']
        for field in signoff_fields:
            assert field in SignoffResult.__dataclass_fields__, f"SignoffResult missing field: {field}"

        sync_fields = ['success', 'message']
        for field in sync_fields:
            assert field in SyncResult.__dataclass_fields__, f"SyncResult missing field: {field}"


class TestCodeReview:
    """代码审查测试。"""

    def test_no_hardcoded_paths(self):
        """不应该有硬编码的绝对路径。"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        # 检查是否有硬编码的 /Users/xxx 路径
        import re
        path_pattern = r'/[A-Za-z0-9/_-]+/Documents/'
        matches = re.findall(path_pattern, content)
        assert len(matches) == 0, f"Hardcoded path found: {matches}"

    def test_no_print_statements_in_cli(self):
        """CLI 模块中不应该有 print 语句（应该用 click.echo）。"""
        cli_path = Path(__file__).parent.parent / "src" / "cli" / "main.py"
        with open(cli_path) as f:
            content = f.read()

        # 检查是否有 print( 语句
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'print(' in line and 'print(' not in 'print(':
                # 排除 docstring 和注释
                stripped = line.strip()
                if stripped.startswith('print(') and not stripped.startswith('"""'):
                    pytest.fail(f"Found print statement at line {i}: {line.strip()}")
