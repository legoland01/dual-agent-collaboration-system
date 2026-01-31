# 详细设计：Git自动同步功能

## 实现方案
- 新增 AutoGitSyncEngine 类
- 检测文件变更 (git status --porcelain)
- 自动执行 add → commit → push
