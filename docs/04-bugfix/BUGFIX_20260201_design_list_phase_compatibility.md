# Bug 总结与测试覆盖

## 问题 1：'list' object has no attribute 'get'

### 根因分析
**问题**：`signoff.py` 的 `can_sign()` 方法假设 `design` 字段是字典，但实际可能是列表。

**触发场景**：
- `financial_case_generator_system` 项目的 `state.yaml` 中 `design` 字段是列表
- 每个设计文档作为列表元素，包含 `version`、`status`、`pm_signoff` 等字段
- 代码执行 `stage_data.get("status", "")` 时，`stage_data` 是列表而非字典

```yaml
design:
  - version: TD-2026-02-01-001    # ← 列表
    status: completed
    pm_signoff: true
```

### 修复方案
添加 `_get_stage_data()` 方法处理两种数据结构：

```python
def _get_stage_data(self, stage: str, state: dict) -> dict:
    """获取阶段数据（处理 design 列表的情况）。"""
    config = self.STAGE_CONFIG.get(stage, {})
    status_field = config.get("status_field", stage)
    stage_data = state.get(status_field, {})
    
    if stage == "design" and isinstance(stage_data, list):
        for doc in stage_data:
            if isinstance(doc, dict) and doc.get("status") in ["in_progress", "completed", "approved"]:
                return doc
        return stage_data[0] if stage_data else {}
    
    return stage_data if isinstance(stage_data, dict) else {}
```

---

## 问题 2：状态显示 phase: unknown

### 根因分析
**问题**：`oc-collab project status` 显示 `unknown`，因为工具读取错误的 `phase` 路径。

**触发场景**：
- `financial_case_generator_system` 使用 `project.phase` 结构
- 工具代码期望根级 `phase` 字段
- 不同项目模板使用了不同的 state 结构

```yaml
# 错误读取
state.get("phase", "未知")  # → None，返回 "unknown"

# 正确结构
project:
  phase: development    # ← phase 在这里
```

### 修复方案
优先读取 `project.phase`，fallback 到根级：

```python
project_info = state.get("project", {})
current_phase = project_info.get("phase") or state.get("phase", "未知")
```

---

## 经验总结

### 1. State 数据结构不一致问题
| 项目/版本 | phase 位置 | design 格式 |
|-----------|-----------|------------|
| 旧项目 | `project.phase` | 列表 |
| 新项目 | `root.phase` | 字典 |

**教训**：代码需要兼容两种结构，不能假设单一格式。

### 2. 测试覆盖建议
1. **数据结构兼容性测试**
   - 测试 `phase` 在 `project` 下 vs 根级
   - 测试 `design` 是列表 vs 字典
   - 测试空列表、缺失字段等边界情况

2. **集成测试**
   - 使用真实项目 state 文件进行测试
   - 测试不同项目模板的 state 结构

3. **Schema 验证**
   - 考虑添加 JSON Schema 验证 state 文件结构
   - 在工具启动时检查兼容性

### 3. 防御性编程
- 使用 `isinstance()` 检查数据类型
- 提供合理的默认值
- 使用 `.get()` 方法替代直接访问

---

## 测试用例

见 `tests/test_state_structure_compatibility.py`
