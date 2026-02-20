# 项目迁移计划

**日期**: 2026-02-18  
**优先级**: 紧急  
**版本**: v2.0

---

## 一、数据模型

### 1.1 产品 → 项目

```
产品 (Product)
│
├── 金融法院卷宗系统（基座产品）
│   └── 项目：数字赋能金融审判子系统
│
├── 掌上公服（产品）
│   └── 项目：徐汇区司法局-掌上公服
│
└── [未来] 其他产品
```

### 1.2 客户 → 项目（纯定制）

```
客户 → 项目
```

---

## 二、客户与项目汇总

### 2.1 金融法院

| 项目名称 | 类型 | 说明 | 状态 | 代码仓库 |
|----------|------|------|------|----------|
| 数字赋能金融审判子系统 | 核心/产品化 | 4个仓库，包含多个模块 | 进行中 | ✅ 4个仓库 |
| 特别代表人诉讼 | 独立定制 | 继续使用 | 进行中 | 待确认 |

**仓库**：
- financial-court-file-assistant (Java后端)
- financial-court-file-assistant-frontend (Vue前端)
- dossierai (Python卷宗AI)
- financial_case_generator_system (Python案例生成)

---

### 2.2 上海市检察院

| 项目名称 | 类型 | 说明 | 状态 | 代码仓库 |
|----------|------|------|------|----------|
| 智能队伍助手 | 定制 | 对话式人员队伍管理 | 需要翻新 | 有（老旧） |
| 智能运维助手 | 定制 | 对话式运维自动化+预警 | 等待数据汇总 | 待开发 |
| 多模态大模型 | 管理项目 | 只做项目管理，不开发 | 进行中 | 无 |

---

### 2.3 上海市检察院第三分院

| 项目名称 | 类型 | 说明 | 状态 | 代码仓库 |
|----------|------|------|------|----------|
| ZWFZ/职务犯罪系统 | 定制 | 分析嫌疑人关系数据 | 上线需改动 | 待导入 |
| 全程一体法律监督 | 独立定制 | 法律监督资料流转 | 基本不使用 | 代码保留 |
| 侦查线索分析系统 | 定制 | 数据建模系统 | 过时 | 待重构 |
| 技侦一体 | 重点 | 卷宗系统+大模型分析工具 | 未立项 | 待开发 |

**说明**：项目1和4都是为自侦部门服务，项目4是最密集开发的重点

---

### 2.4 上海市生态环境局

| 项目名称 | 类型 | 说明 | 状态 | 代码仓库 |
|----------|------|------|------|----------|
| 智能环评 | 核心 | 环评报告智能审核，第二个迭代中 | 进行中 | 待导入 |
| 环境e小二 | 独立 | RAG问答系统，部署一网通办 | 已上线 | - |

---

### 2.5 上海市环境科学研究院

| 项目名称 | 类型 | 说明 | 状态 | 代码仓库 |
|----------|------|------|------|----------|
| 环科院项目 | 智能环节目子项 | 历史环评报告数据提取 | 进行中 | 待导入 |

---

### 2.6 徐汇区司法局

| 项目名称 | 类型 | 说明 | 状态 | 代码仓库 |
|----------|------|------|------|----------|
| 数字法律服务中心/友法速达 | 定制 | 81号公众服务+三所联动 | 进行中 | 部分参与 |
| ⊂ 掌上公服 | 产品化 | 全权负责 | 进行中 | 待导入 |
| ⊂ 全球一小时 | 掌上公服子功能 | - | - | - |
| 司法智能体 | 硬件+适配 | 采购GPU服务器+Pad | 已采购 | 适配 |
| 阳光执法平台 | 定制 | 执法监督+行政复议 | 进行中 | - |
| 数字调解 | 定制 | 智能调解仪 | 部分推出 | API调用 |

---

### 2.7 江浦路街道

| 项目名称 | 类型 | 说明 | 状态 | 代码仓库 |
|----------|------|------|------|----------|
| 综治中心 | 战略跟进 | 咨询阶段 | 待定 | 待定 |

**策略**：
- 公众端：输出81号功能
- 工作人员端：基于卷宗系统智能化模块

---

## 三、JSON导入数据

### 3.1 customers.json

```json
[
  {"name": "金融法院", "keywords": "金融,法院,案件,审判,卷宗", "git_repo": "https://gitee.com/qushen-data/financial-court-file-assistant", "contact": ""},
  {"name": "上海市检察院", "keywords": "检察院,公诉,批捕", "git_repo": "", "contact": ""},
  {"name": "上海市检察院第三分院", "keywords": "三分院,检察,自侦", "git_repo": "", "contact": ""},
  {"name": "上海市生态环境局", "keywords": "环保,生态,环评", "git_repo": "", "contact": ""},
  {"name": "上海市环境科学研究院", "keywords": "环科院,研究", "git_repo": "", "contact": ""},
  {"name": "徐汇区司法局", "keywords": "司法,调解,法律服务", "git_repo": "", "contact": ""},
  {"name": "江浦路街道", "keywords": "街道,综治", "git_repo": "", "contact": ""}
]
```

