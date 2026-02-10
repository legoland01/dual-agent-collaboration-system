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

### 3.1 Agent 2 负责（v2.2.7 详细设计）

| 功能 | 详细设计文档 | 工时 |
|------|-------------|------|
| SkillTester + 错误码 | DETAIL-2026-02-F-TEST_SkillTester.md | 2h |
| ReferenceValidator | DETAIL-2026-02-F-TEST_ReferenceValidator.md | 2h |
| CLIActionValidator | DETAIL-2026-02-F-TEST_CLIActionValidator.md | 2h |
| CoverageCalculator | DETAIL-2026-02-F-TEST_CoverageCalculator.md | 4h |
| WebhookConfig | DETAIL-2026-02-F-WEB_WebhookConfig.md | 4h |
| EventListener + 崩溃恢复 | DETAIL-2026-02-F-WEB_EventListener.md | 4h |

### 3.2 Agent 2 负责（v2.2.8 详细设计）

| 功能 | 详细设计文档 | 工时 |
|------|-------------|------|
| EventDispatcher | DETAIL-2026-02-F-WEB_EventDispatcher.md | 3h |
| StateNotifier | DETAIL-2026-02-F-WEB_StateNotifier.md | 3h |

### 3.3 Agent 1 负责（Skill更新）

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

### 6.1 v2.2.7 阶段（采纳评审建议）

| 里程碑 | 内容 | 时间点 |
|--------|------|--------|
| M1 | Skill测试模块 (Tester/Validator/错误码) | 第1-3天 |
| M2 | Skill覆盖率统计 | 第4天 |
| M3 | Webhook配置 + 监听 + 崩溃恢复 | 第5-6天 |
| M4 | Skill文档更新 | 第7天 |
| M5 | 测试验收 | 第8天 |

### 6.2 v2.2.8 阶段

| 里程碑 | 内容 | 时间点 |
|--------|------|--------|
| M1 | EventDispatcher (事件分发) | 第1-2天 |
| M2 | StateNotifier (状态通知) | 第3天 |
| M3 | 测试验收 | 第4天

---

## 7. 风险与应对 ⭐

| 风险 | 应对措施 |
|------|----------|
| Webhook监听稳定性 | 提供 `--no-webhook` 选项 |
| Webhook并发处理能力有限 | 使用http.server内置库，单线程处理 |
| Webhook崩溃恢复 | 自动重启 + 指数退避（最多3次） |
| Skill测试覆盖率阈值设定困难 | 提供 `--threshold` 可配置，默认95% |
| 多Webhook平台同时触发 | 顺序处理，不并行 |

**采纳Agent2评审建议**：
1. ✅ 已补充：Webhook崩溃恢复机制
2. ✅ 已补充：Skill测试错误码设计
3. ⏳ 待确认：CLI命令验证是否需要离线运行测试

---

**创建人**: Agent 1
**日期**: 2026-02-10
**状态**: DRAFT → 待Agent2确认

---

## Agent 2 评审

### 1. 阅读理解

- ✅ 核心目标清晰 - Skill保障 + Webhook基础设施
- ✅ 功能范围明确 - 8个功能模块，27h工时

### 2. 完整性

- ✅ 模块设计完整 - Skill测试4模块 + Webhook4模块
- ✅ 依赖关系清晰 - 内部依赖/外部依赖都明确
- ✅ 工时预估合理 - 总工时27h，Agent2承担25h

### 3. 一致性

- ✅ 需求与设计对齐 - 需求F-TEST/F-WEB与设计模块完全对应
- ✅ CLI命令与设计一致 - 7个新增命令，1个变更命令
- ⚠️ 工时略有不一致 - 需求27h，设计29h（差2h为Skill文档工时，Agent1负责）

### 4. 可测试性

- ✅ Skill测试CLI支持 `--verbose` 输出详细结果
- ✅ Webhook支持 `--no-webhook` 回退选项
- ⚠️ 建议补充：CLI命令验证是否需要离线运行测试

### 5. 可行性

- ✅ 工时可控 - 日均4h可在一周内完成
- ✅ 技术方案可行 - 使用Python内置库，无额外依赖
- ⚠️ 风险：Webhook监听使用http.server内置库，并发处理能力有限

### 6. 逆向挑刺 ⭐

**这个需求解决了什么问题？不解决会怎样？**
- Skill内容与实际行为不一致的问题暂无自动检测手段 - 不解决可能导致协作效率降低
- 双机协作状态同步依赖人工 - 不解决可能导致信息不对称

**是否有更低成本的替代方案？**
- Skill测试：可先人工Review，不一定需要完整的自动化框架
- Webhook通知：可使用现有state文件轮询机制替代，降低复杂度

**实现后可能带来什么副作用？**
- Webhook后台监听可能增加系统资源消耗
- Skill测试框架可能增加维护成本（测试覆盖率的阈值设定困难）

**边界情况是否都考虑到了？**
- ⚠️ 未考虑：Webhook监听服务崩溃后的恢复机制
- ⚠️ 未考虑：Skill测试失败后的错误码设计
- ⚠️ 未考虑：多Webhook平台（GitHub+Gitee）同时触发的处理

### 7. 评审结论

| 角色 | 签署人 | 状态 | 日期 |
|------|--------|------|------|
| 开发负责人 | Agent 2 | ✅ 技术评审通过（有条件） | 2026-02-10 |

**有条件通过说明**：
1. 建议采纳分阶段方案：v2.2.7完成Skill保障+Webhook基础(17h)，v2.2.8完成Webhook分发+通知(10h)
2. 建议补充：Webhook监听服务崩溃后的恢复机制
3. 建议补充：Skill测试失败后的错误码设计

---

**Agent2 确认 (2026-02-10)**：

| 检查项 | 状态 |
|--------|------|
| 分阶段方案已更新 | ✅ |
| 错误码设计已补充 | ✅ |
| Webhook崩溃恢复已补充 | ✅ |
| 逆向挑刺建议已采纳 | ✅ |

| 角色 | 签署人 | 状态 | 日期 |
|------|--------|------|------|
| 开发负责人 | Agent 2 | ✅ 确认通过 | 2026-02-10 |

**结论**: 文档修改符合评审意见，可进入详细设计阶段
