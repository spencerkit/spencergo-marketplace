# Writing Content

> 独立的内容写作模块 - 根据大纲写作，实时风格对比，嵌入式自检

## 功能

### 核心功能

- **大纲写作** - 根据确定的大纲进行内容创作
- **实时风格对比** - 与目标风格进行对比，确保一致
- **嵌入式自检** - AI 写作痕迹检测、节奏检查、逻辑检查
- **多种写作节奏** - 干货型、故事型、情感型等

### 支持的内容类型

- 公众号文章
- 小红书/微博帖子
- 短视频脚本
- B 站视频脚本
- 技术教程
- 故事/短篇小说

## 使用方法

```bash
/spencergo:writing-content
```

或描述写作需求：
- "帮我写一篇文章"
- "写一个关于 XX 的内容"

## 触发方式

- 直接调用：`/spencergo:writing-content`
- 描述式："帮我写作"、"写篇文章"

## 工作流程

1. 确认大纲（通常由 writing-outline 生成）
2. 按章节/段落逐步写作
3. 实时对比目标风格
4. 完成后进行自检

## 示例

```
> /spencergo:writing-content

请提供大纲或写作需求...
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
