# 黑盒测试用例：Git自动同步 + 文档自动添加git

## TC-GIT-001: 检测变更文件
输入: git status --porcelain 输出
预期: 返回变更文件列表

## TC-GIT-002: 自动 git add
输入: 检测到变更文件
预期: 执行 git add，文件进入暂存区

## TC-GIT-003: 自动 commit
输入: 暂存区有内容
预期: 创建提交

## TC-GIT-004: 自动 push
输入: 有待推送的提交
预期: 推送到远程

## TC-DOC-001: 检测新文档
输入: git ls-files --others
预期: 返回 docs/ 下的新文件

## TC-DOC-002: 自动添加文档
输入: 检测到新文档
预期: 执行 git add
