# spencergo-rules

TypeScript/JavaScript coding standards and best practices for Claude Code.

## Structure

```
rules/
├── README.md              # This file
├── common/                # Language-agnostic principles
│   ├── coding-style.md    # Code style guidelines
│   ├── git-workflow.md    # Git conventions
│   └── testing.md        # Testing requirements
└── javascript/           # JavaScript/TypeScript specific
    ├── coding-style.md    # TS/JS code patterns
    └── testing.md        # Vitest testing guide
```

## Installation

### Option 1: Install to Global Rules

Copy the rules to your global Claude Code rules directory:

```bash
# Install common rules (required)
cp -r rules/common ~/.claude/rules/common

# Install JavaScript rules
cp -r rules/javascript ~/.claude/rules/javascript
```

### Option 2: Project-Level Rules

Reference these rules in your project's `.claude/` directory:

```bash
# Create project-level rules directory
mkdir -p .claude/rules

# Link or copy rules
ln -s ../../rules/common .claude/rules/common
ln -s ../../rules/javascript .claude/rules/javascript
```

## What's Included

### Common Rules

- **coding-style.md**: Immutability, file organization, error handling, input validation
- **git-workflow.md**: Commit message format, branch naming, PR workflow
- **testing.md**: Coverage requirements (80%), TDD workflow

### JavaScript/TypeScript Rules

- **coding-style.md**: TypeScript patterns, Zod validation, naming conventions
- **testing.md**: Vitest configuration, Testing Library patterns, mocking

## Usage

When Claude Code works on your project, it will automatically load rules that match the file paths specified in each rule file's frontmatter.

## Extending

To add your own rules:

1. Edit files in `common/` for universal rules
2. Edit files in `javascript/` for JS/TS-specific rules
3. Create new rule files following the same pattern
