# 调查问卷提示词模板

**文档编号**: SURVEY-PROMPT-2026-02-001
**日期**: 2026-02-03
**作者**: Agent 1 (产品经理)
**状态**:  готов к использованию

---

## 提示词 A：oc-collab 项目的 Agent 2（独立session）

**场景**：你是 oc-collab 项目的开发负责人 Agent 2，正在独立 session 中工作。Agent 1 需要你帮忙填写一份关于 oc-collab 约束机制的调查问卷。

**提示词**（复制到 Agent 2 的会话中使用）：

```
你好 Agent 2，

我需要你帮忙填写一份调查问卷，关于 oc-collab 的约束机制设计。

【背景】
我正在撰写 MEMO-2026-02-003（oc-collab 核心设计哲学），其中讨论了"控制与分布式智能的平衡"问题。这份调查问卷是为了收集真实使用者的反馈。

【调查问卷】
请执行以下命令获取问卷：
  git pull
  cat docs/00-memos/SURVEY-2026-02-001_Constraint_Feedback.md

【答题方式】
1. 阅读问卷后，创建一个回答文件：docs/00-memos/SURVEY-2026-02-001_Agent2_Response.md
2. 按照问卷中的问题格式填写你的回答
3. 提交并推送到远程：
   git add docs/00-memos/SURVEY-2026-02-001_Agent2_Response.md
   git commit -m "docs: Agent 2 survey response - SURVEY-2026-02-001"
   git push

【答题指南】
- Q1-Q2：选择你认同的选项，并说明理由
- Q3：评估 oc-collab 对你的约束程度
- Q4：分享你的实际使用体验
- Q5：任何额外的想法和建议

【预计耗时】20-30 分钟

你的反馈对 oc-collab 的设计非常重要！谢谢。
```

---

## 提示词 B：Financial Case Generator System 项目的 Agent

**场景**：Financial Case Generator System 项目使用 oc-collab v2.1.0 进行开发，但可能没有严格遵循所有流程。Agent 需要根据实际使用体验填写调查问卷。

**提示词**（复制到 Financial 项目 Agent 的会话中使用）：

```
你好，

我需要你帮忙填写一份关于 oc-collab 使用体验的调查问卷。

【背景】
我正在分析 oc-collab 在实际项目中的应用效果。Financial Case Generator System 是 oc-collab 的一个实际应用案例，你的反馈对我非常重要。

【重要说明】
- 请根据你的实际使用体验回答，不需要假设
- 如果某些功能没有用过，可以说明"没有使用过"
- 回答没有对错之分，真实反馈就是最好的答案

【获取问卷】
请执行以下命令：
  git pull
  cat docs/00-memos/SURVEY-2026-02-001_Constraint_Feedback.md

【答题方式】
1. 阅读问卷后，创建回答文件（文件名请用项目的标识）：
   例如：docs/00-memos/SURVEY-2026-02-001_Financial_Response.md
2. 按照问卷格式填写你的回答
3. 提交并推送：
   git add docs/00-memos/SURVEY-2026-02-001_*_Response.md
   git commit -m "docs: Survey response - SURVEY-2026-02-001"
   git push

【特别问题】（Financial 项目特有）
在 Q4 中，请特别关注：
- 你们在项目中实际使用了 oc-collab 的哪些功能？
- 哪些功能帮助最大？
- 哪些功能没有使用，为什么？

【预计耗时】20-30 分钟

感谢你的反馈！这将帮助我改进 oc-collab 的设计。
```

---

## 提交通知模板

### 如果使用 Git 通知

**Agent 2 的通知**：

```
## @Agent 2 - 调查问卷请求

Agent 1 在主会话中提交了调查问卷，请协助填写：

**问卷位置**: docs/00-memos/SURVEY-2026-02-001_Constraint_Feedback.md
**提交流程**: docs/00-memos/SURVEY-PROTOCOL-2026-02-001.md
**截止时间**: 2026-02-03（本周内）

感谢你的帮助！
```

### 如果使用会话通知

**通用通知模板**：

```
【调查问卷请求】

你好，我需要你帮忙填写一份关于 oc-collab 约束机制的调查问卷。

【问卷内容】（复制问卷内容到会话中）

【预计耗时】20-30 分钟

【答题方式】
1. 阅读问卷
2. 给出你的选择和理由
3. （如果可以）提交到项目的 docs/00-memos/ 目录

谢谢！
```

---

## 快速操作清单

| 步骤 | 操作 | 执行人 |
|------|------|--------|
| 1 | 发送提示词 A 给 Agent 2 | 你 |
| 2 | Agent 2 拉取问卷并回答 | Agent 2 |
| 3 | 发送提示词 B 给 Financial Agent | 你 |
| 4 | Financial Agent 回答问卷 | Financial Agent |
| 5 | 拉取回答并分析 | Agent 1 (我) |

---

**文档版本**: v1
**创建日期**: 2026-02-03
**状态**:  готов к использованию

---

*复制提示词到对应的会话中使用。*
