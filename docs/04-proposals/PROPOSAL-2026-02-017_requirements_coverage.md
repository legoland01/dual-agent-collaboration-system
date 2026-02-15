# PROPOSAL-2026-02-017: 需求覆盖率检查功能

**Proposal ID**: PROPOSAL-2026-02-017
**标题**: 需求覆盖率自动检查功能
**类型**: 新功能 (Feature)
**状态**: DRAFT
**创建日期**: 2026-02-15
**作者**: Agent 1 (产品经理)

---

## 1. 概述

### 1.1 问题背景

当前项目有代码覆盖率指标（≥80%），但没有需求覆盖率指标。

| 指标 | 状态 |
|------|------|
| 代码覆盖率 | ✅ ≥80% |
| 测试通过率 | ✅ 100% |
| 需求覆盖率 | ❌ 未实现 |

### 1.2 问题描述

- 需求文档中的功能描述可能在测试中未覆盖
- 无法量化需求实现的完整度
- 缺乏自动化的需求-测试追溯机制

---

## 2. 目标

### 2.1 核心目标

实现需求覆盖率自动检查功能，确保需求文档中的功能描述在测试中得到覆盖。

### 2.2 量化指标

```
需求覆盖率 = (已验证的需求数 / 总需求数) × 100%
```

### 2.3 成功标准

- [ ] 提供 `oc-collab requirements coverage` 命令
- [ ] 自动分析需求文档和测试代码
- [ ] 输出覆盖率报告
- [ ] 集成到发布流程

---

## 3. 方案设计

### 3.1 核心技术：LLM 语义匹配

**核心思路：**
- 使用 oc-collab 内置的 LLM 能力
- 直接理解"自然语言需求"和"测试代码"的语义
- 不依赖正则匹配、模块映射或测试标注

**实现方式：**

```python
# src/core/requirements_coverage.py

class RequirementsCoverageChecker:
    """需求覆盖率检查器"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
    
    def check_coverage(self, requirements_doc: str, test_code: str) -> bool:
        """
        使用 LLM 判断测试是否覆盖需求
        
        Args:
            requirements_doc: 需求文档内容
            test_code: 测试代码
            
        Returns:
            bool: 是否覆盖
        """
        prompt = f"""
你是一个测试覆盖率分析专家。

需求文档：
{requirements_doc}

测试代码：
{test_code}

请判断：这个测试代码是否覆盖了这个需求？

判断标准：
1. 测试代码是否验证了需求中描述的功能
2. 测试代码是否覆盖了需求的验收标准

只回答 "是" 或 "否"，不需要解释。
"""
        response = self.llm_client.chat(prompt)
        return "是" in response
```

### 3.2 CLI 命令设计

```bash
# 检查当前项目需求覆盖率
oc-collab requirements coverage

# 输出报告
oc-collab requirements coverage --report

# 详细模式
oc-collab requirements coverage --verbose
```

### 3.3 输出格式

```
╔════════════════════════════════════════════════════════╗
║           📈 需求覆盖率报告                             ║
╠════════════════════════════════════════════════════════╣
║  项目: dual-agent-collaboration-system               ║
║  需求总数: 15                                        ║
║  已覆盖: 12                                           ║
║  未覆盖: 3                                            ║
║  覆盖率: 80%                                          ║
╠════════════════════════════════════════════════════════╣
║  ❌ 未覆盖的需求:                                      ║
║     - F-DEPLOY-002: 部署验证自动化                    ║
║     - F-AUTO-002: 自动重试机制                        ║
║     - F-RETRY-001: 错误恢复                           ║
╚════════════════════════════════════════════════════════╝
```

---

## 4. 实现计划

### 4.1 Phase 1: 核心模块

| 任务 | 说明 | 状态 |
|------|------|------|
| 创建 RequirementsCoverageChecker 类 | LLM 语义匹配核心逻辑 | ⏳ |
| 实现需求提取方法 | 从文档提取功能描述 | ⏳ |
| 实现测试提取方法 | 从测试文件提取代码 | ⏳ |
| 实现覆盖率计算 | LLM 判断 + 统计 | ⏳ |

### 4.2 Phase 2: CLI 集成

| 任务 | 说明 | 状态 |
|------|------|------|
| 创建 requirements_commands.py | CLI 命令模块 | ⏳ |
| 注册到 main.py | 命令行集成 | ⏳ |
| 输出格式化 | 报告样式 | ⏳ |

### 4.3 Phase 3: 自动化

| 任务 | 说明 | 状态 |
|------|------|------|
| 集成到部署流程 | 发布前自动检查 | ⏳ |
| Git Hook 集成 | 提交前检查 | ⏳ |
| 阈值告警 | 覆盖率低于阈值警告 | ⏳ |

---

## 5. 技术细节

### 5.1 需求提取

从需求文档提取功能描述：

```python
def extract_requirements(doc_path: Path) -> List[Requirement]:
    """从需求文档提取需求"""
    content = doc_path.read_text()
    
    # 提取功能ID和描述
    # - F-xxx: 描述
    # - **F-xxx** 描述
    # - `oc-collab xxx` 命令
```

### 5.2 测试提取

从测试文件提取测试代码：

```python
def extract_tests(test_dir: Path) -> List[Test]:
    """从测试目录提取测试代码"""
    tests = []
    
    for test_file in test_dir.glob("test_*.py"):
        content = test_file.read_text()
        
        # 提取测试函数
        # def test_xxx(): ...
        
        tests.append(Test(
            name=func_name,
            code=func_code,
            file=test_file.name
        ))
    
    return tests
```

### 5.3 LLM 判断

使用 LLM 进行语义匹配：

```python
def check_single_coverage(requirement: Requirement, test: Test) -> bool:
    """判断单个测试是否覆盖需求"""
    
    prompt = f"""
需求: {requirement.id} - {requirement.description}

测试: {test.name}
```python
{test.code}
```

这个测试是否覆盖了该需求？
- 如果测试验证了需求中的功能，返回"是"
- 否则返回"否"
"""
    
    response = llm.chat(prompt)
    return "是" in response
```

---

## 6. 验收标准

### 6.1 功能验收

- [ ] `oc-collab requirements coverage` 命令可用
- [ ] 输出需求覆盖率报告
- [ ] 列出未覆盖的需求
- [ ] 支持 `--verbose` 详细模式

### 6.2 质量验收

- [ ] 覆盖率报告准确率 > 90%
- [ ] 单次检查时间 < 30秒
- [ ] 支持大规模项目（100+ 需求）

### 6.3 集成验收

- [ ] 可集成到部署流程
- [ ] 支持 CI/CD 集成
- [ ] 支持阈值告警

---

## 7. 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| LLM 判断不准确 | 人工复核 + 阈值设置 |
| 检查时间过长 | 增量检查 + 并行处理 |
| 需求格式不统一 | 支持多种格式解析 |

---

## 8. 相关文档

| 文档 | 说明 |
|------|------|
| RESEARCH_requirements_coverage.md | 研究文档 |
| tests/test_deployment_modules.py | 示例测试文件 |
| src/core/ | 核心模块目录 |

---

**状态历史**

| 日期 | 状态 | 说明 |
|------|------|------|
| 2026-02-15 | DRAFT | 创建提案 |
| - | - | - |

---

**签署**

| 角色 | 签署 | 时间 |
|------|------|------|
| Agent1 (产品) | - | - |
| Agent2 (技术) | - | - |
