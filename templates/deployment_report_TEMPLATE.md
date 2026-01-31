# {{ project_name }} - 部署报告

## 版本信息
- **版本**: {{ version }}
- **部署日期**: {{ deployment_date | default(created_at) }}
- **部署人**: {{ deployer | default("Agent 1") }}
- **部署环境**: {{ environment | default("生产环境") }}

## 1. 部署概述

### 1.1 部署目标
{{ deployment_objective | default("完成项目部署") }}

### 1.2 部署范围
{{ deployment_scope | default("待补充部署范围") }}

### 1.3 部署类型
{{ deployment_type | default("全量部署") }}

## 2. 部署准备

### 2.1 环境检查
| 检查项 | 状态 | 备注 |
|-------|------|------|
| 服务器状态 | {{ server_status | default("正常") }} | |
| 磁盘空间 | {{ disk_status | default("充足") }} | |
| 网络连接 | {{ network_status | default("正常") }} | |
| 依赖服务 | {{ dependency_status | default("正常") }} | |

### 2.2 数据准备
{{ data_preparation | default("待补充数据准备情况") }}

### 2.3 回滚方案
{{ rollback_plan | default("待补充回滚方案") }}

## 3. 部署步骤

### 3.1 部署执行
| 步骤 | 操作 | 执行人 | 执行时间 | 状态 |
|-----|------|-------|---------|------|
{% for step in deployment_steps | default([], true) -%}
| {{ loop.index }} | {{ step.operation | default("待补充") }} | {{ step.operator | default("Agent 1") }} | {{ step.time | default("") }} | {{ step.status | default("待执行") }} |
{% endfor %}

### 3.2 关键操作记录
{{ key_operations | default("待补充关键操作记录") }}

## 4. 部署验证

### 4.1 健康检查
| 检查项 | 预期结果 | 实际结果 | 状态 |
|-------|---------|---------|------|
{% for check in health_checks | default([], true) -%}
| {{ check.item | default("检查项" + loop.index|string) }} | {{ check.expected | default("正常") }} | {{ check.actual | default("待检查") }} | {{ check.status | default("待验证") }} |
{% endfor %}

### 4.2 功能验证
{{ functional_verification | default("待补充功能验证结果") }}

### 4.3 性能验证
{{ performance_verification | default("待补充性能验证结果") }}

## 5. 部署结果

### 5.1 部署状态
**部署结果**: {{ deployment_result | default("成功") }}

### 5.2 部署耗时
**总耗时**: {{ deployment_duration | default("待统计") }}

### 5.3 问题与解决
| 问题 | 解决措施 | 状态 |
|-----|---------|------|
{% for issue in deployment_issues | default([], true) -%}
| {{ issue.description | default("待补充") }} | {{ issue.solution | default("待制定") }} | {{ issue.status | default("待解决") }} |
{% endfor %}

## 6. 后续建议

### 6.1 监控建议
{{ monitoring_suggestions | default("待补充") }}

### 6.2 维护建议
{{ maintenance_suggestions | default("待补充") }}

### 6.3 优化建议
{{ optimization_suggestions | default("待补充") }}

## 7. 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|-------|---------|------|
| 部署负责人 | {{ deployer | default("") }} | {{ deployment_date | default("") }} | {{ deployer_confirm | default("") }} |
| 项目负责人 | {{ project_leader | default("") }} | {{ leader_confirm_date | default("") }} | {{ leader_confirm | default("") }} |
