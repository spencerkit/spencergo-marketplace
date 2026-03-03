# Writing Outline

> 独立的大纲生成模块 - 智能结构推荐，3-5 个大纲选项

## 功能

### 核心功能

- **多选项生成** - 提供 3-5 个大纲选项
- **内容类型结构库** - 公众号/小红书/技术教程/故事/短视频
- **智能结构推荐** - 根据内容类型推荐最佳结构
- **大纲调整确认** - 支持修改和确认

### 支持的内容平台

- 公众号文章
- 小红书帖子
- 技术教程
- 故事/小说
- 短视频脚本
- B 站视频脚本

## 使用方法

```bash
/spencergo:writing-outline
```

或描述需求：
- "帮我列个公众号文章大纲"
- "生成一个关于 XX 的大纲"

## 触发方式

- 直接调用：`/spencergo:writing-outline`
- 描述式："列个大纲"、"生成outline"

## 工作流程

1. 用户描述写作需求（主题、平台、目标读者）
2. AI 生成 3-5 个大纲选项
3. 用户选择或提出修改意见
4. 确认最终大纲

## 示例

```
> /spencergo:writing-outline

请告诉我：
1. 写作平台
2. 主题
3. 目标读者
```

## 安装

This skill is part of spencergo-marketplace.

Installation:
```bash
/plugin marketplace add spencerkit/spencergo-marketplace
/plugin install spencergo@spencerkit/spencergo-marketplace
```

## License

MIT
