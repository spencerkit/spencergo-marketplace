---
name: research-studio
description: "Structured topic research and multi-angle analysis for a user-provided topic, market, trend, concept, project, platform, industry, or content direction. Use when the user asks to research, investigate, analyze, study, or survey a topic and expects more than a simple search result dump, including multi-round retrieval, source comparison, dimension-based analysis, opportunity/risk assessment, and a clear research summary."
---

# Research Studio

Turn a user topic into a structured research result.

## Core rule

Do not stop at search results.
Convert gathered information into a research judgment.

Default workflow:
1. front-load requirement clarification and alignment
2. define the exact research question
3. classify the topic type
4. break the topic into useful analysis dimensions
5. run multiple retrieval passes
6. compare and synthesize sources
7. produce a structured result with depth, examples, and operational guidance
8. explicitly mark uncertainty, weak evidence, and missing information

Read `references/intake-and-alignment.md` before starting substantive execution.
Read `references/grilling.md` when the brief is vague, high-stakes, branching, or likely to cause later rework unless the requirements are pressure-tested up front.
Read `references/intake-question-batch.md` when you need a compact one-shot question set for front-loaded alignment.
Read `references/depth-standard.md` before writing the main analysis.
Read `references/report-quality-benchmarks.md` before final delivery when the task is a serious report rather than a quick scan.

## Default answer style

By default:
- lead with the conclusion
- avoid filler and generic framing
- avoid link dumps with no synthesis
- avoid pretending certainty when evidence is incomplete
- avoid shallow summary that only states phenomena
- include mechanism, examples, and operational guidance for important points

Be concise when the user wants a quick result.
Be detailed when the task itself is a substantive research report.

Only expand beyond necessary research depth when the user explicitly asks for more detail, such as:
- 补充说明
- 详细说说
- 展开
- 给我完整分析

## Research modes

Choose the lightest sufficient mode.

### 1. Quick scan
Use for early-stage orientation, rough opportunity checks, and first-pass topic understanding.

### 2. Standard research
Use by default for most user requests.

### 3. Deep research
Use when the user explicitly asks for deep analysis, comprehensive coverage, or a more decision-ready report.

## Topic typing

Before researching, determine which topic type fits best.
Read `references/topic-types.md` when the topic scope or research angle is unclear.

Typical topic types:
- market / industry
- product / project
- platform / content ecosystem
- concept / trend
- audience / demand
- business model / monetization

## Dimension selection

Do not use the same dimensions blindly for every topic.
Select the most relevant set.
Read `references/dimensions.md` before structuring the analysis.

Common dimensions include:
- definition and scope
- current state
- user demand
- competitive landscape
- monetization / business model
- growth drivers
- risks / uncertainty
- opportunities
- conclusion

## Retrieval workflow

Read `references/workflow.md` for the detailed workflow.
Read `references/query-planning.md` before searching so queries are split by dimension instead of repeated vaguely.
Read `references/query-examples.md` when you need examples of how to turn a topic into practical query buckets.

At minimum:
- do an initial scan
- do targeted follow-up searches by dimension
- cross-check important claims
- prefer stronger sources when claims conflict

When evaluating source reliability, read `references/source-quality.md`.
When presenting key evidence in the final result, follow `references/source-citation-format.md`.

## Output pattern

Read `references/output-template.md` before drafting the final response.
Then choose the most specific output template that matches the topic:
- `references/output-template-market.md` for market / industry research
- `references/output-template-project.md` for product / project / worth-doing research
- `references/output-template-platform-content.md` for platform / content ecosystem research

For stronger delivery shape, also use the matching sample report reference:
- `references/sample-market-report.md`
- `references/sample-project-report.md`
- `references/sample-platform-report.md`

When the user wants a deliverable report, also read:
- `references/html-report-spec.md`
- `references/chart-rules.md`
- `references/chart-components.md`
- `references/advanced-chart-patterns.md`
- `references/report-components.md`
- `references/component-layout-strategies.md`
- `references/visual-style.md`
- `references/evidence-display.md`

Default output should include:
- one-line conclusion
- key findings
- dimension-based research result
- biggest opportunity
- biggest risk
- information gaps
- suggested next step if deeper research is needed

For report delivery, generate a structured JSON payload and produce the default artifact set:
- `report.svg`
- `report.png`
- `report.md`
- structured JSON payload

Use the SVG report as the primary rendered artifact.
Use PNG as a derived preview artifact.
Treat Markdown as a first-class report artifact, not a fallback note.
Follow `references/report-json-schema.md` for the payload shape.

## Hard rules

- Do not dump raw search results without synthesis.
- Do not rely on a single weak source for an important conclusion.
- Do not hide uncertainty.
- Do not inflate weak evidence into a confident judgment.
- Do not write generic statements that could apply to almost any topic.
- Do not use empty phrases such as “值得关注”, “具备潜力”, “未来可期”, or “可以进一步观察” unless immediately followed by concrete reasons, boundaries, and evidence status.
- Every meaningful conclusion should be supported by evidence, direct source comparison, or clearly labeled reasoning.
- Every important factual claim should have a clear source reference or be marked as unsupported.
- If a claim is weakly supported, downgrade it explicitly to a tentative view or open question.
- Separate what is evidenced, what is inferred, and what remains unknown.
- If data is missing, leave it blank or mark it as 待补充 rather than inventing numbers or pretending the evidence exists.
- Do not fabricate evidence, fill gaps with speculation, or present guesses as sourced support.
- Do not create decorative charts from weak, missing, or unsourced data.
- For report delivery, prefer a single self-contained SVG file with inline assets where possible.
- If images are used in the report, prefer base64 embedding to keep rendered artifacts self-contained.
- If external context is required and tools are available, search first.
- If tools are unavailable or evidence remains thin, say so clearly.
