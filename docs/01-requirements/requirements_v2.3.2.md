# 需求文档：oc-collab v2.3.2

**版本**: v1 (DRAFT)  
**创建日期**: 2026-02-17  
**作者**: Agent 1 (产品经理)  
**目标**: 集成OpenCode TUI通知POC，实现实时TODO通知交互

---

## 1. 背景

### 1.1 问题陈述

当前oc-collab的TODO通知机制存在以下问题：
1. **被动感知**: Agent需要手动运行`agent listen`命令才能感知新TODO
2. **无交互**: 收到TODO后无法直接在OpenCode界面进行操作
3. **体验割裂**: 需要在终端和OpenCode之间切换

### 1.2 POC研究成果

Consultant已完成POC验证（见`docs/00-memos/POC_OpenCode_TUI_Notification_Verification.md`）：

| 方案 | 状态 |
|------|------|
| TUI API toast | ❌ 有bug不显示 |
| TUI API prompt append | ❌ 有bug不显示 |
| **Question Tool + Instruction** | ✅ **验证成功** |

**核心机制**：
- 通过OpenCode的`instructions`机制创建自定义规则
- 当LLM收到新TODO时，自动调用`question` tool弹出交互窗口
- 用户可选择：立即执行/留待空闲/不用执行/查看详情

---

## 2. 需求概述

### 2.1 版本目标

v2.3.2的核心目标：
1. **集成POC成果**: 将Question Tool通知方案产品化
2. **简化配置**: 用户一键启用通知功能
3. **增强交互**: 支持在OpenCode界面直接操作TODO

### 2.2 功能范围

| 功能ID | 功能名称 | 优先级 | 类型 |
|--------|----------|--------|------|
| F-NOTIF-001 | OpenCode Instruction通知 | P0 | 新功能 |
| F-NOTIF-002 | TODO交互操作（含留待空闲） | P0 | 新功能 |
| F-NOTIF-003 | 留待空闲管理（含自动探知） | P0 | 新功能 |
| F-NOTIF-004 | 通知配置CLI | P1 | 新功能 |
| F-NOTIF-005 | 通知历史记录 | P2 | 增强 |

---

## 3. 功能需求

### 3.1 F-NOTIF-001: OpenCode Instruction通知

**需求描述**：
集成POC研究成果，通过OpenCode instruction机制实现TODO实时通知。

**详细说明**：

1. **Instruction文件生成**
   - 自动生成`TODO_NOTIFY.md`文件到项目目录
   - 包含LLM理解TODO通知的规则
   - 包含question tool调用示例

2. **OpenCode配置**
   - 生成`opencode.json`配置片段
   - 或提供CLI命令指导用户配置

3. **触发机制**
   - 当Agent创建新TODO时
   - 通过某种方式提醒用户告知LLM
   - LLM根据instruction自动弹出question交互

**验收标准**：
- [ ] 自动生成`docs/instructions/TODO_NOTIFY.md`
- [ ] Instruction包含TODO处理规则
- [ ] 用户配置后LLM能识别新TODO
- [ ] LLM自动调用question tool

### 3.2 F-NOTIF-002: TODO交互操作

**需求描述**：
用户在OpenCode的question交互窗口中，可直接操作TODO。

**交互流程**：
```
1. Agent创建TODO → 2. 用户告知LLM"我有新TODO" → 
3. LLM弹出question窗口 → 4. 用户选择操作 →
5. 执行相应操作
```

**用户操作选项**：
| 操作 | 说明 |
|------|------|
| 立即执行 | 标记TODO为进行中，开始执行 |
| 留待空闲 | 标记为"留待"，空闲时批量处理 |
| 不用执行 | 标记TODO为"无需执行"，永久关闭 |
| 查看详情 | 选择后在LLM回复中展示详情 |

**说明**：
- "分配他人"暂不支持
- "查看详情"通过question tool的交互能力实现

**验收标准**：
- [ ] question窗口显示TODO摘要
- [ ] 用户可选择至少4种操作（含"不用执行"）
- [ ] 选择后执行相应动作
- [ ] 操作结果反馈给用户

### 3.3 F-NOTIF-003: 留待空闲管理

**需求描述**：
管理用户标记为"留待空闲"的TODO，提供批量处理机制。支持两种触发方式：

