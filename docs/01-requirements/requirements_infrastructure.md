# 基础设施需求文档：Agent 上下文与 Skill 机制

**版本**: v1
**创建日期**: 2026-02-07
**作者**: Agent 1 (产品经理)
**状态**: DRAFT (待评审)

---

## 1. 概述

### 1.1 背景

OC-Collab 开发过程中发现一个**根本性问题**：

- Compaction 后、Session 重启后，Agent 会"忘记"自己的身份和协作规则
- 现有的 Skill 机制声明了 `session_start` 触发条件，但从未被正确实现
- Agent 1 反复越权、混淆职责，每次都被提醒

### 1.2 问题本质

| 问题 | 表现 | 根因 |
|------|------|------|
| 身份遗忘 | Compaction 后忘记职责 | 没有即时上下文恢复 |
| 协作规则丢失 | 不知道自己能做什么 | 没有轻量级规则加载 |
| Skill 机制失效 | skill.json 配置了但没触发 | 代码实现缺失 + 路径错误 |

### 1.3 解决方案

采用**分层上下文机制**：

| 层级 | 机制 | 用途 | 复杂度 |
|------|------|------|--------|
| **L0 极简上下文** | `.a` 文件 | 用户身份、当前阶段、协作规则摘要 | 低 |
| **L1 扩展知识** | Skill 机制 | 复杂项目知识、技能、动态加载 | 中 |

---

## 2. 功能需求

### 2.1 F-CONTEXT-001: 极简上下文机制

**需求编号**: F-CONTEXT-001

**核心设计**: 用户只需记住一句话，AI 自动加载上下文。

#### 2.1.1 `.a` 文件格式

**文件名**: `.a` (极简短)

**文件内容**:

```yaml
# .a 极简上下文文件
# 格式: YAML
# 说明: 轻量级上下文，快速恢复 Agent 身份和协作规则

agent_id: agent1
phase: requirements_review
milestone: v2.2.2
role: 产品经理

responsibilities:
  - 编写需求文档
  - 编写黑盒测试
  - 执行测试
  - 部署发布

forbidden:
  - 触碰代码文件 (src/)
  - 创建设计文档 (docs/02-design/)
  - 签署需求文档

pending_tasks:
  - TODO-034: 评审 REQ-CONTEXT-001 需求
  - TODO-035: 评审 REQ-INIT-001 需求

last_reminder: "你是产品经理，不要触碰代码"
```

#### 2.1.2 交互设计

**用户操作**:

```
用户: "你是 agent1"
AI:   (自动读取 .a 文件)
      === 欢迎回来，Agent 1 (产品经理) ===

      当前阶段: requirements_review
      当前里程碑: v2.2.2

      你的职责:
        - 编写需求文档
        - 编写黑盒测试
        - 执行测试
        - 部署发布

      你不能做:
        - 触碰代码文件 (src/)
        - 创建设计文档 (docs/02-design/)
        - 签署需求文档

      待办任务:
        - TODO-034: 评审 REQ-CONTEXT-001 需求
        - TODO-035: 评审 REQ-INIT-001 需求

      下一步: 查看待办任务 - oc-collab todo
```

#### 2.1.3 验收标准

- [ ] `.a` 文件格式为 YAML
- [ ] 文件名极简短: `.a`
- [ ] 用户只需说"你是 agent1"，AI 自动读取并显示摘要
- [ ] 显示职责列表
- [ ] 显示禁止事项列表
- [ ] 显示待办任务列表
- [ ] 显示当前阶段和里程碑

#### 2.1.4 工时预估

| 功能 | 预估时间 | 复杂度 |
|------|----------|--------|
| `.a` 文件格式定义 | 0.5h | 低 |
| 读取和解析 `.a` 文件 | 1h | 低 |
| 生成欢迎消息 | 1h | 低 |
| 集成到 CLI 入口 | 1h | 低 |

**总计**: 3.5h

---

### 2.2 F-INIT-001: 智能初始化

**需求编号**: F-INIT-001

**核心设计**: 检测 `.a` 文件，已存在则跳过初始化；不存在则创建。

#### 2.2.1 初始化逻辑

```
oc-collab init <project_name>
    │
    ├─ 检测项目目录是否存在 .a 文件
    │
    ├─ .a 存在
    │   └─ 跳过初始化，显示"项目已初始化"
    │
    └─ .a 不存在
        ├─ 创建项目目录结构
        ├─ 创建 .a 文件 (包含 agent_id=None, phase=init)
        ├─ 创建 docs/ 目录结构
        ├─ 创建 state/ 目录结构
        └─ 完成初始化
```

#### 2.2.2 初始化后行为

**场景 1**: 新项目

