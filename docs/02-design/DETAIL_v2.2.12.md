# 详细设计说明书：oc-collab v2.2.12

**版本**: v1
**创建日期**: 2026-02-14
**作者**: Agent 2 (开发负责人)
**关联概要设计**: OUTLINE_v2.2.12.md
**版本号**: v2.2.12
**状态**: DRAFT

---

## 1. 功能模块映射

### 1.1 映射表

| 功能模块 (概要设计) | 技术模块 (详细设计) | 对应文件 |
|---------------------|---------------------|----------|
| 部署前检查 | DocChecker, StateChecker | src/cli/deploy_commands.py |
| 版本号管理 | VersionManager | src/core/version_manager.py |
| 包构建 | PackageBuilder | src/core/package_builder.py |
| PyPI发布 | PyPIUploader | src/core/pypi_uploader.py |
| Git推送 | GitPusher | src/core/git_pusher.py |
| 发布验证 | Verifier | src/core/deploy_verifier.py |
| 状态更新 | StateUpdater | src/core/state_updater.py |
| 编排层 | DeploymentOrchestrator | src/core/deployment_orchestrator.py |

### 1.2 新增/变更文件

| 文件路径 | 功能 | 工时 |
|----------|------|------|
| src/core/deployment_orchestrator.py | 部署编排器 | 2h |
| src/core/version_manager.py | 版本号管理器 | 1h |
| src/core/package_builder.py | 包构建器 | 1h |
| src/core/pypi_uploader.py | PyPI上传器 | 1h |
| src/core/git_pusher.py | Git推送器 | 1h |
| src/core/deploy_verifier.py | 部署验证器 | 1h |
| src/core/state_updater.py | 状态更新器 | 1h |
| src/cli/deploy_commands.py | CLI命令 | 1h |
| tests/test_deployment_orchestrator.py | 单元测试 | 1h |
| tests/test_deployment_e2e.py | E2E测试 | 1h |

---

## 2. 技术架构

### 2.1 模块架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    oc-collab CLI                                 │
│                                                                 │
│   oc-collab deploy [OPTIONS]                                    │
│          │                                                      │
│          ▼                                                      │
│   ┌──────────────────────┐                                      │
│   │ DeploymentOrchestrator │                                    │
│   │     (部署编排器)      │                                    │
│   └──────────┬───────────┘                                      │
│              │                                                   │
│    ┌────────┼────────┬────────┬────────┬────────┬────────┐      │
│    ▼        ▼        ▼        ▼        ▼        ▼        ▼      │
│ ┌──────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐ │
│ │ Doc- │ │State- │ │ Version │ │Package │ │ PyPI  │ │ Git  │ │
│ │Checker│ │Checker│ │Manager │ │ Builder│ │Uploader│ │Pusher│ │
│ └───┬──┘ └───┬──┘ └────┬───┘ └────┬───┘ └────┬───┘ └──┬───┘ │
│     │        │         │          │          │         │      │
│     │        │         │          │          │         │      │
│     ▼        ▼         ▼          ▼          ▼         ▼      │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │                  StateUpdater                            │   │
│ │            (project_state.yaml)                          │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                    src/core/deploy_verifier.py                  │
│                         (发布验证)                               │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 模块 | 技术/库 | 版本 | 选型依据 |
|------|---------|------|----------|
| CLI框架 | Click | >=8.0 | 现有技术栈 |
| TOML解析 | tomllib | Python 3.11+ | pyproject.toml原生支持 |
| HTTP请求 | requests | >=2.0 | 现有依赖，PyPI API |
| 子进程 | subprocess | 标准库 | 执行shell命令 |
| Git操作 | GitPython | >=5.0 | 现有依赖 |

### 2.3 数据流图

#### 2.3.1 数据存储位置

