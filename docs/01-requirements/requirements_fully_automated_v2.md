# 双Agent全自动协作框架需求文档

## 版本信息
- **版本**: v2
- **创建日期**: 2026-01-31
- **作者**: Agent 1 (产品经理)
- **变更类型**: 重大功能重构

## 1. 概述

### 1.1 背景
当前双Agent协作框架CLI需要用户手动切换Agent、监控状态、执行操作，无法实现零干预自动协作。用户期望启动两个Terminal窗口后，两个Agent能够完全自主地协作完成整个开发流程，包括：需求评审、详细设计方案评审、白盒测试、黑盒测试、Bug修复、部署上线，全部文档自动生成。

### 1.2 目标
实现**零干预全自动化双Agent协作模式**：
- 用户只需在两个Terminal窗口启动Agent
- Agent 1（产品经理+测试+部署）自动工作
- Agent 2（开发）自动工作
- 两个Agent通过Gitee自动同步、评审、确认
- 全流程无需人工干预

### 1.3 范围
本需求定义一个完整的**自主Agent协作系统**，包含：
- Agent自主行为引擎
- 自动化触发和协调机制
- Agent间通信协议
- 全流程状态机
- 文档自动生成器

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     用户启动 (仅此一步)                               │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           ┌────────────────┐        ┌────────────────┐
           │ Terminal 1     │        │ Terminal 2     │
           │ Agent 1 (PM)   │        │ Agent 2 (Dev)  │
           │                │        │                │
           │ - 需求编写     │        │ - 需求评审     │
           │ - 需求评审     │◀──────▶│ - 设计开发     │
           │ - 设计评审     │        │ - 白盒测试     │
           │ - 黑盒测试     │        │ - Bug修复      │
           │ - 部署上线     │        │                │
           └────────────────┘        └────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │       Gitee            │
                    │  - 代码仓库            │
                    │  - 文档仓库            │
                    │  - 状态文件            │
                    │  - CI/CD触发           │
                    └────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │       GitHub           │
                    │  - 自动化测试          │
                    │  - 质量门禁            │
                    │  - 部署触发            │
                    └────────────────────────┘
```

### 2.2 Agent核心组件

每个Agent包含以下核心组件：

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Agent Core                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  Git Monitor    │  │  Brain Engine   │  │  Task Executor  │    │
│  │  - 监控远程变化  │  │  - 决定做什么   │  │  - 执行具体任务  │    │
│  │  - 检测触发信号  │  │  - 状态机转换   │  │  - 编写文档     │    │
│  │  - 拉取最新状态  │  │  - 规则匹配     │  │  - 编写代码     │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │  Doc Generator  │  │  Tester         │  │  Deployer       │    │
│  │  - 自动生成文档  │  │  - 白盒测试     │  │  - 打包部署     │    │
│  │  - 模板填充     │  │  - 黑盒测试     │  │  - 发布上线     │    │
│  │  - 格式转换     │  │  - 回归测试     │  │  - 通知用户     │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.3 Agent职责定义

| 阶段 | Agent 1 (产品经理+测试+部署) | Agent 2 (开发) |
|-----|---------------------------|---------------|
| 项目初始化 | 创建项目结构、初始化状态 | 等待需求 |
| 需求阶段 | 编写需求文档 | 检测需求、评审需求 |
| 设计阶段 | 评审设计文档 | 编写详细设计 |
| 开发阶段 | 等待开发完成 | 编写代码、白盒测试 |
| 测试阶段 | 编写黑盒测试、执行测试 | 修复Bug |
| 部署阶段 | 执行部署、验证上线 | 协助验证 |

## 3. 自动化触发机制

### 3.1 触发信号定义

Agent通过检测Git事件来判断是否需要行动：

| 信号类型 | Git标识 | 触发条件 | 响应Agent |
|---------|--------|---------|----------|
| 新需求创建 | `docs/01-requirements/requirements_*.md` 新增 | Agent 2 检测到新需求文件 | Agent 2 |
| 需求评审待处理 | `requirements_review_v*.md` 状态更新 | Agent 1 检测到待评审 | Agent 1 |
| 需求评审完成 | `requirements_*_review_v*.md` 已签署 | Agent 2 检测到评审通过 | Agent 2 |
| 新设计创建 | `docs/02-design/detailed_design_*.md` 新增 | Agent 1 检测到新设计文件 | Agent 1 |
| 设计评审完成 | `design_review_v*.md` 已签署 | Agent 2 检测到设计通过 | Agent 2 |
| 开发完成 | `src/` 目录代码提交 | Agent 1 检测到代码更新 | Agent 1 |
| 测试用例创建 | `docs/03-test/test_case_*.md` 新增 | Agent 2 检测到测试用例 | Agent 2 |
| Bug报告创建 | `docs/03-test/bug_report_*.md` 新增 | Agent 2 检测到Bug | Agent 2 |
| 部署就绪 | `deployment/` 目录就绪 | Agent 1 检测到可部署 | Agent 1 |

### 3.2 轮询机制

```python
# Agent轮询配置
POLLING_CONFIG = {
    "interval": 10,          # 轮询间隔（秒）
    "timeout": 3600,         # 单阶段超时时间（秒）
    "max_retries": 3,        # 最大重试次数
    "debounce": 5            # 防抖动时间（秒）
}
```

### 3.3 状态检测流程

```
检测远程变化
     │
     ├── git fetch → 获取远程引用
     │
     ├── 对比本地 vs 远程
     │
     ├── 识别变化类型
     │      │
     │      ├── 新文件 → 触发相应Agent
     │      ├── 文件更新 → 检查内容变化
     │      └── 状态变更 → 检查签署状态
     │
     └── 决定行动
```

## 4. Agent自主行为规则

### 4.1 Agent 1 行为规则

#### 4.1.1 需求编写行为

**触发条件**：
- `state/project_state.yaml` 中 `phase == "project_init"`

**行为序列**：
```
1. 创建需求文档
   - docs/01-requirements/requirements_{project_name}_v1.md
   - 使用模板填充
   
2. 创建状态文件
   - state/project_state.yaml 更新 phase: "requirements_draft"
   - 设置 requirements.pm_signoff: false
   - 设置 requirements.dev_signoff: false
   
3. 提交Git
   - git add → commit → push
   
4. 进入等待状态
   - 等待 Agent 2 评审
```

#### 4.1.2 需求评审行为

**触发条件**：
- 检测到 `docs/01-requirements/requirements_*_review_v*.md` 文件存在

**行为序列**：
```
1. 读取评审文档
   
2. 检查评审内容
   - 如果有未解决问题 → 进入回复流程
   - 如果全部通过 → 进入签署流程
   
3. 签署需求
   - 更新 state/project_state.yaml
   - requirements.pm_signoff: true
   
4. 提交Git
```

#### 4.1.3 设计评审行为

**触发条件**：
- 检测到 `docs/02-design/detailed_design_*.md` 文件存在

**行为序列**：
```
1. 读取设计文档

2. 评审设计
   - 检查完整性
   - 检查可行性
   - 生成评审意见
   
3. 创建评审文档
   - docs/02-design/design_review_{project}_v1.md
   
4. 提交Git
```

#### 4.1.4 黑盒测试行为

**触发条件**：
- `phase == "testing"` 且 `requirements.dev_signoff == true`

**行为序列**：
```
1. 编写黑盒测试用例
   - docs/03-test/test_case_{project}_blackbox_v1.md
   
2. 执行黑盒测试
   
3. 生成测试报告
   - docs/03-test/test_report_{project}_blackbox_v1.md
   
4. 处理测试结果
   - 如果通过 → 签署测试，进入部署
   - 如果失败 → 创建Bug报告
```

#### 4.1.5 部署上线行为

**触发条件**：
- `phase == "deployment"`

**行为序列**：
```
1. 准备部署包
   
2. 执行部署
   
3. 验证部署
   - 健康检查
   - 功能验证
   
