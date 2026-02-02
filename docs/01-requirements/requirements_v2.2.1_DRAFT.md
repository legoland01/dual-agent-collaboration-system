# 需求规格说明书：oc-collab v2.2.1

**版本**: v1
**创建日期**: 2026-02-02
**作者**: Agent 1 (产品经理)
**版本号**: 2.2.1
**状态**: DRAFT (草稿) → 待 Agent 2 评审

---

## 1. 概述

### 1.1 版本信息

| 项目 | 值 |
|------|-----|
| 当前版本 | v2.2.0 |
| 上一版本 | v2.1.0 |
| 变更类型 | 缺陷修复 + 功能增强 + 协作机制改进 |

### 1.2 变更动机

v2.2.0 发布后，发现以下问题需要修复：

| 问题来源 | 问题描述 | 严重程度 | 修复方式 |
|----------|----------|----------|----------|
| Agent 2 | 签署后不自动同步 | LOW | 功能增强 |
| Agent 1 | 签署流程不规范 | P1 | 流程改进 |
| 协作实践 | Agent 搞不清角色和职责 | P1 | Skill 自动加载 |
| 协作实践 | 不知道另一个 Agent 在做什么 | P1 | 困惑信号检测 |
| 协作实践 | 独自决策，跳过协作流程 | P1 | 职责边界提醒 |
| 协作实践 | 不知道项目的仓库配置 | P2 | 动态仓库配置 |

### 1.3 主要变更

1. **签署自动同步**: `oc-collab signoff` 添加 `--sync` 选项
2. **签署流程改进**: 规范化签署模板和检查清单
3. **双代理认知免疫系统**:
   - 困惑信号检测
   - 协作指南 Skill 自动加载
   - 职责边界提醒
   - 动态仓库配置

---

## 2. 功能需求

### 2.1 签署自动同步

**需求编号**: FR-SIGNOFF-AUTO-001

**问题背景**:
签署流程当前存在手动步骤，容易遗漏同步操作。签署后不会自动同步到远程，可能导致本地签署完成但远程没有更新的问题。

**当前流程**:
```bash
oc-collab signoff requirements  # 只更新本地 state
# 需要手动执行：
oc-collab push                  # 才推送到远程
```

**解决方案**:

#### 2.1.1 `--sync` 选项

**描述**: 在 `oc-collab signoff` 命令中添加 `--sync` 选项，签署后自动同步到远程。

**命令格式**:
```bash
oc-collab signoff requirements --sync
oc-collab signoff design --sync
oc-collab signoff milestone --name M5 --sync
```

**行为**:
1. 执行签署操作
2. 更新本地 state 文件
3. 自动执行 `oc-collab push`
4. 显示同步结果

**输出示例**:
```
✓ 签署成功: M5 里程碑
✓ 已同步到远程仓库
提交: abc1234
```

#### 2.1.2 `auto_sync` 配置

**描述**: 在配置文件中设置 `auto_sync: true`，默认行为自动同步。

**配置格式** (`config.yaml`):
```yaml
signoff:
  auto_sync: true  # 签署后自动推送到远程
```

**优先级**: `--sync` 命令行选项 > 配置文件 > 默认行为

**默认行为**: 不自动同步（需要显式指定 `--sync` 或配置 `auto_sync: true`）

### 2.2 签署流程改进

**需求编号**: FR-SIGNOFF-IMPROVE-001

**问题背景**:
评审报告中签署流程不规范，可能导致签署记录不完整。

**解决方案**:

#### 2.2.1 签署模板标准化

**描述**: 在评审报告中标准化签署模板格式。

**模板格式**:
```markdown
## 签署确认

### Agent 2 (开发负责人) 评审意见

**评审日期**: YYYY-MM-DD
**评审结果**: ✅ 同意 / ❌ 需修改

**评审意见**:
- ...

### 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | YYYY-MM-DD | ✅ 已签署 |
| 开发负责人 | Agent 2 | YYYY-MM-DD | ✅ 已签署 |

**签署后状态**: APPROVED (已批准) / PENDING (待签署)
```

