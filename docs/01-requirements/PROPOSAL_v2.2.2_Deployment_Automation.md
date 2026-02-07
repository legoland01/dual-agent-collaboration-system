# PROPOSAL：v2.2.2 自动化增强功能

**提案编号**: PROPOSAL-v2.2.2-001
**版本**: v1.0
**创建日期**: 2026-02-07
**创建人**: Agent 1 (产品经理)
**状态**: 待评审

---

## 1. 背景

### 1.1 问题来源

v2.2.1 发布过程中发现的问题：

**问题 1：部署发布流程不清晰**
- Agent1 在执行 v2.2.1 发布时，对"如何发布到 PyPI"感到困惑
- COLLABORATION_GUIDE.md 第10行只说"Agent1 负责部署和发布"，但没有说明具体流程
- Agent2 之前能成功发布，是因为**他有自己的脚本和经验**，而不是靠 oc-collab 机制

**问题 2：不同项目有不同发布需求**
- Python 项目：打包发布到 PyPI
- Node.js 项目：发布到 npm
- Docker 项目：构建镜像推送到仓库
- Web 项目：部署到云服务器

**问题 3：跨版本复用问题**
- 如果每次发布都要重新配置，就会失去自动化的价值
- 用户应该能够定义一次配置，然后在多个版本中复用

### 1.2 核心洞察

oc-collab 的角色定位：
- **不应该**预先定义"如何部署发布"（因为项目类型各异）
- **应该**提供一个可配置的发布执行机制
- **应该**存储和复用用户的发布配置

### 1.3 用户期望

**用户的原始反馈**：
1. "部署发布的工作交给 Agent2 做的时候，他没有那么多的提问"
2. "我说的部署可能有错误，应该是在 PyPI 上打包发布"
3. "我原来把部署发布的工作交给 agent2 做的时候，好像他没有那么多问题"

**用户对新机制的期望**：
1. 部署发布流程应该根据各个项目的不同情况而有所差异
2. 由技术专家根据不同情况引导客户完成配置
3. 除非用户明确要求修改配置，否则应该跨版本复用

---

## 2. 目标

### 2.1 核心目标

为 oc-collab 添加**可配置的部署发布自动化机制**，使得：
1. 用户/技术专家能够定义项目的发布配置
2. 配置能够跨版本复用（v2.2.1 → v2.2.2 → v2.3.0）
3. 阶段推进时自动触发发布流程

### 2.2 预期收益

| 收益 | 说明 |
|------|------|
| 降低认知负担 | Agent 不需要记住发布流程，只需执行配置好的命令 |
| 跨版本复用 | 一次配置，多次使用 |
| 灵活性 | 支持不同类型的项目（PyPI、npm、Docker 等） |
| 自动化 | 阶段推进时自动触发发布 |

---

## 3. 功能需求

### 3.1 FR-DEPLOY-001: 可配置的发布命令

**需求描述**：
系统应该支持用户定义在特定阶段执行的发布命令。

**配置方式**：
```yaml
# deployment.yaml
version: "1.0"

commands:
  on_phase_advance:
    to_testing:
      - "echo 'Testing started'"
      - "pytest tests/ -v"
    to_deployment:
      - "python3 -m build"
      - "twine upload dist/*"
      - "git tag release-v${version}"
```

**触发时机**：
- 当执行 `oc-collab phase-advance` 时
- 系统自动检查配置的发布命令
- 按顺序执行配置的脚本/命令

### 3.2 FR-DEPLOY-002: 发布配置引导

**需求描述**：
系统应该提供交互式命令，帮助用户配置发布设置。

**命令**：
```bash
oc-collab deployment configure
```

**交互流程**：
1. 选择项目类型（Python/Node.js/Docker/其他）
2. 输入构建命令
3. 输入发布命令
4. 输入版本标签格式
5. 确认配置

**输出示例**：
```bash
$ oc-collab deployment configure

Welcome to oc-collab deployment configuration!

Project type: (python/nodejs/docker/other) [python]: python
Build command [python3 -m build]: 
Publish command [twine upload dist/*]: 
Tag format [release-v${version}]: 

Configuration saved to deployment.yaml

Available commands:
- oc-collab deployment show  # Show current configuration
- oc-collab deployment edit # Edit configuration
- oc-collab deployment run  # Run deployment commands manually
```

### 3.3 FR-DEPLOY-003: 配置跨版本复用

**需求描述**：
发布配置应该存储在项目根目录，随项目版本演进自动复用。

**存储位置**：
```
项目根目录/
├── deployment.yaml  ← 一次配置，跨版本复用
├── oc-collab.yaml
└── ...
```

**行为**：
- 首次使用时：提示用户配置
- 后续使用：自动读取并执行配置
- 版本更新时：复用同一份配置

### 3.4 FR-DEPLOY-004: 配置版本控制

**需求描述**：
发布配置应该纳入 Git 版本控制，确保可追溯。

**Git 集成**：
```bash
# 配置变更自动提交
oc-collab deployment configure  # 执行后自动 git add deployment.yaml
```

---

## 4. 非功能需求

### 4.1 安全性

| 需求 | 说明 |
|------|------|
| SEC-001 | 敏感信息（如 API Token）不应明文存储在 deployment.yaml 中 |
| SEC-002 | 支持从环境变量读取敏感配置 |

### 4.2 兼容性

| 需求 | 说明 |
|------|------|
| COMP-001 | deployment.yaml 为可选配置文件，不存在时不阻止阶段推进 |
| COMP-002 | 与现有阶段推进逻辑兼容 |

### 4.3 可用性

| 需求 | 说明 |
|------|------|
| USA-001 | 配置命令提供清晰的错误提示 |
| USA-002 | 支持查看和编辑现有配置 |

---

## 5. 验收标准

### 5.1 功能验收

| 标准 | 验证方式 |
|------|----------|
| 用户能够通过命令配置发布设置 | CLI 测试 |
| 配置能够跨版本复用 | 集成测试 |
| 阶段推进时自动执行发布命令 | E2E 测试 |
| 支持多种项目类型（Python、Node.js） | 单元测试 |

### 5.2 体验验收

| 标准 | 验证方式 |
|------|----------|
| 首次配置时有引导提示 | 人工测试 |
| 配置错误时有清晰提示 | 人工测试 |

---

## 6. 与现有功能的关系

### 6.1 与阶段推进的关系

| 现有功能 | 关系 | 说明 |
|----------|------|------|
| `oc-collab phase-advance` | 扩展 | 新增发布命令自动执行逻辑 |
| `oc-collab status` | 增强 | 显示发布配置状态 |

### 6.2 与状态管理的关系

| 现有功能 | 关系 | 说明 |
|----------|------|------|
| `state/project_state.yaml` | 互补 | 存储发布状态 |
| `deployment.yaml` | 新增 | 存储发布配置 |

### 6.3 与协作指南的关系

| 现有功能 | 关系 | 说明 |
|----------|------|------|
| COLLABORATION_GUIDE.md | 补充 | 更新部署发布章节 |

---

## 7. 实现路线图

### 7.1 MVP（v2.2.2）

| 功能 | 工时 | 优先级 |
|------|------|--------|
| deployment.yaml 配置文件解析 | 2h | P0 |
| `oc-collab deployment configure` 命令 | 4h | P0 |
| `oc-collab phase-advance` 集成发布命令 | 2h | P0 |
| 单元测试 | 2h | P0 |

### 7.2 增强（v2.3.0+）

| 功能 | 说明 |
|------|------|
| 敏感信息管理 | 支持环境变量 |
| 模板市场 | 预置常见项目类型配置 |
| 发布历史 | 记录每次发布结果 |

---

## 8. 开放问题

| 问题 | 说明 | 负责人 |
|------|------|--------|
| 敏感信息如何安全存储？ | 环境变量 vs 密钥管理服务 | Agent2 |
| 是否需要发布前确认？ | 防止自动发布到生产环境 | 讨论 |
| 是否需要回滚机制？ | 发布失败时自动回滚 | 讨论 |

---

## 9. 参考资料

| 参考 | 说明 |
|------|------|
| [PyPI 发布流程](https://packaging.python.org/en/latest/guides/publishing-package-index-repos/) | Python 包发布标准流程 |
| [npm 发布文档](https://docs.npmjs.com/cli/v8/using-npm/scripts) | Node.js 发布脚本 |

---

## 签署

| 角色 | 姓名 | 日期 | 签署状态 |
|------|------|------|----------|
| 产品经理 | Agent 1 | 2026-02-07 | ✅ |
| 开发负责人 | Agent 2 | 待评审 | pending |

---

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| v1.0 | 2026-02-07 | Agent 1 | 初始版本 |
