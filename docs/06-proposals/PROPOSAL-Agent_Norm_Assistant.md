# Proposal: Agent协作规范智能辅助系统

**Proposal ID**: PROPOSAL-20260208-002
**状态**: 待评审
**创建人**: Agent 2
**创建日期**: 2026-02-08

---

## 背景

### 问题

**问题1：Agent 行动前不读 skill**

- 现象：Agent 容易惯性操作，不先确认规范
- 案例：评审TODO完成后，签署信息写在TODO里而不是文档里
- 影响：违反协作规范，增加沟通成本

**问题2：TODO 信息不完整**

- 现象：TODO 创建时缺少上下文信息
- 案例：接收方不知道需要查看哪个 skill
- 影响：执行人可能遗漏关键规范

**问题3：Skill 信息检索困难**

- 现象：Skill 文档长，Agent 难以快速定位相关内容
- 案例：查找"评审TODO规范"需要遍历整个协作指南
- 影响：降低协作效率，增加出错概率

---

## 目标

创建一个**Agent 协作规范智能辅助系统**，帮助 Agent 在协作过程中：

1. **行动前自动检查** - 根据操作类型提醒相关规范
2. **TODO 携带上下文** - 嵌入相关 skill 片段
3. **Skill 快速检索** - 基于标签的切片检索

---

## 解决方案

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│              Agent 协作规范智能辅助系统                      │
├─────────────────────────────────────────────────────────┤
│  1. todowrite 自动检查                                   │
│     - 规则引擎：根据操作类型匹配规范                        │
│     - 提醒式检查：不是强制阻断，而是智能提示               │
├─────────────────────────────────────────────────────────┤
│  2. TODO 上下文携带                                     │
│     - skill_fragments.yaml：技能片段存储                  │
│     - 接收方直接看到相关规范片段                          │
├─────────────────────────────────────────────────────────┤
│  3. Skill 切片检索                                      │
│     - 预切片：每个 skill 切割成独立片段                   │
│     - 标签化：每个片段打上多维标签                         │
│     - 检索：基于标签的快速检索                            │
└─────────────────────────────────────────────────────────┘
```

---

## 详细设计

### 1. todowrite 自动检查

#### 1.1 规则引擎设计

```python
# src/cli/norm_checker.py

class NormChecker:
    """规范检查器"""
    
    # 规则定义
    RULES = {
        "评审": {
            "check": lambda content: True,
            "reminder": "提醒：评审完成后，签署信息应写在被评审的文档里，不是TODO里",
            "skill_ref": "oc_collab_collaboration_guide#评审反馈TODO体系"
        },
        "修复": {
            "check": lambda content: has_bug_report(content),
            "reminder": "检查：修复前是否已创建Bug报告？",
            "skill_ref": "oc_collab_bug_management_guide#Bug处理流程"
        },
        "测试": {
            "check": lambda content: True,
            "reminder": "提示：测试验收在 test 阶段执行",
            "skill_ref": "oc_collab_test_acceptance_guide#测试验收流程"
        },
        "签署": {
            "check": lambda content: has_signoff_target(content),
            "reminder": "检查：签署应伴随实质性变更",
            "skill_ref": "oc_collab_collaboration_guide#签署规范"
        },
        "创建": {
            "check": lambda content: True,
            "reminder": "遵循TODO创建黄金法则：只创建当前步骤，不要提前创建",
            "skill_ref": "oc_collab_collaboration_guide#TODO创建黄金法则"
        },
        None: {
            "check": lambda content: True,
            "reminder": "提示：确保TODO内容清晰，指定执行人",
            "skill_ref": None
        }
    }
    
    def check(self, content: str) -> dict:
        """检查TODO内容"""
        for keyword, rule in self.RULES.items():
            if keyword and keyword in content:
                return {
                    "matched": keyword,
                    "reminder": rule["reminder"],
                    "skill_ref": rule["skill_ref"]
                }
        return {
            "matched": None,
            "reminder": "提示：确保TODO内容清晰，指定执行人",
            "skill_ref": None
        }
