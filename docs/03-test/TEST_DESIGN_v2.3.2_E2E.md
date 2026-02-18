# v2.3.2 E2E测试设计（完整版）

**版本**: v1  
**创建日期**: 2026-02-17  
**作者**: Agent 1 (产品经理)  
**目标**: 需求覆盖率 100% + 过往版本功能回归测试

---

## 测试验证方式说明

**重要**: 所有测试验证必须查询SQLite数据库（state/todos.db），禁止查询YAML文件。

### 测试前置条件

**每次测试执行前必须**：
1. 删除YAML文件：`rm state/agent_adhoc_todos.yaml`
2. 保留SQLite数据库：`state/todos.db`
3. 执行迁移（如尚未迁移）：`oc-collab migrate --to-sqlite`

```bash
# 测试前置脚本
rm -f state/agent_adhoc_todos.yaml
rm -f state/todo_queue.yaml
rm -f state/state_queue.yaml
# 仅保留SQLite数据库
ls state/*.db
```

**原因**：v2.3.2使用SQLite存储，禁止使用YAML文件。所有测试必须基于SQLite数据验证。

### 验证方式

| 验证类型 | 说明 | 示例 |
|----------|------|------|
| SQLite查询 | 查询数据库验证数据 | `SELECT * FROM todos WHERE id='xxx'` |
| CLI输出 | 验证命令行输出 | `oc-collab todo list` |
| 文件检查 | 检查文件存在 | `ls state/todos.db` |
| 进程检查 | 检查进程状态 | `ps aux \| grep listen` |

### 数据库表结构

```sql
-- todos表
CREATE TABLE todos (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    sender TEXT,
    receiver TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    deferred_until TIMESTAMP,
    is_read INTEGER DEFAULT 0,
    metadata TEXT
);

-- agent_status表
CREATE TABLE agent_status (
    agent_id TEXT PRIMARY KEY,
    status TEXT DEFAULT 'offline',
    last_seen_at TIMESTAMP,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- notifications表
CREATE TABLE notifications (
    id TEXT PRIMARY KEY,
    todo_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_action TEXT,
    user_action_at TIMESTAMP,
    response_time_seconds INTEGER
);
```

---

## 测试范围

### 一、本版本新功能 (v2.3.2)

| 功能ID | 功能名称 | 验收标准数 |
|--------|----------|-----------|
| F-STORE-001 | SQLite存储 | 3 |
| F-STORE-002 | 数据迁移 | 3 |
| F-LISTEN-001 | 监听进程 | 3 |
| F-LISTEN-002 | 状态感知 | 3 |
| F-LISTEN-003 | 上线拉取 | 3 |
| F-NOTIF-001 | 实时通知 | 3 |
| F-NOTIF-002 | 交互操作 | 3 |
| F-CONFIG-001 | 配置管理 | 3 |
| **本版本小计** | | **24** |

---

## 第二部分：过往版本CLI命令回归测试（按命令分类）

### 1. todowrite 命令（8个子命令）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R001 | 基本创建 | `oc-collab todowrite --content "测试"` | 创建成功 | SQLite: SELECT * FROM todos WHERE content='测试' |
| R002 | 指定接收者 | `oc-collab todowrite --content "测试" --to agent2` | TODO-1to2-xxx | SQLite: SELECT * FROM todos WHERE receiver='agent2' |
| R003 | 指定来源 | `oc-collab todowrite --content "测试" --source BUG` | source=BUG | SQLite: SELECT * FROM todos WHERE source='BUG' |
| R004 | 指定优先级 | `oc-collab todowrite --content "测试" --priority high` | priority=high | SQLite: SELECT * FROM todos WHERE priority='high' |
| R005 | 指定模板 | `oc-collab todowrite --content "测试" --type BUG_FIX` | 使用模板 | SQLite: SELECT * FROM todos WHERE id LIKE 'TODO-%' |
| R006 | 测试模式 | `oc-collab todowrite --content "测试" --test-mode` | 不创建只验证 | SQLite: 验证无新记录 |
| R007 | 自动检查 | `oc-collab todowrite --content "测试" --auto-check` | 参数自动检查 | CLI输出检查 |
| R008 | 环境变量 | 设置OC_AGENT_ID后执行 | 使用环境变量值 | SQLite: SELECT * FROM todos WHERE sender='agentX' |

---

