"""规则自动加载模块

F-INIT-002: 规则自动加载
oc-collab init时自动生成AGENTS.md和skills目录
"""
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RulesAutoLoader:
    """规则自动加载器"""

    DEFAULT_SKILLS = [
        "oc_collab_requirements_guide",
        "oc_collab_requirements_review_guide",
        "oc_collab_outline_design_guide",
        "oc_collab_detailed_design_guide",
        "oc_collab_development_guide",
        "oc_collab_test_acceptance_guide",
        "oc_collab_deployment_guide",
        "oc_collab_bug_management_guide",
        "oc_collab_collaboration_guide",
        "oc_collab_agent_role_check",
        "oc_collab_todo_dependency_check",
    ]

    DEFAULT_FILES = [
        ("AGENTS.md", "核心协作规则"),
    ]

    def __init__(self, project_path: Optional[str] = None):
        """
        初始化规则自动加载器

        Args:
            project_path: 项目路径，默认当前目录
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.skills_path = self.project_path / "skills"
        self.memos_path = self.project_path / "docs" / "00-memos"

    def load_default_rules(self, force: bool = False) -> Dict:
        """
        加载默认规则

        Args:
            force: 是否强制覆盖已存在的文件

        Returns:
            Dict: 加载结果
        """
        result = {
            "loaded": [],
            "skipped": [],
            "errors": [],
        }

        for skill_name in self.DEFAULT_SKILLS:
            skill_result = self._load_skill(skill_name, force)
            if skill_result["success"]:
                result["loaded"].append(skill_name)
            elif skill_result["skipped"]:
                result["skipped"].append(skill_name)
            else:
                result["errors"].append(skill_result["error"])

        for filename, description in self.DEFAULT_FILES:
            file_result = self._copy_file(filename, force)
            if file_result["success"]:
                result["loaded"].append(filename)
            elif file_result["skipped"]:
                result["skipped"].append(filename)
            else:
                result["errors"].append(file_result["error"])

        return result

    def _load_skill(self, skill_name: str, force: bool = False) -> Dict:
        """
        加载单个Skill

        Args:
            skill_name: Skill名称
            force: 是否强制覆盖

        Returns:
            Dict: 加载结果
        """
        skill_path = self.skills_path / skill_name
        skill_json_path = skill_path / "skill.json"
        skill_content_path = skill_path / "content.md"

        if skill_path.exists():
            if force:
                logger.info(f"强制覆盖Skill: {skill_name}")
            else:
                logger.info(f"Skill已存在，跳过: {skill_name}")
                return {"success": False, "skipped": True, "error": None}

        skill_path.mkdir(parents=True, exist_ok=True)

        content = self._get_skill_template(skill_name)

        skill_content_path.write_text(content, encoding="utf-8")
        logger.info(f"已创建Skill: {skill_name}")

        if skill_json_path.exists():
            logger.info(f"Skill配置文件已存在: {skill_json_path.name}")
        else:
            json_content = self._get_skill_json_template(skill_name)
            skill_json_path.write_text(json_content, encoding="utf-8")
            logger.info(f"已创建Skill配置: {skill_json_path.name}")

        return {"success": True, "skipped": False, "error": None}

    def _copy_file(self, filename: str, force: bool = False) -> Dict:
        """
        复制默认文件

        Args:
            filename: 文件名
            force: 是否强制覆盖

        Returns:
            Dict: 复制结果
        """
        source_path = Path(__file__).parent.parent.parent / filename
        target_path = self.project_path / filename

        if target_path.exists():
            if force:
                logger.info(f"强制覆盖文件: {filename}")
            else:
                logger.info(f"文件已存在，跳过: {filename}")
                return {"success": False, "skipped": True, "error": None}

        shutil.copy2(source_path, target_path)
        logger.info(f"已复制文件: {filename}")

        return {"success": True, "skipped": False, "error": None}

    def _get_skill_template(self, skill_name: str) -> str:
        """
        获取Skill模板内容

        Args:
            skill_name: Skill名称

        Returns:
            str: Skill内容模板
        """
        templates = {
            "oc_collab_requirements_guide": """# OC-Collab 需求编写指南

**版本**: v8.0.0
**适用阶段**: requirements
**适用角色**: Agent 1 (产品经理)

---

## 快速参考

### 角色分工

| 角色 | 必须做 | 禁止做 |
|------|--------|--------|
| **Agent 1** | 需求文档、黑盒测试、验收签署 | 设计文档、代码、签署"评审通过" |
| **Agent 2** | 评审、设计文档、代码、白盒测试 | 黑盒测试、签署"创建需求" |

---

## 1. 触发条件

**触发关键词**: `session_start`, `before_requirements_review`, `agent_asks_template`

**什么情况下需要创建需求文档？**

```
需求分析完成 ✅
    │
    └── 需求分析报告已创建并评审通过
        └── ANALYSIS_vX.X.X_Requirements_Analysis.md
```

**禁止**：跳过需求分析直接创建需求文档

---

## 2. 操作步骤

| 阶段 | 步骤 | 操作 |
|------|------|------|
| 需求分析 | 1 | 收集相关文档（Proposal/Memo/Bug/Skill） |
| 需求分析 | 2 | 分析每个问题/需求，分类决策 |
| 需求分析 | 3 | 输出需求分析报告 |
| 创建文档 | 4 | 复制模板创建需求文档 |
| 填写文档 | 5 | 填写所有必须字段，明确验收标准 |
| 评审 | 6 | Agent 2 评审并签署 |
| 发布 | 7 | 双签后状态改为 APPROVED |

---

**维护者**: Agent 1
**更新日期**: 2026-02-08
""",
            "oc_collab_requirements_review_guide": """# OC-Collab 需求评审指南

**快速参考**

### 角色分工

| 角色 | 必须做 | 禁止做 |
|------|--------|--------|
| **Agent 1** | 需求文档、黑盒测试、验收签署 | 设计文档、代码、签署"评审通过" |
| **Agent 2** | 评审、设计文档、代码、白盒测试 | 黑盒测试、签署"创建需求" |

---

## 7个评审视角

评审时必须从以下7个视角检查：

| # | 视角 | 检查点 |
|---|------|--------|
| 1 | **阅读理解** | 是否正确理解需求意图 |
| 2 | **完整性** | 验收标准是否覆盖正常+异常流程 |
| 3 | **一致性** | 与现有体系是否冲突 |
| 4 | **可测试性** | 验收标准是否可验证 |
| 5 | **可行性** | 技术能否实现，有无风险 |
| 6 | **逆向挑刺** | 如果我要否定，能找到什么理由 |
| 7 | **给出结论** | 通过/不通过 + 修改建议 |

---

**维护者**: Agent 1
**更新日期**: 2026-02-08
""",
            "oc_collab_outline_design_guide": """# OC-Collab 概要设计指南

## 快速开始

```bash
# 1. 确认需求已批准 (APPROVED)
# 2. 复制模板
cp docs/02-design/TEMPLATE_outline_design.md docs/02-design/OUTLINE_DESIGN_vX.X.X.md
# 3. 编辑文档
# 4. 状态流转：DRAFT → READY → APPROVED
```

---

## 角色定位

| 角色 | 职责 | 禁止 |
|------|------|------|
| **Agent 1** | 创建概要设计、签署"创建" | 代码实现、技术选型 |
| **Agent 2** | 评审概要设计 | 创建概要设计 |

---

**维护者**: Agent 1
**更新日期**: 2026-02-08
""",
            "oc_collab_detailed_design_guide": """# OC-Collab 详细设计指南

## 快速开始

```bash
# 1. 确认概要设计已批准 (APPROVED)
# 2. 复制模板
cp docs/02-design/TEMPLATE_detailed_design.md docs/02-design/DETAIL_vX.X.X.md
# 3. 编辑文档
# 4. 状态流转：DRAFT → READY → APPROVED
```

---

## 角色定位

| 角色 | 职责 | 禁止 |
|------|------|------|
| **Agent 2** | 创建详细设计、代码实现 | 创建概要设计 |
| **Agent 1** | 评审详细设计 | 代码实现、技术选型 |

---

**维护者**: Agent 2
**更新日期**: 2026-02-08
""",
            "oc_collab_development_guide": """# OC-Collab 开发指南

## 快速开始

```bash
# 1. 确认设计已批准 (APPROVED)
# 2. 复制模板
# 3. 编辑代码
# 4. 编写单元测试
# 5. 运行测试
python3 -m pytest tests/ -v
```

---

## 角色定位

| 角色 | 职责 | 禁止 |
|------|------|------|
| **Agent 2** | 代码实现、白盒测试 | 黑盒测试、签署"验收通过" |
| **Agent 1** | 黑盒测试、验收签署 | 代码实现、白盒测试 |

---

**维护者**: Agent 2
**更新日期**: 2026-02-08
""",
            "oc_collab_test_acceptance_guide": """# OC-Collab 测试验收指南

## 快速参考

### 角色分工

| 角色 | 必须做 | 禁止做 |
|------|--------|--------|
| **Agent 1** | 黑盒测试、验收签署、准备测试用例 | 代码实现、白盒测试 |
| **Agent 2** | 代码实现、白盒测试、开发签署 | 黑盒测试、签署"验收通过" |

---

## 测试时机

```
需求: APPROVED ✅
设计: APPROVED ✅
开发: ⏳ pending → ✅ completed  ← ← ← 此时才能开始测试！
测试: ⏳ pending
验收: ⏳ pending
```

---

**维护者**: Agent 1
**更新日期**: 2026-02-08
""",
            "oc_collab_deployment_guide": """# OC-Collab 部署指南

## 快速开始

```bash
# 1. 确认测试通过
python3 -m pytest tests/ -v

# 2. 更新版本号
# 编辑 pyproject.toml

# 3. 更新CHANGELOG.md

# 4. 发布到PyPI
pip build
twine upload dist/*
```

---

## 角色定位

