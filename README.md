# 双 Agent 协作开发系统

基于 OpenCode 的双 Agent 协作框架，实现产品经理与开发的分离式协作。

---

## 安装

```bash
pip install opencode-collaboration
```

---

## 快速开始

### 1. 初始化项目

```bash
# 创建新项目
oc-collab init myproject
cd myproject
```

### 2. 创建需求文档

编辑 `docs/01-requirements/requirements_v*.md` 文件，定义需求。

### 3. 评审并签署

```bash
# Agent 2 (开发) 评审需求
oc-collab review requirements --comment "技术方案可行"

# Agent 1 (产品) 签署确认
oc-collab signoff requirements --comment "同意实现"
```

### 4. 推进到下一阶段

```bash
# 推进到设计阶段
oc-collab advance -p design
```

---

## 常用命令

| 命令 | 说明 |
|------|------|
| `oc-collab status` | 查看项目状态和待办摘要 (v2.2.3) |
| `oc-collab .a` | 显示当前关联的项目信息 (v2.2.3) |
| `oc-collab todowrite` | 创建待办任务 (v2.2.3) |
| `oc-collab todoedit` | 编辑待办任务 (v2.2.3) |
| `oc-collab todo` | 查看待办事项 |
| `oc-collab advance -p <phase>` | 推进到指定阶段 |
| `oc-collab signoff <stage>` | 签署确认 |
| `oc-collab history` | 查看协作历史 |

---

## 协作流程

```
需求评审 → 设计评审 → 开发完成 → 测试通过 → 部署上线
    ↓          ↓           ↓          ↓         ↓
   签署       签署         签署       签署      完成

每个阶段必须双方签署后才能进入下一阶段
```

---

## 阶段说明

| 阶段 | 说明 |
|------|------|
| `requirements` | 需求评审阶段 |
| `design` | 设计评审阶段 |
| `development` | 开发阶段 |
| `testing` | 测试阶段 |
| `deployment` | 部署阶段 |

---

## 项目结构

```
myproject/
├── docs/
│   ├── 01-requirements/   # 需求文档
│   ├── 02-design/         # 设计文档
│   └── 03-test/           # 测试报告
├── state/
│   └── project_state.yaml # 项目状态
└── src/                   # 源代码
```

---

## 版本历史

| 版本 | 日期 | 功能 |
|------|------|------|
| v2.2.3 | 2026-02-08 | Agent体验优化：`.a`项目信息、任务同步、状态摘要 |
| v2.2.2 | 2026-02-07 | 协作规范强制执行、Git同步集成 |
| v2.2.1 | 2026-02-07 | 双代理认知免疫系统、动态Checklist |
| v2.2.0 | 2026-02-06 | 初始版本 |

---

## 详细文档

完整使用指南请参见项目 GitHub 仓库：
https://github.com/legoland01/dual-agent-collaboration-system

---

**Author**: liuzhen
**License**: MIT
