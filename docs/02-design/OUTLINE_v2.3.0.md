# 概要设计说明书：oc-collab v2.3.0

**版本**: v1
**创建日期**: 2026-02-15
**作者**: Agent 1 (产品经理)
**关联需求**: requirements_v2.3.0_DRAFT.md
**版本号**: v2.3.0
**状态**: DRAFT

---

## 1. 功能模块概览

### 1.1 v2.3.0 功能模块图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        oc-collab v2.3.0 质量保证工具集                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                     CLI 命令层 (v2.3.0 新增)                                  │ │
│  ├─────────────────────────────────────────────────────────────────────────────┤ │
│  │  Skill检索命令                     │ BUG管理命令              │ 需求命令        │ │
│  │  ├─ oc-collab skill search        │ ├─ oc-collab bug link   │ ├─ oc-collab   │ │
│  │  │   [--slice] [--verbose]        │ │   [--unlisted]         │ │   requirements │ │
│  │  └─ oc-collab skill index --sync  │ └─ oc-collab signoff +  │ │   coverage    │ │
│  │                                    │     BUG完整性检查        │ └─ signoff +   │ │
│  │                                    │                         │     需求覆盖检查 │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                              │
│                                    ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         核心功能模块                                           │ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  【v2.3.0新增】Skill检索模块                                            ││ │
│  │  │  ├─ SkillIndex: 索引管理 [v2.3.0]                                     ││ │
│  │  │  ├─ SkillSearchEngine: 搜索引擎 [v2.3.0]                              ││ │
│  │  │  └─ IndexAutoUpdater: 索引自动更新 [v2.3.0]                            ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  【v2.3.0新增】BUG关联测试模块                                           ││ │
│  │  │  ├─ BugTestLinker: BUG-测试关联 [v2.3.0]                              ││ │
│  │  │  ├─ TestSuggestionEngine: 测试建议 [v2.3.0]                           ││ │
│  │  │  └─ CoverageChecker: 完整性检查 [v2.3.0]                              ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  【v2.3.0新增】需求覆盖率模块                                            ││ │
│  │  │  ├─ RequirementsCoverageAnalyzer: 覆盖率分析 [v2.3.0]                  ││ │
│  │  │  ├─ RequirementTestMapper: 需求-测试映射 [v2.3.0]                     ││ │
│  │  │  └─ CoverageReportGenerator: 报告生成 [v2.3.0]                         ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 v2.3.0 功能清单

| 功能模块 | 功能 | 类型 | 工时 | 架构模块 |
|----------|------|------|------|----------|
| Skill检索模块 | SkillIndex (索引管理) | 新增 | 1h | 6.1 |
| Skill检索模块 | SkillSearchEngine (搜索引擎) | 新增 | 3h | 6.1 |
| Skill检索模块 | IndexAutoUpdater (索引自动更新) | 新增 | 2h | 6.1 |
| Skill检索模块 | AutoTriggerPrompt (自动触发提示) | 新增 | 1h | 6.1 |
| BUG关联测试模块 | BugTestLinker (BUG-测试关联) | 新增 | 2h | 4.2 |
| BUG关联测试模块 | TestSuggestionEngine (测试建议) | 新增 | 2h | 4.2 |
| BUG关联测试模块 | BugCoverageChecker (完整性检查) | 新增 | 1h | 4.2 |
| BUG关联测试模块 | BugTestTemplate (测试模板) | 新增 | 1h | 4.2 |
| 需求覆盖率模块 | RequirementsCoverageAnalyzer (覆盖率分析) | 新增 | 2h | 4.1 |
| 需求覆盖率模块 | RequirementTestMapper (需求-测试映射) | 新增 | 1h | 4.1 |
| 需求覆盖率模块 | CoverageReportGenerator (报告生成) | 新增 | 1h | 4.1 |
| 需求覆盖率模块 | RequirementSuggestionEngine (需求建议) | 新增 | 1h | 4.1 |

