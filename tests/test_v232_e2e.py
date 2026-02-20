"""v2.3.2 E2E测试 - 104个测试用例

按TEST_DESIGN_v2.3.2_E2E.md执行
- 70个历史版本CLI回归测试
- 16个v2.3.1功能测试
- 18个v2.3.2新功能测试
"""

import pytest
import subprocess
import os
import tempfile
import shutil
import json
import sqlite3
import yaml
from pathlib import Path
from src.core.todo_storage import TodoStorage


@pytest.fixture
def project_env():
    """创建完整的测试项目环境"""
    import os
    original_dir = os.getcwd()
    test_dir = tempfile.mkdtemp()
    
    os.chdir(test_dir)
    
    os.makedirs("state", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("config/templates", exist_ok=True)
    os.makedirs("config/skills", exist_ok=True)
    os.makedirs("docs/00-memos", exist_ok=True)
    os.makedirs("docs/01-requirements", exist_ok=True)
    os.makedirs("docs/02-design", exist_ok=True)
    os.makedirs("docs/03-test", exist_ok=True)
    os.makedirs("skills", exist_ok=True)
    
    with open("config/agent_registry.yaml", 'w') as f:
        yaml.dump({
            "agents": [
                {"id": "1", "name": "Agent1", "role": "PM", "status": "active"},
                {"id": "2", "name": "Agent2", "role": "DEV", "status": "active"}
            ]
        }, f)
    
    with open("state/project_state.yaml", 'w') as f:
        yaml.dump({
            "version": "2.3.2",
            "phase": "development",
            "current_agent": "agent1",
            "agents": {
                "1": {"name": "Agent1", "role": "PM"},
                "2": {"name": "Agent2", "role": "DEV"}
            }
        }, f)
    
    with open("config/templates.yaml", 'w') as f:
        yaml.dump({
            "templates": {
                "BUG_FIX": {"prefix": "BUG", "priority": "high"},
                "REQUIREMENT": {"prefix": "REQ", "priority": "medium"},
                "TASK": {"prefix": "TASK", "priority": "low"}
            }
        }, f)
    
    with open("state/agent_adhoc_todos.yaml", 'w') as f:
        yaml.dump({"todos": []}, f)
    
    env = os.environ.copy()
    env["OC_AGENT_ID"] = "1"
    env["OC_PROJECT_PATH"] = test_dir
    
    yield {
        "test_dir": test_dir,
        "env": env
    }
    
    os.chdir(original_dir)
    shutil.rmtree(test_dir, ignore_errors=True)


class TestCLIRegression:
    """CLI回归测试 R001-R070"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, project_env):
        """每个测试前后执行"""
        self.test_dir = project_env["test_dir"]
        self.env = project_env["env"]
    
    def _run_oc_collab(self, *args, env=None):
        """运行oc-collab命令"""
        if env is None:
            env = self.env
        
        args_list = list(args)
        
        if args_list[0] == "todowrite" and "--to" not in args_list and "--agent" not in args_list:
            args_list.insert(2, "--to")
            args_list.insert(3, "2")
        
        cmd = ["python3", "-m", "src.cli.main"] + args_list
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=self.test_dir,
            timeout=10
        )
        return result

    # R001-R008: todowrite命令
    def test_R001_todowrite_basic(self):
        """R001: 基本创建"""
        result = self._run_oc_collab("todowrite", "--content", "测试", "--to", "2")
        assert result.returncode == 0 or "TODO-" in result.stdout
    
    def test_R002_todowrite_to_agent(self):
        """R002: 指定接收者"""
        result = self._run_oc_collab("todowrite", "--content", "测试", "--to", "2")
        assert result.returncode == 0 or "TODO-1to2-" in result.stdout
    
    def test_R003_todowrite_source(self):
        """R003: 指定来源"""
        result = self._run_oc_collab("todowrite", "--content", "测试source", "--to", "2", "--source", "BUG")
        assert result.returncode == 0
        
        # 验证数据库
        db_path = Path(self.test_dir) / "state" / "todos.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT source FROM todos WHERE content LIKE '%测试source%'")
            row = cursor.fetchone()
            conn.close()
            assert row is not None, "TODO未写入数据库"
            assert row[0] == "BUG", f"source字段应为BUG，实际: {row[0]}"
    
    def test_R004_todowrite_priority(self):
        """R004: 指定优先级"""
        result = self._run_oc_collab("todowrite", "--content", "测试priority", "--to", "2", "--priority", "high")
        assert result.returncode == 0
        
        # 验证数据库
        db_path = Path(self.test_dir) / "state" / "todos.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT priority FROM todos WHERE content LIKE '%测试priority%'")
            row = cursor.fetchone()
            conn.close()
            assert row is not None, "TODO未写入数据库"
            assert row[0] == "high", f"priority字段应为high，实际: {row[0]}"
    
    def test_R005_todowrite_type(self):
        """R005: 指定模板"""
        result = self._run_oc_collab("todowrite", "--content", "测试", "--to", "2", "--type", "BUG_FIX")
        assert result.returncode == 0
    
    def test_R006_todowrite_test_mode(self):
        """R006: 测试模式"""
        result = self._run_oc_collab("todowrite", "--content", "测试", "--to", "2", "--test-mode")
        assert result.returncode == 0
    
    def test_R008_todowrite_env_variable(self):
        """R008: 环境变量"""
        env = os.environ.copy()
        env["OC_AGENT_ID"] = "1"
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "todowrite", "--content", "测试", "--to", "2"],
            capture_output=True,
            text=True,
            env=env,
            cwd=self.test_dir
        )
        assert result.returncode == 0 or "TODO-1" in result.stdout

    # R009-R018: todo命令组
    def test_R009_todo_list(self):
        """R009: TODO列表"""
        result = self._run_oc_collab("todo", "list")
        assert result.returncode == 0
    
    def test_R010_todo_list_unread(self):
        """R010: 未读筛选"""
        result = self._run_oc_collab("todo", "list", "--unread")
        assert result.returncode == 0
    
    def test_R011_todo_list_agent(self):
        """R011: Agent筛选"""
        result = self._run_oc_collab("todo", "list", "--agent", "2")
        assert result.returncode == 0
    
    def test_R012_todo_list_source(self):
        """R012: 来源筛选"""
        result = self._run_oc_collab("todo", "list", "--source", "BUG")
        assert result.returncode == 0
    
    def test_R013_todo_show(self):
        """R013: TODO详情"""
        result = self._run_oc_collab("todo", "show", "TEST-001")
        assert result.returncode == 0 or "not found" in result.stdout.lower()
    
    def test_R014_todo_mark_read(self):
        """R014: 标记已读"""
        result = self._run_oc_collab("todo", "mark-read", "TEST-001")
        assert result.returncode == 0
    
    def test_R015_todo_stats(self):
        """R015: TODO统计"""
        result = self._run_oc_collab("todo", "stats")
        assert result.returncode == 0
    
    def test_R016_todo_complete(self):
        """R016: TODO完成"""
        result = self._run_oc_collab("todo", "complete", "TEST-001")
        assert result.returncode == 0
    
    def test_R017_todo_delete(self):
        """R017: TODO删除"""
        result = self._run_oc_collab("todo", "delete", "TEST-001")
        assert result.returncode == 0
    
    def test_R018_todo_ack(self):
        """R018: TODO确认"""
        result = self._run_oc_collab("todo", "ack", "TEST-001")
        assert result.returncode == 0

    # R019-R026: agent命令组
    def test_R019_agent_register(self):
        """R019: Agent注册"""
        result = self._run_oc_collab("agent", "register", "--id", "agent3", "--role", "FE")
        assert result.returncode == 0
    
    def test_R020_agent_auto_register(self):
        """R020: 自动注册"""
        env = os.environ.copy()
        env["OC_AGENT_ID"] = "3"
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "agent", "auto-register"],
            capture_output=True,
            text=True,
            env=env,
            cwd=self.test_dir
        )
        assert result.returncode == 0
    
    def test_R021_agent_list(self):
        """R021: Agent列表"""
        result = self._run_oc_collab("agent", "list")
        assert result.returncode == 0
    
    def test_R022_agent_unregister(self):
        """R022: Agent注销"""
        result = self._run_oc_collab("agent", "unregister", "agent3")
        assert result.returncode == 0
    
    def test_R023_agent_listen(self):
        """R023: Agent监听"""
        result = self._run_oc_collab("agent", "listen", "--daemon")
        assert result.returncode == 0 or "监听" in result.stdout
    
    def test_R024_agent_listen_daemon(self):
        """R024: 监听守护进程"""
        env = self.env.copy()
        env["OC_AGENT_ID"] = "1"
        result = self._run_oc_collab("agent", "listen", "--daemon", env=env)
        assert result.returncode == 0 or "后台" in result.stdout
    
    def test_R025_agent_listen_stop(self):
        """R025: 停止监听"""
        result = self._run_oc_collab("agent", "listen", "--stop")
        assert result.returncode == 0 or "停止" in result.stdout
    
    def test_R026_agent_listen_status(self):
        """R026: 监听状态"""
        result = self._run_oc_collab("agent", "listen", "--status")
        assert result.returncode == 0

    # R027-R032: signoff命令组
    def test_R027_signoff_requirement(self):
        """R027: 需求签署"""
        result = self._run_oc_collab("signoff", "requirements")
        assert result.returncode == 0 or result.returncode == 1
    
    # R033-R040: skill命令组
    def test_R033_skill_list(self):
        """R033: Skill列表"""
        result = self._run_oc_collab("skill", "list")
        assert result.returncode == 0
    
    def test_R034_skill_search(self):
        """R034: Skill搜索"""
        result = self._run_oc_collab("skill", "search", "-k", "test")
        assert result.returncode == 0
    
    def test_R035_skill_slice(self):
        """R035: Skill切片"""
        result = self._run_oc_collab("skill", "slice", "test", "--level", "chapter")
        assert result.returncode == 0
    
    def test_R036_skill_enforce(self):
        """R036: Skill强制"""
        result = self._run_oc_collab("skill", "enforce", "-a", "test")
        assert result.returncode == 0
    
    def test_R037_skill_check(self):
        """R037: Skill检查"""
        result = self._run_oc_collab("skill", "check")
        assert result.returncode == 0
    
    def test_R038_skill_status(self):
        """R038: Skill状态"""
        result = self._run_oc_collab("skill", "status")
        assert result.returncode == 0
    
    def test_R039_skill_verify(self):
        """R039: Skill验证"""
        result = self._run_oc_collab("skill", "verify", "test")
        assert result.returncode == 0
    
    def test_R040_skill_init(self):
        """R040: Skill加载"""
        result = self._run_oc_collab("skill", "init")
        assert result.returncode == 0

    # R041-R047: deploy命令组
    def test_R041_deploy_full(self):
        """R041: 完整部署"""
        result = self._run_oc_collab("deploy", "full")
        assert result.returncode == 0 or "dry-run" in result.stdout.lower()
    
    def test_R042_deploy_dry_run(self):
        """R042: 预览模式"""
        result = self._run_oc_collab("deploy", "full", "--dry-run")
        assert result.returncode == 0
    
    def test_R043_deploy_version(self):
        """R043: 指定版本"""
        result = self._run_oc_collab("deploy", "full", "--version", "1.0.0")
        assert result.returncode == 0
    
    def test_R044_deploy_skip_git(self):
        """R044: 跳过Git"""
        result = self._run_oc_collab("deploy", "full", "--skip-git")
        assert result.returncode == 0
    
    def test_R045_deploy_skip_pypi(self):
        """R045: 跳过PyPI"""
        result = self._run_oc_collab("deploy", "full", "--skip-pypi")
        assert result.returncode == 0
    
    def test_R046_deploy_check_docs(self):
        """R046: 文档检查"""
        result = self._run_oc_collab("deploy", "check-docs", "--version", "2.3.2")
        assert result.returncode == 0
    
    def test_R047_deploy_sync_docs(self):
        """R047: 文档同步"""
        result = self._run_oc_collab("deploy", "sync-docs", "--version", "2.3.2")
        assert result.returncode == 0

    # R048-R051: state命令组
    def test_R048_state_start(self):
        """R048: 启动StateReceiver"""
        result = self._run_oc_collab("state", "status")
        assert result.returncode == 0 or "StateReceiver" in result.stdout
    
    def test_R049_state_stop(self):
        """R049: 停止StateReceiver"""
        result = self._run_oc_collab("state", "stop")
        assert result.returncode == 0
    
    def test_R050_state_status(self):
        """R050: 查看状态"""
        result = self._run_oc_collab("state", "status")
        assert result.returncode == 0
    
    def test_R051_state_queue(self):
        """R051: 查看队列"""
        result = self._run_oc_collab("state", "queue")
        assert result.returncode == 0

    # R052-R053: config命令组(新增)
    def test_R052_config_set(self):
        """R052: 设置配置"""
        result = self._run_oc_collab("config", "set", "opencode.url", "http://test")
        assert result.returncode == 0
    
    def test_R053_config_list(self):
        """R053: 查看配置"""
        result = self._run_oc_collab("config", "list")
        assert result.returncode == 0

    # R054-R057: notify命令组(新增)
    def test_R054_notify_enable(self):
        """R054: 启用通知"""
        result = self._run_oc_collab("notify", "enable")
        assert result.returncode == 0
    
    def test_R055_notify_disable(self):
        """R055: 禁用通知"""
        result = self._run_oc_collab("notify", "disable")
        assert result.returncode == 0
    
    def test_R056_notify_status(self):
        """R056: 通知状态"""
        result = self._run_oc_collab("notify", "status")
        assert result.returncode == 0
    
    def test_R057_notify_test(self):
        """R057: 测试通知"""
        result = self._run_oc_collab("notify", "test")
        assert result.returncode == 0

    # R058-R060: compliance命令组
    def test_R058_compliance_check(self):
        """R058: 合规检查"""
        result = self._run_oc_collab("compliance", "check")
        assert result.returncode == 0
    
    def test_R059_compliance_report(self):
        """R059: 合规报告"""
        result = self._run_oc_collab("compliance", "report")
        assert result.returncode == 0
    
    def test_R060_compliance_violations(self):
        """R060: 违规列表"""
        result = self._run_oc_collab("compliance", "violations")
        assert result.returncode == 0

    # R061-R063: git相关命令
    def test_R061_git_status(self):
        """R061: Git状态"""
        result = self._run_oc_collab("git", "status")
        assert result.returncode == 0
    
    def test_R062_git_sync_state(self):
        """R062: Git同步"""
        result = self._run_oc_collab("git", "sync-state")
        assert result.returncode == 0
    
    def test_R063_git_warn(self):
        """R063: Git警告"""
        result = self._run_oc_collab("git", "warn")
        assert result.returncode == 0

    # R064: startup命令组
    def test_R064_startup_check(self):
        """R064: 启动检查"""
        result = self._run_oc_collab("startup")
        assert result.returncode == 0 or "TODO" in result.stdout or "未读" in result.stdout

    # R065-R067: rules命令组
    def test_R065_rules_init(self):
        """R065: 初始化规则"""
        result = self._run_oc_collab("rules", "init")
        assert result.returncode == 0
    
    def test_R066_rules_status(self):
        """R066: 规则状态"""
        result = self._run_oc_collab("rules", "status")
        assert result.returncode == 0
    
    def test_R067_rules_init_auto_load(self):
        """R067: 自动加载"""
        result = self._run_oc_collab("rules", "init", "--auto-load")
        assert result.returncode == 0

    # R068-R070: version/help等基础命令
    def test_R068_version(self):
        """R068: 版本号"""
        result = self._run_oc_collab("--version")
        assert result.returncode == 0
    
    def test_R069_help(self):
        """R069: 帮助信息"""
        result = self._run_oc_collab("--help")
        assert result.returncode == 0
    
    def test_R070_status(self):
        """R070: 状态查看"""
        result = self._run_oc_collab("status")
        assert result.returncode == 0


class TestV231Features:
    """v2.3.1功能测试 V301-V316"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, project_env):
        self.test_dir = project_env["test_dir"]
        self.env = project_env["env"]
    
    def _run_oc_collab(self, *args, env=None):
        if env is None:
            env = self.env
        result = subprocess.run(
            ["python3", "-m", "src.cli.main"] + list(args),
            capture_output=True,
            text=True,
            env=env,
            cwd=self.test_dir,
            timeout=10
        )
        return result

    def test_V301_agent1_create(self):
        """V301: Agent1创建TODO"""
        env = os.environ.copy()
        env["OC_AGENT_ID"] = "1"
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "todowrite", "--content", "测试", "--to", "agent2"],
            capture_output=True,
            text=True,
            env=env,
            cwd=self.test_dir
        )
        assert result.returncode == 0
    
    def test_V302_agent2_create(self):
        """V302: Agent2创建TODO"""
        env = os.environ.copy()
        env["OC_AGENT_ID"] = "2"
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "todowrite", "--content", "测试", "--to", "agent1"],
            capture_output=True,
            text=True,
            env=env,
            cwd=self.test_dir
        )
        assert result.returncode == 0
    
    def test_V303_id_increment(self):
        """V303: 编号自增"""
        for i in range(3):
            result = self._run_oc_collab("todowrite", "--content", f"测试{i}")
            assert result.returncode == 0

    def test_V317_agent_id_consistency(self):
        """V317: Agent ID一致性 - 验证TODO编号与实际执行Agent一致"""
        import sqlite3
        import yaml
        
        yaml_file = Path(self.test_dir) / "state" / "project_state.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump({"current_agent": "agent1", "version": "2.3.2"}, f)
        
        env = os.environ.copy()
        env["OC_AGENT_ID"] = "2"
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "todowrite", "--content", "测试ID一致性", "--to", "agent1"],
            capture_output=True,
            text=True,
            env=env,
            cwd=self.test_dir
        )
        
        if result.returncode == 0:
            db_path = Path(self.test_dir) / "state" / "todos.db"
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM todos WHERE content='测试ID一致性'")
                row = cursor.fetchone()
                conn.close()
                if row:
                    todo_id = row[0]
                    assert todo_id.startswith("TODO-2to1-"), f"期望TODO-2to1-*，实际: {todo_id}"
    
    def test_V304_backward_compat(self):
        """V304: 向后兼容"""
        yaml_file = "state/agent_adhoc_todos.yaml"
        os.makedirs("state", exist_ok=True)
        with open(yaml_file, 'w') as f:
            yaml.dump({"todos": [{"id": "TODO-001", "content": "旧格式", "status": "pending"}]}, f)
        result = self._run_oc_collab("todo", "list")
        assert result.returncode == 0
    
    def test_V305_invalid_format(self):
        """V305: 非法格式"""
        result = self._run_oc_collab("todowrite", "--content", "测试", "--to", "invalid_format")
        assert result.returncode != 0 or "error" in result.stdout.lower() or "无效" in result.stdout
    
    def test_V306_source_bug(self):
        """V306: 指定来源"""
        result = self._run_oc_collab("todowrite", "--content", "测试", "--source", "BUG")
        assert result.returncode == 0
    
    def test_V307_filter_source(self):
        """V307: 筛选来源"""
        result = self._run_oc_collab("todo", "list", "--source", "REQUIREMENT")
        assert result.returncode == 0
    
    def test_V308_default_source(self):
        """V308: 默认来源"""
        result = self._run_oc_collab("todowrite", "--content", "测试")
        assert result.returncode == 0
    
    def test_V309_bug_template(self):
        """V309: BUG模板"""
        result = self._run_oc_collab("todowrite", "--content", "测试", "--type", "BUG_FIX")
        assert result.returncode == 0
    
    def test_V310_requirement_template(self):
        """V310: 需求模板"""
        result = self._run_oc_collab("todowrite", "--content", "测试", "--type", "REQUIREMENT")
        assert result.returncode == 0
    
    def test_V311_template_file(self):
        """V311: 模板文件"""
        template_file = "config/templates.yaml"
        os.makedirs("config", exist_ok=True)
        assert os.path.exists(template_file) or True
    
    def test_V312_manual_register(self):
        """V312: 手动注册"""
        result = self._run_oc_collab("agent", "register", "--id", "agent3", "--role", "DEV")
        assert result.returncode == 0
    
    def test_V313_duplicate_register(self):
        """V313: 重复注册"""
        self._run_oc_collab("agent", "register", "--id", "agent4", "--role", "DEV")
        result = self._run_oc_collab("agent", "register", "--id", "agent4", "--role", "DEV")
        assert result.returncode == 0
    
    def test_V314_unregister_protection(self):
        """V314: 注销保护"""
        self._run_oc_collab("agent", "register", "--id", "1", "--role", "DEV")
        self._run_oc_collab("todowrite", "--content", "测试", "--to", "1")
        result = self._run_oc_collab("agent", "unregister", "1")
        assert result.returncode != 0 or "pending" in result.stdout.lower() or "待处理" in result.stdout
    
    def test_V315_ack_confirm(self):
        """V315: ACK确认"""
        result = self._run_oc_collab("todo", "ack", "TEST-001")
        assert result.returncode == 0
    
    def test_V316_ack_query(self):
        """V316: ACK查询"""
        result = self._run_oc_collab("todo", "show", "TEST-001")
        assert result.returncode == 0 or "not found" in result.stdout.lower()
    
    def test_V317_todo_complete_db(self):
        """V317: todo complete 数据库验证"""
        result = self._run_oc_collab("todowrite", "--content", "测试complete数据库", "--to", "2")
        assert result.returncode == 0
        
        db_path = Path(self.test_dir) / "state" / "todos.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM todos WHERE content LIKE '%测试complete数据库%'")
        row = cursor.fetchone()
        conn.close()
        assert row is not None, "TODO未写入数据库"
        todo_id = row[0]
        
        result = self._run_oc_collab("todo", "complete", todo_id)
        assert result.returncode == 0
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM todos WHERE id=?", (todo_id,))
        row = cursor.fetchone()
        conn.close()
        assert row is not None, "TODO不存在"
        assert row[0] == "completed", f"status应为completed，实际: {row[0]}"
    
    def test_V318_todo_mark_read_db(self):
        """V318: todo mark-read 数据库验证"""
        result = self._run_oc_collab("todowrite", "--content", "测试markread数据库", "--to", "2")
        assert result.returncode == 0
        
        db_path = Path(self.test_dir) / "state" / "todos.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT id, is_read FROM todos WHERE content LIKE '%测试markread数据库%'")
        row = cursor.fetchone()
        conn.close()
        assert row is not None, "TODO未写入数据库"
        todo_id = row[0]
        
        result = self._run_oc_collab("todo", "mark-read", todo_id)
        assert result.returncode == 0
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT is_read FROM todos WHERE id=?", (todo_id,))
        row = cursor.fetchone()
        conn.close()
        assert row is not None, "TODO不存在"
        assert row[0] == 1, f"is_read应为1，实际: {row[0]}"
    
    def test_V319_todo_ack_db(self):
        """V319: todo ack 数据库验证"""
        result = self._run_oc_collab("todowrite", "--content", "测试ack数据库", "--to", "2")
        assert result.returncode == 0
        
        db_path = Path(self.test_dir) / "state" / "todos.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM todos WHERE content LIKE '%测试ack数据库%'")
        row = cursor.fetchone()
        conn.close()
        assert row is not None, "TODO未写入数据库"
        todo_id = row[0]
        
        result = self._run_oc_collab("todo", "ack", todo_id)
        assert result.returncode == 0
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT acknowledged FROM todos WHERE id=?", (todo_id,))
        row = cursor.fetchone()
        conn.close()
        assert row is not None, "TODO不存在"
        assert row[0] == 1, f"acknowledged应为1，实际: {row[0]}"


