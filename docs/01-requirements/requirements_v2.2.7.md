# v2.2.7 需求文档

**版本**: v1.0
**日期**: 2026-02-10
**状态**: DRAFT → 待Agent2评审

---

## 零、核心架构参考

**参考文档**: `docs/00-architecture/CORE_ARCHITECTURE.md`

### 架构映射

| 功能ID | 功能名称 | 架构模块 | 映射路径 |
|--------|----------|----------|----------|
| F-TEST-001 | Skill行为自动测试框架 | 9.2 Skill管理 | 核心架构 → 9.2 |
| F-TEST-002 | Skill覆盖率统计CLI | 9.2 Skill管理 | 核心架构 → 9.2 |
| F-DOC-001 | Skill测试规范文档 | 9.2 Skill管理 | 核心架构 → 9.2 |
| F-DOC-002 | Skill维护清单 | 9.2 Skill管理 | 核心架构 → 9.2 |
| F-WEB-001 | Webhook基础配置 | 10.3 Webhook通知 | 核心架构 → 10.3 |
| F-WEB-002 | 事件监听 | 10.3 Webhook通知 | 核心架构 → 10.3 |
| F-WEB-003 | 事件分发 | 10.3 Webhook通知 | 核心架构 → 10.3 |
| F-WEB-004 | 状态通知 | 10.3 Webhook通知 | 核心架构 → 10.3 |

---

## 1. 版本概述

### 1.1 版本目标

**核心目标**：
1. 构建Skill可靠性保障体系，确保Skill内容与实际行为一致
2. 构建Webhook实时通知基础设施（双机协作核心能力）

### 1.2 来源文档

| 类型 | 文档 | 说明 |
|------|------|------|
| 测试报告 | Skill_Behavior_Test_Plan.md | Skill行为测试框架 |
| 测试报告 | test_skill_behavior_reliability.py | 自动化测试代码 |
| 提案 | PROPOSAL_COLLAB_Phase3_Webhook_Notification.md | Webhook原提案 |
| 分析报告 | ANALYSIS_v2.2.7_Requirements_Analysis.md | 本版本需求分析 |

---

## 2. 功能需求

### 2.1 功能清单

| 功能ID | 功能名称 | 类型 | 工时 | 架构模块 |
|--------|----------|------|------|----------|
| F-TEST-001 | Skill行为自动测试框架 | 需开发 | 6h | 9.2 |
| F-TEST-002 | Skill覆盖率统计CLI | 需开发 | 4h | 9.2 |
| F-DOC-001 | Skill测试规范文档 | 用Skill | 2h | 9.2 |
| F-DOC-002 | Skill维护清单 | 用Skill | 1h | 9.2 |
| F-WEB-001 | Webhook基础配置 | 需开发 | 4h | 10.3 |
| F-WEB-002 | 事件监听 | 需开发 | 4h | 10.3 |
| F-WEB-003 | 事件分发 | 需开发 | 3h | 10.3 |
| F-WEB-004 | 状态通知 | 需开发 | 3h | 10.3 |

### 2.2 功能详情

#### F-TEST-001: Skill行为自动测试框架

**描述**: 自动化验证Skill内容与实际行为的一致性

**子功能**:
| 子功能 | 说明 | 工时 |
|--------|------|------|
| 内容准确性验证 | 验证outputs文件存在、触发条件匹配 | 2h |
| 引用关系验证 | 验证内部链接、跨Skill引用有效 | 2h |
| CLI命令验证 | 验证skill中描述的CLI命令存在 | 2h |

**验收标准**:
- [ ] Skill内容准确性测试通过率 100%
- [ ] 引用关系验证通过率 100%
- [ ] CLI命令验证通过率 100%
- [ ] 支持 `--verbose` 输出详细结果
- [ ] 支持 `--fix` 自动修复可修复问题

#### F-TEST-002: Skill覆盖率统计CLI

**描述**: 统计Skill内容的切片覆盖率

**子功能**:
| 子功能 | 说明 | 工时 |
|--------|------|------|
| 覆盖率计算 | 计算skill切片覆盖率 | 2h |
| 统计报告 | 生成覆盖率统计报告 | 1h |
| 阈值检查 | 支持配置覆盖率阈值 | 1h |