```
$ oc-collab init myproject
✓ 项目 myproject 初始化成功
✓ 已创建 .a 文件
✓ 已创建 docs/ 目录
✓ 已创建 state/ 目录

下一步:
1. 进入项目目录: cd myproject
2. 设置 Agent 身份: "你是 agent1"
3. 查看状态: oc-collab status
```

**场景 2**: 已有项目 (存在 .a)

```
$ oc-collab init myproject
⚠️ 项目 myproject 已初始化 (.a 文件存在)
如需重新初始化，请先删除 .a 文件

当前状态:
- Agent: 未设置 (请说"你是 agent1" 或 "你是 agent2")
- 阶段: 未定义
```

#### 2.2.3 验收标准

- [ ] `oc-collab init` 检测 `.a` 文件
- [ ] `.a` 存在时跳过初始化，显示提示
- [ ] `.a` 不存在时创建项目结构
- [ ] 创建 `.a` 文件，包含 agent_id=None, phase=init
- [ ] 创建 `docs/` 和 `state/` 目录结构

#### 2.2.4 工时预估

| 功能 | 预估时间 | 复杂度 |
|------|----------|--------|
| 检测 .a 文件 | 0.5h | 低 |
| 创建目录结构 | 0.5h | 低 |
| 生成 .a 文件 | 0.5h | 低 |
| CLI 集成 | 0.5h | 低 |

**总计**: 2h

---

### 2.3 F-SKILL-001: 修复 Skill 机制

**需求编号**: F-SKILL-001

**核心设计**: 修复 SkillLoader 路径错误，实现正确的 skill 加载。

#### 2.3.1 问题描述

**现有代码问题**:

```python
# cognitive_immune.py 第220行
guide_file = self.skills_dir / "collaboration_guide.md"  # ❌ 错误路径

# 实际文件路径
skills/oc_collab_collaboration_guide/content.md           # ✅ 正确路径
```

**结果**: skill.json 配置了但从未被加载。

#### 2.3.2 修复方案

```python
class SkillLoader:
    def load_collaboration_guide(self):
        # 修复前
        guide_file = self.skills_dir / "collaboration_guide.md"  # ❌

        # 修复后
        guide_file = self.skills_dir / "oc_collab_collaboration_guide" / "content.md"  # ✅
```

#### 2.3.3 验收标准

- [ ] SkillLoader 正确加载 `skills/oc_collab_collaboration_guide/content.md`
- [ ] skill.json 触发条件 (`session_start`, `agent_confused`) 被正确注册
- [ ] `oc-collab switch` 后自动加载协作指南

#### 2.3.4 工时预估

| 功能 | 预估时间 | 复杂度 |
|------|----------|--------|
| 修复 SkillLoader 路径 | 0.5h | 低 |
| 测试 skill 加载 | 0.5h | 低 |

**总计**: 1h

---

### 2.4 F-SKILL-002: Skill 触发机制

**需求编号**: F-SKILL-002

**核心设计**: 实现 skill.json 中声明的触发条件。

#### 2.4.1 触发条件

```json
// skills/oc_collab_collaboration_guide/skill.json

"triggers": [
  {
    "condition": "session_start",
    "priority": "high"
  },
  {
    "condition": "agent_confused",
    "priority": "high"
  },
  {
    "condition": "role_boundary_check",
    "priority": "medium"
  }
]
```

#### 2.4.2 触发实现

| 触发条件 | 实现位置 | 行为 |
|----------|----------|------|
| `session_start` | CLI 入口 `main()` | 显示欢迎消息 + 加载协作指南 |
| `agent_confused` | `CognitiveImmuneSystem` | 检测困惑信号后加载协作指南 |
| `role_boundary_check` | 敏感操作前 | 检查职责边界 |

#### 2.4.3 代码实现

```python
# src/cli/main.py

@click.group()
def main():
    """双Agent协作框架 CLI工具。"""
    # P0: Session 启动时自动触发
    session_manager = SessionManager(project_path)
    active_agent = state_manager.get_active_agent()
    session_manager.show_welcome(active_agent)  # 显示欢迎消息
    session_manager.load_skill("session_start")  # 加载 Skill
    pass
```

#### 2.4.4 验收标准

- [ ] `session_start` 触发: CLI 入口自动调用
- [ ] `agent_confused` 触发: 困惑信号检测后自动调用
- [ ] `role_boundary_check` 触发: 敏感操作前检查
- [ ] Skill 内容正确加载和显示

#### 2.4.5 工时预估

| 功能 | 预估时间 | 复杂度 |
|------|----------|--------|
| session_start 触发实现 | 1h | 低 |
| agent_confused 触发实现 | 1h | 低 |
| role_boundary_check 触发实现 | 2h | 中 |
| 测试所有触发条件 | 1h | 低 |

**总计**: 5h

---

## 3. 架构设计

### 3.1 分层上下文机制

