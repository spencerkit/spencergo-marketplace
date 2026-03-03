# Writing Review

> 独立的内容审核模块 - AI 预测读者问题，多维度审核，量化评分

## 功能

### 核心功能

- **AI 读者视角** - 预测读者可能提出的问题
- **多维度审核** - 逻辑/读者视角/情感/结构/AI 模式检测
- **量化评分** - 给出具体的质量分数
- **改进建议** - 提供可操作的优化建议

### 审核维度

- 逻辑完整性
- 读者理解度
- 情感表达
- 结构层次
- AI 写作痕迹检测

## 使用方法

```bash
/spencergo:writing-review
```

或直接描述审核需求：
- "帮我审核这篇文章"
- "检查一下这段内容"

## 触发方式

- 直接调用：`/spencergo:writing-review`
- 描述式："帮我审核"、"检查内容"

## 工作流程

1. 用户提供需要审核的内容
2. AI 进行多维度分析
3. 输出审核结果和评分
4. 提供改进建议

## 示例

```
> /spencergo:writing-review

请提供需要审核的内容...
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
