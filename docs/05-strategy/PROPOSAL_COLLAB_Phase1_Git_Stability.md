# Proposal: Phase 1 - Git稳定性改进

**提案编号**: PROPOSAL-COLLAB-P1-001
**版本**: v1
**创建日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**状态**: DRAFT
**关联战略**: STRATEGY_Dual_Machine_Collaboration.md

---

## 1. 背景

### 1.1 问题描述

| 问题 | 表现 | 影响 |
|------|------|------|
| GitHub不稳定 | 推送失败、连接超时 | 协作中断、等待 |
| 无统一推送策略 | GitHub/Gitee无优先级 | 不可预测的失败 |

### 1.2 当前状态

```python
# src/core/git.py
def push_all_remotes(message: str):
    """推送到所有远程仓库（无优先级）"""
    for remote in self.get_all_remotes():
        self.push_to_remote(remote)
```

**问题**：GitHub失败时，整个操作失败，即使Gitee可用。

---

## 2. 需求

### 2.1 功能需求

| 功能 | 实现方式 | 优先级 |
|------|----------|--------|
| Gitee优先级 | GitHelper优先推送Gitee | P0 |
| 自动fallback | Gitee失败时自动尝试GitHub | P0 |
| 重试机制 | 失败后自动重试3次 | P1 |
| 详细日志 | 记录每次推送结果 | P1 |

### 2.2 非功能需求

| 需求 | 值 |
|------|-----|
| 性能 | 推送时间<30秒 |
| 可靠性 | 推送成功率>99% |
| 可观测性 | 每次推送有详细日志 |

---

## 3. 实现方案

### 3.1 GitHelper增强

```python
# src/core/git.py

class GitHelper:
    """Git操作助手，增强稳定性"""

    # 远程仓库优先级（按可靠性排序）
    REMOTE_PRIORITY = ["gitee", "github", "origin"]

    def push_with_priority(self, message: str) -> Dict[str, Any]:
        """
        按优先级推送到远程仓库

        Returns:
            {
                "success": bool,
                "primary_remote": str,
                "fallback_remote": str,
                "attempted_remotes": List[str],
                "duration": float,
                "errors": List[str]
            }
        """
        remotes = self.get_all_remotes()

        # 按优先级排序
        sorted_remotes = self._sort_by_priority(remotes)

        result = {
            "success": False,
            "primary_remote": None,
            "fallback_remote": None,
            "attempted_remotes": [],
            "duration": 0.0,
            "errors": []
        }

        start_time = time.time()

        for remote in sorted_remotes:
            try:
                self.push_to_remote(remote, message)
                result["attempted_remotes"].append(remote)

                if result["primary_remote"] is None:
                    result["primary_remote"] = remote
                    # 第一个成功的即为最终成功
                    result["success"] = True
                    break
            except Exception as e:
                result["attempted_remotes"].append(remote)
                result["errors"].append(f"{remote}: {str(e)}")

        result["duration"] = time.time() - start_time
        return result

    def _sort_by_priority(self, remotes: List[str]) -> List[str]:
        """按优先级排序远程仓库"""
        priority_map = {r: i for i, r in enumerate(self.REMOTE_PRIORITY)}
        return sorted(remotes, key=lambda r: priority_map.get(r, 999))
```

### 3.2 CLI命令增强

```python
# src/cli/main.py

@main.command("push-priority")
@click.option("--message", "-m", help="提交信息")
@click.option("--dry-run", is_flag=True, help="仅显示要推送的远程，不实际推送")
def push_priority_command(message: str, dry_run: bool):
    """按优先级推送到远程仓库（Gitee优先）"""
    project_path = get_project_path()
    git_helper = GitHelper(project_path)

    if dry_run:
        remotes = git_helper.get_all_remotes()
        sorted_remotes = git_helper._sort_by_priority(remotes)
        click.echo(f"将按以下优先级推送: {sorted_remotes}")
        return

    if not message:
        message = click.prompt("请输入提交信息", default="auto-sync: 更新")

    result = git_helper.push_with_priority(message)

    if result["success"]:
        click.echo(f"✅ 成功推送到 {result['primary_remote']}")
    else:
        click.echo(f"❌ 推送到所有远程仓库失败")

    if result["attempted_remotes"]:
        click.echo(f"已尝试: {result['attempted_remotes']}")

    click.echo(f"耗时: {result['duration']:.2f}秒")
```

