# PROPOSAL-2026-02-018: RAG 文档检索系统

**Proposal ID**: PROPOSAL-2026-02-018
**标题**: RAG 文档智能检索系统
**类型**: 新功能 (Feature)
**状态**: DRAFT
**创建日期**: 2026-02-15
**作者**: Agent 1 (产品经理)

---

## 1. 概述

### 1.1 问题背景

当前项目文档分散，检索效率低下：

| 文档类型 | 位置 | 检索难度 |
|---------|------|---------|
| Bug 报告 | docs/00-memos/ | 高（需记文件名格式） |
| 需求文档 | docs/01-requirements/ | 高（需记版本号） |
| Skill | skills/ | 中 |
| 设计文档 | docs/02-design/ | 中 |
| 提案 | docs/04-proposals/ | 中 |

### 1.2 当前方法的问题

| 方法 | 问题 |
|------|------|
| grep 关键词 | 依赖精确匹配，无法语义理解 |
| glob 找文件 | 需要知道文件名规律 |
| 手动翻目录 | 效率低下，浪费时间 |

### 1.3 目标

建立基于 LLM + Subagent 的 RAG 文档检索系统，实现：
- 自然语言提问
- 语义理解检索
- 后台异步处理

---

## 2. 技术方案

### 2.1 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    CLI 入口                              │
│  oc-collab ask "Agent2 修了哪些Bug？"                   │
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

### 2.2 技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| 检索方式 | LLM 语义理解 | 语义理解能力强 |
| 后台处理 | Subagent | 不阻塞主流程 |
| 向量库 | 不使用 | 维护成本高 |
| LLM | oc-collab 内置 | 无需额外 API |

---

## 3. 功能设计

### 3.1 CLI 命令

```bash
# 提问（推荐）
oc-collab ask "Agent2 最近修复了哪些Bug？"
oc-collab ask "部署自动化功能的需求来源是什么？"

# 搜索
oc-collab rag find --type bug "20260215"
oc-collab rag find --type requirement "部署"

# 列出支持的文档类型
oc-collab rag types
```

### 3.2 输出示例

```
$ oc-collab ask "Agent2 修了哪些Bug？"

🔍 正在检索文档...
（后台处理中）

═══════════════════════════════════════════════════════════
📋 回答:

根据文档，Agent2 最近修复了以下Bug:

1. BUG-20260215-001: todowrite编号生成逻辑
   - 修复: TODO-1-012 重复问题
   - 状态: ✅ 已修复

2. BUG-20260215-002: AutoBugDetector CLI集成
   - 修复: 新增 self_review() 方法
   - 状态: ✅ 已修复

3. BUG-20260215-006: AutoBugDetector self_review误报
   - 修复: LLM智能判断方案（待实现）
   - 状态: 🔶 进行中
═══════════════════════════════════════════════════════════

📄 参考文档:
- docs/00-memos/BUG-20260215-001_todo_id_generation.md
- docs/00-memos/BUG-20260215-002_auto_bug_detector_not_working.md
```

### 3.3 支持的文档类型

