# Proposal: Git集成方案

**提案编号**: PROPOSAL_2026-02-024  
**日期**: 2026-02-16  
**作者**: Consultant (战略规划)  
**状态**: DRAFT

---

## 一、背景

### 1.1 Git的双重角色

Git在oc-collab系统中承担双重职责：
1. **代码版本管理** - 传统开发用途
2. **状态同步底层** - TODO、签署、状态依托Git同步

---

## 二、Git集成设计

### 2.1 仓库结构

```
project/
├── .oc-collab/           # oc-collab配置
│   ├── config.yaml       # 项目配置
│   ├── project_state.yaml # 项目状态
│   ├── milestone_signoffs.yaml # 签署记录
│   ├── audit_log.yaml    # 审计日志
│   └── state_history.yaml # 状态变更历史
├── docs/                 # 文档
├── src/                  # 代码
└── tests/                # 测试
```

### 2.2 同步策略

| 操作 | 触发时机 | 同步方式 |
|------|----------|----------|
| 状态变更 | 即时 | commit + push |
| TODO更新 | 即时 | commit + push |
| 签署完成 | 即时 | commit + push |
| 定时同步 | 每5分钟 | fetch + merge |

### 2.3 Commit规范

```
# 格式
<type>(<scope>): <message>

# 示例
feat(todo): 创建TODO-1to2-001
fix(signoff): 修正签署状态
chore(state): 更新项目状态
```

### 2.4 冲突处理

| 场景 | 处理策略 |
|------|----------|
| 状态文件冲突 | 拒绝合并，要求手动解决 |
| TODO并发修改 | 拒绝合并，提示重新提交 |
| 文档冲突 | 允许合并，人工确认 |

---

## 三、与通信层整合

### 3.1 Git作为通信底层

| 通信能力 | Git实现 |
|----------|----------|
| 可靠传输 | Git push/pull |
| 顺序保证 | commit时间顺序 |
| 版本历史 | git log可追溯 |
| 离线支持 | 本地先操作 |

### 3.2 Webhook集成

```yaml
# Webhook配置
webhooks:
  - url: http://localhost:8080/webhook
    events:
      - push
      - merge_request
    filter:
      paths:
        - .oc-collab/**
```

---

## 四、实施计划

| 版本 | 功能 | 工时 |
|------|------|------|
| v2.2 | 仓库结构规范 | 2h |
| v2.2 | Commit规范 | 2h |
| v2.4 | 冲突处理策略 | 4h |
| v2.4 | Webhook集成 | 6h |

---

**提案状态**: DRAFT