### 3.3 配置文件

```yaml
# config/git.yaml
git:
  # 远程仓库优先级（按可靠性排序）
  remote_priority:
    - gitee
    - github
    - origin

  # 重试配置
  retry:
    enabled: true
    max_attempts: 3
    delay: 1.0  # 秒

  # 超时配置
  timeout:
    push: 60
    pull: 30
    clone: 120
```

---

## 4. 验收标准

### 4.1 功能验收

| 序号 | 验收项 | 验收标准 |
|------|--------|----------|
| G-01 | Gitee优先 | `push-priority`命令优先推送Gitee |
| G-02 | 自动fallback | Gitee失败时自动尝试GitHub |
| G-03 | 重试机制 | 失败后自动重试3次 |
| G-04 | 详细日志 | 记录每次推送的详细结果 |

### 4.2 性能验收

| 序号 | 验收项 | 验收标准 |
|------|--------|----------|
| P-01 | 推送时间 | 单次推送<30秒 |
| P-02 | 成功率 | 连续100次推送>99%成功 |

### 4.3 单元测试

```python
# tests/test_git_priority.py

class TestGitPriority:
    """Git优先级推送测试"""

    def test_priority_order(self, git_helper):
        """测试远程仓库按优先级排序"""
        remotes = ["github", "origin", "gitee"]
        sorted_remotes = git_helper._sort_by_priority(remotes)
        assert sorted_remotes == ["gitee", "github", "origin"]

    def test_push_priority_success(self, git_helper):
        """测试优先级推送成功"""
        result = git_helper.push_with_priority("test message")
        assert result["success"] is True
        assert result["primary_remote"] == "gitee"

    def test_push_priority_fallback(self, git_helper, mock_gitee_fail):
        """测试Gitee失败时自动fallback"""
        result = git_helper.push_with_priority("test message")
        assert result["success"] is True
        assert result["fallback_remote"] == "github"

    def test_push_priority_all_fail(self, git_helper, mock_all_remotes_fail):
        """测试所有远程都失败"""
        result = git_helper.push_with_priority("test message")
        assert result["success"] is False
        assert len(result["attempted_remotes"]) == 3
```

---

## 5. 工时预估

| 任务 | 工时 | 说明 |
|------|------|------|
| GitHelper优先级推送 | 4h | 核心功能 |
| CLI命令 | 2h | push-priority命令 |
| 配置文件 | 1h | git.yaml |
| 单元测试 | 3h | 覆盖所有场景 |
| E2E测试 | 2h | 实际Git操作测试 |
| **合计** | **12h** | 2天 |

---

## 6. 依赖关系

| 依赖 | 说明 |
|------|------|
| `src/core/git.py` | 核心Git操作 |
| `src/cli/main.py` | CLI入口 |
| `config/git.yaml` | 配置文件 |

---

## 7. 风险与应对

| 风险 | 可能性 | 影响 | 应对 |
|------|--------|------|------|
| Gitee也连不上 | 低 | 中 | fallback到GitHub |
| 优先级配置错误 | 低 | 高 | 提供默认值，CLI可覆盖 |
| 重试导致延迟 | 中 | 低 | 提供超时配置 |

---

## 8. 实施计划

| 日期 | 任务 | 交付物 |
|------|------|--------|
| Day 1 | GitHelper优先级推送 | `src/core/git.py` |
| Day 2 | CLI命令 | `src/cli/main.py` |
| Day 3 | 单元测试 | `tests/test_git_priority.py` |
| Day 4 | E2E测试 | 测试报告 |
| Day 5 | 文档更新 | 更新README.md |

---

## 9. 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-08 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT
