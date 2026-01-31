# {{ project_name }} - Bug报告

## 版本信息
- **版本**: {{ version }}
- **创建日期**: {{ created_at }}
- **报告人**: {{ reporter | default("Agent 1") }}
- **严重程度**: {{ severity | default("中") }}
- **状态**: {{ status | default("待修复") }}

## 1. Bug概述

### 1.1 Bug标题
{{ bug_title | default("待补充Bug标题") }}

### 1.2 Bug描述
{{ bug_description | default("待补充Bug描述") }}

### 1.3 影响范围
{{ affected_scope | default("待补充影响范围") }}

## 2. 重现步骤

### 2.1 环境信息
- **操作系统**: {{ os | default("待补充") }}
- **浏览器/版本**: {{ browser | default("待补充") }}
- **复现环境**: {{ environment | default("待补充") }}

### 2.2 复现步骤
{{ reproduction_steps | default("1. 待补充\n2. 待补充\n3. 待补充") }}

### 2.3 预期结果
{{ expected_result | default("待补充预期结果") }}

### 2.4 实际结果
{{ actual_result | default("待补充实际结果") }}

## 3. 截图/日志

### 3.1 截图
{% if screenshot_url %}
![Bug截图]({{ screenshot_url }})
{% else %}
待添加截图
{% endif %}

### 3.2 错误日志
```
{{ error_log | default("待添加错误日志") }}
```

## 4. 分析结果

### 4.1 根因分析
{{ root_cause | default("待分析") }}

### 4.2 修复建议
{{ fix_suggestion | default("待制定") }}

### 4.3 修复优先级
{{ fix_priority | default("待定") }}

## 5. 修复记录

### 5.1 修复人
{{ fixer | default("") }}

### 5.2 修复日期
{{ fix_date | default("") }}

### 5.3 修复方案
{{ fix_solution | default("待填写") }}

### 5.4 验证结果
{{ verification_result | default("待验证") }}
