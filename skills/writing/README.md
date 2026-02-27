# Writing Skill V3

> Comprehensive writing skill with Fast/Standard dual modes and 6-stage collaborative workflow

## Features

### Core Features

- **Smart Mode Selection** - Auto-detect Fast mode vs Standard mode
- **6-Stage Collaborative Writing** - Shift from one-way output to full collaboration
- **Dynamic Demo** - Adjust demo length and format based on content type
- **Real-time Style Check** - Continuously compare against demo style during writing
- **Progress Visualization** - Show progress indicator for each stage
- **Flexible Rollback** - Return to previous step at any stage
- **Embedded Self-Check** - Lightweight quality checks during writing

### Supported Content Types

- WeChat Official Account / Blog Articles
- Xiaohongshu / Weibo Posts
- Short Video Scripts
- Bilibili Video Scripts
- Technical Tutorials / Analysis
- Stories / Short Fiction

## Mode Selection

**Fast Mode** (triggers when ANY condition is met):
- Word count < 500
- User says "简单写写" / "随便写写" (quick write)
- Content type is Xiaohongshu / Weibo / Moments

**Fast Mode Workflow**: Requirements → Style Check → One-shot Writing → Delivery

**Standard Mode Workflow**: Full 6 stages (with progress indicators [1/6] ~ [6/6])

---

## Writing Workflow (6 Stages)

| Stage | Name | Core Content | Progress |
|-------|------|--------------|----------|
| 1 | Requirements | Purpose, background, viewpoint, audience, writing pace | [1/6] |
| 2 | Outline | 3-5 outline options → Select → Confirm | [2/6] |
| 3 | Style Check | Preferences + Dynamic Demo + User Approval | [3/6] |
| 4 | Section Writing | Write by pace + Real-time style check + Self-check | [4/6] |
| 5 | Review | AI questions + User additions + Revisions | [5/6] |
| 6 | Style Review + Delivery | Style comparison + Auto-fix + Final review | [6/6] |

## Usage

```bash
/写作
```

Or describe your需求 directly:
- "帮我写一篇公众号文章，主题是..." (Write a WeChat article about...)
- "写一个科幻短故事" (Write a sci-fi short story)
- "一篇Python入门教程" (A Python beginner tutorial)

## Workflow

1. Type `/写作` or describe your writing needs
2. **Auto-detect mode**: Short content (<500 words) → Fast mode, otherwise → Standard mode
3. **Stage 1 - Requirements [1/6]**: Answer questions about type, purpose, background, viewpoint, audience; choose writing pace
4. **Stage 2 - Outline [2/6]** (Standard): Select from 3-5 outline options
5. **Stage 3 - Style Check [3/6]**: Answer style preferences, generate dynamic demo based on content type, confirm
6. **Stage 4 - Section Writing [4/6]**: Write according to chosen pace, compare with demo style in real-time, self-check after each section
7. **Stage 5 - Review [5/6]** (Standard): AI anticipates questions, user adds input, revisions made
8. **Stage 6 - Style Review + Delivery [6/6]**: Final style review, deliver

> 💡 Type "返回上一步" (return to previous step) at any stage to adjust

## Examples

### WeChat Article
```
User: /写作
Skill: What type of article do you want to write?
User: WeChat article
Skill: What's the topic?
User: About AI's impact on future work
Skill: Who is the target audience?
...
```

### Story Writing
```
User: Write a sci-fi story
Skill: What type of sci-fi? Hard sci-fi/Soft sci-fi/Cyberpunk?
User: Cyberpunk
Skill: Who are the main characters?
...
```

## Refinement Options

After generation, you can:
- Change style
- Shorten/expand
- Adjust tone
- Regenerate

## License

MIT
