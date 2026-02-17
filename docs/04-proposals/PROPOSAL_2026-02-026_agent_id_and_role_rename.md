# Proposal: Agent身份体系与角色重命名

**版本**: v1  
**日期**: 2026-02-16  
**作者**: Consultant (战略规划)  
**状态**: 待评审

---

## 零、关联文档

本Proposal是**多Agent体系建设**的核心组成部分，与以下模块有密切关系：

### 0.1 交叉引用

| 关联模块 | 文档 | 关系说明 |
|----------|------|----------|
| **TODO系统** | `requirements_v2.3.1.md`<br>`OUTLINE_v2.3.1.md` | Agent编号用于TODO唯一标识<br>TODO-1to2-001中的编号对应Agent编号 |
| **Skill系统** | `skills/oc_collab_*.md` | Skill按职责编写，不按岗位<br>职责与岗位的映射关系 |
| **Git集成** | `ROADMAP_oc-collab.md` | 项目资源通过Git配置管理<br>项目成员信息同步 |
| **数据存储** | `PROPOSAL_2026-02-023_state_management.md` | Agent注册表、项目配置<br>使用SQLite存储 |
| **PM-Agent** | `PROPOSAL_2026-02-018_pm_agent.md` | PM-Agent项目同样使用<br>Agent身份体系 |

### 0.2 模块关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                     多Agent体系建设                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Agent体系   │  │  TODO系统    │  │  Skill系统  │           │
│  │  (本文)      │←→│  (编号关联)  │←→│  (职责关联)  │           │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘           │
│         │                  │                  │                   │
│         ▼                  ▼                  ▼                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Git集成                              │    │
│  │     项目配置同步 + 成员管理 + 变更追溯                   │    │
│  └─────────────────────────┬───────────────────────────────┘    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SQLite存储                           │    │
│  │     Agent注册表 + 项目配置 + 映射关系                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 0.3 版本依赖

| 本Proposal版本 | 依赖模块版本 | 说明 |
|----------------|--------------|------|
| v1 | v2.3.1 | Agent编号纳入TODO系统 |
| v1 | Skill v1.x | 职责按岗位自动映射 |
| v1 | SQLite存储 | Agent注册表实现 |

---

## 一、背景

### 1.1 问题来源

随着oc-collab框架的发展，项目数量和Agent数量都在增长：

| 项目 | 产品经理 | 架构师 | 状态 |
|------|----------|--------|------|
| oc-collab | Agent1 | Agent2 | v2.3.1开发中 |
| PM-Agent | Agent3 | Agent4 | 待启动 |

当前问题：
- "Agent1"、"Agent2"在不同项目中指代不同的人
- TODO编号（如TODO-1to2-001）产生歧义
- 规范文档无法明确指向具体的Agent

### 1.2 需求来源

- v2.3.1 TODO多Agent支持规划
- PM-Agent项目启动（4个Agent同时工作）

---

## 二、现状分析

### 2.1 当前术语

| 术语 | 定义 |
|------|------|
| Agent1 | 负责需求、设计、验收的产品角色 |
| Agent2 | 负责开发、实现的技术角色 |
| TODO编号 | TODO-X-xxx（单Agent）、TODO-XtoY-xxx（双Agent） |

### 2.2 存在的问题

| 问题 | 影响 |
|------|------|
| 角色命名抽象 | "Agent1"在不同项目中指不同人 |
| TODO编号歧义 | TODO-1to2-001 无法确定是哪个项目的 |
| 文档指向模糊 | 规范文档说"Agent1"不知道指向谁 |
| 多项目冲突 | 两个项目同时有"Agent1" |

### 2.3 已有方案

v2.3.1规划中使用角色编号：
```
TODO-1to2-001  (Agent1 → Agent2)
```

但这无法解决多项目并行问题。

---

## 三、方案设计

### 3.1 方案A：保持现状（不推荐）

**内容**：
- 继续使用Agent1/Agent2
- TODO编号保持角色格式：TODO-1to2-001

**问题**：
- ❌ 多项目并行时无法区分
- ❌ 文档指向模糊
- ❌ 未来扩展困难

### 3.2 方案B：角色重命名 + Agent ID（推荐）

#### 3.2.1 角色重命名

