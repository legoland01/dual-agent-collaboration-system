# {{ project_name }} - 设计评审

## 版本信息
- **版本**: {{ version }}
- **评审日期**: {{ review_date | default(created_at) }}
- **评审人**: {{ reviewer | default("Agent 1 (产品经理)") }}
- **评审状态**: {{ review_status | default("待评审") }}

## 1. 评审结论

### 1.1 总体评价
{{ overall_evaluation | default("待补充总体评价") }}

### 1.2 架构评审
{{ architecture_review | default("待评估") }}

### 1.3 完整性评审
{{ completeness_review | default("待评估") }}

## 2. 架构设计评审

### 2.1 架构合理性
{{ architecture_assessment | default("待补充") }}

### 2.2 技术选型评审
{{ tech_selection_assessment | default("待补充") }}

### 2.3 可扩展性
{{ extensibility_assessment | default("待评估") }}

## 3. 模块设计评审

### 3.1 模块划分合理性
{{ module_design_assessment | default("待补充") }}

### 3.2 模块接口评审
{{ interface_design_assessment | default("待补充") }}

## 4. 数据设计评审

### 4.1 数据模型评审
{{ data_model_assessment | default("待补充") }}

### 4.2 数据库设计评审
{{ database_design_assessment | default("待补充") }}

## 5. 接口设计评审

### 5.1 API设计评审
{{ api_design_assessment | default("待补充") }}

### 5.2 安全性评审
{{ security_assessment | default("待补充") }}

## 6. 待解决问题

| 序号 | 问题描述 | 严重程度 | 建议解决方案 |
|------|---------|:-------:|-------------|
{% for issue in pending_issues | default([], true) -%}
| {{ loop.index }} | {{ issue.description | default("待补充") }} | {{ issue.severity | default("中") }} | {{ issue.solution | default("待制定") }} |
{% endfor %}

## 7. 评审总结

### 7.1 通过项
{{ approved_items | default("待补充") }}

### 7.2 需修改项
{{ required_changes | default("待补充") }}
