# oc-collab 产品路线图

**版本**: v6  
**创建日期**: 2026-02-14  
**更新日期**: 2026-02-17

---

## 一、版本愿景总览

| 版本 | 愿景 | 核心能力 | 阶段 |
|------|------|----------|------|
| **v1** | 基础框架验证 | 单Agent流程 | 已完成 |
| **v2** | 稳定可靠的双Agent协作 | Agent1+Agent2分离式协作 | 🔄 **当前** |
| **v3** | TODO系统独立 + L3 PM-Agent | 全局TODO + 单点入口 | ⏳ 待规划 |

---

## 一、版本愿景总览

| 版本 | 愿景 | 核心能力 | 阶段 |
|------|------|----------|------|
| **v1** | 基础框架验证 | 单Agent流程 | 已完成 |
| **v2** | 稳定可靠的双Agent协作 | Agent1+Agent2分离式协作 | 🔄 **当前** |
| **v3** | TODO系统独立 + L3 PM-Agent | 全局TODO + 单点入口 | ⏳ 待规划 |

---

## 二、架构分层（做什么）

```
L1: oc-collab-core     → CLI工具，项目内Agent协作（不含TODO）
L2: TODO系统           → 全局共享，跨项目任务传递
L3: PM-Agent          → 单点入口，项目管理
```

**详细设计**: 见 `CORE_ARCHITECTURE.md`

**研究结论**: 见 `RESEARCH_Multi_Project_Collaboration.md`

---

## 三、v2 版本规划（何时做）

### v2 核心目标

```
v2目标：实现稳定可靠的双Agent协作框架

├── Agent1职责：发现问题 → 创建TODO → 记录文档
├── Agent2职责：执行代码 → 修复Bug → 合并到分支
├── 核心能力：CLI工具 + Skill规范 + 流程自动化 + 状态通知
└── TODO系统：从oc-collab独立，全局共享
```

### v2 版本结构

| 版本号 | 名称 | 目标 | 状态 |
|--------|------|------|------|
| **v2.0** | 基础框架 | 双Agent协作基础 | ✅ 已发布 |
| **v2.1** | 异常处理 | 异常捕获 + E2E测试 | ✅ 已发布 |
| **v2.2** | 流程规范 | 签署 + Git同步 + Skill强制 | ✅ 已发布 |
| **v2.3** | TODO系统 | Agent注册 + 跨项目路由 | 🔄 **当前规划** |
| **v2.4** | **刚性框架** | **里程碑锁 + 审批权校验 + 审计** | ⏳ 待规划 |

---

## 四、v2.0：基础框架（已完成）

**目标**: 双Agent协作基础框架

| 子版本 | 核心功能 | 状态 |
|--------|----------|------|
| v2.0.0 | Agent1/Agent2职责定义 | ✅ |
| v2.0.1 | 基础CLI命令 | ✅ |
| v2.0.2 | State状态管理 | ✅ |

---

## 五、v2.1：异常处理（已完成）

**目标**: 异常捕获与处理

| 子版本 | 核心功能 | 状态 |
|--------|----------|------|
| v2.1.0 | 异常分类与处理 | ✅ |
| v2.1.1 | E2E测试框架 | ✅ |
| v2.1.2 | 状态验证器 | ✅ |

---

## 六、v2.2：流程规范（当前规划）

**目标**: 签署流程、Git同步、Skill强制执行、状态通知

**截止条件**: 以下功能全部完成后，v2.2结束，进入v2.3

| 功能 | 来源 | 工时 | 状态 |
|------|------|------|------|
| Agent独立TODO编号 | BUG-007, P-006 | 7.5h | pending |
| Skill强制执行CLI钩子 | BUG-005, P-004, P-007 | 10h | pending |
| StateNotifier Receiver | P-005 | 8h | pending |
| 部署自动化 | F-AUTO-001 | 8h | pending |
| AutoBugDetector修复 | BUG-20260215-002, P-015 | 4h | pending |

**v2.2 预计工时**: ~35h

---

## 七、v2.3：TODO系统（全局独立）