**验收标准**:
- [ ] 支持 `oc-collab skill coverage` 命令
- [ ] 覆盖率计算精度 >= 95%
- [ ] 支持 `--threshold` 配置阈值
- [ ] 覆盖率 < 阈值时返回警告

#### F-WEB-001: Webhook基础配置

**描述**: 配置GitHub/Gitee Webhook

**子功能**:
| 子功能 | 说明 | 工时 |
|--------|------|------|
| Webhook配置 | 生成Webhook配置文件 | 2h |
| 密钥管理 | 生成/验证Webhook签名密钥 | 1h |
| 服务端点 | 生成回调URL | 1h |

**验收标准**:
- [ ] 支持 `oc-collab webhook init` 初始化配置
- [ ] 生成 secret 用于签名验证
- [ ] 生成回调URL格式: `/api/webhook/callback`
- [ ] 配置写入 `config/webhook.yaml`

#### F-WEB-002: 事件监听

**描述**: 监听Git push/pull request事件

**子功能**:
| 子功能 | 说明 | 工时 |
|--------|------|------|
| 事件解析 | 解析GitHub/Gitee webhook payload | 2h |
| 事件过滤 | 支持配置过滤规则 | 1h |
| 本地监听 | 本地HTTP服务监听webhook | 1h |

**验收标准**:
- [ ] 支持 GitHub webhook 事件解析
- [ ] 支持 Gitee webhook 事件解析
- [ ] 支持 `filter` 配置只监听特定事件
- [ ] 本地监听端口默认 8080

#### F-WEB-003: 事件分发

**描述**: 将事件分发给Agent1/Agent2

**子功能**:
| 子功能 | 说明 | 工时 |
|--------|------|------|
| 路由规则 | 根据事件类型路由到Agent | 1h |
| 消息格式 | 标准化事件消息格式 | 1h |
| 发送机制 | 通过state文件发送通知 | 1h |

**验收标准**:
- [ ] push事件 → 通知Agent1
- [ ] pull_request事件 → 通知Agent2
- [ ] 消息格式: `{event_type, repo, branch, author, timestamp}`
- [ ] 写入 `state/notifications/` 目录

#### F-WEB-004: 状态通知

**描述**: 阶段变更时通知对方Agent

**子功能**:
| 子功能 | 说明 | 工时 |
|--------|------|------|
| 阶段变更检测 | 检测阶段推进事件 | 1h |
| 通知模板 | 标准化通知模板 | 1h |
| 发送通知 | 发送状态变更通知 | 1h |

**验收标准**:
- [ ] 检测 `phase-advance` 事件
- [ ] 生成阶段变更通知
- [ ] 通知写入 `state/notifications/`
- [ ] 支持 `--no-notify` 关闭通知

---

## 3. CLI命令清单

### 新增命令

| 命令 | 说明 | 工时 |
|------|------|------|
| `oc-collab skill test --all` | 运行所有Skill测试 | 2h |
| `oc-collab skill test --skill <id>` | 运行指定Skill测试 | 1h |
| `oc-collab skill coverage` | 统计Skill覆盖率 | 2h |
| `oc-collab webhook init` | 初始化Webhook配置 | 2h |
| `oc-collab webhook status` | 查看Webhook状态 | 1h |
| `oc-collab webhook start` | 启动本地Webhook监听 | 3h |
| `oc-collab webhook stop` | 停止Webhook监听 | 1h |

### 变更命令

| 命令 | 变更 |
|------|------|
| `oc-collab phase-advance` | 新增 `--no-notify` 选项关闭通知 |

---

## 4. 工时预估

### 4.1 按功能模块

| 模块 | 功能数 | 工时 |
|------|--------|------|
| Skill保障体系 | 4 | 13h |
| Webhook基础设施 | 4 | 14h |
| **合计** | **8** | **27h** |

### 4.2 分阶段方案（建议）

| 阶段 | 内容 | 工时 | 交付物 |
|------|------|------|--------|
| v2.2.7 | Skill保障 + Webhook基础 | 17h | Skill测试 + Webhook配置+监听 |
| v2.2.8 | Webhook完成 | 10h | 事件分发+状态通知 |

### 4.3 详细工时拆分

| 功能 | 子任务 | 工时 | 负责人 |
|------|--------|------|--------|
| F-TEST-001 | 内容准确性验证 | 2h | Agent2 |
| F-TEST-001 | 引用关系验证 | 2h | Agent2 |
| F-TEST-001 | CLI命令验证 | 2h | Agent2 |
| F-TEST-002 | 覆盖率计算 | 2h | Agent2 |
| F-TEST-002 | 统计报告+阈值 | 2h | Agent2 |
| F-WEB-001 | Webhook配置+密钥 | 3h | Agent2 |
| F-WEB-001 | 服务端点 | 1h | Agent2 |
| F-WEB-002 | 事件解析 | 2h | Agent2 |
| F-WEB-002 | 事件过滤+监听 | 2h | Agent2 |
| F-WEB-003 | 路由规则+消息格式 | 2h | Agent2 |
| F-WEB-003 | 发送机制 | 1h | Agent2 |
| F-WEB-004 | 阶段变更检测 | 1h | Agent2 |
| F-WEB-004 | 通知模板+发送 | 2h | Agent2 |
| F-DOC-001 | Skill测试规范文档 | 2h | Agent1 |
| F-DOC-002 | Skill维护清单 | 1h | Agent1 |
| **合计** | | **27h** | |

---

## 5. 依赖关系

### 内部依赖

| 依赖项 | 说明 |
|--------|------|
| Skill文件 | F-TEST → skills/*/content.md, skill.json |
| state目录 | F-WEB → state/notifications/ |
| existing CLI | F-WEB → 基于现有 `oc-collab` CLI框架 |

### 外部依赖

| 依赖项 | 说明 |
|--------|------|
| GitHub Webhook API | 官方文档: https://docs.github.com/en/webhooks |
| Gitee Webhook API | 官方文档: https://gitee.com/help/articles/11825 |
| Flask/FastAPI | 可选用于本地监听 |

---

## 6. 约束条件

### 6.1 技术约束

- Webhook监听使用Python内置 `http.server`（避免引入Flask依赖）
- Skill测试需兼容现有 `test_skill_*.py` 测试文件
- CLI命令风格与现有命令一致

### 6.2 资源约束

- 开发资源：Agent2（25h）
- 测试资源：Agent1（黑盒测试 + Skill文档更新）
- 服务器资源：无（使用本地监听）

### 6.3 兼容性约束

- `oc-collab webhook start` 需后台运行，不阻塞CLI
- Skill测试需支持离线运行（不依赖GitHub/Gitee API）

---

## 7. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| Webhook监听稳定性 | 中 | 高 | 提供 `--no-webhook` 选项回退 |
| GitHub API变更 | 低 | 中 | 使用官方SDK，封装API调用 |
| Skill测试覆盖率不达标 | 中 | 中 | 提供 `--threshold` 可配置阈值 |
| Webhook密钥泄露 | 低 | 高 | 不写入版本控制，使用环境变量 |

---

## 8. 签署确认

### Agent 1 创建

| 角色 | 签署人 | 状态 | 日期 |
|------|--------|------|------|
| 产品负责人 | Agent 1 | ✅ | 2026-02-10 |

### Agent 2 评审

| 角色 | 签署人 | 状态 | 日期 |
|------|--------|------|------|
| 开发负责人 | Agent 2 | ⏳ | 待评审 |

---

## 附录A: Webhook事件格式

### GitHub Push事件

```json
{
  "event_type": "push",
  "repo": "owner/repo",
  "branch": "main",
  "author": "username",
  "commits": [
    {
      "id": "abc123",
      "message": "fix: bug",
      "timestamp": "2026-02-10T10:00:00Z"
    }
  ],
  "timestamp": "2026-02-10T10:00:01Z"
}
```

### Gitee Pull Request事件

```json
{
  "event_type": "pull_request",
  "repo": "owner/repo",
  "branch": "main",
  "author": "username",
  "action": "open",
  "number": 123,
  "timestamp": "2026-02-10T10:00:01Z"
}
```

---

## 附录B: 状态通知格式

### 阶段变更通知

```yaml
type: phase_advance
from_phase: development
to_phase: testing
initiator: agent1
timestamp: "2026-02-10T10:00:00Z"
message: "Agent1 已推进阶段到 testing"
```

---

**创建人**: Agent 1
**日期**: 2026-02-10
**状态**: DRAFT → 待Agent2评审