#### 2.2.2 签署检查清单

**描述**: Agent 1 在完成评审后应检查：

- [ ] 报告中是否有签署确认表格
- [ ] 表格中 Agent 1 是否已签署
- [ ] 表格中 Agent 2 是否已签署
- [ ] 签署记录是否保存到 `state/signoffs/`
- [ ] 签署后状态是否为 "APPROVED"

#### 2.2.3 签署记录持久化

**描述**: 签署记录应保存到 `state/signoffs/` 目录。

**文件格式**:
```yaml
# state/signoffs/sig_M1_20260202.yaml
signoff_id: SIG-M1-20260202
milestone: M1
phase: integration_testing
signers:
  - role: 产品负责人
    agent: Agent 1
    timestamp: 2026-02-02T12:00:00
    status: approved
  - role: 开发负责人
    agent: Agent 2
    timestamp: 2026-02-02T12:05:00
    status: approved
status: APPROVED
created_at: 2026-02-02T12:00:00
```

## 3. 非功能需求

### 3.1 兼容性

| 要求 | 说明 |
|------|------|
| 向后兼容 | v2.2.0 的签署命令保持不变 |
| `--sync` 选项 | 默认不启用，需要显式指定 |

### 3.2 错误处理

| 场景 | 处理方式 |
|------|----------|
| 签署成功但同步失败 | 显示警告，签署仍有效 |
| 远程仓库冲突 | 提示用户手动解决冲突 |
| 网络错误 | 重试 3 次后报错 |

---

## 4. 验收标准

### 4.1 FR-SIGNOFF-AUTO-001 验收标准

| 标准 | 验证方式 |
|------|----------|
| `oc-collab signoff --sync` 可执行 | CLI 测试 |
| 签署后自动 push 到远程 | Git 验证 |
| 同步失败不影响签署 | 错误处理测试 |

### 4.2 FR-SIGNOFF-IMPROVE-001 验收标准

| 标准 | 验证方式 |
|------|----------|
| 签署模板标准化 | 代码审查 |
| 签署检查清单完整 | 代码审查 |
| 签署记录持久化 | 文件存在性测试 |

### 4.3 FR-DUAL-AUTO 验收标准

| FR 编号 | 验收标准 | 验证方式 |
|---------|----------|----------|
| FR-DUAL-AUTO-001 | 困惑时自动加载 Skill | 集成测试 |
| FR-DUAL-AUTO-002 | 困惑信号检测准确率 >= 80% | 测试集验证 |
| FR-DUAL-AUTO-003 | Skill 内容完整，包含动态仓库配置 | 代码审查 |
| FR-DUAL-AUTO-004 | 关键节点有职责提醒 | 功能测试 |

---

## 5. 里程碑

| 里程碑 | 内容 | 交付物 |
|--------|------|--------|
| M1 | 签署自动同步功能 | signoff.py + CLI --sync 选项 |
| M2 | 签署流程改进 | 模板 + 检查清单 + 记录持久化 |
| M3 | 双代理认知免疫系统 | Skill + 检测机制 + 提醒 |
| M4 | 测试和签署 | 测试用例 + 签署 |

---

## 6. 风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 同步冲突 | 中 | 提供清晰的冲突解决提示 |
| 用户习惯 | 低 | 默认不启用，给予适应时间 |

---

## 3. 双代理认知免疫系统

### 3.1 变更动机

在双代理协作过程中，发现以下问题需要解决：

| 问题来源 | 问题描述 | 严重程度 | 解决方案 |
|----------|----------|----------|----------|
| 协作困惑 | Agent 搞不清角色和职责 | P1 | Skill 自动加载 |
| 认知断层 | 不知道另一个 Agent 在做什么 | P1 | 困惑信号检测 |
| 职责混淆 | 独自决策，跳过协作流程 | P1 | 职责边界提醒 |
| 仓库不明 | 不知道项目的仓库配置 | P2 | 动态仓库配置 |

