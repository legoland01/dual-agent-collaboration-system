# 双Agent协作框架 - 系统设计

## 版本信息
- **版本**: v2（根据 Agent 2 评审意见更新）
- **关联需求版本**: v2
- **创建日期**: 2026-01-31
- **作者**: Agent 1 (产品经理)
- **更新日期**: 2026-01-31

## 1. 系统架构

### 1.1 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                    用户层 (User Layer)                   │
│         OpenCode CLI / IDE / Desktop Application         │
├─────────────────────────────────────────────────────────┤
│                   协作框架层 (Collaboration Layer)       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │  状态管理   │ │  工作流引擎 │ │    模板引擎         │ │
│  │ StateManager│ │WorkflowEngine│ │  TemplateEngine    │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                   Git 集成层 (Git Layer)                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │  版本控制   │ │  分支管理   │ │    签署记录         │ │
│  │GitControl  │ │BranchManager│ │  SignoffManager    │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                   存储层 (Storage Layer)                 │
│  ┌─────────────────────┐  ┌────────────────────────────┐ │
│  │  state/project.yaml │  │  docs/**/*.md             │ │
│  └─────────────────────┘  └────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 1.2 技术选型

| 组件 | 技术选择 | 理由 |
|-----|---------|------|
| 开发语言 | Python 3.8+ | 跨平台、生态丰富 |
| 状态文件 | YAML | 人类可读、易于版本控制 |
| 模板引擎 | Jinja2 | 功能强大、广泛应用 |
| Git 集成 | GitPython | 成熟的 Python Git 库 |
| CLI 框架 | Click | 简单易用、OpenCode 原生支持 |
| 终端输出 | Rich | 漂亮的终端 UI |

## 2. 模块设计

### 2.1 状态管理器 (StateManager)

**职责**：
- 读取和写入 `state/project_state.yaml`
- 管理项目当前阶段
- 跟踪签署状态
- 记录协作历史

**核心方法**：
```python
class StateManager:
    def load_state() -> dict
    def save_state(state: dict)
    def update_phase(phase: str)
    def update_signoff(stage: str, agent: str, signed: bool)
    def get_current_phase() -> str
    def get_signoff_status(stage: str) -> dict
```

### 2.2 工作流引擎 (WorkflowEngine)

**职责**：
- 根据当前状态判断下一步操作
- 管理评审流程
- 管理签署流程
- 处理状态转换

**状态机**：
```
project_init
    ├──> requirements_draft
    │         ├──> requirements_review
    │         ├──> requirements_approved
    ├──> design_draft
    │         ├──> design_review
    │         ├──> design_approved
    ├──> development
    ├──> testing
    └──> deployment
```

### 2.3 模板引擎 (TemplateEngine)

**职责**：
- 渲染各类文档模板
- 替换占位符
- 生成版本化的文档

**支持的模板**：
| 模板类型 | 文件路径 |
|---------|---------|
| 需求文档 | `docs/01-requirements/requirements_v{版本}.md` |
| 系统设计 | `docs/01-requirements/system_design_v{版本}.md` |
| 详细设计 | `docs/02-design/detailed_design_v{版本}.md` |
| 评审意见 | `docs/01-requirements/requirements_review_v{版本}.md` |
| 签署确认 | `docs/01-requirements/requirements_signoff.md` |
| 黑盒用例 | `docs/03-test/blackbox_test_cases.md` |
| 白盒结果 | `docs/03-test/whitebox_test_results.md` |
| 黑盒结果 | `docs/03-test/blackbox_test_results.md` |

### 2.4 Git 集成模块

**职责**：
- 初始化 Git 仓库
- 管理分支策略
- 处理提交和推送
- 处理合并冲突

**分支策略**：
```
main (主分支，长期存在)
│
├─ feature/*              (功能开发分支，从 main 创建)
│   ├─ feature/cli-commands
│   └─ feature/state-manager
│
├─ requirements-review-*  (需求评审分支)
│   ├─ requirements-review-1
│   └─ requirements-review-2
│
├─ design-review-*        (设计评审分支)
│   ├─ design-review-1
│   └─ design-review-2
│
└─ fix/*                  (修复分支，从 main 创建)
    ├─ fix/correct-spelling
    └─ fix/resolve-conflict
```

**标签策略**（语义化版本）：

| 阶段 | 标签格式 | 示例 | 说明 |
|-----|---------|------|------|
| 需求确认 | `requirements-v{版本}` | `requirements-v1` | 需求评审通过 |
| 设计确认 | `design-v{版本}` | `design-v1` | 设计评审通过 |
| 测试通过 | `test-v{版本}` | `test-v1` | 测试用例全部通过 |
| 发布版本 | `v{主版本}.{次版本}.{修订版本}` | `v1.0.0` | 正式发布版本 |
| 预发布 | `v{版本}-{预发布标签}` | `v1.0.0-rc1` | 候选发布版本 |

**版本号规则**：
- **主版本 (MAJOR)**: 不兼容的重大变更
- **次版本 (MINOR)**: 向后兼容的功能新增
- **修订版本 (PATCH)**: 向后兼容的问题修复

**签署确认标签**：
当某一阶段双方签署确认后，创建对应的里程碑标签，如：
```bash
git tag requirements-v1
git tag design-v1
git tag test-v1
```

**Git 操作安全机制**：
1. 所有关键操作前强制执行 `git pull`
2. 检测到本地修改时，提示用户先提交或暂存
3. 冲突检测：Git pull 后检查状态，如有冲突提示用户解决
4. 降级方案：当 GitPython 不可用时，使用 subprocess 调用 git 命令

## 3. 数据设计

### 3.1 状态文件结构

```yaml
version: "1.0.0"

project:
  name: "项目名称"
  type: "PYTHON/TYPESCRIPT/MIXED"
  created_at: "创建时间"
  updated_at: "更新时间"

phase: "当前阶段"

agents:
  agent1:
    role: "产品经理"
    current: true/false
  agent2:
    role: "开发"
    current: true/false

requirements:
  version: "v1"
  status: "draft/review/approved"
  pm_signoff: true/false
  dev_signoff: true/false
  review_cycles: 0

design:
  version: "v1"
  status: "draft/review/approved"
  pm_signoff: true/false
  dev_signoff: true/false

test:
  version: "v1"
  status: "pending/in_progress/passed"
  blackbox_cases: 0
  whitebox_passed: 0
  blackbox_passed: 0

development:
  status: "pending/in_progress/completed"
  branch: ""

deployment:
  status: "pending/in_progress/completed"
  version: ""
```

### 3.2 评审意见结构

```markdown
# 评审意见 - {文档类型}

## 基本信息
- **评审版本**: v1
- **评审人**: Agent X
- **评审日期**: YYYY-MM-DD

## 评审意见
| 序号 | 问题描述 | 严重程度 | 建议 |
|------|---------|---------|------|
| 1 | ... | 高/中/低 | ... |

## 决策记录
| 日期 | 决策 | 决策人 |
|-----|------|--------|
| ... | ... | ... |
```

## 4. 安全设计

### 4.1 签署安全
- 签署记录写入文件，不可篡改
- 签署通过 Git 版本控制追溯
- 强制要求双方签署后才能进入下一阶段

### 4.2 访问控制
- 依赖 Git 仓库的访问控制
- 支持私有仓库

### 4.3 审计日志
记录所有关键操作，便于追溯：

| 操作类型 | 记录内容 | 示例 |
|---------|---------|------|
| 状态变更 | 操作人、时间、新状态 | "Agent 1 将状态从 draft 改为 review" |
| 签署操作 | 签署人、时间、阶段 | "Agent 2 签署需求确认" |
| 文件修改 | 操作人、时间、文件 | "Agent 1 更新 requirements_v1.md" |
| Git 操作 | 操作人、时间、操作 | "Agent 1 git push 到 main" |

审计日志存储位置：`docs/04-changelog/audit_log.md`

## 5. 部署方案

### 5.1 部署流程
```
测试通过 (test-v1)
    │
    ├─> 创建发布分支 (release/v1.0.0)
    │         │
    │         ├─> 最后的修复和完善
    │         │
    ├─> 合并到 main
    │         │
    │         └─> 打标签 (v1.0.0)
    │
    └─> 创建 GitHub Release
```

### 5.2 部署检查清单
- [ ] 所有测试用例通过
- [ ] 双方签署确认完成
- [ ] 文档更新完成
- [ ] 版本号更新
- [ ] CHANGELOG 更新

### 5.3 部署模式
- **本地开发环境**: 直接使用源码
- **pip 安装**: `pip install opencode-collaboration`
- **CI/CD 环境**: 通过 GitHub Actions 自动构建和测试

## 6. 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|-----|------|---------|--------|
| v1 | 2026-01-31 | 初始版本 | Agent 1 |
| v2 | 2026-01-31 | 补充分支/标签策略、Git安全机制、审计日志 | Agent 1 |

## 7. 未来扩展

### 7.1 计划中的功能
- Web UI 管理界面
- 通知集成（邮件、Slack、飞书）
- AI 辅助生成测试用例
- 模板市场

### 7.2 扩展点
- 插件系统支持自定义工作流
- 多语言支持
- 导出报告功能
