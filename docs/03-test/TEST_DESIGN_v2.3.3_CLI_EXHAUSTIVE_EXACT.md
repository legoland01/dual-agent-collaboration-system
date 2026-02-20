# oc-collab CLI穷尽式E2E测试用例精确统计

**生成日期**: 2026-02-20  
**目标**: 精确到个位数的统计

---

## 一、命令组详细统计

### 1.1 todo命令组 (10个子命令)

| 子命令 | 选项 | 选项值 | 组合数 | 用例数 |
|--------|------|--------|--------|--------|
| todo ack | TODO_ID(必填) | - | 1 | 1 |
| todo cleanup | - | - | 1 | 1 |
| todo clear | - | - | 1 | 1 |
| todo complete | TODO_ID(必填) | - | 1 | 1 |
| todo delete | TODO_ID(必填) | - | 1 | 1 |
| todo list | --unread T/F | 2 | | |
| | --agent 1/2/无 | 3 | | |
| | --priority high/medium/low/无 | 4 | | |
| | --source BUG/REQUIREMENT/FEEDBACK/MANUAL/无 | 5 | | |
| | --json T/F | 2 | 2×3×4×5×2=120 | 120 |
| todo mark-all-read | - | - | 1 | 1 |
| todo mark-read | TODO_ID(必填) | - | 1 | 1 |
| todo show | TODO_ID(必填) | --json T/F | 2 | 2 |
| todo stats | - | - | 1 | 1 |

**todo小计**: 1+1+1+1+1+120+1+1+2+1 = **130用例**

---

### 1.2 todowrite命令

| 选项 | 必填 | 选项值 | 组合数 |
|------|------|--------|--------|
| --content | 是 | 文本 | 1 |
| --to/--receiver/--agent | 是 | 1,2,... | 1 |
| --priority | 否 | high/medium/low/无 | 4 |
| -s/--source | 否 | BUG/REQUIREMENT/FEEDBACK/MANUAL/无 | 5 |
| --type | 否 | REQUIREMENT/BUG_FIX/MANUAL/无 | 4 |
| --test-mode | 否 | T/F | 2 |

**todowrite组合数**: 4×5×4×2 = **160用例**

---

### 1.3 todoedit命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| TODO_ID | 是 | - |
| --content | 否 | 文本 |
| --status | 否 | pending/in_progress/completed/cancelled |
| --priority | 否 | high/medium/low |

**todoedit组合数**: 2×4×4 = **32用例**

---

### 1.4 switch命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| AGENT_ID | 是 | 1,2 |
| -w/--welcome/--no-welcome | 否 | 2 |

**switch组合数**: 2×2 = **4用例**

---

### 1.5 signoff命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| requirements/design/test | 是 | 3 |
| -m/--comment | 否 | 文本 |
| -r/--reject | 否 | 文本 |
| -s/--sync T/F | 否 | 2 |

**signoff组合数**: 3×2×2 = **12用例**

---

### 1.6 signoffs命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -l/--list | 否 | 1 |
| -i/--id | 否 | 文本 |

**signoffs组合数**: 2+1 = **3用例**

---

### 1.7 status命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| (无) | - | 1 |

**status用例数**: **1用例**

---

### 1.8 history命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -n/--limit | 否 | 整数 |

**history用例数**: **2用例** (无参数 + 有参数)

---

### 1.9 advance命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -p/--phase | 否 | 文本 |
| -f/--force | 否 | 1 |
| -c/--check | 否 | 1 |
| -s/--sync/--no-sync | 否 | 2 |

**advance组合数**: 2×2×2×2 = **16用例**

---

### 1.10 review命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| requirements/design/test | 是 | 3 |
| -f/--file | 否 | 文本 |
| --new | 否 | 1 |
| -l/--list | 否 | 1 |

**review组合数**: 3×2×2×2 = **24用例**

---

### 1.11 signoffs命令 (查看签署记录)

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -l/--list | 否 | 1 |
| -i/--id | 否 | 文本 |

**signoffs用例数**: **3用例**

---

### 1.12 rules命令 (2个子命令)

| 子命令 | 选项 | 组合数 |
|--------|------|--------|
| rules init | - | 1 |
| rules status | - | 1 |

