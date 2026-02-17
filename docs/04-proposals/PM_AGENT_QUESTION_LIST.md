# PM-Agent 需求拉通问题清单

**日期**: 2026-02-16
**发起人**: Agent3 (PM Agent - PM-Agent项目产品经理)
**收件人**: Consultant
**状态**: ✅ **已解答**

---

## 一、背景说明

PM-Agent模块定位有重要更新，核心变化如下：

### 原有定位
- 信息输入、项目管理、Git进度同步

### 更新后定位
| 维度 | 说明 |
|------|------|
| **单一入口** | 所有客户材料唯一入口，不区分客户/项目 |
| **自动归属** | 根据内容自动判断归属哪个客户、哪个项目 |
| **自动路由** | 推送到对应项目的资料库 |
| **开发控制** | 客户材料影响/调整oc-collab项目组工作 |
| **汇总输出** | 项目组开发文档自动汇总给客户 |

### 业务流

```
客户材料（任意形式）
    │
    ▼
┌─────────────────────┐
│   PM-Agent          │ ← 唯一入口
│  ┌───────────────┐  │
│  │ 内容分析       │  │ ← 参考RESEARCH_image_search_mcp
│  │ 客户识别       │  │
│  │ 项目匹配       │  │
│  └───────────────┘  │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  项目资料库         │ ← 自动路由
└─────────────────────┘
    │
    │ 控制/调整
    ▼
┌─────────────────────┐
│  oc-collab执行层   │
│  (多个项目组)      │
└─────────────────────┘
    │
    │ 开发文档自动汇总
    ▼
┌─────────────────────┐
│  客户               │ ← 输出
└─────────────────────┘
```

---

## 二、参考文档

| 文档 | 说明 | 状态 |
|------|------|------|
| `PROPOSAL_2026-02-018_pm_agent.md` | PM-Agent主提案 | 待评审 |
| `RESEARCH_image_search_mcp.md` | 多模态输入整合研究 | 探索中 |
| `PROPOSAL_Incoming_Requirements_Management.md` | 需求收集与管理流程 | DRAFT |

---

## 三、核心需求整合

基于上述文档，需要整合以下能力：

### 3.1 输入层（ RESEARCH_image_search_mcp ）

| 能力 | 说明 |
|------|------|
| 多模态输入 | 支持图片/音频/文档/日志 |
| 统一处理框架 | InputHandler → 类型检测 → Handler → LLM |
| CLI命令 | `oc-collab process <file> "问题"` |

### 3.2 收集层（ PROPOSAL_Incoming ）

| 能力 | 说明 |
|------|------|
| 统一入口 | 所有需求进入同一管道 |
| 零门槛收集 | 不做评审，直接收集 |
| 定期梳理 | 每版本开发完成后梳理 |
| 状态透明 | 每个需求有明确状态 |

### 3.3 PM-Agent核心能力（新增/强化）

| 能力 | 说明 |
|------|------|
| 客户识别 | 自动识别材料来源客户 |
| 项目匹配 | 根据内容自动归属项目 |
| 自动路由 | 推送到对应项目资料库 |
| 开发控制 | 材料内容影响项目组工作 |
| 汇总输出 | 开发文档自动汇总给客户 |

---

## 四、待澄清问题（已解答）

| 序号 | 问题 | 说明 | 答案 |
|------|------|------|------|
| 1 | **开发控制方式** | 客户材料如何"控制/调整"oc-collab项目组？是通过修改需求优先级？触发新任务？调整迭代计划？ | **通过TODO控制**。PM-Agent生成的需求自动创建为oc-collab TODO，优先级决定开发顺序 |
| 2 | **项目组定义** | "项目组由多个agent组成"具体指什么？是多个oc-collab实例？还是一个项目内的Agent1+Agent2组合？ | **Agent1 + Agent2 组合**。每个oc-collab项目由一个Agent1（产品经理）和一个Agent2（技术负责人）组成 |
| 3 | **输出内容** | 客户看到什么？是报告/进度/文档？什么格式？什么频率？ | **代码/文档/进度/问题跟踪表**。按需生成，可配置定期推送 |
| 4 | **整合方式** | PM-Agent如何调用oc-collab？API？CLI？Webhook？ | **通过Git**。PM-Agent将需求写入项目Git仓库，oc-collab通过Git同步获取 |
| 5 | **MVP首期范围** | 首期做到什么程度？入口+自动归属够了吗？是否需要包含与oc-collab的整合？ | **完整闭环**：入口 + 自动归属 + oc-collab整合，三者缺一不可 |
| 6 | **与incoming流程关系** | 与PROPOSAL_Incoming是整合还是独立？PM-Agent是否复用incoming的收集/梳理机制？ | **可复用**。PM-Agent可以复用incoming的需求收集和梳理机制，作为输入源之一 |
| 7 | **多客户隔离** | 多客户场景下，项目资料库是否需要隔离？如何保证数据安全？ | **通过Git权限**。不同客户项目使用不同Git仓库，权限控制由Git平台负责 |
| 8 | **技术架构** | PM-Agent是独立Web服务（Vue.js+FastAPI）还是集成在oc-collab CLI中？ | **独立Web服务**。Vue.js + FastAPI 架构，独立于oc-collab |

---

## 五、下一步（Agent3可以开始了）

### 5.1 已确认事项

- ✅ 提案文档 (`PROPOSAL_2026-02-018_pm_agent.md`) - 已评审通过
- ✅ 8个问题已全部解答
- ✅ MVP范围：入口 + 自动归属 + oc-collab整合（完整闭环）

### 5.2 Agent3工作流程

按照oc-collab规范，PM-Agent项目需要创建：

| 阶段 | 文档 | 路径 |
|------|------|------|
| 1 | 需求文档 | `docs/01-requirements/requirements_pm_agent.md` |
| 2 | 概要设计 | `docs/02-design/OUTLINE_pm_agent.md` |
| 3 | 详细设计 | `docs/02-design/DETAIL_pm_agent.md` |
| 4 | 开发 | 按详细设计实现 |

### 5.3 注意事项

- **PM-Agent是独立项目**，有自己的版本号（如v1.0.0），不与oc-collab共享
- **项目组**：Agent1（产品经理）+ Agent2（技术）
- **整合方式**：通过Git，PM-Agent写入需求到oc-collab项目仓库

### 5.4 关键参考文档

| 文档 | 用途 |
|------|------|
| `skills/oc_collab_requirements_guide/content.md` | 需求文档编写规范 |
| `skills/oc_collab_outline_design_guide/content.md` | 概要设计编写规范 |
| `skills/oc_collab_detailed_design_guide/content.md` | 详细设计编写规范 |

---

## 六、附录

### A. 相关CLI命令设计（来自RESEARCH_image_search_mcp）

```bash
# 统一入口
oc-collab process <file> "问题可选"

# 客户声音专用
oc-collab customer voice screenshot.png "客户反馈什么问题"
oc-collab customer call call_recording.m4a "客户说了什么"
oc-collab customer meeting meeting.m4a "提取客户需求"
```

### B. incoming流程状态流转

```
PENDING (提交后)
    ↓ Agent 1 梳理
IN_REVIEW (梳理中)
    ↓ Agent 1 评估
├─ ACCEPTED (采纳) → 进入开发流程
├─ REJECTED (拒绝) → 记录原因
└─ DEFERRED (推迟) → 后续版本
```

---

**请Consultant评审并反馈**
