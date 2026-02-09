# Skill体系全面测试方案

**版本**: v1.0
**日期**: 2026-02-09
**测试目标**: 全面验证Skill重组后在系统中的应用情况
**覆盖率目标**: Skill文字切片覆盖率 >= 95%

---

## 1. 测试范围

### 1.1 测试对象

| # | Skill | 行数 | 切片数(预估) | 测试优先级 |
|---|-------|------|-------------|------------|
| 1 | oc_collab_bug_management_guide | 727 | 50+ | P0 |
| 2 | oc_collab_test_acceptance_guide | 388 | 30+ | P0 |
| 3 | oc_collab_development_guide | 329 | 25+ | P0 |
| 4 | oc_collab_detailed_design_guide | 387 | 25+ | P1 |
| 5 | oc_collab_outline_design_guide | 283 | 20+ | P1 |
| 6 | oc_collab_requirements_guide | 474 | 35+ | P0 |
| 7 | oc_collab_requirements_review_guide | 181 | 15+ | P1 |
| 8 | oc_collab_collaboration_guide | 100+ | 10+ | P1 |
| 9 | oc_collab_deployment_guide | 509 | 35+ | P0 |

### 1.2 测试类型

| 测试类型 | 说明 | 覆盖率目标 |
|----------|------|------------|
| skill.json测试 | 验证skill.json完整性 | 100% |
| skill.json触发测试 | 验证触发条件匹配 | 100% |
| skill search测试 | 关键词检索功能 | 95% |
| skill slice测试 | 切片查看功能 | 95% |
| skill enforce测试 | 强制查找功能 | 100% |
| SOP四要素测试 | 验证四要素完整性 | 100% |

---

## 2. 覆盖率评估方法

### 2.1 文字切片覆盖率公式

```
切片覆盖率 = (已测试的切片数 / 总切片数) × 100%
```

### 2.2 切片定义

