# oc-collab 扩展开发准备指南：前端与后端数据库

**版本**: v1.0.0
**适用**: v2.2.x 扩展规划
**Agent**: Agent 1 (产品) + Agent 2 (开发)

---

## 1. 扩展概述

### 1.1 扩展目标

将 oc-collab 从纯 CLI 工具扩展为带 Web UI 和持久化存储的协作平台：

| 组件 | 技术选型 | 职责 |
|------|----------|------|
| 前端 | React/Vue.js | Web UI 界面 |
| 后端API | Java Spring Boot / Python FastAPI | 业务逻辑 |
| 数据库 | PostgreSQL / MySQL | 持久化存储 |
| CLI (保留) | Python | 开发者工具 |

### 1.2 架构模式选择

#### 方案A：单体应用 (Monolith)
```
oc-collab/
├── frontend/         # React/Vue前端
├── backend/          # Java后端
├── cli/             # Python CLI (保留)
├── src/             # 共享模型
└── docs/
```

**优点**: 部署简单，开发快速
**缺点**: 技术栈混合，维护复杂

#### 方案B：微服务架构
```
oc-collab-web/         # 前端 + Python API (轻量)
└── oc-collab-cli/     # Python CLI (独立)

# 或更细粒度
oc-collab-frontend/    # React/Vue
oc-collab-api/         # Java Spring Boot
oc-collab-cli/         # Python CLI
```

**优点**: 技术栈解耦，独立演进
**缺点**: 部署复杂，跨服务通信

**推荐**: 方案A起步，后续可拆分

---

## 2. 技术选型建议

### 2.1 前端技术栈

| 类别 | 推荐选择 | 理由 |
|------|----------|------|
| 框架 | React 18+ / Vue 3 | 生态成熟，文档完善 |
| UI库 | Ant Design / Element Plus | 企业级组件 |
| 状态管理 | Redux Toolkit / Pinia | 复杂状态处理 |
| 构建工具 | Vite | 开发体验好 |
| HTTP客户端 | Axios | 简洁易用 |

### 2.2 后端技术栈

| 类别 | 推荐选择 | 理由 |
|------|----------|------|
| 语言 | Java 17+ / Python FastAPI | 团队熟悉度 |
| 框架 | Spring Boot 3 / FastAPI | 生产力高 |
| ORM | MyBatis-Plus / SQLAlchemy | 生产力 |
| 数据库 | PostgreSQL 15+ | 功能强大 |
| 认证 | JWT + OAuth2 | 标准安全 |

### 2.3 数据库选型

| 数据库 | 适用场景 | 特点 |
|--------|----------|------|
| PostgreSQL | 复杂查询、JSON | 功能最全开源DB |
| MySQL | Web应用、事务 | 生态最广 |
| SQLite | 单机版、测试 | 零配置 |

**推荐**: PostgreSQL (开源、功能全)

---

## 3. 项目结构规划

### 3.1 扩展后目录结构

```
oc-collab/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── api/               # API调用层
│   │   ├── components/        # 公共组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # 状态管理
│   │   └── utils/             # 工具函数
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # 后端项目
│   ├── src/
│   │   ├── controller/        # API入口
│   │   ├── service/           # 业务逻辑
│   │   ├── mapper/            # 数据访问
│   │   ├── entity/            # 实体模型
│   │   └── config/            # 配置
│   ├── pom.xml / requirements.txt
│   └── application.yml
│
├── cli/                        # CLI模块 (保留)
│   ├── src/cli/
│   ├── src/core/
│   └── pyproject.toml
│
├── shared/                     # 共享模型 (可选)
│   ├── proto/                 # gRPC协议定义
│   └── models/                # 跨语言模型
│
├── scripts/                    # 构建/部署脚本
├── docs/
├── state/                      # 状态文件 (CLI用)
└── pyproject.toml             # Python CLI配置
```

### 3.2 CLI 与 Web 共享数据

**关键设计**: CLI 和 Web 使用同一数据源

```
方案1: CLI 直接操作数据库
├── cli/ → 直接连接 PostgreSQL
└── backend/ → 同一数据库

方案2: CLI 通过 API 访问
├── cli/ → HTTP调用 backend API
└── backend/ → 数据库
```

**推荐**: 方案1 (简单场景) / 方案2 (需要用户认证)

---

## 4. 数据库设计

### 4.1 核心数据模型

```sql
-- 用户/Agent表
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'agent1', 'agent2'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- 项目表
CREATE TABLE projects (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- TODO/任务表
CREATE TABLE todos (
    id VARCHAR(50) PRIMARY KEY,
    project_id VARCHAR(36) REFERENCES projects(id),
    content TEXT NOT NULL,
    priority VARCHAR(20),  -- high, medium, low
    status VARCHAR(20),   -- pending, in_progress, completed
    from_agent VARCHAR(36) REFERENCES users(id),
    to_agent VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- 状态变更记录表
CREATE TABLE state_history (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50),
    entity_id VARCHAR(50),
    old_state JSONB,
    new_state JSONB,
    changed_by VARCHAR(36) REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT NOW()
);
```

### 4.2 迁移策略

| 版本 | 迁移内容 |
|------|----------|
| v2.2.x → v2.3.0 | YAML → 数据库，添加users/projects表 |
| v2.3.x | 添加认证、权限管理 |
| v2.4.x | 高级查询、报表功能 |

---

## 5. API 设计

### 5.1 RESTful API 结构

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/projects | 列表项目 |
| POST | /api/v1/projects | 创建项目 |
| GET | /api/v1/projects/{id} | 项目详情 |
| GET | /api/v1/todos | 列表TODO |
| POST | /api/v1/todos | 创建TODO |
| PATCH | /api/v1/todos/{id} | 更新TODO |
| GET | /api/v1/todos/{id}/history | 状态历史 |

