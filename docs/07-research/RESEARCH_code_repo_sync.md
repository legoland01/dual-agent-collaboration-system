# 代码仓库同步清单

**日期**: 2026-02-18  
**状态**: 待同步

---

## 一、已克隆仓库

| 序号 | 项目 | 仓库 | 技术栈 | 状态 |
|------|------|------|--------|------|
| 1 | 金融法院-数字赋能金融审判子系统 | financial-court-file-assistant | Java后端 | ✅ |
| 2 | 金融法院-数字赋能金融审判子系统 | financial-court-file-assistant-frontend | Vue前端 | ✅ |
| 3 | 金融法院-数字赋能金融审判子系统 | wocheng-ai-service | Python AI | ✅ |
| 4 | 金融法院-数字赋能金融审判子系统 | financial_case_generator_system | Python案例生成 | ⚠️ 手动同步中 |
| 5 | 徐汇区司法局-友法速达 | wocheng-ai-service | Python AI | ✅ 复用 |
| 6 | 徐汇区司法局-阳光执法平台 | xuhui_law_enforcement | Vue前端 | ✅ |
| 7 | 徐汇区司法局-智能检查问答 | lhjczs_java_backend | Java后端 | ✅ |
| 8 | 环科院-环科院项目 | hbtools | Python | ✅ |

---

## 二、缺失仓库

### 需要确认仓库名

| 项目 | 预期仓库 | 状态 |
|------|----------|------|
| 三分院-ZWFZ职务犯罪 | 未知 | ❌ 需确认仓库名 |

### 需要同步代码

| 项目 | 缺失部分 | 说明 |
|------|----------|------|
| 金融法院-数字赋能金融审判子系统 | Java后端 | financial-court-file-assistant 已克隆 |
| 金融法院-数字赋能金融审判子系统 | Vue前端 | financial-court-file-assistant-frontend 已克隆 |
| 金融法院-数字赋能金融审判子系统 | Python AI | wocheng-ai-service 已克隆 |
| 金融法院-数字赋能金融审判子系统 | Python案例生成 | financial_case_generator_system 手动同步中 |

---

## 三、代码完整性分析

### 3.1 金融法院 - 数字赋能金融审判子系统 ✅

| 层级 | 仓库 | 技术栈 | 状态 |
|------|------|--------|------|
| 后端 | financial-court-file-assistant | Java/Spring Boot | ✅ 完整 |
| 前端 | financial-court-file-assistant-frontend | Vue 3/TypeScript | ✅ 完整 |
| AI服务 | wocheng-ai-service | Python/FastAPI | ✅ 完整 |
| 案例生成 | financial_case_generator_system | Python | ⚠️ 同步中 |

**状态**: ✅ 基本完整

---

### 3.2 徐汇区司法局 - 友法速达

| 层级 | 仓库 | 技术栈 | 状态 |
|------|------|--------|------|
| AI服务 | wocheng-ai-service | Python/FastAPI | ✅ |
| 前端 | ? | Vue | ❌ 缺失 |

**状态**: ⚠️ 缺少前端

---

### 3.3 徐汇区司法局 - 阳光执法平台

| 层级 | 仓库 | 技术栈 | 状态 |
|------|------|--------|------|
| 前端 | xuhui_law_enforcement | Vue 3 | ✅ |
| 后端 | ? | Java/Python | ❌ 缺失 |

**状态**: ⚠️ 缺少后端API

---

### 3.4 徐汇区司法局 - 智能检查问答

| 层级 | 仓库 | 技术栈 | 状态 |
|------|------|--------|------|
| 后端 | lhjczs_java_backend | Java/Spring Boot | ✅ |
| 前端 | ? | Vue | ❌ 缺失 |

**状态**: ⚠️ 缺少前端

---

### 3.5 环科院 - 环科院项目

| 层级 | 仓库 | 技术栈 | 状态 |
|------|------|--------|------|
| 提取工具 | hbtools | Python/Flask | ✅ |
| 前端 | ? | Vue | ❌ 缺失 |
| 后端API | ? | Java/Python | ❌ 缺失 |

**状态**: ⚠️ 缺少前后端

---

### 3.6 三分院 - ZWFZ职务犯罪系统

| 层级 | 仓库 | 技术栈 | 状态 |
|------|------|--------|------|
| ? | mindsage_qa | ? | ❌ 仓库不存在 |

**状态**: ❌ 需确认仓库名

---

### 3.7 上海市检察院 - 智能队伍助手

| 层级 | 仓库 | 技术栈 | 状态 |
|------|------|--------|------|
| 后端 | ? | Java | ❌ 需翻新 |
| 前端 | ? | Vue | ❌ 需翻新 |

**状态**: ❌ 需重新开发

---

### 3.8 上海市生态环境局 - 智能环评

| 层级 | 仓库 | 技术栈 | 状态 |
|------|------|--------|------|
| ? | ? | ? | ❌ 待导入 |

**状态**: ❌ 待开发

---

## 四、同步任务清单

### 高优先级

| 任务 | 说明 | 状态 |
|------|------|------|
| 确认 ZWFZ 仓库名 | mindsage_qa 不存在 | ⏳ |
| 同步 financial_case_generator_system | 案例生成模块 | ⏳ |

### 中优先级

| 任务 | 说明 | 状态 |
|------|------|------|
| 友法速达前端 | 补充Vue前端代码 | ⏳ |
| 阳光执法后端 | 补充Java/Python后端 | ⏳ |
| 智能检查问答前端 | 补充Vue前端代码 | ⏳ |

### 低优先级

| 任务 | 说明 | 状态 |
|------|------|------|
| 环科院项目前后端 | 补充完整系统 | ⏳ |
| 智能环评项目 | 新建项目 | ⏳ |
| 智能队伍助手翻新 | 重新开发 | ⏳ |

---

## 五、仓库位置

代码仓库本地路径:

```
/Users/liuzhen/Documents/河广/ProductDevelopment/chatGPT/DigitalLaw/DigitalCourt/金融法院/法官数字助手/案卷材料样例/融资租赁/2024-沪74民初721号/OpenCodeTrial/pm-agent/data/repos/
```

---

**下一步**: 请安排人员按清单同步代码
