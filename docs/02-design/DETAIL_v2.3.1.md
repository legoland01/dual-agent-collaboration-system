# 详细设计说明书：oc-collab v2.3.1

**版本**: v1
**创建日期**: 2026-02-17
**作者**: Agent 2 (开发负责人)
**关联概要设计**: OUTLINE_v2.3.1.md
**版本号**: 2.3.1
**状态**: DRAFT → READY

---

## 1. 功能模块映射

### 1.1 映射表

| 功能模块 (概要设计) | 技术模块 (详细设计) | 对应文件 |
|---------------------|---------------------|----------|
| TodoIdGenerator | 编号生成器 | src/core/todo_id_generator.py |
| SourceTag | 来源标签 | src/core/source_tag.py |
| Template | 模板系统 | src/core/todo_template.py |
| AgentRegistry | Agent注册表 | src/core/agent_registry.py |
| GitSync | Git同步 | src/core/git_sync.py |
| ACKConfirm | ACK确认 | src/core/ack_confirm.py |
| ComplianceChecker | 合规检查 | src/core/compliance_checker.py |

### 1.2 新增/变更文件

| 文件路径 | 功能 | 工时 |
|----------|------|------|
| src/core/todo_id_generator.py | TODO编号生成 | 4h |
| src/core/source_tag.py | 来源标签管理 | 2h |
| src/core/todo_template.py | 模板系统 | 3h |
| src/core/agent_registry.py | Agent注册表 | 3h |
| src/core/git_sync.py | Git同步 | 4h |
| src/core/ack_confirm.py | ACK确认 | 3h |
| src/core/compliance_checker.py | 合规检查 | 1h |
| src/cli/commands.py | 新增CLI命令 | 4h |
| src/cli/agent_commands.py | Agent管理命令(含listen) | 2h |
| config/git_sync.yaml | 配置文件 | 0.5h |
| config/templates.yaml | 配置文件 | 0.5h |

---

## 1.3 Agent间通信机制

### 1.3.1 设计目标

实现Agent1和Agent2之间的TODO实时通知机制，确保：
- Agent2创建TODO给Agent1后，Agent1能自动感知
- Agent1创建TODO给Agent2后，Agent2能自动感知
- 每个Agent终端有独立的监听进程

### 1.3.2 通信流程

```
Agent2终端                          Agent1终端
    |                                   |
    |-- todowrite --to 1 -------------> |
    |   (创建TODO)                      |
    |                                   |
    |   写入state/agent_adhoc_todos.yaml |
    |                                   |
    |   <-- 轮询检测 (agent listen) --- |
    |   (发现新TODO)                     |
    |                                   |
    |   显示通知: 新TODO: [TODO-2to1-xxx]|
```

### 1.3.3 伴随监听进程

**重要**: 每个Agent终端需要启动一个伴随的监听进程：

```bash
# Agent1终端
nohup oc-collab agent listen --interval 3 > logs/agent1_listen.log &

# Agent2终端
nohup oc-collab agent listen --interval 3 > logs/agent2_listen.log &
```

**进程特性**:
- 独立进程：每个Agent终端一个
- 后台运行：不占用终端
- 轮询检测：默认3秒间隔检查TODO队列
- 日志输出：写入独立日志文件

### 1.3.4 相关命令

| 命令 | 功能 |
|------|------|
| `oc-collab agent listen` | 启动后台监听 |
| `oc-collab agent listen --interval 5` | 自定义轮询间隔 |
| `oc-collab agent listen --daemon` | 后台模式启动 |

### 1.3.5 技术实现

- **核心组件**: `TodoQueueManager` - 管理TODO队列读写
- **监听机制**: 轮询式检测新TODO（避免文件锁冲突）
- **通知展示**: 发现新TODO时输出到日志/终端

---

## 2. 技术架构

### 2.1 模块架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI 命令层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ todowrite│  │ todo list│  │ todo show│  │ agent    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
┌───────┼─────────────┼─────────────┼─────────────┼──────────┐
│       ▼             ▼             ▼             ▼           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              ComplianceChecker (合规检查)              │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │TodoIdGen   │ │SourceTag   │ │Template    │              │
│  └────────────┘ └────────────┘ └────────────┘              │
│                           │                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              状态管理层                                │    │
│  │  ┌────────────────────────────────────────────┐      │    │
│  │  │         project_state.yaml                  │      │    │
│  │  │  - todo_id_counters: {...}               │      │    │
│  │  │  - agents: {...}                          │      │    │
│  │  └────────────────────────────────────────────┘      │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │GitSync     │ │AgentRegistry│ │ACKConfirm  │              │
│  └────────────┘ └────────────┘ └────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 模块 | 技术/库 | 版本 | 选型依据 |
|------|---------|------|----------|
| CLI框架 | Click | >=8.0 | 现有技术栈 |
| 配置解析 | PyYAML | >=6.0 | 现有依赖 |
| Git操作 | GitPython | >=3.1 | 现有依赖 |
| 文件监控 | watchdog | >=3.0 | 新增依赖，用于自动Git同步 |

