# 多项目代码仓库分析报告

**日期**: 2026-02-17  
**角色**: Consultant (架构规划)

---

## 一、Gitee仓库总览 (qushen-data企业)

| 仓库 | 语言 | 状态 | 用途 |
|------|------|------|------|
| dossierai | Python | ✅ 活跃 | 卷宗系统 |
| financialcasegeneratorsystem | Python | ✅ 活跃 | 测试数据生成 |
| financial-court-file-assistant | Java | ✅ 活跃 | 卷宗后端 |
| financial-court-file-assistant-frontend | Vue/JS | ✅ 活跃 | 卷宗前端 |
| xhtools | Python | ✅ 活跃 | AI工具平台(通用) |
| wocheng-ai-service | Python | ✅ 活跃 | AI工具服务(通用) |
| xuhui_law_enforcement | Vue/JS | ✅ 活跃 | 阳光执法前端 |
| lhjczs_java_backend | Java | ⚠️ 旧版 | 久荣华后端(旧) |
| xuhui_lhjc_data | - | ❌ 空 | 模板(空) |
| mindsageqa | - | ❌ 空 | 预留(空) |
| hbtools | - | ❌ 空 | 预留(空) |
| wocheng-ai-service | Python | ✅ 活跃 | - |

---

## 二、15个需求与仓库映射

### 金融法院 (4个需求)

| 需求 | 仓库 | 状态 |
|------|------|------|
| 卷宗系统更新版上线 | dossierai + financial-court-file-assistant + financial-court-file-assistant-frontend | ✅ 已有 |
| 融资租赁纠纷案情分析功能 | dossierai (extract模块) | ✅ 已有 |
| 诉讼风险评估 | xhtools/wocheng-ai-service | ✅ 已有 |
| 重新开启代表人诉讼 | - | ❓ 待确认 |

### 上海市检察院 (4个需求)

| 需求 | 仓库 | 状态 |
|------|------|------|
| 改造组织智能化 | - | ❓ 待开发 |
| 运维智能化(log分析) | - | ❓ 待开发 |
| 视频项目进度管理 | - | ❓ 待开发 |
| GPU服务器上架 | - | ❓ 硬件 |

### 上海市检察院第三分院 (2个需求)

| 需求 | 仓库 | 状态 |
|------|------|------|
| 案件智能分析(自侦) | - | ❓ 待开发 |
| 职务犯罪软件部署 | lhjczs_java_backend | ⚠️ 旧版需迁移 |

### 掌上公服 (1个需求)

| 需求 | 仓库 | 状态 |
|------|------|------|
| 法律咨询+风险评估 | xhtools/wocheng-ai-service | ✅ 已有 |

### 上海市生态环境局 (1个需求)

| 需求 | 仓库 | 状态 |
|------|------|------|
| 环评智能审核 | - | ❓ 待开发 |

### 上海市环境科学研究院 (1个需求)

| 需求 | 仓库 | 状态 |
|------|------|------|
| 报告数据提取 | hbtools | ❌ 空 |

### 徐汇区司法局 (2个需求)

| 需求 | 仓库 | 状态 |
|------|------|------|
| 阳光执法部署 | xuhui_law_enforcement | ✅ 已有 |
| 行政复议doc | - | ❓ 待开发 |

---

## 三、缺的代码列表

### 3.1 需要新建仓库

| 项目 | 需求 | 建议仓库名 |
|------|------|------------|
| 上海市检察院 | 组织智能化 | proc_org_service |
| 上海市检察院 | 运维log分析 | proc_ops_log |
| 上海市检察院 | 视频项目管理 | proc_video |
| 上海市检察院第三分院 | 案件智能分析 | proc3_case_analysis |
| 上海市生态环境局 | 环评审核 | env_impact |
| 徐汇区司法局 | 行政复议 | xuhui_admin_doc |

### 3.2 需要迁移/清理

| 仓库 | 状态 | 建议 |
|------|------|------|
| xuhui_lhjc_data | 空 | 删除或用作数据配置 |
| mindsageqa | 空 | 删除或预留 |
| hbtools | 空 | 填充数据提取功能 |
| lhjczs_java_backend | 旧版 | 迁移到新项目 |

---

## 四、仓库与人员分工

| 人员 | 技术栈 | 仓库 | 状态 |
|------|--------|------|------|
| 李杨峰 | Python | dossierai, xhtools, wocheng-ai-service | ✅ |
| 郭汉盟 | Java | financial-court-file-assistant, lhjczs_java_backend | ✅ |
| 陈伟 | Vue/JS | financial-court-file-assistant-frontend, xuhui_law_enforcement | ✅ |
| 章秀芹 | - | financialcasegeneratorsystem | ✅ |

---

## 五、PM-Agent代码提交汇总报告设计

### 5.1 报告维度

| 维度 | 数据来源 | 说明 |
|------|----------|------|
| 每日提交数 | Gitee API | 每个仓库的commit数量 |
| 提交人员 | Gitee API | 按作者统计 |
| 提交内容 | Gitee API | 提交message摘要 |
| 仓库状态 | Gitee API | 新增/删除文件 |
| 代码行数 | Gitee API | 新增/删除行数 |

### 5.2 报告模板

```markdown
# 代码提交日报

**日期**: 2026-02-17

## 汇总

| 指标 | 今日 | 昨日 | 变化 |
|------|------|------|------|
| 总提交数 | 12 | 8 | ↑50% |
| 活跃人数 | 4 | 3 | ↑1 |
| 活跃仓库 | 6 | 5 | ↑1 |

## 详细

### 仓库: dossierai (Python)
| 作者 | 提交数 | 主要内容 |
|------|--------|----------|
| 李杨峰 | 3 | 卷宗解析优化 |

### 仓库: financial-court-file-assistant (Java)
| 作者 | 提交数 | 主要内容 |
|------|--------|----------|
| 郭汉盟 | 2 | API接口修复 |
```

### 5.3 自动化方案

1. 每日定时调用Gitee API获取所有仓库的提交
2. 按仓库/人员聚合
3. 生成Markdown报告
4. 推送到指定位置

---

## 六、下一步行动

1. **确认仓库映射** - 核对15个需求对应的仓库
2. **新建仓库** - 6个待开发需求需要新仓库
3. **迁移代码** - lhjczs_java_backend迁移
4. **清理空仓库** - xuhui_lhjc_data, mindsageqa, hbtools
5. **PM-Agent集成** - 接入Gitee API实现日报

---

**作者**: Consultant  
**日期**: 2026-02-17
