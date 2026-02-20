# v2.3.3 E2E测试设计（完整场景覆盖版）

**版本**: v2  
**创建日期**: 2026-02-19  
**作者**: Agent 1 (产品经理)  
**目标**: 39个场景100%覆盖

---

## 测试环境要求（必读）

### 沙箱测试原则

1. **数据保护原则**：测试只清理自己创建的数据
2. **沙箱数据库**：`state/todos_test.db`
3. **测试标记**：测试创建的TODO应包含"测试_"前缀

---

## 场景覆盖总览

| 阶段 | 场景数 | 覆盖数 | 覆盖状态 |
|------|--------|--------|----------|
| 需求评审 | 5 | 5 | ✅ |
| 需求签署 | 3 | 3 | ✅ |
| 概要设计 | 4 | 4 | ✅ |
| 详细设计 | 4 | 4 | ✅ |
| 任务分配 | 4 | 4 | ✅ |
| 代码开发 | 4 | 4 | ✅ |
| Bug处理 | 5 | 5 | ✅ |
| 测试执行 | 4 | 4 | ✅ |
| 测试验收 | 3 | 3 | ✅ |
| 发布 | 3 | 3 | ✅ |
| **总计** | **39** | **39** | ✅ |

---

## 第一部分：需求评审场景 (S1.1-S1.5)

### S1.1 评审通过 → 发出签署通知 → 确认签署

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S1.1-TC01 | 需求评审通过触发签署 | 1.创建需求评审TODO 2.状态变更为completed | 自动创建签署TODO | SQLite: SELECT * FROM todos WHERE source='auto_trigger' AND content LIKE '%签署%' |
| S1.1-TC02 | 签署TODO分配正确 | 查询创建的签署TODO | receiver=agent1 | SQLite: SELECT receiver FROM todos WHERE content LIKE '%签署%' |
| S1.1-TC03 | 签署通知生成 | 检查notifications表 | 新增签署通知记录 | SQLite: SELECT * FROM notifications |

### S1.2 评审要求补充 → 发出补充TODO → 确认补充内容

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S1.2-TC01 | 评审要求补充 | 评审状态=需要补充 | 自动创建补充TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%补充%' |
| S1.2-TC02 | 补充TODO包含原事项 | 查询补充TODO | metadata包含原评审ID | SQLite: SELECT metadata FROM todos |
| S1.2-TC03 | 补充完成触发再次评审 | 补充TODO状态=completed | 自动创建新评审TODO | SQLite: SELECT COUNT(*) FROM todos WHERE content LIKE '%评审%' |

### S1.3 评审不通过 → 发出修正TODO → 确认修正方案

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S1.3-TC01 | 评审不通过触发修正 | 评审状态=不通过 | 创建修正TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%修正%' |
| S1.3-TC02 | 修正TODO分配正确 | 查询修正TODO | 分配给正确Agent | SQLite: SELECT receiver FROM todos WHERE content LIKE '%修正%' |
| S1.3-TC03 | 修正完成触发再次评审 | 修正TODO=completed | 触发新评审流程 | SQLite: SELECT status FROM todos WHERE content LIKE '%评审%' |

### S1.4 补充后再次评审 → 自动触发

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S1.4-TC01 | 补充后自动触发评审 | 补充TODO状态=completed | 自动创建评审TODO | SQLite: SELECT * FROM todos WHERE type='评审' |
| S1.4-TC02 | 循环计数正确 | 连续补充评审 | review_count递增 | SQLite: SELECT review_count FROM todos |
| S1.4-TC03 | 循环上限10次 | 触发10次循环 | 第10次触发预警 | SQLite/CLI: 验证预警触发 |

### S1.5 多次反复（3次+） → 预警 → 人工介入

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S1.5-TC01 | 第3次反复触发预警 | 重复评审3次 | 触发预警通知 | SQLite: SELECT * FROM notifications WHERE type='retry_warning' |
| S1.5-TC02 | 反复次数正确计数 | 3次评审不通过 | retry_count=3 | SQLite: SELECT retry_count FROM todos |
| S1.5-TC03 | 人工介入标记 | 预警产生后 | status包含人工介入标记 | SQLite: SELECT status FROM todos |

---

## 第二部分：需求签署场景 (S2.1-S2.3)

### S2.1 Agent1签署

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S2.1-TC01 | Agent1签署操作 | 执行signoff操作 | 签署记录生成 | SQLite: SELECT * FROM signoffs WHERE agent='agent1' |
| S2.1-TC02 | 签署状态更新 | 签署完成后 | 文档状态=已签署 | SQLite: SELECT status FROM documents |
| S2.1-TC03 | 签署通知 | Agent1签署后 | 通知Agent2 | SQLite: SELECT * FROM notifications |

### S2.2 Agent2签署

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S2.2-TC01 | Agent2签署操作 | 执行signoff操作 | 签署记录生成 | SQLite: SELECT * FROM signoffs WHERE agent='agent2' |
| S2.2-TC02 | 双方签署状态检查 | Agent2签署后 | 检查双方签署状态 | SQLite: SELECT COUNT(*) FROM signoffs WHERE status='signed' |
| S2.2-TC03 | 签署完成通知 | 双方签署完成 | 触发下一阶段通知 | SQLite: SELECT * FROM notifications WHERE type='phase_advanced' |

### S2.3 双方签署完成 → 自动触发下一阶段

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S2.3-TC01 | 双方签署完成检测 | 两个Agent都签署 | 状态变更为已签署 | SQLite: SELECT status FROM signoffs |
| S2.3-TC02 | 自动触发开发阶段 | 签署完成 | 自动创建开发TODO | SQLite: SELECT * FROM todos WHERE source='auto_trigger' |
| S2.3-TC03 | 阶段推进事件记录 | 阶段推进 | events表新增phase_advanced记录 | SQLite: SELECT * FROM events WHERE type='phase_advanced' |

---

## 第三部分：概要设计评审场景 (S3.1-S3.4)

### S3.1 评审通过 → 发出签署通知

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S3.1-TC01 | 概要设计评审通过 | 评审状态=通过 | 创建签署TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%签署%' |
| S3.1-TC02 | 签署通知发送 | 评审通过 | 发送签署通知 | SQLite: SELECT * FROM notifications |
| S3.1-TC03 | 签署TODO优先级 | 创建签署TODO | priority=high | SQLite: SELECT priority FROM todos WHERE content LIKE '%签署%' |

### S3.2 要求补充设计 → 发出补充TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S3.2-TC01 | 补充设计TODO | 评审要求补充 | 创建补充TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%补充%' |
| S3.2-TC02 | 补充内容关联 | 补充TODO | 关联原设计ID | SQLite: SELECT metadata FROM todos |
| S3.2-TC03 | 补充完成触发评审 | 补充TODO=completed | 触发新评审 | SQLite: SELECT * FROM todos WHERE content LIKE '%评审%' |

### S3.3 评审不通过 → 发出修正TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S3.3-TC01 | 修正TODO创建 | 评审不通过 | 创建修正TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%修正%' |
| S3.3-TC02 | 修正分配正确 | 修正TODO | 分配给Agent2 | SQLite: SELECT receiver FROM todos WHERE content LIKE '%修正%' |
| S3.3-TC03 | 修正触发再次评审 | 修正TODO=completed | 触发评审 | SQLite: SELECT status FROM todos |

### S3.4 补充后再次评审 → 自动触发

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S3.4-TC01 | 自动触发评审 | 补充完成 | 自动创建评审TODO | SQLite: SELECT * FROM todos WHERE source='auto_trigger' |
| S3.4-TC02 | 循环计数 | 补充评审 | review_count递增 | SQLite: SELECT review_count FROM todos |
| S3.4-TC03 | 循环上限 | 10次循环 | 触发预警 | SQLite: SELECT * FROM notifications |

---

## 第四部分：详细设计场景 (S4.1-S4.4)

### S4.1 详细设计完成 → 发出评审TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S4.1-TC01 | 详细设计完成后自动评审 | 设计文档状态=完成 | 创建评审TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%评审%' |
| S4.1-TC02 | 评审TODO分配 | 评审TODO | 分配给Agent1 | SQLite: SELECT receiver FROM todos |
| S4.1-TC03 | 评审事件记录 | 创建评审TODO | events表新增记录 | SQLite: SELECT * FROM events |

### S4.2 评审通过 → 发出签署通知

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S4.2-TC01 | 详细设计评审通过 | 评审状态=通过 | 创建签署TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%签署%' |
| S4.2-TC02 | 签署通知 | 评审通过 | 发送通知 | SQLite: SELECT * FROM notifications |
| S4.2-TC03 | 签署完成触发开发 | 签署完成 | 触发开发阶段 | SQLite: SELECT * FROM todos WHERE source='auto_trigger' |

### S4.3 评审要求修改 → 发出修改TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S4.3-TC01 | 修改TODO创建 | 评审要求修改 | 创建修改TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%修改%' |
| S4.3-TC02 | 修改关联 | 修改TODO | 关联原设计 | SQLite: SELECT metadata FROM todos |
| S4.3-TC03 | 修改完成触发评审 | 修改TODO=completed | 触发新评审 | SQLite: SELECT * FROM todos |

### S4.4 多次反复 → 预警

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S4.4-TC01 | 反复预警触发 | 3次评审不通过 | 触发预警 | SQLite: SELECT * FROM notifications WHERE type='retry_warning' |
| S4.4-TC02 | 反复计数 | 评审操作 | retry_count正确 | SQLite: SELECT retry_count FROM todos |
| S4.4-TC03 | 人工介入标记 | 预警产生 | 标记人工介入 | SQLite: SELECT status FROM todos |

---

## 第五部分：任务分配场景 (S5.1-S5.4)

### S5.1 创建TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S5.1-TC01 | 自动创建TODO | 触发条件满足 | TODO创建成功 | SQLite: SELECT * FROM todos |
| S5.1-TC02 | TODO必填字段 | 创建TODO | 字段完整 | SQLite: SELECT content,receiver,priority FROM todos |
| S5.1-TC03 | TODO唯一ID | 创建多个TODO | ID唯一 | SQLite: SELECT COUNT(DISTINCT id) FROM todos |

### S5.2 TODO分配给Agent → 自动推送

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S5.2-TC01 | TODO自动分配 | 创建TODO | receiver字段正确 | SQLite: SELECT receiver FROM todos |
| S5.2-TC02 | Agent推送通知 | TODO分配 | 推送通知 | SQLite: SELECT * FROM notifications WHERE todo_id=xxx |
| S5.2-TC03 | 跨Agent分配 | Agent1创建给Agent2 | receiver=agent2 | SQLite: SELECT receiver FROM todos WHERE id=xxx |

### S5.3 TODO被拒绝 → 通知创建者

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S5.3-TC01 | TODO被拒绝 | 执行reject操作 | status=dismissed | SQLite: SELECT status FROM todos |
| S5.3-TC02 | 通知创建者 | TODO被拒绝 | 通知原创建者 | SQLite: SELECT * FROM notifications |
| S5.3-TC03 | 拒绝记录 | TODO被拒绝 | 记录reject原因 | SQLite: SELECT metadata FROM todos |

### S5.4 TODO超时未处理 → 预警

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S5.4-TC01 | 超时检测 | TODO超时 | timeout_notified=1 | SQLite: SELECT timeout_notified FROM todos |
| S5.4-TC02 | 超时预警 | 超时后 | 发送预警通知 | SQLite: SELECT * FROM notifications WHERE type='timeout_warning' |
| S5.4-03 | 超时阈值可配置 | 修改timeout配置 | 生效 | 配置文件检查 |

---

## 第六部分：代码开发场景 (S6.1-S6.4)

### S6.1 开发完成 → 触发自检

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S6.1-TC01 | 开发完成标记 | 开发TODO=completed | 触发自检 | SQLite: SELECT * FROM events |
| S6.1-TC02 | 自检事件记录 | 自检触发 | events表新增记录 | SQLite: SELECT * FROM events WHERE type='self_test' |
| S6.1-TC03 | 自检完成通知 | 自检完成 | 通知结果 | SQLite: SELECT * FROM notifications |

### S6.2 自检通过 → 自动提测

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S6.2-TC01 | 自检通过 | 自检结果=通过 | 自动创建测试TODO | SQLite: SELECT * FROM todos WHERE source='auto_trigger' |
| S6.2-TC02 | 测试TODO分配 | 创建测试TODO | 分配给Agent1 | SQLite: SELECT receiver FROM todos |
| S6.2-TC03 | 提测通知 | 创建测试TODO | 通知相关Agent | SQLite: SELECT * FROM notifications |

### S6.3 自检不通过 → 发出修复TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S6.3-TC01 | 自检失败 | 自检结果=失败 | 创建修复TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%修复%' |
| S6.3-TC02 | 修复TODO关联 | 修复TODO | 关联原开发TODO | SQLite: SELECT metadata FROM todos |
| S6.3-TC03 | 修复完成触发自检 | 修复TODO=completed | 触发新自检 | SQLite: SELECT * FROM events |

### S6.4 代码冲突 → 预警

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S6.4-TC01 | 冲突检测 | 检测到冲突 | 触发预警 | SQLite: SELECT * FROM notifications WHERE type='conflict_warning' |
| S6.4-TC02 | 冲突通知 | 冲突产生 | 通知相关开发者 | SQLite: SELECT * FROM notifications |
| S6.4-TC03 | 冲突解决记录 | 解决冲突 | 记录解决状态 | SQLite: SELECT metadata FROM todos |

---

## 第七部分：Bug处理场景 (S7.1-S7.5)

### S7.1 发现Bug → 自动创建修复TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S7.1-TC01 | Bug发现 | 检测到Bug | 自动创建修复TODO | SQLite: SELECT * FROM todos WHERE source='auto_create' |
| S7.1-TC02 | Bug TODO内容 | 创建TODO | 包含bug_id | SQLite: SELECT content FROM todos |
| S7.1-TC03 | Bug TODO分配 | 创建TODO | 分配给Agent2 | SQLite: SELECT receiver FROM todos |

### S7.2 Bug修复完成 → 自动创建验收TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S7.2-TC01 | 修复完成 | 修复TODO=completed | 自动创建验收TODO | SQLite: SELECT * FROM todos WHERE source='auto_trigger' |
| S7.2-TC02 | 验收TODO内容 | 创建验收TODO | 包含bug_id引用 | SQLite: SELECT metadata FROM todos |
| S7.2-TC03 | 验收TODO分配 | 创建TODO | 分配给Agent1 | SQLite: SELECT receiver FROM todos |

### S7.3 验收通过 → 关闭Bug

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S7.3-TC01 | 验收通过 | 验收TODO=completed | Bug状态=已关闭 | SQLite: SELECT status FROM bugs |
| S7.3-TC02 | 关闭事件记录 | Bug关闭 | events表记录 | SQLite: SELECT * FROM events |
| S7.3-TC03 | 关闭通知 | Bug关闭 | 通知创建者 | SQLite: SELECT * FROM notifications |

### S7.4 验收不通过 → 重新修复

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S7.4-TC01 | 验收不通过 | 验收结果=不通过 | 创建新修复TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%修复%' |
| S7.4-TC02 | 循环计数 | 验收不通过 | review_count递增 | SQLite: SELECT review_count FROM todos |
| S7.4-TC03 | 重新修复触发 | 修复TODO=completed | 触发新验收 | SQLite: SELECT * FROM todos |

### S7.5 Bug反复出现(3次+) → 预警

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S7.5-TC01 | 反复预警 | 3次验收不通过 | 触发预警 | SQLite: SELECT * FROM notifications WHERE type='retry_warning' |
| S7.5-TC02 | 反复计数 | 验收操作 | retry_count=3 | SQLite: SELECT retry_count FROM todos |
| S7.5-TC03 | 人工介入 | 预警产生 | 标记人工介入 | SQLite: SELECT status FROM todos |

---

## 第八部分：测试执行场景 (S8.1-S8.4)

### S8.1 测试通过 → 自动记录

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S8.1-TC01 | 测试通过记录 | 测试结果=通过 | events表记录 | SQLite: SELECT * FROM events WHERE type='test_passed' |
| S8.1-TC02 | 测试结果统计 | 测试通过 | 更新统计 | SQLite: SELECT test_passed_count FROM test_stats |
| S8.1-TC03 | 测试通过通知 | 测试通过 | 通知相关Agent | SQLite: SELECT * FROM notifications |

### S8.2 测试失败 → 自动创建Bug TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S8.2-TC01 | 测试失败创建Bug | 测试结果=失败 | 自动创建Bug TODO | SQLite: SELECT * FROM todos WHERE source='auto_create' |
| S8.2-TC02 | Bug关联测试 | Bug TODO | 关联测试用例ID | SQLite: SELECT metadata FROM todos |
| S8.2-TC03 | Bug分配 | 创建Bug TODO | 分配给Agent2 | SQLite: SELECT receiver FROM todos |

### S8.3 回归测试失败 → 预警

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S8.3-TC01 | 回归失败预警 | 回归测试失败 | 触发预警 | SQLite: SELECT * FROM notifications WHERE type='regression_warning' |
| S8.3-TC02 | 回归失败记录 | 回归失败 | 记录失败详情 | SQLite: SELECT * FROM events |
| S8.3-TC03 | 回归失败通知 | 回归失败 | 通知团队 | SQLite: SELECT * FROM notifications |

### S8.4 测试完成(全部通过) → 发出验收TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S8.4-TC01 | 全部通过触发验收 | 测试全部通过 | 创建验收TODO | SQLite: SELECT * FROM todos WHERE source='auto_trigger' |
| S8.4-TC02 | 验收TODO内容 | 创建验收TODO | 包含测试引用 | SQLite: SELECT metadata FROM todos |
| S8.4-TC03 | 验收TODO分配 | 创建TODO | 分配给Agent1 | SQLite: SELECT receiver FROM todos |

---

## 第九部分：测试验收场景 (S9.1-S9.3)

### S9.1 验收通过 → 自动进入下一阶段

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S9.1-TC01 | 验收通过 | 验收TODO=completed | 阶段推进 | SQLite: SELECT phase FROM project_state |
| S9.1-TC02 | 阶段推进事件 | 阶段变化 | events表记录 | SQLite: SELECT * FROM events WHERE type='phase_advanced' |
| S9.1-TC03 | 阶段推进通知 | 阶段变化 | 通知所有Agent | SQLite: SELECT COUNT(*) FROM notifications |

### S9.2 验收不通过 → 发出修复TODO

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S9.2-TC01 | 验收不通过 | 验收结果=不通过 | 创建修复TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%修复%' |
| S9.2-TC02 | 修复关联 | 修复TODO | 关联验收TODO | SQLite: SELECT metadata FROM todos |
| S9.2-TC03 | 修复触发验收 | 修复TODO=completed | 触发新验收 | SQLite: SELECT * FROM todos |

### S9.3 部分通过 → 列出未通过项

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S9.3-TC01 | 部分通过记录 | 验收部分通过 | 记录未通过项 | SQLite: SELECT failed_items FROM test_results |
| S9.3-TC02 | 未通过项通知 | 部分通过 | 列出未通过项 | SQLite: SELECT * FROM notifications |
| S9.3-TC03 | 未通过项处理 | 确认未通过项 | 创建对应修复TODO | SQLite: SELECT COUNT(*) FROM todos WHERE failed_item_id=xxx |

---

## 第十部分：发布场景 (S10.1-S10.3)

### S10.1 验收通过 → 准备发布

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S10.1-TC01 | 验收通过触发发布 | 验收完成 | 准备发布流程 | SQLite: SELECT status FROM deployment WHERE phase='preparing' |
| S10.1-TC02 | 发布准备TODO | 准备发布 | 创建发布TODO | SQLite: SELECT * FROM todos WHERE content LIKE '%发布%' |
| S10.1-TC03 | 版本号确认 | 发布准备 | 需要确认版本号 | SQLite: SELECT require_confirmation FROM deployment |