---

## 3. 核心模块设计

### 3.1 TodoIdGenerator

```python
import os
import yaml
import fcntl
from typing import Dict, Tuple, Optional
from pathlib import Path


class TodoIdGenerator:
    """TODO编号生成器，支持多Agent编号格式"""
    
    DEFAULT_COUNTERS = {
        "1to1": 0,
        "1to2": 0,
        "2to1": 0,
        "2to2": 0,
    }
    
    def __init__(self, state_file: str = "state/project_state.yaml"):
        self.state_file = state_file
        self.lock_file = "state/.todo_id.lock"
        self._ensure_state_file()
    
    def _ensure_state_file(self):
        """确保状态文件存在并包含计数器"""
        state = self._load_state()
        if "todo_id_counters" not in state:
            state["todo_id_counters"] = self.DEFAULT_COUNTERS.copy()
            self._save_state(state)
    
    def _load_state(self) -> Dict:
        """加载状态"""
        if not os.path.exists(self.state_file):
            return {"todo_id_counters": self.DEFAULT_COUNTERS.copy()}
        with open(self.state_file, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def _save_state(self, state: Dict):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            yaml.safe_dump(state, f)
    
    def generate(self, creator: str, receiver: str) -> str:
        """
        生成TODO编号
        
        Args:
            creator: 创建者Agent ID (如 "1", "2")
            receiver: 接收者Agent ID (如 "1", "2")
        
        Returns:
            TODO编号 (如 "TODO-1to2-001")
        """
        key = f"{creator}to{receiver}"
        
        with open(self.lock_file, 'a') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                state = self._load_state()
                counters = state.get("todo_id_counters", self.DEFAULT_COUNTERS)
                
                if key not in counters:
                    counters[key] = 0
                
                counters[key] += 1
                seq = counters[key]
                
                state["todo_id_counters"] = counters
                self._save_state(state)
                
                return f"TODO-{creator}to{receiver}-{seq:03d}"
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    
    def parse(self, todo_id: str) -> Optional[Dict]:
        """
        解析TODO编号
        
        Args:
            todo_id: TODO编号
        
        Returns:
            dict{creator, receiver, seq, is_legacy} 或 None
        """
        import re
        
        # 新格式: TODO-1to2-001
        match = re.match(r'TODO-(\d+)to(\d+)-(\d+)', todo_id)
        if match:
            return {
                "creator": match.group(1),
                "receiver": match.group(2),
                "seq": int(match.group(3)),
                "is_legacy": False
            }
        
        # 旧格式: TODO-1-001
        match = re.match(r'TODO-(\d+)-(\d+)', todo_id)
        if match:
            return {
                "creator": match.group(1),
                "receiver": match.group(1),  # 旧格式视为给自己
                "seq": int(match.group(2)),
                "is_legacy": True
            }
        
        return None
    
    def is_legacy_format(self, todo_id: str) -> bool:
        """判断是否旧格式"""
        parsed = self.parse(todo_id)
        return parsed.get("is_legacy", False) if parsed else False
```

### 3.2 SourceTag

```python
import re
from typing import Optional


class SourceTag:
    """TODO来源标签管理"""
    
    VALID_SOURCES = ["REQUIREMENT", "BUG", "FEEDBACK", "MANUAL"]
    
    # 自动推断关键词
    KEYWORDS = {
        "BUG": ["bug", "修复", "错误", "defect"],
        "REQUIREMENT": ["需求", "实现", "功能", "requirement", "feature"],
        "FEEDBACK": ["反馈", "意见", "feedback", "suggestion"]
    }
    
    def validate(self, source: str) -> bool:
        """验证来源是否有效"""
        return source.upper() in self.VALID_SOURCES
    
    def get_source_from_context(self, content: str) -> str:
        """
        从内容自动推断来源
        
        Args:
            content: TODO内容
        
        Returns:
            来源类型
        """
        content_lower = content.lower()
        
        for source, keywords in self.KEYWORDS.items():
            if any(kw in content_lower for kw in keywords):
                return source
        
        return "MANUAL"
    
    def normalize(self, source: str) -> str:
        """标准化来源名称"""
        return source.upper() if self.validate(source) else "MANUAL"
```

### 3.3 TodoTemplate

```python
import os
import yaml
from typing import Dict, Optional, List


DEFAULT_TEMPLATES = {
    "REQUIREMENT": {
        "content_prefix": "实现",
        "required_fields": ["requirement_id"],
        "optional_fields": ["acceptance_criteria"]
    },
    "BUG_FIX": {
        "content_prefix": "修复",
        "required_fields": ["bug_id", "root_cause"],
        "optional_fields": ["fix_plan", "test_case"]
    },
    "MANUAL": {
        "content_prefix": "",
        "required_fields": [],
        "optional_fields": []
    }
}


class TodoTemplate:
    """TODO模板管理"""
    
    def __init__(self, config_file: str = "config/templates.yaml"):
        self.config_file = config_file
        self.templates = DEFAULT_TEMPLATES.copy()
        self._load_templates()
    
    def _load_templates(self):
        """从配置文件加载模板"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                user_templates = yaml.safe_load(f)
                if user_templates and "templates" in user_templates:
                    self.templates.update(user_templates["templates"])
    
    def get_template(self, template_type: str) -> Optional[Dict]:
        """获取模板"""
        return self.templates.get(template_type.upper())
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        return list(self.templates.keys())
    
    def apply(self, template_type: str, context: Dict) -> Dict:
        """
        应用模板
        
        Args:
            template_type: 模板类型
            context: 上下文数据
        
        Returns:
            填充后的字段
        """
        template = self.get_template(template_type)
        if not template:
            return context
        
        result = context.copy()
        
        # 添加前缀
        if template.get("content_prefix"):
            if "content" in result:
                result["content"] = f"{template['content_prefix']}: {result['content']}"
        
        return result
```

### 3.4 AgentRegistry

```python
import os
import yaml
from typing import Dict, List, Optional
from datetime import datetime


class AgentRegistry:
    """Agent注册表管理"""
    
    VALID_ROLES = [
        "PRODUCT_MANAGER",
        "DEVELOPMENT_LEAD",
        "FRONTEND_DEV",
        "BACKEND_DEV",
        "QA_ENGINEER"
    ]
    
    def __init__(self, state_file: str = "state/project_state.yaml"):
        self.state_file = state_file
        self._ensure_state_file()
    
    def _ensure_state_file(self):
        """确保状态文件存在"""
        if not os.path.exists(self.state_file):
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            self._save_state({"agents": {}})
    
    def _load_state(self) -> Dict:
        """加载状态"""
        with open(self.state_file, 'r') as f:
            return yaml.safe_load(f) or {"agents": {}}
    
    def _save_state(self, state: Dict):
        """保存状态"""
        with open(self.state_file, 'w') as f:
            yaml.safe_dump(state, f)
    
    def get_current_agent_id(self) -> Optional[str]:
        """
        获取当前Agent ID
        
        优先级: CLI参数 > 环境变量 > Git config
        """
        # 1. 环境变量
        agent_id = os.environ.get("OC_AGENT_ID")
        if agent_id:
            return agent_id
        
        # 2. Git config
        import subprocess
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout:
                email = result.stdout.strip()
                # 从email提取agent_id，如 "agent1@opencode.ai" -> "agent1"
                return email.split("@")[0]
        except Exception:
            pass
        
        return None
    
    def register(self, agent_id: str, role: str, team: str = "internal") -> bool:
        """
        注册Agent
        
        Args:
            agent_id: Agent ID
            role: 角色
            team: 团队
        
        Returns:
            是否成功
        """
        if role not in self.VALID_ROLES:
            return False
        
        state = self._load_state()
        
        if "agents" not in state:
            state["agents"] = {}
        
        state["agents"][agent_id] = {
            "id": agent_id,
            "role": role,
            "team": team,
            "status": "active",
            "registered_at": datetime.now().isoformat()
        }
        
        self._save_state(state)
        return True
    
    def auto_register(self) -> bool:
        """自动注册"""
        agent_id = self.get_current_agent_id()
        if not agent_id:
            return False
        
        # 默认角色
        role = "DEVELOPMENT_LEAD"
        
        return self.register(agent_id, role)
    
    def list_agents(self) -> List[Dict]:
        """列出所有Agent"""
        state = self._load_state()
        return list(state.get("agents", {}).values())
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """获取Agent信息"""
        state = self._load_state()
        return state.get("agents", {}).get(agent_id)
    
    def can_unregister(self, agent_id: str) -> bool:
        """
        检查是否可以注销
        
        Args:
            agent_id: Agent ID
        
        Returns:
            是否可以注销（有pending TODO时返回False）
        """
        state = self._load_state()
        todos = state.get("todos", [])
        
        # 检查是否有分配给该Agent的pending TODO
        for todo in todos:
            if todo.get("receiver") == agent_id and todo.get("status") == "pending":
                return False
        
        return True
    
    def unregister(self, agent_id: str) -> bool:
        """
        注销Agent
        
        Args:
            agent_id: Agent ID
        
        Returns:
            是否成功
        """
        if not self.can_unregister(agent_id):
            return False
        
        state = self._load_state()
        if agent_id in state.get("agents", {}):
            del state["agents"][agent_id]
            self._save_state(state)
            return True
        return False
```

