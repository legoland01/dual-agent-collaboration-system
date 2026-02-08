# Proposal: v2.2.4 CLI设计命令支持

**提案编号**: PROPOSAL-v2.2.4-CLI-001
**版本**: v1
**创建日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**状态**: 待评审

---

## 背景

v2.2.4 引入了设计流程分离：
- **概要设计**：Agent 1 负责，功能视角
- **详细设计**：Agent 2 负责，技术视角

现有CLI `design`命令只支持单一设计文档，需要扩展以支持两种设计类型。

---

## 需求

### 新增命令

| 命令 | 说明 | 责任人 | 权限 |
|------|------|--------|------|
| `oc-collab design outline` | 概要设计管理 | Agent 1 | Agent 1创建/编辑 |
| `oc-collab design detail` | 详细设计管理 | Agent 2 | Agent 2创建/编辑 |

### 命令行为

#### `oc-collab design outline`

| 子命令 | 说明 |
|--------|------|
| `oc-collab design outline create` | 创建概要设计文档 |
| `oc-collab design outline edit <file>` | 编辑概要设计文档 |
| `oc-collab design outline view <file>` | 查看概要设计文档 |
| `oc-collab design outline list` | 列出所有概要设计文档 |

#### `oc-collab design detail`

| 子命令 | 说明 |
|--------|------|
| `oc-collab design detail create` | 创建详细设计文档 |
| `oc-collab design detail edit <file>` | 编辑详细设计文档 |
| `oc-collab design detail view <file>` | 查看详细设计文档 |
| `oc-collab design detail list` | 列出所有详细设计文档 |

### 权限控制

| 角色 | 概要设计 | 详细设计 |
|------|----------|----------|
| Agent 1 | ✅ 创建/编辑/查看 | ❌ 仅查看 |
| Agent 2 | ❌ 仅查看 | ✅ 创建/编辑/查看 |

### 文件命名规则

| 类型 | 前缀 | 示例 |
|------|------|------|
| 概要设计 | `OUTLINE_DESIGN_` | `OUTLINE_DESIGN_v2.2.4.md` |
| 详细设计 | `DETAIL_` | `DETAIL_v2.2.4.md` |

---

## 实现方案

### 1. 修改 `src/cli/main.py`

将现有 `design` 命令改为分组命令：

```python
@main.group("design")
def design_group():
    """设计文档管理。"""
    pass

@design_group.command("outline")
@click.argument("action", type=click.Choice(["create", "edit", "view", "list"]), default="list")
@click.argument("target", default="")
def outline_command(action: str, target: str):
    """概要设计管理（Agent 1 专用）。"""
    pass

@design_group.command("detail")
@click.argument("action", type=click.Choice(["create", "edit", "view", "list"]), default="list")
@click.argument("target", default="")
def detail_command(action: str, target: str):
    """详细设计管理（Agent 2 专用）。"""
    pass
```

### 2. 权限检查

在 `compliance_engine.py` 中增加概要设计权限检查：

```python
def check_design_permission(agent_id: str, design_type: str, action: str) -> bool:
    """检查设计文档操作权限。"""
    if design_type == "outline":
        return agent_id == "agent1"  # 只有Agent 1能操作概要设计
    elif design_type == "detail":
        return agent_id == "agent2"  # 只有Agent 2能操作详细设计
    return False
```

### 3. 文件检测

自动识别设计文档类型：

```python
def detect_design_type(file_path: str) -> str:
    """识别设计文档类型。"""
    if file_path.startswith("OUTLINE_"):
        return "outline"
    elif file_path.startswith("DETAIL_"):
        return "detail"
    return "unknown"
```

---

## 验收标准

- [ ] `oc-collab design outline create` 命令可用
- [ ] `oc-collab design detail create` 命令可用
- [ ] Agent 1 无法创建/编辑详细设计
- [ ] Agent 2 无法创建/编辑概要设计
- [ ] 单元测试覆盖权限边界

---

## 工时预估

| 任务 | 工时 |
|------|------|
| CLI命令实现 | 3h |
| 权限检查增强 | 1h |
| 单元测试 | 2h |
| **总计** | **6h** |

---

## 依赖

| 依赖 | 说明 |
|------|------|
| `src/cli/main.py` | CLI入口 |
| `src/core/compliance_engine.py` | 权限检查 |
| `docs/02-design/TEMPLATE_outline_design.md` | 概要设计模板 |
| `docs/02-design/TEMPLATE_detailed_design.md` | 详细设计模板 |

---

## 风险与应对

| 风险 | 可能性 | 影响 | 应对 |
|------|--------|------|------|
| 现有设计命令兼容 | 低 | 中 | 提供 `design` 别名兼容 |

---

## 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-08 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT
