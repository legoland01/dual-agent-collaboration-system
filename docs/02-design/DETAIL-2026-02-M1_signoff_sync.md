# 详细设计：签署自动同步功能

**设计文档ID**: DETAIL-2026-02-M1
**版本**: v1
**日期**: 2026-02-05
**作者**: Agent 2 (开发负责人)
**状态**: DRAFT

---

## 1. 概述

### 1.1 功能描述

在 `oc-collab signoff` 命令中添加 `--sync` 选项，签署后自动同步到远程仓库。

### 1.2 相关需求

- FR-SIGNOFF-AUTO-001

---

## 2. 技术设计

### 2.1 命令设计

```bash
# 签署并自动同步
oc-collab signoff requirements --sync

# 只签署不同步
oc-collab signoff requirements

# 里程碑签署并同步
oc-collab signoff milestone --name M5 --sync
```

### 2.2 配置选项

```yaml
# config.yaml
signoff:
  auto_sync: false  # 默认关闭
```

### 2.3 优先级

```
--sync 命令行选项 > 配置文件 > 默认行为
```

---

## 3. 实现方案

### 3.1 CLI 修改

修改 `src/cli/main.py`:

```python
@main.command("signoff")
@click.argument("stage", type=click.Choice(["requirements", "design", "test", "milestone"]))
@click.option("--name", "-n", help="里程碑名称 (仅 milestone 阶段需要)")
@click.option("--sync", "-s", is_flag=True, default=False, help="签署后自动同步到远程")
@click.option("--comment", "-m", default="")
@click.option("--reject", "-r", default=None)
def signoff_command(stage: str, name: str, sync: bool, comment: str, reject: str):
    """签署确认。"""
    try:
        project_path = get_project_path()
        state_manager = StateManager(project_path)
        signoff_engine = SignoffEngine(project_path)

        if sync:
            result = signoff_engine.signoff_with_sync(stage, name, comment, reject)
        else:
            result = signoff_engine.execute(stage, name, comment, reject)

        if result.success:
            click.echo(f"✓ {result.message}")
        else:
            click.echo(f"✗ {result.message}")

    except Exception as e:
        click.echo(f"错误: {e}")
        sys.exit(1)
```

### 3.2 SignoffEngine 修改

修改 `src/core/signoff.py`:

```python
class SignoffEngine:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.state_manager = StateManager(project_path)
        self.git_helper = GitHelper(project_path)

    def signoff_with_sync(self, stage: str, name: str = None, comment: str = "", reject: str = None) -> SignoffResult:
        """签署并同步"""
        result = self.execute(stage, name, comment, reject)

        if result.success:
            sync_result = self._sync_to_remote()
            result.message = f"{result.message}\n{sync_result.message}"

        return result

    def _sync_to_remote(self) -> SyncResult:
        """同步到远程"""
        try:
            self.git_helper.push()
            return SyncResult(success=True, message="✓ 已同步到远程仓库")
        except Exception as e:
            return SyncResult(success=False, message=f"⚠ 同步失败: {e}")
```

### 3.3 配置文件集成

```python
def _load_auto_sync_config(self) -> bool:
    """加载 auto_sync 配置"""
    config_file = Path(self.project_path) / "config.yaml"
    if config_file.exists():
        import yaml
        with open(config_file) as f:
            config = yaml.safe_load(f) or {}
        return config.get("signoff", {}).get("auto_sync", False)
    return False
```

---

## 4. 测试用例

### 4.1 单元测试

```python
def test_signoff_with_sync():
    """测试签署并同步"""
    engine = SignoffEngine(project_path)
    result = engine.signoff_with_sync("requirements")
    assert result.success is True
    assert "已同步到远程仓库" in result.message

def test_signoff_without_sync():
    """测试只签署不同步"""
    engine = SignoffEngine(project_path)
    result = engine.execute("requirements")
    assert result.success is True
    assert "已同步到远程仓库" not in result.message
```

---

## 5. 验收标准

| 标准 | 验证方式 |
|------|----------|
| `--sync` 选项生效 | CLI 测试 |
| auto_sync 配置生效 | 配置测试 |
| 签署失败时不同步 | 异常测试 |
| 错误处理正确 | 异常测试 |

---

**设计版本**: v1
**创建日期**: 2026-02-05
**状态**: DRAFT