### 3.5 GitSync

```python
import os
import yaml
import subprocess
from typing import List, Optional
from datetime import datetime


class GitSync:
    """Git同步管理"""
    
    def __init__(self, config_file: str = "config/git_sync.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        
        return {
            "enabled": False,
            "remotes": ["origin"],
            "retry": {
                "max_attempts": 3,
                "delay_seconds": 1
            }
        }
    
    def sync(self, message: str, files: Optional[List[str]] = None) -> bool:
        """
        执行同步
        
        Args:
            message: 提交信息
            files: 要同步的文件列表
        
        Returns:
            是否成功
        """
        if not self.config.get("enabled", False):
            return True
        
        if not files:
            files = ["state/"]
        
        try:
            # git add
            for f in files:
                subprocess.run(["git", "add", f], check=True)
            
            # git commit
            subprocess.run(["git", "commit", "-m", message], check=True)
            
            # git push
            remotes = self.config.get("remotes", ["origin"])
            for remote in remotes:
                self._push_with_retry(remote)
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _push_with_retry(self, remote: str) -> bool:
        """带重试的push"""
        max_attempts = self.config.get("retry", {}).get("max_attempts", 3)
        
        for attempt in range(max_attempts):
            try:
                subprocess.run(
                    ["git", "push", remote],
                    check=True,
                    capture_output=True
                )
                return True
            except subprocess.CalledProcessError:
                if attempt < max_attempts - 1:
                    import time
                    delay = self.config.get("retry", {}).get("delay_seconds", 1)
                    time.sleep(delay * (attempt + 1))  # 指数退避
        
        return False
```

### 3.6 ACKConfirm

```python
import subprocess
from typing import Optional
from datetime import datetime


class ACKConfirm:
    """TODO ACK确认管理"""
    
    def __init__(self, state_file: str = "state/project_state.yaml"):
        self.state_file = state_file
    
    def acknowledge(self, todo_id: str, agent_id: str) -> bool:
        """
        确认TODO
        
        Args:
            todo_id: TODO编号
            agent_id: 确认者ID
        
        Returns:
            是否成功
        """
        try:
            # 生成commit message
            commit_msg = f"[ACK] {todo_id} acknowledged by {agent_id}"
            
            # 执行commit
            subprocess.run(
                ["git", "commit", "--allow-empty", "-m", commit_msg],
                check=True,
                capture_output=True
            )
            
            # 更新project_state.yaml中的TODO状态
            state = self._load_state()
            todos = state.get("todos", [])
            
            for todo in todos:
                if todo.get("id") == todo_id:
                    todo["acknowledged"] = True
                    todo["acknowledged_by"] = agent_id
                    todo["acknowledged_at"] = datetime.now().isoformat()
                    todo["status"] = "acknowledged"
                    break
            
            state["todos"] = todos
            self._save_state(state)
            
            return True
        except (subprocess.CalledProcessError, IOError):
            return False
    
    def is_acknowledged(self, todo_id: str) -> bool:
        """
        检查是否已确认
        
        Args:
            todo_id: TODO编号
        
        Returns:
            是否已确认
        """
        state = self._load_state()
        todos = state.get("todos", [])
        
        for todo in todos:
            if todo.get("id") == todo_id:
                return todo.get("acknowledged", False)
        
        return False
    
    def get_ack_status(self, todo_id: str) -> dict:
        """
        获取确认状态
        
        Args:
            todo_id: TODO编号
        
        Returns:
            确认状态详情
        """
        state = self._load_state()
        todos = state.get("todos", [])
        
        for todo in todos:
            if todo.get("id") == todo_id:
                return {
                    "acknowledged": todo.get("acknowledged", False),
                    "acknowledged_by": todo.get("acknowledged_by"),
                    "acknowledged_at": todo.get("acknowledged_at"),
                    "status": todo.get("status", "pending")
                }
        
        return {
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None,
            "status": "not_found"
        }
```