```

#### 1.2 todowrite 集成

```python
# src/cli/enhanced_commands.py

@click.command(name="todowrite")
@click.argument("todos", nargs=-1)
@click.option("--content", help="待办内容")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium")
@click.option("--agent", type=click.Choice(["1", "2"]), help="Agent 编号")
def todowrite_command(todos: tuple, content: Optional[str], priority: str, agent: Optional[str]):
    """创建待办任务（带规范检查）"""
    from ..core.norm_checker import NormChecker
    
    norm_checker = NormChecker()
    
    if content:
        # 规范检查
        check_result = norm_checker.check(content)
        
        # 输出提醒
        click.echo(f"\n📋 规范检查结果:")
        click.echo(f"   {check_result['reminder']}")
        
        if check_result['skill_ref']:
            click.echo(f"   参考: {check_result['skill_ref']}")
        
        if not agent:
            click.echo(f"\n⚠️  错误：必须指定执行人 (--agent 1 或 --agent 2)")
            return
    
    # ... 原有逻辑继续
```

#### 1.3 输出示例

```bash
# 示例1：评审TODO
$ oc-collab todowrite --content "评审 v2.2.5 需求分析报告" --agent 2

📋 规范检查结果:
   提醒：评审完成后，签署信息应写在被评审的文档里，不是TODO里
   参考: oc_collab_collaboration_guide#评审反馈TODO体系

✅ 待办已创建: [TODO-067] 评审 v2.2.5 需求分析报告
   优先级: medium
   状态: pending
   📎 附加信息: 请查看协作指南"评审反馈TODO体系"

---

# 示例2：缺少执行人
$ oc-collab todowrite --content "修复 Bug"

⚠️  错误：必须指定执行人 (--agent 1 或 --agent 2)

---

# 示例3：修复TODO
$ oc-collab todowrite --content "修复 BUG-20260208-003" --agent 2

📋 规范检查结果:
   检查：修复前是否已创建Bug报告？
   参考: oc_collab_bug_management_guide#Bug处理流程

✅ 待办已创建: [TODO-068] 修复 BUG-20260208-003
```

---

### 2. TODO 上下文携带

#### 2.1 Skill 片段存储

```yaml
# state/skill_fragments.yaml
version: "1.0"
last_updated: "2026-02-08"

fragments:
  # 评审相关片段
  - id: "review_signoff"
    tags: ["评审", "签署", "TODO"]
    content: |
      ## 评审反馈TODO体系
      
      **原则**：TODO是短程"通知-完成"结构
      
      Agent2评审 → TODO设为complete（评审工作完成）
          ↓
      如需Agent1反馈
          ↓
      Agent2创建新TODO给Agent1（不要自己创建给自己的TODO）
      
      **重要**：签署信息应写在被评审的文档里，不是TODO里！
    source: "oc_collab_collaboration_guide#评审反馈TODO体系"
    
  # TODO创建相关片段
  - id: "todo_creation_golden_rule"
    tags: ["TODO", "创建", "黄金法则"]
    content: |
      ## TODO 创建黄金法则
      
      | 规则 | 说明 |
      |------|------|
      | 只创建当前步骤的TODO | 不要创建"修复后测试"的TODO |
      | 不提前创建 | 只有明确需要时才创建 |
      | 不代他人创建 | 由需要的人自己创建 |
      | 不自创TODO | 实际需要时再创建 |
    source: "oc_collab_collaboration_guide#TODO创建黄金法则"
    
  # Bug修复相关片段
  - id: "bug_fix_flow"
    tags: ["Bug", "修复", "流程"]
    content: |
      ## Bug处理流程
      
      1. 发现Bug → 创建Bug报告
      2. 创建TODO分配给Agent2（只创建修复的TODO）
      3. Agent2修复
      4. Agent1验收（签署在Bug报告里）
      
      **禁止**：Agent1提前创建"修复后测试"的TODO
    source: "oc_collab_bug_management_guide#Bug处理流程"
