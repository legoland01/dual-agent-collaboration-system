# 开发任务书：oc-collab agent 守护进程

**版本**: v1  
**创建日期**: 2026-02-01  
**任务负责人**: Agent 2 (开发)  
**产品经理**: Agent 1  
**关联需求**: requirements_agent_daemon_v1.1  
**关联设计**: detailed_design_agent_daemon_v1

---

## 一、任务概述

开发 oc-collab agent 守护进程功能，实现双 Agent 自动协作流程。

## 二、开发任务清单

| 序号 | 任务 | 文件 | 优先级 | 验收标准 |
|------|------|------|--------|----------|
| M1 | AgentDaemon 后台模式 | `src/core/daemon.py` | 高 | 支持 --daemon 参数，守护进程正常后台运行 |
| M2 | ProcessSupervisor 进程监管 | `src/core/supervisor.py` | 高 | 异常退出后自动重启，限制重启次数 |
| M3 | Git 超时控制 | `src/core/git_monitor.py` | 中 | git status/add/commit/push 超时生效 |
| M4 | CLI 命令集成 | `src/cli/main.py` | 高 | oc-collab agent 命令正常工作 |
| M5 | 单元测试 | `tests/test_agent_daemon.py` | 中 | 核心功能测试覆盖率 > 80% |

---

## 三、开发顺序

### 第一阶段：核心模块
- **M1** `src/core/daemon.py` - AgentDaemon 类
  - daemonize() 方法
  - PID 文件管理
  - 信号处理
  - 日志记录

- **M2** `src/core/supervisor.py` - ProcessSupervisor 类
  - 进程监控
  - 自动重启逻辑
  - 退避策略
  - 重启次数限制

### 第二阶段：功能集成
- **M3** `src/core/git_monitor.py` - Git 超时控制
  - timeout 参数支持
  - 超时配置表

- **M4** `src/cli/main.py` - CLI 集成
  - --daemon 参数
  - --interval 参数
  - --status 参数

### 第三阶段：测试验证
- **M5** `tests/test_agent_daemon.py` - 单元测试
  - AgentDaemon 测试
  - ProcessSupervisor 测试
  - Git 超时测试

---

## 四、验收标准

### 必须通过
- [ ] `oc-collab agent` 前台模式正常启动运行
- [ ] `oc-collab agent --daemon` 后台模式正常启动
- [ ] `oc-collab agent --interval 30` 配置生效
- [ ] 守护进程异常退出后自动重启（最多5次/小时）
- [ ] Git 操作超时控制生效（status 10s, add 5s, commit 10s, push 60s）
- [ ] PID 文件正确创建和删除
- [ ] SIGTERM/SIGINT 信号正确处理

### 加分项
- [ ] 日志文件正常生成 (logs/agent_daemon.log)
- [ ] 状态文件正确更新 (state/agent_status.yaml)
- [ ] 单元测试覆盖率 > 80%

---

## 五、开发规范

### 5.1 代码风格
- 遵循 PEP 8
- 使用类型提示
- 添加文档字符串

### 5.2 提交规范
```
feat(daemon): 添加 AgentDaemon 类
fix(supervisor): 修复重启计数错误
test(daemon): 添加 AgentDaemon 单元测试
docs: 更新开发记录
```

### 5.3 测试要求
- 每个核心类至少 5 个单元测试
- 测试覆盖率不低于 80%
- 使用 pytest 框架

---

## 六、时间要求

| 阶段 | 内容 | 时间 |
|------|------|------|
| 第一阶段 | M1 + M2 核心模块 | 2 个工作轮次 |
| 第二阶段 | M3 + M4 功能集成 | 2 个工作轮次 |
| 第三阶段 | M5 测试验证 | 1 个工作轮次 |

---

## 七、交付物

| 交付物 | 文件 | 说明 |
|--------|------|------|
| 代码 | `src/core/daemon.py` | AgentDaemon 实现 |
| 代码 | `src/core/supervisor.py` | ProcessSupervisor 实现 |
| 代码 | `src/core/git_monitor.py` | Git 超时实现 |
| 代码 | `src/cli/main.py` | CLI 集成修改 |
| 测试 | `tests/test_agent_daemon.py` | 单元测试 |
| 文档 | `docs/05-development/dev_log_agent_daemon.md` | 开发记录 |

---

## 八、沟通机制

1. **任务获取**: Agent 2 通过 git pull 获取最新任务书
2. **进度更新**: 每次提交更新开发记录
3. **问题反馈**: 通过评审文档沟通

---

## 九、签署

**产品经理**: Agent 1  
**任务负责人**: Agent 2  
**创建时间**: 2026-02-01
