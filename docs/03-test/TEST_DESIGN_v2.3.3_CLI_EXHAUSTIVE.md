# v2.3.3 CLI穷尽式E2E测试用例设计

**版本**: v1  
**创建日期**: 2026-02-20  
**作者**: Agent1 (产品经理)  
**目标**: 穷尽所有CLI指令+选项组合

---

## 一、指令与选项矩阵

### 1.1 todo命令组

#### 1.1.1 `oc-collab todo list`
| 选项 | 值 | 组合数 |
|------|-----|--------|
| --unread | true/false | 2 |
| --agent | 1/2/不填 | 3 |
| --priority | high/medium/low/不填 | 4 |
| --source | BUG/REQUIREMENT/FEEDBACK/MANUAL/不填 | 5 |
| --json | true/false | 2 |

**组合数**: 2×3×4×5×2 = 240种（但很多互斥，实际约50种有效组合）

**用例设计**: 
- 每个选项单独测试
- 选项组合测试（unread+agent, priority+source等）

#### 1.1.2 `oc-collab todo show`
| 选项 | 值 |
|------|-----|
| TODO_ID | 必填 |
| --json | true/false |

**用例数**: 2

#### 1.1.3 `oc-collab todo complete`
| 选项 | 值 |
|------|-----|
| TODO_ID | 必填 |
| --signoff | true/false |
| --test-results | JSON/不填 |

**用例数**: 2×2 = 4

#### 1.1.4 `oc-collab todo delete`
| 选项 | 值 |
|------|-----|
| TODO_ID | 必填 |

**用例数**: 1

#### 1.1.5 `oc-collab todo ack`
| 选项 | 值 |
|------|-----|
| TODO_ID | 必填 |

**用例数**: 1

#### 1.1.6 `oc-collab todo mark-read`
| 选项 | 值 |
|------|-----|
| TODO_ID | 必填 |

**用例数**: 1

#### 1.1.7 `oc-collab todo mark-all-read`
| 选项 | 值 |
|------|-----|
| (无选项) | - |

**用例数**: 1

#### 1.1.8 `oc-collab todo cleanup`
| 选项 | 值 |
|------|-----|
| (无选项) | - |

**用例数**: 1

#### 1.1.9 `oc-collab todo clear`
| 选项 | 值 |
|------|-----|
| (无选项) | - |

**用例数**: 1

#### 1.1.10 `oc-collab todo stats`
| 选项 | 值 |
|------|-----|
| (无选项) | - |

**用例数**: 1

**todo命令组总计**: ~65用例

---

### 1.2 todowrite命令

| 选项 | 值 |
|------|-----|
| --content | 必填 |
| --to | 必填 (agent1/agent2/...) |
| --priority | high/medium/low |
| --source | BUG/REQUIREMENT/FEEDBACK/MANUAL |
| --deadline | 日期时间/不填 |
| --from | agent1/agent2/... |

**用例数**: 1×1×3×4×2×3 = 72种组合
**实际有效用例**: ~20

---

### 1.3 switch命令

| 选项 | 值 |
|------|-----|
| 1 | - |
| 2 | - |

**用例数**: 2

---

### 1.4 signoff命令

| 选项 | 值 |
|------|-----|
| requirements | - |
| design | - |
| test | - |
| -m, --comment | 文本/不填 |
| -r, --reject | 文本/不填 |
| -s, --sync | true/false |

**用例数**: 3×2×2×2 = 24种组合

---

### 1.5 project命令

#### 1.5.1 `oc-collab project <name> status`
| 选项 | 值 |
|------|-----|
| --json | true/false |
| --internal | true/false |

**用例数**: 2×2 = 4

#### 1.5.2 `oc-collab project <name> todos`
| 选项 | 值 |
|------|-----|
| --status | pending/completed/不填 |
| --json | true/false |
| --internal | true/false |

**用例数**: 3×2×2 = 12

#### 1.5.3 `oc-collab project <name> changes`
| 选项 | 值 |
|------|-----|
| --since | 日期/不填 |
| --json | true/false |
| --internal | true/false |

**用例数**: 2×2×2 = 8

#### 1.5.4 `oc-collab project <name> progress`
| 选项 | 值 |
|------|-----|
| --json | true/false |
| --internal | true/false |

**用例数**: 2×2 = 4

**project命令组总计**: ~28用例

---

### 1.6 docs命令

