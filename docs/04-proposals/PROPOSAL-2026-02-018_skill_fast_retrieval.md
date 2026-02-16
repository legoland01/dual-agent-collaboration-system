# PROPOSAL-2026-02-018: Skill快速检索系统

**类型**: Feature Enhancement
**优先级**: P1
**影响版本**: v2.3.0
**提出者**: Agent 1
**日期**: 2026-02-15
**状态**: Draft

---

## 1. 背景

### 1.1 问题

当前Agent使用Skill时存在以下痛点：
- Skill内容完整但查找慢，需要手动执行 `oc-collab skill slice` 
- 关键词触发机制未集成到工作流
- Agent遇到问题时无法快速定位相关Skill

### 1.2 研究结论

根据 RESEARCH_PLAN_skill_fast_retrieval.md 的PoC验证结果：

| 指标 | 索引方案 | RAG方案 |
|------|----------|---------|
| 准确率 | 100% | 100% |
| 速度 | <0.1ms | <0.1ms |
| 实现成本 | 低 | 中 |
| 外部依赖 | 无 | sentence-transformers |

**结论**：选择**索引方案**，实现简单、无需外部依赖、100%准确率。

---

## 2. 目标

构建Skill快速检索系统，实现：
1. 关键词索引文件 (skill_index.yaml)
2. `oc-collab skill search` 命令
3. 与现有 `skill slice` 集成

---

## 3. 方案设计

### 3.1 索引文件结构

```yaml
# config/skill_index.yaml
version: 1.0
last_updated: "2026-02-15"

index:
  # 版本管理
  - keywords:
      - 版本
      - 发布
      - version
      - release
      - PyPI
    skill: oc_collab_version_management_guide
    description: 版本号管理、发布流程

  # Bug管理
  - keywords:
      - Bug
      - bug
      - 报Bug
      - 问题
    skill: oc_collab_bug_management_guide
    description: Bug报告、处理流程

  # 部署
  - keywords:
      - 部署
      - 部署流程
      - deploy
      - 上传
    skill: oc_collab_deployment_guide
    description: 部署到PyPI流程

  # 需求
  - keywords:
      - 需求
      - 创建需求
      - requirements
    skill: oc_collab_requirements_guide
    description: 需求文档创建规范

  # 设计
  - keywords:
      - 设计
      - 概要设计
      - 详细设计
      - design
    skill: oc_collab_outline_design_guide
    description: 设计文档规范

  # 测试
  - keywords:
      - 测试
      - 验收
      - test
    skill: oc_collab_test_acceptance_guide
    description: 测试验收规范

  # 开发
  - keywords:
      - 开发
      - 实现
      - develop
    skill: oc_collab_development_guide
    description: 开发流程规范

  # Skill
  - keywords:
      - Skill
      - skill
    skill: oc_collab_skill_authoring_guide
    description: Skill编写规范
```

### 3.2 命令设计

```bash
# 基本搜索
oc-collab skill search "怎么发版本？"
# → 找到关键词"版本" → 匹配 oc_collab_version_management_guide

# 显示匹配结果
oc-collab skill search "Bug怎么处理？" --verbose
# → oc_collab_bug_management_guide (confidence: 100%)

# 搜索后直接slice
oc-collab skill search "版本号规则" --slice
# → 搜索 + 打开skill slice界面
```

### 3.3 架构设计

```
┌─────────────────────────────────────────┐
│           CLI Layer                     │
│  oc-collab skill search <query>         │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│       SkillSearchEngine                 │
│  - load_index()                         │
│  - search(query) → List[SearchResult]  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│       skill_index.yaml                  │
│  关键词 → Skill映射                     │
└─────────────────────────────────────────┘
```

### 3.4 核心模块

```python
# src/core/skill_search.py

class SearchResult:
    skill: str
    keywords: List[str]
    confidence: float  # 0.0-1.0

class SkillSearchEngine:
    def __init__(self, index_path: str):
        self.index = self._load_index(index_path)
    
    def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        # 1. 分词
        tokens = self._tokenize(query)
        
        # 2. 匹配关键词
        results = []
        for entry in self.index["index"]:
            matched = set(tokens) & set(entry["keywords"])
            if matched:
                results.append(SearchResult(
                    skill=entry["skill"],
                    keywords=list(matched),
                    confidence=len(matched) / len(entry["keywords"])
                ))
        
        # 3. 排序返回
        return sorted(results, key=lambda x: x.confidence, reverse=True)[:top_k]
```

---

## 4. 实现计划

### 4.1 阶段划分

| 阶段 | 内容 | 工时 |
|------|------|------|
| **Phase 1** | 索引文件 + 核心引擎 | 1h |
| **Phase 2** | CLI命令实现 | 0.5h |
| **Phase 3** | 与skill slice集成 | 0.5h |

### 4.2 详细任务

- [ ] 创建 `config/skill_index.yaml` 索引文件
- [ ] 实现 `src/core/skill_search.py` 搜索引擎
- [ ] 实现 `src/cli/skill_search_command.py` 命令
- [ ] 注册CLI命令到 `__init__.py`
- [ ] 单元测试 (≥80%覆盖率)
- [ ] E2E测试

---

## 5. 验收标准

### 5.1 功能验收

- [ ] 索引文件正确加载
- [ ] `skill search` 命令正确匹配关键词
- [ ] 返回结果按置信度排序
- [ ] `--slice` 参数可触发skill slice
- [ ] `--verbose` 参数显示详细信息

### 5.2 测试验收

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] E2E测试通过
- [ ] 21个历史查询样本全部命中

---

## 6. 风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| 关键词冲突 | 匹配到多个Skill | 按置信度排序，用户选择 |
| 索引维护 | Skill更新时需同步 | 文档规范 + 定期检查 |
| 新Skill未索引 | 无法搜索到 | 创建Skill时同步更新索引 |

---

## 7. 利益相关者

| 角色 | 关注点 |
|------|--------|
| Agent1 | 快速找到相关Skill，提升工作效率 |
| Agent2 | 索引维护成本可接受 |

---

**提出者**: Agent 1
**日期**: 2026-02-15
**状态**: Draft → Pending Review
