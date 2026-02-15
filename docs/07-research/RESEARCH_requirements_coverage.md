# Research: 需求覆盖率指标 PoC

**目标**: 确保需求文档中的功能描述在 E2E 测试中得到覆盖

**日期**: 2026-02-15
**状态**: 🔬 Researching → ⚠️ 遇到障碍

---

## 1. 问题背景

### 当前情况

| 指标 | 状态 |
|------|------|
| 代码覆盖率 | ✅ 已实现 (≥80%) |
| 测试通过率 | ✅ 100% |
| 需求覆盖率 | ❌ 未实现 |

### 痛点

```
需求文档: "oc-collab deploy full 执行完整部署流程"
    ↓
测试: 只验证命令能执行
    ↓
问题: 是否真正覆盖了"完整部署流程"的所有步骤？
```

---

## 2. PoC 执行结果

### 运行命令

```bash
python scripts/requirements_coverage_poc.py
```

### 输出结果

```
📄 扫描需求文档...
  requirements_v2.2.0.md: 26 个命令
  requirements_v2.2.12.md: 8 个命令
  ...

🧪 扫描测试文件...
  test_e2e_v221.py: 0 个命令
  test_e2e.py: 0 个命令
  ...

📈 覆盖率报告
  需求命令总数: 107
  已覆盖: 0
  未覆盖: 107
  覆盖率: 0.0%
```

### ⚠️ 关键发现

**问题：需求与测试不在同一抽象级别**

```
需求文档层 (CLI):
  `oc-collab todowrite`
  `oc-collab deploy full`

测试文件层 (内部函数):
  StateManager.initialize_project()
  SignoffRecordManager.save_signoff()
  AutoGitSyncEngine.detect_changes()
```

**分析：**
- 需求文档描述的是 CLI 命令
- E2E 测试直接调用内部函数
- 两者无法通过字符串匹配关联

---

## 3. 问题根因

### 3.1 架构分层

```
┌─────────────────────────────────────────┐
│  用户层 (CLI)                           │
│  `oc-collab todowrite --content "test"`│
└─────────────────────────────────────────┘
                 ↓ 调用
┌─────────────────────────────────────────┐
│  内部函数层 (E2E 测试)                  │
│  StateManager, SignoffRecordManager    │
└─────────────────────────────────────────┘
```

### 3.2 测试方式差异

| 测试类型 | 调用方式 | 可提取性 |
|---------|---------|---------|
| CLI 测试 | `runner.invoke(command)` | ✅ 可提取 |
| E2E 测试 | `StateManager.method()` | ❌ 不可提取 |

---

## 4. 改进方案

### 方案 A：功能模块映射

建立需求与模块的映射关系：

```yaml
# requirements_modules_mapping.yaml
requirements_v2.2.12.md:
  - "部署自动化CLI"
  modules:
    - deployment_orchestrator
    - version_manager
    - package_builder
    - pypi_uploader
    - git_pusher
    - deploy_verifier
    - state_updater
```

测试检查：

```python
def check_module_coverage():
    """检查测试是否覆盖了需求中的模块"""
    required_modules = load_required_modules()
    tested_modules = set()

    for test_file in glob("tests/*.py"):
        tested_modules.update(extract_modules(test_file))

    uncovered = required_modules - tested_modules
    return uncovered
```

### 方案 B：测试用例标注

在测试中添加需求关联标注：

```python
@pytest.mark.requirement("F-DEPLOY-001")
@pytest.mark.module("deployment_orchestrator")
def test_deploy_full_workflow():
    """测试完整部署流程"""
    ...
```

覆盖率检查：

```bash
pytest --collect-only -q | grep "requirement"
```

### 方案 C：测试日志追踪

在测试执行时记录测试的功能：

```python
# conftest.py

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    outcome = yield
    # 记录测试覆盖的功能
    test_coverage[item.name] = {
        "requirements": getattr(item, 'pytestrequirement', []),
        "modules": getattr(item, 'pytestmodule', []),
    }
```

---

## 5. PoC 代码

### 文件: `scripts/requirements_coverage_poc.py`

已实现，但发现架构分层问题。

### 发现的问题

1. **抽象级别不匹配**
   - 需求描述 CLI 命令
   - 测试使用内部函数

2. **正则提取失效**
   - `runner.invoke()` 模式在部分测试中存在
   - 但大部分 E2E 测试直接调用内部函数

3. **需要人工映射**
   - 需求 ↔ 模块 ↔ 测试 的关系需要维护

---

## 6. 待解决问题

| 问题 | 说明 | 解决方案 |
|------|------|---------|
| 抽象级别 | CLI vs 内部函数 | 改用模块映射 |
| 匹配方式 | 字符串匹配失效 | 人工标注 |
| 维护成本 | 映射需要同步更新 | 测试标注 + Git Hook |

---

## 7. 下一步

### 推荐方案：测试用例标注

1. **修改测试框架**：在 pytest 添加 requirement 标记
2. **生成覆盖率报告**：基于标注计算覆盖率
3. **集成到 CI**：每次 PR 检查覆盖率

### 备选方案：模块覆盖

