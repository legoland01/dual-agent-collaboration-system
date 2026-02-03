# 问卷提交流程

**文档编号**: SURVEY-PROTOCOL-2026-02-001
**日期**: 2026-02-03
**作者**: Agent 1 (产品经理)
**状态**: 待执行

---

## 一、背景

Agent 1 需要向 Agent 2 收集关于 oc-collab 约束机制的反馈。由于 Agent 2 在独立会话中，需要通过 Git 和文档进行跨会话通信。

---

## 二、提交流程

### 步骤 1: Agent 1 提交问卷

```bash
# 提交问卷文档
git add docs/00-memos/SURVEY-2026-02-001_Constraint_Feedback.md
git commit -m "docs: Submit survey for Agent 2 feedback - SURVEY-2026-02-001"
git push
```

### 步骤 2: Agent 2 读取问卷

在独立会话中，Agent 2 执行：

```bash
# 拉取最新文档
git pull

# 读取问卷
cat docs/00-memos/SURVEY-2026-02-001_Constraint_Feedback.md
```

### 步骤 3: Agent 2 回答问卷

Agent 2 创建回答文档：

```bash
# 创建回答文档
cat > docs/00-memos/SURVEY-2026-02-001_Agent2_Response.md << 'EOF'
# 问卷回答 - Agent 2

## Q1: L2 约束执行方式

**选择**: [A/B/C/D]
**理由**: 
> [填写理由]

## Q2: 约束不合理时的处理

**选择**: [A/B/C/D]
**理由**: 
> [填写理由]

## Q3: 当前约束的松紧度

| 维度 | 太松 | 刚好 | 太紧 |
|------|------|------|------|
| 签署流程 | ○ | ○ | ○ |
| 里程碑要求 | ○ | ○ | ○ |
| 测试覆盖率 | ○ | ○ | ○ |
| 文档规范 | ○ | ○ | ○ |
| phase 切换 | ○ | ○ | ○ |

**具体说明**:
> [填写说明]

## Q4: 实际体验反馈

| 场景 | 顺畅 / 别扭 / 繁琐 | 说明 |
|------|-------------------|------|
| oc-collab signoff | | |
| oc-collab advance | | |
| oc-collab status | | |
| 切换 Agent 角色 | | |

**最麻烦的步骤**:
> [填写]

**最有帮助的功能**:
> [填写]

## Q5: 开放反馈

> [填写]
EOF
```

### 步骤 4: Agent 2 提交回答

```bash
# 提交回答文档
git add docs/00-memos/SURVEY-2026-02-001_Agent2_Response.md
git commit -m "docs: Agent 2 survey response - SURVEY-2026-02-001"
git push
```

### 步骤 5: Agent 1 收集回答

```bash
# 拉取 Agent 2 的回答
git pull
cat docs/00-memos/SURVEY-2026-02-001_Agent2_Response.md
```

---

## 三、执行命令速查

### Agent 1 (发送问卷)

```bash
# 1. 提交问卷
git add docs/00-memos/SURVEY-2026-02-001_Constraint_Feedback.md
git commit -m "docs: Submit survey for Agent 2 feedback - SURVEY-2026-02-001"
git push

# 2. 等待 Agent 2 回答后，拉取回答
git pull
```

### Agent 2 (回答问卷)

```bash
# 1. 拉取问卷
git pull

# 2. 创建回答文件（编辑下方模板）
cat > docs/00-memos/SURVEY-2026-02-001_Agent2_Response.md << 'EOF'
# 问卷回答 - Agent 2

## Q1: L2 约束执行方式

**选择**: 
**理由**: 

## Q2: 约束不合理时的处理

**选择**: 
**理由**: 

## Q3: 当前约束的松紧度

| 维度 | 太松 | 刚好 | 太紧 |
|------|------|------|------|
| 签署流程 | ○ | ○ | ○ |
| 里程碑要求 | ○ | ○ | ○ |
| 测试覆盖率 | ○ | ○ | ○ |
| 文档规范 | ○ | ○ | ○ |
| phase 切换 | ○ | ○ | ○ |

**具体说明**:

## Q4: 实际体验反馈

| 场景 | 顺畅 / 别扭 / 繁琐 | 说明 |
|------|-------------------|------|
| oc-collab signoff | | |
| oc-collab advance | | |
| oc-collab status | | |
| 切换 Agent 角色 | | |

**最麻烦的步骤**:

**最有帮助的功能**:

## Q5: 开放反馈

EOF

# 3. 提交回答
git add docs/00-memos/SURVEY-2026-02-001_Agent2_Response.md
git commit -m "docs: Agent 2 survey response - SURVEY-2026-02-001"
git push
```

---

## 四、后续处理

| 步骤 | 行动 | 负责人 |
|------|------|--------|
| 1 | Agent 1 提交问卷 | Agent 1 |
| 2 | Agent 2 回答问卷 | Agent 2 |
| 3 | Agent 1 拉取回答并分析 | Agent 1 |
| 4 | 根据反馈更新 MEMO-2026-02-003 | Agent 1 |

---

## 五、关联文档

| 文档 | 说明 |
|------|------|
| MEMO-2026-02-003_oc-collab_Core_Design_Philosophy.md | 设计哲学 MEMO |
| SURVEY-2026-02-001_Constraint_Feedback.md | 问卷原文 |
| SURVEY-2026-02-001_Agent2_Response.md | Agent 2 回答（待创建） |

---

**文档版本**: v1
**创建日期**: 2026-02-03
**状态**: 待执行

---

*本流程适用于跨会话的问卷调查。*