### 3.2 projects.json

```json
[
  {"customer": "金融法院", "name": "数字赋能金融审判子系统", "type": "product_based", "status": "developing", "git_repo": "financial-court-file-assistant", "notes": "4个仓库，包含卷宗系统"},
  {"customer": "金融法院", "name": "特别代表人诉讼", "type": "custom", "status": "developing", "notes": ""},
  
  {"customer": "上海市检察院", "name": "智能队伍助手", "type": "custom", "status": "needs_update", "git_repo": "", "notes": "代码老旧，需要翻新"},
  {"customer": "上海市检察院", "name": "智能运维助手", "type": "custom", "status": "planning", "notes": "等待数据汇总，需oc-collab运维模块"},
  {"customer": "上海市检察院", "name": "多模态大模型", "type": "management", "status": "developing", "notes": "只做项目管理"},
  
  {"customer": "上海市检察院第三分院", "name": "ZWFZ/职务犯罪系统", "type": "custom", "status": "online", "notes": "保密系统，需改动"},
  {"customer": "上海市检察院第三分院", "name": "全程一体法律监督", "type": "custom", "status": "inactive", "notes": "代码保留"},
  {"customer": "上海市检察院第三分院", "name": "侦查线索分析系统", "type": "custom", "status": "needs_refactor", "notes": "过时，需融合卷宗系统"},
  {"customer": "上海市检察院第三分院", "name": "技侦一体", "type": "product_based", "status": "planning", "notes": "重点！数据底座+大模型分析工具"},
  
  {"customer": "上海市生态环境局", "name": "智能环评", "type": "product_based", "status": "developing", "notes": "第二个迭代，以卷宗系统为基座"},
  {"customer": "上海市生态环境局", "name": "环境e小二", "type": "custom", "status": "online", "notes": "RAG问答，不升级"},
  
  {"customer": "上海市环境科学研究院", "name": "环科院项目", "type": "custom", "status": "developing", "notes": "智能环节目子项"},
  
  {"customer": "徐汇区司法局", "name": "数字法律服务中心/友法速达", "type": "custom", "status": "developing", "notes": "部分参与"},
  {"customer": "徐汇区司法局", "name": "掌上公服", "type": "product_based", "status": "developing", "notes": "全权负责"},
  {"customer": "徐汇区司法局", "name": "司法智能体", "type": "custom", "status": "online", "notes": "硬件采购+Pad适配"},
  {"customer": "徐汇区司法局", "name": "阳光执法平台", "type": "custom", "status": "developing", "notes": "未来不延续"},
  {"customer": "徐汇区司法局", "name": "数字调解", "type": "custom", "status": "partial", "notes": "提供大模型API"},
  
  {"customer": "江浦路街道", "name": "综治中心", "type": "planning", "status": "planning", "notes": "战略跟进，待定"}
]
```

---

## 四、代码仓库汇总

### 4.1 已有仓库

| 仓库名 | 所属项目 | 状态 |
|--------|----------|------|
| financial-court-file-assistant | 金融法院 | ✅ |
| financial-court-file-assistant-frontend | 金融法院 | ✅ |
| dossierai | 金融法院 | ✅ |
| financial_case_generator_system | 金融法院 | ✅ |

### 4.2 需要导入

| 项目 | 仓库状态 | 优先级 |
|------|----------|--------|
| 智能队伍助手 | 老旧代码需翻新 | P0 |
| 智能环评 | 需导入 | P1 |
| 职务犯罪系统 | 需导入 | P1 |
| 掌上公服 | 需导入 | P1 |
| 其他 | 待定 | P2 |

---

## 五、迁移步骤

| 步骤 | 任务 | 状态 |
|------|------|------|
| 1 | PM-Agent数据库增加产品表 | ⏳ |
| 2 | 导入customers.json | ⏳ |
| 3 | 导入projects.json | ⏳ |
| 4 | 确认代码仓库导入清单 | ⏳ |
| 5 | 执行代码导入 | ⏳ |
| 6 | 验证查询 | ⏳ |

---

## 六、下一步

1. ✅ 访谈完成
2. ⏳ 确认JSON数据
3. ⏳ PM-Agent开发（客户/项目CRUD）
4. ⏳ 代码仓库整理