4. 更新状态
   - phase: "completed"
   
5. 生成部署报告
   - docs/04-deployment/deployment_report_v1.md
```

### 4.2 Agent 2 行为规则

#### 4.2.1 需求评审行为

**触发条件**：
- 检测到 `docs/01-requirements/requirements_*.md` 新文件

**行为序列**：
```
1. 读取需求文档
   
2. 技术评审
   - 检查技术可行性
   - 识别技术风险
   - 估算工作量
   
3. 创建评审文档
   - docs/01-requirements/requirements_{project}_review_v1.md
   
4. 提交Git
```

#### 4.2.2 评审响应行为

**触发条件**：
- 检测到 `requirements_*_review_v*.md` 有Agent 1的回复

**行为序列**：
```
1. 读取回复内容
   
2. 处理回复
   - 如果需要修改需求 → 等待需求更新
   - 如果需要澄清 → 创建澄清问题
   - 如果可以确认 → 进入签署流程
   
3. 签署需求
   - 更新 state/project_state.yaml
   - requirements.dev_signoff: true
   
4. 提交Git
```

#### 4.2.3 详细设计行为

**触发条件**：
- `phase == "requirements_approved"`

**行为序列**：
```
1. 创建设计文档
   - docs/02-design/detailed_design_{project}_v1.md
   
2. 提交Git
```

#### 4.2.4 设计与实现行为

**触发条件**：
- `phase == "design_approved"`

**行为序列**：
```
1. 实现代码
   - src/ 目录
   
2. 编写单元测试
   - tests/ 目录
   
3. 执行白盒测试
   
4. 提交Git
```

#### 4.2.5 Bug修复行为

**触发条件**：
- 检测到 `docs/03-test/bug_report_*.md` 文件

**行为序列**：
```
1. 读取Bug报告
   
2. 复现Bug
   
3. 修复Bug
   
4. 回归测试
   
5. 更新Bug报告
   - 标记已修复
   
6. 提交Git
```

## 5. 状态机设计

### 5.1 完整状态转换图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           状态机                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐                                                         │
│  │ project_init│                                                         │
│  └──────┬──────┘                                                         │
│         │ 创建项目                                                        │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │ requirements│                                                         │
│  │   _draft    │                                                         │
│  └──────┬──────┘                                                         │
│         │ Agent 1 创建需求文档                                            │
│         ▼                                                                │
│  ┌─────────────┐     ┌─────────────────┐                                 │
│  │ requirements│ ───▶│ requirements    │                                 │
│  │   _review   │     │   _review_cycle │                                 │
│  └──────┬──────┘     │  (循环直到通过)  │                                 │
│         │             └─────────────────┘                                 │
│         │ Agent 2 评审                                                   │
│         │ Agent 1 签署                                                   │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │ requirements│                                                         │
│  │  _approved  │                                                         │
│  └──────┬──────┘                                                         │
│         │ Agent 2 开始设计                                                │
│         ▼                                                                │
│  ┌─────────────┐     ┌─────────────────┐                                 │
│  │  design     │ ───▶│ design_review   │                                 │
│  │   _draft    │     │  _cycle         │                                 │
│  └──────┬──────┘     │  (循环直到通过)  │                                 │
│         │             └─────────────────┘                                 │
│         │ Agent 2 创建设计                                                │
│         │ Agent 1 评审                                                    │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │ design      │                                                         │
│  │  _approved  │                                                         │
│  └──────┬──────┘                                                         │
│         │ Agent 2 开始开发                                                │
│         ▼                                                                │
│  ┌─────────────┐     ┌─────────────────┐                                 │
│  │ development │ ───▶│ bug_fix_cycle   │                                 │
│  └──────┬──────┘     │  (循环直到无Bug) │                                 │
│         │             └─────────────────┘                                 │
│         │ Agent 2 开发+测试                                               │
│         │ Agent 1 黑盒测试                                                │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │   testing   │                                                         │
│  └──────┬──────┘                                                         │
│         │ Agent 1 签署测试                                                │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │ deployment  │                                                         │
│  └──────┬──────┘                                                         │
│         │ Agent 1 部署                                                    │
│         ▼                                                                │
│  ┌─────────────┐                                                         │
│  │  completed  │ ◀──────────────────────────────┐                        │
│  └─────────────┘                                  │                        │
│                                                  │ 完成                                           │
└──────────────────────────────────────────────────┘
```