```
用户输入: "你是 agent1"
    │
    ├─ L0 极简上下文
    │   └─ 读取 .a 文件
    │       ├─ agent_id
    │       ├─ phase
    │       ├─ responsibilities
    │       └─ pending_tasks
    │
    └─ L1 扩展知识 (Skill)
        └─ 加载 skill.json 中的协作指南
            ├─ session_start: 显示欢迎消息
            ├─ agent_confused: 加载困惑解决方案
            └─ role_boundary_check: 检查职责边界

    输出:
        === Agent 1 (产品经理) ===
        当前阶段: requirements_review
        ...
```

### 3.2 文件结构

```
oc-collab 项目/
├── .a                          # 极简上下文 (L0)
├── skills/
│   └── oc_collab_collaboration_guide/
│       ├── skill.json          # Skill 配置
│       └── content.md          # 协作指南 (L1)
├── src/
│   └── core/
│       ├── session_manager.py  # L0 + L1 集成
│       └── cognitive_immune.py # 困惑检测
└── docs/
    └── 01-requirements/
        └── requirements_infrastructure.md  # 本需求文档
```

---

## 4. 非功能需求

### 4.1 性能需求

| 需求项 | 要求 |
|--------|------|
| `.a` 文件读取 | ≤ 100ms |
| Skill 加载 | ≤ 200ms |

### 4.2 兼容性需求

| 需求项 | 要求 |
|--------|------|
| `.a` 文件格式 | YAML |
| Skill 格式 | JSON + Markdown |
| Python 版本 | ≥ 3.8 |

---

## 5. 验收标准汇总

| 功能 | 验收项 | 状态 |
|------|--------|------|
| F-CONTEXT-001 | `.a` 文件格式正确 | ⏳ |
| F-CONTEXT-001 | 用户说"你是 agent1" 自动显示职责 | ⏳ |
| F-CONTEXT-001 | 显示禁止事项 | ⏳ |
| F-CONTEXT-001 | 显示待办任务 | ⏳ |
| F-INIT-001 | 检测 `.a` 文件，已存在则跳过 | ⏳ |
| F-INIT-001 | 不存在时创建项目结构 | ⏳ |
| F-SKILL-001 | SkillLoader 路径正确 | ⏳ |
| F-SKILL-001 | skill.json 正确加载 | ⏳ |
| F-SKILL-002 | session_start 触发实现 | ⏳ |
| F-SKILL-002 | agent_confused 触发实现 | ⏳ |
| F-SKILL-002 | role_boundary_check 触发实现 | ⏳ |

---

## 6. 开发顺序

| 顺序 | 功能 | 理由 |
|------|------|------|
| 1 | F-SKILL-001 | 修复 SkillLoader 路径 |
| 2 | F-SKILL-002 | 实现 session_start 触发 |
| 3 | F-CONTEXT-001 | 实现 .a 文件 |
| 4 | F-INIT-001 | 实现智能初始化 |

---

## 7. 工时预估

| 功能 | 预估时间 | 复杂度 |
|------|----------|--------|
| F-SKILL-001 | 1h | 低 |
| F-SKILL-002 | 5h | 中 |
| F-CONTEXT-001 | 3.5h | 低 |
| F-INIT-001 | 2h | 低 |

**总计**: 11.5h

---

## 8. 风险分析

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| OpenCode 不支持自动触发 session_start | 中 | 高 | L0 机制作为兜底 |
| Skill 机制与 OpenCode 集成复杂 | 低 | 中 | 先实现 L0，再完善 L1 |

---

## 9. 签署确认

### Agent 1 确认

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-07 | ⏳ |

### Agent 2 技术评审

| 评审项 | 结论 | 日期 |
|--------|------|------|
| F-CONTEXT-001 设计合理性 | ⏳ | |
| F-INIT-001 技术可行性 | ⏳ | |
| F-SKILL-001 实现正确性 | ⏳ | |
| F-SKILL-002 触发机制 | ⏳ | |

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-07 | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-07
**状态**: DRAFT (待 Agent2 评审)

---

## 附录 A: 参考文档

| 文档编号 | 文档名称 | 说明 |
|----------|----------|------|
| TODO-034 | REQ-CONTEXT-001 原始需求 | Agent 上下文自动恢复 |
| TODO-035 | REQ-INIT-001 原始需求 | 智能初始化 |
| cognitive_immune.py | 认知免疫系统 | 现有代码 |
| session_manager.py | 会话管理器 | 现有代码 |
| skill.json | Skill 配置 | 现有配置 |

---

## 附录 B: 术语表

| 术语 | 定义 |
|------|------|
| L0 极简上下文 | `.a` 文件，轻量级上下文恢复 |
| L1 扩展知识 | Skill 机制，复杂知识动态加载 |
| Compaction | OpenCode 会话压缩/重启 |
| Session | OpenCode 会话 |