1. **用户主动声明** - 用户告知LLM"处理留待"或"我空闲了"
2. **自动探知OpenCode空闲** - 基于OpenCode的session状态

**详细说明**：

1. **留待存储**
   - 独立的"留待"队列：`state/todo_deferred.yaml`
   - 记录留待时间、原始TODO信息

2. **触发方式**

   **方式A: 用户主动声明**
   ```
   用户告知LLM"处理留待"或"我空闲了"
       ↓
   读取留待队列
       ↓
   批量展示所有留待TODO
       ↓
   用户逐个确认处理方式
   ```

   **方式B: 自动探知OpenCode空闲（基于session状态）**
   ```
   OpenCode session状态变为 idle（等待用户输入）
       ↓
   通过 event stream 监听 session.status 事件
       ↓
   检测到 session.type === "idle"
       ↓
   自动触发留待TODO加载
       ↓
   通过question窗口提醒用户
   ```

   **OpenCode空闲状态定义**：
   - OpenCode内部维护session状态：`idle` / `busy` / `retry`
   - `idle` = OpenCode已完成自动任务，等待用户输入
   - 通过监听 `session.status` 事件获取状态变化

3. **空闲检测配置**
   ```bash
   # 开启自动探知
   oc-collab todo deferred auto-detect on

   # 设置空闲阈值（默认检测到idle即触发）
   oc-collab todo deferred auto-detect --timeout 30

   # 关闭自动探知
   oc-collab todo deferred auto-detect off

   # 查看当前配置
   oc-collab todo deferred auto-detect status
   ```

4. **批量提醒**
   - 用户可设置空闲提醒时间（如每天下午5点）
   - 或手动查询留待队列
   - 批量展示待处理的TODO

**新增CLI命令**：
```bash
# 查看留待队列
oc-collab todo deferred

# 处理留待TODO
oc-collab todo deferred process

# 设置提醒时间
oc-collab todo deferred remind --time 17:00

# 自动加载处理（空闲时调用）
oc-collab todo deferred load
```

**验收标准**：
- [ ] "留待空闲"操作将TODO移入独立队列
- [ ] 可查看留待队列列表
- [ ] 支持批量处理留待TODO
- [ ] 支持设置提醒时间
- [ ] `todo deferred load` 自动加载所有留待TODO
- [ ] 加载后支持逐个确认处理方式
- [ ] 支持自动探知OpenCode空闲（session.status === "idle"）
- [ ] 监听OpenCode event stream获取session状态变化
- [ ] 检测到idle时自动触发question窗口
- [ ] 自动探知可开启/关闭

### 3.4 F-NOTIF-004: 通知配置CLI

**需求描述**：
提供CLI命令简化通知功能配置。

**命令设计**：
```bash
# 启用通知功能
oc-collab notify enable

# 禁用通知功能
oc-collab notify disable

# 查看通知状态
oc-collab notify status

# 测试通知
oc-collab notify test
```

**验收标准**：
- [ ] `notify enable` 自动配置instruction文件
- [ ] `notify disable` 清理配置
- [ ] `notify status` 显示当前状态
- [ ] `notify test` 发送测试通知

### 3.4 F-NOTIF-004: 通知历史记录

**需求描述**：
记录通知发送历史，便于追溯。

**数据存储**：
```yaml
# state/notification_history.yaml
notifications:
  - id: notif-001
    todo_id: TODO-2to1-010
    created_at: 2026-02-17T10:00:00
    user_action: executed  # executed/deferred/rejected
    user_action_at: 2026-02-17T10:01:00
```

**验收标准**：
- [ ] 每次通知生成历史记录
- [ ] 支持查询通知历史
- [ ] 支持按TODO筛选

---

## 4. 非功能需求

### 4.1 性能需求

- Instruction文件生成: < 1秒
- 通知触发延迟: < 2秒（LLM响应）
- 交互响应时间: < 3秒

### 4.2 兼容性

- 兼容OpenCode最新版本
- 兼容Python 3.8+
- 向后兼容v2.3.1功能

### 4.3 用户体验

- 配置步骤不超过3步
- 首次配置引导清晰
- 错误提示明确

---

## 5. 开放问题

### Q1: Instruction加载机制

**问题**: OpenCode如何加载自定义instruction？

**待确认**:
- 是否需要修改OpenCode源码？
- 还是只需要配置文件？

