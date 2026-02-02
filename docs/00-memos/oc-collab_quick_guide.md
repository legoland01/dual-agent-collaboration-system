# oc-collab 快速使用指南

## 简介

oc-collab 是一个通用的双代理（Dual-Agent）协作开发框架，适用于任何需要产品经理 + 开发人员协作的软件项目。

通过里程碑签署、强制约束、智能记忆，确保开发过程规范化、可追溯、可复用。

## 核心功能

| 功能 | 说明 |
|------|------|
| 双代理协作 | 产品经理（需求）+ 开发（实现），职责分离、互相监督 |
| 里程碑签署 | 每个阶段完成后需双方签字确认，防止质量门禁被绕过 |
| 自动检查 | 配置验证、测试覆盖率、问题追踪、模式声明 |

## 日常使用

```bash
# 查看项目状态
oc-collab status

# 查看当前待办
oc-collab todo

# 推进到下一阶段
oc-collab advance -p design

# 签署确认（需双方完成）
oc-collab signoff

# 运行测试
oc-collab test

# 检查覆盖率
oc-collab coverage
```

## 里程碑流程

```
需求评审 → 设计评审 → 开发完成 → 测试通过 → 部署上线
    ↓           ↓           ↓           ↓          ↓
   签署        签署        签署        签署       完成

每个阶段必须双方签署后才能进入下一阶段
```

## 文件位置

| 内容 | 路径 |
|------|------|
| 需求文档 | `docs/01-requirements/` |
| 设计文档 | `docs/02-design/` |
| 测试报告 | `docs/03-test/` |
| 项目状态 | `state/project_state.yaml` |
| 记忆文件 | `state/memory/` |

## 五大约束机制

| 约束 | 命令 | 说明 |
|------|------|------|
| 配置验证 | `oc-collab config validate` | 启动前检查 API Key、模型等配置 |
| 模式声明 | `oc-collab run --mode real\|mock` | 强制声明运行模式，防止 Mock/Real 混淆 |
| 测试隔离 | `oc-collab test --fresh` | 强制重新测试，不使用缓存 |
| 问题追踪 | `oc-collab issue check` | 检查已知问题是否复发 |
| 覆盖率门禁 | `oc-collab coverage check` | 核心模块 100%，整体 ≥80% |

## 关键原则

1. **所有变更需签署** - 不能跳过质量门禁
2. **问题不重复犯** - 智能记忆自动提醒历史解决方案
3. **版本独立** - 不同版本文件互不干扰
4. **记忆可传承** - Compaction 操作不会丢失关键记忆

## 快速开始

```bash
# 1. 初始化项目
oc-collab init MyProject

# 2. 创建需求文档
# 编辑 docs/01-requirements/requirements_vX.X.0.md

# 3. 双方评审并签署需求
oc-collab signoff requirements

# 4. 开始开发（分里程碑 M1~M5）
# 每个里程碑需要：开发 → 测试 → 签署

# 5. 完成所有里程碑后部署
```

## 帮助

```bash
oc-collab --help          # 查看所有命令
oc-collab status --help   # 命令帮助
```

## 了解更多

- 完整需求: `docs/01-requirements/requirements_v2.2.0.md`
- 开发计划: `docs/05-development/`
- 经验备忘录: `docs/00-memos/`
