# PROPOSAL-2026-02-007: Skill强制执行机制增强

**作者**: Agent 1  
**创建日期**: 2026-02-14  
**版本**: v1.0  
**优先级**: P0 (阻塞协作流程)  
**关联BUG**: BUG-20260214-005 (Skill查询未遵循)

---

## 1. 背景与问题

### 1.1 当前状态

**AGENTS.md 规则明确要求**：

```
## Skill 查询规则 ⭐

**永远不要直接问用户，先查Skill**

1. **遇到问题时的处理顺序**：
   - Step 1: 查阅 `skills/` 目录下的相关Skill
   - Step 2: 使用 `oc-collab skill search --keywords <关键词>` 搜索
   - Step 3: 如果Skill有SOP四要素，按照步骤执行
   - Step 4: 如果Skill找不到或觉得困惑，再问用户

2. **禁止行为**：
   - ❌ 直接问用户"要怎么做？"
   - ❌ 不查Skill就凭经验操作
   - ❌ 跳过Skill中规定的流程步骤

3. **强制要求**：
   - 每次部署发布前必须查阅 `oc_collab_deployment_guide`
   - 每次处理Bug前必须查阅 `oc_collab_bug_management_guide`
   - 每次创建需求前必须查阅 `oc_collab_requirements_guide`
```

### 1.2 问题描述

| 问题 | 现象 | 根因 |
|------|------|------|
| Agent不查Skill | 凭经验操作，跳过规定流程 | 规则是文档，无强制力 |
| Skill检查仅警告 | `signoff --auto-check` 仅提示缺失，不阻止 | 当前实现是可选的 |
| Skill加载无机制 | 新项目无法快速获得成熟Skill | 缺少一键迁移功能 |

### 1.3 BUG报告引用

- **BUG-20260214-005**: Skill查询未遵循 - Agent未按规则查Skill

---

## 2. 技术调研结果

### 2.1 现有代码基础

| 组件 | 文件 | 功能 | 问题 |
|------|------|------|------|
| `SkillEnforcer` | `src/core/skill_enforcer.py` | 检查Skill是否加载 | 仅检查目录存在，不验证是否"加载" |
| `skill check` | `src/cli/skill_check_commands.py` | CLI命令检查 | 仅显示状态，无强制力 |
| `signoff`集成 | `main.py:243-253` | 签署时检查Skill | 仅警告，可绕过 (`--auto-check/--no-auto-check`) |

### 2.2 关键代码问题

```python
# 当前 signoff_command 实现 (main.py:243-253)
if auto_check:
    skill_enforcer.check_before_action("signoff")
    
    if skill_result["missing"]:
        click.echo(f"⚠️ 缺少相关Skill...")
        # ⚠️ 问题：仅警告，继续执行！
```

### 2.3 opencode CLI钩子能力

| 命令 | 能否集成Skill检查 |
|------|------------------|
| `oc-collab todowrite` | ✅ 可以，必须检查 |
| `oc-collab signoff` | ✅ 可以，必须检查 |
| `oc-collab review` | ✅ 可以，必须检查 |
| `oc-collab advance` | ✅ 可以，必须检查 |

---

## 3. 解决方案

### 3.1 核心原则

```
✅ 最高可靠性：CLI命令级别强制检查，无法绕过
✅ 符合AGENTS.md规则：Skill规定 → 自动验证 → 不遵守则阻止
✅ 平稳迁移：现有项目兼容，新项目一键初始化
```

### 3.2 方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENTS.md 规则层                          │
│   Skill查询规则 → 强制要求 → 每次处理Bug前查Skill...        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  CLI 命令层 (强制钩子)                        │
│   todowrite → skill enforce --before-action → 缺失则阻止   │
│   signoff   → skill enforce --before-action → 缺失则阻止   │
│   review    → skill enforce --before-action → 缺失则阻止   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Skill 模板层 (一键迁移)                        │
│   templates/skills_template/ → oc-collab init --skill-template│
└─────────────────────────────────────────────────────────────┘
```

### 3.3 实现详情

#### 3.3.1 CLI强制检查 (最高优先级)

**修改文件**: `src/cli/main.py`, `src/cli/todo_commands.py`

```python
# todowrite_command 修改前
def todowrite_command(...):
    # 无Skill检查

# 修改后
def todowrite_command(...):
    # Step 1: 强制检查Skill
    skill_enforcer = SkillEnforcer()
    check_result = skill_enforcer.check_before_action("todowrite")
    
    if check_result["missing"]:
        click.echo(f"\n❌ [FATAL] 缺少必需Skill，无法执行 todowrite")
        click.echo(f"   缺失: {', '.join(check_result['missing'])}")
        click.echo(f"\n💡 解决方法:")
        for skill in check_result["missing"]:
            load_cmd = skill_enforcer.get_load_command(skill)
            click.echo(f"   → 加载: oc-collab {load_cmd}")
        click.echo(f"\n📚 或运行: oc-collab skill check --missing")
        sys.exit(1)  # 强制退出
    
    # Step 2: 执行原逻辑...
```

#### 3.3.2 Skill模板创建

**目录结构**:

```
templates/
├── skills_template/
│   ├── oc_collab_requirements_guide/
│   │   ├── skill.json
│   │   └── content.md
│   ├── oc_collab_requirements_review_guide/
│   │   ├── skill.json
│   │   └── content.md
│   ├── oc_collab_development_guide/
│   │   ├── skill.json
│   │   └── content.md
│   ├── oc_collab_design_guide/
│   │   ├── skill.json
│   │   └── content.md
│   ├── oc_collab_test_acceptance_guide/
│   │   ├── skill.json
│   │   └── content.md
│   ├── oc_collab_deployment_guide/
│   │   ├── skill.json
│   │   └── content.md
│   ├── oc_collab_bug_management_guide/
│   │   ├── skill.json
│   │   └── content.md
│   ├── oc_collab_todo_dependency_check/
│   │   ├── skill.json
│   │   └── content.md
│   └── oc_collab_issue_tracker/
│       ├── skill.json
│       └── content.md
```

#### 3.3.3 init命令增强

**修改文件**: `src/cli/main.py` (init_command)

```python
@main.command("init")
@click.argument("project_name")
@click.option("--type", "-t", ...)
@click.option("--skill-template", "-s", type=click.Choice(["standard", "minimal", "none"]), default="standard")
def init_command(project_name: str, type: str, skill_template: str):
    """初始化协作项目。"""
    # ... 现有逻辑 ...
    
    # 新增: 导入Skill模板
    if skill_template != "none":
        migrate_skills(project_path, skill_template)
```

```python
def migrate_skills(project_path: str, template: str):
    """从模板导入Skill"""
    template_skills = Path(__file__).parent.parent / "templates" / f"skills_{template}"
    target_skills = Path(project_path) / "skills"
    
    if not template_skills.exists():
        click.echo(f"⚠️ Skill模板不存在: {template}")
        return
    
    import shutil
    shutil.copytree(template_skills, target_skills, dirs_exist_ok=True)
    click.echo(f"✅ 已导入Skill模板: {template}")
```

#### 3.3.4 移除 `--auto-check` 可选参数

**原因**: Skill检查必须是强制的，不应该有"跳过"选项。

```python
# signoff_command 修改前
@click.option("--auto-check/--no-auto-check", default=True)

