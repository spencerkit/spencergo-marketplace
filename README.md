# spencergo

> Spencer's personal skills bundle for Claude Code

## Installation

```bash
# Add the marketplace
/plugin marketplace add spencerkit/spencergo-marketplace

# Install the skills bundle
/plugin install spencergo@spencerkit/spencergo-marketplace
```

## Available Skills

| Skill | Description | Usage |
|-------|-------------|-------|
| **writing** | Comprehensive writing assistant (V4 hybrid mode) | `/spencergo:writing` |
| **naming** | AI naming assistant (26+ scenarios) | `/spencergo:naming` |
| **yi** | I Ching divination (64 hexagrams) | `/spencergo:yi` |
| **code-review** | Multi-language code review with security audit | `/spencergo:code-review` |

## Capability Matrix

| Skill | Input | Output | Best For | Notes |
|-------|-------|--------|----------|-------|
| **writing** | Topic, audience, platform, style preferences | End-to-end draft (style/outline/content/review/polish) | Full content creation workflow | Use `/spencergo:writing` for template mode |
| **writing-style** | Sample text or target style | Style analysis and writing guidance | Defining tone before writing | Analysis-only module |
| **writing-outline** | Topic, audience, length goal | Structured outline | Planning article/script structure | Best used before content drafting |
| **writing-content** | Topic or outline + writing requirements | First draft content | Rapid content generation | Pair with review/polish for final quality |
| **writing-review** | Existing draft | Quality feedback (logic, clarity, structure) | Pre-publish review | Review-focused, not final rewrite |
| **writing-polish** | Existing draft | Polished version with improved fluency | Final refinement pass | Does not replace factual verification |
| **naming** | Naming target, style, keywords, language preference | Candidate names with rationale | Product/brand/account/code naming | Trademark/domain availability should be checked separately |
| **code-review** | Code snippets/files + context | Findings across quality/security/performance | Pre-commit or pre-merge checks | Complements, not replaces tests/runtime validation |
| **yi** | User question for divination | Hexagram result and interpretation | Cultural/entertainment exploration | Not a software productivity workflow |

## Documentation

See [complete documentation](https://spencerkit.github.io/spencergo-marketplace/) for detailed usage guides and examples.

## Writing Sub-modules

The writing skill includes 5 independent sub-modules:

| Module | Description | Usage |
|--------|-------------|-------|
| writing-style | Style analysis | `/spencergo:writing-style` |
| writing-outline | Outline generation | `/spencergo:writing-outline` |
| writing-content | Content writing | `/spencergo:writing-content` |
| writing-review | Content review | `/spencergo:writing-review` |
| writing-polish | Polish & de-AI-ify | `/spencergo:writing-polish` |

For detailed documentation, see each skill's README in `skills/` directory.

## License

MIT
