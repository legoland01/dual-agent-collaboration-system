# PM-Agent 与 oc-collab 同步开发计划

**日期**: 2026-02-18  
**版本**: v1.0

---

## 一、当前状态

### 1.1 PM-Agent

| 模块 | 状态 | 说明 |
|------|------|------|
| 项目管理 | ✅ 基础完成 | CRUD功能，数据库已创建 |
| 客户管理 | ✅ 基础完成 | 7个客户已导入 |
| 材料处理 | ⚠️ 框架有，逻辑未串联 | Service层未集成 |
| Agent管理 | ❌ 未开发 | 待开发 |
| 配置管理 | ❌ 未开发 | 待开发 |
| 测试平台 | ❌ 未开发 | 待开发 |

### 1.2 oc-collab

| 模块 | 状态 | 说明 |
|------|------|------|
| Skill机制 | ✅ 已有 | 核心规范 |
| TODO管理 | ✅ POC完成 | SQLite存储 |
| 通知机制 | ✅ POC完成 | Webhook基础 |
| 自动流程 | ❌ 未开发 | v2.3.3 |
| Agent Pool | ❌ 未开发 | v2.3.5 |
| 配置管理 | ❌ 未开发 | v2.3.4 |

---

## 二、开发模式

### 2.1 协作方式

```
PM-Agent (管理平台)
    │
    ├── 调用 ──────▶ oc-collab CLI
    │
    ◀── 状态通知 ─ Webhook

oc-collab (核心框架)
    │
    ├── 被PM-Agent调用
    ├── Skill规范
    └── Agent协作
```

### 2.2 同步原则

| 原则 | 说明 |
|------|------|
| PM-Agent先动 | PM-Agent发起调用，oc-collab响应 |
| 版本锁定 | oc-collab先升级，PM-Agent后适配 |
| 接口稳定 | CLI接口不频繁变更 |

---

## 三、近期开发任务

### Phase 1: 通知机制 (Week 1)

| 系统 | 任务 | 依赖 |
|------|------|------|
| **oc-collab v2.3.2** | SQLite存储完善 | - |
| oc-collab | Webhook服务端 | 监听进程 |
| PM-Agent | Webhook接收API | - |
| PM-Agent | 调用oc-collab CLI | - |

### Phase 2: 自动流程 (Week 2)

| 系统 | 任务 | 依赖 |
|------|------|------|
| **oc-collab v2.3.3** | 场景匹配器 | Phase 1 |
| oc-collab | 自动继续处理器 | - |
| PM-Agent | 问题分类服务集成 | - |

### Phase 3: 配置管理 (Week 3)

| 系统 | 任务 | 依赖 |
|------|------|------|
| **oc-collab v2.3.4** | 配置管理模块 | Phase 2 |
| PM-Agent | 版本仓库管理 | - |

### Phase 4: Agent管理 (Week 4)

| 系统 | 任务 | 依赖 |
|------|------|------|
| **oc-collab v2.3.5** | Agent Pool CLI | Phase 3 |
| PM-Agent | Agent管理界面 | - |

---

## 四、CLI接口约定

### 4.1 PM-Agent 调用 oc-collab

```bash
# 创建需求
oc-collab requirement create --project <项目> --title "<标题>"

# 创建TODO
oc-collab todo create --project <项目> --agent <AgentID> --content "<内容>"

# 查询TODO
oc-collab todo list --agent <AgentID> --project <项目>

# 项目同步
oc-collab project sync --project <项目>
```

### 4.2 oc-collab 回调 PM-Agent

```yaml
# Webhook配置
webhooks:
  pm_agent:
    url: "http://localhost:8000/api/webhook/oc-collab"
    events:
      - todo.completed
      - requirement.created
      - bug.resolved
```

---

## 五、关键同步点

| 同步点 | PM-Agent | oc-collab | 验证 |
|--------|-----------|-----------|------|
| 1 | 能调用oc-collab命令 | CLI接口可用 | 命令执行成功 |
| 2 | 能接收Webhook | Webhook可推送 | 收到通知 |
| 3 | 能查询TODO | TODO存储可用 | 数据正确 |
| 4 | Agent Pool管理 | Agent Pool CLI | 分配成功 |

---

## 六、开发分工

| 负责方 | 任务 |
|--------|------|
| oc-collab团队 | CLI接口、Webhook、存储、Agent Pool |
| PM-Agent团队 | Webhook接收、调用CLI、界面、Agent管理 |
| Agent1(我) | 协调接口设计、进度同步 |

---

## 七、下一步

1. ✅ 确定开发模式
2. ⏳ 确认Phase 1任务优先级
3. ⏳ 分配开发资源
4. ⏳ 开始Phase 1开发

---

**协调者**: Agent1