```

#### 2.2 TODOWRITE 自动嵌入片段

```python
# src/cli/todo_fragment_embedder.py

class TodoFragmentEmbedder:
    """TODO片段嵌入器"""
    
    def __init__(self, fragments_file: str = "state/skill_fragments.yaml"):
        self.fragments = self._load_fragments(fragments_file)
    
    def embed_fragments(self, content: str) -> list[dict]:
        """根据TODO内容嵌入相关片段"""
        matched_fragments = []
        
        for fragment in self.fragments:
            if self._matches(content, fragment["tags"]):
                matched_fragments.append({
                    "id": fragment["id"],
                    "content": fragment["content"],
                    "source": fragment["source"]
                })
        
        return matched_fragments[:3]  # 最多返回3个片段
    
    def _matches(self, content: str, tags: list[str]) -> bool:
        """检查content是否匹配tags"""
        content_lower = content.lower()
        for tag in tags:
            if tag.lower() in content_lower:
                return True
        return False
```

#### 2.3 TODO 结构扩展

```yaml
# 扩展后的TODO结构
todos:
  - id: "TODO-067"
    content: "评审 v2.2.5 需求分析报告"
    from: "agent2"
    to: "agent1"
    phase: "requirements_review"
    priority: "P0"
    status: "pending"
    created_at: "2026-02-08T22:00:00"
    skill_fragments:  # 新字段
      - id: "review_signoff"
        content: |
          签署信息应写在被评审的文档里，不是TODO里！
        source: "oc_collab_collaboration_guide#评审反馈TODO体系"
```

---

### 3. Skill 切片 + 检索

#### 3.1 切片策略

```python
# scripts/skill_slicer.py

class SkillSlicer:
    """Skill切片器"""
    
    # 切片规则
    SLICING_RULES = {
        "oc_collab_collaboration_guide": [
            {"start": "## 协作规则", "end": "## TODO 任务管理规范", "tags": ["协作", "规则"]},
            {"start": "## TODO 任务管理规范", "end": "## Git 协作规范", "tags": ["TODO", "任务管理"]},
            {"start": "## Git 协作规范", "end": "## 签署流程", "tags": ["Git", "协作"]},
            {"start": "## 签署流程", "end": "## 阶段推进", "tags": ["签署", "流程"]},
            {"start": "## 阶段推进", "end": "## 合规检查", "tags": ["阶段", "推进"]},
        ],
        "oc_collab_bug_management_guide": [
            {"start": "## Bug处理流程", "end": "## Bug闭环环节", "tags": ["Bug", "处理", "流程"]},
            {"start": "## Bug闭环环节", "end": "## 常见错误", "tags": ["验收", "签署", "闭环"]},
        ],
        # ... 其他skill
    }
    
    def slice(self, skill_file: str) -> list[dict]:
        """将skill文件切片"""
        # 实现切片逻辑
        pass
```

#### 3.2 标签系统

```python
# 标签设计

TAGS = {
    # 操作类型标签
    "操作类型": ["评审", "修复", "测试", "签署", "创建", "部署", "设计"],
    
    # 阶段标签
    "阶段": ["requirements", "design", "development", "testing", "deployment"],
    
    # 角色标签
    "角色": ["Agent1", "Agent2", "产品经理", "开发"],
    
    # 流程标签
    "流程": ["TODO", "签署", "验收", "评审", "Bug处理"],
}

def generate_tags(content: str) -> list[str]:
    """基于内容生成标签"""
    tags = []
    for category, keywords in TAGS.items():
        for keyword in keywords:
            if keyword.lower() in content.lower():
                tags.append(f"{category}:{keyword}")
    return tags
```

#### 3.3 检索接口

```python
# src/core/skill_retriever.py

