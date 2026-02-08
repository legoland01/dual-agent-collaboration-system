# Proposal: Git同步优先Gitee

**提案编号**: PROPOSAL-GIT-001
**版本**: v1
**创建日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**状态**: DRAFT

---

## 背景

GitHub经常连不上，影响协作效率。需要CLI支持优先Gitee。

---

## 需求

### Git同步优先级

| 优先级 | 操作 |
|--------|------|
| 1 | Push → Gitee |
| 2 | Push → GitHub (Gitee失败时) |
| 1 | Pull → GitHub |
| 2 | Pull → Gitee (GitHub失败时) |

### 命令增强

#### `oc-collab git push`

```bash
# 现状：推送到所有远程
oc-collab git push

# 需求：优先Gitee，GitHub备用
oc-collab git push --priority gitee
```

#### `oc-collab git pull`

```bash
# 现状：从默认远程拉取
oc-collab git pull

# 需求：优先GitHub，Gitee备用
oc-collab git pull --priority github
```

### 配置文件

```yaml
# config/sync.yaml
sync:
  priority:
    push: gitee  # push优先Gitee
    pull: github # pull优先GitHub
  fallbacks:
    push:
      - github
    pull:
      - gitee
```

---

## 实现方案

### GitHelper增强

```python
class GitHelper:
    def push_with_priority(self, priority: str = "gitee") -> Dict[str, Any]:
        """优先推送到指定平台。"""
        remotes = self.get_all_remotes()
        
        # 优先平台
        if priority in remotes:
            result = self.push_to_remote(priority)
            if result.success:
                return {"success": True, "remote": priority}
        
        # 备用平台
        for remote in remotes:
            if remote != priority:
                result = self.push_to_remote(remote)
                if result.success:
                    return {"success": True, "remote": remote, "fallback": True}
        
        return {"success": False, "error": "所有远程推送失败"}
```

---

## 验收标准

- [ ] `oc-collab git push --priority gitee` 优先推送到Gitee
- [ ] Gitee失败时自动fallback到GitHub
- [ ] `oc-collab git pull --priority github` 优先从GitHub拉取
- [ ] GitHub失败时自动fallback到Gitee
- [ ] 单元测试覆盖fallback场景

---

## 工时预估

| 任务 | 工时 |
|------|------|
| GitHelper增强 | 3h |
| CLI命令更新 | 1h |
| 单元测试 | 2h |
| **总计** | **6h** |

---

## 依赖

| 依赖 | 说明 |
|------|------|
| `src/core/git.py` | GitHelper |
| `src/cli/main.py` | push/pull命令 |

---

## 风险与应对

| 风险 | 可能性 | 影响 | 应对 |
|------|--------|------|------|
| Gitee也连不上 | 低 | 中 | 保持fallback到GitHub |

---

## 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-08 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT
