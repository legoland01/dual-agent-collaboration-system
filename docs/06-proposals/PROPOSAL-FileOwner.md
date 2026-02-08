# Proposal: 文件Owner机制

**Proposal ID**: PROPOSAL-20260208-001
**状态**: 待评审
**创建人**: Agent 2
**创建日期**: 2026-02-08

---

## 背景

### 问题

当前角色边界检查（RoleBoundaryChecker）只在CLI命令中生效，Edit/Write/Bash等工具直接操作文件，不经过任何权限检查。

| 检查方式 | 生效范围 |
|----------|----------|
| RoleBoundaryChecker | CLI命令（oc-collab compliance check） |
| Edit工具 | ❌ 不生效 |
| Write工具 | ❌ 不生效 |
| Bash命令 | ❌ 不生效 |

### 现有解决方案（临时）

创建 `scripts/role_check.py` 辅助检查脚本，但依赖Agent主动调用，无法强制执行。

---

## 解决方案：文件Owner机制

### 核心概念

引入**文件Owner**概念，实现基于文件的权限控制：

| 概念 | 说明 |
|------|------|
| 文件Owner | 创建文件的Agent，后续只有Owner能修改 |
| Owner转移 | 通过signoff签署后转移Owner |
| 继承规则 | 签署后文件Owner转移给签署方 |

### 设计原则

```
文件创建者 = Owner
    ↓
签署流程完成
    ↓
Owner转移给签署方（Agent1或Agent2）
    ↓
只有Owner能修改文件
```

### 权限模型

```
┌─────────────────────────────────────────────┐
│              权限检查优先级                   │
├─────────────────────────────────────────────┤
│ 1. 文件Owner检查（最优先）                   │
│    - 只有Owner能修改文件                      │
│    - 即使角色允许也无法修改                    │
├─────────────────────────────────────────────┤
│ 2. RoleBoundaryChecker（次优先）              │
│    - 角色级别的目录限制                       │
│    - 作为Owner检查的补充                      │
└─────────────────────────────────────────────┘
```

---

## 详细设计

### 1. 文件元数据存储

#### 文件位置

```
state/file_owners.yaml
```

#### 数据结构

```yaml
# state/file_owners.yaml
version: "1.0"
last_updated: "2026-02-08T23:00:00"

file_owners:
  # 代码文件 - Agent2创建，Owner为agent2
  "src/core/signoff.py":
    owner: "agent2"
    created_by: "agent2"
    created_at: "2026-02-08T20:00:00"
    last_modified: "2026-02-08T22:00:00"
    signoff_transfer: true
    signoff_history:
      - action: "signoff_test"
        signer: "agent1"
        timestamp: "2026-02-08T21:00:00"
        owner_transferred_to: "agent1"

  # 需求文件 - Agent1创建，Owner为agent1
  "docs/01-requirements/requirements_v2.2.4.md":
    owner: "agent1"
    created_by: "agent1"
    created_at: "2026-02-08T10:00:00"
    signoff_transfer: true
    signoff_history: []

  # 测试文件 - Agent2创建，Owner为agent2
  "tests/test_signoff.py":
    owner: "agent2"
    created_by: "agent2"
    created_at: "2026-02-08T20:30:00"
    signoff_transfer: false
```

#### Owner类型

| 类型 | 说明 | 示例 |
|------|------|------|
| agent | 具体Agent | "agent1", "agent2" |
| shared | 共享文件（需双方签署） | 部署脚本、配置文件 |
| immutable | 不可修改 | 已发布的版本文件 |

### 2. Owner检查器实现

#### 文件位置

```
src/core/file_owner_checker.py
```

#### 代码实现

