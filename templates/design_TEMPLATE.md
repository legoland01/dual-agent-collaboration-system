# {{ project_name }} - 详细设计

## 版本信息
- **版本**: {{ version }}
- **创建日期**: {{ created_at }}
- **关联需求版本**: {{ requirements_version | default("v1") }}
- **状态**: {{ status | default("草稿") }}

## 1. 系统架构

### 1.1 整体架构
{{ architecture_overview | default("待补充系统架构概述") }}

### 1.2 技术选型
| 层级 | 技术 | 版本 | 说明 |
|-----|------|------|------|
| 前端 | {{ frontend_tech | default("待定") }} | | |
| 后端 | {{ backend_tech | default("待定") }} | | |
| 数据库 | {{ database_tech | default("待定") }} | | |
| 部署 | {{ deployment_tech | default("待定") }} | | |

### 1.3 架构图
{{ architecture_diagram | default("待添加架构图") }}

## 2. 模块设计

### 2.1 模块列表
| 模块名 | 职责 | 依赖 |
|-------|------|------|
{% for module in modules | default([], true) -%}
| {{ module.name | default("模块" + loop.index|string) }} | {{ module.responsibility | default("待补充") }} | {{ module.dependencies | default("无") }} |
{% endfor %}

### 2.2 模块详情
{% for module in modules | default([], true) -%}
#### {{ loop.index }}.{{ module.name | default("模块" + loop.index|string) }}
**职责**: {{ module.responsibility | default("待补充") }}

**接口**:
{{ module.interfaces | default("    待补充") }}

**业务流程**:
{{ module.workflow | default("    待补充") }}

{% endfor %}

## 3. 数据设计

### 3.1 数据模型
{{ data_model | default("待补充数据模型") }}

### 3.2 数据库设计
| 表名 | 字段 | 类型 | 说明 |
|-----|------|------|------|
{% for table in database_tables | default([], true) -%}
| {{ table.name | default("表" + loop.index|string) }} | | | |
{% endfor %}

### 3.3 数据流
{{ data_flow | default("待补充数据流") }}

## 4. 接口设计

### 4.1 API列表
| 接口 | 方法 | 路径 | 说明 |
|-----|------|------|------|
{% for api in apis | default([], true) -%}
| {{ api.name | default("接口" + loop.index|string) }} | {{ api.method | default("GET") }} | {{ api.path | default("/api/...") }} | {{ api.description | default("待补充") }} |
{% endfor %}

### 4.2 接口详情
{% for api in apis | default([], true) -%}
#### {{ loop.index }}.{{ api.name | default("接口" + loop.index|string) }}
**路径**: `{{ api.method | default("GET") }} {{ api.path | default("/api/...") }}`

**请求参数**:
{{ api.request_params | default("    待补充") }}

**响应示例**:
```json
{{ api.response_example | default('{}') }}
```

{% endfor %}

## 5. 安全设计

### 5.1 认证授权
{{ authentication | default("待补充认证授权设计") }}

### 5.2 数据安全
{{ data_security | default("待补充数据安全设计") }}

### 5.3 异常处理
{{ exception_handling | default("待补充异常处理设计") }}

## 6. 测试设计

### 6.1 测试策略
{{ testing_strategy | default("待补充测试策略") }}

### 6.2 测试用例
| 用例ID | 测试场景 | 预期结果 |
|-------|---------|---------|
{% for test_case in test_cases | default([], true) -%}
| {{ test_case.id | default("TC" + loop.index|string) }} | {{ test_case.scenario | default("待补充") }} | {{ test_case.expected | default("待补充") }} |
{% endfor %}

## 7. 部署设计

### 7.1 部署架构
{{ deployment_architecture | default("待补充部署架构") }}

### 7.2 部署流程
{{ deployment_process | default("待补充部署流程") }}
