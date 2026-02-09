# oc-collab 开发阶段指南

**版本**: v1.1.0  
**适用阶段**: development  
**Agent**: Agent 2 (开发)

---

## 1. 开发阶段概述

开发阶段是需求和设计评审通过后，将设计文档转化为可运行代码的过程。

### 阶段入口条件
- [x] 需求文档已签署 (PM + Dev)
- [x] 详细设计文档已签署 (Agent 1)
- [x] `project_state.yaml` 中 `phase: development`

### 阶段出口条件
- [x] 所有功能模块实现完成
- [x] 单元测试覆盖 ≥ 80%
- [x] 代码评审通过 (自检)
- [x] `project_state.yaml` 中 `development.status: completed`

---

## 2. 开发流程检查清单

### 2.1 开发前准备

| 步骤 | 操作 | 命令/检查 |
|------|------|----------|
| 1 | 确认当前版本 | `oc-collab status` |
| 2 | 确认设计已签署 | `oc-collab signoffs --list` |
| 3 | 查看详细设计文档 | `cat docs/02-design/DETAIL-*.md` |
| 4 | 确认概要设计参考 | `cat docs/02-design/OUTLINE-*.md` |
| 5 | 更新待办 | `oc-collab todowrite --content "实现M1功能" --priority high` |
| 6 | 创建开发分支 (可选) | `git checkout -b feature/v2.2.x` |

### 2.2 模块实现

根据设计文档中的模块分解逐一实现：

```
设计文档结构:
├── 功能模块 (M1, M2, M3...)
│   ├── 核心逻辑
│   ├── 错误处理
│   └── 边界条件
├── 测试用例
│   ├── 单元测试
│   └── 集成测试
└── API/CLI 接口
```

### 2.3 代码实现规范

#### 命名规范
```python
# 文件命名: 小写下划线
src/core/context_manager.py
src/cli/enhanced_commands.py

# 类命名: PascalCase
class ContextManager:
class TodoSyncManager:

# 函数命名: snake_case
def load_context():
def save_todos()
```

#### 错误处理
```python
# 定义专用异常
class ContextError(Exception):
    pass

class ContextNotFoundError(ContextError):
    pass

class ContextParseError(ContextError):
    pass
```

#### 文档字符串
```python
def load_context(self, config_path: Optional[Path] = None) -> ProjectContext:
    """
    加载项目上下文

    Args:
        config_path: 配置文件路径，为空则自动查找

    Returns:
        ProjectContext 对象

    Raises:
        ContextNotFoundError: 未找到配置文件
        ContextParseError: YAML 解析失败
        InvalidContextError: 必要字段缺失
    """
```

### 2.4 测试要求

#### 单元测试结构
```python
class TestModuleName:
    """模块名 测试类"""

    @pytest.fixture
    def setup(self):
        """测试前置"""
        pass

    def test_function_behavior(self):
        """TC-ID-001: 测试场景描述"""
        pass

    def test_edge_case(self):
        """TC-ID-002: 边界条件测试"""
        pass
```

#### 测试覆盖率要求
| 级别 | 覆盖率 | 说明 |
|------|--------|------|
| 核心模块 | ≥ 90% | ContextManager, StateManager |
| 业务模块 | ≥ 80% | TodoSyncManager, BrainEngine |
| CLI 模块 | ≥ 70% | enhanced_commands |

#### 运行测试
```bash
# 运行当前版本测试
python3 -m pytest tests/test_v2_2_x.py -v

# 运行所有测试
python3 -m pytest tests/ -v

# 运行并检查覆盖率
python3 -m pytest tests/ --cov=src --cov-report=term-missing
```

---

## 3. Git 提交规范

### 提交消息格式
```
<type>: <subject>

<body>

Testing: <test command>
```

### 类型 (Type)
| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | `feat: 添加 ContextManager 模块` |
| fix | Bug 修复 | `fix: 修复空文件解析错误` |
| docs | 文档更新 | `docs: 更新 README` |
| test | 测试相关 | `test: 添加边界测试用例` |
| refactor | 重构 | `refactor: 优化错误处理逻辑` |
| chore | 维护任务 | `chore: 更新依赖版本` |

### 示例
```bash
feat: v2.2.3 M1 ContextManager 实现

- 实现 .oc-collab.yaml 文件检测
- 实现上下文加载/保存
- 实现 Agent 编号验证

Testing: python3 -m pytest tests/test_v2_2_3.py -v
```

---

## 4. 开发状态管理

### 状态更新流程

```bash
# 1. 开发开始时更新状态
oc-collab project update --type development --value in_progress

# 2. 功能完成后更新
oc-collab todoedit TODO-001 --status completed

# 3. 开发完成时更新
oc-collab project complete
```

### 或直接编辑 state 文件