### 2. todo 命令组（6个子命令）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R009 | TODO列表 | `oc-collab todo list` | 显示列表 | SQLite: SELECT * FROM todos |
| R010 | 未读筛选 | `oc-collab todo list --unread` | 只显示未读 | SQLite: SELECT * FROM todos WHERE is_read=0 |
| R011 | Agent筛选 | `oc-collab todo list --agent 2` | 只显示Agent2的 | SQLite: SELECT * FROM todos WHERE receiver='agent2' |
| R012 | 来源筛选 | `oc-collab todo list --source BUG` | 只显示BUG来源 | SQLite: SELECT * FROM todos WHERE source='BUG' |
| R013 | TODO详情 | `oc-collab todo show <id>` | 显示详情 | SQLite: SELECT * FROM todos WHERE id='<id>' |
| R014 | 标记已读 | `oc-collab todo mark-read <id>` | 标记成功 | SQLite: SELECT is_read FROM todos WHERE id='<id>' = 1 |
| R015 | TODO统计 | `oc-collab todo stats` | 显示统计 | SQLite: SELECT status, COUNT(*) FROM todos GROUP BY status |
| R016 | TODO完成 | `oc-collab todo complete <id>` | 标记完成 | SQLite: SELECT status FROM todos WHERE id='<id>' = 'completed' |
| R017 | TODO删除 | `oc-collab todo delete <id>` | 删除成功 | SQLite: SELECT * FROM todos WHERE id='<id>' 返回空 |
| R018 | TODO确认 | `oc-collab todo ack <id>` | ACK确认成功 | SQLite: 验证acknowledged_at字段 |

---

### 3. agent 命令组（5个子命令）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R019 | Agent注册 | `oc-collab agent register --id agent3 --role FE` | 注册成功 | SQLite: SELECT * FROM agent_status WHERE agent_id='agent3' |
| R020 | 自动注册 | `oc-collab agent auto-register` | 读取环境变量注册 | SQLite: SELECT * FROM agent_status |
| R021 | Agent列表 | `oc-collab agent list` | 显示所有Agent | SQLite: SELECT * FROM agent_status |
| R022 | Agent注销 | `oc-collab agent unregister <id>` | 注销成功 | SQLite: 验证agent不存在或status='offline' |
| R023 | Agent监听 | `oc-collab agent listen` | 启动监听 | 进程检查: ps aux |
| R024 | 监听守护进程 | `oc-collab agent listen --daemon` | 守护进程运行 | 进程检查: 后台进程存在 |
| R025 | 停止监听 | `oc-collab agent listen --stop` | 监听停止 | 进程检查: 进程不存在 |
| R026 | 监听状态 | `oc-collab agent listen --status` | 显示状态 | CLI输出检查 |

---

### 4. signoff 命令组（4个子命令）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R027 | 需求签署 | `oc-collab signoff requirement` | 签署成功 | 文件检查: state/signoffs.yaml |
| R028 | 设计签署 | `oc-collab signoff design` | 签署成功 | 文件检查: state/signoffs.yaml |
| R029 | 测试签署 | `oc-collab signoff test` | 签署成功 | 文件检查: state/signoffs.yaml |
| R030 | 部署签署 | `oc-collab signoff deployment` | 签署成功 | 文件检查: state/signoffs.yaml |
| R031 | 签署状态 | `oc-collab signoff status` | 显示状态 | 文件检查 |
| R032 | 签署历史 | `oc-collab signoff history` | 显示历史 | 文件检查 |

---

### 5. skill 命令组（6个子命令）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R033 | Skill列表 | `oc-collab skill list` | 显示所有Skill | 文件检查: skills/目录 |
| R034 | Skill搜索 | `oc-collab skill search -k <keyword>` | 搜索结果 | CLI输出检查 |
| R035 | Skill切片 | `oc-collab skill slice <skill> --level chapter` | 章节切片 | 文件检查 |
| R036 | Skill强制 | `oc-collab skill enforce -a <action>` | 强制检查 | CLI输出检查 |
| R037 | Skill检查 | `oc-collab skill check` | 检查状态 | CLI输出检查 |
| R038 | Skill状态 | `oc-collab skill status` | 显示状态 | CLI输出检查 |
| R039 | Skill验证 | `oc-collab skill verify <action>` | 操作前验证 | CLI输出检查 |
| R040 | Skill加载 | `oc-collab skill init` | 初始化Skill | 文件检查 |

---

