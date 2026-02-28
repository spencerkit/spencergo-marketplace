# spencergo

> Spencer's personal skills bundle for Claude Code

A collection of Claude Code skills for daily life and productivity.

## Installation

```bash
# Add the marketplace
/plugin marketplace add spencerkit/spencergo-marketplace

# Install the skills bundle
/plugin install spencergo@spencergo-marketplace
```

## Available Skills

### yi - I Ching Divination

I Ching divination skill using coin tossing to generate hexagrams, providing interpretations and AI analysis.

**Usage:**
```bash
/yi
```

### naming - AI Naming Assistant

Universal AI naming skill for generating suitable names in any scenario. Supports 26+ naming scenarios including project names, product names, character names, brand names, pet names, and more.

**Usage:**
```bash
/naming
```

### writing - AI Writing Assistant

Comprehensive writing skill supporting multiple writing types including WeChat articles, Little Red Book notes, short video scripts, stories, novels, poetry, technical articles, and more.

**Usage:**
```bash
/writing
```

## Rules

This repository includes TypeScript/JavaScript coding standards that can be used with Claude Code.

### Installation

```bash
# Install common rules (required)
cp -r rules/common ~/.claude/rules/common

# Install JavaScript rules
cp -r rules/javascript ~/.claude/rules/javascript
```

For more details, see [rules/README.md](rules/README.md).

## Adding New Skills

Feel free to submit PRs to add more useful skills!

## License

MIT
