"""v2.2.6 用户场景验收测试

覆盖用户使用场景：
1. 找不到参数格式 → todowrite自动检查
2. 记不住历史TODO → TODO上下文携带
3. 重复创建TODO → 冲突检测
4. 找不到相关Skill → Skill关键词检索
5. Skill太长看不懂 → Skill切片
6. 忘记检查Skill → Skill强制查找
"""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


class TestUserScenario_找不到参数格式:
    """用户场景：Agent不知道todowrite需要什么参数"""

    def test_scenario_1_忘记带content参数(self):
        """
        场景：Agent执行todowrite忘记带--content
        预期：系统提示--content是必填参数
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite", "--agent", "1"],
            capture_output=True,
            text=True
        )
        # 应该提示缺少--content
        assert "content" in result.stdout.lower() or "content" in result.stderr.lower()

    def test_scenario_2_忘记带agent参数(self):
        """
        场景：Agent执行todowrite忘记带--agent
        预期：系统提示--agent是必填参数
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite", "--content", "完成设计"],
            capture_output=True,
            text=True
        )
        # 应该提示缺少--agent
        assert "agent" in result.stdout.lower() or "agent" in result.stderr.lower()

    def test_scenario_3_给了无效agent_id(self):
        """
        场景：Agent给了个不存在的agent_id（如3）
        预期：系统提示agent_id无效
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", "完成设计", "--agent", "3"],
            capture_output=True,
            text=True
        )
        # 应该提示无效的agent_id
        assert result.returncode != 0
        assert "invalid" in result.stderr.lower() or "3" in result.stderr

    def test_scenario_4_完全无参数执行(self):
        """
        场景：Agent直接执行todowrite，什么都不带
        预期：系统提示需要哪些参数
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite"],
            capture_output=True,
            text=True
        )
        # 应该给出使用提示
        assert "usage" in result.stdout.lower() or "content" in result.stdout.lower()


class TestUserScenario_记不住历史TODO:
    """用户场景：Agent创建TODO时忘记之前的任务"""

    def test_scenario_5_创建时显示历史摘要(self):
        """
        场景：Agent创建新TODO时，系统自动显示历史TODO摘要
        预期：输出包含历史TODO信息
        """
        import uuid
        test_content = f"场景5测试_{uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # 应该显示历史TODO信息
        assert "历史" in result.stdout or "TODO" in result.stdout

    def test_scenario_6_自动关联版本信息(self):
        """
        场景：创建TODO时自动记录当前版本
        预期：TODO元数据包含版本信息
        """
        import uuid
        test_content = f"场景6测试_{uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # 应该显示版本信息
        assert "2.2.6" in result.stdout or "version" in result.stdout.lower()


class TestUserScenario_重复创建TODO:
    """用户场景：Agent不小心重复创建了任务"""

    def test_scenario_7_检测到重复(self):
        """
        场景：Agent尝试创建与现有TODO内容相同的任务
        预期：系统检测到重复并提示
        """
        import uuid
        test_content = f"场景7重复测试_{uuid.uuid4().hex[:8]}"

        # 先创建一个TODO
        subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )

        # 再次创建相同内容
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1"],
            capture_output=True,
            text=True
        )

        # 应该检测到重复
        assert "重复" in result.stdout or "duplicate" in result.stdout.lower()

    def test_scenario_8_检测到优先级冲突(self):
        """
        场景：Agent创建了大量相同优先级的任务
        预期：系统检测到优先级冲突并提示
        """
        import uuid
        for i in range(6):
            content = f"场景8优先级测试_{uuid.uuid4().hex[:8]}"
            subprocess.run(
                [sys.executable, "-m", "src.cli.main", "todowrite",
                 "--content", content, "--agent", "1", "--priority", "high"],
                capture_output=True,
                text=True
            )

        # 第6个应该提示优先级冲突
        test_content = f"场景8第6个_{uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "todowrite",
             "--content", test_content, "--agent", "1", "--priority", "high"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "冲突" in result.stdout or "priority" in result.stdout.lower()


class TestUserScenario_找不到相关Skill:
    """用户场景：Agent不知道去哪里找相关操作指南"""

    def test_scenario_9_搜索关键词(self):
        """
        场景：Agent想找"todowrite"相关的Skill
        预期：系统返回包含todowrite的Skill列表
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "search",
             "--keywords", "todowrite"],
            capture_output=True,
            text=True
        )
        # skill命令应该存在并返回结果
        assert result.returncode == 0
        assert "skill" in result.stdout.lower() or "todowrite" in result.stdout.lower()

    def test_scenario_10_搜索不存在的关键词(self):
        """
        场景：Agent搜索一个不存在的关键词
        预期：系统返回"未找到"提示
        """
        import uuid
        keyword = f"不存在的词_{uuid.uuid4().hex[:8]}"
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "search",
             "--keywords", keyword],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "未找到" in result.stdout or "not found" in result.stdout.lower()


class TestUserScenario_Skill太长看不懂:
    """用户场景：Agent看到一大坨文字不知道重点"""

    def test_scenario_11_列出Skill章节(self):
        """
        场景：Agent想看某个Skill有哪些章节
        预期：系统返回指定Skill的章节列表
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "slice", "oc_collab_requirements_guide"],
            capture_output=True,
            text=True
        )
        # skill slice命令应该存在
        assert result.returncode == 0
        assert "章节" in result.stdout or "chapter" in result.stdout.lower()

    def test_scenario_12_只看某个章节(self):
        """
        场景：Agent只想看某个特定章节
        预期：系统返回指定章节内容
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "slice", "oc_collab_requirements_guide", "--level", "1"],
            capture_output=True,
            text=True
        )
        # 应该能获取章节内容
        assert result.returncode == 0


class TestUserScenario_忘记检查Skill:
    """用户场景：Agent行动前忘记先看Skill"""

    def test_scenario_13_执行前自动检查(self):
        """
        场景：Agent执行命令前，系统自动检查需要的Skill
        预期：显示当前已加载/缺失的Skill
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "enforce"],
            capture_output=True,
            text=True
        )
        # skill enforce命令应该存在
        assert result.returncode == 0
        assert "skill" in result.stdout.lower()

    def test_scenario_14_显示缺失的Skill(self):
        """
        场景：系统检查并显示缺失的Skill
        预期：列出需要但缺失的Skill
        """
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "skill", "enforce"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        # 应该显示Skill状态
        assert "缺失" in result.stdout or "missing" in result.stdout.lower() or \
               "已加载" in result.stdout or "loaded" in result.stdout.lower()
