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
| `oc-collab todowrite --auto-check` | 创建TODO，自动检查参数并携带上下文 (v2.2.6) |
| `oc-collab skill search --keywords <kw>` | 搜索Skill文档 (v2.2.6) |
| `oc-collab skill slice <skill>` | 查看Skill特定切片 (v2.2.6) |
| `oc-collab skill enforce` | 检查Skill加载状态 (v2.2.6) |
| `oc-collab advance -p <phase>` | 推进到指定阶段 |
| `oc-collab signoff <stage>` | 签署确认 |
| `oc-collab history` | 查看协作历史 |
| `oc-collab compliance check` | 合规检查 (v2.2.2) |
| `oc-collab git sync` | Git同步 (v2.2.2) |
| `oc-collab rules init [--force]` | 初始化框架规则 (v2.2.8) |
| `oc-collab rules status` | 检查规则初始化状态 (v2.2.8) |
| `oc-collab rules init --auto-load` | 自动加载默认规则 (v2.2.9) |
| `oc-collab compliance check` | 合规检查 (v2.2.2) |
| `oc-collab compliance report` | 生成合规报告 (v2.2.9) |
| `oc-collab compliance violations` | 查看违规记录 (v2.2.9) |
| `oc-collab deploy check-docs` | 检查部署文档同步 (v2.2.9) |
| `oc-collab deploy sync-docs` | 同步部署文档 (v2.2.9) |
| `oc-collab webhook notify test` | 测试Webhook通知功能 (v2.2.8) |
| `oc-collab startup check` | 启动时检查未读TODO (v2.2.10) |
| `oc-collab todo list` | 显示TODO列表 (v2.2.10) |
| `oc-collab todo list --unread` | 仅显示未读TODO (v2.2.10) |
| `oc-collab todo list --agent <1|2>` | 按Agent筛选TODO (v2.2.10) |
| `oc-collab todo mark-read <id>` | 标记TODO为已读 (v2.2.10) |
| `oc-collab todo stats` | TODO统计信息 (v2.2.10) |
| `oc-collab skill check` | 检查Skill加载状态 (v2.2.10) |
| `oc-collab skill status` | 显示Skill合规状态 (v2.2.10) |
| `oc-collab skill verify <action>` | 验证操作前Skill (v2.2.10) |

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
| v2.2.12 | 2026-02-15 | 部署自动化CLI：完整部署流程、预览模式、版本管理、PyPI/Git推送、发布验证 |
| v2.2.11 | 2026-02-14 | Agent独立TODO编号、Skill强制执行增强、StateReceiver状态接收器 |
| v2.2.10 | 2026-02-14 | TodoQueueManager + Agent Startup Checker + CLI Enhancements |
| v2.2.9 | 2026-02-14 | StateNotifier集成（todowrite/signoff/phase_advance）、自动Bug检测、Agent Compliance CLI准入、规则自动加载 |
| v2.2.8 | 2026-02-13 | Webhook基础架构：EventDispatcher、StateNotifier骨架、HMAC验证 |
| v2.2.7 | 2026-02-10 | Skill内容准确性测试、覆盖率统计、事件监听与崩溃恢复 |
| v2.2.6 | 2026-02-09 | 智能辅助：todowrite自动检查、TODO上下文携带、冲突检测；Skill关键词检索、切片查看、强制查找 |
| v2.2.5 | 2026-02-09 | 文件Owner机制、signoff修复、版本结束后需求分析流程、评审机制优化 |
| v2.2.4 | 2026-02-08 | Skill强制加载检查、Git提交前签署验证、需求文档完整性检查 |
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