---

## 2. 详细设计

### 2.1 Skill检索模块 (F-QUAL-001)

#### 2.1.1 SkillIndex

**功能**: 管理skill_index.yaml索引文件

```python
class SkillIndex:
    def __init__(self, index_path: str = "config/skill_index.yaml"):
        self.index = self._load_index()
    
    def _load_index(self) -> dict:
        """加载索引文件"""
        
    def add_entry(self, keywords: List[str], skill: str):
        """添加索引条目"""
        
    def update_keywords(self, skill: str, keywords: List[str]):
        """更新关键词"""
        
    def get_all_skills(self) -> List[str]:
        """获取所有Skill名称"""
```

#### 2.1.2 SkillSearchEngine

**功能**: 关键词搜索

```python
class SearchResult:
    skill: str
    keywords: List[str]
    confidence: float

class SkillSearchEngine:
    def __init__(self, index: SkillIndex):
        self.index = index
    
    def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """搜索Skill"""
        tokens = self._tokenize(query)
        # 匹配关键词，返回置信度排序结果
```

#### 2.1.3 IndexAutoUpdater

**功能**: Skill新增/更新时自动同步索引

```python
class IndexAutoUpdater:
    def __init__(self, index: SkillIndex):
        self.index = index
    
    def on_skill_created(self, skill_path: str):
        """Skill创建时自动更新索引"""
        
    def on_skill_updated(self, skill_path: str):
        """Skill更新时自动更新索引"""
```

### 2.2 BUG关联测试模块 (F-QUAL-002)

#### 2.2.1 BugTestLinker

**功能**: BUG与测试用例关联

```python
class BugTestLinker:
    def __init__(self):
        self.links = self._load_links()  # bug_test_links.yaml
    
    def link(self, bug_id: str, test_file: str):
        """关联BUG与测试"""
        
    def unlink(self, bug_id: str, test_file: str):
        """解除关联"""
        
    def get_tests_for_bug(self, bug_id: str) -> List[str]:
        """获取BUG关联的测试"""
        
    def get_bugs_without_tests(self) -> List[str]:
        """获取未关联测试的BUG"""
```

#### 2.2.2 TestSuggestionEngine

**功能**: 创建BUG时自动建议测试用例

```python
class TestSuggestionEngine:
    def __init__(self):
        self.knowledge_base = self._load_kb()
    
    def suggest_tests(self, bug: BugReport) -> List[str]:
        """根据BUG建议可能的测试用例"""
        # 基于BUG类型、模块、关键词推荐测试
```

### 2.3 需求覆盖率模块 (F-QUAL-003)

#### 2.3.1 RequirementsCoverageAnalyzer

**功能**: 分析需求覆盖率

```python
class RequirementsCoverageAnalyzer:
    def __init__(self):
        self.requirements = self._load_requirements()
        self.tests = self._load_tests()
    
    def analyze_coverage(self) -> CoverageReport:
        """分析覆盖率"""
        
    def get_uncovered_requirements(self) -> List[str]:
        """获取未覆盖的需求"""
```

#### 2.3.2 RequirementTestMapper

**功能**: 需求与测试映射

```python
class RequirementTestMapper:
    def __init__(self):
        self.mapping = self._load_mapping()  # requirement_test_mapping.yaml
    
    def map(self, requirement_id: str, test_file: str):
        """映射需求与测试"""
        
    def get_tests_for_requirement(self, req_id: str) -> List[str]:
        """获取需求关联的测试"""
```

---

## 3. 数据结构设计

### 3.1 skill_index.yaml

```yaml
version: 1.0
last_updated: "2026-02-15"

index:
  - keywords: [版本, 发布, version, release]
    skill: oc_collab_version_management_guide
    description: 版本号管理、发布流程
    
  - keywords: [Bug, bug, 报Bug]
    skill: oc_collab_bug_management_guide
    description: Bug报告、处理流程
    # ... 更多条目
```

