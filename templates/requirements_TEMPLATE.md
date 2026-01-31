# {{ project_name }} - 需求文档

## 版本信息
- **版本**: {{ version }}
- **创建日期**: {{ created_at }}
- **状态**: {{ status | default("草稿") }}

## 1. 项目概述

### 1.1 项目名称
{{ project_name }}

### 1.2 项目背景
{{ project_background | default("待补充项目背景") }}

### 1.3 项目目标
{{ project_goal | default("待补充项目目标") }}

## 2. 功能需求

### 2.1 功能列表
| 序号 | 功能名称 | 功能描述 | 优先级 |
|------|---------|---------|-------|
{% for feature in features | default([], true) -%}
| {{ loop.index }} | {{ feature.name | default("功能" + loop.index|string) }} | {{ feature.description | default("待补充") }} | {{ feature.priority | default("P1") }} |
{% endfor %}

### 2.2 功能详情
{% for feature in features | default([], true) -%}
#### {{ loop.index }}.{{ feature.name | default("功能" + loop.index|string) }}
- **描述**: {{ feature.description | default("待补充") }}
- **输入**: {{ feature.input | default("待补充") }}
- **输出**: {{ feature.output | default("待补充") }}
- **业务流程**:
{{ feature.business_flow | default("    待补充") }}

{% endfor %}

## 3. 非功能需求

### 3.1 性能需求
{{ performance_requirements | default("待补充性能需求") }}

### 3.2 安全需求
{{ security_requirements | default("待补充安全需求") }}

### 3.3 兼容性需求
{{ compatibility_requirements | default("待补充兼容性需求") }}

## 4. 验收标准

### 4.1 功能验收标准
{{ acceptance_criteria | default("待补充验收标准") }}

### 4.2 质量验收标准
{{ quality_criteria | default("待补充质量标准") }}

## 5. 约束条件

### 5.1 技术约束
{{ technical_constraints | default("待补充技术约束") }}

### 5.2 业务约束
{{ business_constraints | default("待补充业务约束") }}

### 5.3 时间约束
{{ time_constraints | default("待补充时间约束") }}

## 6. 假设与依赖

### 6.1 假设条件
{{ assumptions | default("待补充假设条件") }}

### 6.2 外部依赖
{{ dependencies | default("待补充外部依赖") }}

## 7. 风险管理

### 7.1 识别风险
{{ risks | default("待补充风险管理") }}

### 7.2 应对措施
{{ risk_mitigation | default("待补充应对措施") }}