#### 1.6.1 `oc-collab docs query`
| 选项 | 值 |
|------|-----|
| 关键字 | 必填 |
| --json | true/false |
| --category | 01-requirements/02-design/.../不填 |

**用例数**: 1×2×3 = 6

#### 1.6.2 `oc-collab docs list`
| 选项 | 值 |
|------|-----|
| --category | 分类/不填 |
| --json | true/false |

**用例数**: 3×2 = 6

#### 1.6.3 `oc-collab docs architecture`
| 选项 | 值 |
|------|-----|
| --json | true/false |

**用例数**: 1

**docs命令组总计**: ~13用例

---

### 1.7 agent命令

#### 1.7.1 `oc-collab agent list`
**用例数**: 1

#### 1.7.2 `oc-collab agent register`
| 选项 | 值 |
|------|-----|
| --id | 必填 |
| --role | PRODUCT_MANAGER/ARCHITECT/TEST_ENGINEER/CONSULTANT |

**用例数**: 1×4 = 4

#### 1.7.3 `oc-collab agent unregister`
| 选项 | 值 |
|------|-----|
| agent_id | 必填 |

**用例数**: 1

#### 1.7.4 `oc-collab agent auto-register`
**用例数**: 1

#### 1.7.5 `oc-collab agent listen`
| 选项 | 值 |
|------|-----|
| --foreground | true/false |

**用例数**: 2

**agent命令组总计**: ~9用例

---

### 1.8 skill命令

| 子命令 | 选项数 | 用例估算 |
|--------|--------|----------|
| skill list | 1 | 1 |
| skill search | 1 | 1 |
| skill query | 1 | 1 |
| skill check | 1 | 1 |
| skill status | 1 | 1 |
| skill init | 1 | 1 |
| skill index | 1 | 1 |
| skill verify | 1 | 1 |
| skill coverage | 1 | 1 |
| skill test | 1 | 1 |
| skill slice | 1 | 1 |
| skill enforce | 1 | 1 |

**skill命令组总计**: ~12用例

---

### 1.9 config命令

| 子命令 | 选项 |
|--------|------|
| config list | - |
| config get | key |
| config set | key value |
| config delete | key |
| config reset | --force |

**用例数**: ~8

---

### 1.10 其他命令

| 命令 | 用例数 |
|------|--------|
| status | 1 |
| history | 1 |
| advance | 1 |
| signoffs | 1 |
| compliance check | 1 |
| compliance status | 1 |
| compliance results | 1 |
| compliance violations | 1 |
| requirements list | 1 |
| requirements map | 1 |
| requirements coverage | 1 |
| bug list | 1 |
| bug link | 1 |
| bug suggest | 1 |
| notify enable | 1 |
| notify disable | 1 |
| notify status | 1 |
| notify test | 1 |
| webhook init | 1 |
| webhook start | 1 |
| webhook stop | 1 |
| webhook status | 1 |
| deploy full | 1 |
| deploy sync-docs | 1 |
| deploy check-docs | 1 |
| init | 1 |
| review | 1 |
| rules | 1 |
| work | 1 |
| workflow | 1 |
| push | 1 |
| sync | 1 |
| sync-all | 1 |

---

## 二、完整用例清单

由于用例数量庞大（200+），建议采用以下策略：

### 策略A: 全量测试（约200-300用例）
- 每个组合都测试
- 耗时: 10-20小时

### 策略B: 核心测试 + 扩展测试
- 核心: 每个子命令至少1个用例
- 扩展: 主要选项组合
- 数量: 80-100用例

---

## 三、建议：采用策略B

**核心测试 (50用例)**:
1. todo list (5): 基本、--unread、--json、--agent、--priority
2. todo show (1)
3. todo complete (2): 基本、--signoff
4. todo delete (1)
5. todowrite (5): 不同选项组合
6. switch (2)
7. signoff (3): requirements/design/test
8. project status (2): --json、--internal
9. project todos (2)
10. docs query (2)
11. docs list (1)
12. agent list (1)
13. agent register (2)
14. skill list (1)
15. config list (1)
16. status (1)
17. history (1)
18. advance (1)
19. 其他命令各1

**扩展测试 (50用例)**:
- 选项组合测试
- 边界情况测试
- 错误输入测试

---

**总计建议**: 80-100个核心用例 + 边缘用例 = 100-150用例

是否需要我按此方案继续编写完整的测试用例代码？