**rules小计**: **2用例**

---

### 1.13 push命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -m/--message | 否 | 文本 |
| -r/--retry/--no-retry | 否 | 2 |
| -n/--max-retries | 否 | 整数 |
| -i/--interval | 否 | 整数 |
| --no-backoff | 否 | 1 |

**push组合数**: 2×2 = **4用例** (关键选项组合)

---

### 1.14 sync命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -r/--retry/--no-retry | 否 | 2 |
| -n/--max-retries | 否 | 整数 |
| -i/--interval | 否 | 整数 |
| --no-backoff | 否 | 1 |

**sync组合数**: 2×2 = **4用例**

---

### 1.15 sync-all命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -m/--message | 否 | 文本 |

**sync-all用例数**: **2用例**

---

### 1.16 work命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -e/--execute | 否 | 1 |

**work用例数**: **2用例**

---

### 1.17 workflow命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| -c/--check | 否 | 1 |
| -s/--suggest | 否 | 1 |

**workflow组合数**: 2+1 = **3用例**

---

### 1.18 init命令

| 选项 | 必填 | 选项值 |
|------|------|--------|
| PROJECT_NAME | 是 | 文本 |
| -t/--type | 否 | 4 |
| -f/--force/--no-force | 否 | 2 |
| --no-git | 否 | 1 |

**init组合数**: 4×2 = **8用例**

---

### 1.19 remote命令 (3个子命令)

| 子命令 | 选项 | 组合数 |
|--------|------|--------|
| remote add | NAME, URL | 1 |
| remote list | - | 1 |
| remote push-all | - | 1 |

**remote小计**: **3用例**

---

### 1.20 git命令 (4个子命令/参数)

| 子命令 | 组合数 |
|--------|--------|
| git status | 1 |
| git sync | 1 |
| git sync-state | 1 |
| git warn | 1 |

**git小计**: **4用例**

---

### 1.21 owner命令 (2个子命令)

| 子命令 | 组合数 |
|--------|--------|
| owner check | 1 |
| owner status | 1 |

**owner小计**: **2用例**

---

### 1.22 agent命令 (5个子命令)

| 子命令 | 选项 | 组合数 |
|--------|------|--------|
| agent list | - | 1 |
| agent register | --id, --role | 1 |
| agent unregister | agent_id | 1 |
| agent auto-register | - | 1 |
| agent listen | --foreground T/F | 2 |

**agent小计**: 1+1+1+1+2 = **6用例**

---

### 1.23 skill命令 (12个子命令)

| 子命令 | 组合数 |
|--------|--------|
| skill list | 1 |
| skill search | 1 |
| skill query | 1 |
| skill check | 1 |
| skill status | 1 |
| skill init | 1 |
| skill index | 1 |
| skill verify | 1 |
| skill coverage | 1 |
| skill test | 1 |
| skill slice | 1 |
| skill enforce | 1 |

**skill小计**: **12用例**

---

### 1.24 skill-check命令 (3个子命令)

| 子命令 | 组合数 |
|--------|--------|
| skill-check check | 1 |
| skill-check status | 1 |
| skill-check verify | 1 |

**skill-check小计**: **3用例**

---

### 1.25 config命令 (5个子命令)

| 子命令 | 选项 | 组合数 |
|--------|------|--------|
| config list | - | 1 |
| config get | key | 1 |
| config set | key value | 1 |
| config delete | key | 1 |
| config reset | --force T/F | 2 |

**config小计**: 1+1+1+1+2 = **6用例**

---

### 1.26 state命令 (6个子命令)

| 子数 |
|--------|--------命令 | 组合|
| state init | 1 |
| state start | 1 |
| state stop | 1 |
| state status | 1 |
| state queue | 1 |
| state mark-read | 1 |

**state小计**: **6用例**

---

### 1.27 notify命令 (5个子命令)

| 子命令 | 选项 | 组合数 |
|--------|------|--------|
| notify enable | - | 1 |
| notify disable | - | 1 |
| notify status | - | 1 |
| notify test | - | 1 |
| notify reply | - | 1 |

**notify小计**: **5用例**

---

### 1.28 webhook命令 (4个子命令)