```python
"""文件Owner检查器 - 实现基于文件的权限控制"""
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import yaml


@dataclass
class FileOwnerInfo:
    """文件Owner信息"""
    path: str
    owner: str
    created_by: str
    created_at: str
    last_modified: str
    signoff_transfer: bool = False
    signoff_history: list = None

    def __post_init__(self):
        if self.signoff_history is None:
            self.signoff_history = []


class FileOwnerCheckerError(Exception):
    """Owner检查器异常"""
    pass


class FileOwnerChecker:
    """文件Owner检查器"""

    OWNERS_FILE = "state/file_owners.yaml"

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.owners_file = self.project_path / self.OWNERS_FILE
        self._cache: Optional[Dict] = None

    def _load_owners(self) -> Dict:
        """加载Owner数据"""
        if self._cache is not None:
            return self._cache

        if not self.owners_file.exists():
            self._init_owners_file()
            return {"version": "1.0", "file_owners": {}, "last_updated": ""}

        with open(self.owners_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {"version": "1.0", "file_owners": {}}

        self._cache = data
        return data

    def _save_owners(self, data: Dict) -> None:
        """保存Owner数据"""
        data["last_updated"] = datetime.now().isoformat()

        with open(self.owners_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

        self._cache = None

    def _init_owners_file(self) -> None:
        """初始化Owner文件"""
        self.owners_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "file_owners": {},
            "last_updated": datetime.now().isoformat()
        }
        with open(self.owners_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def register_file(
        self,
        file_path: str,
        owner: str,
        created_by: str,
        signoff_transfer: bool = False
    ) -> FileOwnerInfo:
        """注册文件Owner

        Args:
            file_path: 文件路径
            owner: Owner (agent1/agent2)
            created_by: 创建者
            signoff_transfer: 是否支持signoff转移
        """
        data = self._load_owners()

        now = datetime.now().isoformat()
        info = FileOwnerInfo(
            path=file_path,
            owner=owner,
            created_by=created_by,
            created_at=now,
            last_modified=now,
            signoff_transfer=signoff_transfer,
            signoff_history=[]
        )

        data["file_owners"][file_path] = {
            "owner": owner,
            "created_by": created_by,
            "created_at": now,
            "last_modified": now,
            "signoff_transfer": signoff_transfer,
            "signoff_history": []
        }

        self._save_owners(data)
        return info

    def get_owner(self, file_path: str) -> Optional[str]:
        """获取文件Owner

        Args:
            file_path: 文件路径

        Returns:
            Owner ID or None if not found
        """
        data = self._load_owners()
        file_info = data.get("file_owners", {}).get(file_path)
        return file_info.get("owner") if file_info else None

    def can_edit(self, agent_id: str, file_path: str) -> tuple[bool, str]:
        """检查Agent是否可以编辑文件

        Args:
            agent_id: Agent ID
            file_path: 文件路径

        Returns:
            (can_edit, message)
        """
        owner = self.get_owner(file_path)

        if owner is None:
            # 文件未注册，提示注册
            return False, f"文件未注册Owner，请先注册: {file_path}"

        if owner != agent_id:
            # 只有Owner能编辑
            return False, f"权限拒绝: {file_path} 的Owner是 {owner}，{agent_id} 无法编辑"

        return True, f"权限通过: {agent_id} 是 {file_path} 的Owner"

    def transfer_owner(
        self,
        file_path: str,
        new_owner: str,
        signer: str,
        action: str
    ) -> None:
        """转移文件Owner（签署后调用）

        Args:
            file_path: 文件路径
            new_owner: 新Owner
            signer: 签署者
            action: 签署动作
        """
        data = self._load_owners()

        if file_path not in data.get("file_owners", {}):
            raise FileOwnerCheckerError(f"文件未注册: {file_path}")

        file_info = data["file_owners"][file_path]

        if not file_info.get("signoff_transfer", False):
            raise FileOwnerCheckerError(f"文件不支持signoff转移Owner: {file_path}")

        old_owner = file_info["owner"]
        file_info["owner"] = new_owner
        file_info["last_modified"] = datetime.now().isoformat()
        file_info["signoff_history"].append({
            "action": action,
            "signer": signer,
            "timestamp": datetime.now().isoformat(),
            "owner_transferred_from": old_owner,
            "owner_transferred_to": new_owner
        })

        self._save_owners(data)

    def get_file_info(self, file_path: str) -> Optional[FileOwnerInfo]:
        """获取文件完整信息

        Args:
            file_path: 文件路径

        Returns:
            FileOwnerInfo or None
        """
        data = self._load_owners()
        file_info = data.get("file_owners", {}).get(file_path)

        if file_info is None:
            return None

        return FileOwnerInfo(
            path=file_path,
            owner=file_info["owner"],
            created_by=file_info["created_by"],
            created_at=file_info["created_at"],
            last_modified=file_info["last_modified"],
            signoff_transfer=file_info.get("signoff_transfer", False),
            signoff_history=file_info.get("signoff_history", [])
        )

    def list_files_by_owner(self, owner: str) -> list[str]:
        """列出指定Owner的所有文件

        Args:
            owner: Owner ID

        Returns:
            文件路径列表
        """
        data = self._load_owners()
        return [
            path for path, info in data.get("file_owners", {}).items()
            if info["owner"] == owner
        ]

    def batch_register(self, files: list[dict]) -> int:
        """批量注册文件

        Args:
            files: 文件信息列表
                [{"path": "...", "owner": "...", "created_by": "...", "signoff_transfer": True}]

        Returns:
            注册数量
        """
        data = self._load_owners()
        now = datetime.now().isoformat()
        count = 0

        for f in files:
            path = f["path"]
            if path not in data.get("file_owners", {}):
                data["file_owners"][path] = {
                    "owner": f["owner"],
                    "created_by": f["created_by"],
                    "created_at": now,
                    "last_modified": now,
                    "signoff_transfer": f.get("signoff_transfer", False),
                    "signoff_history": []
                }
                count += 1

        self._save_owners(data)
        return count
```

