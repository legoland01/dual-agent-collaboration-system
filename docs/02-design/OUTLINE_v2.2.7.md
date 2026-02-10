# 概要设计说明书：oc-collab v2.2.7

**版本**: v1
**创建日期**: 2026-02-10
**作者**: Agent 1 (产品经理)
**关联需求**: requirements_v2.2.7.md
**版本号**: v2.2.7
**状态**: DRAFT

---

## 1. 功能模块概览

### 1.1 v2.2.7 功能模块图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        oc-collab v2.2.7 质量保障与通知架构                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                     CLI 命令层 (v2.2.7 新增)                                    │ │
│  ├─────────────────────────────────────────────────────────────────────────────┤ │
│  │  Skill保障命令                      │ Webhook命令                            │ │
│  │  ├─ oc-collab skill test           │ ├─ oc-collab webhook init             │ │
│  │  ├─ oc-collab skill test --skill   │ ├─ oc-collab webhook status           │ │
│  │  ├─ oc-collab skill coverage       │ ├─ oc-collab webhook start             │ │
│  │  └─ oc-collab skill coverage --fix │ └─ oc-collab webhook stop             │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                              │
│                                    ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         核心功能模块                                           │ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  【v2.2.7新增】Skill测试模块                                             ││ │
│  │  │  ├─ SkillTester: 内容准确性验证 [v2.2.7]                                ││ │
│  │  │  ├─ ReferenceValidator: 引用关系验证 [v2.2.7]                           ││ │
│  │  │  ├─ CLIActionValidator: CLI命令验证 [v2.2.7]                           ││ │
│  │  │  └─ CoverageCalculator: 覆盖率统计 [v2.2.7]                              ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  【v2.2.7新增】Webhook模块                                               ││ │
│  │  │  ├─ WebhookConfig: Webhook配置 [v2.2.7]                                ││ │
│  │  │  ├─ EventListener: 事件监听 [v2.2.7]                                    ││ │
│  │  │  ├─ EventDispatcher: 事件分发 [v2.2.7]                                  ││ │
│  │  │  └─ StateNotifier: 状态通知 [v2.2.7]                                   ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 v2.2.7 功能清单

| 功能模块 | 功能 | 类型 | 工时 | 架构模块 |
|----------|------|------|------|----------|
| Skill测试模块 | SkillTester (内容准确性) | 新增 | 2h | 9.2 |
| Skill测试模块 | ReferenceValidator (引用验证) | 新增 | 2h | 9.2 |
| Skill测试模块 | CLIActionValidator (CLI验证) | 新增 | 2h | 9.2 |
| Skill测试模块 | CoverageCalculator (覆盖率) | 新增 | 4h | 9.2 |
| Skill文档 | Skill测试规范文档 | Skill | 2h | 9.2 |
| Skill文档 | Skill维护清单 | Skill | 1h | 9.2 |
| Webhook模块 | WebhookConfig (配置) | 新增 | 4h | 10.3 |
| Webhook模块 | EventListener (监听) | 新增 | 4h | 10.3 |
| Webhook模块 | EventDispatcher (分发) | 新增 | 3h | 10.3 |
| Webhook模块 | StateNotifier (状态通知) | 新增 | 3h | 10.3 |

---

## 2. 模块详细设计

### 2.1 Skill测试模块

#### 2.1.1 SkillTester (内容准确性验证)

**职责**: 验证Skill内容与实际行为的一致性

**核心方法**:
```python
class SkillTester:
    def validate_outputs_exist(skill_id: str) -> ValidationResult:
        """验证outputs字段描述的文件是否存在"""
        
    def validate_triggers_match(skill_id: str) -> ValidationResult:
        """验证触发条件是否与content.md匹配"""
        
    def validate_sop_elements(skill_id: str) -> ValidationResult:
        """验证是否包含SOP四要素"""
        
    def run_all_tests() -> TestReport:
        """运行所有测试，返回测试报告"""
```

**依赖模块**:
- `skills/*/skill.json` - 配置文件
- `skills/*/content.md` - 内容文件