### 3.7 ComplianceChecker

```python
import re
from typing import Tuple


class ComplianceChecker:
    """合规检查器"""
    
    def __init__(self, current_agent: str):
        self.current_agent = current_agent
    
    def check_todo_create(self, todo: dict) -> Tuple[bool, str]:
        """
        检查TODO创建是否符合规则
        
        Args:
            todo: TODO数据
        
        Returns:
            (是否通过, 错误信息)
        """
        todo_id = todo.get("id", "")
        
        # 1. 编号格式检查
        if not self._check_format(todo_id):
            return False, f"无效的TODO编号格式: {todo_id}"
        
        # 2. 创建者/接收者关系检查
        parsed = self._parse_id(todo_id)
        if parsed and not self._check_creator_receiver(parsed):
            creator = parsed.get("creator")
            receiver = parsed.get("receiver")
            if creator != self.current_agent:
                return False, f"Agent{self.current_agent}不能创建非自己的TODO: {todo_id}"
            
            if creator == "1" and receiver not in ["1", "2"]:
                return False, "Agent1只能创建给自己的TODO"
        
        return True, ""
    
    def _check_format(self, todo_id: str) -> bool:
        """检查编号格式"""
        # 新格式: TODO-1to2-001
        if re.match(r'TODO-\d+to\d+-\d+', todo_id):
            return True
        # 旧格式: TODO-1-001
        if re.match(r'TODO-\d+-\d+', todo_id):
            return True
        return False
    
    def _parse_id(self, todo_id: str) -> dict:
        """解析编号"""
        match = re.match(r'TODO-(\d+)to(\d+)-(\d+)', todo_id)
        if match:
            return {
                "creator": match.group(1),
                "receiver": match.group(2),
                "seq": int(match.group(3))
            }
        return None
    
    def _check_creator_receiver(self, parsed: dict) -> bool:
        """检查创建者/接收者关系"""
        creator = parsed.get("creator")
        receiver = parsed.get("receiver")
        
        # Agent1只能创建给自己或Agent2
        if creator == "1":
            return receiver in ["1", "2"]
        
        return True
```

---

## 4. 数据结构

### 4.1 状态文件Schema

```yaml
# state/project_state.yaml
todo_id_counters:
  "1to1": 5
  "1to2": 10
  "2to1": 8
  "2to2": 3

agents:
  agent1:
    id: agent1
    role: DEVELOPMENT_LEAD
    team: internal
    status: active
    registered_at: "2026-02-16T10:00:00"
  agent2:
    id: agent2
    role: PRODUCT_MANAGER
    team: internal
    status: active
    registered_at: "2026-02-16T10:00:00"

todos:
  - id: TODO-1to2-001
    content: "实现功能X"
    status: pending
    creator: agent1
    receiver: agent2
    source: REQUIREMENT
    acknowledged: false
    created_at: "2026-02-16T10:00:00"
```

### 4.2 配置Schema

```yaml
# config/git_sync.yaml
enabled: false
remotes:
  - origin
  - backup
retry:
  max_attempts: 3
  delay_seconds: 1
```

```yaml
# config/templates.yaml
templates:
  REQUIREMENT:
    content_prefix: "实现"
    required_fields:
      - requirement_id
    optional_fields:
      - acceptance_criteria
  BUG_FIX:
    content_prefix: "修复"
    required_fields:
      - bug_id
      - root_cause
    optional_fields:
      - fix_plan
      - test_case
```

---

## 5. 算法与逻辑

### 5.1 TODO创建流程

```
开始
  ↓
检查CLI参数 (--to, --source, --type)
  ↓
合规检查 (ComplianceChecker.check_todo_create)
  ↓ [失败] 返回错误信息
  ↓ [成功]
来源处理 (SourceTag)
  ↓
模板处理 (Template.apply)
  ↓
生成编号 (TodoIdGenerator.generate)
  ↓ [文件锁]
保存状态 (StateManager.save)
  ↓
Git同步 (GitSync.sync) [可选，不阻塞]
  ↓
返回TODO ID
结束
```