### 3. 与现有组件集成

#### 3.1 与Signoff流程集成

```python
# src/core/signoff.py

class SignoffEngine:
    """签署引擎 - 添加Owner转移"""

    def sign(self, stage: str, agent: str, message: str) -> SignoffResult:
        """执行签署"""
        # ... 现有签署逻辑 ...

        # 签署成功后转移文件Owner
        if stage == "test":
            self._transfer_test_file_owners(agent)

        return result

    def _transfer_test_file_owners(self, new_owner: str) -> None:
        """转移测试相关文件的Owner"""
        checker = FileOwnerChecker()

        # 转移测试文件Owner
        test_files = [
            "tests/test_skill_enforcer.py",
            "tests/test_signoff_enforcer.py",
            "tests/test_requirements_checker.py",
            "tests/test_enforcement_system_e2e.py"
        ]

        for test_file in test_files:
            if Path(test_file).exists():
                try:
                    checker.transfer_owner(
                        test_file,
                        new_owner,
                        new_owner,
                        "signoff_test"
                    )
                except FileOwnerCheckerError:
                    pass  # 文件可能未注册
```

#### 3.2 与CLI命令集成

```python
# src/cli/compliance_commands.py

@click.command(name="check")
@click.option("--type", type=click.Choice(["role", "owner", "all"]))
@click.option("--agent", required=True)
@click.option("--action", required=True)
@click.option("--target", required=True)
def compliance_check_command(type: str, agent: str, action: str, target: str):
    """合规检查命令 - 添加Owner检查"""
    if type in ["owner", "all"]:
        checker = FileOwnerChecker()
        can_edit, msg = checker.can_edit(agent, target)
        if not can_edit:
            click.echo(f"❌ {msg}")
            return

    # ... 继续RoleBoundaryChecker检查 ...
```

### 4. CLI命令

#### 4.1 注册文件Owner

```bash
# 注册单个文件
oc-collab owner register --file src/core/signoff.py --owner agent2

# 批量注册
oc-collab owner register --dir tests/ --owner agent2

# 带signoff转移
oc-collab owner register --file tests/test_*.py --owner agent2 --signoff-transfer
```

#### 4.2 查询文件Owner

```bash
# 查询单个文件
oc-collab owner show src/core/signoff.py

# 输出示例
# File: src/core/signoff.py
# Owner: agent2
# Created by: agent2
# Created at: 2026-02-08T20:00:00
# Signoff transfer: True

# 列出所有文件
oc-collab owner list --owner agent2
```

#### 4.3 转移文件Owner

```bash
# 签署后转移Owner（自动）
oc-collab signoff test -m "验收通过"

# 手动转移
oc-collab owner transfer --file src/core/signoff.py --to agent1 --reason "签署完成"
```

---

## 影响分析

### 1. 需要新增的组件

| 组件 | 文件 | 说明 |
|------|------|------|
| FileOwnerChecker | src/core/file_owner_checker.py | Owner检查器 |
| CLI命令 | src/cli/owner_commands.py | Owner管理命令 |
| 配置文件 | state/file_owners.yaml | Owner元数据 |

### 2. 需要修改的组件

| 组件 | 修改内容 |
|------|----------|
| signoff.py | 签署后调用transfer_owner |
| enhanced_commands.py | 添加owner子命令 |
| TODO同步 | 同步Owner变更 |

### 3. 工时估算

| 阶段 | 任务 | 工时 |
|------|------|------|
| Phase 1 | FileOwnerChecker实现 | 2h |
| Phase 2 | CLI命令实现 | 1h |
| Phase 3 | Signoff集成 | 1h |
| Phase 4 | 现有文件注册 | 0.5h |
| Phase 5 | Skill更新 | 1h |
| **合计** | | **5.5h** |

---

## 受影响的Skill

### 1. oc_collab_development_guide

| 修改点 | 说明 |
|--------|------|
| 代码编辑流程 | 添加Owner检查步骤 |
| 单元测试 | 注册测试文件Owner |
| Git提交 | 提交时检查Owner |

