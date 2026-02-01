# State Validator 使用指南

**版本**: v1  
**创建日期**: 2026-02-01  
**模块**: src/core/state_validator.py

---

## 1. 概述

State Validator 是 oc-collab 系统的核心验证组件，负责验证 project_state.yaml 文件的结构是否符合 Schema 规范。

### 1.1 主要功能

- **结构验证**: 验证 State 文件的必填字段、数据类型
- **格式验证**: 验证 version、phase 等字段的格式
- **枚举值验证**: 验证 status、phase 等枚举字段的有效值
- **兼容性检测**: 检测 State 文件格式与代码期望的兼容性
- **错误建议**: 提供详细的错误信息和修复建议

### 1.2 核心类

| 类名 | 说明 |
|-----|------|
| `ValidationLevel` | 验证级别枚举 (ERROR, WARNING, INFO) |
| `ValidationResult` | 验证结果数据类 |
| `StateValidator` | 主验证器类 |

---

## 2. 快速开始

### 2.1 基本使用

```python
from src.core.state_validator import StateValidator

# 创建验证器
validator = StateValidator()

# 待验证的 State
state = {
    "version": "2.0.0",
    "project": {
        "name": "My Project",
        "type": "PYTHON",
        "phase": "development"
    },
    "requirements": [{"version": "v1", "status": "approved"}],
    "design": [{"version": "v1", "status": "completed"}],
    "test": {"status": "pending"},
    "development": {"status": "in_progress"},
    "deployment": {"status": "pending"}
}

# 执行验证
results = validator.validate(state)

# 检查结果
if validator.is_valid():
    print("✅ State 结构有效")
else:
    print(f"❌ 发现 {len(validator.get_errors())} 个错误")
    for result in results:
        print(result)
```

### 2.2 命令行使用

```bash
python -m src.core.state_validator state/project_state.yaml
```

---

## 3. ValidationLevel 验证级别

```python
from src.core.state_validator import ValidationLevel

# ERROR - 严重错误，State 无效
ValidationLevel.ERROR

# WARNING - 警告，建议修复
ValidationLevel.WARNING

# INFO - 信息性提示
ValidationLevel.INFO
```

---

## 4. ValidationResult 验证结果

### 4.1 属性

| 属性 | 类型 | 说明 |
|-----|------|------|
| `level` | ValidationLevel | 验证级别 |
| `field` | str | 字段名 |
| `message` | str | 错误信息 |
| `suggestion` | str | 修复建议 |

### 4.2 方法

```python
# 转换为字典
result.to_dict()
# 返回: {"level": "error", "field": "version", "message": "...", "suggestion": "..."}

# 字符串表示
str(result)
# 返回: "[ERROR] version: version 字段缺失\n  💡 在 state 文件开头添加 version: X.Y.Z"
```

---

## 5. StateValidator API

### 5.1 初始化

```python
validator = StateValidator(strict_mode=False)
```

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `strict_mode` | bool | False | 严格模式，增加更多验证规则 |

### 5.2 validate()

```python
results = validator.validate(state: Dict[str, Any]) -> List[ValidationResult]
```

验证 State 结构，返回验证结果列表。

### 5.3 is_valid()

```python
is_valid = validator.is_valid() -> bool
```

检查是否有错误级别的验证结果。

### 5.4 get_errors()

```python
errors = validator.get_errors() -> List[ValidationResult]
```

获取所有错误级别的验证结果。

### 5.5 get_warnings()

```python
warnings = validator.get_warnings() -> List[ValidationResult]
```

获取所有警告级别的验证结果。

### 5.6 check_compatibility()

```python
issues = validator.check_compatibility(state: Dict[str, Any]) -> List[ValidationResult]
```

检测 State 文件格式与代码期望是否兼容。

---

## 6. Schema 定义

### 6.1 支持的字段

| 字段 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| `version` | string | ✅ | 版本号，格式: X.Y.Z |
| `project` | dict | ✅ | 项目信息 |
| `requirements` | dict/list | ✅ | 需求列表 |
| `design` | dict/list | ✅ | 设计文档 |
| `test` | dict | ✅ | 测试状态 |
| `development` | dict | ✅ | 开发状态 |
| `deployment` | dict | ✅ | 部署状态 |
| `iteration` | dict | ❌ | 迭代信息 |
| `iterations` | dict | ❌ | 迭代历史 |

### 6.2 project 字段

