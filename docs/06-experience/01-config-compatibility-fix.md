# 经验文档：项目配置兼容性问题修复

## 问题描述

在 `financial_case_generator_system` 项目中运行 `oc-collab status` 命令时，出现以下错误：

```
项目状态
错误: 'project_name'
```

### 问题根因

`oc-collab` CLI 的 `status_command` 函数直接从 `state["metadata"]["project_name"]` 和 `state["metadata"]["project_type"]` 读取字段，没有进行空值检查和容错处理。

同时，`financial_case_generator_system` 的 `state/project_state.yaml` 配置文件结构与 CLI 期望的结构不一致：
- 缺少 `metadata.project_name` 字段
- 缺少 `metadata.project_type` 字段
- 项目名称存储在 `project.name` 而非 `metadata.project_name`

## 问题影响

1. **用户体验差**：错误信息不明确，用户无法快速定位问题
2. **兼容性差**：无法处理不同结构的配置文件
3. **健壮性不足**：任何字段缺失都会导致命令完全失败

## 解决方案

### 1. CLI 容错修复 (`src/cli/main.py`)

修改 `status_command` 函数，增加以下处理逻辑：

- 使用 `.get()` 方法安全读取字段
- 支持从 `metadata` 或 `project` 两种结构读取
- 缺失字段时显示默认值而非报错
- 添加 `KeyError` 专用异常处理

```python
# 修复前 - 直接访问导致 KeyError
table.add_row("项目名称", state["metadata"]["project_name"])
table.add_row("项目类型", state["metadata"]["project_type"])

# 修复后 - 安全访问 + 兼容旧结构
metadata = state.get("metadata", {})
project_info = state.get("project", {})

project_name = metadata.get("project_name") or project_info.get("name", "未配置")
project_type = metadata.get("project_type") or project_info.get("type", "未知")

table.add_row("项目名称", project_name)
table.add_row("项目类型", project_type)
```

### 2. 临时配置文件修复

为 `financial_case_generator_system` 添加缺失字段：

```yaml
metadata:
  project_name: "金融案件测试数据生成系统"
  project_type: "PYTHON"
  ...
```

## 经验总结

### 问题分类

| 问题类型 | 描述 | 解决方案 |
|---------|------|---------|
| 健壮性问题 | 缺乏空值检查 | 使用 `.get()` 安全访问 |
| 兼容性问题 | 配置文件结构不一致 | 支持多结构兼容读取 |
| 异常处理 | 未区分错误类型 | 添加 KeyError 专用处理 |

### 设计原则

1. **防御性编程**：始终假设输入数据可能不完整
2. **向后兼容**：支持新旧配置文件结构
3. **友好错误**：提供清晰的错误提示和默认值

### 后续改进建议

1. 添加配置文件验证命令：`oc-collab validate`
2. 自动补全缺失字段：`oc-collab init --fix`
3. 统一配置文件模板和版本管理

## 日期

2026-01-31

---

# 智能重试与自动文档同步功能

## 功能描述

新增两个自动化功能：
1. **智能重试机制** - Git 操作失败时自动重试直到成功
2. **自动文档同步** - 代码变更时自动更新相关文档

## 需求与设计

- **需求文档**: `docs/01-requirements/requirements_auto_features_v1.md`
- **设计文档**: `docs/02-design/detailed_design_auto_features_v1.md`

## 新增命令

### 1. `oc-collab sync --retry` - 智能同步

```bash
# 启用智能重试
oc-collab sync --retry

# 自定义重试参数
oc-collab sync --retry --max-retries 20 --interval 60
```

### 2. `oc-collab push --retry` - 智能推送

```bash
# 带智能重试的推送
oc-collab push --retry -m "feat: 新功能"
```

### 3. `oc-collab docs` - 文档自动同步

```bash
# 检查需要更新的文档
oc-collab docs check

# 预览更新
oc-collab docs preview

# 应用更新
oc-collab docs apply -m "docs: 更新文档"
```

## 实现原理

### AutoRetry 核心逻辑

```python
class AutoRetry:
    def push_with_retry(self, message: str, remotes: List[str]) -> Dict:
        # 1. 首次尝试推送
        # 2. 失败时检查错误类型
        # 3. 可重试错误：等待后重试
        # 4. 不可重试错误：立即返回失败
        # 5. 达到最大重试次数：返回失败
```

### AutoDocs 核心逻辑

```python
class AutoDocs:
    def detect_changes(self) -> Dict:
        # 1. 获取变更文件列表
        # 2. 匹配文件与文档映射
        # 3. 返回影响范围

    def update_changelog(self, change_type: str, message: str):
        # 1. 读取变更记录
        # 2. 追加新条目
        # 3. 保存
```

## 相关文件

- 核心实现：`src/core/auto_retry.py`
- 核心实现：`src/core/auto_docs.py`
- CLI 命令：`src/cli/main.py`
- 测试用例：`tests/test_e2e.py`
- 使用手册：`docs/使用手册.md`
- 变更记录：`docs/04-changelog/change_log.md`

## 文档更新清单

| 文档 | 状态 | 说明 |
|------|------|------|
| `docs/04-changelog/change_log.md` | ✅ 已更新 | v1.2 新增功能 |
| `docs/使用手册.md` | ✅ 已更新 | 4.7-4.9 章节 |
| `tests/test_e2e.py` | ✅ 已更新 | 新增测试类 |
| `docs/01-requirements/requirements_auto_features_v1.md` | ✅ 已创建 | 需求文档 |
| `docs/02-design/detailed_design_auto_features_v1.md` | ✅ 已创建设计文档 |

## 日期

2026-01-31