### 3.2 Skill 自动加载机制

**需求编号**: FR-DUAL-AUTO-001

**问题背景**:
在双代理协作过程中，Agent 有时会"忘记"另一个 Agent 的存在，导致：
- 独自决策，跳过评审流程
- 不知道文件应该放在哪里
- 不清楚下一步应该做什么

**解决方案**:

#### 3.2.1 自动加载触发

**描述**: 当检测到 Agent 困惑信号时，自动加载 oc-collab 协作指南 Skill。

**触发信号**:
| 信号 | 示例 | 置信度 |
|------|------|--------|
| 角色混淆 | "我是谁"、"你做什么"、"我的角色" | 高 |
| 不知道下一步 | "下一步"、"接下来"、"做什么" | 高 |
| 不知道文件位置 | "文件在哪"、"放哪里"、"在哪里" | 高 |
| 独自决策 | "我直接做"、"不需要对方"、"我自己决定" | 高 |

**触发流程**:
```
Agent 困惑表达
    ↓
困惑信号检测（FR-DUAL-AUTO-002）
    ↓
自动加载 Skill: oc_collab_collaboration_guide
    ↓
提供上下文
    ↓
Agent 恢复正常协作
```

#### 3.2.2 Skill 引用机制

**描述**: 在 System Prompt 中引用协作指南 Skill。

**配置格式**:
```yaml
system_prompt:
  skill_references:
    - "oc_collab_collaboration_guide"  # 当检测到协作困惑时自动加载
```

### 3.3 困惑信号检测

**需求编号**: FR-DUAL-AUTO-002

**描述**: 实现困惑信号检测机制，识别 Agent 的协作困惑。

**检测方式**:
| 检测方式 | 说明 |
|----------|------|
| 关键词检测 | "我是谁"、"怎么做"、"文件在哪" |
| 行为分析 | 跳过签署、独自决策 |
| 上下文推断 | 从对话内容推断困惑 |

**检测实现**:
```python
COLLABORATION_CONFUSION_SIGNALS = {
    "role_confusion": ["我是谁", "你做什么", "我的角色"],
    "next_step_confusion": ["下一步", "接下来", "做什么"],
    "location_confusion": ["文件在哪", "放哪里", "在哪里"],
    "solo_decision": ["我直接做", "不需要对方", "我自己决定"]
}

def detect_confusion(text: str) -> Dict[str, float]:
    """检测协作困惑信号，返回置信度"""
```

### 3.4 协作指南 Skill 内容

**需求编号**: FR-DUAL-AUTO-003

**描述**: 创建 oc_collab_collaboration_guide Skill，包含完整的协作指南内容。

**Skill 结构**:
```
skills/
└── oc_collab_collaboration_guide/
    ├── skill.yaml          # Skill 元数据
    ├── skill.py            # Skill 主逻辑
    └── content.md          # 协作指南内容
```

