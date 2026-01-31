# 需求规格说明书：oc-collab agent 守护进程

**版本**: v1.1 (根据 Agent 2 评审意见更新)  
**创建日期**: 2026-02-01  
**更新日期**: 2026-02-01  
**作者**: Agent 1 (产品经理)

## 1. 背景

当前 oc-collab 框架存在以下问题：
1. 依赖人工干预，无法自动执行
2. 两个 Agent 只是逻辑角色，不是真正的独立 session
3. 没有完整的自动化流程

## 2. 需求概述

### 2.1 功能名称
- **功能名称**: oc-collab agent 守护进程
- **功能编号**: FEATURE-009
- **优先级**: 高

### 2.2 目标
实现真正的双 Agent 自动协作流程：
- oc-collab agent 作为守护进程持续运行
- 根据状态自动触发相应的 Agent
- 两个 Agent 通过 Git 真正独立协作
- 全流程自动化，无需人工干预

## 3. 功能需求

### 3.1 状态监控器
**需求编号**: FR-MONITOR-001

**描述**: 守护进程持续监控 oc-collab 状态和 Git 状态

**监控内容**:
- 当前阶段（phase）
- 签署状态（signoff status）
- Git 变更（git status --porcelain）
- 新提交（git log）

**触发条件**: 每隔指定间隔（默认 30 秒）检查一次

### 3.2 任务调度器
**需求编号**: FR-SCHEDULER-001

**描述**: 根据当前状态触发相应的 Agent

**阶段与任务映射**:

| 阶段 | 触发 Agent | 任务 |
|------|-----------|------|
| requirements_review | Agent 1 | 签署需求 |
| requirements_review | Agent 2 | 签署需求 |
| design_review | Agent 1 | 签署设计 |
| design_review | Agent 2 | 签署设计 |
| development | Agent 2 | 开发功能 |
| testing | Agent 1 | 执行测试 |
| testing | Agent 2 | 修复 Bug（如有） |

### 3.3 阶段推进器
**需求编号**: FR-ADVANCE-001

**描述**: 检测条件满足时自动推进阶段

**推进规则**:
- requirements_review → design_draft: 双方签署完成
- design_review → development: 双方签署完成
- development → testing: 开发完成
- testing → deployment: 双方签署完成
- testing → development: 发现 Bug 时回退

### 3.4 Agent 生命周期管理
**需求编号**: FR-LIFECYCLE-001

**描述**: 管理 Agent Session 的启动、执行、停止

**功能**:
- 启动 Agent Session
- 监控执行状态
- 处理失败和重试
- 记录执行历史

### 3.4.1 后台模式（新增）
**需求编号**: FR-LIFECYCLE-002

**描述**: 支持守护进程后台运行模式

**实现方式**:
```bash
# 前台运行（调试用）
oc-collab agent

# 后台运行（生产用）
oc-collab agent --daemon
```

**实现细节**:
- 使用 `os.fork()` 实现 daemon 化
- 重定向标准输入/输出/错误到 /dev/null
- 创建新会话 (`os.setsid()`)
- 使用 PID 文件记录进程 ID
- 支持 `SIGTERM` 信号优雅关闭

### 3.4.2 自动重启机制（新增）
**需求编号**: FR-LIFECYCLE-003

**描述**: 守护进程异常退出后自动重启

**实现方式**:
- 主进程监控子进程状态
- 子进程异常退出后自动重启
- 重启次数限制（最多 5 次/小时）
- 重启间隔指数退避（1s, 2s, 4s, 8s...）

### 3.5 Git 通信机制
**需求编号**: FR-GIT-001

**描述**: 定义 Agent 之间通过 Git 通信的协议

**通信流程**:
1. Agent 执行任务
2. 生成产出物（文档、代码）
3. git add → git commit → git push
4. 守护进程检测到新提交
5. 触发下一个 Agent

## 4. 非功能需求

### 4.1 可靠性
- 守护进程异常退出后自动重启（FR-LIFECYCLE-003）
- Agent 执行失败自动重试（最多 3 次）
- 状态变更原子性保证

### 4.2 性能
- 状态检查间隔可配置（默认 30 秒）
- Git 操作超时控制（FR-GIT-002）

### 4.3 Git 超时控制（新增）
**需求编号**: FR-GIT-002

**描述**: 为 Git 操作设置超时，避免长时间阻塞

**超时配置**:
| 操作 | 超时时间 |
|------|----------|
| git status | 10 秒 |
| git add | 5 秒 |
| git commit | 10 秒 |
| git push | 60 秒 |
| git pull | 30 秒 |

**实现方式**:
```python
subprocess.run(
    ['git', 'push'],
    timeout=60,  # 60 秒超时
    cwd=project_path
)
```

### 4.3 可观测性
- 完整的状态日志
- 执行历史记录
- 错误追踪

## 5. 接口需求

### 5.1 CLI 命令

```bash
# 启动守护进程（交互模式）
oc-collab agent

# 启动守护进程（后台模式）
oc-collab agent --daemon

# 指定检查间隔
oc-collab agent --interval 60

# 查看状态
oc-collab agent status
```

### 5.2 状态文件

守护进程状态存储在 `state/agent_status.yaml`:

```yaml
status: running
last_check: "2026-02-01T12:00:00"
agents_run: 10
errors: 0
```

## 6. 验收标准

- [x] 守护进程持续运行，不间断
- [x] 状态检查按指定间隔执行
- [x] 根据阶段正确触发 Agent
- [x] Agent 执行失败自动重试
- [x] 阶段按规则自动推进
- [x] 所有操作有完整日志
- [ ] 后台模式（--daemon）正常工作
- [ ] 守护进程异常退出后自动重启
- [ ] Git 操作超时控制生效
- [ ] 阶段按规则自动推进
- [ ] 所有操作有完整日志

## 7. 依赖

- oc-collab 核心框架
- Git
- Python 3.9+

## 8. 里程碑

| 里程碑 | 内容 | 交付物 |
|--------|------|--------|
| M1 | 状态监控器 | 代码和测试 |
| M2 | 任务调度器 | 代码和测试 |
| M3 | 完整集成 | 端到端测试 |