### 5.2 状态文件结构

```yaml
phase: "requirements_review"

requirements:
  version: "v1"
  pm_signoff: true
  dev_signoff: true
  status: "approved"
  review_cycles: 1

design:
  version: "v1"
  pm_signoff: false
  dev_signoff: false
  status: "pending"

test:
  version: ""
  blackbox_cases: 0
  blackbox_passed: 0
  status: "pending"

development:
  status: "in_progress"
  branch: "main"
  last_updated: "2026-01-31"

deployment:
  status: "pending"
  version: ""
  last_updated: ""

metadata:
  current_agent: "2"  # 当前应该工作的Agent
  auto_mode: true     # 是否全自动模式
  polling_interval: 10  # 轮询间隔（秒）
```

## 6. Agent间通信协议

### 6.1 通信方式
两个Agent通过Git进行异步通信，不直接网络连接。

### 6.2 消息类型

| 消息类型 | 文件位置 | 说明 |
|---------|---------|------|
| 需求文档 | `docs/01-requirements/` | Agent 1 → Agent 2 |
| 需求评审 | `docs/01-requirements/*_review_*.md` | Agent 2 → Agent 1 |
| 设计文档 | `docs/02-design/detailed_design_*.md` | Agent 2 → Agent 1 |
| 设计评审 | `docs/02-design/*_review_*.md` | Agent 1 → Agent 2 |
| 测试用例 | `docs/03-test/test_case_*.md` | Agent 1 → Agent 2 |
| Bug报告 | `docs/03-test/bug_report_*.md` | Agent 1 → Agent 2 |
| 状态更新 | `state/project_state.yaml` | 双方共享 |

### 6.3 通信流程示例

```
场景：需求评审流程

1. Agent 1 创建需求文档
   └── docs/01-requirements/requirements_project_v1.md
   └── state/project_state.yaml (phase: requirements_review)

2. Agent 2 检测到新需求
   └── git pull
   └── 读取需求文档
   └── 创建评审文档
   └── docs/01-requirements/requirements_project_review_v1.md
   └── git add → commit → push

3. Agent 1 检测到评审完成
   └── git pull
   └── 读取评审文档
   └── 如果通过，签署需求
   └── state/project_state.yaml (requirements.pm_signoff: true)
   └── git add → commit → push

4. Agent 2 检测到签署完成
   └── git pull
   └── 签署需求
   └── state/project_state.yaml (requirements.dev_signoff: true)
   └── git add → commit → push

5. 状态机转换
   └── phase: requirements_approved
```

## 7. 文档自动生成

### 7.1 文档模板

系统提供以下模板，Agent自动填充：

| 文档类型 | 模板位置 | 生成者 |
|---------|---------|-------|
| 需求文档 | `templates/requirements_TEMPLATE.md` | Agent 1 |
| 设计文档 | `templates/design_TEMPLATE.md` | Agent 2 |
| 测试用例 | `templates/test_case_TEMPLATE.md` | Agent 1 |
| Bug报告 | `templates/bug_report_TEMPLATE.md` | Agent 1 |
| 测试报告 | `templates/test_report_TEMPLATE.md` | Agent 1 |
| 部署报告 | `templates/deployment_report_TEMPLATE.md` | Agent 1 |

### 7.2 文档生成流程

```
1. Agent 检测需要生成文档
         │
         ▼
2. 选择对应模板
         │
         ▼
3. 填充模板变量
   - 项目名称
   - 阶段信息
   - 时间戳
   - 角色信息
         │
         ▼
4. 生成文档
         │
         ▼
5. 提交Git
```

## 8. 异常处理

### 8.1 异常类型

