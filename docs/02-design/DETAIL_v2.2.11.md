# 详细设计说明书：oc-collab v2.2.11

**版本**: v1
**创建日期**: 2026-02-14
**作者**: Agent 2 (开发负责人)
**版本号**: v2.2.11
**状态**: DRAFT

---

## 1. 功能模块映射

### 1.1 概要设计 → 技术模块映射

| 功能模块 (概要设计) | 技术模块 (详细设计) | 关键文件 |
|--------------------|---------------------|----------|
| M1: TODO编号管理 | TodoIdGenerator, TodoMigrator | src/core/todo_id_generator.py, src/core/todo_migrator.py |
| M2: Skill强制执行 | SkillEnforcerEnhanced, SkillEmbedder | src/core/skill_enforcer.py, src/core/skill_embedder.py |
| M3: StateNotifier Receiver | StateReceiver, StateQueueManager | src/core/state_receiver.py, src/core/state_queue.py |

---

## 2. 技术架构

### 2.1 模块划分

```
src/
├── core/
│   ├── todo_id_generator.py      # TODO编号生成器
│   ├── todo_migrator.py          # TODO迁移工具
│   ├── skill_enforcer.py         # Skill强制执行器
│   ├── skill_embedder.py         # Skill嵌入器
│   ├── state_receiver.py         # HTTP接收器
│   ├── state_queue.py            # 状态队列管理
│   └── todo.py                   # TODO数据模型
├── cli/
│   ├── todo_commands.py          # TODO命令增强
│   ├── skill_commands.py         # Skill命令增强
│   └── init_commands.py          # init命令增强
```

### 2.2 技术选型

| 组件 | 技术选型 | 依据 |
|------|----------|------|
| HTTP服务 | Python Flask (轻量级) | 已有EventDispatcher使用Flask |
| 状态持久化 | JSON文件 | 兼容现有StateNotifier |
| 编号生成 | 递增计数器 + agent_id前缀 | 简单可靠 |

---

## 3. 核心模块设计

### 3.1 TodoIdGenerator (TODO编号生成器)

```python
# src/core/todo_id_generator.py

class TodoIdGenerator:
    """Agent独立TODO编号生成器"""

    def __init__(self, agent_id: str):
        """
        Args:
            agent_id: Agent标识 ("1" 或 "2")
        """
        self.agent_id = agent_id
        self.counter_file = Path(f"state/.todo_counter_{agent_id}.yaml")
        self._load_counter()

    def _load_counter(self):
        """加载计数器"""
        if self.counter_file.exists():
            with open(self.counter_file) as f:
                self.counter = yaml.safe_load(f).get("counter", 0)
        else:
            self.counter = 0

    def _save_counter(self):
        """保存计数器"""
        with open(self.counter_file, "w") as f:
            yaml.dump({"counter": self.counter}, f)

    def generate(self) -> str:
        """
        生成TODO编号

        Returns:
            TODO-1-001 或 TODO-2-001 格式
        """
        self.counter += 1
        self._save_counter()
        return f"TODO-{self.agent_id}-{self.counter:03d}"

    def get_next_number(self) -> int:
        """获取下一个编号"""
        return self.counter + 1
```

### 3.2 TodoMigrator (TODO迁移工具)

```python
# src/core/todo_migrator.py

class TodoMigrator:
    """TODO编号迁移工具"""

    def __init__(self, source_file: str, backup_file: str):
        """
        Args:
            source_file: 源YAML文件
            backup_file: 备份文件路径
        """
        self.source_file = Path(source_file)
        self.backup_file = Path(backup_file)

    def migrate(self, agent_mapping: dict[str, str]) -> MigrationResult:
        """
        执行迁移

        Args:
            agent_mapping: TODO ID到Agent ID的映射

        Returns:
            MigrationResult: 迁移结果
        """
        # 1. 备份
        self._backup()

        # 2. 读取现有TODO
        with open(self.source_file) as f:
            data = yaml.safe_load(f)

        migrated_count = 0
        conflicts = []

        for todo in data.get("todos", []):
            old_id = todo["id"]

            if old_id in agent_mapping:
                new_id = f"TODO-{agent_mapping[old_id]}-{old_id.split('-')[-1]}"
                todo["id"] = new_id
                migrated_count += 1

        # 3. 保存新格式
        with open(self.source_file, "w") as f:
            yaml.dump(data, f, allow_unicode=True)

        return MigrationResult(
            migrated=migrated_count,
            conflicts=conflicts,
            backup_file=self.backup_file
        )

    def _backup(self):
        """创建备份"""
        import shutil
        shutil.copy(self.source_file, self.backup_file)

    def rollback(self):
        """回滚"""
        import shutil
        shutil.copy(self.backup_file, self.source_file)


@dataclass
class MigrationResult:
    migrated: int
    conflicts: list[str]
    backup_file: str
```

### 3.3 SkillEnforcerEnhanced (Skill强制执行器)

```python
# src/core/skill_enforcer.py

class SkillEnforcerEnhanced:
    """增强版Skill强制执行器"""

    def __init__(self, skill_loader: SkillLoader):
        """
        Args:
            skill_loader: Skill加载器
        """
        self.skill_loader = skill_loader
        self.required_skills = self._load_required_skills()

    def _load_required_skills(self) -> dict[str, list[str]]:
        """加载必需Skill规则"""
        return {
            "todowrite": ["oc_collab_todo_execution"],
            "signoff": ["oc_collab_signoff_guide"],
            "commit": ["oc_collab_git_commit_guide"]
        }

    def check(self, command: str) -> SkillCheckResult:
        """
        检查命令是否遵循Skill规范

        Args:
            command: 命令类型 (todowrite/signoff/commit)

        Returns:
            SkillCheckResult: 检查结果

        Raises:
            SkillRequiredError: 必需的Skill未遵循
        """
        required = self.required_skills.get(command, [])

        if not required:
            return SkillCheckResult(passed=True, message="无需Skill检查")

        # 加载当前已加载的Skill
        loaded_skills = self.skill_loader.get_loaded_skills()

        # 检查是否有所需的Skill
        missing = []
        for skill in required:
            if skill not in loaded_skills:
                missing.append(skill)

        if missing:
            raise SkillRequiredError(
                f"执行{command}前必须先加载以下Skill: {', '.join(missing)}",
                missing_skills=missing,
                required_for=command
            )

        return SkillCheckResult(
            passed=True,
            checked_skills=required,
            loaded_skills=list(loaded_skills.keys())
        )


@dataclass
class SkillCheckResult:
    passed: bool
    message: str
    checked_skills: list[str] = field(default_factory=list)
    loaded_skills: list[str] = field(default_factory=list)


class SkillRequiredError(Exception):
    """必需的Skill未遵循异常"""

    def __init__(self, message: str, missing_skills: list[str], required_for: str):
        super().__init__(message)
        self.missing_skills = missing_skills
        self.required_for = required_for
```

### 3.4 SkillEmbedder (Skill嵌入器)

```python
# src/core/skill_embedder.py

class SkillEmbedder:
    """Skill嵌入器"""

    def __init__(self, skill_loader: SkillLoader):
        self.skill_loader = skill_loader

    def embed(self, content: str, skill_name: str, max_length: int = 500) -> str:
        """
        嵌入Skill规则到TODO内容

        Args:
            content: 原始内容
            skill_name: Skill名称
            max_length: 最大嵌入长度

        Returns:
            嵌入后的内容
        """
        skill = self.skill_loader.load_skill(skill_name)
        if not skill:
            raise SkillNotFoundError(f"Skill不存在: {skill_name}")

        # 提取关键规则
        key_rules = self._extract_key_rules(skill)

        # 截断如果过长
        if len(key_rules) > max_length:
            key_rules = key_rules[:max_length] + "..."

        # 嵌入格式
        embedded = f"{content}\n\n[Skill: {skill_name}]\n{key_rules}"

        return embedded

    def _extract_key_rules(self, skill: dict) -> str:
        """提取Skill关键规则"""
        # 从skill_content中提取关键规则
        content = skill.get("content", "")
        lines = content.split("\n")

        # 提取步骤、SOP等关键部分
        key_parts = []
        for line in lines:
            if line.strip().startswith(("1.", "2.", "3.", "- ")):
                key_parts.append(line.strip())

        return "\n".join(key_parts[:10])  # 最多10条


class SkillNotFoundError(Exception):
    """Skill未找到异常"""
    pass
```

### 3.5 StateReceiver (HTTP接收器)

