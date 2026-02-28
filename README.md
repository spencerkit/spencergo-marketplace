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
