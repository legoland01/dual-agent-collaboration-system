import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.test_suggestion_engine import TestSuggestionEngine


class TestTestSuggestionEngine:
    @pytest.fixture
    def engine(self):
        return TestSuggestionEngine()
    
    def test_suggest_tests_by_keyword_todo(self, engine):
        suggestions = engine.suggest_tests("test todo functionality")
        assert len(suggestions) > 0
        assert any("todo" in s.lower() for s in suggestions)
    
    def test_suggest_tests_by_keyword_skill(self, engine):
        suggestions = engine.suggest_tests("skill enforce检查失败")
        assert len(suggestions) > 0
        assert any("skill" in s.lower() for s in suggestions)
    
    def test_suggest_tests_by_bug_id(self, engine):
        suggestions = engine.suggest_tests("", "BUG-20260215-todo-001")
        assert len(suggestions) > 0
    
    def test_suggest_tests_empty_description(self, engine):
        suggestions = engine.suggest_tests("")
        assert suggestions == []
    
    def test_extract_keywords(self, engine):
        keywords = engine._extract_keywords("Hello World Test")
        assert "hello" in keywords
        assert "world" in keywords
    
    def test_extract_bug_type(self, engine):
        bug_type = engine._extract_bug_type("BUG-20260215-todo-001")
        assert bug_type == "todo"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
