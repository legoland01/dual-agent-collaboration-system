# 双Agent协作框架 - 系统设计

## 版本信息
- **版本**: v1
- **关联需求版本**: v1
- **创建日期**: 2026-01-31
- **作者**: Agent 1 (产品经理)

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
main
├── requirements-v1     (需求版本标签)
├── design-v1           (设计版本标签)
├── test-v1-passed      (测试通过标签)
└── release-v1.0.0      (发布标签)

feature/*              (功能开发分支)
requirements-review-*  (需求评审分支)
design-review-*        (设计评审分支)
fix/*                  (修复分支)
```

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

## 5. 部署方案

### 5.1 部署模式
- 本地开发环境
- CI/CD 环境

### 5.2 安装方式
```bash
# 方式1: pip 安装
pip install opencode-collaboration

# 方式2: 源码安装
git clone <repo>
cd opencode-collaboration
pip install -e .
```

## 6. 未来扩展

### 6.1 计划中的功能
- Web UI 管理界面
- 通知集成（邮件、Slack、飞书）
- AI 辅助生成测试用例
- 模板市场

### 6.2 扩展点
- 插件系统支持自定义工作流
- 多语言支持
- 导出报告功能
