---
name: writing
description: Comprehensive writing skill V4 (hybrid mode). Supports independent module invocation or preset template combinations.
---

# Writing Skill V4 (Hybrid Mode)

## Module Architecture

writing (Main Skill)
├── writing-style    → Style analysis
├── writing-outline  → Outline generation
├── writing-content  → Content writing
├── writing-review   → Content review
└── writing-polish   → Polish

## Preset Templates

| Template | Modules | Use Case |
|----------|---------|----------|
| Full writing | style → outline → content → review → polish | Complete article from scratch |
| Quick writing | style → content | Short content, familiar topic |
| Polish only | polish | Already have draft, just polish |
| Review + polish | review → polish | Written, want review + polish |

## Independent Invocation

User can invoke any sub-module directly:
- /spencergo:writing-style - Style analysis
- /spencergo:writing-outline - Outline generation
- /spencergo:writing-content - Content writing
- /spencergo:writing-review - Content review
- /spencergo:writing-polish - Polish

---

## Flow Guide (Claude Auto-Chaining)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Writing Flow                              │
├─────────────────────────────────────────────────────────────────┤
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐  │
│   │  Style   │───▶│  Outline │───▶│  Content │───▶│ Review │  │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬────┘  │
│        │                │                │                │        │
│        ▼                ▼                ▼                ▼        │
│   /spencergo:writing-       /spencergo:writing-       /spencergo:writing-       /spencergo:writing-     │
│     style          outline         content         review         │
│        │                │                │                │        │
│        │                │                │                ▼        │
│        │                │                │            ┌────────┐  │
│        │                │                │            │ Polish │  │
│        │                │                │            └───┬────┘  │
│        │                │                │                │        │
│        │                │                │                ▼        │
│        │                │                │            ┌────────┐  │
│        │                │                │            │Delivery│  │
│        │                │                │            └────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Each phase MUST invoke corresponding skill after user confirmation:

1. Style → confirmed → invoke /spencergo:writing-outline
2. Outline → confirmed → invoke /spencergo:writing-content
3. Content → confirmed → invoke /spencergo:writing-review
4. Review → confirmed → invoke /spencergo:writing-polish
5. Polish → delivery

### Key Rules

- DO NOT skip any phase (unless user explicitly requests quick mode)
- MUST get user confirmation before moving to next phase
- DO NOT invoke review during content writing - wait for user to confirm draft
- DO NOT auto-polish after review - wait for user to confirm review results

---

The terminal state is delivery. DO NOT skip any phase. The ONLY flow is: style → outline → content → review → polish → delivery.

<CRITICAL>
When user says "continue", "next", "start", etc., you MUST:

1. Tell user which phase you're entering
2. Use Skill tool to invoke the corresponding sub-skill
3. Example: user says "continue with outline" → you MUST invoke /spencergo:writing-outline via Skill tool
</CRITICAL>

---

For detailed flow, please refer to sub-modules:
- /spencergo:writing-style - Style analysis detailed flow
- /spencergo:writing-outline - Outline generation detailed flow
- /spencergo:writing-content - Content writing detailed flow
- /spencergo:writing-review - Content review detailed flow
- /spencergo:writing-polish - Polish detailed flow