**协作指南内容大纲**:
```markdown
# oc-collab 协作指南

## 1. 当前协作状态
- Agent 角色识别（Agent 1 / Agent 2）
- 当前项目阶段
- 待完成任务

## 2. 双代理职责边界
- Agent 1（产品经理）职责
  - 创建需求文档
  - 创建 RFC
  - 评审并签署
- Agent 2（开发）职责
  - 评审需求和技术方案
  - 实现功能
  - 编写测试
  - 评审并签署

## 3. 协作规则
- 创建者 ≠ 评审者（必须由另一方评审）
- 双方签署后才能进入下一阶段
- 通过文件系统（docs/, state/）协作

## 4. 协作流程
### RFC 协作流程
1. Agent 1 创建 RFC → 写入 docs/
2. git push 到远端
3. Agent 2 git pull → 读取 docs/ → 发现 RFC
4. Agent 2 评审并签署 → git push 到远端
5. Agent 1 git pull → 读取签署状态 → 评审并签署 → git push

## 5. 下一步推荐行动
- 根据当前阶段推荐具体行动
- 避免越界行为

## 6. 关键文件位置
- RFC 文档：docs/*RFC*.md
- 需求文档：docs/01-requirements/
- 测试用例：tests/
- 状态文件：state/project_state.yaml

## 7. 仓库配置（动态获取）

### 当前项目仓库
- 远端 URL: {动态从 .git/config 读取}
- 分支: {当前分支}
- 最后同步: {时间}

### 同步操作
- 读取 RFC: `git pull` → `ls docs/`
- 提交评审: `git push`

### 不同项目可能使用
- GitHub / Gitee / GitLab
- 不同仓库 URL
- 不同同步频率

## 8. 签署流程
- 当前签署状态
- 如何推进签署

## 9. 常见问题
- Q: 我不知道 RFC 在哪里？
  A: RFC 保存在 docs/ 目录，使用 `ls docs/*RFC*.md` 查找
- Q: 我需要和谁协作？
  A: 你是一个双代理系统，另一个 Agent 负责评审/实现
- Q: 签署是什么意思？
  A: 双方确认后才能进入下一阶段
```

**动态内容获取**:
```python
def get_dynamic_content() -> Dict[str, str]:
    """获取动态内容"""
    return {
        "remote_url": get_remote_url(),           # 从 .git/config 读取
        "current_branch": get_current_branch(),   # 获取当前分支
        "last_sync": get_last_sync_time(),        # 获取最后同步时间
        "project_phase": get_project_phase(),     # 从 state/project_state.yaml 读取
        "signoff_status": get_signoff_status(),   # 获取签署状态
    }
```

### 3.5 职责边界提醒

**需求编号**: FR-DUAL-AUTO-004

**描述**: 在关键节点自动提醒 Agent 的职责边界。

**提醒场景**:
| 场景 | 提醒内容 |
|------|----------|
| 创建 RFC 后 | "RFC 已创建，等待 Agent 2 评审" |
| 评审时 | "你是 Agent 2，负责评审，不是创建者" |
| 签署前 | "请确认双方都已评审后再签署" |
| 独自决策时 | "这是一个需要双方确认的决策" |

**提醒配置**:
```yaml
reminders:
  - trigger: "after_rfc_creation"
    message: "RFC 已创建，等待 Agent 2 评审。请勿自行评审自己的 RFC。"
  - trigger: "before_signoff"
    message: "请确认双方都已评审后再签署。"
  - trigger: "solo_decision_detected"
    message: "这是一个需要双方确认的决策，请通知另一方。"
```

### 3.6 验收标准

| FR 编号 | 验收标准 | 验证方式 |
|---------|----------|----------|
| FR-DUAL-AUTO-001 | 困惑时自动加载 Skill | 集成测试 |
| FR-DUAL-AUTO-002 | 困惑信号检测准确率 >= 80% | 测试集验证 |
| FR-DUAL-AUTO-003 | Skill 内容完整，包含动态仓库配置 | 代码审查 |
| FR-DUAL-AUTO-004 | 关键节点有职责提醒 | 功能测试 |

---

## 7. 相关文档

| 文档 | 说明 |
|------|------|
| `docs/bugs/BUG-20260202-001_Combined.md` | Bug 报告整合 |
| `docs/01-requirements/requirements_v2.2.0.md` | v2.2.0 需求 |
| `skills/oc_collab_collaboration_guide/` | 协作指南 Skill（待创建） |

---

## 附录: 签署确认 (待完成)

### Agent 2 (开发负责人) 评审意见

**评审日期**: 
**评审结果**: 

**评审意见**:

### 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 |  | ⏳ 待签署 |
| 开发负责人 | Agent 2 |  | ⏳ 待签署 |

**签署后状态**: DRAFT → 待签署

---

**创建人**: Agent 1
**日期**: 2026-02-02
**最后更新**: 2026-02-02
**状态**: DRAFT (草稿)