| 类型 | 目录 | 示例 |
|------|------|------|
| bug | docs/00-memos/BUG-*.md | BUG-20260215-001 |
| requirement | docs/01-requirements/*.md | requirements_v2.2.12.md |
| design | docs/02-design/*.md | DETAIL_v2.2.12.md |
| proposal | docs/04-proposals/PROPOSAL-*.md | PROPOSAL-2026-02-018 |
| skill | skills/*.md | oc_collab_*.md |
| state | state/*.yaml | project_state.yaml |

---

## 4. 实现计划

### 4.1 Phase 1: 核心功能

| 任务 | 说明 | 状态 |
|------|------|------|
| 创建 RAGSystem 类 | 文档加载、LLM 调用 | ⏳ |
| 创建 ask 命令 | 异步提问 | ⏳ |
| 创建 rag 命令 | 搜索功能 | ⏳ |

### 4.2 Phase 2: Subagent 集成

| 任务 | 说明 | 状态 |
|------|------|------|
| 后台任务处理 | Subagent 机制 | ⏳ |
| 进度反馈 | 实时显示检索状态 | ⏳ |
| 结果缓存 | 避免重复检索 | ⏳ |

### 4.3 Phase 3: 增强功能

| 任务 | 说明 | 状态 |
|------|------|------|
| 多轮对话 | 支持上下文 | ⏳ |
| 文档类型过滤 | --type 参数 | ⏳ |
| 结果导出 | JSON/Markdown | ⏳ |

---

## 5. 核心代码设计

### 5.1 RAGSystem 类

```python
# src/core/rag_system.py

from pathlib import Path
from typing import List, Dict, Optional
import asyncio

class RAGSystem:
    """基于 LLM + Subagent 的文档问答系统"""
    
    SUPPORTED_EXTENSIONS = {'.md', '.yaml', '.yml', '.txt', '.json'}
    EXCLUDE_DIRS = {'__pycache__', '.git', 'node_modules', '.venv', 'venv'}
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
    
    def load_documents(
        self,
        doc_type: Optional[str] = None,
        max_content_len: int = 5000
    ) -> List[Dict]:
        """加载文档"""
        documents = []
        
        for path in self.project_root.rglob('*'):
            if not path.is_file():
                continue
            if path.suffix not in self.SUPPORTED_EXTENSIONS:
                continue
            if any(ex in path.parts for ex in self.EXCLUDE_DIRS):
                continue
            
            # 文档类型过滤
            if doc_type:
                if not self._match_type(path, doc_type):
                    continue
            
            try:
                content = path.read_text(encoding='utf-8')
                documents.append({
                    'path': str(path.relative_to(self.project_root)),
                    'type': self._get_doc_type(path),
                    'content': content[:max_content_len],
                })
            except Exception:
                pass
        
        return documents
    
    def _match_type(self, path: Path, doc_type: str) -> bool:
        """判断文档类型"""
        type_mapping = {
            'bug': '00-memos/BUG-',
            'requirement': '01-requirements/',
            'design': '02-design/',
            'proposal': '04-proposals/',
            'skill': 'skills/',
            'state': 'state/',
        }
        return type_mapping.get(doc_type, '') in str(path)
    
    def _get_doc_type(self, path: Path) -> str:
        """获取文档类型"""
        path_str = str(path)
        if '00-memos/BUG-' in path_str:
            return 'bug'
        elif '01-requirements/' in path_str:
            return 'requirement'
        elif '02-design/' in path_str:
            return 'design'
        elif '04-proposals/' in path_str:
            return 'proposal'
        elif 'skills/' in path_str:
            return 'skill'
        elif 'state/' in path_str:
            return 'state'
        return 'other'
    
    def ask(self, question: str, doc_type: Optional[str] = None) -> Dict:
        """
        提问（同步版本）
        
        Returns:
            {
                'answer': '...',
                'references': ['doc1.md', 'doc2.md']
            }
        """
        documents = self.load_documents(doc_type)
        
        # 构建 prompt
        prompt = self._build_prompt(question, documents)
        
        # 调用 LLM
        answer = self._call_llm(prompt)
        
        return {
            'answer': answer,
            'documents': [d['path'] for d in documents[:10]]
        }
    
    def _build_prompt(self, question: str, documents: List[Dict]) -> str:
        """构建 LLM prompt"""
        docs_text = "\n\n---\n\n".join([
            f"【{d['path']}】\n{d['content'][:2000]}"
            for d in documents[:10]
        ])
        
        return f"""你是一个熟悉项目的文档助手。

项目文档位置: {self.project_root}

用户问题: {question}

请根据项目文档回答问题。
如果文档中没有相关信息，请回答"未找到相关信息"。
回答时引用相关文档路径。

---
项目文档:
{docs_text}
---
"""
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM（TODO: 实现）"""
        # 这里调用 oc-collab 内置的 LLM
        pass
```

### 5.2 CLI 命令

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
@click.option('--type', '-t', help='文档类型: bug/requirement/proposal/skill')
def ask(question: str, type: str):
    """提问关于项目文档的问题"""
    click.echo("🔍 正在检索文档...")
    
    rag = RAGSystem()
    result = rag.ask(question, doc_type=type)
    
    click.echo("\n" + "=" * 60)
    click.echo("📋 回答:")
    click.echo("=" * 60)
    click.echo(result['answer'])
    click.echo("\n📄 参考文档:")
    for doc in result['documents']:
        click.echo(f"  - {doc}")

@rag_group.command()
@click.option('--type', '-t', help='文档类型')
@click.option('--keyword', '-k', help='关键字')
def find(type: str, keyword: str):
    """搜索文档"""
    rag = RAGSystem()
    docs = rag.load_documents(doc_type=type)
    
    results = [
        d for d in docs
        if keyword.lower() in d['content'].lower()
    ]
    
    click.echo(f"找到 {len(results)} 个文档:")
    for d in results[:20]:
        click.echo(f"  - {d['path']}")

@rag_group.command()
def types():
    """列出支持的文档类型"""
    click.echo("支持的文档类型:")
    click.echo("  bug         - Bug报告 (docs/00-memos/BUG-*.md)")
    click.echo("  requirement - 需求文档 (docs/01-requirements/*.md)")
    click.echo("  design      - 设计文档 (docs/02-design/*.md)")
    click.echo("  proposal    - 提案 (docs/04-proposals/PROPOSAL-*.md)")
    click.echo("  skill       - Skill文档 (skills/*.md)")
    click.echo("  state       - 状态文件 (state/*.yaml)")
```

---

## 6. 验收标准

### 6.1 功能验收

- [ ] `oc-collab ask` 命令可用
- [ ] `oc-collab rag find` 命令可用
- [ ] 支持文档类型过滤
- [ ] 返回结果包含引用文档

### 6.2 性能验收

- [ ] 检索响应时间 < 30 秒
- [ ] 支持 100+ 文档
- [ ] 后台处理不阻塞主流程

### 6.3 体验验收

- [ ] 输出格式清晰
- [ ] 错误提示友好
- [ ] 支持帮助文档

---

## 7. 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| LLM 处理慢 | Subagent 后台处理 |
| 文档太大 | 截断 + 分页 |
| 理解错误 | 引用原文路径 |

---

## 8. 相关文档

| 文档 | 说明 |
|------|------|
| docs/07-research/RESEARCH_rag_system.md | 研究文档 |
| PROPOSAL-2026-02-017 | 需求覆盖率（类似设计） |

---

**状态历史**

| 日期 | 状态 | 说明 |
|------|------|------|
| 2026-02-15 | DRAFT | 创建提案 |

---

**签署**

| 角色 | 签署 | 时间 |
|------|------|------|
| Agent1 (产品) | - | - |
| Agent2 (技术) | - | - |