| 原术语 | 新术语 | 理由 |
|--------|--------|------|
| Agent1 | **产品经理** | 语义更清晰 |
| Agent2 | **架构师** | 强调技术设计，可扩展多个技术角色 |

**影响范围**：
- AGENTS.md
- CORE_ARCHITECTURE.md
- 所有Skill文档
- CLI命令输出

### 3.2.3 Agent ID设计

**命名规则**：
- 使用昵称（不是真名），好记即可
- 例如：zhangsan、lisi、xiaowang
- 不犯忌讳，易于识别

**使用场景**：
- 系统内部存储和追溯
- AI使用者无需记住，通过职务自动映射

### 3.2.4 项目内称呼规则

```
项目中互相称呼：职务（产品经理/架构师）
系统自动映射到Agent ID
```

**示例**：
```
张三在oc-collab项目中担任"产品经理"(编号1)
李四在oc-collab项目中担任"架构师"(编号2)

项目内对话：
  "产品经理，这个需求..."
  "架构师，这个实现..."

系统内部：
  发送者: zhangsan (产品经理, 编号1)
  接收者: lisi (架构师, 编号2)
  TODO内部: TODO-1to2-001
  TODO展示: 张三→李四-001
```

#### 3.2.3 统一编号体系

**编号规则**：
- 产品经理：编号1
- 架构师：编号2
- 其他Agent：编号3, 4, 5...
- 编号在项目内唯一

**编号→ID→名字映射**：
```yaml
# 项目配置中的Agent映射
agents:
  1:
    id: zhangsan
    name: 张三
    position: 产品经理
    
  2:
    id: lisi
    name: 李四
    position: 架构师
```

#### 3.2.4 TODO编号格式（内部使用编号）

| 版本 | 格式 | 示例 | 说明 |
|------|------|------|------|
| v2.3.1之前 | TODO-X-xxx | TODO-001 | 单Agent |
| v2.3.1 | TODO-XtoY-xxx | TODO-1to2-001 | 角色编号 |
| **新方案** | **TODO-XtoY-xxx** | **TODO-1to2-001** | Agent编号（内部） |

**格式说明**：
```
TODO-{发送者编号}→{接收者编号}-{序号}
例如：
  TODO-1to2-001  (张三发给李四)
  TODO-2to1-002  (李四发给张三)
  TODO-1to3-001  (张三发给王五)
```

#### 3.2.5 TODO展示（对外使用名字）

**展示规则**：
- 内部存储：TODO-1to2-001
- 对外展示：张三→李四-001

**CLI输出示例**：
```bash
$ oc-collab todo list

ID                  发送者    接收者    内容              状态
TODO-1to2-001      张三      李四      实现登录功能      进行中
TODO-2to1-002      李四      张三      代码评审          待处理
```

#### 3.2.6 注册表设计（带编号）

```yaml
# state/agents.yaml
agents:
  zhangsan:
    id: zhangsan
    name: 张三
    number: 1              # 项目内编号
    position: 产品经理      # 岗位
    project: oc-collab    # 所属项目
    status: active
    registered_at: "2026-02-16"
    
  lisi:
    id: lisi
    name: 李四
    number: 2
    position: 架构师
    project: oc-collab
    status: active
    registered_at: "2026-02-16"
```

#### 3.2.7 项目资源分配

**项目启动时必须分配资源**：
- 指定每个岗位由哪个Agent ID担任
- 产品经理和架构师是必须岗位
- 其他岗位可按需配置

**CLI命令**：
```bash
# 项目初始化时分配资源
oc-collab project init --name oc-collab \
  --member zhangsan:产品经理 \
  --member lisi:架构师

# 添加成员
oc-collab project add-member --project oc-collab \
  --member wangwu:测试工程师
```

**项目配置示例**：
```yaml
# state/projects/oc-collab.yaml
project:
  name: oc-collab
  created_at: "2026-02-16"
  
members:
  - agent_id: zhangsan
    position: 产品经理      # 岗位
    responsibilities:       # 职责（可多个）
      - 产品设计
      - 需求分析
      - 验收测试
      
  - agent_id: lisi
    position: 架构师
    responsibilities:
      - 系统设计
      - 技术选型
      - 代码实现
      - 开发测试
```

#### 3.2.6 agent.md动态调整

**原则**：agent.md根据项目setup自动调整

**示例：小型项目（2人）**
```
岗位：产品经理、架构师

产品经理实际职责：
  - 产品设计
  - 需求分析
  - 验收测试
  - 测试执行（兼）

架构师实际职责：
  - 系统设计
  - 技术选型
  - 代码实现
  - 开发测试（兼）
```

**示例：中型项目（3人）**
```
岗位：产品经理、架构师、测试工程师

产品经理职责：产品设计、需求分析、验收测试
架构师职责：系统设计、技术选型、代码实现
测试工程师职责：测试执行、缺陷跟踪
```

#### 3.2.7 职责与岗位的关系

**概念区分**：
- **岗位**：项目中的角色名称（产品经理、架构师、测试工程师）
- **职责**：具体工作内容（产品设计、代码实现、测试执行）

**映射规则**：
```
岗位 → 职责列表
产品经理 → [产品设计, 需求分析, 验收测试]
架构师 → [系统设计, 技术选型, 代码实现]
测试工程师 → [测试执行, 缺陷跟踪]

Skill按职责编写，不按岗位
```

**示例**：
- Skill: `oc_collab_requirements_guide` - 职责：需求分析
- Skill: `oc_collab_detailed_design_guide` - 职责：系统设计
- Skill: `oc_collab_development_guide` - 职责：代码实现
- Skill: `oc_collab_test_acceptance_guide` - 职责：验收测试

**一人多职处理**：
```yaml
# 2人项目
zhangsan:
  position: 产品经理
  responsibilities:
    - 产品设计（核心）
    - 验收测试（兼）

lisi:
  position: 架构师
  responsibilities:
    - 系统设计（核心）
    - 代码实现（核心）
    - 测试执行（兼）
```

```yaml
# state/agents.yaml
agents:
  zhangsan:
    id: zhangsan
    role: 产品经理      # 角色
    project: oc-collab # 所属项目
    status: active
    registered_at: "2026-02-16"
    
  lisi:
    id: lisi
    role: 架构师
    project: oc-collab
    status: active
    registered_at: "2026-02-16"
    
  wangwu:
    id: wangwu
    role: 产品经理
    project: pm-agent
    status: active
    registered_at: "2026-02-16"
    
  zhaoliu:
    id: zhaoliu
    role: 架构师
    project: pm-agent
    status: active
    registered_at: "2026-02-16"
```

#### 3.2.5 CLI命令更新

```bash
# 查看当前身份（自动根据项目和岗位映射）
oc-collab whoami
# 输出: Agent: zhangsan, Role: 产品经理, Project: oc-collab

# 项目初始化（分配资源）
oc-collab project init --name oc-collab \
  --member zhangsan:产品经理 \
  --member lisi:架构师

# 添加项目成员
oc-collab project add-member --project oc-collab \
  --member wangwu:测试工程师

# 列出所有Agent
oc-collab agent list

# 创建TODO（指定接收者职务，系统自动映射到编号）
oc-collab todowrite --to 架构师 --content "实现XXX功能"
# 内部存储: TODO-1to2-001
# 对外展示: 张三→李四-001
```

---

## 四、对比分析

### 4.1 方案对比

| 维度 | 方案A（保持现状） | 方案B（推荐） |
|------|-------------------|---------------|
| 多项目支持 | ❌ 差 | ✅ 好 |
| 精确追溯 | ❌ 差 | ✅ 好 |
| 语义清晰度 | ❌ 差 | ✅ 好 |
| 扩展性 | ❌ 差 | ✅ 好 |
| 实现复杂度 | ✅ 简单 | ✅ 中等 |

### 4.2 迁移兼容性

**向后兼容策略**：

| 旧格式 | 新格式 | 处理 |
|--------|--------|------|
| TODO-001 | TODO-1to1-001 | 自动转换 |
| TODO-1to2-001 | TODO-zhangsan→lisi-001 | 需要映射表 |

**映射表示例**：
```yaml
legacy_mapping:
  "1": "zhangsan"
  "2": "lisi"
  "3": "wangwu"
```

### 4.3 数据存储：SQLite

**选择SQLite的原因**：
- Agent和项目数据有关联查询需求
- 嵌入式，无需单独部署
- 支持事务，保证数据一致性