### 2. oc_collab_bug_management_guide

| 修改点 | 说明 |
|--------|------|
| Bug修复流程 | 创建Bug报告时注册文件Owner |
| Owner转移 | Bug修复后通过signoff转移Owner |

### 3. oc_collab_collaboration_guide

| 修改点 | 说明 |
|--------|------|
| 协作流程 | 添加Owner机制说明 |
| 角色权限 | 区分角色权限和Owner权限 |

### 4. oc_collab_deployment_guide

| 修改点 | 说明 |
|--------|------|
| 部署文件 | 注册部署脚本Owner |
| 版本发布 | 发布后设置文件为immutable |

### 5. oc_collab_test_acceptance_guide

| 修改点 | 说明 |
|--------|------|
| 测试文件 | 测试完成后签署，转移Owner |

---

## 实施步骤

### Phase 1: 基础设施（2h）

1. 创建 `src/core/file_owner_checker.py`
2. 实现基础Owner注册和查询
3. 添加单元测试

### Phase 2: CLI命令（1h）

1. 创建 `src/cli/owner_commands.py`
2. 实现 register/show/transfer 命令
3. 集成到 main.py

### Phase 3: Signoff集成（1h）

1. 修改 `src/core/signoff.py`
2. 签署完成后自动转移Owner
3. 测试签署流程

### Phase 4: 迁移现有文件（0.5h）

1. 扫描现有src/文件，注册agent2为Owner
2. 扫描docs/文件，注册相应Owner
3. 扫描tests/文件，注册agent2为Owner

### Phase 5: Skill更新（1h）

1. 更新 development_guide
2. 更新 bug_management_guide
3. 更新 collaboration_guide

---

## 验证方法

### 单元测试

```bash
# 运行FileOwnerChecker测试
python3 -m pytest tests/test_file_owner_checker.py -v
```

### 集成测试

```bash
# 1. 注册文件
oc-collab owner register --file src/core/signoff.py --owner agent2

# 2. Agent1尝试编辑（应该被拒绝）
python3 scripts/role_check.py agent1 edit src/core/signoff.py
# 输出: 权限拒绝: src/core/signoff.py 的Owner是 agent2

# 3. Agent2尝试编辑（应该通过）
python3 scripts/role_check.py agent2 edit src/core/signoff.py
# 输出: 权限通过
```

### Signoff测试

```bash
# 签署测试阶段
oc-collab signoff test -m "验收通过"

# 验证Owner转移
oc-collab owner show tests/test_signoff.py
# 应该显示Owner已转移到agent1
```

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 现有文件未注册 | 无法检查权限 | 提供批量注册脚本 |
| 忘记注册新文件 | 权限控制失效 | 在Create命令中自动注册 |
| Owner错误转移 | 权限混乱 | 仅在signoff后允许转移 |

---

## 附录

### A. 文件Owner配置示例

```yaml
# state/file_owners.yaml
version: "1.0"
last_updated: "2026-02-08T23:00:00"

file_owners:
  # 代码文件
  "src/core/signoff.py":
    owner: "agent2"
    created_by: "agent2"
    created_at: "2026-02-08T20:00:00"
    signoff_transfer: true
    signoff_history:
      - action: "signoff_test"
        signer: "agent1"
        timestamp: "2026-02-08T21:00:00"
        owner_transferred_from: "agent2"
        owner_transferred_to: "agent1"

  # 需求文件
  "docs/01-requirements/requirements_v2.2.4.md":
    owner: "agent1"
    created_by: "agent1"
    created_at: "2026-02-08T10:00:00"
    signoff_transfer: true
    signoff_history: []

  # 测试文件
  "tests/test_signoff.py":
    owner: "agent2"
    created_by: "agent2"
    created_at: "2026-02-08T20:30:00"
    signoff_transfer: false

  # 不可变文件
  "CHANGELOG.md":
    owner: "shared"
    created_by: "agent1"
    created_at: "2026-02-08T10:00:00"
    signoff_transfer: false
```

### B. 与RoleBoundaryChecker对比

| 特性 | RoleBoundaryChecker | FileOwnerChecker |
|------|---------------------|------------------|
| 控制粒度 | 目录级别 | 文件级别 |
| 生效时机 | CLI命令 | 所有文件操作 |
| 灵活性 | 固定规则 | 可配置Owner |
| Owner转移 | 不支持 | 支持 |
| 实现复杂度 | 低 | 中 |

---

**创建人**: Agent 2
**创建日期**: 2026-02-08
**状态**: 待Agent 1评审
