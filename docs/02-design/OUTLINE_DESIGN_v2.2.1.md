# 概要设计说明书：oc-collab v2.2.1

**版本**: v1
**创建日期**: 2026-02-07
**作者**: Agent 2 (开发负责人)
**版本号**: 2.2.1
**状态**: 概要设计 (待 Agent 1 评审)

---

## 1. 技术架构概览

### 1.1 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         oc-collab v2.2.1 系统架构                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │  Agent 1    │    │  Agent 2    │    │  其他 Agent │                  │
│  │ (产品经理)   │    │ (开发负责人) │    │  (动态添加)  │                  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                  │
│         │                  │                  │                           │
│         └──────────────────┼──────────────────┘                           │
│                            │                                              │
│                            ▼                                              │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    Git 通信协议层                              │          │
│  │  ├─ 需求文档 (requirements_*.md)                            │          │
│  │  ├─ 设计文档 (detailed_design_*.md)                         │          │
│  │  ├─ 状态文件 (project_state.yaml)                            │          │
│  │  └─ 签署记录 (state/signoffs/*.yaml)                         │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                            │                                              │
│                            ▼                                              │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    v2.2.1 新增功能模块                        │          │
│  │  ├─ SignoffSync: 签署自动同步 (M1)                          │          │
│  │  ├─ ChangeComplianceChecker: 变更合规检查 (M2)               │          │
│  │  ├─ SignoffImprover: 签署流程改进 (M3)                      │          │
│  │  ├─ ExtendedChecklistGenerator: 动态 Checklist (M4)          │          │
│  │  └─ CognitiveImmuneSystem: 认知免疫系统 (M5)                   │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                            │                                              │
│                            ▼                                              │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    核心功能模块 (v2.2.0)                       │          │
│  │  ├─ AgentManager: Agent 动态管理                             │          │
│  │  ├─ ProjectManager: 项目管理                                │          │
│  │  ├─ ResourceLock: 资源锁管理                                │          │
│  │  ├─ MeetingManager: 会议管理                               │          │
│  │  └─ StoryE2ETests: 用户故事 E2E 测试                       │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术选型

| 模块 | 技术/依赖 | 说明 |
|------|----------|------|
| 签署同步 | subprocess + GitPython | 签署后自动 push |
| 变更合规 | 关键词提取 + 对比 | PRD/RFC 冲突检测 |
| 签署记录 | YAML | 持久化到 state/signoffs/ |
| 动态 Checklist | 正则表达式 + pytest | 质量门禁检查 |
| 认知免疫 | 规则引擎 + Skill 加载 |困惑信号检测 |

---

## 2. 模块划分 (M1-M5)

### 2.1 M1: 签署自动同步功能

**模块**: SignoffSync
**功能**: 在签署命令中添加 `--sync` 选项，自动同步到远程仓库

**核心类**:
```python
class SignoffEngine:
    def signoff_with_sync(self, stage: str, name: str, comment: str, reject: str):
        """签署并同步"""
        result = self.execute(stage, name, comment, reject)
        if result.success:
            self._sync_to_remote()
        return result
```

**依赖模块**:
- StateManager: 更新签署状态
- GitHelper: 执行 push 操作

### 2.2 M2: 变更载体明确化

**模块**: ChangeComplianceChecker
**功能**: 检测 PRD/RFC 的合规性和冲突

**核心类**:
```python
class ChangeComplianceChecker:
    def check_prd_compliance(self, prd_file: str) -> ComplianceResult:
        """检查 PRD 合规性"""
        
    def check_rfc_compliance(self, rfc_file: str) -> ComplianceResult:
        """检查 RFC 合规性"""
        
    def detect_conflicts(self, prd_file: str, rfc_file: str) -> List[Conflict]:
        """检测冲突"""
        
    def handle_violation(self, violation_type: str) -> ViolationAction:
        """处理违规"""
```

**依赖模块**:
- StateManager: 检查签署状态
- GitHelper: 读取文件

### 2.3 M3: 签署流程改进

**模块**: SignoffImprover
**功能**: 标准化签署模板、添加检查清单、实现记录持久化

**核心类**:
```python
class SignoffRecordManager:
    """签署记录管理器"""
    def save_signoff(self, signoff_data: dict) -> str:
        """保存签署记录到 state/signoffs/"""
        
    def get_signoff(self, signoff_id: str) -> dict:
        """获取签署记录"""
        
    def list_signoffs(self) -> List[dict]:
        """列出所有签署记录"""
```

**依赖模块**:
- StateManager: 获取当前状态
- YAML: 持久化格式

### 2.4 M4: 动态 Checklist 机制

**模块**: ExtendedChecklistGenerator
**功能**: 扩展 checklist_generator.py，增加需求追溯、任务范围、质量门禁检查

**核心类**:
```python
class ExtendedChecklistGenerator(ChecklistGenerator):
    def generate_full_checklist(self, stage: str) -> List[CheckItem]:
        """生成完整检查清单"""
        
    def generate_traceability_checklist(self) -> List[CheckItem]:
        """需求追溯检查"""
        
    def generate_task_scope_checklist(self) -> List[CheckItem]:
        """任务范围检查"""
        
    def generate_quality_gate_checklist(self) -> List[CheckItem]:
        """质量门禁检查"""
```

**依赖模块**:
- ChecklistGenerator (v2.2.0): 基础检查项生成
- StateManager: 获取状态信息
- pytest-cov: 测试覆盖率

### 2.5 M5: 双代理认知免疫系统

**模块**: CognitiveImmuneSystem
**功能**: 检测困惑信号、自动加载 Skill、提供职责提醒

**核心类**:
```python
class CognitiveImmuneSystem:
    """双代理认知免疫系统"""
    def analyze_message(self, agent_id: str, message: str) -> ImmuneResponse:
        """分析消息，返回免疫响应"""

class SessionStarter:
    """会话起始引导器"""
    def display_welcome(self, agent_id: str):
        """显示欢迎消息和上下文信息"""

class ConfusionDetector:
    """困惑信号检测器"""
    def detect_confusion(self, message: str) -> ConfusionResult:
        """检测困惑信号"""

class ResponsibilityDetector:
    """职责边界检测器"""
    def check_responsibility(self, agent_id: str, action: str) -> ResponsibilityResult:
        """检查职责边界"""
```

**依赖模块**:
- StateManager: 获取当前状态
- SkillLoader: 加载协作指南 Skill
- ProjectConfig: 仓库配置

---

## 3. 模块间依赖关系

```
┌─────────────────────────────────────────────────────────┐
│                    模块依赖关系                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Agent 1/2                                              │
│      │                                                   │
│      ▼                                                   │
│  ┌─────────────────────────────────────────────┐         │
│  │         CognitiveImmuneSystem (M5)       │         │
│  └─────────────────────────────────────────────┘         │
│      │         │         │         │                   │
│      ▼         ▼         ▼         ▼                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │Session │ │Confuse│ │RespDet│ │SkillLoa│      │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │
│      │         │         │                               │
│      └─────────┴─────────┘                               │
│                    │                                     │
│                    ▼                                     │
│  ┌─────────────────────────────────────────────┐         │
│  │     ExtendedChecklistGenerator (M4)       │         │
│  └─────────────────────────────────────────────┘         │
│                    │                                     │
│                    ▼                                     │
│  ┌───────────────────────────┐                           │
│  │ SignoffImprover (M3)    │                           │
│  └───────────────────────────┘                           │
│                    │                                     │
│      ┌─────────────┴─────────────┐                       │
│      ▼                           ▼                       │
│  ┌─────────┐           ┌─────────────┐                 │
│  │Signoff │           │ChangeComp  │                 │
│  │Sync    │           │Checker     │                 │
│  │(M1)    │           │(M2)        │                 │
│  └─────────┘           └─────────────┘                 │
│      │                       │                         │
│      └───────────────────────┘                         │
│                    │                                   │
│                    ▼                                   │
│  ┌─────────────────────────────────────────────┐     │
│  │           StateManager (v2.2.0)             │     │
│  └─────────────────────────────────────────────┘     │
│                    │                                 │
│                    ▼                                 │
│  ┌─────────────────────────────────────────────┐     │
│  │              GitHelper (v2.2.0)              │     │
│  └─────────────────────────────────────────────┘     │
│                                                        │
└─────────────────────────────────────────────────────────┘
```

**依赖说明**:
- M1 (SignoffSync) 依赖 StateManager + GitHelper
- M2 (ChangeCompliance) 依赖 StateManager + GitHelper
- M3 (SignoffImprover) 依赖 StateManager + YAML
- M4 (ExtendedChecklist) 依赖 StateManager + checklist_generator.py
- M5 (CognitiveImmune) 依赖 StateManager + SkillLoader

---

## 4. 与 v2.2.0 的差异

| 方面 | v2.2.0 | v2.2.1 | 差异说明 |
|------|---------|----------|----------|
| 签署命令 | `oc-collab signoff` | `oc-collab signoff --sync` | 新增同步功能 |
| 签署记录 | 无持久化 | `state/signoffs/*.yaml` | 新增持久化 |
| 合规检查 | 无 | `oc-collab compliance check` | 新增功能 |
| Checklist | 基础检查 | 追溯+范围+质量门禁 | 功能扩展 |
| 协作引导 | 无 | 会话起始自动显示 | 新增功能 |
| 困惑检测 | 无 | 信号检测+提醒 | 新增功能 |

---

## 5. 文件变更

### 5.1 新增文件

| 文件路径 | 功能 | M |
|----------|------| - |
| `src/core/signoff_sync.py` | 签署同步 | M1 |
| `src/core/change_compliance.py` | 变更合规检查 | M2 |
| `src/core/signoff_improver.py` | 签署改进 | M3 |
| `src/core/extended_checklist.py` | 动态 Checklist | M4 |
| `src/core/cognitive_immune.py` | 认知免疫系统 | M5 |
| `skills/oc_collab_collaboration_guide/*` | 协作指南 Skill | M5 |
| `state/signoffs/*.yaml` | 签署记录 | M3 |

### 5.2 修改文件

| 文件路径 | 修改内容 | M |
|----------|----------| - |
| `src/cli/main.py` | `--sync` 选项、compliance 命令、agent 命令 | M1/M2/M5 |
| `src/core/signoff.py` | signoff_with_sync 方法 | M1 |
| `src/core/state_manager.py` | 签署记录查询 | M3 |
| `src/core/checklist_generator.py` | 继承扩展 | M4 |

### 5.3 测试文件

| 文件路径 | 测试内容 |
|----------|----------|
| `tests/test_signoff_sync.py` | 签署同步测试 |
| `tests/test_change_compliance.py` | 变更合规测试 |
| `tests/test_signoff_improver.py` | 签署改进测试 |
| `tests/test_extended_checklist.py` | 动态 Checklist 测试 |
| `tests/test_cognitive_immune.py` | 认知免疫测试 |

---

## 6. 验收标准

| 里程碑 | 验收标准 | 验证方式 |
|--------|----------|----------|
| M1 | `--sync` 选项生效 | CLI 测试 |
| M2 | 合规检测可执行 | CLI 测试 |
| M3 | 签署记录持久化 | 集成测试 |
| M4 | 动态 Checklist 覆盖 | 代码审查 |
| M5 | Skill 加载成功 | CLI 测试 |

---

## 7. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 签署成功但同步失败 | 低 | 中 | 显示警告，签署仍有效 |
| 冲突检测误报 | 中 | 低 | 使用 WARN 而非阻止 |
| Skill 格式不兼容 | 低 | 中 | 验证 Skill 格式 |
| 性能影响 | 低 | 低 | 按需加载，非每次都检查 |

---

**设计版本**: v1
**创建日期**: 2026-02-07
**状态**: DRAFT

---

## 附录: Agent 1 评审意见

### A.1 评审信息

| 项目 | 内容 |
|------|------|
| 评审人 | Agent 1 (产品负责人) |
| 评审日期 | 2026-02-07 |
| 评审结论 | ✅ 确认通过 |

### A.2 评审意见

**评审意见**:
- 架构清晰，模块划分合理
- M1-M5 覆盖所有功能需求
- 风险识别全面，应对措施可行

### A.3 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-07 | ✅ 已签署 |
| 开发负责人 | Agent 2 | 2026-02-07 | ✅ 已创建 |

**签署后状态**: DRAFT → APPROVED
