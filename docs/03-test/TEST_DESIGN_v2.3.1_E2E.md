# v2.3.1 E2E测试设计

**版本**: v1  
**创建日期**: 2026-02-17  
**作者**: Agent 1 (产品经理)  
**目标**: 需求覆盖率 100%

---

## 测试范围

| 功能ID | 功能名称 | 验收标准数 |
|--------|----------|-----------|
| F-TODO-001 | TODO编号优化 | 6 |
| F-TODO-002 | 向后兼容 | 5 |
| F-TODO-003 | 来源标签 | 5 |
| F-TODO-004 | 模板系统 | 5 |
| F-COMM-001 | 自动Git同步 | 4 |
| F-COMM-002 | Agent注册表 | 6 |
| F-COMM-003 | ACK确认 | 4 |
| F-COMP-001 | 合规规则更新 | 4 |
| **总计** | | **39** |

---

## 测试用例

### F-TODO-001: TODO编号优化

| 序号 | 测试场景 | 验收标准 | 测试步骤 | 预期结果 |
|------|----------|----------|----------|----------|
| T001 | Agent1创建TODO | Agent1创建TODO生成格式 TODO-1to2-xxx | 1. 切换到Agent1<br>2. 执行 `oc-collab todowrite --content "测试" --to agent2` | 输出 TODO-1to2-xxx |
| T002 | Agent2创建TODO | Agent2创建TODO生成格式 TODO-2to1-xxx | 1. 切换到Agent2<br>2. 执行 `oc-collab todowrite --content "测试" --to agent1` | 输出 TODO-2to1-xxx |
| T003 | 多Agent编号 | TODO-1to3-xxx | 1. 注册Agent3<br>2. Agent1创建TODO分配给Agent3 | 输出 TODO-1to3-xxx |
| T004 | 编号自增 | 编号按接收者独立自增 | 1. 创建多个TODO给同一接收者 | 编号依次递增 |
| T005 | 现有TODO不受影响 | 现有TODO不受影响 | 1. 查询旧格式TODO | 正常显示 |
| T006 | 未知接收者降级 | 未知接收者降级处理 | 1. Agent1创建TODO分配给不存在的Agent9 | 警告但允许创建 |

---

### F-TODO-002: 向后兼容

| 序号 | 测试场景 | 验收标准 | 测试步骤 | 预期结果 |
|------|----------|----------|----------|----------|
| T007 | 旧格式识别 | 旧格式 TODO-1-xxx 视为 TODO-1to1-xxx | 1. 查询旧格式TODO | 显示为 TODO-1to1-xxx |
| T008 | CLI显示 | CLI输出同时支持两种格式 | 1. 执行 `oc-collab todo list` | 显示正确格式 |
| T009 | 命令支持 | 支持 list 和 show 命令 | 1. 执行 `oc-collab todo show <id>` | 显示详情 |
| T010 | 边界测试 | TODO-12-001 和 TODO-1to2-001 不混淆 | 1. 创建两个不同格式TODO | 分别正确解析 |
| T011 | 非法格式拒绝 | 非法格式拒绝创建 | 1. 尝试创建 TODO-abc-123 | 拒绝并报错 |

---

### F-TODO-003: 来源标签

| 序号 | 测试场景 | 验收标准 | 测试步骤 | 预期结果 |
|------|----------|----------|----------|----------|
| T012 | 指定来源 | 支持 REQUIREMENT/BUG/FEEDBACK/MANUAL | 1. `oc-collab todowrite --content "测试" --source BUG` | source=BUG |
| T013 | 筛选功能 | CLI支持按来源筛选 | 1. `oc-collab todo --source BUG` | 只显示BUG来源 |
| T014 | 详情显示 | show命令显示来源 | 1. `oc-collab todo show <id>` | 显示source字段 |
| T015 | 简写支持 | 支持 -s 简写 | 1. `oc-collab todowrite -s REQUIREMENT` | 正确设置 |
| T016 | 默认值 | 不指定时默认 MANUAL | 1. 不指定source创建TODO | 默认 MANUAL |

---

### F-TODO-004: 模板系统

| 序号 | 测试场景 | 验收标准 | 测试步骤 | 预期结果 |
|------|----------|----------|----------|----------|
| T017 | 模板选择 | 支持 --type 选择模板 | 1. `oc-collab todowrite --type BUG_FIX` | 使用BUG_FIX模板 |
| T018 | 需求模板 | REQUIREMENT模板 | 1. 使用REQUIREMENT模板创建 | 包含需求字段 |
| T019 | BUG模板 | BUG_FIX模板 | 1. 使用BUG_FIX模板创建 | 包含bug_id等字段 |
| T020 | 模板文件 | config/templates.yaml存在 | 1. 检查配置文件 | 文件存在 |
| T021 | 自定义模板 | 支持用户扩展 | 1. 添加自定义模板到配置文件 | 可使用 |

---

### F-COMM-001: 自动Git同步

| 序号 | 测试场景 | 验收标准 | 测试步骤 | 预期结果 |
|------|----------|----------|----------|----------|
| T022 | 自动触发 | TODO创建触发git | 1. 创建TODO<br>2. 检查git status | 自动add+commit |
| T023 | 配置文件 | config/git_sync.yaml | 1. 检查配置文件 | 文件存在 |
| T024 | 失败处理 | 失败不阻塞主流程 | 1. 模拟同步失败 | 警告但不阻塞 |
| T025 | 开关控制 | 支持配置开关 | 1. 关闭开关<br>2. 创建TODO | 不同步 |

---

### F-COMM-002: Agent注册表

| 序号 | 测试场景 | 验收标准 | 测试步骤 | 预期结果 |
|------|----------|----------|----------|----------|
| T026 | 手动注册 | register命令 | 1. `oc-collab agent register --id agent3 --role FRONTEND_DEV` | 注册成功 |
| T027 | 自动注册 | auto-register命令 | 1. `oc-collab agent auto-register` | 自动读取环境变量 |
| T028 | 环境变量 | OC_AGENT_ID | 1. 设置环境变量<br>2. 执行register | 使用环境变量值 |
| T029 | 列表查询 | agent list | 1. `oc-collab agent list` | 显示所有Agent |
| T030 | 重复注册 | 重复注册覆盖 | 1. 重复注册同一ID | 更新而非拒绝 |
| T031 | 注销保护 | 有pending TODO的Agent禁止注销 | 1. 有pending TODO<br>2. 尝试注销 | 拒绝注销 |

---

### F-COMM-003: ACK确认

| 序号 | 测试场景 | 验收标准 | 测试步骤 | 预期结果 |
|------|----------|----------|----------|----------|
| T032 | 自动ACK | todo show触发ACK | 1. 接收者执行 `todo show` | 自动ACK |
| T033 | 手动ACK | ack命令 | 1. `oc-collab todo ack <id>` | 手动ACK成功 |
| T034 | 状态更新 | acknowledged状态 | 1. ACK后检查 | 状态为acknowledged |
| T035 | 创建者可见 | 创建者查看ACK状态 | 1. 创建者执行 `todo show` | 显示ACK状态 |

---

### F-COMP-001: 合规规则更新

| 序号 | 测试场景 | 验收标准 | 测试步骤 | 预期结果 |
|------|----------|----------|----------|----------|
| T036 | 新格式检查 | 支持TODO-XtoY-xxx | 1. 创建新格式TODO | 正确识别 |
| T037 | 旧格式检查 | 兼容TODO-X-xxx | 1. 创建旧格式TODO | 正确识别 |
| T038 | 非法创建阻止 | Agent1创建非法的TODO | 1. Agent1尝试创建 TODO-2to3-xxx | 阻止并报错 |
| T039 | 合规提示 | 错误信息明确 | 1. 违规操作 | 清晰的错误提示 |

---

## 测试执行计划

| 阶段 | 测试内容 | 负责Agent |
|------|----------|-----------|
| 单元测试 | 各模块独立测试 | Agent2 |
| 集成测试 | 模块间协作测试 | Agent2 |
| E2E测试 | 完整业务流程测试 | Agent1 |
| 验收测试 | 需求覆盖率验证 | Agent1 |

---

## 覆盖率目标

- **需求覆盖率**: 100% (39/39 验收标准)
- **测试用例数**: 39个
- **通过标准**: 所有T001-T039测试用例通过

---

**状态**: DRAFT