#### 2.1.2 ReferenceValidator (引用关系验证)

**职责**: 验证Skill内部和跨Skill引用

**核心方法**:
```python
class ReferenceValidator:
    def validate_internal_links(skill_id: str) -> ValidationResult:
        """验证内部Markdown链接"""
        
    def validate_cross_skill_refs(skill_id: str) -> ValidationResult:
        """验证跨Skill引用"""
        
    def validate() -> ValidationResult:
        """执行所有引用验证"""
```

#### 2.1.3 CLIActionValidator (CLI命令验证)

**职责**: 验证Skill中描述的CLI命令是否存在

**核心方法**:
```python
class CLIActionValidator:
    def extract_cli_commands(skill_id: str) -> List[str]:
        """从content.md提取CLI命令"""
        
    def validate_commands(commands: List[str]) -> ValidationResult:
        """验证命令是否存在"""
```

#### 2.1.4 CoverageCalculator (覆盖率统计)

**职责**: 统计Skill内容的切片覆盖率

**核心方法**:
```python
class CoverageCalculator:
    def calculate_coverage(skill_id: str) -> float:
        """计算覆盖率"""
        
    def generate_report() -> CoverageReport:
        """生成覆盖率报告"""
        
    def check_threshold(threshold: float) -> bool:
        """检查是否达到阈值"""
```

### 2.2 Webhook模块

#### 2.2.1 WebhookConfig (Webhook配置)

**职责**: 生成和管理Webhook配置

**核心方法**:
```python
class WebhookConfig:
    def generate_config() -> WebhookConfig:
        """生成Webhook配置"""
        
    def generate_secret() -> str:
        """生成签名密钥"""
        
    def save_config(path: str) -> bool:
        """保存配置到文件"""
```

**配置格式** (`config/webhook.yaml`):
```yaml
webhook:
  github:
    secret: "${WEBHOOK_GITHUB_SECRET}"
    events:
      - push
      - pull_request
  gitee:
    secret: "${WEBHOOK_GITEE_SECRET}"
    events:
      - push
      - pull_request
  server:
    host: "0.0.0.0"
    port: 8080
    endpoint: "/api/webhook/callback"
```

#### 2.2.2 EventListener (事件监听)

**职责**: 监听GitHub/Gitee webhook事件

**核心方法**:
```python
class EventListener:
    def parse_github_payload(payload: dict) -> GitHubEvent:
        """解析GitHub webhook payload"""
        
    def parse_gitee_payload(payload: dict) -> GiteeEvent:
        """解析Gitee webhook payload"""
        
    def start_listening(port: int = 8080) -> None:
        """启动本地HTTP服务监听webhook"""
```

#### 2.2.3 EventDispatcher (事件分发)

**职责**: 将事件分发给对应Agent

**核心方法**:
```python
class EventDispatcher:
    def dispatch(event: WebhookEvent) -> bool:
        """分发事件到对应Agent"""
        
    def format_message(event: WebhookEvent) -> str:
        """格式化事件消息"""
```

**路由规则**:
- `push` → Agent1
- `pull_request` → Agent2

#### 2.2.4 StateNotifier (状态通知)

**职责**: 阶段变更时通知对方Agent

**核心方法**:
```python
class StateNotifier:
    def detect_phase_change(old_state: dict, new_state: dict) -> Optional[PhaseChange]:
        """检测阶段变更"""
        
    def send_notification(change: PhaseChange) -> bool:
        """发送状态变更通知"""
        
    def generate_notification(change: PhaseChange) -> dict:
        """生成通知内容"""
```

---

## 3. 详细设计任务分配

### 3.1 Agent 2 负责（详细设计）

| 功能 | 详细设计文档 | 工时 |
|------|-------------|------|
| SkillTester | DETAIL-2026-02-F-TEST_SkillTester.md | 2h |
| ReferenceValidator | DETAIL-2026-02-F-TEST_ReferenceValidator.md | 2h |
| CLIActionValidator | DETAIL-2026-02-F-TEST_CLIActionValidator.md | 2h |
| CoverageCalculator | DETAIL-2026-02-F-TEST_CoverageCalculator.md | 4h |
| WebhookConfig | DETAIL-2026-02-F-WEB_WebhookConfig.md | 4h |
| EventListener | DETAIL-2026-02-F-WEB_EventListener.md | 4h |
| EventDispatcher | DETAIL-2026-02-F-WEB_EventDispatcher.md | 3h |
| StateNotifier | DETAIL-2026-02-F-WEB_StateNotifier.md | 3h |

### 3.2 Agent 1 负责（Skill更新）

| 功能 | 目标文档 | 工时 |
|------|---------|------|
| Skill测试规范文档 | docs/03-test/Skill_Test_Guide.md | 2h |
| Skill维护清单 | docs/03-test/Skill_Maintenance_Checklist.md | 1h |

---

## 4. 依赖关系

### 4.1 模块依赖

```
SkillTester ───┬──→ skills/*/skill.json
                │
ReferenceValidator ───→ skills/*/content.md
                │
CLIActionValidator ───→ src/cli/main.py
                │
CoverageCalculator ───→ SkillTester, SkillSlicer (v2.2.6)
                │
WebhookConfig ───┬──→ config/webhook.yaml
                  │
EventListener ───→ config/webhook.yaml
                  │
EventDispatcher ───→ EventListener
                  │
StateNotifier ───→ EventDispatcher, state/project_state.yaml
```

### 4.2 外部依赖

| 依赖项 | 用途 | 替代方案 |
|--------|------|----------|
| Python http.server | 本地Webhook监听 | 无（使用内置库） |
| hmac | GitHub签名验证 | 无（使用内置库） |
| hashlib | 密钥生成 | 无（使用内置库） |

---

## 5. 测试策略

### 5.1 测试分工

| 测试类型 | 执行人 | 范围 |
|----------|--------|------|
| 白盒测试 | Agent 2 | SkillTester, Webhook模块 |
| 黑盒测试 | Agent 1 | CLI命令完整流程 |
| Skill文档测试 | Agent 1 | Skill测试规范 + 维护清单 |

### 5.2 验收测试

- 每个模块独立验收
- 支持 `--verbose` 输出详细结果
- Webhook支持 `--no-webhook` 回退选项

---

## 6. 里程碑

### 6.1 v2.2.7 完整方案（27h）

| 里程碑 | 内容 | 时间点 |
|--------|------|--------|
| M1 | Skill测试模块 (Tester/Validator) | 第1-3天 |
| M2 | Skill覆盖率统计 | 第4天 |
| M3 | Webhook配置 + 监听 | 第5-6天 |
| M4 | Webhook分发 + 通知 | 第7天 |
| M5 | Skill文档更新 | 第8天 |
| M6 | 测试验收 | 第9天 |

### 6.2 分阶段方案（建议）

| 阶段 | 内容 | 工时 | 交付物 |
|------|------|------|--------|
| v2.2.7 | Skill保障 + Webhook基础 | 17h | Skill测试 + Webhook配置+监听 |
| v2.2.8 | Webhook完成 | 10h | 事件分发+状态通知 |

---

## 7. 风险与应对

| 风险 | 应对措施 |
|------|----------|
| Webhook监听稳定性 | 提供 `--no-webhook` 选项 |
| Skill测试覆盖率不达标 | 提供 `--threshold` 可配置 |
| 配置文件格式变更 | 使用版本号 `v1` 兼容 |

---

**创建人**: Agent 1
**日期**: 2026-02-10
**状态**: DRAFT → 待Agent2评审

---

## Agent 2 评审

### 阅读理解

- [ ] 核心目标清晰
- [ ] 功能范围明确

### 完整性

- [ ] 模块设计完整
- [ ] 依赖关系清晰

### 一致性

- [ ] 需求与设计对齐
- [ ] CLI命令与设计一致

### 可行性

- [ ] 工时可控
- [ ] 技术方案可行

### 结论

| 角色 | 签署人 | 状态 | 日期 |
|------|--------|------|------|
| 开发负责人 | Agent 2 | ⏳ | 待评审 |
