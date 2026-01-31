# 详细设计：文档自动添加git功能

## 实现方案
- 新增 AutoDocGitAddEngine 类
- 监听 docs/ 目录变化
- 自动执行 git add
