# 详细设计文档：智能同步与自动文档更新

## 文档信息

| 项目 | 内容 |
|------|------|
| 设计ID | DES-AUTO-SYNC-001 |
| 需求ID | REQ-AUTO-SYNC-001 |
| 版本 | v1 |
| 状态 | 待评审 |
| 创建日期 | 2026-01-31 |

## 1. 系统架构

### 1.1 组件图

```
┌─────────────────────────────────────────────────────────────┐
│                    oc-collab CLI                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ 智能重试模块  │  │ 文档自动同步  │  │   Git Helper    │  │
│  │ (AutoRetry)  │  │ (AutoDocs)   │  │                 │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│         └─────────────────┴────────────────────┘            │
│                           │                                │
│                   ┌───────▼───────┐                        │
│                   │  配置管理器    │                        │
│                   │ (Config)      │                        │
│                   └───────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 类图

```python
class AutoRetryConfig:
    """智能重试配置"""
    max_retries: int           # 最大重试次数
    retry_interval: int        # 重试间隔（秒）
    exponential_backoff: bool  # 是否启用指数退避
    max_interval: int          # 最大间隔（秒）

class AutoRetry:
    """智能重试器"""
    config: AutoRetryConfig
    git_helper: GitHelper
    
    def push_with_retry(message: str) -> bool
    def pull_with_retry() -> bool
    def _should_retry(error: Exception) -> bool
    def _calculate_delay(attempt: int) -> int

class AutoDocsConfig:
    """文档自动同步配置"""
    enabled: bool              # 是否启用
    update_changelog: bool     # 更新变更记录
    update_manual: bool        # 更新使用手册
    update_tests: bool         # 更新测试用例
    require_confirm: bool      # 是否需要确认（重大变更）

class AutoDocs:
    """文档自动同步器"""
    config: AutoDocsConfig
    project_path: Path
    
    def detect_changes() -> List[str]
    def update_changelog(change_type: str, message: str)
    def update_manual(command: str)
    def update_tests(command: str)
    def preview_updates() -> str
    def apply_updates() -> bool