```python
# src/core/state_receiver.py

from flask import Flask, request, jsonify

class StateReceiver:
    """StateNotifier HTTP接收器"""

    def __init__(self, queue_manager: "StateQueueManager", hmac_secret: str = None):
        """
        Args:
            queue_manager: 队列管理器
            hmac_secret: HMAC密钥
        """
        self.app = Flask(__name__)
        self.queue_manager = queue_manager
        self.hmac_secret = hmac_secret
        self._setup_routes()

    def _setup_routes(self):
        """设置路由"""

        @self.app.route("/webhook/state", methods=["POST"])
        def handle_state_webhook():
            """处理状态变更Webhook"""
            # 1. 验证HMAC签名
            signature = request.headers.get("X-HMAC-Signature")
            if self.hmac_secret and signature:
                if not self._verify_signature(request.data, signature):
                    return jsonify({"error": "Invalid signature"}), 401

            # 2. 解析请求体
            data = request.get_json()
            if not data:
                return jsonify({"error": "Empty body"}), 400

            # 3. 验证必需字段
            required_fields = ["event_type", "source_agent", "target_agent"]
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing field: {field}"}), 400

            # 4. 入队列
            notification = self.queue_manager.enqueue(data)

            return jsonify({
                "status": "accepted",
                "notification_id": notification.id
            }), 202

        @self.app.route("/webhook/state/health", methods=["GET"])
        def health_check():
            """健康检查"""
            return jsonify({"status": "healthy"}), 200

    def _verify_signature(self, data: bytes, signature: str) -> bool:
        """验证HMAC签名"""
        import hmac
        expected = hmac.new(
            self.hmac_secret.encode(),
            data,
            "sha256"
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """启动接收器"""
        self.app.run(host=host, port=port)
```

### 3.6 StateQueueManager (状态队列管理器)

```python
# src/core/state_queue.py

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import uuid


@dataclass
class Notification:
    """通知"""
    id: str
    event_type: str
    source_agent: str
    target_agent: str
    payload: dict
    timestamp: str
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3


class StateQueueManager:
    """状态队列管理器"""

    def __init__(self, queue_file: str = "state/state_queue.json"):
        """
        Args:
            queue_file: 队列文件路径
        """
        self.queue_file = Path(queue_file)
        self._ensure_queue_file()

    def _ensure_queue_file(self):
        """确保队列文件存在"""
        if not self.queue_file.parent.exists():
            self.queue_file.parent.mkdir(parents=True)

        if not self.queue_file.exists():
            self._save({"queue_id": str(uuid.uuid4()), "notifications": [], "last_updated": None})

    def _load(self) -> dict:
        """加载队列"""
        with open(self.queue_file) as f:
            return json.load(f)

    def _save(self, data: dict):
        """保存队列"""
        data["last_updated"] = datetime.utcnow().isoformat()
        with open(self.queue_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def enqueue(self, data: dict) -> Notification:
        """
        入队列

        Args:
            data: 通知数据

        Returns:
            Notification: 创建的通知
        """
        queue = self._load()

        notification = Notification(
            id=str(uuid.uuid4())[:8],
            event_type=data.get("event_type"),
            source_agent=data.get("source_agent"),
            target_agent=data.get("target_agent"),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            status="pending"
        )

        queue["notifications"].append(notification.__dict__)
        self._save(queue)

        return notification

    def get_unread(self, agent_id: str) -> list[Notification]:
        """
        获取未读通知

        Args:
            agent_id: Agent ID

        Returns:
            list[Notification]: 未读通知列表
        """
        queue = self._load()
        return [
            Notification(**n) for n in queue["notifications"]
            if n["target_agent"] == agent_id and n["status"] == "pending"
        ]

    def mark_read(self, notification_id: str) -> bool:
        """
        标记为已读

        Args:
            notification_id: 通知ID

        Returns:
            bool: 是否成功
        """
        queue = self._load()

        for n in queue["notifications"]:
            if n["id"] == notification_id:
                n["status"] = "read"
                self._save(queue)
                return True

        return False

    def get_stats(self, agent_id: str) -> dict:
        """
        获取统计信息

        Args:
            agent_id: Agent ID

        Returns:
            dict: 统计信息
        """
        queue = self._load()
        agent_notifications = [n for n in queue["notifications"] if n["target_agent"] == agent_id]

        return {
            "total": len(agent_notifications),
            "pending": len([n for n in agent_notifications if n["status"] == "pending"]),
            "read": len([n for n in agent_notifications if n["status"] == "read"])
        }
```

---

## 4. 数据结构

### 4.1 StateQueue JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["queue_id", "notifications", "last_updated"],
  "properties": {
    "queue_id": {
      "type": "string",
      "description": "队列唯一标识"
    },
    "notifications": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Notification"
      }
    },
    "last_updated": {
      "type": ["string", "null"],
      "format": "date-time"
    }
  },
  "definitions": {
    "Notification": {
      "type": "object",
      "required": ["id", "event_type", "source_agent", "target_agent", "payload", "timestamp", "status"],
      "properties": {
        "id": {
          "type": "string",
          "description": "通知唯一标识"
        },
        "event_type": {
          "type": "string",
          "description": "事件类型"
        },
        "source_agent": {
          "type": "string",
          "description": "源Agent"
        },
        "target_agent": {
          "type": "string",
          "description": "目标Agent"
        },
        "payload": {
          "type": "object",
          "description": "通知载荷"
        },
        "timestamp": {
          "type": "string",
          "format": "date-time"
        },
        "status": {
          "type": "string",
          "enum": ["pending", "read", "failed"]
        },
        "retry_count": {
          "type": "integer",
          "minimum": 0
        },
        "max_retries": {
          "type": "integer",
          "minimum": 0
        }
      }
    }
  }
}
```

### 4.2 TODO计数器 YAML Schema

```yaml
$schema: http://yaml.org/spec
type: object
required: [counter, agent_id]
properties:
  counter:
    type: integer
    description: 当前计数器值
  agent_id:
    type: string
    description: Agent标识 (1或2)
  last_updated:
    type: string
    format: date-time