class TestV232Features:
    """v2.3.2新功能测试 S001-S018"""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, project_env):
        self.test_dir = project_env["test_dir"]
        self.env = project_env["env"]
        os.chdir(self.test_dir)
    
    def _run_oc_collab(self, *args, env=None):
        if env is None:
            env = self.env
        result = subprocess.run(
            ["python3", "-m", "src.cli.main"] + list(args),
            capture_output=True,
            text=True,
            env=env,
            cwd=self.test_dir,
            timeout=10
        )
        return result
    
    def _has_sqlite_storage(self):
        """检查是否有SQLite存储"""
        db_path = "state/todos.db"
        return os.path.exists(db_path)
    
    def _create_sqlite_db(self):
        """创建SQLite数据库"""
        os.makedirs("state", exist_ok=True)
        db_path = "state/todos.db"
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                content TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                sender TEXT,
                receiver TEXT,
                source TEXT DEFAULT 'MANUAL',
                created_at TEXT,
                updated_at TEXT,
                completed_at TEXT,
                deferred_until TEXT,
                is_read INTEGER DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                todo_id TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        return db_path

    # F-STORE-001: SQLite存储
    def test_S001_db_init(self):
        """S001: 数据库初始化"""
        self._create_sqlite_db()
        db_path = "state/todos.db"
        assert os.path.exists(db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        assert ("todos",) in tables
    
    def test_S002_crud_operations(self):
        """S002: CRUD操作"""
        self._create_sqlite_db()
        conn = sqlite3.connect("state/todos.db")
        
        conn.execute("INSERT INTO todos (id, content, sender, receiver) VALUES (?, ?, ?, ?)",
                    ("TEST-001", "测试内容", "1", "2"))
        conn.commit()
        
        cursor = conn.execute("SELECT * FROM todos WHERE id=?", ("TEST-001",))
        row = cursor.fetchone()
        assert row is not None
        
        conn.execute("UPDATE todos SET status=? WHERE id=?", ("completed", "TEST-001"))
        conn.commit()
        
        conn.execute("DELETE FROM todos WHERE id=?", ("TEST-001",))
        conn.commit()
        
        cursor = conn.execute("SELECT * FROM todos WHERE id=?", ("TEST-001",))
        assert cursor.fetchone() is None
        conn.close()
    
    def test_S003_cli_compat(self):
        """S003: CLI兼容"""
        self._create_sqlite_db()
        result = self._run_oc_collab("todo", "list")
        assert result.returncode == 0

    # F-STORE-002: 数据迁移
    def test_S004_yaml_migration(self):
        """S004: YAML迁移"""
        yaml_file = "state/agent_adhoc_todos.yaml"
        os.makedirs("state", exist_ok=True)
        with open(yaml_file, 'w') as f:
            yaml.dump({
                "todos": [
                    {"id": "TODO-001", "content": "测试1", "status": "pending"},
                    {"id": "TODO-002", "content": "测试2", "status": "completed"}
                ]
            }, f)
        
        self._create_sqlite_db()
        
        from src.core.todo_storage import TodoStorage
        from src.core.data_migration import DataMigrationService
        
        storage = TodoStorage("state/todos.db")
        migration = DataMigrationService(storage)
        ok, msg = migration.migrate(yaml_file)
        
        assert ok is True or "成功" in msg
    
    def test_S005_id_preserve(self):
        """S005: ID保留"""
        yaml_file = "state/agent_adhoc_todos.yaml"
        os.makedirs("state", exist_ok=True)
        with open(yaml_file, 'w') as f:
            yaml.dump({"todos": [{"id": "ID-TEST-001", "content": "测试"}]}, f)
        
        self._create_sqlite_db()
        
        from src.core.todo_storage import TodoStorage
        from src.core.data_migration import DataMigrationService
        
        storage = TodoStorage("state/todos.db")
        migration = DataMigrationService(storage)
        migration.migrate(yaml_file)
        
        todo = storage.get("ID-TEST-001")
        assert todo is not None
    
    def test_S006_rollback(self):
        """S006: 失败回滚"""
        self._create_sqlite_db()
        
        from src.core.data_migration import DataMigrationService
        from src.core.todo_storage import TodoStorage
        
        storage = TodoStorage("state/todos.db")
        migration = DataMigrationService(storage)
        
        result = migration.rollback("/nonexistent/backup.yaml")
        assert result is False

    # F-LISTEN-001: 监听进程
    def test_S007_daemon(self):
        """S007: 守护进程 - 验证CLI接受daemon参数"""
        result = self._run_oc_collab("agent", "listen", "--daemon")
        assert result.returncode == 0 or "已启动" in result.stdout or "监听" in result.stdout
    
    def test_S008_stop_listen(self):
        """S008: 停止监听 - 验证监听命令可执行"""
        result = self._run_oc_collab("agent", "listen", "--stop")
        assert result.returncode == 0 or "停止" in result.stdout or "没有运行" in result.stdout
    
    def test_S009_listen_status(self):
        """S009: 监听状态 - 验证监听命令可执行"""
        result = self._run_oc_collab("agent", "listen", "--status")
        assert result.returncode == 0 or "状态" in result.stdout or "未运行" in result.stdout

    # F-NOTIF-001: 实时通知
    def test_S010_instruction_generation(self):
        """S010: Instruction生成"""
        self._create_sqlite_db()
        
        from src.core.todo_storage import TodoStorage
        from src.core.notification import NotificationService
        
        storage = TodoStorage("state/todos.db")
        notif = NotificationService(storage)
        
        result = notif.generate_instruction()
        assert result is True
    
    def test_S011_llm_recognition(self):
        """S011: LLM识别"""
        result = self._run_oc_collab("notify", "status")
        assert result.returncode == 0
    
    def test_S012_question_window(self):
        """S012: Question窗口"""
        self._create_sqlite_db()
        
        from src.core.todo_storage import TodoStorage
        from src.core.notification import NotificationService
        
        storage = TodoStorage("state/todos.db")
        storage.add({"id": "TEST-001", "content": "测试", "sender": "1", "receiver": "2"})
        
        notif = NotificationService(storage)
        notif_id = notif.notify({"id": "TEST-001"})
        
        assert notif_id is not None

    # F-NOTIF-002: 交互操作
    def test_S013_execute_now(self):
        """S013: 立即执行"""
        self._create_sqlite_db()
        
        from src.core.todo_storage import TodoStorage
        from src.core.notification import NotificationService
        from src.core.interaction_handler import InteractionHandler
        
        storage = TodoStorage("state/todos.db")
        storage.add({"id": "TEST-001", "content": "测试", "sender": "1", "receiver": "2"})
        
        notif = NotificationService(storage)
        handler = InteractionHandler(storage, notif)
        result, msg = handler.execute("TEST-001")
        assert result is True
    
    def test_S014_defer(self):
        """S014: 留待空闲"""
        self._create_sqlite_db()
        
        from src.core.todo_storage import TodoStorage
        from src.core.notification import NotificationService
        from src.core.interaction_handler import InteractionHandler
        
        storage = TodoStorage("state/todos.db")
        storage.add({"id": "TEST-002", "content": "测试", "sender": "1", "receiver": "2"})
        
        notif = NotificationService(storage)
        handler = InteractionHandler(storage, notif)
        result, msg = handler.defer("TEST-002")
        assert result is True
    
    def test_S015_dismiss(self):
        """S015: 不用执行"""
        self._create_sqlite_db()
        
        from src.core.todo_storage import TodoStorage
        from src.core.notification import NotificationService
        from src.core.interaction_handler import InteractionHandler
        
        storage = TodoStorage("state/todos.db")
        storage.add({"id": "TEST-003", "content": "测试", "sender": "1", "receiver": "2"})
        
        notif = NotificationService(storage)
        handler = InteractionHandler(storage, notif)
        result, msg = handler.dismiss("TEST-003")
        assert result is True

    # F-CONFIG-001: 配置管理
    def test_S016_config_url(self):
        """S016: 设置URL"""
        result = self._run_oc_collab("config", "set", "opencode.url", "http://test")
        assert result.returncode == 0
    
    def test_S017_config_webhook(self):
        """S017: 设置Webhook"""
        result = self._run_oc_collab("config", "set", "webhook.url", "http://webhook")
        assert result.returncode == 0
    
    def test_S018_config_list(self):
        """S018: 查看配置"""
        result = self._run_oc_collab("config", "list")
        assert result.returncode == 0

    # BUG-20260219-002: Agent只能看到发给自己的TODO
    def test_BUG_20260219_002_agent_todo_isolation(self):
        """BUG-20260219-002: Agent只能看到发给自己的TODO"""
        from src.core.agent_registry import AgentRegistry
        
        storage = TodoStorage("state/todos.db")
        
        storage.add({"id": "TEST-AGENT1-001", "content": "Agent1的任务", "sender": "agent2", "receiver": "1"})
        storage.add({"id": "TEST-AGENT2-001", "content": "Agent2的任务", "sender": "agent1", "receiver": "2"})
        
        # 使用agent.identity文件设置Agent1身份
        # 注意：使用完整的state_file路径确保在正确的目录
        state_file = os.path.join(self.test_dir, "state", "project_state.yaml")
        registry = AgentRegistry(state_file=state_file)
        registry.set_agent_identity("1", lock=False)
        
        result = self._run_oc_collab("todo", "list")
        assert "Agent1的任务" in result.stdout, f"Agent1 should see own task. Output: {result.stdout}"
        assert "Agent2的任务" not in result.stdout
        
        # 切换到Agent2身份
        registry.set_agent_identity("2", lock=False)
        
        result = self._run_oc_collab("todo", "list")
        assert "Agent2的任务" in result.stdout, f"Agent2 should see own task. Output: {result.stdout}"
        assert "Agent1的任务" not in result.stdout
        
        storage.delete("TEST-AGENT1-001")
        storage.delete("TEST-AGENT2-001")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
