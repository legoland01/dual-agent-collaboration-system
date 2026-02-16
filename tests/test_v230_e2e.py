"""
v2.3.0 E2E测试 - CLI命令

测试所有CLI命令实际运行
"""
import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path


class TestCLIE2E:
    """CLI命令E2E测试"""
    
    def test_requirements_coverage_command(self):
        """测试 requirements coverage 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "requirements", "coverage"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
        assert "需求覆盖率报告" in result.stdout
        assert "覆盖率:" in result.stdout
    
    def test_requirements_coverage_json(self):
        """测试 requirements coverage --json 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "requirements", "coverage", "--json"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
        assert "total" in result.stdout
    
    def test_bug_list_command(self):
        """测试 bug list 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "bug", "list"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
    
    def test_bug_list_unlinked(self):
        """测试 bug list --unlinked 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "bug", "list", "--unlinked"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
    
    def test_bug_link_command(self):
        """测试 bug link 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "bug", "link", "BUG-TEST-001", "tests/test_v230_skill_index.py"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
        assert "已关联" in result.stdout
    
    def test_bug_suggest_command(self):
        """测试 bug suggest 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "bug", "suggest", "-d", "todo同步失败"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
    
    def test_skill_search_command(self):
        """测试 skill search 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "skill", "query", "版本"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
    
    def test_skill_index_command(self):
        """测试 skill index 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "skill", "index"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
    
    def test_skill_index_sync_command(self):
        """测试 skill index --sync 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "skill", "index", "--sync"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0
    
    def test_requirements_list_command(self):
        """测试 requirements list 命令"""
        result = subprocess.run(
            ["python3", "-m", "src.cli.main", "requirements", "list"],
            capture_output=True,
            text=True,
            cwd="/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/dual-agent-collaboration-system"
        )
        assert result.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
