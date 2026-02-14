# 概要设计说明书：oc-collab v2.2.12

**版本**: v1
**创建日期**: 2026-02-14
**作者**: Agent 1 (产品经理)
**版本号**: v2.2.12
**状态**: DRAFT

---

## 1. 功能模块概览

### 1.1 功能模块清单

| 模块 | 子功能 | 描述 | 优先级 |
|------|--------|------|--------|
| **M1: 部署自动化CLI** | 部署前检查 | 自动检查文档同步、测试验收状态 | P0 |
| **M1: 部署自动化CLI** | 版本号管理 | 自动读取/更新pyproject.toml版本号 | P0 |
| **M1: 部署自动化CLI** | 包构建 | 自动执行python -m build | P0 |
| **M1: 部署自动化CLI** | PyPI发布 | 自动执行twine upload | P0 |
| **M1: 部署自动化CLI** | Git推送 | 自动执行commit、tag、push | P0 |
| **M1: 部署自动化CLI** | 发布验证 | 自动调用PyPI API验证 | P0 |
| **M1: 部署自动化CLI** | 状态更新 | 自动更新project_state.yaml | P0 |

### 1.2 功能模块图

```
oc-collab CLI
├── 命令层
│   └── deploy ──→ DeploymentOrchestrator
│                      │
├── 检查层              │
│   ├── DocChecker ────┤
│   └── StateChecker ──┤
│                      │
├── 执行层              │
│   ├── VersionManager ─┤
│   ├── PackageBuilder ─┤
│   ├── PyPIUploader ───┤
│   ├── GitPusher ──────┤
│   └── Verifier ───────┤
│                      │
└── 存储层
    └── StateUpdater ──→ project_state.yaml
```

---

## 2. 功能模块关系

### 2.1 调用关系

| 调用方 | 被调用方 | 说明 |
|--------|----------|------|
| deploy | DeploymentOrchestrator | 主入口，协调各子模块 |
| DeploymentOrchestrator | DocChecker | 检查文档同步状态 |
| DeploymentOrchestrator | StateChecker | 检查测试验收状态 |
| DeploymentOrchestrator | VersionManager | 版本号读取/更新 |
| DeploymentOrchestrator | PackageBuilder | 执行包构建 |
| DeploymentOrchestrator | PyPIUploader | 上传到PyPI |
| DeploymentOrchestrator | GitPusher | Git推送 |
| DeploymentOrchestrator | Verifier | 验证发布结果 |
| DeploymentOrchestrator | StateUpdater | 更新项目状态 |

### 2.2 数据依赖

| 数据提供方 | 数据使用方 | 数据类型 |
|------------|------------|----------|
| pyproject.toml | VersionManager | TOML配置 |
| pyproject.toml | PackageBuilder | 版本号 |
| dist/ | PyPIUploader | 构建产物 |
| project_state.yaml | StateUpdater | 状态记录 |
| CLI args | DeploymentOrchestrator | 命令参数 |

### 2.3 时序关系

| 功能A | 功能B | 说明 |
|-------|-------|------|
| DocChecker | StateChecker | 检查完成后才能继续 |
| StateChecker | VersionManager | 版本检查后才能构建 |
| VersionManager | PackageBuilder | 版本确定后才能构建 |
| PackageBuilder | PyPIUploader | 构建完成后才能上传 |
| PyPIUploader | GitPusher | 上传完成后才能推送 |
| GitPusher | Verifier | 推送完成后才能验证 |
| Verifier | StateUpdater | 验证完成后才能更新状态 |

---

## 3. 产品路线图定位

### 3.1 路线图位置

| 版本 | 功能 | 状态 |
|------|------|------|
| v2.2.11 | TODO编号独立、Skill强制执行、Receiver | 已完成 |
| **v2.2.12** | **部署自动化CLI** | **当前版本** |
| v2.2.13 | 逆向验证评审 | 待开发 |
| v3.0.0 | Agent自动化协同 | 待开发 |

### 3.2 本版本解决的问题

**核心价值**：完成v2.2版本的最后一个功能，实现一键部署

| 问题 | 解决方案 |
|------|----------|
| 部署步骤繁琐易错 | DeploymentOrchestrator 编排全流程 |
| 缺乏自动化验证 | Verifier 自动调用PyPI API |
| 状态更新不及时 | StateUpdater 自动更新project_state.yaml |

### 3.3 与前后版本关系

| 前置版本 | 功能依赖 | 后置版本 |
|----------|----------|----------|
| v2.2.11 | StateNotifier基础设施 | v2.2.13 |
| - | - | 无 |

---

## 4. 用户故事/场景

### 4.1 用户故事

| ID | 故事描述 | 验收标准 | 优先级 |
|----|----------|----------|--------|
| US-001 | 作为开发者，我希望一键部署到PyPI | 执行oc-collab deploy完成全部步骤 | P0 |
| US-002 | 作为开发者，我希望预览部署而不实际执行 | 使用--dry-run模式预览 | P0 |
| US-003 | 作为开发者，我希望跳过某些步骤 | 使用--skip-git或--skip-pypi | P0 |
| US-004 | 作为开发者，我希望验证手动部署结果 | 使用--verify-only仅验证 | P0 |

### 4.2 使用场景

| 场景 | 触发条件 | 主要步骤 | 预期结果 |
|------|----------|----------|----------|
| **场景1: 完整部署** | 执行oc-collab deploy | 1. 检查文档同步<br>2. 检查测试状态<br>3. 版本号管理<br>4. 包构建<br>5. PyPI上传<br>6. Git推送<br>7. 验证发布<br>8. 更新状态 | 部署完成，状态更新 |
| **场景2: 预览部署** | 执行oc-collab deploy --dry-run | 同上，但只显示不执行 | 显示执行计划 |
| **场景3: 仅验证** | 执行oc-collab deploy --verify-only | 1. 调用PyPI API<br>2. 验证安装 | 显示验证结果 |
| **场景4: 跳过Git** | 执行oc-collab deploy --skip-git | 跳过Git步骤 | 只执行PyPI相关步骤 |

---

## 5. 外部接口定义

### 5.1 与外部系统的交互

| 外部系统 | 接口类型 | 数据方向 | 说明 |
|----------|----------|----------|------|
| PyPI | REST API | 出站 | 包发布和验证 |
| Git | CLI | 出站 | 提交和推送 |
| 用户终端 | CLI | 双向 | 命令行交互 |

### 5.2 命令行接口

```bash
# 完整部署
oc-collab deploy [OPTIONS]

# 选项
--version <ver>    指定版本号（默认读取当前版本）
--dry-run          预览模式，不执行实际变更
--skip-git         跳过Git推送步骤
--skip-pypi        跳过PyPI上传步骤
--verify-only      仅执行验证
--verbose          输出详细日志
--help             显示帮助信息
```

### 5.3 状态输出格式

```json
{
  "step": "pypi_upload",
  "status": "success",
  "message": "Package uploaded successfully",
  "details": {
    "version": "2.2.12",
    "url": "https://pypi.org/project/opencode-collaboration/2.2.12/"
  }
}
```

---

## 6. 约束与假设

### 6.1 产品约束

| 约束类型 | 约束内容 | 影响范围 |
|----------|----------|----------|
| 范围控制 | 本版本只做CLI能做的事情 | 功能边界 |
| 安全性 | PyPI Token不写入代码，仅读取配置文件 | 安全要求 |
| 兼容性 | 现有部署流程保持兼容 | 向后兼容 |

### 6.2 技术假设

| 假设 | 验证方式 | 不成立时的应对 |
|------|----------|----------------|
| 用户已配置PyPI Token | 检查~/.pypirc | 提示用户配置 |
| Git远程仓库可访问 | 测试网络连接 | 提示权限错误 |
| PyPI API可用 | 测试API调用 | 显示错误信息 |

### 6.3 风险点

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| PyPI Token缺失 | 中 | 高 | 检测并提示用户 |
| 网络问题 | 中 | 中 | 重试机制+错误提示 |
| 版本冲突 | 低 | 中 | 检测已存在版本 |

---

## 7. 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-14 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-14 | ✅ 技术评审通过（附建议） |

---

**评审建议**:
1. 建议增加"错误处理"章节
2. 建议增加"回滚机制"章节
3. dry-run模式详细输出格式可进一步完善

---

**文档版本**: v1
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: APPROVED
