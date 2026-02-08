# 双机协作改进战略规划

**目标**：解决Agent1和Agent2分机协作的实时性问题

---

## 文档结构

| 文档 | 说明 | 状态 |
|------|------|------|
| [STRATEGY_Dual_Machine_Collaboration.md](./STRATEGY_Dual_Machine_Collaboration.md) | 总体战略规划 | DRAFT |
| [PROPOSAL_COLLAB_Phase1_Git_Stability.md](./PROPOSAL_COLLAB_Phase1_Git_Stability.md) | Git稳定性改进 | DRAFT |
| [PROPOSAL_COLLAB_Phase2_State_Sync.md](./PROPOSAL_COLLAB_Phase2_State_Sync.md) | 状态同步改进 | DRAFT |
| [PROPOSAL_COLLAB_Phase3_Webhook_Notification.md](./PROPOSAL_COLLAB_Phase3_Webhook_Notification.md) | Webhook实时通知 | DRAFT |

---

## 实施路线图

```
Phase 1: Git稳定性（1周）
    ├── Gitee优先级推送
    └── 自动fallback
            ↓
Phase 2: 状态同步（1周）
    ├── 自动拉取
    ├── 冲突检测
    └── 冲突解决指引
            ↓
Phase 3: Webhook实时通知（1周）
    ├── Webhook接收服务
    ├── 事件处理器
    └── 邮件/CLI通知
```

---

## 快速参考

### Phase 1 核心改动

```bash
# 新命令
oc-collab push-priority --message "xxx"

# 行为
# 1. 优先推送Gitee
# 2. Gitee失败时自动fallback到GitHub
# 3. 记录详细日志
```

### Phase 2 核心改动

```bash
# 新命令
oc-collab sync-state        # 同步状态
oc-collab check-conflicts    # 检查冲突

# 自动行为
# 1. CLI命令执行前自动拉取
# 2. 检测state/文件冲突
# 3. 提供解决指引
```

### Phase 3 核心改动

```bash
# Agent2电脑需要
oc-collab webhook start --port 8080 --secret xxx

# GitHub/Gitee需要配置Webhook
Payload URL: http://agent2.example.com:8080/webhook
```

---

## 状态汇总

| Phase | 名称 | 风险 | 改动范围 | 预计工时 |
|-------|------|------|----------|-----------|
| 1 | Git稳定性 | 低 | git.py | 12h |
| 2 | 状态同步 | 低 | state_manager.py, main.py | 16h |
| 3 | Webhook通知 | 低 | webhook_service.py | 18h |

---

**最后更新**: 2026-02-08
