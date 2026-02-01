# 需求评审记录：oc-collab v2.1.0

**需求文档**: requirements_v2.1.0.md  
**评审日期**: 2026-02-01  
**评审人**: Agent 1 (产品经理)
**评审轮次**: 第 2 轮 (Agent 2 补充评审意见)

---

## 评审信息

| 项目 | 内容 |
|------|------|
| 需求版本 | v1 |
| 评审轮次 | 第 1 轮 → 第 2 轮 |
| 评审类型 | 设计评审 |
| 评审结论 | ✅ 批准（需纳入补充建议） |

---

## 评审意见

### 1. 总体评价

| 维度 | 评分 | 说明 |
|------|------|------|
| 需求完整性 | 5/5 | 功能覆盖全面，结构清晰 |
| 技术可行性 | 4/5 | 方案可行，部分需补充依赖 |
| 文档规范性 | 5/5 | 格式规范，要素齐全 |
| 可维护性 | 4/5 | 考虑较全，可增加测试策略 |

### 2. 通过的条款

| 条款编号 | 内容 | 评审意见 |
|---------|------|---------|
| 2.1 | E2E 测试框架 | ✅ 需要分阶段实现 |
| 2.2 | 异常处理增强 | ✅ 网络重试和磁盘检查有价值 |
| 2.3 | 监控告警功能 | ✅ 建议使用轻量级方案 |
| 2.4 | 配置热重载 | ✅ 支持热重载的配置项清晰 |
| 2.5 | Agent 行为约束系统 | ✅ 创新功能，职责分离更清晰 |

### 3. 需要修改的条款

| 条款编号 | 问题 | 建议修改内容 |
|---------|------|-------------|
| 5.2 | 外部依赖不完整 | 添加 `psutil` 和 `watchdog` |
| 2.3.1 | 监控依赖缺失 | 在 pyproject.toml 添加 psutil >= 5.0.0 |
| 2.4.1 | 文件监听依赖缺失 | 添加 watchdog >= 3.0.0 |

### 4. 待确认问题

| 问题 | 负责人 | 状态 |
|------|--------|------|
| 监控采样频率是否可配置？ | Agent 2 | 待确认 |
| 配置热重载的锁机制设计？ | Agent 2 | 待确认 |
| E2E 测试的范围边界？ | Agent 2 | 待确认 |

### 5. 需补充的多轮评审机制（重要）

**问题描述**:
当前需求文档仅定义了单次评审流程：
```
Agent 1 创建需求 → Agent 2 评审 → 双方签署
```

但实际项目中，评审可能有**多轮来回**：
```
第1轮: Agent 2 提出修改意见 → Agent 1 更新需求 → Agent 2 再次评审
第2轮: Agent 2 提出新意见 → Agent 1 更新 → Agent 2 再次评审
...
最终: 双方签署
```

**遗漏的要素**:
| 要素 | 当前状态 | 问题 |
|------|---------|------|
| 评审轮次 | ❌ 未定义 | 无法区分第1轮、第2轮 |
| 修改标记 | ❌ 未定义 | 无法追踪哪些内容已修改 |
| 争议解决 | ❌ 未定义 | 双方意见不一致时如何处理 |
| 签署时机 | ❌ 未明确 | 每轮评审后还是最终签署 |

**建议补充**:
```yaml
# 需求评审流程（多轮）
评审流程:
  - 轮次编号: "R1", "R2", "R3"...
  - 每次评审生成: review_v{n}.md
  - 每次修改生成: requirements_v{n}.md
  - 最终签署: 双方确认无新意见后

争议解决:
  - 优先级: P0/P1/P2
  - 仲裁: Agent 1 有最终决定权
  - 记录: 所有争议必须记录在案
```

**优先级**: P0 - 这是核心流程问题

---

## 改进建议（主动提出）

基于 v2.0.0 开发中遇到的问题，建议在 v2.1.0 中增加以下功能：

### 建议 1：State Schema 验证

**问题背景**: 
v2.0.0 开发中遇到 `design` 字段格式不兼容问题：
- 某些项目使用 `design: [列表]`
- 某些项目使用 `design: {字典}`
- 代码假设单一格式，导致运行时错误

**建议内容**:
```yaml
# state/project_schema.yaml
schema_version: "2.0.0"

project_structure:
  phase:
    type: string
    enum: [unknown, requirements, design, development, testing, deployment, completed]
  
  design:
    type: [list, dict]
    item_structure:
      version: string
      status: enum
      pm_signoff: boolean
      dev_signoff: boolean
```

**价值**:
- 启动时自动验证 state 结构
- 给出明确的错误提示
- 避免运行时崩溃

### 建议 2：State 版本自动迁移

**问题背景**:
不同版本的 state 结构可能不同：
- v1.0: `phase` 在根级
- v2.0: `phase` 在 `project` 下

**建议内容**:
```python
# src/core/state_migrator.py

class StateMigrator:
    MIGRATIONS = {
        "1.0": self.migrate_v1_to_v2,
        "2.0": self.migrate_v2_to_v3,
    }
    
    def migrate_v1_to_v2(self, state):
        # 将 root.phase 迁移到 project.phase
        if "phase" in state and "project" in state:
            state["project"]["phase"] = state.pop("phase")
        return state
```

**价值**:
- 自动兼容旧项目
- 减少用户手动调整
- 向后兼容性好

### 建议 3：包完整性测试

**问题背景**:
v2.0.0 发布时发现打包不完整：
- `src/cli/` 和 `src/core/` 目录未包含在 wheel 中
- 导致用户安装后无法使用 CLI 命令

**建议内容**:
在 `tests/test_package完整性.py` 中添加：
```python
def test_wheel_contents():
    wheel = zipfile.ZipFile("dist/opencode_collaboration-*.whl")
    required_files = [
        "src/cli/main.py",
        "src/core/signoff.py",
        "src/core/daemon.py",
    ]
    for f in required_files:
        assert f in wheel.namelist(), f"Missing: {f}"
```

**价值**:
- 防止发布不完整的包
- 提高发布质量
- 自动化验证

### 建议 4：更好的错误提示

**问题背景**:
用户遇到错误时，提示信息不够明确：
- `'list' object has no attribute 'get'`
- `phase: unknown`

**建议内容**:
```python
# 在 signoff.py 中
try:
    stage_data = state.get("design", {})
    if isinstance(stage_data, list):
        # 友好提示
        raise StateFormatError(
            "design 字段是列表格式，请确保使用正确的 state 结构。 "
            "参考: docs/state_structure_guide.md"
        )
except AttributeError as e:
    raise StateFormatError(
        f"无法读取 design 字段: {e}。 "
        "可能原因：state.yaml 格式不正确或版本不兼容。"
    )
```

**价值**:
- 帮助用户快速定位问题
- 减少技术支持成本
- 提升用户体验

### 建议 5：Git 工作流强制约束（新增）

**问题背景**:
在 `financial_case_generator_system` 项目中发现：
- Agent 2 直接读取本地测试报告，而非通过 Git
- 这违反了"双 Agent 通信必须走 Git"的核心原则

**建议内容**:
在附录 A 中添加 **A.5 Git 工作流强制约束**：

```yaml
所有项目通信必须通过 Git 进行:
- ✅ Agent 1 提交文档 → Git push → Agent 2 git pull → 读取
- ❌ Agent 2 直接读取本地文件（禁止）

强制 Git 拉取的操作:
- 读取需求文档 (Agent 2)
- 读取设计文档 (Agent 1)
- 读取测试报告 (Agent 2)
- 读取签署记录 (Agent 1/2)
- 读取代码变更 (Agent 1)
```

**违规检测**:
```python
def verify_git_workflow(agent_id, file_path):
    local_content = read_local_file(file_path)
    git_content = run_git_show(f"HEAD:{file_path}")
    if local_content != git_content:
        raise WorkflowViolation("请先执行 git pull 获取最新版本")
```

**价值**:
- 确保双 Agent 使用相同的项目视图
- 防止本地缓存导致的数据不一致
- 强化 Git 作为唯一通信桥梁的原则

---

## 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品经理（评审人） | Agent 1 | 2026-02-01 | ✅ |
| 开发（被评审人） | Agent 2 | 2026-02-01 | 待签署 |

---

## 后续行动

| 行动项 | 负责人 | 截止日期 |
|--------|--------|---------|
| 根据评审意见更新需求文档 | Agent 1 | 2026-02-01 |
| 创建技术设计文档 | Agent 2 | 2026-02-02 |
| 评估改进建议的可行性 | Agent 2 | 2026-02-02 |

---

## 第 2 轮评审：Agent 2 补充评审意见

**评审日期**: 2026-02-01  
**评审人**: Agent 2 (开发)

### 评审背景

基于 v2.0.0 开发中实际遇到的问题，补充以下建议到正式需求。

### 建议 6：State Schema 验证机制（正式纳入）

**问题背景**:
v2.0.0 开发中遇到 `design` 字段格式不兼容问题：
- 某些项目使用 `design: [列表]`
- 某些项目使用 `design: {字典}`
- 代码假设单一格式，导致运行时错误 `'list' object has no attribute 'get'`

**建议纳入正式需求**:

```yaml
## 2.6 State 结构验证（新增）

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
    
    # 检测 design 字段类型
    if 'design' in state:
        if isinstance(state['design'], list):
            issues.append("design 字段是列表格式")
        elif isinstance(state['design'], dict):
            issues.append("design 字段是字典格式")
    
    # 检测 phase 位置
    if 'phase' in state:
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

### 建议 7：包完整性测试（正式纳入）

**问题背景**:
v2.0.0 发布时发现打包不完整：
- `src/cli/` 和 `src/core/` 目录未包含在 wheel 中
- 导致用户安装后 CLI 命令不可用

**建议纳入正式需求**:

```yaml
## 2.7 包完整性验证（新增）

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
| src/core/*.py | 其他核心模块 | P1 |
| src/utils/*.py | 工具模块 | P1 |

**验证方法**:
```python
def test_wheel_contents(wheel_path):
    """验证 wheel 包包含所有必要文件。"""
    with zipfile.ZipFile(wheel_path) as zf:
        namelist = zf.namelist()
        
        required_files = [
            "src/cli/main.py",
            "src/cli/agent.py",
            "src/core/signoff.py",
            "src/core/daemon.py",
            "src/core/state_manager.py",
        ]
        
        for f in required_files:
            assert f in namelist, f"wheel 缺少必要文件: {f}"
```

### 2.7.2 发布前检查清单

**需求编号**: FR-PKG-002

**发布前必须执行**:
- [ ] 运行 `python -m pytest tests/test_package_completeness.py`
- [ ] 验证 wheel 文件大小 > 50KB
- [ ] 验证所有 CLI 命令可用
- [ ] 验证 PyPI 页面可访问

---

### 建议 8：友好错误提示（正式纳入）

**问题背景**:
当前错误提示技术化，用户难以理解：
- `'list' object has no attribute 'get'`
- `phase: unknown`

**建议纳入正式需求**:

```yaml
## 2.8 用户友好错误提示（新增）

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
        "reference": "https://github.com/.../state_structure_guide.md"
    },
    "PHASE_UNKNOWN": {
        "title": "未知的项目阶段",
        "message": "当前 phase 值为 'unknown'，系统无法识别。",
        "solution": "请运行 'oc-collab init' 重新初始化项目。",
    },
    "GIT_PULL_TIMEOUT": {
        "title": "Git 拉取超时",
        "message": "从远程仓库拉取更新超时。",
        "solution": "请检查网络连接，或稍后重试。",
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

### 建议 9：多轮评审机制（正式纳入）

**问题背景**:
当前需求文档仅定义了单次评审流程，但实际可能有**多轮来回**。

**建议纳入正式需求**:

```yaml
## 2.9 多轮评审机制（新增）

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
| diff_v2.1.0_R{n}.md | 与上一轮的差异 |

### 2.9.2 修改追踪

**需求编号**: FR-REVIEW-002

**描述**: 标记哪些内容在本次评审中修改

**修改标记格式**:
```markdown
## v2.1.0 R2 更新内容

### 新增
- [NEW] State Schema 验证机制 (FR-VAL-001)
- [NEW] 包完整性测试 (FR-PKG-001)

### 修改
- [MOD] Git 工作流约束细化 (A.5)
- [MOD] 错误提示模板扩展 (2.8)

### 修复
- [FIX] 多轮评审机制补充 (2.9)
```

### 2.9.3 签署时机

**需求编号**: FR-REVIEW-003

**描述**: 明确多轮评审中的签署规则

**签署规则**:
- 每轮评审后可以**选择性签署**
- 最终版本必须**双方完整签署**
- 签署后本轮锁定，不可再修改

---

## 第 2 轮评审总结

### 新增正式需求

| 编号 | 需求名称 | 优先级 | 纳入章节 |
|------|---------|--------|---------|
| FR-VAL-001 | State Schema 验证 | P0 | 2.6 |
| FR-VAL-002 | 兼容性检测 | P1 | 2.6 |
| FR-VAL-003 | State 版本迁移 | P1 | 2.6 |
| FR-PKG-001 | Wheel 内容验证 | P0 | 2.7 |
| FR-PKG-002 | 发布前检查清单 | P1 | 2.7 |
| FR-ERR-001 | 错误提示模板 | P1 | 2.8 |
| FR-ERR-002 | 上下文帮助 | P2 | 2.8 |
| FR-REVIEW-001 | 评审轮次管理 | P1 | 2.9 |
| FR-REVIEW-002 | 修改追踪 | P1 | 2.9 |
| FR-REVIEW-003 | 签署时机 | P1 | 2.9 |

### 评审结论

| 项目 | 结果 |
|------|------|
| 需求完整性 | ✅ 补充完整 |
| 技术可行性 | ✅ 可实现 |
| 优先级合理 | ✅ P0/P1/P2 分配合理 |
| 总体评估 | ✅ 建议纳入正式需求 |

---

## 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品经理（评审人） | Agent 1 | 2026-02-01 | ✅ 第1轮 |
| 开发（被评审人） | Agent 2 | 2026-02-01 | ✅ 第2轮 |

---

## 后续行动

| 行动项 | 负责人 | 截止日期 |
|--------|--------|---------|
| 将第2轮建议纳入正式需求文档 | Agent 1 | 2026-02-01 |
| 创建技术设计文档 | Agent 2 | 2026-02-02 |
