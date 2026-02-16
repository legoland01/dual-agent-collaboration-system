import pytest
import tempfile
import shutil
from pathlib import Path
import yaml
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.skill_index import SkillIndex, SkillIndexError


class TestSkillIndex:
    @pytest.fixture
    def temp_dir(self):
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp, ignore_errors=True)
    
    @pytest.fixture
    def skill_index(self, temp_dir):
        index_path = Path(temp_dir) / "skill_index.yaml"
        return SkillIndex(str(index_path))
    
    def test_load_empty_index(self, skill_index):
        assert skill_index.index is not None
        assert "version" in skill_index.index
    
    def test_add_entry(self, skill_index):
        result = skill_index.add_entry(["version", "release"], "oc_collab_version_management_guide", "版本管理")
        assert result is True
        assert len(skill_index.index.get("index", [])) == 1
    
    def test_add_duplicate_entry(self, skill_index):
        skill_index.add_entry(["version"], "oc_collab_version_guide", "版本")
        result = skill_index.add_entry(["version"], "oc_collab_version_guide", "版本")
        assert result is False
    
    def test_update_keywords(self, skill_index):
        skill_index.add_entry(["version"], "oc_collab_version_guide", "版本")
        result = skill_index.update_keywords("oc_collab_version_guide", ["version", "release", "publish"])
        assert result is True
        info = skill_index.get_skill_info("oc_collab_version_guide")
        assert "release" in info["keywords"]
    
    def test_get_all_skills(self, skill_index):
        skill_index.add_entry(["version"], "skill1", "desc1")
        skill_index.add_entry(["bug"], "skill2", "desc2")
        skills = skill_index.get_all_skills()
        assert "skill1" in skills
        assert "skill2" in skills
    
    def test_get_skill_info(self, skill_index):
        skill_index.add_entry(["version", "release"], "oc_collab_version_guide", "版本管理")
        info = skill_index.get_skill_info("oc_collab_version_guide")
        assert info is not None
        assert info["skill"] == "oc_collab_version_guide"
        assert "version" in info["keywords"]
    
    def test_remove_entry(self, skill_index):
        skill_index.add_entry(["version"], "skill1", "desc")
        result = skill_index.remove_entry("skill1")
        assert result is True
        assert skill_index.get_skill_info("skill1") is None
    
    def test_load_performance(self, skill_index):
        import time
        skill_index.add_entry(["version"], "skill1", "desc")
        skill_index.add_entry(["bug"], "skill2", "desc")
        
        start = time.time()
        for _ in range(100):
            index = SkillIndex(str(skill_index.index_path))
        elapsed = (time.time() - start) / 100 * 1000
        assert elapsed < 100, f"Load time {elapsed:.2f}ms exceeds 100ms"
    
    def test_sync_from_skills_dir(self, skill_index):
        from src.core.index_auto_updater import IndexAutoUpdater
        updater = IndexAutoUpdater(skill_index, "skills")
        count = updater.sync_all()
        assert count >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
