# {{ project_name }} - 需求评审

## 版本信息
- **版本**: {{ version }}
- **评审日期**: {{ review_date | default(created_at) }}
- **评审人**: {{ reviewer | default("Agent 2 (开发)") }}
- **评审状态**: {{ review_status | default("待评审") }}

## 1. 评审结论

### 1.1 总体评价
{{ overall_evaluation | default("待补充总体评价") }}

### 1.2 评审结论
| 项目 | 结论 |
|-----|------|
| 技术可行性 | {{ technical_feasibility | default("待评估") }} |
| 完整性 | {{ completeness | default("待评估") }} |
| 一致性 | {{ consistency | default("待评估") }} |
| 清晰度 | {{ clarity | default("待评估") }} |

## 2. 技术可行性评估

### 2.1 技术方案评估
{{ technical_assessment | default("待补充技术方案评估") }}

### 2.2 风险识别
| 风险项 | 可能性 | 影响 | 应对措施 |
|-------|:------:|:----:|---------|
{% for risk in identified_risks | default([], true) -%}
| {{ risk.name | default("风险" + loop.index|string) }} | {{ risk.probability | default("中") }} | {{ risk.impact | default("中") }} | {{ risk.mitigation | default("待制定") }} |
{% endfor %}

### 2.3 技术依赖
{{ technical_dependencies | default("待补充技术依赖") }}

## 3. 工时估算

### 3.1 阶段工时
| 阶段 | 工时（人天） | 备注 |
|-----|:----------:|------|
| 需求分析 | {{ effort_requirements | default("待估算") }} | |
| 设计 | {{ effort_design | default("待估算") }} | |
| 开发 | {{ effort_development | default("待估算") }} | |
| 测试 | {{ effort_testing | default("待估算") }} | |
| 部署 | {{ effort_deployment | default("待估算") }} | |
| **合计** | {{ effort_total | default("待估算") }} | |

## 4. 需求质量评估

### 4.1 完整性
{{ completeness_assessment | default("待评估") }}

### 4.2 明确性
{{ clarity_assessment | default("待评估") }}

### 4.3 可测试性
{{ testability_assessment | default("待评估") }}

## 5. 待解决问题

| 序号 | 问题描述 | 严重程度 | 建议解决方案 |
|------|---------|:-------:|-------------|
{% for issue in pending_issues | default([], true) -%}
| {{ loop.index }} | {{ issue.description | default("待补充") }} | {{ issue.severity | default("中") }} | {{ issue.solution | default("待制定") }} |
{% endfor %}

## 6. 评审意见汇总

### 6.1 必须修改项
{{ must_fix_items | default("待补充必须修改项") }}

### 6.2 建议修改项
{{ should_fix_items | default("待补充建议修改项") }}

### 6.3 可选修改项
{{ could_fix_items | default("待补充可选修改项") }}

## 7. 签署确认

| 角色 | 签署人 | 签署日期 | 意见 |
|-----|-------|---------|------|
| 开发 | {{ dev_signer | default("") }} | {{ dev_sign_date | default("") }} | {{ dev_comment | default("") }} |
| 产品 | {{ pm_signer | default("") }} | {{ pm_sign_date | default("") }} | {{ pm_comment | default("") }} |
