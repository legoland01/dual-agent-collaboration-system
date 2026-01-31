# {{ project_name }} - 测试用例

## 版本信息
- **版本**: {{ version }}
- **创建日期**: {{ created_at }}
- **关联需求版本**: {{ requirements_version | default("v1") }}
- **关联设计版本**: {{ design_version | default("v1") }}

## 1. 测试概述

### 1.1 测试目标
{{ test_objective | default("验证功能实现的正确性和完整性") }}

### 1.2 测试范围
{{ test_scope | default("待补充测试范围") }}

### 1.3 测试策略
{{ test_strategy | default("待补充测试策略") }}

## 2. 测试用例

### 2.1 功能测试用例

| 用例编号 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|---------|---------|---------|---------|-------|
{% for tc in functional_tests | default([], true) -%}
| {{ tc.id | default("TC-FUNC-" + loop.index|string) }} | {{ tc.name | default("用例" + loop.index|string) }} | {{ tc.precondition | default("无") }} | {{ tc.steps | default("待补充") | replace('\n', '<br>') | safe }} | {{ tc.expected | default("待补充") | replace('\n', '<br>') | safe }} | {{ tc.priority | default("P1") }} |
{% endfor %}

### 2.2 边界测试用例

| 用例编号 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|---------|---------|---------|---------|-------|
{% for tc in boundary_tests | default([], true) -%}
| {{ tc.id | default("TC-BOUND-" + loop.index|string) }} | {{ tc.name | default("用例" + loop.index|string) }} | {{ tc.precondition | default("无") }} | {{ tc.steps | default("待补充") | replace('\n', '<br>') | safe }} | {{ tc.expected | default("待补充") | replace('\n', '<br>') | safe }} | {{ tc.priority | default("P2") }} |
{% endfor %}

### 2.3 异常测试用例

| 用例编号 | 用例名称 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
|---------|---------|---------|---------|---------|-------|
{% for tc in exception_tests | default([], true) -%}
| {{ tc.id | default("TC-EXP-" + loop.index|string) }} | {{ tc.name | default("用例" + loop.index|string) }} | {{ tc.precondition | default("无") }} | {{ tc.steps | default("待补充") | replace('\n', '<br>') | safe }} | {{ tc.expected | default("待补充") | replace('\n', '<br>') | safe }} | {{ tc.priority | default("P2") }} |
{% endfor %}

## 3. 测试数据准备

### 3.1 基础数据
{{ test_data | default("待补充测试数据") }}

### 3.2 测试环境
{{ test_environment | default("待补充测试环境") }}