| 数据类型 | 存储文件 | 格式 | 读取方 | 写入方 |
|----------|----------|------|--------|--------|
| 项目状态 | state/project_state.yaml | YAML | 所有Agent | DeploymentOrchestrator |
| 构建产物 | dist/*.whl, dist/*.tar.gz | 二进制 | PyPIUploader | PackageBuilder |
| 版本配置 | pyproject.toml | TOML | VersionManager | VersionManager |

#### 2.3.2 部署数据流

```
用户执行 oc-collab deploy
         │
         ▼
┌─────────────────────┐
│  1. DocChecker     │ ──▶ 检查 CHANGELOG.md, README.md
│  2. StateChecker   │ ──▶ 检查 testing.status: APPROVED
│  3. VersionManager │ ──▶ 读取/更新 pyproject.toml
│  4. PackageBuilder │ ──▶ python -m build → dist/
│  5. PyPIUploader   │ ──▶ twine upload dist/*
│  6. GitPusher      │ ──▶ git add/commit/tag/push
│  7. Verifier       │ ──▶ PyPI API 验证
│  8. StateUpdater   │ ──▶ 更新 project_state.yaml
└─────────────────────┘
```

---

## 3. 核心模块设计

### 3.1 DeploymentOrchestrator (部署编排器)

```python
class DeploymentOrchestrator:
    """部署编排器 - 协调部署全流程"""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        """
        Args:
            dry_run: 预览模式，不执行实际变更
            verbose: 输出详细日志
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.steps = []
        self.results = []

    def run(self, version: Optional[str] = None,
            skip_git: bool = False,
            skip_pypi: bool = False,
            verify_only: bool = False) -> dict:
        """
        执行完整部署流程

        Args:
            version: 指定版本号，None则自动读取
            skip_git: 跳过Git推送步骤
            skip_pypi: 跳过PyPI上传步骤
            verify_only: 仅执行验证

        Returns:
            部署结果字典
        """
        pass

    def add_step(self, step: "DeploymentStep"):
        """添加部署步骤"""
        pass

    def _execute_steps(self):
        """按顺序执行所有步骤"""
        pass
```

### 3.2 VersionManager (版本号管理器)

```python
class VersionManager:
    """版本号管理器 - 读取和更新版本号"""

    def __init__(self, pyproject_path: str = "pyproject.toml"):
        self.pyproject_path = pyproject_path

    def get_current_version(self) -> str:
        """读取当前版本号"""
        pass

    def update_version(self, new_version: str) -> bool:
        """
        更新版本号

        Args:
            new_version: 新版本号，如 "2.2.12"

        Returns:
            是否更新成功
        """
        pass

    def validate_version(self, version: str) -> tuple[bool, str]:
        """验证版本号格式"""
        pass
```

### 3.3 PackageBuilder (包构建器)

```python
class PackageBuilder:
    """包构建器 - 执行python -m build"""

    def __init__(self, dist_dir: str = "dist"):
        self.dist_dir = dist_dir

    def clean(self) -> bool:
        """清理旧的构建产物"""
        pass

    def build(self) -> bool:
        """执行构建"""
        pass

    def verify_build(self) -> tuple[bool, list[str]]:
        """
        验证构建产物

        Returns:
            (是否成功, 构建产物列表)
        """
        pass
```

### 3.4 PyPIUploader (PyPI上传器)

```python
class PyPIUploader:
    """PyPI上传器"""

    def __init__(self, dist_dir: str = "dist"):
        self.dist_dir = dist_dir

    def upload(self, dry_run: bool = False) -> tuple[bool, str]:
        """
        上传到PyPI

        Args:
            dry_run: 预览模式

        Returns:
            (是否成功, 消息)
        """
        pass

    def check_package_exists(self, package_name: str, version: str) -> bool:
        """检查包是否已存在"""
        pass
```

### 3.5 GitPusher (Git推送器)

```python
class GitPusher:
    """Git推送器"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = project_dir

    def commit_and_push(self, version: str, dry_run: bool = False) -> tuple[bool, str]:
        """
        执行git add, commit, tag, push

        Args:
            version: 版本号
            dry_run: 预览模式

        Returns:
            (是否成功, 消息)
        """
        pass

    def create_tag(self, version: str, dry_run: bool = False) -> tuple[bool, str]:
        """创建版本标签"""
        pass
```

### 3.6 Verifier (部署验证器)

```python
class DeployVerifier:
    """部署验证器"""

    def __init__(self, package_name: str = "opencode-collaboration"):
        self.package_name = package_name

    def verify_pypi(self, version: str) -> tuple[bool, dict]:
        """
        验证PyPI发布结果

        Returns:
            (是否成功, 验证结果详情)
        """
        pass

    def pip_install_test(self, version: str) -> tuple[bool, str]:
        """
        pip安装测试

        Returns:
            (是否成功, 消息)
        """
        pass
```

### 3.7 StateUpdater (状态更新器)

```python
class StateUpdater:
    """状态更新器"""

    def __init__(self, state_file: str = "state/project_state.yaml"):
        self.state_file = state_file

    def update_deployment_status(self, version: str,
                                 pypi_url: str,
                                 git_tag: str) -> bool:
        """
        更新部署状态

        Args:
            version: 版本号
            pypi_url: PyPI URL
            git_tag: Git标签

        Returns:
            是否更新成功
        """
        pass

    def read_state(self) -> dict:
        """读取当前状态"""
        pass
```

### 3.8 CLI命令设计

| 命令 | 函数 | 描述 | 工时 |
|------|------|------|------|
| `oc-collab deploy` | `deploy()` | 执行完整部署流程 | 1h |
| `oc-collab deploy --dry-run` | `dry_run=True` | 预览模式 | - |
| `oc-collab deploy --version <ver>` | `version=<ver>` | 指定版本号 | - |
| `oc-collab deploy --skip-git` | `skip_git=True` | 跳过Git推送 | - |
| `oc-collab deploy --skip-pypi` | `skip_pypi=True` | 跳过PyPI上传 | - |
| `oc-collab deploy --verify-only` | `verify_only=True` | 仅执行验证 | - |
| `oc-collab deploy --verbose` | `verbose=True` | 输出详细日志 | - |

---

## 4. 数据结构

### 4.1 project_state.yaml 部署状态Schema

```yaml
# state/project_state.yaml
v2.2.12:
  deployment:
    status: completed / pending / failed
    completed_at: "2026-02-14T22:00:00"
    version: "2.2.12"
    git_tag: v2.2.12
    pypi_url: "https://pypi.org/project/opencode-collaboration/2.2.12/"
    pypi_version: "2.2.12"
    agent_id: "2"
    steps:
      - step: doc_check
        status: passed
        timestamp: "2026-02-14T22:00:00"
      - step: state_check
        status: passed
        timestamp: "2026-02-14T22:00:01"
      # ... 其他步骤
```

### 4.2 pyproject.toml 版本号格式

```toml
[project]
name = "opencode-collaboration"
version = "2.2.12"  # 需更新的字段
```

### 4.3 部署结果响应格式

```json
{
  "success": true,
  "version": "2.2.12",
  "steps": [
    {
      "name": "doc_check",
      "status": "passed",
      "message": "All documents synchronized"
    }
  ],
  "pypi_url": "https://pypi.org/project/opencode-collaboration/2.2.12/",
  "git_tag": "v2.2.12"
}
```

---

## 5. 算法与逻辑

### 5.1 核心流程

```
开始
  │
  ▼
┌──────────────────┐
│  解析命令行参数    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  DocChecker      │──▶ 检查 CHANGELOG.md, README.md
│  (文档同步检查)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  StateChecker    │──▶ 检查 testing.status
│  (状态检查)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  VersionManager  │──▶ 读取/更新版本号
│  (版本号管理)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  PackageBuilder  │──▶ python -m build
│  (包构建)       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  PyPIUploader   │──▶ twine upload
│  (PyPI上传)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  GitPusher       │──▶ git add/commit/tag/push
│  (Git推送)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Verifier        │──▶ PyPI API 验证
│  (发布验证)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  StateUpdater    │──▶ 更新 project_state.yaml
│  (状态更新)      │
└────────┬─────────┘
         │
         ▼
结束
```

### 5.2 状态机

| 当前状态 | 事件 | 下一状态 |
|----------|------|----------|
| idle | 执行deploy | checking |
| checking | 检查通过 | building |
| checking | 检查失败 | failed |
| building | 构建成功 | uploading |
| building | 构建失败 | failed |
| uploading | 上传成功 | pushing |
| uploading | 上传失败 | failed |
| pushing | 推送成功 | verifying |
| pushing | 推送失败 | failed |
| verifying | 验证成功 | completed |
| verifying | 验证失败 | failed |

### 5.3 边界条件

| 边界条件 | 处理方式 |
|----------|----------|
| CHANGELOG.md/README.md 未同步 | 提示缺失文件，退出 |
| testing.status != APPROVED | 提示测试未完成，退出 |
| pyproject.toml 不存在 | 提示错误，退出 |
| 版本号格式无效 | 提示格式要求 |
| dist/ 目录为空 | 提示构建失败 |
| PyPI Token未配置 | 提示配置 ~/.pypirc |
| Git远程仓库无权限 | 提示权限错误 |
| 包已存在 | 提示版本冲突，建议递增 |
| 网络超时 | 重试3次，提示错误 |

---

## 6. API设计

### 6.1 内部CLI命令

| 命令 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `oc-collab deploy` | --dry-run, --version, --skip-git, --skip-pypi, --verify-only, --verbose | JSON | 执行部署 |
| `oc-collab deploy --dry-run` | 同上 | JSON | 预览模式 |

### 6.2 PyPI API

| 端点 | 方法 | 输入 | 输出 | 说明 |
|------|------|------|------|------|
| https://pypi.org/pypi/{package}/json | GET | - | JSON | 查询包信息 |

### 6.3 错误码

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 1001 | 文档未同步 | 提示缺失文件路径 |
| 1002 | 测试未完成 | 提示测试状态要求 |
| 2001 | 版本号格式错误 | 提示正确格式 (x.y.z) |
| 2002 | 版本冲突 | 提示已存在版本 |
| 3001 | PyPI Token缺失 | 提示配置 ~/.pypirc |
| 3002 | PyPI上传失败 | 显示错误详情 |
| 4001 | Git权限不足 | 提示检查远程仓库 |
| 4002 | Git推送失败 | 显示详细错误 |
| 5001 | 网络超时 | 建议重试 |

---

## 7. 错误处理

### 7.1 异常类型

| 异常类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| DeploymentError | 部署步骤失败 | 记录错误，中止部署 |
| VersionError | 版本号相关错误 | 提示用户 |
| BuildError | 包构建失败 | 显示构建日志 |
| UploadError | PyPI上传失败 | 显示错误信息 |
| GitError | Git操作失败 | 显示Git错误 |
| VerificationError | 验证失败 | 显示验证结果 |

### 7.2 错误恢复

| 错误场景 | 恢复方式 | 重试策略 |
|----------|----------|----------|
| 网络超时 | 重试 | 最多3次 |
| PyPI上传失败 | 重试 | 最多3次 |
| Git推送失败 | 手动确认 | 无自动重试 |

### 7.3 dry-run 模式

在 dry-run 模式下，所有步骤只显示不执行：

```bash
$ oc-collab deploy --dry-run

[DRY-RUN] 部署预览
版本: 2.2.12

步骤 1: DocChecker
  - [DRY-RUN] 检查 CHANGELOG.md
  - [DRY-RUN] 检查 README.md

步骤 2: StateChecker
  - [DRY-RUN] 检查 testing.status

步骤 3: VersionManager
  - [DRY-RUN] 读取当前版本: 2.2.11
  - [DRY-RUN] 更新版本: 2.2.12

步骤 4: PackageBuilder
  - [DRY-RUN] 清理 dist/ 目录
  - [DRY-RUN] 执行 python -m build

步骤 5: PyPIUploader
  - [DRY-RUN] 执行 twine upload dist/*

步骤 6: GitPusher
  - [DRY-RUN] git add pyproject.toml
  - [DRY-RUN] git commit -m "release: v2.2.12"
  - [DRY-RUN] git tag v2.2.12
  - [DRY-RUN] git push

步骤 7: Verifier
  - [DRY-RUN] 调用 PyPI API 验证

步骤 8: StateUpdater
  - [DRY-RUN] 更新 project_state.yaml

预览结束。执行 oc-collab deploy 以执行实际部署。
```

---

## 8. 测试策略

### 8.1 单元测试

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| VersionManager.get_current_version | 读取 pyproject.toml | 返回正确版本号 |
| VersionManager.update_version | 更新版本号 | 文件内容正确 |
| VersionManager.validate_version | 验证无效版本号 | 返回 False |
| PackageBuilder.clean | 清理 dist/ | 目录为空 |
| PackageBuilder.build | 执行构建 | 生成 .whl 和 .tar.gz |
| PyPIUploader.check_exists | 检查已存在包 | 返回 True |
| GitPusher.create_tag | 创建 Git 标签 | 标签创建成功 |
| DeployVerifier.verify_pypi | 验证 PyPI 发布 | 返回包信息 |
| StateUpdater.update | 更新状态文件 | 文件内容正确 |
| DeploymentOrchestrator.run | 完整部署流程 | 所有步骤成功 |

### 8.2 E2E测试

| 测试场景 | 测试步骤 | 验收标准 |
|----------|----------|----------|
| 完整部署 | 1. 执行 oc-collab deploy | 部署成功 |
| | 2. 检查 pyproject.toml | 版本号更新 |
| | 3. 检查 dist/ | 构建产物存在 |
| 预览模式 | 1. 执行 oc-collab deploy --dry-run | 只显示不执行 |
| | 2. 检查文件 | 无变更 |
| 仅验证 | 1. 执行 oc-collab deploy --verify-only | 显示验证结果 |
| 跳过步骤 | 1. 执行 oc-collab deploy --skip-git | Git步骤跳过 |
| | 2. 检查 PyPI | 上传成功 |

---

## 9. 签署确认

### Agent 2 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-14 | ✅ |

### Agent 1 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: APPROVED
