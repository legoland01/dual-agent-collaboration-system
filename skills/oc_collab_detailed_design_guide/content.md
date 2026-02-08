# OC-Collab 详细设计指南

## 快速开始

```bash
# 1. 确认概要设计已批准 (APPROVED)
# 2. 复制模板
cp docs/02-design/TEMPLATE_detailed_design.md docs/02-design/DETAIL_vX.X.X.md
# 3. 编辑文档
# 4. 状态流转：DRAFT → READY → APPROVED
```

---

## 角色定位

| 角色 | 职责 | 禁止 |
|------|------|------|
| **Agent 2** | 创建详细设计、代码实现 | 创建概要设计 |
| **Agent 1** | 评审详细设计 | 代码实现、技术选型 |

---

## 概要设计 vs 详细设计

| 维度 | 概要设计 | 详细设计 |
|------|----------|----------|
| 视角 | 用户/功能 | 技术/代码 |
| 抽象级别 | 高（What） | 低（How） |
| 责任人 | Agent 1 | Agent 2 |
| 关注点 | 功能模块、分组、关系 | 技术模块、代码实现 |
| 与产品关系 | 直接对应 | 间接映射 |

---

## 核心原则

### 1. 功能模块 → 技术模块映射

**原则**：将概要设计中的功能模块映射为技术实现

```
概要设计：
- 功能模块：需求管理
- 子功能：需求创建、需求评审

详细设计：
- 技术模块：RequirementManager
- 代码类：Requirement, RequirementService
- CLI命令：oc-collab requirement create, oc-collab requirement review
```

### 2. 技术选型依据

| 选型 | 依据 | 参考 |
|------|------|------|
| Python Click | CLI框架 | 项目技术栈 |
| PyYAML | 配置解析 | 现有依赖 |
| GitPython | Git操作 | 现有依赖 |

### 3. 代码级设计

详细设计必须包含：

| 设计项 | 说明 | 详细程度 |
|--------|------|----------|
| 类设计 | 类名、属性、方法签名 | 具体实现 |
| 接口设计 | 函数签名、参数、返回值 | 具体定义 |
| 数据结构 | JSON/YAML结构 | 完整Schema |
| 异常处理 | 异常类型、错误码 | 完整列表 |
| 测试策略 | 单元测试、E2E测试 | 关键场景 |

### 4. 与概要设计的追溯

详细设计必须引用概要设计：

```markdown
## 功能模块映射

| 功能模块 (概要设计) | 技术模块 (详细设计) |
|---------------------|---------------------|
| 需求管理 | RequirementManager |
| 签署确认 | SignoffService |
```

---

## 标准文档结构

### 必须章节

| 章节 | 是否必须 | 说明 |
|------|---------|------|
| 1. 功能模块映射 | ✅ | 功能→技术模块映射 |
| 2. 技术架构 | ✅ | 模块划分、技术选型 |
| 3. 核心模块设计 | ✅ | 类/函数设计、接口定义 |
| 4. 数据结构 | ✅ | 状态文件、数据库Schema |
| 5. 算法与逻辑 | ✅ | 核心业务流程实现 |
| 6. API设计 | ✅ | 内部/外部接口 |
| 7. 错误处理 | ✅ | 异常场景、边界条件 |
| 8. 测试策略 | ✅ | 单元测试、E2E测试 |
| 9. 签署确认 | ✅ | 双人签署 |

---

## 章节模板

### 1. 功能模块映射

```markdown
## 1. 功能模块映射

### 1.1 映射表

| 功能模块 (概要设计) | 技术模块 (详细设计) | 对应文件 |
|---------------------|---------------------|----------|
| 需求管理 | RequirementManager | core/requirement.py |
| 签署确认 | SignoffService | core/signoff.py |
| Skill检查 | SkillEnforcer | core/skill.py |

### 1.2 新增文件

| 文件路径 | 功能 | 工时 |
|----------|------|------|
| src/core/xxx.py | xxx | Xh |
```

### 2. 技术架构

```markdown
## 2. 技术架构

### 2.1 模块架构图

```
[模块架构图 - 用文字描述或ASCII图]
```

### 2.2 技术选型

| 模块 | 技术/库 | 版本 | 选型依据 |
|------|---------|------|----------|
| CLI框架 | Click | >=8.0 | 现有技术栈 |
| 配置解析 | PyYAML | >=6.0 | 现有依赖 |
```

### 3. 核心模块设计