### S10.2 发布成功 → 自动记录

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S10.2-TC01 | 发布成功记录 | 发布完成 | 记录发布时间 | SQLite: SELECT * FROM deployments WHERE status='success' |
| S10.2-TC02 | 发布成功事件 | 发布完成 | events表记录 | SQLite: SELECT * FROM events WHERE type='deployment_success' |
| S10.2-TC03 | 发布成功通知 | 发布完成 | 通知所有Agent | SQLite: SELECT COUNT(*) FROM notifications |

### S10.3 发布失败 → 自动回滚

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| S10.3-TC01 | 发布失败检测 | 发布失败 | 状态=回滚中 | SQLite: SELECT status FROM deployment |
| S10.3-TC02 | 自动回滚 | 发布失败 | 执行回滚 | SQLite: SELECT rollback_status FROM deployment |
| S10.3-TC03 | 回滚预警 | 回滚完成 | 触发预警通知 | SQLite: SELECT * FROM notifications WHERE type='rollback_warning' |

---

## 第十一部分：F-AT-09 测试沙箱

### 测试场景说明

验证独立测试数据库 `state/todos_test.db` 的创建和使用。

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| T09-TC01 | 测试数据库创建 | 1.执行测试初始化命令 2.检查文件 | state/todos_test.db存在 | 文件检查: ls state/todos_test.db |
| T09-TC02 | 测试数据库表结构 | 1.连接测试库 2.检查表 | todos表存在 | SQLite: .tables todos_test.db |
| T09-TC03 | 切换到测试数据库 | 1.设置OC_TEST_DB=1 2.创建TODO | 使用测试库 | SQLite: SELECT * FROM todos WHERE source='test_db' |
| T09-TC04 | 测试数据隔离 | 1.在测试库创建数据 2.检查生产库 | 生产数据不受影响 | SQLite: 对比生产库数据 |
| T09-TC05 | 测试环境还原 | 1.在测试库操作 2.清理测试数据 | 测试数据删除，生产数据保留 | SQLite: 对比数据 |

---

## 第十一部分b：F-AT-09b 与Test-Agent协作

### 测试场景说明

验证oc-collab测试沙箱与Test-Agent测试平台的协作能力。

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| T09b-TC01 | 环境变量调用测试功能 | 1.设置OC_TEST_DB=1 2.执行oc-collab命令 3.验证使用测试数据库 | 使用测试数据库 | 环境变量检查+SQLite验证 |
| T09b-TC02 | Test-Agent查询项目信息 | 1.设置OC_COLLAB_INTERNAL=Test-Agent 2.执行project查询命令 | 返回项目信息 | CLI输出检查 |
| T09b-TC03 | Test-Agent无权限拒绝 | 1.不设置认证 2.执行project查询命令 | 拒绝访问 | CLI输出检查: 包含"denied"或"unauthorized" |
| T09b-TC04 | 测试数据隔离验证 | 1.Test-Agent创建测试TODO 2.查询生产数据库 | 测试数据不在生产库 | SQLite对比验证 |
| T09b-TC05 | 跨系统数据流转 | 1.Test-Agent执行测试 2.通过API查询结果 3.验证数据完整 | 数据正确流转 | SQLite验证 |

---

## 第十二部分：F-AT-10 测试数据保护

### 测试场景说明

验证测试只清理自己创建的数据，不污染其他数据。

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| T10-TC01 | 测试数据标记 | 1.创建测试TODO 2.检查source字段 | source包含测试标记 | SQLite: SELECT source FROM todos WHERE content LIKE '%测试%' |
| T10-TC02 | 选择性清理 | 1.创建测试TODO 2.执行清理命令 3.检查 | 只删除测试标记的数据 | SQLite: 验证非测试数据保留 |
| T10-TC03 | 保留其他测试数据 | 1.创建多个测试TODO 2.清理其中一个 3.检查 | 其他测试数据保留 | SQLite: 验证其他测试TODO存在 |
| T10-TC04 | 清理脚本执行 | 1.运行测试清理脚本 2.检查 | 只清理测试数据 | SQLite: 验证测试数据删除 |
| T10-TC05 | 清理配置可修改 | 1.修改清理配置 2.执行清理 3.验证 | 配置生效 | 配置文件检查 |

