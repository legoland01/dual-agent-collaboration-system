import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.skill_index import SkillIndex
from src.core.skill_search_engine import SkillSearchEngine, SearchResult


class TestSkillSearchEngine:
    @pytest.fixture
    def temp_dir(self):
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp, ignore_errors=True)
    
    @pytest.fixture
    def skill_index(self, temp_dir):
        index_path = Path(temp_dir) / "skill_index.yaml"
        index = SkillIndex(str(index_path))
        index.add_entry(["版本", "发布", "version", "release"], "oc_collab_version_management_guide", "版本管理")
        index.add_entry(["Bug", "bug", "缺陷"], "oc_collab_bug_management_guide", "Bug管理")
        index.add_entry(["需求", "requirements"], "oc_collab_requirements_guide", "需求管理")
        return index
    
    @pytest.fixture
    def search_engine(self, skill_index):
        return SkillSearchEngine(skill_index)
    
    def test_search_exact_match(self, search_engine):
        results = search_engine.search("版本")
        assert len(results) > 0
        assert any(r.skill == "oc_collab_version_management_guide" for r in results)
    
    def test_search_partial_match(self, search_engine):
        results = search_engine.search("release")
        assert len(results) > 0
    
    def test_search_empty_query(self, search_engine):
        results = search_engine.search("")
        assert results == []
    
    def test_search_no_match(self, search_engine):
        results = search_engine.search("完全不存在的关键词xyz123")
        assert results == []
    
    def test_search_top_k(self, search_engine):
        results = search_engine.search("版本", top_k=1)
        assert len(results) <= 1
    
    def test_search_confidence_order(self, search_engine):
        results = search_engine.search("版本 Bug", top_k=3)
        if len(results) > 1:
            assert results[0].confidence >= results[1].confidence
    
    def test_tokenize(self, search_engine):
        tokens = search_engine._tokenize("Hello World Test")
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
    
    def test_calculate_confidence(self, search_engine):
        conf1 = search_engine._calculate_confidence(["version"], ["version", "release"])
        conf2 = search_engine._calculate_confidence(["xyz"], ["version", "release"])
        assert conf1 > conf2
    
    def test_hit_rate(self, search_engine):
        test_queries = ["版本", "bug", "需求", "部署", "测试"]
        hits = 0
        for q in test_queries:
            results = search_engine.search(q)
            if results:
                hits += 1
        rate = hits / len(test_queries) * 100
        # Accept >= 50% as passing given limited test data
        assert rate >= 50, f"Hit rate {rate}% below 50%"
    
    def test_search_verbose(self, search_engine):
        results = search_engine.search("version", top_k=3)
        for r in results:
            assert hasattr(r, 'keywords')
            assert hasattr(r, 'description')
            assert hasattr(r, 'confidence')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