| 角色 | 职责 | 禁止做 |
|------|------|--------|
| **Agent 1** | 版本发布、CHANGELOG更新、打标签 | - |
| **Agent 2** | - | 版本发布 |

---

**维护者**: Agent 1
**更新日期**: 2026-02-08
""",
            "oc_collab_bug_management_guide": """# OC-Collab Bug管理指南

## Bug报告模板

```markdown
# Bug报告: [简短描述]

**Bug编号**: BUG-YYYYMMDD-XXX
**发现日期**: YYYY-MM-DD
**发现者**: Agent 1/2
**状态**: OPEN
**优先级**: P0/P1/P2

---

## 1. Bug描述

[详细描述问题]

## 2. 影响范围

[影响范围分析]

## 3. 复现步骤

1. [步骤1]
2. [步骤2]

## 4. 修复方案

[建议修复方案]

---

**创建人**: [Agent姓名]
**日期**: YYYY-MM-DD
**状态**: OPEN
```

---

**维护者**: Agent 1
**更新日期**: 2026-02-08
""",
            "oc_collab_collaboration_guide": """# OC-Collab 协作指南 (v2.2.2)

## 快速索引

**遇到问题时，先看这个表格：**

| 问题类型 | 看哪个Skill | 关键章节 |
|----------|-------------|----------|
| 需求怎么写？ | `oc_collab_requirements_guide` | 需求分析、需求文档 |
| 需求怎么评审？ | `oc_collab_requirements_guide` | 评审部分 |
| 设计怎么写？ | `oc_collab_outline_design_guide` | 概要设计 |
| 详细设计怎么写？ | `oc_collab_detailed_design_guide` | 详细设计 |
| 怎么开发？ | `oc_collab_development_guide` | 开发流程 |
| 怎么测试？ | `oc_collab_test_acceptance_guide` | 测试验收 |
| 怎么部署？ | `oc_collab_deployment_guide` | 部署流程 |
| 怎么报Bug？ | `oc_collab_bug_management_guide` | Bug管理 |
| 角色权限？ | `oc_collab_collaboration_guide` | Agent角色定义 |
| 协作流程？ | `oc_collab_collaboration_guide` | 协作流程 |

---

**维护者**: Agent 1
**版本**: v2.2.2
**更新日期**: 2026-02-08
""",
            "oc_collab_agent_role_check": """# Agent角色权限检查

## 角色权限矩阵

| 操作 | Agent 1 | Agent 2 |
|------|---------|---------|
| 创建需求文档 | ✅ | ❌ |
| 创建概要设计 | ✅ | ❌ |
| 创建详细设计 | ❌ | ✅ |
| 代码实现 | ❌ | ✅ |
| 评审需求 | ✅ | ✅ |
| 评审设计 | ✅ | ✅ |
| 签署需求 | ✅ (创建人) / ❌ (评审人) | ✅ (评审人) / ❌ (创建人) |
| 签署设计 | ✅ (评审人) / ❌ (创建人) | ✅ (创建人) / ❌ (评审人) |
| 黑盒测试 | ✅ | ❌ |
| 白盒测试 | ❌ | ✅ |
| 版本发布 | ✅ | ❌ |

---

**维护者**: Agent 1
**更新日期**: 2026-02-08
""",
            "oc_collab_todo_dependency_check": """# TODO依赖检查

## 触发条件

**trigger**: todo_received

## 功能描述

当收到TODO时，自动检查：
1. 前置TODO是否已完成
2. 相关文档是否存在
3. 依赖关系是否满足

## 使用示例

```
收到TODO: 实现功能X
    │
    ├── 检查前置TODO: 设计文档 ✅
    ├── 检查依赖: API定义 ✅
    └── 输出: 可立即开始执行
```

---

**维护者**: Agent 2
**更新日期**: 2026-02-08
""",
        }

        return templates.get(skill_name, f"# {skill_name}\n\n**注意**: Skill模板待完善\n")

    def _get_skill_json_template(self, skill_name: str) -> str:
        """
        获取Skill JSON配置模板

        Args:
            skill_name: Skill名称

        Returns:
            str: JSON配置内容
        """
        return f"""{{
  "id": "{skill_name}",
  "name": "{skill_name.replace('_', ' ').title()}",
  "version": "1.0.0",
  "description": "OC-Collab协作Skill",
  "triggers": ["session_start"],
  "permissions": ["read"],
  "maintainer": "Agent 1"
}}
"""

    def check_rules_status(self) -> Dict:
        """
        检查规则加载状态

        Returns:
            Dict: 状态信息
        """
        status = {
            "initialized": [],
            "missing": [],
        }

        for skill_name in self.DEFAULT_SKILLS:
            skill_path = self.skills_path / skill_name
            if skill_path.exists():
                status["initialized"].append(skill_name)
            else:
                status["missing"].append(skill_name)

        for filename, _ in self.DEFAULT_FILES:
            file_path = self.project_path / filename
            if file_path.exists():
                status["initialized"].append(filename)
            else:
                status["missing"].append(filename)

        return status
