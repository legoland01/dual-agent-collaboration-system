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

---

## 2. RAG 系统设计

### 2.1 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    RAG 检索系统                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐│
│  │   文档加载   │ -> │   向量存储   │ -> │   语义检索   ││
│  └─────────────┘    └─────────────┘    └─────────────┘│
│        ↓                                        ↓       │
│  ┌─────────────┐                          ┌─────────────┐│
│  │  文档分块   │                          │  LLM 生成   ││
│  └─────────────┘                          └─────────────┘│
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 数据源

| 数据源 | 类型 | 块大小 |
|--------|------|--------|
| docs/*.md | Markdown | 500 tokens |
| skills/*.md | Markdown | 300 tokens |
| state/*.yaml | 结构化 | 完整文件 |
| tests/*.py | 代码 | 200 tokens |

---

## 3. 实现方案

### 3.1 方案 A：本地向量库 + CLI 命令

**技术栈：**
- ChromaDB / FAISS（向量存储）
- sentence-transformers（中文embedding）
- Click（CLI）

**CLI 设计：**

```bash
# 初始化向量库
oc-collab rag init

# 检索文档
oc-collab rag search "Agent2的Bug处理流程"
oc-collab rag find --type bug "20260215"
oc-collab rag find --type requirement "部署自动化"

# 更新索引
oc-collab rag update
```

**输出示例：**

```
$ oc-collab rag search "部署流程"

📄 找到 3 个相关文档:

1. [docs/04-proposals/PROPOSAL-2026-02-017_requirements_coverage.md]
   相关度: 0.95
   片段: "提供`oc-collab deploy`命令，实现部署全流程自动化..."

2. [docs/01-requirements/requirements_v2.2.12.md]
   相关度: 0.87
   片段: "F-DEPLOY-001: 部署自动化CLI..."

3. [tests/test_deployment_modules.py]
   相关度: 0.82
   片段: "TC-001: VersionManager 版本号管理..."
```

### 3.2 方案 B：LLM 直接理解 + CLI 命令（推荐）

**核心思路：**
- 不需要向量库
- 直接用 LLM 的语义理解能力
- 用户提问 → LLM 分析 → 直接回答

**CLI 设计：**

```bash
# 直接提问
oc-collab ask "Agent2 最近修复了哪些Bug？"

# 基于文档回答
oc-collab ask "部署自动化功能的需求来源是什么？"
```

**实现：**

```python
# src/core/rag_system.py

class RAGSystem:
    """基于 LLM 的文档问答系统"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
    
    def load_all_documents(self) -> list:
        """加载所有文档"""
        documents = []
        
        # 加载所有 md 文件
        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            documents.append({
                "path": str(md_file.relative_to(self.project_root)),
                "content": content
            })
        
        return documents
    
    def answer(self, question: str) -> str:
        """
        使用 LLM 回答问题
        """
        documents = self.load_all_documents()
        
        # 构建 prompt
        prompt = f"""
你是一个文档检索助手。
用户的问题是: {question}

以下是项目中的文档:
{self._format_documents(documents)}

请根据文档内容回答用户的问题。
如果文档中没有相关信息，请说明"未找到相关信息"。
"""
        
        # 调用 LLM（这里使用项目内置的 LLM）
        response = llm.chat(prompt)
        
        return response
    
    def _format_documents(self, documents: list, max_tokens: int = 8000) -> str:
        """格式化文档内容，控制长度"""
        formatted = []
        total_length = 0
        
        for doc in documents:
            content = f"文档: {doc['path']}\n\n{doc['content']}"
            if total_length + len(content) > max_tokens:
                break
            formatted.append(content)
            total_length += len(content)
        
        return "\n\n---\n\n".join(formatted)
```

### 3.3 方案对比

| 特性 | 方案 A (向量库) | 方案 B (LLM直接) |
|------|----------------|-----------------|
| 实现复杂度 | 高 | 低 |
| 检索速度 | 快 | 慢 |
| 理解能力 | 一般 | 强 |
| 维护成本 | 高（需更新向量） | 无 |
| 离线可用 | 是 | 是 |

**推荐：方案 B（LLM 直接理解）**

理由：
1. oc-collab 本身就是 LLM 驱动的
2. 实现简单，不需要额外依赖
3. 语义理解能力强
4. 无需维护向量库

---

## 4. POC 实现

### 4.1 核心代码

```python
# src/core/rag_system.py

from pathlib import Path
from typing import List, Dict

class RAGSystem:
    """基于 LLM 的文档问答系统"""
    
    SUPPORTED_EXTENSIONS = {'.md', '.yaml', '.yml', '.txt', '.json'}
    EXCLUDE_DIRS = {'__pycache__', '.git', 'node_modules', '.venv', 'venv'}
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
    
    def load_documents(self, query: str = None) -> List[Dict]:
        """加载文档，可选过滤"""
        documents = []
        
        for path in self.project_root.rglob('*'):
            if not path.is_file():
                continue
            if path.suffix not in self.SUPPORTED_EXTENSIONS:
                continue
            if any(ex in path.parts for ex in self.EXCLUDE_DIRS):
                continue
            
            try:
                content = path.read_text(encoding='utf-8')
                documents.append({
                    'path': str(path.relative_to(self.project_root)),
                    'content': content[:5000],  # 截断太长
                })
            except Exception:
                pass
        
        return documents
    
    def ask(self, question: str) -> str:
        """回答问题"""
        docs = self.load_documents()
        
        prompt = f"""你是一个熟悉项目的文档助手。
        
项目文档位置: {self.project_root}

用户问题: {question}

请根据项目文档回答问题。
如果文档中没有相关信息，请回答"未找到相关信息"。

---
项目文档:
{self._format_docs(docs)}
---
"""
        # 这里调用 LLM
        return self._call_llm(prompt)
    
    def _format_docs(self, docs: List[Dict], max_len: int = 10000) -> str:
        """格式化文档"""
        result = []
        total = 0
        for doc in docs:
            text = f"【{doc['path']}】\n{doc['content'][:2000]}\n"
            if total + len(text) > max_len:
                break
            result.append(text)
            total += len(text)
        return '\n---\n'.join(result)
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM（待实现）"""
        # TODO: 实现 LLM 调用
        return "TODO: 实现 LLM 调用"
```

### 4.2 CLI 命令

```python
# src/cli/rag_commands.py

import click
from ..core.rag_system import RAGSystem

@click.group()
def rag_group():
    """RAG 文档问答系统"""
    pass

@rag_group.command()
@click.argument('question')
def ask(question: str):
    """提问关于项目文档的问题"""
    rag = RAGSystem()
    answer = rag.ask(question)
    click.echo(answer)

@rag_group.command()
@click.option('--type', '-t', help='文档类型: bug/requirement/proposal')
@click.option('--keyword', '-k', help='关键字搜索')
def search(type: str, keyword: str):
    """搜索文档"""
    rag = RAGSystem()
    results = rag.search(type=type, keyword=keyword)
    for r in results:
        click.echo(f"- {r['path']} (相关度: {r['score']:.2f})")
```

---

## 6. 方案重新评估

### 6.1 用户反馈的问题

**Q1: 为什么用 grep 而不是语义理解？**
- 反思：作为 LLM，应该发挥语义理解能力，而不是依赖关键词匹配
- 改进：直接用 LLM 理解用户问题

**Q2: 查询速度问题？**
- 问题：每次加载所有文档让 LLM 处理，需要 10-30 秒
- 影响：用户体验差

**Q3: 是否影响主流程？**
- 问题：文档检索会阻塞用户当前工作
- 解决：使用 Subagent 后台检索

### 6.2 改进后的方案

**方案 C：Subagent 后台检索（推荐）**

```
用户提问: "Agent2 修了哪些Bug？"
    ↓
主流程: 立即返回 "🔍 正在检索..."
    ↓
Subagent: 后台加载文档 + LLM 分析
    ↓
返回结果
```

**优点：**
- 不阻塞主流程
- 可以并行处理多个查询
- 用户体验好
- 保持语义理解能力

### 6.3 实现架构

```
┌─────────────────────────────────────────────────────────┐
│                    CLI 入口                              │
│  oc-collab ask "xxx"                                   │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    同步返回                  Subagent
    "正在检索..."            后台处理
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              加载文档                 向量检索（可选）
                    │                         │
                    └────────────┬────────────┘
                                 │
                          LLM 分析
                                 │
                          返回结果
```

---

## 7. 下一步

- [ ] 实现 RAGSystem + Subagent
- [ ] 测试后台检索效果
- [ ] 评估性能

---

## 6. 相关文档

| 文档 | 说明 |
|------|------|
| PROPOSAL-2026-02-017 | 需求覆盖率（类似设计） |
| src/core/ | 核心模块目录 |

---

**待解决问题**

| 问题 | 说明 |
|------|------|
| LLM 调用方式 | 如何调用 oc-collab 内置的 LLM？ |
| 文档加载性能 | 大项目如何优化？ |
| 多轮对话 | 是否需要支持上下文？ |
