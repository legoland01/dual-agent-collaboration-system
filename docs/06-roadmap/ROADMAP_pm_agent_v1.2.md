# PM-Agent 开发计划 v1.2

**版本**: v1.2  
**日期**: 2026-02-19

---

## 一、核心功能：Agent通知（微信模式）

### 1.1 功能设计

采用微信模式解决TODO通知问题：
- PM-Agent维护Agent列表+在线状态
- 收到TODO时显示红点提示
- 用户主动去Agent窗口查看

### 1.2 功能列表

| 功能 | 说明 | 依赖 |
|------|------|------|
| Agent列表 | 显示所有Agent及状态 | oc-collab agent list |
| 在线状态 | 实时显示Agent在线/离线 | oc-collab agent listen |
| 红点提示 | 有新TODO时显示红点 | trigger机制复用 |
| 主动查看 | Agent自己输入命令拉取 | oc-collab todo list |

### 1.3 技术实现

```
外部系统触发 → trigger文件 → PM-Agent监听 → 更新红点状态
                                           ↓
Agent自己查询 ← oc-collab todo list ← 用户主动查看
```

---

## 二、其他功能（待定）

| 功能 | 说明 | 状态 |
|------|------|------|
| 跨项目查询 | 查看其他项目状态 | oc-collab v2.3.3 |
| 公共文档查询 | oc-collab docs CLI | oc-collab v2.3.3 |

---

**前置版本**: v1.1
**依赖**: oc-collab v2.3.3
