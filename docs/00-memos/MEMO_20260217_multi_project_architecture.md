# 多项目管理体系沟通Memo

**日期**: 2026-02-17  
**参与者**: Consultant (战略规划)  
**主题**: 多项目管理体系架构讨论

---

## 一、现有资源

### 1.1 代码仓库 (Gitee qushen-data)

| 仓库 | 语言 | 说明 |
|------|------|------|
| dossierai | Python | 卷宗系统 |
| financialcasegeneratorsystem | Python | 测试数据 |
| financial-court-file-assistant | Java | 后端 |
| financial-court-file-assistant-frontend | Vue/JS | 前端 |
| xhtools | Python | AI工具平台 |
| wocheng-ai-service | Python | AI服务 |
| xuhui_law_enforcement | Vue/JS | 阳光执法 |
| lhjczs_java_backend | Java | 旧版后端 |

### 1.2 开发人员分工

| 人员 | 技术栈 | 仓库 |
|------|--------|------|
| 李杨峰 | Python | dossierai, xhtools, wocheng-ai |
| 郭汉盟 | Java | financial-court-file-assistant |
| 陈伟 | Vue/JS | financial-court-file-assistant-frontend |
| 章秀芹 | - | financialcasegeneratorsystem |

### 1.3 CODING平台项目 (7个)

| 项目 | 名称 | 仓库数 |
|------|------|--------|
| JRFY-IntJudge | 金融法院法官助手 | 4 |
| XHDoJ-2C | 徐汇司法友法速达 | 1 |
| XH-DoJ-Sun | 徐汇司法阳光执法 | 2 |
| SFY-KQH | 跨区划 | 0 |
| SFY-YTH | 一体化 | 0 |
| SFY-ZWFZ | 职务犯罪 | 0 |
| ZNHP-Full | 智能环评 | 0 |
| TXT-Ext | 文本抽取 | 1 |

---

## 二、15个需求清单

### 2.1 金融法院 (4)
- 卷宗系统更新版上线
- 融资租赁纠纷案情分析功能
- 诉讼风险评估-融资租赁板块(2C)
- 重新开启代表人诉讼

### 2.2 上海市检察院 (4)
- 改造组织智能化
- 运维智能化(log分析)
- 视频项目进度管理(2/28周会)
- GPU服务器上架

### 2.3 上海市检察院第三分院 (2)
- 案件智能分析(自侦)
- 职务犯罪软件部署

### 2.4 掌上公服 (1)
- 法律咨询+诉讼风险评估

### 2.5 上海市生态环境局 (1)
- 环评智能审核

### 2.6 上海市环境科学研究院 (1)
- 报告数据提取

### 2.7 徐汇区司法局 (2)
- 阳光执法部署
- 行政复议doc

---

## 三、架构讨论

### 3.1 分布式多Agent协作

**用户** → 掌握所有Agent分配权  
**PM-Agent** → 管理Agent资源池，自动分配  
**oc-collab** → 入组后协调Agent工作

### 3.2 Agent资源池

- 用户给每个开发人员分配Agent（如李10个：agent3-001 ~ agent3-010）
- Agent有ID、状态（idle/busy/assigned）
- 忙闲状态由PM-Agent管理

### 3.3 项目组建立流程

1. 用户创建项目组
2. 拉开发人员进组
3. 指定负责内容
4. PM-Agent自动分配空闲Agent入组
5. 入组后oc-collab接管，PM-Agent不再管理

### 3.4 Agent归属机制

- Agent绑定：开发者 + 项目 + 仓库
- 项目决定用谁的Agent
- 同一开发者可参与多个项目

---

## 四、待确认问题

### 4.1 仓库映射
- 15个需求 → 哪些仓库？ 部分待确认

### 4.2 需要新建
- 上海市检察院相关需求
- 上海市生态环境局需求
- 职务犯罪软件

### 4.3 空的仓库
- xuhui_lhjc_data
- mindsageqa
- hbtools

---

## 五、PM-Agent统计功能

每日统计维度：
- 工作进展（TODO完成数）
- 代码提交（Gitee API）
- 测试情况
- Bug情况
- Issue跟踪
- 需求满足
- 部署情况

---

## 六、下一步

1. 确认仓库与需求映射
2. 确定需要新建的仓库
3. 迁移/清理空仓库
4. 完善Agent分配机制细节
5. 设计PM-Agent统计实现

---

**日期**: 2026-02-17