**目标**: 将TODO系统从oc-collab独立，支持跨项目任务传递

**背景**: 
- 多项目协作需要全局共享的TODO系统
- oc-collab只管项目内流程，TODO独立出来
- 参考: `RESEARCH_Multi_Project_Collaboration.md`

### v2.3.1：TODO核心功能

**目标**: 支持跨项目TODO分发

| 功能 | 说明 | 工时 | 优先级 |
|------|------|------|--------|
| TODO编号优化 | 支持多Agent：TODO-1to2-xxx | 4h | P0 |
| 向后兼容 | 旧格式兼容 | 2h | P0 |
| Agent注册表 | 支持注册多个Agent | 3h | P0 |
| 项目标签 | 区分TODO属于哪个项目 | 2h | P0 |
| 跨项目路由 | sender-to-receiver规则 | 4h | P0 |

### v2.3.2：TODO存储 + 监听 + 实时通知

**目标**: SQLite存储 + 伴随监听进程 + 实时通知交互

**技术方案**: OpenCode Question Tool交互（已通过POC验证 ✅）

**参考**: 
- `POC_OpenCode_TUI_Notification_Verification.md`
- `PROPOSAL_2026-02-027_agent_notification_interaction.md`

| 功能 | 说明 | 工时 | 优先级 | 状态 |
|------|------|------|--------|------|
| SQLite存储 | 直接使用SQLite | 4h | P0 | pending |
| 数据迁移 | YAML转SQLite脚本 | 2h | P1 | pending |
| 监听进程 | agent listen自动启动 | 3h | P0 | pending |
| 状态感知 | online/offline实时感知 | 2h | P1 | pending |
| 上线拉取 | Agent上线后先处理积压 | 2h | P1 | pending |
| **实时通知** | Question窗口显示通知 | 4h | P0 | 🔄 POC完成 |
| **交互选项** | 执行/推迟/拒绝 | 4h | P0 | 🔄 POC完成 |
| 配置管理 | opencode连接配置 | 2h | P1 | pending |

**技术实现**:
1. 使用OpenCode `instructions`机制加载自定义规则
2. LLM根据规则自动调用question tool
3. 用户在OpenCode界面选择操作

**实现文件**:
- `opencode_src/instructions/TODO_NOTIFY.md` - 通知处理instruction
- `opencode_src/opencode.json` - 加载配置

**v2.3.2预计工时**: ~15h

### v2.3.3：Skill遵从 + 自动流程触发

**目标**: 确保oc-collab流程可靠 + 自动化流程触发

**参考**: 
- `PROPOSAL_2026-02-026_agent_id_and_role_rename.md`
- `docs/05-design/RESEARCH_v2.3.3_auto_flow_trigger.md`

| 功能 | 说明 | 工时 | 优先级 | 状态 |
|------|------|------|--------|------|
| **TODO自动推送** | StateNotifier增强，推给目标Agent | 4h | P0 | pending |
| **StateReceiver自动启动** | 接收Webhook自动启动 | 2h | P0 | pending |
| **agent listen自动启动** | Agent启动时自动运行 | 2h | P0 | pending |
| 需求签署自动创建设计 | 文档签署后自动创建 | 2h | P1 | pending |
| 开发自检自动创建提测 | 自检通过自动创建 | 2h | P1 | pending |
| Bug自动创建TODO | 发现Bug自动创建 | 2h | P1 | pending |
| Skill强制 | 关键操作必须使用Skill | 3h | P1 | pending |

**预计工时**: ~17h（一次开发完成）

### v2.3.4：配置管理（新增）

**目标**: 解决版本不匹配导致的运行时问题

**设计文档**: `docs/05-design/DESIGN_config_management_module.md`

| 功能 | 说明 | 工时 | 优先级 | 状态 |
|------|------|------|--------|------|
| ConfigRegistry | 版本注册表 | 4h | P0 | pending |
| VersionChecker | 版本检查器 | 3h | P0 | pending |
| ConfigWatcher | 配置变更监听 | 3h | P1 | pending |
| Skill版本管理 | Skill更新同步 | 3h | P0 | pending |
| 跨项目同步 | 全局配置同步 | 3h | P0 | pending |
| CLI命令 | config status/sync/check | 3h | P1 | pending |

---

## 八、v2.4：刚性框架
    status: active
    git_name: "zhangsan"
  agent2:
    id: agent2
    role: PRODUCT_MANAGER
    team: internal
    status: active
```

**添加新Agent流程**：
```bash
# Agent3启动时
export OC_AGENT_ID=agent3
oc-collab agent auto-register

# 自动添加到agents列表
# 立即可以使用：TODO-1to3-xxx, TODO-2to3-xxx
```

#### 4. Git可靠性保障

**核心原则**：Git是唯一数据源，所有变更立即同步

| 机制 | 说明 |
|------|------|
| 每次操作后立即push | 确保变更立即同步到所有远程 |
| 每次操作前先pull | 获取最新状态 |
| 冲突检测 | 检测到冲突提示手动解决 |
| 多远程仓库 | 自动同步到GitHub + Gitee |

**自动同步范围**：
- TODO创建/变更
- 需求文档变更
- 设计文档变更
- Bug报告创建
- 签署状态变更

#### 5. 多Agent通信示例

```
Agent1 创建TODO-1to2-001（给Agent2的任务）
    ↓
写入本地 state/todo_queue.yaml
    ↓
自动执行 git add + commit + push
    ↓
Agent2 拉取最新状态
    ↓
读取并处理TODO
    ↓
更新状态 + 自动push
    ↓
Agent1 看到状态更新
```

**依赖**: Webhook感知、状态通知 v2.2.8 已实现 ✅

**v2.3.1 预计工时**: ~23h

**v2.3.1 结束标志**:
- [ ] TODO新编号格式完成（支持多Agent）
- [ ] 旧格式兼容
- [ ] Agent注册表支持多Agent
- [ ] 所有文档操作自动Git同步
- [ ] ACK确认机制完成

---

## 八、v2.4：刚性框架

**目标**: 里程碑锁、审批权校验、自验收阻断、审计系统

**背景**: 需要充分研究规划，确保刚性框架有效可行

---

## 九、v2.5：Agent扩展 + Skill系统

**目标**: L1 Skill完善

| 功能 | 说明 | 工时 |
|------|------|------|
| Skill模板机制 | 缺省加载、继承 | 6h |
| Skill锁定控制 | 强制使用标准模板 | 4h |
| Skill自动升级 | 检测并同步变更 | 4h |

**v2.5 预计工时**: ~14h

---

## 十、v2.6：刚性框架

**目标**: 里程碑锁、审批权校验、自验收阻断、审计系统

**提案**: PROPOSAL_2026-02-020

### v2.5.1 阶段1：R3审计模式 (第1-2周)

| 功能 | 说明 | 工时 | 状态 |
|------|------|------|------|
| 审计日志存储 | audit_log.yaml结构 | 4h | pending |
| 规则引擎基础 | 规则定义+触发+记录 | 8h | pending |
| 日志查询CLI | 查看审计日志 | 4h | pending |
| 里程碑依赖检测 | 检测依赖，记录不阻断 | 6h | pending |
| 自验收检测 | 检测自验收，记录不阻断 | 4h | pending |

**阶段1工时**: 26h

### v2.5.2 阶段2：R2警告模式 (第3-4周)

| 功能 | 说明 | 工时 | 状态 |
|------|------|------|------|
| R2响应实现 | 警告+记录+部分阻断 | 6h | pending |
| 豁免通道 | 紧急情况可申请豁免 | 8h | pending |
| 里程碑阻断 | 前置未完成则阻断 | 6h | pending |
| Skill冲突检测 | 检测Skill与刚性冲突 | 4h | pending |
| 通知集成 | 阻断时Webhook通知 | 4h | pending |

**阶段2工时**: 28h

### v2.5.3 阶段3：R1强制模式 (第5-6周)

| 功能 | 说明 | 工时 | 状态 |
|------|------|------|------|
| R1响应实现 | 直接阻断高风险操作 | 6h | pending |
| 自验收强制阻断 | 禁止自己验收自己的代码 | 6h | pending |
| 审批权校验 | 验证审批人是否有权限 | 4h | pending |
| 动态阈值调优 | 根据阶段2数据调整 | 4h | pending |
| 监控告警 | 阻断率异常时告警 | 4h | pending |

**阶段3工时**: 24h

**v2.5 预计工时**: ~78h

**v2.5 结束标志**:
- [ ] 1260个组合全部覆盖
- [ ] 误阻断率 < 2%
- [ ] 豁免使用率 < 5%
- [ ] 审计周期 ≤ 1周

---

## 十、v3：L3管理平台

**目标**: PM-Agent项目管理

### v3.1 PM-Agent MVP

| 功能 | 说明 | 工时 |
|------|------|------|
| 基础项目CRUD | 创建、查看、编辑项目 | 8h |
| 信息输入 | 文本输入、意图识别 | 8h |
| 项目列表 | 查看所有项目及状态 | 6h |
| 手动进度更新 | 手动更新进度 | 4h |

### v3.2 Git集成

| 功能 | 说明 | 工时 |
|------|------|------|
| Git连接配置 | 配置仓库地址 | 4h |
| 自动拉取 | 定时拉取提交 | 6h |
| 提交分析 | 统计、提取变更 | 6h |
| 进度计算 | 根据提交计算进度 | 4h |

### v3.3 文档自动化

| 功能 | 说明 | 工时 |
|------|------|------|
| 需求文档生成 | 按模板生成 | 4h |
| BUG报告生成 | 按模板生成 | 4h |
| 进度报告生成 | 自动生成周报 | 6h |

### v3.4 oc-collab整合

| 功能 | 说明 | 工时 |
|------|------|------|
| 需求导入oc-collab | 一键转成TODO | 4h |
| 进度同步 | oc-collab进度回写 | 4h |

---

## 十一、版本总结

| 版本 | 目标 | 预计工时 | 状态 |
|------|------|----------|------|
| v2.0 | 基础框架 | - | ✅ |
| v2.1 | 异常处理 | - | ✅ |
| v2.2 | 流程规范 | ~35h | ✅ |
| v2.3.0 | 质量保证 | ~18h | ✅ |
| v2.3.1 | TODO多Agent支持 | ~23h | ✅ |
| v2.3.2 | TODO存储+通知 | ~15h | 🔄 POC完成 |
| v2.3.3 | Skill遵从+自动流程 | ~17h | ⏳ pending |
| v2.3.4 | 配置管理 | ~26h | ⏳ 设计完成 |
| v2.4 | 刚性框架 | ~78h | ⏳ |
| v2.5 | Agent扩展 + Skill系统 | ~14h | ⏳ |
| v3.x | PM-Agent | ~60h | ⏳ |

---

## 十二、相关Proposal

| Proposal | 内容 |
|----------|------|
| PROPOSAL_2026-02-015 | 版本规划 + L1 Skill系统 |
| PROPOSAL_2026-02-016 | TODO优化（应用层）- 已整合到v2.3.1 |
| PROPOSAL_2026-02-017 | TODO通信系统 - 已整合到v2.4 |
| PROPOSAL_2026-02-018 | PM-Agent设计 |
| PROPOSAL_2026-02-019 | 里程碑锁机制 |
| PROPOSAL_2026-02-020 | 刚性框架实施规划 |
| PROPOSAL_2026-02-021 | TODO系统整合设计 |
| PROPOSAL_2026-02-022 | 签署流程设计 |
| PROPOSAL_2026-02-023 | 状态管理系统 |
| PROPOSAL_2026-02-024 | Git集成方案 |
| PROPOSAL_2026-02-025 | Agent协作规范 |
| PROPOSAL_2026-02-027 | Agent通知交互方案 - ✅ POC已通过 |
| PROPOSAL_2026-02-028 | 配置管理模块设计 |

---

**作者**: Agent 1 + Consultant  
**日期**: 2026-02-17  
**版本**: v5