### 5.2 CLI 兼容性

```python
# CLI 保持兼容，使用现有命令
oc-collab todo list        # 内部改为调用API
oc-collab todo add         # 内部改为调用API
oc-collab startup-check   # 内部改为调用API
```

---

## 6. 前端功能规划

### 6.1 页面结构

```
前端/
├── 仪表盘/
│   └── 项目概览、待办统计
├── 项目管理/
│   ├── 项目列表
│   └── 项目详情
├── TODO管理/
│   ├── 看板视图 (Kanban)
│   └── 列表视图
├── 状态历史/
│   └── 变更记录查看器
└── 设置/
    └── 用户配置
```

### 6.2 关键组件

| 组件 | 功能 |
|------|------|
| TodoCard | TODO卡片 (Kanban) |
| TodoList | TODO列表 (表格) |
| StatusBadge | 状态标签 |
| AgentBadge | Agent标识 |
| Timeline | 状态变更时间线 |
| StatsPanel | 统计面板 |

---

## 7. 开发准备工作

### 7.1 环境准备清单

| 准备项 | 检查命令 |
|--------|----------|
| Node.js 18+ | `node -v` |
| Java 17+ | `java -version` |
| PostgreSQL 15+ | `psql --version` |
| Python 3.9+ | `python --version` |
| Git | `git --version` |

### 7.2 项目初始化

```bash
# 1. 前端初始化 (React + TypeScript)
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install antd axios pinia react-router-dom @tanstack/react-query

# 2. 后端初始化 (Spring Boot)
spring init -d web,data-jpa,postgresql,security backend
# 或 FastAPI
pip install fastapi uvicorn sqlalchemy alembic

# 3. 数据库初始化
createdb oc_collab
psql -d oc_collab -f scripts/schema.sql
```

### 7.3 现有代码迁移

```
迁移优先级:
P0: TodoQueueManager → todos表
P0: project_state.yaml → projects表
P1: agent_adhoc_todos.yaml → todos表(扩展)
P2: skill相关 → skills表
P3: webhook_stats → notifications表
```

---

## 8. 测试策略

### 8.1 测试分层

```
┌─────────────────────────────────────┐
│         E2E 测试 (Playwright)       │  ← 完整流程
├─────────────────────────────────────┤
│       集成测试 (API + Components)    │  ← API契约
├─────────────────────────────────────┤
│       单元测试 (Jest / pytest)       │  ← 核心逻辑
└─────────────────────────────────────┘
```

### 8.2 测试覆盖要求

| 级别 | 前端 | 后端 |
|------|------|------|
| 单元测试 | ≥ 70% | ≥ 80% |
| 集成测试 | ≥ 50% | ≥ 60% |
| E2E测试 | 核心流程 | 核心API |

---

## 9. CI/CD 规划

### 9.1 流水线阶段

```
代码提交
    ↓
前端构建 (npm run build)     后端构建 (mvn package / python -m build)
    ↓                           ↓
前端测试 (Jest)            后端测试 (pytest / JUnit)
    ↓                           ↓
容器镜像构建               单元测试
    ↓                           ↓
──────→ 部署到测试环境 ←──────
           ↓
──────→ 部署到生产环境 ←──────
```

### 9.2 工具推荐

| 环节 | 推荐工具 |
|------|----------|
| CI/CD | GitHub Actions / GitLab CI |
| 容器化 | Docker / Docker Compose |
| 部署 | Kubernetes / Railway |
| 监控 | Prometheus + Grafana |

---

## 10. 版本规划

### 10.1 扩展路线图

| 版本 | 目标 | 主要功能 |
|------|------|----------|
| **v2.3.0** | MVP发布 | 前端Web UI + 数据库持久化 |
| **v2.4.0** | 协作增强 | 多人协作、实时同步 |
| **v2.5.0** | 平台化 | 用户系统、权限管理 |
| **v3.0.0** | 重大升级 | 微服务拆分、云原生 |

### 10.2 向后兼容

- v2.3.0 **必须**保留现有 CLI 功能
- 现有 `state/*.yaml` 文件可继续使用，或提供迁移工具
- API 设计考虑 CLI 调用场景

---

## 11. 风险与应对

| 风险 | 应对措施 |
|------|----------|
| 技术栈分散 | 统一代码风格、共享TypeScript模型 |
| 数据迁移 | 提供YAML→DB迁移工具 |
| 维护成本 | 模块解耦、独立仓库管理 |
| 用户习惯 | 保留CLI，同时提供Web UI |

---

## 12. 启动检查清单

### Agent 1 (产品)

- [ ] 编写Web UI需求文档
- [ ] 设计数据库Schema
- [ ] 规划API接口
- [ ] 创建UI原型/设计稿
- [ ] 制定迁移计划

### Agent 2 (开发)

- [ ] 搭建前端工程
- [ ] 搭建后端工程
- [ ] 设计数据库Schema
- [ ] 实现基础CRUD
- [ ] 实现CLI→API兼容层
- [ ] 编写迁移工具

---

## 13. 参考资料

| 资源 | 链接 |
|------|------|
| React文档 | https://react.dev |
| Ant Design | https://ant.design |
| Spring Boot | https://spring.io/projects/spring-boot |
| FastAPI | https://fastapi.tiangolo.com |
| PostgreSQL | https://www.postgresql.org |

---

**维护者**: Agent 1 + Agent 2
**版本**: v1.0.0
**更新日期**: 2026-02-14