### 5.2 Agent注册流程

```
开始
  ↓
检查环境变量 OC_AGENT_ID
  ↓ [存在] 使用环境变量
  ↓ [不存在]
检查Git config user.email
  ↓ [存在] 提取agent_id
  ↓ [不存在] 返回错误
注册Agent (AgentRegistry.register)
  ↓
保存状态
  ↓
Git同步
  ↓
返回成功
结束
```

### 5.3 状态机

```
TODO状态:
  draft → pending → acknowledged → completed
                     ↓
                  cancelled

Agent状态:
  registered → active → inactive
```

### 5.4 边界条件

| 边界条件 | 处理方式 |
|----------|----------|
| 接收者不存在 | 警告但允许创建，降级为TODO-XtoX |
| 接收者未注册 | 降级处理，继续允许创建 |
| 重复注册 | 覆盖更新 |
| 已分配TODO的Agent注销 | 禁止注销 |
| Git同步失败 | 记录日志，不阻塞主流程 |

---

## 6. CLI命令设计

### 6.1 新增命令

| 命令 | 函数 | 描述 | 工时 |
|------|------|------|------|
| `oc-collab todowrite --to <id>` | todowrite() | 指定接收者 | 0.5h |
| `oc-collab todowrite --source <type>` | todowrite() | 指定来源 | 0.5h |
| `oc-collab todowrite --type <type>` | todowrite() | 选择模板 | 0.5h |
| `oc-collab todo show <id>` | todo_show() | 查看详情 | 1h |
| `oc-collab todo --source <type>` | todo_list() | 按来源筛选 | 0.5h |
| `oc-collab todo ack <id>` | todo_ack() | 手动ACK | 0.5h |
| `oc-collab agent register` | agent_register() | 注册Agent | 1h |
| `oc-collab agent list` | agent_list() | 列出Agent | 0.5h |
| `oc-collab agent auto-register` | agent_auto_register() | 自动注册 | 0.5h |
| `oc-collab sync` | sync() | 手动同步 | 0.5h |

### 6.2 错误码

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 1001 | 参数错误 | 提示用户正确的用法 |
| 1002 | 无效的TODO编号 | 提示正确的编号格式 |
| 1003 | 合规检查失败 | 显示违规原因 |
| 1004 | Agent未注册 | 提示先注册 |
| 1005 | 注销被拒绝 | 提示有pending TODO |
| 2001 | Git同步失败 | 记录日志，提示手动处理 |

---

## 7. 错误处理

### 7.1 异常类型

| 异常类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| ValidationError | 参数验证失败 | 返回错误信息，退出码1 |
| ComplianceViolationError | 合规检查失败 | 返回违规原因，退出码3 |
| AgentNotFoundError | Agent不存在 | 降级处理或报错 |
| GitSyncError | Git同步失败 | 记录日志，继续执行 |

---

## 8. 测试策略

### 8.1 单元测试

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| TodoIdGenerator.generate | 生成新编号 | 返回正确格式 |
| TodoIdGenerator.parse | 解析编号 | 返回正确dict |
| TodoIdGenerator.is_legacy_format | 判断旧格式 | 返回正确bool |
| SourceTag.validate | 验证来源 | 返回正确bool |
| SourceTag.get_source_from_context | 自动推断 | 返回正确来源 |
| TodoTemplate.get_template | 获取模板 | 返回正确模板 |
| AgentRegistry.register | 注册Agent | 成功保存 |
| AgentRegistry.list_agents | 列出Agent | 返回列表 |
| ComplianceChecker.check_todo_create | 合规检查 | 返回正确结果 |

### 8.2 E2E测试

| 测试场景 | 测试步骤 | 验收标准 |
|----------|----------|----------|
| 创建TODO | oc-collab todowrite --content "test" --to 2 | 生成正确编号 |
| 查看TODO | oc-collab todo show TODO-1to2-001 | 显示详情 |
| 列出TODO | oc-collab todo --source BUG | 正确筛选 |
| 注册Agent | oc-collab agent register --id agent3 --role FRONTEND_DEV | 成功注册 |
| 自动注册 | oc-collab agent auto-register | 成功注册 |

---

## 9. 签署确认

### Agent 2 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-17 | ✅ |

### Agent 1 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-17
**状态**: DRAFT / READY / APPROVED