| 子命令 | 组合数 |
|--------|--------|
| webhook init | 1 |
| webhook start | 1 |
| webhook stop | 1 |
| webhook status | 1 |

**webhook小计**: **4用例**

---

### 1.29 deploy命令 (3个子命令)

| 子命令 | 组合数 |
|--------|--------|
| deploy full | 1 |
| deploy sync-docs | 1 |
| deploy check-docs | 1 |

**deploy小计**: **3用例**

---

### 1.30 requirements命令 (3个子命令)

| 子命令 | 组合数 |
|--------|--------|
| requirements list | 1 |
| requirements map | 1 |
| requirements coverage | 1 |

**requirements小计**: **3用例**

---

### 1.31 bug命令 (3个子命令)

| 子命令 | 选项 | 组合数 |
|--------|------|--------|
| bug list | --unlinked | 2 |
| bug link | - | 1 |
| bug suggest | - | 1 |

**bug小计**: **4用例**

---

### 1.32 compliance命令 (5个子命令)

| 子命令 | 组合数 |
|--------|--------|
| compliance check | 1 |
| compliance report | 1 |
| compliance results | 1 |
| compliance status | 1 |
| compliance violations | 1 |

**compliance小计**: **5用例**

---

### 1.33 migrate命令 (5个子命令)

| 子命令 | 组合数 |
|--------|--------|
| migrate list-backups | 1 |
| migrate preview | 1 |
| migrate rollback | 1 |
| migrate status | 1 |
| migrate to-sqlite | 1 |

**migrate小计**: **5用例**

---

### 1.34 project命令 (5个子命令)

| 子命令 | 选项 | 组合数 |
|--------|------|--------|
| project update | -t, -v, --cases, --passed, -b | 3×3×2×2×2=72 |
| project set-phase | --phase | 1 |
| project status | --json, --internal | 4 |
| project complete | - | 1 |
| project info | - | 1 |

**project小计**: 72+1+4+1+1 = **79用例**

---

### 1.35 docs命令 (3个子命令)

| 子命令 | 选项 | 组合数 |
|--------|------|--------|
| docs check | -m, --auto/--no-auto | 2×2=4 |
| docs preview | -m, --auto/--no-auto | 4 |
| docs apply | -m, --auto/--no-auto | 4 |

**docs小计**: 4+4+4 = **12用例**

---

### 1.36 startup命令

| 选项 | 组合数 |
|------|--------|
| --no-confirm, --quiet | 2×2=4 |

**startup用例数**: **4用例**

---

### 1.37 startup-check命令

| 选项 | 组合数 |
|------|--------|
| --no-confirm, --quiet | 2×2=4 |

**startup-check用例数**: **4用例**

---

### 1.38 .a命令

| 选项 | 组合数 |
|------|--------|
| (无选项) | 1 |

**.a用例数**: **1用例**

---

## 二、总计

| 命令组 | 用例数 |
|--------|--------|
| todo | 130 |
| todowrite | 160 |
| todoedit | 32 |
| switch | 4 |
| signoff | 12 |
| signoffs | 3 |
| status | 1 |
| history | 2 |
| advance | 16 |
| review | 24 |
| rules | 2 |
| push | 4 |
| sync | 4 |
| sync-all | 2 |
| work | 2 |
| workflow | 3 |
| init | 8 |
| remote | 3 |
| git | 4 |
| owner | 2 |
| agent | 6 |
| skill | 12 |
| skill-check | 3 |
| config | 6 |
| state | 6 |
| notify | 5 |
| webhook | 4 |
| deploy | 3 |
| requirements | 3 |
| bug | 4 |
| compliance | 5 |
| migrate | 5 |
| project | 79 |
| docs | 12 |
| startup | 4 |
| startup-check | 4 |
| .a | 1 |

**总计: 619用例**

---

## 三、补充说明

1. **项目子命令(project)组合数最多** - 因为有5个选项，每个有多个值
2. **todowrite组合数160** - 因为6个可选选项，每个有多个值
3. **部分命令选项互斥**，实际有效组合可能略少
4. **建议分批次实现**:
   - 第一批: todo/signoff/switch等核心命令 (~300用例)
   - 第二批: project/docs等重要命令 (~100用例)
   - 第三批: 其他命令 (~219用例)

---

**精确总数: 619用例**
