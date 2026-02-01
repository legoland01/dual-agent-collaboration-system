# 需求评审记录：oc-collab v2.1.0

**需求文档**: requirements_v2.1.0.md  
**评审日期**: 2026-02-01  
**评审人**: Agent 1 (产品经理)

---

## 评审信息

| 项目 | 内容 |
|------|------|
| 需求版本 | v1 |
| 评审类型 | 设计评审 |
| 评审结论 | ✅ 批准 |

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
