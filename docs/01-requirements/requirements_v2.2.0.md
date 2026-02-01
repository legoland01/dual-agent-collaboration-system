# 需求规格说明书：oc-collab v2.2.0

**版本**: v2
**创建日期**: 2026-02-01
**作者**: Agent 1 (产品经理)
**版本号**: 2.2.0
**状态**: 评审中 (REVIEW) → 等待Agent 2评审和签署

---

## 附录A: Draft 环节

### A.1 Draft 环节定义

**目的**: 确保 draft 阶段的材料不会意外进入正式流程，避免干扰正式开发工作。

**适用场景**:
- 新版本需求文档 (requirements_v*.md)
- 新版本设计文档 (detailed_design_*.md)
- 实验性功能设计
- 待讨论的提案

### A.2 Draft 文件命名规范

| 类型 | 正式文件 | Draft 文件 |
|------|----------|------------|
| 需求文档 | requirements_v2.2.0.md | requirements_v2.2.0_DRAFT.md |
| 设计文档 | detailed_design_v2.2.0.md | detailed_design_v2.2.0_DRAFT.md |
| 测试用例 | test_cases_v2.2.0.md | test_cases_v2.2.0_DRAFT.md |

**规则**:
1. Draft 文件必须添加 `_DRAFT` 后缀
2. Draft 文件保存在同一目录
3. Draft 文件不进入发布清单

### A.3 Draft 工作流程

```
┌─────────────────────────────────────────────────────────┐
│                     Draft 环节                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 创建 Draft                                          │
│     oc-collab draft create requirements --version 2.2.0 │
│     ↓                                                   │
│     生成: requirements_v2.2.0_DRAFT.md                  │
│     ↓                                                   │
│     状态: DRAFT (草稿)                                   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  2. 评审和修订                                          │
│     - Agent 评审 Draft 内容                             │
│     - 提出修改意见                                       │
│     - 更新 Draft 文件                                    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  3. 提交评审                                            │
│     oc-collab draft submit requirements --version 2.2.0│
│     ↓                                                   │
│     - 检查: 是否包含 _DRAFT 后缀                         │
│     - 检查: 是否满足完成标准                             │
│     - 重命名: _DRAFT.md → .md                           │
│     - 状态: REVIEW (评审中)                              │
│     ↓                                                   │
│     进入正式评审流程                                     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  4. 签署完成                                            │
│     - 双方签署确认                                       │
│     - 状态: APPROVED (已批准)                           │
│     ↓                                                   │
│     进入开发阶段                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### A.4 Draft 文件保护机制

**自动保护**:
```python
# Draft 文件保护规则

PROTECTION_RULES = {
    "draft_files": {
        "pattern": "*_DRAFT.md",
        "protection": {
            "git_ignore": True,        # 默认忽略
            "commit_block": True,      # 阻止提交
            "release_exclude": True    # 不进入发布清单
        }
    },
    
    "正式文件": {
        "pattern": "*.md (无 _DRAFT 后缀)",
        "protection": {
            "git_ignore": False,
            "commit_block": False,
            "release_exclude": False
        }
    }
}
```

**Git 保护**:
```bash
.gitignore 增加:
# Draft 文件
*_DRAFT.md
*_DRAFT_*.md

# 但不忽略正式的 .gitignore 规则
!requirements_v*.md
!detailed_design_v*.md
```

### A.5 Draft 提交检查清单

提交前必须通过以下检查:

| 检查项 | 说明 | 通过标准 |
|--------|------|----------|
| 后缀检查 | 文件名必须包含 `_DRAFT` | `_DRAFT.md` 后缀 |
| 完整性检查 | 文档结构完整 | 包含所有必需章节 |
| 签署检查 | 预留签署位置 | 有签署表格 |
| 链接检查 | 内部链接有效 | 无死链 |
| 格式检查 | Markdown 格式正确 | 无语法错误 |

**命令**:
```bash
# 检查 Draft 文件
oc-collab draft validate --file requirements_v2.2.0_DRAFT.md

# 输出检查报告
# ✓ 后缀检查通过
# ✓ 完整性检查通过
# ✓ 签署检查通过
# ✗ 链接检查失败: [链接不存在]
```

### A.6 Draft 转换为正式文件

**提交 Draft**:
```bash
oc-collab draft submit --file requirements_v2.2.0_DRAFT.md

# 执行:
# 1. 验证 Draft 文件
# 2. 重命名: _DRAFT.md → .md
# 3. 更新状态为 REVIEW
# 4. 创建评审通知
# 5. 提交到 Git
```

**回滚**:
```bash
# 如果发现问题，可以回滚
oc-collab draft rollback --file requirements_v2.2.0.md

# 执行:
# 1. 重命名: .md → _DRAFT.md
# 2. 状态改回 DRAFT
# 3. 记录回滚原因
```

### A.7 交付物完整性检查机制

**问题背景**: 阶段交付时可能出现文档不全、测试缺失等问题（如 M1 缺少测试文件、M4 缺少测试文件）。

**v2.2.0 阶段交付检查清单**:
```yaml
milestone_checklist:
  M1:
    required_deliverables:
      - src/core/agent_manager.py
      - tests/test_agent_manager.py
    
    required_signoffs:
      - dev_signoff: true
      - pm_signoff: false
    
    quality_gates:
      - code_coverage: >= 80%
      - all_tests_pass: true
      - no_critical_bugs: true
  
  M2:
    required_deliverables:
      - src/core/project_manager.py
      - src/core/resource_lock.py
      - tests/test_project_manager.py
      - tests/test_resource_lock.py
    
    required_signoffs:
      - dev_signoff: true
      - pm_signoff: false
```

**检查流程**:
```bash
# 执行阶段检查
oc-collab milestone check --milestone M1

# 输出检查报告
# ✓ src/core/agent_manager.py 存在
# ✗ tests/test_agent_manager.py 缺失
# 检查结果: ❌ 失败
```

**v2.2.0 缺失处理规则**:
| 缺失类型 | 处理方式 | 后续步骤 |
|----------|----------|----------|
| 代码缺失 | 阻断 | 补交前不能签署 |
| 测试缺失 | 阻断 | 补交前不能签署（基于 M4 教训） |
| 文档缺失 | 警告 | 48小时内补交 |
| 签署缺失 | 阻断 | 补签前不能推进 |

**M4 教训总结**:
- 测试文件与代码文件同等重要
- 测试缺失应设为阻断级别，而非警告级别
- 每次里程碑检查前必须确认测试文件完整
- **M5教训**: 验收标准写了"覆盖率>=80%"，但没人真的检查；必须运行coverage命令并分析报告

### A.8 分阶段交付和验收标准

**阶段定义**:
```
需求阶段 → 设计阶段 → 开发阶段(M1-M5) → 测试阶段 → 部署阶段
```

**v2.2.0 开发阶段里程碑**:
| 里程碑 | 内容 | 交付物 | 签署 |
|--------|------|--------|------|
| M1 | 多 Agent 基础 | agent_manager.py, blackbox_tests_M1.md | Agent 1 |
| M2 | 项目管理 | project_manager.py, resource_lock.py, blackbox_tests_M2.md | Agent 1 |
| M3 | 会议管理 | meeting_manager.py, blackbox_tests_M3.md | Agent 1 |
| M4 | 用户故事 | story_e2e_tests.py, blackbox_tests_M4.md | Agent 1 |
| M5 | 完整测试套件 | 集成测试, blackbox_tests_full.md | Agent 1+Agent 2 |

**v2.2.0 验收标准模板**:
```yaml
acceptance_criteria:
  milestone: M1

  code_quality:
    - 代码通过静态检查: true
    - 命名规范一致: true
    - 注释覆盖率 >= 30%: true

  functionality:
    - 核心功能完整实现: true
    - 无阻断性 bug: true

   testing:
     - 单元测试覆盖率 >= 80%: true
     - 核心模块覆盖率 100%: true  # v2.2.0 新增: daemon.py, supervisor.py, signoff.py
     - 所有测试用例通过: true
     - 测试文件完整: true
     - 覆盖率报告已生成: true      # v2.2.0 新增: 必须运行coverage命令
     - 覆盖率报告已分析: true      # v2.2.0 新增: 必须确认核心模块覆盖达标
     - 黑盒测试 P0 用例 100% 通过: true   # v2.2.0 新增: 防止 M5 教训重演
     - 黑盒测试 P1 用例 100% 通过: true   # v2.2.0 新增: CLI 功能验证
     - 黑盒测试结果已记录: true           # v2.2.0 新增: docs/03-test/blackbox_test_results.md
     - E2E 测试完整: true

  signoff:
    dev_signoff: true
    pm_signoff: false
```

**覆盖率检查规则**（详细说明见2.6节）:
| 检查项 | 要求 | 违约处理 |
|--------|------|----------|
| 核心模块覆盖率 | 100% | 阻断: 不能签署 |
| 整体覆盖率 | >=80% | 阻断: 不能签署 |
| 覆盖率下降 | 不能比上次低 | 警告: 需说明原因 |
| 覆盖率报告 | 必须生成 | 阻断: 不能签署 |

**核心模块清单**（必须100%覆盖）:
| 模块 | 文件路径 |
|------|----------|
| 守护进程 | src/core/daemon.py |
| 进程监管 | src/core/supervisor.py |
| 签署引擎 | src/core/signoff.py |
| 状态管理 | src/core/state_manager.py |
| 异常处理 | src/core/exception_handler.py |

> **详细说明**: 覆盖率检查机制见 [2.6 覆盖率检查机制](#26-覆盖率检查机制v210-m5教训)

### A.9 Draft 状态管理

| 状态 | 说明 | 操作 |
|------|------|------|
| DRAFT | 草稿中 | 编辑、评审 |
| REVIEW | 评审中 | 签署、讨论 |
| APPROVED | 已批准 | 等待开发 |
| REJECTED | 被拒绝 | 修订后重新提交 |

**状态转换**:
```
DRAFT → REVIEW    (oc-collab draft submit)
REVIEW → APPROVED (双方签署)
REVIEW → REJECTED (评审不通过)
REJECTED → DRAFT  (修订后重新提交)
APPROVED → DRAFT  (发现重大问题，需回滚)
```

### A.10 v2.2.0 Draft 状态

| 项目 | 文件 | 状态 |
|------|------|------|
| 需求文档 | requirements_v2.2.0_DRAFT.md | DRAFT ⏳ |
| 设计文档 | detailed_design_v2.2.0_DRAFT.md | 未创建 |
| 测试用例 | test_cases_v2.2.0_DRAFT.md | 未创建 |

**当前状态**: 需求文档 Draft 完成，待 Agent 2 评审。

---

## 1. 概述

### 1.1 背景

v2.1.0 已实现多 Agent 基础协作框架，但存在以下限制：

1. **Agent 数量固定**: 当前仅支持 2 个 Agent (Agent 1 + Agent 2)
2. **无 UE/UI 设计管理**: 设计稿管理、对比、评审流程缺失
3. **单技术栈限制**: 难以支持前后端分离、多技术栈项目
4. **项目管理薄弱**: 缺乏多 Agent 任务分配和进度协调

### 1.2 目标

v2.2.0 旨在实现：

1. **多 Agent 动态管理**: 支持 2+ Agent，动态添加/移除
2. **UE/UI 设计工作流**: 设计稿管理、版本、对比、评审
3. **多技术栈协同**: 支持前后端分离，不同技术栈独立 Agent
4. **项目管理增强**: 任务分配、进度协调、冲突避免

### 1.3 版本范围

| 功能模块 | 优先级 | 状态 |
|---------|--------|------|
| 多 Agent 动态管理 | P0 | 新增 |
| UE/UI 设计管理 | P1 | 新增 |
| 多技术栈协同 | P0 | 新增 |
| 项目管理增强 | P0 | 新增 |
| 执行约束管理 | P0 | 新增 |
| **黑盒测试管理** | **P0** | **新增** |

---

## 2. 功能需求

### 2.1 多 Agent 动态管理

#### 2.1.1 Agent 角色体系

**需求编号**: FR-AGENT-001

**描述**: 定义 Agent 角色和初始配置

**初始配置**:
```yaml
项目启动时:
  Agent 数量: 2
  Agent 列表:
    - Agent 1:
        role: 产品经理/项目经理
        responsibilities: 需求管理、项目规划、签署确认
        forbidden: 编写代码
    - Agent 2:
        role: 开发负责人
        responsibilities: 技术架构、后端开发、代码评审
        forbidden: 创建需求
```

**Agent 类型**:
| 类型 | 说明 | 初始数量 |
|------|------|----------|
| 产品经理 | Agent 1 | 1 (必需) |
| 开发负责人 | Agent 2 | 1 (必需) |
| 前端开发 | 根据技术栈 | 动态 |
| 后端开发 | 根据技术栈 | 动态 |
| UI/UE 设计 | 如需要 | 动态 |
| 测试 | 如需要 | 动态 |

#### 2.1.2 Agent 动态添加

**需求编号**: FR-AGENT-002

**描述**: 项目启动后可动态添加 Agent

**命令**:
```bash
# 添加前端 Agent
oc-collab agent add --role frontend --tech react --count 1

# 添加后端 Agent
oc-collab agent add --role backend --tech go --count 1

# 添加设计师
oc-collab agent add --role designer --count 1

# 查看当前 Agent 列表
oc-collab agent list
```

**添加流程**:
```
1. Agent 1 (项目经理) 执行添加命令
2. 系统创建新 Agent 配置文件
3. 新 Agent 初始化，读取项目状态
4. 新 Agent 加入协作
```

#### 2.1.3 Agent 职责约束

**需求编号**: FR-AGENT-003

**描述**: 不同角色 Agent 有不同的职责边界

**约束规则**:
```yaml
Agent 约束:
  产品经理:
    allowed: [CREATE_REQUIREMENTS, REVIEW_DESIGN, SIGN_OFF, MANAGE_PROJECT]
    forbidden: [WRITE_CODE, CREATE_DESIGN]
  
  开发负责人:
    allowed: [REVIEW_REQUIREMENTS, CREATE_DESIGN, WRITE_CODE, CODE_REVIEW]
    forbidden: [CREATE_REQUIREMENTS]
  
  前端开发:
    allowed: [WRITE_CODE_FRONTEND, REVIEW_DESIGN_FRONTEND]
    forbidden: [WRITE_CODE_BACKEND, CREATE_REQUIREMENTS]
  
  后端开发:
    allowed: [WRITE_CODE_BACKEND, API_DESIGN]
    forbidden: [WRITE_CODE_FRONTEND, CREATE_REQUIREMENTS]
  
  设计师:
    allowed: [CREATE_DESIGN, UPLOAD_DESIGN, REVIEW_DESIGN]
    forbidden: [WRITE_CODE, CREATE_REQUIREMENTS]
```

---

### 2.2 UE/UI 设计管理

#### 2.2.1 需求阶段设计决策

**需求编号**: FR-DESIGN-001

**描述**: 需求阶段确定是否需要 UI/UE 设计

**需求文档模板**:
```yaml
需求文档:
  design_requirements:
    need_ui_design: true/false  # 是否需要 UI 设计
    design_scope: [web, mobile, both]  # 设计范围
    design_type: [new, redesign, update]  # 设计类型
    reference_links: []  # 参考链接
```

**触发条件**:
- `need_ui_design: true` 时，Agent 1 可添加设计师 Agent

#### 2.2.2 设计稿上传

**需求编号**: FR-DESIGN-002

**描述**: 设计师上传设计稿文件

**命令**:
```bash
# 上传设计稿
oc-collab design upload --file header.png --component navbar

# 上传并添加标注
oc-collab design upload --file homepage.png --annotations annotations.md

# 上传 Figma 链接
oc-collab design upload --link https://figma.com/file/xxx
```

**支持格式**:
| 格式 | 说明 |
|------|------|
| PNG | 位图格式 |
| SVG | 矢量格式 |
| Figma Link | Figma 在线链接 |

#### 2.2.3 设计稿版本管理

**需求编号**: FR-DESIGN-003

**描述**: 自动记录设计稿版本历史

**版本记录**:
```yaml
design_versions:
  - version: 1.0
    file: header_v1.png
    upload_date: 2026-02-01
    uploader: agent_designer
    changes: "初稿"
  
  - version: 2.0
    file: header_v2.png
    upload_date: 2026-02-02
    uploader: agent_designer
    changes: "修改颜色和间距"
    diff_from: 1.0
```

**命令**:
```bash
# 查看版本历史
oc-collab design versions --component navbar

# 回滚到指定版本
oc-collab design rollback --component navbar --version 1.0
```

#### 2.2.4 设计稿对比

**需求编号**: FR-DESIGN-004

**描述**: 对比两个设计稿版本的差异

**对比方式**:
| 方式 | 说明 |
|------|------|
| 像素对比 | 逐像素对比，标记差异位置 |
| 并排对比 | 左右并排显示 |
| 叠加对比 | 透明度滑块叠加显示 |

**命令**:
```bash
# 对比版本
oc-collab design diff --version 1.0 --version 2.0

# 输出差异报告
oc-collab design diff --version 1.0 --version 2.0 --output report.md

# 差异类型
# - 新增元素 (绿色标记)
# - 删除元素 (红色标记)
# - 修改元素 (黄色标记)
```

#### 2.2.5 设计标注管理

**需求编号**: FR-DESIGN-005

**描述**: 管理设计标注和交互说明

**标注格式**:
```markdown
# 导航栏设计标注

## 组件信息
- 名称: 主导航栏
- 位置: 页面顶部
- 尺寸: 1200px × 60px

## 交互说明
- 悬停效果: 背景色变深 10%
- 点击效果: 下划线显示
- 响应式: 768px 以下隐藏

## 状态
- 默认状态: 显示全部菜单
- 移动端: 折叠为汉堡菜单
```

**命令**:
```bash
# 添加标注
oc-collab design annotate --file navbar.png --annotations nav_annotations.md

# 查看标注
oc-collab design annotations --component navbar
```

---

### 2.3 多技术栈协同

#### 2.3.1 技术栈选择流程

**需求编号**: FR-TECH-001

**描述**: 详细设计阶段确定技术栈

**流程**:
```
详细设计阶段:
  │
  ├─ Agent 2 (开发负责人) 提出技术栈建议
  │   ├─ 前端技术: React / Vue / Angular
  │   ├─ 后端技术: Node.js / Go / Java / Python
  │   ├─ 数据库: PostgreSQL / MySQL / MongoDB
  │   └─ 部署方案: Docker / K8s / 云函数
  │
  └─ Agent 1 确认技术栈选择
```

**技术栈模板**:
```yaml
tech_stack:
  frontend:
    - react
    - vue
    - angular
  
  backend:
    - nodejs
    - go
    - java
    - python
  
  database:
    - postgresql
    - mysql
    - mongodb
```

#### 2.3.2 技术栈 Agent 分配

**需求编号**: FR-TECH-002

**描述**: 根据技术栈分配专属 Agent

**分配规则**:
| 技术栈 | Agent 类型 | 说明 |
|--------|------------|------|
| React | Agent (前端-React) | 专注 React 技术栈 |
| Vue | Agent (前端-Vue) | 专注 Vue 技术栈 |
| Angular | Agent (前端-Angular) | 专注 Angular 技术栈 |
| Node.js | Agent (后端-Node) | 专注 Node.js 技术栈 |
| Go | Agent (后端-Go) | 专注 Go 技术栈 |
| Java | Agent (后端-Java) | 专注 Java 技术栈 |

**命令**:
```bash
# 添加技术栈 Agent
oc-collab agent add --role frontend --tech react --count 1
oc-collab agent add --role backend --tech go --count 1
```

**原则**: 每个技术栈由专门的 Agent 负责，确保专业性和问题暴露。

#### 2.3.3 多仓库协作

**需求编号**: FR-TECH-003

**描述**: 支持前端/后端独立仓库协作

**协作模式**:
| 模式 | 说明 |
|------|------|
| 分离仓库 | 前端 repo + 后端 repo |
| Monorepo | 同一仓库不同目录 |
| 微服务 | 每个服务对应一个 Agent |

**配置**:
```yaml
repositories:
  frontend:
    url: https://github.com/project/frontend
    agent: agent_frontend_react
  
  backend:
    url: https://github.com/project/backend
    agent: agent_backend_go
```

**命令**:
```bash
# 查看仓库状态
oc-collab repo status

# 同步所有仓库
oc-collab repo sync --all
```

#### 2.3.4 接口规范管理

**需求编号**: FR-TECH-004

**描述**: 管理 API 接口文档和 Mock 数据

**接口文档**:
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0

paths:
  /users:
    get:
      summary: 获取用户列表
      responses:
        200:
          description: 成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

**命令**:
```bash
# 生成接口文档
oc-collab api generate --spec openapi.yaml

# 生成 Mock 数据
oc-collab api mock --spec openapi.yaml --output mocks/

# 接口一致性测试
oc-collab api test --spec openapi.yaml --实际实现
```

---

### 2.4 多 Agent 项目管理

#### 2.4.1 任务分配机制

**需求编号**: FR-PROJECT-001

**描述**: 按 Agent 类型分配任务，采用两层粒度（Feature + Task）

**层级设计**:
```
┌─────────────────────────────────────────┐
│ L1: Feature (功能模块)                   │
│   ├─ 定义: 大型功能单元                  │
│   ├─ 示例: "用户登录模块", "支付系统"    │
│   ├─ 创建者: Agent 1 (产品经理)          │
│   └─ 粒度: 1-2 周开发周期               │
│                                          │
│   L2: Task (技术任务) ← 隶属于 Feature   │
│   ├─ 定义: 开发单元                      │
│   ├─ 示例: "实现 JWT 认证"               │
│   ├─ 创建者: Agent 1 (产品经理)          │
│   └─ 执行者: 指定 Agent                  │
└─────────────────────────────────────────┘
```

**任务模板**:
```yaml
features:
  - id: FEATURE-001
    title: "用户认证模块"
    description: "用户登录、注册、登出功能"
    agent: agent_backend_go  # 默认负责 Agent
    status: pending
    tasks:
      - id: TASK-001
        title: "设计用户认证 API"
        assignee: agent_backend_go
        status: completed
        dependencies: []
      
      - id: TASK-002
        title: "实现 JWT 认证"
        assignee: agent_backend_go
        status: in_progress
        dependencies: [TASK-001]
      
      - id: TASK-003
        title: "实现登录页面 React 组件"
        assignee: agent_frontend_react
        status: pending
        dependencies: [TASK-001]
```

**命令**:
```bash
# 分配 Feature（功能模块）
oc-collab project assign --feature "用户认证模块" --agent backend

# 分配 Task（必须指定 Feature）
oc-collab project assign --task "实现JWT" --feature "用户认证模块" --agent backend

# 查看所有任务
oc-collab project tasks

# 查看我的任务
oc-collab project my-tasks

# 查看 Feature 下的任务
oc-collab project tasks --feature "用户认证模块"
```

#### 2.4.2 依赖关系管理

**需求编号**: FR-PROJECT-002

**描述**: 管理任务间的依赖关系，包括循环依赖检测

**依赖规则**:
| 依赖类型 | 说明 | 处理方式 |
|----------|------|----------|
| 前置依赖 | 任务 B 需要任务 A 完成 | B 阻塞，直到 A 完成 |
| 并行依赖 | 任务 A 和 B 可并行 | 无阻塞 |
| 参考依赖 | 任务 B 参考任务 A | 无阻塞，建议参考 |

**循环依赖检测**:
```yaml
circular_dependency_detection:
  trigger: "PR/MR 提交时"
  action: "阻止合并，通知 Agent 1"
  processing_flow:
    - "CI 阶段检测依赖图"
    - "发现循环 → 阻止合并"
    - "在 PR 中标记冲突任务"
    - "通知 Agent 1 (项目经理)"
    - "Agent 1 重新设计依赖关系"
  
  解环方案:
    - "合并依赖: A 和 B 合并为一个任务"
    - "抽取公共依赖: A 和 B 都依赖 C"
    - "调整任务边界: 重新划分任务职责"
```

**命令**:
```bash
# 设置依赖
oc-collab project dependency --task TASK-003 --depends-on TASK-001,TASK-002

# 查看依赖关系
oc-collab project dependencies --task TASK-003

# 查看循环依赖
oc-collab project dependencies --check-circular

# 可视化依赖图
oc-collab project dependencies --graph --output dependency_graph.png
```

#### 2.4.3 进度可视化

**需求编号**: FR-PROJECT-003

**描述**: 各 Agent 任务进度可视化

**进度看板**:
```bash
$ oc-collab project progress

项目进度看板
============

Agent 1 (产品经理) [████████████] 100%
  [✓] TASK-001 用户模块需求分析

Agent 2 (开发负责人) [████████░░░] 80%
  [✓] TASK-002 后端 API 设计与开发
  [>] TASK-005 用户认证模块 [进行中]

Agent (前端-React) [████░░░░░░░░] 40%
  [✓] TASK-003 基础框架搭建
  [>] TASK-004 首页开发 [进行中]
  [待] TASK-006 用户页面开发

Agent (设计师) [██████████░░░░] 60%
  [✓] TASK-007 首页设计
  [✓] TASK-008 用户页面设计
  [>] TASK-009 响应式设计 [进行中]

总体进度: 65%
```

**命令**:
```bash
# 查看进度看板
oc-collab project progress

# 查看单个 Agent 进度
oc-collab project progress --agent agent_frontend_react
```

#### 2.4.4 协调通知

**需求编号**: FR-PROJECT-004

**描述**: 任务状态变更时通知相关 Agent，采用双层通知机制

**双层通知机制**:
| 层级 | 方式 | 用途 | 触发事件 |
|------|------|------|----------|
| **Git层** | Comment/Commit消息 | 正式协作记录，可追溯 | 所有事件 |
| **Webhook层** | 可配置 (Slack/邮件/飞书) | 即时通知重要事件 | 仅重要事件 |

**重要事件（Webhook通知）**:
| 事件 | 通知对象 | 说明 |
|------|----------|------|
| 锁超时释放 | Agent 1 | "资源锁已超时释放" |
| 循环依赖检测 | Agent 1、涉及 Agent | "发现循环依赖" |
| 任务阻塞 | 任务负责人 | "有依赖任务未完成" |
| 任务完成 | 依赖该任务的所有 Agent | "前置任务已完成" |
| 任务分配 | 被分配 Agent | "新任务已分配" |
| PR评审请求 | 评审者 | "请评审 PR" |
| 设计稿更新 | 相关开发者 | "设计稿已更新" |
| API 更新 | 相关前端 Agent | "API 接口已更新" |

**通知配置**:
```yaml
notification_config:
  git:
    enabled: true
    events: [all]  # 所有事件
    
  webhook:
    enabled: true
    endpoint: "https://hooks.slack.com/services/xxx"
    events: [lock_timeout, circular_dependency, task_blocked, pr_review_request]
    
  channels:
    - type: slack
      enabled: true
      events: [lock_timeout, circular_dependency, task_blocked]
    - type: email
      enabled: false
      events: [task_completed]
```

**命令**:
```bash
# 查看通知
oc-collab notifications list

# 设置 Git 层通知
oc-collab notifications config --git --level detailed

# 设置 Webhook 通知
oc-collab notifications config --webhook --endpoint https://hooks.slack.com/xxx

# 设置通知偏好
oc-collab notifications settings --email true --webhook true --slack false

# 测试通知
oc-collab notifications test --type webhook
```

#### 2.4.5 资源锁机制

**需求编号**: FR-PROJECT-005

**描述**: 防止多个 Agent 并发修改同一文件，包含超时自动处理

**锁类型**:
| 锁类型 | 说明 | 默认超时 | 可配置 |
|--------|------|----------|--------|
| 文件锁 | 锁定单个文件 | 30 分钟 | 是 |
| 目录锁 | 锁定整个目录 | 2 小时 | 是 |
| 任务锁 | 锁定整个任务 | 按任务周期 | 是 |

**超时处理流程**:
```yaml
lock_timeout_handling:
  warning_before_timeout: "5 minutes"  # 提前警告
  
  timeout_actions:
    - "自动释放锁"
    - "通知 Agent 1 (项目经理)"
    - "任务状态改为 BLOCKED"
    - "记录超时日志"
  
  agent1_decision_options:
    - "重新分配: 分配给其他 Agent"
    - "等待原Agent: 通知原 Agent 继续工作"
    - "取消任务: 标记为已取消"
```

**超时处理流程图**:
```
锁持有者工作
    │
    ├── 剩余 5 分钟 ──→ 发送警告 (Git Comment @持有者)
    │
    ├── 超时 (30分钟)
    │   ├── 自动释放锁
    │   ├── 通知 Agent 1
    │   │   ├── 锁信息: {文件, 原持有者, 超时时间}
    │   │   └── 建议操作: [重新分配] / [等待原Agent]
    │   ├── 任务状态改为 "BLOCKED"
    │   └── 记录超时日志
    │
    └── Agent 1 决策
        ├── 重新分配 → 分配给其他 Agent
        └── 等待原Agent → 通知原 Agent 继续工作
```

**命令**:
```bash
# 锁定文件
oc-collab lock acquire --file src/components/Header.tsx

# 锁定文件（自定义超时）
oc-collab lock acquire --file src/components/Header.tsx --timeout 60

# 查看锁定状态
oc-collab lock status --file src/components/Header.tsx

# 查看所有锁
oc-collab lock list

# 释放锁
oc-collab lock release --file src/components/Header.tsx

# 强制解锁 (Agent 1)
oc-collab lock force-release --file src/components/Header.tsx --reason "超时释放"

# 检查锁超时
oc-collab lock check-timeout
```

---

### 2.5 执行约束管理

**背景**: 基于金融案件PDF生成系统案例研究（附录B），发现独立执行时存在4类反复发生的问题：
- API Key配置错误反复发生（EXE-001）
- Mock/Real模式混淆（EXE-002）
- 中间结果复用导致测试失效（EXE-003）
- PDF问题重复发生（EXE-004）

**设计原则**:
- 约束机制强制执行，非可选
- 问题修复后自动添加回归测试
- 配置/模式/测试必须明确声明

#### 2.5.1 配置验证器

**需求编号**: FR-CONFIG-001

**描述**: 启动时验证配置完整性，防止配置错误直到运行时才暴露

**验证项**:
| 验证项 | 错误类型 | 处理方式 |
|--------|----------|----------|
| API Key缺失 | MISSING_API_KEY | 阻止运行，提示配置 |
| 模型不存在 | MODEL_NOT_FOUND | 阻止运行，建议模型名 |
| 模式未声明 | AMBIGUOUS_MODE | 阻止运行，要求--mode |

**命令**:
```bash
# 验证配置完整性
oc-collab config validate

# 生成配置模板
oc-collab config template

# 完整配置检查
oc-collab config check --full

# 输出示例
# ✓ API Key验证通过
# ✗ 错误: 缺少OPENAI_API_KEY
# 建议: 请参考 config/template.yaml 配置
```

#### 2.5.2 模式管理器

**需求编号**: FR-MODE-001

**描述**: 强制声明运行模式，防止Mock/Real混淆

**模式类型**:
| 模式 | 说明 | 用途 |
|------|------|------|
| real | 实际调用LLM | 正式生成 |
| mock | 使用Mock数据 | 单元测试 |
| dry-run | 仅验证配置 | 配置检查 |

**约束规则**:
- 运行前必须声明 `--mode`
- 模式切换记录到审计日志
- Mock模式下强制警告

**命令**:
```bash
# 实际运行
oc-collab run --mode real

# Mock模式
oc-collab run --mode mock

# 仅验证配置
oc-collab run --mode dry-run

# 查看当前模式
oc-collab mode status

# 查看模式切换历史
oc-collab mode history
```

#### 2.5.3 测试隔离器

**需求编号**: FR-TEST-001

**描述**: 防止中间结果复用，确保测试结果可复现

**约束规则**:
- 测试必须使用独立输出目录
- 缓存必须明确声明
- 每次测试可强制 `--fresh` 重新生成

**命令**:
```bash
# 强制重新生成（不使用缓存）
oc-collab test --fresh

# 隔离测试（独立输出目录）
oc-collab test --isolated

# 清理过期输出（超过24小时）
oc-collab test cleanup --older-than 24h

# 输出示例
# ✓ 已清除 5 个过期输出目录
# ✓ 创建隔离输出目录: outputs/test_20260201_120000/
```

#### 2.5.4 问题追踪器

**需求编号**: FR-ISSUE-001

**描述**: 记录问题并自动生成回归测试，防止问题复发

**功能**:
| 功能 | 说明 |
|------|------|
| 问题记录 | 记录问题类型、描述、严重性 |
| 回归测试 | 修复后自动生成回归测试用例 |
| 问题复发检测 | 发现已知问题复发时阻止PR |

**约束规则**:
- 问题修复必须关联Issue ID
- 修复后自动添加回归测试
- 同一问题复发 → PR阻止

**命令**:
```bash
# 记录问题
oc-collab issue create --type BUG --description "LLM响应前缀残留"

# 列出已知问题
oc-collab issue list

# 运行回归测试
oc-collab issue regression

# 检查是否有问题复发
oc-collab issue check

# 关闭问题
oc-collab issue close --id ISSUE-20260201001
```

#### 2.5.5 PDF质量验证器

**需求编号**: FR-PDF-001

**描述**: 验证PDF输出质量，防止同样的PDF问题反复发生

**验证项**:
| 验证项 | 问题类型 | 严重性 |
|--------|----------|--------|
| LLM响应前缀残留 | PREFIX_RESIDUE | HIGH |
| Markdown表格残留 | MARKDOWN_TABLE | HIGH |
| 脱敏标记残留 | ANONYMIZATION | HIGH |
| 分页错误 | PAGINATION | MEDIUM |

**约束规则**:
- PDF生成后必须通过质量验证
- 质量问题 → 阻止进入下一阶段
- 历史问题复发 → PR阻止

**命令**:
```bash
# 验证PDF质量
oc-collab pdf validate outputs/case_001.pdf

# 生成质量报告
oc-collab pdf report outputs/case_001.pdf --output quality_report.md

# 检查历史问题复发
oc-collab pdf check-regression outputs/case_001.pdf

# 输出示例
# ✓ LLM响应前缀检查: 通过
# ✗ Markdown表格残留: 发现3处
# 检查结果: ❌ 失败
```

---

### 2.6 覆盖率检查机制（v2.1.0 M5教训）

**背景**: v2.1.0 M5发现核心模块（daemon.py, supervisor.py）覆盖率仅16%，但M1-M4都签署了"测试通过"。根本原因是验收标准写了"覆盖率>=80%"但没人真的运行coverage命令检查。

**设计原则**:
- 覆盖率检查是签署的前置条件
- 核心模块必须100%覆盖
- 覆盖率报告必须生成并分析

#### 2.6.1 覆盖率检查器

**需求编号**: FR-COVERAGE-001

**描述**: 运行覆盖率检查并生成报告，确保核心模块100%覆盖

**核心模块清单**（必须100%覆盖）:
| 模块 | 文件路径 | 说明 |
|------|----------|------|
| 守护进程 | src/core/daemon.py | Agent生命周期管理 |
| 进程监管 | src/core/supervisor.py | Agent进程监控 |
| 签署引擎 | src/core/signoff.py | 签署流程管理 |
| 状态管理 | src/core/state_manager.py | 状态持久化 |
| 异常处理 | src/core/exception_handler.py | 异常处理 |

**检查流程**:
```bash
# 1. 运行覆盖率检查
oc-collab coverage run

# 2. 检查核心模块覆盖率
oc-collab coverage check --module daemon.py --module supervisor.py --module signoff.py

# 3. 生成覆盖率报告
oc-collab coverage report --format markdown --output coverage_report.md

# 4. 检查覆盖率趋势（与上次对比）
oc-collab coverage trend

# 5. 输出示例
# === 覆盖率检查结果 ===
# ✓ daemon.py: 100% (142/142 行)
# ✓ supervisor.py: 100% (98/98 行)
# ✓ signoff.py: 100% (156/156 行)
# ✗ exception_handler.py: 67% (234/350 行)
# TOTAL: 89%
#
# 核心模块覆盖率: 3/5 = 60%
# 检查结果: ❌ 失败
#
# 问题: exception_handler.py 覆盖率不足
# 建议: 补充单元测试覆盖未测试的代码行
```

#### 2.6.2 覆盖率门禁

**需求编号**: FR-COVERAGE-002

**描述**: 覆盖率不达标时阻止签署或PR合并

**门禁规则**:
| 条件 | 动作 | 说明 |
|------|------|------|
| 核心模块<100% | 阻断签署 | 不能进入下一里程碑 |
| 整体覆盖率<80% | 阻断签署 | 不能进入下一里程碑 |
| 覆盖率下降>5% | 警告+说明 | 需要解释为什么下降 |
| 覆盖率报告未生成 | 阻断签署 | 必须生成报告 |

**约束配置**:
```yaml
coverage_gates:
  core_modules:
    - daemon.py
    - supervisor.py
    - signoff.py
    - state_manager.py
    - exception_handler.py
  
  thresholds:
    core_coverage: 100%    # 核心模块必须100%
    overall_coverage: 80%  # 整体至少80%
    max_decline: 5%        # 下降不能超过5%
  
  actions:
    core_below_100: "BLOCK_SIGNOFF"
    overall_below_80: "BLOCK_SIGNOFF"
    decline_exceeded: "WARN_AND_REQUIRE_EXPLANATION"
    report_missing: "BLOCK_SIGNOFF"
```

#### 2.6.3 覆盖率趋势监控

**需求编号**: FR-COVERAGE-003

**描述**: 跟踪覆盖率变化趋势，发现退化

**趋势检查**:
```bash
# 查看覆盖率趋势
oc-collab coverage trend

# 输出示例
# === 覆盖率趋势 ===
# 版本    日期        daemon   supervisor   signoff   TOTAL
# v2.0.0  2026-01-15  100%     100%         100%      95%
# v2.1.0  2026-01-20  44%      35%          75%       16%
# v2.2.0  2026-02-01  100%     100%         100%      100%
#
# 警告: v2.1.0覆盖率严重下降 (95% → 16%)
# 原因: 新增模块未补充测试
```

**趋势规则**:
- 覆盖率下降 > 5%: 触发警告，需要在PR中说明原因
- 覆盖率下降 > 10%: 触发审查，需要Agent 1确认
- 核心模块覆盖率下降: 阻断合并，必须修复

#### 2.6.4 CI集成

**需求编号**: FR-COVERAGE-004

**描述**: 在CI流程中自动运行覆盖率检查

**CI配置**:
```yaml
# .github/workflows/test.yml
jobs:
  coverage:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Tests with Coverage
      run: |
        pytest tests/ --cov=src --cov-report=term-missing
    
    - name: Check Core Module Coverage
      run: |
        # 检查核心模块100%覆盖
        coverage report --include="src/core/daemon.py" | grep -q "100%"
        coverage report --include="src/core/supervisor.py" | grep -q "100%"
        coverage report --include="src/core/signoff.py" | grep -q "100%"
    
    - name: Upload Coverage Report
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
    
    - name: Check Coverage Regression
      run: |
        # 与上次覆盖率对比
        python scripts/check_coverage_regression.py
```

---

### 2.7 用户故事管理

**需求编号**: FR-STORY-001

**描述**: 管理用户故事的全生命周期，包括创建、跟踪、E2E测试覆盖、验收验证

#### 2.7.1 用户故事模板

```markdown
## Story S-XXX: [用户场景标题]

### 用户目标
**作为** [用户角色]  
**我希望** [完成什么目标]  
**以便** [获得什么价值]

### 前置条件
- [条件 1]
- [条件 2]

### 交互流程
| 步骤 | 用户操作 | 系统响应 |
|------|----------|----------|
| 1    | [操作]   | [响应]   |
| 2    | [操作]   | [响应]   |
| 3    | [操作]   | [响应]   |

### 预期结果
**成功场景**:
- [结果 1]
- [结果 2]

**失败场景**:
- [条件]: [处理方式]

### E2E 测试覆盖
| 测试用例 | 说明 |
|----------|------|
| test_story_SXXX_[场景] | [说明] |
| test_story_SXXX_[边界] | [说明] |

### 验收标准
- [ ] 标准 1
- [ ] 标准 2
```

#### 2.7.2 用户故事特点

| 特点 | 说明 |
|------|------|
| **独立性** | Story 独立描述，不关联 Feature |
| **用户视角** | 描述用户与系统的交互 |
| **可测试** | 每个 Story 至少有一个 E2E 测试用例 |
| **可追溯** | Story 关联到具体的E2E测试用例和验收结果 |

#### 2.7.3 用户故事管理命令

```bash
# 创建用户故事
oc-collab story create --title "用户登录" --role "终端用户"

# 列出oc-collab story list

# 查看所有用户故事
用户故事详情
oc-collab story show --id S-001

# 关联E2E测试用例
oc-collab story link-test --id S-001 --test test_login.py

# 标记验收通过
oc-collab story accept --id S-001 --evidence test_report.md
```

#### 2.7.4 Story 与 Feature 的关系

Story 和 Feature 是**正交关系**（独立维度，无层级隶属）。

| 维度 | 视角 | 示例 |
|------|------|------|
| **Feature** | 技术视角——"系统由哪些模块组成" | Agent动态管理、覆盖率检查 |
| **Story** | 用户视角——"用户如何使用系统" | Agent 1如何使用覆盖率检查签署 |

#### 2.7.5 E2E 测试组织

```bash
tests/
└── test_stories/
    ├── __init__.py
    ├── conftest.py               # Story 相关的 fixtures
    ├── test_story_S001.py        # Story S-001
    ├── test_story_S002.py        # Story S-002
    └── ...
```

#### 2.7.6 oc-collab 用户故事列表

> oc-collab 的用户故事见 [第9章 用户故事](#9-用户故事-user-stories)

---

### 2.8 黑盒测试管理

**背景**: v2.1.0 M5 签署时发现黑盒测试未完整执行，仅部分用例通过代码审查。v2.2.0 将黑盒测试纳入正式验收标准，确保签署前所有 P0/P1 测试用例实际执行通过。

**v2.1.0 教训**:
- 黑盒测试用例已编写，但未实际执行
- M5 仅依赖单元测试覆盖率，未验证 CLI 功能
- 导致部分 CLI 命令（如 `oc-collab advance -p`）未经验证

#### 2.8.1 黑盒测试用例管理

**需求编号**: FR-BLACKBOX-001

**描述**: 管理黑盒测试用例的全生命周期，包括创建、执行、结果记录

**测试用例模板**:
```markdown
## TC-XXX: [用例名称]

| 属性 | 值 |
|-----|------|
| 用例编号 | TC-XXX |
| 用例名称 | [名称] |
| 优先级 | P0/P1/P2 |
| 前置条件 | [条件] |
| 测试步骤 | 1. [步骤1]<br>2. [步骤2] |
| 预期结果 | 1. [结果1]<br>2. [结果2] |
| 执行状态 | 待执行/通过/失败 |
```

**用例文件位置**:
```
docs/03-test/
├── blackbox_test_cases.md      # 测试用例定义
├── blackbox_test_results.md    # 测试结果记录
└── test_cases_v{version}.md    # 版本专用测试用例
```

#### 2.8.2 黑盒测试执行机制

**需求编号**: FR-BLACKBOX-002

**描述**: 里程碑签署前必须执行黑盒测试并通过

**测试执行要求**:
| 里程碑 | P0 用例 | P1 用例 | P2 用例 | 通过标准 |
|--------|---------|---------|---------|----------|
| M1 | 100% | 100% | - | 所有 P0/P1 通过 |
| M2 | 100% | 100% | - | 所有 P0/P1 通过 |
| M3 | 100% | 100% | - | 所有 P0/P1 通过 |
| M4 | 100% | 100% | 90% | P0/P1 100%，P2 ≥90% |
| M5 | 100% | 100% | 100% | 所有用例通过 |

**黑盒测试命令**:
```bash
# 执行所有黑盒测试
oc-collab test blackbox

# 执行特定用例
oc-collab test blackbox --tc TC-001

# 生成测试报告
oc-collab test blackbox --report

# 查看测试结果
oc-collab test blackbox --results
```

#### 2.8.3 黑盒测试结果记录

**需求编号**: FR-BLACKBOX-003

**描述**: 自动记录黑盒测试执行结果

**结果记录模板**:
```markdown
### TC-XXX: [用例名称]
- **用例编号**: TC-XXX
- **优先级**: P0
- **测试步骤**: [步骤]
- **测试结果**: 通过/失败
- **测试说明**: [说明]
- **执行日期**: YYYY-MM-DD
- **执行人**: Agent X
- **状态**: ✓ 通过 / ✗ 失败
```

**结果文件**:
- `docs/03-test/blackbox_test_results.md` - 记录所有测试结果
- 每次执行更新文件，保留历史记录

#### 2.8.4 签署前黑盒测试验证

**需求编号**: FR-BLACKBOX-004

**描述**: 里程碑签署前自动检查黑盒测试通过状态

**签署条件**:
```yaml
signoff_prerequisites:
  blackbox_tests:
    required: true
    passes:
      - "所有 P0 用例通过"
      - "所有 P1 用例通过"
      - "P2 用例通过率 >= 90%"
    evidence: "blackbox_test_results.md 已更新"
```

**自动检查**:
```bash
# 签署前检查
oc-collab signoff --check-blackbox

# 输出示例
# === 黑盒测试检查 ===
# P0 用例: 5/5 通过 ✅
# P1 用例: 6/6 通过 ✅
# P2 用例: 4/4 通过 ✅
# 检查结果: ✅ 通过
# 可以签署 M5
```

#### 2.8.5 黑盒测试模板库

**需求编号**: FR-BLACKBOX-005

**描述**: 提供可复用的黑盒测试模板

**标准测试模板**:
| 模板名称 | 适用场景 | 优先级 |
|----------|----------|--------|
| 项目初始化 | `oc-collab init` | P0 |
| 状态查看 | `oc-collab status` | P0 |
| Agent 切换 | `oc-collab switch` | P0 |
| 阶段推进 | `oc-collab advance` | P0 |
| 签署确认 | `oc-collab signoff` | P0 |
| Git 同步 | `oc-collab sync` | P1 |
| 状态验证 | YAML 格式验证 | P1 |
| 帮助信息 | `--help` | P2 |

**模板使用**:
```bash
# 从模板创建测试用例
oc-collab test template --from init --output test_my_feature.md

# 执行模板测试
oc-collab test template --name "项目初始化"
```

#### 2.8.6 黑盒测试验收标准

**v2.2.0 黑盒测试验收标准**:
| 标准 | 要求 | 验证方式 |
|------|------|----------|
| P0 用例 | 100% 通过 | `oc-collab test blackbox --priority P0` |
| P1 用例 | 100% 通过 | `oc-collab test blackbox --priority P1` |
| P2 用例 | ≥90% 通过 | `oc-collab test blackbox --priority P2` |
| 测试报告 | 已生成 | `oc-collab test blackbox --report` |
| 结果记录 | 已更新 | `docs/03-test/blackbox_test_results.md` |

**验收检查命令**:
```bash
# 执行完整黑盒测试
oc-collab test blackbox --full --report

# 检查签署准备状态
oc-collab signoff --check-all

# 输出示例
# === 签署准备检查 ===
# ✓ 单元测试: 245/245 通过
# ✓ E2E 测试: 27/27 通过
# ✓ 黑盒测试: 15/15 通过
# ✓ 覆盖率: 88% >= 80%
# 检查结果: ✅ 所有检查通过，可以签署 M5
```

#### 2.8.7 黑盒测试与 E2E 测试关系

黑盒测试和 E2E 测试是**正交关系**（独立维度）：

| 维度 | 视角 | 测试对象 | 示例 |
|------|------|----------|------|
| **黑盒测试** | CLI 命令视角 | 外部接口 | `oc-collab init`, `oc-collab status` |
| **E2E 测试** | 端到端视角 | 完整流程 | 完整用户故事流程 |

**测试覆盖**:
- 黑盒测试: 覆盖所有 CLI 命令
- E2E 测试: 覆盖用户故事完整流程
- 两者互补，确保功能完整

---

### 2.9 会议管理

#### 2.8.1 会议类型

| 类型 | 说明 |
|------|------|
| Agent 间讨论 | Agent 1 ↔ Agent 2 ↔ 其他 Agent 的讨论 |
| 产品经理与客户讨论 | 需要导入外部会议信息 |

#### 2.8.2 外部会议导入

| 导入内容 | 说明 |
|----------|------|
| 录音文件 | .mp3, .wav 等格式 |
| 录音转写文字 | 语音转文字结果 |
| 会议纪要 | 人工整理的纪要 |

#### 2.8.3 会议结构

```yaml
meeting:
  id: MTG-001                    # 会议编号
  title: "v2.2.0 需求讨论"       # 会议主题
  participants:                  # 参与者
    - Agent 1
    - Agent 2
  version: "v2.2.0"              # 关联版本
  date: "2026-02-01"             # 会议日期
  decisions:                     # 关键决策
    - "资源锁超时采用分层通知机制"
    - "Story 与 Feature 为正交关系"
  action_items:                  # 待办事项
    - "创建概要设计文档"
  attachments:                   # 附件
    - "recording.mp3"
    - "transcript.txt"
```

#### 2.8.4 会议纪要生成

| 场景 | 生成方式 |
|------|----------|
| Agent 间讨论 | Agent 自动生成纪要 |
| 上传录音/转写 | Agent 自动生成纪要 |

#### 2.8.5 版本关联

- 每个会议只关联特定版本 (v2.1.0, v2.2.0)
- 防止不同版本的内容互相污染
- 可以追溯某版本的所有相关会议

#### 2.8.6 会议命令

```bash
# 创建会议
oc-collab meeting create --title "v2.2.0 需求讨论" --version v2.2.0

# 上传会议录音
oc-collab meeting upload --meeting MTG-001 --file recording.mp3

# 查看会议列表
oc-collab meeting list --version v2.2.0

# 查看会议详情
oc-collab meeting show --meeting MTG-001

# 生成会议纪要
oc-collab meeting summary --meeting MTG-001
```

---

### 2.9 持续反馈闭环机制

**需求编号**: FR-FEEDBACK-001

**描述**: 建立持续反馈收集和处理机制，确保问题自动纳入下一版本draft

#### 2.9.1 反馈收集范围

| 阶段 | 反馈类型 | 处理方式 |
|------|----------|----------|
| **版本开发过程中** | bug报告、支持请求、问题调查、细碎讨论 | 纳入下一版本 draft |
| **版本部署上线后** | bug报告、支持请求、问题调查、细碎讨论 | 纳入下一版本 draft |
| **确认为当前版本bug** | - | 当前版本补丁解决 |

#### 2.9.2 处理流程

```
发现问题
    │
    ├── 确认为当前版本bug ──→ 当前版本补丁修复 (Hotfix)
    │
    └── 其他问题 ──→ 自动纳入下一版本 draft
```

#### 2.9.3 反馈分类规则

| 分类 | 判断标准 | 处理方式 |
|------|----------|----------|
| 当前版本bug | 问题由当前版本引入，且影响核心功能 | 当前版本 Hotfix |
| 历史遗留问题 | 已知存在，但在新版本发现 | 纳入下一版本 draft |
| 新需求建议 | 用户提出的新功能想法 | 纳入下一版本 draft |
| 体验改进 | 优化建议，非bug | 纳入下一版本 draft |
| 配置问题 | 用户配置错误导致 | 文档补充，不纳入 |

#### 2.9.4 自动纳入机制

```yaml
feedback_auto_routing:
  trigger:
    - "bug_report"
    - "support_request"
    - "problem_investigation"
    - "discussion"
  
  routing_rules:
    - if: "is_current_version_bug"
      then: "current_version_hotfix"
    - else: "next_version_draft"
```

#### 2.9.5 版本追溯

| 追溯维度 | 说明 |
|----------|------|
| 问题来源 | 从哪个版本收集 |
| 解决版本 | 在哪个版本解决 |
| 处理历史 | 状态变更记录 |
| 关联讨论 | 相关的会议/讨论 |

#### 2.9.6 反馈收集点

| 收集点 | 说明 |
|--------|------|
| GitHub Issues | Bug 报告、功能请求 |
| 支持工单 | 用户支持请求 |
| 会议讨论 | 需求讨论中的问题 |
| 代码评审 | 评审中发现的遗漏 |
| 部署监控 | 生产环境问题 |

---

## 2.10 智能记忆与提醒机制（解决Agent遗忘问题）

**背景**: Agent 在 Compaction 后容易遗忘历史经验和 oc-collab 约束要求，导致同样的问题反复发生。需要建立智能记忆机制，确保：
1. 记住历史教训（问题模式、解决方案）
2. 在合适时机提醒（不是事后，而是事前）
3. Compaction 不丢失关键记忆

### 2.10.1 问题模式识别与记忆

**需求编号**: FR-MEMORY-001

**描述**: 记录问题类型、原因、解决方案，当相同模式再次出现时自动提醒

**问题模式库**:
```yaml
problem_patterns:
  - id: PATTERN-001
    category: CONFIGURATION
    pattern: "API Key.*missing|MISSING_API_KEY"
    description: "API Key 配置缺失"
    solutions:
      - "使用环境变量: export OPENAI_API_KEY=xxx"
      - "参考 config/template.yaml 配置"
    occurrences: 5
    last_occurrence: "2026-02-01"
    
  - id: PATTERN-002
    category: MODE_CONFUSION
    pattern: "mock|real.*混淆|mode.*ambiguous"
    description: "Mock/Real 模式混淆"
    solutions:
      - "运行前必须声明 --mode real 或 --mode mock"
      - "使用 mode_manager.py 验证模式"
    occurrences: 3
    last_occurrence: "2026-01-28"
    
  - id: PATTERN-003
    category: TEST_ISOLATION
    pattern: "中间结果.*复用|cache.*未清理|test.*隔离"
    description: "中间结果复用导致测试失效"
    solutions:
      - "每次测试使用 --fresh 参数"
      - "测试前运行 oc-collab test cleanup"
    occurrences: 4
    last_occurrence: "2026-01-30"
```

**触发机制**:
| 触发时机 | 行为 |
|----------|------|
| Agent 启动时 | 加载问题模式库，检查是否有相关历史 |
| 执行操作前 | 检测是否匹配已知问题模式 |
| 发现新问题时 | 自动添加到问题模式库 |

**命令**:
```bash
# 查看已知问题模式
oc-collab memory patterns

# 查看特定模式详情
oc-collab memory pattern --id PATTERN-001

# 添加新问题模式
oc-collab memory pattern add --category CONFIGURATION --pattern "API Key.*error" --solution "xxx"

# 检查当前操作是否匹配已知问题
oc-collab memory check --operation "配置API Key"
# 输出: ⚠️ 发现已知问题模式 PATTERN-001
#       解决方案: 使用环境变量配置
```

### 2.10.2 决策追溯

**需求编号**: FR-MEMORY-002

**描述**: 记录关键决策及其理由，支持回溯查看"当时为什么这么做"

**决策记录模板**:
```yaml
decisions:
  - id: DEC-001
    date: "2026-01-15"
    topic: "Mock/Real 模式强制声明"
    decision: "运行前必须声明 --mode 参数"
    reason: |
      1. Financial 项目多次发生 Mock/Real 混淆
      2. 隐蔽性强，问题直到运行时才暴露
      3. 模式声明成本低，收益高
    alternatives:
      - "默认值模式": 风险高，可能被忽略
      - "配置文件声明": 增加配置复杂度
    impact: "每次运行需额外1个参数，但防止重大混淆"
    status: "ACTIVE"
    
  - id: DEC-002
    date: "2026-01-20"
    topic: "覆盖率验收标准"
    decision: "核心模块必须100%覆盖，整体>=80%"
    reason: |
      1. v2.1.0 M5 发现核心模块覆盖率仅16%
      2. M1-M4 都签署了"测试通过"，但实际未检查
      3. 核心模块是系统骨架，必须全覆盖
    status: "ACTIVE"
```

**命令**:
```bash
# 查看决策历史
oc-collab memory decisions

# 查看特定决策
oc-collab memory decision --id DEC-001

# 搜索相关决策
oc-collab memory decisions --keyword "模式"

# 回溯场景：遇到类似问题时查看历史决策
oc-collab memory trace --problem "Mock模式混淆"
# 输出: 相关决策 DEC-001
```

### 2.10.3 周期性回顾提醒

**需求编号**: FR-MEMORY-003

**描述**: 定期回顾之前的经验教训，防止长期遗忘

**回顾机制**:
| 周期 | 触发条件 | 提醒内容 |
|------|----------|----------|
| 每次会话开始 | Agent 启动 | "上次会话遗留问题: 3个" |
| 每10次操作 | 操作计数 | "请回顾最近的经验教训" |
| 遇到类似问题 | 问题匹配 | "此问题已发生 N 次，上次解决方案..." |
| 里程碑签署前 | signoff 前 | "请确认已覆盖所有历史问题" |

**提醒配置**:
```yaml
reminder_config:
  session_start:
    enabled: true
    show_pending_issues: true
    
  operation_count:
    interval: 10
    show_lessons: true
    
  problem_pattern:
    enabled: true
    show_solutions: true
    
  before_signoff:
    enabled: true
    require_confirmation: true
```

**命令**:
```bash
# 查看待回顾事项
oc-collab memory review pending

# 执行回顾
oc-collab memory review --lessons --issues --patterns

# 配置提醒
oc-collab memory reminder config --session-start true --before-signoff true

# 忽略本次提醒
oc-collab memory reminder dismiss --session
```

### 2.10.4 Compaction 知识保留

**需求编号**: FR-MEMORY-004

**描述**: 确保 Compaction 操作不丢失关键记忆，包括问题模式、决策历史、经验教训

**Compaction 安全机制**:
```yaml
compaction_memory_protection:
  export_before_compaction:
    - "问题模式库 (state/memory/patterns.yaml)"
    - "决策历史 (state/memory/decisions.yaml)"
    - "经验教训 (state/memory/lessons.yaml)"
    - "历史问题记录 (state/issues.json)"
    
  import_after_compaction:
    - "检查是否存在记忆文件"
    - "验证记忆完整性"
    - "恢复到内存"
    - "确认无丢失"
    
  safety_checks:
    - "记忆文件签名验证"
    - "版本兼容性检查"
    - "完整性校验"
```

**Compaction 流程**:
```
用户执行 Compaction
    │
    ├── 1. 暂停所有 Agent
    │
    ├── 2. 导出关键记忆
    │   ├── 导出问题模式库
    │   ├── 导出决策历史
    │   ├── 导出经验教训
    │   └── 生成记忆摘要
    │
    ├── 3. 执行 Compaction
    │
    ├── 4. 导入记忆
    │   ├── 验证记忆文件
    │   ├── 恢复记忆到内存
    │   └── 生成导入报告
    │
    ├── 5. Agent 恢复
    │   ├── Agent 启动时加载记忆
    │   └── 确认记忆完整
    │
    └── 6. 输出确认
        └── "✓ 记忆已保留: 5 个问题模式, 10 个决策, 20 条经验"
:
```bash
```

**命令**# 查看 Compaction 保护状态
oc-collab memory compaction status

# 手动导出记忆（备份）
oc-collab memory export --output memory_backup_20260201.tar.gz

# 手动导入记忆（恢复）
oc-collab memory import --file memory_backup_20260201.tar.gz

# Compaction 前预览要保留的内容
oc-collab memory compaction preview
# 输出:
# === Compaction 记忆预览 ===
# 问题模式: 12 个
# 决策历史: 15 个
# 经验教训: 28 条
# 历史问题: 45 个
```

### 2.10.5 上下文继承

**需求编号**: FR-MEMORY-005

**描述**: 新会话继承之前会话的关键信息，Agent 启动时自动加载历史记忆

**继承内容**:
| 继承项 | 说明 | 优先级 |
|--------|------|--------|
| 项目状态 | 当前阶段、里程碑进度 | P0 |
| 问题模式库 | 已知问题及解决方案 | P0 |
| 决策历史 | 关键决策及理由 | P1 |
| 待办事项 | 未完成的任务 | P0 |
| 活跃问题 | 正在处理的问题 | P0 |
| 配置约束 | 当前生效的约束 | P1 |

**Agent 启动流程**:
```
Agent 启动
    │
    ├── 1. 加载项目状态
    │   └── state/project_state.yaml
    │
    ├── 2. 加载记忆
    │   ├── 加载问题模式库
    │   ├── 加载决策历史
    │   └── 加载经验教训
    │
    ├── 3. 生成会话摘要
    │   └── "欢迎回来！您有 3 个待处理问题..."
    │
    └── 4. 提供上下文
        └── 可以通过 memory 命令查看历史
```

**命令**:
```bash
# 查看当前会话继承的上下文
oc-collab memory context

# 查看历史问题
oc-collab memory history --type issues

# 查看决策历史
oc-collab memory history --type decisions

# 清除当前会话记忆（保留持久化）
oc-collab memory clear --session-only
```

### 2.10.6 智能提醒机制

**需求编号**: FR-MEMORY-006

**描述**: 在正确的时间提醒正确的 oc-collab 要求，不是"出错后提醒"，而是"开始前提醒"

**提醒策略**:
| 场景 | 提醒时机 | 提醒内容 |
|------|----------|----------|
| 写代码前 | 开始前 | "请确认已添加测试用例" |
| 提交前 | commit 前 | "请确认覆盖率检查通过" |
| 签署前 | signoff 前 | "请确认所有核心模块100%覆盖" |
| 配置 API Key | 配置时 | "建议使用环境变量，参考 config/template.yaml" |
| 运行测试 | 执行前 | "请使用 --fresh 参数确保结果可复现" |
| 模式切换 | --mode 前 | "Mock 模式仅用于测试，真实生成请用 --mode real" |

**提醒示例**:
```bash
# 用户尝试配置 API Key
$ oc-collab config set api_key=xxx

# 系统自动提醒
# ⚠️ 提醒: Financial 项目曾多次发生 API Key 配置错误
# 💡 建议: 使用环境变量配置
#    export OPENAI_API_KEY=xxx
# 📖 历史决策: DEC-001 (2026-01-15)
```

**提醒配置**:
```yaml
smart_reminders:
  enabled: true
  
  levels:
    - level: "blocking"
      description: "阻止操作，必须处理"
      examples: ["覆盖率不足", "缺少测试"]
      
    - level: "warning"
      description: "警告，但可继续"
      examples: ["历史问题复发", "配置建议"]
      
    - level: "info"
      description: "信息提示"
      examples: ["回顾提醒", "历史决策"]
```

**命令**:
```bash
# 查看当前生效的提醒
oc-collab memory reminders active

# 配置提醒策略
oc-collab memory reminders config --level blocking --enabled true

# 临时禁用提醒
oc-collab memory reminders disable --session

# 查看历史提醒
oc-collab memory reminders history
```

### 2.10.7 经验教训沉淀

**需求编号**: FR-MEMORY-007

**描述**: 将问题解决经验沉淀为可复用的知识卡片

**经验卡片模板**:
```yaml
lesson_cards:
  - id: LESSON-001
    title: "API Key 配置最佳实践"
    category: CONFIGURATION
    situation: |
      Financial 项目反复发生 API Key 配置错误
    solution: |
      1. 使用环境变量而非硬编码
      2. 配置文件模板 + .gitignore 保护
      3. 启动时 config_validator.py 检查
    outcome: |
      后续项目未再发生同类问题
    tags: [API_KEY, CONFIGURATION, BEST_PRACTICE]
    
  - id: LESSON-002
    title: "Mock/Real 模式隔离"
    category: TESTING
    situation: |
      测试时误用 Real 模式导致费用增加
    solution: |
      1. 强制 --mode 参数声明
      2. Mock 模式添加水印
      3. CI 流程强制 Mock 模式
    outcome: |
      误用率降为 0
    tags: [MOCK, TESTING, COST_CONTROL]
```

**命令**:
```bash
# 查看所有经验卡片
oc-collab memory lessons

# 查看特定经验
oc-collab memory lesson --id LESSON-001

# 搜索经验
oc-collab memory lessons --tag CONFIGURATION

# 从问题生成经验卡片
oc-collab memory lesson create --from-issue ISSUE-001
```

### 2.10.8 智能记忆验收标准

| 标准 | 要求 | 验证方式 |
|------|------|----------|
| 问题模式记忆 | 记录并提醒已知问题 | `oc-collab memory patterns` 显示已知问题 |
| 决策追溯 | 可回溯关键决策 | `oc-collab memory decision --id DEC-001` |
| Compaction 安全 | 记忆不丢失 | Compaction 前/后记忆一致 |
| 智能提醒 | 操作前提醒 | 配置 API Key 时显示建议 |
| 上下文继承 | 新会话加载历史 | Agent 启动时显示会话摘要 |
| 经验沉淀 | 问题→经验卡片 | `oc-collab memory lessons` 显示沉淀经验 |

**测试用例**:
```bash
# 1. 测试问题模式识别
oc-collab memory test pattern --input "API Key 错误"
# 预期: 匹配 PATTERN-001，显示解决方案

# 2. 测试 Compaction 记忆保护
oc-collab memory test compaction
# 预期: Compaction 后记忆完整

# 3. 测试智能提醒
oc-collab config set api_key=test
# 预期: 显示提醒和建议

# 4. 测试上下文继承
oc-collab agent start
# 预期: 显示会话摘要和待处理问题
```

---

## 3. 非功能需求

### 3.1 性能需求

| 指标 | 要求 |
|------|------|
| Agent 启动时间 | < 5 秒 |
| 状态同步延迟 | < 1 秒 |
| 任务分配响应 | < 2 秒 |
| 进度看板更新 | < 3 秒 |

### 3.2 可扩展性

| 需求 | 说明 |
|------|------|
| 最大 Agent 数量 | 20 |
| 最大任务数量 | 1000 |
| 最大项目周期 | 12 个月 |

### 3.3 可靠性

| 需求 | 说明 |
|------|------|
| 状态持久化 | 每次变更保存 |
| 锁超时自动释放 | 防止死锁 |
| 冲突检测 | 并发修改时警告 |

---

## 4. 验收标准

### 4.1 多 Agent 管理验收

| 标准 | 验证方式 |
|------|----------|
| 支持 2+ Agent | 启动 3 个 Agent 测试 |
| Agent 动态添加 | 执行 `oc-collab agent add` |
| 职责约束生效 | Agent 越权操作被拒绝 |

### 4.2 UE/UI 设计管理验收

| 标准 | 验证方式 |
|------|----------|
| 设计稿上传 | 上传 PNG/SVG 文件 |
| 版本管理 | 创建 3 个版本，对比差异 |
| 设计对比 | PNG vs PNG 对比标记 |

### 4.3 多技术栈协同验收

| 标准 | 验证方式 |
|------|----------|
| 技术栈选择 | 详细设计阶段选择 React + Go |
| 多仓库协作 | 前端/后端独立 repo |
| 接口规范 | API 文档生成 + Mock 数据 |

### 4.4 项目管理验收

| 标准 | 验证方式 |
|------|----------|
| 任务分配 | 任务分配给正确 Agent |
| 依赖管理 | 前置任务阻塞后置任务 |
| 进度看板 | 显示所有 Agent 进度 |
| 协调通知 | 状态变更通知相关 Agent |

### 4.5 执行约束管理验收

| 标准 | 验证方式 |
|------|----------|
| 配置验证器 | `oc-collab config validate` 检测缺失配置 |
| 模式管理器 | `oc-collab run --mode mock` 正常工作 |
| 测试隔离器 | `oc-collab test --isolated` 生成独立目录 |
| 问题追踪器 | 问题记录后自动生成回归测试 |
| PDF质量验证器 | `oc-collab pdf validate` 检测已知问题 |
| 问题复发阻止 | 已知问题复发时PR被阻止 |

### 4.6 覆盖率检查验收（v2.1.0 M5教训）

**背景**: v2.1.0 M5发现核心模块覆盖率仅16%，但M1-M4都签署了"测试通过"。原因是验收标准写了"覆盖率>=80%"但没人真的运行coverage命令检查。

**v2.2.0 覆盖率验收标准**:

| 标准 | 要求 | 验证方式 |
|------|------|----------|
| 核心模块覆盖率 | 100% | `oc-collab coverage check --module daemon.py ...` |
| 整体覆盖率 | >=80% | `oc-collab coverage report` |
| 覆盖率报告 | 已生成 | `oc-collab coverage report --output coverage.md` |
| 覆盖率无下降 | 不能比上次低 | `oc-collab coverage trend` |
| CI门禁 | 通过 | GitHub Actions自动检查 |

**核心模块清单**（必须100%覆盖）:
| 模块 | 文件路径 | 优先级 |
|------|----------|--------|
| daemon.py | src/core/daemon.py | P0 |
| supervisor.py | src/core/supervisor.py | P0 |
| signoff.py | src/core/signoff.py | P0 |
| state_manager.py | src/core/state_manager.py | P0 |
| exception_handler.py | src/core/exception_handler.py | P0 |

**覆盖率检查命令**:
```bash
# 运行覆盖率检查
oc-collab coverage run

# 检查核心模块覆盖率
oc-collab coverage check --core-modules

# 生成覆盖率报告
oc-collab coverage report --format markdown

# 检查覆盖率趋势
oc-collab coverage trend

# CI模式（失败时返回非0退出码）
oc-collab coverage check --strict
```

**覆盖率验收检查清单**:
```bash
# 1. 运行覆盖率
oc-collab coverage run
# ✓ 测试通过

# 2. 检查核心模块覆盖率
oc-collab coverage check --core-modules
# ✓ daemon.py: 100%
# ✓ supervisor.py: 100%
# ✓ signoff.py: 100%
# ✓ state_manager.py: 100%
# ✓ exception_handler.py: 100%

# 3. 检查整体覆盖率
oc-collab coverage report
# TOTAL: 100%

# 4. 检查覆盖率趋势
oc-collab coverage trend
# ✓ 覆盖率无下降

# 检查结果: ✅ 通过
```

**覆盖率门禁规则**:
| 条件 | 动作 | 说明 |
|------|------|------|
| 核心模块<100% | 阻断签署 | 不能进入下一里程碑 |
| 整体覆盖率<80% | 阻断签署 | 不能进入下一里程碑 |
| 覆盖率下降>5% | 警告+说明 | PR中需要解释原因 |
| 覆盖率报告未生成 | 阻断签署 | 必须生成报告 |

---

## 5. 依赖

### 5.1 内部依赖

| 模块 | 用途 | 版本 |
|------|------|------|
| `src/core/state_manager.py` | 状态管理 | v2.1.0 |
| `src/core/signoff.py` | 签署引擎 | v2.1.0 |
| `src/core/daemon.py` | 守护进程 | v2.1.0 |
| `src/core/supervisor.py` | 进程监管 | v2.1.0 |

### 5.2 v2.2.0 新增模块

| 模块 | 功能 | 交付里程碑 |
|------|------|-----------|
| `src/core/config_validator.py` | 配置验证器 | M5 |
| `src/core/mode_manager.py` | 模式管理器 | M5 |
| `src/core/test_isolator.py` | 测试隔离器 | M5 |
| `src/core/issue_tracker.py` | 问题追踪器 | M5 |
| `src/core/pdf_quality_validator.py` | PDF质量验证器 | M5 |
| `src/core/coverage_checker.py` | 覆盖率检查器 | M6 |
| `src/core/coverage_gates.py` | 覆盖率门禁 | M6 |

### 5.3 覆盖率检查专用依赖

| 依赖 | 用途 | 最低版本 |
|------|------|---------|
| watchdog | 文件监听 | 3.0.0 |
| imagehash | 图像对比 | 4.0 |

---

## 6. 里程碑

| 里程碑 | 内容 | 交付物 | 签署 |
|--------|------|--------|------|
| M1 | 多 Agent 基础 | Agent 动态管理 | Agent 1 |
| M2 | UE/UI 设计管理 | 设计稿管理、对比 | Agent 1 |
| M3 | 多技术栈协同 | 技术栈选择、接口管理 | Agent 1 |
| M4 | 项目管理 | 任务分配、进度看板、资源锁 | Agent 1 |
| M5 | 执行约束管理 | ConfigValidator, ModeManager, TestIsolator, IssueTracker, PDFQualityValidator | Agent 1 |
| M6 | 覆盖率门禁+完整测试套件 | coverage_check.py, CI集成, 集成测试 | Agent 1+Agent 2 |

---

## 7. 多 Agent 协作机制

### 7.1 Agent 角色互动关系

**核心原则**: 所有 Agent 通过 Git 通信，禁止直接读取本地文件。

#### 7.1.1 角色互动矩阵

| 角色组合 | 互动频率 | 互动方式 | 主要协作内容 |
|---------|----------|----------|-------------|
| Agent 1 ↔ Agent 2 | 高 | Git + 状态机 | 需求评审、设计评审、签署确认 |
| Agent 1 ↔ 设计师 | 中 | Git + 任务分配 | 设计需求、设计评审 |
| Agent 2 ↔ 前端 | 高 | Git + 任务分配 | API 定义、代码评审 |
| Agent 2 ↔ 后端 | 高 | Git + 任务分配 | API 定义、代码评审 |
| 前端 ↔ 后端 | 高 | Git + 接口规范 | API 开发、集成测试 |
| 前端 ↔ 设计师 | 中 | Git + 设计稿 | UI 实现、设计走查 |
| 后端 ↔ 测试 | 中 | Git + 任务分配 | API 测试、集成测试 |

#### 7.1.2 协作流程图

```
项目启动
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    Agent 1 (产品经理)                    │
│  - 创建需求文档                                          │
│  - 确定是否需要 UI 设计                                   │
│  - 添加设计师 (如需要)                                    │
└─────────────────────────────────────────────────────────┘
    │ 创建需求文档 (Git)
    ▼
┌─────────────────────────────────────────────────────────┐
│                    Agent 2 (开发负责人)                  │
│  - 评审需求                                              │
│  - 补充需求 (基于开发经验)                                 │
│  - 确定技术栈                                            │
│  - 添加技术栈 Agent (前端/后端)                           │
└─────────────────────────────────────────────────────────┘
    │ 技术栈决策 (Git)
    ▼
┌──────────────────┬──────────────────┬──────────────────┐
│  Agent (前端)    │  Agent (后端)    │  Agent (设计师)  │
│  - 前端开发      │  - 后端开发      │  - UI 设计       │
│  - API 调用      │  - API 开发      │  - 设计走查      │
│  - UI 实现       │  - 数据库设计    │                 │
└──────────────────┴──────────────────┴──────────────────┘
    │         │                  │
    │         │ API 接口 (Git)    │ 设计稿 (Git)
    │         ▼                  ▼
    │    ┌──────────────────────────────────────────┐
    │    │              API 集成                      │
    │    │    - 前端调用后端 API                      │
    │    │    - 接口一致性测试                       │
    │    └──────────────────────────────────────────┘
    │
    │ 完成任务 (Git)
    ▼
┌─────────────────────────────────────────────────────────┐
│                    Agent 1 (产品经理)                    │
│  - 验收测试                                              │
│  - 签署确认                                              │
│  - 推进到下一阶段                                        │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Agent 间通信机制

#### 7.2.1 Git 通信协议

```yaml
# Agent 通信规范
communication_protocol:
  
  # 需求评审
  requirements_review:
    trigger: "Agent 1 提交需求文档"
    participants: [Agent 1, Agent 2]
    action: "Agent 2 评审并签署"
    notification: "GitHub Issue @Agent2"
  
  # 设计评审
  design_review:
    trigger: "Agent 2 提交设计文档"
    participants: [Agent 1, Agent 2]
    action: "Agent 1 评审并签署"
    notification: "GitHub Issue @Agent1"
  
  # 任务分配
  task_assignment:
    trigger: "Agent 1 分配任务"
    participants: [Agent 1, 指定 Agent]
    action: "Agent 认领任务"
    notification: "GitHub Issue @指定 Agent"
  
  # 设计稿更新
  design_update:
    trigger: "设计师提交设计稿"
    participants: [设计师, 相关开发 Agent]
    action: "开发 Agent 拉取设计稿"
    notification: "GitHub Issue @相关 Agent"
  
  # API 更新
  api_update:
    trigger: "后端 Agent 更新 API"
    participants: [后端 Agent, 前端 Agent]
    action: "前端 Agent 拉取 API 文档"
    notification: "GitHub Issue @前端 Agent"
  
  # 设计走查
  design_review_cycle:
    trigger: "前端 Agent 完成 UI 实现"
    participants: [前端 Agent, 设计师]
    action: "设计师进行走查"
    notification: "GitHub Issue @设计师"
```

#### 7.2.2 状态变更通知

```python
class AgentNotifier:
    """Agent 通知器。"""
    
    def notify_state_change(self, event_type: str, agent_id: str, details: dict):
        """通知状态变更。"""
        notification = {
            "type": event_type,
            "from_agent": agent_id,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        # 根据事件类型通知相关 Agent
        target_agents = self._get_target_agents(event_type, details)
        for agent in target_agents:
            self._send_notification(agent, notification)
    
    def _get_target_agents(self, event_type: str, details: dict) -> list:
        """获取需要通知的 Agent 列表。"""
        mapping = {
            "requirements_submitted": ["Agent 2"],
            "design_submitted": ["Agent 1"],
            "task_assigned": [details["assignee"]],
            "design_uploaded": [details["related_developer"]],
            "api_updated": [details["frontend_agent"]],
            "task_completed": [details["project_manager"]],
        }
        return mapping.get(event_type, [])
```

### 7.3 任务协作流程

#### 7.3.1 跨 Agent 任务协作示例

**示例: 用户模块开发**

```
场景: 开发一个用户模块，涉及前端、后端、UI 设计

1. 需求阶段 (Agent 1)
   ├── 创建需求: "用户模块需要登录、注册、个人资料"
   ├── 确定需要 UI 设计: 是
   └── 添加 Agent (设计师)

2. 设计阶段 (Agent 2 + 设计师)
   ├── Agent 2: 设计 API (用户 CRUD)
   ├── 设计师: 设计登录页、注册页、个人资料页
   └── Agent 1: 评审设计稿

3. 开发阶段
   ├── Agent (后端-Go): 开发用户 API
   │   └── 提交: api/users.py, api/auth.py
   │
   ├── Agent (前端-React): 开发前端页面
   │   ├── 拉取 API 文档
   │   ├── 提交: Login.tsx, Register.tsx, Profile.tsx
   │   └── 设计走查: 设计师检查 UI 一致性
   │
   └── Agent (设计师): 设计走查
       ├── 检查: 登录页 UI 是否符合设计稿
       ├── 问题: "登录按钮颜色不对"
       └── 前端 Agent 修复

4. 测试阶段
   ├── Agent (后端-Go): API 单元测试
   └── Agent (前端-React): UI 集成测试

5. 验收阶段 (Agent 1)
   ├── 检查: 所有功能是否实现
   └── 签署: "测试通过，同意部署"
```

#### 7.3.2 依赖管理

```yaml
# 任务依赖配置
task_dependencies:
  - id: TASK-001
    title: "用户模块需求分析"
    type: requirements
    assignee: Agent 1
    status: completed
  
  - id: TASK-002
    title: "用户 API 设计与开发"
    type: backend
    assignee: Agent (后端-Go)
    status: in_progress
    depends_on: [TASK-001]
  
  - id: TASK-003
    title: "登录/注册 UI 开发"
    type: frontend
    assignee: Agent (前端-React)
    status: pending
    depends_on: [TASK-001, TASK-002]
    # TASK-002 完成前，TASK-3 被阻塞
  
  - id: TASK-004
    title: "用户模块 UI 设计"
    type: design
    assignee: Agent (设计师)
    status: completed
    depends_on: [TASK-001]
  
  - id: TASK-005
    title: "设计走查"
    type: design_review
    assignee: Agent (设计师)
    status: pending
    depends_on: [TASK-003, TASK-004]
    # 等前端开发和设计都完成后进行走查
```

### 7.4 冲突避免机制

#### 7.4.1 资源锁

```python
class ResourceLock:
    """资源锁管理器。"""
    
    def acquire_lock(self, resource_type: str, resource_id: str, agent_id: str) -> bool:
        """获取资源锁。"""
        lock_key = f"{resource_type}:{resource_id}"
        
        if lock_key in self.active_locks:
            if self.active_locks[lock_key] != agent_id:
                return False  # 已被其他 Agent 锁定
        
        self.active_locks[lock_key] = agent_id
        self.lock_timers[lock_key] = time.time()
        return True
    
    def release_lock(self, resource_type: str, resource_id: str, agent_id: str):
        """释放资源锁。"""
        lock_key = f"{resource_type}:{resource_id}"
        
        if lock_key in self.active_locks:
            if self.active_locks[lock_key] == agent_id:
                del self.active_locks[lock_key]
    
    def check_timeout_locks(self):
        """检查超时的锁并自动释放。"""
        timeout = 30 * 60  # 30 分钟
        for lock_key, lock_time in self.lock_timers.items():
            if time.time() - lock_time > timeout:
                del self.active_locks[lock_key]
```

#### 7.4.2 任务冲突避免

```yaml
conflict_prevention:
  # 同一任务只能被一个 Agent 认领
  task_assignment:
    rule: "first_claim"
    lock_duration: "task_completion"
  
  # 文件编辑冲突检测
  file_editing:
    rule: "lock_before_edit"
    timeout: 30 minutes
  
  # 状态变更冲突检测
  state_change:
    rule: "atomic_operation"
    validation: "state_machine"
```

### 7.5 协作命令

```bash
# Agent 协作命令

# 查看任务分配
oc-collab project tasks --agent frontend

# 查看进度
oc-collab project progress

# 分配任务
oc-collab project assign --task TASK-003 --agent agent_frontend_react

# 设置依赖
oc-collab project dependency --task TASK-003 --depends-on TASK-001,TASK-002

# 锁定文件
oc-collab lock acquire --file src/api/users.go --agent agent_backend_go

# 查看锁定状态
oc-collab lock status --file src/api/users.go

# 协调会议（Agent 间同步）
oc-collab project sync --agents frontend,backend,designer --topic "API集成"

# 查看依赖关系
oc-collab project dependencies --task TASK-003
```

### 7.6 协作监控

```bash
# 协作监控面板
oc-collab project monitor

# 输出:
协作监控面板
============
项目: 用户模块开发
状态: 进行中

Agent 状态:
├─ Agent 1 (产品经理) [在线]
│   ├─ 当前任务: 验收测试
│   └─ 通知: 2 条未读
│
├─ Agent (后端-Go) [在线]
│   ├─ 当前任务: TASK-002 用户 API 开发
│   ├─ 进度: 80%
│   └─ 阻塞: 无
│
├─ Agent (前端-React) [在线]
│   ├─ 当前任务: TASK-003 登录 UI 开发
│   ├─ 进度: 40%
│   ├─ 阻塞: 等待 API 完成 (TASK-002)
│   └─ 通知: API 已更新
│
└─ Agent (设计师) [在线]
    ├─ 当前任务: TASK-005 设计走查
    ├─ 进度: 0%
    └─ 阻塞: 等待前端完成 (TASK-003)

冲突检测:
├─ 无文件冲突
├─ 无任务冲突
└─ 无状态冲突

资源使用:
├─ CPU: 15%
├─ 内存: 512MB
└─ 磁盘: 2.1GB
```

---

## 8. 用户故事 (User Stories)

> **说明**: 本章节描述 oc-collab 产品的用户故事列表，每个 Story 描述用户如何使用 oc-collab 及其功能。Story 编号伴随产品功能延伸而不断增长。

### Story S-001: 覆盖率检查作为签署前置条件

**作为** 产品经理（Agent 1）
**我希望** 在签署里程碑前系统强制检查代码覆盖率
**以便** 确保核心模块（daemon.py, supervisor.py等）有足够的测试覆盖

**前置条件**:
- Agent 2 提交了代码和测试
- 项目配置了覆盖率检查规则

**交互流程**:
| 步骤 | 用户操作 | 系统响应 |
|------|----------|----------|
| 1 | Agent 2 提交 PR | 系统运行测试和覆盖率检查 |
| 2 | 系统检测到核心模块覆盖率 < 100% | 系统返回错误，阻止合并 |
| 3 | Agent 2 补充测试 | 系统重新运行覆盖率检查 |
| 4 | 系统确认覆盖率达标 | 允许合并，通知 Agent 1 签署 |

**预期结果**:
- **成功场景**:
  - 核心模块覆盖率 100% 时，允许合并
  - Agent 1 可以在覆盖率报告上签署"通过"
  
- **失败场景**:
  - 核心模块覆盖率 < 100%: 系统阻止合并，显示缺失的模块列表
  - 覆盖率报告未生成: 系统要求先运行覆盖率检查

**E2E 测试覆盖**:
| 测试用例 | 说明 |
|----------|------|
| test_story_S001_coverage_gate | 验证覆盖率不足时PR被阻止 |
| test_story_S001_core_modules_100 | 验证核心模块必须100%覆盖 |
| test_story_S001_signoff_with_coverage | 验证签署时必须检查覆盖率 |

**验收标准**:
- [ ] daemon.py 覆盖率 100%
- [ ] supervisor.py 覆盖率 100%
- [ ] signoff.py 覆盖率 100%
- [ ] 覆盖率报告已生成并分析

### Story S-002: 执行模式强制声明

**作为** 开发负责人（Agent 2）
**我希望** 在运行系统时必须声明使用 Mock 模式还是 Real 模式
**以便** 避免测试时错误使用 Mock 数据导致结果失真

**前置条件**:
- 项目配置了模式声明规则

**交互流程**:
| 步骤 | 用户操作 | 系统响应 |
|------|----------|----------|
| 1 | Agent 2 执行 `oc-collab run` | 系统要求必须指定 --mode |
| 2 | Agent 2 指定 `--mode mock` | 系统使用 Mock 数据运行 |
| 3 | Agent 2 指定 `--mode real` | 系统使用真实 LLM 运行 |
| 4 | Agent 2 未指定模式 | 系统拒绝执行，提示需要声明 |

**预期结果**:
- **成功场景**:
  - 声明 --mode mock 时，系统使用 Mock 数据
  - 声明 --mode real 时，系统使用真实 LLM
  
- **失败场景**:
  - 未声明模式: 系统返回错误 "请使用 --mode real | mock | dry-run"

**E2E 测试覆盖**:
| 测试用例 | 说明 |
|----------|------|
| test_story_S002_mode_required | 验证必须声明模式才能运行 |
| test_story_S002_mock_mode | 验证 Mock 模式正常工作 |
| test_story_S002_real_mode | 验证 Real 模式正常工作 |

**验收标准**:
- [ ] 未声明模式时运行被拒绝
- [ ] Mock 模式返回预定义数据
- [ ] Real 模式调用实际 LLM
- [ ] 模式切换有审计日志

### Story S-003: 问题追踪与回归测试

**作为** 产品经理（Agent 1）
**我希望** 系统自动记录发现的问题，并在修复后生成回归测试
**以便** 防止同样的问题反复发生

**前置条件**:
- 发现了一个新问题（如 LLM 响应前缀残留）

**交互流程**:
| 步骤 | 用户操作 | 系统响应 |
|------|----------|----------|
| 1 | Agent 1 记录问题 | 系统创建 Issue，记录问题类型和描述 |
| 2 | Agent 2 修复问题 | 系统自动生成回归测试用例 |
| 3 | Agent 2 提交修复 | CI 运行回归测试验证 |
| 4 | 相同问题再次出现 | 系统检测到已知问题复发，阻止 PR |

**预期结果**:
- **成功场景**:
  - 问题记录后自动生成 Issue ID
  - 问题修复后自动生成回归测试
  - 相同问题复发时被 CI 阻止
  
- **失败场景**:
  - 问题未记录: 系统提醒需要先记录问题
  - 回归测试失败: 系统要求修复测试

**E2E 测试覆盖**:
| 测试用例 | 说明 |
|----------|------|
| test_story_S003_issue_creation | 验证问题记录功能 |
| test_story_S003_regression_test | 验证回归测试自动生成 |
| test_story_S003_regression_detection | 验证问题复发检测 |

**验收标准**:
- [ ] 问题记录后生成唯一 Issue ID
- [ ] 问题修复后自动生成回归测试
- [ ] 相同问题复发时 PR 被阻止
- [ ] 可以查询历史问题和修复状态

### Story S-004: 会议纪要自动生成

**作为** 产品经理（Agent 1）
**我希望** 系统能自动从会议录音或讨论中生成会议纪要
**以便** 减少人工整理时间，并确保决策可追溯

**前置条件**:
- 有会议录音文件或 Agent 间讨论记录

**交互流程**:
| 步骤 | 用户操作 | 系统响应 |
|------|----------|----------|
| 1 | 上传会议录音 | 系统调用语音转文字服务 |
| 2 | 生成转写文本 | 系统提取关键决策和待办 |
| 3 | 生成会议纪要 | 系统格式化输出纪要文档 |
| 4 | 关联版本 | 会议纪要与当前版本关联 |

**预期结果**:
- **成功场景**:
  - 会议纪要包含日期、参与者、决策、待办
  - 会议纪要关联到版本 (v2.2.0)
  - 可以通过命令查询历史会议
  
- **失败场景**:
  - 无录音文件: 系统提示需要提供录音或讨论记录

**E2E 测试覆盖**:
| 测试用例 | 说明 |
|----------|------|
| test_story_S004_meeting_import | 验证会议导入功能 |
| test_story_S004_minutes_generation | 验证纪要生成功能 |
| test_story_S004_version_association | 验证版本关联 |

**验收标准**:
- [ ] 可以导入录音或讨论记录
- [ ] 生成的纪要包含决策和待办
- [ ] 会议纪要关联到版本
- [ ] 可以通过命令查询历史会议

### Story S-005: 持续反馈纳入版本draft

**作为** 产品经理（Agent 1）
**我希望** 在版本开发过程中发现的问题能自动纳入下一版本的 draft
**以便** 确保问题不会被遗忘

**前置条件**:
- 版本开发过程中发现了一个新问题（非当前版本bug）

**交互流程**:
| 步骤 | 用户操作 | 系统响应 |
|------|----------|----------|
| 1 | 发现新问题（非当前版本bug） | 系统标记为"历史遗留问题" |
| 2 | 问题分类完成 | 系统自动纳入下一版本 draft |
| 3 | 查看下一版本 draft | 可以看到已纳入的问题列表 |
| 4 | 新版本开发开始 | 问题从 draft 移入需求清单 |

**预期结果**:
- **成功场景**:
  - 非当前版本问题自动进入下一版本 draft
  - 可以追溯问题的来源版本
  - 问题状态变更有完整记录
  
- **失败场景**:
  - 问题被错误分类为"当前版本bug": 需要人工重新分类

**E2E 测试覆盖**:
| 测试用例 | 说明 |
|----------|------|
| test_story_S005_feedback_routing | 验证反馈自动路由 |
| test_story_S005_draft_inclusion | 验证问题纳入 draft |
| test_story_S005_version_traceability | 验证版本追溯 |

**验收标准**:
- [ ] 问题被正确分类（非当前版本bug）
- [ ] 问题自动进入下一版本 draft
- [ ] 可以追溯问题来源版本
- [ ] 反馈收集有完整记录

### Story S-006: 多Agent动态管理

**作为** 项目经理（Agent 1）
**我希望** 能动态添加和移除 Agent
**以便** 根据项目需要灵活调整团队配置

**前置条件**:
- 项目已启动，至少有 Agent 1 和 Agent 2

**交互流程**:
| 步骤 | 用户操作 | 系统响应 |
|------|----------|----------|
| 1 | Agent 1 执行 `oc-collab agent add` | 系统提示选择 Agent 类型 |
| 2 | Agent 1 指定 `--role frontend --tech react` | 系统创建前端 Agent 配置 |
| 3 | 新 Agent 初始化完成 | 新 Agent 加入协作，开始读取项目状态 |
| 4 | Agent 1 执行 `oc-collab agent remove` | 系统移除指定 Agent |

**预期结果**:
- **成功场景**:
  - 新 Agent 可以正确初始化并加入协作
  - Agent 的职责约束生效
  - 移除 Agent 后不再参与协作
  
- **失败场景**:
  - 尝试添加超出限制数量的 Agent: 系统拒绝

**E2E 测试覆盖**:
| 测试用例 | 说明 |
|----------|------|
| test_story_S006_agent_add | 验证动态添加 Agent |
| test_story_S006_agent_remove | 验证动态移除 Agent |
| test_story_S006_role_constraints | 验证 Agent 职责约束 |

**验收标准**:
- [ ] 可以添加新 Agent (frontend, backend, designer等)
- [ ] 新 Agent 能正确初始化并加入协作
- [ ] Agent 有明确的职责约束
- [ ] 可以移除 Agent

### Story S-007: 项目进度看板

**作为** 项目经理（Agent 1）
**我希望** 有一个可视化的进度看板，显示所有 Agent 的任务进度
**以便** 实时了解项目整体状态

**前置条件**:
- 项目中有多个 Agent，且有分配的任务

**交互流程**:
| 步骤 | 用户操作 | 系统响应 |
|------|----------|----------|
| 1 | Agent 1 执行 `oc-collab project progress` | 系统显示进度看板 |
| 2 | 看板上显示所有 Agent 的任务状态 | 包括已完成、进行中、待处理的任务 |
| 3 | Agent 1 可以指定查看特定 Agent | 系统只显示该 Agent 的进度 |
| 4 | 任务状态变更 | 看板实时更新 |

**预期结果**:
- **成功场景**:
  - 进度看板显示所有 Agent 的任务
  - 任务状态清晰标注（已完成/进行中/待处理）
  - 可以查看整体进度百分比
  
- **失败场景**:
  - 无任务分配时: 看板显示为空状态

**E2E 测试覆盖**:
| 测试用例 | 说明 |
|----------|------|
| test_story_S007_progress_display | 验证进度看板显示 |
| test_story_S007_filter_by_agent | 验证按 Agent 过滤 |
| test_story_S007_progress_percentage | 验证进度百分比计算 |

**验收标准**:
- [ ] 显示所有 Agent 的任务状态
- [ ] 显示整体进度百分比
- [ ] 支持按 Agent 过滤
- [ ] 任务状态实时更新

---

## 9. 风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 多 Agent 状态一致 | 高 | 状态机保证原子性 |
| 任务依赖复杂 | 中 | 依赖关系可视化 |
| 资源锁死锁 | 中 | 超时自动释放 |

---

## 10. 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-01 | 待签署 |
| 开发负责人 | Agent 2 | 2026-02-01 | 待签署 |

---

## 附录B: 案例研究 - 金融案件PDF生成系统问题分析

### B.1 案例研究概述

本附录记录了对金融案件PDF生成系统（Financial Case Generator System）的深入分析。该项目采用双代理（Dual-Agent）模式开发，但未使用 oc-collab 协作框架。通过对其老版本（v1.0）与当前版本的对比分析，我们发现了导致项目陷入混乱状态的系统性根因。

**核心结论**: **没有约束机制，混乱是必然的，同样的问题会永远反复发生**

**案例研究文档**: [MEMO-2026-02-001_Financial_Case_Generator_Analysis.md](../00-memos/MEMO-2026-02-001_Financial_Case_Generator_Analysis.md)

### B.2 观察发现的问题摘要

#### B.2.1 文档体系混乱问题

| 观察编号 | 问题类别 | 问题描述 |
|----------|----------|----------|
| DOC-001 | 文档数量爆炸 | 根目录md文件从3个增加到24个，增长700% |
| DOC-002 | 命名规范缺失 | 同一类型文档采用随意命名 |
| DOC-003 | 版本隔离缺失 | 5个输出目录并行存在，无法区分有效版本 |
| DOC-004 | 变更追踪脱节 | 需求/设计与代码不一致 |
| DOC-005 | 质量门禁缺失 | 同样的内容污染问题反复发生 |
| DOC-006 | 测试报告泛滥 | 10+份测试报告无法快速定位最新结果 |
| DOC-007 | 入口脚本混乱 | 文档描述与实际情况不符 |
| DOC-008 | 版本信息错误 | 文档标注日期为2024年（应为2026年） |
| DOC-009 | 配置管理缺失 | 无配置模板、验证、文档 |
| DOC-010 | 问题修复无闭环 | Bug修复后无回归测试 |

#### B.2.2 独立执行时的反复执行问题

| 观察编号 | 问题类别 | 问题描述 | 对应v2.2.0解决方案 |
|----------|----------|----------|-------------------|
| EXE-001 | API Key配置错误 | 反复忘记LLM的key，模型不存在 | ConfigValidator |
| EXE-002 | Mock/Real模式混淆 | 测试用Mock，正式用Real，模式不明确 | ModeManager |
| EXE-003 | 中间结果复用 | 使用历史输出导致测试结果失真 | TestIsolator |
| EXE-004 | PDF问题重复发生 | 同样的PDF格式/内容问题反复发生 | IssueTracker |

### B.3 对oc-collab v2.2.0设计的启示

#### B.3.1 新增模块（已纳入主体需求）

> **说明**: 以下模块已纳入v2.2.0主体需求（第2.5节执行约束管理），此处为案例研究到需求的映射。

| 模块 | 功能 | 需求编号 | 章节 |
|------|------|----------|------|
| **ConfigValidator** | 配置验证，防止API Key/模型错误 | FR-CONFIG-001 | 2.5.1 |
| **ModeManager** | 模式管理，防止Mock/Real混淆 | FR-MODE-001 | 2.5.2 |
| **TestIsolator** | 测试隔离，防止复用中间结果 | FR-TEST-001 | 2.5.3 |
| **IssueTracker** | 问题追踪，防止问题复发 | FR-ISSUE-001 | 2.5.4 |
| **PDFQualityValidator** | PDF质量验证 | FR-PDF-001 | 2.5.5 |

**交付里程碑**: M5 - 执行约束管理

#### B.3.2 新增约束

| 约束 | 触发条件 | 动作 |
|------|----------|------|
| 配置完整性约束 | 启动时发现配置缺失 | 阻止运行，提示配置 |
| 模式声明约束 | 运行前未指定--mode | 阻止运行，要求声明 |
| 缓存使用警告 | 测试时检测到缓存 | 警告，建议--fresh |
| 问题复发阻止 | 发现已知问题 | PR阻止，要求修复 |
| 质量门禁约束 | 质量验证失败 | 阻止进入下一阶段 |

#### B.3.3 新增命令（已纳入主体需求）

> **说明**: 以下命令已纳入v2.2.0主体需求，此处为参考。

**详细命令说明见**: [2.5 执行约束管理](#25-执行约束管理)

```bash
# 配置相关
oc-collab config validate          # 验证配置完整性 (2.5.1)
oc-collab config template          # 生成配置模板 (2.5.1)

# 模式相关
oc-collab run --mode real          # 实际运行 (2.5.2)
oc-collab run --mode mock          # Mock模式 (2.5.2)
oc-collab mode status              # 查看当前模式 (2.5.2)

# 测试相关
oc-collab test --fresh             # 强制重新生成 (2.5.3)
oc-collab test --isolated          # 隔离测试 (2.5.3)

# 问题追踪
oc-collab issue list               # 列出已知问题 (2.5.4)
oc-collab issue regression         # 运行回归测试 (2.5.4)

# PDF质量验证
oc-collab pdf validate             # 验证PDF质量 (2.5.5)
oc-collab pdf check-regression     # 检查问题复发 (2.5.5)
```

### B.4 根因总结

| 根因 | 文档层面表现 | 执行层面表现 |
|------|-------------|-------------|
| **规范缺失** | 命名混乱、版本混乱 | 配置错误反复发生 |
| **隔离缺失** | 历史文档堆积 | 模式混淆、测试失效 |
| **追踪缺失** | 内容与代码脱节 | 问题修复无闭环 |
| **门禁缺失** | 无强制质量检查 | 同一问题反复发生 |

### B.5 建议行动项

#### 对oc-collab v2.2.0开发团队

> **说明**: 以下模块已纳入主体需求（2.5节），由Agent 2在M5阶段实现。

| 优先级 | 行动项 | 需求编号 | 章节 | 预期效果 |
|--------|--------|----------|------|----------|
| P0 | 实现ConfigValidator | FR-CONFIG-001 | 2.5.1 | 解决EXE-001 |
| P0 | 实现ModeManager | FR-MODE-001 | 2.5.2 | 解决EXE-002 |
| P0 | 实现TestIsolator | FR-TEST-001 | 2.5.3 | 解决EXE-003 |
| P0 | 实现IssueTracker | FR-ISSUE-001 | 2.5.4 | 解决EXE-004 |
| P0 | 实现PDFQualityValidator | FR-PDF-001 | 2.5.5 | 解决DOC-005 |
| P2 | 完善文档规范化 | - | - | 解决DOC-001至DOC-010 |

**交付里程碑**: M5 - 执行约束管理

### B.6 相关文档

| 文档编号 | 文档名称 | 说明 |
|----------|----------|------|
| MEMO-2026-02-001 | 金融案件PDF生成系统问题分析备忘录 | 完整案例研究 |
| docs/01-requirements/requirements_v2.2.0_DRAFT.md | v2.2.0需求文档 | 需求来源 |
| docs/02-design/OUTLINE_DESIGN_v2.2.0.md | v2.2.0概要设计 | 设计依据 |

---

**附录B版本**: v1
**创建日期**: 2026-02-01
**作者**: Agent 1 (产品经理)
**基于**: MEMO-2026-02-001_Financial_Case_Generator_Analysis.md

---

**创建人**: Agent 1
**日期**: 2026-02-01
**最后更新**: 2026-02-01
**状态**: 评审中 (REVIEW) - v2.2.0需求定稿，待Agent 2评审签署
