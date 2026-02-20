import os
import pytest

os.environ["OC_SKIP_SKILL_CHECK"] = "1"


@pytest.fixture(autouse=True)
def clean_test_environment():
    """每个测试后清理测试环境"""
    yield
    
    db_path = "state/todos.db"
    if os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM todos")
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    identity_file = "state/agent.identity"
    if os.path.exists(identity_file):
        try:
            os.remove(identity_file)
        except Exception:
            pass
    
    project_state = "state/project_state.yaml"
    if os.path.exists(project_state):
        try:
            import yaml
            with open(project_state, 'r') as f:
                state = yaml.safe_load(f) or {}
            if 'current_agent' in state:
                del state['current_agent']
            with open(project_state, 'w') as f:
                yaml.safe_dump(state, f)
        except Exception:
            pass