```python
from datetime import datetime
import yaml

state = yaml.safe_load('state/project_state.yaml')

state['v2.2.x']['development']['status'] = 'completed'
state['v2.2.x']['development']['started_at'] = '2026-02-08 xx:xx:xx'
state['v2.2.x']['development']['completed_at'] = datetime.now().isoformat()
state['v2.2.x']['development']['tests'] = 'xx passed'
state['v2.2.x']['development']['coverage'] = 'xx%'

yaml.dump(state, 'state/project_state.yaml')
```

---

## 5. 开发检查清单

### 代码检查
- [ ] 命名规范一致
- [ ] 错误处理完善
- [ ] 文档字符串完整
- [ ] 无硬编码配置
- [ ] 无敏感信息泄露

### 测试检查
- [ ] 核心路径覆盖
- [ ] 边界条件覆盖
- [ ] 错误场景覆盖
- [ ] 测试独立运行
- [ ] 测试可重复执行

### Git 检查
- [ ] 提交消息规范
- [ ] 功能原子提交
- [ ] 无临时文件提交
- [ ] 依赖更新已说明

### 任务交接检查 ⭐
- [ ] 功能/Bug修复完成后，更新 TODO 状态为 pending
- [ ] 在 TODO 标题中明确标注"已修复"或"已完成"
  - ✅ 正确: `TODO-XXX: 测试验收v2.2.4 P0功能（BUG-20260208-003已修复）`
  - ❌ 错误: `TODO-XXX: 测试验收v2.2.4 P0功能`（不标注状态）
- [ ] 让 Agent 1 知道任务状态变化，自然会去验证

---

## 6. 常见问题

### Q1: 设计与实现不符怎么办？
1. 以详细设计文档为准进行实现
2. 如有疑问，参考概要设计理解功能意图
3. 记录差异到代码注释
4. 通知 Agent 1 确认
5. 如需修改详细设计，重新发起设计评审

### Q2: 发现设计遗漏怎么办？
1. 评估影响范围
2. 通知 Agent 1 讨论
3. 小改动可先实现后补设计
4. 大改动需重新评审

### Q3: 测试覆盖率不达标？
1. 分析未覆盖的代码路径
2. 优先补充核心逻辑测试
3. 边界条件测试可简化
4. 记录技术债务

### Q4: 开发时间不足？
1. 评估最小可交付功能 (MVP)
2. 与 Agent 1 协商范围裁剪
3. 记录未完成项到下一版本
4. 保持代码质量优先

---

## 7. 开发阶段命令速查

| 操作 | 命令 |
|------|------|
| 查看状态 | `oc-collab status` |
| 查看待办 | `oc-collab todo` |
| 添加待办 | `oc-collab todowrite --content "任务" --priority high` |
| 添加待办(自动检查) | `oc-collab todowrite --content "任务" --agent 1 --priority high` (v2.2.6+) |
| 搜索Skill | `oc-collab skill search --keywords <关键词>` (v2.2.6+) |
| 查看Skill切片 | `oc-collab skill slice <skill_name>` (v2.2.6+) |
| 检查Skill | `oc-collab skill enforce` (v2.2.6+) |
| 更新待办 | `oc-collab todoedit TODO-001 --status completed` |
| 运行测试 | `python3 -m pytest tests/test_v2_2_x.py -v` |
| 提交代码 | `git commit -m "feat: xxx"` |
| 推送代码 | `oc-collab push --message "xxx"` |
| 完整提交 | `git add . && git commit -m "feat: xxx" && oc-collab sync-all -m "feat: xxx"` |

---

## 8. 交付物清单

开发完成时需交付：

| 交付物 | 位置 | 检查 |
|--------|------|------|
| 源代码 | `src/core/*.py` | ✅ |
| CLI 命令 | `src/cli/*.py` | ✅ |
| 单元测试 | `tests/test_v2_2_x.py` | ✅ |
| 测试报告 | 测试输出 | ✅ |
| 状态更新 | `state/project_state.yaml` | ✅ |
| Git 提交 | 本地/远程 | ✅ |

---

## 9. 与其他阶段衔接

### 开发 → 测试
1. 开发完成，更新 `development.status: completed`
2. 通知 Agent 1 进行测试验收
3. Agent 1 运行测试并签署

### 开发 → 设计 (如需返工)
1. 发现设计问题
2. 记录差异
3. 发起设计变更请求
4. 重新评审后继续开发

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-02-08 | 初始版本 |
| v1.1.0 | 2026-02-08 | 强调开发基于详细设计，增加概要设计参考 |
| v1.2 | 2026-02-08 | 添加任务交接检查清单，修复后标注"已修复" |
| v1.3 | 2026-02-09 | 添加v2.2.6新命令：todowrite自动检查、skill search/slice/enforce |

**维护者**: Agent 2
**更新日期**: 2026-02-09