### 6. deploy 命令组（5个子命令）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R041 | 完整部署 | `oc-collab deploy full` | 部署成功 | CLI输出检查 |
| R042 | 预览模式 | `oc-collab deploy full --dry-run` | 只预览不执行 | CLI输出检查 |
| R043 | 指定版本 | `oc-collab deploy full --version 1.0.0` | 指定版本号 | CLI输出检查 |
| R044 | 跳过Git | `oc-collab deploy full --skip-git` | 跳过Git | CLI输出检查 |
| R045 | 跳过PyPI | `oc-collab deploy full --skip-pypi` | 跳过PyPI | CLI输出检查 |
| R046 | 文档检查 | `oc-collab deploy check-docs` | 检查文档 | CLI输出检查 |
| R047 | 文档同步 | `oc-collab deploy sync-docs` | 同步文档 | 文件检查 |

---

### 7. state 命令组（4个子命令）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R048 | 启动StateReceiver | `oc-collab state start` | 服务启动 | 进程检查 |
| R049 | 停止StateReceiver | `oc-collab state stop` | 服务停止 | 进程检查 |
| R050 | 查看状态 | `oc-collab state status` | 显示状态 | CLI输出检查 |
| R051 | 查看队列 | `oc-collab state queue` | 显示队列 | 文件检查 |

---

### 8. config 命令组（新增）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R052 | 设置配置 | `oc-collab config set opencode.url xxx` | 设置成功 | 文件检查: config/notification.yaml |
| R053 | 查看配置 | `oc-collab config list` | 显示配置 | CLI输出检查 |

---

### 9. notify 命令组（新增）

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R054 | 启用通知 | `oc-collab notify enable` | 启用成功 | 文件检查: config/instructions/TODO_NOTIFY.md |
| R055 | 禁用通知 | `oc-collab notify disable` | 禁用成功 | 文件检查 |
| R056 | 通知状态 | `oc-collab notify status` | 显示状态 | CLI输出检查 |
| R057 | 测试通知 | `oc-collab notify test` | 发送测试 | SQLite: SELECT * FROM notifications |

---

### 10. compliance 命令组

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R058 | 合规检查 | `oc-collab compliance check` | 检查执行 | CLI输出检查 |
| R059 | 合规报告 | `oc-collab compliance report` | 生成报告 | 文件检查 |
| R060 | 违规列表 | `oc-collab compliance violations` | 显示违规 | CLI输出检查 |

---

### 11. git 相关命令

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R061 | Git状态 | `oc-collab git status` | 显示状态 | CLI输出检查 |
| R062 | Git同步 | `oc-collab git sync-state` | 同步状态 | 文件检查 |
| R063 | Git警告 | `oc-collab git warn` | 显示警告 | CLI输出检查 |

---

### 12. startup 命令组

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R064 | 启动检查 | `oc-collab startup check` | 检查未读TODO | SQLite: SELECT COUNT(*) FROM todos WHERE is_read=0 |

---

### 13. rules 命令组

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R065 | 初始化规则 | `oc-collab rules init` | 初始化成功 | 文件检查: config/rules.yaml |
| R066 | 规则状态 | `oc-collab rules status` | 显示状态 | CLI输出检查 |
| R067 | 自动加载 | `oc-collab rules init --auto-load` | 自动加载 | 文件检查 |

---

### 14. version/help 等基础命令

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| R068 | 版本号 | `oc-collab --version` | 显示版本 | CLI输出检查 |
| R069 | 帮助信息 | `oc-collab --help` | 显示帮助 | CLI输出检查 |
| R070 | 状态查看 | `oc-collab status` | 显示状态 | CLI输出检查 |

---

## 第三部分：v2.3.1新功能测试

### F-TODO-001: TODO编号优化

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| V301 | Agent1创建 | Agent1: `oc-collab todowrite --to agent2` | TODO-1to2-xxx | SQLite: SELECT id FROM todos ORDER BY created_at DESC LIMIT 1 |
| V302 | Agent2创建 | Agent2: `oc-collab todowrite --to agent1` | TODO-2to1-xxx | SQLite: SELECT id FROM todos WHERE sender='agent2' |
| V303 | 编号自增 | 连续创建多个 | 编号递增 | SQLite: 对比id序号 |
| V304 | 向后兼容 | 查询旧格式TODO | 正常显示 | SQLite: SELECT * FROM todos WHERE id LIKE 'TODO-%' |
| V305 | 非法格式 | 尝试创建非法格式 | 拒绝并报错 | CLI输出检查 |

---

### F-TODO-002: 来源标签

| 序号 | 测试场景 | 测试命令 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| V306 | 指定来源 | `--source BUG` | source=BUG | SQLite: SELECT source FROM todos WHERE source='BUG' |
| V307 | 筛选来源 | `--source REQUIREMENT` | 只显示该来源 | SQLite: SELECT * FROM todos WHERE source='REQUIREMENT' |
| V308 | 默认来源 | 不指定source | 默认MANUAL | SQLite: SELECT source FROM todos WHERE source='MANUAL' |