**数据库结构**：
```sql
-- Agent表
CREATE TABLE agents (
  id TEXT PRIMARY KEY,           -- 唯一标识（昵称）
  name TEXT,                     -- 展示名字
  number INTEGER,                -- 项目内编号
  position TEXT,                 -- 岗位
  project TEXT,                  -- 所属项目
  status TEXT DEFAULT 'active',  -- 状态
  registered_at TEXT             -- 注册时间
);

-- 项目表
CREATE TABLE projects (
  name TEXT PRIMARY KEY,
  created_at TEXT
);

-- 项目成员表
CREATE TABLE project_members (
  project TEXT,
  agent_id TEXT,
  position TEXT,
  responsibilities TEXT,         -- JSON数组
  PRIMARY KEY (project, agent_id)
);

-- 索引
CREATE INDEX idx_agents_project ON agents(project);
CREATE INDEX idx_agents_position ON agents(position);
```

**数据文件位置**：
```
state/
  oc-collab.db    -- SQLite数据库（Agent、项目）
  todo_queue.yaml -- TODO队列（保持YAML）
```

---

## 五、实施计划

### 5.1 版本安排

| 版本 | 内容 |
|------|------|
| v2.3.1 | 实现Agent ID + 角色重命名（与TODO多Agent支持一起） |
| 后续 | 完善注册表功能、多项目支持 |

### 5.2 实施步骤

1. **更新文档**（立即）
   - AGENTS.md：引入Agent ID概念
   - CORE_ARCHITECTURE.md：更新角色定义
   - 所有Skill：Agent1/Agent2 → 产品经理/架构师

2. **数据库实现**（v2.3.1）
   - 创建SQLite数据库 `state/oc-collab.db`
   - 实现Agent注册、项目管理模块
   - 保留TODO使用YAML

3. **CLI实现**（v2.3.1）
   - `oc-collab whoami` 命令 - 查看当前身份
   - `oc-collab agent register` 命令 - 注册Agent ID
   - `oc-collab agent list` 命令 - 列出所有Agent
   - `oc-collab project init` 命令 - 项目初始化 + 资源分配
   - `oc-collab project add-member` 命令 - 添加项目成员
   - TODO编号格式升级

3. **agent.md动态生成**
   - 根据项目setup自动生成
   - 包含当前项目的岗位和职责

4. **数据迁移**
   - 旧格式自动兼容
   - 映射表配置

### 5.3 影响评估

| 影响项 | 范围 | 风险 |
|--------|------|------|
| 规范文档 | 所有Skill和模板 | 低，需批量更新 |
| CLI命令 | 新增3个命令 | 低 |
| 历史TODO | 已有TODO | 低，兼容处理 |
| 用户习惯 | Agent称呼 | 中，需适应 |

---

## 六、开放问题（已更新）

| 问题 | 选项 | 建议 | 已确认 |
|------|------|------|--------|
| Agent ID格式 | 真实姓名/昵称/编号 | 昵称，好记 | ✅ 昵称 |
| 项目内称呼 | Agent ID/职务 | 职务 | ✅ 职务（系统自动映射） |
| 多项目兼任 | 允许/不允许 | 不允许 | ✅ 不允许 |
| 角色数量 | 仅2个/可扩展 | 可扩展 | ✅ 可扩展 |
| 项目资源分配 | - | 项目启动时分配 | ✅ 需要 |
| agent.md调整 | - | 根据项目setup | ✅ 需要 |
| Skill按职责 | - | 职责≠岗位 | ✅ 需要 |
| 数据存储 | YAML/SQLite | SQLite | ✅ SQLite |

---

## 七、结论

**推荐方案B**：角色重命名 + Agent ID体系

**理由**：
1. 彻底解决多项目并行时的指代模糊问题
2. TODO编号精确追溯到个人
3. 为未来扩展留出空间
4. 语义更清晰，与行业惯例一致

**下一步**：
1. 评审此Proposal
2. 确认后更新到v2.3.1需求文档
3. 开始实现

---

## 附录

### A. 相关文档

| 文档 | 当前状态 |
|------|----------|
| AGENTS.md | 待更新 |
| CORE_ARCHITECTURE.md | 待更新 |
| requirements_v2.3.1.md | 待更新 |
| OUTLINE_v2.3.1.md | 待更新 |

### B. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-02-16 | 初始版本 |