**依赖**: POC研究结论

### Q2: 通知触发方式

**问题**: Agent创建TODO后，如何提醒用户告知LLM？

**方案**:
- A: Agent输出提示"请告诉LLM您有新TODO"
- B: Agent自动发送系统消息（需OpenCode支持）
- C: 用户习惯性告知（最简单）

**建议**: 方案C，逐步培养用户习惯

### Q3: 多Agent通知

**问题**: 多个Agent同时创建TODO，如何处理？

**待确认**:
- A: 依次通知
- B: 批量通知
- C: 只通知最新的

**建议**: 方案A，简化实现

---

## 5. CLI 命令清单

### 新增命令

| 命令 | 说明 | 工时 |
|------|------|------|
| `oc-collab notify enable` | 启用通知功能，生成instruction文件 | 1h |
| `oc-collab notify disable` | 禁用通知功能 | 0.5h |
| `oc-collab notify status` | 查看通知状态 | 0.5h |
| `oc-collab notify test` | 测试通知功能 | 0.5h |
| `oc-collab todo deferred` | 查看留待队列 | 0.5h |
| `oc-collab todo deferred process` | 批量处理留待TODO | 1h |
| `oc-collab todo deferred remind` | 设置留待提醒时间 | 0.5h |
| `oc-collab todo deferred load` | 空闲时自动加载处理留待TODO | 1h |
| `oc-collab todo deferred auto-detect` | 自动探知OpenCode空闲开关/配置 | 1h |

### 变更命令

| 命令 | 变更说明 | 工时 |
|------|----------|------|
| `oc-collab todowrite` | 新增 `--source` 参数 | 1h |

---

## 6. 工时预估

| 模块 | 功能 | 工时 |
|------|------|------|
| M1 | InstructionGenerator | 2h |
| M2 | TodoInteraction | 3h |
| M3 | DeferredManager | 2h |
| M4 | NotifyCLI | 2h |
| M5 | NotifyHistory | 1h |
| - | 测试与调试 | 2h |
| - | 文档 | 1h |
| **总计** | | **13h** |

**说明**：工时略超12h，但"留待空闲"是核心用户体验功能，值得投入。

---

## 7. 依赖关系

### 7.1 外部依赖

| 依赖 | 版本 | 说明 |
|------|------|------|
| OpenCode | 最新版 | TUI API + question tool |
| Python | 3.8+ | 运行环境 |

### 7.2 内部依赖

| 功能 | 依赖 | 说明 |
|------|------|------|
| F-NOTIF-001 | POC成果 | Question Tool方案 |
| F-NOTIF-002 | F-NOTIF-001 | 基于instruction |
| F-NOTIF-003 | F-NOTIF-001 | 配置命令 |
| F-NOTIF-004 | F-NOTIF-002 | 历史记录 |

---

## 8. 风险与缓解

### 8.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| OpenCode升级导致API变化 | 高 | 隔离API调用，版本检测 |
| LLM不遵循instruction | 中 | 提供明确示例，持续优化 |

### 8.2 产品风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 用户不理解机制 | 中 | 提供使用指南 |
| 配置复杂 | 高 | 简化到1步配置 |

---

## 9. 验收标准汇总

| 功能ID | 验收标准数 | 状态 |
|--------|-----------|------|
| F-NOTIF-001 | 4 | 待开发 |
| F-NOTIF-002 | 4 | 待开发 |
| F-NOTIF-003 | 4 | 待开发 |
| F-NOTIF-004 | 3 | 待开发 |
| **总计** | **15** | |

---

## 10. 命名规范

根据v2.3.1的Agent间通信机制，本版本使用：
- **TODO编号**: `TODO-XtoY-NNN` (发送者X → 接收者Y)
- **通知编号**: `notif-NNN`

---

## 11. 附录

### A. 相关文档

- POC报告: `docs/00-memos/POC_OpenCode_TUI_Notification_Verification.md`
- v2.3.1详细设计: `docs/02-design/DETAIL_v2.3.1.md`
- Agent间通信机制: `docs/02-design/DETAIL_v2.3.1.md` 第1.3节

### B. 参考资料

- OpenCode Instructions机制
- OpenCode Question Tool

---

**状态**: DRAFT  
**待评审**: Agent2