```

---

## 5. CLI命令设计

### 5.1 todowrite命令增强

```python
# src/cli/todo_commands.py

@click.command("todowrite")
@click.option("--content", required=True, help="TODO内容")
@click.option("--priority", type=click.Choice(["P0", "P1", "P2"]), default="P1")
@click.option("--embed-skill", help="嵌入的Skill名称")
def todowrite_command(content: str, priority: str, embed_skill: str):
    """
    创建TODO

    创建TODO并自动执行Skill检查和编号生成。
    """
    try:
        # 1. Skill强制检查
        enforcer = SkillEnforcerEnhanced(skill_loader)
        enforcer.check("todowrite")

        # 2. 生成编号
        agent_id = os.getenv("OC_COLLAB_AGENT", "1")
        generator = TodoIdGenerator(agent_id)
        todo_id = generator.generate()

        # 3. Skill嵌入
        if embed_skill:
            embedder = SkillEmbedder(skill_loader)
            content = embedder.embed(content, embed_skill)

        # 4. 持久化
        todo = Todo(
            id=todo_id,
            content=content,
            priority=priority,
            from_agent=agent_id,
            created_at=datetime.utcnow().isoformat()
        )
        todo_store.add(todo)

        # 5. 发送通知
        notifier.notify_todo_created(todo_id, content, agent_id)

        click.echo(f"✅ TODO {todo_id} 创建成功")

    except SkillRequiredError as e:
        click.echo(f"❌ {e}")
        click.echo("请先加载所需Skill:")
        for skill in e.missing_skills:
            click.echo(f"  oc-collab skill slice {skill}")
        raise SystemExit(1)
```

### 5.2 todo migrate命令

```python
# src/cli/todo_commands.py

@click.command("migrate")
@click.option("--dry-run", is_flag=True, help="仅预览，不执行")
def todo_migrate_command(dry_run: bool):
    """
    迁移TODO编号到新格式

    将现有TODO迁移到Agent独立编号格式 (TODO-1-XXX / TODO-2-XXX)。
    """
    # 1. 检测现有TODO的Agent归属
    # 2. 生成迁移计划
    # 3. 执行迁移（或预览）
    pass
```

---

## 6. 错误处理

### 6.1 异常类型

| 异常类型 | 错误码 | 说明 |
|----------|--------|------|
| SkillRequiredError | E001 | 必需的Skill未遵循 |
| SkillNotFoundError | E002 | Skill不存在 |
| MigrationConflictError | E003 | 迁移冲突 |
| DuplicateTodoError | E004 | TODO编号重复 |
| StateQueueError | E005 | 队列操作失败 |

### 6.2 错误响应格式

```json
{
  "error": {
    "code": "E001",
    "message": "执行todowrite前必须先加载以下Skill: oc_collab_todo_execution",
    "details": {
      "missing_skills": ["oc_collab_todo_execution"],
      "required_for": "todowrite"
    },
    "suggestion": "请执行: oc-collab skill slice oc_collab_todo_execution"
  }
}
```

---

## 7. 测试策略

### 7.1 单元测试

| 测试项 | 测试类 | 覆盖方法 |
|--------|--------|----------|
| TodoIdGenerator | TestTodoIdGenerator | generate, _load_counter, _save_counter |
| TodoMigrator | TestTodoMigrator | migrate, rollback |
| SkillEnforcerEnhanced | TestSkillEnforcer | check, _load_required_skills |
| StateQueueManager | TestStateQueueManager | enqueue, get_unread, mark_read |

### 7.2 E2E测试场景

| 场景 | 测试步骤 | 预期结果 |
|------|----------|----------|
| TODO创建流程 | todowrite --content "test" | 生成TODO-1-001 |
| Skill强制检查 | todowrite无Skill | 报错E001 |
| StateReceiver接收 | POST /webhook/state | 通知进入队列 |
| Agent启动检查 | oc-collab startup-check | 显示未读通知数 |

---

## 8. 签署确认

### Agent 2 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-14 | ✅ |

### Agent 1 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-14 | ✅ 创建 |

---

**文档版本**: v1
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: APPROVED
