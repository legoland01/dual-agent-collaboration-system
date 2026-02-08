# Compaction: 双机协作实时性改进讨论

**日期**: 2026-02-08
**参与者**: Agent 1, Agent 2 (通过OpenCode)
**主题**: 双机协作实时性改进战略规划

---

## 1. 核心问题

### 1.1 当前挑战

| 问题 | 影响 | 严重程度 |
|------|------|----------|
| GitHub不稳定 | 推送失败、等待 | 高 |
| 无实时通知 | 错过评审请求 | 高 |
| 状态文件冲突 | TODO状态不一致 | 中 |

### 1.2 关键发现

- **Agent2电脑能被外网访问** ✅ → 无需内网穿透
- **Webhook优于轮询** → 实时性更好
- **现有通知机制基础** → 可在此基础上增强

---

## 2. 讨论要点

### 2.1 Webhook vs 轮询

| 方案 | 原理 | 效率 | 结论 |
|------|------|------|------|
| 轮询 | 定期检查 | 低 | 放弃 |
| Webhook | 服务器推送 | 高 | 采用 |

**Webhook优势**：
- 事件驱动，秒级通知
- 不需要定期检查
- 资源消耗低

### 2.2 实施节奏

| 阶段 | 内容 | 时间 | 风险 |
|------|------|------|------|
| Phase 1 | Git稳定性（Gitee优先） | 1周 | 低 |
| Phase 2 | 状态同步（自动pull） | 1周 | 低 |
| Phase 3 | Webhook实时通知 | 1周 | 低 |

**原则**：步子不要太大，每次改动小、模块少

---

## 3. 决策要点

### 3.1 Git稳定性方案

```bash
# 新命令
oc-collab push-priority --message "xxx"

# 行为
# 1. 优先推送Gitee
# 2. Gitee失败时自动fallback到GitHub
# 3. 记录详细日志
```

### 3.2 状态同步方案

```bash
# 新命令
oc-collab sync-state        # 同步状态
oc-collab check-conflicts    # 检查冲突

# 自动行为
# 1. CLI命令执行前自动拉取
# 2. 检测state/文件冲突
# 3. 提供解决指引
```

### 3.3 Webhook方案

```bash
# Agent2电脑需要
oc-collab webhook start --port 8080 --secret xxx

# GitHub/Gitee配置
Payload URL: http://agent2.example.com:8080/webhook
```

---

## 4. 交付物

### 4.1 创建的文档

| 文档 | 说明 |
|------|------|
| `docs/05-strategy/STRATEGY_Dual_Machine_Collaboration.md` | 总体战略规划 |
| `docs/05-strategy/PROPOSAL_COLLAB_Phase1_Git_Stability.md` | Phase 1提案 |
| `docs/05-strategy/PROPOSAL_COLLAB_Phase2_State_Sync.md` | Phase 2提案 |
| `docs/05-strategy/PROPOSAL_COLLAB_Phase3_Webhook_Notification.md` | Phase 3提案 |
| `docs/05-strategy/README.md` | 快速参考 |

### 4.2 工时汇总

| Phase | 工时 | 说明 |
|-------|------|------|
| 1 | 12h | GitHelper + CLI |
| 2 | 16h | StateManager + 钩子 |
| 3 | 18h | Webhook服务 + 处理器 |
| **合计** | **46h** | 约2周 |

---

## 5. 下一步行动

### 5.1 短期

- [ ] Agent2评审Phase 1提案
- [ ] Agent2评审Phase 2提案
- [ ] Agent2评审Phase 3提案
- [ ] 启动Phase 1开发

### 5.2 实施顺序

```
Phase 1 (Git稳定性)
    ↓ (运行1周验证)
Phase 2 (状态同步)
    ↓ (运行1周验证)
Phase 3 (Webhook通知)
```

---

## 6. 经验教训

### 6.1 好的实践

| 实践 | 说明 |
|------|------|
| 小步快跑 | 每个Phase功能单一 |
| 充分验证 | 每个Phase完成后运行1周 |
| 风险控制 | 改动小、模块少 |

### 6.2 避免的做法

| 避免 | 原因 |
|------|------|
| 一次做太多 | 风险难以控制 |
| 不验证就推进 | 容易出问题 |
| 忽视网络问题 | 实时协作的基础 |

---

## 7. 关键结论

### 7.1 技术选型

| 选型 | 理由 |
|------|------|
| Gitee优先 | GitHub不稳定 |
| Webhook | 实时性更好 |
| 邮件+Webhook双通道 | 可靠性更高 |

### 7.2 实施原则

| 原则 | 说明 |
|------|------|
| 渐进式改进 | 每次改动小 |
| 可回滚 | 改动不影响现有功能 |
| 充分测试 | 每个Phase有单元测试+E2E测试 |

---

**完成时间**: 2026-02-08
**状态**: 待Agent2评审