```

---

## 2. 智能重试机制详细设计

### 2.1 可重试错误类型

| 错误类型 | 错误码/关键词 | 是否重试 |
|---------|--------------|---------|
| 网络超时 | `ConnectionError`, `Timeout` | ✓ |
| 网络不可达 | `NetworkUnreachable` | ✓ |
| HTTP 5xx | 500, 502, 503, 504 | ✓ |
| HTTP 429 | 429 (Too Many Requests) | ✓ |
| Git 锁等待 | `Waiting for lock` | ✓ |
| 认证失败 | `Authentication failed` | ✗ |
| 权限拒绝 | `Permission denied` | ✗ |
| 冲突解决失败 | `CONFLICT` | ✗ |
| 分支不存在 | `branch not found` | ✗ |

### 2.2 重试策略

#### 2.2.1 简单重试

```python
# 固定间隔
retry_interval = 30  # 秒
max_retries = 10
```

#### 2.2.2 指数退避（推荐）

```python
# 间隔序列: 30, 60, 120, 240, 480...
delay = min(retry_interval * (2 ** attempt), max_interval)
```

### 2.3 进度反馈

```
[RETRY 3/10] 推送到 GitHub...
等待 60 秒后重试...
✓ 推送成功
```

---

## 3. 文档自动同步详细设计

### 3.1 变更检测规则

| 代码变更 | 影响文档 |
|---------|---------|
| `src/cli/main.py` 新增命令 | 使用手册、测试用例、变更记录 |
| `src/core/git.py` 修改 | 使用手册、变更记录 |
| `src/core/*.py` 修改 | 变更记录 |
| `docs/*.md` 修改 | 变更记录 |
| `tests/test_e2e.py` 修改 | 测试用例文档、变更记录 |

### 3.2 文档更新模板

#### 3.2.1 变更记录更新

```markdown
## [v1.2] - YYYY-MM-DD

### 新功能
- 新增 `auto-sync` 命令 (#ID)

### 改进
- 提升同步稳定性 (#ID)

### 修复
- 修复配置兼容性问题 (#ID)

### 测试
- 新增端到端测试用例 (#ID)
```

#### 3.2.2 使用手册更新

当检测到 CLI 命令变更时，自动更新：

```markdown
### 4.X [命令名] - [功能描述]

[命令格式]
[参数说明]
[使用示例]
```

---

## 4. 配置文件

### 4.1 自动同步配置

```yaml
# state/project_state.yaml

auto_sync:
  enabled: true
  
  retry:
    max_retries: 10           # 最大重试次数
    retry_interval: 30        # 基础间隔（秒）
    exponential_backoff: true  # 启用指数退避
    max_interval: 300         # 最大间隔（秒）
  
  docs:
    enabled: true             # 启用文档自动同步
    update_changelog: true    # 自动更新变更记录
    update_manual: true       # 自动更新使用手册
    update_tests: false       # 不自动更新测试用例
    require_confirm: true     # 重大变更需要确认
```

---

## 5. 接口设计

### 5.1 AutoRetry 类

```python
class AutoRetry:
    """智能重试器"""
    
    def __init__(self, project_path: str, config: Optional[AutoRetryConfig] = None):
        """初始化"""
        self.git_helper = GitHelper(project_path)
        self.config = config or AutoRetryConfig()
    
    def push_with_retry(self, message: str, remote: str = "all") -> Dict[str, Any]:
        """
        带重试的推送
        
        Args:
            message: 提交信息
            remote: 远程仓库（默认 all）
        
        Returns:
            {
                "success": bool,
                "remotes": List[str],  # 成功推送的远程
                "attempts": int,        # 重试次数
                "duration": int         # 总耗时（秒）
            }
        """
        pass
    
    def _should_retry(self, error: Exception) -> bool:
        """判断是否应该重试"""
        pass
    
    def _calculate_delay(self, attempt: int) -> int:
        """计算延迟时间"""
        pass
```

### 5.2 AutoDocs 类

```python
class AutoDocs:
    """文档自动同步器"""
    
    def __init__(self, project_path: str, config: Optional[AutoDocsConfig] = None):
        """初始化"""
        self.project_path = Path(project_path)
        self.config = config or AutoDocsConfig()
    
    def detect_changes(self) -> Dict[str, List[str]]:
        """
        检测代码变更影响
        
        Returns:
            {
                "commands": [...],  # 受影响的命令
                "modules": [...],   # 受影响的模块
                "docs": [...]       # 需要更新的文档
            }
        """
        pass
    
    def update_changelog(self, change_type: str, message: str) -> bool:
        """更新变更记录"""
        pass
    
    def preview_updates(self) -> str:
        """预览待更新内容"""
        pass
    
    def apply_updates(self, confirmed: bool = False) -> Dict[str, bool]:
        """应用更新"""
        pass
```

---

## 6. 命令行接口

### 6.1 新增命令

#### 6.1.1 `oc-collab sync --retry`

```bash
oc-collab sync --retry [OPTIONS]
```

**选项**：
| 选项 | 说明 |
|-----|------|
| `--max-retries, -n` | 最大重试次数（默认 10） |
| `--interval, -i` | 重试间隔（秒，默认 30） |
| `--no-backoff` | 禁用指数退避 |

**示例**：
```bash
# 带重试的同步
oc-collab sync --retry

# 自定义重试参数
oc-collab sync --retry --max-retries 20 --interval 60
```

#### 6.1.2 `oc-collab docs --auto`

```bash
oc-collab docs --auto [OPTIONS]
```

**选项**：
| 选项 | 说明 |
|-----|------|
| `--preview, -p` | 预览待更新内容 |
| `--apply, -a` | 应用更新 |
| `--check` | 检查需要更新的文档 |

**示例**：
```bash
# 预览文档更新
oc-collab docs --auto --preview

# 应用文档更新
oc-collab docs --auto --apply

# 检查需要更新的文档
oc-collab docs --auto --check
```

---

## 7. 错误处理

### 7.1 错误码

| 错误码 | 说明 |
|-------|------|
| ERR-001 | 重试次数耗尽 |
| ERR-002 | 不可恢复的错误 |
| ERR-003 | 文档更新失败 |
| ERR-004 | 配置文件不存在 |

### 7.2 恢复策略

| 错误类型 | 恢复策略 |
|---------|---------|
| 网络超时 | 重试 |
| 认证失败 | 提示用户检查凭据 |
| 文档冲突 | 提示用户手动解决 |

---

## 8. 测试用例

### 8.1 单元测试

| 测试项 | 输入 | 预期输出 |
|-------|------|---------|
| 重试成功 | 网络超时 | 最终成功 |
| 重试耗尽 | 连续失败 10 次 | 返回失败 |
| 指数退避 | 3 次失败 | 间隔递增 |
| 文档检测 | 代码变更 | 正确识别影响范围 |
| 变更记录更新 | 提交信息 | 正确追加条目 |

### 8.2 集成测试

| 测试项 | 说明 |
|-------|------|
| sync --retry | 测试完整重试流程 |
| docs --auto | 测试完整文档同步流程 |

---

## 9. 实施计划

| 阶段 | 任务 | 优先级 |
|------|------|--------|
| 1 | 实现 AutoRetry 核心逻辑 | P0 |
| 2 | 实现 AutoDocs 核心逻辑 | P1 |
| 3 | 集成到 CLI | P0 |
| 4 | 编写测试用例 | P1 |
| 5 | 更新文档 | P1 |

---

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| v1 | 2026-01-31 | Agent 1 | 初始设计 |