```markdown
## 3. 核心模块设计

### 3.1 类设计

```python
class RequirementManager:
    """需求管理器。"""
    
    def __init__(self, state_file: str = "state/project_state.yaml"):
        self.state_file = state_file
    
    def create(self, requirement: Requirement) -> bool:
        """创建需求。"""
        pass
    
    def validate(self, requirement: Requirement) -> tuple[bool, str]:
        """验证需求。"""
        pass
```

### 3.2 命令设计

| 命令 | 函数 | 描述 | 工时 |
|------|------|------|------|
| `oc-collab requirement create` | `create()` | 创建需求 | Xh |
| `oc-collab requirement review` | `review()` | 评审需求 | Xh |
```

### 4. 数据结构

```markdown
## 4. 数据结构

### 4.1 状态文件Schema

```yaml
# state/project_state.yaml
requirement:
  version: str
  status: str  # draft/ready/approved
  features:
    - id: str
      name: str
      status: str
```

### 4.2 配置Schema

```yaml
# config/xxx.yaml
xxx:
  key: value
```

### 4.3 API请求/响应

```json
// Request
{
  "action": "create",
  "data": {}
}

// Response
{
  "success": true,
  "data": {}
}
```
```

### 5. 算法与逻辑

```markdown
## 5. 算法与逻辑

### 5.1 核心流程

```mermaid
[流程图 - 用文字描述]
开始 → 步骤1 → 步骤2 → 结束
```

### 5.2 状态机

| 当前状态 | 事件 | 下一状态 |
|----------|------|----------|
| draft | submit | ready |
| ready | approve | approved |
| ready | reject | draft |
```

### 5.3 边界条件

| 边界条件 | 处理方式 |
|----------|----------|
| 空输入 | 提示错误 |
| 重复创建 | 拒绝并提示 |
| 超长字段 | 截断或拒绝 |
```
```

### 6. API设计

```markdown
## 6. API设计

### 6.1 内部CLI命令

| 命令 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `oc-collab xxx` | xxx | xxx | xxx |

### 6.2 外部API（可选）

| 端点 | 方法 | 输入 | 输出 | 说明 |
|------|------|------|------|------|
| /api/xxx | POST | JSON | JSON | xxx |
```

### 6.3 错误码

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 1001 | 参数错误 | 提示用户 |
| 2001 | 文件不存在 | 创建或报错 |
```
```

### 7. 错误处理

```markdown
## 7. 错误处理

### 7.1 异常类型

| 异常类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| ValidationError | 参数验证失败 | 返回错误信息 |
| FileNotFoundError | 文件不存在 | 创建或报错 |
| StateError | 状态不合法 | 阻止操作 |

### 7.2 错误恢复

| 错误场景 | 恢复方式 | 重试策略 |
|----------|----------|----------|
| xxx | xxx | xxx |
```
```

### 8. 测试策略

```markdown
## 8. 测试策略

### 8.1 单元测试

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| RequirementManager.create | 正常创建 | 返回True |
| RequirementManager.create | 重复创建 | 返回False |
| RequirementManager.validate | 有效需求 | 返回True |
| RequirementManager.validate | 无效需求 | 返回False |

### 8.2 E2E测试

| 测试场景 | 测试步骤 | 验收标准 |
|----------|----------|----------|
| 需求创建 | 1. 执行命令 | 成功创建 |
| | 2. 验证文件 | 文件存在 |
```

---

## 签署确认

### Agent 2 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | YYYY-MM-DD | ✅ |

### Agent 1 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | YYYY-MM-DD | ⏳ |

---

## 与开发的关联

详细设计完成后，直接进入开发阶段：

| 详细设计输出 | 开发输入 |
|--------------|----------|
| 类设计 | 代码实现 |
| 命令设计 | CLI实现 |
| 数据结构 | 状态文件 |
| 测试策略 | 单元测试 |

---

## 后续动作 ⭐

详细设计完成后，必须执行以下动作：

### 1. 创建TODO

```bash
# 创建开发TODO
oc-collab todowrite --content "实现vX.X.X功能：FR-XXX-001" --priority high
```

### 2. 同步到Git

```bash
# 提交详细设计文档
git add docs/02-design/DETAIL_vX.X.X.md
git commit -m "feat: vX.X.X详细设计 - xxx"

# 同步TODO状态
git add state/agent_adhoc_todos.yaml state/project_state.yaml
git commit -m "sync: 更新todo状态 - 进入开发阶段"

# 推送到所有远程（GitHub + Gitee）
git push --all
git push --tags
```

### 3. 开始开发

详细设计签署后，直接进入开发阶段，无需额外通知。

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-02-08 | 初始版本 |
| v2 | 2026-02-08 | 新增"后续动作"章节，明确TODO和Git同步要求 |
