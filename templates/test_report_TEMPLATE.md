# {{ project_name }} - 测试报告

## 版本信息
- **版本**: {{ version }}
- **执行日期**: {{ execution_date | default(created_at) }}
- **执行人**: {{ executor | default("Agent 1") }}
- **测试类型**: {{ test_type | default("黑盒测试") }}

## 1. 测试概述

### 1.1 测试范围
{{ test_scope | default("待补充测试范围") }}

### 1.2 测试环境
{{ test_environment | default("待补充测试环境") }}

### 1.3 测试工具
{{ test_tools | default("待补充测试工具") }}

## 2. 测试执行摘要

### 2.1 测试用例统计
| 类别 | 数量 |
|-----|------|
| 已执行 | {{ executed_count | default(0) }} |
| 通过 | {{ passed_count | default(0) }} |
| 失败 | {{ failed_count | default(0) }} |
| 阻塞 | {{ blocked_count | default(0) }} |
| 未执行 | {{ not_executed_count | default(0) }} |

### 2.2 通过率
**通过率**: {{ pass_rate | default("0%") }}

### 2.3 测试结论
{{ test_conclusion | default("待补充测试结论") }}

## 3. 测试详情

### 3.1 通过的测试用例
{% for tc in passed_tests | default([], true) -%}
- {{ tc.id | default("用例" + loop.index|string) }}: {{ tc.name | default("待补充") }}
{% else %}
无通过的测试用例
{% endfor %}

### 3.2 失败的测试用例
{% for tc in failed_tests | default([], true) -%}
| {{ tc.id | default("用例" + loop.index|string) }} | {{ tc.name | default("待补充") }} | {{ tc.failure_reason | default("待补充") }} |
{% else %}
无失败的测试用例
{% endfor %}

### 3.3 阻塞的测试用例
{% for tc in blocked_tests | default([], true) -%}
- {{ tc.id | default("用例" + loop.index|string) }}: {{ tc.block_reason | default("待补充") }}
{% else %}
无阻塞的测试用例
{% endfor %}

## 4. 缺陷统计

### 4.1 新增缺陷
| 缺陷ID | 严重程度 | 描述 | 状态 |
|-------|:-------:|------|------|
{% for bug in new_bugs | default([], true) -%}
| {{ bug.id | default("BUG-" + loop.index|string) }} | {{ bug.severity | default("中") }} | {{ bug.description | default("待补充") }} | {{ bug.status | default("待修复") }} |
{% endfor %}

### 4.2 已修复缺陷
{% for bug in fixed_bugs | default([], true) -%}
- {{ bug.id | default("BUG-" + loop.index|string) }}: {{ bug.description | default("待补充") }}
{% else %}
无已修复的缺陷
{% endfor %}

## 5. 风险与建议

### 5.1 识别的风险
{{ identified_risks | default("待补充") }}

### 5.2 改进建议
{{ improvement_suggestions | default("待补充") }}

## 6. 附件

### 6.1 测试日志
{% if test_log_attachment %}
[测试日志]({{ test_log_attachment }})
{% else %}
待添加测试日志
{% endif %}

### 6.2 截图
{% if screenshot_attachment %}
[截图]({{ screenshot_attachment }})
{% else %}
待添加截图
{% endif %}