---

### F-TODO-003: 模板系统

| 序号 | 测试场景 | 测试命令 | 预期结果 |
|------|----------|----------|----------|
| V309 | BUG模板 | `--type BUG_FIX` | 使用模板 |
| V310 | 需求模板 | `--type REQUIREMENT` | 使用模板 |
| V311 | 模板文件 | 检查config/templates.yaml | 文件存在 |

---

### F-COMM-001: Agent注册表

| 序号 | 测试场景 | 测试命令 | 预期结果 |
|------|----------|----------|----------|
| V312 | 手动注册 | `agent register --id agent3` | 注册成功 |
| V313 | 重复注册 | 重复注册同一ID | 更新而非拒绝 |
| V314 | 注销保护 | 有pending时注销 | 拒绝注销 |

---

### F-COMM-002: ACK确认

| 序号 | 测试场景 | 测试命令 | 预期结果 |
|------|----------|----------|----------|
| V315 | ACK确认 | `oc-collab todo ack <id>` | 确认成功 |
| V316 | ACK查询 | `oc-collab todo show <id>` | 显示ACK状态 |

---

## 第四部分：v2.3.2新功能测试

### F-STORE-001: SQLite存储

| 序号 | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| S001 | 数据库初始化 | 首次运行，检查state/todos.db | 文件创建 | 文件检查: ls state/todos.db |
| S002 | CRUD操作 | 创建/查询/更新/删除 | 全部正常 | SQLite: SELECT/INSERT/UPDATE/DELETE |
| S003 | CLI兼容 | 现有命令 | 正常工作 | SQLite: 验证数据一致性 |

---

### F-STORE-002: 数据迁移

| 序号 | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| S004 | YAML迁移 | 执行迁移命令 | 数据完整 | SQLite: SELECT COUNT(*) 对比原YAML |
| S005 | ID保留 | 迁移后对比 | ID一致 | SQLite: SELECT id FROM todos |
| S006 | 失败回滚 | 模拟失败 | 回滚成功 | SQLite: 验证无新数据 + YAML备份存在 |

---

### F-LISTEN-001: 监听进程

| 序号 | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| S007 | 守护进程 | `agent listen --daemon` | 后台运行 | 进程检查: ps aux |
| S008 | 停止监听 | `agent listen --stop` | 进程停止 | 进程检查: 进程不存在 |
| S009 | 监听状态 | `agent listen --status` | 显示状态 | CLI输出检查 |

---

### F-NOTIF-001: 实时通知

| 序号 | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| S010 | Instruction生成 | `notify enable` | 文件生成 | 文件检查: config/instructions/TODO_NOTIFY.md |
| S011 | LLM识别 | 创建TODO后告知LLM | 识别成功 | SQLite: notifications表新增记录 |
| S012 | Question窗口 | LLM调用question | 窗口弹出 | 事件日志检查 |

---

### F-NOTIF-002: 交互操作

| 序号 | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| S013 | 立即执行 | 选择该操作 | status=in_progress | SQLite: SELECT status FROM todos WHERE status='in_progress' |
| S014 | 留待空闲 | 选择该操作 | 移入deferred | SQLite: SELECT status FROM todos WHERE status='deferred' |
| S015 | 不用执行 | 选择该操作 | status=dismissed | SQLite: SELECT status FROM todos WHERE status='cancelled' |

---

### F-CONFIG-001: 配置管理

| 序号 | 测试场景 | 测试步骤 | 预期结果 | 验证方式 |
|------|----------|----------|----------|----------|
| S016 | 设置URL | `config set opencode.url xxx` | 配置成功 | 文件检查: config/notification.yaml |
| S017 | 设置Webhook | `config set webhook.url xxx` | 配置成功 | 文件检查: config/notification.yaml |
| S018 | 查看配置 | `config list` | 显示配置 | CLI输出检查 |

---

## 测试统计

| 测试阶段 | 测试数 |
|----------|--------|
| 过往版本CLI回归测试 | 70 |
| v2.3.1新功能测试 | 16 |
| v2.3.2新功能测试 | 18 |
| **总计** | **104** |

---

## 测试执行原则

1. **先跑过往版本CLI** - 确保迁移不影响现有功能
2. **再跑v2.3.1功能** - 验证多Agent支持
3. **最后跑v2.3.2新功能** - 验证本次改动
4. **全部通过才能发布** - 104个用例必须100%通过