| 切片级别 | 定义 | 示例 |
|----------|------|------|
| L1: SOP元素 | 触发条件、操作步骤、输出产物、验收标准 | 4个/个Skill |
| L2: 章节 | 每个二级标题(##)下的内容 | 10-50个/个Skill |
| L3: 规则 | 每个独立规则/检查清单 | 20-100个/个Skill |

### 2.3 覆盖率目标

| 测试类型 | 覆盖率目标 |
|----------|------------|
| L1 SOP元素 | 100% |
| L2 章节 | 95% |
| L3 规则 | 90% |

---

## 3. 测试用例设计

### 3.1 skill.json完整性测试 (100%覆盖率)

| 用例ID | 测试场景 | 验证点 |
|--------|----------|--------|
| JSON-001 | 所有Skill有skill.json | ls skills/*/skill.json |
| JSON-002 | skill.json语法正确 | python -c "import json; json.load()" |
| JSON-003 | skill.json包含必需字段 | id, name, version, triggers, outputs |
| JSON-004 | skill.json包含可选字段 | tags, applicable_phase, applicable_role |

### 3.2 skill.json触发测试 (100%覆盖率)

| 用例ID | 测试场景 | 验证点 |
|--------|----------|--------|
| TRIG-001 | requirements_approved触发 | oc-collab skill enforce 时匹配 |
| TRIG-002 | development_completed触发 | 测试阶段触发 |
| TRIG-003 | before_review触发 | 评审前触发 |
| TRIG-004 | test_failure触发 | Bug管理触发 |

### 3.3 skill search测试 (95%覆盖率)

| 用例ID | 测试场景 | 关键词 | 验证点 |
|--------|----------|--------|--------|
| SEARCH-001 | 搜索"需求" | 需求 | 返回requirements_guide |
| SEARCH-002 | 搜索"设计" | 设计 | 返回design相关 |
| SEARCH-003 | 搜索"测试" | 测试 | 返回test_acceptance_guide |
| SEARCH-004 | 搜索"Bug" | Bug | 返回bug_management_guide |
| SEARCH-005 | 搜索"部署" | 部署 | 返回deployment_guide |
| SEARCH-006 | 搜索"协作" | 协作 | 返回collaboration_guide |
| SEARCH-007 | 搜索"开发" | 开发 | 返回development_guide |
| SEARCH-008 | 搜索"评审" | 评审 | 返回requirements_review_guide |
| SEARCH-009 | 搜索"详细设计" | 详细设计 | 返回detailed_design_guide |
| SEARCH-010 | 搜索"概要设计" | 概要设计 | 返回outline_design_guide |

### 3.4 skill slice测试 (95%覆盖率)

| 用例ID | 测试场景 | 切片级别 | 验证点 |
|--------|----------|----------|--------|
| SLICE-001 | 查看完整Skill | L1 | 返回全部内容 |
| SLICE-002 | 查看触发条件章节 | L2 | 返回触发条件 |
| SLICE-003 | 查看操作步骤章节 | L2 | 返回操作步骤 |
| SLICE-004 | 查看输出产物章节 | L2 | 返回输出产物 |
| SLICE-005 | 查看验收标准章节 | L2 | 返回验收标准 |
| SLICE-006 | 查看单个规则 | L3 | 返回规则内容 |

### 3.5 skill enforce测试 (100%覆盖率)

| 用例ID | 测试场景 | 验证点 |
|--------|----------|--------|
| ENFORCE-001 | 执行前检查 | 返回已加载/缺失Skill |
| ENFORCE-002 | 显示缺失Skill | 返回缺失列表 |
| ENFORCE-003 | 显示已加载Skill | 返回已加载列表 |

### 3.6 SOP四要素测试 (100%覆盖率)

| 用例ID | Skill | 验证点 |
|--------|-------|--------|
| SOP-001 | bug_management_guide | 触发条件、操作步骤、输出产物、验收标准 |
| SOP-002 | test_acceptance_guide | 触发条件、操作步骤、输出产物、验收标准 |
| SOP-003 | development_guide | 触发条件、操作步骤、输出产物、验收标准 |
| SOP-004 | deployment_guide | 触发条件、操作步骤、输出产物、验收标准 |
| SOP-005 | requirements_guide | 触发条件、操作步骤、输出产物、验收标准 |
| SOP-006 | requirements_review_guide | 触发条件、操作步骤、输出产物、验收标准 |
| SOP-007 | outline_design_guide | 触发条件、操作步骤、输出产物、验收标准 |
| SOP-008 | detailed_design_guide | 触发条件、操作步骤、输出产物、验收标准 |
| SOP-009 | collaboration_guide | 触发条件、操作步骤、输出产物、验收标准 |

---

## 4. 测试执行计划

### 4.1 Phase 1: skill.json完整性测试

```bash
# 执行
python3 -m pytest tests/test_skill_json_completeness.py -v

# 预期结果
# 9/9 Skill有skill.json
# 9/9 skill.json语法正确
# 9/9 skill.json包含必需字段
```

### 4.2 Phase 2: skill命令功能测试

```bash
# 执行
python3 -m pytest tests/test_skill_commands.py -v

# 预期结果
# skill search: 10/10 测试通过
# skill slice: 6/6 测试通过
# skill enforce: 3/3 测试通过
```

### 4.3 Phase 3: SOP四要素测试

```bash
# 执行
python3 -m pytest tests/test_sop_completeness.py -v

# 预期结果
# 9/9 Skill有完整的SOP四要素
```

### 4.4 Phase 4: 覆盖率评估

```bash
# 执行
python3 -m pytest tests/test_skill_coverage.py --cov-report=term-missing --cov-report=html

# 预期结果
# L1 SOP元素: 36/36 = 100%
# L2 章节: 190/200 = 95%
# L3 规则: 450/500 = 90%
```

---

## 5. 覆盖率评估报告模板

### 5.1 整体覆盖率

| 测试类型 | 目标覆盖率 | 实际覆盖率 | 结果 |
|----------|------------|------------|------|
| skill.json完整性 | 100% | % | ✅/❌ |
| skill.json触发 | 100% | % | ✅/❌ |
| skill search | 95% | % | ✅/❌ |
| skill slice | 95% | % | ✅/❌ |
| skill enforce | 100% | % | ✅/❌ |
| SOP四要素 | 100% | % | ✅/❌ |
| **整体** | **95%** | % | ✅/❌ |

### 5.2 各Skill覆盖率

| Skill | L1覆盖率 | L2覆盖率 | L3覆盖率 | 综合 |
|-------|----------|----------|----------|-------|
| bug_management_guide | % | % | % | % |
| test_acceptance_guide | % | % | % | % |
| development_guide | % | % | % | % |
| deployment_guide | % | % | % | % |
| requirements_guide | % | % | % | % |
| requirements_review_guide | % | % | % | % |
| outline_design_guide | % | % | % | % |
| detailed_design_guide | % | % | % | % |
| collaboration_guide | % | % | % | % |

---

## 6. 测试工具

### 6.1 测试文件结构

```
tests/
├── test_skill_json_completeness.py    # skill.json完整性测试
├── test_skill_commands.py             # skill命令功能测试
├── test_sop_completeness.py           # SOP四要素测试
├── test_skill_coverage.py             # 覆盖率评估
└── test_skill_text_coverage.py        # 文字切片覆盖率
```

### 6.2 覆盖率计算脚本

```python
# 伪代码
def calculate_coverage(skill_path):
    total_slices = count_slices(skill_path)  # 统计切片数
    tested_slices = count_tested_slices(skill_path)  # 统计已测试切片
    return tested_slices / total_slices
```

---

## 7. 测试验收标准

### 7.1 通过标准

| 标准 | 目标 | 说明 |
|------|------|------|
| skill.json完整性 | 100% | 9个Skill全部有完整skill.json |
| skill.json触发 | 100% | 所有触发条件都能匹配 |
| skill search | 95% | 关键词检索返回正确结果 |
| skill slice | 95% | 切片查看功能正常 |
| skill enforce | 100% | 强制查找功能正常 |
| SOP四要素 | 100% | 所有Skill都有完整四要素 |
| 整体覆盖率 | 95% | 综合覆盖率 >= 95% |

### 7.2 不通过标准

| 标准 | 阈值 | 说明 |
|------|------|------|
| skill.json完整性 | < 100% | 任何Skill缺少skill.json |
| skill.json触发 | < 100% | 任何触发条件不匹配 |
| skill search | < 95% | 超过2个搜索结果不正确 |
| skill slice | < 95% | 超过2个切片无法查看 |
| skill enforce | < 100% | 强制查找功能异常 |
| SOP四要素 | < 100% | 任何Skill缺少四要素 |
| 整体覆盖率 | < 95% | 综合覆盖率 < 95% |

---

## 8. 执行时间

预计执行时间：30分钟

| Phase | 执行时间 | 说明 |
|-------|----------|------|
| Phase 1 | 5分钟 | skill.json完整性测试 |
| Phase 2 | 10分钟 | skill命令功能测试 |
| Phase 3 | 5分钟 | SOP四要素测试 |
| Phase 4 | 10分钟 | 覆盖率评估 |

---

**创建人**: Agent 1
**日期**: 2026-02-09
**状态**: 待执行