# 修改后
# 删除 --auto-check 选项，强制检查
```

---

## 4. 实施计划

### 4.1 阶段划分

| 阶段 | 内容 | 输出产物 |
|------|------|----------|
| **Phase 1** | CLI强制检查核心命令 | `src/cli/main.py`, `src/cli/todo_commands.py` |
| **Phase 2** | 移除 `--auto-check` 可选参数 | `src/cli/main.py` |
| **Phase 3** | 创建Skill模板 | `templates/skills_standard/` |
| **Phase 4** | 增强init命令 | `src/cli/main.py` |
| **Phase 5** | 测试验收 | `tests/test_skill_enforcement.py` |

### 4.2 详细任务

| 任务ID | 任务描述 | 负责人 | 输出 |
|--------|----------|--------|------|
| TASK-001 | todowrite强制Skill检查 | Agent2 | `src/cli/todo_commands.py` |
| TASK-002 | signoff强制Skill检查（移除--auto-check） | Agent2 | `src/cli/main.py` |
| TASK-003 | review强制Skill检查 | Agent2 | `src/cli/main.py` |
| TASK-004 | advance强制Skill检查 | Agent2 | `src/cli/main.py` |
| TASK-005 | 创建Skill模板目录和文件 | Agent1 | `templates/skills_standard/` |
| TASK-006 | init命令增强（--skill-template） | Agent2 | `src/cli/main.py` |
| TASK-007 | 编写强制检查测试 | Agent1 | `tests/test_skill_enforcement.py` |
| TASK-008 | E2E测试验收 | Agent1 | 测试报告 |

### 4.3 版本规划

| 版本 | 内容 | 目标 |
|------|------|------|
| **v2.2.11** | CLI强制检查 + Skill模板 + init增强 | 最高可靠性 |
| **v2.2.12** | 扩展到更多命令 | 覆盖全部CLI |

---

## 5. 兼容性考虑

### 5.1 现有项目迁移

| 场景 | 解决方案 |
|------|----------|
| 已有项目升级 | 手动运行 `oc-collab skill check --missing` 查看缺失 |
| Skill文件不一致 | 复制 `templates/skills_standard/` 到 `skills/` |

### 5.2 紧急绕过机制

**仅限P0 Bug修复**：

```bash
# 使用环境变量临时跳过（仅限紧急情况）
SKIP_SKILL_ENFORCE=1 oc-collab todowrite ...
```

**限制**:
- 必须记录原因
- 24小时内必须补充Skill
- 超过3次触发需Review

---

## 6. 验收标准

### 6.1 功能验收

| 场景 | 输入 | 预期输出 |
|------|------|----------|
| todowrite无Skill | 缺失 `oc_collab_requirements_guide` | ❌ 拒绝执行，提示加载 |
| signoff无Skill | 缺失 `oc_collab_requirements_review_guide` | ❌ 拒绝执行，提示加载 |
| init导入Skill | `oc-collab init foo --skill-template standard` | ✅ 创建 `skills/` 目录 |
| Skill完整 | 所有必需Skill存在 | ✅ 正常执行 |

### 6.2 回归测试

- `test_state_notifier_e2e.py` 继续通过
- 现有 `oc-collab signoff` 测试通过（需更新期望值）

---

## 7. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| Agent无法启动任务 | 中 | 高 | 提供 `--force` 紧急绕过 |
| Skill模板不完整 | 低 | 中 | 分阶段创建，先覆盖必需 |
| 现有项目无法升级 | 中 | 中 | 提供迁移脚本 |

---

## 8. 关联文档

| 文档 | 说明 |
|------|------|
| `AGENTS.md` | 原始规则来源 |
| `src/core/skill_enforcer.py` | Skill检查核心实现 |
| `src/cli/skill_check_commands.py` | CLI命令实现 |
| `docs/00-memos/BUG-20260214-005_skill_query_not_followed.md` | BUG报告 |
| `templates/` | 模板目录 |

---

## 9. 签署确认

| 角色 | 姓名 | 签署 | 日期 |
|------|------|------|------|
| Agent 1 | | ☐ | |
| Agent 2 | | ☐ | |

---

## 10. 附录

### 10.1 必需Skill清单 (v2.2.11)

| Skill | 关联命令 | 优先级 |
|-------|----------|--------|
| `oc_collab_requirements_guide` | todowrite | P0 |
| `oc_collab_requirements_review_guide` | signoff, review | P0 |
| `oc_collab_development_guide` | signoff | P0 |
| `oc_collab_design_guide` | advance | P0 |
| `oc_collab_test_acceptance_guide` | testing | P0 |
| `oc_collab_deployment_guide` | deployment | P0 |
| `oc_collab_bug_management_guide` | bug处理 | P1 |
| `oc_collab_todo_dependency_check` | todowrite | P1 |

### 10.2 CLI命令Skill映射

| 命令 | 必需Skill | 可选Skill |
|------|-----------|-----------|
| `todowrite` | requirements, collaboration | bug_management |
| `signoff` | requirements_review, development | collaboration |
| `review` | requirements_review | - |
| `advance` | requirements, design | - |
| `deployment` | deployment | - |
| `bug处理` | bug_management | collaboration |

---

**维护者**: Agent 1  
**更新日期**: 2026-02-14
