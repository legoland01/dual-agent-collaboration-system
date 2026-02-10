# Proposal: oc-collab 规则自动加载机制

**提案人**: Agent 1  
**日期**: 2026-02-10  
**目标版本**: v2.2.8 或后续版本  
**状态**: 待评审

---

## 1. 问题背景

oc-collab 采用 Agent1/Agent2 双代理协作模式：
- Agent1: 发现问题 → 创建TODO → 记录文档
- Agent2: 执行代码 → 修复Bug → 合并到分支

**当前问题**：
1. 规则依赖用户手动创建 `AGENTS.md`，容易遗漏
2. 新用户不知道需要配置什么规则
3. 老项目想用 oc-collab 时没有现成规则可用
4. Compaction 后规则容易丢失

---

## 2. 解决方案

### 2.1 内置默认规则

oc-collab 内置 `AGENTS.md` 默认规则，包含：
- Agent1/Agent2 分工定义
- 关键规则：Agent1 不直接改代码
- 引用文件路径（TODO、Bug报告位置）

**效果**：任何项目直接使用 oc-collab 时自动加载规则，无需配置。

### 2.2 模板初始化命令

提供 `oc-collab init` 命令：
```
oc-collab init
```

自动生成：
```
project/
├── AGENTS.md           # 内置规则（可覆盖）
├── state/
│   └── agent_adhoc_todos.yaml
├── docs/
│   └── 00-memos/
├── skills/
└── README.md
```

**效果**：新项目快速初始化，结构一致。

### 2.3 项目级规则覆盖

项目可创建 `AGENTS.md` 覆盖默认规则：
- 继承内置规则
- 添加项目特定规则
- 调整 Agent 分工

**效果**：灵活定制，不影响工具默认行为。

---

## 3. 用户场景

| 场景 | 用户操作 | 系统行为 |
|------|----------|----------|
| **新项目** | `oc-collab init` | 生成目录结构 + 内置规则 |
| **老项目** | 直接用命令 | 自动加载内置规则 |
| **特殊项目** | 创建自定义 AGENTS.md | 覆盖默认规则 |

---

## 4. 优先级

| 优先级 | Feature | 说明 |
|--------|---------|------|
| P1 | 内置默认规则 | 基础能力，无则无法工作 |
| P1 | 模板初始化 | 提升用户体验 |
| P2 | 规则覆盖 | 高级功能，非必须 |

---

## 5. 依赖

- 无外部依赖
- 利用 OpenCode 现有的 AGENTS.md 加载机制

---

## 6. 验收标准

- [ ] 任意项目运行 `oc-collab todowrite` 自动加载内置规则
- [ ] `oc-collab init` 命令生成标准目录结构
- [ ] 项目 AGENTS.md 可覆盖内置规则
- [ ] Compaction 后规则不丢失

---

## 7. 估算工时

| 任务 | 工时 |
|------|------|
| 内置默认规则 | 1h |
| `oc-collab init` 命令 | 2h |
| 规则覆盖机制 | 1h |
| 测试 | 1h |
| **总计** | **5h** |

---

## 8. 相关文档

- OpenCode AGENTS.md 机制: https://opencode.ai/docs/rules
- oc-collab AGENTS.md: `AGENTS.md` (已创建)

---

**请评审此提案，决定是否纳入 v2.2.x 规划**
