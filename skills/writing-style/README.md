# Writing Style

> 独立的风格分析模块 - 风格样本分析，量化指标，风格冲突检测

## 功能

### 核心功能

- **风格样本分析** - 分析给定文本的风格特征
- **量化指标** - 给出具体的风格数值（句长、词汇、情感等）
- **风格冲突检测** - 检测内容中的风格不一致
- **内容类型适配** - 根据平台调整风格

### 分析维度

- 词汇特征（口语化/书面语/专业术语）
- 句式结构（长句/短句/变化）
- 语气语调（幽默/严肃/温暖）
- 开头结尾模式

## 使用方法

```bash
/spencergo:writing-style
```

或直接提供内容分析：
- "分析这个风格：..."
- "这个写作风格怎么样"

## 触发方式

- 直接调用：`/spencergo:writing-style`
- 描述式："分析风格"、"这是什么风格"

## 工作流程

1. 用户提供风格样本或描述需求
2. AI 分析风格特征
3. 输出量化指标和风格画像
4. 提供风格适配建议

## 示例

```
> /spencergo:writing-style

请提供风格样本或描述你想要的风格：
- 粘贴一段文字进行分析
- 或描述你想要的风格特点
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