```python
"project": {
    "name": str,           # 项目名称 (必填)
    "type": str,           # 项目类型 (必填)
    "phase": str           # 项目阶段 (必填)
}
```

**phase 有效值**: `unknown`, `requirements`, `design`, `development`, `testing`, `deployment`, `completed`

### 6.3 status 字段有效值

| 字段 | 有效值 |
|-----|--------|
| `test.status` | `pending`, `in_progress`, `passed`, `failed` |
| `development.status` | `pending`, `in_progress`, `completed` |
| `deployment.status` | `pending`, `in_progress`, `released` |

---

## 7. 错误处理示例

### 7.1 版本号缺失

```python
state = {"project": {...}}
validator.validate(state)

# 输出:
# [ERROR] version: version 字段缺失
#   💡 在 state 文件开头添加 version: X.Y.Z
```

### 7.2 无效的 phase

```python
state = {
    "version": "2.0.0",
    "project": {"name": "Test", "type": "PYTHON", "phase": "invalid_phase"}
}
validator.validate(state)

# 输出:
# [ERROR] project.phase: 无效的 phase 值: invalid_phase
#   💡 有效值: ['unknown', 'requirements', 'design', 'development', 'testing', 'deployment', 'completed']
```

### 7.3 字典格式 design（兼容性问题）

```python
state = {
    "version": "2.0.0",
    "project": {...},
    "design": {"status": "completed"}  # 旧格式
}
validator.check_compatibility(state)

# 输出:
# [WARNING] design: design 字段是字典格式，建议迁移到列表格式
#   💡 使用 StateMigrator 迁移到列表格式
```

---

## 8. 与 StateMigrator 集成

StateValidator 常与 StateMigrator 配合使用：

```python
from src.core.state_validator import StateValidator
from src.core.state_migrator import StateMigrator

# 创建迁移器
migrator = StateMigrator("state/project_state.yaml", dry_run=True)

# 执行迁移
success, migrated_state = migrator.migrate(old_state)

if success:
    # 验证迁移后的 State
    validator = StateValidator()
    results = validator.validate(migrated_state)
    
    if validator.is_valid():
        print("✅ 迁移成功，State 结构有效")
    else:
        print("⚠️  迁移成功，但 State 结构存在问题")
```

---

## 9. 测试覆盖

### 9.1 测试文件

- `tests/test_state_validator.py` - 单元测试

### 9.2 测试用例

| 测试类 | 测试用例数 | 说明 |
|-------|----------|------|
| TestStateValidatorVersion | 3 | version 格式验证 |
| TestStateValidatorProject | 3 | project 字段验证 |
| TestStateValidatorRequirements | 2 | requirements 字段验证 |
| TestStateValidatorDesign | 2 | design 字段验证 |
| TestStateValidatorCompatibility | 2 | 兼容性检测 |
| TestStateValidatorErrorMessages | 1 | 错误信息完整性 |
| TestStateValidatorEdgeCases | 4 | 边界情况 |
| TestValidationResult | 1 | ValidationResult 类 |

**总测试用例**: 18+

### 9.3 运行测试

```bash
# 运行所有测试
python3 -m pytest tests/test_state_validator.py -v

# 运行特定测试类
python3 -m pytest tests/test_state_validator.py::TestStateValidatorVersion -v

# 生成覆盖率报告
python3 -m pytest tests/test_state_validator.py --cov=src.core.state_validator --cov-report=html
```

---

## 10. 常见问题

### Q1: 验证通过但缺少 project.name

`project.name` 是可选字段，缺失时会有 WARNING 级别的提示，不会阻止验证通过。

### Q2: design 字段支持哪些格式

支持两种格式：
- 列表格式 (推荐): `[{"version": "v1", "status": "completed"}]`
- 字典格式 (兼容旧版本): `{"status": "completed"}`

### Q3: 如何跳过某些验证

目前不支持跳过特定验证。如有需要，可以继承 StateValidator 并重写对应方法。

### Q4: 严格模式有什么不同

`strict_mode=True` 时会启用更多验证规则，目前保留用于未来扩展。

---

## 11. 相关文件

| 文件 | 说明 |
|-----|------|
| `src/core/state_validator.py` | 验证器实现 |
| `src/core/state_migrator.py` | 版本迁移器 |
| `tests/test_state_validator.py` | 单元测试 |
| `docs/01-requirements/requirements_v2.1.0.md` | 需求文档 |

---

**文档版本**: v1  
**最后更新**: 2026-02-01
