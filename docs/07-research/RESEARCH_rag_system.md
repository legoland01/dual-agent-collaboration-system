# Research: RAG 文档检索系统

**目标**: 建立一个基于 LLM 的 RAG 系统，高效检索所有文档材料

**日期**: 2026-02-15
**状态**: 🔬 Researching

---

## 1. 当前问题

### 1.1 文档现状

```
项目文档结构:
├── docs/
│   ├── 00-memos/          # Bug报告、备忘录
│   ├── 01-requirements/   # 需求文档
│   ├── 02-design/         # 设计文档
│   ├── 03-analysis/       # 分析报告
│   ├── 04-proposals/      # 提案
│   ├── 05-skills/         # Skill文档
│   ├── 06-roadmap/        # 路线图
│   └── 07-research/        # 研究文档
├── skills/                 # Skill定义
├── state/                  # 状态文件
└── tests/                  # 测试
```

### 1.2 检索痛点

| 场景 | 问题 |
|------|------|
| 查找 Bug 报告 | 需要记住文件名格式 `BUG-YYYY-MM-DD-xxx.md` |
| 查找需求 | 需要知道在哪个版本文档中 |
| 查找 Skill | 文件分散在 skills/ 目录 |
| 查找历史决策 | 需要grep搜索关键字 |

### 1.3 当前解决方案的问题

| 方法 | 问题 |
|------|------|
| grep 关键词 | 依赖精确匹配，无法语义理解 |
| glob 找文件 | 需要知道文件名规律 |
| 手动翻目录 | 效率低下，浪费时间 |

---

## 2. 方案评估

### 2.1 方案 A：向量库 + Embedding

```
技术栈: ChromaDB + sentence-transformers
优点: 检索速度快
缺点: 需要额外依赖，维护向量库
```

### 2.2 方案 B：LLM 直接理解（不使用 Subagent）

```
优点: 语义理解强
缺点: 阻塞主流程，10-30秒等待
```

### 2.3 方案 C：Subagent 后台检索（最终选择）

```
架构:
用户: oc-collab ask "xxx"
    ↓
主流程: 立即返回 "🔍 正在检索..."
    ↓
Subagent: 后台加载文档 + LLM 分析
    ↓
返回结果

优点:
- 不阻塞主流程
- 保持语义理解能力
- 实现简单
```

---

## 3. 方案评估结论

**选择方案 C: Subagent 后台检索**

| 评估项 | 得分 |
|--------|------|
| 语义理解能力 | ⭐⭐⭐⭐⭐ |
| 响应速度 | ⭐⭐⭐⭐⭐ |
| 实现复杂度 | ⭐⭐⭐ |
| 维护成本 | ⭐⭐⭐⭐ |
| 用户体验 | ⭐⭐⭐⭐⭐ |

---

## 4. POC 验证

### 4.1 核心代码

```python
# src/core/rag_system.py

class RAGSystem:
    """基于 LLM + Subagent 的文档问答系统"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root)
    
    def load_documents(self, query: str = None) -> List[Dict]:
        """加载文档"""
        documents = []
        
        for path in self.project_root.rglob('*'):
            if not path.is_file():
                continue
            if path.suffix not in self.SUPPORTED_EXTENSIONS:
                continue
            
            try:
                content = path.read_text(encoding='utf-8')
                documents.append({
                    'path': str(path.relative_to(self.project_root)),
                    'content': content[:5000],
                })
            except Exception:
                pass
        
        return documents
    
    def ask_async(self, question: str):
        """异步提问（Subagent 方式）"""
        # 后台执行，不阻塞
        pass
```

### 4.2 CLI 命令

```bash
# 提问
oc-collab ask "Agent2 最近修复了哪些Bug？"

# 搜索
oc-collab rag find --type bug "20260215"
```

---

## 5. 待解决问题

| 问题 | 说明 |
|------|------|
| Subagent 实现 | 如何实现后台任务？ |
| LLM 调用 | 如何调用 oc-collab 内置的 LLM？ |
| 上下文管理 | 多轮对话如何处理？ |

---

## 6. 下一步

- [ ] 创建 PROPOSAL-2026-02-018
- [ ] 实现核心功能
- [ ] 集成 Subagent