### 3.2 bug_test_links.yaml

```yaml
version: 1.0
links:
  - bug_id: BUG-20260215-001
    test_files:
      - tests/test_todo_sync.py
    created_at: "2026-02-15"
    
  - bug_id: BUG-20260215-002
    test_files: []
```

### 3.3 requirement_test_mapping.yaml

```yaml
version: 1.0
mappings:
  - requirement_id: F-QUAL-001
    test_files:
      - tests/test_skill_search.py
    coverage: 100
    
  - requirement_id: F-QUAL-002
    test_files: []
    coverage: 0
```

---

## 4. 集成设计

### 4.1 CLI集成

| 命令 | 集成模块 |
|------|----------|
| `oc-collab skill search` | SkillSearchEngine |
| `oc-collab skill index --sync` | IndexAutoUpdater |
| `oc-collab bug link` | BugTestLinker |
| `oc-collab bug list --unlinked` | BugTestLinker |
| `oc-collab requirements coverage` | RequirementsCoverageAnalyzer |
| `oc-collab signoff` | BugCoverageChecker + CoverageChecker |

### 4.2 自动触发

| 触发场景 | 执行操作 |
|----------|----------|
| Skill文件创建/更新 | IndexAutoUpdater.on_skill_updated() |
| BUG报告创建 | TestSuggestionEngine.suggest_tests() |
| 测试文件创建 | RequirementSuggestionEngine.suggest_requirements() |
| signoff执行 | CoverageChecker.check_bug_coverage() + check_requirement_coverage() |

---

## 5. 工时预估

| 模块 | 组件 | 工时 | 小计 |
|------|------|------|------|
| Skill检索 | SkillIndex + SearchEngine | 4h | |
| Skill检索 | IndexAutoUpdater | 2h | |
| Skill检索 | AutoTriggerPrompt | 1h | 7h |
| BUG关联 | BugTestLinker | 2h | |
| BUG关联 | TestSuggestionEngine | 2h | |
| BUG关联 | CoverageChecker | 1h | |
| BUG关联 | BugTestTemplate | 1h | 6h |
| 需求覆盖 | CoverageAnalyzer | 2h | |
| 需求覆盖 | RequirementTestMapper | 1h | |
| 需求覆盖 | ReportGenerator | 1h | |
| 需求覆盖 | SuggestionEngine | 1h | 5h |
| **总计** | | | **18h** |

**与需求文档对比**: 需求21h vs 设计18h（差异3h为测试+修复预留）

---

## 6. 风险与依赖

### 6.1 技术风险

| 风险 | 影响 | 应对 |
|------|------|------|
| 索引关键词覆盖不足 | 搜索命中率低 | 定期更新 + 用户反馈 |
| LLM集成复杂度 | 实现难度高 | 提供简化版本 |

### 6.2 依赖关系

| 组件 | 依赖 |
|------|------|
| SkillSearchEngine | SkillIndex |
| IndexAutoUpdater | SkillIndex |
| TestSuggestionEngine | BugTestLinker |
| CoverageChecker | BugTestLinker |
| RequirementSuggestionEngine | RequirementTestMapper |

---

## 7. 验收标准

| 功能模块 | 设计验收标准 |
|----------|--------------|
| Skill检索 | 索引结构完整，搜索算法可行 |
| BUG关联 | 关联数据结构设计合理 |
| 需求覆盖 | 覆盖率分析逻辑可行 |

---

## 8. 与需求对齐

| 需求ID | 设计模块 | 覆盖情况 |
|--------|----------|----------|
| F-QUAL-001 | Skill检索模块 | ✅ 完整覆盖 |
| F-QUAL-002 | BUG关联测试模块 | ✅ 完整覆盖 |
| F-QUAL-003 | 需求覆盖率模块 | ✅ 完整覆盖 |

---

## 9. 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-15 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | - | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-15
**修订日期**: 2026-02-15
**状态**: DRAFT
