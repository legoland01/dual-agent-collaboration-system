import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.bug_test_linker import BugTestLinker, BugLinkError


class TestBugTestLinker:
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
    def bug_linker(self, temp_dir):
        links_path = Path(temp_dir) / "bug_test_links.yaml"
        return BugTestLinker(str(links_path))
    
    def test_link_bug_to_test(self, bug_linker, test_file):
        result = bug_linker.link("BUG-20260215-001", test_file)
        assert result is True
        tests = bug_linker.get_tests_for_bug("BUG-20260215-001")
        assert test_file in tests
    
    def test_link_nonexistent_test_file(self, bug_linker):
        with pytest.raises(BugLinkError):
            bug_linker.link("BUG-20260215-001", "/nonexistent/test.py")
    
    def test_unlink_test(self, bug_linker, test_file):
        bug_linker.link("BUG-20260215-001", test_file)
        result = bug_linker.unlink("BUG-20260215-001", test_file)
        assert result is True
        tests = bug_linker.get_tests_for_bug("BUG-20260215-001")
        assert test_file not in tests
    
    def test_get_bugs_without_tests(self, bug_linker, test_file):
        from src.core.bug_test_linker import BugTestLinker
        linker2 = BugTestLinker(str(bug_linker.links_path))
        linker2.links.setdefault("links", []).append({
            "bug_id": "BUG-20260215-001",
            "test_files": [],
            "created_at": "2026-02-15"
        })
        linker2._save_links()
        unlinked = linker2.get_bugs_without_tests()
        assert "BUG-20260215-001" in unlinked
    
    def test_get_all_links(self, bug_linker, test_file):
        bug_linker.link("BUG-20260215-001", test_file)
        links = bug_linker.get_all_links()
        assert len(links) == 1
        assert links[0]["bug_id"] == "BUG-20260215-001"
    
    def test_create_template(self, bug_linker):
        template = bug_linker._create_test_template("BUG-20260215-001")
        assert "BUG-20260215-001" in template
        assert "test_" in template
    
    def test_auto_record(self, bug_linker, test_file):
        result = bug_linker.link("BUG-20260215-auto", test_file)
        assert result is True
        tests = bug_linker.get_tests_for_bug("BUG-20260215-auto")
        assert test_file in tests
    
    def test_p0_bug_coverage(self, bug_linker, test_file):
        bug_linker.link("BUG-20260215-001", test_file)
        unlinked = bug_linker.get_bugs_without_tests()
        all_links = bug_linker.get_all_links()
        if all_links:
            for link in all_links:
                if "P0" in link.get("bug_id", ""):
                    assert link.get("test_files"), "P0 BUG must have test files"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
