# 版本管理指南

**版本**: v1.0.0  
**适用阶段**: all  
**Agent**: Agent 1, Agent 2

> **⚠️ 本Skill引用其他Skill的特定章节，不重复内容。**
> **查看完整章节**: `oc-collab skill slice oc_collab_version_management_guide`

---

## SOP结构概览

| SOP要素 | 内容 |
|---------|------|
| **1. 版本类型** | 见 [Patch发布条件](oc_collab_patch_release_guide/content.md#1-patch触发条件) |
| **2. 版本号规则** | 见 [版本号管理规则](oc_collab_detailed_design_guide/content.md#版本号管理规则) |
| **3. 发布流程** | 见 [Patch发布流程](oc_collab_patch_release_guide/content.md#2-patch发布流程) |
| **4. 发布前检查** | 见 [发布前检查](oc_collab_test_acceptance_guide/content.md#3-版本核对) |
| **5. 文档版本** | 见 [文档版本管理](oc_collab_detailed_design_guide/content.md#版本历史标准化格式) |

---

## 引用关系

| 章节 | 引用Skill | 引用章节 |
|------|-----------|----------|
| 版本类型 | oc_collab_patch_release_guide | 1. Patch触发条件 |
| 版本号规则 | oc_collab_detailed_design_guide | 版本号管理规则 |
| 发布流程 | oc_collab_patch_release_guide | 2. Patch发布流程 |
| 发布前检查 | oc_collab_test_acceptance_guide | 3. 版本核对 |
| 文档版本 | oc_collab_detailed_design_guide | 版本历史标准化格式 |

---

## 快速参考

### Patch发布

```bash
# 查看Patch发布完整流程
oc-collab skill slice oc_collab_patch_release_guide --level section
```

### 版本号管理

```bash
# 查看版本号规则
oc-collab skill slice oc_collab_detailed_design_guide --level subsection --filter "版本号"
```

### 发布检查

```bash
# 查看发布前检查清单
oc-collab skill slice oc_collab_test_acceptance_guide --level section --filter "版本核对"
```

---

## 相关Skill

| Skill | 说明 |
|-------|------|
| [oc_collab_patch_release_guide](../oc_collab_patch_release_guide/) | Patch发布流程 |
| [oc_collab_deployment_guide](../oc_collab_deployment_guide/) | 部署步骤 |
| [oc_collab_test_acceptance_guide](../oc_collab_test_acceptance_guide/) | 测试验收 |
| [oc_collab_detailed_design_guide](../oc_collab_detailed_design_guide/) | 详细设计 |

---

## 常用命令

```bash
# 查看所有章节
oc-collab skill slice oc_collab_version_management_guide

# 查看特定章节
oc-collab skill slice oc_collab_patch_release_guide --level section

# 过滤特定内容
oc-collab skill slice oc_collab_detailed_design_guide --filter "版本号"
```

---

**维护者**: Agent 1
**版本**: v1.0.0
**更新日期**: 2026-02-15

---

## SOP结构概览 ⭐

| SOP要素 | 内容 |
|---------|------|
| **1. 版本类型** | Patch/Minor/Major定义 |
| **2. 版本号规则** | v2.2.12 → v2.2.12.1 → v2.2.13 |
| **3. 发布流程** | Patch/Minor/Major发布步骤 |
| **4. 发布前检查** | 检查清单速查表 |
| **5. 文档版本** | 文档版本号管理 |

---

## 触发条件 ⭐

**触发关键词**: `版本`, `version`, `发布`, `release`, `patch`, `tag`

| 场景 | 触发条件 |
|------|----------|
| Patch发布 | Bug影响日常开发，需立即修复 |
| Minor发布 | 新功能完成，向后兼容 |
| 版本核对 | 确认版本号一致性 |

---

## 操作步骤 ⭐

| 阶段 | 步骤 | 操作 | 强制 |
|------|------|------|------|
| **准备** | 1 | 判断发布类型（Patch/Minor/Major） | ✅ |
| **准备** | 2 | 更新版本号 | ✅ |
| **准备** | 3 | 更新CHANGELOG | ✅ |
| **准备** | 4 | 单元测试通过 | ✅ |
| **发布** | 5 | 构建包 | |
| **发布** | 6 | PyPI上传 | |
| **发布** | 7 | Git推送 | |
| **验证** | 8 | API验证 | ✅ |
| **验证** | 9 | pip安装测试 | ✅ |

---

## 输出产物 ⭐

| 产物 | 位置 | 格式 |
|------|------|------|
| PyPI包 | https://pypi.org/project/opencode-collaboration/ | Python包 |
| Git标签 | git tag v2.2.12.1 | Git |
| 版本提交 | git commit | Git |
| CHANGELOG | CHANGELOG.md | Markdown |

---

## 验收标准 ⭐

| 标准 | 检查方法 |
|------|----------|
| 版本号正确 | grep "version" pyproject.toml |
| 测试全部通过 | pytest tests/ |
| CHANGELOG已更新 | grep "v2.2.12.1" CHANGELOG.md |
| Git标签已创建 | git tag --list |
| PyPI可安装 | pip install opencode-collaboration==2.2.12.1 |