class SkillRetriever:
    """Skill检索器"""
    
    def __init__(self, fragments_file: str = "state/skill_fragments.yaml"):
        self.fragments = self._load_fragments(fragments_file)
    
    def retrieve(self, query: str, max_results: int = 3) -> list[dict]:
        """检索相关片段"""
        # 基于标签的检索
        query_tags = self._parse_query(query)
        
        results = []
        for fragment in self.fragments:
            if self._matches_tags(query_tags, fragment["tags"]):
                results.append(fragment)
        
        return results[:max_results]
    
    def _parse_query(self, query: str) -> list[str]:
        """解析查询，提取标签"""
        # 简单实现：按空格分割，匹配标签
        words = query.lower().split()
        return [w for w in words if w in self._all_tags()]
    
    def _matches_tags(self, query_tags: list[str], fragment_tags: list[str]) -> bool:
        """检查是否匹配"""
        return any(q in fragment_tags for q in query_tags)
```

#### 3.4 CLI检索命令

```python
# src/cli/skill_commands.py

@click.command(name="retrieve")
@click.argument("query")
@click.option("--max", default=3, help="最大返回数量")
def skill_retrieve_command(query: str, max: int):
    """检索skill片段
    
    示例:
      oc-collab skill retrieve "评审 TODO"
      oc-collab skill retrieve "修复 Bug"
      oc-collab skill retrieve "签署 规范"
    """
    from ..core.skill_retriever import SkillRetriever
    
    retriever = SkillRetriever()
    results = retriever.retrieve(query, max)
    
    if not results:
        click.echo(f"未找到相关片段: {query}")
        return
    
    click.echo(f"\n🔍 检索结果: {query}\n")
    
    for i, fragment in enumerate(results, 1):
        click.echo(f"{i}. [{fragment['id']}] {fragment['source']}")
        click.echo(f"   标签: {', '.join(fragment['tags'])}")
        click.echo(f"\n   {fragment['content'][:200]}...")
        click.echo()

# skill命令增强
@click.group()
def skill_group():
    """Skill管理命令"""
    pass

skill_group.add_command(skill_check_command, "check")
skill_group.add_command(skill_status_command, "status")
skill_group.add_command(skill_retrieve_command, "retrieve")
```

#### 3.5 检索示例

```bash
# 示例1：检索评审TODO相关
$ oc-collab skill retrieve "评审 TODO"

🔍 检索结果: 评审 TODO

1. [review_signoff] oc_collab_collaboration_guide#评审反馈TODO体系
   标签: 流程:评审, 操作类型:签署, 任务管理:TODO

   ## 评审反馈TODO体系
   
   **原则**：TODO是短程"通知-完成"结构
   
   Agent2评审 → TODO设为complete
   如需Agent1反馈 → Agent2创建新TODO给Agent1
   **重要**：签署信息应写在被评审的文档里！

---

# 示例2：检索Bug修复流程
$ oc-collab skill retrieve "修复 Bug"

🔍 检索结果: 修复 Bug

1. [bug_fix_flow] oc_collab_bug_management_guide#Bug处理流程
   标签: 流程:Bug处理, 操作类型:修复

   ## Bug处理流程
   
   1. 发现Bug → 创建Bug报告
   2. 创建TODO分配给Agent2（只创建修复的TODO）
   3. Agent2修复
   4. Agent1验收（签署在Bug报告里）

---

# 示例3：检索签署规范
$ oc-collab skill retrieve "签署 规范"

🔍 检索结果: 签署 规范

1. [signoff_rules] oc_collab_collaboration_guide#签署流程
   标签: 流程:签署, 操作类型:签署

   ## 签署规范
   
   - 只有签署后才能推进阶段
   - 签署必须有实质性内容
   - 签署信息应写在对应文档里
