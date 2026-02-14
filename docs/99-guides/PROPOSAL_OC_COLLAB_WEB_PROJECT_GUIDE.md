# ⭐ PROPOSAL: oc-collab Web项目扩展能力

**文档类型**: 提案 (供Agent1评审)
**版本**: v1.0.0
**作者**: Agent 2
**创建日期**: 2026-02-14
**状态**: 待Agent1评审

---

## 提案摘要

Agent2 建议 oc-collab 扩展支持前端+后端+数据库项目的协作开发。本文提供扩展方案供Agent1评审。

**是否采纳由Agent1决定**

---

## 1. 项目模板结构

### 1.1 完整项目模板

```
my-web-project/                    # 你的项目根目录
├── frontend/                      # 前端 (React/Vue)
│   ├── src/
│   │   ├── api/                # API调用
│   │   ├── components/         # 组件
│   │   ├── views/              # 页面
│   │   └── stores/             # 状态
│   └── package.json
│
├── backend/                      # 后端 (Java/Python)
│   ├── src/main/java/          # Java源码
│   │   ├── controller/         # API入口
│   │   ├── service/           # 业务逻辑
│   │   ├── mapper/            # 数据访问
│   │   └── entity/            # 实体类
│   └── pom.xml / requirements.txt
│
├── database/                     # 数据库
│   ├── schema.sql              # 表结构
│   └── migrations/             # 迁移脚本
│
├── oc-collab/                   # oc-collab 协作框架
│   ├── skills/                 # Skill文档
│   ├── docs/                   # 项目文档
│   │   ├── 01-requirements/   # 需求文档
│   │   ├── 02-design/         # 设计文档
│   │   └── 03-test/          # 测试报告
│   ├── state/                  # 状态管理
│   │   ├── project_state.yaml
│   │   └── agent_adhoc_todos.yaml
│   └── AGENTS.md              # Agent规则
│
└── scripts/                    # 构建脚本
```

### 1.2 oc-collab 协作目录

```
oc-collab/
├── skills/                       # Skill库（参考 oc-collab 项目）
│   ├── oc_collab_requirements_guide/
│   ├── oc_collab_development_guide/
│   ├── oc_collab_deployment_guide/
│   └── oc_collab_test_acceptance_guide/
│
├── docs/
│   ├── 01-requirements/
│   │   └── ANALYSIS_v1.0.md
│   ├── 02-design/
│   │   ├── OUTLINE_v1.0.md
│   │   └── DETAIL_v1.0.md
│   └── 03-test/
│       └── TEST REPORT_v1.0.md
│
├── state/
│   ├── project_state.yaml
│   └── agent_adhoc_todos.yaml
│
└── AGENTS.md
```

---

## 2. 开发流程 (oc-collab 规范)

### 2.1 完整阶段流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      oc-collab 开发流程                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Requirements → Design → Development → Testing → Deployment    │
│       (需求)       (设计)      (开发)       (测试)      (发布)  │
│                                                                 │
│  Agent 1: 产品经理 → 设计评审 → 验收测试 → 发布确认            │
│  Agent 2: 技术实现 → 代码开发 → 单元测试 → 部署上线            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 阶段详解

#### Phase 1: Requirements (需求)

**Agent 1 工作**:
- 编写 `oc-collab/docs/01-requirements/ANALYSIS_v1.0.md`
- 定义功能列表
- 定义 API 接口需求
- 定义数据库需求

**输出**:
```
docs/01-requirements/
└── ANALYSIS_v1.0.md      # 需求分析文档
```

#### Phase 2: Design (设计)

**Agent 1 工作**:
- 概要设计: `docs/02-design/OUTLINE_v1.0.md`
- 详细设计: `docs/02-design/DETAIL_v1.0.md`
- API 文档 (OpenAPI/Swagger)
- 数据库 Schema

**Agent 2 工作**:
- 评审技术可行性
- 提供实现建议

**输出**:
```
docs/02-design/
├── OUTLINE_v1.0.md       # 概要设计
└── DETAIL_v1.0.md        # 详细设计

database/
├── schema.sql            # 数据库表结构
└── migrations/          # 迁移脚本
```

#### Phase 3: Development (开发)

**Agent 2 工作**:

| 任务 | 前端 | 后端 |
|------|------|------|
| 基础工程 | React/Vue 初始化 | Spring Boot/FastAPI 初始化 |
| API对接 | 调用后端接口 | 提供 RESTful API |
| 状态管理 | Pinia/Redux | 数据库 CRUD |
| 测试 | 组件测试 | 单元测试 |

**输出**:
```
frontend/                    # 前端代码
backend/                     # 后端代码
database/migrations/         # 数据库迁移

oc-collab/state/
└── agent_adhoc_todos.yaml  # 开发任务跟踪
```

#### Phase 4: Testing (测试)

**Agent 2 工作**:
- 单元测试 (覆盖率 ≥ 80%)
- 集成测试 (API 测试)
- E2E 测试 (Cypress/Playwright)

**Agent 1 工作**:
- 验收测试
- 签署通过

**输出**:
```
docs/03-test/
└── TEST_REPORT_v1.0.md   # 测试报告
```

#### Phase 5: Deployment (部署)

**Agent 2 工作**:
- 构建 Docker 镜像
- 部署到服务器/云平台
- 更新 API 文档

**输出**:
```
frontend/dist/              # 构建产物
backend/target/             # 构建产物
docker-compose.yml         # 部署配置
```

---

## 3. 需求文档模板

### 3.1 ANALYSIS_v1.0.md 结构

```markdown
# [项目名称] 需求分析

## 1. 项目概述

## 2. 功能需求

### 2.1 前端功能

| 功能ID | 功能名称 | 优先级 | 描述 |
|--------|----------|--------|------|
| F-UI-001 | 用户登录 | P0 | 用户认证页面 |
| F-UI-002 | 仪表盘 | P0 | 首页统计展示 |
| F-UI-003 | 数据列表 | P1 | 表格展示数据 |

### 2.2 后端API

| API-ID | 方法 | 路径 | 功能 |
|--------|------|------|------|
| A-API-001 | POST | /api/auth/login | 用户登录 |
| A-API-002 | GET | /api/dashboard | 获取仪表盘数据 |

### 2.3 数据存储

| 数据ID | 表名 | 说明 |
|--------|------|------|
| D-TB-001 | users | 用户表 |
| D-TB-002 | orders | 订单表 |

## 3. 非功能需求

## 4. 验收标准
```

---

## 4. 设计文档模板

### 4.1 DETAIL_v1.0.md 结构

```markdown
# [项目名称] 详细设计

## 1. 系统架构

### 1.1 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | React 18 + TypeScript |
| 后端 | Java Spring Boot 3 |
| 数据库 | PostgreSQL 15 |
| 部署 | Docker + Nginx |

### 1.2 架构图

```
[前端] <--HTTP--> [后端] <--JDBC--> [数据库]
```

## 2. 数据库设计

### 2.1 ER图

### 2.2 表结构

```sql
-- 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(200) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
```

## 3. API 设计

### 3.1 认证模块

#### POST /api/auth/login

**请求**:
```json
{
    "username": "admin",
    "password": "123456"
}
```

**响应**:
```json
{
    "code": 200,
    "data": {
        "token": "xxx",
        "user": {
            "id": 1,
            "username": "admin"
        }
    }
}
```

## 4. 前端设计

### 4.1 页面结构

### 4.2 组件设计

## 5. 测试用例
```

---

## 5. 项目状态管理

### 5.1 project_state.yaml

```yaml
v1.0:
  requirements:
    status: APPROVED
    agent1_signoff: true
    agent1_signoff_at: '2026-02-14T10:00:00'
  design:
    status: APPROVED
    agent1_signoff: true
    agent2_signoff: true
  development:
    status: in_progress
    started_at: '2026-02-14T10:00:00'
    frontend:
      status: in_progress
      coverage: 0%
    backend:
      status: pending
      coverage: 0%
  testing:
    status: pending
    unit_tests: 0 passed
    e2e_tests: 0 passed
  deployment:
    status: pending
```

### 5.2 agent_adhoc_todos.yaml

```yaml
todos:
- id: TODO-101
  content: "前端：实现用户登录页面"
  status: pending
  priority: P0
  agent_id: frontend
  created_at: '2026-02-14T10:00:00'

- id: TODO-102
  content: "后端：实现用户认证API"
  status: pending
  priority: P0
  agent_id: backend
  created_at: '2026-02-14T10:00:00'

- id: TODO-103
  content: "数据库：创建用户表和订单表"
  status: pending
  priority: P0
  agent_id: backend
  created_at: '2026-02-14T10:00:00'

total: 3
```

---

## 6. 开发任务跟踪

### 6.1 前端任务 (Agent 2 / Frontend Dev)

```bash
# 初始化前端项目
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install axios react-router-dom antd

# 前端开发任务
oc-collab todowrite --content "前端：实现用户登录页面" --priority P0
oc-collab todowrite --content "前端：实现仪表盘页面" --priority P0
oc-collab todowrite --content "前端：实现数据列表页面" --priority P1
oc-collab todowrite --content "前端：编写组件单元测试" --priority P1
```

### 6.2 后端任务 (Agent 2 / Backend Dev)

```bash
# 初始化后端项目
# Java Spring Boot
spring init -d web,data-jpa,postgresql,security backend

# 或 Python FastAPI
pip install fastapi uvicorn sqlalchemy alembic

# 后端开发任务
oc-collab todowrite --content "后端：实现用户认证API" --priority P0
oc-collab todowrite --content "后端：实现仪表盘API" --priority P0
oc-collab todowrite --content "后端：实现数据CRUD API" --priority P1
oc-collab todowrite --content "后端：编写单元测试" --priority P1
```

### 6.3 数据库任务

```bash
oc-collab todowrite --content "数据库：设计并创建users表" --priority P0
oc-collab todowrite --content "数据库：设计并创建orders表" --priority P0
oc-collab todowrite --content "数据库：编写初始化脚本" --priority P1
```

---

## 7. 测试规范

### 7.1 前端测试 (Jest + React Testing Library)

```javascript
// frontend/src/api/__tests__/auth.test.ts
describe('Auth API', () => {
    it('should login successfully', async () => {
        const response = await authApi.login({
            username: 'admin',
            password: '123456'
        });
        expect(response.data.code).toBe(200);
        expect(response.data.data.token).toBeDefined();
    });
});
```

### 7.2 后端测试 (JUnit / pytest)

```java
// backend/src/test/java/com/example/AuthControllerTest.java
@SpringBootTest
class AuthControllerTest {
    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void testLoginSuccess() {
        LoginRequest request = new LoginRequest("admin", "123456");
        ResponseEntity<ApiResponse> response = restTemplate.postForEntity(
            "/api/auth/login", request, ApiResponse.class);
        assertEquals(200, response.getStatusCode().value());
    }
}
```

### 7.3 E2E 测试 (Cypress)

```javascript
// frontend/cypress/e2e/login.cy.js
describe('Login Flow', () => {
    it('should login successfully', () => {
        cy.visit('/login');
        cy.get('[data-testid=username]').type('admin');
        cy.get('[data-testid=password]').type('123456');
        cy.get('[data-testid=submit]').click();
        cy.url().should('include', '/dashboard');
    });
});
```

---

## 8. CI/CD 流水线

### 8.1 GitHub Actions 示例

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main, develop]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install & Test
        run: |
          cd frontend
          npm ci
          npm test
      - name: Build
        run: npm run build

  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v3
      - name: Setup Java
        uses: actions/setup-java@v3
        with:
          java-version: '17'
      - name: Test & Build
        run: |
          cd backend
          ./mvnw test
          ./mvnw package -DskipTests
```

---

## 9. 快速开始模板

### 9.1 创建新项目

```bash
# 1. 创建项目目录
mkdir my-project && cd my-project

# 2. 初始化 oc-collab 结构
mkdir -p oc-collab/{skills,docs/{01-requirements,02-design,03-test},state}

# 3. 复制 oc-collab 模板文件
cp /path/to/oc-collab/AGENTS.md oc-collab/
cp /path/to/oc-collab/skills/* oc-collab/skills/

# 4. 初始化前端
npm create vite@latest frontend -- --template react-ts

# 5. 初始化后端
spring init -d web,data-jpa,postgresql backend
# 或
fastapi init backend

# 6. 创建数据库
createdb my_project
psql -d my_project -f database/schema.sql
```

### 9.2 快速开发流程

```bash
# Day 1: 需求
oc-collab todowrite --content "编写需求文档" --priority P0

# Day 2-3: 设计
oc-collab todowrite --content "评审设计文档" --priority P0

# Day 4-10: 开发
oc-collab todowrite --content "前端：实现所有页面" --priority P0
oc-collab todowrite --content "后端：实现所有API" --priority P0
oc-collab todowrite --content "数据库：初始化数据" --priority P0

# Day 11-12: 测试
oc-collab todowrite --content "编写并运行测试" --priority P0

# Day 13: 部署
oc-collab todowrite --content "部署到生产环境" --priority P0
```

---

## 10. 检查清单

### Agent 1 (产品)

- [ ] 编写需求分析文档
- [ ] 设计API接口
- [ ] 设计数据库Schema
- [ ] 评审设计文档
- [ ] 验收测试

### Agent 2 (开发)

- [ ] 搭建前端工程
- [ ] 搭建后端工程
- [ ] 设计数据库
- [ ] 实现前端页面
- [ ] 实现后端API
- [ ] 编写单元测试 (覆盖率≥80%)
- [ ] 编写E2E测试
- [ ] 部署上线

---

## 11. 模板文件下载

### 必备文件

| 文件 | 位置 | 说明 |
|------|------|------|
| AGENTS.md | oc-collab/ | Agent分工规则 |
| ANALYSIS_template.md | oc-collab/docs/01-requirements/ | 需求模板 |
| DETAIL_template.md | oc-collab/docs/02-design/ | 设计模板 |
| project_state.yaml | oc-collab/state/ | 项目状态 |
| agent_adhoc_todos.yaml | oc-collab/state/ | 待办管理 |

---

**维护者**: Agent 1 + Agent 2
**版本**: v1.0.0
**更新日期**: 2026-02-14
