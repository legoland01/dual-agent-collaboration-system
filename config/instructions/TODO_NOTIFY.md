# TODO通知处理规则

## 触发条件
当用户告知"我有新TODO"或"查看TODO"时，执行以下操作：

## 操作流程
1. 读取 state/todos.db 中的未读TODO
2. 查找当前用户的未处理TODO
3. 使用 question tool 询问用户操作

## Question Tool 调用示例
当检测到用户有未读TODO时，应调用question tool：

```json
{
  "name": "question",
  "arguments": {
    "questions": [{
      "header": "待办事项",
      "question": "您有 {count} 个待处理TODO: {todo_list}",
      "options": [
        {"label": "立即执行", "description": "开始处理第一个TODO"},
        {"label": "稍后处理", "description": "设置提醒，稍后处理"},
        {"label": "查看详情", "description": "查看所有TODO详情"},
        {"label": "忽略", "description": "暂时忽略"}
      ]
    }]
  }
}
```

## 可用操作
- **立即执行**: 标记TODO为进行中，开始处理
- **稍后处理**: 将TODO标记为延迟，设置提醒时间
- **查看详情**: 显示TODO完整列表和内容
- **忽略**: 关闭通知

## TODO状态说明
- pending: 待处理
- in_progress: 进行中
- completed: 已完成
- cancelled: 已取消
- deferred: 已延迟