---

## 第十三部分：F-AT-11 跨项目信息查询

### 测试场景说明

验证跨项目查询CLI命令的可用性和正确性。

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| T11-TC01 | 查询项目状态 | 1.执行`oc-collab project <name> status --json` | 返回JSON格式项目状态 | CLI输出检查 |
| T11-TC02 | 查询项目TODO | 1.执行`oc-collab project <name> todos --json` | 返回TODO列表 | CLI输出检查 |
| T11-TC03 | 查询项目变更 | 1.执行`oc-collab project <name> changes --since=xxx --json` | 返回变更列表 | CLI输出检查 |
| T11-TC04 | 查询项目进度 | 1.执行`oc-collab project <name> progress --json` | 返回进度信息 | CLI输出检查 |
| T11-TC05 | 项目TODO状态过滤 | 1.执行`oc-collab project <name> todos --status=completed --json` | 只返回完成的TODO | CLI输出检查 |

---

## 第十四部分：F-AT-12 项目查询权限控制

### 测试场景说明

验证跨项目查询的权限控制机制。

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| T12-TC01 | 环境变量认证 | 1.设置OC_COLLAB_INTERNAL=PM-Agent 2.执行查询 | 查询成功 | CLI输出检查 |
| T12-TC02 | --internal参数认证 | 1.执行查询带--internal参数 | 查询成功 | CLI输出检查 |
| T12-TC03 | 无认证拒绝访问 | 1.不设置认证直接查询 | 拒绝访问 | CLI输出检查: 包含"denied"或"unauthorized" |
| T12-TC04 | 非白名单拒绝 | 1.设置OC_COLLAB_INTERNAL=UnknownSystem 2.查询 | 拒绝访问 | CLI输出检查 |

---

## 第十五部分：F-AT-13 公共文档查询CLI

### 测试场景说明

验证docs子命令的可用性。

| 用例ID | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|--------|----------|----------|----------|----------|
| T13-TC01 | 文档查询 | 1.执行`oc-collab docs query "keyword" --json` | 返回包含关键字的文档 | CLI输出检查 |
| T13-TC02 | 文档列表 | 1.执行`oc-collab docs list --json` | 返回文档列表 | CLI输出检查 |
| T13-TC03 | 架构查看 | 1.执行`oc-collab docs architecture --json` | 返回架构信息 | CLI输出检查 |
| T13-TC04 | 分类查询 | 1.执行`oc-collab docs list --category 01-requirements --json` | 只返回分类文档 | CLI输出检查 |
| T13-TC05 | 空结果处理 | 1.查询不存在关键字 | 返回空列表 | CLI输出检查 |

---

## 测试统计

| 阶段 | 场景数 | 用例数 |
|------|--------|--------|
| 需求评审 | 5 | 12 |
| 需求签署 | 3 | 8 |
| 概要设计 | 4 | 10 |
| 详细设计 | 4 | 10 |
| 任务分配 | 4 | 10 |
| 代码开发 | 4 | 10 |
| Bug处理 | 5 | 13 |
| 测试执行 | 4 | 10 |
| 测试验收 | 3 | 8 |
| 发布 | 3 | 8 |
| F-AT-09 测试沙箱 | - | 5 |
| F-AT-09b 与Test-Agent协作 | - | 5 |
| F-AT-10 测试数据保护 | - | 5 |
| F-AT-11 跨项目查询 | - | 5 |
| F-AT-12 权限控制 | - | 4 |
| F-AT-13 文档查询CLI | - | 5 |
| **总计** | **39** | **139** |

---

## 测试执行原则

1. **按场景顺序执行** - S1.1 到 S10.3
2. **每个场景至少一个用例** - 39个场景全部覆盖
3. **全部通过才能发布** - 134个用例必须100%通过
4. **测试环境隔离** - 使用沙箱数据库
5. **新功能单独测试** - F-AT-09~13 单独执行