1. **建立映射表**：需求 ↔ 模块
2. **分析测试导入**：哪些模块被测试导入
3. **计算模块覆盖**

---

## 8. 结论

**当前 PoC 方法（命令匹配）不可行**，因为架构分层导致无法直接匹配。

**新思路：LLM 语义匹配**

### 传统方法（失败）

```
需求: "oc-collab deploy full 执行完整部署"
测试: "def test_deploy_full(): ..."
    ↓ 正则匹配
结果: 无法匹配（抽象级别不同）
```

### LLM 方法（重新设计）

```
需求（自然语言）:
"部署自动化CLI：执行完整的部署流程，包括构建、上传、Git推送"

测试代码:
"def test_deploy_full():
    result = runner.invoke(deploy_full, ['--dry-run'])
    assert result.exit_code == 0"

    ↓ LLM 语义理解
判断: "这段测试覆盖了部署自动化CLI的需求"
```

### 实现方案

```python
# llm_coverage_poc.py

import json
from pathlib import Path

# 1. 提取需求的功能描述
def extract_requirements():
    """从需求文档提取功能描述"""
    # 使用正则提取带描述的完整需求
    pass

# 2. 提取测试代码片段
def extract_test_snippets():
    """提取测试函数的代码"""
    pass

# 3. LLM 判断覆盖率
def llm_check_coverage(requirement: str, test_code: str) -> bool:
    """使用LLM判断测试是否覆盖需求"""
    prompt = f"""
需求描述：{requirement}

测试代码：
{test_code}

请判断：这个测试代码是否覆盖了这个需求？
只回答 "是" 或 "否"。
"""
    response = llm.chat(prompt)
    return "是" in response

# 4. 计算覆盖率
def calculate_coverage():
    requirements = extract_requirements()
    tests = extract_test_snippets()
    
    covered = 0
    for req in requirements:
        for test in tests:
            if llm_check_coverage(req, test):
                covered += 1
                break
    
    return covered / len(requirements)
```

---

## 9. LLM 语义匹配方案（最终方案）

### 9.1 方案设计

**核心思路：**
- 不依赖正则匹配或字符串匹配
- 直接使用 LLM 的语义理解能力
- LLM 可以理解"自然语言需求"和"测试代码"的语义关系

**架构：**

```
┌─────────────────────────────────────────────────────────┐
│                    LLM (oc-collab)                      │
│                                                          │
│  需求: "部署自动化CLI：实现完整部署流程"                  │
│      ↓ 语义理解                                        │
│  测试: "def test_deploy(): ..."                        │
│      ↓ 语义判断                                        │
│  结果: "覆盖" / "不覆盖"                               │
└─────────────────────────────────────────────────────────┘
```

### 9.2 实现方式

**方式 A：运行时分析（当前我作为 LLM）**

用户在开发过程中直接问我：
```
用户: 帮我检查需求覆盖率
我(LLM): 分析需求文档和测试代码，输出覆盖报告
```

**方式 B：CLI 命令（设计中的功能）**

```bash
oc-collab requirements coverage
```

### 9.3 PoC 验证

**手动测试（我作为 LLM）：**

需求：
> F-DEPLOY-001: 部署自动化CLI
> 提供`oc-collab deploy`命令，实现部署全流程自动化

测试代码：
> test_deployment_modules.py 包含 VersionManager, PackageBuilder, PyPIUploader, GitPusher 测试

LLM 判断结果：
| 需求子项 | 是否覆盖 |
|---------|---------|
| 版本号管理 | ✅ TestVersionManager |
| 包构建 | ✅ TestPackageBuilder |
| PyPI发布 | ✅ TestPyPIUploader |
| Git推送 | ✅ TestGitPusher |
| 部署前检查 | ❌ 缺失 |

### 9.4 优势

| 优势 | 说明 |
|------|------|
| **语义理解** | 理解自然语言需求，不依赖格式 |
| **无需 API** | 直接使用 oc-collab 的 LLM 能力 |
| **灵活判断** | 可处理模糊需求和间接覆盖 |
| **可解释** | 可以说明为什么覆盖/不覆盖 |

### 9.5 待设计功能

**CLI 命令设计：**

```bash
# 检查当前项目需求覆盖率
oc-collab requirements coverage

# 输出示例：
# 📈 需求覆盖率报告
# 总需求: 15
# 已覆盖: 12
# 覆盖率: 80%
# 
# 未覆盖:
# - F-DEPLOY-002: 部署验证
# - F-AUTO-002: 自动重试
```

---

## 10. 结论

| 方案 | 可行性 | 说明 |
|------|--------|------|
| 命令匹配 | ❌ 不可行 | 架构分层导致无法匹配 |
| 模块映射 | ⚠️ 可行 | 需要维护映射表 |
| 测试标注 | ⚠️ 可行 | 需要改造测试代码 |
| **LLM 语义匹配** | ✅ 可行 | 直接使用 LLM 能力，无需额外实现 |

**最终推荐：LLM 语义匹配方案**

---

## 11. 下一步

- [ ] 在 Research 文档中记录 LLM 方案 ✅
- [ ] 设计 CLI 命令 `oc-collab requirements coverage`
- [ ] 实现功能并集成到 oc-collab