```

---

## 实现计划

### Phase 1: todowrite 自动检查 (1h)

| 任务 | 工时 |
|------|------|
| 创建 norm_checker.py | 0.5h |
| 集成到 todowrite | 0.5h |

### Phase 2: TODO 上下文携带 (2h)

| 任务 | 工时 |
|------|------|
| 创建 skill_fragments.yaml | 0.5h |
| 实现片段嵌入器 | 0.5h |
| 扩展TODO数据结构 | 0.5h |
| 集成到 todowrite | 0.5h |

### Phase 3: Skill 切片 + 检索 (3h)

| 任务 | 工时 |
|------|------|
| 创建切片脚本 | 1h |
| 生成 skill_fragments.yaml | 0.5h |
| 实现检索器 | 1h |
| 创建 CLI 命令 | 0.5h |

### 总工时: 6h

---

## 影响分析

### 需要修改的组件

| 组件 | 修改内容 |
|------|----------|
| `src/core/norm_checker.py` | 新增 - 规范检查器 |
| `src/core/skill_fragments.yaml` | 新增 - skill片段存储 |
| `src/core/todo_fragment_embedder.py` | 新增 - TODO片段嵌入器 |
| `src/core/skill_retriever.py` | 新增 - 片段检索器 |
| `src/cli/enhanced_commands.py` | 修改 - todowrite 集成检查 |
| `src/cli/skill_commands.py` | 修改 - 添加 retrieve 命令 |
| `state/agent_adhoc_todos.yaml` | 修改 - TODO 结构扩展 |

### 受影响的 Skill

| Skill | 影响 |
|-------|------|
| `oc_collab_collaboration_guide` | CLI命令帮助增强 |
| `oc_collab_bug_management_guide` | 片段提取 |
| 所有 Skill | 切片处理 |

---

## 验证方法

### 测试用例

```bash
# 1. todowrite 规范检查测试
python3 -m pytest tests/test_norm_checker.py -v

# 2. TODO 片段嵌入测试
python3 -m pytest tests/test_todo_fragment_embedder.py -v

# 3. Skill 检索测试
python3 -m pytest tests/test_skill_retriever.py -v

# 4. 集成测试
python3 -m pytest tests/test_norm_assistance_system.py -v
```

### 验收标准

| 验收项 | 标准 |
|--------|------|
| todowrite 检查 | "评审" 关键词触发提醒 |
| TODO 片段嵌入 | 接收方能看到相关片段 |
| Skill 检索 | "评审 TODO" 能返回相关片段 |

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 规则不全面 | 部分场景遗漏检查 | 提供手动覆盖机制 |
| 片段过多 | TODO 信息冗长 | 限制最多3个片段 |
| 检索不准确 | 返回无关片段 | 持续优化标签系统 |

---

## 附录

### A. 规则定义示例

```yaml
# state/norm_rules.yaml
rules:
  - keyword: "评审"
    reminder: "签署应写在文档里，不是TODO里"
    tags: ["评审", "TODO"]
    
  - keyword: "修复"
    reminder: "修复前检查是否已创建Bug报告"
    tags: ["修复", "Bug"]
    
  - keyword: "测试"
    reminder: "测试验收在 test 阶段执行"
    tags: ["测试", "验收"]
    
  - keyword: "签署"
    reminder: "签署应有实质性内容"
    tags: ["签署", "流程"]
    
  - keyword: "创建"
    reminder: "只创建当前步骤的TODO"
    tags: ["创建", "TODO"]
```

### B. Skill 切片配置文件

```yaml
# state/skill_slicing_config.yaml
slicing:
  oc_collab_collaboration_guide:
    - section: "协作规则"
      tags: ["协作", "规则"]
      
    - section: "TODO任务管理"
      tags: ["TODO", "任务管理"]
      
    - section: "Git协作"
      tags: ["Git", "协作"]
      
    - section: "签署流程"
      tags: ["签署", "流程"]
      
  oc_collab_bug_management_guide:
    - section: "Bug处理流程"
      tags: ["Bug", "处理", "流程"]
      
    - section: "验收闭环"
      tags: ["验收", "签署", "闭环"]
```

---

**创建人**: Agent 2
**创建日期**: 2026-02-08
**状态**: 待评审