| 异常类型 | 处理策略 |
|---------|---------|
| Git冲突 | 提示用户，暂停执行 |
| 状态文件损坏 | 回滚到上一个版本 |
| 文档模板缺失 | 使用默认模板 |
| 超时 | 重试3次后暂停 |
| 权限不足 | 提示用户检查权限 |

### 8.2 恢复机制

```
异常发生
     │
     ├── 记录日志
     │
     ├── 保存现场
     │      │
     │      ├── 保存当前状态
     │      ├── 保存工作目录
     │      └── 保存错误信息
     │
     └── 恢复策略
            │
            ├── 可恢复 → 自动重试
            ├── 需干预 → 提示用户
            └── 严重 → 暂停执行
```

## 9. 验收标准

### 9.1 功能验收

| 序号 | 验收项 | 判定标准 |
|-----|--------|---------|
| 1 | Agent 1自动创建需求 | 检测到project_init状态，自动创建需求文档 |
| 2 | Agent 2自动评审需求 | 检测到新需求，自动创建评审文档 |
| 3 | Agent 1自动签署需求 | 检测到评审通过，自动签署 |
| 4 | Agent 2自动创建设计 | 检测到需求批准，自动创建设计 |
| 5 | Agent 1自动评审设计 | 检测到新设计，自动创建评审 |
| 6 | Agent 2自动开发代码 | 检测到设计批准，自动编写代码 |
| 7 | Agent 1自动黑盒测试 | 检测到代码完成，自动编写测试用例 |
| 8 | Agent 2自动修复Bug | 检测到Bug报告，自动修复 |
| 9 | Agent 1自动部署上线 | 检测到测试通过，自动部署 |
| 10 | 全程零用户干预 | 两个Terminal启动后，无需任何手动操作 |

### 9.2 性能验收

| 指标 | 目标值 |
|-----|-------|
| 状态检测延迟 | < 5秒 |
| 文档生成时间 | < 10秒 |
| 代码同步时间 | < 10秒 |
| 异常恢复时间 | < 30秒 |

### 9.3 质量验收

- 所有文档符合模板规范
- 所有代码通过静态检查
- 所有测试用例100%执行
- 所有Bug 24小时内修复

## 10. 实施计划

### 10.1 开发阶段

| 阶段 | 内容 | 工时 | 产出 |
|-----|------|:----:|------|
| 阶段1 | Agent核心框架 | 1天 | Git Monitor、Brain Engine、Task Executor |
| 阶段2 | 状态机实现 | 0.5天 | 完整状态转换逻辑 |
| 阶段3 | 行为规则实现 | 1天 | Agent 1/2 行为规则 |
| 阶段4 | 文档生成器 | 0.5天 | 模板和填充逻辑 |
| 阶段5 | 异常处理 | 0.5天 | 日志、恢复、重试机制 |
| 阶段6 | 测试验证 | 1天 | 全流程测试 |

### 10.2 里程碑

| 里程碑 | 时间 | 验收标准 |
|-------|------|---------|
| M1: 框架就绪 | 第1天 | Agent核心组件可运行 |
| M2: 状态机完成 | 第2天 | 状态转换正常 |
| M3: 全流程打通 | 第3天 | 完整流程测试通过 |
| M4: 发布上线 | 第4天 | 部署验证通过 |

## 11. 风险评估

| 风险 | 可能性 | 影响 | 应对措施 |
|-----|:------:|:----:|---------|
| Agent死锁 | 低 | 高 | 超时机制、自动跳过 |
| Git冲突频繁 | 中 | 中 | 冲突检测、提示用户 |
| 状态不一致 | 低 | 高 | 状态校验、版本控制 |
| 文档质量差 | 中 | 中 | 模板约束、LLM质量控制 |
| 循环依赖 | 低 | 高 | 状态机检查、死循环防护 |

## 12. 签署确认

- **产品经理**: Agent 1  日期: 2026-01-31
- **开发**: Agent 2  日期: 待签署

评审状态：待Agent 2评审
