# Testing Framework

Automated testing framework for spencergo skills.

## Structure

```
tests/
├── run-all.sh                    # Main test runner
├── test-helpers.sh               # Shared test utilities
├── analyze-session.py             # Session transcript analyzer
├── skill-triggering/
│   ├── run-all.sh                 # Run all skill tests
│   └── cases/                     # Test cases
│       ├── naming.json
│       ├── writing-style.json
│       ├── writing-outline.json
│       ├── writing-content.json
│       ├── writing-review.json
│       ├── writing-polish.json
│       └── yi.json
└── integration/                   # Integration tests (future)
```

## Quick Start

```bash
# Run all tests
cd tests
./run-all.sh

# Or run skill tests directly
cd tests/skill-triggering
./run-all.sh
```

## Adding Test Cases

Add test cases to `cases/<skill-name>.json`:

```json
{
  "skill": "spencergo:naming",
  "description": "AI naming assistant test cases",
  "test_cases": [
    {
      "name": "project-naming",
      "prompt": "帮我起一个项目名称",
      "expected_contains": ["项目", "名称"],
      "not_expected": ["错误", "失败"],
      "timeout": 60
    }
  ]
}
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique test name |
| `prompt` | Yes | Input prompt for the skill |
| `expected_contains` | No | List of strings that should appear in response |
| `not_expected` | No | List of strings that should NOT appear |
| `timeout` | No | Timeout in seconds (default: 60) |

## Analyzing Sessions

After running tests, analyze session transcripts:

```bash
# Find session files
ls ~/.claude/projects/

# Analyze a session
node tests/analyze-session.js ~/.claude/projects/<session-id>.jsonl

# Check if specific skill was invoked
node tests/analyze-session.js <session>.jsonl --check-skill spencergo:naming
```

## Requirements

- Claude Code CLI installed (`claude` command)
- Node.js 14+
- Test project directory in `~/.claude/projects/`

## Test Types

### Skill Triggering Tests

Verify skills can be invoked and respond correctly.

### Integration Tests (Future)

Test complete workflows across multiple skills.
