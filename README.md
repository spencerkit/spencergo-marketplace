# spencergo

> Spencer 的 Claude Code 个人技能包

日常生活和生产力工具的 Claude Code 技能集合。

## 安装

```bash
# 添加市场
/plugin marketplace add spencerkit/spencergo-marketplace

# 安装技能包
/plugin install spencergo@spencergo-marketplace
```

## 可用技能

### yi - 易经占卜

使用投币方式生成易经卦象的占卜技能，提供解释和 AI 分析。

**使用方法：**
```bash
/yi
```

### naming - AI 命名助手

通用 AI 命名技能，可在任何场景下生成合适的名称。支持 26+ 种命名场景，包括项目名称、产品名称、角色名称、品牌名称、宠物名称等。

**使用方法：**
```bash
/命名
```

### writing - AI 写作助手

综合写作技能，支持公众号文章、小红书笔记、短视频脚本、故事小说、诗歌、技术文章等多种写作类型。

**使用方法：**
```bash
/写作
```

## 规范

本仓库包含可与 Claude Code 一起使用的 TypeScript/JavaScript 编码规范。

### 安装

```bash
# 安装通用规范（必需）
cp -r rules/common ~/.claude/rules/common

# 安装 JavaScript 规范
cp -r rules/javascript ~/.claude/rules/javascript
```

更多详情，请参阅 [rules/README.md](rules/README.md)。

## 添加新技能

欢迎提交 PR 来添加更多有用的技能！

## 许可证

MIT
