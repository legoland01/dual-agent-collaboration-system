# Proposal: Phase 2 - 状态同步改进

**提案编号**: PROPOSAL-COLLAB-P2-001
**版本**: v1
**创建日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**状态**: DRAFT
**关联战略**: STRATEGY_Dual_Machine_Collaboration.md
**前置提案**: PROPOSAL_COLLAB_Phase1_Git_Stability.md

---

## 1. 背景

### 1.1 问题描述

| 问题 | 表现 | 影响 |
|------|------|------|
| 状态文件不同步 | `state/agent_adhoc_todos.yaml` 未及时同步 | TODO状态不一致 |
| 冲突无检测 | 不知道何时有冲突 | 手动检查，易遗漏 |
| 冲突无解决 | 冲突后不知道如何处理 | 状态混乱 |

### 1.2 当前状态

**状态文件**：`state/agent_adhoc_todos.yaml`

**当前流程**：
1. Agent1创建TODO → commit → push
2. Agent2不知道有新TODO → 手动检查

**问题**：无自动同步，无冲突检测。

---

## 2. 需求

### 2.1 功能需求

| 功能 | 实现方式 | 优先级 |
|------|----------|--------|
| 自动拉取 | 每次CLI命令执行前自动`git pull` | P0 |
| 冲突检测 | 检测`state/`目录文件冲突 | P0 |
| 冲突解决指引 | 提供冲突解决步骤 | P0 |
| 状态变更通知 | 检测到变更时提示 | P1 |

### 2.2 非功能需求

| 需求 | 值 |
|------|-----|
| 性能 | pull时间<10秒 |
| 可靠性 | 冲突检测准确率100% |

---

## 3. 实现方案

### 3.1 自动拉取增强

```python
# src/core/state_manager.py

class StateManager:
    """状态管理器，增强同步功能"""

    def auto_pull_before_command(self) -> Dict[str, Any]:
        """
        在执行命令前自动拉取最新状态

        Returns:
            {
                "success": bool,
                "pulled_files": List[str],
                "conflicts": List[str],
                "message": str
            }
        """
        git_helper = GitHelper(self.project_path)

        result = {
            "success": False,
            "pulled_files": [],
            "conflicts": [],
            "message": ""
        }

        # 检查是否有远程变更
        if not git_helper.has_remote_changes():
            result["success"] = True
            result["message"] = "无需拉取，状态已是最新"
            return result

        # 执行拉取
        pull_result = git_helper.pull_with_retry()
        result["pulled_files"] = pull_result.get("pulled_files", [])

        if pull_result["success"]:
            result["success"] = True
            result["message"] = f"已拉取最新状态: {result['pulled_files']}"
        else:
            result["message"] = f"拉取失败: {pull_result.get('error', '未知错误')}"

        return result
```

### 3.2 冲突检测

```python
# src/core/state_manager.py

class StateConflictDetector:
    """状态文件冲突检测器"""

    STATE_FILES = [
        "agent_adhoc_todos.yaml",
        "project_state.yaml",
        "compliance_results.yaml"
    ]

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        检测状态文件冲突

        Returns:
            [
                {
                    "file": str,
                    "has_conflict": bool,
                    "conflict_type": str,  # "content" | "version" | "concurrent"
                    "local_version": str,
                    "remote_version": str
                }
            ]
        """
        conflicts = []

        for filename in self.STATE_FILES:
            filepath = self.project_path / "state" / filename
            if not filepath.exists():
                continue

            # 比较本地和远程版本
            local_hash = self._get_file_hash(filepath)
            remote_hash = self._get_remote_file_hash(filename)

            if local_hash != remote_hash:
                conflicts.append({
                    "file": filename,
                    "has_conflict": True,
                    "conflict_type": "content",
                    "local_version": local_hash[:8],
                    "remote_version": remote_hash[:8]
                })

        return conflicts

    def suggest_resolution(self, conflicts: List[Dict]) -> str:
        """生成冲突解决建议"""
        if not conflicts:
            return "✅ 无冲突"

        suggestions = ["⚠️ 检测到以下冲突："]

        for conflict in conflicts:
            suggestions.append(f"""
文件: {conflict['file']}
本地版本: {conflict['local_version']}
远程版本: {conflict['remote_version']}

解决步骤:
1. 执行 `git stash` 暂存本地变更
2. 执行 `git pull` 拉取远程
3. 执行 `git stash pop` 合并变更
4. 解决冲突后重新提交""")

        return "\n".join(suggestions)
```

### 3.3 CLI命令增强

```python
# src/cli/main.py

@main.command("sync-state")
@click.option("--force", is_flag=True, help="强制拉取，不检查变更")
def sync_state_command(force: bool):
    """同步最新状态文件"""
    project_path = get_project_path()
    state_manager = StateManager(project_path)

    if force:
        result = state_manager.force_pull()
    else:
        result = state_manager.auto_pull_before_command()

    if result["success"]:
        click.echo(f"✅ {result['message']}")

        # 检查冲突
        detector = StateConflictDetector(project_path)
        conflicts = detector.detect_conflicts()

        if conflicts:
            click.echo(f"⚠️ 检测到 {len(conflicts)} 个冲突")
            suggestion = detector.suggest_resolution(conflicts)
            click.echo(suggestion)
        else:
            click.echo("✅ 无冲突")
    else:
        click.echo(f"❌ {result['message']}")


@main.command("check-conflicts")
def check_conflicts_command():
    """检查状态文件冲突"""
    project_path = get_project_path()
    detector = StateConflictDetector(project_path)

    conflicts = detector.detect_conflicts()

    if not conflicts:
        click.echo("✅ 无冲突，状态同步正常")
        return

    click.echo(f"⚠️ 检测到 {len(conflicts)} 个冲突")

    for conflict in conflicts:
        click.echo(f"""
文件: {conflict['file']}
类型: {conflict['conflict_type']}
本地: {conflict['local_version']}
远程: {conflict['remote_version']}
""")

    suggestion = detector.suggest_resolution(conflicts)
    click.echo(suggestion)
```

### 3.4 钩子集成

```python
# src/core/hooks/auto_sync_hook.py

class AutoSyncHook:
    """自动同步钩子，在CLI命令前执行"""

    @staticmethod
    def before_command(command_name: str):
        """在命令执行前自动同步状态"""
        project_path = get_project_path()
        state_manager = StateManager(project_path)

        # 只对需要状态的操作进行同步
        sync_commands = ["todo", "status", "signoff", "review", "advance"]

        if any(cmd in command_name for cmd in sync_commands):
            result = state_manager.auto_pull_before_command()

            if result["success"] and result.get("pulled_files"):
                console.print(
                    f"[green]✅ 已同步状态: {', '.join(result['pulled_files'])}[/green]"
                )
```

---

## 4. 验收标准

### 4.1 功能验收

| 序号 | 验收项 | 验收标准 |
|------|--------|----------|
| S-01 | 自动拉取 | CLI命令执行前自动拉取最新状态 |
| S-02 | 冲突检测 | 检测`state/`目录文件冲突 |
| S-03 | 冲突指引 | 提供解决步骤 |
| S-04 | 状态变更提示 | 检测到变更时提示 |

### 4.2 单元测试

```python
# tests/test_state_sync.py

class TestStateSync:
    """状态同步测试"""

    def test_auto_pull_no_changes(self, state_manager, mock_no_remote_changes):
        """测试无远程变更时"""
        result = state_manager.auto_pull_before_command()
        assert result["success"] is True
        assert "已是最新" in result["message"]

    def test_auto_pull_with_changes(self, state_manager, mock_has_remote_changes):
        """测试有远程变更时"""
        result = state_manager.auto_pull_before_command()
        assert result["success"] is True
        assert len(result["pulled_files"]) > 0

    def test_detect_conflicts(self, state_manager, mock_conflict):
        """测试冲突检测"""
        conflicts = state_manager.detect_conflicts()
        assert len(conflicts) > 0
        assert conflicts[0]["file"] == "agent_adhoc_todos.yaml"

    def test_suggest_resolution(self, state_manager, mock_conflict):
        """测试解决建议"""
        conflicts = state_manager.detect_conflicts()
        suggestion = state_manager.suggest_resolution(conflicts)
        assert "冲突" in suggestion
        assert "git stash" in suggestion
```

---

## 5. 工时预估

| 任务 | 工时 | 说明 |
|------|------|------|
| 自动拉取 | 3h | StateManager增强 |
| 冲突检测 | 4h | StateConflictDetector |
| CLI命令 | 2h | sync-state, check-conflicts |
| 钩子集成 | 2h | before_command钩子 |
| 单元测试 | 3h | 覆盖所有场景 |
| E2E测试 | 2h | 实际场景测试 |
| **合计** | **16h** | 2天 |

---

## 6. 依赖关系

| 依赖 | 说明 |
|------|------|
| `src/core/state_manager.py` | 状态管理 |
| `src/core/git.py` | Git操作 |
| `src/cli/main.py` | CLI入口 |

---

## 7. 风险与应对

| 风险 | 可能性 | 影响 | 应对 |
|------|--------|------|------|
| Git不稳定导致拉取失败 | 中 | 低 | 提供`--force`跳过选项 |
| 误判冲突 | 低 | 中 | 提供手动确认机制 |
| 性能影响 | 中 | 低 | 异步拉取，不阻塞命令 |

---

## 8. 实施计划

| 日期 | 任务 | 交付物 |
|------|------|--------|
| Day 1 | 自动拉取 | `src/core/state_manager.py` |
| Day 1 | 冲突检测 | `src/core/state_manager.py` (增强) |
| Day 2 | CLI命令 | `src/cli/main.py` |
| Day 3 | 单元测试 | `tests/test_state_sync.py` |
| Day 4 | E2E测试 | 测试报告 |
| Day 5 | 文档更新 | 更新README.md |

---

## 9. 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-08 | ✅ |

### Agent  评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT
