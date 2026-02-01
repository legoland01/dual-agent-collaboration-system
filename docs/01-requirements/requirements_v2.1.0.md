# 需求规格说明书：oc-collab v2.1.0

**版本**: v1  
**创建日期**: 2026-02-01  
**作者**: Agent 1 (产品经理)  
**版本号**: 2.1.0

---

## 附录 A: Agent 职责分工约束

### A.1 Agent 角色定义

| Agent | 角色 | 主要职责 |
|-------|------|----------|
| Agent 1 | 产品经理 | 创建需求、评审设计、黑盒测试、发布确认 |
| Agent 2 | 开发 | 评审需求、创建设计、代码实现、白盒测试、PyPI 发布 |

### A.2 职责边界

**Agent 1 (产品经理) - 必须做**:
- [x] 创建需求文档
- [x] 评审详细设计文档
- [x] 执行黑盒测试
- [x] 确认部署报告
- [x] 签署发布确认

**Agent 1 (产品经理) - 禁止做**:
- [ ] 创建详细设计文档
- [ ] 编写产品代码
- [ ] 执行白盒测试
- [ ] 直接操作 PyPI 发布

**Agent 2 (开发) - 必须做**:
- [ ] 评审需求文档
- [ ] 创建详细设计文档
- [ ] 实现代码功能
- [ ] 执行白盒测试
- [ ] 构建并上传 PyPI

**Agent 2 (开发) - 禁止做**:
- [ ] 创建需求文档
- [ ] 签署产品需求确认
- [ ] 直接发布到生产环境

### A.3 协作流程

```
需求阶段 (Agent 1 主导)
    │
    ├─ Agent 1 创建需求文档
    │
    └─ Agent 2 评审需求 ──────┐
      │                       │
      │   ├─ 补充遗漏需求 ────────┤ (Agent 2 主动补充)
      │   │   基于开发经验补充:
      │   │   - 异常场景遗漏
      │   │   - 技术约束
      │   │   - 可维护性需求
      │   │
      │   └─ 签署确认 ────────────┘
                              │
设计阶段 (Agent 2 主导)        │
    │                         │
    ├─ Agent 2 创建设计文档    │
    │                         │
    └─ Agent 1 评审设计 ──────┤
                              │
开发阶段 (Agent 2 主导)        │
    │                         │
    ├─ Agent 2 实现代码       │
    │                         │
    └─ Agent 1 执行黑盒测试 ──┤
                              │
发布阶段 (Agent 2 执行, Agent 1 确认)
    │                         │
    ├─ Agent 2 更新版本号      │
    ├─ Agent 2 构建 PyPI 包   │
    ├─ Agent 2 上传 PyPI      │
    │                         │
    └─ Agent 1 签署发布确认 ──┘
```

### A.3.1 Agent 评审时主动补充需求机制

**目的**: 充分发挥多 Agent 协作优势，Agent 2 基于开发经验补充产品经理可能遗漏的需求。

**触发条件**:
- Agent 2 在评审需求文档时

**补充范围**:
| 类型 | 示例 | 价值 |
|------|------|------|
| 异常场景 | 网络中断、磁盘空间、权限问题 | 提高系统健壮性 |
| 技术约束 | API 限制、版本兼容性、性能要求 | 避免实现困难 |
| 可维护性 | 日志规范、监控需求、文档要求 | 降低长期维护成本 |
| 安全考虑 | 输入验证、权限控制、审计日志 | 提高安全性 |

**补充流程**:
```
Agent 2 评审需求
    │
    ├─ 发现遗漏需求
    │
    ├─ 评估影响范围
    │   ├─ P0 (必须): 核心功能缺失、重大风险
    │   ├─ P1 (建议): 重要但非紧急
    │   └─ P2 (可选): 锦上添花
    │
    ├─ 补充需求文档
    │   ├─ 使用 "### 补充-by-Agent2" 标记
    │   ├─ 说明补充原因
    │   ├─ 提供实现建议
    │   └─ 标注优先级
    │
    └─ 双方确认签署
        ├─ Agent 1 确认补充合理
        └─ Agent 2 确认实现可行
```

**补充示例**:
```markdown
### 补充-by-Agent2: 异常处理增强

**补充原因**: 在开发 v2.0.0 时发现网络中断场景未覆盖，导致 Git 操作阻塞。

**需求内容**: 见 FR-EXC-001 网络异常处理

**优先级**: P0

**实现建议**: 使用重试机制，参考 Python tenacity 库
```

**Agent 1 的职责**:
- [x] 欢迎 Agent 2 补充需求
- [x] 评估补充需求的合理性
- [x] 与 Agent 2 讨论优先级
- [x] 纳入最终需求文档

**Agent 2 的职责**:
- [x] 主动发现需求遗漏
- [x] 基于项目经验提出补充
- [x] 提供实现可行性和工作量评估
- [x] 配合 Agent 1 完成确认

**约束**:
- 补充需求需要双方确认
- 重大补充需要更新版本号
- 补充内容使用统一格式标记

### A.4 系统约束机制

**自动约束**:
```python
# 伪代码：Agent 操作验证
def verify_agent_action(agent_id, action_type):
    if agent_id == "agent1" and action_type == "CREATE_DESIGN":
        raise PermissionError("Agent 1 禁止创建设计文档")
    
    if agent_id == "agent2" and action_type == "CREATE_REQUIREMENTS":
        raise PermissionError("Agent 2 禁止创建需求文档")
```

**手动约束**:
- 每个阶段需要双方签署才能推进
- 发布前需要 Agent 1 确认

### A.5 Git 工作流强制约束

**核心原则**：所有双 Agent 通信必须通过 Git 进行，禁止直接读取本地文件。

```
双 Agent 协作通信规则
==========================

✅ 正确做法:
  Agent 1 提交文档 → Git push → Agent 2 Git pull → 读取最新文档
  Agent 2 提交代码 → Git push → Agent 1 Git pull → 读取最新代码
  Agent 1 提交测试报告 → Git push → Agent 2 Git pull → 拉取测试报告

❌ 错误做法（禁止）:
  Agent 2 直接读取本地项目目录的测试报告
  Agent 1 直接读取本地项目目录的代码文件
  Agent 之间通过非 Git 方式传递文件
```

**强制 Git 拉取的操作**：

| 操作 | Agent | 必须执行 | 说明 |
|------|-------|---------|------|
| 读取需求文档 | Agent 2 | `git pull` | 必须获取 Agent 1 最新提交 |
| 读取设计文档 | Agent 1 | `git pull` | 必须获取 Agent 2 最新提交 |
| 读取测试报告 | Agent 2 | `git pull` | 必须获取 Agent 1 最新测试结果 |
| 读取签署记录 | Agent 1/2 | `git pull` | 必须获取对方签署状态 |
| 读取代码变更 | Agent 1 | `git pull` | 必须获取 Agent 2 实现代码 |

**违规检测机制**：

```python
# 伪代码：检测本地文件修改 vs Git 最新版本
def verify_git_workflow(agent_id, file_path):
    local_content = read_local_file(file_path)
    git_content = run_git_show(f"HEAD:{file_path}")
    
    if local_content != git_content:
        raise WorkflowViolation(
            f"Agent {agent_id} 未通过 Git 读取 {file_path}。 "
            f"本地文件与 Git HEAD 不一致，可能直接修改了本地文件。 "
            f"正确做法: git pull → 读取文件"
        )
```

**典型反模式（需避免）**：
```
financial_case_generator_system 项目中的问题:
❌ Agent 2 直接读取 docs/03-test/blackbox_test_results_*.md
✅ 正确做法: git pull → 读取 docs/03-test/blackbox_test_results_*.md
```

**违反此约束的处理**：
| 场景 | 处理方式 | 输出 |
|------|----------|------|
| 检测到本地文件与 Git 不一致 | 阻止读取，提示 Git pull | "请先执行 git pull 获取最新版本" |
| 多次违规 | 记录到状态报告 | 状态报告中标记违规次数 |
| 强制模式 | 抛出异常阻止执行 | "违反 Git 工作流约束"

---

## 附录 B: 部署发布流程

### B.1 发布流程定义

**发布阶段 (Deployment)** 是项目生命周期的关键阶段，包含以下步骤：

```
Deployment 阶段步骤:
│
├─ 1. 测试确认
│   ├─ 所有单元测试通过
│   ├─ 所有集成测试通过
│   └─ 测试报告已生成
│
├─ 2. 部署准备
│   ├─ 更新版本号 (pyproject.toml)
│   ├─ 生成部署报告
│   └─ 更新变更日志
│
├─ 3. 构建发布包
│   ├─ 清理 dist/ 目录
│   ├─ python3 -m build
│   └─ 生成 .whl 和 .tar.gz
│
├─ 4. PyPI 上传
│   ├─ 验证 ~/.pypirc 配置
│   ├─ python3 -m twine upload dist/*
│   └─ 验证上传成功
│
└─ 5. 发布确认
    ├─ Agent 1 签署发布确认
    ├─ 更新项目状态为 released
    └─ 通知利益相关者
```

### B.2 发布责任分配

| 步骤 | 执行者 | 验证者 | 签署 |
|------|--------|--------|------|
| 更新版本号 | Agent 2 | Agent 1 | - |
| 生成部署报告 | Agent 1 | Agent 2 | - |
| 构建发布包 | Agent 2 | - | - |
| PyPI 上传 | Agent 2 | Agent 1 | - |
| 发布确认 | Agent 1 | - | ✅ Agent 1 |

### B.3 发布检查清单

**发布前检查**:
- [ ] 所有测试通过 (pytest)
- [ ] 版本号已更新
- [ ] 部署报告已生成
- [ ] 变更日志已更新
- [ ] PyPI token 配置正确
- [ ] dist/ 目录已清理

**发布后验证**:
- [ ] PyPI 页面可访问
- [ ] pip install 正常
- [ ] 版本号匹配

### B.4 回滚策略

**回滚触发条件**:
- PyPI 上传失败
- 安装包验证失败
- 关键功能测试失败

**回滚步骤**:
```bash
# 1. 删除已上传的包 (PyPI Web UI)
# 2. 回退版本号
git checkout e39c1b7
# 3. 重新构建
python3 -m build
# 4. 重新上传
python3 -m twine upload dist/*
```

---

## 1. 概述

### 1.1 背景

v2.0.0 版本已完成 Agent 守护进程核心功能 (FEATURE-009)，但存在以下遗留问题：

1. **E2E 测试缺失**: 仅有单元测试和长时间运行测试，缺少完整的端到端测试场景
2. **异常处理不完善**: 网络中断、磁盘空间等关键异常未覆盖
3. **可观测性不足**: 缺少资源监控和告警机制
4. **配置更新不便**: 修改配置需要重启守护进程

### 1.2 目标

v2.1.0 版本旨在提升系统稳定性和可维护性：

1. **补充 E2E 测试**: 实现完整的端到端测试覆盖
2. **增强异常处理**: 覆盖关键异常场景
3. **添加监控告警**: 实现资源监控和告警机制
4. **支持配置热重载**: 无需重启即可更新配置

### 1.3 版本范围

| 功能模块 | 优先级 | 状态 |
|---------|--------|------|
| E2E 测试框架 | P0 | 新增 |
| 异常处理增强 | P0 | 新增 |
| 监控告警功能 | P1 | 新增 |
| 配置热重载 | P1 | 新增 |

---

## 2. 功能需求

### 2.1 E2E 测试框架

#### 2.1.1 完整工作流测试

**需求编号**: FR-E2E-001

**描述**: 测试完整的双 Agent 协作流程

**测试场景**:
```
1. 项目初始化 (init)
2. 需求阶段 (requirements_draft → requirements_review → requirements_approved)
3. 设计阶段 (design_draft → design_review → design_approved)
4. 开发阶段 (development)
5. 测试阶段 (testing)
6. 部署阶段 (deployment → completed)
```

**预期结果**: 全流程自动执行，每个阶段正确推进

#### 2.1.2 异常场景测试

**需求编号**: FR-E2E-002

**描述**: 测试各种异常场景的处理

**测试场景**:
| 场景 | 预期行为 |
|------|----------|
| Git 超时 | 抛出异常，记录日志，不阻塞流程 |
| 网络中断 | 重试 3 次，失败后降级处理 |
| 进程崩溃 | Supervisor 自动重启，恢复状态 |
| 配置文件损坏 | 使用默认值，告警提示用户 |
| 磁盘空间不足 | 提前告警，阻止写入 |

#### 2.1.3 并发场景测试

**需求编号**: FR-E2E-003

**描述**: 测试双 Agent 并发操作场景

**测试场景**:
| 场景 | 预期行为 |
|------|----------|
| 同时提交签署 | 串行处理，结果一致 |
| 并发文件写入 | 文件锁保护，无数据损坏 |
| 同时修改状态 | 状态机保证原子性 |

---

### 2.2 异常处理增强

#### 2.2.1 网络异常处理

**需求编号**: FR-EXC-001

**描述**: 处理网络中断导致的 Git 操作失败

**功能**:
| 功能 | 描述 |
|------|------|
| 网络检测 | 操作前检测网络连通性 |
| 自动重试 | 失败后自动重试，最多 3 次 |
| 降级策略 | 重试失败后记录告警，使用缓存 |
| 超时配置 | 可配置的网络超时时间 (默认 30 秒) |

**用户故事**:
> 作为用户，当网络不稳定时，我希望系统能够自动重试 Git 操作，而不是直接失败，这样我可以专注于工作而不被网络问题打扰。

#### 2.2.2 磁盘空间检查

**需求编号**: FR-EXC-002

**描述**: 预防磁盘空间不足导致的写入失败

**功能**:
| 功能 | 描述 |
|------|------|
| 空间检测 | 写入前检查可用空间 |
| 阈值配置 | 可配置的最小剩余空间 (默认 100MB) |
| 自动清理 | 清理过期日志文件 |
| 告警提示 | 空间不足时输出警告 |

**用户故事**:
> 作为用户，当磁盘空间不足时，我希望系统能够提前告警并阻止写入失败，这样我可以及时清理空间而不丢失数据。

#### 2.2.3 权限验证增强

**需求编号**: FR-EXC-003

**描述**: 增强配置文件和目录的权限验证

**功能**:
| 功能 | 描述 |
|------|------|
| 配置文件权限 | 检查配置文件是否可读 |
| 目录权限 | 检查工作目录和日志目录可写 |
| Git 权限 | 验证 Git 仓库的读写权限 |
| 详细错误 | 提供详细的权限错误信息 |

---

### 2.3 监控告警功能

#### 2.3.1 资源监控

**需求编号**: FR-MON-001

**描述**: 监控守护进程的资源使用情况

**监控指标**:
| 指标 | 单位 | 采样频率 |
|------|------|---------|
| CPU 使用率 | % | 10 秒 |
| 内存使用率 | % | 10 秒 |
| 磁盘使用率 | % | 60 秒 |
| Git 操作耗时 | ms | 每次操作 |
| 进程重启次数 | 次 | 每次重启 |
| 异常发生次数 | 次 | 每次异常 |

#### 2.3.2 告警机制

**需求编号**: FR-MON-002

**描述**: 基于阈值的告警通知

**告警规则**:
| 告警级别 | 条件 | 触发阈值 |
|----------|------|----------|
| INFO | 配置变更 | 任意 |
| WARNING | CPU 使用率 | > 80% |
| WARNING | 内存使用率 | > 85% |
| WARNING | 磁盘使用率 | > 90% |
| ERROR | Git 超时 | > 60 秒 |
| ERROR | 进程崩溃 | 任意 |

**告警输出**:
```bash
# CLI 状态输出
oc-collab agent status
[告警] CPU 使用率 85% (阈值: 80%)
[告警] 内存使用率 88% (阈值: 85%)

# 日志输出
[2026-02-01 12:00:00] [WARNING] CPU 使用率 85%
```

#### 2.3.3 状态增强

**需求编号**: FR-MON-003

**描述**: 增强 `oc-collab agent status` 输出

**输出内容**:
```bash
$ oc-collab agent status

Agent 守护进程状态
==================
状态: 运行中
PID: 12345
运行时长: 2h 30m

资源使用:
- CPU: 15%
- 内存: 512MB (32%)
- 磁盘: 45GB (45%)

运行统计:
- 重启次数: 2
- Git 操作: 150 次
- 异常次数: 0

最近告警:
- 无

系统健康: ✅ 良好
```

---

### 2.4 配置热重载

#### 2.4.1 配置变更检测

**需求编号**: FR-CFG-001

**描述**: 监听配置文件变更并自动重新加载

**功能**:
| 功能 | 描述 |
|------|------|
| 文件监听 | 监听配置文件变更 |
| 定期检查 | 定期检查文件修改时间 (默认 60 秒) |
| 变更通知 | 配置变更时输出通知 |
| 优雅重载 | 不中断正在执行的任务 |

#### 2.4.2 热重载生效

**需求编号**: FR-CFG-002

**描述**: 配置变更后无需重启守护进程

**支持热重载的配置**:
| 配置项 | 支持热重载 | 说明 |
|--------|-----------|------|
| polling_interval | ✅ | 轮询间隔 |
| log_level | ✅ | 日志级别 |
| git_timeout | ✅ | Git 超时时间 |
| max_restarts | ✅ | 最大重启次数 |
| backoff_factor | ✅ | 退避因子 |

**不支持热重载的配置**:
| 配置项 | 说明 |
|--------|------|
| project_path | 需要重启 |
| pid_file | 需要重启 |
| log_file | 需要重启 |

#### 2.4.3 配置验证

**需求编号**: FR-CFG-003

**描述**: 新配置加载前的验证

**验证规则**:
| 规则 | 处理方式 |
|------|----------|
| 格式错误 | 回滚到旧配置，输出错误 |
| 值范围超限 | 使用默认值，输出警告 |
| 依赖冲突 | 回滚到旧配置，输出错误 |

---

### 2.5 Agent 行为约束系统

#### 2.5.1 约束配置管理

**需求编号**: FR-CONSTRAINT-001

**描述**: 定义和管理 Agent 的行为约束配置

**约束配置文件**: `state/agent_constraints.yaml`

**配置结构**:
```yaml
agent_constraints:
  version: "1.0"
  last_updated: "2026-02-01"
  
  agent1:
    role: "产品经理"
    allowed_actions:
      - CREATE_REQUIREMENTS      # 创建需求文档
      - REVIEW_DESIGN            # 评审设计文档
      - EXECUTE_BLACKBOX_TEST   # 执行黑盒测试
      - CONFIRM_DEPLOYMENT      # 确认部署
      - SIGN_OFF                # 签署确认
    forbidden_actions:
      - CREATE_DESIGN           # 禁止: 创建设计文档
      - WRITE_CODE              # 禁止: 编写代码
      - EXECUTE_WHITEBOX_TEST  # 禁止: 执行白盒测试
      - UPLOAD_PYPI             # 禁止: 直接操作 PyPI
      
  agent2:
    role: "开发"
    allowed_actions:
      - REVIEW_REQUIREMENTS     # 评审需求文档
      - SUPPLEMENT_REQUIREMENTS # 补充需求文档 (基于开发经验)
      - CREATE_DESIGN           # 创建设计文档
      - WRITE_CODE              # 编写代码
      - EXECUTE_WHITEBOX_TEST  # 执行白盒测试
      - UPLOAD_PYPI             # 上传 PyPI
    forbidden_actions:
      - CREATE_REQUIREMENTS     # 禁止: 创建原始需求文档
      - SIGN_OFF_REQUIREMENTS  # 禁止: 签署需求确认
      - CONFIRM_DEPLOYMENT     # 禁止: 直接确认部署
```

**职责分配**:

| 操作 | Agent 1 | Agent 2 | 说明 |
|------|---------|---------|------|
| 创建原始需求文档 | ✅ 允许 | ❌ 禁止 | Agent 1 的职责 |
| 补充需求文档 | ❌ 禁止 | ✅ 允许 | Agent 2 评审时主动补充 |
| 评审需求文档 | ❌ 禁止 | ✅ 允许 | 开发者评审需求 |
| 确认补充需求 | ✅ 允许 | ❌ 禁止 | 产品经理确认合理性 |
| 实现约束系统代码 | ❌ 禁止 | ✅ 允许 | Agent 2 的职责 |
| 评审约束系统设计 | ✅ 允许 | ❌ 禁止 | 产品经理评审 |
| 执行约束系统测试 | ✅ 允许 | ❌ 禁止 | 黑盒测试 |

**Agent 2 补充需求的权限说明**:
- Agent 2 可以在评审需求时**主动补充**遗漏的需求
- 补充行为标记为 `SUPPLEMENT_REQUIREMENTS`
- 补充后需要 Agent 1 确认 (`CONFIRM_SUPPLEMENT`)
- 补充不能替代原始需求创建 (`CREATE_REQUIREMENTS` 仍禁止)

**约束系统的自我约束**:
- 本需求文档由 Agent 1 创建（符合 CREATE_REQUIREMENTS）
- 本需求的代码由 Agent 2 实现（符合 WRITE_CODE）
- 约束系统本身也遵循约束配置，不允许越权操作

#### 2.5.2 操作验证机制

**需求编号**: FR-CONSTRAINT-002

**描述**: 在执行操作前验证 Agent 权限

**功能**:
| 功能 | 描述 |
|------|------|
| 权限预检查 | 执行操作前验证 Agent 是否有权限 |
| 越权拦截 | 发现越权行为时阻止执行并警告 |
| 动态加载 | 约束配置变更后自动重新加载 |
| 详细日志 | 记录所有权限检查结果 |

**验证流程**:
```
用户请求操作
    │
    ├─ 获取当前 Agent ID
    │
    ├─ 加载约束配置 (agent_constraints.yaml)
    │
    ├─ 检查操作类型
    │   │
    │   ├─ 在 allowed_actions 中 ──→ 允许执行
    │   │
    │   └─ 在 forbidden_actions 中 ─→ 拒绝执行
    │       │
    │       └─ 抛出 PermissionError
    │
    └─ 记录操作日志
```

**用户故事**:
> 作为项目管理者，我希望系统能够自动约束 Agent 的行为范围，确保每个 Agent 只做自己职责范围内的工作，这样协作流程更加规范和可控。

#### 2.5.3 约束违反处理

**需求编号**: FR-CONSTRAINT-003

**描述**: 处理 Agent 越权行为

**处理方式**:
| 场景 | 处理方式 | 输出 |
|------|----------|------|
| 发现越权操作 | 阻止执行 | 错误消息: "Agent 1 禁止执行 CREATE_DESIGN 操作" |
| 自动纠正 | 记录警告日志 | [WARNING] 越权操作尝试: CREATE_DESIGN |
| 统计报告 | 记录越权次数 | 状态报告中包含越权统计 |

**输出示例**:
```bash
$ oc-collab design --create

错误: 越权操作
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent: Agent 1 (产品经理)
操作: CREATE_DESIGN (创建设计文档)
原因: Agent 1 禁止执行此操作
建议: 请 Agent 2 (开发) 创建设计文档
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 2.5.4 约束配置热更新

**需求编号**: FR-CONSTRAINT-004

**描述**: 支持在不重启服务的情况下更新约束配置

**功能**:
- 监听 `state/agent_constraints.yaml` 变更
- 自动重新加载新配置
- 实时生效新的约束规则

**命令**:
```bash
# 查看当前约束配置
oc-collab agent constraints --show

# 重新加载约束配置
oc-collab agent constraints --reload

# 验证约束配置语法
oc-collab agent constraints --validate
```

---

## 2.6 State 结构验证（Agent 2 补充）

### 2.6.1 Schema 定义

**需求编号**: FR-VAL-001

**描述**: 定义项目 state 文件的结构规范，启动时自动验证

**验证范围**:
| 字段 | 类型 | 必填 | 验证规则 |
|------|------|------|---------|
| version | string | 是 | 版本号格式 |
| project.phase | string | 是 | 必须在阶段列表中 |
| design | list/dict | 是 | 列表或字典格式 |
| requirements.status | string | 是 | pending/review/approved |
| test.status | string | 是 | pending/in_progress/passed |

**错误处理**:
| 场景 | 处理方式 | 用户提示 |
|------|---------|---------|
| 字段缺失 | 使用默认值 | WARNING 日志 |
| 类型错误 | 抛出异常 | 详细错误信息 + 参考文档 |
| 格式错误 | 抛出异常 | 期望格式 vs 实际格式 |

### 2.6.2 兼容性检测

**需求编号**: FR-VAL-002

**描述**: 检测 state 文件格式与代码期望是否兼容

**检测逻辑**:
```python
def check_compatibility(state):
    issues = []
    if 'design' in state:
        if isinstance(state['design'], list):
            issues.append("design 字段是列表格式")
        elif isinstance(state['design'], dict):
            issues.append("design 字段是字典格式")
    if 'phase' in state and 'project' not in state:
        issues.append("phase 在根级，请迁移到 project.phase")
    return issues
```

### 2.6.3 State 版本迁移

**需求编号**: FR-VAL-003

**描述**: 自动将旧版本 state 格式迁移到新版本

**迁移规则**:
| 源版本 | 目标版本 | 迁移内容 |
|--------|---------|---------|
| v1.0 | v2.0 | phase: root → project.phase |
| v1.0 | v2.0 | design: 字典 → 列表 |
| v2.0 | v2.1 | 添加 agent_constraints |

**自动迁移触发**:
- 项目初始化时检测版本
- 版本不匹配时自动迁移
- 迁移前备份原始文件
- 迁移后验证完整性

---

## 2.7 包完整性验证（Agent 2 补充）

### 2.7.1 Wheel 内容验证

**需求编号**: FR-PKG-001

**描述**: 确保发布的 wheel 包包含所有必要文件

**必须包含的文件**:
| 文件路径 | 说明 | 重要性 |
|---------|------|--------|
| src/cli/main.py | CLI 入口 | P0 |
| src/cli/agent.py | Agent 命令 | P0 |
| src/core/signoff.py | 签署引擎 | P0 |
| src/core/daemon.py | 守护进程 | P0 |
| src/core/state_manager.py | 状态管理 | P0 |

### 2.7.2 发布前检查清单

**需求编号**: FR-PKG-002

**发布前必须执行**:
- [ ] 运行 `python -m pytest tests/test_package_completeness.py`
- [ ] 验证 wheel 文件大小 > 50KB
- [ ] 验证所有 CLI 命令可用
- [ ] 验证 PyPI 页面可访问

---

## 2.8 用户友好错误提示（Agent 2 补充）

### 2.8.1 错误分类与提示模板

**需求编号**: FR-ERR-001

**描述**: 将技术错误转换为用户友好的提示信息

**错误分类**:
| 错误类型 | 示例 | 提示级别 |
|---------|------|---------|
| State 结构错误 | design 是列表而非字典 | ERROR + 解决建议 |
| Git 操作错误 | git pull 超时 | WARNING + 重试建议 |
| 权限错误 | 无写入权限 | ERROR + 权限说明 |
| 版本不兼容 | state 版本过旧 | ERROR + 迁移指南 |

**提示模板**:
```python
ERROR_TEMPLATES = {
    "STATE_DESIGN_LIST": {
        "title": "State 文件格式不兼容",
        "message": "design 字段是列表格式，但代码期望字典格式。",
        "solution": "请参考 docs/state_structure_guide.md 进行修复。",
    },
    "PHASE_UNKNOWN": {
        "title": "未知的项目阶段",
        "message": "当前 phase 值为 'unknown'，系统无法识别。",
        "solution": "请运行 'oc-collab init' 重新初始化项目。",
    }
}
```

### 2.8.2 上下文相关帮助

**需求编号**: FR-ERR-002

**描述**: 根据错误类型提供相关帮助链接

**帮助系统**:
```bash
$ oc-collab signoff requirements
错误: 当前阶段状态不允许签署: pending
提示: 请先运行 'oc-collab advance --phase requirements' 推进阶段状态。
参考: https://docs/collaboration_guide.md#signoff-flow
```

---

## 2.9 多轮评审机制（Agent 2 补充）

### 2.9.1 评审轮次管理

**需求编号**: FR-REVIEW-001

**描述**: 支持多轮评审，每轮产生独立版本

**轮次编号规则**:
- 第 1 轮: R1 (requirements_v2.1.0.md)
- 第 2 轮: R2 (requirements_v2.1.0_R2.md)
- 第 3 轮: R3 (requirements_v2.1.0_R3.md)

**每轮评审产出**:
| 文件 | 说明 |
|------|------|
| requirements_v2.1.0_R{n}.md | 更新后的需求文档 |
| review_v2.1.0_R{n}.md | 本轮评审意见 |

### 2.9.2 修改追踪

**需求编号**: FR-REVIEW-002

**描述**: 标记哪些内容在本次评审中修改

**修改标记格式**:
```markdown
## v2.1.0 R2 更新内容

### 新增
- [NEW] State Schema 验证机制 (FR-VAL-001)
- [NEW] 包完整性测试 (FR-PKG-001)
```

---

## 3. 非功能需求

### 3.1 性能需求

| 指标 | 要求 |
|------|------|
| 监控采样开销 | < 1% CPU |
| 告警检测延迟 | < 5 秒 |
| 配置重载延迟 | < 1 秒 |
| E2E 测试执行时间 | < 5 分钟 |

### 3.2 可靠性需求

| 场景 | 要求 |
|------|------|
| 网络中断 | 不丢失已执行的操作状态 |
| 进程崩溃 | 自动重启，恢复执行 |
| 配置损坏 | 使用默认配置，不中断服务 |
| 磁盘空间不足 | 提前告警，阻止写入失败 |

### 3.3 可维护性需求

| 需求 | 描述 |
|------|------|
| 测试覆盖 | E2E 测试覆盖率 > 80% |
| 日志记录 | 所有异常和告警都有日志 |
| 配置文档 | 所有配置项都有说明 |

---

## 4. 验收标准

### 4.1 E2E 测试验收标准

| 标准 | 验证方式 |
|------|----------|
| 完整工作流测试通过 | test_full_workflow() |
| 异常场景测试通过 | test_exception_handling() |
| 并发场景测试通过 | test_concurrent_operations() |
| 测试覆盖率 > 80% | pytest-cov |

### 4.2 异常处理验收标准

| 标准 | 验证方式 |
|------|----------|
| 网络中断自动重试 | test_network_retry() |
| 磁盘空间检查生效 | test_disk_space_check() |
| 权限验证生效 | test_permission_check() |
| 异常信息详细 | 手动验证错误消息 |

### 4.3 监控告警验收标准

| 标准 | 验证方式 |
|------|----------|
| 资源监控数据准确 | 对比系统工具 |
| 告警阈值触发正确 | 手动触发阈值 |
| 状态输出完整 | `oc-collab agent status` |
| 日志记录完整 | 检查日志文件 |

### 4.4 配置热重载验收标准

| 标准 | 验证方式 |
|------|----------|
| 配置文件变更检测 | 手动修改配置文件 |
| 热重载生效 | `oc-collab agent status` 显示新配置 |
| 配置验证生效 | 故意设置错误配置 |
| 不影响运行任务 | 观察运行中的任务 |

---

## 5. 依赖

### 5.1 内部依赖

- `src/core/state_machine.py` - 状态机
- `src/core/signoff.py` - 签署引擎
- `src/core/daemon.py` - 守护进程
- `src/core/supervisor.py` - 进程监管
- `src/core/git.py` - Git 操作

### 5.2 外部依赖

| 依赖 | 用途 | 最低版本 |
|------|------|---------|
| psutil | 资源监控 | 5.0.0 |
| watchdog | 文件监听 | 3.0.0 |
| pytest | 测试框架 | 7.0.0 |
| pytest-cov | 覆盖率 | 4.0.0 |

---

## 6. 里程碑

| 里程碑 | 内容 | 交付物 |
|--------|------|--------|
| M1 | E2E 测试框架 | test_e2e.py |
| M2 | 异常处理增强 | exception_handler.py |
| M3 | 监控告警 | monitor.py |
| M4 | 配置热重载 | config_reload.py |
| M5 | 集成测试 | 完整测试套件 |

---

## 7. 风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| E2E 测试复杂度高 | 可能延期 | 分阶段实现，先核心场景 |
| 监控告警性能开销 | 影响守护进程 | 使用轻量级监控，采样频率可配置 |
| 配置热重载竞态 | 可能出现异常 | 添加锁机制，串行化热重载 |

---

## 7.1 问题分析：Agent 1 需求文档为何不完整

### 7.1.1 问题现象

在 v2.1.0 需求评审中，Agent 2 补充了 9 个正式需求，包括：
- State Schema 验证机制 (3个)
- 包完整性测试 (2个)
- 友好错误提示 (2个)
- 多轮评审机制 (2个)

这说明 Agent 1 创建的需求文档存在**遗漏**。

### 7.1.2 原因分析

| 原因 | 说明 | 影响 |
|------|------|------|
| **知识盲点** | Agent 1 未参与 v2.0.0 实际开发，不知道 State 结构不兼容问题 | 遗漏 FR-VAL-001/002/003 |
| **视角差异** | Agent 1 从产品角度思考，Agent 2 从实现角度思考 | 遗漏 FR-PKG-001/002 |
| **经验差距** | Agent 1 缺乏实际打包发布经验 | 遗漏 FR-ERR-001/002 |
| **流程缺失** | 原流程只定义了单轮评审 | 遗漏 FR-REVIEW-001/002 |

### 7.1.3 为什么 Agent 2 能发现这些问题

| Agent | 优势 | 能发现的问题 |
|-------|------|-------------|
| Agent 2 | 参与 v2.0.0 开发，遇到过 State 兼容性问题 | FR-VAL-001/002/003 |
| Agent 2 | 负责打包发布，遇到过 wheel 不完整问题 | FR-PKG-001/002 |
| Agent 2 | 负责问题排查，收到过用户错误反馈 | FR-ERR-001/002 |
| Agent 2 | 实际执行评审，发现单轮评审流程不足 | FR-REVIEW-001/002 |

**结论**: Agent 2 在评审时补充需求，正是多 Agent 协作的核心价值！

### 7.1.4 解决方案

**方案 A：强制多轮评审（已实施）**
- 第 1 轮：Agent 1 创建 → Agent 2 评审 + 补充
- 第 2 轮：Agent 1 更新 → Agent 2 再次评审
- 循环直到双方同意

**方案 B：知识共享机制**
- Agent 2 在开发过程中发现的问题，及时同步给 Agent 1
- 使用 `docs/06-experience/` 记录经验教训

**方案 C：评审检查清单**
- Agent 2 评审时必须检查：
  - [ ] State 结构是否正确定义？
  - [ ] 包完整性是否有测试？
  - [ ] 错误提示是否友好？
  - [ ] 流程是否支持多轮？

### 7.1.5 迭代状态隔离机制（新增）

**问题现象**: `design.status: approved` 是 v2.0.0 的遗留状态，v2.1.0 迭代开始时未被重置，导致状态不一致。

**根因分析**:
| 字段 | 值 | 来源 | 问题 |
|------|------|------|------|
| design.status | approved | v2.0.0 遗留 | v2.1.0 详细设计未关联 |
| development.status | completed | v2.0.0 遗留 | v2.1.0 开发未开始 |
| iteration.status | design | v2.1.0 新增 | ✅ 正确 |

**解决方案**:

**FR-STATE-001: 迭代状态隔离**

```yaml
# 方案：使用迭代维度的状态结构
state:
  deployment:  # 全局状态 (跨迭代共享)
    status: released
    version: 2.0.0
  
  iterations:
    v2.0.0:
      status: completed
      requirements: approved
      design: approved
      development: completed
      testing: passed
      deployment: completed
    
    v2.1.0:
      status: in_progress
      requirements: approved  # 新迭代需要重新审批
      design: in_progress
      development: pending
      testing: pending
      deployment: pending
```

**FR-STATE-002: 状态自动验证**

```python
def validate_iteration_state(iteration_version):
    """验证当前迭代状态与实际进度一致。"""
    state = load_state()
    iteration = state['iterations'].get(iteration_version)
    
    checks = [
        (iteration['requirements'] == 'approved', "需求未审批"),
        (iteration['design'] == 'in_progress' or iteration['design'] == 'approved', "设计阶段状态异常"),
        (iteration['development'] == 'pending', "开发已开始但状态未更新"),
    ]
    
    for passed, message in checks:
        if not passed:
            raise StateInconsistencyError(message)
```

**FR-STATE-003: 状态重置命令**

```bash
# 开始新迭代时重置状态
oc-collab iteration start v2.1.0 --reset-state

# 手动重置指定阶段状态
oc-collab state reset --phase design
```

**验收标准**:
- [ ] 新迭代开始时，所有阶段状态初始化为 `pending`
- [ ] `oc-collab status` 显示当前迭代的正确状态
- [ ] 状态与实际进度不一致时抛出警告
- [ ] 支持手动重置状态命令

### 7.1.6 设计阶段需求变更处理规则

**背景**: 在设计阶段可能发现需求遗漏或需要补充新需求，需要明确的处理规则。

**变更分类**:
| 类型 | 定义 | 示例 | 处理方式 |
|------|------|------|---------|
| **核心变更** | 影响架构、接口、核心功能的变更 | State 结构根本性改变 | 退回需求阶段，重新评审 |
| **流程改进** | 检查清单、验证机制、约束规则 | 状态隔离机制、多轮评审 | 设计评审时补充，无需退回 |
| **缺陷修复** | 代码bug、错误 | 类型错误、逻辑错误 | 直接修复 |
| **文档完善** | 格式、示例、说明 | 文档描述不清晰 | 直接更新 |

**处理流程**:
```
设计阶段发现需求遗漏
        │
        ├─ 评估变更类型
        │   │
        │   ├─ 核心变更 → 退回需求阶段 → 重新评审 → R(n+1)
        │   │
        │   ├─ 流程改进 → 设计评审时补充 → 签署时标注
        │   │
        │   ├─ 缺陷修复 → 直接修复 → 记录在案
        │   │
        │   └─ 文档完善 → 直接更新 → 记录在案
```

**签署规则**:
- 核心变更: 需要 Agent 1 和 Agent 2 重新签署需求
- 流程改进: Agent 2 签署时标注"含新增需求 FR-XXX"
- 缺陷修复/文档完善: 无需特殊处理

**本需求中 FR-STATE-001/002/003 的处理**:
- 类型: 流程改进
- 处理方式: 设计评审时补充
- 签署: Agent 2 签署时标注"含新增需求 FR-STATE-001/002/003"

---

## 7.2 Agent 2 补充需求的正式纳入

### 7.2.1 补充记录

| 轮次 | 补充内容 | 优先级 | 状态 |
|------|---------|--------|------|
| R2 | State Schema 验证 (FR-VAL-001/002/003) | P0 | ✅ 已纳入 |
| R2 | 包完整性测试 (FR-PKG-001/002) | P0 | ✅ 已纳入 |
| R2 | 友好错误提示 (FR-ERR-001/002) | P1 | ✅ 已纳入 |
| R2 | 多轮评审机制 (FR-REVIEW-001/002) | P1 | ✅ 已纳入 |

### 7.2.2 补充价值评估

| 补充需求 | 实际背景 | 价值 |
|---------|---------|------|
| FR-VAL-001 | v2.0.0 开发中遇到 `'list' object has no attribute 'get'` | 避免重复踩坑 |
| FR-PKG-001 | v2.0.0 发布时 wheel 不完整 | 提高发布质量 |
| FR-ERR-001 | 用户反馈错误提示不友好 | 改善用户体验 |
| FR-REVIEW-001 | 单轮评审流程不足 | 规范评审流程 |

**总计**: Agent 2 补充了 9 个需求条目，提升了需求完整性。

---

## 8. 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-01 | 待签署 |
| 开发负责人 | Agent 2 | 2026-02-01 | 待签署 |
| 测试负责人 | - | - | 待确认 |
