# oc-collab 新项目启动指南

## 快速启动

```bash
# 1. 创建项目目录
mkdir my-new-feature && cd my-new-feature

# 2. 初始化oc-collab项目结构
oc-collab init

# 3. 设置当前Agent (agent1或agent2)
export OC_COLLAB_AGENT=agent1
```

## 项目结构

```
my-new-feature/
├── src/                    # 源代码
│   ├── cli/                # CLI命令
│   ├── core/               # 核心模块
│   └── utils/              # 工具函数
├── tests/                  # 测试文件
├── docs/                   # 文档
│   ├── 00-architecture/    # 架构文档
│   ├── 01-requirements/    # 需求文档
│   ├── 02-design/         # 设计文档
│   └── 03-test/           # 测试报告
├── skills/                 # Skill文档
├── state/                  # 状态文件
│   ├── project_state.yaml  # 项目状态
│   └── agent_adhoc_todos.yaml  # 待办列表
└── pyproject.toml          # 项目配置
```

## 开发流程

### 1. 需求阶段 (Requirements)

- [ ] 创建需求文档: `docs/01-requirements/ANALYSIS_v<version>.md`
- [ ] Agent1分析需求并编写
- [ ] Agent2评审技术可行性
- [ ] 双方签署 → status: APPROVED

### 2. 设计阶段 (Design)

- [ ] 创建概要设计: `docs/02-design/OUTLINE_v<version>.md`
- [ ] 创建详细设计: `docs/02-design/DETAIL_v<version>.md`
- [ ] Agent1评审功能完整性
- [ ] Agent2评审技术实现
- [ ] 双方签署 → status: APPROVED

### 3. 开发阶段 (Development)

```bash
# 创建功能分支
git checkout -b feature/v<version>

# 开发实现
# - 核心模块: src/core/
# - CLI命令: src/cli/
# - 测试: tests/test_v<version>_modules.py

# 运行测试
python -m pytest tests/ -v

# 检查覆盖率
python -m pytest tests/ --cov=src --cov-report=term-missing
```

**覆盖率要求**: ≥ 80%

### 4. 测试阶段 (Testing)

- [ ] 单元测试: 全部通过
- [ ] E2E测试: 核心场景覆盖
- [ ] 黑盒测试: CLI命令验证
- [ ] 代码评审: self-check

### 5. 部署阶段 (Deployment)

```bash
# 更新版本号 pyproject.toml: version = "x.x.x"

# 更新CHANGELOG: docs/00-changelog/CHANGELOG.md

# Git提交
git add .
git commit -m "feat: v<x.x.x> description"
git tag v<x.x.x>

# 发布到PyPI
pip install -e .
twine upload dist/*
```

## 版本号规则

```
主版本.次版本.修订版本

v2.2.10
│ │   └─ Patch: Bug修复
│ └─ Minor: 新功能
└─ Major: 重大变更
```

## 关键文件

### project_state.yaml 更新

```yaml
v<x.x.x>:
  requirements:
    status: APPROVED
    agent1_signoff: true
    agent2_signoff: true
  design:
    status: APPROVED
    agent1_signoff: true
    agent2_signoff: true
  development:
    status: completed
    tests: <n> passed
    coverage: <n>%
  testing:
    status: completed
    unit_tests_passed: <n>
    e2e_tests: <n> passed
  version: <x.x.x>
```

### 提交通知Agent1

使用TODO通知：

```python
from src.core.state_notifier import StateNotifier

notifier = StateNotifier()
notifier.notify_todo_created(
    todo_id="TODO-<id>",
    content="验收v<x.x.x>: ...",
    agent_id="agent2",
    to_agent="agent1"
)
```

## Skill查询

遇到问题时先查Skill：

```bash
# 搜索相关Skill
oc-collab skill search --keywords <keyword>

# 查看Skill内容
oc-collab skill slice <skill_id>
```

## 常见问题

**Q: 不知道下一步做什么？**
A: 运行 `oc-collab startup-check` 检查未读TODO

**Q: 需要验证CLI命令？**
A: 运行 `--help` 检查命令是否正确注册

**Q: 测试失败怎么办？**
A: 检查错误信息，修复后重新运行

## Checklist

- [ ] 项目初始化完成
- [ ] 需求文档创建并签署
- [ ] 设计文档创建并签署
- [ ] 核心功能实现
- [ ] 单元测试覆盖 ≥ 80%
- [ ] E2E测试通过
- [ ] CLI命令验证
- [ ] project_state.yaml更新
- [ ] CHANGELOG更新
- [ ] 版本发布

---

**更新日期**: 2026-02-14
